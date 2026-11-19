#!/usr/bin/env python3
"""Surah pages in the Midad design (paper & ink, light/dark).

    python3 tools/build_surahs_midad.py   # surah/…, en/surah/…, 404.html, sitemap.xml

Builds Arabic (/surah/…) and English (/en/surah/…) pages.
Shares the data (names, verse counts, Makki/Madani) with build_surahs.py.
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_surahs import AUDIO, ROOT, SITE, ar_num, ayat_word, load_surahs, sitemap  # noqa: E402

OUT_DIR = os.path.join(ROOT, "surah")            # Arabic: /surah/…
OUT_DIR_EN = os.path.join(ROOT, "en", "surah")   # English: /en/surah/…

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
h1{font:700 clamp(2.2rem,9vw,4rem)/1.1 'Thmanyah Serif Display',serif;overflow-wrap:anywhere}
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
.rec.is-from{border-color:var(--accent)}
.from-t{margin-top:10px;font-size:.85rem;color:var(--accent)}
.about{font:400 1.08rem/2 'Thmanyah Serif Text',serif;color:var(--fg-2);margin:30px 0 22px}
.btn{display:inline-flex;align-items:center;gap:10px;padding:12px 22px;border-radius:2px;font-weight:500;font-size:.95rem;background:var(--btn);color:var(--btn-fg);transition:background .2s}
.btn:hover{background:var(--accent);color:#fff}
.nf{text-align:center;padding-top:24px;padding-bottom:40px}.nf .sub{margin-inline:auto}.nf .kicker{justify-content:center}
.nf-links{display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:12px 22px;margin-top:28px}
.nf-en{margin-top:36px;opacity:.75;font-size:.95rem}
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
.lang-link{border:1px solid var(--line-2);border-radius:2px;padding:2px 10px;font-size:.85rem;color:var(--fg-2)}
.lang-link:hover{border-color:var(--fg)}
html[dir=ltr] .sub span{text-align:left}
html[dir=ltr] .pager .next{text-align:right}
@media (max-width:640px){
  .site-header nav{gap:14px}
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
  var meta=document.querySelector('meta[name="theme-color"]'),en=root.lang==='en';
  function dark(){var t=root.getAttribute('data-theme');return t?t==='dark':mq.matches;}
  function sync(){if(meta)meta.setAttribute('content',dark()?'#121110':'#f7f4ee');
    if(btn){var l=dark()?(en?'Light mode':'الوضع النهاري'):(en?'Dark mode':'الوضع الليلي');btn.title=l;btn.setAttribute('aria-label',l);}}
  if(btn)btn.addEventListener('click',function(){var n=dark()?'light':'dark';root.setAttribute('data-theme',n);try{localStorage.setItem('theme',n)}catch(e){}sync();});
  sync();
  // Following the language link remembers the choice for the home page
  document.querySelectorAll('.lang-link').forEach(function(a){a.addEventListener('click',function(){
    try{localStorage.setItem('lang',a.getAttribute('hreflang'));}catch(e){}});});
  var list=document.querySelectorAll('audio');
  list.forEach(function(a){a.addEventListener('play',function(){
    list.forEach(function(b){if(b!==a)b.pause();});
    if('mediaSession' in navigator&&window.MediaMetadata){navigator.mediaSession.metadata=new MediaMetadata({
      title:a.dataset.title,artist:en?'Sheikh Muhammad Siddiq Al-Minshawi':'الشيخ محمد صديق المنشاوي',album:a.dataset.album,
      artwork:[{src:'/images/icons/icon-512.png',sizes:'512x512',type:'image/png'}]});}
  });});
  // A shared link can start a recitation part-way: ?t=754 or ?t=12:34 (and &r=2 for the mujawwad)
  var q=new URLSearchParams(location.search),sec=(q.get('t')||'').split(':').reduce(function(x,y){return x*60+(+y||0);},0),a=list[q.get('r')==='2'?1:0];
  if(a&&sec>0){
    a.src=a.getAttribute('src').split('#')[0]+'#t='+sec;a.preload='metadata';
    a.addEventListener('loadedmetadata',function f(){a.removeEventListener('loadedmetadata',f);if(a.currentTime<1)a.currentTime=sec;});
    var h=Math.floor(sec/3600),m=Math.floor(sec/60)%60,lbl=(h?h+':'+('0'+m).slice(-2):m)+':'+('0'+sec%60).slice(-2);
    if(!en)lbl=lbl.replace(/\d/g,function(d){return '٠١٢٣٤٥٦٧٨٩'[d];});
    var n=document.createElement('p');n.className='from-t';n.textContent=en?'This link starts at '+lbl:'الرابط يبدأ من '+lbl;
    a.after(n);var box=a.closest('.rec');box.classList.add('is-from');setTimeout(function(){box.scrollIntoView({block:'center'});},60);
  }
})();
</script>"""

