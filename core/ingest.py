from pathlib import Path
from core.load import load_folder
from core.chunking import chunk
import chromadb


client = chromadb.PersistentClient(path="storage/chroma")


def ingest():
    collection = client.get_or_create_collection("fiba_rules")
    folder = load_folder("data/corpus")
    texts = []
    collection_id = []
    collection_metadatas = []
    

    for file in folder:
        for i, chunk_text in enumerate(chunk(file["text"])):
            texts.append(chunk_text)
            collection_id.append(f"{file['id']}-{i}")
            collection_metadatas.append({"doc_id": file["id"]})


    collection.add(
            documents=texts,
            ids=collection_id,
            metadatas=collection_metadatas
        )



    

    






