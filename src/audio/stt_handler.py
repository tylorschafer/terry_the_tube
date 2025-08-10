"""
Speech-to-Text Handler for Terry the Tube
"""
import os
import subprocess
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import (
    WHISPER_MODEL, WHISPER_LANGUAGE, TRANSCRIPTS_DIR,
    STT_ERROR_MESSAGE, STT_TECHNICAL_ERROR
)


class STTHandler:
    def __init__(self):
        """Initialize Speech-to-Text handler"""
        self.model = WHISPER_MODEL
        self.language = WHISPER_LANGUAGE
        
        # Ensure transcripts directory exists
        if not os.path.exists(TRANSCRIPTS_DIR):
            os.makedirs(TRANSCRIPTS_DIR)
    
    def speech_to_text(self, audio_file):
        """Convert speech to text using Whisper"""
        try:
            # Get the base filename without path
            base_filename = os.path.basename(audio_file)
            base_name = os.path.splitext(base_filename)[0]
            
            # Run Whisper transcription
            result = subprocess.run(
                ["whisper", audio_file, "--model", self.model, "--language", self.language, 
                 "--output_format", "txt", "--output_dir", TRANSCRIPTS_DIR],
                capture_output=True,
                text=True
            )
            
            # Read transcription result
            txt_file = os.path.join(TRANSCRIPTS_DIR, f"{base_name}.txt")
            if os.path.exists(txt_file):
                with open(txt_file, 'r') as f:
                    transcription = f.read().strip()
                    if transcription:
                        return transcription
            
            # Return empty string for silent/empty recordings (let bot handle silence)
            return ""
            
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            return STT_TECHNICAL_ERROR
    
    def is_available(self):
        """Check if Whisper is available"""
        try:
            result = subprocess.run(["whisper", "--help"], capture_output=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def get_model_info(self):
        """Get current model information"""
        return {
            "model": self.model,
            "language": self.language
        }