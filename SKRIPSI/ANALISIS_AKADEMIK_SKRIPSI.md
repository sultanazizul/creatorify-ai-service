# Analisis Akademik Skripsi

## RANCANG BANGUN ARSITEKTUR BACKEND BERBASIS SERVERLESS GPU UNTUK SKALABILITAS LAYANAN GENERATIF SUARA DAN VIDEO AVATAR

**Creatorify AI Service — Backend Analysis**

---

## 0. Ruang Lingkup Analisis

### 0.1 Batasan Analisis

Dokumen ini menyajikan analisis akademik mendalam terhadap **kontribusi individu pada sisi backend** dari project "Creatorify AI Service". Analisis berfokus pada:

- Arsitektur backend dan pola desain yang diimplementasikan
- API RESTful dan alur data
- Logika bisnis dan pipeline pemrosesan AI
- Integrasi sistem dengan layanan eksternal
- Orkestrasi tugas pada infrastruktur *serverless GPU*

### 0.2 Identifikasi Komponen Project

Berdasarkan eksplorasi struktur project, komponen yang teridentifikasi adalah:

| Komponen | Lokasi | Deskripsi |
|----------|--------|-----------|
| **API Layer** | `api/v1/routers/` | Endpoint FastAPI (Audio, Video, Avatar, Upload) |
| **Service Layer** | `services/` | Logika bisnis domain Audio dan Video |
| **Infrastructure Layer** | `services/infrastructure/` | Integrasi Supabase (PostgreSQL) dan Cloudinary |
| **Core Logic** | `core/` | Konfigurasi dan keamanan (API Key authentication) |
| **Models** | `models/` | Pydantic schemas untuk validasi request/response |
| **Vendor Libraries** | `vendor/` | Library eksternal (Chatterbox, InfiniteTalk) |
| **Main Application** | `app.py` (1673 baris) | Entry point Modal.com, FastAPI app, GPU Model class |
| **Microservice** | `chatterbox_app.py` | Microservice terpisah untuk Chatterbox TTS |

### 0.3 Disclaimer

> **Catatan Penting**: Analisis ini sepenuhnya berbasis pada *source code* dan dokumentasi yang tersedia di repository backend. Informasi yang tidak eksplisit dinyatakan dalam project tidak diasumsikan atau dispekulasikan. Bagian frontend dikembangkan oleh anggota tim lain dan hanya dibahas sejauh relevan untuk memahami alur sistem.

---

## 1. Deskripsi Faktual Aplikasi (Dari Sisi Backend)

### 1.1 Tujuan Aplikasi

Berdasarkan analisis kode sumber dan dokumentasi (`README.md`, `ARCHITECTURE.md`), **Creatorify AI Service** merupakan platform backend yang menyediakan **layanan generatif** dalam dua domain utama:

**A. Domain Generatif Suara (Audio Generative Services):**
1. **Text-to-Speech (TTS)** — Konversi teks menjadi audio dengan berbagai bahasa dan karakter suara (Kokoro-82M: in-process, Chatterbox: microservice)
2. **Voice Cloning** — Kloning karakteristik suara dari sampel audio referensi (Chatterbox microservice)
3. **Voice Conversion** — Transformasi suara dari satu identitas ke identitas lain (Chatterbox microservice)

**B. Domain Generatif Video (Video Generative Services):**
4. **AI Video Avatar Generation** — Pembuatan video avatar berbicara (*talking head*) dari gambar statis dan audio menggunakan model diffusion Wan2.1 + InfiniteTalk

### 1.2 Peran Backend dalam Sistem

Backend berperan sebagai:

1. **API Gateway** — Titik masuk tunggal untuk semua request dari klien (frontend/mobile)
2. **Orchestrator** — Mengatur eksekusi tugas AI yang intensif secara komputasi ke worker GPU
3. **State Manager** — Mengelola status dan *progress* tugas melalui database
4. **Media Pipeline Controller** — Mengontrol alur pemrosesan media dari input hingga penyimpanan akhir

### 1.3 Fungsi Backend yang Diimplementasikan

Berdasarkan analisis `app.py`, `api/v1/routers/`, dan `services/`, fungsi yang benar-benar diimplementasikan meliputi:

#### Domain Audio (`services/audio/`)

