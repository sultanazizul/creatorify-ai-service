"""
Chatterbox TTS Service - HTTP Client
Calls Chatterbox microservice for TTS generation
"""
from typing import Optional
from io import BytesIO
import httpx
import logging

# Use standard logging
logger = logging.getLogger(__name__)

# Chatterbox microservice URL
CHATTERBOX_SERVICE_URL = "https://sultanazizul--chatterbox-tts-service-fastapi-app.modal.run"


class ChatterboxTTSService:
    """Service for Chatterbox English TTS via microservice."""
    
    def __init__(self):
        self.service_url = CHATTERBOX_SERVICE_URL
    
    def generate_audio(
        self,
        text: str,
        voice_sample_url: Optional[str] = None,
        exaggeration: float = 0.5,
        temperature: float = 0.8,
        cfg_weight: float = 0.5,
        repetition_penalty: float = 1.2,
        min_p: float = 0.05,
        top_p: float = 1.0
    ) -> BytesIO:
        """
        Generate English TTS audio via microservice.
        
        Args:
            text: Text to synthesize
            voice_sample_url: Optional URL to voice sample for cloning
            exaggeration: Emotion control (0.0-1.0)
            temperature: Sampling temperature
            cfg_weight: Classifier-free guidance weight
            repetition_penalty: Penalty for repetition
            min_p: Minimum probability threshold
            top_p: Top-p sampling threshold
            
        Returns:
            BytesIO object containing WAV audio
        """
        try:
            payload = {
                "text": text,
                "voice_sample_url": voice_sample_url,
                "exaggeration": exaggeration,
                "temperature": temperature,
                "cfg_weight": cfg_weight,
                "repetition_penalty": repetition_penalty,
                "min_p": min_p,
                "top_p": top_p
            }
            
            logger.info(f"Calling Chatterbox TTS microservice for: '{text[:50]}...'")
            
            with httpx.Client(timeout=300.0) as client:
                response = client.post(
                    f"{self.service_url}/tts/generate",
                    json=payload
                )
                response.raise_for_status()
                
                # Return audio as BytesIO
                buffer = BytesIO(response.content)
                buffer.seek(0)
                
                logger.info("TTS generation completed via microservice")
                return buffer
                
        except Exception as e:
            logger.error(f"Error calling Chatterbox TTS microservice: {e}")
            raise e
