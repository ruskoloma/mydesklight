# mydesklight - Quick Reference

## Installation

```bash
# macOS/Linux
./setup.sh

# Windows
cd platform\windows
build.bat
```

## Basic Commands

```bash
# Configure Govee IP (first time)
mydesklight configure

# Start service
mydesklight on

# Stop service
mydesklight off

# Check status
mydesklight status
```

## Colors

- **English (ABC/US)**: RGB(255, 180, 110) - Warm orange
- **Other layouts**: RGB(120, 180, 255) - Blue

## Features

- ✅ Automatic color switching based on keyboard layout
- ✅ Keepalive every 20 seconds
- ✅ Auto turn off on screen lock
- ✅ Auto restore on screen unlock
- ✅ Native performance (minimal CPU/memory)

## Configuration Files

- **macOS/Linux**: `~/.config/mydesklight/config.json`
- **Windows**: `%APPDATA%\mydesklight\config.json`

## Troubleshooting

```bash
# Check if service is running
mydesklight status

# Rebuild monitor
cd platform/[macos|windows|linux]
./build.sh  # or build.bat on Windows

# Test Govee connection
ping <your-govee-ip>

# View config
cat ~/.config/mydesklight/config.json  # macOS/Linux
type %APPDATA%\mydesklight\config.json  # Windows
```

## Platform-Specific Guides

- [macOS](README.md#macos-installation)
- [Windows](platform/windows/README.md)
- [Linux](platform/linux/README.md)

## Customization

To change colors, edit the platform-specific source file and rebuild:

- **macOS**: `platform/macos/KeyboardMonitor.swift` (lines 14-15)
- **Windows**: `platform/windows/KeyboardMonitor.c` (lines 17-24)
- **Linux**: `platform/linux/keyboard_monitor.c` (lines 20-27)
