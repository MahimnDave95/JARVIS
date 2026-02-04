"""
Text parsing utilities for natural language command extraction.
"""

import re
from typing import Optional, Dict, Any, Tuple
from loguru import logger

def normalize_text(text: str) -> str:
    """Normalize text for parsing."""
    return text.lower().strip().rstrip('.!?')

def extract_quoted_text(text: str) -> Optional[str]:
    """Extract text between quotes."""
    patterns = [
        r'"([^"]+)"',
        r"'([^']+)'",
        r'«([^»]+)»',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None

def parse_app_launch(text: str) -> Optional[str]:
    """Parse app launch command."""
    patterns = [
        r'open\s+(.+)',
        r'launch\s+(.+)',
        r'start\s+(.+)',
        r'run\s+(.+)',
    ]
    
    text = normalize_text(text)
    for pattern in patterns:
        match = re.match(pattern, text)
        if match:
            app_name = match.group(1).strip()
            # Remove extra words
            app_name = re.sub(r'\s+(please|now|for me)$', '', app_name)
            return app_name
    return None

def parse_browser_action(text: str) -> Optional[Dict[str, Any]]:
    """Parse browser-related commands."""
    text = normalize_text(text)
    
    # Google search
    search_patterns = [
        r'search\s+(?:google\s+)?for\s+(.+)',
        r'google\s+(.+)',
        r'search\s+(.+)',
        r'look\s+up\s+(.+)',
    ]
    for pattern in search_patterns:
        match = re.match(pattern, text)
        if match:
            return {
                "action": "google_search",
                "query": match.group(1).strip()
            }
    
    # YouTube search
    youtube_patterns = [
        r'(?:open\s+)?youtube\s+(?:for\s+)?(.+)',
        r'search\s+youtube\s+(?:for\s+)?(.+)',
        r'play\s+(.+)\s+on\s+youtube',
    ]
    for pattern in youtube_patterns:
        match = re.match(pattern, text)
        if match:
            return {
                "action": "youtube_search",
                "query": match.group(1).strip()
            }
    
    # Direct URL
    url_patterns = [
        r'(?:open\s+|go\s+to\s+)(https?://\S+)',
        r'(?:open\s+|go\s+to\s+)(www\.\S+)',
    ]
    for pattern in url_patterns:
        match = re.match(pattern, text)
        if match:
            url = match.group(1)
            if not url.startswith('http'):
                url = 'https://' + url
            return {
                "action": "open_url",
                "url": url
            }
    
    return None

def parse_file_operation(text: str) -> Optional[Dict[str, Any]]:
    """Parse file operation commands."""
    text = normalize_text(text)
    
    # Copy files
    copy_patterns = [
        r'copy\s+(?:files?|folder|directory)?\s*(?:from)?\s+(.+?)\s+to\s+(.+)',
        r'copy\s+(.+?)\s+(?:to|into)\s+(.+)',
    ]
    for pattern in copy_patterns:
        match = re.match(pattern, text)
        if match:
            return {
                "action": "copy",
                "source": match.group(1).strip().strip('"\''),
                "destination": match.group(2).strip().strip('"\'')
            }
    
    # Move files
    move_patterns = [
        r'move\s+(?:files?|folder|directory)?\s*(?:from)?\s+(.+?)\s+to\s+(.+)',
        r'move\s+(.+?)\s+(?:to|into)\s+(.+)',
    ]
    for pattern in move_patterns:
        match = re.match(pattern, text)
        if match:
            return {
                "action": "move",
                "source": match.group(1).strip().strip('"\''),
                "destination": match.group(2).strip().strip('"\'')
            }
    
    # Delete
    delete_patterns = [
        r'delete\s+(?:file|folder)?\s*(?:at|in)?\s+(.+)',
        r'remove\s+(?:file|folder)?\s*(?:at|in)?\s+(.+)',
    ]
    for pattern in delete_patterns:
        match = re.match(pattern, text)
        if match:
            return {
                "action": "delete",
                "path": match.group(1).strip().strip('"\'')
            }
    
    return None

def parse_system_command(text: str) -> Optional[Dict[str, Any]]:
    """Parse system control commands."""
    text = normalize_text(text)
    
    # Volume control
    if re.search(r'volume\s+up|increase\s+volume|louder', text):
        return {"action": "volume_up"}
    if re.search(r'volume\s+down|decrease\s+volume|quieter', text):
        return {"action": "volume_down"}
    if re.search(r'mute|silence', text):
        return {"action": "mute"}
    if re.search(r'unmute', text):
        return {"action": "unmute"}
    
    # Screenshot
    if re.search(r'screenshot|screen\s+shot|take\s+a?\s*picture', text):
        return {"action": "screenshot"}
    
    # Shutdown/Restart
    if re.search(r'shut\s*down|turn\s+off|power\s+off', text):
        return {"action": "shutdown"}
    if re.search(r'restart|reboot', text):
        return {"action": "restart"}
    
    return None

def parse_typing_command(text: str) -> Optional[str]:
    """Parse typing commands."""
    text = normalize_text(text)
    
    patterns = [
        r'type\s+["\']?(.+?)["\']?$',
        r'write\s+["\']?(.+?)["\']?$',
        r'enter\s+["\']?(.+?)["\']?$',
        r'input\s+["\']?(.+?)["\']?$',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, text)
        if match:
            return match.group(1).strip()
    
    # Handle "type this: ..." format
    if 'type this' in text or 'type the following' in text:
        parts = text.split(':', 1)
        if len(parts) > 1:
            return parts[1].strip()
    
    return None

def parse_command(text: str) -> Dict[str, Any]:
    """
    Main command parser. Returns structured command info.
    
    Returns dict with:
        - type: 'app_launch', 'browser', 'file', 'system', 'typing', 'chat'
        - data: parsed data specific to command type
        - original: original text
    """
    if not text or not text.strip():
        return {"type": "unknown", "data": None, "original": text}
    
    original = text
    text = normalize_text(text)
    
    # Check for typing first (most specific)
    typing_text = parse_typing_command(original)
    if typing_text:
        return {
            "type": "typing",
            "data": {"text": typing_text},
            "original": original
        }
    
    # Check app launch
    app_name = parse_app_launch(text)
    if app_name:
        return {
            "type": "app_launch",
            "data": {"app_name": app_name},
            "original": original
        }
    
    # Check browser actions
    browser_data = parse_browser_action(text)
    if browser_data:
        return {
            "type": "browser",
            "data": browser_data,
            "original": original
        }
    
    # Check file operations
    file_data = parse_file_operation(text)
    if file_data:
        return {
            "type": "file",
            "data": file_data,
            "original": original
        }
    
    # Check system commands
    system_data = parse_system_command(text)
    if system_data:
        return {
            "type": "system",
            "data": system_data,
            "original": original
        }
    
    # Default to chat
    return {
        "type": "chat",
        "data": {"message": original},
        "original": original
    }