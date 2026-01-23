@echo off
REM Install mydesklight as Windows Task Scheduler service

echo ========================================
echo mydesklight - Windows Service Installer
echo ========================================
echo.

REM Get current directory
set PROJECT_DIR=%~dp0..\..
cd /d "%PROJECT_DIR%"
set PROJECT_DIR=%CD%

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python from https://python.org/downloads/
    pause
    exit /b 1
)

REM Check if configured
if not exist "%APPDATA%\mydesklight\config.json" (
    echo WARNING: mydesklight not configured yet
    echo Run: python mydesklight configure
    echo.
    set /p CONTINUE="Continue anyway? (y/n): "
    if /i not "%CONTINUE%"=="y" exit /b 1
)

echo.
echo Creating Task Scheduler task...
echo.

REM Create task using schtasks
schtasks /create /tn "mydesklight" /tr "pythonw.exe \"%PROJECT_DIR%\mydesklight\" on" /sc onlogon /rl highest /f

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to create task
    echo Please run this script as Administrator
    pause
    exit /b 1
)

echo.
echo ========================================
echo Service installed successfully!
echo.
echo The service will now:
echo   - Start automatically on login
echo   - Run in the background
echo   - Control your lights based on keyboard layout
echo.
echo Useful commands:
echo   - Check status:  python mydesklight status
echo   - Start task:    schtasks /run /tn "mydesklight"
echo   - Stop task:     taskkill /f /im python.exe /fi "WINDOWTITLE eq mydesklight*"
echo   - Disable task:  schtasks /change /tn "mydesklight" /disable
echo   - Enable task:   schtasks /change /tn "mydesklight" /enable
echo   - Uninstall:     .\platform\windows\uninstall_service.bat
echo.
pause
