from app.rag.vectorstore import get_vector_store
from app.rag.retriever import retrieve_context
from app.llm.openai_client import generate_answer


def run_analysis_agent(
    query: str,
    session_id: str
) -> dict:
    """
    Analyze information retrieved only from documents
    uploaded in the current chat session.
    """

    # Get only this session's vector store
    vector_store = get_vector_store(session_id)

    # Retrieve relevant document chunks
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
                "I could not find documents for this chat session. "
                "Please upload a PDF before requesting document analysis."
            ),
            "context": [],
        }

    context = "\n\n".join(context_texts)

    prompt = f"""
You are an Analysis Agent in an enterprise multi-agent AI system.

Perform a detailed analysis using ONLY the document context provided below.

Your responsibilities:
- Identify important facts and patterns.
- Compare relevant information when requested.
- Identify trends, risks, or insights when supported by the context.
- Explain your reasoning clearly.
- Do not invent information that is not present in the context.
- Do not claim information is unavailable when the provided context contains
  enough information to perform a reasonable analysis.

Document Context:
{context}

User Question:
{query}

Detailed Analysis:
"""

    answer = generate_answer(prompt)

    return {
        "answer": answer,
        "context": context_texts,
    }