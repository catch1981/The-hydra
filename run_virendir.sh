#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/virendir-assistant" && pwd)"
cd "$ROOT"

# Load .env if present
if [[ -f .env ]]; then
  # shellcheck disable=SC2046
  export $(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env | xargs)
else
  echo "[warn] .env not found in $ROOT (some features may be disabled)"
fi

# Create and use virtualenv locally
PY=${PYTHON:-python3}
VENV_DIR="$ROOT/.venv"
if [[ ! -d "$VENV_DIR" ]]; then
  echo "[setup] Creating venv at $VENV_DIR"
  $PY -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
PY="$(command -v python)"
PIP="$(command -v pip)"

# Ensure dependencies
$PIP install --upgrade pip >/dev/null
$PIP install -r requirements_exe.txt >/dev/null

# Ensure Python can import local modules
export PYTHONPATH="$ROOT:$ROOT/server:${PYTHONPATH:-}"

# Stop any existing instances
pkill -f "uvicorn.*server\.app:app" >/dev/null 2>&1 || true
pkill -f "relay_py/relay.py" >/dev/null 2>&1 || true
command -v fuser >/dev/null 2>&1 && { fuser -k 8765/tcp >/dev/null 2>&1 || true; fuser -k 8787/tcp >/dev/null 2>&1 || true; }

# Start relay and api server
set -m
$PY relay_py/relay.py >/tmp/virendir-relay.log 2>&1 &
RELAY_PID=$!

$PY -m uvicorn server.app:app --host 0.0.0.0 --port 8765 >/tmp/virendir-api.log 2>&1 &
API_PID=$!

# Readiness check
for i in {1..30}; do
  if curl -fsS http://127.0.0.1:8765/healthz >/dev/null; then
    break
  fi
  sleep 0.5
  if [[ $i -eq 30 ]]; then
    echo "[error] API did not become ready. See /tmp/virendir-api.log"
  fi
done

echo "Virendir running. Health: http://127.0.0.1:8765/healthz"
trap 'kill $RELAY_PID $API_PID 2>/dev/null || true' INT TERM EXIT
wait