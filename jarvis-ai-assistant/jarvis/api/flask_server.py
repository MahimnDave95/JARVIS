"""
Flask REST API server for remote control from Android app.
"""

import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from loguru import logger

from jarvis.config.settings import FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from jarvis.remote.remote_controller import remote_controller
from jarvis.core.ai_engine import ai_engine

def create_app() -> Flask:
    """Create and configure Flask app."""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for mobile app
    
    @app.route('/status', methods=['GET'])
    def status():
        """Get JARVIS status."""
        return jsonify(remote_controller.get_status())
    
    @app.route('/command', methods=['POST'])
    def command():
        """Receive command from remote device."""
        try:
            data = request.get_json()
            if not data or 'command' not in data:
                return jsonify({
                    "success": False,
                    "error": "Missing 'command' field"
                }), 400
            
            command_text = data['command']
            result = remote_controller.handle_remote_command(command_text)
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"API error in /command: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/type', methods=['POST'])
    def type_text():
        """Receive text to type on PC."""
        try:
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({
                    "success": False,
                    "error": "Missing 'text' field"
                }), 400
            
            text = data['text']
            result = remote_controller.handle_type_command(text)
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"API error in /type: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/ask', methods=['POST'])
    def ask():
        """Direct AI chat endpoint."""
        try:
            data = request.get_json()
            if not data or 'message' not in data:
                return jsonify({
                    "success": False,
                    "error": "Missing 'message' field"
                }), 400
            
            message = data['message']
            response = ai_engine.generate_reply(message)
            
            return jsonify({
                "success": True,
                "response": response,
                "action": "chat"
            })
            
        except Exception as e:
            logger.error(f"API error in /ask: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "success": False,
            "error": "Endpoint not found"
        }), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500
    
    return app

class FlaskServer:
    """Wrapper to run Flask in a background thread."""
    
    def __init__(self):
        self.app = create_app()
        self.thread = None
        self.running = False
    
    def start(self, host: str = None, port: int = None, debug: bool = None):
        """Start Flask server in background thread."""
        host = host or FLASK_HOST
        port = port or FLASK_PORT
        debug = debug if debug is not None else FLASK_DEBUG
        
        if self.running:
            logger.warning("Flask server already running")
            return
        
        def run_server():
            logger.info(f"Starting Flask server on {host}:{port}")
            self.app.run(
                host=host,
                port=port,
                debug=debug,
                use_reloader=False,  # Disable reloader in thread
                threaded=True
            )
        
        self.thread = threading.Thread(target=run_server, daemon=True)
        self.thread.start()
        self.running = True
        logger.info("Flask server thread started")
    
    def stop(self):
        """Stop the server (limited support in Flask dev server)."""
        self.running = False
        logger.info("Flask server stop requested")

# Global instance
flask_server = FlaskServer()