| Modul | File | Fungsi |
|-------|------|--------|
| **Kokoro TTS** | `tts/kokoro/service.py` | TTS multilingual 9 bahasa, model 82M parameter |
| **Voice Library** | `voice_library/voice_manager.py` | Manajemen sampel suara untuk kloning |
| **Chatterbox Integration** | `tts/chatterbox/` | Integrasi microservice TTS dengan voice cloning |

#### Domain Video (`services/video/`)

| Modul | File | Fungsi |
|-------|------|--------|
| **Talking Head** | `talking_head/service.py` | Placeholder, logika utama di `app.py` class `Model` |

#### Infrastructure (`services/infrastructure/`)

| Service | File | Baris Kode | Fungsi |
|---------|------|------------|--------|
| **SupabaseService** | `supabase.py` | 466 baris | CRUD untuk 4 tabel database |
| **CloudinaryService** | `cloudinary.py` | 103 baris | Upload video, audio, gambar |

---

## 2. Identifikasi Domain & Kategori Aplikasi

### 2.1 Domain Teknologi Backend

Berdasarkan arsitektur dan implementasi, sistem ini termasuk dalam kategori:

| Aspek | Klasifikasi | Justifikasi |
|-------|-------------|-------------|
| **Domain Utama** | AI-as-a-Service (AIaaS) | Menyediakan inferensi model AI melalui API |
| **Arsitektur** | Microservices + Serverless | Dua aplikasi terpisah (`app.py`, `chatterbox_app.py`) berjalan di Modal.com |
| **Pola Pemrosesan** | Asynchronous Pipeline | Background task dengan `.spawn()`, polling status |
| **Tipe API** | RESTful API | HTTP endpoints dengan JSON request/response |

### 2.2 Jenis Permasalahan yang Ditangani Backend

1. **Compute-Intensive AI Inference** — Menjalankan model diffusion 14B parameter (Wan2.1) membutuhkan GPU H100
2. **Long-Running Task Management** — Generasi video dapat memakan waktu 2-5 menit per request
3. **Multi-Modal Processing** — Menangani input gambar, audio, dan teks secara simultan
4. **Resource Optimization** — Cold-start mitigation dengan volume persisten untuk model weights (>50GB)

### 2.3 Posisi Sistem

| Kriteria | Status | Bukti dari Kode |
|----------|--------|-----------------|
| **B2B/B2C** | B2C (Service Layer untuk Consumer App) | API Key tunggal, `user_id` per record di database |
| **Internal/External** | External Service | Endpoint publik di Modal.com, Cloudinary URLs untuk distribusi |
| **Service Architecture** | Backend-as-a-Service (BaaS) dengan GPU capability | FastAPI + Modal serverless GPU |

---

## 3. Analisis Solusi Existing & Kompetitor (Level Sistem)

### 3.1 Identifikasi Solusi Sejenis

Berdasarkan fitur yang diimplementasikan di backend, solusi sejenis yang ada di pasar meliputi:

| Kategori | Solusi Existing | Karakteristik |
|----------|-----------------|---------------|
| **TTS API** | ElevenLabs, Google Cloud TTS, Amazon Polly | Cloud-based, pay-per-use |
| **Voice Cloning** | Resemble.AI, Descript Overdub | Proprietari, membutuhkan dataset besar |
| **Talking Head** | D-ID, HeyGen, Synthesia | Closed platform, berbasis langganan |

### 3.2 Perbandingan Arsitektur (Bukan UI)

| Aspek | Creatorify AI Backend | Solusi Existing Tipikal |
|-------|----------------------|-------------------------|
| **Deployment Model** | Serverless GPU (Modal.com) | Dedicated GPU clusters atau Cloud VMs |
| **Model Ownership** | Open-source models (Kokoro, Chatterbox, Wan2.1) | Proprietary models |
| **Scaling Strategy** | Auto-scaling per request | Manual scaling atau reserved capacity |
| **Cost Model** | Pay-per-second GPU usage | Monthly subscription atau per-minute |
| **Customization** | Full access ke parameters model | Limited exposed parameters |

### 3.3 Kelebihan Solusi Existing

1. **Produktisasi Matang** — UI yang polished, dokumentasi ekstensif, SLA terjamin
2. **Kualitas Output Konsisten** — Model fine-tuned dengan dataset besar
3. **Latensi Rendah** — Infrastruktur optimized, CDN global

### 3.4 Keterbatasan Solusi Existing

1. **Vendor Lock-in** — Ketergantungan penuh pada penyedia layanan
2. **Biaya Tinggi** — Model subscription mahal untuk high-volume usage
3. **Limited Customization** — Parameter model tidak dapat dimodifikasi
4. **Data Privacy** — Data pengguna diproses di server pihak ketiga

