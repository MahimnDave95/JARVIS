"""
Typing controller for remote text input.
Uses pyautogui to type text into the active window.
"""

import pyautogui
from loguru import logger

from jarvis.config.settings import ENABLE_REMOTE_TYPING

class TypingController:
    """Control typing on the PC remotely."""
    
    def __init__(self):
        self.enabled = ENABLE_REMOTE_TYPING
        # Configure pyautogui for safety
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = 0.01  # Small pause between actions
    
    def type_text(self, text: str, interval: float = 0.01) -> tuple[bool, str]:
        """
        Type text into the currently active window.
        
        Args:
            text: Text to type
            interval: Delay between keystrokes
            
        Returns:
            Tuple of (success, message)
        """
        if not self.enabled:
            return False, "Remote typing is disabled in settings. ⚠️"
        
        if not text:
            return False, "No text provided to type."
        
        try:
            # Type the text
            pyautogui.write(text, interval=interval)
            logger.info(f"Typed text ({len(text)} chars)")
            return True, f"Typed {len(text)} characters! ⌨️"
            
        except Exception as e:
            logger.error(f"Typing failed: {e}")
            return False, f"Couldn't type text: {str(e)}"
    
    def press_key(self, key: str) -> tuple[bool, str]:
        """
        Press a specific key.
        
        Args:
            key: Key to press (e.g., 'enter', 'tab', 'ctrl')
            
        Returns:
            Tuple of (success, message)
        """
        if not self.enabled:
            return False, "Remote typing is disabled."
        
        try:
            pyautogui.press(key)
            return True, f"Pressed {key}"
        except Exception as e:
            return False, str(e)
    
    def hotkey(self, *keys: str) -> tuple[bool, str]:
        """
        Press a hotkey combination.
        
        Args:
            *keys: Keys to press together (e.g., 'ctrl', 'c')
            
        Returns:
            Tuple of (success, message)
        """
        if not self.enabled:
            return False, "Remote typing is disabled."
        
        try:
            pyautogui.hotkey(*keys)
            return True, f"Pressed {'+'.join(keys)}"
        except Exception as e:
            return False, str(e)

# Global instance
typing_controller = TypingController()