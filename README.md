# 🚗 Hindi Car Music Vault — Bollywood Archive (4,283 Verified Tracks | 1950–2026)

A fully automated, high-fidelity (320kbps MP3) Bollywood music library with **4,283 verified master tracks** organized by era. Built for car infotainment systems with embedded HD album artwork, proper ID3 tags, and 1-click USB sync.

> **Zero manual work.** Run one `.bat` file, go to sleep, wake up with your entire Bollywood library sorted, tagged, and artwork-embedded — ready for your car USB.

---

## 📁 Folder Structure

```
Hindi_Music_Vault\
│
├── 📁 01_Retro_Classics_60s_70s\        →  795 Tracks (1950–1979: Lata, Rafi, Kishore, Mukesh, RD Burman)
├── 📁 02_Evergreen_Romance_80s_90s\     →  928 Tracks (1980–1999: Kumar Sanu, Udit, Alka, Sonu, AR Rahman)
├── 📁 03_Noughties_Hits_2000s\          →  711 Tracks (2000–2009: KK, Shreya, Sunidhi, Mohit, Atif)
├── 📁 04_Modern_Bollywood_2010s\        →  749 Tracks (2010–2019: Arijit, Badshah, Neha Kakkar, Pritam)
├── 📁 05_Latest_Hits_2020s_to_Today\    →  700 Tracks (2020–2026: Animal, Stree 2, Pushpa 2, Jawan)
├── 📁 06_Hindi_Bhajans_Devotional\      →  255 Tracks (Hanuman Chalisa, Gayatri Mantra, Aartis)
├── 📁 07_Car_Highway_Roadtrip_Special\  →   47 Tracks (High Energy Driving: ZNMD, YJHD, Highway)
├── 📁 08_Late_Night_Chill_Drive\        →   98 Tracks (Midnight Soul: Anuv Jain, Prateek Kuhad)
│
├── 📁 Catalogs\          → 8 JSON catalogs with verified release years
├── 📁 Scripts\           → Download engine + per-playlist scripts
├── 📁 bin\               → FFmpeg binaries (auto-downloaded on first run)
│
├── 🚀 DOWNLOAD_ALL_MASTER.bat    → 1-Click download all 4,283 tracks
├── 🚗 SYNC_TO_CAR_USB.bat        → 1-Click USB exporter for car
└── 📄 README.md
```

---

## ⚡ Quick Start

### Prerequisites

