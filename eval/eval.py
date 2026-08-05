from pathlib import Path
import json
import sys
from dotenv import load_dotenv
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.verify import verify_answer
from core.retrieve import retrieve
import time


load_dotenv()


evalFile = Path(__file__).parent.parent / "eval" / "eval.jsonl"

DELAY_TIME = 30

def read_file():
      if not evalFile.exists():
            return []
      else:
            with open(evalFile, encoding="utf-8") as f:
                  return [json.loads(line) for line in f if line.strip()]


def evalSet():
    evalQuestions = read_file()
    numQuestions = len(evalQuestions)
    confusion_matrix = {}
    missed_questions = []
    true_positive = 0
    false_positive = 0
    false_negative = 0
    true_negative = 0


    for i, line in enumerate(evalQuestions, start=1):
          
          if i > 1: 
               time.sleep(DELAY_TIME)

          question = line["question"]
          chunks = retrieve(question)
          verification = verify_answer(question, chunks)

          correct = line["answerable"] == verification["answerable"]
          print(f"[{i:2d}/{numQuestions}] {'ok  ' if correct else 'MISS'} "
                f"{line['id']}  {question[:56]}")

          if line["answerable"] == True and verification["answerable"] == True:
                true_negative += 1

          elif line["answerable"] == True and verification["answerable"] == False:
                false_positive += 1
                missed_questions.append(("false refusal", line["id"], question))


          elif line["answerable"] == False and verification["answerable"] == True:
                false_negative += 1
                missed_questions.append(("false ACCEPT ", line["id"], question))

          else:
                true_positive += 1


    confusion_matrix["true_negative"] = true_negative
    confusion_matrix["false_positive"] = false_positive
    confusion_matrix["false_negative"] = false_negative
    confusion_matrix["true_positive"] = true_positive


    refused_total = true_positive + false_positive   
    should_refuse = true_positive + false_negative     

    accuracy = (true_positive + true_negative) / numQuestions if numQuestions else 0
    precision = true_positive / refused_total if refused_total else 0
    recall = true_positive / should_refuse if should_refuse else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    lines = [
        "",
        "=" * 62,
        f"EVAL — {numQuestions} questions",
        "",
        "                          gate: ANSWERABLE   gate: REFUSED",
        f"  truly answerable              {true_negative:3d}              {false_positive:3d}   <- false refusals",
        f"  truly NOT answerable          {false_negative:3d}              {true_positive:3d}",
        "                                ^ hallucination risk",
        "",
        f"  accuracy           {accuracy:.0%}",
        f"  refusal precision  {precision:.0%}   ({true_positive}/{refused_total} refusals were correct)",
        f"  refusal recall     {recall:.0%}   ({true_positive}/{should_refuse} out-of-corpus questions caught)",
        f"  F1                 {f1:.0%}",
    ]

    if missed_questions:
        lines.append("")
        lines.append(f"{len(missed_questions)} miss(es):")
        for kind, qid, text in missed_questions:
            lines.append(f"  {kind} [{qid}] {text}")

    return "\n".join(lines)




if __name__ == "__main__":
    print(evalSet())


    
         
          
                

           
                
                
                
                
                







    





    
