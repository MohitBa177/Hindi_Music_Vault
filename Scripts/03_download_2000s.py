"""
Hindi Music Vault — 03. Noughties Hits (2000s Bollywood)
KK, Sonu Nigam, Shreya Ghoshal, Sunidhi Chauhan, Mohit Chauhan, Atif Aslam, Pritam & SEL.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_music_engine import batch_download_from_catalog

if __name__ == "__main__":
    batch_download_from_catalog(
        catalog_filename="03_2000s.json",
        folder_rel_name="03_Noughties_Hits_2000s",
        collection_name="Noughties Hits (2000s Bollywood)",
        max_workers=4
    )
