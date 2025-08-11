"""
Advanced TTS Cache with automatic cleanup and persistence
Improves performance by avoiding redundant audio generation
"""
import os
import json
import time
import threading
from pathlib import Path
from utils.common import setup_logging, ensure_directory, get_cache_key

logger = setup_logging(__name__)


class TTSCache:
    """Advanced TTS caching with metadata and automatic cleanup"""
    
    def __init__(self, cache_dir, max_size_mb=100, max_age_hours=24):
        self.cache_dir = Path(cache_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024  # Convert to bytes
        self.max_age_seconds = max_age_hours * 3600
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.cache_metadata = {}
        self._lock = threading.Lock()
        
        ensure_directory(str(self.cache_dir))
        self._load_metadata()
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def get(self, text, personality=None):
        """Get cached audio file path if exists and valid"""
        cache_key = get_cache_key(text, personality)
        
        with self._lock:
            if cache_key in self.cache_metadata:
                metadata = self.cache_metadata[cache_key]
                file_path = self.cache_dir / metadata['filename']
                
                # Check if file exists and is not too old
                if file_path.exists():
                    age = time.time() - metadata['created_at']
                    if age < self.max_age_seconds:
                        # Update last accessed time
                        metadata['last_accessed'] = time.time()
                        self._save_metadata()
                        logger.debug(f"Cache hit for key: {cache_key[:8]}...")
                        return str(file_path)
                    else:
                        logger.debug(f"Cache entry expired for key: {cache_key[:8]}...")
                        self._remove_cache_entry(cache_key)
                else:
                    logger.debug(f"Cache file missing for key: {cache_key[:8]}...")
                    self._remove_cache_entry(cache_key)
        
        logger.debug(f"Cache miss for key: {cache_key[:8]}...")
        return None
    
    def put(self, text, personality, audio_file_path):
        """Add audio file to cache"""
        cache_key = get_cache_key(text, personality)
        
        if not os.path.exists(audio_file_path):
            logger.warning(f"Cannot cache non-existent file: {audio_file_path}")
            return
        
        # Generate cache filename
        cache_filename = f"{cache_key[:16]}.wav"
        cache_file_path = self.cache_dir / cache_filename
        
        try:
            # Copy file to cache directory if not already there
            if str(cache_file_path) != audio_file_path:
                import shutil
                shutil.copy2(audio_file_path, cache_file_path)
            
            # Add metadata
            with self._lock:
                file_size = cache_file_path.stat().st_size
                self.cache_metadata[cache_key] = {
                    'filename': cache_filename,
                    'text_length': len(text),
                    'personality': personality,
                    'file_size': file_size,
                    'created_at': time.time(),
                    'last_accessed': time.time()
                }
                self._save_metadata()
                logger.info(f"Cached audio file: {cache_filename} (Size: {file_size} bytes)")
                
                # Check if we need cleanup
                self._cleanup_if_needed()
                
            return str(cache_file_path)
            
        except Exception as e:
            logger.error(f"Failed to cache audio file: {e}")
            return audio_file_path
    
    def _load_metadata(self):
        """Load cache metadata from disk"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    self.cache_metadata = json.load(f)
                logger.info(f"Loaded {len(self.cache_metadata)} cache entries")
            else:
                self.cache_metadata = {}
        except Exception as e:
            logger.warning(f"Failed to load cache metadata: {e}")
            self.cache_metadata = {}
    
    def _save_metadata(self):
        """Save cache metadata to disk"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.cache_metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache metadata: {e}")
    
    def _remove_cache_entry(self, cache_key):
        """Remove a cache entry and its file"""
        if cache_key in self.cache_metadata:
            metadata = self.cache_metadata[cache_key]
            file_path = self.cache_dir / metadata['filename']
            
            try:
                if file_path.exists():
                    file_path.unlink()
                del self.cache_metadata[cache_key]
                logger.debug(f"Removed cache entry: {cache_key[:8]}...")
            except Exception as e:
                logger.warning(f"Failed to remove cache entry {cache_key[:8]}...: {e}")
    
    def _cleanup_if_needed(self):
        """Cleanup cache if it exceeds size limits"""
        total_size = sum(metadata['file_size'] for metadata in self.cache_metadata.values())
        
        if total_size > self.max_size_bytes:
            logger.info(f"Cache size ({total_size / 1024 / 1024:.1f}MB) exceeds limit, cleaning up...")
            
            # Sort by last accessed time (oldest first)
            entries_by_age = sorted(
                self.cache_metadata.items(),
                key=lambda x: x[1]['last_accessed']
            )
            
            # Remove oldest entries until we're under the limit
            for cache_key, metadata in entries_by_age:
                self._remove_cache_entry(cache_key)
                total_size -= metadata['file_size']
                
                if total_size <= self.max_size_bytes * 0.8:  # Clean to 80% of limit
                    break
            
            self._save_metadata()
            logger.info(f"Cache cleanup complete. New size: {total_size / 1024 / 1024:.1f}MB")
    
    def _start_cleanup_thread(self):
        """Start background thread for periodic cleanup"""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(3600)  # Check every hour
                    current_time = time.time()
                    
                    with self._lock:
                        expired_keys = []
                        for cache_key, metadata in self.cache_metadata.items():
                            age = current_time - metadata['created_at']
                            if age > self.max_age_seconds:
                                expired_keys.append(cache_key)
                        
                        for cache_key in expired_keys:
                            self._remove_cache_entry(cache_key)
                        
                        if expired_keys:
                            self._save_metadata()
                            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
                            
                except Exception as e:
                    logger.error(f"Cache cleanup thread error: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.info("Started TTS cache cleanup thread")
    
    def get_stats(self):
        """Get cache statistics"""
        with self._lock:
            total_size = sum(metadata['file_size'] for metadata in self.cache_metadata.values())
            return {
                'entries': len(self.cache_metadata),
                'total_size_mb': total_size / 1024 / 1024,
                'max_size_mb': self.max_size_bytes / 1024 / 1024,
                'max_age_hours': self.max_age_seconds / 3600
            }
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            for cache_key in list(self.cache_metadata.keys()):
                self._remove_cache_entry(cache_key)
            self._save_metadata()
            logger.info("Cache cleared")