"""
Hindi Music Vault — 06. Sacred Hindi Bhajans & Devotional
Gulshan Kumar, Anuradha Paudwal, Hariharan, Anup Jalota (Hanuman Chalisa, Krishna, Shiv, Ram, Mataji).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_music_engine import batch_download_from_catalog

if __name__ == "__main__":
    batch_download_from_catalog(
        catalog_filename="06_bhajans.json",
        folder_rel_name="06_Hindi_Bhajans_Devotional",
        collection_name="Sacred Hindi Bhajans & Devotional",
        max_workers=4
    )
