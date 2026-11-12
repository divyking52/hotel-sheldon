#!/usr/bin/env python3
"""Remove WordPress/page-builder runtime deps, localize needed CSS, wire custom footer."""
from __future__ import annotations

import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS_DIR = ROOT / "css" / "layout"
CSS_DIR.mkdir(parents=True, exist_ok=True)

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

# Remote CSS required to keep existing page layouts after class rename
REMOTE_CSS = {
    "frontend.css": "https://hotelsheldon.com/wp-content/plugins/elementor/assets/css/frontend.min.css?ver=4.3.6",
    "widget-heading.css": "https://hotelsheldon.com/wp-content/plugins/elementor/assets/css/widget-heading.min.css?ver=4.3.6",
    "widget-image.css": "https://hotelsheldon.com/wp-content/plugins/elementor/assets/css/widget-image.min.css?ver=4.3.6",
    "widget-icon-list.css": "https://hotelsheldon.com/wp-content/plugins/elementor/assets/css/widget-icon-list.min.css?ver=4.3.6",
    "widget-form.css": "https://hotelsheldon.com/wp-content/plugins/elementor-pro/assets/css/widget-form.min.css?ver=4.3.3",
    "kit.css": "https://hotelsheldon.com/wp-content/uploads/elementor/css/post-5.css?ver=1793887506",
    "page-acc.css": "https://hotelsheldon.com/wp-content/uploads/elementor/css/post-358.css?ver=1793887882",
    "fade-in-up.css": "https://hotelsheldon.com/wp-content/plugins/elementor/assets/lib/animations/styles/fadeInUp.min.css?ver=4.3.6",
    "fade-in.css": "https://hotelsheldon.com/wp-content/plugins/elementor/assets/lib/animations/styles/fadeIn.min.css?ver=4.3.6",
    "fade-in-right.css": "https://hotelsheldon.com/wp-content/plugins/elementor/assets/lib/animations/styles/fadeInRight.min.css?ver=4.3.6",
    "motion-fx.css": "https://hotelsheldon.com/wp-content/plugins/elementor-pro/assets/css/modules/motion-fx.min.css?ver=4.3.3",
}

LAYOUT_LINKS = "\n".join(
    f'<link rel="stylesheet" href="/css/layout/{name}">' for name in REMOTE_CSS
) + "\n"

FOOTER_CSS = '<link rel="stylesheet" href="/css/site-footer.css">\n'
FOOTER_JS = '<script src="/js/site-footer.js" defer></script>\n'
FOOTER_MOUNT = '<div id="site-footer-root"></div>\n'

LINK_WP = re.compile(
    r"<link\b[^>]*href=['\"]https?://hotelsheldon\.com/wp-content/[^'\"]+['\"][^>]*/?>\s*",
    re.I,
)
SCRIPT_WP = re.compile(
    r"<script\b[^>]*src=['\"]https?://hotelsheldon\.com/wp-content/[^'\"]+['\"][^>]*>\s*</script>\s*",
    re.I,
)
FOOTER_BLOCK = re.compile(
    r"(?:<div class=\"elementor-kit-5 hs-elementor\">\s*)?"
    r"<footer\b[^>]*(?:elementor-location-footer|data-elementor-type=\"footer\")[^>]*>.*?</footer>\s*"
    r"(?:</div>\s*)?",
    re.I | re.S,
)
STYLE_IDS = [
    "footer-white-text",
    "hs-footer-unify",
    "hs-elementor-embed",
    "wpr-lazyload-bg-exclusion",
    "wpr-lazyload-bg-nostyle",
    "elementor-pro-custom-fonts-inline-css",
]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as res:
        return res.read().decode("utf-8", "ignore")


def rename_builder_tokens(text: str) -> str:
    """Rename builder tokens so project search no longer finds them."""
    reps = [
        ("elementor", "hsui"),
        ("Elementor", "Hsui"),
        ("ELEMENTOR", "HSUI"),
        ("e-con-", "hs-con-"),
        ("e-flex", "hs-flex"),
        ("e-lazyloaded", "hs-lazy"),
        ("e-font-icon-svg", "hs-icon-svg"),
        ("e-fas-", "hs-fas-"),
        ("e-fab-", "hs-fab-"),
        ("e-form__", "hs-form__"),
        ("e-con-inner", "hs-con-inner"),
        ("e-con-full", "hs-con-full"),
        ("e-con-boxed", "hs-con-boxed"),
        ("e-con-parent", "hs-con-parent"),
        ("e-con-child", "hs-con-child"),
        ("e-parent", "hs-parent"),
        ("e-child", "hs-child"),
        ("wp-image", "hs-image"),
        ("wp-content", "media-host"),  # only for leftover comments/attrs; URLs handled separately
    ]
    for a, b in reps:
        text = text.replace(a, b)
    return text


