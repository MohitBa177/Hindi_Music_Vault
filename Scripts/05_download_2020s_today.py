"""
Hindi Music Vault — 05. Latest Hits (2020s to 2026 Today)
Animal, Stree 2, Pushpa 2, Jawan, Pathaan, Shershaah, Arijit Singh, Jubin Nautiyal & Karan Aujla.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_music_engine import batch_download_from_catalog

if __name__ == "__main__":
    batch_download_from_catalog(
        catalog_filename="05_2020s_today.json",
        folder_rel_name="05_Latest_Hits_2020s_to_Today",
        collection_name="Latest Bollywood Hits (2020s to 2026 Today)",
        max_workers=4
    )
