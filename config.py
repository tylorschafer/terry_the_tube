"""
Configuration constants for Terry the Tube AI Beer Dispenser
"""
import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Look for .env file in the project root
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print("Loaded environment variables from .env file")
    else:
        print("No .env file found - using system environment variables only")
except ImportError:
    print("python-dotenv not installed - using system environment variables only")

# AI Model Configuration
USE_OPENAI_CHAT = True  # Use OpenAI GPT for chat generation (paid service)
OPENAI_CHAT_MODEL = "gpt-5-mini"  # OpenAI chat model
OPENAI_CHAT_TEMPERATURE = 0.7
OPENAI_CHAT_TIMEOUT = 30

# Ollama Fallback Configuration (used when USE_OPENAI_CHAT=False)
OLLAMA_MODEL = "mistral-small:24b"
OLLAMA_TEMPERATURE = 0.7
OLLAMA_TIMEOUT = 6

# TTS Configuration
USE_OPENAI_TTS = True  # Use OpenAI TTS for high-quality, fast generation (paid service)
OPENAI_TTS_MODEL = "gpt-4o-mini-tts"  # Options: "tts-1", "tts-1-hd", "gpt-4o-mini-tts" (supports instructions)
OPENAI_TTS_VOICE = "echo"  # Options: "alloy", "echo", "fable", "onyx", "nova", "shimmer"
OPENAI_TTS_SPEED = 1.0  # Speed: 0.25 to 4.0
OPENAI_TTS_FORMAT = "wav"  # Format: "mp3", "opus", "aac", "flac", "wav", "pcm"

# Fallback: macOS 'say' command is used if OpenAI TTS fails

# Text Chat Configuration
ENABLE_TEXT_CHAT = True  # Enable text chat input in web interface
TEXT_CHAT_ONLY = False   # Text-only mode (no audio processing at all)

# Audio Configuration
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
MAX_RECORDING_TIME = 30  # seconds
MIN_AUDIO_FILE_SIZE = 1000  # bytes

# Whisper Configuration
WHISPER_MODEL = "tiny.en"
WHISPER_LANGUAGE = "en"

# Directory Configuration
RECORDINGS_DIR = "recordings"
AUDIO_DIR = "audio"
TRANSCRIPTS_DIR = "transcripts"
ASSETS_DIR = "asset"

# Web Interface Configuration
WEB_PORT = 8080
WEB_HOST = "localhost"

# Personality Configuration
DEFAULT_PERSONALITY = "sarcastic_comedian"  # Default personality key
BEER_DISPENSED_TRIGGER = "BEER HERE!"
BEER_DISPENSED_MESSAGE = "🍺 BEER DISPENSED! 🍺"
CONVERSATION_ENDED_MESSAGE = "Conversation ended - Ready for next customer"

# Error Messages
TTS_ERROR_FALLBACK = "TTS error, falling back to macOS say"
STT_ERROR_MESSAGE = "I couldn't understand what you said."
STT_TECHNICAL_ERROR = "I'm having technical difficulties understanding you."
RECORDING_TOO_SMALL_ERROR = "Recording too small or failed"
RECORDING_FAILED_WEB_ERROR = "Recording failed - please try again"
TRANSCRIPTION_FAILED_ERROR = "Failed to understand - please try again"

# File Extensions for Cleanup
TRANSCRIPT_EXTENSIONS = ['.vtt', '.srt', '.tsv', '.txt', '.json']

# System Commands (macOS specific)
AUDIO_PLAY_COMMAND = ["afplay"]
TTS_FALLBACK_COMMAND = ["say", "-v", "fred"]
AUDIO_RECORD_COMMAND = ["rec", "-r", str(AUDIO_SAMPLE_RATE), "-c", str(AUDIO_CHANNELS)]