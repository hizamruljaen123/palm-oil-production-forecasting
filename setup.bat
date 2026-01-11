@echo off
echo ========================================
echo NISA - Water Prediction System
echo Quick Start Setup
echo ========================================
echo.

echo [1/5] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo.

echo [2/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo [3/5] Checking MySQL connection...
echo Please make sure MySQL/MariaDB is running
echo.

echo [4/5] Setting up database...
echo Please run the following command manually in MySQL:
echo mysql -u root -p ^< database_setup.sql
echo.
pause

echo [5/5] Creating default users...
python create_users.py
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Dropbox integration is configured automatically
echo 2. Run: python app.py
echo 3. Open browser: http://localhost:5000
echo 4. Login with:
echo    - Admin: admin / admin123
echo    - User: user / user123
echo.
echo ========================================
pause
