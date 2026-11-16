#!/usr/bin/env python3
"""Build one static page per surah under surah/<slug>/index.html, the
surah index at surah/index.html, and sitemap.xml.

Surah names are read from the `surahs` array in index.html so the site
keeps a single source of truth. Run from the repo root:

    python3 tools/build_surahs.py
"""
import datetime
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.elminshawy.net"
AUDIO = {
    "murattal": "https://cdn.mp3quran.net/audio/muhammad-minshawi/r1/",
    "mujawwad": "https://cdn.mp3quran.net/audio/muhammad-minshawi/r2/",
}

# Verse counts (Hafs, Kufan count) — sums to 6236.
AYAT = [7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111, 43, 52, 99, 128,
        111, 110, 98, 135, 112, 78, 118, 64, 77, 227, 93, 88, 69, 60, 34, 30, 73,
        54, 45, 83, 182, 88, 75, 85, 54, 53, 89, 59, 37, 35, 38, 29, 18, 45, 60,
        49, 62, 55, 78, 96, 29, 22, 24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52,
        44, 28, 28, 20, 56, 40, 31, 50, 40, 46, 42, 29, 19, 36, 25, 22, 17, 19,
        26, 30, 20, 15, 21, 11, 8, 8, 19, 5, 8, 8, 11, 11, 8, 3, 9, 5, 4, 7, 3,
        6, 3, 5, 4, 5, 6]
assert len(AYAT) == 114 and sum(AYAT) == 6236

# Medinan surahs as classified in the Madinah (King Fahd) Mushaf.
MEDINAN = {2, 3, 4, 5, 8, 9, 13, 22, 24, 33, 47, 48, 49, 55, 57, 58, 59, 60, 61,
           62, 63, 64, 65, 66, 76, 98, 99, 110}

AR_DIGITS = "٠١٢٣٤٥٦٧٨٩"


def ar_num(n):
    return "".join(AR_DIGITS[int(d)] for d in str(n))


def ayat_word(n):
    return "آيات" if 3 <= n % 100 <= 10 else "آية"


