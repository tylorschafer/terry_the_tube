import shutil
import os
import glob

def cleanup_directory(directory_name):
    """Safely clean up a directory, handling permission errors"""
    if os.path.exists(directory_name):
        # Try to remove individual files first
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

# Clean up old recordings, audio files, and transcript files
def cleanup_old_files():
    """Delete all recordings, AI output files, and transcript files at startup"""
    print("Cleaning up old files...")
    
    # Clean up recordings directory
    cleanup_directory("recordings")
    
    # Clean up audio directory  
    cleanup_directory("audio")
    
    # Create transcipts folder
    if not os.path.exists("transcripts"):
        os.makedirs("transcripts")
    else:
        # Clean up existing transcript files
        for file_ext in ['.vtt', '.srt', '.tsv', '.txt', '.json']:
            for file in glob.glob(f"*.{file_ext}"):
                try:
                    # Move to transcripts folder then delete
                    shutil.move(file, os.path.join("transcripts", os.path.basename(file)))
                except Exception as e:
                    print(f"Error moving {file}: {e}")
        
        # Now clean up the transcripts folder
        for file in os.listdir("transcripts"):
            file_path = os.path.join("transcripts", file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
    
    print("Cleanup complete.")
