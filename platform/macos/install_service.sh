#!/bin/bash
# Install mydesklight as a macOS LaunchAgent service

set -e

echo "mydesklight - macOS Service Installer"
echo "======================================"
echo ""

# Get absolute path to project directory
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MYDESKLIGHT_BIN="$PROJECT_DIR/mydesklight"
PLIST_FILE="$HOME/Library/LaunchAgents/com.mydesklight.plist"

# Check if mydesklight exists
if [ ! -f "$MYDESKLIGHT_BIN" ]; then
    echo "Error: mydesklight not found at $MYDESKLIGHT_BIN"
    exit 1
fi

# Check if monitor binary exists
if [ ! -f "$PROJECT_DIR/platform/macos/KeyboardMonitor" ]; then
    echo "Error: Monitor binary not found"
    echo "Please build it first: cd platform/macos && ./build.sh"
    exit 1
fi

# Check if already configured
if [ ! -f "$HOME/.config/mydesklight/config.json" ]; then
    echo "Warning: mydesklight not configured yet"
    echo "Run './mydesklight configure' first"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$HOME/Library/LaunchAgents"

# Create plist file
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mydesklight</string>
    <key>ProgramArguments</key>
    <array>
        <string>$MYDESKLIGHT_BIN</string>
        <string>on</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
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

echo "✓ Created LaunchAgent plist: $PLIST_FILE"

# Unload if already loaded
launchctl unload "$PLIST_FILE" 2>/dev/null || true

# Load the service
launchctl load "$PLIST_FILE"
echo "✓ Loaded LaunchAgent"

# Start the service
launchctl start com.mydesklight
echo "✓ Started service"

echo ""
echo "======================================"
echo "Service installed successfully!"
echo ""
echo "The service will now:"
echo "  • Start automatically on login"
echo "  • Run in the background"
echo "  • Control your lights based on keyboard layout"
echo ""
echo "Useful commands:"
echo "  • Check status:  ./mydesklight status"
echo "  • Stop service:  launchctl stop com.mydesklight"
echo "  • Start service: launchctl start com.mydesklight"
echo "  • View logs:     tail -f /tmp/mydesklight.log"
echo "  • Uninstall:     ./platform/macos/uninstall_service.sh"
echo ""
