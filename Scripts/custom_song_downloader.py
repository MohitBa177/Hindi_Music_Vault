"""
Hindi Music Vault — Custom Song & Playlist Downloader
Download ANY custom song, singer, movie track, or YouTube/YouTube Music/Playlist link
and automatically organize it into the right folder with car-compatible ID3 tags.
"""

import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_music_engine import download_song, VAULT_ROOT

CATEGORIES = [
    ("01", "01_Retro_Classics_60s_70s", "Classic Bollywood 60s & 70s"),
    ("02", "02_Evergreen_Romance_80s_90s", "Evergreen Romance 80s & 90s"),
    ("03", "03_Noughties_Hits_2000s", "2000s Bollywood Hits"),
    ("04", "04_Modern_Bollywood_2010s", "2010s Modern Bollywood"),
    ("05", "05_Latest_Hits_2020s_to_Today", "Bollywood 2020s Hits"),
    ("06", "06_Hindi_Bhajans_Devotional", "Hindi Devotional / Bhajan"),
    ("07", "07_Car_Highway_Roadtrip_Special", "Car Highway & Roadtrip Hits"),
    ("08", "08_Late_Night_Chill_Drive", "Late Night Chill Drive / Acoustic")
]

def main():
    print("=" * 70)
    print("  🎵 HINDI MUSIC VAULT — CUSTOM SONG & PLAYLIST DOWNLOADER")
    print("=" * 70)
    print("  Download any song or link directly for your car stereo!\n")
    
    query_or_url = input("Enter Song Name / Singer / Movie / YouTube URL: ").strip()
    if not query_or_url:
        print("[!] No input provided. Exiting.")
        return
        
    title = input("Song Title (optional, press Enter to auto-detect): ").strip()
    artist = input("Singer/Artist (optional, press Enter to auto-detect): ").strip()
    year = input("Release Year (optional, e.g. 1995): ").strip()
    
    if not title:
        is_url = query_or_url.startswith("http://") or query_or_url.startswith("https://")
        if not is_url:
            title = query_or_url.split("/")[-1].replace("+", " ").replace("-", " ")
            if len(title) > 40:
                title = title[:40]
    if not artist:
        artist = "Hindi Music" if not (query_or_url.startswith("http://") or query_or_url.startswith("https://")) else ""

    print("\nSelect Target Folder:")
    for idx, (num, folder_name, genre) in enumerate(CATEGORIES, start=1):
        print(f"  [{idx:2d}] {folder_name} ({genre})")
    print("  [ 9] Custom / Root Folder")
    
    choice = input("\nEnter choice [1-9] (Default: 05): ").strip()
    if not choice:
        choice = "5"
        
    try:
        c_idx = int(choice) - 1
        if 0 <= c_idx < len(CATEGORIES):
            selected_folder = os.path.join(VAULT_ROOT, CATEGORIES[c_idx][1])
            selected_genre = CATEGORIES[c_idx][2]
        else:
            selected_folder = VAULT_ROOT
            selected_genre = "Bollywood"
    except ValueError:
        selected_folder = os.path.join(VAULT_ROOT, "05_Latest_Hits_2020s_to_Today")
        selected_genre = "Bollywood 2020s Hits"
        
    song_info = {
        "title": title,
        "artist": artist,
        "year": year,
        "album": os.path.basename(selected_folder),
        "genre": selected_genre,
        "query": query_or_url,
        "is_url": query_or_url.startswith("http://") or query_or_url.startswith("https://")
    }
    
    print(f"\n[*] Downloading '{title}' to {os.path.basename(selected_folder)}...")
    try:
        ok, status, final_file = download_song(song_info, selected_folder, track_index=None)
        if ok:
            print(f"\n[✓] Success! Track saved and tagged for car playback: {final_file}")
        else:
            print(f"\n[!] Download failed: {status}")
    except Exception as e:
        print(f"\n[!] Download failed due to an error: {e}")

if __name__ == "__main__":
    main()
