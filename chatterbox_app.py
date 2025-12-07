"""
Chatterbox TTS Microservice - Separate Modal App
Handles Chatterbox TTS, Multilingual TTS, and Voice Conversion
Uses torch 2.6.0 to avoid dependency conflicts with main app
"""
import modal
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import os

# Create Modal app
app = modal.App("chatterbox-tts-service")

# Create Modal volume for model storage
chatterbox_volume = modal.Volume.from_name("chatterbox-models", create_if_missing=True)

# Define image with torch 2.6.0 and chatterbox-tts
chatterbox_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "git")
    .pip_install("numpy")  # Install numpy first to avoid pkuseg setup.py error
    .pip_install(
        "chatterbox-tts",  # This will install torch 2.6.0 and all correct dependencies
        "fastapi",
        "python-multipart",
        "loguru",
        "requests"  # For downloading voice samples
    )
)

# Pydantic models for API
class TTSRequest(BaseModel):
    text: str
    voice_sample_url: Optional[str] = None
    exaggeration: float = 0.5
    temperature: float = 0.8
    cfg_weight: float = 0.5
    repetition_penalty: float = 1.2
    min_p: float = 0.05
    top_p: float = 1.0


class MultilingualTTSRequest(BaseModel):
    text: str
    language_id: str  # ar, da, de, el, en, es, fi, fr, he, hi, it, ja, ko, ms, nl, no, pl, pt, ru, sv, sw, tr, zh
    voice_sample_url: Optional[str] = None
    exaggeration: float = 0.5
    temperature: float = 0.8
    cfg_weight: float = 0.5
    repetition_penalty: float = 1.2
    min_p: float = 0.05
    top_p: float = 1.0


class VoiceConversionRequest(BaseModel):
    source_audio_url: str
    target_voice_url: str


