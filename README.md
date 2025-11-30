# Govee Keyboard Layout Monitor

A macOS service that automatically changes Govee light bar colors based on your current keyboard layout via UDP commands.

## How It Works

- **English layout (ABC)**: RGB(255, 180, 110) - warm orange
- **Other layouts**: RGB(120, 180, 255) - blue

The service subscribes to system keyboard layout change events and sends UDP commands to your Govee light bars.

## Features

- Real-time keyboard layout monitoring
- UDP commands sent 3x for reliability (handles packet loss)
- Keepalive every 20 seconds to prevent lamp sleep
- No API key required - direct UDP control
- Lightweight Swift binary

## Requirements

- macOS with Swift compiler (pre-installed)
- Govee light bars on the same network
- IP address of your Govee device

## Finding Your Govee IP Address

### Option 1: Govee App
1. Open Govee Home app
2. Select your device
3. Settings → Device Info → IP Address

### Option 2: Router
Check your router's admin panel for connected devices

### Option 3: Network Scan
```bash
# Install nmap if needed
brew install nmap

# Scan your local network (adjust subnet)
nmap -sn 192.168.1.0/24
```

## Installation & Usage

### 1. Compile the Program

```bash
cd /Users/rsln-ua/Projects/monitor-backlight-service
swiftc -o KeyboardMonitor KeyboardMonitor.swift
```

### 2. Run (replace with your IP)

```bash
./KeyboardMonitor 10.0.0.111
```

### 3. Test

Switch your keyboard layout (Ctrl+Space or Cmd+Space) - the color should change!

## Auto-Start on System Boot

Edit the plist file with your IP:

```bash
nano com.user.keyboardmonitor.plist
```

Replace `GOVEE_IP_HERE` with your actual IP, then:

```bash
# Copy to LaunchAgents
cp com.user.keyboardmonitor.plist ~/Library/LaunchAgents/

# Load and start the service
launchctl load ~/Library/LaunchAgents/com.user.keyboardmonitor.plist
launchctl start com.user.keyboardmonitor

# Check logs
tail -f /tmp/keyboard-monitor.log
```

## Stop the Service

```bash
launchctl stop com.user.keyboardmonitor
launchctl unload ~/Library/LaunchAgents/com.user.keyboardmonitor.plist
```

## Customizing Colors

Edit `KeyboardMonitor.swift`:

```swift
// Lines 12-13
private let englishColor = (r: 255, g: 180, b: 110)  // English layout color
private let otherColor = (r: 120, g: 180, b: 255)    // Other layouts color
```

After changes, recompile:
```bash
swiftc -o KeyboardMonitor KeyboardMonitor.swift
```

## UDP Commands

The program sends JSON via UDP to port 4003:

**English layout:**
```json
{
  "msg": {
    "cmd": "colorwc",
    "data": {
      "color": {"r": 255, "g": 180, "b": 110},
      "colorTemInKelvin": 0
    }
  }
}
```

**Other layouts:**
```json
{
  "msg": {
    "cmd": "colorwc",
    "data": {
      "color": {"r": 120, "g": 180, "b": 255},
      "colorTemInKelvin": 0
    }
  }
}
```

## Troubleshooting

**Not working?**
1. Verify device IP address
2. Ensure device is on the same network
3. Check UDP port 4003 is not blocked
4. View logs: `tail -f /tmp/keyboard-monitor.log`

**Find current layout name:**
```bash
defaults read ~/Library/Preferences/com.apple.HIToolbox.plist AppleSelectedInputSources
```

**Restart the service:**
```bash
# Kill the process
pkill -f KeyboardMonitor

# Recompile and run
swiftc -o KeyboardMonitor KeyboardMonitor.swift && ./KeyboardMonitor 10.0.0.111
```

## Technical Details

- **Language**: Swift
- **Protocol**: UDP on port 4003
- **Reliability**: Each command sent 3 times with 10ms delay
- **Keepalive**: Every 20 seconds to prevent device sleep
- **Event Source**: macOS DistributedNotificationCenter

## License

MIT - Do whatever you want with it
