r"""
Hindi Music Vault — Master Multi-Worker Music Engine
Primary: Studio 320kbps Direct Stream (Zero Bot Checks, Pure CD Quality)
Fallback: YouTube multi-candidate audio extractor
Embedded ID3v2 & HD Album Artwork for Car Infotainment Dashboards.
Supports Multi-Worker Parallel Downloads with UUID thread collision safety.
"""

import os
import sys
import re
import html
import time
import json
import uuid
import subprocess
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

try:
    import mutagen
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC, TCON, TRCK
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mutagen"])
    import mutagen
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC, TCON, TRCK

from setup_ffmpeg import get_ffmpeg_path, is_ffmpeg_available, download_and_extract_ffmpeg

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
CATALOGS_DIR = os.path.join(VAULT_ROOT, "Catalogs")

HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://www.jiosaavn.com/',
    'Origin': 'https://www.jiosaavn.com',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8'
}

def sanitize_filename(name):
    name = html.unescape(name).strip()
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = "".join(ch for ch in name if ch.isprintable())
    name = re.sub(r'\s+', " ", name).strip()
    return name[:150].strip()

def tag_mp3_file(filepath, title, artist, album, year, genre=None, track_num=None, cover_url=None):
    try:
        try:
            audio = EasyID3(filepath)
        except mutagen.id3.ID3NoHeaderError:
            audio = mutagen.File(filepath, easy=True)
            if audio is None:
                return
            audio.add_tags()
            
        audio['title'] = str(title)
        audio['artist'] = str(artist)
        audio['album'] = str(album)
        if year:
            audio['date'] = str(year)
        if genre:
            audio['genre'] = str(genre)
        if track_num:
            audio['tracknumber'] = str(track_num)
        audio.save(v2_version=3)
    except Exception:
        pass

    # Embed HD Album Artwork
    if cover_url:
        try:
            req_img = urllib.request.Request(cover_url, headers=HTTP_HEADERS)
            with urllib.request.urlopen(req_img, timeout=8) as resp:
                image_data = resp.read()
            id3 = ID3(filepath)
            id3.add(APIC(
                encoding=3,
                mime='image/jpeg',
                type=3, # Front Cover
                desc='Cover',
                data=image_data
            ))
            id3.save(v2_version=3)
        except Exception:
            pass

def ensure_ffmpeg():
    if not is_ffmpeg_available():
        download_and_extract_ffmpeg()
    return get_ffmpeg_path()

def download_via_studio_stream(query, target_filepath, ffmpeg_bin):
    """Downloads high quality 320kbps master stream directly from studio CDN."""
    clean_query = query.replace("official song", "").replace("video", "").replace("full song", "").strip()
    search_url = 'https://www.jiosaavn.com/api.php?__call=search.getResults&_format=json&_marker=0&api_version=4&ctx=web6dot0&n=5&p=1&q=' + urllib.parse.quote(clean_query)
    
    req = urllib.request.Request(search_url, headers=HTTP_HEADERS)
    with urllib.request.urlopen(req, timeout=12) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        
    if not data.get('results'):
        return False, "No studio search results", {}
        
    song = data['results'][0]
    enc_media_url = song.get('more_info', {}).get('encrypted_media_url')
    if not enc_media_url:
        return False, "No encrypted media URL", {}
        
    cover_art = (song.get('image') or '').replace("150x150", "500x500")
    
    token_params = {
        '__call': 'song.generateAuthToken',
        'url': enc_media_url,
        'bitrate': '320',
        'api_version': '4',
        '_format': 'json',
        'ctx': 'web6dot0',
        '_marker': '0'
    }
    token_url = 'https://www.jiosaavn.com/api.php?' + urllib.parse.urlencode(token_params)
    req_token = urllib.request.Request(token_url, headers=HTTP_HEADERS)
    with urllib.request.urlopen(req_token, timeout=12) as resp:
        auth_data = json.loads(resp.read().decode('utf-8'))
        stream_url = auth_data.get('auth_url')
        
    if not stream_url:
        return False, "No stream auth URL", {}
        
    # Thread-safe temp file using UUID
    unique_id = uuid.uuid4().hex
    temp_raw = target_filepath + f".tmp_{unique_id}.mp4"
    req_media = urllib.request.Request(stream_url, headers=HTTP_HEADERS)
    with urllib.request.urlopen(req_media, timeout=35) as resp, open(temp_raw, 'wb') as f:
        f.write(resp.read())
        
    if not os.path.exists(temp_raw) or os.path.getsize(temp_raw) < 40000:
        if os.path.exists(temp_raw): os.remove(temp_raw)
        return False, "Stream download corrupted or empty", {}
    
    try:
        temp_target = target_filepath + ".tmp"
        cmd = [ffmpeg_bin, '-y', '-i', temp_raw, '-b:a', '320k', '-vn', temp_target]
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.replace(temp_target, target_filepath)
    finally:
        # ALWAYS clean up raw .mp4 temp file, even if FFmpeg fails
        for tmp in [temp_raw, target_filepath + ".tmp"]:
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except Exception:
                pass
        
    meta = {
        'cover_url': cover_art,
        'official_title': song.get('title'),
        'album': song.get('more_info', {}).get('album'),
        'year': song.get('year')
    }
    return True, "STUDIO_SUCCESS", meta

