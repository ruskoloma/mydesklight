"""
UDP client for Govee device communication
"""

import json
import socket
import time
from typing import Tuple


class GoveeUDPClient:
    """Handles UDP communication with Govee devices"""
    
    def __init__(self, ip: str, port: int = 4003):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def send_command(self, command: dict, repeat: int = 3, delay_ms: int = 10) -> None:
        """
        Send UDP command to Govee device
        
        Args:
            command: Command dictionary to send
            repeat: Number of times to send (for reliability)
            delay_ms: Delay between sends in milliseconds
        """
        try:
            json_data = json.dumps(command).encode('utf-8')
            
            for i in range(repeat):
                self.sock.sendto(json_data, (self.ip, self.port))
                if i < repeat - 1:
                    time.sleep(delay_ms / 1000.0)
        except Exception as e:
            print(f"Error sending UDP command: {e}")
    
    def set_color(self, r: int, g: int, b: int, temp_kelvin: int = 0) -> None:
        """Set Govee device color"""
        command = {
            "msg": {
                "cmd": "colorwc",
                "data": {
                    "color": {"r": r, "g": g, "b": b},
                    "colorTemInKelvin": temp_kelvin
                }
            }
        }
        self.send_command(command)
    
    def turn_off(self) -> None:
        """Turn off Govee device"""
        command = {
            "msg": {
                "cmd": "turn",
                "data": {
                    "value": 0
                }
            }
        }
        self.send_command(command)
    
    def turn_on(self) -> None:
        """Turn on Govee device"""
        command = {
            "msg": {
                "cmd": "turn",
                "data": {
                    "value": 1
                }
            }
        }
        self.send_command(command)
    
    def close(self) -> None:
        """Close UDP socket"""
        self.sock.close()


# Color presets
ENGLISH_COLOR = (255, 180, 110)  # Warm orange
OTHER_COLOR = (120, 180, 255)    # Blue


def get_color_for_layout(layout: str) -> Tuple[int, int, int]:
    """
    Get RGB color for keyboard layout
    
    Args:
        layout: Keyboard layout identifier (e.g., "ABC", "Russian", "Ukrainian")
    
    Returns:
        RGB tuple (r, g, b)
    """
    # English layouts
    if layout.upper() in ['ABC', 'US', 'EN', 'ENGLISH']:
        return ENGLISH_COLOR
    else:
        return OTHER_COLOR
