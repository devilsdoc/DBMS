@echo off
echo ========================================================
echo   Starting CSE Attendance Management System
echo ========================================================

set USE_SQLITE=true

echo [1/2] Starting Backend API on http://localhost:8000 ...
start "DBMS Backend (FastAPI)" cmd /k "set USE_SQLITE=true && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

echo [2/2] Starting Frontend on http://localhost:3000 ...
start "DBMS Frontend (Vite)" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================================
echo System is ONLINE:
echo   - Frontend Web App: http://localhost:3000
echo   - Fullstack (Served via Backend): http://localhost:8000
echo   - Interactive API Docs: http://localhost:8000/docs
echo ========================================================

