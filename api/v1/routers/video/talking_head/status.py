from fastapi import APIRouter, HTTPException, Depends
from models.video.talking_head import ProjectStatus
from services.infrastructure.supabase import SupabaseService
from services.infrastructure.cloudinary import CloudinaryService
from core.security import get_api_key
import modal
import os
import tempfile

router = APIRouter(dependencies=[Depends(get_api_key)])

def get_services():
    return SupabaseService(), CloudinaryService()

@router.get("/{id}/status", response_model=ProjectStatus)
async def get_project_status(
    id: str,
    services: tuple = Depends(get_services)
):
    db, cloudinary_service = services
    project = db.get_project(id)
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
            
            # If we get here, video generation is done!
            # Now we need to upload it to Cloudinary
            # Call the upload function
            if output_filename:
                print(f"[DEBUG] Video generated: {output_filename}. Triggering upload...")
                
                # Get the upload function from Modal
                try:
                    upload_func = modal.Function.lookup("creatorify-api", "upload_video_to_cloudinary")
                    # Spawn the upload (async)
                    upload_func.spawn(id, output_filename)
                    print(f"[DEBUG] Upload task spawned for project {id}")
                    
                    # Mark as processing upload
                    db.update_status(id, "processing", 95)
                    project['status'] = 'processing'
                    project['progress'] = 95
                except Exception as upload_error:
                    print(f"[ERROR] Failed to spawn upload: {upload_error}")
                    # Fall back to marking as finished without URL
                    db.update_status(id, "finished", 100)
                    project['status'] = 'finished'
                    project['progress'] = 100
            else:
                # Something went wrong
                error_msg = "Video generated but filename not returned"
                print(f"[ERROR] {error_msg}")
                db.update_status(id, "failed", error_message=error_msg)
                project['status'] = 'failed'
                project['error_message'] = error_msg

        except TimeoutError:
            # Still running
            print(f"[DEBUG] Job still running (TimeoutError)")
            # We can't easily get progress % from Modal without a separate side-channel (like DB updates from the job)
            # For now, just keep it as processing
            if project['status'] == 'queued':
                db.update_status(id, "processing", 10)
                project['status'] = 'processing'
                project['progress'] = 10
            
        except Exception as e:
            # Execution failed
            import traceback
            error_msg = f"Modal job execution failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            db.update_status(id, "failed", error_message=error_msg)
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