#!/bin/bash
# Setup script for mydesklight

set -e

echo "mydesklight - Setup"
echo "==================="
echo ""

# Detect platform
PLATFORM=$(uname -s)

case "$PLATFORM" in
    Darwin)
        echo "Platform: macOS"
        echo ""
        
        # Check for Swift compiler
        if ! command -v swiftc &> /dev/null; then
            echo "Error: Swift compiler not found"
            echo "Please install Xcode Command Line Tools:"
            echo "  xcode-select --install"
            exit 1
        fi
        
        # Build macOS monitor
        echo "Building macOS keyboard monitor..."
        cd platform/macos
        chmod +x build.sh
        ./build.sh
        cd ../..
        echo ""
        ;;
    
    Linux)
        echo "Platform: Linux"
        echo ""
        
        # Check for GCC
        if ! command -v gcc &> /dev/null; then
            echo "Error: GCC compiler not found"
            echo "Please install build tools:"
            echo "  Ubuntu/Debian: sudo apt-get install build-essential"
            echo "  Fedora/RHEL:   sudo dnf install gcc"
            echo "  Arch:          sudo pacman -S base-devel"
            exit 1
        fi
        
        # Build Linux monitor
        echo "Building Linux keyboard monitor..."
        cd platform/linux
        chmod +x build.sh
        ./build.sh
        cd ../..
        echo ""
        ;;
    
    MINGW*|MSYS*|CYGWIN*)
        echo "Platform: Windows"
        echo ""
        echo "Please build manually:"
        echo "  1. Open Visual Studio Developer Command Prompt"
        echo "  2. cd platform\\windows"
        echo "  3. build.bat"
        echo ""
        echo "Or use MinGW:"
        echo "  cd platform/windows"
        echo "  gcc -o KeyboardMonitor.exe KeyboardMonitor.c -lws2_32 -lwtsapi32 -O2"
        exit 0
        ;;
    
    *)
        echo "Error: Unsupported platform: $PLATFORM"
        exit 1
        ;;
esac

# Make CLI executable
chmod +x mydesklight

echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Configure your Govee device IP:"
echo "     ./mydesklight configure"
echo ""
echo "  2. Start the service:"
echo "     ./mydesklight on"
echo ""
echo "  3. (Optional) Add to PATH:"
echo "     echo 'export PATH=\"\$PATH:$(pwd)\"' >> ~/.bashrc"
echo "     source ~/.bashrc"
echo ""
