"""
Cover Art Patcher — Hindi Music Vault
Scans all MP3s, finds ones missing cover art, fetches from JioSaavn, embeds in-place.
No audio is touched — only the APIC (image) ID3 tag is added.
"""

import os
import sys
import re
import json
import time
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

try:
    import mutagen
    from mutagen.id3 import ID3, APIC, ID3NoHeaderError
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mutagen"])
    from mutagen.id3 import ID3, APIC, ID3NoHeaderError

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://www.jiosaavn.com/',
    'Origin': 'https://www.jiosaavn.com',
    'Accept': '*/*',
}

# All music folders
MUSIC_FOLDERS = [
    "01_Retro_Classics_60s_70s",
    "02_Evergreen_Romance_80s_90s",
    "03_Noughties_Hits_2000s",
    "04_Modern_Bollywood_2010s",
    "05_Latest_Hits_2020s_to_Today",
    "06_Hindi_Bhajans_Devotional",
    "07_Car_Highway_Roadtrip_Special",
    "08_Late_Night_Chill_Drive",
]


def has_cover_art(filepath):
    """Check if MP3 already has an embedded cover image."""
    try:
        tags = ID3(filepath)
        for tag in tags.values():
            if isinstance(tag, APIC) and len(tag.data) > 1000:
                return True
    except Exception:
        pass
    return False


def extract_search_query(filepath):
    """Extract a search query from MP3 ID3 tags or filename."""
    # Try ID3 tags first
    try:
        tags = ID3(filepath)
        title = str(tags.get('TIT2', ''))
        artist = str(tags.get('TPE1', ''))
        if title and artist:
            return f"{title} {artist}".strip()
        if title:
            return title.strip()
    except Exception:
        pass

    # Fallback: parse filename
    # Format: "001. Artist - Title (Year).mp3"
    basename = os.path.splitext(os.path.basename(filepath))[0]
    # Remove track number prefix
    basename = re.sub(r'^\d{1,3}\.\s*', '', basename)
    # Remove year suffix
    basename = re.sub(r'\s*\(\d{4}\)\s*$', '', basename)
    return basename.strip()


def fetch_cover_art_url(query):
    """Query JioSaavn and return HD cover art URL."""
    try:
        clean_q = re.sub(r'(official|song|video|full|audio)', '', query, flags=re.IGNORECASE).strip()
        search_url = (
            'https://www.jiosaavn.com/api.php?__call=search.getResults'
            '&_format=json&_marker=0&api_version=4&ctx=web6dot0&n=3&p=1&q='
            + urllib.parse.quote(clean_q)
        )
        req = urllib.request.Request(search_url, headers=HTTP_HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        if data.get('results'):
            img = data['results'][0].get('image', '')
            if img:
                return img.replace("150x150", "500x500").replace("50x50", "500x500")
    except Exception:
        pass
    return None


def embed_cover_art(filepath, cover_url):
    """Download cover image and embed into MP3."""
    try:
        req_img = urllib.request.Request(cover_url, headers=HTTP_HEADERS)
        with urllib.request.urlopen(req_img, timeout=10) as resp:
            image_data = resp.read()

        if len(image_data) < 2000:
            return False, "Image too small"

        try:
            tags = ID3(filepath)
        except ID3NoHeaderError:
            tags = ID3()

        tags.add(APIC(
            encoding=3,
            mime='image/jpeg',
            type=3,  # Front Cover
            desc='Cover',
            data=image_data
        ))
        tags.save(filepath, v2_version=3)
        return True, f"{len(image_data) // 1024} KB"
    except Exception as e:
        return False, str(e)[:60]


def patch_single(filepath):
    """Patch a single MP3 with cover art. Returns (filepath, success, message)."""
    if has_cover_art(filepath):
        return filepath, True, "ALREADY_HAS_COVER"

    query = extract_search_query(filepath)
    if not query or len(query) < 4:
        return filepath, False, "NO_QUERY"

    cover_url = fetch_cover_art_url(query)
    if not cover_url:
        return filepath, False, "NO_COVER_FOUND"

    ok, msg = embed_cover_art(filepath, cover_url)
    if ok:
        return filepath, True, f"PATCHED ({msg})"
    else:
        return filepath, False, f"EMBED_FAILED: {msg}"


def main():
    print("\n" + "=" * 70)
    print("  COVER ART PATCHER — Hindi Music Vault")
    print("  Scanning all folders for MP3s missing cover art...")
    print("=" * 70)

    # Collect all MP3s
    all_mp3s = []
    for folder_name in MUSIC_FOLDERS:
        folder_path = os.path.join(VAULT_ROOT, folder_name)
        if not os.path.exists(folder_path):
            continue
        for f in sorted(os.listdir(folder_path)):
            if f.lower().endswith('.mp3'):
                all_mp3s.append((folder_name, os.path.join(folder_path, f)))

    print(f"\n  Total MP3 files found: {len(all_mp3s)}")

    # Phase 1: Quick scan to find which ones need patching
    print("\n  Phase 1: Checking existing cover art...\n")
    needs_patch = []
    already_ok = 0
    for folder_name, fpath in all_mp3s:
        if has_cover_art(fpath):
            already_ok += 1
        else:
            needs_patch.append((folder_name, fpath))

    print(f"  Already have cover art : {already_ok}")
    print(f"  Need patching          : {len(needs_patch)}")

    if not needs_patch:
        print("\n  All MP3s already have cover art! Nothing to do.")
        return

    # Phase 2: Patch missing cover art with parallel workers
    print(f"\n  Phase 2: Fetching & embedding cover art (4 workers)...\n")

    patched = 0
    failed = 0
    total = len(needs_patch)
    start_time = time.time()

    def worker(item):
        folder_name, fpath = item
        return folder_name, patch_single(fpath)

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(worker, item): item for item in needs_patch}
        for i, future in enumerate(as_completed(futures), 1):
            try:
                folder_name, (fpath, ok, msg) = future.result()
                basename = os.path.basename(fpath)
                short_folder = folder_name.split('_')[0]

                if ok and msg != "ALREADY_HAS_COVER":
                    patched += 1
                    print(f"  [{i:4d}/{total}] [{short_folder}] [+COVER] {basename[:65]}  ({msg})")
                elif not ok:
                    failed += 1
                    print(f"  [{i:4d}/{total}] [{short_folder}] [MISSED] {basename[:65]}  ({msg})")
            except Exception as e:
                failed += 1
                item = futures[future]
                print(f"  [{i:4d}/{total}] [CRASH] {os.path.basename(item[1])[:65]}  ({str(e)[:40]})")

    elapsed = time.time() - start_time
    print("\n" + "-" * 70)
    print(f"  COVER ART PATCHER — Complete!")
    print(f"     Patched with cover art : {patched}")
    print(f"     Could not find cover   : {failed}")
    print(f"     Already had cover      : {already_ok}")
    print(f"     Time taken             : {elapsed:.0f} seconds")
    print("-" * 70 + "\n")


if __name__ == "__main__":
    main()
