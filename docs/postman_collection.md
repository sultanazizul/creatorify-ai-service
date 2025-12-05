# Postman Collection Checklist

## Environment Variables
Create an environment in Postman with:
- `base_url`: `https://<your-workspace>--infinitetalk-api-fastapi-app.modal.run`
- `api_key`: `your-super-secret-key`

## Endpoints

### 1. Create Project
- **Method**: `POST`
- **URL**: `{{base_url}}/api/v1/projects/`
- **Headers**:
  - `X-API-Key`: `{{api_key}}`
- **Body** (JSON):
```json
{
  "title": "My First Avatar",
  "image_url": "https://example.com/image.jpg",
  "audio_url": "https://example.com/audio.wav",
  "prompt": "A talking head video",
  "parameters": {
    "sample_steps": 8,
    "sample_shift": 3.0,
    "sample_text_guide_scale": 1.0,
    "sample_audio_guide_scale": 6.0,
    "lora_scale": 1.0,
    "seed": 42
  }
}
```
- **Response** (200 OK):
```json
{
  "id": "uuid-...",
  "status": "queued",
  "call_id": "call-...",
  ...
}
```

### 2. List Projects
- **Method**: `GET`
- **URL**: `{{base_url}}/api/v1/projects/`
- **Query Params**:
  - `user_id` (optional)
  - `limit` (optional, default 20)

### 3. Get Project Details
- **Method**: `GET`
- **URL**: `{{base_url}}/api/v1/projects/{id}`

### 4. Get Project Status (Polling)
- **Method**: `GET`
- **URL**: `{{base_url}}/api/v1/projects/{id}/status`
- **Response** (Processing):
```json
{
  "id": "...",
  "status": "processing",
  "progress": 10
}
```
- **Response** (Finished):
```json
{
  "id": "...",
  "status": "finished",
  "progress": 100,
  "video_url": "https://res.cloudinary.com/..."
}
```

### 5. Delete Project
- **Method**: `DELETE`
- **URL**: `{{base_url}}/api/v1/projects/{id}`
- **Response** (200 OK):
```json
{
  "detail": "Project deleted successfully"
}
```

### 6. Get Projects by User ID
- **Method**: `GET`
- **URL**: `{{base_url}}/api/v1/projects/?user_id=user_123`
- **Response** (200 OK):
```json
[
  {
    "id": "...",
    "user_id": "user_123",
    "status": "finished",
    ...
  }
]
```
