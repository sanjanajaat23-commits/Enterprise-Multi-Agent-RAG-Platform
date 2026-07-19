from pathlib import Path
import shutil

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.rag.loader import load_pdf
from app.rag.splitter import split_documents
from app.rag.vectorstore import (
    create_vectorstore,
    get_vector_store_info,
    clear_vector_store,
)


router = APIRouter()

UPLOAD_ROOT = Path("uploads")


# =========================================================
# UPLOAD DOCUMENT
# =========================================================

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    """
    Upload a PDF and store its embeddings inside
    the current session's persistent FAISS vector store.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    session_upload_dir = (
        UPLOAD_ROOT / session_id
    )

    session_upload_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = (
        session_upload_dir / file.filename
    )

    try:
        with open(
            file_path,
            "wb"
        ) as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        # Load PDF
        documents = load_pdf(
            str(file_path)
        )

        if not documents:
            raise HTTPException(
                status_code=400,
                detail="No readable content found in PDF."
            )

        # Split PDF into chunks
        chunks = split_documents(
            documents
        )

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="Unable to create document chunks."
            )

        # Add metadata
        for chunk in chunks:
            chunk.metadata[
                "session_id"
            ] = session_id

            chunk.metadata[
                "filename"
            ] = file.filename

        # Add to persistent session FAISS store
        create_vectorstore(
            chunks,
            session_id=session_id
        )

        info = get_vector_store_info(
            session_id
        )

        return {
            "status": "success",
            "session_id": session_id,
            "filename": file.filename,
            "pages": len(documents),
            "chunks_added": len(chunks),
            "total_chunks": info[
                "total_chunks"
            ],
            "total_documents": info[
                "total_documents"
            ],
            "documents": info[
                "documents"
            ],
            "persistent": True,
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(error)}"
        )


# =========================================================
# LIST SESSION DOCUMENTS
# =========================================================

@router.get(
    "/documents/{session_id}"
)
async def list_documents(
    session_id: str
):
    """
    Return information about documents stored
    for the current session.
    """

    info = get_vector_store_info(
        session_id
    )

    return {
        "status": "success",
        **info,
    }


# =========================================================
# CLEAR ALL SESSION DOCUMENTS
# =========================================================

@router.delete(
    "/documents/{session_id}"
)
async def clear_documents(
    session_id: str
):
    """
    Delete all uploaded documents and persistent
    FAISS data belonging to a session.
    """

    vector_store_removed = (
        clear_vector_store(
            session_id
        )
    )

    session_upload_dir = (
        UPLOAD_ROOT / session_id
    )

    files_removed = False

    if session_upload_dir.exists():
        shutil.rmtree(
            session_upload_dir
        )

        files_removed = True

    return {
        "status": "success",
        "session_id": session_id,
        "vector_store_removed":
            vector_store_removed,
        "uploaded_files_removed":
            files_removed,
        "message":
            "All documents for this session were cleared.",
    }