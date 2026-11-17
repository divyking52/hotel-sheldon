#!/usr/bin/env python3
"""Compare image natural resolutions: hotelsheldon.com vs local clone sources."""
from __future__ import annotations

import json
import re
import ssl
import subprocess
import urllib.request
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin, urlparse

try:
    from PIL import Image
except ImportError:
    subprocess.check_call(["pip", "install", "pillow", "-q"])
    from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ORIG = "https://hotelsheldon.com/"
PAGES = [
    "",
    "accommodations/",
    "attractions/",
    "gallery/",
    "blog/",
    "contact/",
]
CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (compatible; image-audit/1.0)"}


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, context=CTX, timeout=45) as r:
        return r.read()


def extract_urls(html: str, base: str) -> set[str]:
    urls: set[str] = set()
    patterns = [
        r"""(?:src|data-src|data-lazy-src|data-full|data-bg)=["']([^"']+\.(?:webp|jpe?g|png|gif)(?:\?[^"']*)?)""",
        r"""url\((?:["']?)(https?://[^)"']+\.(?:webp|jpe?g|png|gif)(?:\?[^)"']*)?)""",
        r"""url\((?:["']?)(/[^)"']+\.(?:webp|jpe?g|png|gif)(?:\?[^)"']*)?)""",
        r"""srcset=["']([^"']+)""",
    ]
    for pat in patterns:
        for m in re.findall(pat, html, re.I):
            if " " in m and "," in m:
                # srcset candidates
                for part in m.split(","):
                    u = part.strip().split(" ")[0]
                    if re.search(r"\.(?:webp|jpe?g|png|gif)", u, re.I):
                        urls.add(urljoin(base, u))
            else:
                urls.add(urljoin(base, m))
    # drop data URIs / blobs
    return {u for u in urls if u.startswith("http")}


def probe(url: str) -> dict | None:
    try:
        data = fetch(url)
        im = Image.open(BytesIO(data))
        return {
            "url": url,
            "w": im.size[0],
            "h": im.size[1],
            "bytes": len(data),
            "format": im.format,
        }
    except Exception as e:
        return {"url": url, "error": f"{type(e).__name__}: {e}"}


def basename_key(url: str) -> str:
    path = urlparse(url).path
    name = Path(path).name.lower()
    # strip size suffixes like -1024x682
    name = re.sub(r"-\d+x\d+(?=\.)", "", name)
    return name


def main() -> None:
    orig_by_key: dict[str, list[dict]] = {}
    for page in PAGES:
        url = urljoin(ORIG, page)
        print(f"\n=== ORIG {url} ===")
        try:
            html = fetch(url).decode("utf-8", "ignore")
        except Exception as e:
            print("FAIL page", e)
            continue
        urls = extract_urls(html, url)
        print(f"image refs: {len(urls)}")
        for u in sorted(urls):
            info = probe(u)
            if not info:
                continue
            key = basename_key(u)
            orig_by_key.setdefault(key, []).append(info)
            if "error" in info:
                print(f"  ERR {key}: {info['error']}")
            else:
                print(f"  {info['w']}x{info['h']}\t{info['bytes']//1024}KB\t{key}")

    # Local assets + remote storebox refs used in clone HTML
    local_html_urls: set[str] = set()
    for html_path in ROOT.rglob("index.html"):
        text = html_path.read_text(encoding="utf-8", errors="ignore")
        local_html_urls |= extract_urls(text, "http://localhost/")

    print("\n=== CLONE HTML IMAGE REFS (unique basenames) ===")
    clone_by_key: dict[str, list[dict]] = {}
    for u in sorted(local_html_urls):
        # prefer probing absolute remote; for /assets use local file
        parsed = urlparse(u)
        if parsed.path.startswith("/assets/"):
            local = ROOT / parsed.path.lstrip("/")
            if local.exists():
                im = Image.open(local)
                info = {
                    "url": str(local),
                    "w": im.size[0],
                    "h": im.size[1],
                    "bytes": local.stat().st_size,
                    "format": im.format,
                    "source": "local-file",
                }
            else:
                info = {"url": u, "error": f"missing local {local}"}
        elif parsed.netloc:
            info = probe(u)
            if info and "error" not in info:
                info["source"] = "remote"
        else:
            continue
        key = basename_key(info.get("url", u) if "url" in info else u)
        # better key from original url path
        key = basename_key(u)
        clone_by_key.setdefault(key, []).append(info)
        if "error" in info:
            print(f"  ERR {key}: {info['error']}")
        else:
            print(
                f"  {info['w']}x{info['h']}\t{info['bytes']//1024}KB\t{key}\t({info.get('source')})"
            )

    # Compare overlapping keys
    print("\n=== MISMATCHES (same basename, different WxH) ===")
    mismatches = []
    only_orig = []
    only_clone = []
    for key in sorted(set(orig_by_key) | set(clone_by_key)):
        o = next((x for x in orig_by_key.get(key, []) if "w" in x), None)
        c = next((x for x in clone_by_key.get(key, []) if "w" in x), None)
        if o and c:
            if (o["w"], o["h"]) != (c["w"], c["h"]):
                mismatches.append(
                    {
                        "key": key,
                        "orig": f"{o['w']}x{o['h']}",
                        "clone": f"{c['w']}x{c['h']}",
                        "orig_url": o["url"],
                        "clone_url": c["url"],
                    }
                )
                print(
                    f"  DIFF {key}: orig {o['w']}x{o['h']} vs clone {c['w']}x{c['h']}"
                )
        elif o and not c:
            only_orig.append(key)
        elif c and not o:
            only_clone.append(key)

    print(f"\nmismatches: {len(mismatches)}")
    print(f"only on original (basename): {len(only_orig)}")
    print(f"only on clone (basename): {len(only_clone)}")
    out = ROOT / "scripts" / "image-resolution-report.json"
    out.write_text(
        json.dumps(
            {
                "mismatches": mismatches,
                "only_orig_sample": only_orig[:40],
                "only_clone_sample": only_clone[:40],
                "orig_count_keys": len(orig_by_key),
                "clone_count_keys": len(clone_by_key),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
