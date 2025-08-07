"""
Conversation Manager for Terry the Tube
Handles conversation flow, state, and beer dispensing logic
"""
import time
import threading
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import (
    BEER_DISPENSED_TRIGGER, 
    BEER_DISPENSED_MESSAGE, CONVERSATION_ENDED_MESSAGE, RECORDINGS_DIR
)
from utils.display import display


class ConversationManager:
    def __init__(self, ai_handler, audio_handler, web_interface=None):
        """Initialize conversation manager"""
        self.ai_handler = ai_handler
        self.audio_handler = audio_handler
        self.web_interface = web_interface
        self.conversation_history = []
        self.beer_dispensed = False
        self.conversation_active = True
        self.question_count = 1  # Start at 1 since greeting is question 1
        self.current_session_folder = None
        self.first_user_message_timestamp = None
    
    def start_conversation(self):
        """Start a new conversation with greeting"""
        self.conversation_history = []
        self.beer_dispensed = False
        self.conversation_active = True
        self.question_count = 1  # Reset to 1 since greeting is question 1
        self.current_session_folder = None
        self.first_user_message_timestamp = None
        
        # Get personality-specific greeting
        greeting_message = self.ai_handler.get_greeting_message()
        
        display.bot_response(greeting_message, question_num=1)
        display.speaking()
        
        if self.web_interface:
            self.web_interface.add_message("Terry", greeting_message, is_ai=True)
            self.web_interface.set_status("Ready to serve beer!")
            # Small delay to ensure message appears before audio starts
            time.sleep(0.1)
        
        self.audio_handler.text_to_speech(greeting_message)
    
    def prepare_session_if_needed(self):
        """Create session folder if this is the first user interaction"""
        if self.first_user_message_timestamp is None:
            self.first_user_message_timestamp = time.strftime("%Y%m%d_%H%M%S")
            self.current_session_folder = os.path.join(RECORDINGS_DIR, self.first_user_message_timestamp)
            self._create_session_folder()
    
    def add_user_message(self, message):
        """Add user message to conversation history"""
        self.conversation_history.append(f"Human: {message}")
        
        # Ensure session is prepared (this will be a no-op if already done)
        self.prepare_session_if_needed()
    
    def _create_session_folder(self):
        """Create folder for current conversation session"""
        if self.current_session_folder and not os.path.exists(self.current_session_folder):
            os.makedirs(self.current_session_folder)
            display.session_start(self.first_user_message_timestamp)
            
            # Update audio handler to use this session folder for both recording and TTS
            if hasattr(self.audio_handler, 'set_recording_session_folder'):
                self.audio_handler.set_recording_session_folder(self.current_session_folder)
            if hasattr(self.audio_handler, 'set_tts_session_folder'):
                self.audio_handler.set_tts_session_folder(self.current_session_folder)
    
    def get_current_session_folder(self):
        """Get the current session folder path"""
        return self.current_session_folder
    
    def generate_and_handle_response(self):
        """Generate AI response and handle special commands"""
        if not self.conversation_active:
            return
        
        try:
            # Show question progress
            display.conversation_question(self.question_count, total=3)
            display.thinking()
            
            # Increment question count after user responds            
            response = self.ai_handler.generate_response(self.conversation_history, self.question_count)
            self.conversation_history.append(f"AI: {response}")

            if len(self.conversation_history) > 0:  # Don't increment on first greeting
                self.question_count += 1
            
            # Clean response of asterisks
            cleaned_response = response.replace("*", "")
            
            display.bot_response(cleaned_response, question_num=self.question_count-1)
            display.speaking()
            
            # Add message to web interface FIRST, then play audio
            if self.web_interface:
                self.web_interface.add_message("Terry", cleaned_response, is_ai=True)
                # Small delay to ensure message appears before audio starts
                time.sleep(0.1)
            
            self.audio_handler.text_to_speech(cleaned_response)
            
            # Handle beer dispensing
            if BEER_DISPENSED_TRIGGER in response and not self.beer_dispensed:
                self.dispense_beer()
            
            # Handle conversation end - use personality-specific exit string
            exit_string = self.ai_handler.get_exit_string()
            if exit_string in response:
                self.end_conversation()
                
        except Exception as e:
            display.error(f"Error generating response: {e}")
            self.handle_error_recovery()
    
    def dispense_beer(self):
        """Handle beer dispensing logic"""
        self.beer_dispensed = True
        display.beer_dispensed()
        
        if self.web_interface:
            self.web_interface.set_status(BEER_DISPENSED_MESSAGE)
    
    def end_conversation(self):
        """End current conversation and prepare for next customer"""
        display.conversation_end()
        
        if self.web_interface:
            self.web_interface.set_status(CONVERSATION_ENDED_MESSAGE)
            # Clear messages after a delay
            threading.Timer(3.0, self.web_interface.clear_messages).start()
        
        # Wait before starting new conversation
        time.sleep(3)
        
        # Reset and start new conversation
        self.start_conversation()
    
    def handle_error_recovery(self):
        """Handle errors by restarting conversation"""
        display.error("Please make sure Ollama is running properly")
        
        if self.web_interface:
            self.web_interface.set_status("Error - please try again")
        
        # Reset conversation
        self.conversation_history = []
        self.question_count = 1  # Reset question count
        self.current_session_folder = None
        self.first_user_message_timestamp = None
        display.warning("Restarting conversation...")
        
        recovery_message = "Sorry about that. Let's start over. You looking for a beer or what?"
        display.bot_response(recovery_message)
        display.speaking()
        
        if self.web_interface:
            self.web_interface.add_message("Terry", recovery_message, is_ai=True)
            self.web_interface.set_status("Ready to serve beer!")
            # Small delay to ensure message appears before audio starts
            time.sleep(0.1)
        
        self.audio_handler.text_to_speech(recovery_message)
    
    def is_conversation_active(self):
        """Check if conversation is currently active"""
        return self.conversation_active
    
    def get_conversation_history(self):
        """Get current conversation history"""
        return self.conversation_history.copy()
    
    def reset_conversation(self):
        """Reset conversation state"""
        self.conversation_history = []
        self.beer_dispensed = False
        self.conversation_active = True
        self.question_count = 1  # Reset question count
        self.current_session_folder = None
        self.first_user_message_timestamp = None