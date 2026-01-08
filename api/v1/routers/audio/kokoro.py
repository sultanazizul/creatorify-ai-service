from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel

from services.infrastructure.supabase import SupabaseService
from services.audio.tts.kokoro.service import TTSService
from services.audio.tts.kokoro.voices import get_all_languages, get_all_voices, get_voices_by_language, get_language_info
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

from models.audio.tts import KokoroTTSRequest as TTSRequest

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
    # Rename id to tts_id and format pipeline
    formatted_projects = []
    for p in projects:
        if "id" in p:
            p["tts_id"] = p.pop("id")
            
        # Lift pipeline logic
        if "metadata" in p and p["metadata"]:
            meta = p["metadata"]
            if "pipeline" in meta:
                p["pipeline"] = meta.pop("pipeline")
            if not meta:
                del p["metadata"]
        
        # Ensure current_stage
        if "current_stage" not in p or not p["current_stage"]:
             if "pipeline" in p and "stages" in p["pipeline"]:
                # Simple infer: check generic status or assume Text Analysis
                p["current_stage"] = "TEXT_ANALYSIS" # Simplified for list view
                for s in p["pipeline"]["stages"]:
                     if s["status"] == "active":
                         p["current_stage"] = s["key"]
                         break
        
        formatted_projects.append(p)
        
    return formatted_projects

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

    # Lift pipeline from metadata and clean up
    if "metadata" in project and project["metadata"]:
        meta = project["metadata"]
        if "pipeline" in meta:
            project["pipeline"] = meta.pop("pipeline")
        
        # Remove metadata if empty
        if not meta:
            del project["metadata"]
    
    # Ensure current_stage is present if missing
    if "current_stage" not in project or not project["current_stage"]:
         if "pipeline" in project and "stages" in project["pipeline"]:
             for s in project["pipeline"]["stages"]:
                 if s["status"] == "active":
                     project["current_stage"] = s["key"]
                     break
             else:
                 # If no active stage, check for last completed
                 for s in reversed(project["pipeline"]["stages"]):
                     if s["status"] == "completed":
                         project["current_stage"] = s["key"]
                         break
                 else:
                    project["current_stage"] = "TEXT_ANALYSIS"
        
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
