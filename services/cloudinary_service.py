import os
import cloudinary
import cloudinary.uploader
import cloudinary.api

class CloudinaryService:
    def __init__(self):
        cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
        api_key = os.environ.get("CLOUDINARY_API_KEY")
        api_secret = os.environ.get("CLOUDINARY_API_SECRET")
        
        if cloud_name and api_key and api_secret:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret
            )
            self.enabled = True
        else:
            print("Warning: Cloudinary credentials not set. Uploads will be skipped.")
            self.enabled = False

    def upload_video(self, file_path: str, public_id: str = None) -> str:
        if not self.enabled:
            return None
            
        try:
            print(f"Uploading {file_path} to Cloudinary...")
            response = cloudinary.uploader.upload(
                file_path, 
                resource_type="video",
                public_id=public_id,
                folder="infinitetalk_outputs"
            )
            return response.get("secure_url")
        except Exception as e:
            print(f"Error uploading to Cloudinary: {e}")
            return None

    def upload_image(self, file_path: str, public_id: str = None) -> str:
        if not self.enabled:
            return None
            
        try:
            print(f"Uploading {file_path} to Cloudinary...")
            response = cloudinary.uploader.upload(
                file_path, 
                resource_type="image",
                public_id=public_id,
                folder="infinitetalk_avatars"
            )
            return response.get("secure_url")
        except Exception as e:
            print(f"Error uploading image to Cloudinary: {e}")
            return None

    def delete_resource(self, public_id: str, resource_type: str = "image") -> bool:
        if not self.enabled:
            return False
            
        try:
            print(f"Deleting {public_id} from Cloudinary...")
            response = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
            return response.get("result") == "ok"
        except Exception as e:
            print(f"Error deleting from Cloudinary: {e}")
            return False
