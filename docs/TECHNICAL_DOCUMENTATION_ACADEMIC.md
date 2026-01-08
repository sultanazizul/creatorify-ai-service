# Dokumentasi Teknis Backend dan Pipeline Kecerdasan Buatan (Creatorify AI)

## 1. Pendahuluan
Dokumen ini menyajikan analisis teknis mendalam mengenai arsitektur, implementasi, dan pipeline orkestrasi sistem "Creatorify AI Service". Sistem ini dirancang untuk memproses tugas-tugas generatif media yang intensif secara komputasi (video avatar dan sintesis suara) menggunakan arsitektur *serverless GPU* yang terdistribusi.

## 2. Arsitektur Sistem Global

Sistem dibangun menggunakan pola arsitektur **Microservices** yang diorkestrasi dalam lingkungan **Serverless Container**.

### 2.1 Komponen Infrastruktur Utama
1.  **Orchestration Logic Layer (Modal.com)**
    *   Platform ini bertindak sebagai tulang punggung eksekusi kode.
    *   **Container Runtime**: Menggunakan *custom Docker image* berbasis `pytorch/pytorch:2.4.1-cuda12.1-cudnn9-devel`.
    *   **Resource Allocation**:
        *   **GPU Tier H100**: Dialokasikan khusus untuk inferensi model video besar (Wan2.1, 14 Miliar parameter).
        *   **GPU Tier A10G**: Dialokasikan untuk tugas sintesis audio (Chatterbox TTS) yang lebih ringan namun membutuhkan akselerasi.
    *   **Persistent Storage**:
        *   `/models` (Modal Volume `creatorify-models`): Menyimpan bobot model AI berukuran besar (>50GB) untuk menghindari *cold-start latency* akibat pengunduhan berulang.
        *   `/outputs` (Modal Volume `creatorify-outputs`): *Staging area* untuk hasil generasi sebelum diunggah ke penyimpanan awan.

2.  **API Gateway Layer (FastAPI)**
    *   Diimplementasikan menggunakan framework **FastAPI** (`v2.0.0`) dalam `app.py`.
    *   Berfungsi sebagai antarmuka RESTful tunggal untuk klien (Frontend/Mobile).
    *   Menggunakan pola **Dependency Injection** untuk layanan infrastruktur (Supabase, Cloudinary) dan keamanan (API Key Bearer Token).
    *   Mengelola *Asynchronous Task Dispatching* ke worker GPU Modal menggunakan metode `.spawn()`.

3.  **Data Persistence Layer (Supabase)**
    *   Digunakan sebagai *Source of Truth* untuk metadata sistem.
    *   **Skema Database (Inferred)**:
        *   `projects`: Menyimpan status generasi video (`queued`, `processing`, `completed`), URL aset input/output, dan konfigurasi parameter.
        *   `avatars`: Katalog aset avatar pengguna dan publik.
        *   `voice_samples`: Metadata sampel suara untuk fitur *Voice Cloning*.
        *   `chatterbox_projects`: Riwayat tugas TTS lanjutan.
        *   `tts_projects`: Riwayat tugas TTS standar (Kokoro).

4.  **Media Storage Layer (Cloudinary)**
    *   Penyimpanan objek untuk aset video dan audio.
    *   Struktur Direktori Terorganisir:
        *   `Creatorify/AI Video Output/Talking Video/Infinitalk/{Type}`
        *   `Creatorify/Avatar Assets/{Public|Users}`
        *   `Creatorify/AI Audio Output/Kokoro82`

## 3. Spesifikasi Pipeline Kecerdasan Buatan (AI Pipeline)

Pipeline ini terbagi menjadi dua domain utama: Video Generatif (Talking Avatar) dan Audio Generatif (TTS).

### 3.1 Pipeline Video 'Talking Head' (Infinitalk)
Fitur ini menghasilkan video avatar yang berbicara sesuai dengan audio input.

**A. Alur Eksekusi (Orkestrasi):**
1.  **Request Entry**: API menerima permintaan via endpoint `POST /api/v1/projects/`.
    *   Input: `image_url` (wajah), `audio_url` (suara), `prompt` (opsional).
    *   Validasi: Menggunakan Pydantic schema `ProjectCreate`.
2.  **Task Queuing**:
    *   Sistem mencatat entri baru di tabel `projects` dengan status `queued`.
    *   Fungsi `Model().submit.spawn(...)` dipanggil, memicu worker serverless baru di Modal.
3.  **Asset Preprocessing (Worker H100)**:
    *   `_download_and_validate()`: Mengunduh aset ke memori lokal container.
    *   Validasi MIME type menggunakan `libmagic` (mencegah serangan file berbahaya).
    *   `librosa`: Analisis durasi audio untuk menghitung jumlah frame video yang dibutuhkan (25 FPS).
