"""
Configuration constants for Terry the Tube AI Beer Dispenser
"""
import os

# AI Model Configuration
OLLAMA_MODEL = "gemma3:12b"
OLLAMA_TEMPERATURE = 0.7
OLLAMA_TIMEOUT = 6

# TTS Model Configuration - Using XTTS V2 for voice cloning
XTTS_MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
USE_XTTS_V2 = True

# Voice cloning configuration
VOICE_CLONES_DIR = "voice_clones"
DEFAULT_VOICE_CLONE = "default_voice.wav"  # Fallback if personality voice not found

# Fallback TTS models (if XTTS V2 fails)
TTS_MODELS_TO_TRY = [
    "tts_models/en/ljspeech/glow-tts",
    "tts_models/en/vctk/vits",
    "tts_models/en/ljspeech/neural_hmm",
    "tts_models/en/ljspeech/fast_pitch",
    "tts_models/en/ljspeech/tacotron2-DDC"
]

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
TTS_FALLBACK_COMMAND = ["say"]
AUDIO_RECORD_COMMAND = ["rec", "-r", str(AUDIO_SAMPLE_RATE), "-c", str(AUDIO_CHANNELS)]