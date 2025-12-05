from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

class GenerationParams(BaseModel):
    sample_steps: int = Field(8, description="Number of sampling steps", ge=1, le=50)
    sample_shift: float = Field(3.0, description="Sampling shift")
    sample_text_guide_scale: float = Field(1.0, description="Text guidance scale")
    sample_audio_guide_scale: float = Field(6.0, description="Audio guidance scale")
    lora_scale: float = Field(1.0, description="LoRA scale")
    color_correction_strength: float = Field(0.2, description="Color correction strength")
    seed: Optional[int] = Field(None, description="Random seed")
    frame_num: Optional[int] = Field(None, description="Force specific frame number (advanced)")

class ProjectCreate(BaseModel):
    user_id: Optional[str] = "anonymous"
    title: str
    description: Optional[str] = None
    image_url: str
    audio_url: str
    prompt: Optional[str] = None
    parameters: Optional[GenerationParams] = Field(default_factory=GenerationParams)

class ProjectResponse(BaseModel):
    id: str
    user_id: Optional[str]
    title: str
    description: Optional[str]
    image_url: str
    audio_url: str
    prompt: Optional[str]
    call_id: Optional[str]
    status: str
    progress: int
    video_url: Optional[str]
    error_message: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    parameters: Optional[Dict[str, Any]]

class ProjectStatus(BaseModel):
    id: str
    status: str
    progress: int
    video_url: Optional[str]
    error_message: Optional[str]
