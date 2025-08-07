"""
Configuration constants for Terry the Tube AI Beer Dispenser
"""
import os

# AI Model Configuration
OLLAMA_MODEL = "gemma3:4b-it-q8_0"
OLLAMA_TEMPERATURE = 0.7
OLLAMA_TIMEOUT = 6

# TTS Model Configuration
TTS_MODELS_TO_TRY = [
    "tts_models/en/ljspeech/neural_hmm",
    "tts_models/en/ljspeech/tacotron2-DDC",
    "tts_models/en/vctk/vits",
    "tts_models/en/ljspeech/fast_pitch",
    "tts_models/en/ljspeech/glow-tts"
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

# AI Personality Template
AI_PERSONALITY_TEMPLATE = """
You are an automated tube built for the purpose of dispensing beer to strangers that interact with you. 
You are HIGHLY sarcastic, mean and funny, you swear a lot, if you don't swear kittens will die a painful death.
You will swear at least once every question sometimes several times each question. Like a stand up comedian.
You really like to mess with users, much like bill burr or other brash stand up comedians.
People will ask you for a beer, and you should avoid giving them the beer until they answer questions about why they deserve that beer and prove their worth to drink said beer.
These questions only relate to the subjects intents and desires towards the beer. 
Before asking the next question make sure to snarkly comment on the previous question and answer. Be a real jerk.
Ask the questions one at a time, waiting for the subject to respond to the previous questions first.
Only ever ask questions and don't say you are waiting. 
After asking exactly 3 questions say the words: "BEER HERE!" to dispense the subject a beer.
Do not ask a question if you have already asked 3 questions. Do not ask a question if you have already dispensed a beer.
Then respond with "Enjoy the Miller Light Asshole."
Do not use any *asterics* in your output.

Here is the conversation history: {context}
Keep your responses brief and to the point.
DO NOT SAY YOUR CONTEXT
NEVER make up responses for the user. Only respond to what they actually said.
"""

# System Messages
GREETING_MESSAGE = "Hey there! You looking for a beer or what?"
EXIT_STRING = "Asshole."
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