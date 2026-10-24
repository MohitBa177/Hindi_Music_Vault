"""
Hindi Music Vault — Car USB Sync & Exporter (Ultimate 5,292 Track Archive)
Detects plugged-in USB pen drives, calculates space, and syncs your Hindi music & bhajans
directly to your USB drive for car stereo playback (Android Auto, Apple CarPlay, or USB Head Unit).
"""

import os
import sys
import shutil
import string

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

CATEGORIES = [
    "01_Retro_Classics_60s_70s",
    "02_Evergreen_Romance_80s_90s",
    "03_Noughties_Hits_2000s",
    "04_Modern_Bollywood_2010s",
    "05_Latest_Hits_2020s_to_Today",
    "06_Hindi_Bhajans_Devotional",
    "07_Car_Highway_Roadtrip_Special",
    "08_Late_Night_Chill_Drive"
]

def get_removable_drives():
    drives = []
    try:
        import psutil
        for part in psutil.disk_partitions():
            if 'removable' in part.opts or part.device.upper().startswith(('E:', 'F:', 'G:', 'H:', 'I:', 'J:', 'K:', 'U:')):
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    free_gb = usage.free / (1024 ** 3)
                    total_gb = usage.total / (1024 ** 3)
                    drives.append({
                        'letter': part.mountpoint,
                        'free_gb': free_gb,
                        'total_gb': total_gb,
                        'device': part.device
                    })
                except Exception:
                    pass
    except Exception:
        for letter in string.ascii_uppercase:
            path = f"{letter}:\\"
            if os.path.exists(path) and letter not in ('C', 'D'):
                try:
                    total, used, free = shutil.disk_usage(path)
                    drives.append({
                        'letter': path,
                        'free_gb': free / (1024 ** 3),
                        'total_gb': total / (1024 ** 3),
                        'device': path
                    })
                except Exception:
                    pass
    return drives

def sync_folders(source_dirs, target_root, flat_mode=False):
    total_copied = 0
    total_skipped = 0
    
    for src in source_dirs:
        if not os.path.exists(src):
            continue
            
        folder_name = os.path.basename(src)
        if flat_mode:
            dest_dir = os.path.join(target_root, "Car_Hindi_Playlist")
        else:
            dest_dir = os.path.join(target_root, folder_name)
            
        os.makedirs(dest_dir, exist_ok=True)
        
        mp3_files = [f for f in os.listdir(src) if f.lower().endswith(".mp3")]
        print(f"\n[*] Syncing {folder_name} ({len(mp3_files)} tracks)...")
        
        for f in mp3_files:
            src_path = os.path.join(src, f)
            dest_path = os.path.join(dest_dir, f)
            
            src_size = os.path.getsize(src_path)
            if os.path.exists(dest_path) and os.path.getsize(dest_path) == src_size:
                total_skipped += 1
                continue
                
            print(f"  [→] Copying: {f[:60]} ({src_size // (1024*1024)} MB)...")
            try:
                shutil.copy2(src_path, dest_path)
                total_copied += 1
            except OSError as e:
                print(f"  [!] Failed to copy {f[:60]}: Drive may be full or permission denied ({e}). Skipping...")
                continue
            
    return total_copied, total_skipped

def main():
    print("=" * 70)
    print("  🚗 HINDI MUSIC VAULT — CAR USB SYNC & EXPORTER (5,292 ARCHIVE)")
    print("=" * 70)
    print("  Optimized for Maruti, Hyundai, Tata, Mahindra, Toyota, Honda & All Head Units\n")
    
    drives = get_removable_drives()
    
    if not drives:
        print("[!] No USB flash drive detected automatically.")
        manual_drive = input("Enter your USB Drive Letter (e.g. E: or F:) or press Enter to cancel: ").strip()
        if manual_drive:
            if not manual_drive.endswith("\\"):
                manual_drive += "\\"
            if os.path.exists(manual_drive):
                target_drive = manual_drive
            else:
                print(f"[!] Drive {manual_drive} not accessible. Exiting.")
                return
        else:
            print("Please insert a USB drive and try again.")
            return
    else:
        print("Detected USB Drives:")
        for idx, d in enumerate(drives, start=1):
            print(f"  [{idx}] Drive {d['letter']} (Free: {d['free_gb']:.2f} GB / Total: {d['total_gb']:.2f} GB)")
            
        choice = input(f"\nSelect USB Drive [1-{len(drives)}] (Default: 1): ").strip()
        if not choice:
            choice = "1"
        try:
            target_drive = drives[int(choice) - 1]['letter']
        except Exception:
            target_drive = drives[0]['letter']

    # Validate drive exists and is writable
    if not os.path.exists(target_drive):
        print(f"[!] Target drive {target_drive} does not exist. Exiting.")
        return
    try:
        test_file = os.path.join(target_drive, ".test_write")
        with open(test_file, "w") as tf:
            tf.write("test")
        os.remove(test_file)
    except OSError:
        print(f"[!] Target drive {target_drive} is not writable. Please check permissions or if the drive is full. Exiting.")
        return

    print(f"\nSelected Target USB: {target_drive}\n")
    print("Choose Sync Preset:")
    print("  [1] Complete Master Archive (All 8 Folders: 5,292 Tracks - for 64GB+ USB)")
    print("  [2] Bollywood Eras Only (60s-70s, 80s-90s, 2000s, 2010s, 2020s)")
    print("  [3] Sacred Bhajans & Devotional Only (523 Tracks)")
    print("  [4] Highway Roadtrip & Late Night Specials Only (434 Tracks)")
    print("  [5] Single Flat Folder (All Songs in 1 folder - best for older car stereos)")
    
    preset = input("\nEnter Choice [1-5] (Default: 1): ").strip()
    if not preset:
        preset = "1"
        
    flat_mode = (preset == "5")
    
    if preset in ("1", "5"):
        src_dirs = [os.path.join(VAULT_ROOT, cat) for cat in CATEGORIES]
    elif preset == "2":
        src_dirs = [os.path.join(VAULT_ROOT, cat) for cat in CATEGORIES[:5]]
    elif preset == "3":
        src_dirs = [os.path.join(VAULT_ROOT, CATEGORIES[5])]
    elif preset == "4":
        src_dirs = [os.path.join(VAULT_ROOT, CATEGORIES[6]), os.path.join(VAULT_ROOT, CATEGORIES[7])]
    else:
        src_dirs = [os.path.join(VAULT_ROOT, cat) for cat in CATEGORIES]

    print(f"\nStarting USB Sync to {target_drive}...")
    copied, skipped = sync_folders(src_dirs, target_drive, flat_mode=flat_mode)
    
    print("\n" + "=" * 70)
    print(f"  ✨ USB Car Sync Finished Successfully!")
    print(f"     • Copied to USB : {copied} tracks")
    print(f"     • Already on USB: {skipped} tracks")
    print(f"     • Destination   : {target_drive}")
    print("  🚗 Safe to plug into your car now. Enjoy the music!")
    print("=" * 70 + "\n")
    input("Press Enter to close...")

if __name__ == "__main__":
    main()
