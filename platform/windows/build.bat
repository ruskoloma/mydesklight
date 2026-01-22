@echo off
REM Build script for Windows keyboard monitor

echo Building Windows Keyboard Monitor...

REM Check if Visual Studio is available
where cl.exe >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Visual Studio compiler not found
    echo Please run this from a Visual Studio Developer Command Prompt
    echo Or install MinGW and use: gcc -o KeyboardMonitor.exe KeyboardMonitor.c -lws2_32 -lwtsapi32
    exit /b 1
)

REM Compile with MSVC
cl.exe /O2 /W3 KeyboardMonitor.c ws2_32.lib wtsapi32.lib /Fe:KeyboardMonitor.exe

if %errorlevel% equ 0 (
    echo Build successful: KeyboardMonitor.exe
    echo Binary location: %CD%\KeyboardMonitor.exe
    del *.obj
) else (
    echo Build failed
    exit /b 1
)
