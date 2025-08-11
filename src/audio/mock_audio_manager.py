"""
Mock Audio Manager for text-only testing mode
Bypasses all TTS/STT operations for faster development testing
"""
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import AUDIO_DIR
from utils.display import display


class MockAudioManager:
    """Mock audio manager that bypasses all audio processing for text-only testing"""
    
    def __init__(self):
        """Initialize mock audio manager"""
        self.current_personality = None
        self.voice_clone_path = None
        self.session_folder = None
        self.recording_in_progress = False
        print("Mock Audio Manager initialized (text-only mode)")
    
    def set_recording_session_folder(self, session_folder):
        """Mock setting recording session folder"""
        self.session_folder = session_folder
        print(f"[MOCK] Recording session folder set: {session_folder}")
    
    def set_tts_session_folder(self, session_folder):
        """Mock setting TTS session folder"""
        print(f"[MOCK] TTS session folder set: {session_folder}")
    
    def text_to_speech(self, text):
        """Mock TTS - just print the text that would be spoken"""
        print(f"[MOCK TTS] Would speak: {text}")
        # Small delay to simulate audio generation/playback
        time.sleep(0.1)
    
    def text_to_speech_with_callback(self, text, callback=None):
        """Mock TTS with callback - immediately call callback"""
        print(f"[MOCK TTS] Would speak: {text}")
        if callback:
            callback()  # Immediately trigger callback
        # Small delay to simulate audio generation/playback
        time.sleep(0.1)
    
    def speech_to_text(self, audio_file):
        """Mock STT - returns empty string to simulate no input"""
        print(f"[MOCK STT] Would transcribe audio file: {audio_file}")
        return ""  # Return empty string to simulate silence/no input
    
    def record_while_spacebar(self):
        """Mock spacebar recording - returns None (no audio file)"""
        print("[MOCK] Spacebar recording bypassed in text-only mode")
        return None
    
    def start_web_recording(self):
        """Mock start web recording"""
        self.recording_in_progress = True
        print("[MOCK] Web recording started (bypassed)")
        return "mock_recording.wav"
    
    def stop_web_recording(self):
        """Mock stop web recording"""
        self.recording_in_progress = False
        print("[MOCK] Web recording stopped (bypassed)")
        return None  # Return None to indicate no audio file
    
    def get_system_info(self):
        """Mock system info for text-only mode"""
        return {
            "tts_available": True,
            "tts_model": "Mock TTS (text-only mode)",
            "stt_available": True, 
            "stt_model": {
                "model": "Mock STT (text-only mode)",
                "device": "mock"
            },
            "voice_clone_info": {
                "personality": self.current_personality,
                "voice_clone_path": "mock_voice_clone.wav",
                "voice_clones_dir": "mock_voice_clones/"
            }
        }
    
    def clear_cache(self):
        """Mock clearing cache"""
        print("[MOCK] TTS cache cleared")
    
    def is_available(self):
        """Mock audio availability check"""
        return True