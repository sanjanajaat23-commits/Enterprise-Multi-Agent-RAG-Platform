import requests


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2"


def generate_answer(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120,
    )

    response.raise_for_status()

    result = response.json()

    return result.get("response", "").strip()