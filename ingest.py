"""
ingest.py - Document ingestion and chunking pipeline
UNC Unofficial Guide RAG System

Loads .txt documents from the documents/ folder, cleans them,
and splits them into chunks using a sentence-aware strategy.
"""

import os
import re
from pathlib import Path


DOCUMENTS_DIR = Path("documents")
CHUNK_SIZE = 400        # characters per chunk (suits short review-style text)
CHUNK_OVERLAP = 80      # overlap to preserve context across chunk boundaries


def load_documents(docs_dir: Path = DOCUMENTS_DIR) -> list[dict]:
    """Load all .txt files from the documents directory."""
    docs = []
    for filepath in sorted(docs_dir.glob("*.txt")):
        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()
        docs.append({
            "source": filepath.name,
            "raw_text": raw_text,
        })
    print(f"Loaded {len(docs)} documents from {docs_dir}/")
    return docs


def clean_text(text: str) -> str:
    """
    Remove boilerplate and noise from document text.
    Keeps substantive review/opinion content; removes header metadata lines.
    """
    # Remove lines that are purely metadata headers (Source:, Collected:, Domain:)
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Skip pure metadata lines at the top of files
        if re.match(r"^(Source|Collected|Domain):", stripped):
            continue
        # Skip horizontal rules
        if stripped in ("---", "===", "***"):
            continue
        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # Collapse excessive blank lines (3+ newlines → 2)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Normalize whitespace within lines
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def split_into_chunks(text: str, source: str,
                      chunk_size: int = CHUNK_SIZE,
                      overlap: int = CHUNK_OVERLAP) -> list[dict]:
    """
    Split text into overlapping chunks.

    Strategy: slide a window of chunk_size characters, stepping by
    (chunk_size - overlap) each time. We snap each boundary to the nearest
    sentence end (period/question mark/exclamation) so chunks don't cut
    mid-sentence when possible.

    Returns a list of dicts with keys: text, source, chunk_id.
    """
    # Collapse text to single-spaced for chunking
    flat = " ".join(text.split())
    step = chunk_size - overlap
    chunks = []
    start = 0
    chunk_id = 0

    while start < len(flat):
        end = min(start + chunk_size, len(flat))

        # Snap end to nearest sentence boundary if not at the end of text
        if end < len(flat):
            # Look backwards up to 60 chars for a sentence end
            search_region = flat[max(start, end - 60): end]
            last_sentence_end = max(
                search_region.rfind(". "),
                search_region.rfind("? "),
                search_region.rfind("! "),
            )
            if last_sentence_end != -1:
                # Adjust end to just past the punctuation
                offset = max(start, end - 60) + last_sentence_end + 2
                end = offset

        chunk_text = flat[start:end].strip()

        if len(chunk_text) > 60:  # skip near-empty chunks
            chunks.append({
                "text": chunk_text,
                "source": source,
                "chunk_id": f"{source}__chunk{chunk_id:03d}",
            })
            chunk_id += 1

        start += step
        if start >= len(flat):
            break

    return chunks


def run_pipeline(docs_dir: Path = DOCUMENTS_DIR) -> list[dict]:
    """
    Full ingestion pipeline: load → clean → chunk.
    Returns a flat list of all chunk dicts across all documents.
    """
    documents = load_documents(docs_dir)
    all_chunks = []

    for doc in documents:
        cleaned = clean_text(doc["raw_text"])
        chunks = split_into_chunks(cleaned, source=doc["source"])
        all_chunks.extend(chunks)
        print(f"  {doc['source']}: {len(chunks)} chunks")

    print(f"\nTotal chunks: {len(all_chunks)}")
    return all_chunks


def inspect_chunks(chunks: list[dict], n: int = 5) -> None:
    """Print n representative chunks for manual inspection."""
    import random
    sample = random.sample(chunks, min(n, len(chunks)))
    print(f"\n{'='*60}")
    print(f"SAMPLE CHUNKS (n={n})")
    print(f"{'='*60}")
    for i, chunk in enumerate(sample, 1):
        print(f"\n--- Chunk {i} | Source: {chunk['source']} | ID: {chunk['chunk_id']} ---")
        print(chunk["text"])
    print(f"\n{'='*60}")


if __name__ == "__main__":
    chunks = run_pipeline()
    inspect_chunks(chunks, n=5)
