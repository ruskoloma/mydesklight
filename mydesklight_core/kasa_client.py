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
    
    def _send_command(self, command: str, retries: int = 3) -> bool:
        """
        Send command to Kasa device with retries
        
        Args:
            command: Command to send ('on' or 'off')
            retries: Number of times to send command (default 3)
        
        Returns:
            True if at least one attempt succeeded, False otherwise
        """
        import time
        
        success = False
        for attempt in range(retries):
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'kasa.cli', '--host', self.ip, command],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    success = True
                
                # Small delay between retries
                if attempt < retries - 1:
                    time.sleep(0.1)
                    
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                if attempt == retries - 1:  # Only print on last attempt
                    print(f"Warning: Failed to {command} Kasa device at {self.ip}: {e}")
        
        return success
    
    def turn_on(self) -> bool:
        """
        Turn on Kasa device (sends command 3 times for reliability)
        
        Returns:
            True if successful, False otherwise
        """
        return self._send_command('on')
    
    def turn_off(self) -> bool:
        """
        Turn off Kasa device (sends command 3 times for reliability)
        
        Returns:
            True if successful, False otherwise
        """
        return self._send_command('off')


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
