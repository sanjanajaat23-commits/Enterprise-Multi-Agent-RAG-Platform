import re


DOCUMENT_KEYWORDS = (
    "document",
    "pdf",
    "file",
    "report",
    "uploaded",
)

ANALYSIS_KEYWORDS = (
    "compare",
    "analyze",
    "analyse",
    "analysis",
    "trend",
    "evaluate",
    "summarize",
    "summarise",
)


def _contains_keyword(query: str, keyword: str) -> bool:
    return re.search(rf"\b{re.escape(keyword)}\b", query) is not None


def route_query(query: str) -> str:
    """Route deterministically so every chat does not require an extra LLM call."""
    query_lower = query.lower().strip()

    has_document_context = any(
        _contains_keyword(query_lower, keyword)
        for keyword in DOCUMENT_KEYWORDS
    )

    if has_document_context:
        if any(
            _contains_keyword(query_lower, keyword)
            for keyword in ANALYSIS_KEYWORDS
        ):
            return "ANALYSIS"
        return "RAG"

    return "GENERAL"
