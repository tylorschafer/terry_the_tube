import warnings
import time
import os
import torch

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from TTS.api import TTS
from cleanup import cleanup_old_files
from conversation_helpers import *

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
    text_to_speech(greeting, tts, tts_cache)
    
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
            text_to_speech(stripped_response, tts, tts_cache)
            
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
            text_to_speech(greeting, tts, tts_cache)

if __name__ == "__main__":
    handle_conversation()