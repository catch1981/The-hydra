Viren Chat EXE / Binary
=======================
This packages `viren_chat_loop.py` into a single executable that includes Python.

Windows (EXE):
1) Open PowerShell or CMD
2) cd to this folder
3) Run: build_exe.bat
4) The EXE will be at: chat\dist\VirenChat.exe

Linux/macOS (one-file binary):
1) Ensure Python 3 and pip are installed
2) cd to this folder
3) Run: bash build_binary.sh
4) The binary will be at: chat/dist/viren-chat

Notes:
- The program talks to an Ollama server at OLLAMA_HOST (default http://127.0.0.1:11434). Make sure it's running.
- You can configure defaults via env vars: OLLAMA_HOST, HYDRA_GPT_MODEL, CHAIN_SYSTEM.