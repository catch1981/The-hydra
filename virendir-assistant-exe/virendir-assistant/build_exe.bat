
@echo off
set ROOT=C:\virendir-assistant
cd /d %ROOT%
if not exist "%ROOT%\.venv" python -m venv "%ROOT%\.venv"
call "%ROOT%\.venv\Scripts\activate"
pip install --upgrade pip pyinstaller -r requirements_exe.txt
pyinstaller --noconfirm --onefile --icon assets\icon.ico ^
  --add-data ".env;." ^
  --add-data "server;server" ^
  --add-data "relay_py;relay_py" ^
  --add-data "assets;assets" ^
  launcher.py -n Virendir
echo.
echo 	Build complete: %ROOT%\dist\Virendir.exe

REM Optionally build SFX if 7-Zip is installed
if exist "%ProgramFiles%\7-Zip\7z.exe" (
  call build_sfx.bat
) else (
  echo 7-Zip not found; skipping SFX build. Install from https://www.7-zip.org/
)