def slugify(en):
    s = en.lower().replace("'", "").replace("’", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def load_surahs():
    src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    block = re.search(r"const surahs = \[(.*?)\];", src, re.S).group(1)
    items = re.findall(r'\{\s*num:\s*(\d+),\s*ar:\s*"([^"]+)",\s*en:\s*"([^"]+)"\s*\}', block)
    surahs = []
    for num, ar, en in items:
        n = int(num)
        surahs.append({
            "num": n, "ar": ar, "en": en, "slug": slugify(en),
            "ayat": AYAT[n - 1], "medinan": n in MEDINAN,
            "file": f"{n:03d}.mp3",
        })
    assert len(surahs) == 114, len(surahs)
    slugs = [s["slug"] for s in surahs]
    assert len(set(slugs)) == 114, "duplicate slugs"
    return surahs


CSP = ("default-src 'self'; script-src 'self' 'unsafe-inline' https://static.cloudflareinsights.com; "
       "style-src 'self' 'unsafe-inline'; img-src 'self' data:; media-src https://cdn.mp3quran.net; "
       "connect-src 'self' https://cloudflareinsights.com; font-src 'self';")

STYLE = """
@font-face{font-family:'Thmanyah Serif Display';src:url('/fonts/thmanyahserifdisplay-Bold.woff2') format('woff2');font-weight:700;font-display:swap}
@font-face{font-family:'Thmanyah Sans';src:url('/fonts/thmanyahsans-Regular.woff2') format('woff2');font-weight:400;font-display:swap}
@font-face{font-family:'Thmanyah Sans';src:url('/fonts/thmanyahsans-Medium.woff2') format('woff2');font-weight:500;font-display:swap}
:root{--paper:#f4ede0;--paper-warm:#ede2cf;--paper-deep:#e0d2b8;--ink:#2a1f12;--ink-soft:#4a3825;--ochre:#b8763a;--ochre-deep:#8b5524;--gold:#c69749}
*{box-sizing:border-box}
html{color-scheme:light}
body{margin:0;background:var(--paper);color:var(--ink);font-family:'Thmanyah Sans',system-ui,sans-serif;line-height:1.8;-webkit-text-size-adjust:100%}
a{color:var(--ochre-deep)}
.top{background:var(--ink);color:var(--paper)}
.top-in{max-width:880px;margin:0 auto;padding:14px 20px;display:flex;justify-content:space-between;align-items:center;gap:12px}
.top a{color:var(--paper);text-decoration:none;font-weight:500}
.top .brand{font-family:'Thmanyah Serif Display',serif;font-weight:700;font-size:1.1rem}
.top .brand::before{content:'۞';color:var(--gold);margin-inline-end:8px}
main{max-width:880px;margin:0 auto;padding:28px 20px 48px}
.crumbs{font-size:.88rem;color:var(--ink-soft);margin:0 0 18px}
.crumbs a{color:var(--ink-soft)}
h1{font-family:'Thmanyah Serif Display',serif;font-weight:700;font-size:clamp(2.4rem,8vw,3.6rem);line-height:1.15;margin:0}
.sub{margin:6px 0 0;font-size:1.1rem;color:var(--ink-soft)}
.sub span{display:block;font-size:.9rem;opacity:.8;direction:ltr;text-align:right}
.facts{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0 28px;padding:0;list-style:none}
.facts li{background:var(--paper-warm);border:1px solid var(--paper-deep);border-radius:999px;padding:4px 14px;font-size:.92rem}
.rec{background:#fbf7ef;border:1px solid var(--paper-deep);border-radius:14px;padding:18px 20px;margin:0 0 16px;box-shadow:0 6px 18px rgba(42,31,18,.06)}
.rec h2{font-family:'Thmanyah Serif Display',serif;font-weight:700;font-size:1.35rem;margin:0 0 10px}
.rec audio{width:100%;display:block}
.rec .dl{display:inline-block;margin-top:10px;font-size:.92rem}
.about{margin:28px 0;color:var(--ink-soft)}
.pager{display:flex;justify-content:space-between;gap:12px;margin:32px 0 0;padding:18px 0 0;border-top:1px solid var(--paper-deep)}
.pager a{text-decoration:none;font-weight:500}
.pager .next{margin-inline-start:auto;text-align:left}
.pager small{display:block;color:var(--ink-soft);font-weight:400}
.home-cta{display:inline-block;margin-top:8px;background:var(--ink);color:var(--paper);text-decoration:none;border-radius:999px;padding:10px 22px;font-weight:500}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;margin:24px 0 0;padding:0;list-style:none}
.grid a{display:flex;gap:10px;align-items:center;background:#fbf7ef;border:1px solid var(--paper-deep);border-radius:12px;padding:10px 12px;text-decoration:none;color:var(--ink)}
.grid a:hover{border-color:var(--ochre)}
.grid b{font-weight:500;color:var(--ochre-deep);min-width:2.2em}
footer{background:var(--ink);color:var(--paper-deep);font-size:.85rem;text-align:center;padding:24px 20px}
footer a{color:var(--paper)}
"""

HEAD_ICONS = """<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="32x32" href="/images/icons/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/images/icons/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#2a1f12">"""

TOP = """<header class="top"><div class="top-in">
  <a class="brand" href="/">محمد صديق المنشاوي</a>
  <a href="/surah/">فهرس السور</a>
</div></header>"""

FOOTER = """<footer>
  <p>موقع غير تجاري لنشر تلاوات الشيخ محمد صديق المنشاوي · حقوق التلاوات محفوظة لمالكيها الأصليين.</p>
  <p><a href="/">الصفحة الرئيسية</a> · <a href="/#bio">سيرة الشيخ</a> · <a href="/surah/">فهرس السور</a></p>
</footer>"""

# One audio at a time + lock-screen info.
PLAYER_JS = """<script>
(function(){
  var list=document.querySelectorAll('audio');
  list.forEach(function(a){
    a.addEventListener('play',function(){
      list.forEach(function(b){ if(b!==a) b.pause(); });
      if('mediaSession' in navigator && window.MediaMetadata){
        navigator.mediaSession.metadata=new MediaMetadata({
          title:a.dataset.title, artist:'الشيخ محمد صديق المنشاوي',
          album:a.dataset.album,
          artwork:[{src:'/images/icons/icon-512.png',sizes:'512x512',type:'image/png'}]
        });
      }
    });
  });
})();
</script>"""


def page(s, prev, nxt):
    n, ar, en, slug = s["num"], s["ar"], s["en"], s["slug"]
    url = f"{SITE}/surah/{slug}/"
    kind = "مدنية" if s["medinan"] else "مكية"
    ayat = f"{ar_num(s['ayat'])} {ayat_word(s['ayat'])}"
    title = f"سورة {ar} بصوت محمد صديق المنشاوي | مرتل ومجود MP3"
    desc = (f"استمع وحمّل سورة {ar} كاملة بصوت الشيخ محمد صديق المنشاوي، من المصحف المرتل والمجود "
            f"برواية حفص عن عاصم. Surah {en} by Sheikh Muhammad Siddiq Al-Minshawi.")
    m_url = AUDIO["murattal"] + s["file"]
    j_url = AUDIO["mujawwad"] + s["file"]

    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "الرئيسية", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "فهرس السور", "item": SITE + "/surah/"},
                {"@type": "ListItem", "position": 3, "name": f"سورة {ar}", "item": url},
            ]},
            {"@type": "AudioObject", "name": f"سورة {ar} - المصحف المرتل - محمد صديق المنشاوي",
             "contentUrl": m_url, "encodingFormat": "audio/mpeg", "inLanguage": "ar",
             "description": f"تلاوة مرتلة لسورة {ar} بصوت الشيخ محمد صديق المنشاوي برواية حفص عن عاصم.",
             "byArtist": {"@id": SITE + "/#person"}},
            {"@type": "AudioObject", "name": f"سورة {ar} - المصحف المجود - محمد صديق المنشاوي",
             "contentUrl": j_url, "encodingFormat": "audio/mpeg", "inLanguage": "ar",
             "description": f"تلاوة مجودة لسورة {ar} بصوت الشيخ محمد صديق المنشاوي.",
             "byArtist": {"@id": SITE + "/#person"}},
        ],
    }

    def nav(o, cls, label):
        if not o:
            return ""
        return (f'<a class="{cls}" href="/surah/{o["slug"]}/"><small>{label}</small>'
                f'سورة {o["ar"]}</a>')

    e = html.escape
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
{HEAD_ICONS}
<meta property="og:type" content="website">
<meta property="og:locale" content="ar_EG">
<meta property="og:site_name" content="الشيخ محمد صديق المنشاوي · الصوت الباكي">
<meta property="og:title" content="{e(f'سورة {ar} بصوت الشيخ محمد صديق المنشاوي')}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/images/social-thumbnail.jpg">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{STYLE}</style>
</head>
<body>
{TOP}
<main>
  <nav class="crumbs" aria-label="مسار التصفح"><a href="/">الرئيسية</a> › <a href="/surah/">فهرس السور</a> › سورة {ar}</nav>
  <h1>سورة {ar}</h1>
  <p class="sub">بصوت الشيخ محمد صديق المنشاوي<span>Surah {e(en)} · Muhammad Siddiq Al-Minshawi</span></p>
  <ul class="facts">
    <li>رقمها في المصحف: {ar_num(n)}</li>
    <li>عدد آياتها: {ayat}</li>
    <li>سورة {kind}</li>
  </ul>

  <section class="rec">
    <h2>المصحف المرتل</h2>
    <audio controls preload="none" src="{m_url}" data-title="سورة {ar}" data-album="المصحف المرتل"></audio>
    <a class="dl" href="{m_url}" rel="nofollow">تحميل سورة {ar} مرتلة (MP3)</a>
  </section>
  <section class="rec">
    <h2>المصحف المجوّد</h2>
    <audio controls preload="none" src="{j_url}" data-title="سورة {ar}" data-album="المصحف المجود"></audio>
    <a class="dl" href="{j_url}" rel="nofollow">تحميل سورة {ar} مجوّدة (MP3)</a>
  </section>

  <p class="about">سورة {ar} هي السورة رقم {ar_num(n)} في ترتيب المصحف الشريف، وهي سورة {kind} عدد آياتها {ayat}.
  تستمع هنا إليها كاملةً بصوت الشيخ محمد صديق المنشاوي، «الصوت الباكي»، مرتلةً ومجوّدة برواية حفص عن عاصم.</p>
  <a class="home-cta" href="/#library">استمع إلى المصحف كاملًا</a>

  <nav class="pager" aria-label="السور المجاورة">{nav(prev, "prev", "السورة السابقة")}{nav(nxt, "next", "السورة التالية")}</nav>
