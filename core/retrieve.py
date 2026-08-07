import chromadb
from core.bm25 import word_search
from core.config import CANDIDATE_K, DB_NAME, RETRIEVER, RRF_K, STORAGE_PATH, TOP_K


client = chromadb.PersistentClient(path=STORAGE_PATH)
collection = client.get_or_create_collection(DB_NAME)

def vector_search(text: str, k=TOP_K):
    query_results = {}
    
    results = collection.query(
        query_texts=[text],
        n_results=k
    )

    query_results["documents"] = results["documents"][0]
    query_results["distance"] = results["distances"][0]
    query_results["doc_id"] = [m["doc_id"] for m in results["metadatas"][0]]
    query_results["chunk_id"] = results["ids"][0]

    return query_results



def hybrid_search(text: str):
    vector_hits = vector_search(text, CANDIDATE_K)
    word_hits = word_search(text, CANDIDATE_K)

    points = {}
    documents = {}
    doc_ids = {}
    distances = {}

    for i, chunk_id in enumerate(vector_hits["chunk_id"]):
        rank = i + 1
        points[chunk_id] = points.get(chunk_id, 0) + 1 / (RRF_K + rank)
        documents[chunk_id] = vector_hits["documents"][i]
        doc_ids[chunk_id] = vector_hits["doc_id"][i]
        distances[chunk_id] = vector_hits["distance"][i]

    for i, chunk_id in enumerate(word_hits["chunk_id"]):
        rank = i + 1
        points[chunk_id] = points.get(chunk_id, 0) + 1 / (RRF_K + rank)
        documents[chunk_id] = word_hits["documents"][i]
        doc_ids[chunk_id] = word_hits["doc_id"][i]


    best = sorted(points, key=lambda c: points[c], reverse=True)[:TOP_K]

    query_results = {}
    query_results["documents"] = [documents[c] for c in best]
    query_results["distance"] = [distances.get(c) for c in best]
    query_results["doc_id"] = [doc_ids[c] for c in best]
    query_results["chunk_id"] = best
    query_results["score"] = [points[c] for c in best]

    return query_results



def retrieve(text: str, retriever: str = RETRIEVER):
    if retriever == "vector":
        return vector_search(text)

    if retriever == "bm25":
        return word_search(text)
    
    if retriever == "hybrid":
        return hybrid_search(text)

    raise NotImplementedError(f"{retriever} retrieval not built yet")


