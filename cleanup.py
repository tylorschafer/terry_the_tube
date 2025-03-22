import shutil
import os
import glob

# Clean up old recordings, audio files, and transcript files
def cleanup_old_files():
    """Delete all recordings, AI output files, and transcript files at startup"""
    print("Cleaning up old files...")
    
    # Clean up recordings directory
    if os.path.exists("recordings"):
        shutil.rmtree("recordings")
        os.makedirs("recordings")
    else:
        os.makedirs("recordings")
    
    # Clean up audio directory
    if os.path.exists("audio"):
        shutil.rmtree("audio")
        os.makedirs("audio")
    else:
        os.makedirs("audio")
    
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