---

## 4. Identifikasi GAP (Masalah Penelitian Backend)

### 4.1 GAP Teknis

Berdasarkan analisis implementasi backend, GAP teknis yang teridentifikasi:

| No | GAP | Deskripsi | Bukti dari Kode |
|----|-----|-----------|-----------------|
| 1 | **Skalabilitas Orkestrasi** | Belum ada load balancing untuk multiple concurrent requests | Single Modal App instance di `app.py` |
| 2 | **Error Recovery** | Tidak ada retry mechanism untuk failed tasks | `update_pipeline()` hanya update status ke "error" tanpa retry |
| 3 | **Monitoring & Observability** | Logging sederhana dengan `print()`, tidak ada metrics collection | Tidak ada integrasi APM atau logging framework |
| 4 | **Rate Limiting** | Tidak ada pembatasan request per user | Endpoint langsung diproses tanpa throttling |
| 5 | **Caching** | Tidak ada caching layer untuk hasil inferensi | Setiap request memicu inferensi baru |

### 4.2 GAP Fungsional Backend

| No | GAP | Deskripsi | Status Saat Ini |
|----|-----|-----------|-----------------|
| 1 | **Batch Processing** | API hanya mendukung single-item request | Tidak ada batch endpoint di router |
| 2 | **Webhook Notification** | Polling-based status check | Tidak ada webhook callback implementation |
| 3 | **Queue Management** | Tidak ada priority queue | FIFO processing tanpa prioritization |
| 4 | **Versioning** | Tidak ada model version management | Model didownload dari HuggingFace tanpa pinning version |

### 4.3 GAP Penelitian Terkait Backend System

1. **Optimasi Cold-Start Latency** — Bagaimana meminimalkan waktu inisialisasi model pada serverless GPU?
2. **Pipeline Progress Reporting** — Bagaimana menyediakan progress tracking yang akurat untuk multi-stage pipeline?
3. **Resource Allocation Strategy** — Bagaimana memilih GPU tier yang optimal berdasarkan karakteristik task?
4. **Cross-Service Communication** — Bagaimana mengoptimalkan latency antara main app dan microservice?

> **Catatan**: GAP penelitian ini berdasarkan observasi arsitektur dan tidak dapat diklaim sebagai gap literatur tanpa tinjauan pustaka formal.

---

## 5. Fenomena Teknologi & Kebutuhan Sistem

### 5.1 Fenomena Teknologi Relevan

| Fenomena | Relevansi dengan Backend | Implementasi di Project |
|----------|-------------------------|------------------------|
| **Serverless GPU Computing** | Paradigma baru deployment AI tanpa manage infrastructure | Modal.com dengan `@app.cls(gpu="H100")` |
| **Generative AI Democratization** | Open-source models berkualitas production-ready | Kokoro-82M, Chatterbox, Wan2.1 semua open-source |
| **Microservices AI** | Memecah monolith AI menjadi specialized services | `app.py` + `chatterbox_app.py` sebagai service terpisah |
| **Pay-per-Use Cloud** | Cost efficiency untuk workload tidak konsisten | Modal billing per-second GPU usage |

### 5.2 Kebutuhan Sistem Modern

Berdasarkan arsitektur yang diimplementasikan, kebutuhan yang dijawab:

1. **Elastic Scaling** — Kemampuan scale-to-zero saat tidak ada request
2. **Cost Optimization** — Penggunaan GPU hanya saat dibutuhkan
3. **Rapid Deployment** — Container-based deployment dalam menit
4. **Integration Simplicity** — RESTful API standar industri

### 5.3 Keterbatasan Analisis

> Fenomena seperti "pertumbuhan pasar AI-generated content" atau "adopsi enterprise terhadap AI" tidak dibahas karena memerlukan data eksternal yang tidak tersedia dalam project.

---

## 6. Pendahuluan Riset (Existing Study Overview — Backend Focus)

### 6.1 Arah Penelitian Terkait Backend System Sejenis

Berdasarkan karakteristik sistem, arah penelitian yang relevan meliputi:

1. **Serverless Computing Performance** — Studi tentang cold-start, warm-start, dan optimasi latensi
2. **AI Pipeline Orchestration** — Manajemen workflow untuk multi-model inference
3. **REST API Design for AI Services** — Best practices desain endpoint untuk long-running tasks
4. **Database Design for Status Tracking** — Pola data untuk monitoring pipeline state

