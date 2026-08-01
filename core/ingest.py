from pathlib import Path
from load import load_folder
from chunking import chunk
import chromadb
from config import *


def ingest(folder: str):
    docs = load_folder(folder)
    client = chromadb.PersistentClient(path="storage/chroma")
    collection = client.get_or_create_collection("fiba_rules")
    texts = []
    collection_id = []
    collection_metadatas = []
    

    for file in docs:
        for i, chunk_text in enumerate(chunk(file["text"])):
            texts.append(chunk_text)
            collection_id.append(f"{file['id']}-{i}")
            collection_metadatas.append({"doc_id": file["id"]})


    collection.add(
            documents=texts,
            ids=collection_id,
            metadatas=collection_metadatas
        )
    
    print(f"stored and embedded {collection.count()} chunks from {len(docs)} documents")
    

    
    



    

    






