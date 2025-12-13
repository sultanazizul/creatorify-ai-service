# Architecture Overview

Creatorify AI Service is built on a modular, domain-driven architecture designed to support rapid expansion of AI capabilities.

## High-Level Architecture

The system is composed of three main layers:

1.  **API Layer (`api/`)**: Handles HTTP requests, authentication, and routing. It is built with FastAPI and exposes RESTful endpoints.
2.  **Service Layer (`services/`)**: Contains the core business logic and AI model interactions. It is organized by domain (Audio, Video).
3.  **Infrastructure Layer (`services/infrastructure/`)**: Manages interactions with external systems like databases (Supabase) and file storage (Cloudinary).

## Domain Organization

### Audio Domain (`services/audio/`)
Handles all audio-related processing.
- **TTS**: Text-to-Speech generation using Kokoro and Chatterbox.
- **Voice Library**: Management of voice samples and cloning.
- **Voice Conversion**: Transforming voice characteristics.

### Video Domain (`services/video/`)
Handles video generation and processing.
- **Talking Head**: Generates videos from image + audio using the Wan2.1 model.

## Infrastructure & Deployment

### Modal.com
The entire application runs on [Modal](https://modal.com), a serverless platform for GPU workloads.
- **`app.py`**: The entry point that defines the Modal App, Image environment, and persistent Volumes.
- **GPU Scaling**: Heavy AI tasks (like video generation) run in isolated containers with dedicated GPUs (H100, A10G).

### Data & Storage
- **Supabase**: Stores project metadata, user info, and task status.
- **Cloudinary**: Stores generated media files (video, audio) for public access.
- **Modal Volumes**: Stores large AI model weights to avoid re-downloading them on every cold start.

## Adding New Features

To add a new feature (e.g., Image Generation):

1.  **Create a new Domain**: Create `services/image/`.
2.  **Implement Service**: Add `image_generation_service.py` with the logic.
3.  **Add Router**: Create `api/v1/routers/image.py` and expose endpoints.
4.  **Register Router**: Import and include the router in `app.py`.
