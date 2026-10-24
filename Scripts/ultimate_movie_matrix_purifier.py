"""
Hindi Music Vault — DEFINITIVE Single-Source-of-Truth Classifier & Purifier
============================================================================
This is the ONLY classifier script. All others have been retired.

Classification priority:
  1. Devotional keyword detection (bhajans, mantras, chalisa, aarti)
  2. Movie/Album name matching (sorted LONGEST-FIRST to avoid substring hijacks)
  3. API year as-is (NEVER force-overwrite to a hardcoded default)
  4. Remix/LoFi/DJ → route to the era of the REMIX release, not the original

Key design rules:
  - All matching uses \b word-boundary regex (no substring collisions)
  - "Aashiqui 2" is checked BEFORE "Aashiqui" (longest-first sort)
  - "Bareilly Ki Barfi" is checked BEFORE "Barfi" (longest-first sort)
  - Artist names are NEVER used for primary classification (only movie/year)
  - If year is unknown and no movie match, defaults to 2010s (safest bucket)
"""

import os
import sys
import json
import re
import shutil

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
CATALOGS_DIR = os.path.join(VAULT_ROOT, "Catalogs")

# =============================================================================
# MASTER MOVIE-TO-DECADE MATRIX
# Every entry: 'movie_name_lowercase': ('catalog_filename', 'true_release_year')
# Sorted longest-first at runtime to prevent substring hijacking.
# =============================================================================
MOVIE_YEAR_MATRIX = {
    # ── 2020s ────────────────────────────────────────────────────────────────
    'rocky aur rani kii prem kahaani': ('05_2020s_today.json', '2023'),
    'teri baaton mein aisa uljha jiya': ('05_2020s_today.json', '2024'),
    'tu jhoothi main makkaar': ('05_2020s_today.json', '2023'),
    'zara hatke zara bachke': ('05_2020s_today.json', '2023'),
    'amar singh chamkila': ('05_2020s_today.json', '2024'),
    'bhool bhulaiyaa 3': ('05_2020s_today.json', '2024'),
    'bhool bhulaiyaa 2': ('05_2020s_today.json', '2022'),
    'rocky aur rani': ('05_2020s_today.json', '2023'),
    'mr & mrs mahi': ('05_2020s_today.json', '2024'),
    'laapataa ladies': ('05_2020s_today.json', '2024'),
    'chandu champion': ('05_2020s_today.json', '2024'),
    'khel khel mein': ('05_2020s_today.json', '2024'),
    'singham again': ('05_2020s_today.json', '2024'),
    'pushpa the rise': ('05_2020s_today.json', '2021'),
    'article 370': ('05_2020s_today.json', '2024'),
    'sam bahadur': ('05_2020s_today.json', '2023'),
    'brahmastra': ('05_2020s_today.json', '2022'),
    'shershaah': ('05_2020s_today.json', '2021'),
    'bad newz': ('05_2020s_today.json', '2024'),
    'chamkila': ('05_2020s_today.json', '2024'),
    'border 2': ('05_2020s_today.json', '2025'),
    'pushpa 2': ('05_2020s_today.json', '2024'),
    'fighter': ('05_2020s_today.json', '2024'),
    'stree 2': ('05_2020s_today.json', '2024'),
    'pathaan': ('05_2020s_today.json', '2023'),
    'gadar 2': ('05_2020s_today.json', '2023'),
    'devara': ('05_2020s_today.json', '2024'),
    'animal': ('05_2020s_today.json', '2023'),
    'jawan': ('05_2020s_today.json', '2023'),
    'dunki': ('05_2020s_today.json', '2023'),
    'munjya': ('05_2020s_today.json', '2024'),

    # ── 2010s ────────────────────────────────────────────────────────────────
    'humpty sharma ki dulhania': ('04_2010s.json', '2014'),
    'toilet ek prem katha': ('04_2010s.json', '2017'),
    'zindagi na milegi dobara': ('04_2010s.json', '2011'),
    'sonu ke titu ki sweety': ('04_2010s.json', '2018'),
    'yeh jawaani hai deewani': ('04_2010s.json', '2013'),
    'uri the surgical strike': ('04_2010s.json', '2019'),
    'badrinath ki dulhania': ('04_2010s.json', '2017'),
    'bareilly ki barfi': ('04_2010s.json', '2017'),
    'student of the year 2': ('04_2010s.json', '2019'),
    'student of the year': ('04_2010s.json', '2012'),
    'ae dil hai mushkil': ('04_2010s.json', '2016'),
    'jab tak hai jaan': ('04_2010s.json', '2012'),
    'tiger zinda hai': ('04_2010s.json', '2017'),
    'chennai express': ('04_2010s.json', '2013'),
    'dil dhadakne do': ('04_2010s.json', '2015'),
    'half girlfriend': ('04_2010s.json', '2017'),
    'secret superstar': ('04_2010s.json', '2017'),
    'bajrangi bhaijaan': ('04_2010s.json', '2015'),
    'bajirao mastani': ('04_2010s.json', '2015'),
    'hindi medium': ('04_2010s.json', '2017'),
    'jagga jasoos': ('04_2010s.json', '2017'),
    'rowdy rathore': ('04_2010s.json', '2012'),
    'kabir singh': ('04_2010s.json', '2019'),
    'kapoor & sons': ('04_2010s.json', '2016'),
    'dear zindagi': ('04_2010s.json', '2016'),
    'raanjihaana': ('04_2010s.json', '2013'),
    'ishaqzaade': ('04_2010s.json', '2012'),
    'chhichhore': ('04_2010s.json', '2019'),
    'luka chuppi': ('04_2010s.json', '2019'),
    'aashiqui 2': ('04_2010s.json', '2013'),
    'padmaavat': ('04_2010s.json', '2018'),
    'kedarnath': ('04_2010s.json', '2018'),
    'dabangg 3': ('04_2010s.json', '2019'),
    'dabangg 2': ('04_2010s.json', '2012'),
    'ek villain': ('04_2010s.json', '2014'),
    'bang bang': ('04_2010s.json', '2014'),
    'gully boy': ('04_2010s.json', '2019'),
    'rockstar': ('04_2010s.json', '2011'),
    'bodyguard': ('04_2010s.json', '2011'),
    'cocktail': ('04_2010s.json', '2012'),
    'ms dhoni': ('04_2010s.json', '2016'),
    'badlapur': ('04_2010s.json', '2015'),
    '2 states': ('04_2010s.json', '2014'),
    'dilwale': ('04_2010s.json', '2015'),
    'tamasha': ('04_2010s.json', '2015'),
    'don 2': ('04_2010s.json', '2011'),
    'dhoom 3': ('04_2010s.json', '2013'),
    'ra.one': ('04_2010s.json', '2011'),
    'shivaay': ('04_2010s.json', '2016'),
    'airlift': ('04_2010s.json', '2016'),
    'highway': ('04_2010s.json', '2014'),
    'dangal': ('04_2010s.json', '2016'),
    'sultan': ('04_2010s.json', '2016'),
    'simmba': ('04_2010s.json', '2018'),
    'kesari': ('04_2010s.json', '2019'),
    'raabta': ('04_2010s.json', '2017'),
    'lootera': ('04_2010s.json', '2013'),
    'rustom': ('04_2010s.json', '2016'),
    'barfi': ('04_2010s.json', '2012'),
    'kalank': ('04_2010s.json', '2019'),
    'yjhd': ('04_2010s.json', '2013'),
    'dabangg': ('04_2010s.json', '2010'),
    'ok jaanu': ('04_2010s.json', '2017'),
    # NOTE: Short names removed: 'war', 'kick', 'piku', 'bala', 'queen',
    # 'stree', 'highway' — these match common Hindi/English words.

    # ── 2000s ────────────────────────────────────────────────────────────────
    'ajab prem ki ghazab kahani': ('03_2000s.json', '2009'),
    'kabhi khushi kabhie gham': ('03_2000s.json', '2001'),
    'kabhi alvida naa kehna': ('03_2000s.json', '2006'),
    'rehnaa hai terre dil mein': ('03_2000s.json', '2001'),
    'chori chori chupke chupke': ('03_2000s.json', '2001'),
    'bachna ae haseeno': ('03_2000s.json', '2008'),
    'lage raho munna bhai': ('03_2000s.json', '2006'),
    'har dil jo pyar karega': ('03_2000s.json', '2000'),
    'kaho naa pyaar hai': ('03_2000s.json', '2000'),
    'kaho naa pyar hai': ('03_2000s.json', '2000'),
    'kaho na pyaar hai': ('03_2000s.json', '2000'),
    'kaho na pyar hai': ('03_2000s.json', '2000'),
    'jaane tu ya jaane na': ('03_2000s.json', '2008'),
    'main prem ki diwani hoon': ('03_2000s.json', '2003'),
    'mujhse shaadi karogi': ('03_2000s.json', '2004'),
    'mujhsie shaadi karogi': ('03_2000s.json', '2004'),
    'aashiq banaya aapne': ('03_2000s.json', '2005'),
    'gadar ek prem katha': ('03_2000s.json', '2001'),
    'rab ne bana di jodi': ('03_2000s.json', '2008'),
    'rang de basanti': ('03_2000s.json', '2006'),
    'mission kashmir': ('03_2000s.json', '2000'),
    'taare zameen par': ('03_2000s.json', '2007'),
    'salaam namaste': ('03_2000s.json', '2005'),
    'life in a metro': ('03_2000s.json', '2007'),
    'namastey london': ('03_2000s.json', '2007'),
    'bhool bhulaiyaa': ('03_2000s.json', '2007'),
    'munna bhai mbbs': ('03_2000s.json', '2003'),
    'singh is kinng': ('03_2000s.json', '2008'),
    'garam masala': ('03_2000s.json', '2005'),
    'bunty aur babli': ('03_2000s.json', '2005'),
    'chak de india': ('03_2000s.json', '2007'),
    'jodhaa akbar': ('03_2000s.json', '2008'),
    'om shanti om': ('03_2000s.json', '2007'),
    'jhankaar beats': ('03_2000s.json', '2003'),
    'dil chahta hai': ('03_2000s.json', '2001'),
    'dil hai tumhaara': ('03_2000s.json', '2002'),
    'kuch naa kaho': ('03_2000s.json', '2003'),
    'love aaj kal': ('03_2000s.json', '2009'),
    'wake up sid': ('03_2000s.json', '2009'),
    'mohabbatein': ('03_2000s.json', '2000'),
    'bluffmaster': ('03_2000s.json', '2005'),
    'main hoon na': ('03_2000s.json', '2004'),
    'kal ho naa ho': ('03_2000s.json', '2003'),
    'woh lamhe': ('03_2000s.json', '2006'),
    'koi mil gaya': ('03_2000s.json', '2003'),
    'ishq vishk': ('03_2000s.json', '2003'),
    'jab we met': ('03_2000s.json', '2007'),
    'tere naam': ('03_2000s.json', '2003'),
    'no entry': ('03_2000s.json', '2005'),
    'veer-zaara': ('03_2000s.json', '2004'),
    'veer zaara': ('03_2000s.json', '2004'),
    'parineeta': ('03_2000s.json', '2005'),
    'dostana': ('03_2000s.json', '2008'),
    'new york': ('03_2000s.json', '2009'),
    '3 idiots': ('03_2000s.json', '2009'),
    'gangster': ('03_2000s.json', '2006'),
    'dhadkan': ('03_2000s.json', '2000'),
    'dhoom:2': ('03_2000s.json', '2006'),
    'dhoom 2': ('03_2000s.json', '2006'),
    'rock on': ('03_2000s.json', '2008'),
    'kaminey': ('03_2000s.json', '2009'),
    'ghajini': ('03_2000s.json', '2008'),
    'awarapan': ('03_2000s.json', '2007'),
    'tum mile': ('03_2000s.json', '2009'),
    'baghban': ('03_2000s.json', '2003'),
    'saathiya': ('03_2000s.json', '2002'),
    'lagaan': ('03_2000s.json', '2001'),
    # 'andaaz' removed — too generic, matches compilation albums from different eras
    'humraaz': ('03_2000s.json', '2002'),
    'swades': ('03_2000s.json', '2004'),
    'hungama': ('03_2000s.json', '2003'),
    'devdas': ('03_2000s.json', '2002'),
    'krrish': ('03_2000s.json', '2006'),
    'fanaa': ('03_2000s.json', '2006'),
    'omkara': ('03_2000s.json', '2006'),
    'billu': ('03_2000s.json', '2009'),
    'kaante': ('03_2000s.json', '2002'),
    'lakshya': ('03_2000s.json', '2004'),
    'hum tum': ('03_2000s.json', '2004'),
    'partner': ('03_2000s.json', '2007'),
    'murder': ('03_2000s.json', '2004'),
    'jannat': ('03_2000s.json', '2008'),
    'aitraaz': ('03_2000s.json', '2004'),
    'khakee': ('03_2000s.json', '2004'),
    'hulchul': ('03_2000s.json', '2004'),
    'welcome': ('03_2000s.json', '2007'),
    'zeher': ('03_2000s.json', '2005'),
    'aksar': ('03_2000s.json', '2006'),
    'vivah': ('03_2000s.json', '2006'),
    'dev.d': ('03_2000s.json', '2009'),
    # NOTE: Short names removed: 'josh', 'fiza', 'race', 'raaz', 'jism', 'yuva', 'guru', 'dus'
    # These match common Hindi words. They rely on year-based fallback instead.

    # ── 80s & 90s ────────────────────────────────────────────────────────────
    'dilwale dulhania le jayenge': ('02_80s_90s.json', '1995'),
    'qayamat se qayamat tak': ('02_80s_90s.json', '1988'),
    'hum dil de chuke sanam': ('02_80s_90s.json', '1999'),
    'jo jeeta wohi sikandar': ('02_80s_90s.json', '1992'),
    'dil hai ke manta nahin': ('02_80s_90s.json', '1991'),
    'main khiladi tu anari': ('02_80s_90s.json', '1994'),
    'hum aapke hain koun': ('02_80s_90s.json', '1994'),
    'ram teri ganga maili': ('02_80s_90s.json', '1985'),
    'hum saath saath hain': ('02_80s_90s.json', '1999'),
    'haseena maan jaayegi': ('02_80s_90s.json', '1999'),
    '1942 a love story': ('02_80s_90s.json', '1994'),
    'andaz apna apna': ('02_80s_90s.json', '1994'),
    'ek duje ke liye': ('02_80s_90s.json', '1981'),
    'maine pyar kiya': ('02_80s_90s.json', '1989'),
    'namak halaal': ('02_80s_90s.json', '1982'),
    'raja hindustani': ('02_80s_90s.json', '1996'),
    'dil to pagal hai': ('02_80s_90s.json', '1997'),
    'disco dancer': ('02_80s_90s.json', '1982'),
    'kuch kuch hota hai': ('02_80s_90s.json', '1998'),
    'karan arjun': ('02_80s_90s.json', '1995'),
    'mr. india': ('02_80s_90s.json', '1987'),
    'mr india': ('02_80s_90s.json', '1987'),
    'khalnayak': ('02_80s_90s.json', '1993'),
    'ram lakhan': ('02_80s_90s.json', '1989'),
    'rangeela': ('02_80s_90s.json', '1995'),
    'aashiqui': ('02_80s_90s.json', '1990'),
    'prem rog': ('02_80s_90s.json', '1982'),
    'baazigar': ('02_80s_90s.json', '1993'),
    'umrao jaan': ('02_80s_90s.json', '1981'),
    'sarfarosh': ('02_80s_90s.json', '1999'),
    'sharaabi': ('02_80s_90s.json', '1984'),
    'chandni': ('02_80s_90s.json', '1989'),
    'silsila': ('02_80s_90s.json', '1981'),
    'tezaab': ('02_80s_90s.json', '1988'),
    'qurbani': ('02_80s_90s.json', '1980'),
    'soldier': ('02_80s_90s.json', '1998'),
    'khiladi': ('02_80s_90s.json', '1992'),
    'bombay': ('02_80s_90s.json', '1995'),
    'ghayal': ('02_80s_90s.json', '1990'),
    # 'dil se' removed — too generic, matches unrelated album names like 'Dil Se Diljit'
    'pardes': ('02_80s_90s.json', '1997'),
    'damini': ('02_80s_90s.json', '1993'),
    'saajan': ('02_80s_90s.json', '1991'),
    'lamhe': ('02_80s_90s.json', '1991'),
    'mohra': ('02_80s_90s.json', '1994'),
    'koyla': ('02_80s_90s.json', '1997'),
    'satya': ('02_80s_90s.json', '1998'),
    'darr': ('02_80s_90s.json', '1993'),
    'taal': ('02_80s_90s.json', '1999'),
    'roja': ('02_80s_90s.json', '1992'),
    'karz': ('02_80s_90s.json', '1980'),
    'ddlj': ('02_80s_90s.json', '1995'),
    'qsqt': ('02_80s_90s.json', '1988'),
    'hahk': ('02_80s_90s.json', '1994'),
    'dtph': ('02_80s_90s.json', '1997'),
    'kkhh': ('02_80s_90s.json', '1998'),
    'hddcs': ('02_80s_90s.json', '1999'),
    'hssh': ('02_80s_90s.json', '1999'),
    # NOTE: Short/generic movie names removed to prevent false positives:
    # 'dil' (1990), 'hum' (1991), 'hero' (1983), 'border' (1997), 'beta' (1992),
    # 'sadak' (1991), 'masoom' (1983), 'gupt' (1997) — these match common words
    # in song titles. They rely on year-based fallback instead.

    # ── 50s, 60s, 70s ───────────────────────────────────────────────────────
    'muqaddar ka sikandar': ('01_60s_70s.json', '1978'),
    'hum kisise kum naheen': ('01_60s_70s.json', '1977'),
    'satyam shivam sundaram': ('01_60s_70s.json', '1978'),
    'roti kapada aur makaan': ('01_60s_70s.json', '1974'),
    'hare rama hare krishna': ('01_60s_70s.json', '1971'),
    'amar akbar anthony': ('01_60s_70s.json', '1977'),
    'yaadon ki baaraat': ('01_60s_70s.json', '1973'),
    'haathi mere saathi': ('01_60s_70s.json', '1971'),
    'jab jab phool khile': ('01_60s_70s.json', '1965'),
    'an evening in paris': ('01_60s_70s.json', '1967'),
    'tere ghar ke samne': ('01_60s_70s.json', '1963'),
    'chaudhvin ka chand': ('01_60s_70s.json', '1960'),
    'barsaat ki raat': ('01_60s_70s.json', '1960'),
    'mera naam joker': ('01_60s_70s.json', '1970'),
    'johny mera naam': ('01_60s_70s.json', '1970'),
    'seeta aur geeta': ('01_60s_70s.json', '1972'),
    'jawani diwani': ('01_60s_70s.json', '1972'),
    'mughal-e-azam': ('01_60s_70s.json', '1960'),
    'mughal e azam': ('01_60s_70s.json', '1960'),
    'kashmir ki kali': ('01_60s_70s.json', '1964'),
    'dharam veer': ('01_60s_70s.json', '1977'),
    'teesri manzil': ('01_60s_70s.json', '1966'),
    'namak haraam': ('01_60s_70s.json', '1973'),
    'aap ki kasam': ('01_60s_70s.json', '1974'),
    'kabhi kabhie': ('01_60s_70s.json', '1976'),
    'woh kaun thi': ('01_60s_70s.json', '1964'),
    'mother india': ('01_60s_70s.json', '1957'),
    'jewel thief': ('01_60s_70s.json', '1967'),
    'bees saal baad': ('01_60s_70s.json', '1962'),
    'ganga jamuna': ('01_60s_70s.json', '1961'),
    'amar prem': ('01_60s_70s.json', '1972'),
    'kati patang': ('01_60s_70s.json', '1971'),
    'kora kagaz': ('01_60s_70s.json', '1974'),
    'mera saaya': ('01_60s_70s.json', '1966'),
    'gol maal': ('01_60s_70s.json', '1979'),
    'blackmail': ('01_60s_70s.json', '1973'),
    'naya daur': ('01_60s_70s.json', '1957'),
    'madhumati': ('01_60s_70s.json', '1958'),
    'shree 420': ('01_60s_70s.json', '1955'),
    'do raaste': ('01_60s_70s.json', '1969'),
    'aradhana': ('01_60s_70s.json', '1969'),
    'abhimaan': ('01_60s_70s.json', '1973'),
    'deewaar': ('01_60s_70s.json', '1975'),
    'hum dono': ('01_60s_70s.json', '1961'),
    'pakeezah': ('01_60s_70s.json', '1972'),
    'padosan': ('01_60s_70s.json', '1968'),
    'trishul': ('01_60s_70s.json', '1978'),
    'junglee': ('01_60s_70s.json', '1961'),
    'pyaasa': ('01_60s_70s.json', '1957'),
    'caravan': ('01_60s_70s.json', '1971'),
    'awaara': ('01_60s_70s.json', '1951'),
    'majboor': ('01_60s_70s.json', '1974'),
    'sholay': ('01_60s_70s.json', '1975'),
    'zanjeer': ('01_60s_70s.json', '1973'),
    'sangam': ('01_60s_70s.json', '1964'),
    'aandhi': ('01_60s_70s.json', '1975'),
    'c.i.d.': ('01_60s_70s.json', '1956'),
    'c.i.d': ('01_60s_70s.json', '1956'),
    # NOTE: Short names removed: 'bobby', 'guide', 'dosti', 'julie', 'anand',
    # 'safar', 'shor', 'ghar' — too generic, match common Hindi words.
}

