# Creatorify AI Service - All-in-One Content Creation Platform

Creatorify AI is a comprehensive, modular platform designed to power the next generation of content creation tools. It leverages state-of-the-art open-source AI models to provide capabilities across Audio, Video, and Image domains.

## 🚀 Features

### 🎥 AI Video
- **Talking Head Generation**: Create realistic talking head videos from a single image and audio input using the Wan2.1 model (via InfiniteTalk).
- **Multi-Person Conversations**: Support for multiple audio inputs to create conversational videos.

### 🎙️ AI Audio
- **Text-to-Speech (TTS)**: High-quality TTS using **Kokoro-82M** and **Chatterbox**.
- **Voice Cloning**: Clone voices from a short audio sample.
- **Voice Conversion**: Convert one voice to another while preserving intonation.
- **Multilingual Support**: Generate speech in over 20 languages.

### 🖼️ AI Image (Coming Soon)
- Image generation and editing capabilities.

## 🏗️ Architecture

The project follows a Domain-Driven Design (DDD) approach to ensure scalability and maintainability.

```
creatorify-ai-service/
├── api/                # API Layer (FastAPI routers)
│   └── v1/
│       └── routers/    # Domain-specific routes (Audio, Video, Projects)
├── core/               # Core configurations and utilities
├── services/           # Business Logic Layer
│   ├── audio/          # Audio domain services (TTS, VC, Cloning)
│   ├── video/          # Video domain services (Talking Head)
│   └── infrastructure/ # External services (Supabase, Cloudinary)
├── models/             # Data Models (Pydantic & DB)
└── docs/               # Detailed Documentation
```

## 🛠️ Tech Stack

- **Framework**: FastAPI (Python)
- **Infrastructure**: Modal.com (Serverless GPU computing)
- **Database**: Supabase (PostgreSQL)
- **Storage**: Cloudinary (Media assets) & Modal Volumes (Model weights)
- **AI Models**:
    - Video: Wan2.1 (InfiniteTalk)
    - Audio: Kokoro-82M, Chatterbox

## 📖 Documentation

- **[Project Structure](docs/PROJECT_STRUCTURE.md)**: Detailed explanation of folders and files.
- **[Architecture](docs/ARCHITECTURE.md)**: High-level system design.
- **[API Documentation](docs/API.md)**: List of available endpoints.
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)**: How to contribute and add features.

## ⚡ Getting Started

### Prerequisites
- Python 3.10+
- Modal account and CLI configured
- Supabase project
- Cloudinary account

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/creatorify-ai-service.git
   cd creatorify-ai-service
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up secrets in Modal:
   ```bash
   modal secret create supabase-secrets DB_URL=... DB_KEY=...
   modal secret create cloudinary-secrets CLOUDINARY_URL=...
   ```

### Running the API

Deploy the app to Modal:
```bash
modal deploy app.py
```

Or run interactively for development:
```bash
modal serve app.py
```

## 🤝 Contributing

We welcome contributions! Please see the [Developer Guide](docs/DEVELOPER_GUIDE.md) for details on how to add new features or models.
