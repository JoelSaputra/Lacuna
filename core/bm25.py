import re
import chromadb
from rank_bm25 import BM25Okapi
from core.config import DB_NAME, STORAGE_PATH, TOP_K

client = chromadb.PersistentClient(path=STORAGE_PATH)
collection = client.get_or_create_collection(DB_NAME)

def tokenize(text:str):
    lowered = text.lower()
    words = re.findall(r"\w+", lowered)
    return words


def build_index():
    everything = collection.get(include=["documents", "metadatas"])

    chunk_ids = everything["ids"]
    documents = everything["documents"]
    doc_ids = [m["doc_id"] for m in everything["metadatas"]]

    tokenized_chunks = [tokenize(d) for d in documents]
    bm25 = BM25Okapi(tokenized_chunks)

    return bm25, chunk_ids, documents, doc_ids





