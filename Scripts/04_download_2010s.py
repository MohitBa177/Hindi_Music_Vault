"""
Hindi Music Vault — 04. Modern Bollywood (2010s Chartbusters)
Arijit Singh, Atif Aslam, Badshah, Yo Yo Honey Singh, Neha Kakkar, Armaan Malik & Amit Trivedi.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_music_engine import batch_download_from_catalog

if __name__ == "__main__":
    batch_download_from_catalog(
        catalog_filename="04_2010s.json",
        folder_rel_name="04_Modern_Bollywood_2010s",
        collection_name="Modern Bollywood (2010s Hits)",
        max_workers=4
    )
