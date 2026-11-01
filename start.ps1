# Start both Backend and Frontend in separate windows
$env:USE_SQLITE = "true"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Starting CSE Attendance Management System" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

Write-Host "[1/2] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:USE_SQLITE='true'; python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

Write-Host "[2/2] Starting Vite Frontend on http://localhost:3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location frontend; npm run dev"

Write-Host "`nSystem is ONLINE:" -ForegroundColor Green
Write-Host "  - Frontend Web App: http://localhost:3000" -ForegroundColor White
Write-Host "  - Fullstack Backend & App: http://localhost:8000" -ForegroundColor White
Write-Host "  - Interactive Swagger Docs: http://localhost:8000/docs" -ForegroundColor White

