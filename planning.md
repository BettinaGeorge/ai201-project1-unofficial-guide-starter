# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

The domain is **student reviews of CS professors and courses at UNC Chapel Hill**. This knowledge is valuable because it represents honest, peer-to-peer student experience that no official university channel provides — Rate My Professors reviews, Reddit threads, and Discord posts contain the real picture of what a professor's exams are like, how the workload compares to other sections, and whether office hours are actually useful. This information is hard to find otherwise because it's scattered across multiple platforms, buried under unrelated content, and impossible to search with a specific question like "what are KMP's exams like?"

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors (UNC) | Reviews of KMP (COMP 401), Majikes (COMP 110), Bishop (COMP 426) | ratemyprofessors.com — UNC Chapel Hill CS dept / `doc_01_comp401_reviews.txt` |
| 2 | Rate My Professors (UNC) | Reviews of Kaur (COMP 311), Singh (COMP 411), Pozefsky (COMP 523), Prins (COMP 455) | ratemyprofessors.com — UNC Chapel Hill CS dept / `doc_06_rmp_more_professors.txt` |
| 3 | Rate My Professors (UNC) | Reviews of Kris Jordan (COMP 110, COMP 423) | ratemyprofessors.com — UNC Chapel Hill CS dept / `doc_12_jordan_reviews.txt` |
| 4 | Rate My Professors (UNC) | Reviews of Kevin Jeffay (COMP 431 - Internet Services) | ratemyprofessors.com — UNC Chapel Hill CS dept / `doc_13_jeffay_reviews.txt` |
| 5 | Rate My Professors (UNC) | Reviews of Jim Anderson (COMP 530 - Operating Systems) | ratemyprofessors.com — UNC Chapel Hill CS dept / `doc_14_anderson_reviews.txt` |
| 6 | Rate My Professors (UNC) | Reviews of David Stotts (COMP 283 - Discrete Math, COMP 550 - Algorithms) | ratemyprofessors.com — UNC Chapel Hill CS dept / `doc_15_stotts_reviews.txt` |
| 7 | Rate My Professors (UNC) | Reviews of Jeff Terrell (COMP 421 - Databases, COMP 110) | ratemyprofessors.com — UNC Chapel Hill CS dept / `doc_16_terrell_reviews.txt` |
| 8 | Rate My Professors (UNC) | Reviews of Brent Munsell (COMP 572 - Computer Vision) | ratemyprofessors.com — UNC Chapel Hill CS dept / `doc_17_munsell_reviews.txt` |
| 9 | Rate My Professors (UNC) | Reviews of Jack Snoeyink (COMP 410 - Data Structures) | ratemyprofessors.com — UNC Chapel Hill CS dept / `doc_18_snoeyink_reviews.txt` |
| 10 | Rate My Professors (UNC) | Reviews of Fabian Monrose (COMP 435 - Computer Security) | ratemyprofessors.com — UNC Chapel Hill CS dept / `doc_19_monrose_reviews.txt` |

---

## Chunking Strategy

**Chunk size:** 400 characters

**Overlap:** 80 characters

