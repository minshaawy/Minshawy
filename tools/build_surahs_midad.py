#!/usr/bin/env python3
"""Surah pages in the Midad design (paper & ink, light/dark).

    python3 tools/build_surahs_midad.py --base /test   # test/surah/…, noindex
    python3 tools/build_surahs_midad.py                # surah/… (when promoted)

Shares the data (names, verse counts, Makki/Madani) with build_surahs.py.
"""
import argparse
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_surahs import AUDIO, ROOT, SITE, ar_num, ayat_word, load_surahs  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--base", default="", help="URL prefix of the site copy, e.g. /test")
args = ap.parse_args()
BASE = args.base.rstrip("/")
TEST = bool(BASE)
OUT_DIR = os.path.join(ROOT, BASE.strip("/"), "surah") if BASE else os.path.join(ROOT, "surah")

LOGO = open(os.path.join(ROOT, "images", "logo-minshawi.svg"), encoding="utf-8").read()
VB = re.search(r'viewBox="([^"]+)"', LOGO).group(1)
VW, VH = VB.split()[2:]
LOGO_PATHS = LOGO[LOGO.index(">") + 1:LOGO.rindex("</svg>")]
SYMBOL = f'<svg width="0" height="0" style="position:absolute" aria-hidden="true"><symbol id="logo" viewBox="{VB}">{LOGO_PATHS}</symbol></svg>'


def logo(label="الشيخ محمد صديق المنشاوي"):
    return f'<svg class="logo" viewBox="0 0 {VW} {VH}" role="img" aria-label="{label}"><use href="#logo"/></svg>'


CSP = ("default-src 'self'; script-src 'self' 'unsafe-inline' https://static.cloudflareinsights.com; "
       "style-src 'self' 'unsafe-inline'; img-src 'self' data:; media-src https://cdn.mp3quran.net; "
       "connect-src 'self' https://cloudflareinsights.com; font-src 'self';")

DARK = """--bg:#121110;--bg-2:#181614;--card:#1c1a17;--fg:#eee8dd;--fg-2:#d6cfc2;--muted:#a0988b;
  --line:rgba(238,232,221,.12);--line-2:rgba(238,232,221,.26);--accent:#d9644c;--btn:#eee8dd;--btn-fg:#121110;color-scheme:dark"""

