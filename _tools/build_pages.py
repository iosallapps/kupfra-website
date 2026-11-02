"""Rewrite the shared head, header and footer of every page, and refuse em or en dashes.

    python3 _tools/build_pages.py

Blocks between <!-- build:NAME --> and <!-- /build:NAME --> are regenerated here.
"""
import os
import re
import sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://kupfra.com/"
APP_STORE = "https://apps.apple.com/app/id6827716801"
APP_ID = "6827716801"
EMAIL = "iosallapps@icloud.com"
STYLE_VERSION = "2"
FORBIDDEN = ["—", "–", "&mdash;", "&ndash;", "&#8212;", "&#8211;"]

DESC = ("Kupfra is an all-in-one construction and electrical calculator for electricians, builders and DIY: "
        "a 3D stair designer with cut list and client PDF, cable and breaker sizing to IEC 60364, BS 7671 or the NEC, "
        "and concrete, tile, paint and roof calculators. 45 languages.")

PAGES = {
    "index.html": ("Kupfra: Construction & Electrical Calculator", DESC, ""),
    "support.html": ("Help with Kupfra", "Unlock, restore, manage a subscription, units and standards by region, languages, "
                     "your logo on client PDFs, and how to get in touch.", "support.html"),
    "privacy.html": ("Privacy Policy | Kupfra", "How Kupfra handles your data: projects stay on your device, there are no accounts, "
                     "and the free app uses Google and RevenueCat for ads, analytics, crash reports and purchases.", "privacy.html"),
    "terms.html": ("Terms of Use | Kupfra", "The terms for using Kupfra: the free version, ads, weekly and monthly subscriptions, "
                   "the lifetime unlock and the guidance disclaimer.", "terms.html"),
    "404.html": ("Page not found | Kupfra", "This page does not exist. Go back to Kupfra, the construction and electrical calculator.", None),
}

HEAD = """<meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="apple-itunes-app" content="app-id={app_id}">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta name="theme-color" content="#0E0C0B">
    <meta name="color-scheme" content="dark">{canonical}
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Kupfra">
    <meta property="og:url" content="{url}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{domain}og-image.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="The Kupfra app icon next to the words Stairs, cables and concrete, over a lit oak and concrete stair.">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{domain}og-image.png">
    <link rel="icon" href="/favicon.ico" sizes="48x48">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16.png">
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">
    <link rel="preload" href="/fonts/archivo-var.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="stylesheet" href="/styles.css?v={style_version}">
    <script>document.documentElement.classList.add("js")</script>"""

HEADER = """<header class="site-header">
        <div class="wrap bar">
            <a class="brand" href="/" aria-label="Kupfra, home">
                <img src="/img/app-icon-64.webp" srcset="/img/app-icon-64.webp 1x, /img/app-icon-128.webp 2x" width="32" height="32" alt="">
                <span>Kupfra</span>
            </a>
            <nav class="nav" aria-label="Main">
                <ul class="nav-links">
                    <li><a href="/#modules">Modules</a></li>
                    <li><a href="/#calculators">Calculators</a></li>
                    <li><a href="/#stairs">Stairs</a></li>
                    <li><a href="/#price">Free and unlock</a></li>
                    <li><a href="/#questions">Questions</a></li>
                </ul>
            </nav>
            <a class="badge badge-nav" href="{app_store}"><img src="/img/app-store-black-en-us.svg" width="120" height="40" alt="Download Kupfra on the App Store"></a>
        </div>
    </header>"""

FOOTER = """<footer class="site-footer">
        <div class="wrap">
            <div class="footer-top">
                <div>
                    <a class="brand" href="/" aria-label="Kupfra, home">
                        <img src="/img/app-icon-64.webp" srcset="/img/app-icon-64.webp 1x, /img/app-icon-128.webp 2x" width="32" height="32" alt="" loading="lazy" decoding="async">
                        <span>Kupfra</span>
                    </a>
                    <p class="footer-maker">Kupfra is made by Darius Cirjan, one person. Questions go straight to me: <a href="mailto:{email}">{email}</a>.</p>
                </div>
                <nav aria-label="Footer">
                    <ul class="footer-links">
                        <li><a href="/#modules">Modules</a></li>
                        <li><a href="/#calculators">Calculators</a></li>
                        <li><a href="/#price">Free and unlock</a></li>
                        <li><a href="/#questions">Questions</a></li>
                        <li><a href="/support.html">Support</a></li>
                        <li><a href="/privacy.html">Privacy</a></li>
                        <li><a href="/terms.html">Terms</a></li>
                    </ul>
                </nav>
            </div>
            <div class="footer-small">
                <p>iPhone, iPad and App Store are trademarks or service marks of Apple Inc. IEC, BS, NEC, DIN and IRC are named only to say which published guidance Kupfra follows. Kupfra is not affiliated with or endorsed by any standards body.</p>
                <p>This website is hosted on GitHub Pages by GitHub, Inc. Contact: <a href="mailto:{email}">{email}</a>.</p>
                <p>&copy; 2026 Darius Cirjan</p>
            </div>
        </div>
    </footer>"""


def render_head(page):
    title, description, path = PAGES[page]
    url = DOMAIN + (path or "")
    canonical = ('\n    <meta name="robots" content="noindex">' if path is None
                 else f'\n    <link rel="canonical" href="{url}">')
    return HEAD.format(app_id=APP_ID, title=title, description=description, canonical=canonical,
                       url=url, domain=DOMAIN, style_version=STYLE_VERSION)


def replace_block(source, name, body):
    pattern = re.compile(rf"(<!-- build:{name} -->)(.*?)(\s*<!-- /build:{name} -->)", re.S)
    if not pattern.search(source):
        raise SystemExit(f"missing build:{name} block")
    return pattern.sub(lambda m: f"{m.group(1)}\n    {body}{m.group(3)}", source, count=1)


def main():
    for page in PAGES:
        path = os.path.join(SITE, page)
        source = open(path, encoding="utf-8").read()
        source = replace_block(source, "head", render_head(page))
        source = replace_block(source, "header", HEADER.format(app_store=APP_STORE))
        source = replace_block(source, "footer", FOOTER.format(email=EMAIL))
        for dash in FORBIDDEN:
            if dash in source:
                sys.exit(f"{page}: contains a forbidden dash {dash!r}")
        open(path, "w", encoding="utf-8").write(source)
        print("built", page)


if __name__ == "__main__":
    main()
