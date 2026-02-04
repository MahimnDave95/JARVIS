"""
Application launcher for opening programs on Windows.
"""

import os
import platform
import subprocess
from typing import Optional
from pathlib import Path
from loguru import logger

from jarvis.config.settings import APP_MAPPINGS

class AppLauncher:
    """Launch applications on the system."""
    
    def __init__(self):
        self.system = platform.system()
        self._verify_platform()
    
    def _verify_platform(self):
        """Verify we're on a supported platform."""
        if self.system != "Windows":
            logger.warning(f"AppLauncher optimized for Windows, running on {self.system}")
    
    def open_app(self, name: str) -> tuple[bool, str]:
        """
        Open an application by name.
        
        Args:
            name: Friendly name of the app (e.g., 'chrome', 'vs code')
            
        Returns:
            Tuple of (success, message)
        """
        name_lower = name.lower().strip()
        
        # Check direct mapping
        if name_lower in APP_MAPPINGS:
            executable = APP_MAPPINGS[name_lower]
            return self._launch(executable, name)
        
        # Try to find partial match
        for key, executable in APP_MAPPINGS.items():
            if name_lower in key or key in name_lower:
                return self._launch(executable, name)
        
        # Try as-is (might be in PATH)
        return self._launch(name, name)
    
    def _launch(self, executable: str, friendly_name: str) -> tuple[bool, str]:
        """Launch the executable."""
        try:
            if self.system == "Windows":
                # Use start command on Windows to avoid blocking
                # Handle Windows Store apps (ms- prefix) and URLs differently
                if executable.startswith(('ms-', 'microsoft.')):
                    subprocess.Popen(
                        f'start {executable}', 
                        shell=True, 
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                else:
                    subprocess.Popen(
                        f'start "" "{executable}"', 
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
            else:
                # Linux/Mac - try generic opener
                subprocess.Popen(
                    ["xdg-open" if self.system == "Linux" else "open", executable],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            logger.info(f"Launched: {friendly_name} ({executable})")
            return True, f"{friendly_name} is opening up!"
            
        except Exception as e:
            logger.error(f"Failed to launch {executable}: {e}")
            return False, f"Couldn't open {friendly_name}. Is it installed?"
    
    def is_app_available(self, name: str) -> bool:
        """Check if an app is available/installed."""
        name_lower = name.lower()
        
        # Check if in mappings
        if name_lower in APP_MAPPINGS:
            return True
        
        # Check if in PATH
        try:
            result = subprocess.run(
                ["where" if self.system == "Windows" else "which", name],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False

# Global instance
app_launcher = AppLauncher()