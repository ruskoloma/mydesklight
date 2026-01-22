# Kasa Integration Update

## Summary

Added support for controlling **Kasa smart devices** in addition to Govee lights. You can now configure up to 2 Kasa devices with different behaviors.

## Device Behaviors

### Govee (Required)
- **On Service Start**: Turn on with keyboard layout color
- **On Screen Unlock**: Restore keyboard layout color
- **On Screen Lock**: Turn off
- **On Service Stop**: Turn off

### Kasa 1 (Optional)
- **On Service Start**: Turn ON
- **On Screen Unlock**: Turn ON
- **On Screen Lock**: Stay ON (не выключается)
- **On Service Stop**: Stay ON (не выключается)

### Kasa 2 (Optional)
- **On Service Start**: Turn ON
- **On Screen Unlock**: Turn ON
- **On Screen Lock**: Turn OFF ✓
- **On Service Stop**: Turn OFF ✓

## Configuration

Run the configuration command to set up all devices:

```bash
./mydesklight configure
```

You'll be prompted for:
1. **Govee IP** (required) - e.g., `10.0.0.9`
2. **Kasa 1 IP** (optional) - e.g., `192.168.1.11` (press Enter to skip)
3. **Kasa 2 IP** (optional) - e.g., `192.168.1.139` (press Enter to skip)

Example configuration session:
```
mydesklight Configuration
========================================

Govee Device (required):
  Enter Govee IP address: 10.0.0.9
  ✓ Govee IP set to: 10.0.0.9

Kasa Device 1 (optional - turns ON with service):
  Enter Kasa 1 IP address (press Enter to skip): 192.168.1.11
  ✓ Kasa 1 IP set to: 192.168.1.11

Kasa Device 2 (optional - turns ON with service, OFF on lock/stop):
  Enter Kasa 2 IP address (press Enter to skip): 192.168.1.139
  ✓ Kasa 2 IP set to: 192.168.1.139

========================================
Configuration saved to: ~/.config/mydesklight/config.json

Behavior:
  • Service START / Screen UNLOCK:
    - Govee: Turn on with layout color
    - Kasa 1 (192.168.1.11): Turn ON
    - Kasa 2 (192.168.1.139): Turn ON

  • Service STOP / Screen LOCK:
    - Govee: Turn off
    - Kasa 1 (192.168.1.11): Stay ON
    - Kasa 2 (192.168.1.139): Turn OFF
```

## Usage

```bash
# Start service (turns on all configured devices)
./mydesklight on

# Check status
./mydesklight status
# Output:
# Service is running (PID: 12345)
#
# Configured devices:
#   Govee: 10.0.0.9
#   Kasa 1: 192.168.1.11
#   Kasa 2: 192.168.1.139

# Stop service (turns off Govee and Kasa 2, Kasa 1 stays on)
./mydesklight off
```

## Requirements

The Kasa integration requires the `python-kasa` library:

```bash
pip3 install python-kasa
```

If not installed, the service will still work but Kasa devices won't be controlled (warnings will be shown).

## Implementation Details

### Architecture

1. **Python Core** (`mydesklight_core/kasa_client.py`)
   - Uses `python-kasa` CLI to control devices
   - Handles both devices with different behaviors

2. **Helper Script** (`mydesklight_core/kasa_helper.py`)
   - Called by native monitors (Swift/C/C++)
   - Actions: `on`, `off`, `lock`, `unlock`

3. **Native Integration**
   - **macOS**: Swift calls Python helper via `Process`
   - **Windows**: C calls Python helper via `CreateProcess`
   - **Linux**: C calls Python helper via `fork/exec`

### Configuration Storage

Stored in `~/.config/mydesklight/config.json`:

```json
{
  "govee_ip": "10.0.0.9",
  "kasa1_ip": "192.168.1.11",
  "kasa2_ip": "192.168.1.139"
}
```

### Control Flow

#### Service Start
```
mydesklight on
  ↓
ServiceManager.start()
  ↓
1. Turn on Kasa 1 & 2 (Python)
2. Start native monitor
  ↓
Native Monitor.start()
  ↓
Call kasa_helper.py on
  ↓
Turn on Kasa 1 & 2
```

#### Screen Lock
```
Screen Lock Event
  ↓
Native Monitor.screenLocked()
  ↓
1. Turn off Govee (UDP)
2. Call kasa_helper.py lock
  ↓
Turn off only Kasa 2
```

#### Screen Unlock
```
Screen Unlock Event
  ↓
Native Monitor.screenUnlocked()
  ↓
1. Restore Govee color (UDP)
2. Call kasa_helper.py unlock
  ↓
Turn on Kasa 1 & 2
```

#### Service Stop
```
mydesklight off
  ↓
ServiceManager.stop()
  ↓
1. Turn off Govee (UDP)
2. Turn off only Kasa 2 (Python)
3. Kill native monitor process
```

## Testing

### Test Kasa Control Manually

```bash
# Turn on Kasa 1
python3 -m kasa.cli --host 192.168.1.11 on

# Turn off Kasa 1
python3 -m kasa.cli --host 192.168.1.11 off

# Turn on Kasa 2
python3 -m kasa.cli --host 192.168.1.139 on

# Turn off Kasa 2
python3 -m kasa.cli --host 192.168.1.139 off
```

### Test Helper Script

```bash
# Test turning on (both devices)
./mydesklight_core/kasa_helper.py on

# Test turning off (only Kasa 2)
./mydesklight_core/kasa_helper.py lock

# Test unlock (both devices)
./mydesklight_core/kasa_helper.py unlock
```

### Test Full Integration

1. Configure devices:
   ```bash
   ./mydesklight configure
   ```

2. Start service:
   ```bash
   ./mydesklight on
   ```
   → Should turn on Govee + Kasa 1 + Kasa 2

3. Lock screen:
   → Should turn off Govee + Kasa 2 (Kasa 1 stays on)

4. Unlock screen:
   → Should turn on Govee + Kasa 1 + Kasa 2

5. Stop service:
   ```bash
   ./mydesklight off
   ```
   → Should turn off Govee + Kasa 2 (Kasa 1 stays on)

## Troubleshooting

### Kasa devices not responding

1. **Check if python-kasa is installed:**
   ```bash
   python3 -m kasa.cli --help
   ```

2. **Test device connectivity:**
   ```bash
   ping 192.168.1.11
   python3 -m kasa.cli --host 192.168.1.11 state
   ```

3. **Check helper script:**
   ```bash
   ./mydesklight_core/kasa_helper.py on
   ```

### Warnings in logs

If you see warnings like:
```
Warning: Failed to turn on Kasa device at 192.168.1.11: ...
```

This means:
- `python-kasa` is not installed, or
- Device is not reachable, or
- Device IP is incorrect

The service will continue to work for Govee, just without Kasa control.

## Files Modified

1. **mydesklight_core/config.py** - Added Kasa IP getters/setters
2. **mydesklight_core/kasa_client.py** - New Kasa control module
3. **mydesklight_core/kasa_helper.py** - New helper script for native monitors
4. **mydesklight_core/service.py** - Integrated Kasa control in start/stop
5. **mydesklight** - Updated configure command and help text
6. **platform/macos/KeyboardMonitor.swift** - Added Kasa helper calls

## Future Enhancements

- Support for more than 2 Kasa devices
- Different color modes for Kasa RGB devices
- Brightness control
- Schedule-based control
- Web UI for configuration
