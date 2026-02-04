"""
System control for volume, screenshots, shutdown, etc.
"""

from ctypes import POINTER
import os
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Tuple, cast
import pyautogui
from loguru import logger

from jarvis.config.settings import DEFAULT_SCREENSHOT_FOLDER, ENABLE_SYSTEM_SHUTDOWN

class SystemControl:
    """Control system-level operations."""
    
    def __init__(self):
        self.system = platform.system()
        self._init_volume_control()
    
    def _init_volume_control(self):
        """Initialize volume control based on platform."""
        self.volume_available = False
        
        if self.system == "Windows":
            try:
                # Try to import Windows-specific modules
                import ctypes
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                self.volume_available = True
                self._volume_lib = True
            except ImportError:
                logger.warning("pycaw not installed, volume control limited")
                self._volume_lib = False
    
    def volume_up(self, step: int = 10) -> Tuple[bool, str]:
        """Increase system volume."""
        if self.system != "Windows":
            return False, "Volume control only available on Windows currently"
        
        try:
            if self._volume_lib:
                self._set_windows_volume_relative(step)
            else:
                # Fallback: media key
                pyautogui.press('volumeup', presses=step//10)
            
            logger.info(f"Volume increased by {step}%")
            return True, f"Volume up! 🔊"
        except Exception as e:
            logger.error(f"Volume up failed: {e}")
            return False, "Couldn't adjust volume. 😅"
    
    def volume_down(self, step: int = 10) -> Tuple[bool, str]:
        """Decrease system volume."""
        if self.system != "Windows":
            return False, "Volume control only available on Windows currently"
        
        try:
            if self._volume_lib:
                self._set_windows_volume_relative(-step)
            else:
                pyautogui.press('volumedown', presses=step//10)
            
            logger.info(f"Volume decreased by {step}%")
            return True, f"Volume down! 🔉"
        except Exception as e:
            logger.error(f"Volume down failed: {e}")
            return False, "Couldn't adjust volume. 😅"
    
    def _set_windows_volume_relative(self, change: int):
        """Adjust Windows volume relatively."""
        try:
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume)) # type: ignore
            
            current = volume.GetMasterVolumeLevelScalar()
            new_vol = max(0.0, min(1.0, current + (change / 100)))
            volume.SetMasterVolumeLevelScalar(new_vol, None)
        except Exception as e:
            logger.error(f"Windows volume control error: {e}")
            raise
    
    def mute(self) -> Tuple[bool, str]:
        """Mute system."""
        try:
            pyautogui.press('volumemute')
            return True, "Muted! 🔇"
        except Exception as e:
            return False, str(e)
    
    def unmute(self) -> Tuple[bool, str]:
        """Unmute system (same key usually toggles)."""
        return self.mute()  # Toggle
    
    def screenshot(self, filename: str = None) -> Tuple[bool, str]:
        """
        Take a screenshot and save it.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            filepath = DEFAULT_SCREENSHOT_FOLDER / filename
            
            screenshot = pyautogui.screenshot()
            screenshot.save(str(filepath))
            
            logger.info(f"Screenshot saved: {filepath}")
            return True, f"Screenshot saved! 📸 Check {filepath.name}"
            
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return False, "Couldn't take screenshot. 😅"
    
    def shutdown(self, confirm: bool = True) -> Tuple[bool, str]:
        """
        Shutdown the system.
        
        WARNING: Requires confirmation and ENABLE_SYSTEM_SHUTDOWN flag.
        """
        if not ENABLE_SYSTEM_SHUTDOWN:
            return False, "Shutdown is disabled in settings for safety. ⚠️"
        
        if not confirm:
            return False, "Safety first! Please confirm shutdown. 🛡️"
        
        try:
            if self.system == "Windows":
                subprocess.run(["shutdown", "/s", "/t", "60", "/c", "JARVIS shutdown initiated"], check=True)
            else:
                subprocess.run(["shutdown", "-h", "+1"], check=True)
            
            logger.warning("System shutdown initiated")
            return True, "Shutting down in 60 seconds. Say 'cancel shutdown' to stop! ⏰"
        except Exception as e:
            logger.error(f"Shutdown failed: {e}")
            return False, "Couldn't initiate shutdown."
    
    def restart(self, confirm: bool = True) -> Tuple[bool, str]:
        """Restart the system."""
        if not ENABLE_SYSTEM_SHUTDOWN:
            return False, "Restart is disabled in settings for safety. ⚠️"
        
        if not confirm:
            return False, "Safety first! Please confirm restart. 🛡️"
        
        try:
            if self.system == "Windows":
                subprocess.run(["shutdown", "/r", "/t", "60"], check=True)
            else:
                subprocess.run(["shutdown", "-r", "+1"], check=True)
            
            logger.warning("System restart initiated")
            return True, "Restarting in 60 seconds. Save your work! 🔄"
        except Exception as e:
            logger.error(f"Restart failed: {e}")
            return False, "Couldn't initiate restart."
    
    def cancel_shutdown(self) -> Tuple[bool, str]:
        """Cancel pending shutdown/restart."""
        try:
            if self.system == "Windows":
                subprocess.run(["shutdown", "/a"], check=True)
            else:
                # Linux - kill shutdown processes
                subprocess.run(["pkill", "-f", "shutdown"], check=False)
            
            return True, "Shutdown cancelled! Crisis averted. 😅"
        except Exception as e:
            return False, "No shutdown to cancel, or failed to cancel."

# Global instance
system_control = SystemControl()