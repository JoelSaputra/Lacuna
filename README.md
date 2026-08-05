# Lacuna

**A RAG system that knows what it doesn't know.**

Standard RAG has a silent failure mode: when the answer isn't in your documents, vector
search returns the nearest chunks anyway — relevant or not — and the model answers
confidently from weak evidence. It hallucinates, and nothing in the pipeline notices.

Lacuna puts a **verification gate** between retrieval and generation. Before answering, a
separate model call judges whether the retrieved chunks actually contain the answer. When
they don't, it refuses with specifics, logs the gap, and turns accumulated gaps into a
coverage report of its own blind spots.

The corpus is the 2026 FIBA Official Basketball Rules — 57 articles and appendices,
34,122 words, 120 chunks.

---

## The difference the gate makes

Same question, two modes:

```
$ python cli.py ask "what is the spin euro hesi move?" --no-gate

```

```
$ python cli.py ask "what is the spin euro hesi move?"

NOT ANSWERABLE
Corpus only covers: basketball travelling definition, pivot definition,
                    throw-in penalty, and scoresheet preparation rules
Missing topics: definition and description of the spin euro hesi move
```

"Spin euro hesi" is basketball slang — plausible enough that retrieval returns the
travelling and pivot rules. Vanilla RAG answers from them. The gate reads the same chunks,
recognises they don't define the move, and says so.

`--no-gate` is an honest baseline: an ordinary answer-from-context prompt with no refusal
instruction, kept in the repo precisely so the comparison is fair.

---

## Does it actually work?

10 hand-labelled questions — 5 answerable from the rulebook, 5 plausible-sounding
questions it cannot answer (NBA and NCAA rules, basketball slang, coaching tactics,
history). Each label was verified against the source text by hand.

Two error types, and they are not equally bad:

- **False refusal** — the corpus had the answer, the gate refused. Annoying, safe.
  Usually a retrieval miss rather than a gate failure.
- **False accept** — the corpus lacked the answer, the gate approved it. This is the
  hallucination the project exists to prevent.

Reporting precision _and_ recall matters because they trade against each other: a stricter
gate catches more out-of-corpus questions but starts refusing answerable ones.

Reproduce with `python cli.py eval` (questions in `eval/eval.jsonl`).

---

## How it works

```
                    ┌──────────────────────┐
 question ─────────▶│  retrieve (Chroma)   │
                    └──────────┬───────────┘
                               │ top-k chunks + distances
                    ┌──────────▼───────────┐
                    │  VERIFICATION GATE   │  ← the twist
                    │  structured verdict: │
                    │  answerable? topic?  │
                    │  covers? missing?    │
                    └─────┬──────────┬─────┘
                 answerable          not answerable
                       │                  │
             ┌─────────▼──────┐  ┌────────▼─────────┐
             │   generate     │  │ specific refusal │
             │  with sources  │  │ covers / missing │
             └─────────┬──────┘  └────────┬─────────┘
                       └────────┬─────────┘
                                ▼
                          ┌───────────┐
                          │  ledger   │ ──▶ coverage report
                          └───────────┘
```

The gate is one extra model call returning a structured verdict:

```json
{
  "answerable": false,
  "topic": "basketball slang move terminology",
  "covered_topics": "travelling, pivot, throw-in penalties",
  "missing_topics": "definition of the spin euro hesi move"
}
```

The prompt's load-bearing instruction is the distinction between _containing_ an answer and
_knowing_ one:

> "Answerable" means the excerpts CONTAIN the answer — not that you know the answer. If
> you know the answer from general knowledge but the excerpts do not state it, mark it NOT
> answerable.

Without that line the model judges its own ability rather than the evidence, and approves
questions the corpus cannot answer.

---

## Design decisions

**Separate judge, separate call.** The gate could have been folded into the generation
prompt ("say NOT ANSWERABLE if the context is insufficient"). It isn't, because a model
asked to produce an answer is biased toward finding the question answerable. A judge with
no answer to write has no such stake.

**No framework.** No LangChain or LlamaIndex — the pipeline is ~450 lines of plain Python.
The project's value lives in the seam between retrieval and generation, which is exactly
what a prebuilt `RetrievalQA` chain hides.

**Structure-aware chunking.** The rulebook declares its own boundaries (every `29.2.1` is a
formally separate rule), so chunks are packed from whole clauses up to a 400-word limit
rather than cut at fixed offsets. No rule is ever split mid-sentence. 31 of 57 documents
come out as a single chunk, which keeps citations clean.

**Preprocessing is corpus-specific and quarantined.** `scripts/preprocess_fiba.py` knows
about FIBA's page headers, article numbering and lettered appendix clauses. Nothing in
`core/` does, so pointing Lacuna at a different corpus means writing a new preprocessing
script and changing nothing else.

---

## Layout

```
cli.py                    ingest / ask / report / eval
core/
  config.py               paths, chunk size, top-k, model
  load.py                 corpus folder → documents
  chunking.py             documents → 400-word chunks on clause boundaries
  ingest.py               load + chunk + embed + store
  retrieve.py             question → chunks with distances
  verify.py               ★ the gate
  generate.py             cited answer from retrieved chunks
  baseline.py             --no-gate comparison (ordinary RAG)
  ledger.py               append-only JSONL query log
  report.py               ledger → coverage report
scripts/preprocess_fiba.py   PDF → 57 markdown articles (FIBA-specific)
eval/
  eval.jsonl              30 labelled questions
  eval.py                 confusion matrix, precision, recall
data/corpus/              the preprocessed rulebook
```

---

## Running it

```bash
python -m venv .venv && source .venv/bin/activate
pip install chromadb google-genai pypdf python-dotenv

echo "GEMINI_API_KEY=your-key" > .env

python scripts/preprocess_fiba.py     # PDF → data/corpus/  (once)
python cli.py ingest data/corpus      # → Chroma vector store (once)

python cli.py ask "how long does a time-out last?"
python cli.py ask "how far is the NBA three-point line?"
python cli.py ask "..." --no-gate     # baseline comparison
python cli.py report                  # coverage map
python cli.py eval                    # confusion matrix
```

Embeddings run locally via Chroma's built-in model; only the gate and generation calls hit
the API.

---
