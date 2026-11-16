#!/usr/bin/env python3
"""English home page (/en/) from the built Arabic page. Used by build_midad.py.

index.html already holds both languages (.lang-ar / .lang-en-text spans) and
switches between them with JavaScript. This gives the English version its own
address (/en/) so it can be shared, bookmarked and indexed: same page, with
English set as the starting language and English titles and meta tags.

Run from the repo root after editing index.html (build_surahs.py runs it too,
and the deploy workflow runs it before publishing):

    python3 tools/build_en_home.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.elminshawy.net"

TITLE = "Sheikh Muhammad Siddiq Al-Minshawi | Complete Murattal & Mujawwad Quran · The Weeping Voice"
SHORT_TITLE = "Sheikh Muhammad Siddiq Al-Minshawi · The Weeping Voice"
DESC = ("A tribute to Sheikh Muhammad Siddiq Al-Minshawi, one of the great Egyptian Quran reciters: "
        "his biography and the complete murattal and mujawwad Quran in his voice, plus live Quran radio from Cairo.")


def swap(src, old, new, count=1, optional=False):
    found = src.count(old)
    if optional and found == 0:
        return src
    if found != count:
        raise SystemExit(f"build_en_home: expected {count}× {old[:70]!r} in index.html, found {found}")
    return src.replace(old, new)


def attr_value(src, prefix):
    """Return the full tag that starts with `prefix` (e.g. '<meta name="description"')."""
    start = src.index(prefix)
    return src[start:src.index(">", start) + 1]


def build(src, base=""):
    """base: URL prefix if the site is ever built under a sub-path; "" for the real site."""
    s = swap(src, '<html lang="ar" dir="rtl">', '<html lang="en" dir="ltr">')
    s = swap(s, '<body>\n', '<body class="lang-en">\n')

    # <head>: title, description, canonical, social cards
    s = swap(s, s[s.index("<title>"):s.index("</title>") + 8], f"<title>{TITLE}</title>")
    for prefix, new in [
        ('<meta name="description"', f'<meta name="description" content="{DESC}">'),
        ('<link rel="canonical"', f'<link rel="canonical" href="{SITE}/en/">'),
        ('<meta name="apple-mobile-web-app-title"', '<meta name="apple-mobile-web-app-title" content="Al-Minshawi">'),
        ('<meta name="application-name"', '<meta name="application-name" content="Al-Minshawi">'),
        ('<meta property="og:site_name"', f'<meta property="og:site_name" content="{SHORT_TITLE}">'),
        ('<meta property="og:locale" ', '<meta property="og:locale" content="en_US">'),
        ('<meta property="og:locale:alternate"', '<meta property="og:locale:alternate" content="ar_EG">'),
        ('<meta property="og:title"', f'<meta property="og:title" content="{SHORT_TITLE}">'),
        ('<meta property="og:description"', f'<meta property="og:description" content="{DESC}">'),
        ('<meta property="og:url"', f'<meta property="og:url" content="{SITE}{base}/en/">'),
        ('<meta name="twitter:title"', f'<meta name="twitter:title" content="{SHORT_TITLE}">'),
        ('<meta name="twitter:description"', f'<meta name="twitter:description" content="{DESC}">'),
        ('<meta property="og:image:alt"', f'<meta property="og:image:alt" content="{SHORT_TITLE}">'),
    ]:
        if prefix in s:
            s = swap(s, attr_value(s, prefix), new)

    # Structured data: describe this English page too
    webpage = {"@type": "WebPage", "@id": f"{SITE}/en/#webpage", "url": f"{SITE}/en/",
               "name": TITLE, "description": DESC, "inLanguage": "en",
               "isPartOf": {"@id": f"{SITE}/#website"}, "about": {"@id": f"{SITE}/#person"}}
    s = swap(s, '"@graph": [\n', '"@graph": [\n    ' + json.dumps(webpage, ensure_ascii=False) + ',\n')

    # Text set before the script runs
    s = swap(s, 'placeholder="ابحث عن سورة..."', 'placeholder="Search surah..."')
    s = swap(s, '<button class="lang-toggle" id="langToggle">EN</button>',
             '<button class="lang-toggle" id="langToggle" lang="ar">عربي</button>')
    s = swap(s, f'<a href="{base}/surah/" data-href-ar="{base}/surah/"',
             f'<a href="{base}/en/surah/" data-href-ar="{base}/surah/"')
    return swap(s, "<!DOCTYPE html>\n", "<!DOCTYPE html>\n"
                "<!-- Generated from index.html by tools/build_en_home.py: edit index.html, not this file. -->\n")


def main():
    """Rebuild en/index.html from the current index.html (build_midad.py normally does this)."""
    src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    out = os.path.join(ROOT, "en")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(build(src))


if __name__ == "__main__":
    main()
