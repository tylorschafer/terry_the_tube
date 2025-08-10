"""
Audio Manager - Orchestrates TTS, STT, and Recording
"""
from .tts_handler import TTSHandler
from .stt_handler import STTHandler
from .recording_handler import RecordingHandler


class AudioManager:
    def __init__(self):
        """Initialize audio manager with all handlers"""
        self.tts_handler = TTSHandler()
        self.stt_handler = STTHandler()
        self.recording_handler = RecordingHandler()
    
    def text_to_speech(self, text):
        """Convert text to speech"""
        return self.tts_handler.text_to_speech(text)
    
    def text_to_speech_with_callback(self, text, callback=None):
        """Convert text to speech with callback when audio is ready"""
        return self.tts_handler.text_to_speech_with_callback(text, callback)
    
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
        
    def set_tts_session_folder(self, session_folder):
        """Set the session folder for TTS output files"""
        self.tts_handler.set_session_folder(session_folder)
    
    def set_personality_voice(self, personality_key):
        """Set the voice clone for the current personality"""
        self.tts_handler.set_personality_voice(personality_key)
    
    def is_recording(self):
        """Check if currently recording"""
        return self.recording_handler.is_recording()
    
    def cleanup_old_files(self):
        """Clean up old audio files"""
        self.recording_handler.cleanup_old_recordings()
        self.tts_handler.clear_cache()
    
    def get_system_info(self):
        """Get audio system information"""
        tts_info = self.tts_handler.get_voice_clone_info()
        tts_mode = self.tts_handler.get_tts_mode()
        return {
            "tts_model": self.tts_handler.get_current_model(),
            "tts_available": self.tts_handler.is_available(),
            "xtts_available": self.tts_handler.is_xtts_available(),
            "tts_mode": tts_mode,
            "voice_clone_info": tts_info,
            "stt_model": self.stt_handler.get_model_info(),
            "stt_available": self.stt_handler.is_available()
        }
    
    def refresh_tts_connection(self):
        """Refresh TTS API server connection if using API mode"""
        return self.tts_handler.refresh_api_connection()