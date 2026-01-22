# mydesklight - Cross-Platform Monitor Backlight Control

Automatically change your monitor backlight color based on keyboard layout. Works on **macOS**, **Windows**, and **Linux**.

## Features

- 🎨 **Automatic color switching** based on keyboard layout
  - English layout (ABC/US): Warm orange RGB(255, 180, 110)
  - Other layouts: Blue RGB(120, 180, 255)
- 🔄 **Keepalive signals** every 20 seconds to prevent device sleep
- 🔒 **Screen lock detection** - automatically turns off lights when locked
- 🚀 **Native performance** - minimal CPU and memory usage
- 📡 **UDP control** - direct communication with Govee devices (no API key needed)
- 💻 **Cross-platform** - works on macOS, Windows, and Linux

## Quick Start

### 1. Install

Choose your platform:

- **macOS**: [Installation Guide](#macos-installation)
- **Windows**: [Installation Guide](#windows-installation)
- **Linux**: [Installation Guide](#linux-installation)

### 2. Configure

Set your Govee device IP address:

```bash
mydesklight configure
```

### 3. Use

```bash
# Start monitoring (changes color based on keyboard layout)
mydesklight on

# Stop monitoring and turn off lights
mydesklight off

# Check status
mydesklight status
```

---

## macOS Installation

### Requirements

- macOS 10.15 or later
- Python 3.7+
- Xcode Command Line Tools (for Swift compiler)

### Installation Steps

1. **Install Xcode Command Line Tools** (if not already installed):
   ```bash
   xcode-select --install
   ```

2. **Clone or download this repository**:
   ```bash
   cd /path/to/monitor-backlight-service
   ```

3. **Build the macOS monitor**:
   ```bash
   cd platform/macos
   chmod +x build.sh
   ./build.sh
   cd ../..
   ```

4. **Make the CLI executable**:
   ```bash
   chmod +x mydesklight
   ```

5. **Add to PATH** (optional but recommended):
   ```bash
   # Add to ~/.zshrc or ~/.bash_profile
   echo 'export PATH="$PATH:/path/to/monitor-backlight-service"' >> ~/.zshrc
   source ~/.zshrc
   ```

### Usage

```bash
# Configure Govee IP
mydesklight configure

# Start service
mydesklight on

# Stop service
mydesklight off

# Check status
mydesklight status
```

### Finding Your Govee IP Address

**Option 1: Govee App**
1. Open Govee Home app
2. Select your device
3. Settings → Device Info → IP Address

**Option 2: Router**
Check your router's admin panel for connected devices

**Option 3: Network Scan**
```bash
brew install nmap
nmap -sn 192.168.1.0/24
```

### Troubleshooting

**Service won't start:**
- Check if binary exists: `ls -l platform/macos/KeyboardMonitor`
- Rebuild if needed: `cd platform/macos && ./build.sh`

**Colors not changing:**
- Check if service is running: `mydesklight status`
- Verify Govee IP: Check config at `~/.config/mydesklight/config.json`
- Test network: `ping <your-govee-ip>`

---

## Windows Installation

### Requirements

- Windows 10 or later
- Python 3.7+
- Visual Studio Build Tools OR MinGW-w64

### Installation Steps

#### Option A: Using Visual Studio (Recommended)

1. **Install Visual Studio Build Tools**:
   - Download from: https://visualstudio.microsoft.com/downloads/
   - Install "Desktop development with C++"

2. **Install Python**:
   - Download from: https://www.python.org/downloads/
   - Check "Add Python to PATH" during installation

3. **Build the Windows monitor**:
   ```cmd
   cd platform\windows
   
   REM Open Visual Studio Developer Command Prompt, then:
   build.bat
   
   cd ..\..
   ```

#### Option B: Using MinGW

1. **Install MinGW-w64**:
   - Download from: https://www.mingw-w64.org/
   - Or use MSYS2: https://www.msys2.org/

2. **Build manually**:
   ```cmd
   cd platform\windows
   gcc -o KeyboardMonitor.exe KeyboardMonitor.c -lws2_32 -lwtsapi32 -O2
   cd ..\..
   ```

3. **Install Python** (if not already installed)

### Usage

```cmd
REM Configure Govee IP
python mydesklight configure

REM Start service
python mydesklight on

REM Stop service
python mydesklight off

REM Check status
python mydesklight status
```

### Add to PATH (Optional)

1. Right-click "This PC" → Properties
2. Advanced system settings → Environment Variables
3. Edit "Path" → Add repository directory
4. Now you can use: `mydesklight on` instead of `python mydesklight on`

### Troubleshooting

**Build errors:**
- Make sure you're using Visual Studio Developer Command Prompt
- Or install MinGW and use the gcc command

**Service won't start:**
- Check if binary exists: `dir platform\windows\KeyboardMonitor.exe`
- Rebuild if needed: `cd platform\windows && build.bat`

**Firewall blocking UDP:**
- Allow Python and KeyboardMonitor.exe through Windows Firewall

---

## Linux Installation

### Requirements

- Linux (any distribution)
- Python 3.7+
- GCC compiler
- X11 development libraries (optional, for better performance)

### Installation Steps

1. **Install dependencies**:

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install build-essential python3 python3-pip
   
   # Optional: For X11 support (recommended)
   sudo apt-get install libx11-dev libxkbfile-dev
   ```

   **Fedora/RHEL:**
   ```bash
   sudo dnf install gcc python3 python3-pip
   
   # Optional: For X11 support (recommended)
   sudo dnf install libX11-devel libxkbfile-devel
   ```

   **Arch Linux:**
   ```bash
   sudo pacman -S base-devel python python-pip
   
   # Optional: For X11 support (recommended)
   sudo pacman -S libx11 libxkbfile
   ```

2. **Build the Linux monitor**:
   ```bash
   cd platform/linux
   chmod +x build.sh
   ./build.sh
   cd ../..
   ```

3. **Make the CLI executable**:
   ```bash
   chmod +x mydesklight
   ```

4. **Add to PATH** (optional):
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   echo 'export PATH="$PATH:/path/to/monitor-backlight-service"' >> ~/.bashrc
   source ~/.bashrc
   ```

### Usage

```bash
# Configure Govee IP
mydesklight configure

# Start service
mydesklight on

# Stop service
mydesklight off

# Check status
mydesklight status
```

### X11 vs Generic Mode

**X11 Mode (Recommended):**
- Real-time keyboard layout detection
- Low CPU usage
- Requires X11 libraries

**Generic Mode (Fallback):**
- Polls keyboard layout every 2 seconds
- Works without X11 (Wayland, etc.)
- Slightly higher CPU usage

The build script automatically detects and uses X11 if available.

### Troubleshooting

**Build fails:**
- Install build tools: `sudo apt-get install build-essential`
- For X11 support: `sudo apt-get install libx11-dev libxkbfile-dev`

**Service won't start:**
- Check if binary exists: `ls -l platform/linux/keyboard_monitor`
- Rebuild if needed: `cd platform/linux && ./build.sh`

**Permission denied:**
- Make sure binary is executable: `chmod +x platform/linux/keyboard_monitor`

---

## CLI Commands Reference

### `mydesklight configure`

Configure Govee device IP address. This must be run before using other commands.

```bash
mydesklight configure
# Enter Govee device IP address: 192.168.1.100
# ✓ Govee IP set to: 192.168.1.100
```

Configuration is stored in:
- **macOS/Linux**: `~/.config/mydesklight/config.json`
- **Windows**: `%APPDATA%\mydesklight\config.json`

### `mydesklight on`

Start the background monitoring service. The service will:
- Monitor keyboard layout changes
- Send color commands to Govee device
- Send keepalive signals every 20 seconds
- Turn off lights when screen locks
- Restore lights when screen unlocks

```bash
mydesklight on
# ✓ Monitor backlight service started
# Lights will change based on keyboard layout
```

### `mydesklight off`

Stop the monitoring service and turn off lights.

```bash
mydesklight off
# Turning off lights...
# Service stopped
# ✓ Monitor backlight service stopped
```

### `mydesklight status`

Check if the service is running and show configuration.

```bash
mydesklight status
# Service is running (PID: 12345)
# Govee IP: 192.168.1.100
```

---

## Color Customization

To change the colors, edit the platform-specific source files:

### macOS
Edit `platform/macos/KeyboardMonitor.swift`:
```swift
// Lines 14-15
private let englishColor = (r: 255, g: 180, b: 110)  // English layout
private let otherColor = (r: 120, g: 180, b: 255)    // Other layouts
```

Then rebuild:
```bash
cd platform/macos && ./build.sh
```

### Windows
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
cd platform\windows && build.bat
```

### Linux
Edit `platform/linux/keyboard_monitor.c`:
```c
// Lines 20-27
#define ENGLISH_R 255
#define ENGLISH_G 180
#define ENGLISH_B 110

#define OTHER_R 120
#define OTHER_G 180
#define OTHER_B 255
```

Then rebuild:
```bash
cd platform/linux && ./build.sh
```

---

## How It Works

### Architecture

```
┌─────────────────┐
│  mydesklight    │  ← Python CLI tool
│  (CLI)          │
└────────┬────────┘
         │
         ├─ Config Management (Python)
         ├─ Service Control (Python)
         └─ UDP Client (Python)
                │
                ▼
┌───────────────────────────────┐
│  Platform-Specific Monitor    │
├───────────────────────────────┤
│  macOS:    Swift              │
│  Windows:  C (Win32 API)      │
│  Linux:    C (X11/Generic)    │
└───────────┬───────────────────┘
            │
            ├─ Keyboard Layout Detection
            ├─ Screen Lock Detection
            └─ Keepalive Timer
                    │
                    ▼
            ┌───────────────┐
            │  Govee Device │  ← UDP Port 4003
            │  (Light Bar)  │
            └───────────────┘
```

### UDP Protocol

Commands are sent as JSON over UDP to port 4003:

**Color Command:**
```json
{
  "msg": {
    "cmd": "colorwc",
    "data": {
      "color": {"r": 255, "g": 180, "b": 110},
      "colorTemInKelvin": 0
    }
  }
}
```

**Turn Off Command:**
```json
{
  "msg": {
    "cmd": "turn",
    "data": {"value": 0}
  }
}
```

Each command is sent 3 times with 10ms delay for reliability (UDP can lose packets).

---

## FAQ

**Q: Does this work with all Govee devices?**
A: It works with Govee devices that support UDP control (most WiFi-enabled light bars and strips). Check your device documentation.

**Q: Do I need a Govee API key?**
A: No! This uses direct UDP control, no API key or cloud connection needed.

**Q: Can I use multiple Govee devices?**
A: Currently, only one device is supported. You can modify the code to send to multiple IPs.

**Q: Will this work on Wayland (Linux)?**
A: Yes, but it will use generic mode (polling) instead of X11 events. Performance is still good.

**Q: Can I customize which layouts trigger which colors?**
A: Yes, edit the source code and rebuild. See [Color Customization](#color-customization).

**Q: Does this drain battery on laptops?**
A: No, the service is very lightweight. CPU usage is negligible, and it automatically turns off when screen locks.

---

## Uninstallation

### macOS/Linux
```bash
# Stop service if running
mydesklight off

# Remove configuration
rm -rf ~/.config/mydesklight

# Delete repository
cd .. && rm -rf monitor-backlight-service
```

### Windows
```cmd
REM Stop service if running
python mydesklight off

REM Remove configuration
rmdir /s %APPDATA%\mydesklight

REM Delete repository
cd .. && rmdir /s monitor-backlight-service
```

---

## License

MIT License - Do whatever you want with it!

---

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section for your platform
2. Verify your Govee device IP is correct
3. Make sure your device is on the same network
4. Check that UDP port 4003 is not blocked by firewall

For bugs or feature requests, please open an issue on GitHub.
