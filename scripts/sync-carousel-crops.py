#!/usr/bin/env python3
"""Download original 500x600 carousel crops and wire them into the clone."""
from __future__ import annotations

import re
import ssl
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "media" / "carousel-500x600"
OUT.mkdir(parents=True, exist_ok=True)

# From live hotelsheldon.com homepage carousel (natural 500x600)
CROPS = {
    "DSC02678": "https://hotelsheldon.com/wp-content/uploads/elementor/thumbs/DSC02678-r9wshs0c3cjeorjyzuuzsr87aryp0tx42yov9jruy8.webp",
    "DSC02324": "https://hotelsheldon.com/wp-content/uploads/elementor/thumbs/DSC02324-r9wsj14l7e9661qfoed34fubt9sbaaw89606atwynk.webp",
    "DSC02321": "https://hotelsheldon.com/wp-content/uploads/elementor/thumbs/DSC02321-r9wsjtbqwfbruclh3qjw78q5mtxbp806d1kqp4r5gw.webp",
    "DSC02774": "https://hotelsheldon.com/wp-content/uploads/elementor/thumbs/DSC02774-r9wr2jszmeetxtys4poywoltssgjiojr1eq7onqa28.webp",
    "DSC02538": "https://hotelsheldon.com/wp-content/uploads/elementor/thumbs/DSC02538-r9wrycoeuly2qvrsfgkk9np9c3ply0stetbm7okrjk.webp",
    "DSC02445": "https://hotelsheldon.com/wp-content/uploads/elementor/thumbs/DSC02445-r9wrvgcbrzz8y5zccpgz2w13ebzv7mam0gwpxyvgq8.webp",
}

CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0"}


def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers=UA)
    data = urllib.request.urlopen(req, context=CTX, timeout=60).read()
    dest.write_bytes(data)
    print(f"wrote {dest.name} ({len(data)//1024}KB)")


def main() -> None:
    local_paths = {}
    for key, url in CROPS.items():
        dest = OUT / f"{key}-500x600.webp"
        download(url, dest)
        local_paths[key] = f"/assets/media/carousel-500x600/{key}-500x600.webp"

    # Update homepage carousel in index.html and home/index.html
    for rel in ["index.html", "home/index.html"]:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        original = text
        # Map current storebox / local full images used in hs-car__item to crops
        replacements = [
            (
                r'(<button class="hs-car__item"[^>]*data-caption="DSC02678"[^>]*>\s*<img[^>]+src=")[^"]+(")',
                rf'\1{local_paths["DSC02678"]}\2',
            ),
            (
                r'(<button class="hs-car__item"[^>]*data-caption="DSC02324"[^>]*>\s*<img[^>]+src=")[^"]+(")',
                rf'\1{local_paths["DSC02324"]}\2',
            ),
            (
                r'(<button class="hs-car__item"[^>]*data-caption="DSC02321"[^>]*>\s*<img[^>]+src=")[^"]+(")',
                rf'\1{local_paths["DSC02321"]}\2',
            ),
            (
                r'(<button class="hs-car__item"[^>]*data-caption="Ocean Front King With Balcony"[^>]*>\s*<img[^>]+src=")[^"]+(")',
                rf'\1{local_paths["DSC02774"]}\2',
            ),
            (
                r'(<button class="hs-car__item"[^>]*data-caption="Partial Ocean View Double"[^>]*>\s*<img[^>]+src=")[^"]+(")',
                rf'\1{local_paths["DSC02538"]}\2',
            ),
            (
                r'(<button class="hs-car__item"[^>]*data-caption="Partial Ocean View King"[^>]*>\s*<img[^>]+src=")[^"]+(")',
                rf'\1{local_paths["DSC02445"]}\2',
            ),
        ]
        for pat, repl in replacements:
            text, n = re.subn(pat, repl, text, count=1, flags=re.I)
            print(f"{rel}: {n} replace for {pat[40:80]}...")

        # Also set width/height attrs on carousel imgs for correct intrinsic size
        text = re.sub(
            r'(class="hs-car__item"[^>]*>\s*<img[^>]*?)(?:\s+width="\d+"|\s+height="\d+")*',
            lambda m: m.group(0),  # leave; handled below
            text,
        )
        # Add width/height=500/600 on car item imgs if missing
        def add_wh(m: re.Match) -> str:
            tag = m.group(0)
            if 'width="' in tag and 'height="' in tag:
                tag = re.sub(r'width="\d+"', 'width="500"', tag)
                tag = re.sub(r'height="\d+"', 'height="600"', tag)
                return tag
            return tag[:-1] + ' width="500" height="600">'

        text = re.sub(
            r'<img src="/assets/media/carousel-500x600/[^"]+"[^>]*>',
            add_wh,
            text,
        )

        if text != original:
            path.write_text(text, encoding="utf-8")
            print(f"updated {rel}")
        else:
            print(f"no change {rel}")


if __name__ == "__main__":
    main()
