import chromadb
from core.ingest import ingest 
from config import *


client = chromadb.PersistentClient(path=STORAGE_PATH)
collection = client.get_collection(DB_NAME)

def retrieve(text: input, folder: str):
    query_results = []
    ingest(folder)
    
    results = collection.query(
        query_texts=[text],
        n_results=TOP_K 
    )

    print(f"Retrieved {len(results["documents"][0])} results for the quetsion: {text}")
    query_results.append(results["documents"][0])
    query_results.append(results["distances"][0])

    return query_results

