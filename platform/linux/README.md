# mydesklight - Linux Installation Guide

## Requirements

- Linux (any distribution)
- Python 3.7+
- GCC compiler
- X11 development libraries (optional, for better performance)

## Quick Install

### Ubuntu/Debian

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install build-essential python3 python3-pip

# Optional: X11 support (recommended for better performance)
sudo apt-get install libx11-dev libxkbfile-dev

# Build
cd platform/linux
chmod +x build.sh
./build.sh
cd ../..
```

### Fedora/RHEL/CentOS

```bash
# Install dependencies
sudo dnf install gcc python3 python3-pip

# Optional: X11 support (recommended)
sudo dnf install libX11-devel libxkbfile-devel

# Build
cd platform/linux
chmod +x build.sh
./build.sh
cd ../..
```

### Arch Linux

```bash
# Install dependencies
sudo pacman -S base-devel python python-pip

# Optional: X11 support (recommended)
sudo pacman -S libx11 libxkbfile

# Build
cd platform/linux
chmod +x build.sh
./build.sh
cd ../..
```

### Other Distributions

```bash
# Install GCC and Python using your package manager
# Then:
cd platform/linux
chmod +x build.sh
./build.sh
cd ../..
```

## Configuration

1. **Find your Govee device IP**:
   ```bash
   # Option 1: Check router's connected devices
   # Option 2: Use nmap
   sudo apt-get install nmap
   nmap -sn 192.168.1.0/24
   ```

2. **Configure mydesklight**:
   ```bash
   ./mydesklight configure
   ```
   Enter your Govee IP when prompted.

## Usage

```bash
# Start monitoring
./mydesklight on

# Stop monitoring and turn off lights
./mydesklight off

# Check status
./mydesklight status
```

## Add to PATH (Optional)

```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export PATH="$PATH:'$(pwd)'"' >> ~/.bashrc
source ~/.bashrc

# Now you can use from anywhere:
mydesklight on
mydesklight off
```

## Auto-Start on Login (Optional)

### systemd (Most Modern Distros)

1. Create service file:
   ```bash
   sudo nano /etc/systemd/user/mydesklight.service
   ```

2. Add content (replace paths):
   ```ini
   [Unit]
   Description=mydesklight Monitor Service
   After=network.target

   [Service]
   Type=simple
   ExecStart=/path/to/monitor-backlight-service/mydesklight on
   ExecStop=/path/to/monitor-backlight-service/mydesklight off
   Restart=on-failure

   [Install]
   WantedBy=default.target
   ```

3. Enable and start:
   ```bash
   systemctl --user enable mydesklight
   systemctl --user start mydesklight
   ```

### Desktop Autostart (Alternative)

```bash
# Create autostart entry
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/mydesklight.desktop << EOF
[Desktop Entry]
Type=Application
Name=mydesklight
Exec=/path/to/monitor-backlight-service/mydesklight on
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
```

## X11 vs Generic Mode

### X11 Mode (Recommended)

**Advantages:**
- Real-time keyboard layout detection
- Event-driven (no polling)
- Very low CPU usage

**Requirements:**
- X11 development libraries
- X11 display server (not Wayland)

**Check if you have X11:**
```bash
echo $XDG_SESSION_TYPE
# If output is "x11", you're using X11
```

### Generic Mode (Fallback)

**Advantages:**
- Works on Wayland
- No X11 dependencies
- Works on any display server

**Disadvantages:**
- Polls every 2 seconds
- Slightly higher CPU usage (still minimal)

The build script automatically detects and uses X11 if available.

## Troubleshooting

### Build Errors

**"gcc: command not found"**
```bash
# Ubuntu/Debian
sudo apt-get install build-essential

# Fedora/RHEL
sudo dnf install gcc

# Arch
sudo pacman -S base-devel
```

**"X11/Xlib.h: No such file or directory"**
```bash
# Ubuntu/Debian
sudo apt-get install libx11-dev libxkbfile-dev

# Fedora/RHEL
sudo dnf install libX11-devel libxkbfile-devel

# Arch
sudo pacman -S libx11 libxkbfile
```

### Runtime Errors

**"Service won't start"**
```bash
# Check if binary exists
ls -l platform/linux/keyboard_monitor

# Rebuild
cd platform/linux && ./build.sh
```

**"Permission denied"**
```bash
# Make binary executable
chmod +x platform/linux/keyboard_monitor
chmod +x mydesklight
```

**"Cannot open display"** (X11 mode)
- Make sure you're running in a graphical session
- Or rebuild without X11 support (generic mode)

**"Govee IP not configured"**
```bash
./mydesklight configure
```

### Firewall Issues

If UDP packets are blocked:

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow out 4003/udp

# Fedora/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=4003/udp
sudo firewall-cmd --reload

# iptables
sudo iptables -A OUTPUT -p udp --dport 4003 -j ACCEPT
```

## Uninstall

```bash
# Stop service
./mydesklight off

# Remove configuration
rm -rf ~/.config/mydesklight

# Remove systemd service (if created)
systemctl --user disable mydesklight
rm ~/.config/systemd/user/mydesklight.service

# Delete repository
cd ..
rm -rf monitor-backlight-service
```

## How It Works

The Linux monitor supports two modes:

### X11 Mode
- Uses **XKB extension** for keyboard layout events
- Event-driven, no polling
- Minimal CPU usage

### Generic Mode
- Uses **setxkbmap** command
- Polls every 2 seconds
- Works on Wayland and other display servers

Both modes use:
- **POSIX sockets** for UDP communication
- **pthreads** for keepalive timer
- **Native C** for minimal resource usage

## Color Customization

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

## Performance

**X11 Mode:**
- CPU: < 0.1%
- Memory: ~2 MB
- Network: ~100 bytes every 20 seconds (keepalive)

**Generic Mode:**
- CPU: < 0.5%
- Memory: ~2 MB
- Network: ~100 bytes every 20 seconds (keepalive)

## Wayland Support

Wayland doesn't provide a standard way to detect keyboard layout changes. The generic mode works but uses polling.

For better Wayland support in the future, we could add:
- **GNOME**: Use `gsettings` monitoring
- **KDE**: Use `kwriteconfig5` monitoring
- **Sway**: Use IPC socket

Currently, generic mode works on all Wayland compositors.

## Support

For issues, check the main [README.md](../../README.md) or open an issue on GitHub.
