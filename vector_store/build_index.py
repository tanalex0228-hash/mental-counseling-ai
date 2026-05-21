import os
from pathlib import Path
import sys


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from vector_store.ingest_documents import ingest_knowledge_base


if __name__ == "__main__":
    count = ingest_knowledge_base()
    print(f"Indexed {count} knowledge chunks.")
