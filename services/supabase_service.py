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
            
        data = {
            "user_id": user_id,
            "title": project_data.title,
            "description": project_data.description,
            "image_url": project_data.image_url,
            "audio_url": project_data.audio_url,
            "prompt": project_data.prompt,
            "call_id": call_id,
            "status": "queued",
            "progress": 0,
            "parameters": project_data.parameters.dict() if project_data.parameters else {},
        }
        
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

    def list_projects(self, user_id: str = None, limit: int = 20):
        if not self.client:
            return []
        
        query = self.client.table("projects").select("*").order("created_at", desc=True).limit(limit)
        if user_id:
            query = query.eq("user_id", user_id)
            
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
