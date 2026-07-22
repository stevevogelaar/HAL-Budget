@echo off
title HAL Budget Launcher
color 0B

echo =========================================
echo   HAL Budget - Privacy-First Finance
echo =========================================
echo.
echo Checking environment...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH.
    echo Please install Python and add it to your PATH.
    pause
    exit /b 1
)

REM Navigate to HAL Budget directory
set "HAL_BUDGET_DIR=C:\Users\Steve Vogelaar\Documents\_IT Oversight\Hackathon\HAL-Budget"

if not exist "%HAL_BUDGET_DIR%" (
    echo ERROR: HAL Budget directory not found.
    echo Expected: %HAL_BUDGET_DIR%
    pause
    exit /b 1
)

cd /d "%HAL_BUDGET_DIR%"
echo OK: Found HAL Budget at %cd%

REM Check if database exists, if not seed it
if not exist "hal_budget.db" (
    echo.
    echo Database not found. Seeding with demo data...
    python seed_data.py
    if errorlevel 1 (
        echo ERROR: Failed to seed database.
        pause
        exit /b 1
    )
    echo OK: Database seeded.
) else (
    echo OK: Database found.
)

echo.
echo Starting HAL Budget on http://localhost:8502 ...
echo (Guardian is on :8501, Budget is on :8502)
echo Press Ctrl+C in this window to stop.
echo.

streamlit run app.py --server.port 8502 --server.address localhost

if errorlevel 1 (
    echo.
    echo ERROR: Streamlit failed to start.
    echo Make sure streamlit is installed: pip install streamlit pandas
    pause
)
