@echo off
setlocal
cd /d "%~dp0"
title EmotionVoice

where python >nul 2>nul
if errorlevel 1 (
  echo Python not found. Install from https://www.python.org/downloads/
  echo Tick "Add python.exe to PATH" during install.
  pause
  exit /b 1
)

if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo Created .env - put your FISH_API_KEY in it, save, then run start.bat again.
  notepad ".env"
  pause
  exit /b 0
)

if not exist ".venv\Scripts\python.exe" (
  echo First run: making virtual env...
  python -m venv .venv || (echo venv failed & pause & exit /b 1)
)

echo Installing / checking packages...
".venv\Scripts\python.exe" -m pip install -q --disable-pip-version-check -r requirements.txt || (echo pip failed & pause & exit /b 1)

set PORT=5000
for /f "usebackq tokens=1,* delims==" %%a in (".env") do if /i "%%a"=="PORT" set PORT=%%b

start "" "http://127.0.0.1:%PORT%"
".venv\Scripts\python.exe" app.py
pause
