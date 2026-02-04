"""
Voice engine for speech recognition and text-to-speech.
Handles microphone input and spoken responses.
"""

import threading
import queue
import time
from typing import Optional, Callable
import speech_recognition as sr
import pyttsx3
from loguru import logger

from jarvis.config.settings import JARVIS_NAME, WAKE_PHRASE

class VoiceEngine:
    """Handles voice input and output for JARVIS."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Defer microphone creation until actually needed to avoid blocking on import
        self.microphone = None
        self.tts_engine = None
        self.speaking = False
        self._mic_calibrated = False
        self._mic_available = False
        self._init_tts()
        
    def _init_tts(self):
        """Initialize text-to-speech engine."""
        try:
            self.tts_engine = pyttsx3.init()
            # Configure voice properties
            self.tts_engine.setProperty('rate', 175)  # Speed
            self.tts_engine.setProperty('volume', 0.9)  # Volume
            
            # Try to use a nicer voice if available
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Prefer a male voice (index 0 usually male on Windows)
                self.tts_engine.setProperty('voice', voices[0].id)
                
            logger.info("TTS engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            self.tts_engine = None
    
    def _ensure_microphone(self):
        """Lazily create and calibrate the microphone; mark availability."""
        if self._mic_calibrated:
            return
        try:
            if self.microphone is None:
                self.microphone = sr.Microphone()
            with self.microphone as source:
                logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                self.recognizer.dynamic_energy_threshold = True
                self._mic_available = True
                logger.info("Microphone calibrated")
        except Exception as e:
            logger.error(f"Microphone initialization/calibration failed: {e}")
            self._mic_available = False
        finally:
            self._mic_calibrated = True
    
    def listen(
        self, 
        timeout: Optional[float] = 5.0,
        phrase_time_limit: Optional[float] = 10.0,
        use_wake_phrase: bool = False
    ) -> Optional[str]:
        """
        Listen for voice input and convert to text.
        
        Args:
            timeout: Maximum time to wait for speech
            phrase_time_limit: Maximum duration of spoken phrase
            use_wake_phrase: If True, only process after wake phrase detected
            
        Returns:
            Recognized text or None if failed/timeout
        """
        try:
            # Lazily initialize microphone and calibrate if needed
            self._ensure_microphone()
            if not self._mic_available or self.microphone is None:
                logger.error("Microphone not available; cannot listen")
                return None

            with self.microphone as source:
                logger.debug("Listening...")
                
                # Listen for audio
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
            logger.debug("Processing speech...")
            
            # Use Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Heard: {text}")
            
            # Check wake phrase if required
            if use_wake_phrase:
                if WAKE_PHRASE not in text.lower():
                    logger.debug(f"Wake phrase '{WAKE_PHRASE}' not detected")
                    return None
                # Remove wake phrase from command
                text = text.lower().replace(WAKE_PHRASE, "").strip()
            
            return text
            
        except sr.WaitTimeoutError:
            logger.debug("Listening timeout - no speech detected")
            return None
        except sr.UnknownValueError:
            logger.debug("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in listen(): {e}")
            return None
    
    def speak(self, text: str, block: bool = False) -> threading.Thread:
        """
        Convert text to speech.
        
        Args:
            text: Text to speak
            block: If True, block until speaking is done
            
        Returns:
            Thread object if non-blocking
        """
        if not self.tts_engine:
            logger.warning("TTS not available, printing instead")
            print(f"[{JARVIS_NAME}]: {text}")
            return None
        
        def _speak():
            try:
                self.speaking = True
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                self.speaking = False
                logger.debug(f"Spoke: {text[:50]}...")
            except Exception as e:
                logger.error(f"TTS error: {e}")
                self.speaking = False
        
        if block:
            _speak()
            return None
        else:
            thread = threading.Thread(target=_speak, daemon=True)
            thread.start()
            return thread
    
    def speak_async(self, text: str):
        """Non-blocking speak."""
        return self.speak(text, block=False)
    
    def is_speaking(self) -> bool:
        """Check if currently speaking."""
        return self.speaking
    
    def listen_continuous(
        self,
        callback: Callable[[str], None],
        use_wake_phrase: bool = True,
        pause_between: float = 1.0
    ):
        """
        Continuously listen for commands.
        
        Args:
            callback: Function to call with recognized text
            use_wake_phrase: Require wake phrase
            pause_between: Seconds to pause between listens
        """
        logger.info(f"Starting continuous listening (wake phrase: {use_wake_phrase})")
        
        while True:
            try:
                # Listen for command
                text = self.listen(
                    timeout=None if use_wake_phrase else 5.0,
                    use_wake_phrase=use_wake_phrase
                )
                
                if text:
                    callback(text)
                
                time.sleep(pause_between)
                
            except KeyboardInterrupt:
                logger.info("Stopping continuous listening")
                break
            except Exception as e:
                logger.error(f"Error in continuous listen: {e}")
                time.sleep(pause_between)
    
    def stop(self):
        """Clean up resources."""
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass

# Global instance
voice_engine = VoiceEngine()