def download_via_ytdlp_fallback(query_or_url, target_filepath, ffmpeg_bin):
    """Fallback yt-dlp downloader for rare indie / custom URLs."""
    import yt_dlp
    
    target_folder = os.path.dirname(target_filepath)
    unique_id = uuid.uuid4().hex
    temp_template = os.path.join(target_folder, f"temp_{unique_id}_%(id)s.%(ext)s")
    
    if query_or_url.startswith("http://") or query_or_url.startswith("https://"):
        candidate_urls = [query_or_url]
    else:
        search_target = f"ytsearch5:{query_or_url}"
        search_opts = {'extract_flat': True, 'quiet': True, 'no_warnings': True}
        candidate_urls = []
        try:
            with yt_dlp.YoutubeDL(search_opts) as ydl_search:
                results = ydl_search.extract_info(search_target, download=False)
                if results and 'entries' in results:
                    for entry in results['entries']:
                        if entry and entry.get('id'):
                            candidate_urls.append(f"https://www.youtube.com/watch?v={entry['id']}")
        except Exception:
            candidate_urls = [f"ytsearch1:{query_or_url}"]

    last_err = "No YouTube results found"
    for cand in candidate_urls[:3]:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': temp_template,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'noplaylist': True,
            'max_filesize': 50 * 1024 * 1024,  # 50 MB max — no song is 778 MB
            'socket_timeout': 30,               # 30s network timeout
            'match_filter': lambda info, *args: 'Video too long' if info.get('duration', 0) and info['duration'] > 900 else None,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                    'player_skip': ['webpage', 'configs']
                }
            },
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'ffmpeg_location': os.path.dirname(ffmpeg_bin)
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(cand, download=True)
                
            candidates = [f for f in os.listdir(target_folder) if f.startswith(f"temp_{unique_id}_") and f.endswith(".mp3")]
            if candidates:
                downloaded_file = os.path.join(target_folder, candidates[0])
                file_size = os.path.getsize(downloaded_file)
                # Reject files > 50MB (no song is that big) or < 100KB (corrupted)
                if file_size > 50 * 1024 * 1024:
                    os.remove(downloaded_file)
                    last_err = f"YouTube file too large ({file_size // (1024*1024)} MB) - likely wrong video"
                    continue
                if file_size < 100000:
                    os.remove(downloaded_file)
                    last_err = "YouTube file too small - corrupted"
                    continue
                os.replace(downloaded_file, target_filepath)
                return True, "YTDLP_SUCCESS", {}
        except Exception as e:
            last_err = str(e)
            for f in os.listdir(target_folder):
                if f.startswith(f"temp_{unique_id}_"):
                    try: os.remove(os.path.join(target_folder, f))
                    except Exception: pass
            continue
            
    return False, last_err, {}

