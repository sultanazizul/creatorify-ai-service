"""
Chatterbox Multilingual TTS Service - HTTP Client
Calls Chatterbox microservice for multilingual TTS generation
"""
from typing import Optional
from io import BytesIO
import httpx
import logging

# Use standard logging
logger = logging.getLogger(__name__)

# Chatterbox microservice URL
CHATTERBOX_SERVICE_URL = "https://sultanazizul--chatterbox-tts-service-fastapi-app.modal.run"

# Supported languages
SUPPORTED_LANGUAGES = {
    "ar": "Arabic", "da": "Danish", "de": "German",
    "el": "Greek", "en": "English", "es": "Spanish",
    "fi": "Finnish", "fr": "French", "he": "Hebrew",
    "hi": "Hindi", "it": "Italian", "ja": "Japanese",
    "ko": "Korean", "ms": "Malay", "nl": "Dutch",
    "no": "Norwegian", "pl": "Polish", "pt": "Portuguese",
    "ru": "Russian", "sv": "Swedish", "sw": "Swahili",
    "tr": "Turkish", "zh": "Chinese"
}


class ChatterboxMultilingualService:
    """Service for Chatterbox Multilingual TTS (23 languages) via microservice."""
    
    def __init__(self):
        self.service_url = CHATTERBOX_SERVICE_URL
    
    @staticmethod
    def get_supported_languages():
        """Get dictionary of supported languages."""
        return SUPPORTED_LANGUAGES.copy()
    
    def generate_audio(
        self,
        text: str,
        language_id: str,
        voice_sample_url: Optional[str] = None,
        exaggeration: float = 0.5,
        temperature: float = 0.8,
        cfg_weight: float = 0.5,
        repetition_penalty: float = 1.2,
        min_p: float = 0.05,
        top_p: float = 1.0
    ) -> BytesIO:
        """
        Generate multilingual TTS audio via microservice.
        
        Args:
            text: Text to synthesize
            language_id: Language code (ar, da, de, el, en, es, fi, fr, he, hi, it, ja, ko, ms, nl, no, pl, pt, ru, sv, sw, tr, zh)
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
        # Validate language
        if language_id.lower() not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language '{language_id}'. "
                f"Supported: {', '.join(SUPPORTED_LANGUAGES.keys())}"
            )
        
        try:
            payload = {
                "text": text,
                "language_id": language_id.lower(),
                "voice_sample_url": voice_sample_url,
                "exaggeration": exaggeration,
                "temperature": temperature,
                "cfg_weight": cfg_weight,
                "repetition_penalty": repetition_penalty,
                "min_p": min_p,
                "top_p": top_p
            }
            
            logger.info(f"Calling Chatterbox Multilingual microservice ({language_id}): '{text[:50]}...'")
            
            with httpx.Client(timeout=300.0) as client:
                response = client.post(
                    f"{self.service_url}/tts/multilingual/generate",
                    json=payload
                )
                response.raise_for_status()
                
                # Return audio as BytesIO
                buffer = BytesIO(response.content)
                buffer.seek(0)
                
                logger.info(f"Multilingual TTS generation completed via microservice ({language_id})")
                return buffer
                
        except Exception as e:
            logger.error(f"Error calling Chatterbox Multilingual microservice: {e}")
            raise e
