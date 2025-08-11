@echo off
if exist "C:\virendir-assistant\dist\Virendir.exe" (
  start "" "C:\virendir-assistant\dist\Virendir.exe" tray
) else (
  echo Virendir.exe not found. Build it first: C:\virendir-assistant\build_exe.bat
)
