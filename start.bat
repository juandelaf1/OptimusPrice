@echo off
echo Starting Optimus Price...
echo.

start "Frontend" cmd /c "cd /d frontend && npx next dev --port 3000"
timeout /t 2 /nobreak > nul
start "Backend" cmd /c "cd /d backend && uvicorn app.main:app --reload --port 8000"

echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo.
echo Para detener: taskkill /fi "WINDOWTITLE eq Frontend" /fi "WINDOWTITLE eq Backend"