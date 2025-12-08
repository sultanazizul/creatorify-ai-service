from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from services.tts_service import TTSService
from services.supabase_service import SupabaseService
from services.cloudinary_service import CloudinaryService
from services.kokoro_voices import get_all_languages, get_all_voices, get_voices_by_language, get_language_info
from fastapi.responses import StreamingResponse
import tempfile
import os
import uuid

router = APIRouter()
tts_service = TTSService()

# Dependency for Supabase
def get_db():
    return SupabaseService()

# Dependency for Cloudinary
def get_cloudinary():
    return CloudinaryService()

class TTSRequest(BaseModel):
    text: str
    voice: str = "af_heart"
    speed: float = 1.0
    lang_code: str = "a"
    user_id: str = "anonymous"

@router.post("/generate")
async def generate_tts(
    request: TTSRequest,
    db: SupabaseService = Depends(get_db),
    req: Request = None
):
    """
    Generate audio from text (Async).
    Creates a pending project and triggers background generation.
    Returns the created TTS project object with status='pending'.
    """
    try:
        # 1. Create Pending Record in Supabase
        tts_data = request.dict()
        project = db.create_tts(tts_data, audio_url=None, user_id=request.user_id)
        
        if not project:
             raise HTTPException(status_code=500, detail="Failed to save TTS project to DB")
        
        # Rename id to tts_id for response consistency
        if "id" in project:
            project["tts_id"] = project.pop("id")

        # 2. Trigger Background Task
        try:
            # Access the Modal function from app state
            from fastapi import Request as FastAPIRequest
            # Get the actual request object
            if hasattr(req, 'app'):
                process_tts_task = req.app.state.process_tts_task
                process_tts_task.spawn(
                    tts_id=project["tts_id"],
                    text=request.text,
                    voice=request.voice,
                    speed=request.speed,
                    lang_code=request.lang_code
                )
            else:
                raise Exception("Cannot access app state - function reference not available")
        except Exception as e:
            print(f"Failed to spawn background task: {e}")
            # Try to update status to failed if spawn fails
            db.update_tts(project["tts_id"], {"status": "failed_to_spawn"})
            raise HTTPException(status_code=500, detail=f"Failed to start generation task: {e}")
             
        return project

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/languages")
async def list_languages():
    """
    Get list of all supported languages.
    Returns language code, name, and technical details.
    """
    return {
        "languages": get_all_languages(),
        "total": len(get_all_languages())
    }

@router.get("/languages/{lang_code}")
async def get_language(lang_code: str):
    """
    Get information about a specific language.
    Returns language details including G2P method and fallback.
    """
    language = get_language_info(lang_code)
    if not language:
        raise HTTPException(
            status_code=404, 
            detail=f"Language code '{lang_code}' not found. Available codes: a, b, e, f, h, i, p, j, z"
        )
    return language

@router.get("/voices")
async def list_voices(lang_code: str = None):
    """
    Get list of all available voices.
    Optionally filter by language code.
    
    Query Parameters:
    - lang_code: Filter voices by language (e.g., 'a' for American English)
    """
    if lang_code:
        voices = get_voices_by_language(lang_code)
        if not voices:
            raise HTTPException(
                status_code=404,
                detail=f"No voices found for language code '{lang_code}'"
            )
        return {
            "voices": voices,
            "language": get_language_info(lang_code),
            "total": len(voices)
        }
    else:
        all_voices = get_all_voices()
        return {
            "voices": all_voices,
            "total": len(all_voices)
        }

@router.get("/voices/{lang_code}")
async def get_voices_for_language(lang_code: str):
    """
    Get all voices for a specific language.
    Returns list of voices with their details.
    """
    language = get_language_info(lang_code)
    if not language:
        raise HTTPException(
            status_code=404,
            detail=f"Language code '{lang_code}' not found"
        )
    
    voices = get_voices_by_language(lang_code)
    return {
        "language": language,
        "voices": voices,
        "total": len(voices)
    }

@router.get("/")
async def list_tts(
    user_id: str = None, 
    limit: int = 20,
    db: SupabaseService = Depends(get_db)
):
    """List TTS projects."""
    projects = db.list_tts(user_id, limit)
    # Rename id to tts_id
    for p in projects:
        if "id" in p:
            p["tts_id"] = p.pop("id")
    return projects

@router.get("/{tts_id}")
async def get_tts(
    tts_id: str,
    db: SupabaseService = Depends(get_db)
):
    """Get TTS project details."""
    project = db.get_tts(tts_id)
    if not project:
        raise HTTPException(status_code=404, detail="TTS project not found")
    
    if "id" in project:
        project["tts_id"] = project.pop("id")
        
    return project

@router.delete("/{tts_id}")
async def delete_tts(
    tts_id: str,
    db: SupabaseService = Depends(get_db)
):
    """Delete a TTS project."""
    success = db.delete_tts(tts_id)
    if not success:
        raise HTTPException(status_code=404, detail="TTS project not found or could not be deleted")
    return {"detail": "TTS project deleted successfully"}
