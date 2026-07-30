from pathlib import Path
from load import load_folder

def ingest():
    docs = load_folder("data/corpus")