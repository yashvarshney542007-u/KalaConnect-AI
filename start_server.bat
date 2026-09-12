@echo off
title KalaConnect AI - Server & Web Studio
echo ========================================================
echo   Starting KalaConnect AI Server on http://127.0.0.1:8000
echo ========================================================

cd /d %~dp0

if not exist venv\Scripts\python.exe (
    echo [ERROR] venv not found at %cd%\venv
    pause
    exit /b 1
)

start " http://127.0.0.1:8000
echo Opening Web Testing Studio in browser...
echo.
venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
