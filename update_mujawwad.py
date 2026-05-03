import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Add CSS for toggle
css_toggle = """
.recitation-toggle {
  display: flex;
  background: rgba(20, 26, 31, 0.6);
  border-radius: 30px;
  padding: 4px;
  margin: 1.5rem auto 2rem;
  width: fit-content;
  border: 1px solid rgba(212, 175, 55, 0.2);
}
.recitation-btn {
  background: transparent;
  border: none;
  color: rgba(244, 237, 224, 0.6);
  font-family: 'Thmanyah Sans', sans-serif;
  font-size: 1rem;
  padding: 0.5rem 1.5rem;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}
.recitation-btn.active {
  background: #d4af37;
  color: #0b0f13;
  font-weight: 600;
  box-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
}
"""
if ".recitation-toggle" not in html:
    html = html.replace("/* ============ RESPONSIVE ============ */", css_toggle + "\n/* ============ RESPONSIVE ============ */")

# 2. Add HTML for toggle inside library header
html_toggle = """
    <div class="recitation-toggle">
      <button class="recitation-btn active" id="btnMurattal">
        <span class="lang-ar">المرتل</span>
        <span class="lang-en-text">Murattal</span>
      </button>
      <button class="recitation-btn" id="btnMujawwad">
        <span class="lang-ar">المجود</span>
        <span class="lang-en-text">Mujawwad</span>
      </button>
    </div>
"""
if "recitation-toggle" not in html[html.find('class="library-inner"'):]:
    html = html.replace('<div class="library-header">', html_toggle + '\n    <div class="library-header">')

# 3. Modify JS to handle the toggle
if "const AUDIO_BASES" not in html:
    js_update = """
const AUDIO_BASES = {
  murattal: 'https://server10.mp3quran.net/minsh/',
  mujawwad: 'https://server10.mp3quran.net/minsh/Almusshaf-Al-Mojawwad/'
};
let currentRecitationType = 'murattal';
let AUDIO_BASE = AUDIO_BASES.murattal;

const btnMurattal = document.getElementById('btnMurattal');
const btnMujawwad = document.getElementById('btnMujawwad');

function setRecitationType(type) {
  if (currentRecitationType === type) return;
  currentRecitationType = type;
  AUDIO_BASE = AUDIO_BASES[type];
  
  if (type === 'murattal') {
    btnMurattal.classList.add('active');
    btnMujawwad.classList.remove('active');
  } else {
    btnMujawwad.classList.add('active');
    btnMurattal.classList.remove('active');
  }
  
  // If playing, restart the current surah with the new audio type
  if (currentSurah && !audio.paused) {
    playSurah(currentSurah.num);
  }
}

btnMurattal.addEventListener('click', () => setRecitationType('murattal'));
btnMujawwad.addEventListener('click', () => setRecitationType('mujawwad'));
"""
    # Replace the old const AUDIO_BASE
    html = re.sub(r"const AUDIO_BASE = '[^']+';", js_update, html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Updated successfully")
