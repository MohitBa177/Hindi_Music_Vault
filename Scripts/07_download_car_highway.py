"""
Hindi Music Vault — 07. Car Highway Roadtrip Special
High Energy driving beats, ZNMD, YJHD, Piku, Tamasha, Dil Dhadakne Do, Highway.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_music_engine import batch_download_from_catalog

if __name__ == "__main__":
    batch_download_from_catalog(
        catalog_filename="07_car_highway.json",
        folder_rel_name="07_Car_Highway_Roadtrip_Special",
        collection_name="Car Highway Roadtrip Special",
        max_workers=4
    )
