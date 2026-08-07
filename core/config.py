from pathlib import Path

ROOT = Path(__file__).parent.parent

CORPUS_PATH = str(ROOT / "data" / "corpus")
STORAGE_PATH = str(ROOT / "storage" / "chroma")

DB_NAME = "fiba_rules"
CHUNK_SIZE = 400

TOP_K = 5

RETRIEVER = "vector"
RETRIEVERS = ("vector", "hybrid", "bm25")

CANDIDATE_K = 20 

RRF_K = 10

MODEL = "gemini-3.1-flash-lite"




