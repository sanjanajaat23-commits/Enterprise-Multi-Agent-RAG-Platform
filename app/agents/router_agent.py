from app.llm.openai_client import generate_answer


def route_query(query: str) -> str:
    query_lower = query.lower()

    document_keywords = [
        "uploaded document",
        "uploaded pdf",
        "document",
        "pdf",
        "file",
        "report",
    ]

    analysis_keywords = [
        "compare",
        "analyze",
        "analyse",
        "trend",
        "evaluate",
    ]

    # Document analysis questions
    if any(word in query_lower for word in document_keywords):
        if any(word in query_lower for word in analysis_keywords):
            return "ANALYSIS"
        return "RAG"

    # General questions don't need document retrieval
    prompt = f"""
Classify this general user query.

Return ANALYSIS only if the question requires complex reasoning,
comparison, evaluation, or detailed analysis.

Otherwise return GENERAL.

Query:
{query}

Return exactly one word: GENERAL or ANALYSIS
"""

    result = generate_answer(prompt).strip().upper()

    if result == "ANALYSIS":
        return "ANALYSIS"

    return "GENERAL"