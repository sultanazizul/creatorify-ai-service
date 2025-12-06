import os
import json
from supabase import create_client, Client
from models.project_model import ProjectCreate, ProjectResponse

class SupabaseService:
    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_SERVICE_ROLE") # Use service role for backend operations
        
        if not url or not key:
            print("Warning: SUPABASE_URL or SUPABASE_SERVICE_ROLE not set. DB operations will fail.")
            self.client = None
        else:
            self.client: Client = create_client(url, key)

    def create_project(self, project_data: ProjectCreate, call_id: str, user_id: str = "anonymous") -> dict:
        if not self.client:
            return {"id": "mock-id", "status": "queued"}
            
        # Determine project type
        project_type = "multi_person" if project_data.audio_url_2 else "single_person"
        
        data = {
            "user_id": user_id,
            "title": project_data.title,
            "description": project_data.description,
            "image_url": project_data.image_url,
            "audio_url": project_data.audio_url,
            # "audio_url_2": project_data.audio_url_2, # Removed to handle conditionally
            "type": project_type,
            "audio_order": project_data.audio_order, # Added for audio ordering
            "prompt": project_data.prompt,
            "call_id": call_id,
            "status": "queued",
            "progress": 0,
            "parameters": project_data.parameters.dict() if project_data.parameters else {},
        }
        
        # Only add audio_url_2 if it exists to avoid schema errors if column is missing
        if project_data.audio_url_2:
            data["audio_url_2"] = project_data.audio_url_2
        
        try:
            response = self.client.table("projects").insert(data).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error creating project: {e}")
            raise e

    def get_project(self, project_id: str) -> dict:
        if not self.client:
            return None
        try:
            response = self.client.table("projects").select("*").eq("id", project_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error getting project: {e}")
            return None

    def update_status(self, project_id: str, status: str, progress: int = None, video_url: str = None, error_message: str = None):
        if not self.client:
            return
            
        data = {"status": status, "updated_at": "now()"}
        if progress is not None:
            data["progress"] = progress
        if video_url:
            data["video_url"] = video_url
        if error_message:
            data["error_message"] = error_message
            
        try:
            self.client.table("projects").update(data).eq("id", project_id).execute()
        except Exception as e:
            print(f"Error updating status: {e}")

    def list_projects(self, user_id: str = None, limit: int = 20, project_type: str = None):
        if not self.client:
            return []
        
        query = self.client.table("projects").select("*").order("created_at", desc=True).limit(limit)
        if user_id:
            query = query.eq("user_id", user_id)
        if project_type:
            query = query.eq("type", project_type)
            
        try:
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error listing projects: {e}")
            return []

    def delete_project(self, project_id: str) -> bool:
        if not self.client:
            return False
            
        try:
            response = self.client.table("projects").delete().eq("id", project_id).execute()
            if response.data and len(response.data) > 0:
                return True
            return False
        except Exception as e:
            print(f"Error deleting project: {e}")
            return False

    def create_avatar(self, name: str, image_url: str, user_id: str = "anonymous") -> dict:
        if not self.client:
            return {"avatar_id": "mock-id", "name": name, "image_url": image_url}
            
        data = {
            "user_id": user_id,
            "name": name,
            "image_url": image_url,
        }
        
        try:
            response = self.client.table("avatars").insert(data).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error creating avatar: {e}")
            raise e

    def get_avatar(self, avatar_id: str) -> dict:
        if not self.client:
            return None
        try:
            response = self.client.table("avatars").select("*").eq("avatar_id", avatar_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error getting avatar: {e}")
            return None

    def list_avatars(self, user_id: str = None, limit: int = 20):
        if not self.client:
            return []
        
        query = self.client.table("avatars").select("*").order("created_at", desc=True).limit(limit)
        if user_id:
            query = query.eq("user_id", user_id)
            
        try:
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error listing avatars: {e}")
            return []

    def delete_avatar(self, avatar_id: str) -> bool:
        if not self.client:
            return False
            
        try:
            response = self.client.table("avatars").delete().eq("avatar_id", avatar_id).execute()
            if response.data and len(response.data) > 0:
                return True
            return False
        except Exception as e:
            print(f"Error deleting avatar: {e}")
            return False