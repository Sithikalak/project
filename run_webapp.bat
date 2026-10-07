@echo off
title GlucoScope AI - Diabetes Risk Intelligence Platform
echo Starting GlucoScope AI Server...
echo Open your browser at http://localhost:8000
start http://localhost:8000

set "PY_CMD=python"
where python >nul 2>&1
if errorlevel 1 (
    if exist "%LocalAppData%\Programs\Python\Python311\python.exe" (
        set "PY_CMD=%LocalAppData%\Programs\Python\Python311\python.exe"
    )
)

"%PY_CMD%" "%~dp0webapp\server.py" 8000
pause