### 6.2 Pendekatan yang Sering Digunakan

| Aspek | Pendekatan Umum | Relevansi dengan Project |
|-------|-----------------|-------------------------|
| **Async Processing** | Queue-based (RabbitMQ, Celery) | Project menggunakan Modal `.spawn()` |
| **Status Management** | State machine pattern | Implementasi di `metadata.pipeline.stages` |
| **Progress Reporting** | Percentage-based atau stage-based | Kombinasi keduanya di `progress` + `current_stage` |
| **Error Handling** | Circuit breaker, retry with backoff | Tidak diimplementasikan di project saat ini |

### 6.3 Aspek yang Sering Dievaluasi

- **API Response Time** — Latensi endpoint synchronous
- **End-to-End Latency** — Waktu total dari request hingga hasil tersedia
- **Throughput** — Request per second yang dapat ditangani
- **Error Rate** — Persentase request yang gagal
- **Resource Utilization** — GPU utilization selama inferensi

> **Catatan**: Tidak ada literatur spesifik yang dikutip karena tidak tersedia dalam project. Pernyataan di atas berdasarkan pengetahuan umum tentang arsitektur backend.

---

## 7. Formulasi Masalah Penelitian (Individu — Backend)

Berdasarkan analisis implementasi backend yang tersedia, berikut rumusan masalah yang dapat diuji:

### Rumusan Masalah

1. **Bagaimana arsitektur *serverless GPU* pada Modal.com dapat dioptimalkan untuk meminimalkan *cold-start latency* pada inferensi model AI berskala besar (14B parameter)?**

2. **Bagaimana desain API RESTful dengan pola *asynchronous polling* dapat menyediakan informasi *progress* yang akurat dan *real-time* untuk pipeline pemrosesan video avatar?**

3. **Bagaimana implementasi pola *Domain-Driven Design* (DDD) pada backend AI service dapat meningkatkan *maintainability* dan *extensibility* sistem?**

4. **Bagaimana strategi pemisahan *microservice* (main app vs. Chatterbox TTS) memengaruhi latensi *end-to-end* dan *cost efficiency* pada platform *serverless*?**

5. **Bagaimana implementasi *cursor-based pagination* dibandingkan dengan *offset-based pagination* dalam konteks performa query dan skalabilitas pada database Supabase (PostgreSQL)?**

### Justifikasi

- **Rumusan 1-2**: Dapat diuji dengan pengukuran performa langsung pada sistem yang sudah diimplementasikan
- **Rumusan 3**: Dapat dianalisis melalui *code review* dan metrik *maintainability*
- **Rumusan 4-5**: Dapat diuji dengan eksperimen komparatif menggunakan variasi konfigurasi

---

## 8. Tujuan Penelitian

### 8.1 Tujuan Umum

Merancang dan membangun arsitektur backend berbasis *serverless GPU* yang skalabel untuk layanan generatif suara (Text-to-Speech, Voice Cloning, Voice Conversion) dan video avatar, serta mengevaluasi aspek arsitektur, performa, dan skalabilitas sistem.

### 8.2 Tujuan Khusus

1. **Menganalisis arsitektur backend** — Mendeskripsikan dan mengevaluasi penerapan pola *Domain-Driven Design*, *layered architecture*, dan *microservices* pada backend Creatorify AI Service.

2. **Mengukur performa API** — Melakukan pengujian performa endpoint API meliputi *response time*, *throughput*, dan *latency* pada berbagai kondisi beban.

3. **Mengevaluasi pipeline AI** — Menganalisis efektivitas orkestrasi pipeline video generation dan TTS dalam hal *progress tracking*, *error handling*, dan *resource utilization*.

4. **Mengidentifikasi optimasi** — Memberikan rekomendasi teknis untuk peningkatan performa, skalabilitas, dan *reliability* sistem berdasarkan hasil analisis.

5. **Mendokumentasikan implementasi** — Menyusun dokumentasi teknis komprehensif yang dapat dijadikan referensi untuk pengembangan sistem sejenis.

---

## 9. Strategi & Metode Penelitian

### 9.1 Jenis Penelitian

**Penelitian Deskriptif-Eksploratif dengan Komponen Eksperimental**

- **Deskriptif**: Mendeskripsikan arsitektur dan implementasi backend yang sudah ada
- **Eksploratif**: Mengeksplorasi karakteristik performa sistem pada berbagai kondisi
- **Eksperimental**: Melakukan pengujian terukur dengan variabel terkontrol

