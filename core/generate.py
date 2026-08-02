import os

from google import genai

from core.config import MODEL


_client = None


def get_client():
    """Create the Gemini client on first use.

    Built lazily so that importing this module (which cli.py does for every
    command) doesn't require an API key — `ingest` never calls Gemini.
    """
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    return _client


def generate_response(question: str, hits):

    context = "\n\n".join(f"[{doc_id}]\n{text}" for doc_id, text in zip(hits["doc_id"], hits["documents"]))

    prompt = f"""Only answer this question: {question} 
                 based on the following context: {context}
                 If the answer is not contained within the context provided, say "NOT ANSWERABLE" and do not make up an answer.
              """
    

    response = get_client().models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return response.text
    






