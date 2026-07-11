from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List
from models.video.talking_head import ProjectCreate, ProjectResponse, ProjectStatus, PaginatedProjectResponse
from services.infrastructure.supabase import SupabaseService
from services.infrastructure.email import EmailService
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
        
        # Save to DB first to get ID
        # Convert Pydantic model to dict for DB creation
        # We don't have call_id yet, but we will update it later or pass "pending"
        db_project = db.create_project(project, call_id="pending", user_id=project.user_id)
        
        if not db_project:
             raise HTTPException(status_code=500, detail="Failed to save project to DB")
        
        project_id = db_project["id"]

        # Send submission email if email is provided
        if project.email:
            email_service = EmailService()
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #fafafa; color: #111111; margin: 0; padding: 40px 20px; }}
        .container {{ max-width: 560px; background: #ffffff; margin: 0 auto; border: 1px solid #e5e5e5; padding: 40px; }}
        .header {{ text-align: left; padding-bottom: 30px; border-bottom: 1px solid #eeeeee; margin-bottom: 30px; }}
        .header h1 {{ margin: 0; font-size: 20px; font-weight: 600; letter-spacing: -0.5px; text-transform: uppercase; color: #000000; }}
        .content {{ line-height: 1.6; font-size: 14px; color: #333333; }}
        .content p {{ margin: 0 0 20px 0; }}
        .project-box {{ background: #fdfdfd; padding: 20px; border: 1px solid #eaeaea; margin: 25px 0; }}
        .project-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #888888; margin-bottom: 5px; }}
        .project-title {{ font-size: 15px; font-weight: 600; color: #000000; }}
        .footer {{ padding-top: 30px; border-top: 1px solid #eeeeee; margin-top: 40px; font-size: 11px; color: #888888; text-align: left; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Creatorify</h1>
        </div>
        <div class="content">
            <p>Halo,</p>
            <p>Terima kasih telah menggunakan Creatorify. Project Anda telah berhasil kami terima dan saat ini sedang diproses oleh sistem AI kami.</p>
            <div class="project-box">
                <div class="project-label">Detail Project</div>
                <div class="project-title">{project.title}</div>
            </div>
            <p>Kami akan mengirimkan email notifikasi baru kepada Anda segera setelah video selesai di-generate.</p>
            <p>Salam hangat,<br>Tim Creatorify</p>
        </div>
        <div class="footer">
            <p>© 2026 Creatorify. Hak cipta dilindungi.</p>
        </div>
    </div>
</body>
</html>
"""
            background_tasks.add_task(
                email_service.send_email,
                project.email,
                "Project Creatorify Berhasil Dikirim",
                html_body,
                is_html=True
            )

        job = Model().submit.spawn(
            image_url=project.image_url,
            audio_url=project.audio_url,
            audio_url_2=project.audio_url_2, 
            audio_order=project.audio_order, 
            prompt=project.prompt,
            params=params_dict,
            project_id=project_id,  # Pass generated ID
            email=project.email # Pass email for completion notification
        )
        call_id = job.object_id
        
        # Update DB with call_id
        # We need a method to update project fields other than status/progress
        # Assuming db.update_status can be used or we add a new method.
        # Check services/infrastructure/supabase.py: update_status updates specific fields.
        # We might need to add a generic update_project method or update call_id via raw query if needed.
        # For now, let's assume call_id is less critical for the user than project_id for upload.
        # But good to have. Using a raw query update here for simplicity if needed, or add to SupabaseService.
        try:
             db.client.table("projects").update({"call_id": call_id}).eq("id", project_id).execute()
        except:
             pass # Not critical
             
        # Add call_id to response
        db_project["call_id"] = call_id
        
        # Lift pipeline from metadata
        if "metadata" in db_project and db_project["metadata"]:
            meta = db_project["metadata"]
            if "pipeline" in meta:
                db_project["pipeline"] = meta.pop("pipeline")
            if not meta:
                 del db_project["metadata"]
              
        return db_project

    except Exception as e:
        import traceback
        print(f"[ERROR] Create Project failed: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=PaginatedProjectResponse)
async def list_projects(
    user_id: str = None, 
    limit: int = 20,
    type: str = None, # Added type filter
    cursor: str = None,
    db: SupabaseService = Depends(get_db)
):
    result = db.list_projects(user_id, limit, project_type=type, cursor=cursor)
    
    # Format responses to lift pipeline
    projects = result.get("items", [])
    formatted_projects = []
    for p in projects:
        # Lift pipeline from metadata
        if "metadata" in p and p["metadata"]:
            meta = p["metadata"]
            if "pipeline" in meta:
                p["pipeline"] = meta.pop("pipeline")
            if not meta:
                del p["metadata"]
        
        formatted_projects.append(p)
        
    return {
        "items": formatted_projects,
        "next_cursor": result.get("next_cursor"),
        "has_more": result.get("has_more")
    }

@router.get("/{id}", response_model=ProjectResponse)
async def get_project(
    id: str,
    db: SupabaseService = Depends(get_db)
):
    project = db.get_project(id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Lift pipeline from metadata
    if "metadata" in project and project["metadata"]:
        meta = project["metadata"]
        if "pipeline" in meta:
            project["pipeline"] = meta.pop("pipeline")
        if not meta:
             del project["metadata"]
             
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