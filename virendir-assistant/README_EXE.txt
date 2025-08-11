
Virendir EXE Build & Run
========================
This folder is EXE-ready. To build a single-file Virendir.exe that launches both relay and daemon:

1) Open PowerShell (Admin) and run:
   Expand-Archive -Path .\virendir_suite_full_keys_openai.zip -DestinationPath C:\ -Force
   cd C:\virendir-assistant
   .\build_exe.bat

2) Run in console mode (shows logs):
   C:\virendir-assistant\dist\Virendir.exe

3) Run in tray mode (background with tray icon):
   C:\virendir-assistant\dist\Virendir.exe tray

The EXE uses the embedded .env (already populated with your keys).
