from pathlib import Path
import os
from google import genai
from core.config import MODEL
import json


def verify_answer(question: str, hits):

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    

    context = "\n\n".join(f"[{doc_id}]\n{text}" for doc_id, text in zip(hits["doc_id"], hits["documents"]))


    prompt = f"""You are judging whether a question can be answered from the excerpts below.

            "Answerable" means the excerpts CONTAIN the answer — not that you know the answer.
            If you know the answer from general knowledge but the excerpts do not state it,
            mark it NOT answerable.

            Question: {question}

            Excerpts:
            {context}

            Return:
            - answerable: true only if the excerpts contain the answer
            - topic: what the question is about, in a few words
            - covered_topics: what subjects the excerpts actually cover
            - missing_topics: what information would be needed but is absent
            """



    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "object",
                "properties": {
                    "answerable":     {"type": "boolean"},
                    "topic":          {"type": "string"},
                    "covered_topics": {"type": "string"},
                    "missing_topics": {"type": "string"},
                },
                "required": ["answerable", "topic", "covered_topics", "missing_topics"],
            },
        },
    )


    return json.loads(response.text)


        