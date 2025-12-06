# Creatorify AI - TTS API Documentation

This document provides details on the Text-to-Speech (TTS) API endpoints provided by the Creatorify AI Service.

## Overview

The TTS service uses the **Kokoro-82M** model to generate high-quality speech from text. The generation process is **asynchronous**:
1.  You submit a generation request.
2.  The API immediately returns a `pending` status with a `tts_id`.
3.  The system processes the request in the background.
4.  You poll the status endpoint to check for completion and retrieve the audio URL.

## Base URL
`https://<your-modal-url>` (e.g., `https://sultanazizul--creatorify-api-fastapi-app.modal.run`)

---

## Endpoints

### 1. Generate TTS (Create Project)
Creates a new TTS project and triggers background audio generation.

- **URL**: `/api/v1/tts/generate`
- **Method**: `POST`
- **Content-Type**: `application/json`

#### Request Body
| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `text` | string | Yes | - | The text to convert to speech. |
| `voice` | string | No | `af_heart` | Voice ID (e.g., `af_heart`, `af_bella`, `am_michael`). |
| `speed` | float | No | `1.0` | Speech speed (0.5 to 2.0). |
| `lang_code` | string | No | `a` | Language code (`a` for American English, `b` for British English). |
| `user_id` | string | No | `anonymous` | ID of the user creating the project. |

**Example Request:**
```json
{
  "text": "Hello, welcome to Creatorify AI.",
  "voice": "af_heart",
  "speed": 1.0,
  "lang_code": "a",
  "user_id": "user_123"
}
```

#### Response (200 OK)
Returns the created project with `pending` status.
```json
{
  "tts_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user_123",
  "text": "Hello, welcome to Creatorify AI.",
  "voice": "af_heart",
  "speed": 1.0,
  "lang_code": "a",
  "audio_url": null,
  "status": "pending",
  "created_at": "2023-10-27T10:00:00Z"
}
```

---

### 2. Get TTS Project (Check Status)
Retrieves the details of a specific TTS project. Use this to check if generation is complete.

- **URL**: `/api/v1/tts/{tts_id}`
- **Method**: `GET`

#### Path Parameters
| Parameter | Type | Description |
|---|---|---|
| `tts_id` | string | The UUID of the TTS project. |

#### Response (200 OK)
**Pending/Processing:**
```json
{
  "tts_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "progress": 0,
  "audio_url": null,
  ...
}
```

**Processing (with progress):**
```json
{
  "tts_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 60,
  "audio_url": null,
  ...
}
```

**Completed:**
```json
{
  "tts_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "audio_url": "https://res.cloudinary.com/.../tts_uuid.wav",
  ...
}
```

**Failed:**
```json
{
  "tts_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "progress": 0,
  "audio_url": null,
  ...
}
```

#### Progress Stages
| Progress | Status | Description |
|---|---|---|
| 0% | `pending` | Job queued, not started |
| 10% | `processing` | Job started |
| 30% | `processing` | Generating audio |
| 60% | `processing` | Processing audio file |
| 80% | `processing` | Uploading to Cloudinary |
| 100% | `completed` | Generation complete |

---

### 3. List TTS Projects
Retrieves a list of TTS projects, optionally filtered by user.

- **URL**: `/api/v1/tts/`
- **Method**: `GET`

#### Query Parameters
| Parameter | Type | Required | Description |
|---|---|---|---|
| `user_id` | string | No | Filter projects by user ID. |
| `limit` | integer | No | Max number of results (default 20). |

#### Response (200 OK)
```json
[
  {
    "tts_id": "550e8400-e29b-41d4-a716-446655440000",
    "text": "Hello...",
    "status": "completed",
    "audio_url": "https://...",
    ...
  },
  ...
]
```

---

### 4. Delete TTS Project
Deletes a TTS project record from the database.

- **URL**: `/api/v1/tts/{tts_id}`
- **Method**: `DELETE`

#### Path Parameters
| Parameter | Type | Description |
|---|---|---|
| `tts_id` | string | The UUID of the TTS project to delete. |

#### Response (200 OK)
```json
{
  "detail": "TTS project deleted successfully"
}
```

---

## Database Schema (Supabase)
The `tts_projects` table schema:
- `id` (uuid, primary key)
- `created_at` (timestamptz)
- `user_id` (text)
- `text` (text)
- `voice` (text)
- `speed` (float)
- `lang_code` (text)
- `audio_url` (text)
- `status` (text) - Values: `pending`, `processing`, `completed`, `failed`
- `progress` (integer) - Values: 0-100
