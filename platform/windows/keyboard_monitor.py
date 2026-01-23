"""
mydesklight - Windows Keyboard Monitor (Pure Python)
Monitors keyboard layout changes and sends UDP commands to Govee devices
"""

import sys
import time
import ctypes
import ctypes.wintypes
from pathlib import Path
import threading

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mydesklight_core.udp_client import GoveeUDPClient, get_color_for_layout, ENGLISH_COLOR, OTHER_COLOR
from mydesklight_core.config import Config
from mydesklight_core.kasa_client import control_kasa_devices

# Windows API constants
WM_INPUTLANGCHANGE = 0x0051
WTS_SESSION_LOCK = 0x7
WTS_SESSION_UNLOCK = 0x8

# Load Windows DLLs
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

class WindowsKeyboardMonitor:
    """Windows keyboard layout monitor using Python and ctypes"""
    
    def __init__(self, govee_ip: str, kasa1_ip: str = None, kasa2_ip: str = None):
        self.govee_ip = govee_ip
        self.kasa1_ip = kasa1_ip
        self.kasa2_ip = kasa2_ip
        self.client = GoveeUDPClient(govee_ip)
        self.current_layout = None
        self.is_screen_locked = False
        self.running = True
        self.keepalive_thread = None
        
    def get_current_layout(self):
        """Get current keyboard layout name"""
        # Get keyboard layout for current thread
        thread_id = kernel32.GetCurrentThreadId()
        hkl = user32.GetKeyboardLayout(thread_id)
        
        # Extract language ID
        lang_id = hkl & 0xFFFF
        
        # Get language name
        buf = ctypes.create_unicode_buffer(256)
        ctypes.windll.kernel32.GetLocaleInfoW(
            lang_id,
            0x00000002,  # LOCALE_SENGLANGUAGE
            buf,
            256
        )
        
        return buf.value
    
    def send_color_for_layout(self, layout: str, is_keepalive: bool = False):
        """Send color command based on layout"""
        r, g, b = get_color_for_layout(layout)
        
        if not is_keepalive:
            layout_type = "English" if layout.lower() in ['english', 'us', 'abc'] else "Other"
            print(f"{layout_type} layout -> RGB({r}, {g}, {b})")
        
        self.client.set_color(r, g, b)
    
    def keepalive_worker(self):
        """Keepalive thread - sends current color every 20 seconds"""
        while self.running:
            time.sleep(20)
            if self.running and not self.is_screen_locked and self.current_layout:
                print(f"Keepalive: sending current layout ({self.current_layout})")
                self.send_color_for_layout(self.current_layout, is_keepalive=True)
    
    def on_screen_lock(self):
        """Handle screen lock event"""
        print("Screen locked - turning off lamps")
        self.is_screen_locked = True
        self.client.turn_off()
        
        # Turn off only Kasa 2
        if self.kasa2_ip:
            control_kasa_devices(None, self.kasa2_ip, turn_on=False, kasa2_only=True)
    
    def on_screen_unlock(self):
        """Handle screen unlock event"""
        print("Screen unlocked - restoring lamp color")
        self.is_screen_locked = False
        
        # Restore current layout color
        if self.current_layout:
            self.send_color_for_layout(self.current_layout)
        
        # Turn on Kasa devices
        if self.kasa1_ip or self.kasa2_ip:
            control_kasa_devices(self.kasa1_ip, self.kasa2_ip, turn_on=True, kasa2_only=False)
    
    def monitor_layout_polling(self):
        """Monitor keyboard layout changes by polling (fallback method)"""
        print("Using polling method (checking every 2 seconds)")
        print("Subscribed to keyboard layout events")
        
        while self.running:
            try:
                layout = self.get_current_layout()
                
                if layout != self.current_layout:
                    if self.current_layout:
                        print(f"Layout changed: {self.current_layout} -> {layout}")
                    else:
                        print(f"Current layout: {layout}")
                    
                    self.current_layout = layout
                    
                    if not self.is_screen_locked:
                        self.send_color_for_layout(layout)
                
                time.sleep(2)  # Poll every 2 seconds
                
            except Exception as e:
                print(f"Error in layout monitoring: {e}")
                time.sleep(2)
    
    def start(self):
        """Start monitoring"""
        print("mydesklight - Windows Keyboard Monitor (Python)")
        print("=" * 45)
        print(f"Govee IP: {self.govee_ip}")
        if self.kasa1_ip:
            print(f"Kasa 1 IP: {self.kasa1_ip}")
        if self.kasa2_ip:
            print(f"Kasa 2 IP: {self.kasa2_ip}")
        print()
        
        # Turn on Kasa devices at startup
        if self.kasa1_ip or self.kasa2_ip:
            control_kasa_devices(self.kasa1_ip, self.kasa2_ip, turn_on=True, kasa2_only=False)
        
        # Get initial layout and send color
        self.current_layout = self.get_current_layout()
        print(f"Current layout: {self.current_layout}")
        self.send_color_for_layout(self.current_layout)
        
        # Start keepalive thread
        self.keepalive_thread = threading.Thread(target=self.keepalive_worker, daemon=True)
        self.keepalive_thread.start()
        print("Keepalive timer started (every 20 sec)")
        
        # Monitor layout changes
        try:
            self.monitor_layout_polling()
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.stop()
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        self.client.close()


def main():
    """Main entry point"""
    # Load configuration
    config = Config()
    govee_ip = config.get_govee_ip()
    
    if not govee_ip:
        print("Error: Govee IP not configured")
        print("Run: python mydesklight configure")
        sys.exit(1)
    
    kasa1_ip = config.get_kasa1_ip()
    kasa2_ip = config.get_kasa2_ip()
    
    # Start monitor
    monitor = WindowsKeyboardMonitor(govee_ip, kasa1_ip, kasa2_ip)
    monitor.start()


if __name__ == '__main__':
    main()
