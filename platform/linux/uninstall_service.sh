#!/bin/bash
# Uninstall mydesklight Linux systemd service

set -e

echo "mydesklight - Linux Service Uninstaller"
echo "========================================"
echo ""

SERVICE_FILE="/etc/systemd/system/mydesklight.service"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Error: Do not run this script as root"
    echo "It will ask for sudo password when needed"
    exit 1
fi

if [ ! -f "$SERVICE_FILE" ]; then
    echo "Service not installed (service file not found)"
    exit 0
fi

# Stop the service
echo "Stopping service..."
sudo systemctl stop mydesklight 2>/dev/null || true

# Disable the service
echo "Disabling service..."
sudo systemctl disable mydesklight 2>/dev/null || true

# Remove service file
echo "Removing service file..."
sudo rm "$SERVICE_FILE"

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

echo ""
echo "✓ Service uninstalled successfully"
echo ""
echo "To remove configuration:"
echo "  rm -rf ~/.config/mydesklight"
echo ""
