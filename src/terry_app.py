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
from web.web_interface import WebInterface
from web.web_server import start_web_server
from utils.cleanup import FileCleanup
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import (
    STT_ERROR_MESSAGE, STT_TECHNICAL_ERROR, 
    TRANSCRIPTION_FAILED_ERROR, RECORDING_FAILED_WEB_ERROR
)

# Filter out TTS/Whisper warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")


class TerryTubeApp:
    def __init__(self, use_web_gui=True):
        """Initialize Terry the Tube application"""
        self.use_web_gui = use_web_gui
        self.web_interface = None
        self.recording_in_progress = False
        self.current_audio_file = None
        
        # Initialize components
        self._initialize_components()
        
        # Setup web interface if needed
        if self.use_web_gui:
            self.web_interface = WebInterface(message_callback=self.handle_web_action)
    
    def _initialize_components(self):
        """Initialize all core components"""
        try:
            print("Initializing Terry the Tube components...")
            
            # Initialize audio manager
            self.audio_manager = AudioManager()
            
            # Initialize AI handler
            self.ai_handler = AIHandler()
            
            # Initialize conversation manager
            self.conversation_manager = ConversationManager(
                self.ai_handler, 
                self.audio_manager,
                self.web_interface
            )
            
            print("All components initialized successfully!")
            
        except Exception as e:
            print(f"Error initializing components: {e}")
            raise
    
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
    
    def process_user_input(self, audio_file):
        """Process user input from audio file"""
        self._set_status("Transcribing your speech...")
        
        print("Transcribing your speech...")
        user_input = self.audio_manager.speech_to_text(audio_file)
        
        self._add_message("You", user_input, is_ai=False)
        print(f"You (transcribed): {user_input}")
        
        # Handle transcription errors
        if user_input in [STT_ERROR_MESSAGE, STT_TECHNICAL_ERROR]:
            self._set_status(TRANSCRIPTION_FAILED_ERROR)
            if not self.use_web_gui:
                print("Failed to understand your speech. Please type your response:")
                user_input = input("You: ")
        
        # Process the input through conversation manager
        self.conversation_manager.add_user_message(user_input)
        self.conversation_manager.generate_and_handle_response()
    
    def run_web_mode(self):
        """Run the application with web interface"""
        print("Terry the Tube activated! Starting web interface...")
        
        # Clean up old files
        cleanup = FileCleanup()
        cleanup.cleanup_all_files()
        
        try:
            # Update conversation manager with web interface
            self.conversation_manager.web_interface = self.web_interface
            
            # Start conversation
            self.conversation_manager.start_conversation()
            
            # Start web server (blocking)
            start_web_server(self.web_interface)
            
        except Exception as e:
            print(f"Web interface failed: {e}")
            print("Falling back to terminal mode...")
            self.run_terminal_mode()
    
    def run_terminal_mode(self):
        """Run the application in terminal-only mode"""
        print("Terry the Tube activated! Ready to interact with humans.")
        
        # Clean up old files
        cleanup = FileCleanup()
        cleanup.cleanup_all_files()
        
        # Start conversation
        self.conversation_manager.start_conversation()
        
        # Main conversation loop
        while True:
            try:
                print("\n" + "="*50)
                print("YOUR TURN TO SPEAK - PRESS AND HOLD SPACEBAR")
                print("="*50 + "\n")
                
                audio_file = self.audio_manager.record_while_spacebar()
                
                if audio_file:
                    self.process_user_input(audio_file)
                else:
                    print("Recording failed or was too quiet. Please type your response:")
                    user_input = input("You: ")
                    self.conversation_manager.add_user_message(user_input)
                    self.conversation_manager.generate_and_handle_response()
                    
            except KeyboardInterrupt:
                print("\nShutting down Terry the Tube...")
                break
            except Exception as e:
                print(f"Error in conversation loop: {e}")
                continue
    
    def _add_message(self, sender, message, is_ai=False):
        """Helper method to add message to web interface"""
        if self.web_interface:
            self.web_interface.add_message(sender, message, is_ai=is_ai)
    
    def _set_status(self, status):
        """Helper method to set status on web interface"""
        if self.web_interface:
            self.web_interface.set_status(status)
    
    def get_system_info(self):
        """Get system information for debugging"""
        audio_info = self.audio_manager.get_system_info()
        ai_available = self.ai_handler.is_model_available()
        
        return {
            "audio": audio_info,
            "ai_available": ai_available,
            "web_mode": self.use_web_gui
        }