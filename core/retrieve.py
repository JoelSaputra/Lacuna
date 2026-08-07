import chromadb
from core.bm25 import word_search
from core.config import DB_NAME, STORAGE_PATH, TOP_K, RETRIEVER




client = chromadb.PersistentClient(path=STORAGE_PATH)
collection = client.get_or_create_collection(DB_NAME)

def vector_search(text: str):
    query_results = {}
    
    results = collection.query(
        query_texts=[text],
        n_results=TOP_K 
    )

    query_results["documents"] = results["documents"][0]
    query_results["distance"] = results["distances"][0]
    query_results["doc_id"] = [m["doc_id"] for m in results["metadatas"][0]]

    return query_results

def retrieve(text: str, retriever: str = RETRIEVER):
    if retriever == "vector":
        return vector_search(text)

    if retriever == "bm25":
        return word_search(text)

    raise NotImplementedError(f"{retriever} retrieval not built yet")


