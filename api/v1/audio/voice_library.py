"""
Voice Library API
Endpoints for managing voice samples (upload, list, delete).
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
import tempfile
import os
import uuid
from services.supabase_service import SupabaseService
from services.cloudinary_service import CloudinaryService
from services.audio_ai.voice_library.voice_manager import VoiceManager
from services.audio_ai.base_service import BaseAudioService


router = APIRouter()


# Dependency injection
def get_db():
    return SupabaseService()

def get_cloudinary():
    return CloudinaryService()

def get_voice_manager():
    return VoiceManager()


# Response models
class VoiceSampleResponse(BaseModel):
    voice_sample_id: str
    name: str
    audio_url: str
    duration_seconds: Optional[float]
    user_id: str
    created_at: str


@router.post("/upload", response_model=VoiceSampleResponse)
async def upload_voice_sample(
    audio_file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(None),
    language_hint: str = Form(None),
    user_id: str = Form("anonymous"),
    is_public: bool = Form(False),
    cloudinary: CloudinaryService = Depends(get_cloudinary),
    voice_manager: VoiceManager = Depends(get_voice_manager)
):
    """
    Upload a voice sample for cloning.
    Audio should be 3-10 seconds of clear speech.
    """
    try:
        # Save uploaded file to temp
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.filename)[1]) as tmp_file:
            content = await audio_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Validate audio
        audio_service = BaseAudioService()
        is_valid, error = audio_service.validate_audio_file(tmp_path)
        
        if not is_valid:
            os.unlink(tmp_path)
            raise HTTPException(status_code=400, detail=f"Invalid audio file: {error}")
        
        # Get duration
        import librosa
        audio, sr = librosa.load(tmp_path, sr=None)
        duration = len(audio) / sr
        
        # Upload to Cloudinary
        public_id = f"voice_samples/{user_id}_{uuid.uuid4()}"
        audio_url = cloudinary.upload_audio(tmp_path, public_id=public_id)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        if not audio_url:
            raise HTTPException(status_code=500, detail="Failed to upload audio to Cloudinary")
        
        # Save to database
        voice_sample = voice_manager.create_voice_sample(
            user_id=user_id,
            name=name,
            description=description,
            audio_url=audio_url,
            duration_seconds=duration,
            language_hint=language_hint,
            sample_rate=sr,
            is_public=is_public
        )
        
        if not voice_sample:
            raise HTTPException(status_code=500, detail="Failed to save voice sample to database")
        
        return VoiceSampleResponse(
            voice_sample_id=voice_sample["id"],
            name=voice_sample["name"],
            audio_url=voice_sample["audio_url"],
            duration_seconds=voice_sample.get("duration_seconds"),
            user_id=voice_sample["user_id"],
            created_at=voice_sample["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_voice_samples(
    user_id: str = None,
    include_public: bool = True,
    limit: int = 50,
    voice_manager: VoiceManager = Depends(get_voice_manager)
):
    """List voice samples."""
    samples = voice_manager.list_voice_samples(
        user_id=user_id,
        include_public=include_public,
        limit=limit
    )
    
    # Rename id to voice_sample_id
    for sample in samples:
        if "id" in sample:
            sample["voice_sample_id"] = sample.pop("id")
    
    return samples


@router.get("/{voice_sample_id}")
async def get_voice_sample(
    voice_sample_id: str,
    voice_manager: VoiceManager = Depends(get_voice_manager)
):
    """Get a specific voice sample."""
    sample = voice_manager.get_voice_sample(voice_sample_id)
    
    if not sample:
        raise HTTPException(status_code=404, detail="Voice sample not found")
    
    if "id" in sample:
        sample["voice_sample_id"] = sample.pop("id")
    
    return sample


@router.delete("/{voice_sample_id}")
async def delete_voice_sample(
    voice_sample_id: str,
    user_id: str = None,
    voice_manager: VoiceManager = Depends(get_voice_manager)
):
    """Delete a voice sample."""
    success = voice_manager.delete_voice_sample(voice_sample_id, user_id=user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Voice sample not found or could not be deleted")
    
    return {"detail": "Voice sample deleted successfully"}
