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
    def __init__(self, message_callback=None):
        """Initialize web interface"""
        self.message_callback = message_callback
        self.messages = []
        self.status = "Ready to serve beer!"
        self.port = WEB_PORT
        self.host = WEB_HOST
        
    def add_message(self, sender, message, is_ai=False):
        """Add a message to display"""
        timestamp = time.strftime("%H:%M:%S")
        self.messages.append({
            'sender': sender,
            'message': message,
            'is_ai': is_ai,
            'timestamp': timestamp
        })
        
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
    
    def handle_action(self, action):
        """Handle actions from web interface"""
        if self.message_callback:
            self.message_callback(action)