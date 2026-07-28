"""Convert the FIBA rulebook PDF into one clean markdown file per Article.

Run once:  python scripts/preprocess_fiba.py

Reads : data/raw/FIBA_Rules2026.pdf
Writes: data/corpus/article_04_teams.md, article_29_shot_clock.md, ...

Why this exists: the PDF's extracted text is one long run with page headers
mixed in and no paragraph breaks. This script cleans it up and splits it into
per-Article files so (a) citations can say "Article 29" and (b) chunking has
real paragraph boundaries to respect.
"""

import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).parent.parent
PDF_PATH = ROOT / "data" / "raw" / "FIBA_Rules2026.pdf"
OUT_DIR = ROOT / "data" / "corpus"

# Page headers/footers appear in a few orderings, e.g.
#   "Page 12 of 107 OFFICIAL BASKETBALL RULES 2026 July 2026"
#   "July 2020 OFFICIAL BASKETBALL RULES 2020 Page 3 of 107"
HEADER_PATTERNS = [
    re.compile(r"Page\s+\d+\s+of\s+\d+", re.I),
    re.compile(r"OFFICIAL\s+BASKETBALL\s+RULES\s+\d{4}", re.I),
    re.compile(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}", re.I),
]

# An Article heading: "Article 29 Shot clock" — the title may start with a
# digit ("Article 26 3 seconds"), so we accept alphanumeric starts. We capture
# generously here and trim the title in clean_title(); real headings are then
# separated from cross-references ("...Article 41 shall apply") by keep_headings().
ARTICLE_RE = re.compile(r"Article\s+(\d{1,2})\s+([A-Za-z0-9][^\n]{0,80})")

# A title runs until the first clause number ("41.1"), a colon, or a bullet.
TITLE_END_RE = re.compile(r"\s*(?:\d{1,2}\.\d|:|•)")

# Table-of-contents entries carry the exact titles, followed by dotted leaders:
#   "Article 26 3 seconds ..................... 42"
TOC_RE = re.compile(r"Article\s+(\d{1,2})\s+(.+?)\s*\.{4,}")

MAX_TITLE_WORDS = 9  # fallback cap when a title isn't in the contents

# Appendices follow the final article: "APPENDIX C – PROTEST PROCEDURE C.1 ..."
APPENDIX_RE = re.compile(r"APPENDIX\s+([A-F])\s*[–-]\s*([A-Z][A-Z’' \-]{3,60})")

# Clause numbers like "29.2.1" mark the start of a new rule paragraph.
CLAUSE_RE = re.compile(r"(?<=[.\s])(\d{1,2}\.\d{1,2}(?:\.\d{1,2})?)\s")


def extract_text(pdf_path: Path) -> str:
    """Pull raw text out of every page."""
    reader = PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def strip_page_junk(text: str) -> str:
    """Remove repeated page headers/footers."""
    for pattern in HEADER_PATTERNS:
        text = pattern.sub(" ", text)
    return text


def drop_table_of_contents(text: str) -> str:
    """Cut everything before the body.

    Table-of-contents lines are recognisable by their dotted leaders
    ("Article 26 3 seconds ......... 42"). We drop every line containing a
    run of dots, then start the body at the last "RULE ONE" heading.
    """
    lines = [ln for ln in text.split("\n") if "....." not in ln]
    text = "\n".join(lines)
    matches = list(re.finditer(r"RULE\s+ONE\b", text, re.I))
    return text[matches[-1].start():] if matches else text


def add_paragraph_breaks(text: str) -> str:
    """Insert blank lines before clause numbers so chunking has paragraphs."""
    text = CLAUSE_RE.sub(r"\n\n\1 ", text)
    text = re.sub(r"[ \t]+", " ", text)          # collapse runs of spaces
    text = re.sub(r"\n{3,}", "\n\n", text)       # collapse runs of blank lines
    return text.strip()


def slugify(number: str, title: str) -> str:
    """article_29_shot_clock — zero-padded so files sort correctly."""
    clean = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    return f"article_{int(number):02d}_{clean[:40]}"


