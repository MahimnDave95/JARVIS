"""
AI Engine with buddy personality.
Wraps Gemini client and maintains conversation context.
"""

from typing import Optional, Dict, Any, List
from loguru import logger

from jarvis.api.gemini_client import gemini_client, GeminiClient
from jarvis.database.db_manager import db_manager
from jarvis.config.settings import JARVIS_NAME, BUDDY_SYSTEM_PROMPT

class AIEngine:
    """
    AI Engine with friendly buddy personality.
    Manages conversations and generates contextual responses.
    """
    
    def __init__(self):
        self.client = gemini_client
        self.session_id = "default"
        self.max_context = 10
    
    def generate_reply(
        self, 
        user_message: str, 
        context: Optional[Dict[str, Any]] = None,
        use_history: bool = True
    ) -> str:
        """
        Generate a friendly reply to user message.
        
        Args:
            user_message: What the user said
            context: Optional context (command results, etc.)
            use_history: Whether to use conversation history
            
        Returns:
            Friendly response string
        """
        # Build enriched prompt with context
        prompt = user_message
        
        if context:
            context_str = self._format_context(context)
            prompt = f"{context_str}\n\nUser: {user_message}"
        
        # Get conversation history if enabled
        history = []
        if use_history and self.client.is_available():
            history = db_manager.get_conversation_history(self.session_id, self.max_context)
        
        # Add history to prompt if available
        if history:
            history_str = "\n".join([
                f"{'User' if msg['role'] == 'user' else JARVIS_NAME}: {msg['content']}"
                for msg in history[-5:]  # Last 5 messages
            ])
            prompt = f"Previous conversation:\n{history_str}\n\nCurrent message: {prompt}"
        
        # Generate response
        response = self.client.chat(prompt)
        
        # Save to conversation history
        if use_history:
            db_manager.add_conversation_message("user", user_message, self.session_id)
            db_manager.add_conversation_message("assistant", response, self.session_id)
        
        return response
    
    def generate_command_response(
        self,
        command_type: str,
        success: bool,
        details: str = "",
        user_friendly: bool = True
    ) -> str:
        """
        Generate response for command execution.
        
        Args:
            command_type: Type of command
            success: Whether it succeeded
            details: Execution details
            user_friendly: If True, use buddy personality
            
        Returns:
            Response message
        """
        if user_friendly:
            return self.client.generate_command_response(
                command_type, success, details
            )
        else:
            # Simple factual response
            if success:
                return f"Command '{command_type}' executed successfully."
            else:
                return f"Command '{command_type}' failed: {details}"
    
    def explain_error(self, error: str, context: str = "") -> str:
        """
        Generate helpful error explanation.
        
        Args:
            error: Error message
            context: What was being attempted
            
        Returns:
            Helpful error message
        """
        prompt = f"""I encountered an error while trying to help the user.
Context: {context}
Error: {error}

Explain this error in a friendly, helpful way (1-2 sentences) and suggest what to try next.
Be supportive and not overly technical."""
        
        try:
            return self.client.chat(prompt, temperature=0.5)
        except:
            return f"Hmm, I hit a snag: {error}. Want to try again? 😅"
    
    def greet(self) -> str:
        """Generate a greeting."""
        import random
        from datetime import datetime
        
        hour = datetime.now().hour
        time_greeting = "morning" if 5 <= hour < 12 else \
                       "afternoon" if 12 <= hour < 17 else \
                       "evening" if 17 <= hour < 22 else "night"
        
        greetings = [
            f"Good {time_greeting}! Ready to help out. 🙂",
            f"Hey there! What's on the agenda today? 🔥",
            f"Hello! I'm all ears. Well, metaphorically speaking. 😄",
            f"Hi buddy! What can I do for you?",
            f"Good {time_greeting}! Let's get things done. 💪",
        ]
        
        return random.choice(greetings)
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dict into string."""
        parts = []
        for key, value in context.items():
            if value:
                parts.append(f"{key}: {value}")
        return " | ".join(parts) if parts else ""
    
    def clear_history(self):
        """Clear conversation history."""
        db_manager.clear_conversation_history(self.session_id)
        logger.info("Conversation history cleared")

# Global instance
ai_engine = AIEngine()