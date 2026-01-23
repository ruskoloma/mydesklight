"""
Service management for mydesklight
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from .config import Config
from .udp_client import GoveeUDPClient
from .kasa_client import control_kasa_devices


class ServiceManager:
    """Manages the mydesklight background service"""
    
    def __init__(self):
        self.config = Config()
    
    def start(self) -> bool:
        """
        Start the monitoring service
        
        Returns:
            True if started successfully, False otherwise
        """
        # Check if already running
        if self.config.is_service_running():
            print("Service is already running")
            return False
        
        # Check if Govee IP is configured
        govee_ip = self.config.get_govee_ip()
        if not govee_ip:
            print("Error: Govee IP not configured. Run 'mydesklight configure' first.")
            return False
        
        # Turn on Kasa devices (both 1 and 2)
        kasa1_ip = self.config.get_kasa1_ip()
        kasa2_ip = self.config.get_kasa2_ip()
        if kasa1_ip or kasa2_ip:
            control_kasa_devices(kasa1_ip, kasa2_ip, turn_on=True, kasa2_only=False)
        
        # Determine platform and start appropriate monitor
        platform = sys.platform
        
        if platform == 'darwin':  # macOS
            return self._start_macos(govee_ip)
        elif platform == 'win32':  # Windows
            return self._start_windows(govee_ip)
        elif platform.startswith('linux'):  # Linux
            return self._start_linux(govee_ip)
        else:
            print(f"Error: Unsupported platform '{platform}'")
            return False
    
    def stop(self) -> bool:
        """
        Stop the monitoring service and turn off lights
        
        Returns:
            True if stopped successfully, False otherwise
        """
        # Check if service is running
        if not self.config.is_service_running():
            print("Service is not running")
            return False
        
        pid = self.config.get_pid()
        if pid is None:
            print("Error: Could not find service PID")
            return False
        
        # Turn off Govee lights
        govee_ip = self.config.get_govee_ip()
        if govee_ip:
            print("Turning off Govee lights...")
            client = GoveeUDPClient(govee_ip)
            client.turn_off()
            client.close()
        
        # Turn off only Kasa 2 (Kasa 1 stays on)
        kasa2_ip = self.config.get_kasa2_ip()
        if kasa2_ip:
            control_kasa_devices(None, kasa2_ip, turn_on=False, kasa2_only=True)
        
        # Kill the process
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                             capture_output=True)
            else:  # macOS and Linux
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.5)
                # Force kill if still running
                if self.config.is_service_running():
                    os.kill(pid, signal.SIGKILL)
            
            self.config.remove_pid()
            print("Service stopped")
            return True
        except Exception as e:
            print(f"Error stopping service: {e}")
            return False
    
    def status(self) -> None:
        """Print service status"""
        if self.config.is_service_running():
            pid = self.config.get_pid()
            print(f"Service is running (PID: {pid})")
        else:
            print("Service is not running")
        
        # Show all configured devices
        config = self.config.get_all_config()
        govee_ip = config.get('govee_ip')
        kasa1_ip = config.get('kasa1_ip')
        kasa2_ip = config.get('kasa2_ip')
        
        print("\nConfigured devices:")
        if govee_ip:
            print(f"  Govee: {govee_ip}")
        else:
            print("  Govee: Not configured")
        
        if kasa1_ip:
            print(f"  Kasa 1: {kasa1_ip}")
        else:
            print(f"  Kasa 1: Not configured")
        
        if kasa2_ip:
            print(f"  Kasa 2: {kasa2_ip}")
        else:
            print(f"  Kasa 2: Not configured")
    
    def _start_macos(self, govee_ip: str) -> bool:
        """Start macOS monitor"""
        # Find the monitor binary
        project_dir = Path(__file__).parent.parent
        monitor_path = project_dir / 'platform' / 'macos' / 'KeyboardMonitor'
        
        if not monitor_path.exists():
            print(f"Error: Monitor binary not found at {monitor_path}")
            print("Please compile it first: cd platform/macos && ./build.sh")
            return False
        
        # Start the monitor in background
        try:
            process = subprocess.Popen(
                [str(monitor_path), govee_ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            # Save PID
            self.config.save_pid(process.pid)
            print(f"Service started (PID: {process.pid})")
            return True
        except Exception as e:
            print(f"Error starting service: {e}")
            return False
    
    def _start_windows(self, govee_ip: str) -> bool:
        """Start Windows monitor (Python version - no compilation needed)"""
        project_dir = Path(__file__).parent.parent
        monitor_path = project_dir / 'platform' / 'windows' / 'keyboard_monitor.py'
        
        if not monitor_path.exists():
            print(f"Error: Monitor script not found at {monitor_path}")
            return False
        
        try:
            # Start Python monitor in background
            DETACHED_PROCESS = 0x00000008
            CREATE_NO_WINDOW = 0x08000000
            
            process = subprocess.Popen(
                [sys.executable, str(monitor_path)],
                creationflags=DETACHED_PROCESS | CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            self.config.save_pid(process.pid)
            print(f"Service started (PID: {process.pid})")
            return True
        except Exception as e:
            print(f"Error starting service: {e}")
            return False
    
    def _start_linux(self, govee_ip: str) -> bool:
        """Start Linux monitor"""
        project_dir = Path(__file__).parent.parent
        monitor_path = project_dir / 'platform' / 'linux' / 'keyboard_monitor'
        
        if not monitor_path.exists():
            print(f"Error: Monitor binary not found at {monitor_path}")
            print("Please compile it first: cd platform/linux && ./build.sh")
            return False
        
        try:
            process = subprocess.Popen(
                [str(monitor_path), govee_ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            self.config.save_pid(process.pid)
            print(f"Service started (PID: {process.pid})")
            return True
        except Exception as e:
            print(f"Error starting service: {e}")
            return False
