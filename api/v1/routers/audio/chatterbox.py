"""
Chatterbox TTS API
Endpoints for voice cloning TTS and multilingual TTS.
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
from services.infrastructure.supabase import SupabaseService
from services.audio.tts.chatterbox.multilingual_service import SUPPORTED_LANGUAGES


router = APIRouter()


# Dependency injection
def get_db():
    return SupabaseService()


# Request models
from models.audio.tts import ChatterboxTTSRequest as TTSRequest, MultilingualTTSRequest


@router.post("/tts/generate")
async def generate_voice_cloning_tts(
    request: TTSRequest,
    req: Request,
    db: SupabaseService = Depends(get_db)
):
    """
    Generate TTS with voice cloning (English only).
    Requires a voice_sample_id from the voice library.
    """
    try:
        # Create project record
        project_data = {
            "project_type": "tts",
            "text": request.text,
            "voice_sample_id": request.voice_sample_id,
            "exaggeration": request.exaggeration,
            "temperature": request.temperature,
            "cfg_weight": request.cfg_weight,
            "repetition_penalty": request.repetition_penalty,
            "min_p": request.min_p,
            "top_p": request.top_p
        }
        
        project = db.create_chatterbox_project(project_data, user_id=request.user_id)
        
        if not project:
            raise HTTPException(status_code=500, detail="Failed to create project")
        
        # Rename id to project_id
        if "id" in project:
            project["project_id"] = project.pop("id")
        
        # Trigger background task
        try:
            if hasattr(req, 'app') and hasattr(req.app.state, 'process_chatterbox_tts'):
                process_task = req.app.state.process_chatterbox_tts
                process_task.spawn(
                    project_id=project["project_id"],
                    text=request.text,
                    voice_sample_id=request.voice_sample_id,
                    exaggeration=request.exaggeration,
                    temperature=request.temperature,
                    cfg_weight=request.cfg_weight,
                    repetition_penalty=request.repetition_penalty,
                    min_p=request.min_p,
                    top_p=request.top_p
                )
            else:
                raise Exception("Background task function not available")
        except Exception as e:
            print(f"Failed to spawn background task: {e}")
            db.update_chatterbox_project(project["project_id"], {"status": "failed_to_spawn"})
            raise HTTPException(status_code=500, detail=f"Failed to start generation: {e}")
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/multilingual/generate")
async def generate_multilingual_tts(
    request: MultilingualTTSRequest,
    req: Request,
    db: SupabaseService = Depends(get_db)
):
    """
    Generate multilingual TTS (23 languages).
    Optionally use voice_sample_id for cross-lingual voice cloning.
    """
    try:
        # Validate language
        if request.language_id.lower() not in SUPPORTED_LANGUAGES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language '{request.language_id}'. Supported: {', '.join(SUPPORTED_LANGUAGES.keys())}"
            )
        
        # Create project record
        project_data = {
            "project_type": "multilingual_tts",
            "text": request.text,
            "language_id": request.language_id.lower(),
            "voice_sample_id": request.voice_sample_id,
            "exaggeration": request.exaggeration,
            "temperature": request.temperature,
            "cfg_weight": request.cfg_weight,
            "repetition_penalty": request.repetition_penalty,
            "min_p": request.min_p,
            "top_p": request.top_p
        }
        
        project = db.create_chatterbox_project(project_data, user_id=request.user_id)
        
        if not project:
            raise HTTPException(status_code=500, detail="Failed to create project")
        
        # Rename id
        if "id" in project:
            project["project_id"] = project.pop("id")
        
        # Trigger background task
        try:
            if hasattr(req, 'app') and hasattr(req.app.state, 'process_chatterbox_multilingual'):
                process_task = req.app.state.process_chatterbox_multilingual
                process_task.spawn(
                    project_id=project["project_id"],
                    text=request.text,
                    language_id=request.language_id.lower(),
                    voice_sample_id=request.voice_sample_id,
                    exaggeration=request.exaggeration,
                    temperature=request.temperature,
                    cfg_weight=request.cfg_weight,
                    repetition_penalty=request.repetition_penalty,
                    min_p=request.min_p,
                    top_p=request.top_p
                )
            else:
                raise Exception("Background task function not available")
        except Exception as e:
            print(f"Failed to spawn background task: {e}")
            db.update_chatterbox_project(project["project_id"], {"status": "failed_to_spawn"})
            raise HTTPException(status_code=500, detail=f"Failed to start generation: {e}")
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/multilingual/languages")
async def get_supported_languages():
    """Get list of supported languages for multilingual TTS."""
    return {"languages": SUPPORTED_LANGUAGES}


@router.get("/projects/{project_id}")
async def get_project_status(
    project_id: str,
    db: SupabaseService = Depends(get_db)
):
    """Get Chatterbox project status and details."""
    project = db.get_chatterbox_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if "id" in project:
        project["project_id"] = project.pop("id")
    
    return project


@router.get("/projects")
async def list_projects(
    user_id: str = None,
    project_type: str = None,
    limit: int = 50,
    db: SupabaseService = Depends(get_db)
):
    """List Chatterbox projects."""
    projects = db.list_chatterbox_projects(
        user_id=user_id,
        project_type=project_type,
        limit=limit
    )
    
    # Rename id
    for p in projects:
        if "id" in p:
            p["project_id"] = p.pop("id")
    
    return projects


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    db: SupabaseService = Depends(get_db)
):
    """Delete a Chatterbox project."""
    success = db.delete_chatterbox_project(project_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Project not found or could not be deleted")
    
    return {"detail": "Project deleted successfully"}
