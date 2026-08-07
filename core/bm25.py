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


_index = None

def get_index():
    global _index
    if _index is None:
        _index = build_index()
    return _index


def word_search(text:str, k:int=TOP_K):
    bm25, chunk_ids, documents, doc_ids = get_index()

    scores = bm25.get_scores(tokenize(text))

    ranked = sorted(range(len(chunk_ids)), key=lambda i: scores[i], reverse=True)
    best = ranked[:k]  

    query_results = {}
    query_results["documents"] = [documents[i] for i in best]
    query_results["distance"] = [None] * len(best)
    query_results["doc_id"] = [doc_ids[i] for i in best]
    query_results["score"] = [scores[i] for i in best]
    query_results["chunk_id"] = [chunk_ids[i] for i in best]

    return query_results 








