import chromadb
from core.ingest import ingest 
from config import *


client = chromadb.PersistentClient(path=STORAGE_PATH)
collection = client.get_collection(DB_NAME)

def retrieve(text: input):
    ingest()
    
    results = collection.query(
        query_texts=[text],
        n_results=TOP_K 
    )