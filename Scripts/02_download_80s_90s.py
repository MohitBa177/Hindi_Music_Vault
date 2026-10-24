"""
Hindi Music Vault — 02. Evergreen Romance (80s & 90s)
Kumar Sanu, Udit Narayan, Alka Yagnik, Sonu Nigam, Anuradha Paudwal, Bappi Lahiri, AR Rahman & more.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_music_engine import batch_download_from_catalog

if __name__ == "__main__":
    batch_download_from_catalog(
        catalog_filename="02_80s_90s.json",
        folder_rel_name="02_Evergreen_Romance_80s_90s",
        collection_name="Evergreen Romance (80s & 90s)",
        max_workers=4
    )
