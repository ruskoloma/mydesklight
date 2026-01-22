# Changelog

All notable changes to mydesklight will be documented in this file.

## [2.0.0] - 2026-01-21

### Added - Cross-Platform Support

- **Windows support** with native C implementation
  - Win32 API for keyboard layout detection
  - WTS API for session lock/unlock detection
  - Winsock2 for UDP communication
  
- **Linux support** with dual-mode implementation
  - X11 mode for event-driven layout detection
  - Generic mode (polling) for Wayland and other display servers
  - pthread-based keepalive timer
  
- **Python core** for cross-platform functionality
  - Configuration management
  - Service control
  - UDP client abstraction
  
- **CLI tool** (`mydesklight`) with commands:
  - `configure` - Set Govee device IP
  - `on` - Start monitoring service
  - `off` - Stop service and turn off lights
  - `status` - Show service status
  - `help` - Show usage information

- **Automated setup**
  - `setup.sh` script for macOS/Linux
  - Platform detection and automatic building
  
- **Comprehensive documentation**
  - Main README with all platforms
  - Platform-specific guides (Windows, Linux)
  - Quick reference guide
  - Build scripts for all platforms

### Changed

- **Refactored macOS implementation**
  - Moved to `platform/macos/` directory
  - Updated to work with new CLI structure
  - Maintained all original features

- **Project structure**
  - Organized into platform-specific directories
  - Separated Python core from native monitors
  - Improved .gitignore for all platforms

### Technical Details

- **macOS**: Swift with Carbon/Network frameworks
- **Windows**: C with Win32 API and Winsock2
- **Linux**: C with optional X11 support
- **Core**: Python 3.7+ for configuration and service management

---

## [1.0.0] - 2025-11-30

### Initial Release - macOS Only

- Keyboard layout monitoring on macOS
- Automatic color switching (English vs Other)
- UDP control for Govee devices
- Screen lock/unlock detection
- Keepalive timer (20 seconds)
- LaunchAgent support for auto-start
- Direct IP-based configuration
