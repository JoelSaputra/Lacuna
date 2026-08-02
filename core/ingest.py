import chromadb

from core.chunking import chunk
from core.config import CORPUS_PATH, DB_NAME, STORAGE_PATH
from core.load import load_folder


def ingest(folder: str = CORPUS_PATH):
    docs = load_folder(folder)
    client = chromadb.PersistentClient(path=STORAGE_PATH)
    collection = client.get_or_create_collection(DB_NAME)
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
    

    
    



    

    






