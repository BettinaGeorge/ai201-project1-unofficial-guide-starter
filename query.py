"""
query.py - Retrieval and grounded response generation
UNC Unofficial Guide RAG System

Given a user query, retrieves the top-k most relevant chunks from ChromaDB
and generates a grounded answer using Groq (llama-3.3-70b-versatile).
Answers are strictly grounded in retrieved context; source attribution is
both instructed in the prompt and appended programmatically.
"""

import os
from typing import Optional
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq

load_dotenv()

COLLECTION_NAME = "unc_unofficial_guide"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_PATH = "./chroma_db"
GROQ_MODEL = "llama-3.3-70b-versatile"
TOP_K = 5  # number of chunks to retrieve per query

# ─── Singletons (loaded once, reused across calls) ───────────────────────────

_model: Optional[SentenceTransformer] = None
_collection: Optional[chromadb.Collection] = None
_groq_client: Optional[Groq] = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def _get_collection() -> chromadb.Collection:
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def _get_groq() -> Groq:
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found. Set it in your .env file.")
        _groq_client = Groq(api_key=api_key)
    return _groq_client


# ─── Retrieval ────────────────────────────────────────────────────────────────

def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    """
    Embed the query and return the top-k most similar chunks from ChromaDB.
    Each result dict has: text, source, distance.
    """
    model = _get_model()
    collection = _get_collection()

    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text": doc,
            "source": meta["source"],
            "distance": dist,
        })
    return chunks


# ─── Generation ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are the UNC Unofficial Guide — a helpful assistant that answers questions \
about UNC Chapel Hill student life using ONLY the information provided in the retrieved documents below.

Rules you must follow:
1. Base your answer EXCLUSIVELY on the provided context. Do not use general knowledge or make up information.
2. If the documents do not contain enough information to answer the question, say exactly: \
"I don't have enough information in my documents to answer that."
3. Be specific and cite facts from the documents rather than speaking in generalities.
4. Do not speculate beyond what the documents say.
5. Keep your answer clear and helpful — write in plain language a fellow student would appreciate."""


def generate_answer(query: str, chunks: list[dict]) -> str:
    """
    Generate a grounded answer from retrieved chunks using Groq LLM.
    Context is passed explicitly; sources are appended programmatically.
    """
    if not chunks:
        return "I don't have enough information in my documents to answer that."

    # Build the context block
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(f"[Document {i} | Source: {chunk['source']}]\n{chunk['text']}")
    context = "\n\n".join(context_parts)

    user_message = f"""Context documents:
{context}

Question: {query}

Answer based only on the context above:"""

    groq = _get_groq()
    response = groq.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,  # low temperature for factual grounding
        max_tokens=600,
    )

    return response.choices[0].message.content.strip()


# ─── End-to-end ask() function ────────────────────────────────────────────────

def ask(query: str, top_k: int = TOP_K) -> dict:
    """
    Full RAG pipeline: retrieve → generate.
    Returns a dict with keys: answer, sources, chunks.
    """
    chunks = retrieve(query, top_k=top_k)
    answer = generate_answer(query, chunks)

    # Deduplicate sources while preserving order
    seen = set()
    sources = []
    for chunk in chunks:
        if chunk["source"] not in seen:
            seen.add(chunk["source"])
            sources.append(chunk["source"])

    return {
        "answer": answer,
        "sources": sources,
        "chunks": chunks,
    }


# ─── CLI entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("UNC Unofficial Guide — RAG Query CLI")
    print("Type 'quit' to exit.\n")

    while True:
        query = input("Your question: ").strip()
        if query.lower() in ("quit", "exit", "q"):
            break
        if not query:
            continue

        result = ask(query)
        print(f"\nAnswer:\n{result['answer']}")
        print(f"\nSources: {', '.join(result['sources'])}")
        print("-" * 60)