def _is_remix_or_junk(title, album, artist=""):
    """Returns True for remixes/mixes/jhankar/lofi/karaoke/dialogues/non-Hindi — NOT for remakes."""
    full = f"{title} {album}".lower()
    full_with_artist = f"{title} {album} {artist}".lower()

    # ── Remix/Mix patterns ──
    remix_patterns = [
        r'\bremix\b', r'\bremixed\b', r'\bjhankar\b', r'\blofi\b', r'\blo-fi\b',
        r'\bslowed\b', r'\breverb\b',
        r'\bmashup\b', r'\bmegamix\b', r'\bnonstop\b',
        r'\bclub\s*mix\b', r'\bparty\s*mix\b', r'\bdance\s*mix\b',
        r'\bhouse\s*mix\b', r'\bdj\s*mix\b', r'\bdestiny\s*mix\b',
        r'\b8d\s*audio\b', r'\b8d\b', r'\brevisited\b',
        r'\bkaraoke\b', r'\binstrumental\b',
        r'\brecreated\b', r'\breprise\b',
        r'\bdubstep\b', r'\bedm\b',
        r'\- jb\b', r'\bjb\b$',
        r'\b8[- ]?bit\b', r'\bemulation\b',
    ]
    if any(re.search(p, full) for p in remix_patterns):
        return True

    # ── Dialogue/Non-song patterns ──
    dialogue_patterns = [
        r'\bdialogue?s?\b', r'\bwith\s+dialogue\b',
        r'\bspeaks?\s+and\b', r'\bcommentary\b',
        r'\bscene\b', r'\bvoice\s*over\b',
        r'\bprevue\b', r'\bstrep[cs]ils?\b',
        r'\bintroduction\b',
    ]
    if any(re.search(p, full) for p in dialogue_patterns):
        return True

    # ── Non-Hindi / English junk keywords ──
    non_hindi_keywords = [
        r'\bcover version\b', r'\bin the style of\b', r'\bmade popular by\b',
        r'\bvocal version\b', r'\btv mix\b', r'\btribute\b',
        r'\boriginally performed by\b',
    ]
    if any(re.search(p, full_with_artist) for p in non_hindi_keywords):
        return True

    # ── Known non-Hindi / English / Bhojpuri artists & labels ──
    non_hindi_artists = [
        'hit co. masters', 'ameritz countdown karaoke', 'ameritz karaoke',
        'starlite karaoke', 'party tyme', 'countdown chartbusters',
        "the o'neill brothers", 'classic rock karaoke', 'ronnie hilton',
        'frank fontaine', 'wrathchild america', 'vehicle city radio',
        "world's end girlfriend", 'independent film support group',
        'snuffed on sight', 'the drifters', 'steppenwolf',
        "60's party", "the 60's pop band",
        # Bhojpuri artists
        'khesari lal', 'pawan singh', 'arvind akela', 'ritesh pandey',
        'pramod premi', 'neelkamal singh', 'shilpi raj',
        # South Indian (non-Hindi)
        'anirudh ravichander',
        # English/Western
        'arch bacon', 'alan paul ett',
    ]
    artist_lower = artist.lower()
    if any(a in artist_lower for a in non_hindi_artists):
        return True

    return False

def _fetch_cover_art_url(query):
    """Fetches album cover art URL from JioSaavn search API as a fallback."""
    try:
        clean_q = re.sub(r'(official|song|video|full|audio)', '', query, flags=re.IGNORECASE).strip()
        search_url = 'https://www.jiosaavn.com/api.php?__call=search.getResults&_format=json&_marker=0&api_version=4&ctx=web6dot0&n=3&p=1&q=' + urllib.parse.quote(clean_q)
        req = urllib.request.Request(search_url, headers=HTTP_HEADERS)
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        if data.get('results'):
            img = data['results'][0].get('image', '')
            if img:
                return img.replace("150x150", "500x500").replace("50x50", "500x500")
    except Exception:
        pass
    return None