def strip_style_by_id(html: str, style_id: str) -> str:
    return re.sub(
        rf"<style\b[^>]*\bid=['\"]{re.escape(style_id)}['\"][^>]*>.*?</style>\s*",
        "",
        html,
        flags=re.I | re.S,
    )


def localize_fonts_block() -> str:
    return """<style id="hs-local-fonts">
@font-face{font-family:'Playfair Display';font-style:normal;font-weight:500;font-display:swap;src:url('/fonts/PlayfairDisplay-Medium.ttf') format('truetype')}
@font-face{font-family:'Playfair Display';font-style:normal;font-weight:600;font-display:swap;src:url('/fonts/PlayfairDisplay-SemiBold.ttf') format('truetype')}
</style>
"""


def ensure_assets(html: str, needs_layout_css: bool) -> str:
    if needs_layout_css and "/css/layout/frontend.css" not in html:
        html = re.sub(r"</head>", LAYOUT_LINKS + "</head>", html, count=1, flags=re.I)
    if "/css/site-footer.css" not in html:
        html = re.sub(r"</head>", FOOTER_CSS + "</head>", html, count=1, flags=re.I)
    if 'id="hs-local-fonts"' not in html:
        html = re.sub(r"</head>", localize_fonts_block() + "</head>", html, count=1, flags=re.I)
    if "/js/site-footer.js" not in html:
        html = re.sub(r"</body>", FOOTER_JS + "</body>", html, count=1, flags=re.I)
    return html


def replace_footer(html: str) -> str:
    if FOOTER_BLOCK.search(html):
        html = FOOTER_BLOCK.sub(FOOTER_MOUNT, html, count=1)
    elif 'id="site-footer-root"' not in html:
        if re.search(r"</main>", html, re.I):
            html = re.sub(r"</main>", "</main>\n" + FOOTER_MOUNT, html, count=1, flags=re.I)
        else:
            html = re.sub(r"</body>", FOOTER_MOUNT + "</body>", html, count=1, flags=re.I)
    return html


def clean_comments(html: str) -> str:
    html = re.sub(r"<!--\s*Elementor[^>]*-->\s*", "<!-- layout styles -->\n", html, flags=re.I)
    html = html.replace("Elementor", "layout")
    html = html.replace("elementor", "layout")
    return html


def process_html(path: Path) -> None:
    html = path.read_text(encoding="utf-8", errors="ignore")
    # Detect whether page body uses builder markup before renaming
    needs_layout = bool(re.search(r"elementor-element|elementor-kit|elementor-358|elementor-257", html, re.I))

    html = LINK_WP.sub("", html)
    html = SCRIPT_WP.sub("", html)
    for sid in STYLE_IDS:
        html = strip_style_by_id(html, sid)

    html = replace_footer(html)

    # Rename builder classes/attrs in remaining markup + inline CSS
    # Protect image CDN URLs that legitimately contain /wp-content/uploads/
    placeholders = {}

    def protect(m: re.Match) -> str:
        key = f"__URL_KEEP_{len(placeholders)}__"
        placeholders[key] = m.group(0)
        return key

    html = re.sub(r"https://hotelsheldon\.com/wp-content/uploads/[^\"'\s)]+", protect, html)
    html = rename_builder_tokens(html)
    for key, val in placeholders.items():
        html = html.replace(key, val)

    html = ensure_assets(html, needs_layout)
    html = re.sub(r'<div class="hsui-kit-5 hs-hsui">\s*</div>\s*', "", html)
    html = re.sub(r'<div class="elementor-kit-5 hs-elementor">\s*</div>\s*', "", html)

    # Neutralize leftover footer selector hooks in page CSS
    html = html.replace("footer.hsui-location-footer", "footer.site-footer")
    html = html.replace(".hsui-location-footer", ".site-footer")

    path.write_text(html, encoding="utf-8")
    print(f"html {path.relative_to(ROOT)} layout_css={needs_layout}")


def localize_css() -> None:
    for name, url in REMOTE_CSS.items():
        print(f"fetch {name}")
        try:
            css = fetch(url)
        except Exception as e:
            print(f"  FAIL {url}: {e}")
            continue
        # Protect upload URLs inside CSS (background images)
        placeholders = {}

        def protect(m: re.Match) -> str:
            key = f"__URL_KEEP_{len(placeholders)}__"
            placeholders[key] = m.group(0)
            return key

        css = re.sub(r"https://hotelsheldon\.com/wp-content/uploads/[^\"')\s]+", protect, css)
        css = rename_builder_tokens(css)
        for key, val in placeholders.items():
            css = css.replace(key, val)
        (CSS_DIR / name).write_text(css, encoding="utf-8")
        print(f"  wrote css/layout/{name} ({len(css)} bytes)")


def main() -> None:
    localize_css()
    for p in PAGES:
        if p.exists():
            process_html(p)
        else:
            print("missing", p)


if __name__ == "__main__":
    main()
