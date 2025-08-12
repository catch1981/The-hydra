#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

python3 -m pip install --user --break-system-packages --upgrade pip pyinstaller

python3 -m PyInstaller --noconfirm --onefile --console --name "viren-chat" viren_chat_loop.py

echo "Built: $SCRIPT_DIR/dist/viren-chat"