"""
Chatterbox Voice Conversion Service - HTTP Client
Calls Chatterbox microservice for voice conversion
"""
from io import BytesIO
import httpx
import logging

# Use standard logging
logger = logging.getLogger(__name__)

# Chatterbox microservice URL
CHATTERBOX_SERVICE_URL = "https://sultanazizul--chatterbox-tts-service-fastapi-app.modal.run"


class ChatterboxVCService:
    """Service for Chatterbox Voice Conversion via microservice."""
    
    def __init__(self):
        self.service_url = CHATTERBOX_SERVICE_URL
    
    def convert_voice(
        self,
        source_audio_url: str,
        target_voice_url: str
    ) -> BytesIO:
        """
        Convert voice from source audio to target voice via microservice.
        
        Args:
            source_audio_url: URL to source audio file
            target_voice_url: URL to target voice sample
            
        Returns:
            BytesIO object containing converted WAV audio
        """
        try:
            payload = {
                "source_audio_url": source_audio_url,
                "target_voice_url": target_voice_url
            }
            
            logger.info(f"Calling Chatterbox VC microservice...")
            
            with httpx.Client(timeout=300.0) as client:
                response = client.post(
                    f"{self.service_url}/vc/convert",
                    json=payload
                )
                response.raise_for_status()
                
                # Return audio as BytesIO
                buffer = BytesIO(response.content)
                buffer.seek(0)
                
                logger.info("Voice conversion completed via microservice")
                return buffer
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Error calling Chatterbox VC microservice: {e}")
            logger.error(f"Response details: {e.response.text}")
            raise e
        except Exception as e:
            logger.error(f"Error calling Chatterbox VC microservice: {e}")
            raise e
