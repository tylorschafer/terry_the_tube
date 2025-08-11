"""
Audio Recording Handler for Terry the Tube
"""
import os
import time
import subprocess
import keyboard
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import (
    RECORDINGS_DIR, AUDIO_SAMPLE_RATE, AUDIO_CHANNELS, MAX_RECORDING_TIME, 
    MIN_AUDIO_FILE_SIZE, AUDIO_RECORD_COMMAND, RECORDING_TOO_SMALL_ERROR
)


class RecordingHandler:
    def __init__(self):
        """Initialize recording handler"""
        self.recording_process = None
        self.current_recording = None
        self.session_folder = None
        
        # Ensure recordings directory exists
        if not os.path.exists(RECORDINGS_DIR):
            os.makedirs(RECORDINGS_DIR)
    
    def set_session_folder(self, session_folder):
        """Set the session folder for recordings"""
        self.session_folder = session_folder
    
    def record_while_spacebar(self):
        """Record audio while spacebar is held down (terminal mode)"""
        filename = self._generate_filename()
        
        print("Press and hold SPACEBAR to record. Release to stop recording.")
        
        # Wait for spacebar to be pressed
        while not keyboard.is_pressed('space'):
            time.sleep(0.1)
        
        print("Recording... (release SPACEBAR to stop)")
        
        # Start recording
        process = subprocess.Popen(
            AUDIO_RECORD_COMMAND + [filename],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Record until spacebar is released or max time reached
        start_time = time.time()
        while keyboard.is_pressed('space'):
            if time.time() - start_time > MAX_RECORDING_TIME:
                print(f"Maximum recording time reached ({MAX_RECORDING_TIME} seconds)")
                break
            time.sleep(0.1)
        
        # Stop recording
        process.terminate()
        process.wait()
        
        print("Recording finished.")
        
        # Validate recording
        if self._is_valid_recording(filename):
            return filename
        else:
            print(RECORDING_TOO_SMALL_ERROR)
            return None
    
    def start_web_recording(self):
        """Start recording for web interface"""
        filename = self._generate_filename()
        self.current_recording = filename
        
        # Start the recording process
        self.recording_process = subprocess.Popen(
            AUDIO_RECORD_COMMAND + [filename],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        return filename
    
    def stop_web_recording(self):
        """Stop recording for web interface"""
        if self.recording_process:
            self.recording_process.terminate()
            self.recording_process.wait()
            self.recording_process = None
        
        # Validate and return the recording
        if self.current_recording and self._is_valid_recording(self.current_recording):
            filename = self.current_recording
            self.current_recording = None
            return filename
        else:
            self.current_recording = None
            return None
    
    def _generate_filename(self):
        """Generate unique filename for recording"""
        timestamp = int(time.time())
        
        # Use session folder if available, otherwise use main recordings dir
        if self.session_folder and os.path.exists(self.session_folder):
            directory = self.session_folder
        else:
            directory = RECORDINGS_DIR
            
        return os.path.join(directory, f"input_{timestamp}.wav")
    
    def _is_valid_recording(self, filename):
        """Check if recording is valid"""
        return (os.path.exists(filename) and 
                os.path.getsize(filename) > MIN_AUDIO_FILE_SIZE)
    
    def is_recording(self):
        """Check if currently recording"""
        return self.recording_process is not None
    
    def cleanup_old_recordings(self):
        """Clean up old recording files"""
        if os.path.exists(RECORDINGS_DIR):
            for file in os.listdir(RECORDINGS_DIR):
                file_path = os.path.join(RECORDINGS_DIR, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")