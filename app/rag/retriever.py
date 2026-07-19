from app.rag.embeddings import get_embedding

def retrieve_context(query, vector_store):
    query_embedding = get_embedding(query)
    results = vector_store.search(query_embedding, top_k=3)
    return results