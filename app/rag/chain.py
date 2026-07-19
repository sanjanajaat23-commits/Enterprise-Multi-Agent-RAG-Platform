from langchain_core.output_parsers import StrOutputParser

from app.llm.openai_client import get_llm
from app.rag.prompt import RAG_PROMPT
from app.rag.retriever import get_retriever


def ask_question(question: str):
    retriever = get_retriever()

    docs = retriever.invoke(question)

    context = "\n\n".join(doc.page_content for doc in docs)

    chain = RAG_PROMPT | get_llm() | StrOutputParser()

    return chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )