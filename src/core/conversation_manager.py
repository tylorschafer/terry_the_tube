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
    def __init__(self, ai_handler, audio_handler, web_interface=None, text_only_mode=False):
        self.ai_handler = ai_handler
        self.audio_handler = audio_handler
        self.web_interface = web_interface
        self.text_only_mode = text_only_mode
        self.conversation_history = []
        self.beer_dispensed = False
        self.conversation_active = True
        self.question_count = 0  # Start at 0, greeting doesn't count as a question
        self.current_session_folder = None
        self.first_user_message_timestamp = None
        
        # Set personality for audio handler
        if hasattr(self.audio_handler, 'set_personality') and hasattr(self.ai_handler, 'personality_key'):
            self.audio_handler.set_personality(self.ai_handler.personality_key)
    
    def start_conversation(self):
        self.conversation_history = []
        self.beer_dispensed = False
        self.conversation_active = True
        self.question_count = 0  # Reset to 0, greeting doesn't count as a question
        self.current_session_folder = None
        self.first_user_message_timestamp = None
        
        # Get personality-specific greeting
        greeting_message = self.ai_handler.get_greeting_message()
        
        display.bot_response(greeting_message, question_num=0)  # Greeting is intro, not question 1
        
        # Handle greeting with loading spinner for web interface
        message_index = None
        if self.web_interface:
            self.web_interface.set_generating_audio(True)
            self.web_interface.set_status("Generating voice...")
            message_index = self.web_interface.add_pending_message("Terry", greeting_message, is_ai=True)
        
        display.speaking()
        
        # Generate and play greeting with callback
        self._generate_and_play_tts(greeting_message, message_index)
        
        if self.web_interface:
            # This will be set by the callback, but we set a fallback status
            self.web_interface.set_status("Ready to serve beer!")
    
    def prepare_session_if_needed(self):
        if self.first_user_message_timestamp is None:
            self.first_user_message_timestamp = time.strftime("%Y%m%d_%H%M%S")
            self.current_session_folder = os.path.join(RECORDINGS_DIR, self.first_user_message_timestamp)
            self._create_session_folder()
    
    def add_user_message(self, message):
        self.conversation_history.append(f"Human: {message}")
        
        # Ensure session is prepared (this will be a no-op if already done)
        self.prepare_session_if_needed()
    
    def _create_session_folder(self):
        if self.current_session_folder and not os.path.exists(self.current_session_folder):
            os.makedirs(self.current_session_folder)
            display.session_start(self.first_user_message_timestamp)
            
            # Update audio handler to use this session folder for both recording and TTS
            if hasattr(self.audio_handler, 'set_recording_session_folder'):
                self.audio_handler.set_recording_session_folder(self.current_session_folder)
            if hasattr(self.audio_handler, 'set_tts_session_folder'):
                self.audio_handler.set_tts_session_folder(self.current_session_folder)
    
    def get_current_session_folder(self):
        return self.current_session_folder
    
    def generate_and_handle_response(self):
        if not self.conversation_active:
            return
        
        try:
            # Show question progress (increment first since we're about to ask the next question)
            display.conversation_question(self.question_count, total=3)
            display.thinking()
            
            # Set generating response status for web interface
            if self.web_interface:
                self.web_interface.set_generating_response(True)
                self.web_interface.set_status("Generating response...")
            
            response = self.ai_handler.generate_response(self.conversation_history, self.question_count)
            self.conversation_history.append(f"AI: {response}")
            self.question_count += 1
            
            # Clean response of asterisks
            cleaned_response = response.replace("*", "")
            
            display.bot_response(cleaned_response, question_num=self.question_count)
            
            # Handle web interface message display with loading spinner
            message_index = None
            if self.web_interface:
                # First, add the hidden message before changing any states
                message_index = self.web_interface.add_pending_message("Terry", cleaned_response, is_ai=True)
                
                # Then transition directly from generating response to generating audio to prevent flash
                self.web_interface.set_generating_audio(True)
                self.web_interface.set_generating_response(False) 
                self.web_interface.set_status("Generating voice...")
            
            display.speaking()
            
            # Generate and play TTS audio with callback to show message
            self._generate_and_play_tts(cleaned_response, message_index)
            
            # Handle beer dispensing
            if BEER_DISPENSED_TRIGGER in response and not self.beer_dispensed:
                self.dispense_beer()
            
            # Handle conversation end - use personality-specific exit string
            exit_string = self.ai_handler.get_exit_string()
            # Make exit string detection more precise - only trigger at the END of response
            if response.strip().endswith(exit_string):
                self.end_conversation()
                
        except Exception as e:
            # Clear generating response status on error
            if self.web_interface:
                self.web_interface.set_generating_response(False)
            display.error(f"Error generating response: {e}")
            self.handle_error_recovery()
    
    def dispense_beer(self):
        self.beer_dispensed = True
        display.beer_dispensed()
        
        if self.web_interface:
            self.web_interface.set_status(BEER_DISPENSED_MESSAGE)
    
    def end_conversation(self):
        display.conversation_end()
        
        if self.web_interface:
            self.web_interface.set_status(CONVERSATION_ENDED_MESSAGE)
            # Clear messages and reset personality selection after delay
            threading.Timer(3.0, self._prepare_next_cycle).start()
        else:
            # Terminal mode - wait and restart automatically
            time.sleep(3)
            self.start_conversation()
    
    def _prepare_next_cycle(self):
        if self.web_interface:
            self.web_interface.clear_messages()
            self.web_interface.reset_personality_selection()
            self.web_interface.set_status("Select a personality to continue")
    
    def handle_error_recovery(self):
        display.error("Please make sure Ollama is running properly")
        
        if self.web_interface:
            self.web_interface.set_status("Error - please try again")
        
        # Reset conversation
        self.conversation_history = []
        self.question_count = 0  # Reset question count to 0
        self.current_session_folder = None
        self.first_user_message_timestamp = None
        
        self._restart_conversation_with_recovery()
    
    def _generate_and_play_tts(self, text, message_index=None):
        if self.text_only_mode:
            # In text-only mode, skip TTS and show message immediately
            if self.web_interface:
                if message_index is not None:
                    self.web_interface.show_message(message_index)
                self.web_interface.set_generating_audio(False)
                self.web_interface.set_status("Ready to serve beer!")
            return
        
        def on_audio_starts():
            if self.web_interface:
                # Show the message now that audio is starting to play
                if message_index is not None:
                    self.web_interface.show_message(message_index)
                
                # Clear generating status and update to speaking status
                self.web_interface.set_generating_audio(False)
                self.web_interface.set_status("Speaking...")
        
        # Generate and play TTS with callback that triggers when playback starts
        self.audio_handler.text_to_speech_with_callback(text, on_audio_starts)
    
    def _restart_conversation_with_recovery(self):
        display.warning("Restarting conversation...")
        
        recovery_message = "Sorry about that. Let's start over. You looking for a beer or what?"
        display.bot_response(recovery_message)
        
        # Handle recovery message with loading spinner
        message_index = None
        if self.web_interface:
            self.web_interface.set_generating_audio(True)
            self.web_interface.set_status("Generating voice...")
            message_index = self.web_interface.add_pending_message("Terry", recovery_message, is_ai=True)
        
        display.speaking()
        
        # Generate and play recovery message with callback
        self._generate_and_play_tts(recovery_message, message_index)
        
        if self.web_interface:
            self.web_interface.set_status("Ready to serve beer!")
    
    def is_conversation_active(self):
        return self.conversation_active
    
    def get_conversation_history(self):
        return self.conversation_history.copy()
    
    def reset_conversation(self):
        self.conversation_history = []
        self.beer_dispensed = False
        self.conversation_active = True
        self.question_count = 0  # Reset question count to 0
        self.current_session_folder = None
        self.first_user_message_timestamp = None