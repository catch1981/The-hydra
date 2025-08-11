
import os, requests

OPENAI_URL = os.getenv("OPENAI_URL","https://api.openai.com/v1/chat/completions")
MODEL      = os.getenv("OPENAI_MODEL","gpt-4o-mini")
KEY        = os.getenv("OPENAI_API_KEY")

class OpenAIBlocked(RuntimeError): pass

def openai_chat(messages, temperature=0.4, max_tokens=800):
    if not KEY:
        raise OpenAIBlocked("OPENAI_API_KEY not set")
    r = requests.post(
        OPENAI_URL,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
        json={"model": MODEL, "messages": messages, "temperature": temperature, "max_tokens": max_tokens},
        timeout=30
    )
    r.raise_for_status()
    data = r.json()
    try:
        return data["choices"][0]["message"]["content"], float(data.get("usage",{}).get("total_tokens",0))
    except Exception:
        return str(data), 0.0
