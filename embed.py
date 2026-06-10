"""
embed.py - Embedding and vector store setup
UNC Unofficial Guide RAG System

Embeds all chunks using sentence-transformers (all-MiniLM-L6-v2)
and stores them in a local ChromaDB collection with source metadata.
Run this ONCE (or re-run to rebuild the index) before using query.py.
"""

import chromadb
from sentence_transformers import SentenceTransformer
from ingest import run_pipeline

COLLECTION_NAME = "unc_unofficial_guide"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_PATH = "./chroma_db"


def build_vector_store(chunks: list[dict]) -> chromadb.Collection:
    """
    Embed all chunks and store them in ChromaDB.
    Returns the ChromaDB collection.
    """
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print(f"Setting up ChromaDB at {CHROMA_PATH}")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Drop and recreate collection for a clean build
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing collection '{COLLECTION_NAME}'")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # use cosine similarity
    )

    # Extract fields for batch embedding
    texts = [c["text"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]
    metadatas = [{"source": c["source"]} for c in chunks]

    # Embed in batches for memory efficiency
    BATCH_SIZE = 64
    all_embeddings = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i: i + BATCH_SIZE]
        embeddings = model.encode(batch, show_progress_bar=False).tolist()
        all_embeddings.extend(embeddings)
        print(f"  Embedded {min(i + BATCH_SIZE, len(texts))}/{len(texts)} chunks")

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=all_embeddings,
        metadatas=metadatas,
    )

    print(f"\nStored {collection.count()} chunks in ChromaDB collection '{COLLECTION_NAME}'")
    return collection


def test_retrieval(collection: chromadb.Collection, model: SentenceTransformer,
                   test_queries: list[str], top_k: int = 4) -> None:
    """Run a few test queries and print results for manual inspection."""
    print(f"\n{'='*60}")
    print("RETRIEVAL TEST")
    print(f"{'='*60}")

    for query in test_queries:
        print(f"\nQuery: {query!r}")
        query_embedding = model.encode(query).tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        for i, (doc, meta, dist) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )):
            print(f"  Result {i+1} | Source: {meta['source']} | Distance: {dist:.4f}")
            print(f"    {doc[:200]}...")


if __name__ == "__main__":
    # Run ingestion pipeline
    chunks = run_pipeline()

    # Build the vector store
    collection = build_vector_store(chunks)

    # Quick retrieval test
    model = SentenceTransformer(EMBEDDING_MODEL)
    test_queries = [
    "How hard is COMP 401 and what are the exams like?",
    "Is Kris Jordan a good professor for beginners?",
    "What is COMP 530 Operating Systems like?",
]
    test_retrieval(collection, model, test_queries)
