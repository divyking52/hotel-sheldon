#!/usr/bin/env python3
"""Strip WordPress/page-builder deps and wire the shared custom footer on every page."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    ROOT / "index.html",
    ROOT / "home" / "index.html",
    ROOT / "accommodations" / "index.html",
    ROOT / "attractions" / "index.html",
    ROOT / "gallery" / "index.html",
    ROOT / "blog" / "index.html",
    ROOT / "contact" / "index.html",
    ROOT / "privacy-policy" / "index.html",
    ROOT / "accessibility-statement" / "index.html",
]

FOOTER_MOUNT = '<div id="site-footer-root"></div>\n'
FOOTER_CSS = '<link rel="stylesheet" href="/css/site-footer.css">\n'
FOOTER_JS = '<script src="/js/site-footer.js" defer></script>\n'

# Remove stylesheet/script tags that load from the original WP install
LINK_WP = re.compile(
    r"<link\b[^>]*href=['\"]https?://hotelsheldon\.com/wp-content/[^'\"]+['\"][^>]*/?>\s*",
    re.I,
)
SCRIPT_WP = re.compile(
    r"<script\b[^>]*src=['\"]https?://hotelsheldon\.com/wp-content/[^'\"]+['\"][^>]*>\s*</script>\s*",
    re.I,
)

# Entire Elementor footer block (and optional wrapping kit div that only contains the footer)
FOOTER_BLOCK = re.compile(
    r"(?:<div class=\"elementor-kit-5 hs-elementor\">\s*)?"
    r"<footer\b[^>]*(?:elementor-location-footer|data-elementor-type=\"footer\")[^>]*>.*?</footer>\s*"
    r"(?:</div>\s*)?",
    re.I | re.S,
)

# Style blocks that only exist to restyle the Elementor footer / embed kit
STYLE_IDS = [
    "footer-white-text",
    "hs-footer-unify",
    "hs-elementor-embed",
    "wpr-lazyload-bg-exclusion",
    "wpr-lazyload-bg-nostyle",
    "elementor-pro-custom-fonts-inline-css",
]


def strip_style_by_id(html: str, style_id: str) -> str:
    return re.sub(
        rf"<style\b[^>]*\bid=['\"]{re.escape(style_id)}['\"][^>]*>.*?</style>\s*",
        "",
        html,
        flags=re.I | re.S,
    )


def ensure_head_assets(html: str) -> str:
    if "/css/site-footer.css" not in html:
        if re.search(r"</head>", html, re.I):
            html = re.sub(r"</head>", FOOTER_CSS + "</head>", html, count=1, flags=re.I)
        else:
            html = FOOTER_CSS + html
    if "/js/site-footer.js" not in html:
        if re.search(r"</body>", html, re.I):
            html = re.sub(r"</body>", FOOTER_JS + "</body>", html, count=1, flags=re.I)
        else:
            html += FOOTER_JS
    return html


def replace_footer(html: str) -> str:
    if FOOTER_BLOCK.search(html):
        html = FOOTER_BLOCK.sub(FOOTER_MOUNT, html, count=1)
    elif 'id="site-footer-root"' not in html:
        # Insert after </main> when possible
        if re.search(r"</main>", html, re.I):
            html = re.sub(r"</main>", "</main>\n" + FOOTER_MOUNT, html, count=1, flags=re.I)
        else:
            html = re.sub(r"</body>", FOOTER_MOUNT + "</body>", html, count=1, flags=re.I)
    return html


def scrub_builder_hooks(html: str) -> str:
    # Neutralize leftover builder class hooks in custom CSS without deleting page layout CSS
    html = html.replace("footer.elementor-location-footer", "footer.site-footer")
    html = html.replace(".elementor-location-footer", ".site-footer")
    html = html.replace("elementor-257", "site-footer-legacy")
    # Keep page content classes for now if present; verification will still flag `elementor`.
    return html


def process(path: Path) -> None:
    html = path.read_text(encoding="utf-8", errors="ignore")
    original = html

    html = LINK_WP.sub("", html)
    html = SCRIPT_WP.sub("", html)
    for sid in STYLE_IDS:
        html = strip_style_by_id(html, sid)

    html = replace_footer(html)
    html = scrub_builder_hooks(html)
    html = ensure_head_assets(html)

    # Drop empty leftover kit wrappers
    html = re.sub(
        r'<div class="elementor-kit-5 hs-elementor">\s*</div>\s*',
        "",
        html,
        flags=re.I,
    )

    if html != original:
        path.write_text(html, encoding="utf-8")
        print(f"updated {path.relative_to(ROOT)}")
    else:
        print(f"unchanged {path.relative_to(ROOT)}")


def main() -> None:
    for p in PAGES:
        if p.exists():
            process(p)
        else:
            print(f"missing {p}")


if __name__ == "__main__":
    main()
