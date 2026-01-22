"""
Configuration management for mydesklight
"""

import json
import os
from pathlib import Path
from typing import Optional


class Config:
    """Manages mydesklight configuration"""
    
    def __init__(self):
        # Platform-specific config locations
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ.get('APPDATA', '')) / 'mydesklight'
        else:  # macOS and Linux
            config_dir = Path.home() / '.config' / 'mydesklight'
        
        self.config_dir = config_dir
        self.config_file = config_dir / 'config.json'
        self.pid_file = config_dir / 'service.pid'
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> dict:
        """Load configuration from file"""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _save_config(self, config: dict) -> None:
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_govee_ip(self) -> Optional[str]:
        """Get configured Govee device IP address"""
        config = self._load_config()
        return config.get('govee_ip')
    
    def set_govee_ip(self, ip: str) -> None:
        """Set Govee device IP address"""
        config = self._load_config()
        config['govee_ip'] = ip
        self._save_config(config)
    
    def get_kasa1_ip(self) -> Optional[str]:
        """Get Kasa device 1 IP address"""
        config = self._load_config()
        return config.get('kasa1_ip')
    
    def set_kasa1_ip(self, ip: str) -> None:
        """Set Kasa device 1 IP address"""
        config = self._load_config()
        config['kasa1_ip'] = ip
        self._save_config(config)
    
    def get_kasa2_ip(self) -> Optional[str]:
        """Get Kasa device 2 IP address"""
        config = self._load_config()
        return config.get('kasa2_ip')
    
    def set_kasa2_ip(self, ip: str) -> None:
        """Set Kasa device 2 IP address"""
        config = self._load_config()
        config['kasa2_ip'] = ip
        self._save_config(config)
    
    def get_all_config(self) -> dict:
        """Get all configuration"""
        return self._load_config()
    
    def get_config_path(self) -> Path:
        """Get path to config file"""
        return self.config_file
    
    def is_service_running(self) -> bool:
        """Check if service is currently running"""
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is actually running
            if os.name == 'nt':  # Windows
                import subprocess
                result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                      capture_output=True, text=True)
                return str(pid) in result.stdout
            else:  # macOS and Linux
                try:
                    os.kill(pid, 0)  # Signal 0 just checks if process exists
                    return True
                except OSError:
                    return False
        except (ValueError, IOError):
            return False
    
    def save_pid(self, pid: int) -> None:
        """Save service process ID"""
        with open(self.pid_file, 'w') as f:
            f.write(str(pid))
    
    def remove_pid(self) -> None:
        """Remove PID file"""
        if self.pid_file.exists():
            self.pid_file.unlink()
    
    def get_pid(self) -> Optional[int]:
        """Get saved service PID"""
        if not self.pid_file.exists():
            return None
        
        try:
            with open(self.pid_file, 'r') as f:
                return int(f.read().strip())
        except (ValueError, IOError):
            return None
