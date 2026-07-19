from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Enterprise Multi-Agent RAG Platform",
        "backend": "FastAPI",
        "llm": "Ollama Llama 3.2",
        "vector_store": "FAISS",
        "vector_persistence": True,
        "session_isolation": True,
        "memory": "SQLite",
        "message": "All core backend services are running",
    }


@router.get("/status")
def system_status():
    return {
        "status": "operational",
        "components": {
            "api": "online",
            "rag": "enabled",
            "multi_agent": "enabled",
            "persistent_memory": "enabled",
            "persistent_vector_store": "enabled",
            "session_isolation": "enabled",
            "multi_document": "enabled",
        },
    }