STYLE = """
@font-face{font-family:'Thmanyah Sans';src:url('/fonts/thmanyahsans-Regular.woff2') format('woff2');font-weight:400;font-display:swap}
@font-face{font-family:'Thmanyah Sans';src:url('/fonts/thmanyahsans-Medium.woff2') format('woff2');font-weight:500;font-display:swap}
@font-face{font-family:'Thmanyah Serif Text';src:url('/fonts/thmanyahseriftext-Regular.woff2') format('woff2');font-weight:400;font-display:swap}
@font-face{font-family:'Thmanyah Serif Display';src:url('/fonts/thmanyahserifdisplay-Bold.woff2') format('woff2');font-weight:700;font-display:swap}
:root{--bg:#f7f4ee;--bg-2:#efebe2;--card:#fffdf9;--fg:#111;--fg-2:#2b2925;--muted:#6a645a;
  --line:rgba(17,17,17,.12);--line-2:rgba(17,17,17,.26);--accent:#9b2a1a;--btn:#111;--btn-fg:#f7f4ee;color-scheme:only light}
:root[data-theme="dark"]{__DARK__}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){__DARK__}}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Thmanyah Sans',system-ui,sans-serif;background:var(--bg);color:var(--fg);line-height:1.8;-webkit-font-smoothing:antialiased}
body *{letter-spacing:0!important}
a{color:inherit;text-decoration:none}
svg.logo{display:block;height:auto;fill:currentColor}
.wrap{max-width:880px;margin:0 auto;padding:0 clamp(16px,5vw,40px)}
.site-header{position:sticky;top:0;z-index:10;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.site-header .wrap{display:flex;align-items:center;justify-content:space-between;height:64px;gap:16px}
.site-header .logo{height:28px;width:auto}
.site-header nav{display:flex;align-items:center;gap:22px;font-size:.92rem;color:var(--muted)}
.site-header nav a:hover{color:var(--fg)}
.icon-btn{width:32px;height:32px;display:inline-grid;place-items:center;border:1px solid var(--line-2);border-radius:2px;background:transparent;color:var(--fg-2);cursor:pointer}
.icon-btn svg{width:16px;height:16px;fill:currentColor}
.icon-btn .sun{display:none}
:root[data-theme="dark"] .icon-btn .sun{display:block}:root[data-theme="dark"] .icon-btn .moon{display:none}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .icon-btn .sun{display:block}:root:not([data-theme="light"]) .icon-btn .moon{display:none}}
main{padding:36px 0 64px}
.crumbs{font-size:.85rem;color:var(--muted);margin-bottom:22px}
.crumbs a{border-bottom:1px solid var(--line-2)}
.kicker{display:flex;align-items:center;gap:12px;font-size:.9rem;color:var(--accent);margin-bottom:10px}
.kicker::before{content:'';width:28px;height:1px;background:currentColor}
h1{font:700 clamp(2.6rem,9vw,4rem)/1.1 'Thmanyah Serif Display',serif}
.sub{margin-top:10px;font-size:1.05rem;color:var(--fg-2);padding-top:12px;border-top:3px solid var(--fg);display:inline-block}
.sub span{display:block;font-size:.85rem;color:var(--muted);direction:ltr;text-align:right}
.facts{display:flex;flex-wrap:wrap;margin:26px 0 34px;padding:0;list-style:none;border-block:1px solid var(--line)}
.facts li{flex:1;min-width:120px;padding:14px 0;font-size:.85rem;color:var(--muted)}
.facts li b{display:block;font:700 1.35rem 'Thmanyah Serif Display',serif;color:var(--fg)}
.rec{border:1px solid var(--line);background:var(--card);padding:20px;margin-bottom:14px;border-radius:2px}
.rec-head{display:flex;justify-content:space-between;align-items:baseline;gap:12px;margin-bottom:12px}
.rec h2{font:700 1.35rem 'Thmanyah Serif Display',serif}
.rec .dl{font-size:.85rem;color:var(--muted);border-bottom:1px solid var(--line-2)}
.rec .dl:hover{color:var(--fg)}
.rec audio{display:block;width:100%;height:44px}
.about{font:400 1.08rem/2 'Thmanyah Serif Text',serif;color:var(--fg-2);margin:30px 0 22px}
.btn{display:inline-flex;align-items:center;gap:10px;padding:12px 22px;border-radius:2px;font-weight:500;font-size:.95rem;background:var(--btn);color:var(--btn-fg);transition:background .2s}
.btn:hover{background:var(--accent);color:#fff}
.btn svg{width:13px;height:13px;fill:currentColor}
.pager{display:grid;grid-template-columns:1fr 1fr;margin-top:40px;border-top:1px solid var(--fg)}
.pager a{padding:16px 0;font:700 1.15rem 'Thmanyah Serif Display',serif}
.pager a small{display:block;font:400 .8rem 'Thmanyah Sans',sans-serif;color:var(--muted)}
.pager a:hover{color:var(--accent)}
.pager .next{grid-column:2;text-align:left}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(170px,100%),1fr));gap:1px;background:var(--line);border:1px solid var(--line);list-style:none;margin-top:28px}
.grid a{display:flex;align-items:center;gap:12px;padding:14px 16px;background:var(--card);transition:background .15s}
.grid a:hover{background:var(--bg)}
.grid b{font:700 1rem 'Thmanyah Serif Display',serif;color:var(--muted);min-width:2.2ch}
.grid span{font:700 1.1rem 'Thmanyah Serif Display',serif}
.site-footer{border-top:1px solid var(--line);padding:44px 0 52px;text-align:center}
.site-footer .logo{width:120px;margin:0 auto}
.site-footer nav{display:flex;justify-content:center;flex-wrap:wrap;gap:10px 22px;margin-top:20px;font-size:.9rem}
.site-footer nav a{border-bottom:1px solid var(--line-2)}
.site-footer p{color:var(--muted);font-size:.8rem;margin-top:18px}
@media (max-width:640px){
  .site-header nav .hide-sm{display:none}
  .grid{grid-template-columns:repeat(2,minmax(0,1fr))}
  .grid a{min-width:0;overflow-wrap:anywhere}
  .rec{padding:16px}
  .facts li{min-width:0;padding-inline-end:8px}
  .facts li b{font-size:1.15rem}
}
""".replace("__DARK__", DARK)

THEME_HEAD = """<script>(function(){try{var t=localStorage.getItem('theme');if(t==='dark'||t==='light')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();</script>"""

