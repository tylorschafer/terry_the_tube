"""
Common utilities for Terry the Tube
Eliminates code duplication across modules
"""
import os
import sys
import logging
import hashlib
import time
from functools import lru_cache


def setup_project_path():
    """Add project root to Python path - used in multiple modules"""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    if project_root not in sys.path:
        sys.path.append(project_root)


def setup_logging(name, level=logging.INFO):
    """Standard logging setup used across modules"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    return logging.getLogger(name)


def ensure_directory(path):
    """Ensure directory exists, create if necessary"""
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    return False


def get_cache_key(text, personality=None):
    """Generate consistent cache key for text and personality"""
    content = f"{personality}:{text}" if personality else text
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def safe_file_hash(text, max_length=10000):
    """Generate safe filename hash from text"""
    return abs(hash(text)) % max_length


@lru_cache(maxsize=128)
def get_project_config():
    """Cached project configuration loading"""
    setup_project_path()
    try:
        import config
        return config
    except ImportError as e:
        raise ImportError(f"Could not load project config: {e}")


def handle_model_loading_error(model_name, exception, fallback_fn=None):
    """Standard error handling for model loading failures"""
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to load {model_name}: {exception}")
    
    if fallback_fn:
        try:
            return fallback_fn()
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {fallback_error}")
            raise exception
    else:
        raise exception


def timing_decorator(operation_name):
    """Decorator to add timing logs to functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            logger.info(f"Starting {operation_name}")
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"{operation_name} completed in {duration:.2f} seconds")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{operation_name} failed after {duration:.2f} seconds: {e}")
                raise
        return wrapper
    return decorator


class FileManager:
    """Utility class for common file operations"""
    
    @staticmethod
    def get_unique_filename(directory, prefix, extension, content_hash=None):
        """Generate unique filename in directory"""
        ensure_directory(directory)
        
        if content_hash:
            filename = f"{prefix}_{content_hash}.{extension}"
        else:
            import time
            timestamp = int(time.time() * 1000)
            filename = f"{prefix}_{timestamp}.{extension}"
            
        return os.path.join(directory, filename)
    
    @staticmethod
    def cleanup_old_files(directory, max_age_hours=24, pattern=None):
        """Clean up old files in directory"""
        if not os.path.exists(directory):
            return 0
            
        import time
        import glob
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        removed_count = 0
        
        search_pattern = os.path.join(directory, pattern or "*")
        for filepath in glob.glob(search_pattern):
            try:
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > max_age_seconds:
                    os.remove(filepath)
                    removed_count += 1
            except (OSError, IOError):
                continue
                
        return removed_count