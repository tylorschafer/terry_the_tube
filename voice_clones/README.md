# Voice Cloning Setup for Terry the Tube

This directory contains voice cloning reference files for each personality in Terry the Tube.

## XTTS V2 Voice Cloning

Terry the Tube now uses XTTS V2 for high-quality voice cloning. Each personality can have its own unique voice by providing a reference audio file.

## Required Voice Clone Files

Place the following WAV files in this directory:

- `sarcastic_comedian.wav` - Voice for the Sarcastic Comedian personality
- `passive_aggressive_librarian.wav` - Voice for the Passive-Aggressive Librarian personality  
- `condescending_childrens_host.wav` - Voice for the Condescending Children's Host personality
- `default_voice.wav` - Fallback voice used when personality-specific file is not found

## Voice Clone File Requirements

- **Format**: WAV files (preferred) or other audio formats supported by XTTS
- **Length**: 6-30 seconds of clear speech
- **Quality**: High quality, minimal background noise
- **Content**: Natural speaking voice, preferably conversational tone
- **Sample Rate**: 22050 Hz recommended (XTTS will resample automatically)

## How Voice Cloning Works

1. When a personality is selected, the system looks for the corresponding voice file
2. If found, XTTS V2 uses that voice for all speech synthesis  
3. If not found, it falls back to `default_voice.wav`
4. If no voice files exist, XTTS uses its built-in default voice

## Example Usage

```bash
# Place your voice clone files
cp my_comedian_voice.wav voice_clones/sarcastic_comedian.wav
cp my_librarian_voice.wav voice_clones/passive_aggressive_librarian.wav
cp my_host_voice.wav voice_clones/condescending_childrens_host.wav

# Run Terry with voice cloning
python main.py
```

## Voice Quality Tips

- Use a quiet environment for recording reference audio
- Speak naturally and conversationally 
- Include varied intonation and emotions
- Avoid background music or noise
- Test with short clips first to verify quality

## Troubleshooting

If voice cloning isn't working:

1. Check that your WAV files are in the correct directory
2. Verify file names match exactly (case-sensitive)
3. Check the console output for XTTS loading messages
4. Ensure the audio files are not corrupted
5. Try with different reference audio if quality is poor

The system will automatically fall back to standard TTS if XTTS V2 fails to load.