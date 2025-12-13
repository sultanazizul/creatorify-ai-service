import os
from typing import Optional

class Settings:
    """Simple settings class using environment variables."""
    
    @property
    def API_KEY(self) -> Optional[str]:
        return os.environ.get("API_KEY")
    
    @property
    def SUPABASE_URL(self) -> Optional[str]:
        return os.environ.get("SUPABASE_URL")
    
    @property
    def SUPABASE_KEY(self) -> Optional[str]:
        return os.environ.get("SUPABASE_KEY")
    
    @property
    def CLOUDINARY_CLOUD_NAME(self) -> Optional[str]:
        return os.environ.get("CLOUDINARY_CLOUD_NAME")
    
    @property
    def CLOUDINARY_API_KEY(self) -> Optional[str]:
        return os.environ.get("CLOUDINARY_API_KEY")
    
    @property
    def CLOUDINARY_API_SECRET(self) -> Optional[str]:
        return os.environ.get("CLOUDINARY_API_SECRET")

settings = Settings()
