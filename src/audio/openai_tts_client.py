import os
import sys
import time
from pathlib import Path
from typing import Optional, Callable

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    print("Warning: openai package not installed. Run: pip install openai")

from config import (
    USE_OPENAI_TTS, OPENAI_TTS_MODEL, OPENAI_TTS_VOICE, 
    OPENAI_TTS_SPEED, OPENAI_TTS_FORMAT, AUDIO_DIR
)
from voice_instructions import get_voice_settings


class OpenAITTSClient:
    def __init__(self):
        """Initialize OpenAI TTS client"""
        self.client = None
        self.available = False
        self.current_personality = None
        
        # Check if OpenAI is available and configured
        if OpenAI is None:
            print("OpenAI package not installed")
            return
            
        if not USE_OPENAI_TTS:
            print("OpenAI TTS disabled in configuration")
            return
            
        # Initialize OpenAI client
        try:
            self.client = OpenAI()  # Uses OPENAI_API_KEY environment variable
            self.available = True
            print(f"OpenAI TTS initialized with model: {OPENAI_TTS_MODEL}, voice: {OPENAI_TTS_VOICE}")
        except Exception as e:
            print(f"Failed to initialize OpenAI TTS: {e}")
            print("Make sure OPENAI_API_KEY environment variable is set")
    
    def is_available(self) -> bool:
        """Check if OpenAI TTS is available"""
        return self.available and self.client is not None
    
    def set_personality(self, personality_key: str):
        """Set the current personality for voice customization"""
        self.current_personality = personality_key
        print(f"OpenAI TTS personality set to: {personality_key}")

    
    def text_to_speech(self, text: str, output_file: Optional[str] = None) -> str:
        """
        Convert text to speech using OpenAI TTS with personality-specific voice settings
        Returns path to the generated audio file
        """
        if not self.is_available():
            raise Exception("OpenAI TTS not available")
        
        # Get personality-specific voice settings
        if self.current_personality:
            voice_settings = get_voice_settings(self.current_personality)
        else:
            # Fallback to config defaults
            voice_settings = {
                "voice": OPENAI_TTS_VOICE,
                "speed": OPENAI_TTS_SPEED,
                "instruction": ""
            }
        
        try:
            print(f"Generating TTS with OpenAI ({voice_settings['voice']}) for: {text[:50]}...")
            
            # Call OpenAI TTS API with personality-specific settings including instructions
            response = self.client.audio.speech.create(
                model=OPENAI_TTS_MODEL,
                voice=voice_settings['voice'],
                input=text,
                instructions=voice_settings['instruction'],  # Pass instructions parameter
                response_format=OPENAI_TTS_FORMAT,
                speed=voice_settings['speed']
            )
            
            # Get audio data
            audio_data = response.content
            
            # Save to output file or temp file
            if output_file:
                with open(output_file, "wb") as f:
                    f.write(audio_data)
                print(f"TTS generated: {output_file}")
                return output_file
            else:
                # Create temporary file
                audio_dir = Path(AUDIO_DIR)
                audio_dir.mkdir(parents=True, exist_ok=True)
                
                temp_file = audio_dir / f"response_{int(time.time() * 1000) % 100000000:08x}.wav"
                with open(temp_file, "wb") as f:
                    f.write(audio_data)
                print(f"TTS generated: {temp_file}")
                return str(temp_file)
            
        except Exception as e:
            print(f"OpenAI TTS generation failed: {e}")
            raise
    
    def text_to_speech_with_callback(self, text: str, on_audio_starts: Optional[Callable] = None) -> str:
        """
        Generate TTS and play it, calling callback when playback starts
        """
        # Generate the audio file
        audio_file = self.text_to_speech(text)
        
        # Call callback before starting playback (audio is ready)
        if on_audio_starts:
            on_audio_starts()
        
        # Play the audio file using system command
        try:
            import subprocess
            from config import AUDIO_PLAY_COMMAND
            
            # Play audio file
            subprocess.run(AUDIO_PLAY_COMMAND + [audio_file], check=True)
            print(f"Finished playing TTS audio: {audio_file}")
            
        except Exception as e:
            print(f"Error playing audio: {e}")
            # Still return the file path even if playback failed
        
        return audio_file
    
    def get_available_voices(self) -> list:
        """Get list of available voices"""
        # OpenAI TTS voices (as of 2024)
        return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    def get_available_models(self) -> list:
        """Get list of available models"""
        return ["tts-1", "tts-1-hd"]
    
    def get_system_info(self) -> dict:
        """Get system information for debugging"""
        return {
            "openai_tts_available": self.is_available(),
            "model": OPENAI_TTS_MODEL if self.is_available() else "N/A",
            "voice": OPENAI_TTS_VOICE if self.is_available() else "N/A",
            "speed": OPENAI_TTS_SPEED if self.is_available() else "N/A",
            "format": OPENAI_TTS_FORMAT if self.is_available() else "N/A",
            "api_key_set": bool(os.getenv("OPENAI_API_KEY")),
            "use_openai_tts": USE_OPENAI_TTS
        }