PAGE_JS = """<script>
(function(){
  var root=document.documentElement,btn=document.getElementById('themeToggle'),mq=matchMedia('(prefers-color-scheme: dark)');
  var meta=document.querySelector('meta[name="theme-color"]');
  function dark(){var t=root.getAttribute('data-theme');return t?t==='dark':mq.matches;}
  function sync(){if(meta)meta.setAttribute('content',dark()?'#121110':'#f7f4ee');if(btn)btn.title=dark()?'الوضع النهاري':'الوضع الليلي';}
  if(btn)btn.addEventListener('click',function(){var n=dark()?'light':'dark';root.setAttribute('data-theme',n);try{localStorage.setItem('theme',n)}catch(e){}sync();});
  sync();
  var list=document.querySelectorAll('audio');
  list.forEach(function(a){a.addEventListener('play',function(){
    list.forEach(function(b){if(b!==a)b.pause();});
    if('mediaSession' in navigator&&window.MediaMetadata){navigator.mediaSession.metadata=new MediaMetadata({
      title:a.dataset.title,artist:'الشيخ محمد صديق المنشاوي',album:a.dataset.album,
      artwork:[{src:'/images/icons/icon-512.png',sizes:'512x512',type:'image/png'}]});}
  });});
})();
</script>"""

THEME_BTN = """<button class="icon-btn" id="themeToggle" aria-label="الوضع الليلي" title="الوضع الليلي">
      <svg class="moon" viewBox="0 0 24 24"><path d="M12.3 2a10 10 0 1 0 9.7 12.6A8 8 0 0 1 12.3 2z"/></svg>
      <svg class="sun" viewBox="0 0 24 24"><path d="M12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10zm0-5 1 3h-2zm0 20-1-3h2zM2 12l3-1v2zm20 0-3 1v-2zM4.9 4.9l2.8 1.4-1.4 1.4zm14.2 14.2-2.8-1.4 1.4-1.4zM4.9 19.1l1.4-2.8 1.4 1.4zM19.1 4.9l-1.4 2.8-1.4-1.4z"/></svg>
    </button>"""


def head(title, desc, url, ld):
    e = html.escape
    share_url = url.replace(SITE, SITE + BASE, 1)  # the address actually being shared
    robots = '<meta name="robots" content="noindex, nofollow">' if TEST else ""
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{robots}
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="32x32" href="/images/icons/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/images/icons/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#f7f4ee">
<meta name="color-scheme" content="only light">
<meta property="og:type" content="website">
<meta property="og:locale" content="ar_EG">
<meta property="og:site_name" content="الشيخ محمد صديق المنشاوي · الصوت الباكي">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{share_url}">
<meta property="og:image" content="{SITE}/images/share-card.jpg">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="الشيخ محمد صديق المنشاوي · الصوت الباكي">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}/images/share-card.jpg">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{THEME_HEAD}
<style>{STYLE}</style>
</head>
<body>
{SYMBOL}
<header class="site-header">
  <div class="wrap">
    <a href="{BASE}/" aria-label="الصفحة الرئيسية">{logo()}</a>
    <nav>
      <a class="hide-sm" href="{BASE}/#bio">السيرة</a>
      <a href="{BASE}/surah/">فهرس السور</a>
      <a class="hide-sm" href="{BASE}/#radio">إذاعة القرآن الكريم</a>
      {THEME_BTN}
    </nav>
  </div>
</header>
"""


FOOTER = f"""<footer class="site-footer">
  <div class="wrap">
    {logo()}
    <nav>
      <a href="{BASE}/">الصفحة الرئيسية</a>
      <a href="{BASE}/#bio">سيرة الشيخ</a>
      <a href="{BASE}/surah/">فهرس السور</a>
      <a href="{BASE}/#radio">إذاعة القرآن الكريم</a>
    </nav>
    <p>موقع غير تجاري لنشر تلاوات الشيخ محمد صديق المنشاوي · حقوق التلاوات محفوظة لمالكيها الأصليين.</p>
  </div>
