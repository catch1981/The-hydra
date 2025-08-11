
def build_task(msg: str, mode: str = "balanced"):
    m = msg.lower()
    return {
        "tool_intent": any(k in m for k in ["write file","run","shell","execute","listdir","delete","copy","move"]),
        "code_intent": any(k in m for k in ["code","function","class","bug","compile","build","test"]),
        "search_intent": any(k in m for k in ["http://","https://","research","sources","cite","article","doc"]),
        "privacy": "local" if any(k in m for k in ["secret","local only","private"]) else "auto",
        "mode": mode
    }
