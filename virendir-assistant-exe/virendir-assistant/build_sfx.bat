@echo off
setlocal enabledelayedexpansion

REM Paths
set ROOT=%~dp0
set OUT=%ROOT%dist
set PAYLOAD=%OUT%\payload
set SFXCFG=%OUT%\config.txt
set SFXEXE=%OUT%\Virendir_SFX.exe

if not exist "%ProgramFiles%\7-Zip\7z.exe" (
  echo ERROR: 7-Zip not found. Install from https://www.7-zip.org/
  exit /b 1
)

if not exist "%OUT%" mkdir "%OUT%"
rmdir /s /q "%PAYLOAD%" 2>nul
mkdir "%PAYLOAD%"

del /q "%OUT%\payload.7z" 2>nul

a:
REM Prepare payload: minimal runtime to start via Run.bat
for %%F in (Run.bat start_virendir.bat load_env.bat requirements_exe.txt) do (
  if exist "%ROOT%%%F" copy /y "%ROOT%%%F" "%PAYLOAD%\"
)

xcopy /e /i /y "%ROOT%assets" "%PAYLOAD%\assets" >nul
xcopy /e /i /y "%ROOT%relay_py" "%PAYLOAD%\relay_py" >nul
xcopy /e /i /y "%ROOT%server" "%PAYLOAD%\server" >nul
if exist "%ROOT%\.env" copy /y "%ROOT%\.env" "%PAYLOAD%\"

REM Create 7z archive
"%ProgramFiles%\7-Zip\7z.exe" a -t7z -mx=9 "%OUT%\payload.7z" "%PAYLOAD%\*" | more

REM Create SFX config that auto-runs Run.bat after extraction
>"%SFXCFG%" echo ;!@Install@!UTF-8!
>>"%SFXCFG%" echo Title="Virendir Assistant"
>>"%SFXCFG%" echo ExtractTitle="Extracting Virendir Assistant"
>>"%SFXCFG%" echo InstallPath="C:\\virendir-assistant"
>>"%SFXCFG%" echo OverwriteMode="1"
>>"%SFXCFG%" echo RunProgram="Run.bat"
>>"%SFXCFG%" echo ;!@InstallEnd@!

REM Assemble SFX: 7z.sfx + config + payload.7z
if exist "%ProgramFiles%\7-Zip\7z.sfx" (
  copy /b "%ProgramFiles%\7-Zip\7z.sfx" + "%SFXCFG%" + "%OUT%\payload.7z" "%SFXEXE%" >nul
  echo SFX created: "%SFXEXE%"
) else (
  echo ERROR: 7z.sfx not found. Ensure it is installed with 7-Zip.
  exit /b 1
)

endlocal