from core.ingest import ingest
from core.load import load_folder
from core.retrieve import retrieve
from core.generate import generate_response
from core.config import *
from google import genai
from dotenv import load_dotenv
from core.verify import verify_answer
from core.baseline import baseline_answer
from core.ledger import store
from core.report import report
from eval.eval import evalSet
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
    p_ask.add_argument("--no-gate", action="store_true", help="Skip the answerability check and generate a response directly")

    sub.add_parser("report", help="Generate a report of all questions asked and their answerability status")
    

    sub.add_parser("eval", help="evaluation and confusion matrix output")

    args = parser.parse_args()


    if (args.command) == "report":
        print(report())
        

    elif (args.command) == "ingest":
        ingest(args.folder)

    elif(args.command) == "eval":
        print(evalSet())

    elif (args.command) == "ask":

        hits = retrieve(args.question)

        if args.no_gate:
            print(baseline_answer(args.question, hits))

        else:
            verdict = verify_answer(args.question, hits)
            store(args.question, verdict, hits)


            if verdict["answerable"]:
                response = generate_response(args.question, hits)
                print(response)

            else: 
                print("NOT ANSWERABLE")
                print(f"Corpus only covers: {verdict['covered_topics']}")
                print(f"Missing topics: {verdict['missing_topics']}")

            


    
if __name__ == "__main__":
    main()
    







