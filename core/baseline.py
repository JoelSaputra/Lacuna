import os
from google import genai
from core.config import MODEL


_client = None


def get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    return _client


def baseline_answer(question: str, hits):

    context = "\n\n".join(f"[{doc_id}]\n{text}" for doc_id, text in zip(hits["doc_id"], hits["documents"]))

    prompt = f"""Only answer this question: {question} 
                 based on the following context: {context}
              """
    

    response = get_client().models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return response.text
    






