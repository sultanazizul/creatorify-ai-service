from pydantic import BaseModel
from typing import Optional

# Kokoro TTS
class KokoroTTSRequest(BaseModel):
    text: str
    voice: str = "af_heart"
    speed: float = 1.0
    lang_code: str = "a"
    user_id: str = "anonymous"

# Chatterbox TTS
class ChatterboxTTSRequest(BaseModel):
    text: str
    voice_sample_id: str
    exaggeration: float = 0.5
    temperature: float = 0.8
    cfg_weight: float = 0.5
    repetition_penalty: float = 1.2
    min_p: float = 0.05
    top_p: float = 1.0
    user_id: str = "anonymous"

class MultilingualTTSRequest(BaseModel):
    text: str
    language_id: str
    voice_sample_id: Optional[str] = None
    exaggeration: float = 0.5
    temperature: float = 0.8
    cfg_weight: float = 0.5
    repetition_penalty: float = 2.0
    min_p: float = 0.05
    top_p: float = 1.0
    user_id: str = "anonymous"
