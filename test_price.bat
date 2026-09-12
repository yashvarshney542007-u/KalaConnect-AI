@echo off
cd /d %~dp0
venv\Scripts\python.exe ml\test_price_prediction.py
pause