4.  **Inference (Model Core)**:
    *   **Model Backbone**: `Wan2.1-I2V-14B-480P` (Image-to-Video Diffusion Model, 14B Params).
    *   **Motion Module**: `InfiniteTalk` checkpoint khusus untuk *lip-sync*.
    *   **Conditioning**:
        *   **Visual**: CLIP Vision Encoder (`open-clip-xlm-roberta-large-vit-huge-14`) mengekstrak fitur visual dari gambar avatar.
        *   **Audio**: Chinese Wav2Vec2 (`chinese-wav2vec2-base`) mengekstrak fitur fonetik dari audio untuk memandu gerakan bibir.
        *   **Text**: T5 Encoder (`umt5-xxl`) memproses prompt teks.
    *   **LoRA**: `FusionX_LoRa` diterapkan untuk penyempurnaan gaya visual.
5.  **Post-processing**:
    *   Hasil video (`.mp4`) disimpan sementara di Volume `/outputs`.
    *   Pemanggilan fungsi terpisah `upload_video_to_cloudinary` untuk mengunggah hasil final.
    *   Pembaruan status database menjadi `finished` beserta `video_url`.

### 3.2 Pipeline Audio (TTS & Voice Cloning)
Sistem memiliki dua strategi berbeda untuk sintesis suara:

**A. On-Device TTS (Kokoro-82M)**
*   **Implementasi**: Berjalan *in-process* di dalam container API utama (`services/audio/tts/kokoro/service.py`).
*   **Karakteristik**: Latensi rendah, model ringan (82M parameter).
*   **Penggunaan**: TTS standar multi-bahasa tanpa kloning suara.
*   **Output**: WAV 24kHz.

**B. Microservice TTS (Chatterbox)**
*   **Implementasi**: Arsitektur **Service-to-Service** communication.
*   **Dependensi Eksternal**: Memanggil layanan eksternal di `sultanazizul--chatterbox-tts-service-fastapi-app.modal.run`.
*   **Metode**: Menggunakan `httpx.Client` untuk mengirim payload JSON ke microservice tersebut.
*   **Fitur**:
    *   **Zero-Shot Voice Cloning**: Menggunakan `voice_sample_id` untuk meniru karakteristik vokal referensi.
    *   **Kontrol Emosi**: Parameter `exaggeration`, `temperature`.
    *   **Cross-Lingual**: Mendukung 23 bahasa dengan kemampuan mempertahankan identitas suara antar bahasa (dibuktikan di `multilingual_service.py`).

## 4. Spesifikasi API Endpoint

### 4.1 Modul Projects (Video)
*   **`POST /api/v1/projects/`**: Membuat tugas generasi video baru.
    *   *Payload*: `{ "image_url": "...", "audio_url": "...", "prompt": "..." }`
*   **`GET /api/v1/projects/{id}`**: Polling status tugas. Mengembalikan persentase `progress` (0-100).
*   **`GET /api/v1/projects/`**: Daftar riwayat proyek pengguna.

### 4.2 Modul Audio (Chatterbox & Voice Library)
*   **`POST /api/v1/audio/chatterbox/tts/generate`**: Request TTS dengan kloning suara (Bahasa Inggris).
*   **`POST /api/v1/audio/chatterbox/multilingual/generate`**: Request TTS multi-bahasa.
*   **`POST /api/v1/voices/`**: (Inferensi dari `voice_library`) Mengunggah sampel suara referensi untuk kloning.

### 4.3 Modul Assets (Avatars & Upload)
*   **`POST /api/v1/avatars/upload`**: Mengunggah gambar avatar. Mendukung opsi `is_public` untuk aset global.
*   **`POST /api/v1/upload/`**: Utilitas umum untuk mengunggah file media sementara (Resource Type: `auto`).

## 5. Keamanan dan Data
*   **Autentikasi API**: Menggunakan skema `Bearer Token` sederhana yang divalidasi via `core.security.get_api_key` terhadap `modal.Secret`.
*   **Isolasi Data**: Setiap *record* database memiliki kolom `user_id`. Query filter di `SupabaseService` membatasi akses data:
    *   Data pribadi (`user_id == current_user`).
    *   Data publik (`is_public == true`).
*   **Manajemen Secrets**: Kredensial sensitif (Supabase Key, Cloudinary Secret, HuggingFace Token) dikelola oleh `modal.Secret` dan diinjeksikan sebagai *Environment Variables* hanya pada container yang berjalan.

## 6. Pustaka & Dependensi Kunci
*   **Backend**: `fastapi`, `uvicorn`, `pydentic`, `httpx`.
*   **AI/ML Framework**: `torch` (PyTorch 2.4+), `diffusers`, `transformers`.
*   **Audio/Video Processing**: `librosa`, `soundfile`, `ffmpeg-python`, `python-magic`.
*   **Services SDK**: `supabase`, `cloudinary`.