**Reasoning:** The documents are made up of short review paragraphs — typically 2 to 6 sentences per review. A 400-character chunk captures roughly 2–3 sentences, which is enough to hold one complete student opinion (e.g., what a professor's exams are like, or how useful office hours are) without mixing it with a different topic. Chunks smaller than this (e.g., 150 characters) would break individual opinions into sentence fragments that can't stand alone to answer a query. Chunks larger than this (e.g., 1000 characters) would blend several different opinions into one embedding, making it harder to match a specific question to the right content. The 80-character overlap ensures that if a key fact (like "no curves" or "exams are based on assignments") happens to fall near a chunk boundary, at least one of the two surrounding chunks will still contain it in full. Each chunk boundary is also snapped backward to the nearest sentence end so chunks don't cut mid-sentence.

---

## Retrieval Approach

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers`

**Top-k:** 5 chunks per query

**Production tradeoff reflection:** `all-MiniLM-L6-v2` was chosen because it runs fully locally — no API key, no rate limits, no cost — which is practical for a student project. It produces 384-dimensional embeddings and handles informal English (review and Reddit-style text) well. For a real production deployment I would weigh several tradeoffs: **accuracy** — OpenAI `text-embedding-3-large` and Cohere `embed-v3` outperform MiniLM on retrieval benchmarks, especially for nuanced or domain-specific queries; **context length** — MiniLM truncates at 256 tokens, whereas OpenAI embeddings support up to 8,191 tokens, which matters if documents are long; **multilingual support** — MiniLM is English-only, so a diverse user base would require something like `multilingual-e5-large`; **latency** — local models have no network round-trip overhead, while API-based models add latency; **cost** — MiniLM is free, while `text-embedding-3-small` costs approximately $0.02 per million tokens. For production I would likely choose `text-embedding-3-small` for the best accuracy-to-cost ratio and its longer context window.

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What are COMP 401 exams like and how should I prepare? | Exams are based almost entirely on the assignments. Understanding every line of code you wrote is the best preparation. Two midterms and a cumulative final. No curves. Study design patterns specifically. |
| 2 | Is Kris Jordan a good professor for intro CS? | Yes — consistently rated highly. Known for making coding accessible to beginners, creative projects, clear instructions, and a well-run course. Good choice for students new to programming. |
| 3 | What is COMP 530 (Operating Systems) like and is it worth taking? | It is a demanding course involving implementing a real OS kernel in C over the semester. Hard but produces deep understanding of how computers work. Worth it for students interested in systems, embedded, or infrastructure roles. |
| 4 | How difficult is COMP 421 (Databases) and what does it cover? | Manageable workload. Covers SQL, schema design, normalization, and transactions. Jeff Terrell teaches it clearly. Assignments are realistic and skills transfer directly to internships. |
| 5 | What do students say about Diane Pozefsky and COMP 523? | Pozefsky is described as direct and supportive. COMP 523 is a real client software project spanning a full semester. Teaches Git workflow, standups, stakeholder communication, and demos. Considered one of the best courses in the major. |

---

## Anticipated Challenges

1. **Chunk boundary splitting key review facts:** A specific piece of advice — like "no curves" or "exams are based on assignments" — might span a sentence that falls right at a chunk boundary. If so, neither of the two surrounding chunks may contain that fact completely, and retrieval will miss it. The 80-character overlap reduces this risk but can't eliminate it for facts spread across multiple sentences or paragraphs.

2. **Query-vocabulary mismatch with professor nicknames and acronyms:** Students often search using professor nicknames (e.g., "KMP" for Ketan Mayer-Patel) or course abbreviations that may not appear in every review. If the query uses "KMP" but a chunk says "Ketan Mayer-Patel," the embedding model may not recognize them as the same person, causing relevant chunks to rank lower than they should. Semantic embeddings help with paraphrasing but struggle with proper-noun acronyms that are out-of-vocabulary for the model.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     OFFLINE: Build Index                    │
│                                                             │
│  documents/*.txt  (10 professor review files)               │
│       │                                                     │
│       ▼                                                     │
│  [ingest.py]  load → clean → chunk                          │
│  Tool: Python (re, pathlib)                                 │
│  Chunk size: 400 chars | Overlap: 80 chars                  │
│       │                                                     │
│       ▼  chunk dicts (text, source, chunk_id)               │
│  [embed.py]   embed all chunks                              │
│  Model: all-MiniLM-L6-v2 (sentence-transformers)            │
│       │                                                     │
│       ▼  384-dim vectors + source metadata                  │
│  [ChromaDB]   persistent local vector store                 │
│  Similarity: cosine distance                                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    ONLINE: Query Pipeline                   │
│                                                             │
│  User query (natural language question)                     │
│       │                                                     │
│       ▼                                                     │
│  [query.py]   embed query with all-MiniLM-L6-v2             │
│               → cosine similarity search in ChromaDB        │
│               → return top-5 chunks + source filenames      │
│       │                                                     │
│       ▼  top-5 chunks with source metadata                  │
│  [query.py]   grounded generation                           │
│  LLM: Groq llama-3.3-70b-versatile                         │
│  Prompt: answer ONLY from retrieved context,                │
│          cite sources, decline if insufficient              │
│       │                                                     │
│       ▼  answer text + source list                          │
│  [app.py]     Gradio web UI (http://localhost:7860)         │
│  Inputs: question textbox                                   │
│  Outputs: answer, sources, chunk debug view                 │
└─────────────────────────────────────────────────────────────┘
```

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**
I gave Claude the Chunking Strategy section of this planning.md along with a description of the document structure (short review paragraphs, 2–6 sentences each, plain .txt files). Claude generated `ingest.py` including `load_documents()`, `clean_text()`, and `split_into_chunks()`. The initial generated version used a plain character slice with no sentence-boundary awareness — I directed Claude to revise it to snap each chunk boundary backward to the nearest sentence-ending punctuation (`.`, `?`, `!`) within the last 60 characters. I also added a minimum chunk length filter (`len(chunk) > 30`) myself after seeing empty-string chunks in the first test run. I verified the output by printing 5 sample chunks and checking each was self-contained and readable.

**Milestone 4 — Embedding and retrieval:**
I gave Claude the Retrieval Approach section of this planning.md and the architecture diagram above. Claude generated `embed.py` with the batch embedding loop, ChromaDB collection setup with cosine similarity, `add()` calls with source metadata, and a test retrieval function. I verified it used `all-MiniLM-L6-v2` (not a different model), stored the `source` field in metadata correctly for attribution, and returned distance scores below 0.5 on relevant queries. I also confirmed the `PersistentClient` was used so the index survives between runs.

**Milestone 5 — Generation and interface:**
I gave Claude the grounding requirement ("answer only from retrieved context, cite sources, say 'I don't have enough information' if the documents don't cover the question") and the Gradio layout spec (question input, answer output, sources display, collapsible chunk debug view). Claude's first system prompt draft included the phrase "use your best judgment to supplement if needed" — I removed that line and replaced it with an explicit fallback instruction to ensure refusal behavior is deterministic and not left to the model's discretion. I verified the final `app.py` by testing an out-of-scope question and confirming the system declined rather than hallucinating.
