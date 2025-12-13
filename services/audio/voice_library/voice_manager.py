"""
Voice Manager Service
Handles voice sample storage, retrieval, and management in Supabase.
"""
from typing import List, Optional, Dict
from services.infrastructure.supabase import SupabaseService


class VoiceManager:
    """Manages voice samples in database and storage."""
    
    def __init__(self):
        self.db = SupabaseService()
    
    def create_voice_sample(
        self,
        user_id: str,
        name: str,
        audio_url: str,
        duration_seconds: float,
        description: str = None,
        language_hint: str = None,
        sample_rate: int = 24000,
        is_public: bool = False,
        metadata: dict = None
    ) -> Optional[Dict]:
        """Create a new voice sample record."""
        if not self.db.client:
            return {
                "id": "mock-voice-id",
                "name": name,
                "audio_url": audio_url
            }
        
        data = {
            "user_id": user_id,
            "name": name,
            "description": description,
            "audio_url": audio_url,
            "duration_seconds": duration_seconds,
            "sample_rate": sample_rate,
            "language_hint": language_hint,
            "is_public": is_public,
            "metadata": metadata
        }
        
        try:
            response = self.db.client.table("voice_samples").insert(data).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error creating voice sample: {e}")
            raise e
    
    def get_voice_sample(self, voice_sample_id: str) -> Optional[Dict]:
        """Get a specific voice sample by ID."""
        if not self.db.client:
            return None
        
        try:
            response = self.db.client.table("voice_samples").select("*").eq("id", voice_sample_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error getting voice sample: {e}")
            return None
    
    def list_voice_samples(
        self,
        user_id: str = None,
        include_public: bool = True,
        limit: int = 50
    ) -> List[Dict]:
        """List voice samples for a user."""
        if not self.db.client:
            return []
        
        try:
            query = self.db.client.table("voice_samples").select("*").order("created_at", desc=True).limit(limit)
            
            if user_id and include_public:
                # Get user's samples + public samples
                query = query.or_(f"user_id.eq.{user_id},is_public.eq.true")
            elif user_id:
                # Only user's samples
                query = query.eq("user_id", user_id)
            elif include_public:
                # Only public samples
                query = query.eq("is_public", True)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error listing voice samples: {e}")
            return []
    
    def delete_voice_sample(self, voice_sample_id: str, user_id: str = None) -> bool:
        """Delete a voice sample."""
        if not self.db.client:
            return False
        
        try:
            query = self.db.client.table("voice_samples").delete().eq("id", voice_sample_id)
            
            # Optional: verify ownership
            if user_id:
                query = query.eq("user_id", user_id)
            
            response = query.execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error deleting voice sample: {e}")
            return False
    
    def update_voice_sample(
        self,
        voice_sample_id: str,
        updates: Dict
    ) -> Optional[Dict]:
        """Update voice sample metadata."""
        if not self.db.client:
            return None
        
        try:
            response = self.db.client.table("voice_samples").update(updates).eq("id", voice_sample_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error updating voice sample: {e}")
            return None
