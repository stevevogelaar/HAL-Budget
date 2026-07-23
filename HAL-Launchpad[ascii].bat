@echo off
setlocal

:: HAL-Launchpad[ASCII] — retro BBS-style menu launcher
:: Wraps the PowerShell script that does all the drawing and menu logic safely.

set "ROOT=%~dp0"
if exist "%ROOT%HAL-Launchpad[ascii].ps1" (
    set "PS1=%ROOT%HAL-Launchpad[ascii].ps1"
) else (
    set "PS1=C:\Users\Steve Vogelaar\Documents\_IT Oversight\Hackathon\HAL-Launchpad[ascii].ps1"
)

powershell -NoExit -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
exit /b %errorlevel%
