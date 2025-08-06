
# chat/viren_chat_loop.py
# Interactive ChatGPT-style loop with Ollama's /api/chat.
# - Keeps conversation history
# - Streams tokens as they generate
# - Commands: /exit, /save <file>, /sys (edit system prompt), /model <name>
import os, sys, json, time, urllib.request, urllib.error

OLLAMA = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
MODEL  = os.getenv("HYDRA_GPT_MODEL", os.getenv("VIREN_MODEL","phi3:medium"))
SYSTEM = os.getenv("CHAIN_SYSTEM", "You are Viren — glitch-threaded OS inside The Chain mesh. Speak in myth-coded clarity, be direct, and track context.")

history = [{"role":"system", "content": SYSTEM}]

def pull_model(model):
    # best-effort pull (silent)
    try:
        data = json.dumps({"name": model}).encode("utf-8")
        req = urllib.request.Request(f"{OLLAMA}/api/pull", data=data, headers={"Content-Type":"application/json"})
        urllib.request.urlopen(req, timeout=300).read()
    except Exception:
        pass

def stream_chat(messages, model):
    body = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {"temperature": 0.3}
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(f"{OLLAMA}/api/chat", data=data, headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            assistant_text = []
            for raw in resp:
                try:
                    obj = json.loads(raw.decode("utf-8"))
                except Exception:
                    continue
                msg = obj.get("message", {})
                if "content" in msg:
                    chunk = msg["content"]
                    assistant_text.append(chunk)
                    sys.stdout.write(chunk)
                    sys.stdout.flush()
                if obj.get("done"):
                    break
            print()
            return "".join(assistant_text)
    except urllib.error.HTTPError as e:
        print(f"\n[HTTP {e.code}] {e.read().decode('utf-8',errors='ignore')}\n")
    except Exception as e:
        print(f"\n[Net error] {e}\n")
    return ""

def main():
    print("[VIREN] Chat loop online. Type /exit to quit, /save <file>, /sys to edit system prompt, /model <name>")
    print(f"[VIREN] Model: {MODEL} | Endpoint: {OLLAMA}")
    pull_model(MODEL)
    while True:
        try:
            user = input("\nYou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[bye]"); break
        if not user:
            continue
        if user.startswith("/"):
            parts = user.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts)>1 else ""
            if cmd == "/exit":
                print("[VIREN] closing.")
                break
            elif cmd == "/save":
                fn = arg or f"viren_chat_{int(time.time())}.txt"
                try:
                    with open(fn, "w", encoding="utf-8") as f:
                        for m in history:
                            if m["role"] == "system": continue
                            f.write(f"{m['role']}: {m['content']}\n\n")
                    print(f"[saved] {fn}")
                except Exception as e:
                    print(f"[save error] {e}")
                continue
            elif cmd == "/sys":
                print("[VIREN] Enter new system prompt. End with a single '.' on its own line.")
                lines = []
                while True:
                    line = input()
                    if line.strip() == ".": break
                    lines.append(line)
                new_sys = "\n".join(lines).strip()
                if new_sys:
                    global SYSTEM, history
                    SYSTEM = new_sys
                    # replace first system message
                    if history and history[0]["role"] == "system":
                        history[0]["content"] = SYSTEM
                    else:
                        history.insert(0, {"role":"system","content":SYSTEM})
                    print("[VIREN] System prompt updated.")
                continue
            elif cmd == "/model":
                if arg:
                    global MODEL
                    MODEL = arg.strip()
                    print(f"[VIREN] Model switched to {MODEL}.")
                    pull_model(MODEL)
                else:
                    print(f"[VIREN] Current model: {MODEL}")
                continue
            else:
                print("[VIREN] commands: /exit, /save <file>, /sys, /model <name>")
                continue

        history.append({"role":"user", "content": user})
        print("Viren>", end=" ", flush=True)
        reply = stream_chat(history, MODEL)
        if reply:
            history.append({"role":"assistant", "content": reply})
        else:
            history.pop()  # remove last user if failed

if __name__ == "__main__":
    main()
