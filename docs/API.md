# API Reference

## Projects

### Create Project
`POST /api/v1/projects/`
Creates a new video generation project.
- **Body**: `ProjectCreate` (image_url, audio_url, etc.)
- **Returns**: `ProjectResponse`

### List Projects
`GET /api/v1/projects/`
List all projects for a user.
- **Query**: `user_id`, `limit`, `type`

### Get Project Status
`GET /api/v1/projects/{id}`
Get the status and details of a specific project.

## Audio

### TTS (Kokoro)
`POST /api/v1/tts/generate`
Generate speech from text using Kokoro-82M.

### Voice Library
`GET /api/v1/audio/voice-library/`
List available voice samples.

`POST /api/v1/audio/voice-library/`
Upload a new voice sample.

### Chatterbox TTS
`POST /api/v1/audio/chatterbox/tts/generate`
Generate TTS using Chatterbox (Voice Cloning).

### Voice Conversion
`POST /api/v1/audio/voice-conversion/convert`
Convert audio from one voice to another.

## Avatars

### Upload Avatar
`POST /api/v1/avatars/upload`
Upload a new avatar image for video generation.
