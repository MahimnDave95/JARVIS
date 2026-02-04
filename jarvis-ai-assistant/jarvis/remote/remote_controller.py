"""
Remote controller - shared logic for handling remote commands.
Acts as bridge between API and command router.
"""

from typing import Dict, Any
from loguru import logger

from jarvis.core.command_router import command_router
from jarvis.remote.typing_controller import typing_controller

class RemoteController:
    """
    Handle commands coming from remote sources (phone API).
    Wraps command router with remote-specific logic.
    """
    
    def __init__(self):
        self.typing_controller = typing_controller
    
    def handle_remote_command(self, command_text: str) -> Dict[str, Any]:
        """
        Handle a command from remote source.
        
        Args:
            command_text: Command string from remote device
            
        Returns:
            Response dict with status and message
        """
        logger.info(f"Remote command received: {command_text}")
        
        # Use the same router as voice commands
        result = command_router.handle_command(command_text, source="phone")
        
        return {
            "success": result.get("success", False),
            "action": result.get("action", "unknown"),
            "message": result.get("spoken_response", "Done!"),
            "details": result.get("details", {})
        }
    
    def handle_type_command(self, text: str) -> Dict[str, Any]:
        """
        Handle a typing command from remote.
        
        Args:
            text: Text to type on PC
            
        Returns:
            Response dict
        """
        logger.info(f"Remote type command: {text[:50]}...")
        
        success, message = self.typing_controller.type_text(text)
        
        return {
            "success": success,
            "action": "type_text",
            "message": message,
            "characters_typed": len(text) if success else 0
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status for remote client."""
        from jarvis.database.db_manager import db_manager
        
        stats = db_manager.get_command_stats()
        
        return {
            "status": "online",
            "jarvis_name": "JARVIS",
            "version": "1.0.0",
            "features": {
                "typing": True,
                "file_operations": True,
                "system_control": True
            },
            "stats": stats
        }

# Global instance
remote_controller = RemoteController()