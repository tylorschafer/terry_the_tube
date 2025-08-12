"""
OpenAI TTS Voice Instructions for Terry the Tube Personalities
Each personality has specific voice direction and speaking style prompts.
"""

VOICE_INSTRUCTIONS = {
    "sarcastic_comedian": {
        "voice": "ash",
        "speed": 1.5,
        "instruction": "Speak like Bill Burr - gravelly Boston accent, sarcastic tone, sound annoyed but amused. Drag out sarcastic words, use rising intonation for mocking questions, drop voice for threats. Sound like a bartender who hates the job but loves roasting customers."
    },
    
    "passive_aggressive_librarian": {
        "voice": "sage",   # Young but can sound stern
        "speed": 1.3,      # Normal speed but with deliberate pauses
        "instruction": "Speak like a soft spoken librarian - artificially sweet tone masking slight irritation, exaggerated politeness that sounds fake, gritted teeth politeness. Over-enunciate when being passive-aggressive, stress polite words sarcastically. Sound like customer service on the verge of breakdown."
    },
    
    "condescending_childrens_host": {
        "voice": "alloy",
        "speed": 1.1,
        "instruction": "Speak like a fake-cheerful children's TV host who secretly hates everyone - artificially bright sing-song voice, exaggerated enthusiasm, baby-talk inflection with adult words. Emphasize simple words patronizingly, use fake gasps and excitement, switch between sweet and sharp tones. Sound like a kindergarten teacher who's lost faith in humanity."
    }
}

def get_voice_instruction(personality_key):
    """Get voice instruction for a specific personality"""
    return VOICE_INSTRUCTIONS.get(personality_key, VOICE_INSTRUCTIONS["sarcastic_comedian"])

def get_voice_settings(personality_key):
    """Get voice settings (voice, speed) for a specific personality"""
    instruction = get_voice_instruction(personality_key)
    return {
        "voice": instruction["voice"],
        "speed": instruction["speed"],
        "instruction": instruction["instruction"]
    }