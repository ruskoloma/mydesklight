# mydesklight - Windows Installation Guide

## Requirements

- Windows 10 or later
- Python 3.7+
- Visual Studio Build Tools OR MinGW-w64

## Quick Install

### Option 1: Visual Studio Build Tools (Recommended)

1. **Install Visual Studio Build Tools**:
   - Download: https://visualstudio.microsoft.com/downloads/
   - Select "Build Tools for Visual Studio"
   - Install "Desktop development with C++"

2. **Install Python**:
   - Download: https://www.python.org/downloads/
   - **Important**: Check "Add Python to PATH" during installation

3. **Build the monitor**:
   ```cmd
   cd platform\windows
   
   REM Open "Developer Command Prompt for VS" from Start Menu
   build.bat
   
   cd ..\..
   ```

### Option 2: MinGW-w64

1. **Install MSYS2** (easiest way to get MinGW):
   - Download: https://www.msys2.org/
   - Install and run MSYS2 terminal
   - Update: `pacman -Syu`
   - Install MinGW: `pacman -S mingw-w64-x86_64-gcc`

2. **Install Python**:
   - Download: https://www.python.org/downloads/
   - Check "Add Python to PATH"

3. **Build manually**:
   ```bash
   cd platform/windows
   gcc -o KeyboardMonitor.exe KeyboardMonitor.c -lws2_32 -lwtsapi32 -O2
   cd ../..
   ```

## Configuration

1. **Find your Govee device IP**:
   - Open Govee Home app
   - Select your device
   - Settings → Device Info → IP Address

2. **Configure mydesklight**:
   ```cmd
   python mydesklight configure
   ```
   Enter your Govee IP when prompted.

## Usage

```cmd
REM Start monitoring
python mydesklight on

REM Stop monitoring and turn off lights
python mydesklight off

REM Check status
python mydesklight status
```

## Add to PATH (Optional)

To use `mydesklight` instead of `python mydesklight`:

1. Press `Win + X` → System
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables", select "Path" → Edit
5. Click "New" and add: `C:\path\to\monitor-backlight-service`
6. Click OK on all dialogs
7. Restart Command Prompt

Now you can use:
```cmd
mydesklight on
mydesklight off
```

## Auto-Start on Login (Optional)

1. Press `Win + R` and type: `shell:startup`
2. Create a shortcut to start the service:
   - Right-click → New → Shortcut
   - Location: `pythonw C:\path\to\monitor-backlight-service\mydesklight on`
   - Name: "mydesklight"

## Troubleshooting

### Build Errors

**"cl.exe is not recognized"**
- You need to use "Developer Command Prompt for VS"
- Or install MinGW and use gcc instead

**"Cannot open include file 'windows.h'"**
- Install "Desktop development with C++" in Visual Studio Build Tools

### Runtime Errors

**"Service won't start"**
- Check if binary exists: `dir platform\windows\KeyboardMonitor.exe`
- Rebuild: `cd platform\windows && build.bat`

**"Govee IP not configured"**
- Run: `python mydesklight configure`

**"Firewall blocking"**
- Allow Python and KeyboardMonitor.exe through Windows Firewall
- Control Panel → Windows Defender Firewall → Allow an app

**"Service keeps stopping"**
- Check Task Manager for errors
- View logs in: `%TEMP%\mydesklight.log`

## Uninstall

```cmd
REM Stop service
python mydesklight off

REM Remove configuration
rmdir /s %APPDATA%\mydesklight

REM Delete repository
cd ..
rmdir /s monitor-backlight-service
```

## How It Works

The Windows monitor uses:
- **Win32 API** for keyboard layout detection (`WM_INPUTLANGCHANGE`)
- **WTS API** for session lock/unlock detection
- **Winsock2** for UDP communication
- **Native C** for minimal resource usage

## Color Customization

Edit `platform/windows/KeyboardMonitor.c`:

```c
// Lines 17-24
#define ENGLISH_R 255
#define ENGLISH_G 180
#define ENGLISH_B 110

#define OTHER_R 120
#define OTHER_G 180
#define OTHER_B 255
```

Then rebuild:
```cmd
cd platform\windows
build.bat
```

## Support

For issues, check the main [README.md](../../README.md) or open an issue on GitHub.
