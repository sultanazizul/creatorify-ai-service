from fastapi import APIRouter, HTTPException, Depends
from models.project_model import ProjectStatus
from services.supabase_service import SupabaseService
from services.cloudinary_service import CloudinaryService
from utils.auth import get_api_key
import modal
import os
import tempfile

router = APIRouter(dependencies=[Depends(get_api_key)])

def get_services():
    return SupabaseService(), CloudinaryService()

@router.get("/{project_id}/status", response_model=ProjectStatus)
async def get_project_status(
    project_id: str,
    services: tuple = Depends(get_services)
):
    db, cloudinary_service = services
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # If already finished or failed, return immediately
    if project['status'] in ['finished', 'failed']:
        return ProjectStatus(
            id=project['id'],
            status=project['status'],
            progress=project['progress'],
            video_url=project.get('video_url'),
            error_message=project.get('error_message')
        )

    # Check Modal status
    call_id = project.get('call_id')
    if not call_id:
        return ProjectStatus(**project) # Should not happen if created correctly

    try:
        fc = modal.FunctionCall.from_id(call_id)
        # Check if done
        try:
            # get(timeout=0) returns the result if ready, raises TimeoutError if not
            # The result from _generate_video is the filename in the volume
            print(f"[DEBUG] Checking Modal job status for call_id: {call_id}")
            result = fc.get(timeout=0)
            print(f"[DEBUG] Job completed! Result type: {type(result)}, Result: {result}")
            
            # IMPORTANT: submit() spawns _generate_video.spawn(), which returns a FunctionCall
            # So result here is actually another FunctionCall object, not the filename
            # We need to get the actual result from this inner FunctionCall
            if isinstance(result, modal.FunctionCall):
                print(f"[DEBUG] Result is a FunctionCall, getting actual output...")
                output_filename = result.get(timeout=0)
                print(f"[DEBUG] Actual output filename: {output_filename}")
            else:
                output_filename = result
            
            # If we get here, it's done!
            # 1. Read from volume
            # We need access to the volume. 
            # In the API container, we need to mount the volume.
            # We'll assume this code runs in the container with the volume mounted at /outputs
            
            output_path = f"/outputs/{output_filename}"
            print(f"[DEBUG] Looking for file at: {output_path}")
            
            # Verify file exists
            if os.path.exists(output_path):
                print(f"[DEBUG] File found! Uploading to Cloudinary...")
                # 2. Upload to Cloudinary
                video_url = cloudinary_service.upload_video(output_path, public_id=f"project_{project_id}")
                print(f"[DEBUG] Cloudinary upload result: {video_url}")
                
                if video_url:
                    # 3. Update DB
                    db.update_status(project_id, "finished", 100, video_url=video_url)
                    project['status'] = 'finished'
                    project['progress'] = 100
                    project['video_url'] = video_url
                    print(f"[DEBUG] Project marked as finished with video URL")
                else:
                    # Upload failed
                    error_msg = "Cloudinary upload failed"
                    print(f"[ERROR] {error_msg}")
                    db.update_status(project_id, "failed", error_message=error_msg)
                    project['status'] = 'failed'
                    project['error_message'] = error_msg
            else:
                # File not found in volume?
                error_msg = f"Output file missing at {output_path}"
                print(f"[ERROR] {error_msg}")
                db.update_status(project_id, "failed", error_message=error_msg)
                project['status'] = 'failed'
                project['error_message'] = error_msg

        except TimeoutError:
            # Still running
            print(f"[DEBUG] Job still running (TimeoutError)")
            # We can't easily get progress % from Modal without a separate side-channel (like DB updates from the job)
            # For now, just keep it as processing
            if project['status'] == 'queued':
                db.update_status(project_id, "processing", 10)
                project['status'] = 'processing'
                project['progress'] = 10
            
        except Exception as e:
            # Execution failed
            import traceback
            error_msg = f"Modal job execution failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            db.update_status(project_id, "failed", error_message=error_msg)
            project['status'] = 'failed'
            project['error_message'] = error_msg

    except Exception as e:
        import traceback
        print(f"[ERROR] Error checking Modal status: {e}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        # Don't fail the request, just return last known status
    
    return ProjectStatus(
        id=project['id'],
        status=project['status'],
        progress=project['progress'],
        video_url=project.get('video_url'),
        error_message=project.get('error_message')
    )