THEME_ICONS = """<svg class="moon" viewBox="0 0 24 24"><path d="M12.3 2a10 10 0 1 0 9.7 12.6A8 8 0 0 1 12.3 2z"/></svg>
      <svg class="sun" viewBox="0 0 24 24"><path d="M12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10zm0-5 1 3h-2zm0 20-1-3h2zM2 12l3-1v2zm20 0-3 1v-2zM4.9 4.9l2.8 1.4-1.4 1.4zm14.2 14.2-2.8-1.4 1.4-1.4zM4.9 19.1l1.4-2.8 1.4 1.4zM19.1 4.9l-1.4 2.8-1.4-1.4z"/></svg>"""

# Interface text per language. Page addresses: Arabic under <base>/, English under <base>/en/.
T = {
    "ar": {"dir": "rtl", "locale": "ar_EG", "home": f"/", "index": f"/surah/",
           "site": "الشيخ محمد صديق المنشاوي · الصوت الباكي", "logo": "الشيخ محمد صديق المنشاوي",
           "home_label": "الصفحة الرئيسية", "crumb_home": "الرئيسية", "crumbs": "مسار التصفح",
           "bio": "السيرة", "bio_long": "سيرة الشيخ", "all": "فهرس السور", "radio": "إذاعة القرآن الكريم",
           "dark": "الوضع الليلي", "other": "English", "other_lang": "en",
           "footer": "موقع غير تجاري لنشر تلاوات الشيخ محمد صديق المنشاوي · حقوق التلاوات محفوظة لمالكيها الأصليين."},
    "en": {"dir": "ltr", "locale": "en_US", "home": f"/en/", "index": f"/en/surah/",
           "site": "Sheikh Muhammad Siddiq Al-Minshawi · The Weeping Voice", "logo": "Sheikh Muhammad Siddiq Al-Minshawi",
           "home_label": "Home", "crumb_home": "Home", "crumbs": "Breadcrumb",
           "bio": "Biography", "bio_long": "Biography", "all": "All surahs", "radio": "Quran Radio",
           "dark": "Dark mode", "other": "العربية", "other_lang": "ar",
           "footer": "A non-commercial site sharing the recitations of Sheikh Muhammad Siddiq Al-Minshawi · Recordings are copyrighted to their owners."},
}


def head(lang, title, desc, url, ld, other_path, ar_url, en_url):
    """other_path: the same page in the other language, inside this site copy."""
    t, e = T[lang], html.escape
    return f"""<!DOCTYPE html>
<html lang="{lang}" dir="{t['dir']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="ar" href="{ar_url}">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="x-default" href="{ar_url}">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="32x32" href="/images/icons/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/images/icons/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#f7f4ee">
<meta name="color-scheme" content="only light">
<meta property="og:type" content="website">
<meta property="og:locale" content="{t['locale']}">
<meta property="og:site_name" content="{e(t['site'])}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/images/og-minshawi.jpg">
<meta property="og:image:secure_url" content="{SITE}/images/og-minshawi.jpg">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(t['site'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}/images/og-minshawi.jpg">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{THEME_HEAD}
<style>{STYLE}</style>
</head>
<body>
{SYMBOL}
<header class="site-header">
  <div class="wrap">
    <a href="{t['home']}" aria-label="{t['home_label']}">{logo(t['logo'])}</a>
    <nav>
      <a class="hide-sm" href="{t['home']}#bio">{t['bio']}</a>
      <a href="{t['index']}">{t['all']}</a>
      <a class="hide-sm" href="{t['home']}#radio">{t['radio']}</a>
      <a class="lang-link" href="{other_path}" hreflang="{t['other_lang']}" lang="{t['other_lang']}">{t['other']}</a>
      <button class="icon-btn" id="themeToggle" aria-label="{t['dark']}" title="{t['dark']}">
      {THEME_ICONS}
    </button>
    </nav>
  </div>
</header>
"""


