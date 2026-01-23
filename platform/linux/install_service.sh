#!/bin/bash
# Install mydesklight as a Linux systemd service

set -e

echo "mydesklight - Linux Service Installer"
echo "======================================"
echo ""

# Get absolute path to project directory
PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
MYDESKLIGHT_BIN="$PROJECT_DIR/mydesklight"
SERVICE_FILE="/etc/systemd/system/mydesklight.service"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Error: Do not run this script as root"
    echo "It will ask for sudo password when needed"
    exit 1
fi

# Check if mydesklight exists
if [ ! -f "$MYDESKLIGHT_BIN" ]; then
    echo "Error: mydesklight not found at $MYDESKLIGHT_BIN"
    exit 1
fi

# Check if monitor binary exists
if [ ! -f "$PROJECT_DIR/platform/linux/keyboard_monitor" ]; then
    echo "Error: Monitor binary not found"
    echo "Please build it first: cd platform/linux && ./build.sh"
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

# Create systemd service file
echo "Creating systemd service file..."
sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=mydesklight Monitor Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$MYDESKLIGHT_BIN on
ExecStop=$MYDESKLIGHT_BIN off
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Created service file: $SERVICE_FILE"

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
echo "Enabling service..."
sudo systemctl enable mydesklight

# Start service now
echo "Starting service..."
sudo systemctl start mydesklight

echo ""
echo "======================================"
echo "Service installed successfully!"
echo ""
echo "The service will now:"
echo "  • Start automatically on boot"
echo "  • Run in the background"
echo "  • Control your lights based on keyboard layout"
echo ""
echo "Useful commands:"
echo "  • Check status:  sudo systemctl status mydesklight"
echo "  • Stop service:  sudo systemctl stop mydesklight"
echo "  • Start service: sudo systemctl start mydesklight"
echo "  • Restart:       sudo systemctl restart mydesklight"
echo "  • View logs:     journalctl -u mydesklight -f"
echo "  • Disable:       sudo systemctl disable mydesklight"
echo "  • Uninstall:     ./platform/linux/uninstall_service.sh"
echo ""
