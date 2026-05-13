@echo off
echo ============================================================
echo STELLAR VOYAGE AI - Starting Backend Server
echo ============================================================
echo.

echo [1/2] Setting environment...
set PYTHONPATH=%CD%

echo [2/2] Starting FastAPI server...
echo.
echo Server will be available at: http://localhost:8080
echo API Documentation: http://localhost:8080/docs
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

uv run python backend\main.py
