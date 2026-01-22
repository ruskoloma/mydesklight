"""
Kasa device control for mydesklight
"""

import subprocess
import sys
from typing import Optional


class KasaClient:
    """Handles communication with Kasa smart devices"""
    
    def __init__(self, ip: str):
        self.ip = ip
    
    def turn_on(self) -> bool:
        """
        Turn on Kasa device
        
        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'kasa.cli', '--host', self.ip, 'on'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"Warning: Failed to turn on Kasa device at {self.ip}: {e}")
            return False
    
    def turn_off(self) -> bool:
        """
        Turn off Kasa device
        
        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'kasa.cli', '--host', self.ip, 'off'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"Warning: Failed to turn off Kasa device at {self.ip}: {e}")
            return False


def control_kasa_devices(kasa1_ip: Optional[str], kasa2_ip: Optional[str], 
                        turn_on: bool, kasa2_only: bool = False) -> None:
    """
    Control Kasa devices
    
    Args:
        kasa1_ip: IP address of Kasa device 1
        kasa2_ip: IP address of Kasa device 2
        turn_on: True to turn on, False to turn off
        kasa2_only: If True, only control Kasa 2 (used for screen lock)
    """
    action = "on" if turn_on else "off"
    
    if kasa2_only:
        # Only control Kasa 2 (screen lock scenario)
        if kasa2_ip:
            print(f"Turning {action} Kasa 2 ({kasa2_ip})...")
            client = KasaClient(kasa2_ip)
            if turn_on:
                client.turn_on()
            else:
                client.turn_off()
    else:
        # Control both devices (service start/stop scenario)
        if kasa1_ip:
            print(f"Turning {action} Kasa 1 ({kasa1_ip})...")
            client = KasaClient(kasa1_ip)
            if turn_on:
                client.turn_on()
            else:
                client.turn_off()
        
        if kasa2_ip:
            print(f"Turning {action} Kasa 2 ({kasa2_ip})...")
            client = KasaClient(kasa2_ip)
            if turn_on:
                client.turn_on()
            else:
                client.turn_off()
