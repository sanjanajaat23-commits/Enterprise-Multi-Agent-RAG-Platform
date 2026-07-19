from app.rag.vectorstore import get_vector_store
from app.rag.retriever import retrieve_context
from app.llm.openai_client import generate_answer


def run_rag_agent(
    query: str,
    session_id: str
) -> dict:
    """
    Retrieve relevant document chunks from the
    current session's vector store and generate
    an answer using the local Ollama LLM.
    """

    # Get only this session's vector store
    vector_store = get_vector_store(session_id)

    # Retrieve relevant chunks
    docs = retrieve_context(
        query,
        vector_store
    )

    context_texts = []

    for doc in docs:
        text = (
            doc.page_content
            if hasattr(doc, "page_content")
            else str(doc)
        )

        context_texts.append(text)

    # No documents available for this session
    if not context_texts:
        return {
            "answer": (
                "I could not find relevant information in documents "
                "uploaded for this chat session. Please upload a PDF first."
            ),
            "context": [],
        }

    context = "\n\n".join(context_texts)

    prompt = f"""
You are a RAG agent in an enterprise multi-agent AI system.

Answer the user's current question using ONLY the provided document context.

Use information from the document when it is available.

Do not say that information is unavailable if the provided context contains
information that can reasonably answer the question.

If the document context truly does not contain enough information,
say that you do not have enough information in the uploaded documents.

Document Context:
{context}

User Question:
{query}

Answer:
"""

    answer = generate_answer(prompt)

    return {
        "answer": answer,
        "context": context_texts,
    }