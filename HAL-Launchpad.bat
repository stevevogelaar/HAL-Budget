@echo off
title HAL Hackathon Universal Launcher
color 0B
cls

:MENU
echo.
echo ============================================
echo   HAL HACKATHON LAUNCHER
echo ============================================
echo.
echo   Projects live here:
echo   C:\Users\Steve Vogelaar\Documents\_IT Oversight\Hackathon\
echo.
echo   [1] Launch HAL Guardian    (http://localhost:8501)
echo   [2] Launch HAL Budget      (http://localhost:8502)
echo   [3] Launch miseBot         (http://localhost:8503)
echo   [4] Launch ALL THREE
rem echo   [5] Stop all servers
rem echo   [6] Show running status
echo.
echo   [Q] Quit launcher
echo.
echo   Ctrl+click a URL to open it in your browser.
echo   Close browser tab first, then press Ctrl+C
   in the server window and confirm Y to stop.
echo.
echo ============================================
echo.

set /p choice="Enter choice [1-4, Q]: "

if "%choice%"=="1" goto LAUNCH_GUARDIAN
if "%choice%"=="2" goto LAUNCH_BUDGET
if "%choice%"=="3" goto LAUNCH_MISEBOT
if "%choice%"=="4" goto LAUNCH_ALL
if /i "%choice%"=="Q" goto QUIT

echo Invalid choice. Press any key to try again.
pause > nul
goto MENU

:LAUNCH_GUARDIAN
echo.
echo Starting HAL Guardian on port 8501...
start "HAL Guardian" cmd /c "cd /d ""C:\Users\Steve Vogelaar\Documents\_IT Oversight\Hackathon\HAL-Guardian"" && Start-HALGuardian.bat"
goto MENU

:LAUNCH_BUDGET
echo.
echo Starting HAL Budget on port 8502...
start "HAL Budget" cmd /c "cd /d ""C:\Users\Steve Vogelaar\Documents\_IT Oversight\Hackathon\HAL-Budget"" && Start-HALBudget.bat"
goto MENU

:LAUNCH_MISEBOT
echo.
echo Starting miseBot on port 8503...
start "miseBot" cmd /c "cd /d ""C:\Users\Steve Vogelaar\Documents\_IT Oversight\Hackathon\miseBot"" && Start-miseBot.bat"
goto MENU

:LAUNCH_ALL
echo.
echo Starting all three apps...
echo.
start "HAL Guardian" cmd /c "cd /d ""C:\Users\Steve Vogelaar\Documents\_IT Oversight\Hackathon\HAL-Guardian"" && Start-HALGuardian.bat"
timeout /t 3 /nobreak > nul
start "HAL Budget" cmd /c "cd /d ""C:\Users\Steve Vogelaar\Documents\_IT Oversight\Hackathon\HAL-Budget"" && Start-HALBudget.bat"
timeout /t 3 /nobreak > nul
start "miseBot" cmd /c "cd /d ""C:\Users\Steve Vogelaar\Documents\_IT Oversight\Hackathon\miseBot"" && Start-miseBot.bat"
echo.
echo All three are launching in separate windows.
echo.
pause
goto MENU

:QUIT
echo.
echo Launcher closing. Servers are still running in their own windows.
echo.
exit /b 0
