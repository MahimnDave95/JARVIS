"""
Tests for text parsing utilities.
"""

import pytest
from jarvis.utils.text_parsing import (
    parse_command,
    parse_app_launch,
    parse_browser_action,
    parse_file_operation,
    parse_system_command,
    parse_typing_command,
    extract_quoted_text
)

class TestTextParsing:
    
    def test_parse_app_launch(self):
        assert parse_app_launch("open chrome") == "chrome"
        assert parse_app_launch("launch VS Code") == "vs code"
        assert parse_app_launch("start notepad please") == "notepad"
        assert parse_app_launch("hello world") is None
    
    def test_parse_browser_action(self):
        # Google search
        result = parse_browser_action("search google for python tutorials")
        assert result["action"] == "google_search"
        assert "python tutorials" in result["query"]
        
        # YouTube
        result = parse_browser_action("search youtube for music")
        assert result["action"] == "youtube_search"
        
        # URL
        result = parse_browser_action("open https://example.com")
        assert result["action"] == "open_url"
    
    def test_parse_file_operation(self):
        # Copy
        result = parse_file_operation('copy files from "C:/folder1" to "C:/folder2"')
        assert result["action"] == "copy"
        
        # Move
        result = parse_file_operation("move folder from /src to /dst")
        assert result["action"] == "move"
        
        # Delete
        result = parse_file_operation("delete file at C:/temp.txt")
        assert result["action"] == "delete"
    
    def test_parse_system_command(self):
        assert parse_system_command("volume up")["action"] == "volume_up"
        assert parse_system_command("take a screenshot")["action"] == "screenshot"
        assert parse_system_command("shutdown")["action"] == "shutdown"
    
    def test_parse_typing_command(self):
        assert parse_typing_command("type 'hello world'") == "hello world"
        assert parse_typing_command('write "test message"') == "test message"
        assert parse_typing_command("type this: custom text") == "custom text"
    
    def test_parse_command_integration(self):
        # App launch
        result = parse_command("open chrome")
        assert result["type"] == "app_launch"
        
        # Browser
        result = parse_command("search for python")
        assert result["type"] == "browser"
        
        # System
        result = parse_command("volume up")
        assert result["type"] == "system"
        
        # Typing
        result = parse_command("type 'hello'")
        assert result["type"] == "typing"
        
        # Chat (fallback)
        result = parse_command("how are you today")
        assert result["type"] == "chat"
    
    def test_extract_quoted_text(self):
        assert extract_quoted_text('say "hello"') == "hello"
        assert extract_quoted_text("type 'world'") == "world"
        assert extract_quoted_text("no quotes here") is None