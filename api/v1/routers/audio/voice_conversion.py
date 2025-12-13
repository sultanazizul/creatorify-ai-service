"""
Voice Conversion API
Endpoints for converting voice of existing audio.
"""
from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
import tempfile
import os
import uuid
from services.infrastructure.supabase import SupabaseService
from services.infrastructure.cloudinary import CloudinaryService
from services.audio.voice_library.voice_manager import VoiceManager


router = APIRouter()


# Dependency injection
def get_db():
    return SupabaseService()

def get_cloudinary():
    return CloudinaryService()


# Request model
from models.audio.voice_conversion import VoiceConversionRequest


@router.post("/convert")
async def convert_voice(
    request: VoiceConversionRequest,
    req: Request,
    db: SupabaseService = Depends(get_db)
):
    """
    Convert voice of source audio to target voice.
    Requires source_audio_url and target_voice_sample_id.
    """
    try:
        # Create project record
        project_data = {
            "project_type": "voice_conversion",
            "source_audio_url": request.source_audio_url,
            "voice_sample_id": request.target_voice_sample_id
        }
        
        project = db.create_chatterbox_project(project_data, user_id=request.user_id)
        
        if not project:
            raise HTTPException(status_code=500, detail="Failed to create project")
        
        # Rename id
        if "id" in project:
            project["project_id"] = project.pop("id")
        
        # Trigger background task
        try:
            if hasattr(req, 'app') and hasattr(req.app.state, 'process_voice_conversion'):
                process_task = req.app.state.process_voice_conversion
                process_task.spawn(
                    project_id=project["project_id"],
                    source_audio_url=request.source_audio_url,
                    target_voice_sample_id=request.target_voice_sample_id
                )
            else:
                raise Exception("Background task function not available")
        except Exception as e:
            print(f"Failed to spawn background task: {e}")
            db.update_chatterbox_project(project["project_id"], {"status": "failed_to_spawn"})
            raise HTTPException(status_code=500, detail=f"Failed to start conversion: {e}")
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/convert-upload")
async def convert_voice_with_upload(
    source_audio: UploadFile = File(...),
    target_voice_sample_id: str = Form(...),
    user_id: str = Form("anonymous"),
    req: Request = None,
    db: SupabaseService = Depends(get_db),
    cloudinary: CloudinaryService = Depends(get_cloudinary)
):
    """
    Convert voice with file upload.
    Upload source audio file and specify target voice sample.
    """
    try:
        # Save uploaded file to temp
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(source_audio.filename)[1]) as tmp_file:
            content = await source_audio.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Upload source audio to Cloudinary
        public_id = f"voice_conversion/{user_id}_{uuid.uuid4()}"
        source_audio_url = cloudinary.upload_audio(tmp_path, public_id=public_id)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        if not source_audio_url:
            raise HTTPException(status_code=500, detail="Failed to upload source audio")
        
        # Create project record
        project_data = {
            "project_type": "voice_conversion",
            "source_audio_url": source_audio_url,
            "voice_sample_id": target_voice_sample_id
        }
        
        project = db.create_chatterbox_project(project_data, user_id=user_id)
        
        if not project:
            raise HTTPException(status_code=500, detail="Failed to create project")
        
        # Rename id
        if "id" in project:
            project["project_id"] = project.pop("id")
        
        # Trigger background task
        try:
            if hasattr(req, 'app') and hasattr(req.app.state, 'process_voice_conversion'):
                process_task = req.app.state.process_voice_conversion
                process_task.spawn(
                    project_id=project["project_id"],
                    source_audio_url=source_audio_url,
                    target_voice_sample_id=target_voice_sample_id
                )
            else:
                raise Exception("Background task function not available")
        except Exception as e:
            print(f"Failed to spawn background task: {e}")
            db.update_chatterbox_project(project["project_id"], {"status": "failed_to_spawn"})
            raise HTTPException(status_code=500, detail=f"Failed to start conversion: {e}")
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
