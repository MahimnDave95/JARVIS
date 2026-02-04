"""
Tests for command router.
"""

import pytest
from unittest.mock import Mock, patch
from jarvis.core.command_router import CommandRouter

class TestCommandRouter:
    
    @pytest.fixture
    def router(self):
        return CommandRouter()
    
    def test_handle_app_launch(self, router):
        with patch.object(router, '_handle_app_launch') as mock_handler:
            mock_handler.return_value = {
                "action": "app_launch",
                "success": True,
                "spoken_response": "Opened!"
            }
            
            result = router.handle_command("open chrome", source="test")
            assert result["action"] == "app_launch"
    
    def test_handle_typing(self, router):
        with patch.object(router, '_handle_typing') as mock_handler:
            mock_handler.return_value = {
                "action": "type_text",
                "success": True,
                "spoken_response": "Typed!"
            }
            
            result = router.handle_command("type 'hello'", source="test")
            assert result["action"] == "type_text"
    
    def test_empty_command(self, router):
        result = router.handle_command("", source="test")
        assert result["success"] is False
    
    def test_command_logging(self, router):
        with patch('jarvis.core.command_router.db_manager') as mock_db:
            with patch.object(router, '_handle_chat'):
                router.handle_command("test command", source="voice")
                mock_db.log_command.assert_called_once()