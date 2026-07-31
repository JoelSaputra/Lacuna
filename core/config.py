from pathlib import Path

ROOT = Path(__file__).parent.parent

CORPUS_PATH = str(ROOT / "data" / "corpus")
STORAGE_PATH = str(ROOT / "storage" / "chroma")

DB_NAME = "fiba_rules"
CHUNK_SIZE = 400
