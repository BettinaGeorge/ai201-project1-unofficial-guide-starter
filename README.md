# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

Student reviews of CS professors and courses at UNC Chapel Hill. This knowledge is valuable because it reflects honest, peer-to-peer student experience that no official university source provides — Rate My Professors reviews contain the real picture of what a professor's exams are like, how heavy the workload is, whether office hours are useful, and whether a course is worth taking. The official course catalog describes what a class covers but says nothing about teaching quality, grading style, or how students actually experience it. This information exists but is scattered across multiple platforms, buried under unrelated content, and impossible to query with a specific natural-language question like "what are KMP's exams like?" or "is COMP 530 worth taking if I want to do systems work?"

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors — UNC Chapel Hill | Professor reviews | ratemyprofessors.com (UNC CS dept) / `doc_01_comp401_reviews.txt` |
| 2 | Rate My Professors — UNC Chapel Hill | Professor reviews | ratemyprofessors.com (UNC CS dept) / `doc_06_rmp_more_professors.txt` |
| 3 | Rate My Professors — UNC Chapel Hill | Professor reviews | ratemyprofessors.com (UNC CS dept) / `doc_12_jordan_reviews.txt` |
| 4 | Rate My Professors — UNC Chapel Hill | Professor reviews | ratemyprofessors.com (UNC CS dept) / `doc_13_jeffay_reviews.txt` |
| 5 | Rate My Professors — UNC Chapel Hill | Professor reviews | ratemyprofessors.com (UNC CS dept) / `doc_14_anderson_reviews.txt` |
| 6 | Rate My Professors — UNC Chapel Hill | Professor reviews | ratemyprofessors.com (UNC CS dept) / `doc_15_stotts_reviews.txt` |
| 7 | Rate My Professors — UNC Chapel Hill | Professor reviews | ratemyprofessors.com (UNC CS dept) / `doc_16_terrell_reviews.txt` |
| 8 | Rate My Professors — UNC Chapel Hill | Professor reviews | ratemyprofessors.com (UNC CS dept) / `doc_17_munsell_reviews.txt` |
| 9 | Rate My Professors — UNC Chapel Hill | Professor reviews | ratemyprofessors.com (UNC CS dept) / `doc_18_snoeyink_reviews.txt` |
| 10 | Rate My Professors — UNC Chapel Hill | Professor reviews | ratemyprofessors.com (UNC CS dept) / `doc_19_monrose_reviews.txt` |

---

## Chunking Strategy

**Chunk size:** 400 characters

**Overlap:** 80 characters

