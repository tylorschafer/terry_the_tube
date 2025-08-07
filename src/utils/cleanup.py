"""
File Cleanup Utilities for Terry the Tube
Refactored and improved cleanup functionality
"""
import os
import glob
import shutil
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import RECORDINGS_DIR, AUDIO_DIR, TRANSCRIPTS_DIR, TRANSCRIPT_EXTENSIONS


class FileCleanup:
    def __init__(self):
        """Initialize file cleanup utility"""
        self.directories_to_clean = [RECORDINGS_DIR, AUDIO_DIR]
        self.transcript_directory = TRANSCRIPTS_DIR
    
    def cleanup_all_files(self):
        """Delete all recordings, audio files, and transcript files at startup"""
        print("Cleaning up old files...")
        
        # Clean up main directories
        for directory in self.directories_to_clean:
            self._cleanup_directory(directory)
        
        # Handle transcripts specially
        self._cleanup_transcripts()
        
        print("Cleanup complete.")
    
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
    
    def ensure_directories_exist(self):
        """Ensure all required directories exist"""
        directories = [RECORDINGS_DIR, AUDIO_DIR, TRANSCRIPTS_DIR]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")


def cleanup_old_files():
    """Legacy function for backward compatibility"""
    cleanup = FileCleanup()
    cleanup.cleanup_all_files()