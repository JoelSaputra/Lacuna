from core.ledger import read_all
from collections import Counter


def report():
    ledger_entries = read_all()

    response = ""

    if not ledger_entries:
        print("No queries logged yet.")
        return
    
    total_queries = len(ledger_entries)
    num_answerable = 0
    num_not_answerable = 0
    
    for entry in ledger_entries:
        num_answerable += 1 if entry["answerable"] else 0
        num_not_answerable += 1 if not entry["answerable"] else 0

    

    num_answerable_percent = (num_answerable / total_queries) * 100 
    num_not_answerable_percent = 100 - num_answerable_percent


    refused = [entry for entry in ledger_entries if not entry["answerable"]]

    lines = [
        f"COVERAGE REPORT - {total_queries} queries logged",
        f"Answered: {num_answerable} ({num_answerable_percent:.0f}%) | "
        f"Not Answered: {num_not_answerable} ({num_not_answerable_percent:.0f}%)",
    ]

    if refused:
        clusters = Counter(entry["topic"] for entry in refused)

        lines.append("")
        lines.append("Gap clusters:")
        for topic, count in clusters.most_common():
            label = f"{topic} ".ljust(30, ".")
            lines.append(f"  {label} {count}")

        lines.append("")
        lines.append("Acquisition list:")
        for missing in sorted({entry["missing_topics"] for entry in refused}):
            lines.append(f"  - {missing}")

    return "\n".join(lines)





   