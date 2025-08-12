import os
import glob
import shutil
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import RECORDINGS_DIR, TRANSCRIPTS_DIR, TRANSCRIPT_EXTENSIONS
from .display import display


class FileCleanup:
    def __init__(self):
        self.directories_to_clean = []  # No directories to clean automatically now - all files saved in sessions
        self.transcript_directory = TRANSCRIPTS_DIR
        self.recordings_directory = RECORDINGS_DIR
    
    def cleanup_all_files(self):
        """Clean up transcript files at startup (preserves all session data)"""
        # Handle transcripts specially
        self._cleanup_transcripts()
        
        # Ensure recordings directory exists (but don't clean it)
        self._ensure_recordings_directory_exists()
    
    def cleanup_recordings(self):
        """Clean up recordings directory (call this manually when needed)"""
        print("Cleaning up recordings directory...")
        self._cleanup_directory(self.recordings_directory)
        print("Recordings cleanup complete.")
    
    def _ensure_recordings_directory_exists(self):
        """Ensure recordings directory exists without cleaning it"""
        if not os.path.exists(self.recordings_directory):
            os.makedirs(self.recordings_directory)
    
    def _cleanup_directory(self, directory_name):
        """Safely clean up a directory, handling permission errors"""
        if os.path.exists(directory_name):
            try:
                for filename in os.listdir(directory_name):
                    file_path = os.path.join(directory_name, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except PermissionError as e:
                        print(f"Permission denied, skipping {file_path}: {e}")
                    except Exception as e:
                        print(f"Error removing {file_path}: {e}")
            except Exception as e:
                print(f"Error accessing directory {directory_name}: {e}")
        else:
            os.makedirs(directory_name)
    
    def _cleanup_transcripts(self):
        """Clean up transcript files with special handling"""
        # Create transcripts folder if it doesn't exist
        if not os.path.exists(self.transcript_directory):
            os.makedirs(self.transcript_directory)
            return
        
        # Move any transcript files from root to transcripts folder, then clean
        for file_ext in TRANSCRIPT_EXTENSIONS:
            pattern = f"*.{file_ext.lstrip('.')}"
            for file in glob.glob(pattern):
                try:
                    target_path = os.path.join(self.transcript_directory, os.path.basename(file))
                    shutil.move(file, target_path)
                except Exception as e:
                    print(f"Error moving {file}: {e}")
        
        # Now clean up the transcripts folder
        self._cleanup_directory(self.transcript_directory)
    
    def cleanup_specific_directory(self, directory_path):
        """Clean up a specific directory"""
        self._cleanup_directory(directory_path)
    
    def cleanup_conversation_session(self, session_folder_name):
        """Clean up a specific conversation session folder"""
        session_path = os.path.join(self.recordings_directory, session_folder_name)
        if os.path.exists(session_path):
            print(f"Cleaning up conversation session: {session_folder_name}")
            self._cleanup_directory(session_path)
            # Remove the empty directory
            try:
                os.rmdir(session_path)
                print(f"Removed session folder: {session_path}")
            except Exception as e:
                print(f"Error removing session folder {session_path}: {e}")
        else:
            print(f"Session folder not found: {session_path}")
    
    def list_conversation_sessions(self):
        """List all conversation session folders"""
        if os.path.exists(self.recordings_directory):
            sessions = [d for d in os.listdir(self.recordings_directory) 
                       if os.path.isdir(os.path.join(self.recordings_directory, d))]
            return sorted(sessions)
        return []
    
    def ensure_directories_exist(self):
        """Ensure all required directories exist"""
        directories = [RECORDINGS_DIR, TRANSCRIPTS_DIR]  # Removed AUDIO_DIR - no longer needed
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")


def cleanup_old_files():
    """Legacy function for backward compatibility"""
    cleanup = FileCleanup()
    cleanup.cleanup_all_files()