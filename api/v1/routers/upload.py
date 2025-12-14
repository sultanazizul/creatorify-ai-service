from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from services.infrastructure.cloudinary import CloudinaryService
from core.security import get_api_key

router = APIRouter(dependencies=[Depends(get_api_key)])

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    resource_type: str = "auto"
):
    """
    Upload a file to Cloudinary and return the secure URL.
    resource_type: "image", "video", or "auto" (default)
    """
    cloudinary = CloudinaryService()
    if not cloudinary.enabled:
        raise HTTPException(status_code=500, detail="Cloudinary service is not configured")

    try:
        # Determine folder based on resource type or mime type
        folder = "Creatorify/Temp Files"
        if resource_type == "image" or (file.content_type and file.content_type.startswith("image/")):
            resource_type = "image"
        elif resource_type == "video" or (file.content_type and file.content_type.startswith("audio/")) or (file.content_type and file.content_type.startswith("video/")):
             # Cloudinary treats audio as video usually
            resource_type = "video"

        response = cloudinary.upload_file_obj(
            file.file, 
            resource_type=resource_type,
            folder=folder
        )
        
        if not response:
             raise HTTPException(status_code=500, detail="Failed to upload file to Cloudinary")
             
        # response is a dict with 'secure_url', 'public_id', etc.
        return {
            "id_file": response.get("public_id"),
            "url": response.get("secure_url"),
            "type": resource_type
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id_file:path}")
async def delete_file(
    id_file: str,
    resource_type: str = None # Make optional to auto-detect
):
    """
    Delete a file from Cloudinary using its public_id (id_file).
    If resource_type is not provided, it attempts to delete as 'image', then 'video'.
    """
    cloudinary = CloudinaryService()
    if not cloudinary.enabled:
         raise HTTPException(status_code=500, detail="Cloudinary service is not configured")

    target_types = [resource_type] if resource_type else ["image", "video"]
    success = False
    
    for r_type in target_types:
        if cloudinary.delete_resource(id_file, resource_type=r_type):
            success = True
            break
            
    if not success:
        raise HTTPException(status_code=404, detail=f"File not found or failed to delete (tried: {target_types})")
        
    return {"detail": "File deleted successfully"}
