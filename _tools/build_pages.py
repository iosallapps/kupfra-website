"""Rewrite the shared head, header and footer of every page, and refuse em or en dashes.

    python3 _tools/build_pages.py

Blocks between <!-- build:NAME --> and <!-- /build:NAME --> are regenerated here.
"""
import json
import os
import re
import sys
import html as htmllib

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://kupfra.com/"
APP_STORE = "https://apps.apple.com/app/id6827716801"
APP_ID = "6827716801"
EMAIL = "iosallapps@gmail.com"
STYLE_VERSION = "20261116s"
FORBIDDEN = ["—", "–", "&mdash;", "&ndash;", "&#8212;", "&#8211;"]

DESC = ("Construction and electrical calculator with a 3D stair designer: cable size, concrete, tiles, roof and more, "
        "with the working shown. Free on iPhone and iPad.")
LASTMOD = "2026-11-15"
ORG = {"@type": "Organization", "name": "Visto Apps", "url": "https://vistoapps.com",
       "founder": {"@type": "Person", "name": "Darius Cirjan"}}

PAGES = {
    "index.html": ("Kupfra: Construction & Electrical Calculator", DESC, ""),
    "support.html": ("Kupfra Support: Unlock, Restore, Units, Contact", "Help with Kupfra: unlock and restore purchases, manage a subscription, "
                     "set units and standards by region, add your logo to client PDFs, and get in touch.", "support.html"),
    "privacy.html": ("Privacy Policy | Kupfra", "How Kupfra handles your data: projects stay on your device, no accounts, and Google and "
                     "RevenueCat handle ads, analytics, crash reports and purchases.", "privacy.html"),
    "terms.html": ("Terms of Use | Kupfra", "The terms for using Kupfra: the free version, ads, subscriptions, the lifetime unlock, "
                   "and why results are estimates, not an electrical or structural sign-off.", "terms.html"),
    "404.html": ("Page not found | Kupfra", "This page does not exist. Go back to Kupfra, the construction and electrical calculator.", None),
}
CRUMBS = {"support.html": "Support", "privacy.html": "Privacy Policy", "terms.html": "Terms of Use"}
SHOTS = ["shot-home", "shot-stair3d", "shot-electrical", "shot-concrete", "shot-cutlist", "shot-pdf", "shot-checks", "shot-cable"]

HEAD = """<meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="apple-itunes-app" content="app-id={app_id}">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta name="theme-color" content="#452424" data-scrolled="#0E0C0B">
    <meta name="color-scheme" content="dark">{canonical}{alternates}
    <meta property="og:type" content="website">
    <meta property="og:locale" content="en_US">
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
    <link rel="preload" href="/fonts/instrument-serif.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
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
                    <p class="footer-maker">Kupfra is made by Visto Apps, the brand of Darius Cirjan. Questions go straight to me: <a href="mailto:{email}">{email}</a>.</p>
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
                        <li><a href="https://vistoapps.com/apps.html">More apps by Visto Apps</a></li>
                    </ul>
                </nav>
            </div>
            <div class="footer-small">
                <p>iPhone, iPad and App Store are trademarks or service marks of Apple Inc. IEC, BS, NEC, DIN and IRC are named only to say which published guidance Kupfra follows. Kupfra is not affiliated with or endorsed by any standards body.</p>
                <p>This website is hosted on GitHub Pages by GitHub, Inc. Contact: <a href="mailto:{email}">{email}</a>.</p>
                <p>&copy; 2026 Visto Apps, the brand of Darius Cirjan. <span class="footer-visto">Made by <a href="https://vistoapps.com">Visto Apps</a>.</span></p>
            </div>
        </div>
    </footer>"""


def render_head(page):
    title, description, path = PAGES[page]
    url = DOMAIN + (path or "")
    canonical = ('\n    <meta name="robots" content="noindex">' if path is None
                 else f'\n    <link rel="canonical" href="{url}">')
    alternates = "" if path is None else (f'\n    <link rel="alternate" hreflang="en" href="{url}">'
                                         f'\n    <link rel="alternate" hreflang="x-default" href="{url}">')
    return HEAD.format(app_id=APP_ID, title=title, description=description, canonical=canonical, alternates=alternates,
                       url=url, domain=DOMAIN, style_version=STYLE_VERSION)



def faq_items(source):
    items = []
    for m in re.finditer(r"<details>\s*<summary>(.*?)</summary>\s*<div class=\"answer\">(.*?)</div>\s*</details>", source, re.S):
        q = htmllib.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
        a = htmllib.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
        items.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}})
    return items


def render_ld(page, source):
    title, description, path = PAGES[page]
    if path is None:
        return ""
    graph = []
    if page == "index.html":
        graph.append({
            "@type": "MobileApplication", "@id": DOMAIN + "#app", "name": "Kupfra",
            "alternateName": "Kupfra Construction Calculator", "description": description,
            "url": DOMAIN, "operatingSystem": "iOS 17.0 or later, iPadOS 17.0 or later",
            "applicationCategory": "UtilitiesApplication", "applicationSubCategory": "Construction and electrical calculators",
            "datePublished": "2026-11-13", "inLanguage": "en", "isAccessibleForFree": True,
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            "downloadUrl": APP_STORE, "installUrl": APP_STORE,
            "image": DOMAIN + "img/app-icon-256.webp",
            "screenshot": [DOMAIN + f"img/{s}-600.webp" for s in SHOTS],
            "author": ORG, "publisher": ORG})
        graph.append({"@type": "WebSite", "@id": DOMAIN + "#site", "name": "Kupfra", "url": DOMAIN, "inLanguage": "en", "publisher": ORG})
        faq = faq_items(source)
        if faq:
            graph.append({"@type": "FAQPage", "mainEntity": faq})
    else:
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Kupfra", "item": DOMAIN},
            {"@type": "ListItem", "position": 2, "name": CRUMBS[page], "item": DOMAIN + path}]})
    data = {"@context": "https://schema.org", "@graph": graph}
    return '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=1) + "\n    </script>"


def sitemap():
    rows = "".join(f"    <url><loc>{DOMAIN + p[2]}</loc><lastmod>{LASTMOD}</lastmod></url>\n"
                   for p in PAGES.values() if p[2] is not None)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + rows + "</urlset>\n")


def replace_block(source, name, body):
    pattern = re.compile(rf"(<!-- build:{name} -->)(.*?)(\s*<!-- /build:{name} -->)", re.S)
    if not pattern.search(source):
        raise SystemExit(f"missing build:{name} block")
    return pattern.sub(lambda m: f"{m.group(1)}\n    {body}{m.group(3)}", source, count=1)


def main():
    for page in PAGES:
        path = os.path.join(SITE, page)
        source = open(path, encoding="utf-8").read()
        source = re.sub(r"\n?\s*<script type=\"application/ld\+json\">.*?</script>", "", source, flags=re.S)
        if "<!-- build:ld -->" not in source:
            source = source.replace("</head>", "    <!-- build:ld -->\n    <!-- /build:ld -->\n</head>", 1)
        source = replace_block(source, "ld", render_ld(page, source))
        source = replace_block(source, "head", render_head(page))
        source = replace_block(source, "header", HEADER.format(app_store=APP_STORE))
        source = replace_block(source, "footer", FOOTER.format(email=EMAIL))
        for dash in FORBIDDEN:
            if dash in source:
                sys.exit(f"{page}: contains a forbidden dash {dash!r}")
        open(path, "w", encoding="utf-8").write(source)
        print("built", page)
    open(os.path.join(SITE, "sitemap.xml"), "w", encoding="utf-8").write(sitemap())


if __name__ == "__main__":
    main()
