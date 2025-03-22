import keyboard
import subprocess
import os
import time

def text_to_speech(text, tts, tts_cache):
    """Convert text to speech and play it (macOS only)"""
    # Create audio directory if it doesn't exist
    if not os.path.exists("audio"):
        os.makedirs("audio")
    
    # Check if we've already generated this text before
    if text in tts_cache:
        audio_file = tts_cache[text]
        if os.path.exists(audio_file):
            # Play the cached audio file
            subprocess.run(["afplay", audio_file], check=True)
            return
    
    # Generate a unique filename
    audio_file = f"audio/response_{abs(hash(text)) % 10000}.wav"
    
    if tts is not None:
        try:
            # Try to use TTS library
            if hasattr(tts, 'synthesizer') and hasattr(tts.synthesizer, 'tts_model') and hasattr(tts.synthesizer.tts_model, 'speaker_manager') and tts.synthesizer.tts_model.speaker_manager is not None:
                # For multi-speaker models like VCTK
                speakers = tts.synthesizer.tts_model.speaker_manager.speaker_names
                speaker = speakers[0] if speakers else None
                tts.tts_to_file(text=text, file_path=audio_file, speaker=speaker)
            else:
                # For single speaker models
                tts.tts_to_file(text=text, file_path=audio_file)
            
            # Cache the result
            tts_cache[text] = audio_file
            
            # Play the audio file
            subprocess.run(["afplay", audio_file], check=True)
        except Exception as e:
            print(f"TTS error: {e}, falling back to macOS say")
            # Use macOS say as fallback
            subprocess.run(["say", text], check=True)
    else:
        # Use macOS say as fallback
        subprocess.run(["say", text], check=True)

def speech_to_text(audio_file):
    """Convert speech to text using Whisper"""
    try:
        # Create transcripts directory if it doesn't exist
        if not os.path.exists("transcripts"):
            os.makedirs("transcripts")
        
        # Get the base filename without path
        base_filename = os.path.basename(audio_file)
        base_name = os.path.splitext(base_filename)[0]
        
        # Use the tiny.en model which is faster, with minimal output
        # Specify output directory for all generated files
        result = subprocess.run(
            ["whisper", audio_file, "--model", "tiny.en", "--language", "en", 
             "--output_format", "txt", "--output_dir", "transcripts"],
            capture_output=True,
            text=True
        )
        
        # Try to read from the generated .txt file in the transcripts directory
        txt_file = os.path.join("transcripts", f"{base_name}.txt")
        if os.path.exists(txt_file):
            with open(txt_file, 'r') as f:
                transcription = f.read().strip()
                if transcription:
                    return transcription
        
        return "I couldn't understand what you said."
    except Exception as e:
        print(f"Error in speech recognition: {e}")
        return "I'm having technical difficulties understanding you."
    
def record_while_spacebar():
    """Record audio while spacebar is held down"""
    # Create recordings directory if it doesn't exist
    if not os.path.exists("recordings"):
        os.makedirs("recordings")
    
    filename = f"recordings/input_{int(time.time())}.wav"
    
    # Start recording process
    print("Press and hold SPACEBAR to record. Release to stop recording.")
    
    # Wait for spacebar to be pressed
    while not keyboard.is_pressed('space'):
        time.sleep(0.1)
    
    print("Recording... (release SPACEBAR to stop)")
    
    # Start the recording process
    process = subprocess.Popen(
        ["rec", "-r", "16000", "-c", "1", filename],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Record until spacebar is released
    start_time = time.time()
    while keyboard.is_pressed('space'):
        # Check if recording has gone on too long (30 seconds max)
        if time.time() - start_time > 30:
            print("Maximum recording time reached (30 seconds)")
            break
        time.sleep(0.1)
    
    # Stop the recording process
    process.terminate()
    process.wait()
    
    print("Recording finished.")
    
    # Check if file exists and has content
    if os.path.exists(filename) and os.path.getsize(filename) > 1000:
        return filename
    else:
        print("Recording too small or failed")
        return None
