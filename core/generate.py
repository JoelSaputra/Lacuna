from pathlib import Path
from core.ingest import ingest
from core.retrieve import retrieve
from config import *
from google import genai
import os 


API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)
model = MODEL

def generate_response(question: str):
    retrieved_docs = retrieve(question)

    prompt = f"""Only answer this question: {question} 
                 based on the following context: {retrieved_docs["documents"]}
                 If the answer is not contained within the context provided, say "NOT ANSWERABLE" and do not make up an answer.
              """
    

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    return response.text
    






