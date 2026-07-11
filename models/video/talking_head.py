from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime
from uuid import UUID

class GenerationParams(BaseModel):
    """
    Advanced generation parameters for InfiniteTalk video generation.
    Users can either use presets or manually configure all parameters.
    """
    
    # === PRESET SYSTEM (Recommended) ===
    quality_preset: Optional[Literal["turbo", "fast", "balanced", "quality", "low_vram"]] = Field(
        "fast",
        description="Quality preset: 'turbo' (4 steps), 'fast' (8 steps), 'balanced' (20 steps), 'quality' (40 steps), 'low_vram' (FP8)"
    )
    
    resolution: Literal["480p", "720p"] = Field(
        "480p",
        description="Video resolution: '480p' (640x640 base) or '720p' (960x960 base). Aspect ratio auto-adjusted based on input."
    )
    
    # === MANUAL PARAMETERS (Advanced Override) ===
    # Sampling
    sample_steps: Optional[int] = Field(
        None,
        description="Number of sampling steps (1-50). If None, uses preset value. Fast=8, Balanced=20, Quality=40",
        ge=1,
        le=50
    )
    
    sample_shift: Optional[float] = Field(
        None,
        description="Sampling shift for noise schedule. If None, auto-calculated based on resolution and LoRA usage."
    )
    
    # Guidance Scales
    sample_text_guide_scale: Optional[float] = Field(
        None,
        description="Text CFG scale. If None, uses preset (Fast/Balanced=1.0, Quality=5.0)",
        ge=0.0,
        le=20.0
    )
    
    sample_audio_guide_scale: Optional[float] = Field(
        None,
        description="Audio CFG scale. If None, uses preset (Fast/Balanced=2.0, Quality=4.0)",
        ge=0.0,
        le=20.0
    )
    
    # LoRA
    lora_scale: Optional[float] = Field(
        None,
        description="LoRA influence scale (0.0-2.0). If None, uses preset (Fast/Balanced=1.0, Quality=0.0)",
        ge=0.0,
        le=2.0
    )
    
    use_lora: Optional[bool] = Field(
        None,
        description="Enable/disable LoRA. If None, auto-determined by preset (Fast/Balanced=True, Quality=False)"
    )
    
    # Performance
    color_correction_strength: float = Field(
        0.2,
        description="Color correction strength (0.0-1.0). 0=no correction, 1=full correction",
        ge=0.0,
        le=1.0
    )
    
    num_persistent_param_in_dit: Optional[int] = Field(
        0,
        description="VRAM management: 0=aggressive offload (low VRAM), None=keep in VRAM (high VRAM)",
        ge=0
    )
    
    # Advanced
    seed: Optional[int] = Field(
        None,
        description="Random seed for reproducibility. If None, uses random seed"
    )
    
    frame_num: Optional[int] = Field(
        None,
        description="Force specific frame number (must be 4n+1). If None, auto-calculated from audio duration"
    )
    
    use_quantization: Optional[bool] = Field(
        None,
        description="Use FP8 quantization. If None, uses preset default (Fast=True, Quality=False)"
    )
    
    # TeaCache & APG (always enabled by default)
    use_teacache: bool = Field(True, description="Enable TeaCache acceleration")
    teacache_thresh: float = Field(0.2, description="TeaCache threshold", ge=0.0, le=1.0)
    use_apg: bool = Field(True, description="Enable Adaptive Projected Guidance")
    
    @validator('frame_num')
    def validate_frame_num(cls, v):
        if v is not None and (v - 1) % 4 != 0:
            raise ValueError(f"frame_num must be 4n+1 (e.g., 1, 5, 9, 81, 85). Got {v}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "quality_preset": "fast",
                "resolution": "480p",
                "color_correction_strength": 0.2,
                "seed": 42
            }
        }

class ProjectCreate(BaseModel):
    user_id: str = "anonymous"
    email: Optional[str] = None
    title: str
    description: Optional[str] = None
    
    # Input files
    image_url: str = Field(..., description="URL to image or video input")
    audio_url: str = Field(..., description="URL to primary audio file (WAV/MP3)")
    audio_url_2: Optional[str] = Field(None, description="URL to secondary audio for multi-person")
    
    # Multi-person settings
    audio_order: Literal["left_right", "right_left", "meanwhile"] = Field(
        "left_right",
        description="Audio order: 'left_right' (sequential), 'right_left' (reverse), 'meanwhile' (parallel)"
    )
    
    # Text prompt
    prompt: Optional[str] = Field(
        "a person is talking",
        description="Text prompt for video generation"
    )
    
    # Generation parameters
    parameters: Optional[GenerationParams] = Field(
        default_factory=GenerationParams,
        description="Advanced generation parameters"
    )

class ProjectResponse(BaseModel):
    id: str
    user_id: Optional[str]
    title: str
    description: Optional[str]
    
    # Inputs
    image_url: str
    audio_url: str
    audio_url_2: Optional[str]
    audio_order: str
    type: str  # "single_person" or "multi_person"
    prompt: Optional[str]
    
    # Status
    call_id: Optional[str]
    status: str
    progress: int
    current_stage: Optional[str]
    
    # Output
    video_url: Optional[str]
    error_message: Optional[str]
    
    # Timestamps
    created_at: Optional[str]
    updated_at: Optional[str]
    
    # Parameters (stored as resolved)
    parameters: Optional[Dict[str, Any]]
    
    # NEW: Metadata enrichment
    resolved_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Resolved configuration showing actual parameters used"
    )
    
    estimated_time: Optional[str] = Field(
        None,
        description="Estimated completion time based on configuration"
    )
    
    # Pipeline
    pipeline: Optional[Dict[str, Any]] = None

class PaginatedProjectResponse(BaseModel):
    items: List[ProjectResponse]
    next_cursor: Optional[str]
    has_more: bool

class ProjectStatus(BaseModel):
    id: str
    status: str
    progress: int
    video_url: Optional[str] = None
    error_message: Optional[str] = None
    current_stage: Optional[str] = None
    pipeline: Optional[Dict[str, Any]] = None
    resolved_config: Optional[Dict[str, Any]] = None
    estimated_time: Optional[str] = None