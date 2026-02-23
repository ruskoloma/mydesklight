# MonitorBacklight

Native macOS menu bar app for Govee + TP-Link Kasa desk light control.

## Requirements

- macOS 13+
- Xcode Command Line Tools (`xcode-select --install`)
- Kasa support: `python3 -m pip install python-kasa`

## Build

```bash
macos/scripts/generate_icon.sh
macos/scripts/build_app.sh
macos/scripts/build_dmg.sh
```

Outputs:

- `/Users/rsln-ua/Projects/monitor-backlight-service/dist/MonitorBacklight.app`
- `/Users/rsln-ua/Projects/monitor-backlight-service/dist/MonitorBacklight.dmg`

## How It Works

`Enabled` controls reactive automation only.

- `Enabled = ON`: app reacts to keyboard layout, screen lock/unlock, and keepalive.
- `Enabled = OFF`: app does not react to events; current device state stays unchanged.

Reactive color logic:

- `ABC/US` -> `RGB(255,180,110)`
- Other layouts -> `RGB(120,180,255)`

Lock behavior (when enabled):

- Govee OFF
- Kasa 2 OFF
- Kasa 1 unchanged

Unlock behavior (when enabled):

- Govee restored by current layout
- Kasa 1 ON
- Kasa 2 ON

## Menu

- `[ ] Enabled`
- `Turn On` -> `All`, `Govee`, `Kasa 1`, `Kasa 2`
- `Turn Off` -> `All`, `Govee`, `Kasa 1`, `Kasa 2`
- `Control Center...`

Manual Turn On/Off actions always send commands, independent of `Enabled`.

## Control Center

- Service toggles: `Enabled`, `Launch at Login`
- Color chips: English, Russian, Custom
- Device IP config: Govee, Kasa 1, Kasa 2
- Manual signal buttons (same as tray menu)

Config file:

- `/Users/<user>/Library/Application Support/MonitorBacklightService/config.json`
- Legacy config is auto-imported from `/Users/<user>/.config/mydesklight/config.json` if needed.
