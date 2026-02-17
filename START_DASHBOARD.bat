@echo off
echo ========================================
echo   Trading Dashboard Startup Script
echo ========================================
echo.
echo Starting backend server...
start "Trading Dashboard Backend" cmd /k "python main.py"
timeout /t 5
echo.
echo Starting frontend...
cd frontend
start "Trading Dashboard Frontend" cmd /k "npm start"
echo.
echo ========================================
echo   Dashboard Starting!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Login with:
echo   Username: testuser
echo   Password: testpassword123
echo.
pause
