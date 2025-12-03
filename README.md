# Creatorify AI Service

**Creatorify AI Service** adalah backend API untuk menghasilkan video talking head (avatar berbicara) menggunakan AI. Proyek ini mengintegrasikan model [InfiniteTalk](https://github.com/MeiGen-AI/InfiniteTalk) dengan infrastruktur modern untuk memberikan layanan video generation yang scalable dan production-ready.

## 🌟 Fitur Utama

- **AI-Powered Video Generation**: Menghasilkan video talking head dari gambar/video dan audio menggunakan InfiniteTalk model
- **RESTful API**: API berbasis FastAPI dengan autentikasi API key
- **Async Job Processing**: Sistem job queue dengan Modal untuk menangani video generation yang memakan waktu lama
- **Cloud Storage**: Integrasi dengan Cloudinary untuk hosting video hasil
- **Database Management**: Supabase untuk tracking project dan status
- **GPU Acceleration**: Optimasi dengan L40S GPU, flash-attention, dan teacache
- **LoRA Optimization**: Menggunakan FusioniX LoRA untuk hasil yang lebih baik

## 🏗️ Arsitektur

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Client    │─────▶│  FastAPI     │─────▶│   Modal     │
│             │      │  (API Layer) │      │  (GPU Jobs) │
└─────────────┘      └──────────────┘      └─────────────┘
                            │                      │
                            ▼                      ▼
                     ┌──────────────┐      ┌─────────────┐
                     │   Supabase   │      │ Modal Volume│
                     │  (Database)  │      │  (Models)   │
                     └──────────────┘      └─────────────┘
                            │                      │
                            ▼                      ▼
                     ┌──────────────┐      ┌─────────────┐
                     │  Cloudinary  │◀─────│   Output    │
                     │   (Storage)  │      │   Volume    │
                     └──────────────┘      └─────────────┘
```

### Komponen Utama

1. **FastAPI Application** (`app.py`): Web server yang menyediakan REST API endpoints
2. **Modal GPU Class**: Menjalankan model InfiniteTalk pada GPU untuk video generation
3. **Supabase Service**: Mengelola data project dan tracking status
4. **Cloudinary Service**: Upload dan hosting video hasil generation
5. **API Routes**: 
   - `/api/v1/projects` - CRUD operations untuk project
   - `/api/v1/projects/{id}/status` - Polling status generation

## 📋 Prerequisites

1. **Modal Account**: Daftar di [modal.com](https://modal.com)
2. **Supabase Account**: Daftar di [supabase.com](https://supabase.com)
3. **Cloudinary Account**: Daftar di [cloudinary.com](https://cloudinary.com)
4. **Python 3.11+**
5. **Git & Git LFS**

## 🚀 Installation & Deployment

### 1. Clone Repository

```bash
git clone <repository-url>
cd creatorify-ai-service
```

### 2. Install Modal CLI

```bash
pip install modal
modal setup
```

### 3. Setup Secrets di Modal

Buat secrets berikut di Modal dashboard:

**a. Supabase Secrets** (`supabase-secrets`):
```bash
modal secret create supabase-secrets \
  SUPABASE_URL=your-supabase-url \
  SUPABASE_KEY=your-supabase-anon-key
```

**b. Cloudinary Secrets** (`cloudinary-secrets`):
```bash
modal secret create cloudinary-secrets \
  CLOUDINARY_CLOUD_NAME=your-cloud-name \
  CLOUDINARY_API_KEY=your-api-key \
  CLOUDINARY_API_SECRET=your-api-secret
```

**c. API Key Secret** (`api-key-secret`):
```bash
modal secret create api-key-secret \
  API_KEY=your-secure-api-key
```

### 4. Setup Supabase Database

Buat tabel `projects` di Supabase dengan schema berikut:

```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id TEXT,
  title TEXT NOT NULL,
  description TEXT,
  image_url TEXT NOT NULL,
  audio_url TEXT NOT NULL,
  prompt TEXT,
  call_id TEXT,
  status TEXT DEFAULT 'queued',
  progress INTEGER DEFAULT 0,
  video_url TEXT,
  error_message TEXT,
  parameters JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index untuk query yang sering digunakan
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);
```

### 5. Deploy ke Modal

```bash
modal deploy app.py
```

Deployment pertama akan memakan waktu beberapa menit karena harus download model weights (~50GB). Deployment selanjutnya akan lebih cepat karena model sudah di-cache di Modal Volume.

## 📖 API Documentation

### Base URL

```
https://<username>--infinitetalk-api-fastapi-app.modal.run
```

### Authentication

Semua endpoint memerlukan API key di header:

```bash
X-API-Key: your-api-key
```

### Endpoints

#### 1. Create Project

Membuat project baru dan memulai video generation.

**Request:**
```http
POST /api/v1/projects
Content-Type: application/json
X-API-Key: your-api-key

