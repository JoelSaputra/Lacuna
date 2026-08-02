from core.ingest import ingest
from core.load import load_folder
from core.retrieve import retrieve
from core.generate import generate_response
from core.config import *
from google import genai
from dotenv import load_dotenv
from core.verify import verify_answer
import os
import argparse

load_dotenv()  

def main():
    parser = argparse.ArgumentParser(description="Lacuna CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="Ingest documents from a folder")
    p_ingest.add_argument("folder", type=str, help="Path to the folder containing documents")

    p_ask = sub.add_parser("ask")
    p_ask.add_argument("question", type=str, help="Question to ask the model")



    args = parser.parse_args()

    if (args.command) == "ingest":
        ingest(args.folder)

    elif (args.command) == "ask":
        hits = retrieve(args.question)
        verdict = verify_answer(args.question, hits)

        if verdict["answerable"]:
            response = generate_response(args.question, hits)
            print(response)

        else: 
            print("NOT ANSWERABLE")
            print(f"Corpus only covers: {verdict['covered_topics']}")
            print(f"Missing topics: {verdict['missing_topics']}")


        


if __name__ == "__main__":
    main()
    







