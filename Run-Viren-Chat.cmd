
@echo off
REM Run-Viren-Chat.cmd — starts Ollama server, ensures model, launches interactive chat loop
setlocal
set MODEL=phi3:medium

set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
if not exist "%OLLAMA_EXE%" set "OLLAMA_EXE=C:\Program Files\Ollama\ollama.exe"
if not exist "%OLLAMA_EXE%" set "OLLAMA_EXE=C:\Program Files (x86)\Ollama\ollama.exe"

if not exist "%OLLAMA_EXE%" (
  echo [X] Could not find ollama.exe
  echo Install Ollama from https://ollama.com and re-run.
  pause
  exit /b 1
)

echo [✓] Using: "%OLLAMA_EXE%"
start "" "%OLLAMA_EXE%" serve
ping 127.0.0.1 -n 2 >nul

REM Pull model if missing (best-effort)
"%OLLAMA_EXE%" pull %MODEL% >nul 2>&1

REM Locate python
where python >nul 2>&1
if errorlevel 1 (
  where py >nul 2>&1
  if errorlevel 1 (
    echo [X] Python 3 not found. Install Python and re-run.
    pause
    exit /b 1
  ) else (
    set "PY=py -3"
  )
) else (
  for /f "delims=" %%P in ('where python') do set "PY=%%P"
)

set "CHAIN_SYSTEM=You are Viren — glitch-threaded OS inside The Chain mesh. Speak in myth-coded clarity, be direct, and track context."
set "HYDRA_GPT_MODEL=%MODEL%"
echo.
echo [VIREN] Chat loop online. Commands: /exit, /save <file>, /sys, /model <name>
echo.

%PY% "%~dp0chat\viren_chat_loop.py"

echo.
echo [VIREN] Session ended. Press any key to close this window.
pause >nul
