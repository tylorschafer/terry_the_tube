"""
Text-to-Speech Handler for Terry the Tube using XTTS V2
"""
import os
import subprocess
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import (
    XTTS_MODEL_NAME, USE_XTTS_V2, VOICE_CLONES_DIR, DEFAULT_VOICE_CLONE,
    TTS_MODELS_TO_TRY, AUDIO_DIR, TTS_FALLBACK_COMMAND, AUDIO_PLAY_COMMAND,
    USE_XTTS_API_SERVER, XTTS_API_SERVER_URL
)
from utils.display import display
from utils.common import setup_logging, ensure_directory, get_cache_key
from audio.tts_model_manager import TTSModelManager
from audio.tts_cache import TTSCache
from audio.xtts_api_client import XTTSAPIClient

logger = setup_logging(__name__)


class TTSHandler:
    def __init__(self):
        """Initialize TTS handler with persistent model manager, API client, and caching"""
        self.model_manager = TTSModelManager()
        self.tts_cache = TTSCache(os.path.join(AUDIO_DIR, 'cache'))
        self.session_folder = None
        self.current_personality = None
        self.voice_clone_path = None
        
        # Initialize XTTS API client if enabled
        self.api_client = None
        self.api_available = False
        if USE_XTTS_API_SERVER:
            try:
                self.api_client = XTTSAPIClient()
                self.api_available = self.api_client.health_check()
                if self.api_available:
                    # Try to set the XTTS model
                    self.api_client.set_model("xtts")
                    logger.info("XTTS API server is ready and will be used for TTS generation")
                else:
                    logger.warning("XTTS API server is not available, falling back to local TTS")
            except Exception as e:
                logger.warning(f"Failed to initialize XTTS API client: {e}")
                self.api_available = False
        
        # Create voice clones directory
        ensure_directory(VOICE_CLONES_DIR)
        
        tts_mode = "XTTS API Server" if self.api_available else f"Local TTS (device: {self.model_manager.device})"
        logger.info(f"TTS Handler initialized using: {tts_mode}")
    
    def set_session_folder(self, session_folder):
        """Set the session folder for saving TTS audio files"""
        self.session_folder = session_folder
    
    def set_personality_voice(self, personality_key):
        """Set the voice clone file for the current personality"""
        self.current_personality = personality_key
        
        # Look for personality-specific voice clone file
        voice_filename = f"{personality_key}.wav"
        voice_path = os.path.join(VOICE_CLONES_DIR, voice_filename)
        
        if os.path.exists(voice_path):
            self.voice_clone_path = voice_path
            print(f"Using voice clone for {personality_key}: {voice_path}")
        else:
            # Try default voice clone
            default_path = os.path.join(VOICE_CLONES_DIR, DEFAULT_VOICE_CLONE)
            if os.path.exists(default_path):
                self.voice_clone_path = default_path
                print(f"Using default voice clone for {personality_key}: {default_path}")
            else:
                self.voice_clone_path = None
                print(f"No voice clone found for {personality_key}, will use XTTS default voice")
    
    def _get_xtts_model(self):
        """Get XTTS model from persistent model manager"""
        if USE_XTTS_V2:
            try:
                return self.model_manager.get_xtts_model(XTTS_MODEL_NAME)
            except Exception as e:
                logger.warning(f"Failed to get XTTS model: {e}")
                return None
        return None
    
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
        
        # Try XTTS API server first if available
        if self.api_available and self.api_client:
            try:
                logger.info("Generating XTTS audio via API server...")
                result_file = self._generate_api_audio(text, audio_file)
                if result_file:
                    cached_file = self.tts_cache.put(text, self.current_personality, result_file)
                    logger.info("XTTS API audio generation complete, starting playback...")
                    self._play_audio_file_with_callback(cached_file, callback)
                    return
                else:
                    logger.warning("XTTS API generation failed, trying local XTTS...")
            except Exception as e:
                logger.warning(f"XTTS API error: {e}, trying local XTTS...")
        
        # Try local XTTS V2 with voice cloning
        xtts_model = self._get_xtts_model()
        if xtts_model is not None:
            try:
                logger.info("Generating local XTTS V2 audio...")
                self._generate_xtts_audio(xtts_model, text, audio_file)
                cached_file = self.tts_cache.put(text, self.current_personality, audio_file)
                logger.info("Local XTTS V2 audio generation complete, starting playback...")
                self._play_audio_file_with_callback(cached_file, callback)
                return
            except Exception as e:
                logger.warning(f"Local XTTS V2 error: {e}, trying fallback TTS...")
        
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
    
    def _generate_xtts_audio(self, xtts_model, text, audio_file):
        """Generate TTS audio using XTTS V2 with voice cloning"""
        logger.info(f"Starting XTTS audio generation - Text length: {len(text)} chars")
        import time
        start_time = time.time()
        
        try:
            if self.voice_clone_path and os.path.exists(self.voice_clone_path):
                # Use voice cloning
                logger.info(f"Generating XTTS audio with voice clone: {self.voice_clone_path}")
                xtts_model.tts_to_file(
                    text=text,
                    file_path=audio_file,
                    speaker_wav=self.voice_clone_path,
                    language="en",
                    speed=1.5
                )
                generation_time = time.time() - start_time
                logger.info(f"XTTS audio generation (voice clone) completed in {generation_time:.2f} seconds")
            else:
                # Use default XTTS voice
                logger.info("Generating XTTS audio with default voice")
                xtts_model.tts_to_file(
                    text=text,
                    file_path=audio_file,
                    language="en"
                )
                generation_time = time.time() - start_time
                logger.info(f"XTTS audio generation (default voice) completed in {generation_time:.2f} seconds")
        except Exception as e:
            generation_time = time.time() - start_time
            logger.error(f"XTTS audio generation failed after {generation_time:.2f} seconds: {e}")
            raise
    
    def _generate_api_audio(self, text, audio_file):
        """Generate TTS audio using XTTS API server"""
        logger.info(f"Starting XTTS API audio generation - Text length: {len(text)} chars")
        import time
        start_time = time.time()
        
        try:
            result_file = self.api_client.generate_speech(
                text=text,
                speaker_wav_path=self.voice_clone_path,
                language="en",
                output_path=audio_file
            )
            
            if result_file and os.path.exists(result_file):
                generation_time = time.time() - start_time
                voice_type = "voice clone" if self.voice_clone_path else "default voice"
                logger.info(f"XTTS API audio generation ({voice_type}) completed in {generation_time:.2f} seconds")
                return result_file
            else:
                generation_time = time.time() - start_time
                logger.error(f"XTTS API audio generation failed - no file generated after {generation_time:.2f} seconds")
                return None
                
        except Exception as e:
            generation_time = time.time() - start_time
            logger.error(f"XTTS API audio generation failed after {generation_time:.2f} seconds: {e}")
            return None
    
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
    
    def is_xtts_available(self):
        """Check if XTTS is available (API server or local)"""
        return self.api_available or self.model_manager.is_xtts_available()
    
    def is_available(self):
        """Check if any TTS is available"""
        return (self.api_available or 
                self.model_manager.is_xtts_available() or 
                self.model_manager.is_fallback_available())
    
    def get_tts_mode(self):
        """Get current TTS mode information"""
        if self.api_available:
            return {
                'mode': 'API Server',
                'url': XTTS_API_SERVER_URL,
                'available': True
            }
        elif self.model_manager.is_xtts_available():
            return {
                'mode': 'Local XTTS',
                'model': self.model_manager.get_model_info().get('xtts_model'),
                'available': True
            }
        elif self.model_manager.is_fallback_available():
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
    
    def refresh_api_connection(self):
        """Refresh XTTS API server connection"""
        if USE_XTTS_API_SERVER and self.api_client:
            self.api_available = self.api_client.health_check()
            if self.api_available:
                self.api_client.set_model("xtts")
                logger.info("XTTS API server connection refreshed")
            else:
                logger.warning("XTTS API server is not responding")
            return self.api_available
        return False
    
    def clear_cache(self):
        """Clear TTS cache"""
        self.tts_cache.clear()
        logger.info("TTS cache cleared")
    
    def get_cache_stats(self):
        """Get TTS cache statistics"""
        return self.tts_cache.get_stats()
    
    def get_voice_clone_info(self):
        """Get information about current voice clone setup"""
        return {
            "personality": self.current_personality,
            "voice_clone_path": self.voice_clone_path,
            "xtts_available": self.is_xtts_available(),
            "voice_clones_dir": VOICE_CLONES_DIR
        }