def _load_skiplist(catalog_filename):
    """Load the skip-list for a catalog. Returns a dict of {track_key: failure_count}."""
    skiplist_path = os.path.join(CATALOGS_DIR, catalog_filename.replace('.json', '_skiplist.json'))
    if os.path.exists(skiplist_path):
        try:
            with open(skiplist_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Migration: old format was a list of strings, new format is a dict
            if isinstance(data, list):
                return {k: 3 for k in data}  # Treat old entries as already maxed
            return data  # dict: {"title|artist": count}
        except Exception:
            pass
    return {}

def _save_skiplist(catalog_filename, skipdict):
    """Save the skip-list dict for a catalog."""
    skiplist_path = os.path.join(CATALOGS_DIR, catalog_filename.replace('.json', '_skiplist.json'))
    try:
        with open(skiplist_path, 'w', encoding='utf-8') as f:
            json.dump(skipdict, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def _add_to_skiplist(catalog_filename, title, artist):
    """Increment failure count for a track. Blacklisted after 3 failures."""
    skipdict = _load_skiplist(catalog_filename)
    key = f"{title}|{artist}"
    skipdict[key] = skipdict.get(key, 0) + 1
    _save_skiplist(catalog_filename, skipdict)
    return skipdict[key]  # Return current failure count

def _is_in_skiplist(skipdict, title, artist):
    """Check if a track is blacklisted (failed 3+ times)."""
    key = f"{title}|{artist}"
    return skipdict.get(key, 0) >= 3

def download_song(song_info, target_folder, track_index=None, ffmpeg_bin="ffmpeg", catalog_filename=None):
    os.makedirs(target_folder, exist_ok=True)
    
    title = song_info.get("title", "Unknown Title")
    artist = song_info.get("artist", "Unknown Artist")
    year = song_info.get("year", "")
    album = song_info.get("album", "Hindi Car Vault")
    genre = song_info.get("genre", "Bollywood")
    query = song_info.get("query", f"{title} {artist} song")

    # ── JUNK FILTER: Skip remixes, non-Hindi, karaoke, English tracks ──
    if _is_remix_or_junk(title, album, artist):
        return True, "SKIPPED_REMIX", None
    
    idx_num = track_index if track_index is not None else song_info.get("track_num")
    prefix = f"{idx_num:03d}. " if idx_num is not None else ""
    year_str = f" ({year})" if year else ""
    clean_title = sanitize_filename(f"{prefix}{artist} - {title}{year_str}")
    final_mp3 = os.path.join(target_folder, f"{clean_title}.mp3")
    
    # ── EXISTENCE CHECK 1: Exact path match ──
    if os.path.exists(final_mp3) and os.path.getsize(final_mp3) > 100000:
        return True, "EXISTS", final_mp3

    # ── EXISTENCE CHECK 2: Title + Artist scan (catches songs at any position) ──
    # Uses BOUNDED matching — "Tere Naam" must match as a complete title,
    # not as a substring of "Tere Naam (Sad)" or "Tere Naam Unplugged".
    sanitized_title_lower = sanitize_filename(title).lower()
    artist_words = set(w.lower() for w in re.split(r'[\s,.\-&]+', artist) if len(w) > 2)
    if sanitized_title_lower and len(sanitized_title_lower) > 3:
        # Build a regex pattern that matches the title as a complete bounded phrase
        title_pattern = re.compile(re.escape(sanitized_title_lower) + r'(?=[\s(.)\-,]|$)', re.IGNORECASE)
        for f in os.listdir(target_folder):
            if not f.lower().endswith(".mp3"):
                continue
            f_lower = f.lower()
            match = title_pattern.search(f_lower)
            if match:
                # Extra check: the matched portion should not be followed by more title words
                # e.g., "Tere Naam" matched in "Tere Naam (Sad)" — check after match
                end_pos = match.end()
                remaining = f_lower[end_pos:].strip()
                # If remaining starts with "(Sad", "(Part", "(Version", "(Duet", "(Female", etc.
                # then it's a DIFFERENT song variant — skip this match
                if remaining and re.match(r'^\(?\s*(sad|happy|part|version|duet|female|male|unplugged|acoustic|remix|ii|iii|2|3)', remaining):
                    continue  # Different variant, not the same song
                fpath = os.path.join(target_folder, f)
                if os.path.getsize(fpath) > 100000:
                    artist_match = any(aw in f_lower for aw in artist_words if len(aw) > 3)
                    if artist_match or not artist_words:
                        return True, "EXISTS", fpath

    # ── EXISTENCE CHECK 3: Same index + bounded title check (NO deletion — just detect) ──
    if idx_num is not None:
        prefix_2d = f"{idx_num:02d}. "
        prefix_3d = f"{idx_num:03d}. "
        prefix_1d = f"{idx_num}. "
        for f in os.listdir(target_folder):
            if not f.lower().endswith(".mp3"):
                continue
            if f.startswith(prefix_2d) or f.startswith(prefix_3d) or f.startswith(prefix_1d):
                fpath = os.path.join(target_folder, f)
                if os.path.getsize(fpath) > 100000:
                    # Use BOUNDED matching (same logic as Check 2) — not plain substring
                    f_lower = f.lower()
                    if sanitized_title_lower and len(sanitized_title_lower) > 3:
                        title_re = re.compile(re.escape(sanitized_title_lower) + r'(?=[\s(.\)\-,]|$)', re.IGNORECASE)
                        chk3_match = title_re.search(f_lower)
                        if chk3_match:
                            # Reject variant matches like "(Sad)", "(Part 2)", etc.
                            remaining = f_lower[chk3_match.end():].strip()
                            if remaining and re.match(r'^\(?\s*(sad|happy|part|version|duet|female|male|unplugged|acoustic|remix|ii|iii|2|3)', remaining):
                                continue  # Different variant — not the same song
                            return True, "EXISTS", fpath

    # ── Download (with 1 retry for transient failures) ──
    cover_art = None
    last_err = "Unknown error"
    source = "UNKNOWN"
    for attempt in range(2):  # Try up to 2 times
        try:
            ok, msg, meta = download_via_studio_stream(query, final_mp3, ffmpeg_bin)
            if ok:
                cover_art = meta.get('cover_url')
                source = "JIOSAAVN"
                break
            else:
                last_err = msg
                try:
                    ok, msg, meta = download_via_ytdlp_fallback(query, final_mp3, ffmpeg_bin)
                    if ok:
                        source = "YOUTUBE"
                        break
                    last_err = msg
                except Exception as yt_e:
                    last_err = f"yt-dlp fallback failed: {yt_e}"
        except Exception as e:
            last_err = str(e)
            try:
                ok, msg, meta = download_via_ytdlp_fallback(query, final_mp3, ffmpeg_bin)
                if ok:
                    source = "YOUTUBE"
                    break
                last_err = msg
            except Exception as yt_e:
                last_err = f"yt-dlp fallback failed: {yt_e}"
        
        if attempt == 0 and not ok:
            time.sleep(3)  # Wait before retry

    if ok and os.path.exists(final_mp3):
        # -- COVER ART FALLBACK: If studio/yt-dlp did not provide cover, fetch from JioSaavn --
        if not cover_art:
            cover_art = _fetch_cover_art_url(query)
        tag_mp3_file(
            filepath=final_mp3,
            title=title,
            artist=artist,
            album=album,
            year=year,
            genre=genre,
            track_num=idx_num,
            cover_url=cover_art
        )
        # -- EMBED SOURCE TAG in ID3 comment --
        try:
            from mutagen.id3 import COMM
            id3 = ID3(final_mp3)
            id3.add(COMM(encoding=3, lang='eng', desc='source', text=source))
            id3.save(v2_version=3)
        except Exception:
            pass
        return True, f"DOWNLOADED|{source}", final_mp3
    else:
        return False, last_err, None


def _renumber_folder_sequential(target_folder):
    """Renumber all MP3s in a folder to be sequential (001, 002, 003...) with no gaps.
    Also updates the ID3 tracknumber tag to match the new serial number.
    Sorts by current serial number to preserve ordering."""
    import re as _re
    mp3s = [f for f in os.listdir(target_folder) if f.lower().endswith('.mp3')]
    if not mp3s:
        return 0

    # Parse serial numbers and sort
    numbered = []
    for f in mp3s:
        m = _re.match(r'^(\d{1,4})\.\s*(.+)$', f)
        if m:
            numbered.append((int(m.group(1)), m.group(2), f))
        else:
            numbered.append((999999, f, f))  # No serial = put at end

    numbered.sort(key=lambda x: x[0])

    # Check if already sequential
    needs_fix = False
    for new_idx, (old_num, _, _) in enumerate(numbered, 1):
        if old_num != new_idx:
            needs_fix = True
            break

    if not needs_fix:
        # Even if filenames are sequential, fix any mismatched ID3 track numbers
        _sync_id3_track_numbers(target_folder)
        return 0

    # Phase 1: Rename all to temp names (avoid collisions)
    temp_map = []
    for new_idx, (old_num, content_part, original_name) in enumerate(numbered, 1):
        if old_num == new_idx:
            continue  # Already correct
        old_path = os.path.join(target_folder, original_name)
        temp_name = f"__RENUM_{new_idx:03d}__" + original_name
        temp_path = os.path.join(target_folder, temp_name)
        new_name = f"{new_idx:03d}. {content_part}"
        new_path = os.path.join(target_folder, new_name)
        if os.path.exists(old_path):
            os.rename(old_path, temp_path)
            temp_map.append((temp_path, new_path, new_idx))

    # Phase 2: Rename from temp to final + update ID3 track number
    renamed = 0
    for temp_path, new_path, new_idx in temp_map:
        if os.path.exists(temp_path):
            os.rename(temp_path, new_path)
            _update_track_number(new_path, new_idx)
            renamed += 1

    # Also sync any files that were already correct but might have wrong ID3
    _sync_id3_track_numbers(target_folder)
    return renamed

def _update_track_number(filepath, track_num):
    """Update the ID3 tracknumber tag of an MP3 file."""
    try:
        audio = EasyID3(filepath)
        audio['tracknumber'] = str(track_num)
        audio.save(v2_version=3)
    except Exception:
        try:
            audio = mutagen.File(filepath, easy=True)
            if audio is not None:
                audio['tracknumber'] = str(track_num)
                audio.save(v2_version=3)
        except Exception:
            pass

def _sync_id3_track_numbers(target_folder):
    """Sync ID3 tracknumber tags to match filename serial numbers for all MP3s."""
    import re as _re
    for f in os.listdir(target_folder):
        if not f.lower().endswith('.mp3'):
            continue
        m = _re.match(r'^(\d{1,4})\.\s', f)
        if not m:
            continue
        serial = int(m.group(1))
        filepath = os.path.join(target_folder, f)
        try:
            audio = EasyID3(filepath)
            current = audio.get('tracknumber', [None])[0]
            if current != str(serial):
                audio['tracknumber'] = str(serial)
                audio.save(v2_version=3)
        except Exception:
            try:
                audio = mutagen.File(filepath, easy=True)
                if audio is not None:
                    audio['tracknumber'] = str(serial)
                    audio.save(v2_version=3)
            except Exception:
                pass

def batch_download_from_catalog(catalog_filename, folder_rel_name, collection_name, max_workers=4, limit=None):
    """
    Downloads songs from a catalog JSON with multi-worker concurrency and smart progress display.
    Features: source tagging, skip-list for failed songs, thread timeouts, proper completion.
    """
    catalog_path = os.path.join(CATALOGS_DIR, catalog_filename)
    if not os.path.exists(catalog_path):
        print(f"[!] Catalog file not found: {catalog_path}")
        return 0

    with open(catalog_path, "r", encoding="utf-8") as f:
        tracklist = json.load(f)

    if limit:
        tracklist = tracklist[:limit]

    target_folder = os.path.join(VAULT_ROOT, folder_rel_name)
    os.makedirs(target_folder, exist_ok=True)

    # ── Load skip-list (dict with failure counts) ──
    skipset = _load_skiplist(catalog_filename)

    print("\n" + "=" * 70)
    print(f"  HINDI CAR MUSIC VAULT -- {collection_name.upper()}")
    print(f"  Destination: {target_folder}")
    print(f"  Total Catalog Tracks: {len(tracklist)} | Workers: {max_workers}x | Skipped (blacklist): {len(skipset)}")
    print("=" * 70 + "\n")
    sys.stdout.flush()

    success = 0
    already_had = 0
    failed = 0
    skipped_remix = 0
    skipped_blacklist = 0
    from_jiosaavn = 0
    from_youtube = 0
    total = len(tracklist)

    ffmpeg_dir = ensure_ffmpeg()
    global_ffmpeg_bin = os.path.join(ffmpeg_dir, "ffmpeg.exe") if ffmpeg_dir else "ffmpeg"

    def worker_task(item_idx_pair):
        idx, item = item_idx_pair
        ok, status, final_file = download_song(item, target_folder, track_index=idx, ffmpeg_bin=global_ffmpeg_bin, catalog_filename=catalog_filename)
        return idx, item, ok, status, final_file

    # ── Filter out blacklisted tracks before submitting ──
    tasks_to_submit = []
    for i, t in enumerate(tracklist, start=1):
        t_title = t.get('title', '')
        t_artist = t.get('artist', '')
        if _is_in_skiplist(skipset, t_title, t_artist):
            skipped_blacklist += 1
            continue
        tasks_to_submit.append((i, t))

    if skipped_blacklist > 0:
        print(f"  [SKIPLIST] {skipped_blacklist} tracks skipped (previously failed, in blacklist)")
        print(f"  [SKIPLIST] To retry them, delete: {catalog_filename.replace('.json', '_skiplist.json')}")
        print()
        sys.stdout.flush()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(worker_task, pair): pair[0] for pair in tasks_to_submit}
        for future in as_completed(futures):
            try:
                idx, item, ok, status, final_file = future.result(timeout=180)
            except TimeoutError:
                crashed_idx = futures[future]
                crashed_item = tracklist[crashed_idx - 1]
                c_title = crashed_item.get('title', 'Unknown')
                c_artist = crashed_item.get('artist', 'Unknown')
                failed += 1
                fail_count = _add_to_skiplist(catalog_filename, c_title, c_artist)
                bl_tag = " [BLACKLISTED]" if fail_count >= 3 else f" [fail {fail_count}/3]"
                print(f"  [{crashed_idx:03d}/{total:03d}] [TIMEOUT]{bl_tag} {c_artist} - {c_title}: exceeded 3 min limit")
                sys.stdout.flush()
                continue
            except Exception as exc:
                crashed_idx = futures[future]
                crashed_item = tracklist[crashed_idx - 1]
                c_title = crashed_item.get('title', 'Unknown')
                c_artist = crashed_item.get('artist', 'Unknown')
                failed += 1
                fail_count = _add_to_skiplist(catalog_filename, c_title, c_artist)
                bl_tag = " [BLACKLISTED]" if fail_count >= 3 else f" [fail {fail_count}/3]"
                print(f"  [{crashed_idx:03d}/{total:03d}] [CRASHED]{bl_tag} {c_artist} - {c_title}: {str(exc)[:80]}")
                sys.stdout.flush()
                continue
            title = item.get('title', 'Unknown')
            artist = item.get('artist', 'Unknown')
            year = item.get('year', '')
            
            if ok:
                if status == "SKIPPED_REMIX":
                    skipped_remix += 1
                elif status == "EXISTS":
                    already_had += 1
                    print(f"  [{idx:03d}/{total:03d}] [ALREADY EXISTS] {artist} - {title} ({year})")
                else:
                    success += 1
                    size_mb = os.path.getsize(final_file) / (1024 * 1024) if final_file and os.path.exists(final_file) else 0
                    # Parse source from status
                    source_tag = ""
                    if "|JIOSAAVN" in status:
                        from_jiosaavn += 1
                        source_tag = " [JioSaavn]"
                    elif "|YOUTUBE" in status:
                        from_youtube += 1
                        source_tag = " [YouTube]"
                    print(f"  [{idx:03d}/{total:03d}] [DOWNLOADED 320k]{source_tag} {artist} - {title} ({year}) -- {size_mb:.1f} MB")
            else:
                failed += 1
                fail_count = _add_to_skiplist(catalog_filename, title, artist)
                bl_tag = " [BLACKLISTED]" if fail_count >= 3 else f" [fail {fail_count}/3]"
                print(f"  [{idx:03d}/{total:03d}] [FAILED]{bl_tag} {artist} - {title}: {status[:50]}")
            sys.stdout.flush()

    # ── RENUMBER: Make serial numbers sequential (no gaps) ──
    renumbered = _renumber_folder_sequential(target_folder)
    if renumbered > 0:
        print(f"\n  [RENUMBER] {renumbered} files renumbered to fill gaps")
        sys.stdout.flush()

    # ── COMPLETION MESSAGE ──
    print("\n" + "-" * 70)
    print(f"  {collection_name} -- COMPLETED!")
    print(f"     Newly Downloaded  : {success} (JioSaavn: {from_jiosaavn}, YouTube: {from_youtube})")
    print(f"     Already in Vault  : {already_had}")
    print(f"     Skipped (Remix)   : {skipped_remix}")
    print(f"     Skipped (Blacklist): {skipped_blacklist}")
    print(f"     Failed            : {failed}")
    print(f"     Total Available   : {success + already_had}/{total}")
    print("-" * 70)
    print(f"  *** PLAYLIST COMPLETE ***")
    print("-" * 70 + "\n")
    sys.stdout.flush()
    return success + already_had
