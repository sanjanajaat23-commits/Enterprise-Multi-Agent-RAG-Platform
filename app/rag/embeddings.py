from functools import lru_cache

from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    print("Loading embedding model...")
    return SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str):
    model = get_embedding_model()
    return model.encode(text).tolist()