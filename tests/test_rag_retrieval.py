from types import SimpleNamespace

from app.rag.retriever import retrieve_context


class FakeVectorStore:
    def __init__(self, results):
        self.results = results
        self.received_query = None
        self.received_top_k = None

    def search(self, query_embedding, top_k=3):
        self.received_top_k = top_k
        return self.results


def test_retrieve_context_normalizes_query_and_removes_duplicate_chunks(monkeypatch):
    chunks = [
        SimpleNamespace(page_content="Revenue increased 20%.", metadata={}),
        SimpleNamespace(page_content="Revenue increased 20%.", metadata={}),
        SimpleNamespace(page_content="Operating margin improved.", metadata={}),
    ]
    store = FakeVectorStore(chunks)

    monkeypatch.setattr("app.rag.retriever.get_embedding", lambda text: [0.1, 0.2])

    results = retrieve_context("  revenue   performance  ", store)

    assert len(results) == 2
    assert results[0].page_content == "Revenue increased 20%."
    assert results[1].page_content == "Operating margin improved."
    assert store.received_top_k == 5


def test_retrieve_context_returns_empty_for_blank_query():
    store = FakeVectorStore([])

    assert retrieve_context("   ", store) == []
    assert store.received_top_k is None
