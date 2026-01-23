# mydesklight - Windows Installation Guide

## Requirements

- Windows 10 or later
- Python 3.7+

## Quick Install (No Compilation Needed!)

### 1. Install Dependencies

```powershell
cd C:\path\to\mydesklight
.\platform\windows\setup.bat
```

Or manually:
```powershell
pip install python-kasa
```

### 2. Configure Devices

```powershell
python mydesklight configure
```

Enter IP addresses when prompted:
- **Govee**: e.g., `10.0.0.9`
- **Kasa 1** (optional): e.g., `192.168.1.11`
- **Kasa 2** (optional): e.g., `192.168.1.139`

### 3. Test the Service

```powershell
python mydesklight on
python mydesklight status
python mydesklight off
```

## Install as Windows Service (Auto-start on Boot)

### Option 1: Using Task Scheduler (Recommended)

1. Open **Task Scheduler** (search in Start menu)
2. Click **Create Task** (not "Create Basic Task")
3. **General tab**:
   - Name: `mydesklight`
   - Description: `Monitor backlight control service`
   - Check: **Run whether user is logged on or not**
   - Check: **Run with highest privileges**
   - Configure for: **Windows 10**

4. **Triggers tab**:
   - Click **New**
   - Begin the task: **At log on**
   - Specific user: (your username)
   - Click **OK**

5. **Actions tab**:
   - Click **New**
   - Action: **Start a program**
   - Program/script: `pythonw.exe`
   - Add arguments: `C:\path\to\mydesklight\mydesklight on`
   - Start in: `C:\path\to\mydesklight`
   - Click **OK**

6. **Conditions tab**:
   - Uncheck: **Start the task only if the computer is on AC power**

7. **Settings tab**:
   - Check: **Allow task to be run on demand**
   - Check: **If the running task does not end when requested, force it to stop**

8. Click **OK** and enter your password if prompted

### Option 2: Using Startup Folder

1. Press `Win + R`
2. Type: `shell:startup` and press Enter
3. Create a new shortcut:
   - Right-click → New → Shortcut
   - Location: `pythonw C:\path\to\mydesklight\mydesklight on`
   - Name: `mydesklight`

### Option 3: Using NSSM (Advanced)

Install NSSM (Non-Sucking Service Manager):

```powershell
# Download from https://nssm.cc/download
# Or use chocolatey:
choco install nssm

# Install service
nssm install mydesklight "C:\Python\python.exe" "C:\path\to\mydesklight\mydesklight" "on"
nssm set mydesklight AppDirectory "C:\path\to\mydesklight"
nssm set mydesklight DisplayName "mydesklight Monitor Service"
nssm set mydesklight Description "Automatic monitor backlight control"
nssm set mydesklight Start SERVICE_AUTO_START

# Start service
nssm start mydesklight

# Check status
nssm status mydesklight

# Stop service
nssm stop mydesklight

# Remove service
nssm remove mydesklight confirm
```

## Make `mydesklight` Command Available Globally

### Option 1: Add to PATH

1. Press `Win + X` → System
2. Click **Advanced system settings**
3. Click **Environment Variables**
4. Under **User variables**, select **Path** → **Edit**
5. Click **New** and add: `C:\path\to\mydesklight`
6. Click **OK** on all dialogs
7. Restart PowerShell

Now you can use:
```powershell
mydesklight on
mydesklight off
mydesklight status
```

### Option 2: Create Batch Wrapper

Create `C:\Windows\mydesklight.bat`:

```batch
@echo off
python C:\path\to\mydesklight\mydesklight %*
```

Now you can use `mydesklight` from anywhere.

## Usage

```powershell
# Start monitoring
python mydesklight on

# Stop monitoring and turn off lights
python mydesklight off

# Check status
python mydesklight status

# Reconfigure devices
python mydesklight configure

# Show help
python mydesklight help
```

## Device Behavior

| Event | Govee | Kasa 1 | Kasa 2 |
|-------|-------|--------|--------|
| **Service Start** | ON (color) | ON | ON |
| **Screen Unlock** | ON (color) | ON | ON |
| **Screen Lock** | OFF | **Stays ON** | OFF |
| **Service Stop** | OFF | **Stays ON** | OFF |

## Colors

- **English layout (EN)**: RGB(255, 180, 110) - Warm orange
- **Other layouts (RU, UA, etc.)**: RGB(120, 180, 255) - Blue

## Testing

### Test Govee Directly

```powershell
# Turn off
python -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.sendto(b'{\"msg\":{\"cmd\":\"turn\",\"data\":{\"value\":0}}}', ('10.0.0.9', 4003))"

# Turn on
python -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.sendto(b'{\"msg\":{\"cmd\":\"turn\",\"data\":{\"value\":1}}}', ('10.0.0.9', 4003))"
```

### Test Kasa Devices

```powershell
# Turn on Kasa 1
python -m kasa.cli --host 192.168.1.11 on

# Turn off Kasa 2
python -m kasa.cli --host 192.168.1.139 off

# Check device status
python -m kasa.cli --host 192.168.1.11 state
```

## Troubleshooting

### "python is not recognized"

Install Python:
1. Download from https://www.python.org/downloads/
2. **Important**: Check "Add Python to PATH" during installation

### "ModuleNotFoundError: No module named 'kasa'"

```powershell
pip install python-kasa
```

### Devices Not Responding

1. Check IP addresses:
   ```powershell
   ping 10.0.0.9
   ping 192.168.1.11
   ping 192.168.1.139
   ```

2. Check configuration:
   ```powershell
   python mydesklight status
   ```

3. Reconfigure:
   ```powershell
   python mydesklight configure
   ```

### Service Won't Start

```powershell
# Stop any running instance
python mydesklight off

# Check for errors by running directly
python platform\windows\keyboard_monitor.py
```

### Firewall Blocking UDP

Allow Python through Windows Firewall:
1. Control Panel → Windows Defender Firewall
2. Allow an app or feature through Windows Defender Firewall
3. Click **Change settings**
4. Find **Python** and check both **Private** and **Public**

## Technical Details

**Implementation**: Pure Python (no compilation required!)
- **Keyboard monitoring**: Windows API via `ctypes`
- **UDP**: Built-in `socket` module
- **Kasa control**: `python-kasa` library
- **Multithreading**: `threading` for keepalive

**Performance**:
- CPU: < 0.5%
- RAM: ~15 MB
- Network: ~100 bytes every 20 seconds

## Advantages of Python Version

- No compilation needed - works immediately
- No Visual Studio required - just Python
- Easy to modify - edit `.py` files directly
- Cross-platform code - easy to port

## Files

- `platform/windows/keyboard_monitor.py` - Main monitor script
- `platform/windows/setup.bat` - Dependency installer
- `mydesklight_core/` - Shared code (UDP, Kasa, config)
- `mydesklight` - CLI tool

## Customization

### Change Colors

Edit `mydesklight_core/udp_client.py`:

```python
# Lines 38-39
ENGLISH_COLOR = (255, 180, 110)  # English layout
OTHER_COLOR = (120, 180, 255)    # Other layouts
```

### View Logs

Run monitor directly to see all events:

```powershell
python platform\windows\keyboard_monitor.py
```

## Uninstall

```powershell
# Stop service
python mydesklight off

# Remove from Task Scheduler (if installed)
# Open Task Scheduler → Delete "mydesklight" task

# Remove configuration
rmdir /s %APPDATA%\mydesklight

# Remove project
cd ..
rmdir /s mydesklight
```

## Support

For issues, check the main [README.md](../../README.md) or open an issue on GitHub.
