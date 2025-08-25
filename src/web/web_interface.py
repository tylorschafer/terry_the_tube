import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import WEB_PORT, WEB_HOST

# Import the template system
from .web_templates import get_main_html_template


class WebInterface:
    def __init__(self, message_callback=None, enable_text_chat=False, text_only_mode=False):
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
        self.websocket_manager = None  # Will be set by web server
        
    def add_message(self, sender, message, is_ai=False, show_immediately=True):
        timestamp = time.strftime("%H:%M:%S")
        message_obj = {
            'sender': sender,
            'message': message,
            'is_ai': is_ai,
            'timestamp': timestamp,
            'show_immediately': show_immediately
        }
        self.messages.append(message_obj)
        self._notify_state_change()
        return len(self.messages) - 1  # Return message index
        
    def set_status(self, status):
        self.status = status
        self._notify_state_change()
    
    def clear_messages(self):
        self.messages = []
        self._notify_state_change()
    
    def get_messages(self):
        return self.messages.copy()
    
    def get_status(self):
        return self.status
    
    def set_generating_audio(self, generating):
        self.generating_audio = generating
        self._notify_state_change()
    
    def is_generating_audio(self):
        return self.generating_audio
    
    def set_generating_response(self, generating):
        self.generating_response = generating
        self._notify_state_change()
    
    def is_generating_response(self):
        return self.generating_response
    
    def show_message(self, message_index):
        if 0 <= message_index < len(self.messages):
            self.messages[message_index]['show_immediately'] = True
            self._notify_state_change()
    
    def add_pending_message(self, sender, message, is_ai=False):
        return self.add_message(sender, message, is_ai, show_immediately=False)
    
    def is_text_chat_enabled(self):
        return self.text_chat_enabled
    
    def is_text_only_mode(self):
        return self.text_only_mode
    
    def handle_action(self, action, data=None):
        if self.message_callback:
            self.message_callback(action, data)
    
    def set_personality(self, personality_info, selected_by_user=False):
        self.current_personality = personality_info
        self.personality_selected = True
        if selected_by_user:
            self.personality_selected_by_user = True
        self._notify_state_change()
    
    def get_personality_info(self):
        return self.current_personality
    
    def is_personality_selected(self):
        return self.personality_selected_by_user
    
    def reset_personality_selection(self):
        self.personality_selected_by_user = False
        # Keep the current personality info but mark as not user-selected
    
    def is_text_only_mode(self):
        """Check if in text-only mode (no audio processing)"""
        return self.text_only_mode
    
    def set_websocket_manager(self, websocket_manager):
        """Set the WebSocket manager for real-time updates"""
        self.websocket_manager = websocket_manager
    
    def _notify_state_change(self):
        """Notify WebSocket clients of state changes"""
        if self.websocket_manager:
            self.websocket_manager.notify_state_change()
    
    def get_html_template(self):
        """Get the HTML template for the web interface"""
        return get_main_html_template(text_only_mode=self.text_only_mode)