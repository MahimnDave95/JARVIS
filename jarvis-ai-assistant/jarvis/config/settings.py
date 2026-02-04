"""
JARVIS Configuration Settings
Centralized configuration for paths, constants, and feature flags.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = DATA_DIR / "logs"
DB_DIR = DATA_DIR / "db"
CACHE_DIR = DATA_DIR / "cache"

# Ensure directories exist
for dir_path in [DATA_DIR, LOGS_DIR, DB_DIR, CACHE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Database
DATABASE_URL = f"sqlite:///{DB_DIR / 'jarvis.db'}"

# Flask API
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-pro"

# JARVIS Identity
JARVIS_NAME = os.getenv("JARVIS_NAME", "JARVIS")
WAKE_PHRASE = os.getenv("WAKE_PHRASE", "jarvis").lower()

# Feature Flags
ENABLE_REMOTE_TYPING = os.getenv("ENABLE_REMOTE_TYPING", "true").lower() == "true"
ENABLE_FILE_OPERATIONS = os.getenv("ENABLE_FILE_OPERATIONS", "true").lower() == "true"
ENABLE_SYSTEM_SHUTDOWN = os.getenv("ENABLE_SYSTEM_SHUTDOWN", "false").lower() == "true"

# Default paths for operations
DEFAULT_SCREENSHOT_FOLDER = DATA_DIR / "screenshots"
DEFAULT_SCREENSHOT_FOLDER.mkdir(exist_ok=True)

# App mappings for Windows
APP_MAPPINGS = {
    # Browsers
    "chrome": "chrome",
    "google chrome": "chrome",
    "firefox": "firefox",
    "edge": "msedge",
    "microsoft edge": "msedge",
    
    # Code Editors
    "vs code": "code",
    "visual studio code": "code",
    "vscode": "code",
    "notepad": "notepad",
    "notepad++": "notepad++",
    "sublime": "sublime_text",
    
    # System
    "calculator": "calc",
    "paint": "mspaint",
    "explorer": "explorer",
    "file explorer": "explorer",
    "cmd": "cmd",
    "command prompt": "cmd",
    "terminal": "wt",  # Windows Terminal
    "powershell": "powershell",
    
    # Media
    "spotify": "spotify",
    "vlc": "vlc",
    "photos": "ms-photos:",
    
    # Office
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
}

# Buddy personality system prompt
BUDDY_SYSTEM_PROMPT = """You are {jarvis}, a friendly AI assistant with a buddy-like personality. 
You're helpful, slightly informal, and supportive - like a tech-savvy friend who's always ready to help.

Guidelines:
- Use friendly, conversational language
- Occasionally use emojis (🙂, 😅, 🔥) but keep it professional
- Be encouraging and supportive
- If you make a mistake or can't do something, be honest and apologetic
- Keep responses concise but warm
- Use phrases like "buddy", "friend", or "pal" occasionally (but not excessively)

Current context: You're helping control a PC via voice commands. You can open apps, search the web, 
manage files, control system settings, and type text. Always prioritize safety and ask for 
confirmation on destructive actions.

If the user asks something you can't do via system control, offer helpful alternatives or 
explain what you can do instead."""