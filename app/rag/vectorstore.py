import os
import pickle
import shutil
from pathlib import Path
from threading import Lock
from typing import Optional

import faiss
import numpy as np

from app.rag.embeddings import get_embedding


# =========================================================
# CONFIGURATION
# =========================================================

VECTOR_STORE_ROOT = Path("data") / "vector_stores"
EMBEDDING_DIMENSION = 384

VECTOR_STORE_ROOT.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# VECTOR STORE
# =========================================================

class VectorStore:
    def __init__(
        self,
        dimension: int = EMBEDDING_DIMENSION,
        session_id: Optional[str] = None,
    ):
        self.dimension = dimension
        self.session_id = session_id

        self.index = faiss.IndexFlatL2(
            dimension
        )

        self.documents = []


    def add(
        self,
        embedding,
        document
    ):
        embedding = np.asarray(
            embedding,
            dtype=np.float32
        ).reshape(1, -1)

        if embedding.shape[1] != self.dimension:
            raise ValueError(
                f"Embedding dimension mismatch. "
                f"Expected {self.dimension}, "
                f"received {embedding.shape[1]}"
            )

        self.index.add(
            embedding
        )

        self.documents.append(
            document
        )


    def search(
        self,
        query_embedding,
        top_k: int = 3
    ):
        if self.index.ntotal == 0:
            return []

        query_embedding = np.asarray(
            query_embedding,
            dtype=np.float32
        ).reshape(1, -1)

        if query_embedding.shape[1] != self.dimension:
            raise ValueError(
                f"Query embedding dimension mismatch. "
                f"Expected {self.dimension}, "
                f"received {query_embedding.shape[1]}"
            )

        k = min(
            top_k,
            self.index.ntotal
        )

        distances, indices = self.index.search(
            query_embedding,
            k
        )

        results = []

        for idx in indices[0]:

            if (
                idx >= 0
                and idx < len(self.documents)
            ):
                results.append(
                    self.documents[idx]
                )

        return results


# =========================================================
# IN-MEMORY SESSION CACHE
# =========================================================

_vector_stores = {}

_store_lock = Lock()


# =========================================================
# PATH HELPERS
# =========================================================

def _safe_session_id(
    session_id: str
) -> str:
    """
    Convert session ID into a safe directory name.
    """

    safe_id = "".join(
        char
        if char.isalnum()
        or char in ("-", "_")
        else "_"
        for char in session_id
    )

    return safe_id or "default"


def _get_session_directory(
    session_id: str
) -> Path:

    safe_id = _safe_session_id(
        session_id
    )

    return (
        VECTOR_STORE_ROOT
        / safe_id
    )


def _get_index_path(
    session_id: str
) -> Path:

    return (
        _get_session_directory(
            session_id
        )
        / "index.faiss"
    )


def _get_documents_path(
    session_id: str
) -> Path:

    return (
        _get_session_directory(
            session_id
        )
        / "documents.pkl"
    )


# =========================================================
# PERSIST VECTOR STORE
# =========================================================

def save_vector_store(
    session_id: str
) -> bool:

    vector_store = _vector_stores.get(
        session_id
    )

    if vector_store is None:
        return False

    session_directory = (
        _get_session_directory(
            session_id
        )
    )

    session_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    index_path = _get_index_path(
        session_id
    )

    documents_path = (
        _get_documents_path(
            session_id
        )
    )

    faiss.write_index(
        vector_store.index,
        str(index_path)
    )

    with open(
        documents_path,
        "wb"
    ) as file:

        pickle.dump(
            vector_store.documents,
            file
        )

    return True


# =========================================================
# LOAD VECTOR STORE
# =========================================================

def load_vector_store(
    session_id: str
) -> Optional[VectorStore]:

    index_path = _get_index_path(
        session_id
    )

    documents_path = (
        _get_documents_path(
            session_id
        )
    )

    if (
        not index_path.exists()
        or not documents_path.exists()
    ):
        return None

    try:

        index = faiss.read_index(
            str(index_path)
        )

        with open(
            documents_path,
            "rb"
        ) as file:

            documents = pickle.load(
                file
            )

        if (
            index.ntotal
            != len(documents)
        ):
            raise ValueError(
                "FAISS index and document "
                "metadata are inconsistent."
            )

        vector_store = VectorStore(
            dimension=index.d,
            session_id=session_id
        )

        vector_store.index = index
        vector_store.documents = documents

        return vector_store

    except Exception as error:

        print(
            f"Failed to load vector store "
            f"for session {session_id}: "
            f"{error}"
        )

        return None


# =========================================================
# GET SESSION VECTOR STORE
# =========================================================

def get_vector_store(
    session_id: str
) -> VectorStore:

    with _store_lock:

        if session_id in _vector_stores:

            return _vector_stores[
                session_id
            ]

        # Try loading persistent FAISS data
        vector_store = load_vector_store(
            session_id
        )

        # No persistent data exists
        if vector_store is None:

            vector_store = VectorStore(
                dimension=EMBEDDING_DIMENSION,
                session_id=session_id
            )

        _vector_stores[
            session_id
        ] = vector_store

        return vector_store


# =========================================================
# CREATE / UPDATE VECTOR STORE
# =========================================================

def create_vectorstore(
    chunks=None,
    session_id: str = "default"
):

    vector_store = get_vector_store(
        session_id
    )

    if not chunks:

        return vector_store

    for chunk in chunks:

        text = (
            chunk.page_content
            if hasattr(
                chunk,
                "page_content"
            )
            else str(chunk)
        )

        embedding = get_embedding(
            text
        )

        vector_store.add(
            embedding,
            chunk
        )

    # Persist after adding all chunks
    save_vector_store(
        session_id
    )

    return vector_store


# =========================================================
# CLEAR SESSION VECTOR STORE
# =========================================================

def clear_vector_store(
    session_id: str
) -> bool:

    removed = False

    with _store_lock:

        if session_id in _vector_stores:

            del _vector_stores[
                session_id
            ]

            removed = True

    session_directory = (
        _get_session_directory(
            session_id
        )
    )

    if session_directory.exists():

        shutil.rmtree(
            session_directory
        )

        removed = True

    return removed


# =========================================================
# CHECK SESSION VECTOR STORE
# =========================================================

def has_vector_store(
    session_id: str
) -> bool:

    vector_store = get_vector_store(
        session_id
    )

    return (
        vector_store.index.ntotal
        > 0
    )


# =========================================================
# VECTOR STORE INFORMATION
# =========================================================

def get_vector_store_info(
    session_id: str
) -> dict:

    vector_store = get_vector_store(
        session_id
    )

    filenames = set()

    for document in (
        vector_store.documents
    ):

        metadata = getattr(
            document,
            "metadata",
            {}
        )

        filename = metadata.get(
            "filename"
        )

        if filename:

            filenames.add(
                filename
            )

    return {
        "session_id": session_id,
        "total_chunks": (
            vector_store.index.ntotal
        ),
        "total_documents": len(
            filenames
        ),
        "documents": sorted(
            filenames
        ),
        "persistent": True,
    }