#!/usr/bin/env python3
"""Match gallery thumb resolutions to hotelsheldon.com (~768px Elementor sizes)."""
from __future__ import annotations

import re
import ssl
import urllib.request
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

try:
    from PIL import Image
except ImportError:
    import subprocess

    subprocess.check_call(["pip", "install", "pillow", "-q"])
    from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
GALLERY_HTML = ROOT / "gallery" / "index.html"
THUMB_DIR = ROOT / "assets" / "media" / "gallery-thumbs"
THUMB_DIR.mkdir(parents=True, exist_ok=True)

CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0"}


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, context=CTX, timeout=60).read()


def basename_key(name: str) -> str:
    name = Path(name).name.lower()
    name = re.sub(r"-\d+x\d+(?=\.)", "", name)
    return Path(name).stem


def make_local_thumb(src_path: Path, dest: Path, target_w: int = 768) -> tuple[int, int]:
    im = Image.open(src_path)
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGB")
    w, h = im.size
    if w > target_w:
        nh = int(round(h * (target_w / w)))
        im = im.resize((target_w, nh), Image.Resampling.LANCZOS)
    elif h > target_w and w < h:
        # portrait: limit by height similarly
        nw = int(round(w * (target_w / h)))
        im = im.resize((nw, target_w), Image.Resampling.LANCZOS)
    im.save(dest, "WEBP", quality=82, method=6)
    return im.size


def scrape_orig_thumbs() -> dict[str, str]:
    html = fetch("https://hotelsheldon.com/gallery/").decode("utf-8", "ignore")
    urls = set(
        re.findall(
            r"https://hotelsheldon\.com/wp-content/uploads/[^\"')\s]+?\.(?:webp|jpe?g|png)",
            html,
            re.I,
        )
    )
    # also background-image escaped urls
    urls |= set(
        re.findall(
            r"https:\\/\\/hotelsheldon\.com\\/wp-content\\/uploads\\/[^\"')\s]+?\.(?:webp|jpe?g|png)",
            html,
            re.I,
        )
    )
    urls = {u.replace("\\/", "/") for u in urls}
    by_key: dict[str, list[str]] = {}
    for u in urls:
        key = basename_key(urlparse(u).path)
        by_key.setdefault(key, []).append(u)

    # Prefer intermediate sizes (~768) for thumbs
    chosen: dict[str, str] = {}
    for key, lst in by_key.items():
        sized = [u for u in lst if re.search(r"-\d+x\d+\.", u)]
        full = [u for u in lst if u not in sized]
        pick = None
        for u in sized:
            m = re.search(r"-(\d+)x(\d+)\.", u)
            if m and 700 <= int(m.group(1)) <= 900:
                pick = u
                break
        if not pick and sized:
            pick = sized[0]
        if not pick and full:
            pick = full[0]
        if pick:
            chosen[key] = pick
    print(f"orig gallery asset keys: {len(chosen)}")
    return chosen


def main() -> None:
    orig = scrape_orig_thumbs()
    html = GALLERY_HTML.read_text(encoding="utf-8")
    srcs = re.findall(r'<button class="gtile[^"]*"[^>]*>\s*<img src="([^"]+)"', html)
    print(f"local gallery thumbs: {len(srcs)}")
    mapping: dict[str, str] = {}

    for src in srcs:
        if "/gallery-thumbs/" in src:
            continue
        local_path = ROOT / src.lstrip("/")
        name = Path(src).name
        key = basename_key(name)
        dest = THUMB_DIR / f"{Path(name).stem}-768.webp"

        if key in orig:
            try:
                data = fetch(orig[key])
                dest.write_bytes(data)
                im = Image.open(BytesIO(data))
                print(
                    f"DL {name}: {im.size[0]}x{im.size[1]} <- {Path(orig[key]).name}"
                )
            except Exception as e:
                print(f"DL fail {name}: {e}")
                if local_path.exists():
                    size = make_local_thumb(local_path, dest)
                    print(f"GEN fallback {name}: {size[0]}x{size[1]}")
                else:
                    continue
        elif local_path.exists():
            size = make_local_thumb(local_path, dest)
            print(f"GEN {name}: {size[0]}x{size[1]}")
        else:
            print(f"SKIP {src}")
            continue

        mapping[src] = f"/assets/media/gallery-thumbs/{dest.name}"

    def repl(m: re.Match) -> str:
        before, src, after = m.group(1), m.group(2), m.group(3)
        new_src = mapping.get(src)
        if not new_src:
            return m.group(0)
        # Keep full-res for lightbox via data-full
        if "data-full=" in m.group(0):
            return f"{before}{new_src}{after}"
        return f'{before}{new_src}" data-full="{src}{after}'

    new_html, n = re.subn(
        r'(<button class="gtile[^"]*"[^>]*>\s*<img src=")([^"]+)(")',
        repl,
        html,
    )
    print(f"rewrote {n} sources")
    if n:
        GALLERY_HTML.write_text(new_html, encoding="utf-8")
        print("updated gallery/index.html")


if __name__ == "__main__":
    main()
