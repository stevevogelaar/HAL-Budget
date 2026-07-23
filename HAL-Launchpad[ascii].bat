@echo off
setlocal EnableDelayedExpansion

:: Get ANSI escape char
for /F "tokens=*" %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"

:: 8-bit colour codes
set "C_TITLE=!ESC![38;5;196;48;5;17;1m"
set "C_LOGO=!ESC![38;5;226;48;5;17;1m"
set "C_BORDER=!ESC![38;5;51m"
set "C_MENU=!ESC![38;5;82m"
set "C_URL=!ESC![38;5;45m"
set "C_WARN=!ESC![38;5;202m"
set "C_RESET=!ESC![0m"

set "ROOT=C:\Users\Steve Vogelaar\Documents\_IT Oversight\Hackathon"
set "LOGPAD=!C_TITLE!  HAL LAUNCHPAD  !C_RESET!"

:MENU
cls
echo !C_BORDER!
echo  +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+
echo !C_TITLE!  _   _    _      _         _                      _       _   _  !C_RESET!
echo !C_TITLE! | | | |  | |    | |       | |     __ _    ___    | |     (_) | | !C_RESET!
echo !C_TITLE! | |_| |  | |    | |       | |    / _` |  / _ \   | |     | | | | !C_RESET!
echo !C_TITLE! |  _  |  | |    | |       | |   | (_| | |  __/   | |___  | | | | !C_RESET!
echo !C_TITLE! | | | |  | |    | |       | |    \__, |  \___|   |_____| |_| |_| !C_RESET!
echo !C_TITLE! |_| |_|  |____| |_____|  |_____| |___/                                  !C_RESET!
echo !C_BORDER!
echo  +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+
echo.
echo !C_LOGO!       O====O                                          !C_RESET!
echo !C_LOGO!       ||  ||     HAL HACKATHON CONTROL CENTER          !C_RESET!
echo !C_LOGO!      /| [] |\                                         !C_RESET!
echo !C_LOGO!     / | <> | \    Local Streamlit App Launcher         !C_RESET!
echo !C_LOGO!    /  |____|  \                                       !C_RESET!
echo !C_LOGO!   '==/      \=='                                      !C_RESET!
echo !C_LOGO!      | 2026 |                                          !C_RESET!
echo !C_LOGO!      |______|                                          !C_RESET!
echo.
echo !C_BORDER!  -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=  !C_RESET!
echo.
echo !C_MENU!   [1] !C_RESET! Launch HAL Guardian    !C_URL!http://localhost:8501!C_RESET!
echo !C_MENU!   [2] !C_RESET! Launch HAL Budget      !C_URL!http://localhost:8502!C_RESET!
echo !C_MENU!   [3] !C_RESET! Launch miseBot         !C_URL!http://localhost:8503!C_RESET!
echo !C_MENU!   [4] !C_RESET! Launch ALL THREE

       [V] View IP addresses / URLs
       [Q] Quit launcher

!C_BORDER!  -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=  !C_RESET!
echo.
echo  Close browser tab first, then press Ctrl+C in the app window and Y to stop.
echo.
set /p choice="!C_MENU!Enter choice [1-4, V, Q]:!C_RESET! "

if "%choice%"=="1" goto LAUNCH_GUARDIAN
if "%choice%"=="2" goto LAUNCH_BUDGET
if "%choice%"=="3" goto LAUNCH_MISEBOT
if "%choice%"=="4" goto LAUNCH_ALL
if /i "%choice%"=="V" goto VIEW_IPS
if /i "%choice%"=="Q" goto QUIT

echo.
echo !C_WARN!Invalid choice. Press any key to try again.!C_RESET!
pause > nul
goto MENU

:LAUNCH_GUARDIAN
cls
echo.
echo !C_TITLE!>> Launching HAL Guardian on port 8501...!C_RESET!
start "HAL Guardian" cmd /c "cd /d ""%ROOT%\HAL-Guardian"" && Start-HALGuardian.bat"
timeout /t 4 /nobreak > nul
goto VIEW_IPS

:LAUNCH_BUDGET
cls
echo.
echo !C_TITLE!>> Launching HAL Budget on port 8502...!C_RESET!
start "HAL Budget" cmd /c "cd /d ""%ROOT%\HAL-Budget"" && Start-HALBudget.bat"
timeout /t 4 /nobreak > nul
goto VIEW_IPS

:LAUNCH_MISEBOT
cls
echo.
echo !C_TITLE!>> Launching miseBot on port 8503...!C_RESET!
start "miseBot" cmd /c "cd /d ""%ROOT%\miseBot"" && Start-miseBot.bat"
timeout /t 4 /nobreak > nul
goto VIEW_IPS

:LAUNCH_ALL
cls
echo.
echo !C_TITLE!>> Launching all three HAL apps...!C_RESET!
start "HAL Guardian" cmd /c "cd /d ""%ROOT%\HAL-Guardian"" && Start-HALGuardian.bat"
timeout /t 3 /nobreak > nul
start "HAL Budget" cmd /c "cd /d ""%ROOT%\HAL-Budget"" && Start-HALBudget.bat"
timeout /t 3 /nobreak > nul
start "miseBot" cmd /c "cd /d ""%ROOT%\miseBot"" && Start-miseBot.bat"
timeout /t 4 /nobreak > nul
goto VIEW_IPS

:VIEW_IPS
cls
echo !C_BORDER!
echo  +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+
echo !C_TITLE!                    LAUNCHPAD IP / URL VIEWPORT                     !C_RESET!
echo !C_BORDER!
echo  +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+
echo.

:: Detect local network IP
for /f "tokens=*" %%a in ('powershell -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 -PrefixOrigin Dhcp | Select-Object -First 1).IPAddress"') do set "LOCAL_IP=%%a"
if not defined LOCAL_IP set "LOCAL_IP=192.168.x.x"

:: Try external IP
echo !C_WARN!>> Detecting external IP...!C_RESET!
for /f "tokens=*" %%a in ('powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri 'https://api.ipify.org' -UseBasicParsing -TimeoutSec 5).Content.Trim() } catch { 'unavailable' }"') do set "EXTERNAL_IP=%%a"
if not defined EXTERNAL_IP set "EXTERNAL_IP=unavailable"

echo.
echo !C_MENU!  Local Host:     !C_URL!http://localhost!C_RESET!
echo !C_MENU!  Local Network:  !C_URL!http://%LOCAL_IP%!C_RESET!
echo !C_MENU!  External/WAN:     !C_URL!http://%EXTERNAL_IP%!C_RESET!
echo.
echo  -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
echo.
echo !C_TITLE!  APP                LOCALHOST            NETWORK              EXTERNAL!C_RESET!
echo.
echo !C_MENU!  [1] HAL Guardian   !C_URL!http://localhost:8501!C_RESET!  !C_URL!http://%LOCAL_IP%:8501!C_RESET!  !C_URL!http://%EXTERNAL_IP%:8501!C_RESET!
echo !C_MENU!  [2] HAL Budget     !C_URL!http://localhost:8502!C_RESET!  !C_URL!http://%LOCAL_IP%:8502!C_RESET!  !C_URL!http://%EXTERNAL_IP%:8502!C_RESET!
echo !C_MENU!  [3] miseBot        !C_URL!http://localhost:8503!C_RESET!  !C_URL!http://%LOCAL_IP%:8503!C_RESET!  !C_URL!http://%EXTERNAL_IP%:8503!C_RESET!
echo.
echo !C_WARN!  Ctrl+click any URL to open it in your browser.!C_RESET!
echo !C_WARN!  For phone demos, connect to the same WiFi and use the NETWORK URL.!C_RESET!
echo.
echo  -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
echo.
pause
goto MENU

:QUIT
cls
echo.
echo !C_LOGO!  Good luck at the hackathon, Steve.!C_RESET!
echo.
echo !C_WARN!  Servers are still running in their own windows.!C_RESET!
echo !C_WARN!  Close each app tab, then Ctrl+C + Y in each server window.!C_RESET!
echo.
timeout /t 2 /nobreak > nul
exit /b 0
