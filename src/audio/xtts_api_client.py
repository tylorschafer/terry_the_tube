"""
XTTS API Server Client
High-performance TTS using external XTTS API server
https://github.com/daswer123/xtts-api-server
"""
import os
import requests
import json
import base64
from pathlib import Path
from utils.common import setup_logging, timing_decorator
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import XTTS_API_SERVER_URL, XTTS_API_TIMEOUT, XTTS_API_RETRIES

logger = setup_logging(__name__)


class XTTSAPIClient:
    """Client for XTTS API Server with voice cloning support"""
    
    def __init__(self, base_url=None, timeout=None, retries=None):
        self.base_url = (base_url or XTTS_API_SERVER_URL).rstrip('/')
        self.timeout = timeout or XTTS_API_TIMEOUT
        self.retries = retries or XTTS_API_RETRIES
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Terry-the-Tube/1.0'
        })
        
        logger.info(f"XTTS API Client initialized: {self.base_url}")
    
    @timing_decorator("XTTS API health check")
    def health_check(self):
        """Check if XTTS API server is available and responsive"""
        try:
            response = self.session.get(
                f"{self.base_url}/docs", 
                timeout=5  # Quick health check
            )
            if response.status_code == 200:
                logger.info("XTTS API server is healthy")
                return True
            else:
                logger.warning(f"XTTS API server returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.warning(f"XTTS API server health check failed: {e}")
            return False
    
    def get_models(self):
        """Get available models from XTTS API server"""
        try:
            response = self.session.get(
                f"{self.base_url}/models",
                timeout=self.timeout
            )
            response.raise_for_status()
            models = response.json()
            logger.info(f"Available XTTS models: {models}")
            return models
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get models from XTTS API: {e}")
            return []
    
    def set_model(self, model_name="xtts"):
        """Set the active XTTS model"""
        try:
            response = self.session.post(
                f"{self.base_url}/set_model",
                json={"model_name": model_name},
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"Successfully set XTTS model to: {model_name}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to set XTTS model {model_name}: {e}")
            return False
    
    @timing_decorator("XTTS API TTS generation")
    def generate_speech(self, text, speaker_wav_path=None, language="en", output_path=None):
        """
        Generate speech using XTTS API server
        
        Args:
            text: Text to synthesize
            speaker_wav_path: Path to speaker reference audio for voice cloning
            language: Language code (default: "en")
            output_path: Where to save the generated audio file
            
        Returns:
            Path to generated audio file or None if failed
        """
        for attempt in range(self.retries + 1):
            try:
                # Prepare the request payload
                payload = {
                    "text": text,
                    "language": language,
                    "stream": False  # We want the full audio file
                }
                
                # Add speaker reference if provided
                if speaker_wav_path and os.path.exists(speaker_wav_path):
                    try:
                        with open(speaker_wav_path, 'rb') as f:
                            speaker_data = base64.b64encode(f.read()).decode('utf-8')
                        payload["speaker_wav"] = speaker_data
                        logger.info(f"Using voice clone: {speaker_wav_path}")
                    except Exception as e:
                        logger.warning(f"Failed to load speaker wav {speaker_wav_path}: {e}")
                
                logger.info(f"Generating TTS via API - Text length: {len(text)} chars (attempt {attempt + 1})")
                
                # Make the API request
                response = self.session.post(
                    f"{self.base_url}/tts_stream",
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                # Handle the response
                if response.headers.get('content-type') == 'audio/wav':
                    # Direct audio response
                    if output_path:
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        with open(output_path, 'wb') as f:
                            f.write(response.content)
                        logger.info(f"Generated audio saved to: {output_path}")
                        return output_path
                    else:
                        logger.error("No output path specified for audio response")
                        return None
                else:
                    # JSON response with base64 encoded audio
                    try:
                        result = response.json()
                        if 'audio_data' in result:
                            audio_data = base64.b64decode(result['audio_data'])
                        elif isinstance(result, str):
                            # Direct base64 string
                            audio_data = base64.b64decode(result)
                        else:
                            logger.error(f"Unexpected API response format: {result}")
                            continue
                            
                        if output_path:
                            os.makedirs(os.path.dirname(output_path), exist_ok=True)
                            with open(output_path, 'wb') as f:
                                f.write(audio_data)
                            logger.info(f"Generated audio saved to: {output_path}")
                            return output_path
                        else:
                            logger.error("No output path specified for base64 audio")
                            return None
                            
                    except (json.JSONDecodeError, KeyError, base64.binascii.Error) as e:
                        logger.error(f"Failed to decode API response: {e}")
                        continue
                        
            except requests.exceptions.Timeout:
                logger.warning(f"XTTS API request timed out (attempt {attempt + 1}/{self.retries + 1})")
                if attempt < self.retries:
                    continue
                else:
                    logger.error("XTTS API request failed after all retries due to timeout")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"XTTS API request failed (attempt {attempt + 1}/{self.retries + 1}): {e}")
                if attempt < self.retries:
                    continue
                else:
                    logger.error(f"XTTS API request failed after all retries: {e}")
                    
            except Exception as e:
                logger.error(f"Unexpected error in XTTS API generation: {e}")
                break
        
        return None
    
    def clone_voice(self, speaker_wav_path, voice_name=None):
        """
        Clone a voice on the XTTS API server (if supported)
        
        Args:
            speaker_wav_path: Path to reference audio file
            voice_name: Name for the cloned voice (optional)
            
        Returns:
            Voice ID or name for future use
        """
        try:
            if not os.path.exists(speaker_wav_path):
                logger.error(f"Speaker wav file not found: {speaker_wav_path}")
                return None
                
            with open(speaker_wav_path, 'rb') as f:
                speaker_data = base64.b64encode(f.read()).decode('utf-8')
            
            payload = {
                "speaker_wav": speaker_data,
                "voice_name": voice_name or f"voice_{int(time.time())}"
            }
            
            response = self.session.post(
                f"{self.base_url}/clone_voice",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            voice_id = result.get('voice_id') or result.get('voice_name')
            
            if voice_id:
                logger.info(f"Voice cloned successfully: {voice_id}")
                return voice_id
            else:
                logger.warning("Voice cloning succeeded but no ID returned")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to clone voice: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in voice cloning: {e}")
            return None
    
    def get_server_info(self):
        """Get XTTS API server information and capabilities"""
        try:
            response = self.session.get(
                f"{self.base_url}/info",
                timeout=self.timeout
            )
            response.raise_for_status()
            info = response.json()
            logger.info(f"XTTS API server info: {info}")
            return info
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to get server info: {e}")
            return None