import warnings
import subprocess
import time
import os
import shutil
import glob
import keyboard
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import torch
from TTS.api import TTS

# Filter out the specific FP16 warning from Whisper
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# Initialize TTS with a different model that might work better
print("Loading TTS model...")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Try different TTS models in order of preference
tts = None
tts_models_to_try = [
    "tts_models/en/vctk/vits",
    "tts_models/en/ljspeech/fast_pitch",
    "tts_models/en/ljspeech/glow-tts"
]

for model_name in tts_models_to_try:
    try:
        print(f"Trying TTS model: {model_name}")
        tts = TTS(model_name, progress_bar=False).to(device)
        print(f"Successfully loaded TTS model: {model_name}")
        break
    except Exception as e:
        print(f"Failed to load TTS model {model_name}: {e}")

if tts is None:
    print("WARNING: Could not load any TTS model. Will use macOS say as fallback.")

# Cache for TTS to avoid regenerating the same responses
tts_cache = {}

# Set up the LLM and prompt
template = """
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

def text_to_speech(text):
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

def handle_conversation():
    """Main conversation loop for the beer tube"""
    print("Beer Tube activated! Ready to interact with humans.")
    
    cleanup_old_files()
    
    # Initialize the LLM
    try:
        # Set a shorter timeout for faster responses
        model = OllamaLLM(model="gemma3:4b-it-q8_0", temperature=0.7, timeout=6)
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | model
        exit_string = "Asshole."
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        print("Please make sure Ollama is running and the model is available")
        return
    
    conversation_history = []
    beer_dispensed = False
    
    # Initial greeting
    greeting = "Hey there! You looking for a beer or what?"
    print("Beer Tube: " + greeting)
    text_to_speech(greeting)
    
    while True:
        # Prompt user for input
        print("\n" + "="*50)
        print("YOUR TURN TO SPEAK - PRESS AND HOLD SPACEBAR")
        print("="*50 + "\n")
        
        audio_file = record_while_spacebar()
        
        if audio_file and os.path.exists(audio_file) and os.path.getsize(audio_file) > 1000:
            # Start transcribing
            print("Transcribing your speech...")
            user_input = speech_to_text(audio_file)
            print(f"You (transcribed): {user_input}")
            
            # Verify if the transcription seems valid
            if user_input == "I couldn't understand what you said." or user_input == "I'm having technical difficulties understanding you.":
                print("Failed to understand your speech. Please type your response:")
                user_input = input("You: ")
        else:
            print("Recording failed or was too quiet. Please type your response:")
            user_input = input("You: ")
        
        # Add user input to conversation history
        conversation_history.append(f"Human: {user_input}")
        
        # Clear visual indicator that the AI is now responding
        print("\n" + "="*50)
        print("BEER TUBE IS THINKING...")
        print("="*50 + "\n")
        
        # Generate response using the LLM
        try:
            context = "\n".join(conversation_history)
            response = chain.invoke({"context": context})
            
            # Add response to conversation history
            conversation_history.append(f"AI: {response}")
            
            # Strip response of * and play back †o user
            stripped_response = response.replace("*", "")
            print("Beer Tube: " + stripped_response)
            text_to_speech(stripped_response)
            
            # Check if beer should be dispensed
            if "BEER HERE!" in response and not beer_dispensed:
                beer_dispensed = True
                print("*Beer dispensing mechanism activated*")
                # Activate Servo to dispense beer
            
            # Check if conversation is over
            if exit_string in response:
                print("\n" + "="*50)
                print("CONVERSATION ENDED - READY FOR NEXT CUSTOMER")
                print("="*50 + "\n")
                
                # Wait a moment before starting a new conversation
                time.sleep(3)
                
                beer_dispensed = False  # Reset for next customer
                conversation_history = []  # Clear history for next customer
                
                # Start with greeting again for the next customer
                greeting = "Hey there! You looking for a beer or what?"
                print("Beer Tube: " + greeting)
                text_to_speech(greeting)
                
                continue
                
        except Exception as e:
            print(f"Error generating response: {e}")
            print("Please make sure Ollama is running properly")
            # Try to recover by restarting the conversation
            conversation_history = []
            print("Restarting conversation...")
            greeting = "Sorry about that. Let's start over. You looking for a beer or what?"
            print("Beer Tube: " + greeting)
            text_to_speech(greeting)

# Clean up old recordings, audio files, and transcript files
def cleanup_old_files():
    """Delete all recordings, AI output files, and transcript files at startup"""
    print("Cleaning up old files...")
    
    # Clean up recordings directory
    if os.path.exists("recordings"):
        shutil.rmtree("recordings")
        os.makedirs("recordings")
    else:
        os.makedirs("recordings")
    
    # Clean up audio directory
    if os.path.exists("audio"):
        shutil.rmtree("audio")
        os.makedirs("audio")
    else:
        os.makedirs("audio")
    
    # Create transcipts folder
    if not os.path.exists("transcripts"):
        os.makedirs("transcripts")
    else:
        # Clean up existing transcript files
        for file_ext in ['.vtt', '.srt', '.tsv', '.txt', '.json']:
            for file in glob.glob(f"*.{file_ext}"):
                try:
                    # Move to transcripts folder then delete
                    shutil.move(file, os.path.join("transcripts", os.path.basename(file)))
                except Exception as e:
                    print(f"Error moving {file}: {e}")
        
        # Now clean up the transcripts folder
        for file in os.listdir("transcripts"):
            file_path = os.path.join("transcripts", file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
    
    print("Cleanup complete.")


if __name__ == "__main__":
    handle_conversation()