# Singleton model class
class ChatterboxModels:
    """Singleton to hold loaded models"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.tts_model = None
            cls._instance.multilingual_model = None
            cls._instance.vc_model = None
        return cls._instance
    
    def load_tts(self):
        """Load English TTS model"""
        if self.tts_model is None:
            from loguru import logger
            from chatterbox import ChatterboxTTS
            import torch
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading Chatterbox TTS on {device}...")
            self.tts_model = ChatterboxTTS.from_pretrained(device)
            logger.info("Chatterbox TTS loaded successfully")
        return self.tts_model
    
    def load_multilingual(self):
        """Load Multilingual TTS model"""
        if self.multilingual_model is None:
            from loguru import logger
            from chatterbox import ChatterboxMultilingualTTS
            import torch
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading Chatterbox Multilingual TTS on {device}...")
            self.multilingual_model = ChatterboxMultilingualTTS.from_pretrained(device)
            logger.info("Chatterbox Multilingual TTS loaded successfully")
        return self.multilingual_model
    
    def load_vc(self):
        """Load Voice Conversion model"""
        if self.vc_model is None:
            from loguru import logger
            from chatterbox import ChatterboxVC
            import torch
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading Chatterbox VC on {device}...")
            self.vc_model = ChatterboxVC.from_pretrained(device)
            logger.info("Chatterbox VC loaded successfully")
        return self.vc_model


# Create FastAPI app
web_app = FastAPI(title="Chatterbox TTS Microservice")


@web_app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chatterbox-tts"}


@web_app.post("/tts/generate")
def generate_tts(request: TTSRequest):
    """Generate English TTS with optional voice cloning"""
    from loguru import logger
    import torch
    import io
    import soundfile as sf
    import requests
    
    try:
        models = ChatterboxModels()
        tts_model = models.load_tts()
        
        # Download voice sample if provided
        audio_prompt_path = None
        if request.voice_sample_url:
            logger.info(f"Downloading voice sample from {request.voice_sample_url}")
            response = requests.get(request.voice_sample_url)
            response.raise_for_status()
            
            # Save to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(response.content)
                audio_prompt_path = f.name
        
        # Generate audio
        logger.info(f"Generating TTS: '{request.text[:50]}...'")
        audio_tensor = tts_model.generate(
            text=request.text,
            audio_prompt_path=audio_prompt_path,
            exaggeration=request.exaggeration,
            temperature=request.temperature,
            cfg_weight=request.cfg_weight,
            repetition_penalty=request.repetition_penalty,
            min_p=request.min_p,
            top_p=request.top_p
        )
        
        # Convert to WAV
        audio_np = audio_tensor.squeeze().cpu().numpy()
        buffer = io.BytesIO()
        sf.write(buffer, audio_np, tts_model.sr, format='WAV')
        buffer.seek(0)
        
        # Cleanup temp file
        if audio_prompt_path:
            os.remove(audio_prompt_path)
        
        logger.info("TTS generation completed")
        return Response(content=buffer.read(), media_type="audio/wav")
        
    except Exception as e:
        logger.error(f"Error in TTS generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@web_app.post("/tts/multilingual/generate")
def generate_multilingual_tts(request: MultilingualTTSRequest):
    """Generate multilingual TTS (23 languages) with optional voice cloning"""
    from loguru import logger
    import torch
    import io
    import soundfile as sf
    import requests
    
    try:
        # Validate text length (max ~500 characters for stable generation)
        MAX_TEXT_LENGTH = 1000
        if len(request.text) > MAX_TEXT_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Text too long ({len(request.text)} chars). Maximum is {MAX_TEXT_LENGTH} characters. "
                       f"Please split your text into smaller chunks."
            )
        
        models = ChatterboxModels()
        multilingual_model = models.load_multilingual()
        
        # Download voice sample if provided
        audio_prompt_path = None
        if request.voice_sample_url:
            logger.info(f"Downloading voice sample from {request.voice_sample_url}")
            response = requests.get(request.voice_sample_url, timeout=30)
            response.raise_for_status()
            
            # Save to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(response.content)
                audio_prompt_path = f.name
        
        # Generate audio
        logger.info(f"Generating multilingual TTS ({request.language_id}): '{request.text[:50]}...' ({len(request.text)} chars)")
        audio_tensor = multilingual_model.generate(
            text=request.text,
            language_id=request.language_id.lower(),
            audio_prompt_path=audio_prompt_path,
            exaggeration=request.exaggeration,
            temperature=request.temperature,
            cfg_weight=request.cfg_weight,
            repetition_penalty=request.repetition_penalty,
            min_p=request.min_p,
            top_p=request.top_p
        )
        
        # Convert to WAV
        audio_np = audio_tensor.squeeze().cpu().numpy()
        buffer = io.BytesIO()
        sf.write(buffer, audio_np, multilingual_model.sr, format='WAV')
        buffer.seek(0)
        
        # Cleanup temp file
        if audio_prompt_path:
            os.remove(audio_prompt_path)
        
        logger.info(f"Multilingual TTS generation completed ({request.language_id})")
        return Response(content=buffer.read(), media_type="audio/wav")
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Error in multilingual TTS generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")


@web_app.post("/vc/convert")
def voice_conversion(request: VoiceConversionRequest):
    """Convert voice from source audio to target voice"""
    from loguru import logger
    import torch
    import io
    import soundfile as sf
    import requests
    import tempfile
    
    try:
        models = ChatterboxModels()
        vc_model = models.load_vc()
        
        # Download source audio
        logger.info(f"Downloading source audio from {request.source_audio_url}")
        response = requests.get(request.source_audio_url, timeout=60)
        response.raise_for_status()
        
        # Check file size (limit to ~10MB to prevent OOM)
        if len(response.content) > 10 * 1024 * 1024:
             raise HTTPException(status_code=400, detail="Source audio too large (max 10MB)")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(response.content)
            source_path = f.name
        
        try:
            # Download target voice
            logger.info(f"Downloading target voice from {request.target_voice_url}")
            response = requests.get(request.target_voice_url, timeout=60)
            response.raise_for_status()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(response.content)
                target_path = f.name
            
            try:
                # Perform voice conversion
                logger.info("Performing voice conversion...")
                audio_tensor = vc_model.generate(
                    audio=source_path,
                    target_voice_path=target_path
                )
                
                # Convert to WAV
                audio_np = audio_tensor.squeeze().cpu().numpy()
                buffer = io.BytesIO()
                sf.write(buffer, audio_np, vc_model.sr, format='WAV')
                buffer.seek(0)
                
                logger.info("Voice conversion completed")
                return Response(content=buffer.read(), media_type="audio/wav")
            finally:
                if os.path.exists(target_path):
                    os.remove(target_path)
        finally:
            if os.path.exists(source_path):
                os.remove(source_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in voice conversion: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Voice conversion failed: {str(e)}")


# Deploy FastAPI app on Modal
@app.function(
    image=chatterbox_image,
    gpu="A10G",  # Chatterbox needs GPU
    timeout=600,
    volumes={"/models": chatterbox_volume}
)
@modal.concurrent(max_inputs=10)  # Allow 10 concurrent requests
@modal.asgi_app()
def fastapi_app():
    return web_app
