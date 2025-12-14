from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List
from models.video.talking_head import ProjectCreate, ProjectResponse, ProjectStatus
from services.infrastructure.supabase import SupabaseService
from core.security import get_api_key
import modal

router = APIRouter(dependencies=[Depends(get_api_key)])

# Dependency for Supabase
def get_db():
    return SupabaseService()

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate, 
    background_tasks: BackgroundTasks,
    db: SupabaseService = Depends(get_db)
):
    """
    Create a new video generation project (JSON).
    1. Save to DB (queued)
    2. Submit to Modal (async)
    """
    try:
        from app import Model
    except ImportError:
        # Fallback
        raise HTTPException(status_code=500, detail="Model class not found")

    try:
        # Pydantic model to dict
        params_dict = project.parameters.dict() if project.parameters else {}
        
        # Default or override params
        # Note: num_persistent_param_in_dit is handled in app.py if inside params_dict
        
        job = Model().submit.spawn(
            image_url=project.image_url,
            audio_url=project.audio_url,
            audio_url_2=project.audio_url_2, 
            audio_order=project.audio_order, 
            prompt=project.prompt,
            params=params_dict
        )
        call_id = job.object_id
        
        # Save to DB
        db_project = db.create_project(project, call_id, user_id=project.user_id)
        
        if not db_project:
             raise HTTPException(status_code=500, detail="Failed to save project to DB")
             
        return db_project

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    user_id: str = None, 
    limit: int = 20,
    type: str = None, # Added type filter
    db: SupabaseService = Depends(get_db)
):
    return db.list_projects(user_id, limit, project_type=type)

@router.get("/{id}", response_model=ProjectResponse)
async def get_project(
    id: str,
    db: SupabaseService = Depends(get_db)
):
    project = db.get_project(id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/{id}")
async def delete_project(
    id: str,
    db: SupabaseService = Depends(get_db)
):
    success = db.delete_project(id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found or could not be deleted")
    return {"detail": "Project deleted successfully"}