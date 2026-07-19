from app.llm.openai_client import generate_answer


def run_general_agent(query: str) -> dict:
    """
    Handle general questions and conversation history
    using the local Ollama LLM.
    """

    prompt = f"""
You are a helpful AI assistant with conversation memory.

The input below may contain previous conversation history
followed by the user's current question.

IMPORTANT:
- Use information from the previous conversation to answer follow-up questions.
- If the user previously provided a fact or preference, remember and use it.
- Focus on answering the CURRENT USER QUESTION.
- Do not claim this is a new interaction if previous conversation is provided.

Conversation and Current Question:
{query}

Answer:
"""

    answer = generate_answer(prompt)

    return {
        "answer": answer,
        "context": [],
    }