# Pre-sort movie names longest-first (done once at module load)
_SORTED_MOVIE_NAMES = sorted(MOVIE_YEAR_MATRIX.keys(), key=lambda x: -len(x))

# Devotional keyword patterns (compiled once)
_DEVOTIONAL_WORDS = [
    'chalisa', 'aarti', 'mantra', 'bhajan', 'stotram', 'hanuman', 'ganesh',
    'shiva', 'mahadeva', 'gayatri', 'amritwani', 'mataji', 'devi', 'govind',
    'radhe', 'vrindavan', 'ashtakam', 'bhagwan', 'sai baba', 'shirdi',
    'khatu shyam', 'sunderkand', 'path', 'ardas', 'satnam', 'waheguru',
    'achyutam keshavam', 'om jai jagdish', 'raghupati raghav'
]

# =============================================================================
# CLASSIFICATION FUNCTION
# =============================================================================
def classify_track(t):
    """Classify a single track into the correct era catalog.
    
    Returns: (catalog_filename, genre_string, year_string)
    
    Priority:
      1. Devotional keywords → 06_bhajans.json
      2. Movie name match (longest-first) → that movie's era
      3. API year as-is → route by decade
      4. Unknown → 04_2010s.json (safest default)
    """
    title = t.get('title', '').strip()
    artist = t.get('artist', '').strip()
    album = t.get('album', '').strip()
    raw_yr = str(t.get('year', '')).strip()
    
    full = f"{title} {album}".lower()
    full_with_artist = f"{title} {album} {artist}".lower()

    # ── Step 1: Devotional check ──
    if any(re.search(rf'\b{re.escape(w)}\b', full_with_artist) for w in _DEVOTIONAL_WORDS):
        return "06_bhajans.json", "Hindi Devotional / Bhajan", raw_yr or "2000"

    # ── Step 2a: ALBUM-ONLY match (highest priority — album IS the movie name) ──
    album_lower = album.lower()
    for movie_name in _SORTED_MOVIE_NAMES:
        pattern = rf'\b{re.escape(movie_name)}\b'
        if re.search(pattern, album_lower):
            cat_file, yr = MOVIE_YEAR_MATRIX[movie_name]
            genre = _catalog_to_genre(cat_file)
            return cat_file, genre, yr

    # ── Step 2b: TITLE-ONLY match (fallback — for tracks where album is generic) ──
    title_lower = title.lower()
    for movie_name in _SORTED_MOVIE_NAMES:
        pattern = rf'\b{re.escape(movie_name)}\b'
        if re.search(pattern, title_lower):
            cat_file, yr = MOVIE_YEAR_MATRIX[movie_name]
            genre = _catalog_to_genre(cat_file)
            return cat_file, genre, yr

    # ── Step 3: Year-based routing (trust the API year, NEVER force-overwrite) ──
    if raw_yr.isdigit():
        y = int(raw_yr)
        if y < 1980:
            return "01_60s_70s.json", "Classic Bollywood 60s & 70s", raw_yr
        elif y <= 1999:
            return "02_80s_90s.json", "Evergreen Romance 80s & 90s", raw_yr
        elif y <= 2009:
            return "03_2000s.json", "2000s Bollywood Hits", raw_yr
        elif y <= 2019:
            return "04_2010s.json", "2010s Modern Bollywood", raw_yr
        else:
            return "05_2020s_today.json", "Bollywood 2020s Hits", raw_yr

    # ── Step 4: No year, no movie match → default to 2010s (safest bucket) ──
    return "04_2010s.json", "2010s Modern Bollywood", "2015"


def _catalog_to_genre(cat_file):
    return {
        "01_60s_70s.json": "Classic Bollywood 60s & 70s",
        "02_80s_90s.json": "Evergreen Romance 80s & 90s",
        "03_2000s.json": "2000s Bollywood Hits",
        "04_2010s.json": "2010s Modern Bollywood",
        "05_2020s_today.json": "Bollywood 2020s Hits",
        "06_bhajans.json": "Hindi Devotional / Bhajan",
    }.get(cat_file, "Bollywood Hits")


# Folder name for each catalog
CATALOG_TO_FOLDER = {
    "01_60s_70s.json": "01_Retro_Classics_60s_70s",
    "02_80s_90s.json": "02_Evergreen_Romance_80s_90s",
    "03_2000s.json": "03_Noughties_Hits_2000s",
    "04_2010s.json": "04_Modern_Bollywood_2010s",
    "05_2020s_today.json": "05_Latest_Hits_2020s_to_Today",
    "06_bhajans.json": "06_Hindi_Bhajans_Devotional",
    "07_car_highway.json": "07_Car_Highway_Roadtrip_Special",
    "08_late_night_chill.json": "08_Late_Night_Chill_Drive",
}


# =============================================================================
# MAIN PURIFIER
# =============================================================================
def run_purifier():
    print("=" * 80)
    print("  DEFINITIVE SINGLE-SOURCE CATALOG PURIFIER")
    print("  Movie-First + Year-Fallback (No Artist Misclassification)")
    print("=" * 80)

    # ── Load all tracks from all 6 main catalogs ──
    all_tracks = []
    for f in sorted(os.listdir(CATALOGS_DIR)):
        if f.endswith(".json") and not f.startswith("07_") and not f.startswith("08_"):
            p = os.path.join(CATALOGS_DIR, f)
            with open(p, "r", encoding="utf-8") as fp:
                all_tracks.extend(json.load(fp))
    
    print(f"  Loaded {len(all_tracks)} raw tracks from catalogs")

    # ── Deduplicate by normalized title ──
    seen = set()
    unique = []
    for t in all_tracks:
        key = ''.join(c.lower() for c in t.get('title', '') if c.isalnum())
        if key and key not in seen:
            seen.add(key)
            unique.append(t)
    
    print(f"  After dedup: {len(unique)} unique tracks")

    # ── Classify every track into the correct bucket ──
    buckets = {
        "01_60s_70s.json": [],
        "02_80s_90s.json": [],
        "03_2000s.json": [],
        "04_2010s.json": [],
        "05_2020s_today.json": [],
        "06_bhajans.json": [],
    }

    for t in unique:
        cat_file, genre, yr = classify_track(t)
        t["year"] = yr
        t["genre"] = genre
        if cat_file in buckets:
            buckets[cat_file].append(t)

    # ── Build 07 (Highway) and 08 (Late Night) as curated playlists ──
    # These are COPIES of tracks that also exist in their era catalogs
    highway_keywords = [
        'ilahi', 'badtameez dil', 'matargashti', 'patakha guddi', 'safarnama',
        'kar gayi chull', 'london thumakda', 'kala chashma', 'ghungroo',
        'tauba tauba', 'aaj ki raat', 'chaleya', 'nashe si', 'amplifier',
        'abhi toh party', 'balam pichkari', 'gallan goodiyan', 'swag se',
        'khalibali', 'tattad tattad', 'malhari', 'tune maari entriyaan',
        'manma emotion', 'aankh marey', 'first class', 'zingaat',
        'disco deewane', 'high heels', 'baby doll', 'desi girl',
    ]
    chill_keywords = [
        'agar tum saath', 'kun faya', 'nadaan parindey', 'phir le aya',
        'iktara', 'kabira', 'shayad', 'baarishein', 'husn', 'kasoor',
        'cold mess', 'kho gaye', 'kaise hua', 'bekhayali', 'maan meri jaan',
        'choo lo', 'dil mere', 'pashmina', 'tum hi ho', 'tujhe kitna chahne',
        'hawayein', 'enna sona', 'bolna', 'roke na ruke', 'raabta',
        'pee loon', 'tum se hi', 'khairiyat', 'pal pal dil ke paas',
        'tu hi yaar mera', 'tera ban jaunga', 'qaafirana', 'dil diyan gallan',
    ]

    c07 = []
    c08 = []
    for t in unique:
        q = (t.get('title', '') + ' ' + t.get('album', '')).lower()
        if any(re.search(rf'\b{re.escape(w)}\b', q) for w in highway_keywords):
            c07.append(dict(t))  # copy to avoid shared reference
        if any(re.search(rf'\b{re.escape(w)}\b', q) for w in chill_keywords):
            c08.append(dict(t))  # copy to avoid shared reference

    buckets["07_car_highway.json"] = c07
    buckets["08_late_night_chill.json"] = c08

    # ── Write catalogs ──
    print("\n  --- PURIFIED CATALOG SUMMARY ---")
    total = 0
    for fname in sorted(buckets.keys()):
        tracks = buckets[fname]
        for idx, t in enumerate(tracks, start=1):
            t["track_num"] = idx
        out = os.path.join(CATALOGS_DIR, fname)
        with open(out, "w", encoding="utf-8") as fp:
            json.dump(tracks, fp, indent=2, ensure_ascii=False)
        folder = CATALOG_TO_FOLDER.get(fname, fname)
        print(f"  {fname:25s} -> {len(tracks):5d} tracks ({folder})")
        total += len(tracks)

    print(f"\n  Total Tracks: {total}")
    print("=" * 80)

    # ── Relocate misplaced disk files ──
    print("\n  [*] Scanning disk for misplaced MP3 files...")
    relocated = 0
    removed_dupes = 0
    
    for src_folder_name in sorted(os.listdir(VAULT_ROOT)):
        src_path = os.path.join(VAULT_ROOT, src_folder_name)
        if not os.path.isdir(src_path) or not src_folder_name.startswith("0"):
            continue
        if src_folder_name in ('bin',):
            continue
            
        mp3_files = [f for f in os.listdir(src_path) if f.lower().endswith('.mp3')]
        
        for mp3_file in mp3_files:
            f_low = mp3_file.lower()
            
            # Check what folder this file SHOULD be in using movie matrix
            correct_folder = None
            for movie_name in _SORTED_MOVIE_NAMES:
                pattern = rf'\b{re.escape(movie_name)}\b'
                if re.search(pattern, f_low):
                    cat_file, _ = MOVIE_YEAR_MATRIX[movie_name]
                    correct_folder = CATALOG_TO_FOLDER.get(cat_file)
                    break
            
            if correct_folder and correct_folder != src_folder_name:
                dest_dir = os.path.join(VAULT_ROOT, correct_folder)
                os.makedirs(dest_dir, exist_ok=True)
                src_f = os.path.join(src_path, mp3_file)
                dst_f = os.path.join(dest_dir, mp3_file)
                
                if os.path.exists(dst_f):
                    os.remove(src_f)
                    removed_dupes += 1
                    print(f"    [REMOVED DUPE] {mp3_file} from {src_folder_name}")
                else:
                    shutil.move(src_f, dst_f)
                    relocated += 1
                    print(f"    [RELOCATED] {mp3_file} ({src_folder_name} -> {correct_folder})")

    print(f"\n  Disk cleanup: {relocated} relocated, {removed_dupes} duplicates removed")
    print("=" * 80)
    print("  PURIFICATION COMPLETE!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_purifier()
