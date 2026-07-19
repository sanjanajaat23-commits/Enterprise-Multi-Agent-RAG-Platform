from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.router_agent import route_query
from app.agents.rag_agent import run_rag_agent
from app.agents.general_agent import run_general_agent
from app.agents.analysis_agent import run_analysis_agent
from app.agents.memory import add_to_memory, get_memory, clear_memory
from app.rag.vectorstore import clear_vector_store


router = APIRouter()


class ChatRequest(BaseModel):
    session_id: str
    query: str


@router.post("/chat")
async def chat(request: ChatRequest):
    session_id = request.session_id
    query = request.query

    # STEP 1: Get previous conversation memory
    memory = get_memory(session_id)

    # STEP 2: Store current user message
    add_to_memory(
        session_id,
        "user",
        query
    )

    # STEP 3: Build query with conversation context
    if memory:
        contextual_query = f"""
Previous Conversation:
{memory}

Current User Question:
{query}
"""
    else:
        contextual_query = query

    # STEP 4: Router Agent decides which agent to use
    route = route_query(query)

    # STEP 5: Execute selected agent
    if route == "RAG":
        result = run_rag_agent(
            contextual_query,
            session_id=session_id
        )

    elif route == "ANALYSIS":
        result = run_analysis_agent(
            contextual_query,
            session_id=session_id
        )

    elif route == "GENERAL":
        result = run_general_agent(
            contextual_query
        )

    else:
        route = "GENERAL"

        result = run_general_agent(
            contextual_query
        )

    # STEP 6: Get final answer
    answer = result["answer"]

    # STEP 7: Store assistant response
    add_to_memory(
        session_id,
        "assistant",
        answer
    )

    # STEP 8: Return response
    return {
        "session_id": session_id,
        "query": query,
        "route": route,
        "answer": answer,
        "context": result.get("context", []),
    }


@router.delete("/chat/memory/{session_id}")
async def delete_chat_memory(session_id: str):
    # Clear SQLite conversation history
    clear_memory(session_id)

    return {
        "status": "success",
        "session_id": session_id,
        "message": "Conversation memory cleared",
    }


@router.delete("/chat/session/{session_id}")
async def delete_chat_session(session_id: str):
    # Clear SQLite conversation history
    clear_memory(session_id)

    # Clear session-specific FAISS vector store
    vector_store_cleared = clear_vector_store(
        session_id
    )

    return {
        "status": "success",
        "session_id": session_id,
        "memory_cleared": True,
        "vector_store_cleared": vector_store_cleared,
        "message": "Session memory and document vector store cleared",
    }