def footer(lang):
    t = T[lang]
    return f"""<footer class="site-footer">
  <div class="wrap">
    {logo(t['logo'])}
    <nav>
      <a href="{t['home']}">{t['home_label']}</a>
      <a href="{t['home']}#bio">{t['bio_long']}</a>
      <a href="{t['index']}">{t['all']}</a>
      <a href="{t['home']}#radio">{t['radio']}</a>
    </nav>
    <p>{t['footer']}</p>
  </div>
</footer>
{PAGE_JS}
</body>
</html>
"""


def surah_page(s, prev, nxt):
    n, ar, en, slug = s["num"], s["ar"], s["en"], s["slug"]
    url = f"{SITE}/surah/{slug}/"  # canonical always points at the real page
    en_url = f"{SITE}/en/surah/{slug}/"
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
        return f'<a class="{cls}" href="/surah/{o["slug"]}/"><small>{label}</small>سورة {o["ar"]}</a>' if o else ""

    return head("ar", title, desc, url, ld, f"/en/surah/{slug}/", url, en_url) + f"""<main>
  <div class="wrap">
    <nav class="crumbs" aria-label="مسار التصفح"><a href="/">الرئيسية</a> › <a href="/surah/">فهرس السور</a> › سورة {ar}</nav>
    <p class="kicker">بصوت الشيخ محمد صديق المنشاوي</p>
    <h1>سورة {ar}</h1>
    <p class="sub">المصحف المرتل والمجوّد · برواية حفص عن عاصم<span lang="en" dir="ltr">Surah {html.escape(en)} · Muhammad Siddiq Al-Minshawi</span></p>
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
    <a class="btn" href="/#library"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>استمع إلى المصحف كاملًا</a>

    <nav class="pager" aria-label="السور المجاورة">{nav(prev, "prev", "السورة السابقة")}{nav(nxt, "next", "السورة التالية")}</nav>
  </div>
</main>
""" + footer("ar")


