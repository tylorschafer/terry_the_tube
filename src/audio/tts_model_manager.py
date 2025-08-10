"""
TTS Model Manager - Singleton for persistent TTS model loading
Eliminates the 5-10 second model initialization on every TTS generation
"""
import os
import torch
from TTS.api import TTS
import logging
import time
from threading import Lock

logger = logging.getLogger(__name__)


class TTSModelManager:
    """Singleton manager for TTS models to avoid repeated initialization"""
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.xtts_model = None
        self.fallback_model = None
        self.current_xtts_model_name = None
        self.current_fallback_model_name = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._initialized = True
        
        logger.info(f"TTSModelManager initialized with device: {self.device}")
    
    def get_xtts_model(self, model_name):
        """Get XTTS model, loading if necessary"""
        if self.xtts_model is None or self.current_xtts_model_name != model_name:
            self._load_xtts_model(model_name)
        return self.xtts_model
    
    def get_fallback_model(self, model_name):
        """Get fallback model, loading if necessary"""
        if self.fallback_model is None or self.current_fallback_model_name != model_name:
            self._load_fallback_model(model_name)
        return self.fallback_model
    
    def _load_xtts_model(self, model_name):
        """Load XTTS model with all the complex setup"""
        logger.info(f"Loading XTTS model: {model_name}")
        start_time = time.time()
        
        try:
            # Handle PyTorch weights_only loading issue with XTTS V2
            self._setup_pytorch_safe_globals()
            
            # Try with safe globals first
            try:
                self.xtts_model = TTS(model_name, progress_bar=False).to(self.device)
                self.current_xtts_model_name = model_name
                load_time = time.time() - start_time
                logger.info(f"XTTS model loaded successfully in {load_time:.2f} seconds")
                return
            except Exception as e:
                logger.warning(f"XTTS loading with safe globals failed: {e}")
                
            # Try with weights_only=False fallback
            self._try_weights_only_fallback(model_name)
            self.current_xtts_model_name = model_name
            load_time = time.time() - start_time
            logger.info(f"XTTS model loaded with fallback in {load_time:.2f} seconds")
            
        except Exception as e:
            load_time = time.time() - start_time
            logger.error(f"XTTS model loading failed after {load_time:.2f} seconds: {e}")
            self.xtts_model = None
            self.current_xtts_model_name = None
            raise
    
    def _setup_pytorch_safe_globals(self):
        """Setup PyTorch safe globals for XTTS"""
        try:
            from TTS.tts.configs.xtts_config import XttsConfig
            safe_classes = [XttsConfig]
            
            # Add additional XTTS classes if available
            optional_classes = [
                'TTS.tts.models.xtts.XttsAudioConfig',
                'TTS.tts.models.xtts.XttsArgs',
                'TTS.config.shared_configs.BaseDatasetConfig'
            ]
            
            for class_path in optional_classes:
                try:
                    module_path, class_name = class_path.rsplit('.', 1)
                    module = __import__(module_path, fromlist=[class_name])
                    class_obj = getattr(module, class_name)
                    safe_classes.append(class_obj)
                except ImportError:
                    continue
            
            torch.serialization.add_safe_globals(safe_classes)
            logger.info(f"Added {len(safe_classes)} XTTS classes to PyTorch safe globals")
            
        except Exception as e:
            logger.warning(f"Failed to setup safe globals: {e}")
    
    def _try_weights_only_fallback(self, model_name):
        """Try loading with weights_only=False patch"""
        original_load = torch.load
        
        def patched_load(*args, **kwargs):
            kwargs['weights_only'] = False
            return original_load(*args, **kwargs)
        
        try:
            torch.load = patched_load
            self.xtts_model = TTS(model_name, progress_bar=False).to(self.device)
        finally:
            torch.load = original_load
    
    def _load_fallback_model(self, model_name):
        """Load fallback TTS model"""
        logger.info(f"Loading fallback TTS model: {model_name}")
        start_time = time.time()
        
        try:
            self.fallback_model = TTS(model_name, progress_bar=False).to(self.device)
            self.current_fallback_model_name = model_name
            load_time = time.time() - start_time
            logger.info(f"Fallback TTS model loaded in {load_time:.2f} seconds")
        except Exception as e:
            load_time = time.time() - start_time
            logger.error(f"Fallback model loading failed after {load_time:.2f} seconds: {e}")
            self.fallback_model = None
            self.current_fallback_model_name = None
            raise
    
    def is_xtts_available(self):
        """Check if XTTS model is loaded and available"""
        return self.xtts_model is not None
    
    def is_fallback_available(self):
        """Check if fallback model is loaded and available"""
        return self.fallback_model is not None
    
    def get_model_info(self):
        """Get information about loaded models"""
        return {
            'xtts_model': self.current_xtts_model_name,
            'fallback_model': self.current_fallback_model_name,
            'device': self.device,
            'xtts_available': self.is_xtts_available(),
            'fallback_available': self.is_fallback_available()
        }
    
    def clear_models(self):
        """Clear all loaded models to free memory"""
        if self.xtts_model is not None:
            del self.xtts_model
            self.xtts_model = None
            self.current_xtts_model_name = None
            
        if self.fallback_model is not None:
            del self.fallback_model
            self.fallback_model = None
            self.current_fallback_model_name = None
            
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        logger.info("TTS models cleared from memory")