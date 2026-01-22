#!/usr/bin/env python3
"""
Helper script to control Kasa devices from native monitors
Called by platform-specific keyboard monitors
"""

import sys
import json
from pathlib import Path

# Add parent directory to path to import mydesklight_core
sys.path.insert(0, str(Path(__file__).parent.parent))

from mydesklight_core.config import Config
from mydesklight_core.kasa_client import control_kasa_devices


def main():
    if len(sys.argv) < 2:
        print("Usage: kasa_helper.py [on|off|lock|unlock]", file=sys.stderr)
        sys.exit(1)
    
    action = sys.argv[1].lower()
    config = Config()
    
    kasa1_ip = config.get_kasa1_ip()
    kasa2_ip = config.get_kasa2_ip()
    
    # No Kasa devices configured
    if not kasa1_ip and not kasa2_ip:
        sys.exit(0)
    
    if action == 'on' or action == 'unlock':
        # Turn on both Kasa devices
        control_kasa_devices(kasa1_ip, kasa2_ip, turn_on=True, kasa2_only=False)
    elif action == 'off' or action == 'lock':
        # Turn off only Kasa 2
        control_kasa_devices(None, kasa2_ip, turn_on=False, kasa2_only=True)
    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
