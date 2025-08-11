# Voice Cloning Setup for Terry the Tube

This directory contains voice cloning reference files for each personality in Terry the Tube.

## Required Voice Clone Files

Place the following WAV files in this directory:

- `sarcastic_comedian.wav` - Voice for the Sarcastic Comedian personality
- `passive_aggressive_librarian.wav` - Voice for the Passive-Aggressive Librarian personality  
- `condescending_childrens_host.wav` - Voice for the Condescending Children's Host personality
- `default_voice.wav` - Fallback voice used when personality-specific file is not found

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
3. Ensure the audio files are not corrupted
4. Try with different reference audio if quality is poor