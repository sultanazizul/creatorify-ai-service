# Chatterbox TTS Microservice

Separate Modal app untuk Chatterbox TTS dengan torch 2.6.0 untuk menghindari dependency conflict dengan main app.

## Deployment

```bash
# Deploy Chatterbox microservice
modal deploy chatterbox_app.py
```

Setelah deployment, Anda akan mendapatkan URL seperti:
```
https://sultanazizul--chatterbox-tts-service-fastapi-app.modal.run
```

## API Endpoints

### 1. Health Check
```
GET /health
```

### 2. English TTS with Voice Cloning
```
POST /tts/generate
Content-Type: application/json

{
  "text": "Hello, this is a test.",
  "voice_sample_url": "https://example.com/voice.wav",  // Optional
  "exaggeration": 0.5,
  "temperature": 0.8,
  "cfg_weight": 0.5,
  "repetition_penalty": 1.2,
  "min_p": 0.05,
  "top_p": 1.0
}
```

### 3. Multilingual TTS (23 Languages)
```
POST /tts/multilingual/generate
Content-Type: application/json

{
  "text": "こんにちは世界",
  "language_id": "ja",
  "voice_sample_url": "https://example.com/voice.wav",  // Optional
  "exaggeration": 0.5,
  "temperature": 0.8
}
```

**Supported Languages:**
ar, da, de, el, en, es, fi, fr, he, hi, it, ja, ko, ms, nl, no, pl, pt, ru, sv, sw, tr, zh

### 4. Voice Changer
```
POST /vc/convert
Content-Type: application/json

{
  "source_audio_url": "https://example.com/source.wav",
  "target_voice_url": "https://example.com/target.wav"
}
```

## Integration with Main App

Update main app untuk call Chatterbox microservice via HTTP instead of running locally.

## Architecture

```
Main App (torch 2.4.1)          Chatterbox App (torch 2.6.0)
├── InfiniteTalk                ├── ChatterboxTTS
├── Kokoro TTS                  ├── ChatterboxMultilingualTTS
├── Avatar Generation           └── ChatterboxVC
└── HTTP Client ─────────────────→ FastAPI Server
```

## Benefits

- ✅ No dependency conflicts
- ✅ Independent scaling
- ✅ Easier debugging
- ✅ Can use different GPU types
- ✅ Isolated failures

## Testing

```bash
# Test health
curl https://your-url/health

# Test TTS
curl -X POST https://your-url/tts/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world"}' \
  --output test.wav
```
