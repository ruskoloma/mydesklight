@echo off
REM Uninstall mydesklight Windows Task Scheduler service

echo ========================================
echo mydesklight - Windows Service Uninstaller
echo ========================================
echo.

REM Check if task exists
schtasks /query /tn "mydesklight" >nul 2>&1
if %errorlevel% neq 0 (
    echo Service not installed (task not found)
    pause
    exit /b 0
)

echo Stopping any running instances...
taskkill /f /im python.exe /fi "WINDOWTITLE eq mydesklight*" >nul 2>&1

echo Deleting scheduled task...
schtasks /delete /tn "mydesklight" /f

if %errorlevel% equ 0 (
    echo.
    echo Service uninstalled successfully
) else (
    echo.
    echo ERROR: Failed to uninstall service
    echo Please run this script as Administrator
)

echo.
echo To remove configuration:
echo   rmdir /s %%APPDATA%%\mydesklight
echo.
pause
