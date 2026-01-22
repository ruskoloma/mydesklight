#!/bin/bash
# Build script for macOS keyboard monitor

echo "Building macOS Keyboard Monitor..."

cd "$(dirname "$0")"

swiftc -o KeyboardMonitor KeyboardMonitor.swift

if [ $? -eq 0 ]; then
    echo "✓ Build successful: KeyboardMonitor"
    echo "Binary location: $(pwd)/KeyboardMonitor"
else
    echo "✗ Build failed"
    exit 1
fi
