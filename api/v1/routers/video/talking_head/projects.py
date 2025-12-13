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
    Create a new video generation project.
    1. Save to DB (queued)
    2. Submit to Modal (async)
    """
    # Import here to avoid circular imports if Model is in app.py
    # We assume 'app' module is available and has 'Model'
    try:
        from app import Model
    except ImportError:
        # Fallback for local testing or if structure differs
        raise HTTPException(status_code=500, detail="Model class not found")

    # 1. Create DB entry (initial)
    # We need a call_id, but we get it after spawning. 
    # Strategy: Create DB entry with pending call_id, then update? 
    # Or spawn first? Spawning is fast.
    
    try:
        # Prepare arguments for the model
        # We need to convert Pydantic model to what Model expects
        # The Model.submit expects GenerationRequest (or similar arguments)
        # We'll adapt the Model.submit to take these args or map them here.
        
        # For now, let's assume we map it to the existing signature or a new one.
        # We'll spawn the job.
        
        # Note: We are passing URLs. The Model._download_and_validate handles them.
        # Fix: Instantiate the class before spawning
        # Fix: Convert Pydantic model to dict for Modal
        params_dict = project.parameters.dict() if project.parameters else {}
        
        job = Model().submit.spawn(
            image_url=project.image_url,
            audio_url=project.audio_url,
            audio_url_2=project.audio_url_2, # Pass second audio if available
            audio_order=project.audio_order, # Pass audio order
            prompt=project.prompt,
            params=params_dict
        )
        call_id = job.object_id
        
        # 2. Save to DB
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