def titles_from_contents(text: str) -> dict[int, str]:
    """Read the exact article titles out of the table of contents."""
    return {
        int(number): " ".join(title.split())
        for number, title in TOC_RE.findall(text)
    }


def split_title(raw: str, known: str | None) -> tuple[str, int]:
    """Return the article's title and how many characters of `raw` it used.

    Knowing where the title ends matters as much as the title itself: the body
    starts immediately after it, so an over-long guess silently eats real text.
    """
    if known and raw.lower().startswith(known.lower()):
        return known, len(known)

    cut = TITLE_END_RE.search(raw)
    end = cut.start() if cut else len(raw)
    words = list(re.finditer(r"\S+", raw[:end]))
    if len(words) > MAX_TITLE_WORDS:
        end = words[MAX_TITLE_WORDS - 1].end()
    return raw[:end].strip(" .,-:"), end


def keep_headings(matches: list[re.Match]) -> list[re.Match]:
    """Drop cross-references, keeping only real headings.

    Real headings run strictly in sequence (1, 2, 3, ... 51), so the only
    match we accept at any point is the next number we expect. A mention like
    "...Article 41 shall apply" sitting inside Article 34's body is skipped
    because we are looking for 35 at that moment.
    """
    kept, expected = [], 1
    for match in matches:
        if int(match.group(1)) == expected:
            kept.append(match)
            expected += 1
    return kept


def split_articles(text: str, known_titles: dict[int, str]) -> list[dict]:
    """Cut the body into one entry per Article heading."""
    matches = keep_headings(list(ARTICLE_RE.finditer(text)))
    articles = []
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        number = match.group(1)
        title, used = split_title(match.group(2), known_titles.get(int(number)))
        body = text[match.start(2) + used:end]
        articles.append({
            "number": number,
            "title": title,
            "slug": slugify(number, title),
            "body": add_paragraph_breaks(body),
        })
    return articles


def split_appendices(tail: str) -> tuple[str, list[dict]]:
    """Separate trailing appendices from the last article's body.

    Returns the trimmed article body plus one entry per appendix.
    """
    matches = list(APPENDIX_RE.finditer(tail))
    if not matches:
        return tail, []

    appendices = []
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(tail)
        letter, title = match.group(1), " ".join(match.group(2).split()).title()
        appendices.append({
            "number": letter,
            "title": title,
            "slug": f"appendix_{letter.lower()}_{re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')[:40]}",
            "body": add_paragraph_breaks(tail[match.end():end]),
        })
    return tail[: matches[0].start()], appendices


def main() -> None:
    if not PDF_PATH.exists():
        raise SystemExit(f"PDF not found: {PDF_PATH}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in list(OUT_DIR.glob("article_*.md")) + list(OUT_DIR.glob("appendix_*.md")):
        old.unlink()  # clean re-runs

    cleaned = strip_page_junk(extract_text(PDF_PATH))
    known_titles = titles_from_contents(cleaned)   # read titles before dropping the contents
    articles = split_articles(drop_table_of_contents(cleaned), known_titles)

    # The appendices trail the final article — pull them out into their own files.
    articles[-1]["body"], appendices = split_appendices(articles[-1]["body"])

    for article in articles:
        header = f"# Article {article['number']} — {article['title']}\n\n"
        (OUT_DIR / f"{article['slug']}.md").write_text(
            header + article["body"], encoding="utf-8"
        )

    for appendix in appendices:
        header = f"# Appendix {appendix['number']} — {appendix['title']}\n\n"
        (OUT_DIR / f"{appendix['slug']}.md").write_text(
            header + appendix["body"], encoding="utf-8"
        )

    written = articles + appendices
    total_words = sum(len(item["body"].split()) for item in written)
    print(
        f"Wrote {len(articles)} articles + {len(appendices)} appendices "
        f"to {OUT_DIR} ({total_words:,} words)"
    )
    shortest = min(written, key=lambda item: len(item["body"].split()))
    longest = max(written, key=lambda item: len(item["body"].split()))
    print(f"  shortest: {shortest['slug']}.md — {len(shortest['body'].split())} words")
    print(f"  longest:  {longest['slug']}.md — {len(longest['body'].split())} words")


if __name__ == "__main__":
    main()
