#!/bin/bash
# Build script for Linux keyboard monitor

echo "Building Linux Keyboard Monitor..."

# Try to build with X11 support first
if pkg-config --exists x11 xkbfile; then
    echo "Building with X11 support..."
    gcc -o keyboard_monitor keyboard_monitor.c \
        -DHAVE_X11 \
        $(pkg-config --cflags --libs x11 xkbfile) \
        -lpthread \
        -O2 -Wall
    
    if [ $? -eq 0 ]; then
        echo "✓ Build successful with X11 support: keyboard_monitor"
        echo "Binary location: $(pwd)/keyboard_monitor"
        exit 0
    fi
fi

# Fallback to generic build
echo "X11 not available, building with generic support (polling)..."
gcc -o keyboard_monitor keyboard_monitor.c -lpthread -O2 -Wall

if [ $? -eq 0 ]; then
    echo "✓ Build successful (generic mode): keyboard_monitor"
    echo "Binary location: $(pwd)/keyboard_monitor"
    echo ""
    echo "Note: For better performance, install X11 development libraries:"
    echo "  Ubuntu/Debian: sudo apt-get install libx11-dev libxkbfile-dev"
    echo "  Fedora/RHEL:   sudo dnf install libX11-devel libxkbfile-devel"
    echo "  Arch:          sudo pacman -S libx11 libxkbfile"
else
    echo "✗ Build failed"
    exit 1
fi
