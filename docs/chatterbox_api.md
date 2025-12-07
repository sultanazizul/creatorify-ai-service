# Creatorify AI - Chatterbox API Documentation

Complete API documentation for Chatterbox TTS features including voice cloning, multilingual TTS, and voice conversion.

---

## Base URL
`https://<your-modal-url>` (e.g., `https://sultanazizul--creatorify-api-fastapi-app.modal.run`)

---

## 🎤 Voice Library Management

### 1. Upload Voice Sample
Upload a voice sample for cloning (3-10 seconds recommended).

**Endpoint:** `POST /api/v1/audio/voice-library/upload`  
**Content-Type:** `multipart/form-data`

**Request:**
```
audio_file: <file upload> (required)
name: string (required)
description: string (optional)
language_hint: string (optional, e.g., "en", "ja")
user_id: string (default: "anonymous")
is_public: boolean (default: false)
```

**Response (200 OK):**
```json
{
  "voice_sample_id": "uuid",
  "name": "My Voice",
  "audio_url": "https://cloudinary.../voice.wav",
  "duration_seconds": 8.5,
  "user_id": "user_123",
  "created_at": "2023-10-27T10:00:00Z"
}
```

### 2. List Voice Samples
**Endpoint:** `GET /api/v1/audio/voice-library?user_id=user_123&include_public=true&limit=50`

### 3. Get Voice Sample
**Endpoint:** `GET /api/v1/audio/voice-library/{voice_sample_id}`

### 4. Delete Voice Sample
**Endpoint:** `DELETE /api/v1/audio/voice-library/{voice_sample_id}?user_id=user_123`

---

## 🗣️ Voice Cloning TTS (English)

### Generate TTS with Voice Cloning
**Endpoint:** `POST /api/v1/audio/chatterbox/tts/generate`

**Request:**
```json
{
  "text": "Hello, this is a test of voice cloning.",
  "voice_sample_id": "uuid",
  "exaggeration": 0.7,
  "temperature": 0.8,
  "cfg_weight": 0.5,
  "repetition_penalty": 1.2,
  "min_p": 0.05,
  "top_p": 1.0,
  "user_id": "user_123"
}
```

**Parameters:**
- `text` (string, required): Text to synthesize
- `voice_sample_id` (string, required): Voice sample from library
- `exaggeration` (float, 0.0-1.0): Emotion control (0=monotone, 1=expressive)
- `temperature` (float): Sampling temperature
- `cfg_weight` (float): Classifier-free guidance weight
- `repetition_penalty` (float): Penalty for repetition
- `min_p`, `top_p` (float): Sampling thresholds

**Response (200 OK):**
```json
{
  "project_id": "uuid",
  "status": "pending",
  "progress": 0,
  "project_type": "tts"
}
```

---

## 🌍 Multilingual TTS (23 Languages)

### Generate Multilingual TTS
**Endpoint:** `POST /api/v1/audio/chatterbox/multilingual/generate`

**Request:**
```json
{
  "text": "こんにちは世界",
  "language_id": "ja",
  "voice_sample_id": "uuid",
  "exaggeration": 0.5,
  "temperature": 0.8,
  "user_id": "user_123"
}
```

**Supported Languages:**
```
ar (Arabic), da (Danish), de (German), el (Greek), en (English),
es (Spanish), fi (Finnish), fr (French), he (Hebrew), hi (Hindi),
it (Italian), ja (Japanese), ko (Korean), ms (Malay), nl (Dutch),
no (Norwegian), pl (Polish), pt (Portuguese), ru (Russian),
sv (Swedish), sw (Swahili), tr (Turkish), zh (Chinese)
```

### Get Supported Languages
**Endpoint:** `GET /api/v1/audio/chatterbox/multilingual/languages`

**Response:**
```json
{
  "languages": {
    "ar": "Arabic",
    "ja": "Japanese",
    "zh": "Chinese",
    ...
  }
}
```

---

## 🔄 Voice Conversion

### Convert Voice (URL)
**Endpoint:** `POST /api/v1/audio/voice-conversion/convert`

**Request:**
```json
{
  "source_audio_url": "https://cloudinary.../source.wav",
  "target_voice_sample_id": "uuid",
  "user_id": "user_123"
}
```

### Convert Voice (File Upload)
**Endpoint:** `POST /api/v1/audio/voice-conversion/convert-upload`  
**Content-Type:** `multipart/form-data`

**Request:**
```
source_audio: <file upload> (required)
target_voice_sample_id: string (required)
user_id: string (default: "anonymous")
```

---

## 📊 Project Status & Management

### Get Project Status
**Endpoint:** `GET /api/v1/audio/chatterbox/projects/{project_id}`

**Response:**
```json
{
  "project_id": "uuid",
  "status": "completed",
  "progress": 100,
  "audio_url": "https://cloudinary.../output.wav",
  "project_type": "tts",
  "created_at": "2023-10-27T10:00:00Z"
}
```

**Status Values:**
- `pending`: Queued
- `processing`: In progress (check `progress` 0-100)
- `completed`: Done (check `audio_url`)
- `failed`: Error (check `error_message`)

### List Projects
**Endpoint:** `GET /api/v1/audio/chatterbox/projects?user_id=user_123&project_type=tts&limit=50`

### Delete Project
**Endpoint:** `DELETE /api/v1/audio/chatterbox/projects/{project_id}`

---

## 🎯 Example Workflow

### 1. Upload Voice Sample
```bash
curl -X POST https://your-url/api/v1/audio/voice-library/upload \
  -F "audio_file=@my_voice.wav" \
  -F "name=My Voice" \
  -F "user_id=user_123"
```

### 2. Generate TTS
```bash
curl -X POST https://your-url/api/v1/audio/chatterbox/tts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "voice_sample_id": "voice-uuid",
    "exaggeration": 0.7,
    "user_id": "user_123"
  }'
```

### 3. Check Status
```bash
curl https://your-url/api/v1/audio/chatterbox/projects/project-uuid
```

---

## 💡 Tips & Best Practices

1. **Voice Samples**: 3-10 seconds of clear speech works best
2. **Exaggeration**: 0.5 = neutral, 0.7-0.8 = expressive, 0.3 = calm
3. **Cross-lingual**: Clone voice in one language, generate in another!
4. **Polling**: Poll status every 2-3 seconds for progress updates
5. **Error Handling**: Check `status` and `error_message` fields

---

## 🔧 Database Schema

### `voice_samples` Table
- `id` (uuid, primary key)
- `user_id` (text)
- `name` (text)
- `audio_url` (text)
- `duration_seconds` (float)
- `language_hint` (text)
- `is_public` (boolean)

### `chatterbox_projects` Table
- `id` (uuid, primary key)
- `user_id` (text)
- `project_type` (text): 'tts', 'multilingual_tts', 'voice_conversion'
- `text` (text)
- `language_id` (text)
- `voice_sample_id` (uuid, foreign key)
- `audio_url` (text)
- `status` (text)
- `progress` (integer, 0-100)
- `error_message` (text)
