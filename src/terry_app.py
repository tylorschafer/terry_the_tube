"""
Main Terry the Tube Application
Orchestrates all components and handles different interface modes
"""
import os
import threading
import warnings
from core.ai_handler import AIHandler
from core.conversation_manager import ConversationManager
from audio.audio_manager import AudioManager
from audio.mock_audio_manager import MockAudioManager
from web.web_interface import WebInterface
from web.web_server import start_web_server
from utils.cleanup import FileCleanup
from utils.display import display
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import (
    STT_ERROR_MESSAGE, STT_TECHNICAL_ERROR, 
    TRANSCRIPTION_FAILED_ERROR, RECORDING_FAILED_WEB_ERROR,
    ENABLE_TEXT_CHAT, TEXT_CHAT_ONLY
)

# Filter out TTS/Whisper warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")


class TerryTubeApp:
    def __init__(self, use_web_gui=True, personality_key=None, enable_text_chat=False, text_only_mode=False):
        """Initialize Terry the Tube application"""
        self.use_web_gui = use_web_gui
        self.personality_key = personality_key
        self.enable_text_chat = enable_text_chat
        self.text_only_mode = text_only_mode
        self.web_interface = None
        self.recording_in_progress = False
        self.current_audio_file = None
        
        # Initialize components
        self._initialize_components()
        
        # Setup web interface if needed
        if self.use_web_gui:
            self.web_interface = WebInterface(message_callback=self.handle_web_action)
            # Set initial personality info
            if self.ai_handler:
                # If personality was explicitly provided, mark as user-selected to skip overlay
                user_selected = self.personality_key is not None
                self.web_interface.set_personality(self.ai_handler.get_personality_info(), selected_by_user=user_selected)
    
    def _initialize_components(self):
        """Initialize all core components"""
        try:
            display.section("Initializing Components")
            
            # Initialize audio manager
            display.component_init("Audio Manager")
            self.audio_manager = AudioManager()
            
            # Initialize AI handler with personality
            display.component_init("AI Handler")
            self.ai_handler = AIHandler(personality_key=self.personality_key)
            
            # Initialize conversation manager
            display.component_init("Conversation Manager")
            self.conversation_manager = ConversationManager(
                self.ai_handler, 
                self.audio_manager,
                self.web_interface
            )
            
            display.success("All components initialized successfully!")
            
        except Exception as e:
            display.error(f"Error initializing components: {e}")
            raise
    
    def handle_web_action(self, action, data=None):
        """Handle actions from the web interface"""
        if action == 'start_recording':
            self.start_recording()
        elif action == 'stop_recording':
            self.stop_recording()
        elif action == 'send_text_message':
            if data and 'message' in data:
                self.process_text_message(data['message'])
        elif action == 'change_personality':
            if data and 'personality' in data:
                self.change_personality(data['personality'])
    
    def start_recording(self):
        """Start recording audio"""
        if not self.recording_in_progress:
            self.recording_in_progress = True
            
            # Prepare session folder before starting recording
            self.conversation_manager.prepare_session_if_needed()
            
            if self.use_web_gui:
                self.current_audio_file = self.audio_manager.start_web_recording()
            else:
                self.current_audio_file = self.audio_manager.record_while_spacebar()
    
    def stop_recording(self):
        """Stop recording and process the audio"""
        if self.recording_in_progress:
            self.recording_in_progress = False
            
            if self.use_web_gui:
                audio_file = self.audio_manager.stop_web_recording()
                if audio_file:
                    threading.Thread(
                        target=self.process_user_input, 
                        args=(audio_file,), 
                        daemon=True
                    ).start()
                else:
                    self._set_status(RECORDING_FAILED_WEB_ERROR)
            else:
                if self.current_audio_file:
                    self.process_user_input(self.current_audio_file)
    
    def process_text_message(self, text_message):
        """Process user input from text message"""
        if not text_message.strip():
            return
        
        display.user_input(text_message)
        self._add_message("You", text_message, is_ai=False)
        
        # Process the text input through conversation manager
        self.conversation_manager.add_user_message(text_message)
        self.conversation_manager.generate_and_handle_response()
    
    def process_user_input(self, audio_file):
        """Process user input from audio file"""
        self._set_status("Transcribing your speech...")
        
        display.transcribing()
        user_input = self.audio_manager.speech_to_text(audio_file)
        
        # Handle display of user input
        if user_input == "":
            # Show silence in the interface but pass empty string to bot
            display_message = "silence"
            display.user_input("", is_silence=True)
        else:
            display_message = user_input
            display.user_input(user_input)
            
        self._add_message("You", display_message, is_ai=False)
        
        # Handle technical transcription errors (but allow empty strings for silence)
        if user_input == STT_TECHNICAL_ERROR:
            self._set_status(TRANSCRIPTION_FAILED_ERROR)
            if not self.use_web_gui:
                display.error("Failed to understand your speech. Please type your response:")
                user_input = input("You: ")
        
        # Process the input through conversation manager (including empty strings)
        self.conversation_manager.add_user_message(user_input)
        self.conversation_manager.generate_and_handle_response()
    
    def run_web_mode(self):
        """Run the application with web interface"""
        display.header("Terry the Tube - Web Mode")
        
        # Clean up old files
        cleanup = FileCleanup()
        display.cleanup_start()
        cleanup.cleanup_all_files()
        display.cleanup_complete()
        
        try:
            # Update conversation manager with web interface
            self.conversation_manager.web_interface = self.web_interface
            
            # Only start conversation if personality was explicitly selected (via CLI or user selection)
            if self.web_interface.is_personality_selected():
                self.conversation_manager.start_conversation()
            
            # Start web server (blocking)
            display.info(f"Web interface started at: http://localhost:8080")
            start_web_server(self.web_interface)
            
        except Exception as e:
            display.error(f"Web interface failed: {e}")
            display.warning("Falling back to terminal mode...")
            self.run_terminal_mode()
    
    def run_terminal_mode(self):
        """Run the application in terminal-only mode"""
        display.header("Terry the Tube - Terminal Mode")
        
        # Clean up old files
        cleanup = FileCleanup()
        display.cleanup_start()
        cleanup.cleanup_all_files()
        display.cleanup_complete()
        
        # Start conversation
        self.conversation_manager.start_conversation()
        
        # Main conversation loop
        while True:
            try:
                display.separator()
                display.recording_start()
                
                audio_file = self.audio_manager.record_while_spacebar()
                
                if audio_file:
                    display.recording_stop()
                    self.process_user_input(audio_file)
                else:
                    display.warning("Recording failed or was too quiet. Please type your response:")
                    user_input = input("You: ")
                    display.user_input(user_input)
                    self.conversation_manager.add_user_message(user_input)
                    self.conversation_manager.generate_and_handle_response()
                    
            except KeyboardInterrupt:
                display.warning("\nShutting down Terry the Tube...")
                break
            except Exception as e:
                display.error(f"Error in conversation loop: {e}")
                continue
    
    def _add_message(self, sender, message, is_ai=False):
        """Helper method to add message to web interface"""
        if self.web_interface:
            self.web_interface.add_message(sender, message, is_ai=is_ai)
    
    def _set_status(self, status):
        """Helper method to set status on web interface"""
        if self.web_interface:
            self.web_interface.set_status(status)
    
    def change_personality(self, personality_key):
        """Change the AI personality"""
        try:
            # Reinitialize AI handler with new personality
            self.ai_handler = AIHandler(personality_key=personality_key)
            
            # Update conversation manager with new AI handler
            self.conversation_manager.ai_handler = self.ai_handler
            
            # Store the current personality key
            self.personality_key = personality_key
            
            # Update web interface with new personality info (marked as user-selected)
            if self.web_interface:
                self.web_interface.set_personality(self.ai_handler.get_personality_info(), selected_by_user=True)
            
            # Restart conversation with new personality
            self.conversation_manager.start_conversation()
            
            display.success(f"Personality changed to: {self.ai_handler.get_personality_info()['name']}")
            return True
            
        except Exception as e:
            display.error(f"Failed to change personality: {e}")
            return False
    
    def get_personality_info(self):
        """Get current personality information"""
        if self.ai_handler:
            return self.ai_handler.get_personality_info()
        return None
    
    def get_system_info(self):
        """Get system information for debugging"""
        audio_info = self.audio_manager.get_system_info()
        ai_available = self.ai_handler.is_model_available()
        personality_info = self.get_personality_info()
        
        return {
            "audio": audio_info,
            "ai_available": ai_available,
            "web_mode": self.use_web_gui,
            "personality": personality_info
        }