</main>
{FOOTER}
{PLAYER_JS}
</body>
</html>
"""


def index_page(surahs):
    url = f"{SITE}/surah/"
    title = "فهرس سور القرآن الكريم بصوت محمد صديق المنشاوي | مرتل ومجود"
    desc = ("فهرس الـ ١١٤ سورة بصوت الشيخ محمد صديق المنشاوي. اختر السورة واستمع إليها أو حمّلها "
            "من المصحف المرتل والمجود برواية حفص عن عاصم.")
    items = "\n".join(
        f'    <li><a href="/surah/{s["slug"]}/"><b>{ar_num(s["num"])}</b>سورة {s["ar"]}</a></li>'
        for s in surahs)
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "الرئيسية", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "فهرس السور", "item": url}]}
    e = html.escape
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
{HEAD_ICONS}
<meta property="og:type" content="website">
<meta property="og:locale" content="ar_EG">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/images/social-thumbnail.jpg">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{STYLE}</style>
</head>
<body>
{TOP}
<main>
  <nav class="crumbs" aria-label="مسار التصفح"><a href="/">الرئيسية</a> › فهرس السور</nav>
  <h1>فهرس السور</h1>
  <p class="sub">القرآن الكريم كاملًا بصوت الشيخ محمد صديق المنشاوي، مرتلًا ومجوّدًا</p>
  <ul class="grid">
{items}
  </ul>
</main>
{FOOTER}
</body>
</html>
"""


def sitemap(surahs):
    today = datetime.date.today().isoformat()
    urls = [f"""  <url>
    <loc>{SITE}/</loc>
    <lastmod>{today}</lastmod>
    <image:image>
      <image:loc>{SITE}/images/sheikh-minshawi.jpg</image:loc>
    </image:image>
  </url>""", f"""  <url>
    <loc>{SITE}/surah/</loc>
    <lastmod>{today}</lastmod>
  </url>"""]
    for s in surahs:
        urls.append(f"""  <url>
    <loc>{SITE}/surah/{s['slug']}/</loc>
    <lastmod>{today}</lastmod>
  </url>""")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
            + "\n".join(urls) + "\n</urlset>\n")


def main():
    surahs = load_surahs()
    out = os.path.join(ROOT, "surah")
    for i, s in enumerate(surahs):
        prev = surahs[i - 1] if i > 0 else None
        nxt = surahs[i + 1] if i < len(surahs) - 1 else None
        d = os.path.join(out, s["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(page(s, prev, nxt))
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_page(surahs))
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap(surahs))
    # Slug map for the home page's library links.
    print(json.dumps({s["num"]: s["slug"] for s in surahs}, ensure_ascii=False))


if __name__ == "__main__":
    main()
