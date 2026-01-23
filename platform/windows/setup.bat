@echo off
REM Quick setup for mydesklight on Windows (Python version - no compilation!)

echo ========================================
echo mydesklight - Windows Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo.
    echo Please install Python from https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/3] Python found
python --version
echo.

REM Install required packages
echo [2/3] Installing required packages...
pip install python-kasa
if %errorlevel% neq 0 (
    echo Warning: Failed to install python-kasa
    echo Kasa devices will not work, but Govee will still function
)
echo.

REM Check if monitor script exists
if not exist "platform\windows\keyboard_monitor.py" (
    echo ERROR: Monitor script not found!
    echo Make sure you're in the mydesklight directory
    pause
    exit /b 1
)

echo [3/3] Setup complete!
echo.
echo ========================================
echo Next steps:
echo ========================================
echo.
echo 1. Configure your devices:
echo    python mydesklight configure
echo.
echo 2. Start the service:
echo    python mydesklight on
echo.
echo 3. Check status:
echo    python mydesklight status
echo.
echo For help: python mydesklight help
echo.
pause
