#!/usr/bin/env python3
"""
JARVIS Personal Assistant - Main Entry Point
Desktop + Mobile voice-controlled assistant with buddy personality.

"""

import sys
import time
import signal
import threading
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jarvis.config.logging_config import setup_logging
from jarvis.config.settings import WAKE_PHRASE, JARVIS_NAME, FLASK_PORT
from jarvis.core.voice_engine import voice_engine
from jarvis.core.command_router import command_router
from jarvis.core.ai_engine import ai_engine
from jarvis.api.flask_server import flask_server
from jarvis.database.db_manager import db_manager

from loguru import logger

class JARVIS:
    """Main JARVIS assistant class."""
    
    def __init__(self):
        self.running = False
        self.use_wake_phrase = False  # Set to True to require wake phrase
        self.flask_enabled = True
        self.voice_enabled = True
        
        # Setup components
        self.voice = voice_engine
        self.router = command_router
        self.ai = ai_engine
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info("Shutdown signal received")
        self.shutdown()
        sys.exit(0)
    
    def start(self):
        """Start JARVIS services."""
        logger.info(f"Starting {JARVIS_NAME}...")
        self.running = True
        
        # Start Flask API server
        if self.flask_enabled:
            flask_server.start()
            logger.info(f"API available at http://localhost:{FLASK_PORT}")
        
        # Greeting
        greeting = self.ai.greet()
        logger.info(f"{JARVIS_NAME}: {greeting}")
        self.voice.speak(greeting, block=False)
        
        # Start voice loop if enabled
        if self.voice_enabled:
            self._voice_loop()
        else:
            # Keep main thread alive
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.shutdown()
    
    def _voice_loop(self):
        """Main voice command loop."""
        logger.info(f"Voice loop started (Wake phrase: '{WAKE_PHRASE}' required: {self.use_wake_phrase})")
        
        while self.running:
            try:
                # Listen for command
                text = self.voice.listen(
                    timeout=None if self.use_wake_phrase else 5.0,
                    use_wake_phrase=self.use_wake_phrase
                )
                
                if text:
                    self._process_command(text)
                
                # Small pause to prevent CPU spinning
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error in voice loop: {e}")
                time.sleep(1)
        
        self.shutdown()
    
    def _process_command(self, text: str):
        """Process a voice command."""
        logger.info(f"Processing: {text}")
        
        # Route command
        result = self.router.handle_command(text, source="voice")
        
        # Speak response
        response = result.get("spoken_response", "Done!")
        if response:
            # Wait for any current speech to finish
            while self.voice.is_speaking():
                time.sleep(0.1)
            
            self.voice.speak(response, block=False)
            
            # Print to console too
            print(f"[{JARVIS_NAME}]: {response}")
    
    def shutdown(self):
        """Graceful shutdown."""
        logger.info("Shutting down...")
        self.running = False
        
        # Stop voice engine
        self.voice.stop()
        
        # Stop Flask
        flask_server.stop()
        
        logger.info("Goodbye!")
        sys.exit(0)

def main():
    """Entry point."""
    # Setup logging first
    setup_logging()
    
    # Create and start JARVIS
    jarvis = JARVIS()
    jarvis.start()

if __name__ == "__main__":
    main()