def surah_page_en(s, prev, nxt):
    n, ar, en, slug = s["num"], s["ar"], s["en"], s["slug"]
    url = f"{SITE}/en/surah/{slug}/"
    ar_url = f"{SITE}/surah/{slug}/"
    kind = "Medinan" if s["medinan"] else "Meccan"
    e = html.escape
    title = f"Surah {en} by Sheikh Muhammad Siddiq Al-Minshawi | Murattal & Mujawwad MP3"
    desc = (f"Listen to and download Surah {en} (سورة {ar}) recited by Sheikh Muhammad Siddiq Al-Minshawi: "
            f"the complete murattal and mujawwad recitations, Hafs from 'Asim. Free MP3.")
    m_url, j_url = AUDIO["murattal"] + s["file"], AUDIO["mujawwad"] + s["file"]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/en/"},
            {"@type": "ListItem", "position": 2, "name": "All surahs", "item": SITE + "/en/surah/"},
            {"@type": "ListItem", "position": 3, "name": f"Surah {en}", "item": url}]},
        {"@type": "AudioObject", "name": f"Surah {en} - Murattal - Muhammad Siddiq Al-Minshawi", "contentUrl": m_url,
         "encodingFormat": "audio/mpeg", "inLanguage": "ar", "byArtist": {"@id": SITE + "/#person"}},
        {"@type": "AudioObject", "name": f"Surah {en} - Mujawwad - Muhammad Siddiq Al-Minshawi", "contentUrl": j_url,
         "encodingFormat": "audio/mpeg", "inLanguage": "ar", "byArtist": {"@id": SITE + "/#person"}}]}

    def nav(o, cls, label):
        return f'<a class="{cls}" href="/en/surah/{o["slug"]}/"><small>{label}</small>Surah {e(o["en"])}</a>' if o else ""

    return head("en", title, desc, url, ld, f"/surah/{slug}/", ar_url, url) + f"""<main>
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/en/">Home</a> › <a href="/en/surah/">All surahs</a> › Surah {e(en)}</nav>
    <p class="kicker">Recited by Sheikh Muhammad Siddiq Al-Minshawi</p>
    <h1>Surah {e(en)}</h1>
    <p class="sub">Murattal &amp; mujawwad · Hafs from 'Asim<span lang="ar" dir="rtl">سورة {ar} · الشيخ محمد صديق المنشاوي</span></p>
    <ul class="facts">
      <li><b>{n}</b>Order in the Mushaf</li>
      <li><b>{s['ayat']}</b>Verses</li>
      <li><b>{kind}</b>Revealed in</li>
    </ul>

    <section class="rec">
      <div class="rec-head"><h2>Murattal</h2><a class="dl" href="{m_url}" rel="nofollow">Download MP3</a></div>
      <audio controls preload="none" src="{m_url}" data-title="Surah {e(en)}" data-album="Murattal"></audio>
    </section>
    <section class="rec">
      <div class="rec-head"><h2>Mujawwad</h2><a class="dl" href="{j_url}" rel="nofollow">Download MP3</a></div>
      <audio controls preload="none" src="{j_url}" data-title="Surah {e(en)}" data-album="Mujawwad"></audio>
    </section>

    <p class="about">Surah {e(en)} (<span lang="ar" dir="rtl">سورة {ar}</span>) is surah {n} of the Holy Quran, a {kind} surah of {s['ayat']} verses.
    Listen to it here in full, recited by Sheikh Muhammad Siddiq Al-Minshawi, “the Weeping Voice”, in both the murattal and mujawwad styles, Hafs from 'Asim.</p>
    <a class="btn" href="/en/#library"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>Listen to the complete Quran</a>

    <nav class="pager" aria-label="Neighbouring surahs">{nav(prev, "prev", "Previous surah")}{nav(nxt, "next", "Next surah")}</nav>
  </div>
</main>
""" + footer("en")


def index_page(surahs):
    url = f"{SITE}/surah/"
    title = "فهرس سور القرآن الكريم بصوت محمد صديق المنشاوي | مرتل ومجود"
    desc = ("فهرس الـ ١١٤ سورة بصوت الشيخ محمد صديق المنشاوي. اختر السورة واستمع إليها أو حمّلها "
            "من المصحف المرتل والمجود برواية حفص عن عاصم.")
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "الرئيسية", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "فهرس السور", "item": url}]}
    items = "\n".join(f'      <li><a href="/surah/{s["slug"]}/"><b>{ar_num(s["num"])}</b><span>{s["ar"]}</span></a></li>'
                      for s in surahs)
    return head("ar", title, desc, url, ld, f"/en/surah/", url, f"{SITE}/en/surah/") + f"""<main>
  <div class="wrap">
    <nav class="crumbs" aria-label="مسار التصفح"><a href="/">الرئيسية</a> › فهرس السور</nav>
    <p class="kicker">١١٤ سورة · مرتل ومجوّد</p>
    <h1>فهرس السور</h1>
    <p class="sub">القرآن الكريم كاملًا بصوت الشيخ محمد صديق المنشاوي<span lang="en" dir="ltr">All 114 surahs · Muhammad Siddiq Al-Minshawi</span></p>
    <ul class="grid">
{items}
    </ul>
  </div>
</main>
""" + footer("ar")