| Requirement | Details |
|---|---|
| **Python** | 3.10 or higher with pip |
| **FFmpeg** | Auto-downloaded to `bin\` on first run — no manual install needed |
| **Internet** | Required for downloading tracks |
| **Disk Space** | ~50 GB for the full 4,283-track library at 320kbps |

Python packages (`mutagen`, `yt-dlp`) are auto-installed on first run if missing.

### Download Everything (Recommended)

```bash
# Double-click or run from terminal:
DOWNLOAD_ALL_MASTER.bat
```

This downloads all 4,283 tracks across all 8 playlists sequentially. Takes ~6–10 hours on a decent connection.

### Download a Specific Playlist

```bash
python Scripts\01_download_60s_70s.py      # 795 retro classics
python Scripts\02_download_80s_90s.py      # 928 evergreen hits
python Scripts\03_download_2000s.py        # 711 noughties tracks
python Scripts\04_download_2010s.py        # 749 modern bollywood
python Scripts\05_download_2020s_today.py  # 700 latest hits
python Scripts\06_download_bhajans.py      # 255 devotional tracks
python Scripts\07_download_car_highway.py  # 47 road trip bangers
python Scripts\08_download_late_night_chill.py  # 98 midnight vibes
```

### Download a Custom Song

```bash
python Scripts\custom_song_downloader.py
# Then enter: "Tum Hi Ho Arijit Singh" → downloads, tags, and embeds cover art
```

### Resume Anytime

The engine **skips already-downloaded tracks** in milliseconds. Stop and restart whenever you want — it picks up right where you left off. No re-downloads, no duplicates.

---

## 🔧 How the Engine Works

### Download Pipeline

```
Catalog JSON → Junk Filter → Existence Check → Download → Tag → Renumber
```

1. **Catalog JSON** — Each playlist has a curated catalog (`Catalogs/*.json`) with title, artist, album, year, and search query for every track.

2. **Junk Filter** — Before downloading, the engine checks the title/album/artist against 40+ regex patterns. Remixes, Jhankar, LoFi, karaoke, dialogues, and non-Hindi tracks are silently skipped.

3. **3-Tier Existence Check** — Prevents re-downloading:
   - **Check 1**: Exact file path match (fastest)
   - **Check 2**: Bounded title + artist regex scan across the folder (catches renamed/moved files)
   - **Check 3**: Same serial number + bounded title match (catches index shifts)
   
   > **Bounded matching** means "Tere Naam" will NOT falsely match "Tere Naam (Sad)" — each title must match as a complete phrase, not a substring. Variant suffixes like `(Sad)`, `(Part 2)`, `(Duet)`, `(Unplugged)` are detected and excluded.

4. **Dual-Source Download**:
   - **Primary**: JioSaavn 320kbps studio CDN — pure CD quality, zero bot checks
   - **Fallback**: YouTube best audio via yt-dlp → FFmpeg 320kbps transcode
   - Each download attempt retries once (3-second delay) before marking as failed

5. **ID3 Tagging** — Every MP3 gets:
   - Title, Artist, Album, Year, Genre, Track Number
   - HD 500×500 album cover art (JPEG embedded as APIC frame)
   - Source comment tag (`JioSaavn` or `YouTube`)

6. **Auto Renumber** — After each playlist completes, serial numbers are made sequential (001, 002, 003...) with no gaps. ID3 track number tags are synced to match.

### Multi-Worker Architecture

- **4 parallel download threads** (configurable via `max_workers`)
- **UUID-based temp files** prevent thread collisions
- **3-minute timeout** per download — no single stuck song blocks the playlist
- **Thread-safe skiplist** writes with load-increment-save pattern

### 3-Failure Skiplist (Smart Retry)

Failed songs are NOT immediately blacklisted. The engine uses a **3-strike system**:

| Failure Count | Behavior |
|---|---|
| 1st failure | Logged as `[fail 1/3]` — will retry on next run |
| 2nd failure | Logged as `[fail 2/3]` — will retry on next run |
| 3rd failure | Logged as `[BLACKLISTED]` — skipped on all future runs |

Skiplist files are stored as `Catalogs/*_skiplist.json` with failure counts:
```json
{
  "Some Song|Some Artist": 2,
  "Another Song|Another Artist": 3
}
```

To reset a blacklisted song, delete the skiplist file or edit the count back to 0.

---

## 🛡️ Built-in Protections

| Feature | Description |
|---|---|
| **Dual Source** | Primary: JioSaavn 320kbps studio CDN. Fallback: YouTube best audio |
| **Source Tagging** | Each download shows `[JioSaavn]` or `[YouTube]` — also embedded in ID3 comment tag |
| **Junk Filter** | 40+ regex patterns block remixes, Jhankar, LoFi, slowed+reverb, karaoke, dialogues, instrumentals, 8-bit, mashups, non-Hindi |
| **Bounded Title Matching** | 3-tier existence check with regex word boundaries — "Tere Naam" ≠ "Tere Naam (Sad)" |
| **Cover Art Fallback** | If download source has no artwork, fetches HD 500×500 cover from JioSaavn search API |
| **3-Strike Skiplist** | Songs blacklisted only after 3 failures — retries twice before giving up |
| **Thread Timeout** | 3-minute timeout per download thread — no more stuck playlists |
| **File Size Guard** | Rejects YouTube files >50MB (wrong video) or <100KB (corrupted) |
| **Duration Filter** | Skips YouTube videos >15 minutes (compilations, not songs) |
| **Auto Renumber** | Serial numbers auto-adjusted after each run — no gaps from skipped/failed songs |
| **ID3 Track Sync** | ID3 `tracknumber` tag always matches filename serial number |
| **Download Retry** | Each song retries once (3s delay) before marking as failed |
| **Completion Message** | `*** PLAYLIST COMPLETE ***` always printed with flush — you always know when it's done |

---

## 🎵 What Gets Filtered Out

### ❌ Blocked (auto-skipped silently):
- Remixes, DJ mixes, Jhankar Beats, club/party/dance/house/destiny mixes
- Slowed, reverb, LoFi, lo-fi, 8D audio, 8-bit emulations
- Mashups, megamix, nonstop mixes, dubstep, EDM
- Karaoke, instrumental, recreated, reprise, revisited versions
- Dialogues, commentary, voiceovers, scenes, introductions
- Bhojpuri artists (Khesari Lal, Pawan Singh, etc.)
- English/Western cover versions and tribute tracks
- Known junk labels (Ameritz, Hit Co. Masters, Starlite Karaoke, etc.)

### ✅ Kept:
- Original movie songs ✅
- Remakes for new movies (e.g., "Tamma Tamma Again" from Badrinath Ki Dulhania) ✅
- Pre-1960 Golden Era classics in the 60s/70s folder ✅

---

## 🚗 Car USB Sync

### Quick Sync
```bash
# Double-click or run:
SYNC_TO_CAR_USB.bat
```

### Storage Guide

| Preset | Tracks | Approx Size | USB Drive |
|---|---|---|---|
| **Complete Archive** | 4,283 | ~42 GB | 64 GB |
| **Decades Only (01–05)** | 3,883 | ~38 GB | 64 GB |
| **Top Favorites** | ~2,000 | ~20 GB | 32 GB |
| **Devotional + Roadtrip** | 400 | ~4 GB | 8 GB |

**USB Format:** FAT32 or exFAT for maximum car head unit compatibility.

### 🎛️ Car Infotainment Compatibility

- **320 kbps MP3** — Universal format, works on all car head units (Maruti SmartPlay, Hyundai BlueLink, Tata Harman, Mahindra AdrenoX, Toyota, Honda, Kia, MG)
- **Full ID3v2.3 Tags** — Song title, artist, album, year, genre, track number all embedded
- **HD Album Cover Art** — 500×500 JPEG front cover embedded in every MP3 for dashboard display
- **Sequential Numbering** — `001, 002, 003...` ensures correct playback order on all car systems
- **Source Tag** — ID3 comment field records whether each track came from JioSaavn or YouTube

---

## 📂 Project Files

### Scripts

| File | Purpose |
|---|---|
| `Scripts/common_music_engine.py` | Core download engine — all 8 playlists use this single engine |
| `Scripts/01-08_download_*.py` | Per-playlist download scripts (call the common engine) |
| `Scripts/build_master_catalogs.py` | Generates catalog JSONs from the movie database |
| `Scripts/expand_catalogs.py` | Expands catalogs with additional discovered tracks |
| `Scripts/ultimate_movie_matrix_purifier.py` | Era classification engine with 250+ movie matrix |
| `Scripts/cover_art_patcher.py` | Batch-patches cover art on existing MP3s missing artwork |
| `Scripts/custom_song_downloader.py` | Interactive single-song downloader |
| `Scripts/usb_car_sync.py` | Syncs library to USB drive with folder selection |
| `Scripts/setup_ffmpeg.py` | Auto-downloads and extracts FFmpeg binary |

### Catalogs

| File | Tracks | Era |
|---|---|---|
| `01_60s_70s.json` | 795 | 1950–1979 |
| `02_80s_90s.json` | 928 | 1980–1999 |
| `03_2000s.json` | 711 | 2000–2009 |
| `04_2010s.json` | 749 | 2010–2019 |
| `05_2020s_today.json` | 700 | 2020–2026 |
| `06_bhajans.json` | 255 | Devotional (all eras) |
| `07_car_highway.json` | 47 | Road trip energy (curated) |
| `08_late_night_chill.json` | 98 | Midnight drive (curated) |

Each catalog entry contains:
```json
{
  "title": "Tujhe Dekha Toh Yeh Jaana Sanam",
  "artist": "Kumar Sanu, Lata Mangeshkar",
  "album": "Dilwale Dulhania Le Jayenge",
  "year": "1995",
  "genre": "Bollywood",
  "query": "Tujhe Dekha Toh Yeh Jaana Sanam Kumar Sanu Lata Mangeshkar song"
}
```

### Recovery Folders

| Folder | Purpose |
|---|---|
| `_cleanup_removed/` | Songs removed by junk filter (recoverable) |
| `_wrong_era_removed/` | Songs moved out of wrong decade folder (recoverable) |
| `_orphan_songs/` | Files with no matching catalog entry (recoverable) |

---

## 🔄 Updating the Library

### Add New Songs to a Catalog

1. Edit the catalog JSON (e.g., `Catalogs/05_2020s_today.json`)
2. Add a new entry with title, artist, album, year, genre, query
3. Run the playlist script — only the new song downloads

### Re-run After Updates

```bash
# Re-run any playlist — only missing songs download
python Scripts\03_download_2000s.py
```

The engine detects existing files in milliseconds and skips them. Only genuinely missing tracks are downloaded.

### Reset Failed Songs

Delete the skiplist file to retry all previously-failed songs:
```bash
del Catalogs\03_2000s_skiplist.json
python Scripts\03_download_2000s.py
```

---

## 📜 License

Personal use only. All music content belongs to respective copyright holders. This tool is a personal archival utility — please support the artists by streaming on official platforms.
