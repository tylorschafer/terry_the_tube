"""
Audio Manager - Orchestrates TTS, STT, and Recording
"""
import subprocess
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from .openai_tts_client import OpenAITTSClient
from .stt_handler import STTHandler
from .recording_handler import RecordingHandler
from config import TTS_FALLBACK_COMMAND


class AudioManager:
    def __init__(self):
        """Initialize audio manager with all handlers"""
        self.openai_tts = OpenAITTSClient()
        self.stt_handler = STTHandler()
        self.recording_handler = RecordingHandler()
        self.current_personality = None
    
    def set_personality(self, personality_key):
        """Set personality for TTS"""
        self.current_personality = personality_key
        if self.openai_tts.is_available():
            self.openai_tts.set_personality(personality_key)
    
    def text_to_speech(self, text):
        """Convert text to speech"""
        try:
            if self.openai_tts.is_available():
                return self.openai_tts.text_to_speech(text)
            else:
                # Fallback to macOS say command
                return self._fallback_tts(text)
        except Exception as e:
            print(f"TTS error: {e}, falling back to macOS say")
            return self._fallback_tts(text)
    
    def text_to_speech_with_callback(self, text, callback=None):
        """Convert text to speech with callback when audio starts"""
        try:
            if self.openai_tts.is_available():
                return self.openai_tts.text_to_speech_with_callback(text, callback)
            else:
                # Fallback to macOS say command with callback
                return self._fallback_tts_with_callback(text, callback)
        except Exception as e:
            print(f"TTS error: {e}, falling back to macOS say")
            return self._fallback_tts_with_callback(text, callback)
    
    def _fallback_tts(self, text):
        """Fallback TTS using macOS say command"""
        try:
            subprocess.run(TTS_FALLBACK_COMMAND + [text], check=True)
            return "macOS_say_output"  # Placeholder since no file is created
        except Exception as e:
            print(f"Fallback TTS failed: {e}")
            return None
    
    def _fallback_tts_with_callback(self, text, callback=None):
        """Fallback TTS with callback"""
        try:
            if callback:
                callback()  # Call callback before speaking
            subprocess.run(TTS_FALLBACK_COMMAND + [text], check=True)
            return "macOS_say_output"
        except Exception as e:
            print(f"Fallback TTS failed: {e}")
            return None
    
    def speech_to_text(self, audio_file):
        """Convert speech to text"""
        return self.stt_handler.speech_to_text(audio_file)
    
    def record_while_spacebar(self):
        """Record audio while spacebar is held"""
        return self.recording_handler.record_while_spacebar()
    
    def start_web_recording(self):
        """Start recording for web interface"""
        return self.recording_handler.start_web_recording()
    
    def stop_web_recording(self):
        """Stop recording for web interface"""
        return self.recording_handler.stop_web_recording()
    
    def set_recording_session_folder(self, session_folder):
        """Set the session folder for recordings"""
        self.recording_handler.set_session_folder(session_folder)
    
    def is_recording(self):
        """Check if currently recording"""
        return self.recording_handler.is_recording()
    
    def cleanup_old_files(self):
        """Clean up old audio files"""
        self.recording_handler.cleanup_old_recordings()
    
    def get_system_info(self):
        """Get audio system information"""
        tts_available = self.openai_tts.is_available()
        tts_model = "OpenAI TTS" if tts_available else "macOS say (fallback)"
        
        return {
            "tts_model": tts_model,
            "tts_available": True,  # Always available due to fallback
            "stt_model": self.stt_handler.get_model_info(),
            "stt_available": self.stt_handler.is_available()
        }