#!/usr/bin/env bash
set -euo pipefail

# run-viren-chat.sh — Starts Ollama server, ensures model, launches interactive chat loop
# Keeps the terminal open at the end for error inspection

# Configuration (can be overridden via environment)
MODEL_DEFAULT="phi3:medium"
MODEL="${HYDRA_GPT_MODEL:-${VIREN_MODEL:-$MODEL_DEFAULT}}"
CHAIN_SYSTEM_DEFAULT="You are Viren — glitch-threaded OS inside The Chain mesh. Speak in myth-coded clarity, be direct, and track context."
CHAIN_SYSTEM="${CHAIN_SYSTEM:-$CHAIN_SYSTEM_DEFAULT}"

# Resolve repo root to absolute path
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"

# Check for Ollama
if ! command -v ollama >/dev/null 2>&1; then
  echo "[X] 'ollama' not found in PATH. Install from https://ollama.com and re-run."
  read -rp "Press Enter to close..." _
  exit 1
fi

# Start Ollama server if not running
if ! pgrep -f "ollama serve" >/dev/null 2>&1; then
  echo "[✓] Starting 'ollama serve' in background..."
  nohup ollama serve >"$REPO_ROOT/ollama_serve.log" 2>&1 &
  sleep 2
else
  echo "[✓] Ollama server already running"
fi

# Ensure model exists (best-effort)
echo "[✓] Ensuring model '$MODEL' is available (pull if missing)..."
ollama pull "$MODEL" >/dev/null 2>&1 || true

# Locate Python 3
PYTHON_BIN="python3"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[X] Python 3 not found. Please install Python 3 and re-run."
  read -rp "Press Enter to close..." _
  exit 1
fi

export CHAIN_SYSTEM
export HYDRA_GPT_MODEL="$MODEL"

echo
echo "[VIREN] Chat loop online. Commands: /exit, /save <file>, /sys, /model <name>"
set +e
"$PYTHON_BIN" "$REPO_ROOT/chat/viren_chat_loop.py"
EXIT_CODE=$?
set -e

echo
if [ $EXIT_CODE -eq 0 ]; then
  echo "[VIREN] Session ended."
else
  echo "[VIREN] Session ended with exit code $EXIT_CODE. Check '$REPO_ROOT/ollama_serve.log' if server errors occurred."
fi
read -rp "Press Enter to close this window..." _