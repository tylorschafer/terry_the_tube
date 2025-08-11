import os
import subprocess
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import (
    VOICE_CLONES_DIR, DEFAULT_VOICE_CLONE,
    TTS_MODELS_TO_TRY, AUDIO_DIR, TTS_FALLBACK_COMMAND, AUDIO_PLAY_COMMAND
)
from utils.display import display
from utils.common import setup_logging, ensure_directory, get_cache_key
from audio.tts_model_manager import TTSModelManager
from audio.tts_cache import TTSCache

logger = setup_logging(__name__)


class TTSHandler:
    def __init__(self):
        """Initialize TTS handler with persistent model manager, API client, and caching"""
        self.model_manager = TTSModelManager()
        self.tts_cache = TTSCache(os.path.join(AUDIO_DIR, 'cache'))
        self.session_folder = None
        self.current_personality = None
        self.voice_clone_path = None
        
        # Create voice clones directory
        ensure_directory(VOICE_CLONES_DIR)
        
        tts_mode = f"Local TTS (device: {self.model_manager.device})"
        logger.info(f"TTS Handler initialized using: {tts_mode}")
    
    def set_session_folder(self, session_folder):
        """Set the session folder for saving TTS audio files"""
        self.session_folder = session_folder
    
    def _get_fallback_model(self):
        """Get fallback model from persistent model manager"""
        for model_name in TTS_MODELS_TO_TRY:
            try:
                return self.model_manager.get_fallback_model(model_name)
            except Exception as e:
                logger.warning(f"Failed to get fallback model {model_name}: {e}")
                continue
        return None
    
    def text_to_speech(self, text):
        """Convert text to speech using voice cloning and play it"""
        self.text_to_speech_with_callback(text, callback=None)
    
    def text_to_speech_with_callback(self, text, callback=None):
        """Convert text to speech using voice cloning and play it with callback when audio is ready"""
        # Create cache key that includes personality for voice cloning
        cache_key = get_cache_key(text, self.current_personality)
        
        # Check cache first
        cached_file = self.tts_cache.get(text, self.current_personality)
        if cached_file:
            logger.info(f"Using cached TTS audio - Text length: {len(text)} chars")
            self._play_audio_file_with_callback(cached_file, callback)
            return
        
        # Generate unique filename - use session folder if available, otherwise use temp directory
        target_dir = self.session_folder if (self.session_folder and os.path.exists(self.session_folder)) else AUDIO_DIR
        ensure_directory(target_dir)
        audio_file = os.path.join(target_dir, f"response_{cache_key[:8]}.wav")
        
        # Try fallback TTS
        fallback_model = self._get_fallback_model()
        if fallback_model is not None:
            try:
                self._generate_fallback_audio(fallback_model, text, audio_file)
                cached_file = self.tts_cache.put(text, self.current_personality, audio_file)
                self._play_audio_file_with_callback(cached_file, callback)
                return
            except Exception as e:
                logger.warning(f"Fallback TTS error: {e}, using macOS say")
        
        # Final fallback to system TTS
        if callback:
            callback()  # Call callback right before system TTS starts
        self._fallback_tts(text)
    
    def _play_audio_file(self, audio_file):
        """Play audio file using system command"""
        subprocess.run(AUDIO_PLAY_COMMAND + [audio_file], check=True)
    
    def _play_audio_file_with_callback(self, audio_file, callback=None):
        """Play audio file with callback triggered when playback starts"""
        if callback:
            callback()  # Call callback right before audio starts playing
        subprocess.run(AUDIO_PLAY_COMMAND + [audio_file], check=True)
    
    def _fallback_tts(self, text):
        """Use system TTS as final fallback"""
        subprocess.run(TTS_FALLBACK_COMMAND + [text], check=True)
    
    def get_current_model(self):
        """Get currently loaded TTS model name"""
        model_info = self.model_manager.get_model_info()
        return model_info.get('xtts_model') or model_info.get('fallback_model')
    
    def is_available(self):
        """Check if any TTS is available"""
        return (self.model_manager.is_fallback_available())
    
    def get_tts_mode(self):
        """Get current TTS mode information"""
        if self.model_manager.is_fallback_available():
            return {
                'mode': 'Fallback TTS',
                'model': self.model_manager.get_model_info().get('fallback_model'),
                'available': True
            }
        else:
            return {
                'mode': 'System TTS',
                'available': True
            }
    
    def get_voice_clone_info(self):
        """Get information about current voice clone setup"""
        return {
            "personality": self.current_personality,
            "voice_clone_path": self.voice_clone_path,
            "voice_clones_dir": VOICE_CLONES_DIR
        }
    
    def _generate_fallback_audio(self, fallback_model, text, audio_file):
        """Generate TTS audio using fallback models"""
        logger.info(f"Starting fallback TTS audio generation - Text length: {len(text)} chars")
        import time
        start_time = time.time()
        
        try:
            if hasattr(fallback_model, 'synthesizer') and \
               hasattr(fallback_model.synthesizer, 'tts_model') and \
               hasattr(fallback_model.synthesizer.tts_model, 'speaker_manager') and \
               fallback_model.synthesizer.tts_model.speaker_manager is not None:
                # Multi-speaker models like VCTK
                speakers = fallback_model.synthesizer.tts_model.speaker_manager.speaker_names
                speaker = speakers[0] if speakers else None
                fallback_model.tts_to_file(text=text, file_path=audio_file, speaker=speaker)
                generation_time = time.time() - start_time
                logger.info(f"Fallback TTS audio generation (multi-speaker) completed in {generation_time:.2f} seconds")
            else:
                # Single speaker models
                fallback_model.tts_to_file(text=text, file_path=audio_file)
                generation_time = time.time() - start_time
                logger.info(f"Fallback TTS audio generation (single speaker) completed in {generation_time:.2f} seconds")
        except Exception as e:
            generation_time = time.time() - start_time
            logger.error(f"Fallback TTS audio generation failed after {generation_time:.2f} seconds: {e}")
            raise