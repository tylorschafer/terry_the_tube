import warnings
import time
import os
import torch
import threading
import sys

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from TTS.api import TTS
from cleanup import cleanup_old_files
from conversation_helpers import *
from web_interface import WebInterface, start_web_server

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

class TerryTubeApp:
    def __init__(self, use_web_gui=True):
        self.use_web_gui = use_web_gui
        self.web_interface = None
        self.recording_in_progress = False
        self.current_audio_file = None
        
        # Initialize the LLM
        try:
            self.model = OllamaLLM(model="gemma3:4b-it-q8_0", temperature=0.7, timeout=6)
            self.prompt = ChatPromptTemplate.from_template(template)
            self.chain = self.prompt | self.model
            self.exit_string = "Asshole."
        except Exception as e:
            print(f"Error initializing LLM: {e}")
            print("Please make sure Ollama is running and the model is available")
            return
        
        self.conversation_history = []
        self.beer_dispensed = False
        
        if self.use_web_gui:
            self.web_interface = WebInterface(message_callback=self.handle_web_action)
    
    def handle_web_action(self, action):
        """Handle actions from the web interface"""
        if action == 'start_recording':
            self.start_recording()
        elif action == 'stop_recording':
            self.stop_recording()
    
    def start_recording(self):
        """Start recording audio"""
        if not self.recording_in_progress:
            self.recording_in_progress = True
            self.current_audio_file = record_while_spacebar() if not self.use_web_gui else self.record_for_web()
    
    def record_for_web(self):
        """Modified recording function for web interface"""
        import subprocess
        
        if not os.path.exists("recordings"):
            os.makedirs("recordings")
        
        filename = f"recordings/input_{int(time.time())}.wav"
        
        # Start the recording process
        self.recording_process = subprocess.Popen(
            ["rec", "-r", "16000", "-c", "1", filename],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        return filename
    
    def stop_recording(self):
        """Stop recording and process the audio"""
        if self.recording_in_progress:
            self.recording_in_progress = False
            
            if self.use_web_gui and hasattr(self, 'recording_process'):
                # Stop the recording process
                self.recording_process.terminate()
                self.recording_process.wait()
                
                # Process the recorded audio
                if self.current_audio_file and os.path.exists(self.current_audio_file) and os.path.getsize(self.current_audio_file) > 1000:
                    threading.Thread(target=self.process_user_input, args=(self.current_audio_file,), daemon=True).start()
                else:
                    self._set_status("Recording failed - please try again")
    
    def process_user_input(self, audio_file):
        """Process user input from audio file"""
        self._set_status("Transcribing your speech...")
        
        print("Transcribing your speech...")
        user_input = speech_to_text(audio_file)
        
        self._add_message("You", user_input, is_ai=False)
        
        print(f"You (transcribed): {user_input}")
        
        # Verify if the transcription seems valid
        if user_input in ["I couldn't understand what you said.", "I'm having technical difficulties understanding you."]:
            self._set_status("Failed to understand - please try again")
            if not self.use_web_gui:
                print("Failed to understand your speech. Please type your response:")
                user_input = input("You: ")
        
        # Add user input to conversation history
        self.conversation_history.append(f"Human: {user_input}")
        
        # Generate AI response
        self.generate_response()
    
    def _add_message(self, sender, message, is_ai=False):
        """Helper method to add message to web interface"""
        if self.web_interface:
            self.web_interface.add_message(sender, message, is_ai=is_ai)
    
    def _set_status(self, status):
        """Helper method to set status on web interface"""
        if self.web_interface:
            self.web_interface.set_status(status)
    
    def _clear_messages(self):
        """Helper method to clear messages on web interface"""
        if self.web_interface:
            self.web_interface.clear_messages()
    
    def generate_response(self):
        """Generate and display AI response"""
        self._set_status("Terry is thinking...")
        
        print("\n" + "="*50)
        print("BEER TUBE IS THINKING...")
        print("="*50 + "\n")
        
        try:
            context = "\n".join(self.conversation_history)
            response = self.chain.invoke({"context": context})
            
            # Add response to conversation history
            self.conversation_history.append(f"AI: {response}")
            
            # Strip response of * and display
            stripped_response = response.replace("*", "")
            
            self._add_message("Terry", stripped_response, is_ai=True)
            self._set_status("Ready to serve beer!")
            
            print("Beer Tube: " + stripped_response)
            text_to_speech(stripped_response, tts, tts_cache)
            
            # Check if beer should be dispensed
            if "BEER HERE!" in response and not self.beer_dispensed:
                self.beer_dispensed = True
                print("*Beer dispensing mechanism activated*")
                self._set_status("🍺 BEER DISPENSED! 🍺")
            
            # Check if conversation is over
            if self.exit_string in response:
                print("\n" + "="*50)
                print("CONVERSATION ENDED - READY FOR NEXT CUSTOMER")
                print("="*50 + "\n")
                
                self._set_status("Conversation ended - Ready for next customer")
                # Clear messages after a delay
                threading.Timer(3.0, self._clear_messages).start()
                
                # Wait a moment before starting a new conversation
                time.sleep(3)
                
                self.beer_dispensed = False
                self.conversation_history = []
                
                # Start with greeting again for the next customer
                greeting = "Hey there! You looking for a beer or what?"
                print("Beer Tube: " + greeting)
                text_to_speech(greeting, tts, tts_cache)
                
                self._add_message("Terry", greeting, is_ai=True)
                self._set_status("Ready to serve beer!")
                
        except Exception as e:
            print(f"Error generating response: {e}")
            print("Please make sure Ollama is running properly")
            self._set_status("Error - please try again")
            
            # Try to recover by restarting the conversation
            self.conversation_history = []
            print("Restarting conversation...")
            greeting = "Sorry about that. Let's start over. You looking for a beer or what?"
            print("Beer Tube: " + greeting)
            text_to_speech(greeting, tts, tts_cache)
            
            self._add_message("Terry", greeting, is_ai=True)
            self._set_status("Ready to serve beer!")

def handle_conversation():
    """Legacy terminal-only conversation loop for backwards compatibility"""
    print("Beer Tube activated! Ready to interact with humans.")
    
    cleanup_old_files()
    
    app = TerryTubeApp(use_web_gui=False)
    
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

def run_web_mode():
    """Run the application with web interface"""
    print("Beer Tube activated! Starting web interface...")
    cleanup_old_files()
    
    try:
        app = TerryTubeApp(use_web_gui=True)
        
        if app.web_interface:
            # Start the web interface
            print("Starting web interface...")
            app._add_message("Terry", "Hey there! You looking for a beer or what?", is_ai=True)
            start_web_server(app.web_interface)
        else:
            print("Web interface initialization failed, falling back to terminal mode...")
            run_terminal_mode()
    except Exception as e:
        print(f"Web interface failed: {e}")
        print("Falling back to terminal mode...")
        run_terminal_mode()

def run_terminal_mode():
    """Run the application in terminal-only mode"""
    handle_conversation()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Terry the Tube - AI Beer Dispenser')
    parser.add_argument('--mode', choices=['web', 'terminal'], default='web',
                        help='Choose interface mode: web (GUI) or terminal (default: web)')
    
    args = parser.parse_args()
    
    if args.mode == 'terminal':
        run_terminal_mode()
    else:
        run_web_mode()