### 9.2 Metode Pengumpulan Data dari Backend

| Sumber Data | Metode | Output |
|-------------|--------|--------|
| **Source Code** | Static Code Analysis | Metrik kompleksitas, dependency mapping |
| **API Endpoints** | API Testing | Response time, status codes, payload validation |
| **Database** | Query Analysis | Execution time, query plan |
| **Logs** | Log Analysis | Error frequency, processing duration |
| **Infrastructure** | Modal Dashboard | GPU utilization, cold-start frequency |

### 9.3 Metode Pengujian yang Memungkinkan

#### A. Functional Testing
- **Endpoint Testing**: Validasi semua endpoint dengan berbagai input
- **Integration Testing**: Verifikasi alur end-to-end dari request hingga response

#### B. Performance Testing
| Jenis | Tool yang Dapat Digunakan | Metrik |
|-------|---------------------------|--------|
| **Load Testing** | k6, Apache JMeter, Locust | RPS, latency percentiles |
| **Stress Testing** | Artillery, Gatling | Breaking point, recovery time |
| **API Benchmarking** | wrk, hey | Throughput, connection handling |

#### C. Code Quality Analysis
- **Static Analysis**: pylint, ruff untuk Python code quality
- **Complexity Metrics**: radon untuk cyclomatic complexity
- **Dependency Analysis**: pipdeptree untuk dependency graph

### 9.4 Output yang Dapat Dianalisis Secara Objektif

1. **Metrik Kuantitatif**:
   - Response time (ms) per endpoint
   - Throughput (requests/second)
   - Error rate (%)
   - Cold-start duration (seconds)
   - GPU utilization (%)
   - Generation time per video/audio (seconds)

2. **Metrik Kualitatif**:
   - Code maintainability index
   - API design compliance (RESTful standards)
   - Documentation completeness

### 9.5 Keterbatasan Metode

> **Metode yang tidak memungkinkan**:
> - **User Survey**: Termasuk ruang lingkup frontend/UX
> - **A/B Testing Produksi**: Memerlukan traffic pengguna real
> - **Comparative Study dengan Kompetitor**: Akses ke sistem kompetitor tidak tersedia

---

## 10. Evaluasi Kelayakan Skripsi Individu

### 10.1 Kelayakan Kontribusi Backend sebagai Skripsi

| Kriteria | Penilaian | Justifikasi |
|----------|-----------|-------------|
| **Kompleksitas Teknis** | ✅ Tinggi | Integrasi AI models, serverless GPU, microservices |
| **Orisinalitas** | ✅ Cukup | Implementasi mandiri dengan open-source models |
| **Keterukuran** | ✅ Baik | Metrik performa dapat diukur secara objektif |
| **Dokumentasi** | ✅ Tersedia | 20+ file dokumentasi, README komprehensif |
| **Ruang Lingkup** | ✅ Fokus | Kontribusi backend terpisah jelas dari frontend |

### 10.2 Kekuatan Utama Penelitian

1. **Implementasi Nyata** — Sistem sudah berjalan di production environment (Modal.com)
2. **Arsitektur Modern** — Menerapkan paradigma serverless GPU yang masih berkembang
3. **Multi-Domain** — Mencakup Audio dan Video processing dalam satu sistem
4. **Open Source Stack** — Dapat direplikasi dan diverifikasi
5. **Dokumentasi Lengkap** — 20+ file dokumentasi teknis tersedia

### 10.3 Keterbatasan Kontribusi

1. **Dependensi pada Layanan Eksternal**
   - Modal.com, Supabase, Cloudinary
   - Pengujian mandiri memerlukan akun berbayar

2. **Keterbatasan Pengujian Komprehensif**
   - Load testing skala besar memerlukan biaya GPU
   - Tidak ada automated test suite yang terdeteksi

3. **Ruang Lingkup Project Kelompok**
   - Frontend dikembangkan terpisah
   - Beberapa keputusan arsitektur mungkin dipengaruhi kebutuhan frontend

4. **Keterbatasan Literatur dalam Dokumen**
   - Tidak ada citation ke academic papers
   - Klaim penelitian memerlukan penambahan literature review

### 10.4 Saran Penajaman Fokus

Untuk memenuhi standar akademik skripsi Informatika/Sistem Informasi:

1. **Fokus pada Satu Aspek Utama**
   > Disarankan memilih salah satu fokus:
   > - **Opsi A**: Analisis Performa Pipeline Video Generation
   > - **Opsi B**: Evaluasi Arsitektur Serverless GPU untuk AI Service
   > - **Opsi C**: Desain API RESTful untuk Long-Running AI Tasks

2. **Tambahkan Literature Review**
   > Lakukan tinjauan pustaka pada topik:
   > - Serverless computing performance optimization
   > - AI pipeline orchestration patterns
   > - RESTful API design for machine learning services

3. **Implementasikan Pengujian Formal**
   > Rancang test suite dengan:
   > - Unit tests untuk service layer
   > - Integration tests untuk API endpoints
   > - Performance benchmarks dengan workload terdefinisi

4. **Dokumentasikan Keputusan Desain**
   > Buat Architecture Decision Records (ADR) untuk:
   > - Pemilihan Modal.com vs alternatif lain
   > - Strategi pagination (cursor vs offset)
   > - Pembagian microservice

5. **Quantitative Analysis**
   > Lakukan pengukuran:
   > - Baseline performance metrics
   > - Comparative analysis dengan/tanpa optimasi
   > - Statistical significance testing

---

## Lampiran: Ringkasan Teknis Backend

### A. Tech Stack

| Layer | Teknologi | Versi/Keterangan |
|-------|-----------|------------------|
| **Framework** | FastAPI | RESTful API framework |
| **Deployment** | Modal.com | Serverless GPU platform |
| **Database** | Supabase | PostgreSQL managed service |
| **Storage** | Cloudinary | Media CDN dan storage |
| **AI Runtime** | PyTorch | 2.4.1 + CUDA 12.1 |

### B. Model AI yang Digunakan

| Model | Parameter | Fungsi | GPU Requirement |
|-------|-----------|--------|-----------------|
| **Kokoro-82M** | 82 juta | TTS multilingual | CPU/GPU ringan |
| **Chatterbox** | N/A | Voice cloning + TTS | A10G |
| **Wan2.1-I2V-14B** | 14 miliar | Image-to-Video diffusion | H100 |
| **InfiniteTalk** | N/A | Lip-sync motion module | H100 (bersama Wan2.1) |

### C. Database Schema (Inferred)

```
projects
├── id (UUID)
├── user_id (STRING)
├── image_url, audio_url, audio_url_2
├── status (queued | processing | finished | error)
├── progress (0-100)
├── current_stage (SETUP | INFERENCE | POST_PROCESS | UPLOADING)
├── metadata (JSON: pipeline stages)
└── video_url (output)

tts_projects
├── id, user_id, text, voice, speed, lang_code
├── status, progress, current_stage
└── audio_url (output)

chatterbox_projects
├── id, user_id, project_type (tts | multilingual | voice_conversion)
├── text, language_id, voice_sample_id
├── exaggeration, temperature, cfg_weight, ...
└── audio_url (output)

avatars
├── avatar_id, user_id, name, image_url
└── is_public (BOOLEAN)
```

### D. API Endpoint Summary

| Domain | Endpoint | Method | Fungsi |
|--------|----------|--------|--------|
| **Video** | `/api/v1/projects/` | POST | Create video generation task |
| **Video** | `/api/v1/projects/{id}` | GET | Get project status |
| **TTS Kokoro** | `/api/v1/tts/generate` | POST | Generate TTS async |
| **TTS Kokoro** | `/api/v1/tts/languages` | GET | List bahasa |
| **TTS Kokoro** | `/api/v1/tts/voices` | GET | List voices |
| **Chatterbox** | `/api/v1/audio/chatterbox/tts/generate` | POST | Voice cloning TTS |
| **Chatterbox** | `/api/v1/audio/chatterbox/multilingual/generate` | POST | Multi-language TTS |
| **Voice Library** | `/api/v1/audio/voice-library/` | GET/POST | CRUD voice samples |
| **Avatar** | `/api/v1/avatars/` | GET/POST/DELETE | CRUD avatars |
| **Upload** | `/api/v1/upload/` | POST | Generic file upload |

---

*Dokumen ini disusun berdasarkan analisis objektif terhadap source code dan dokumentasi project Creatorify AI Service. Seluruh pernyataan didukung oleh bukti dari implementasi yang tersedia.*

**Tanggal Analisis**: Januari 2026  
**Versi Dokumen**: 1.1 (Updated: Diselaraskan dengan judul skripsi final)
