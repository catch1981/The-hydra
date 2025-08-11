
@echo off
set ROOT=C:\virendir-assistant
cd /d %ROOT%

:: Load env
call "%ROOT%\load_env.bat" || exit /b 1

:: Activate venv (create if missing)
if not exist "%ROOT%\.venv" (
  python -m venv "%ROOT%\.venv"
)
call "%ROOT%\.venv\Scripts\activate"

:: Install deps
pip install --upgrade pip >nul
pip install fastapi uvicorn pydantic requests websockets psutil firebase-admin cryptography >nul

:: Verify critical envs (fail fast if missing)
if "%VIREN_SUDO_TOKEN%"=="" echo ERROR: VIREN_SUDO_TOKEN missing & exit /b 1
if "%RELAY_SHARED_SECRET%"=="" echo ERROR: RELAY_SHARED_SECRET missing & exit /b 1
if "%MESH_E2E_KEY%"=="" echo ERROR: MESH_E2E_KEY missing & exit /b 1

:: Optional APIs: if provided, features work; if not, daemon will 500 on those endpoints (no silent fallback)
:: Start Python relay (local WS broker)
start "virendir-relay" /min cmd /c ""%ROOT%\.venv\Scripts\python.exe" "%ROOT%\relay_py\relay.py""

:: Launch daemon
uvicorn server.app:app --host 0.0.0.0 --port 8765
