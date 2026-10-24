r"""
Hindi Music Vault - FFmpeg Auto-Setup Utility
Checks if ffmpeg is in PATH or in D:\Hindi_Music_Vault\bin.
"""

import os
import sys
import shutil
import urllib.request
import zipfile

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
BIN_DIR = os.path.join(VAULT_ROOT, "bin")

FFMPEG_EXE = os.path.join(BIN_DIR, "ffmpeg.exe")
FFPROBE_EXE = os.path.join(BIN_DIR, "ffprobe.exe")

def is_ffmpeg_available():
    # 1. Check local bin
    if os.path.exists(FFMPEG_EXE) and os.path.getsize(FFMPEG_EXE) > 100000:
        return True
    
    # 2. Check system PATH
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return True
        
    return False

def get_ffmpeg_path():
    if os.path.exists(FFMPEG_EXE):
        return BIN_DIR
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return os.path.dirname(system_ffmpeg)
    return BIN_DIR

def download_and_extract_ffmpeg():
    os.makedirs(BIN_DIR, exist_ok=True)
    if is_ffmpeg_available():
        print(" [✓] FFmpeg binaries ready at bin/ folder.")
        return True
        
    print(" [*] Downloading FFmpeg...")
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_path = os.path.join(BIN_DIR, "ffmpeg.zip")
    
    try:
        urllib.request.urlretrieve(url, zip_path)
        print(" [*] Extracting FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                if member.endswith("ffmpeg.exe"):
                    source = zip_ref.open(member)
                    target = open(FFMPEG_EXE, "wb")
                    with source, target:
                        shutil.copyfileobj(source, target)
                elif member.endswith("ffprobe.exe"):
                    source = zip_ref.open(member)
                    target = open(FFPROBE_EXE, "wb")
                    with source, target:
                        shutil.copyfileobj(source, target)
        os.remove(zip_path)
        print(" [✓] FFmpeg downloaded and extracted.")
        return True
    except Exception as e:
        print(f" [!] Failed to download or extract FFmpeg: {e}")
        return False

if __name__ == "__main__":
    download_and_extract_ffmpeg()
