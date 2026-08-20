from app.rag.embeddings import get_embedding


DEFAULT_TOP_K = 5


def retrieve_context(query: str, vector_store, top_k: int = DEFAULT_TOP_K):
    """Retrieve a small, diverse context set for the current query."""
    cleaned_query = " ".join(query.split())

    if not cleaned_query:
        return []

    query_embedding = get_embedding(cleaned_query)
    results = vector_store.search(query_embedding, top_k=top_k)

    # Avoid feeding duplicate chunks to the LLM when ingestion produces repeats.
    unique_results = []
    seen = set()

    for document in results:
        text = getattr(document, "page_content", str(document)).strip()
        fingerprint = text

        if not text or fingerprint in seen:
            continue

        seen.add(fingerprint)
        unique_results.append(document)

    return unique_results
