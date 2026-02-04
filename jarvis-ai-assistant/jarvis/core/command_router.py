"""
Command Router - the brain that decides what to do with user input.
Parses commands and routes to appropriate handlers.
"""

from typing import Dict, Any, Optional
from loguru import logger

from jarvis.utils.text_parsing import parse_command
from jarvis.core.ai_engine import ai_engine
from jarvis.automation.app_launcher import app_launcher
from jarvis.automation.browser_control import browser_control
from jarvis.automation.system_control import system_control
from jarvis.automation.file_manager import file_manager
from jarvis.remote.typing_controller import typing_controller
from jarvis.database.db_manager import db_manager

class CommandRouter:
    """
    Routes parsed commands to appropriate handlers.
    Central hub for all command processing.
    """
    
    def __init__(self):
        self.ai = ai_engine
        self.pending_confirmations = {}  # Store pending destructive actions
    
    def handle_command(self, text: str, source: str = "voice") -> Dict[str, Any]:
        """
        Main entry point for processing commands.
        
        Args:
            text: Raw command text
            source: 'voice', 'phone', or 'api'
            
        Returns:
            Dict with action results and response
        """
        if not text or not text.strip():
            return self._error_response("No command provided")
        
        text = text.strip()
        logger.info(f"Processing command from {source}: {text[:50]}...")
        
        # Parse the command
        parsed = parse_command(text)
        command_type = parsed["type"]
        data = parsed["data"]
        
        # Route to handler
        result = None
        
        try:
            if command_type == "app_launch":
                result = self._handle_app_launch(data)
            elif command_type == "browser":
                result = self._handle_browser(data)
            elif command_type == "system":
                result = self._handle_system(data, text)
            elif command_type == "file":
                result = self._handle_file(data, text)
            elif command_type == "typing":
                result = self._handle_typing(data)
            elif command_type == "chat":
                result = self._handle_chat(data)
            else:
                result = self._handle_unknown(text)
            
            # Log the command
            db_manager.log_command(
                source=source,
                raw_text=text,
                action_type=command_type,
                success=result.get("success", False),
                error_message=result.get("error"),
                response_text=result.get("spoken_response")
            )
            
            return result
            
        except Exception as e:
            logger.exception("Command handling failed")
            error_result = self._error_response(str(e))
            
            db_manager.log_command(
                source=source,
                raw_text=text,
                action_type=command_type,
                success=False,
                error_message=str(e),
                response_text=error_result.get("spoken_response")
            )
            
            return error_result
    
    def _handle_app_launch(self, data: Dict) -> Dict[str, Any]:
        """Handle app launch command."""
        app_name = data["app_name"]
        success, message = app_launcher.open_app(app_name)
        
        response = self.ai.generate_command_response(
            f"open {app_name}", success, message
        ) if success else message
        
        return {
            "action": "app_launch",
            "success": success,
            "app_name": app_name,
            "spoken_response": response,
            "details": {"message": message}
        }
    
    def _handle_browser(self, data: Dict) -> Dict[str, Any]:
        """Handle browser commands."""
        action = data["action"]
        success, message = False, ""
        
        if action == "open_url":
            success, message = browser_control.open_url(data["url"])
        elif action == "google_search":
            success, message = browser_control.google_search(data["query"])
        elif action == "youtube_search":
            success, message = browser_control.open_youtube_search(data["query"])
        
        return {
            "action": f"browser_{action}",
            "success": success,
            "spoken_response": message,
            "details": data
        }
    
    def _handle_system(self, data: Dict, raw_text: str) -> Dict[str, Any]:
        """Handle system control commands."""
        action = data["action"]
        success, message = False, ""
        
        # Check for cancellation first
        if "cancel" in raw_text.lower() and "shutdown" in raw_text.lower():
            success, message = system_control.cancel_shutdown()
            return {
                "action": "system_cancel_shutdown",
                "success": success,
                "spoken_response": message
            }
        
        if action == "volume_up":
            success, message = system_control.volume_up()
        elif action == "volume_down":
            success, message = system_control.volume_down()
        elif action == "mute":
            success, message = system_control.mute()
        elif action == "unmute":
            success, message = system_control.unmute()
        elif action == "screenshot":
            success, message = system_control.screenshot()
        elif action == "shutdown":
            # Require explicit confirmation
            if "confirm" in raw_text.lower():
                success, message = system_control.shutdown(confirm=True)
            else:
                return {
                    "action": "system_shutdown",
                    "success": False,
                    "spoken_response": "Shutdown requires confirmation. Say 'confirm shutdown' to proceed. ⚠️",
                    "requires_confirmation": True
                }
        elif action == "restart":
            if "confirm" in raw_text.lower():
                success, message = system_control.restart(confirm=True)
            else:
                return {
                    "action": "system_restart",
                    "success": False,
                    "spoken_response": "Restart requires confirmation. Say 'confirm restart' to proceed. ⚠️",
                    "requires_confirmation": True
                }
        
        return {
            "action": f"system_{action}",
            "success": success,
            "spoken_response": message
        }
    
    def _handle_file(self, data: Dict, raw_text: str) -> Dict[str, Any]:
        """Handle file operations."""
        action = data["action"]
        success, message = False, ""
        
        # Check for confirmation on destructive operations
        needs_confirm = action == "delete"
        has_confirm = "confirm" in raw_text.lower()
        
        if needs_confirm and not has_confirm:
            # Store pending action
            self.pending_confirmations["last_file_op"] = data
            return {
                "action": f"file_{action}",
                "success": False,
                "spoken_response": f"Delete operation requires confirmation. Say 'confirm delete' to proceed. 🛡️",
                "requires_confirmation": True
            }
        
        if action == "copy":
            success, message = file_manager.copy_files(data["source"], data["destination"])
        elif action == "move":
            success, message = file_manager.move_files(data["source"], data["destination"])
        elif action == "delete":
            success, message = file_manager.delete_path(data["path"], confirm=True)
        
        response = message
        if success:
            response = self.ai.generate_command_response(
                f"{action} files", True, message
            )
        
        return {
            "action": f"file_{action}",
            "success": success,
            "spoken_response": response,
            "details": data
        }
    
    def _handle_typing(self, data: Dict) -> Dict[str, Any]:
        """Handle typing commands."""
        text = data["text"]
        success, message = typing_controller.type_text(text)
        
        return {
            "action": "type_text",
            "success": success,
            "spoken_response": message if not success else f"Typed that for you! ⌨️",
            "characters_typed": len(text)
        }
    
    def _handle_chat(self, data: Dict) -> Dict[str, Any]:
        """Handle general chat - pass to AI."""
        message = data["message"]
        response = self.ai.generate_reply(message)
        
        return {
            "action": "chat",
            "success": True,
            "spoken_response": response,
            "is_chat": True
        }
    
    def _handle_unknown(self, text: str) -> Dict[str, Any]:
        """Handle unrecognized commands."""
        response = self.ai.generate_reply(
            f"I don't know how to handle this command: '{text}'. "
            f"Can you help me understand what you'd like me to do?"
        )
        
        return {
            "action": "unknown",
            "success": False,
            "spoken_response": response,
            "error": "Unknown command type"
        }
    
    def _error_response(self, error: str) -> Dict[str, Any]:
        """Generate error response."""
        return {
            "action": "error",
            "success": False,
            "spoken_response": self.ai.explain_error(error),
            "error": error
        }

# Global instance
command_router = CommandRouter()