{
  "title": "My Talking Avatar",
  "description": "Test video generation",
  "image_url": "https://example.com/portrait.jpg",
  "audio_url": "https://example.com/speech.mp3",
  "prompt": "A person is talking",
  "parameters": {
    "sample_steps": 8,
    "sample_shift": 3.0,
    "sample_text_guide_scale": 1.0,
    "sample_audio_guide_scale": 6.0,
    "lora_scale": 1.0,
    "color_correction_strength": 0.2,
    "seed": 42
  }
}
```

**Response:**
```json
{
  "id": "uuid-here",
  "user_id": null,
  "title": "My Talking Avatar",
  "description": "Test video generation",
  "image_url": "https://example.com/portrait.jpg",
  "audio_url": "https://example.com/speech.mp3",
  "prompt": "A person is talking",
  "call_id": "modal-call-id",
  "status": "queued",
  "progress": 0,
  "video_url": null,
  "error_message": null,
  "created_at": "2025-12-03T10:00:00Z",
  "updated_at": "2025-12-03T10:00:00Z",
  "parameters": { ... }
}
```

#### 2. Get Project Status

Mengecek status generation dan mendapatkan video URL jika sudah selesai.

**Request:**
```http
GET /api/v1/projects/{project_id}/status
X-API-Key: your-api-key
```

**Response:**
```json
{
  "id": "uuid-here",
  "status": "finished",
  "progress": 100,
  "video_url": "https://res.cloudinary.com/.../video.mp4",
  "error_message": null
}
```

**Status Values:**
- `queued`: Job sudah di-submit ke Modal
- `processing`: Job sedang diproses
- `finished`: Video berhasil di-generate dan di-upload
- `failed`: Terjadi error

#### 3. List Projects

Mendapatkan list semua project.

**Request:**
```http
GET /api/v1/projects?user_id=optional&limit=20
X-API-Key: your-api-key
```

**Response:**
```json
[
  {
    "id": "uuid-1",
    "title": "Project 1",
    "status": "finished",
    ...
  },
  {
    "id": "uuid-2",
    "title": "Project 2",
    "status": "processing",
    ...
  }
]
```

#### 4. Get Project Details

Mendapatkan detail lengkap sebuah project.

**Request:**
```http
GET /api/v1/projects/{project_id}
X-API-Key: your-api-key
```

## 🔧 Generation Parameters

Parameter yang dapat dikustomisasi untuk video generation:

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `sample_steps` | int | 8 | 1-50 | Jumlah sampling steps (lebih tinggi = lebih detail, lebih lambat) |
| `sample_shift` | float | 3.0 | - | Sampling shift parameter |
| `sample_text_guide_scale` | float | 1.0 | - | Text guidance scale |
| `sample_audio_guide_scale` | float | 6.0 | - | Audio guidance scale (lebih tinggi = lebih mengikuti audio) |
| `lora_scale` | float | 1.0 | 0-2 | LoRA strength (1.0 = default, >1 = stronger effect) |
| `color_correction_strength` | float | 0.2 | 0-1 | Kekuatan color correction |
| `seed` | int | random | - | Random seed untuk reproducibility |
| `frame_num` | int | auto | - | Force specific frame count (advanced, auto-calculated dari audio duration) |

## 💡 Usage Examples

### Python Example

```python
import requests
import time

API_URL = "https://<username>--infinitetalk-api-fastapi-app.modal.run"
API_KEY = "your-api-key"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# 1. Create project
project_data = {
    "title": "Test Avatar",
    "image_url": "https://example.com/face.jpg",
    "audio_url": "https://example.com/speech.mp3",
    "prompt": "A person is talking about AI",
    "parameters": {
        "sample_steps": 8,
        "seed": 42
    }
}

response = requests.post(
    f"{API_URL}/api/v1/projects",
    headers=headers,
    json=project_data
)
project = response.json()
project_id = project["id"]

print(f"Project created: {project_id}")

# 2. Poll for status
while True:
    response = requests.get(
        f"{API_URL}/api/v1/projects/{project_id}/status",
        headers=headers
    )
    status = response.json()
    
    print(f"Status: {status['status']} - Progress: {status['progress']}%")
    
    if status["status"] == "finished":
        print(f"Video URL: {status['video_url']}")
        break
    elif status["status"] == "failed":
        print(f"Error: {status['error_message']}")
        break
    
    time.sleep(10)  # Poll every 10 seconds
