#!/bin/bash
# Uninstall mydesklight macOS LaunchAgent service

set -e

echo "mydesklight - macOS Service Uninstaller"
echo "========================================"
echo ""

PLIST_FILE="$HOME/Library/LaunchAgents/com.mydesklight.plist"

if [ ! -f "$PLIST_FILE" ]; then
    echo "Service not installed (plist file not found)"
    exit 0
fi

# Stop the service
echo "Stopping service..."
launchctl stop com.mydesklight 2>/dev/null || true

# Unload the service
echo "Unloading service..."
launchctl unload "$PLIST_FILE" 2>/dev/null || true

# Remove plist file
echo "Removing plist file..."
rm "$PLIST_FILE"

echo ""
echo "✓ Service uninstalled successfully"
echo ""
echo "To remove configuration:"
echo "  rm -rf ~/.config/mydesklight"
echo ""
