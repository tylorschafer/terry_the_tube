"""
Web Interface for Terry the Tube
Refactored and cleaned up version
"""
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import WEB_PORT, WEB_HOST


class WebInterface:
    def __init__(self, message_callback=None, enable_text_chat=False, text_only_mode=False):
        """Initialize web interface"""
        self.message_callback = message_callback
        self.messages = []
        self.status = "Ready to serve beer!"
        self.port = WEB_PORT
        self.host = WEB_HOST
        self.current_personality = None
        self.personality_selected = False
        self.personality_selected_by_user = False  # Track if user explicitly selected personality
        self.generating_audio = False  # Track if we're generating TTS audio
        self.generating_response = False  # Track if we're generating LLM response
        self.text_chat_enabled = enable_text_chat  # Track if text chat is enabled
        self.text_only_mode = text_only_mode  # Track if in text-only mode
        
    def add_message(self, sender, message, is_ai=False, show_immediately=True):
        """Add a message to display"""
        timestamp = time.strftime("%H:%M:%S")
        message_obj = {
            'sender': sender,
            'message': message,
            'is_ai': is_ai,
            'timestamp': timestamp,
            'show_immediately': show_immediately
        }
        self.messages.append(message_obj)
        return len(self.messages) - 1  # Return message index
        
    def set_status(self, status):
        """Update status"""
        self.status = status
    
    def clear_messages(self):
        """Clear all messages"""
        self.messages = []
    
    def get_messages(self):
        """Get all messages"""
        return self.messages.copy()
    
    def get_status(self):
        """Get current status"""
        return self.status
    
    def set_generating_audio(self, generating):
        """Set audio generation status"""
        self.generating_audio = generating
    
    def is_generating_audio(self):
        """Check if currently generating audio"""
        return self.generating_audio
    
    def set_generating_response(self, generating):
        """Set response generation status"""
        self.generating_response = generating
    
    def is_generating_response(self):
        """Check if currently generating response"""
        return self.generating_response
    
    def show_message(self, message_index):
        """Make a message visible (used when audio is ready)"""
        if 0 <= message_index < len(self.messages):
            self.messages[message_index]['show_immediately'] = True
    
    def add_pending_message(self, sender, message, is_ai=False):
        """Add a message that will be hidden until show_message is called"""
        return self.add_message(sender, message, is_ai, show_immediately=False)
    
    def is_text_chat_enabled(self):
        """Check if text chat is enabled"""
        return self.text_chat_enabled
    
    def handle_action(self, action, data=None):
        """Handle actions from web interface"""
        if self.message_callback:
            self.message_callback(action, data)
    
    def set_personality(self, personality_info, selected_by_user=False):
        """Set current personality information"""
        self.current_personality = personality_info
        self.personality_selected = True
        if selected_by_user:
            self.personality_selected_by_user = True
    
    def get_personality_info(self):
        """Get current personality information"""
        return self.current_personality
    
    def is_personality_selected(self):
        """Check if personality has been selected by user (not just set by system)"""
        return self.personality_selected_by_user
    
    def reset_personality_selection(self):
        """Reset personality selection to show overlay for next cycle"""
        self.personality_selected_by_user = False
        # Keep the current personality info but mark as not user-selected
    
    def is_text_only_mode(self):
        """Check if in text-only mode (no audio processing)"""
        return self.text_only_mode