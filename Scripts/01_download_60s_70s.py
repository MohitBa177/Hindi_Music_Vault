"""
Hindi Music Vault — 01. Retro Golden Classics (60s & 70s)
Lata Mangeshkar, Mohammed Rafi, Kishore Kumar, Mukesh, RD Burman, Asha Bhosle, Manna Dey & more.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_music_engine import batch_download_from_catalog

if __name__ == "__main__":
    batch_download_from_catalog(
        catalog_filename="01_60s_70s.json",
        folder_rel_name="01_Retro_Classics_60s_70s",
        collection_name="Retro Golden Classics (60s & 70s)",
        max_workers=4
    )
