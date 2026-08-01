import chromadb
from ingest import ingest 
from config import *


client = chromadb.PersistentClient(path=STORAGE_PATH)
collection = client.get_or_create_collection(DB_NAME)

def retrieve(text: str):
    query_results = {}
    
    results = collection.query(
        query_texts=[text],
        n_results=TOP_K 
    )

    print(f"Retrieved {len(results["documents"][0])} results for the quetsion: {text}")
    query_results["documents"] = results["documents"][0]
    query_results["distance"] = results["distances"][0]
    query_results["doc_id"] = [m["doc_id"] for m in results["metadatas"][0]]

    return query_results