</footer>
{PAGE_JS}
</body>
</html>
"""


def surah_page(s, prev, nxt):
    n, ar, en, slug = s["num"], s["ar"], s["en"], s["slug"]
    url = f"{SITE}/surah/{slug}/"  # canonical always points at the real page
    kind = "مدنية" if s["medinan"] else "مكية"
    ayat = f"{ar_num(s['ayat'])} {ayat_word(s['ayat'])}"
    title = f"سورة {ar} بصوت محمد صديق المنشاوي | مرتل ومجود MP3"
    desc = (f"استمع وحمّل سورة {ar} كاملة بصوت الشيخ محمد صديق المنشاوي، من المصحف المرتل والمجود "
            f"برواية حفص عن عاصم. Surah {en} by Sheikh Muhammad Siddiq Al-Minshawi.")
    m_url, j_url = AUDIO["murattal"] + s["file"], AUDIO["mujawwad"] + s["file"]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "الرئيسية", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "فهرس السور", "item": SITE + "/surah/"},
            {"@type": "ListItem", "position": 3, "name": f"سورة {ar}", "item": url}]},
        {"@type": "AudioObject", "name": f"سورة {ar} - المصحف المرتل - محمد صديق المنشاوي", "contentUrl": m_url,
         "encodingFormat": "audio/mpeg", "inLanguage": "ar", "byArtist": {"@id": SITE + "/#person"}},
        {"@type": "AudioObject", "name": f"سورة {ar} - المصحف المجود - محمد صديق المنشاوي", "contentUrl": j_url,
         "encodingFormat": "audio/mpeg", "inLanguage": "ar", "byArtist": {"@id": SITE + "/#person"}}]}

    def nav(o, cls, label):
        return f'<a class="{cls}" href="{BASE}/surah/{o["slug"]}/"><small>{label}</small>سورة {o["ar"]}</a>' if o else ""

    return head(title, desc, url, ld) + f"""<main>
  <div class="wrap">
    <nav class="crumbs" aria-label="مسار التصفح"><a href="{BASE}/">الرئيسية</a> › <a href="{BASE}/surah/">فهرس السور</a> › سورة {ar}</nav>
    <p class="kicker">بصوت الشيخ محمد صديق المنشاوي</p>
    <h1>سورة {ar}</h1>
    <p class="sub">المصحف المرتل والمجوّد · برواية حفص عن عاصم<span>Surah {html.escape(en)} · Muhammad Siddiq Al-Minshawi</span></p>
    <ul class="facts">
      <li><b>{ar_num(n)}</b>ترتيبها في المصحف</li>
      <li><b>{ayat}</b>عدد آياتها</li>
      <li><b>{kind}</b>نزولها</li>
    </ul>

    <section class="rec">
      <div class="rec-head"><h2>المصحف المرتل</h2><a class="dl" href="{m_url}" rel="nofollow">تحميل MP3</a></div>
      <audio controls preload="none" src="{m_url}" data-title="سورة {ar}" data-album="المصحف المرتل"></audio>
    </section>
    <section class="rec">
      <div class="rec-head"><h2>المصحف المجوّد</h2><a class="dl" href="{j_url}" rel="nofollow">تحميل MP3</a></div>
      <audio controls preload="none" src="{j_url}" data-title="سورة {ar}" data-album="المصحف المجود"></audio>
    </section>

    <p class="about">سورة {ar} هي السورة رقم {ar_num(n)} في ترتيب المصحف الشريف، وهي سورة {kind} عدد آياتها {ayat}.
    تستمع هنا إليها كاملةً بصوت الشيخ محمد صديق المنشاوي، «الصوت الباكي»، مرتلةً ومجوّدة برواية حفص عن عاصم.</p>
    <a class="btn" href="{BASE}/#library"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>استمع إلى المصحف كاملًا</a>

    <nav class="pager" aria-label="السور المجاورة">{nav(prev, "prev", "السورة السابقة")}{nav(nxt, "next", "السورة التالية")}</nav>
  </div>
</main>
""" + FOOTER


def index_page(surahs):
    url = f"{SITE}/surah/"
    title = "فهرس سور القرآن الكريم بصوت محمد صديق المنشاوي | مرتل ومجود"
    desc = ("فهرس الـ ١١٤ سورة بصوت الشيخ محمد صديق المنشاوي. اختر السورة واستمع إليها أو حمّلها "
            "من المصحف المرتل والمجود برواية حفص عن عاصم.")
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "الرئيسية", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "فهرس السور", "item": url}]}
    items = "\n".join(f'      <li><a href="{BASE}/surah/{s["slug"]}/"><b>{ar_num(s["num"])}</b><span>{s["ar"]}</span></a></li>'
                      for s in surahs)
    return head(title, desc, url, ld) + f"""<main>
  <div class="wrap">
    <nav class="crumbs" aria-label="مسار التصفح"><a href="{BASE}/">الرئيسية</a> › فهرس السور</nav>
    <p class="kicker">١١٤ سورة · مرتل ومجوّد</p>
    <h1>فهرس السور</h1>
    <p class="sub">القرآن الكريم كاملًا بصوت الشيخ محمد صديق المنشاوي<span>All 114 surahs · Muhammad Siddiq Al-Minshawi</span></p>
    <ul class="grid">
{items}
    </ul>
  </div>
</main>
""" + FOOTER


def main():
    surahs = load_surahs()
    for i, s in enumerate(surahs):
        d = os.path.join(OUT_DIR, s["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(surah_page(s, surahs[i - 1] if i else None, surahs[i + 1] if i < 113 else None))
    with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_page(surahs))
    print("wrote", OUT_DIR, "(115 pages)")


if __name__ == "__main__":
    main()
