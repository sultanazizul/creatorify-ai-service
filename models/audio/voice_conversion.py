from pydantic import BaseModel

class VoiceConversionRequest(BaseModel):
    source_audio_url: str
    target_voice_sample_id: str
    user_id: str = "anonymous"
