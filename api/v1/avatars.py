from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel
from services.supabase_service import SupabaseService
from services.cloudinary_service import CloudinaryService
from utils.auth import get_api_key
import shutil
import tempfile
import os

router = APIRouter(dependencies=[Depends(get_api_key)])

# Dependency for Supabase
def get_db():
    return SupabaseService()

# Dependency for Cloudinary
def get_cloudinary():
    return CloudinaryService()

class AvatarResponse(BaseModel):
    avatar_id: str
    user_id: str
    name: str
    image_url: str
    created_at: Optional[str] = None

@router.post("/upload", response_model=AvatarResponse)
async def upload_avatar(
    name: str = Form(...),
    file: UploadFile = File(...),
    user_id: str = Form("anonymous"),
    db: SupabaseService = Depends(get_db),
    cloudinary: CloudinaryService = Depends(get_cloudinary)
):
    """
    Upload an avatar image to Cloudinary and save metadata to Supabase.
    """
    if not cloudinary.enabled:
        raise HTTPException(status_code=500, detail="Cloudinary service is not configured")

    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Handle empty user_id from form
    if not user_id:
        user_id = "anonymous"

    # Save uploaded file to temp file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded file: {e}")

    try:
        # Upload to Cloudinary
        image_url = cloudinary.upload_image(tmp_path)
        if not image_url:
            raise HTTPException(status_code=500, detail="Failed to upload image to Cloudinary. Check server logs for details.")
        
        # Save to Supabase
        try:
            avatar = db.create_avatar(name, image_url, user_id)
        except Exception as db_error:
            # Re-raise with specific message
            raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")

        if not avatar:
            raise HTTPException(status_code=500, detail="Failed to save avatar metadata to database (unknown error)")
            
        return avatar
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
        
    finally:
        # Cleanup temp file
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)

@router.delete("/{avatar_id}")
async def delete_avatar(
    avatar_id: str,
    db: SupabaseService = Depends(get_db),
    cloudinary: CloudinaryService = Depends(get_cloudinary)
):
    """
    Delete an avatar from Supabase and Cloudinary.
    """
    # Get avatar details first to get the image URL
    avatar = db.get_avatar(avatar_id)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
        
    # Delete from Supabase first
    success = db.delete_avatar(avatar_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete avatar from database")
        
    # Delete from Cloudinary
    # Extract public_id from URL
    # Example URL: https://res.cloudinary.com/demo/image/upload/v1234567890/infinitetalk_avatars/sample.jpg
    # public_id: infinitetalk_avatars/sample
    try:
        image_url = avatar.get("image_url")
        if image_url:
            # Simple extraction logic, might need refinement based on exact URL structure
            parts = image_url.split("/")
            # Find the version part (starts with v) or the folder part
            # Assuming standard structure with folder
            if "infinitetalk_avatars" in parts:
                idx = parts.index("infinitetalk_avatars")
                filename = parts[-1]
                public_id_with_ext = f"infinitetalk_avatars/{filename}"
                public_id = os.path.splitext(public_id_with_ext)[0]
                
                cloudinary.delete_resource(public_id)
    except Exception as e:
        print(f"Warning: Failed to delete image from Cloudinary: {e}")
        # We don't fail the request if Cloudinary delete fails, as DB record is gone.
        
    return {"detail": "Avatar deleted successfully"}

@router.get("/", response_model=List[AvatarResponse])
async def list_avatars(
    user_id: str = None,
    limit: int = 20,
    db: SupabaseService = Depends(get_db)
):
    return db.list_avatars(user_id, limit)
