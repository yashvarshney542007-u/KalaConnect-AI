@echo off
title KalaConnect AI - Server & Swagger Docs
echo ========================================================
echo   Starting KalaConnect AI Server on http://127.0.0.1:8002
echo ========================================================

cd /d %~dp0KalaConnect-AI

if not exist venv\Scripts\python.exe (
    echo [ERROR] venv not found at %cd%\venv
    pause
    exit /b 1
)

start " http://127.0.0.1:8002/docs
echo Opening Swagger Docs in browser: http://127.0.0.1:8002/docs
echo.
venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload
pause