def index_page_en(surahs):
    url = f"{SITE}/en/surah/"
    title = "All 114 surahs recited by Sheikh Muhammad Siddiq Al-Minshawi | Murattal & Mujawwad MP3"
    desc = ("The complete Quran recited by Sheikh Muhammad Siddiq Al-Minshawi. Pick a surah to listen to or download "
            "the murattal and mujawwad recitations, Hafs from 'Asim.")
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/en/"},
        {"@type": "ListItem", "position": 2, "name": "All surahs", "item": url}]}
    items = "\n".join(f'      <li><a href="/en/surah/{s["slug"]}/"><b>{s["num"]}</b><span>{html.escape(s["en"])}</span></a></li>'
                      for s in surahs)
    return head("en", title, desc, url, ld, f"/surah/", f"{SITE}/surah/", url) + f"""<main>
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/en/">Home</a> › All surahs</nav>
    <p class="kicker">114 surahs · murattal &amp; mujawwad</p>
    <h1>All surahs</h1>
    <p class="sub">The complete Quran recited by Sheikh Muhammad Siddiq Al-Minshawi<span lang="ar" dir="rtl">فهرس السور · الشيخ محمد صديق المنشاوي</span></p>
    <ul class="grid">
{items}
    </ul>
  </div>
</main>
""" + footer("en")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def page_404():
    title = "الصفحة غير موجودة · الشيخ محمد صديق المنشاوي"
    page = head("ar", title, "", f"{SITE}/", {"@context": "https://schema.org", "@type": "WebPage", "name": title},
                f"/en/", f"{SITE}/", f"{SITE}/en/")
    # Not a real page: no canonical / alternates / description, and keep it out of search results.
    page = re.sub(r'<meta name="description"[^>]*>\n|<link rel="(canonical|alternate)"[^>]*>\n', "", page)
    page = page.replace("<title>", '<meta name="robots" content="noindex">\n<title>', 1)
    # The old /test/ preview copy is gone: send its links to the same page on the main site.
    page = page.replace("<title>", "<script>if(/^\\/test(\\/|$)/.test(location.pathname))"
                        "location.replace((location.pathname.slice(5)||'/')+location.search+location.hash)</script>\n<title>", 1)
    return page + f"""<main>
  <div class="wrap nf">
    <p class="kicker">٤٠٤</p>
    <h1>الصفحة غير موجودة</h1>
    <p class="sub">ربما تغيّر الرابط أو كُتب خطأ. تقدر تكمّل من هنا:</p>
    <p class="nf-links">
      <a class="btn" href="/">الصفحة الرئيسية</a>
      <a href="/#library">المصحف كاملًا</a>
      <a href="/surah/">فهرس السور</a>
      <a href="/#radio">إذاعة القرآن الكريم</a>
    </p>
    <p class="nf-en" lang="en" dir="ltr">Page not found. Try the <a href="/en/">home page</a> or <a href="/en/surah/">all surahs</a>.</p>
  </div>
</main>
""" + footer("ar")


def main():
    surahs = load_surahs()
    for i, s in enumerate(surahs):
        prev, nxt = (surahs[i - 1] if i else None), (surahs[i + 1] if i < 113 else None)
        write(os.path.join(OUT_DIR, s["slug"], "index.html"), surah_page(s, prev, nxt))
        write(os.path.join(OUT_DIR_EN, s["slug"], "index.html"), surah_page_en(s, prev, nxt))
    write(os.path.join(OUT_DIR, "index.html"), index_page(surahs))
    write(os.path.join(OUT_DIR_EN, "index.html"), index_page_en(surahs))
    print("wrote", OUT_DIR, "and", OUT_DIR_EN, "(230 pages)")
    write(os.path.join(ROOT, "404.html"), page_404())
    write(os.path.join(ROOT, "sitemap.xml"), sitemap(surahs))
    print("wrote 404.html and sitemap.xml")


if __name__ == "__main__":
    main()
