from pathlib import Path
import datetime
import json

ledger_path = Path(__file__).parent.parent / "storage" / "ledger.jsonl"


def store(question: str, verdict: dict, hits: dict):

    ledgerFile = {
        "time": datetime.datetime.now().isoformat(),
        "question": question,
        "answerable": verdict["answerable"],
        "topic": verdict["topic"],
        "covered_topics": verdict["covered_topics"],   
        "missing_topics": verdict["missing_topics"],
        "hits": {
            "distance": hits["distance"],
            "doc_id": hits["doc_id"]
        }
    }

    ledger_path.parent.mkdir(parents=True, exist_ok=True)

    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(ledgerFile) + "\n"
        )


def read_all():
    if not ledger_path.exists():
        return []
    with open(ledger_path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

