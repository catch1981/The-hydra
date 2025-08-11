
@echo off
setlocal enabledelayedexpansion
if not exist C:\virendir-assistant\.env (
  echo ERROR: C:\virendir-assistant\.env missing. Run configure.ps1 first.
  exit /b 1
)
for /f "usebackq tokens=1,* delims==" %%A in ("C:\virendir-assistant\.env") do (
  if not "%%A"=="" set %%A=%%B
)
endlocal & (
  for /f "usebackq tokens=1,* delims==" %%A in ("C:\virendir-assistant\.env") do (
    set %%A=%%B
  )
)
