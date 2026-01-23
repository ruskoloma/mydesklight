# mydesklight - Quick Start Guide

## Installation by Platform

### macOS

```bash
# 1. Build monitor
cd platform/macos
./build.sh
cd ../..

# 2. Configure
./mydesklight configure

# 3. Test
./mydesklight on
./mydesklight status
./mydesklight off
```

**Install as Service (Auto-start on login):**

```bash
# Create LaunchAgent plist
cat > ~/Library/LaunchAgents/com.mydesklight.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mydesklight</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/mydesklight</string>
        <string>on</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/monitor-backlight-service</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/mydesklight.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/mydesklight.err</string>
</dict>
</plist>
EOF

# Replace /path/to/ with actual path
sed -i '' "s|/path/to/|$(pwd)/|g" ~/Library/LaunchAgents/com.mydesklight.plist

# Load service
launchctl load ~/Library/LaunchAgents/com.mydesklight.plist

# Start now
launchctl start com.mydesklight
```

**Make `mydesklight` available globally:**

```bash
# Add to PATH in ~/.zshrc or ~/.bash_profile
echo "export PATH=\"\$PATH:$(pwd)\"" >> ~/.zshrc
source ~/.zshrc
```

---

### Windows

```powershell
# 1. Install dependencies
cd C:\path\to\mydesklight
.\platform\windows\setup.bat

# Or manually:
pip install python-kasa

# 2. Configure
python mydesklight configure

# 3. Test
python mydesklight on
python mydesklight status
python mydesklight off
```

**Install as Service (Auto-start on boot):**

Using Task Scheduler:
1. Open **Task Scheduler**
2. Create Task → **General** tab:
   - Name: `mydesklight`
   - Run whether user is logged on or not
   - Run with highest privileges
3. **Triggers** tab → New:
   - Begin: At log on
4. **Actions** tab → New:
   - Program: `pythonw.exe`
   - Arguments: `C:\path\to\mydesklight\mydesklight on`
   - Start in: `C:\path\to\mydesklight`
5. **Conditions** tab:
   - Uncheck: Start only if on AC power
6. Click OK

**Make `mydesklight` available globally:**

1. Win + X → System → Advanced → Environment Variables
2. Edit **Path** → Add: `C:\path\to\mydesklight`
3. Restart PowerShell

---

### Linux

```bash
# 1. Install dependencies
sudo apt-get install build-essential libx11-dev libxkbfile-dev  # Ubuntu/Debian
# OR
sudo dnf install gcc libX11-devel libxkbfile-devel  # Fedora/RHEL

# Install Python package
pip3 install python-kasa

# 2. Build monitor
cd platform/linux
./build.sh
cd ../..

# 3. Configure
./mydesklight configure

# 4. Test
./mydesklight on
./mydesklight status
./mydesklight off
```

**Install as systemd Service (Auto-start on boot):**

```bash
# Create service file
sudo tee /etc/systemd/system/mydesklight.service > /dev/null << EOF
[Unit]
Description=mydesklight Monitor Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/mydesklight on
ExecStop=$(pwd)/mydesklight off
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable mydesklight

# Start service now
sudo systemctl start mydesklight

# Check status
sudo systemctl status mydesklight

# View logs
journalctl -u mydesklight -f
```

**Make `mydesklight` available globally:**

```bash
# Add to PATH in ~/.bashrc or ~/.zshrc
echo "export PATH=\"\$PATH:$(pwd)\"" >> ~/.bashrc
source ~/.bashrc
```

---

## Basic Commands

```bash
# Configure devices (run first time)
mydesklight configure

# Start service
mydesklight on

# Stop service
mydesklight off

# Check status
mydesklight status

# Show help
mydesklight help
```

## Device Behavior

| Event | Govee | Kasa 1 | Kasa 2 |
|-------|-------|--------|--------|
| Service START | ON (color) | ON | ON |
| Screen UNLOCK | ON (color) | ON | ON |
| Screen LOCK | OFF | **Stays ON** | OFF |
| Service STOP | OFF | **Stays ON** | OFF |

## Colors

- **English (ABC/US)**: RGB(255, 180, 110) - Warm orange
- **Other layouts**: RGB(120, 180, 255) - Blue

## Configuration

Stored in:
- **macOS/Linux**: `~/.config/mydesklight/config.json`
- **Windows**: `%APPDATA%\mydesklight\config.json`

Example:
```json
{
  "govee_ip": "10.0.0.9",
  "kasa1_ip": "192.168.1.11",
  "kasa2_ip": "192.168.1.139"
}
```

## Troubleshooting

### Service won't start

```bash
# Check if already running
mydesklight status

# Stop and restart
mydesklight off
mydesklight on

# View logs (if installed as service)
# macOS:
tail -f /tmp/mydesklight.log

# Linux:
journalctl -u mydesklight -f

# Windows:
# Run directly to see output:
python platform\windows\keyboard_monitor.py
```

### Devices not responding

```bash
# Test connectivity
ping 10.0.0.9
ping 192.168.1.11

# Test Kasa directly
python -m kasa.cli --host 192.168.1.11 state

# Reconfigure
mydesklight configure
```

### Rebuild monitor

```bash
# macOS
cd platform/macos && ./build.sh && cd ../..

# Linux
cd platform/linux && ./build.sh && cd ../..

# Windows (no build needed - uses Python)
```

## Platform-Specific Guides

- **macOS**: See main [README.md](README.md#macos-installation)
- **Windows**: See [platform/windows/README.md](platform/windows/README.md)
- **Linux**: See [platform/linux/README.md](platform/linux/README.md)

## Requirements

### All Platforms
- Python 3.7+
- `python-kasa` package (for Kasa devices)

### Platform-Specific
- **macOS**: Xcode Command Line Tools
- **Windows**: None (pure Python)
- **Linux**: GCC, optionally X11 dev libraries

## Features

- Automatic color switching based on keyboard layout
- Keepalive every 20 seconds
- Auto turn off on screen lock
- Auto restore on screen unlock
- Native performance (minimal CPU/memory)
- Support for Govee + up to 2 Kasa devices
- Kasa commands sent 3x for reliability
