# Project Structure Documentation

This document explains the organization of the **Creatorify AI Service** codebase. The project follows a **Domain-Driven Design (DDD)** approach, separating concerns into distinct domains (Audio, Video) and layers (API, Services, Models, Core).

## Directory Overview

```
creatorify-ai-service/
├── api/                    # API Layer (Routers, Endpoints)
├── core/                   # Core Application Logic (Config, Security)
├── docs/                   # Project Documentation
├── models/                 # Data Models (Pydantic Schemas)
├── services/               # Business Logic & External Services
├── tests/                  # Verification & Test Scripts
├── vendor/                 # Third-party/External Libraries
├── app.py                  # Main Application Entry Point (Modal App)
└── README.md               # Project Overview
```

## Detailed Breakdown

### 1. `api/` (API Layer)
Contains the FastAPI routers that define the HTTP endpoints.
- **`v1/routers/`**:
    - **`audio/`**: Audio-related endpoints.
        - `kokoro.py`: Kokoro TTS endpoints.
        - `chatterbox.py`: Chatterbox TTS & Voice Cloning endpoints.
        - `voice_conversion.py`: Voice Conversion endpoints.
        - `voice_library.py`: Voice sample management endpoints.
    - **`video/talking_head/`**: Video-related endpoints (specifically Talking Head).
        - `projects.py`: Video generation project management (Create, List).
        - `status.py`: Project status checking endpoints.
    - `avatars.py`: Avatar management endpoints.

### 2. `core/` (Core Logic)
Contains essential, cross-cutting application logic.
- `config.py`: Application configuration and environment variables (using Pydantic Settings).
- `security.py`: Authentication logic (API Key validation).

### 3. `models/` (Data Models)
Contains Pydantic models used for API request/response validation and database schemas.
- **`audio/`**:
    - `tts.py`: Request schemas for TTS (Kokoro & Chatterbox).
    - `voice_conversion.py`: Request schemas for Voice Conversion.
- **`video/`**:
    - `talking_head.py`: Schemas for Talking Head video projects.

### 4. `services/` (Business Logic)
Contains the core business logic and integrations with external services.
- **`audio/`**:
    - **`tts/kokoro/`**: Kokoro TTS logic.
        - `service.py`: Main TTS service class.
        - `voices.py`: Voice management for Kokoro.
- **`video/`**:
    - **`talking_head/`**: Talking Head video logic.
        - `service.py`: Placeholder for video generation logic (currently in `app.py`).
- **`infrastructure/`**:
    - `supabase.py`: Supabase database client and helper methods.
    - `cloudinary.py`: Cloudinary media storage client.

### 5. `vendor/` (External Libraries)
Contains external libraries or cloned repositories that are not available via `pip` or require custom modification.
- `chatterbox/`: Chatterbox TTS library.
- `infinitetalk/`: InfiniteTalk (Talking Head) library.

### 6. `tests/` (Testing)
Contains scripts for verifying functionality.
- `verify_tts.py`: Script to test TTS generation locally.

### 7. Root Files
- **`app.py`**: The heart of the application.
    - Defines the Modal App and Image.
    - Configures the FastAPI app.
    - Includes all routers.
    - Defines the main `Model` class for video generation (Modal Function).
    - Handles background tasks.
- **`README.md`**: General project overview and setup instructions.

## Key Changes Summary
- **Separation of Concerns**: Audio and Video logic are now completely separated.
- **Centralized Models**: All data models are in `models/`, not hidden in routers.
- **Core Logic**: Config and Auth are centralized in `core/`.
- **Clean Root**: External libs moved to `vendor/`, making the root directory cleaner.