**Why these choices fit your documents:** The documents are composed of short review paragraphs — typically 2 to 6 sentences per review. A 400-character chunk captures roughly 2–3 complete sentences, which is enough to hold one self-contained student opinion (e.g., what a professor's exams are like, or whether office hours are useful) without blending it with unrelated content from a different review. Chunks smaller than this (e.g., 150 characters) would break individual opinions into sentence fragments that can't stand alone to answer a query. Chunks larger than this (e.g., 1000 characters) would merge several different opinions about different topics into one embedding, making it harder to match a specific question to the right content. The 80-character overlap ensures that if a key fact falls near a chunk boundary, at least one of the two surrounding chunks still contains it. Each chunk boundary is also snapped backward to the nearest sentence-ending punctuation (`.`, `?`, `!`) within 60 characters so chunks don't cut mid-sentence. Chunks shorter than 60 characters are filtered out to remove tail fragments.

**Final chunk count:** 103 chunks across 10 documents

---

## Sample Chunks

Five representative chunks from the final pipeline, each shown with its source document:

**Chunk 1** — Source: `doc_01_comp401_reviews.txt`
> "Professor: Ketan Mayer-Patel (COMP 401 - Foundations of Programming) Rating: 3.2/5 Review 1: KMP is brilliant but moves at lightning speed. If you don't do the assignments every week you will fall behind and there's no catching up."

**Chunk 2** — Source: `doc_01_comp401_reviews.txt`
> "ssignments - if you understand every line of code you wrote, you'll be fine. Don't expect curves. Attendance is not taken but you will be lost if you skip. Review 2: COMP 401 with KMP is the weed-out course for CS majors."

**Chunk 3** — Source: `doc_12_jordan_reviews.txt`
> "Professor: Kris Jordan (COMP 110 - Introduction to Programming, COMP 423 - Foundations of Software Engineering) Rating: 4.7/5 Review 1: Kris Jordan is genuinely one of the best professors in the CS department. He redesigned COMP 110 from scratch and it shows."

**Chunk 4** — Source: `doc_14_anderson_reviews.txt`
> "Professor: Jim Anderson (COMP 530 - Operating Systems, COMP 530L - OS Lab) Rating: 3.7/5 Review 1: Anderson is one of the most knowledgeable professors in the department on systems topics. COMP 530 is a serious course - you implement a real operating system kernel over the semester in C."

**Chunk 5** — Source: `doc_06_rmp_more_professors.txt`
> "MP 523 - Software Engineering Lab) Rating: 4.5/5 Review 1: Pozefsky is a legend in the department. COMP 523 is unlike any other CS course - you're working with a real external client on an actual software project. She manages the chaos really well."

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`

**Production tradeoff reflection:** `all-MiniLM-L6-v2` was chosen because it runs fully locally with no API key, no rate limits, and no cost — practical for a student prototype. It produces 384-dimensional embeddings and handles informal English (review-style text) well. For a real production deployment I would weigh several tradeoffs. For **accuracy**, OpenAI `text-embedding-3-large` and Cohere `embed-v3` consistently outperform MiniLM on retrieval benchmarks, especially for nuanced queries about specific course details. For **context length**, MiniLM truncates at 256 tokens, whereas OpenAI embeddings support up to 8,191 tokens — relevant if documents are longer. For **multilingual support**, MiniLM is English-only; a diverse university user base might require `multilingual-e5-large`. For **latency**, local models have no network overhead while API-based models add round-trip time. For **cost**, MiniLM is free while `text-embedding-3-small` costs approximately $0.02 per million tokens — negligible at low volume but adds infrastructure dependency. For production I would choose `text-embedding-3-small` for the best accuracy-to-cost ratio and longer context window.

---

## Retrieval Test Results

**Query 1:** "How hard is COMP 401 and what are the exams like?"

| Rank | Source | Distance | Chunk preview |
|------|--------|----------|---------------|
| 1 | `doc_01_comp401_reviews.txt` | 0.4515 | "ssignments - if you understand every line of code you wrote, you'll be fine. Don't expect curves..." |
| 2 | `doc_06_rmp_more_professors.txt` | 0.5550 | "than once for that section. Her exam style is to give you a small program and ask you to trace through it..." |
| 3 | `doc_01_comp401_reviews.txt` | 0.5590 | "Professor: Ketan Mayer-Patel (COMP 401 - Foundations of Programming) Rating: 3.2/5 Review 1: KMP is brilliant..." |

**Why results 1 and 3 are relevant:** Both chunks come from `doc_01_comp401_reviews.txt`, the dedicated COMP 401 review file. Result 1 directly answers the exam question ("understand every line of code you wrote, you'll be fine. Don't expect curves"). Result 3 introduces the professor and course context. The low distances (0.45 and 0.56) confirm strong semantic alignment between the query and these chunks.

---

**Query 2:** "Is Kris Jordan a good professor for beginners?"

| Rank | Source | Distance | Chunk preview |
|------|--------|----------|---------------|
| 1 | `doc_12_jordan_reviews.txt` | 0.4361 | "Professor: Kris Jordan (COMP 110 - Introduction to Programming...) Rating: 4.7/5 Review 1: Kris Jordan is genuinely one of the best professors..." |
| 2 | `doc_17_munsell_reviews.txt` | 0.4418 | "as undergrads, he is one of the better faculty to approach. Show up knowing the basics..." |
| 3 | `doc_06_rmp_more_professors.txt` | 0.4851 | "Professor: Jasleen Kaur (COMP 311 - Systems Fundamentals) Rating: 4.3/5..." |

**Why result 1 is relevant:** The top chunk comes directly from the Jordan review file and contains his name, the intro course (COMP 110), and his rating (4.7/5). The query phrase "good for beginners" semantically matches "Introduction to Programming" and "one of the best professors," which is why this chunk ranked first with distance 0.44.

---

**Query 3:** "What is COMP 530 Operating Systems like?"

| Rank | Source | Distance | Chunk preview |
|------|--------|----------|---------------|
| 1 | `doc_14_anderson_reviews.txt` | 0.3384 | "Professor: Jim Anderson (COMP 530 - Operating Systems, COMP 530L - OS Lab)..." |
| 2 | `doc_14_anderson_reviews.txt` | 0.6361 | "but when you're done you genuinely understand how computers work at a level most CS graduates never reach..." |
| 3 | `doc_16_terrell_reviews.txt` | 0.6615 | "uches databases - take COMP 421 with Terrell..." |

---

## Grounded Generation

**System prompt grounding instruction:** The system prompt explicitly tells the model: *"Base your answer EXCLUSIVELY on the provided context. Do not use general knowledge or make up information. If the documents do not contain enough information to answer the question, say exactly: 'I don't have enough information in my documents to answer that.'"* The temperature is set to 0.2 to reduce creative extrapolation. The retrieved chunks are passed directly in the user message as numbered, labeled context blocks (e.g., `[Document 1 | Source: doc_01_comp401_reviews.txt]`) so the model sees exactly where each piece of information comes from.

**How source attribution is surfaced in the response:** Source attribution is enforced programmatically — after generation, the `ask()` function collects the `source` field from each retrieved chunk and deduplicates them into a list, which is returned separately from the LLM answer. The Gradio UI displays this list in a dedicated "Retrieved from" field. This means source attribution is always present even if the LLM omits it in its text, because it is appended by the pipeline, not left to the model to include.

---

## Example Responses

**Response 1 — Grounded answer with source attribution:**

> **Query:** What are COMP 401 exams like and how should students prepare?
>
> **Answer:** According to Document 1 and Document 2, COMP 401 exams are based almost entirely on the assignments. To prepare, students should understand every line of code they wrote for the assignments. If they do, they will be fine. It is also mentioned that lectures are recorded, which can be helpful for review. Additionally, it is advised not to fall behind on assignments, as it can be difficult to catch up.
>
> **Retrieved from:** doc_01_comp401_reviews.txt, doc_13_jeffay_reviews.txt, doc_06_rmp_more_professors.txt

---

**Response 2 — Grounded answer with source attribution:**

> **Query:** What do students say about Diane Pozefsky and COMP 523?
>
> **Answer:** According to the documents, students say that Diane Pozefsky is a "legend in the department" and that COMP 523 - Software Engineering Lab is "unlike any other CS course." They appreciate that she manages the chaos of working with real external clients well, is direct, gives useful feedback, and wants teams to produce something they're proud of. Additionally, students note that the grade in COMP 523 depends heavily on team and client relationship, and that Pozefsky checks in throughout the semester to ensure everyone is contributing. Overall, she has a rating of 4.5/5.
>
> **Retrieved from:** doc_06_rmp_more_professors.txt, doc_18_snoeyink_reviews.txt, doc_15_stotts_reviews.txt

---

**Out-of-scope refusal:**

> **Query:** What is the current tuition at UNC Chapel Hill for out-of-state students?
>
> **Answer:** I don't have enough information in my documents to answer that.
>
> **Retrieved from:** doc_14_anderson_reviews.txt, doc_01_comp401_reviews.txt, doc_06_rmp_more_professors.txt

---

## Query Interface

The system has a Gradio web UI (`app.py`) accessible at `http://localhost:7860` after running `python3 app.py`.

**Input fields:**
- **Your question** — a free-text textbox (2 rows). Submit by pressing Enter or clicking the "Ask the Guide" button.

**Output fields:**
- **Answer** — 8-row textbox showing the LLM-generated grounded response.
- **Retrieved from** — accordion (open by default) showing a bulleted list of source document filenames the answer drew from.
- **Retrieved chunks (debug view)** — collapsible accordion showing all top-5 retrieved chunks with their source filename and cosine distance score.

**Sample interaction transcript:**

```
Input: Is Kris Jordan a good professor for intro CS?

Answer:
According to the documents, yes, Kris Jordan is a good professor for intro CS.
Review 1 states that he "is genuinely one of the best professors in the CS
department" and that his redesign of COMP 110 "is modern, well-structured, and
actually fun." Review 7 also mentions that Kris Jordan "single-handedly made me
like CS" and that the course is "designed with beginners in mind." His use of
TypeScript instead of Python is seen as a positive aspect for web-focused
projects. Overall, the reviews suggest that Kris Jordan is a great professor
for intro CS, especially for beginners.

Retrieved from:
• doc_12_jordan_reviews.txt
• doc_18_snoeyink_reviews.txt
• doc_01_comp401_reviews.txt
```

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What are COMP 401 exams like and how should students prepare? | Exams based on assignments; understand every line you wrote. Two midterms + cumulative final. No curves. Study design patterns. | Exams are based almost entirely on the assignments; understanding every line of code written is key. Lectures are recorded for review. Don't fall behind on assignments. | Relevant | Partially accurate |
| 2 | Is Kris Jordan a good professor for intro CS? | Yes — rated 4.7/5, makes coding accessible to beginners, creative projects, clear instructions, well-run course. | Yes — rated 4.7/5, described as one of the best in the department, redesigned COMP 110 to be modern and fun, designed with beginners in mind. | Relevant | Accurate |
| 3 | What is COMP 530 Operating Systems like and is it worth taking? | Demanding — implement a real OS kernel in C. Hard but worth it for systems-oriented students. Take 311 and 411 first. | Serious, brutal and time-consuming course implementing a real OS kernel. Worth it for systems/embedded/infrastructure roles. Recommends taking 311 and 411 first. | Relevant | Accurate |
| 4 | How difficult is COMP 421 Databases and what does it cover? | Manageable workload. SQL, schema design, normalization, transactions. Terrell teaches clearly with live demos. Skills transfer to internships. | Well-taught with manageable workload. Covers SQL, normalization, transactions, indexing. No trick questions; keep up with SQL syntax. | Relevant | Accurate |
| 5 | What do students say about Diane Pozefsky and COMP 523? | Direct and supportive, a legend in the dept. Real client project all semester. Teaches Git, standups, stakeholder comms. One of the best courses in the major. | Described as a "legend in the department." COMP 523 involves real external clients, public demo, Pozefsky does check-ins throughout. Grade depends on team and client relationship. | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** Question 1 — "What are COMP 401 exams like and how should students prepare?"

**What the system returned:** The system correctly identified that exams are based on the assignments, but missed two specific facts from the expected answer: "no curves" and the grade breakdown (two midterms at 30%, cumulative final at 20%). The response was accurate in its main claim but incomplete.

**Root cause (tied to a specific pipeline stage):** The root cause is at the **chunking stage**. The chunk that contains "Don't expect curves" and the grade breakdown begins with `"ssignments - if you understand every line..."` — it is an overlap fragment that starts mid-sentence from the previous chunk. When the LLM received this chunk, the most important specific facts ("Don't expect curves," "two midterms (30%), and a final (20%)") appeared in the middle of a fragmented chunk alongside other content. The LLM synthesized the main message correctly but did not extract those specific numerical details. Additionally, retrieval pulled in two chunks from `doc_13_jeffay_reviews.txt` (about Kevin Jeffay's exams, not KMP) as results 3 and 4, which diluted the context with information about a different professor's exam style.

**What you would change to fix it:** Two changes would help. First, increase the minimum chunk length filter so that overlap-start fragments are dropped, reducing noise in retrieval. Second, reduce top-k from 5 to 3 for professor-specific queries to avoid pulling in chunks from other professors' reviews that share vocabulary (words like "exams," "assignments," "practice") but are about different people.

---

## Spec Reflection

**One way the spec helped you during implementation:** Writing the chunking strategy section of `planning.md` before writing any code forced a concrete decision about chunk size. Having committed to 400 characters with 80-character overlap before opening a code editor meant the `split_into_chunks()` function had a clear target to implement and test against. When the first run produced a tiny tail fragment (`"s runtime, you'll do well on his exams."` — 39 characters), the spec's reasoning made it obvious why that fragment was useless and what the fix should be: raise the minimum length filter from 30 to 60 characters.

**One way your implementation diverged from the spec, and why:** The spec described sentence-boundary snapping as part of the chunking strategy, but the initial AI-generated `ingest.py` used a plain character slice with no boundary awareness — chunks cut mid-sentence regularly. I had to explicitly direct a revision to add the snapping logic (scanning backward 60 characters for `.`, `?`, or `!`). The spec was correct in calling for this feature; the divergence was that the first implementation didn't include it, requiring a second pass.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The Chunking Strategy section of `planning.md` describing the document structure (short review paragraphs, 2–6 sentences each, plain `.txt` files), along with a request to implement `ingest.py` including `load_documents()`, `clean_text()`, and `split_into_chunks()` with 400-character chunks and 80-character overlap.
- *What it produced:* A working ingestion pipeline with all three functions. The `split_into_chunks()` function used a plain `text[start:end]` character slice with no sentence-boundary awareness, producing chunks that frequently cut mid-sentence.
- *What I changed or overrode:* I directed Claude to revise `split_into_chunks()` to snap each chunk boundary backward to the nearest sentence-ending punctuation (`.`, `?`, `!`) within the last 60 characters. I also added a minimum chunk length filter (`len(chunk) > 60`) myself after observing a 39-character tail fragment in the first test run that the original `> 30` filter failed to catch.

**Instance 2**

- *What I gave the AI:* The grounding requirement for `query.py`: "the model must answer only from the provided retrieved context, must cite sources, and must decline with a specific phrase if the documents don't contain enough information."
- *What it produced:* A system prompt and `generate_answer()` function using the Groq API. The first draft of the system prompt included the phrase "use your best judgment to supplement if needed" — which directly contradicted the grounding requirement.
- *What I changed or overrode:* I removed the "supplement" phrase entirely and replaced it with an explicit fallback instruction: *"If the documents do not contain enough information to answer the question, say exactly: 'I don't have enough information in my documents to answer that.'"* This makes refusal behavior deterministic rather than leaving it to the model's judgment. I verified the change worked by testing an out-of-scope question (tuition cost) and confirming the system returned the exact refusal phrase rather than hallucinating an answer.