```

### cURL Example

```bash
# Set variables
API_URL="https://<username>--infinitetalk-api-fastapi-app.modal.run"
API_KEY="your-api-key"

# Create project
PROJECT_ID=$(curl -s -X POST "$API_URL/api/v1/projects" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Video",
    "image_url": "https://example.com/portrait.jpg",
    "audio_url": "https://example.com/audio.mp3",
    "prompt": "A person talking"
  }' | jq -r '.id')

echo "Project ID: $PROJECT_ID"

# Check status
curl -X GET "$API_URL/api/v1/projects/$PROJECT_ID/status" \
  -H "X-API-Key: $API_KEY"
```

## 🔍 Model Details

### InfiniteTalk Model

Project ini menggunakan InfiniteTalk, sebuah model AI untuk menghasilkan video talking head dengan fitur:

- **Input**: Gambar/video wajah + audio speech
- **Output**: Video dengan lip-sync yang natural
- **Model Size**: ~14B parameters (Wan 2.1 I2V)
- **Resolution**: 480p (dapat di-upscale)
- **Frame Rate**: 25 FPS
- **Duration**: Auto-calculated dari audio duration

### Optimizations

- **FusioniX LoRA**: Meningkatkan kualitas dan konsistensi
- **Flash Attention**: Mempercepat inference
- **TeaCache**: Caching untuk efisiensi
- **GPU Snapshots**: Fast cold start dengan Modal

## 📁 Project Structure

```
creatorify-ai-service/
├── app.py                      # Main Modal application
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       ├── projects.py         # Project CRUD endpoints
│       └── status.py           # Status polling endpoint
├── models/
│   ├── __init__.py
│   └── project_model.py        # Pydantic models
├── services/
│   ├── __init__.py
│   ├── supabase_service.py     # Supabase integration
│   └── cloudinary_service.py   # Cloudinary integration
├── utils/
│   ├── __init__.py
│   └── auth.py                 # API key authentication
├── infinitetalk/               # InfiniteTalk model code (git subtree)
├── outputs/                    # Local output directory
└── README.md
```

## 🐛 Troubleshooting

### Model Download Issues

Jika model gagal di-download:
1. Pastikan Modal volume `infinitetalk-models` ada
2. Check Hugging Face access (beberapa model mungkin gated)
3. Lihat logs dengan `modal logs infinitetalk-api`

### GPU Out of Memory

Jika terjadi OOM error:
1. Reduce `sample_steps` (default: 8)
2. Gunakan video/audio yang lebih pendek
3. Upgrade ke GPU dengan VRAM lebih besar

### Video Generation Timeout

Modal function timeout default adalah 2700 detik (45 menit). Untuk video yang sangat panjang, sesuaikan timeout di `app.py`.

### Cloudinary Upload Failed

Pastikan:
1. Credentials Cloudinary benar
2. Account memiliki quota yang cukup
3. File size tidak melebihi limit

## 📚 Resources

- [InfiniteTalk Paper](https://arxiv.org/pdf/2508.14033)
- [InfiniteTalk Repository](https://github.com/MeiGen-AI/InfiniteTalk)
- [Modal Documentation](https://modal.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Supabase Documentation](https://supabase.com/docs)
- [Cloudinary Documentation](https://cloudinary.com/documentation)

## 🔄 Development Notes

### Git Subtree Management

InfiniteTalk code diintegrasikan menggunakan git subtree:

```bash
# Initial add (sudah dilakukan)
git subtree add --prefix infinitetalk https://github.com/MeiGen-AI/InfiniteTalk main --squash

# Update ke versi terbaru
git subtree pull --prefix infinitetalk https://github.com/MeiGen-AI/InfiniteTalk main --squash
```

### Local Development

Untuk testing lokal tanpa deploy:

```bash
# Run Modal function locally
modal run app.py

# Serve FastAPI locally (requires Modal volumes mounted)
modal serve app.py
```

### Changes to InfiniteTalk

Modifikasi yang dilakukan pada InfiniteTalk base repo:
- `generate_infinitetalk.py`: Attention fix untuk compatibility
- Environment variable setup untuk distributed training

## 📝 License

Project ini menggunakan InfiniteTalk model yang memiliki lisensi sendiri. Pastikan untuk mematuhi terms of use dari:
- InfiniteTalk model
- Wan model
- Modal platform
- Cloudinary service

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📧 Support

Untuk pertanyaan atau issues, silakan buka issue di repository ini.
