"""
Conversation Manager for Terry the Tube
Handles conversation flow, state, and beer dispensing logic
"""
import time
import threading
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import (
    GREETING_MESSAGE, EXIT_STRING, BEER_DISPENSED_TRIGGER, 
    BEER_DISPENSED_MESSAGE, CONVERSATION_ENDED_MESSAGE
)


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
    
    def start_conversation(self):
        """Start a new conversation with greeting"""
        self.conversation_history = []
        self.beer_dispensed = False
        self.conversation_active = True
        self.question_count = 1  # Reset to 1 since greeting is question 1
        
        print("Beer Tube: " + GREETING_MESSAGE)
        
        if self.web_interface:
            self.web_interface.add_message("Terry", GREETING_MESSAGE, is_ai=True)
            self.web_interface.set_status("Ready to serve beer!")
            # Small delay to ensure message appears before audio starts
            time.sleep(0.1)
        
        self.audio_handler.text_to_speech(GREETING_MESSAGE)
    
    def add_user_message(self, message):
        """Add user message to conversation history"""
        self.conversation_history.append(f"Human: {message}")
    
    def generate_and_handle_response(self):
        """Generate AI response and handle special commands"""
        if not self.conversation_active:
            return
        
        try:
            # Increment question count after user responds            
            response = self.ai_handler.generate_response(self.conversation_history, self.question_count)
            self.conversation_history.append(f"AI: {response}")

            if len(self.conversation_history) > 0:  # Don't increment on first greeting
                self.question_count += 1
            
            # Clean response of asterisks
            cleaned_response = response.replace("*", "")
            
            print("Beer Tube: " + cleaned_response)
            
            # Add message to web interface FIRST, then play audio
            if self.web_interface:
                self.web_interface.add_message("Terry", cleaned_response, is_ai=True)
                # Small delay to ensure message appears before audio starts
                time.sleep(0.1)
            
            self.audio_handler.text_to_speech(cleaned_response)
            
            # Handle beer dispensing
            if BEER_DISPENSED_TRIGGER in response and not self.beer_dispensed:
                self.dispense_beer()
            
            # Handle conversation end
            if EXIT_STRING in response:
                self.end_conversation()
                
        except Exception as e:
            print(f"Error generating response: {e}")
            self.handle_error_recovery()
    
    def dispense_beer(self):
        """Handle beer dispensing logic"""
        self.beer_dispensed = True
        print("*Beer dispensing mechanism activated*")
        
        if self.web_interface:
            self.web_interface.set_status(BEER_DISPENSED_MESSAGE)
    
    def end_conversation(self):
        """End current conversation and prepare for next customer"""
        print("\n" + "="*50)
        print("CONVERSATION ENDED - READY FOR NEXT CUSTOMER")
        print("="*50 + "\n")
        
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
        print("Please make sure Ollama is running properly")
        
        if self.web_interface:
            self.web_interface.set_status("Error - please try again")
        
        # Reset conversation
        self.conversation_history = []
        self.question_count = 1  # Reset question count
        print("Restarting conversation...")
        
        recovery_message = "Sorry about that. Let's start over. You looking for a beer or what?"
        print("Beer Tube: " + recovery_message)
        
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