from core.ingest import ingest
from core.retrieve import retrieve

def ask():
    input_text = input("Ask a question: ")
    result = retrieve(input_text)
