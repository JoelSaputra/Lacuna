import chromadb
from core.ingest import ingest 
from config import *


client = chromadb.PersistentClient(path=STORAGE_PATH)
collection = client.get_collection(DB_NAME)

def retrieve():
    ingest()
    
    result = collection.query()