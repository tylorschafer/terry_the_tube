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
            
        self.fallback_model = None
        self.current_fallback_model_name = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._initialized = True
        
        logger.info(f"TTSModelManager initialized with device: {self.device}")
    
    def get_fallback_model(self, model_name):
        """Get fallback model, loading if necessary"""
        if self.fallback_model is None or self.current_fallback_model_name != model_name:
            self._load_fallback_model(model_name)
        return self.fallback_model
    
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
    
    def is_fallback_available(self):
        """Check if fallback model is loaded and available"""
        return self.fallback_model is not None
    
    def get_model_info(self):
        """Get information about loaded models"""
        return {
            'fallback_model': self.current_fallback_model_name,
            'device': self.device,
            'fallback_available': self.is_fallback_available()
        }
    
    def clear_models(self):
        """Clear all loaded models to free memory"""
            
        if self.fallback_model is not None:
            del self.fallback_model
            self.fallback_model = None
            self.current_fallback_model_name = None
            
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        logger.info("TTS models cleared from memory")