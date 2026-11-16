#!/usr/bin/env python3
"""Build the Midad redesign as a working page from index.html.

Keeps the original head, media player markup and the whole script (so
playback, radio, search, favourites, language switch keep working),
and swaps in new markup for the sections plus tools/midad.css.

    python3 tools/build_midad.py            # writes test/index.html
    python3 tools/build_midad.py out.html   # custom output
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
CSS = open(os.path.join(ROOT, "tools", "midad.css"), encoding="utf-8").read()
LOGO = open(os.path.join(ROOT, "images", "logo-minshawi.svg"), encoding="utf-8").read()
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "test", "index.html")
# Links stay inside the copy being built: /test/… for the test site, /… for the real one.
BASE = "/test" if OUT.replace(os.sep, "/").endswith("test/index.html") else ""


def between(s, a, b, inclusive_a=True):
    i = s.index(a)
    j = s.index(b, i + len(a))
    return s[i if inclusive_a else i + len(a):j]


# ---------- pieces from the current site ----------
head = SRC[:SRC.index("<style>")]
fonts_css = "\n".join(re.findall(r"@font-face\s*\{[^}]*\}", between(SRC, "/* ============ THMANYAH TYPEFACE", "/* ============ NAVIGATION")))
fonts_css = fonts_css.replace("url('fonts/", "url('/fonts/").replace('url("fonts/', 'url("/fonts/')

player_css = between(SRC, "/* ============ PRO MEDIA PLAYER (FIXED BOTTOM)", "/* ============ FOOTER ============ */")
# Re-colour the original gold/brown player with the Midad player tokens.
player_css = re.sub(r"rgba\(\s*198\s*,\s*151\s*,\s*73\s*,\s*([\d.]+)\s*\)", r"rgba(var(--p-acc-rgb),\1)", player_css)
player_css = re.sub(r"rgba\(\s*244\s*,\s*237\s*,\s*224\s*,\s*([\d.]+)\s*\)", r"rgba(var(--p-fg-rgb),\1)", player_css)
player_css = re.sub(r"rgba\(\s*26\s*,\s*20\s*,\s*16\s*,\s*[\d.]+\s*\)", "var(--p-bg)", player_css)
for c in ("#1a1410", "#0d0906", "#151009", "#1a140d"):
    player_css = player_css.replace(c, "var(--p-bg)")
player_css = (player_css.replace("#d4af37", "var(--p-acc)").replace("var(--gold)", "var(--p-acc)")
              .replace("var(--ochre)", "var(--p-acc)").replace("var(--paper)", "var(--p-fg)")
              .replace("var(--rust)", "var(--accent)").replace("var(--ink)", "var(--p-bg)"))

player_css = player_css.replace("url('images/", "url('/images/").replace('url("images/', 'url("/images/')

player_html = between(SRC, "<!-- ============ PRO MEDIA PLAYER ============ -->", "\n<script>\n")
script = SRC[SRC.rindex("\n<script>\n"):SRC.rindex("</body>")]
CARD_HREF = "href=\"${isEnglish() ? '/en' : ''}/surah/${surahSlug(s)}/\""
assert CARD_HREF in script
script = script.replace(CARD_HREF, 'href="' + BASE + CARD_HREF[6:])
# Language picked before paint (?lang= → /en/ → saved choice), same as index.html
EARLY_LANG = "<script>" + between(SRC, "<body>\n<script>", "</script>\n", inclusive_a=False) + "</script>"
assert "__initialLang" in EARLY_LANG
# Tag the "مرتل" bit of the player subtitle so it can follow the chosen
# recitation and hide during the radio.
player_html = player_html.replace(
    """          <span class="dot"></span>
          <span class="lang-ar">مرتل</span>
          <span class="lang-en-text">Murattal</span>""",
    """          <span class="dot sub-type"></span>
          <span class="lang-ar sub-type" id="subTypeAr">مرتل</span>
          <span class="lang-en-text sub-type" id="subTypeEn">Murattal</span>""", 1)
assert 'id="subTypeAr"' in player_html

# Logo as one <symbol>, reused everywhere.
vb = re.search(r'viewBox="([^"]+)"', LOGO).group(1)
paths = LOGO[LOGO.index(">") + 1:LOGO.rindex("</svg>")]
logo_symbol = f'<svg width="0" height="0" style="position:absolute" aria-hidden="true"><symbol id="logo" viewBox="{vb}">{paths}</symbol></svg>'


_vw, _vh = vb.split()[2:]


def logo(cls="logo", label="الشيخ محمد صديق المنشاوي"):
    # The symbol carries the real viewBox; the outer svg only needs the aspect ratio.
    return f'<svg class="{cls}" viewBox="0 0 {_vw} {_vh}" role="img" aria-label="{label}"><use href="#logo"/></svg>'


def ar_en(ar, en, tag="span"):
    return f'<{tag} class="lang-ar">{ar}</{tag}><{tag} class="lang-en-text">{en}</{tag}>'


# ---------- biography & timeline content (both languages) ----------
bio_src = between(SRC, '<section class="biography" id="bio">', "<!-- ============ TIMELINE")
labels = [("الفصل الأول", "Chapter One"), ("الفصل الثاني", "Chapter Two"),
          ("الفصل الثالث", "Chapter Three"), ("الفصل الرابع", "Chapter Four")]
chapters = []
for i, ch in enumerate(re.findall(r'<div class="bio-chapter.*?</div>\s*</div>', bio_src, re.S)):
    t_ar = re.search(r'<h3 class="chapter-title">\s*<span class="lang-ar">([^<]+)', ch).group(1)
    t_en = re.search(r'<h3 class="chapter-title">.*?<span class="lang-en-text">([^<]+)', ch, re.S).group(1)
    ps_ar = [re.sub(r"\s+", " ", p) for p in re.findall(r'<p class="lang-ar">\s*(.*?)\s*</p>', ch, re.S)]
    ps_en = [re.sub(r"\s+", " ", p) for p in re.findall(r'<p class="lang-en-text">\s*(.*?)\s*</p>', ch, re.S)]
    ps_ar = [p for p in ps_ar if "الشعراوي" not in p]
    body = "".join(f'<p class="lang-ar">{p}</p>' for p in ps_ar) + "".join(f'<p class="lang-en-text">{p}</p>' for p in ps_en)
    chapters.append(f'''      <article class="chapter fade-in">
        <h3><span class="label">{ar_en(*labels[i])}</span>{ar_en(t_ar, t_en)}</h3>
        {body}
      </article>''')
shar = re.search(r"«(إنّ المنشاوي[^»]+)»", SRC).group(1)
chapters.insert(2, f'''      <blockquote class="pull fade-in">
        <span class="lang-ar">«{shar}»</span>
        <span class="lang-en-text">“Al-Minshawi, al-Husary, al-Bahtimi, Abdul Basit and al-Banna ride one ship sailing the sea of the Quran, and it will not stop until God inherits the earth.”</span>
        <cite>{ar_en("— يُروى عن الشيخ محمد متولي الشعراوي", "— attributed to Sheikh Muhammad Metwally al-Sha'rawi")}</cite>
      </blockquote>''')

tl = re.findall(r'<span class="timeline-year"><span class="lang-ar">([^<]+)</span><span class="lang-en-text">([^<]+)</span></span>\s*'
                r'<span class="timeline-event">\s*<span class="lang-ar">([^<]+)</span>\s*<span class="lang-en-text">([^<]+)</span>', SRC)
assert tl, "timeline not found"
timeline = "\n".join(f'      <li class="fade-in"><b>{ar_en(ya, ye)}</b><span>{ar_en(ea, ee)}</span></li>' for ya, ye, ea, ee in tl)

PLAY = '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>'

body = f'''<body>
{EARLY_LANG}
{logo_symbol}

<header class="site-header">
  <div class="wrap">
    <a class="brand" href="#top" aria-label="أعلى الصفحة" data-aria-en="Back to top">{logo()}</a>
    <nav>
      <a href="#library">{ar_en("التلاوات", "Recitations")}</a>
      <a href="#bio">{ar_en("السيرة", "Biography")}</a>
      <button class="nav-radio" id="navRadio" type="button">
        <svg class="i-play" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg><svg class="i-pause" viewBox="0 0 24 24"><path d="M6 5h4v14H6zm8 0h4v14h-4z"/></svg>
        {ar_en("إذاعة القرآن الكريم", "Quran Radio")}<span class="live-dot"></span>
      </button>
    </nav>
    <div class="tools">
      <button class="icon-btn" id="themeToggle" aria-label="الوضع الليلي / Dark mode" title="الوضع الليلي">
        <svg class="moon" viewBox="0 0 24 24"><path d="M12.3 2a10 10 0 1 0 9.7 12.6A8 8 0 0 1 12.3 2z"/></svg>
        <svg class="sun" viewBox="0 0 24 24"><path d="M12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10zm0-5 1 3h-2zm0 20-1-3h2zM2 12l3-1v2zm20 0-3 1v-2zM4.9 4.9l2.8 1.4-1.4 1.4zm14.2 14.2-2.8-1.4 1.4-1.4zM4.9 19.1l1.4-2.8 1.4 1.4zM19.1 4.9l-1.4 2.8-1.4-1.4z"/></svg>
      </button>
      <button class="lang-toggle" id="langToggle">EN</button>
    </div>
  </div>
</header>

<main id="top">
<section class="hero">
  <div class="wrap">
    <div>
      <p class="kicker">{ar_en("الصوت الباكي", "The Weeping Voice")}</p>
      {logo()}
      <h1>{ar_en("الشيخ محمد صديق المنشاوي", "Sheikh Muhammad Siddiq Al-Minshawi")}<small class="lang-ar">Sheikh Muhammad Siddiq Al-Minshawi</small><small class="lang-en-text">الشيخ محمد صديق المنشاوي</small></h1>
      <p class="verse">{ar_en("﴿وَرَتِّلِ الْقُرْآنَ تَرْتِيلًا﴾ — المزمل ٤", "“And recite the Quran with measured recitation.” — 73:4")}</p>
      <div class="ctas">
        <a class="btn primary" href="#library">{PLAY}{ar_en("استمع إلى المصحف", "Listen to the Mushaf")}</a>
        <a class="btn ghost" href="#radio"><span class="live-dot"></span>{ar_en("إذاعة القرآن الكريم", "Quran Radio")}</a>
      </div>
      <div class="years">
        <span><b>{ar_en("١٩٢٠", "1920")}</b>{ar_en("المولد · سوهاج", "Born · Sohag")}</span>
        <span><b>{ar_en("١٩٦٩", "1969")}</b>{ar_en("الوفاة · القاهرة", "Died · Cairo")}</span>
      </div>
    </div>
    <figure class="portrait">
      <picture>
        <source srcset="/images/sheikh-minshawi.avif" type="image/avif">
        <source srcset="/images/sheikh-minshawi.webp" type="image/webp">
        <img src="/images/sheikh-minshawi.jpg" alt="الشيخ محمد صديق المنشاوي - Sheikh Muhammad Siddiq Al-Minshawi" width="765" height="1024" fetchpriority="high">
      </picture>
      <figcaption>{ar_en("الشيخ محمد صديق المنشاوي", "Sheikh Muhammad Siddiq Al-Minshawi")}<span>{ar_en("١٩٢٠ — ١٩٦٩", "1920 — 1969")}</span></figcaption>
    </figure>
  </div>
</section>

<section class="block library" id="library">
  <div class="wrap">
    <div class="head"><span class="num">{ar_en("٠١", "01")}</span><h2>{ar_en("المصحف الشريف كاملًا", "The Complete Mushaf")}</h2><p>{ar_en("التلاوات · ١١٤ سورة برواية حفص عن عاصم", "Recitations · 114 surahs, Hafs from 'Asim")}</p></div>
    <div class="lib-bar">
      <div class="recitation-toggle">
        <button class="recitation-btn active" id="btnMurattal">{ar_en("المرتل", "Murattal")}</button>
        <button class="recitation-btn" id="btnMujawwad">{ar_en("المجوّد", "Mujawwad")}</button>
      </div>
      <label class="search-box"><svg viewBox="0 0 24 24"><path d="M10 2a8 8 0 0 1 6.32 12.9l5.39 5.4-1.41 1.4-5.4-5.39A8 8 0 1 1 10 2zm0 2a6 6 0 1 0 0 12 6 6 0 0 0 0-12z"/></svg><input type="text" id="searchInput" placeholder="ابحث عن سورة..."></label>
      <div class="lib-stats">
        <span class="lang-ar">يُعرض <strong id="visibleCount">١١٤</strong> من <strong>١١٤</strong> سورة</span>
        <span class="lang-en-text">Showing <strong id="visibleCountEn">114</strong> of <strong>114</strong> surahs</span>
      </div>
    </div>
    <div class="surahs-grid" id="surahsGrid"></div>
    <p class="lib-more">{ar_en(f'لكل سورة صفحة خاصة بها — <a href="{BASE}/surah/">فهرس السور</a>', f'Every surah has its own page — <a href="{BASE}/en/surah/">All surahs</a>')}</p>
  </div>
</section>

<section class="live-radio" id="radio">
  <div class="wrap radio-band">
    <div class="radio-text">
      <span class="live-badge"><span class="live-dot"></span>{ar_en("بث مباشر", "Live")}</span>
      <h2 class="live-radio-title">{ar_en("إذاعة القرآن الكريم", "Holy Quran Radio")}</h2>
      <p class="live-radio-subtitle">{ar_en("من القاهرة · على مدار الساعة", "From Cairo · around the clock")}</p>
    </div>
    <div class="radio-control">
      <div class="radio-speaker">
        <span class="radio-ring"></span><span class="radio-ring"></span><span class="radio-ring"></span>
        <button class="radio-play-btn" id="radioPlayBtn" aria-label="تشغيل/إيقاف الإذاعة" data-aria-en="Play/Pause radio">
          <svg viewBox="0 0 24 24" id="radioPlayIcon"><path d="M8 5v14l11-7z"></path></svg>
        </button>
      </div>
      <span class="radio-status" id="radioStatus">{ar_en("اضغط للاستماع", "Tap to listen")}</span>
    </div>
  </div>
  <audio id="radioAudio" preload="none"></audio>
</section>

<section class="block" id="bio">
  <div class="wrap">
    <div class="head"><span class="num">{ar_en("٠٢", "02")}</span><h2>{ar_en("حياة وُهبت للقرآن", "A Life Devoted to the Quran")}</h2><p>{ar_en("السيرة الذاتية", "Life &amp; Legacy")}</p></div>
    <p class="bio-intro">{ar_en("وُلد الشيخ محمد صديق المنشاوي عام ١٩٢٠ في المنشأة بمحافظة سوهاج، في أسرة توارثت تلاوة القرآن الكريم، وأتمّ حفظه صغيرًا. اعتُمد قارئًا بالإذاعة المصرية سنة ١٩٥٣، ولُقِّب بـ«الصوت الباكي» لخشوع تلاوته، وسجّل المصحف كاملًا مرتّلًا ومجوّدًا، وطاف بتلاوته بلاد العالم الإسلامي حتى رحيله عام ١٩٦٩.", "Born in 1920 in al-Minsha'ah, Sohag, into a family of Quran reciters, Sheikh Muhammad Siddiq al-Minshawi memorized the Quran as a child, joined Egyptian Radio in 1953 and became known as “the Weeping Voice.” He recorded the complete Quran, murattal and mujawwad, and recited across the Muslim world until his death in 1969.")}</p>
    <details class="bio-more" id="bioMore">
      <summary class="btn ghost"><span class="more">{ar_en("اقرأ السيرة كاملة", "Read the full biography")}</span><span class="less">{ar_en("إخفاء السيرة", "Hide the biography")}</span><svg viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z"/></svg></summary>
      <div class="bio">
{chr(10).join(chapters)}
      </div>
      <h3 class="tl-title">{ar_en("المسيرة · رحلة في تسعٍ وأربعين سنة", "Timeline · a journey in 49 years")}</h3>
      <ol class="timeline" id="timeline">
{timeline}
      </ol>
    </details>
  </div>
</section>
</main>

<footer class="site-footer">
  <div class="wrap">
    {logo()}
    <p class="verse">{ar_en("﴿وَرَتِّلِ الْقُرْآنَ تَرْتِيلًا﴾", "“And recite the Quran with measured recitation.”")}</p>
    <nav>
      <a href="#library">{ar_en("التلاوات", "Recitations")}</a>
      <a href="#bio">{ar_en("السيرة", "Biography")}</a>
      <a href="{BASE}/surah/" data-href-ar="{BASE}/surah/" data-href-en="{BASE}/en/surah/">{ar_en("فهرس السور", "All Surahs")}</a>
      <a href="#radio">{ar_en("إذاعة القرآن الكريم", "Quran Radio")}</a>
    </nav>
    <p class="fine">{ar_en("تلاوات القرآن الكريم بصوت الشيخ محمد صديق المنشاوي محفوظة الحقوق لمالكيها الأصليين. هذا الموقع غير تجاري ويهدف لنشر القرآن الكريم.", "Quran recitations by Sheikh Muhammad Siddiq Al-Minshawi are copyrighted to their original owners. This is a non-commercial website aimed at spreading the Holy Quran.")}</p>
  </div>
</footer>

{player_html}
'''

THEME_HEAD = """<script>
(function(){try{var t=localStorage.getItem('theme');if(t==='dark'||t==='light')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();
</script>
"""

THEME_JS = """<script>
// ============ THEME (light / dark) ============
(function(){
  var root=document.documentElement, btn=document.getElementById('themeToggle');
  var meta=document.querySelector('meta[name="theme-color"]');
  var mq=window.matchMedia('(prefers-color-scheme: dark)');
  function isDark(){var t=root.getAttribute('data-theme');return t?t==='dark':mq.matches;}
  function sync(){if(meta)meta.setAttribute('content',isDark()?'#121110':'#f7f4ee');
    if(btn){var en=document.body.classList.contains('lang-en');
      btn.title=isDark()?(en?'Light mode':'الوضع النهاري'):(en?'Dark mode':'الوضع الليلي');btn.setAttribute('aria-label',btn.title);}}
  if(btn)btn.addEventListener('click',function(){
    var next=isDark()?'light':'dark';root.setAttribute('data-theme',next);
    try{localStorage.setItem('theme',next);}catch(e){}sync();});
  if(mq.addEventListener)mq.addEventListener('change',sync);
  new MutationObserver(sync).observe(document.body,{attributes:true,attributeFilter:['class']});
  sync();
})();
// Header radio button: plays/stops the live radio in place, and mirrors its state
(function(){
  var nb=document.getElementById('navRadio'),card=document.getElementById('radioPlayBtn'),sec=document.querySelector('.live-radio');
  if(!nb||!card||!sec)return;
  nb.addEventListener('click',function(){card.click();});
  function upd(){var on=sec.classList.contains('radio-playing'),en=document.body.classList.contains('lang-en');nb.classList.toggle('on',on);
    nb.setAttribute('aria-label',on?(en?'Stop Quran radio':'إيقاف إذاعة القرآن الكريم'):(en?'Play Quran radio':'تشغيل إذاعة القرآن الكريم'));}
  new MutationObserver(upd).observe(sec,{attributes:true,attributeFilter:['class']});
  new MutationObserver(upd).observe(document.body,{attributes:true,attributeFilter:['class']});upd();
})();
// Full biography: open it when the address points inside it (e.g. #timeline)
(function(){
  var d=document.getElementById('bioMore');if(!d)return;
  function chk(){if(location.hash==='#timeline'){d.open=true;var t=document.getElementById('timeline');if(t)setTimeout(function(){t.scrollIntoView();},50);}}
  window.addEventListener('hashchange',chk);chk();
  d.addEventListener('toggle',function(){if(!d.open){var b=document.getElementById('bio');if(b&&b.getBoundingClientRect().top<0)b.scrollIntoView();}});
})();
// Player subtitle follows murattal / mujawwad
(function(){
  var mj=document.getElementById('btnMujawwad'),ar=document.getElementById('subTypeAr'),en=document.getElementById('subTypeEn');
  if(!mj||!ar)return;
  function upd(){var on=mj.classList.contains('active');ar.textContent=on?'مجوّد':'مرتل';en.textContent=on?'Mujawwad':'Murattal';}
  new MutationObserver(upd).observe(mj,{attributes:true,attributeFilter:['class']});upd();
})();
</script>
"""

head = head.replace("</head>", "")
head = re.sub(r"<title>[^<]*</title>", "<title>الشيخ محمد صديق المنشاوي · الصوت الباكي</title>", head, count=1)
if "/test/" in OUT.replace(os.sep, "/") or OUT.endswith("test/index.html"):
    head = head.replace('<meta name="robots" content="index, follow, max-image-preview:large">',
                        '<meta name="robots" content="noindex, nofollow">')
head = head.replace('<meta name="theme-color" content="#2a1f12">',
                    '<meta name="theme-color" content="#f7f4ee">\n<meta name="color-scheme" content="only light">')
# Link previews (WhatsApp, X, Facebook…): Midad share card, 1200×630.
head = (head.replace("images/social-thumbnail.jpg", "images/og-minshawi.jpg")
            .replace('<meta property="og:image:type" content="image/jpeg">',
                     '<meta property="og:image:secure_url" content="https://www.elminshawy.net/images/og-minshawi.jpg">\n<meta property="og:image:type" content="image/jpeg">')
            .replace('<meta property="og:image:width" content="1024">', '<meta property="og:image:width" content="1200">')
            .replace('<meta property="og:image:height" content="537">',
                     '<meta property="og:image:height" content="630">\n<meta property="og:image:alt" content="الشيخ محمد صديق المنشاوي · الصوت الباكي">')
            .replace('<meta property="og:url" content="https://www.elminshawy.net/">',
                     f'<meta property="og:url" content="https://www.elminshawy.net{BASE}/">'))
assert "og-minshawi.jpg" in head and 'content="1200"' in head

page = (head + THEME_HEAD + "<style>\n" + fonts_css + "\n" + player_css + "\n" + CSS + "\n</style>\n</head>\n"
        + body + script + THEME_JS + "</body>\n</html>\n")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(page)
print("wrote", OUT, len(page.encode()), "bytes")

# English home of this copy: <base>/en/
if OUT.replace(os.sep, "/").endswith("/index.html") and os.path.basename(os.path.dirname(OUT)) != "en":
    import build_en_home  # noqa: E402
    out_en = os.path.join(os.path.dirname(OUT), "en", "index.html")
    os.makedirs(os.path.dirname(out_en), exist_ok=True)
    open(out_en, "w", encoding="utf-8").write(build_en_home.build(page, base=BASE))
    print("wrote", out_en)
