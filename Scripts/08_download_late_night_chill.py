"""
Hindi Music Vault — 08. Late Night Chill & Slow Drive
Acoustic melodies, Soulful vocals, Anuv Jain, Prateek Kuhad, The Local Train, Lo-Fi Hindi.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_music_engine import batch_download_from_catalog

if __name__ == "__main__":
    batch_download_from_catalog(
        catalog_filename="08_late_night_chill.json",
        folder_rel_name="08_Late_Night_Chill_Drive",
        collection_name="Late Night Chill & Slow Drive",
        max_workers=4
    )
