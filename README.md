# Creatorify AI Service

Platform all-in-one untuk pembuatan konten AI yang mencakup **Text-to-Speech (TTS)**, **Voice Cloning**, **Voice Conversion**, dan **AI Avatar Video Generation**. Dibangun dengan arsitektur domain-driven yang modular dan scalable.

## 🎯 Fitur Utama

### 🎙️ Audio Domain
- **Kokoro TTS** - Text-to-speech multilingual dengan 9 bahasa
- **Chatterbox Voice Cloning** - Voice cloning dengan kualitas tinggi
- **Multilingual TTS** - TTS dalam 23 bahasa dengan voice cloning
- **Voice Conversion** - Konversi suara dari audio ke target voice
- **Voice Library** - Manajemen voice samples

### 🎬 Video Domain
- **Talking Head Generation** - Generate video avatar berbicara dari gambar + audio
- **Multi-Person Support** - Support 2 orang dalam satu video
- **Audio Order Control** - Kontrol urutan audio (left-right, right-left, meanwhile)

## 🏗️ Arsitektur

Project ini menggunakan **Domain-Driven Design (DDD)** dengan pemisahan yang jelas antara domain Audio dan Video:

```
creatorify-ai-service/
├── api/v1/routers/          # API Endpoints
│   ├── audio/               # Audio endpoints (TTS, Voice Cloning, dll)
│   └── video/talking_head/  # Video endpoints (Talking Head)
├── core/                    # Core logic (Config, Security)
├── models/                  # Data Models (Pydantic schemas)
│   ├── audio/              # Audio request/response models
│   └── video/              # Video request/response models
├── services/               # Business Logic
│   ├── audio/             # Audio services
│   ├── video/             # Video services
│   └── infrastructure/    # External services (Supabase, Cloudinary)
├── vendor/                # External libraries
│   ├── chatterbox/       # Chatterbox TTS library
│   └── infinitetalk/     # InfiniteTalk video library
├── tests/                # Verification scripts
└── docs/                 # Documentation

```

## 📚 Dokumentasi

- **[Struktur Project](docs/PROJECT_STRUCTURE.md)** - Penjelasan detail struktur folder
- **[Arsitektur](docs/ARCHITECTURE.md)** - Desain sistem high-level
- **[API Documentation](docs/API.md)** - Daftar endpoint yang tersedia
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Panduan untuk developer

## 🚀 Quick Start

### Prerequisites

- Python 3.11 (Recommended) - *Note: Python 3.13 is not yet fully supported by some AI libraries*
- Modal account ([modal.com](https://modal.com))
- Supabase account (untuk database)
- Cloudinary account (untuk media storage)

### Setup Environment

1. **Clone repository**
```bash
git clone https://github.com/sultanazizul/creatorify-ai-service.git
cd creatorify-ai-service
```

2. **Install Modal CLI**
```bash
pip install modal
modal setup
```

3. **Install Dependencies (Opsional, untuk development lokal)**
   Untuk development lokal atau testing, install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**

Buat secret di Modal dengan nama `creatorify-secrets` yang berisi:
- `API_KEY` - API key untuk authentication
- `SUPABASE_URL` - URL Supabase project
- `SUPABASE_KEY` - Supabase service key
- `CLOUDINARY_CLOUD_NAME` - Cloudinary cloud name
- `CLOUDINARY_API_KEY` - Cloudinary API key
- `CLOUDINARY_API_SECRET` - Cloudinary API secret

### Deploy

```bash
# Deploy aplikasi utama
modal deploy app.py

# Deploy Chatterbox microservice
modal deploy chatterbox_app.py
```

## 🔌 API Endpoints

### Audio Endpoints

**Kokoro TTS**
- `POST /api/v1/tts/generate` - Generate TTS
- `GET /api/v1/tts/languages` - List bahasa yang didukung
- `GET /api/v1/tts/voices` - List voice yang tersedia

**Chatterbox**
- `POST /api/v1/audio/chatterbox/tts/generate` - Voice cloning TTS
- `POST /api/v1/audio/chatterbox/multilingual/generate` - Multilingual TTS
- `POST /api/v1/audio/voice-conversion/convert` - Voice conversion

**Voice Library**
- `POST /api/v1/audio/voice-library/upload` - Upload voice sample
- `GET /api/v1/audio/voice-library/` - List voice samples

### Video Endpoints

**Talking Head**
- `POST /api/v1/projects` - Create video project
- `GET /api/v1/projects/{id}/status` - Check project status
- `GET /api/v1/projects` - List projects

### Avatar Management
- `POST /api/v1/avatars/upload` - Upload avatar image
- `GET /api/v1/avatars/` - List avatars
- `DELETE /api/v1/avatars/{id}` - Delete avatar

## 🛠️ Development

### Menambahkan Fitur Baru

1. **Audio Feature** - Tambahkan di `api/v1/routers/audio/` dan `services/audio/`
2. **Video Feature** - Tambahkan di `api/v1/routers/video/` dan `services/video/`
3. **Data Models** - Definisikan di `models/audio/` atau `models/video/`

Lihat [Developer Guide](docs/DEVELOPER_GUIDE.md) untuk detail lengkap.



### Troubleshooting Installation (macOS)

If you encounter `llvmlite` errors or issues with `torch`:

1.  **Install dependencies via Homebrew:**
    ```bash
    brew install cmake llvm@15
    ```

2.  **Uninstall conflicting pip packages:**
    ```bash
    pip uninstall -y cmake
    ```

3.  **Install `llvmlite` linking to LLVM 15:**
    ```bash
    export CMAKE_PREFIX_PATH="$(brew --prefix llvm@15)"
    export LLVM_CONFIG="$(brew --prefix llvm@15)/bin/llvm-config"
    pip install llvmlite
    ```

4.  **Install remaining requirements:**
    ```bash
    pip install -r requirements.txt
    ```

## 🔐 Authentication

Semua endpoint memerlukan API Key di header:
```
X-API-Key: your-api-key-here
```

## 📦 Tech Stack

- **Framework**: FastAPI
- **Deployment**: Modal (Serverless GPU)
- **Database**: Supabase (PostgreSQL)
- **Storage**: Cloudinary
- **AI Models**:
  - Kokoro-82M (TTS)
  - Chatterbox (Voice Cloning)
  - InfiniteTalk (Talking Head)

## 🤝 Contributing

Contributions are welcome! Please read our [Developer Guide](docs/DEVELOPER_GUIDE.md) first.

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

- [Kokoro-82M](https://github.com/hexgrad/kokoro) - TTS model
- [Chatterbox](https://github.com/resemble-ai/chatterbox) - Voice cloning
- [InfiniteTalk](https://github.com/MeiGen-AI/InfiniteTalk) - Talking head generation

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

Made with ❤️ by Sultan Azizul
