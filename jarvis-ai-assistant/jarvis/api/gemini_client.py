"""
Google Gemini API client wrapper with retry logic and error handling.
"""

import os
import time
from typing import Optional, List, Dict, Any
import google.generativeai as genai
from loguru import logger

from jarvis.config.settings import GEMINI_API_KEY, GEMINI_MODEL, JARVIS_NAME, BUDDY_SYSTEM_PROMPT

class GeminiClient:
    """Wrapper for Google Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key:
            logger.warning("No Gemini API key provided. AI features will be limited.")
            self.model = None
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if Gemini API is configured and available."""
        return self.model is not None
    
    def chat(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_retries: int = 3
    ) -> str:
        """
        Send a chat message to Gemini with retry logic.
        
        Args:
            prompt: User message
            system_prompt: Optional system instructions
            temperature: Creativity level (0.0 to 1.0)
            max_retries: Number of retry attempts
            
        Returns:
            Response text or fallback message
        """
        if not self.is_available():
            return self._fallback_response()
        
        # Build system prompt with personality
        if system_prompt is None:
            system_prompt = BUDDY_SYSTEM_PROMPT.format(name=JARVIS_NAME)
        
        full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\n{JARVIS_NAME}:"
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=500,
                    )
                )
                
                if response.text:
                    logger.debug(f"Gemini response received ({len(response.text)} chars)")
                    return response.text.strip()
                else:
                    logger.warning("Empty response from Gemini")
                    if attempt < max_retries - 1:
                        time.sleep(0.5 * (attempt + 1))
                        
            except Exception as e:
                logger.error(f"Gemini API error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(1 * (attempt + 1))
                else:
                    break
        
        return self._fallback_response(error=True)
    
    def generate_command_response(
        self, 
        command_type: str, 
        success: bool, 
        details: str = "",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a buddy-style response for command execution.
        
        Args:
            command_type: Type of command executed
            success: Whether command succeeded
            details: Additional details about the result
            context: Optional context dict
            
        Returns:
            Friendly response string
        """
        if not self.is_available():
            return self._generate_local_response(command_type, success, details)
        
        # Build contextual prompt
        status = "succeeded" if success else "failed"
        prompt = f"""The user asked me to {command_type}. It {status}.
Details: {details}

Give a brief, friendly response (1-2 sentences) as a helpful buddy. 
Be natural and conversational. If it failed, be supportive and suggest what might have gone wrong."""

        try:
            response = self.chat(prompt, temperature=0.6)
            return response
        except Exception as e:
            logger.error(f"Failed to generate command response: {e}")
            return self._generate_local_response(command_type, success, details)
    
    def _generate_local_response(
        self, 
        command_type: str, 
        success: bool, 
        details: str
    ) -> str:
        """Generate a local fallback response without API."""
        import random
        
        success_phrases = [
            "Done! Got it handled for you, buddy. 🙂",
            "All set! Anything else you need? 😊",
            "Finished! That was easy. 🔥",
            "Done and done! Let me know what's next.",
            "Success! Your wish is my command. ✨",
        ]
        
        failure_phrases = [
            "Hmm, I ran into a snag there. 😅 Want to try again?",
            "Oops, that didn't work. Could you double-check the details?",
            "I couldn't quite pull that off. Maybe a different approach?",
            "That one gave me trouble. Want to try rephrasing it?",
            "Hmm, no luck that time. Let's give it another shot! 💪",
        ]
        
        if success:
            return random.choice(success_phrases)
        else:
            return random.choice(failure_phrases)
    
    def _fallback_response(self, error: bool = False) -> str:
        """Return fallback response when API is unavailable."""
        if error:
            return "I'm having trouble connecting to my brain right now. 😅 Can you try again in a moment?"
        return "I'm running in offline mode right now, buddy. I can still help with basic commands!"
    
    def quick_chat(self, message: str) -> str:
        """Quick chat without context."""
        return self.chat(message)

# Global instance
gemini_client = GeminiClient()