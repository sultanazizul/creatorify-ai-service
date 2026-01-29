# **BAB III**

METODOLOGI PENELITIAN

## **3.1 Waktu dan Tempat Penelitian**

**Penjelasan:** Sub-bab ini mendeskripsikan konteks waktu dan lokasi pelaksanaan penelitian sesuai dengan ketentuan institusi.

**Isi Outline:**

- **Lokasi Penelitian:** Penelitian disusun di Kampus Bukit Universitas Udayana, Fakultas Teknik, Program Studi Teknologi Informasi, Jimbaran.
- **Waktu Penelitian:** Penelitian berlangsung dari September 2024 hingga Juni 2025.
- **Aktivitas Utama:** Studi literatur, analisis sistem, perancangan arsitektur backend, implementasi kode (coding), deployment ke Modal.com, dan pengujian sistem.

## **3.2 Jenis dan Pendekatan Penelitian**

**Penjelasan:** Menjelaskan metodologi riset yang digunakan untuk memecahkan masalah backend serverless. Mengacu pada Analisis Akademik poin 9.1.

**Isi Outline:**

- **Jenis Penelitian:** Penelitian Terapan (*Applied Research*).
- **Pendekatan:** Deskriptif-Eksploratif dengan komponen Eksperimental.
    - *Deskriptif:* Menjabarkan arsitektur serverless GPU yang dibangun.
    - *Eksploratif:* Mengeksplorasi kemampuan teknis model AI (InfiniteTalk, Chatterbox, Kokoro) untuk menentukan solusi terbaik.
    - *Eksperimental:* Menguji latensi dan throughput pada endpoint API.
- **Alur Pikir:** Identifikasi Masalah -> Analisis & Pemilihan Solusi -> Eksplorasi Teknis -> Perancangan -> Implementasi -> Validasi.

## **3.3 Alur Penelitian**

### **3.3.1 Tahapan Penelitian**

**Penjelasan:** Langkah-langkah sistematis yang dilakukan peneliti dari awal hingga akhir.

**Isi Outline:**

- **Tahap 1: Identifikasi Masalah** (Analisis gap antara sistem konvensional yang mahal/lambat vs kebutuhan industri).
- **Tahap 2: Studi Literatur & Penentuan Solusi** (Mengkaji komparasi arsitektur Serverless vs Monolitik, serta memilih model AI terbaik). *Output:* Dipilihnya arsitektur Modal.com dan model InfiniteTalk/Chatterbox sebagai solusi.
- **Tahap 3: Eksplorasi Teknis (Environment Setup)** (Mendalami dokumentasi teknis & menyiapkan lingkungan development untuk model yang dipilih).
- **Tahap 4: Perancangan Sistem Backend** (Arsitektur Microservices, Database Schema, & RESTful API Contract).
- **Tahap 5: Implementasi Backend** (Coding FastAPI, Konfigurasi Modal, Integrasi Supabase, & Integrasi Cloudinary).
- **Tahap 6: Pengujian Sistem & Evaluasi** (Latency Test & Functional Test).
- **Tahap 7: Selesai & Penyusunan Laporan**.

### **3.3.2 Diagram Alur Penelitian**

**Penjelasan:** Visualisasi flowchart tahapan di atas.

**Isi Outline:**

- **Diagram:** Mulai -> Identifikasi Masalah -> Studi Literatur & Penentuan Solusi -> Eksplorasi Teknis (Environment) -> Perancangan Sistem Backend -> Implementasi Backend -> Pengujian Sistem & Evaluasi -> Selesai.
- **Keterangan:** Alur logis dari analisis masalah, pemilihan solusi teknologi, hingga eksekusi teknis.

## **3.4 Alat dan Bahan Penelitian**

### **3.4.1 Perangkat Keras**

**Penjelasan:** Spesifikasi infrastruktur pengembangan dan deployment.

**Isi Outline:**

- **Laptop Pengembang (Local Environment):**
    - Model: MacBook Pro (13-inch, 2020, Four Thunderbolt 3 ports)
    - Processor: 2.3 GHz Quad-Core Intel Core i7
    - RAM: 32 GB 3733 MHz LPDDR4X
    - Graphics: Intel Iris Plus Graphics 1536 MB
    - Storage: 1 TB SSD
    - OS: macOS Tahoe 26.1
- **Cloud Infrastructure (Deployment & Inference):**
    - **GPU Tier 1:** NVIDIA H100 (80GB VRAM).
        - *Justifikasi:* Dipilih karena model **Wan2.1-I2V-14B** membutuhkan VRAM > 40GB untuk memuat bobot model (`fp16`) dan buffer inferensi. GPU kelas consumer (e.g., RTX 4090 24GB) tidak mencukupi untuk parameter 14B.
    - **GPU Tier 2:** NVIDIA A10G (24GB VRAM).
        - *Justifikasi:* Dipilih untuk model **Kokoro-82M** dan **Chatterbox** yang lebih ringan. VRAM 24GB cukup untuk menampung kedua model sekaligus dalam satu container (efisiensi biaya dibanding H100).
    - **Storage:** Modal Persistent Volume (High-performance network storage) untuk caching model agar tidak redownload.

### **3.4.2 Perangkat Lunak**

**Penjelasan:** Stack teknologi yang digunakan dalam implementasi backend.

**Isi Outline:**

- **Bahasa Pemrograman:** Python 3.10+ (Logic utama).
- **Framework:** FastAPI (REST API), Modal SDK (Serverless Orchestration).
- **Database:** PostgreSQL via Supabase (Relational & JSONB).
- **Storage & CDN:** Cloudinary (Media assets management).
- **AI Models:**
    - **Video Generation:** InfiniteTalk (Talking Head Module) berbasis **Wan2.1-I2V-14B** (Backbone).
    - **Audio Generation:** Kokoro-82M (TTS) & Chatterbox (Voice Cloning).
- **Tools Pendukung:** VS Code (IDE), Git (Version Control), Postman (API Testing).

## **3.5 Analisis Sistem**

### **3.5.1 Gambaran Umum Sistem**

**Penjelasan:** Deskripsi high-level arsitektur *Decoupled Services* dimana backend menyediakan "building blocks" independen.

**Isi Outline:**

- **Konsep Sistem:** Backend berfungsi sebagai penyedia layanan terpisah (*Service Provider*):
    1. *Service Audio:* Input Text/Voice -> Output Audio URL.
    2. *Service Video:* Input Image + Audio URL -> Output Video URL.
- **Alur Integrasi:** Logika penggabungan (chaining) dilakukan di sisi Frontend. Backend **tidak** secara otomatis memicu video generation setelah audio selesai.
- **Aktor:** User (via Frontend) merequest layanan satu per satu sesuai kebutuhan.

### **3.5.2 Analisis Masalah Sistem Konvensional**

**Penjelasan:** Mengidentifikasi akar masalah mengapa arsitektur biasa tidak cukup. Wajib menggunakan Fishbone.

**Isi Outline:**

- **Masalah Utama:** Latensi tinggi dan biaya infrastruktur mahal pada layanan Generative AI.
- **Diagram Fishbone:**
    - *Man:* Keterbatasan keahlian manajemen server fisik.
    - *Machine:* GPU idle time memboroskan biaya, Cold-start latency.
    - *Method:* Arsitektur Monolitik menyebabkan blocking proses.
    - *Material:* Model AI berukuran besar (>50GB) sulit didistribusikan.
- **Solusi:** Migrasi ke arsitektur Serverless GPU dengan manajemen state asinkron.

### **3.5.3 Analisis Kebutuhan Sistem**

**Penjelasan:** Daftar spesifikasi teknis yang harus dipenuhi backend.

**Isi Outline:**

- **Kebutuhan Fungsional (Functional Requirements):**
    - Backend mampu menerima request generasi video avatar (Image+Audio).
    - Backend mampu memproses TTS multilingual (Kokoro) serta Voice Cloning dan Voice Conversion (Chatterbox).
    - Backend mampu mengelola antrian tugas (*task queue*) secara asinkron.
    - Backend mampu menyimpan status progress ke database secara real-time.
    - Backend mampu mengunggah hasil akhir ke Cloudinary otomatis.
- **Kebutuhan Non-Fungsional (Non-Functional Requirements):**
    - *Scalability:* Sistem dapat menangani lonjakan request tanpa down (Auto-scaling Modal).
    - *Performance:* Waktu cold-start seminimal mungkin (<30 detik dengan Volume).
    - *Reliability:* Mekanisme error handling jika GPU worker gagal.
    - *Interoperability:* Output API berupa JSON standar.

## **3.6 Perancangan Arsitektur Sistem (High-Level Design)**

### **3.6.1 Arsitektur Topologi Cloud (Deployment Diagram)**

**Penjelasan:** Visualisasi infrastruktur cloud terdistribusi.

**Isi Outline:**

- **Diagram Deployment:** Menunjukkan hubungan antara Client -> API Gateway (FastAPI) -> Modal.com Cloud (Worker H100/A10G) -> External Services (Supabase, Cloudinary).
- **Penjelasan:** Alur komunikasi data dan pemisahan *Control Plane* (API) dengan *Data Plane* (GPU Workers).

### **3.6.2 Mekanisme Serverless & GPU Orchestration**

**Penjelasan:** Detail teknis bagaimana Modal mengatur container.

**Isi Outline:**

- **Mekanisme `.spawn()`:** Pemisahan proses HTTP request dengan proses GPU background.
- **Lifecycle Container:** Start -> Load Model (from Volume) -> Inference -> Shutdown/Scale-to-zero.
- **Manajemen Volume:** Penggunaan persistent volume untuk menyimpan bobot model Wan2.1 agar tidak didownload ulang setiap request.

## **3.7 Perancangan Perangkat Lunak (Detailed Design)**

### **3.7.1 Diagram Konteks**

**Penjelasan:** Diagram level 0 DFD (Data Flow Diagram) atau biasa disebut *Diagram Konteks*. Digunakan khusus untuk memetakan batasan sistem (*system boundary*) dan interaksi dengan entitas eksternal, tanpa mendetailkan proses internal yang akan dijelaskan menggunakan UML.

**Isi Outline:**

- **Entitas Luar:**
    - **Aplikasi Frontend (Client):** Aktor utama yang mengirimkan request API. Bertugas mengambil `user_id` dari Auth Service dan meneruskannya ke Backend ini sebagai parameter input.
    - **Cloudinary:** Layanan penyimpanan media eksternal.
    - **Supabase:** Layanan basis data eksternal.
- **Alur Data:** Input pengguna masuk ke Sistem Backend, Sistem Backend mengirim aset ke Cloudinary, dll.

### **3.7.2 Unified Modeling Language (UML)**

**Penjelasan:** Serangkaian diagram UML untuk memodelkan struktur dan perilaku kode backend yang modular.

**Isi Outline:**

- **Use Case Diagram:**
    - Use Case terpisah: "Generate TTS Audio", "Clone Voice Reference", "Generate Video Avatar".
    - Tidak ada garis dependensi langsung antar use case di backend.
- **Activity Diagram:**
    - *Activity 1 (Audio Flow):* Receive Text -> Queue TTS -> Generate Audio -> Return URL.
    - *Activity 2 (Video Flow):* Receive Image & Audio URL -> Queue Video -> Sync Lip -> Render -> Return URL.
- **Sequence Diagram:**
    - *Skenario A (Generate Suara):* Frontend -> API TTS -> Worker -> DB (Updates Status) -> Frontend (Get Audio URL).
    - *Skenario B (Generate Video):* Frontend (Sends Audio URL from A) -> API Video -> Worker -> DB -> Frontend.
    - *Catatan:* Menunjukkan Frontend sebagai inisiator masing-masing request secara terpisah.
- **Class Diagram:**
    - Class `App` sebagai entry point.
    - Pemisahan jelas antara class `KokoroService`/`ChatterboxService` (Audio) dan `TalkingHeadModel` (Video).

## **3.8 Perancangan Basis Data**

### **3.8.1 Entity Relationship Diagram (ERD)**

**Penjelasan:** Relasi konseptual antar data.

**Isi Outline:**

- **Entitas:** `User`, **Project** (Video), **TTSProject**, `ChatterboxProject`, **Avatar**, **VoiceSample**.
- **Relasi:** User *one-to-many* Projects, User *one-to-many* Avatars, User *one-to-many* VoiceSamples.

### **3.8.2 Physical Data Model (PDM)**

**Penjelasan:** Implementasi tabel di PostgreSQL (Supabase).

**Isi Outline:**

- **Tabel projects:** **id** (UUID), **status**, **progress**, `metadata` (JSONB), `video_url`.
- **Tabel `tts_projects`:** **id**, `text`, **voice**, `audio_url`.
- **Tabel chatterbox_projects:** **id**, `voice_sample_id`, `source_audio_url`.
- **Tabel avatars:** `avatar_id`, `image_url`, `is_public`.
- **Tabel voice_samples:** **id**, `name`, `audio_url`, `duration_seconds`, `is_public`, `created_at`.

### **3.8.3 Kamus Data**

**Penjelasan:** Detail tipe data dan constraints per kolom.

**Isi Outline:**

- Deskripsi kolom penting seperti `metadata` (berisi JSON pipeline stages) dan **status** (enum: queued, processing, finished, failed).

### **3.8.4 Manajemen Penyimpanan Data (Cloudinary Storage Design)**

**Penjelasan:** Desain struktur direktori penyimpanan awan (*Cloud Storage*) untuk mengelola aset media yang dihasilkan secara terorganisir.

**Isi Outline:**

- **Root Directory:** `Creatorify/`
- **Struktur Hirarki:**
    - `AI Video Output/` -> `Talking Video/` -> `Infinitalk/` ({Tipe: Single/Multi Person}).
    - `AI Audio Output/` -> `Kokoro82/` (TTS Standard) & **Chatterbox/** (Cloning/Multilingual).
    - `Avatar Assets/` -> `{Public/Users}`.
    - `Voice Sample/` -> `{Public/Users}`.
- **Justifikasi:** Pemisahan folder berdasarkan *Service Type* dan *User Access Level* untuk mempermudah manajemen aset dan kontrol akses.

### **3.9 Perancangan Antarmuka API (API Contract)**

Bagian ini mendefinisikan spesifikasi teknis API yang disediakan oleh *backend*. Penjelasan mencakup metode HTTP, *endpoint*, parameter input, dan struktur respons yang valid. Informasi ini disusun berdasarkan analisis dokumentasi teknis `Creatorify API.postman_collection.json`.

**Poin-poin Kunci:**

- **Autentikasi & Otorisasi:** Menggunakan header `X-API-Key` untuk keamanan servis. Parameter `user_id` dikirim oleh **Frontend** (sebagai *authorized client*) pada setiap body request untuk mengasosiasikan data dengan pengguna.
- **Format:** Request dan Response menggunakan JSON.

**Daftar Endpoint Utama:**

1. **Manajemen Media (Cloudinary):**
    - `POST /api/v1/cloudinary/upload-file`: Mengunggah aset (gambar/audio) untuk source project.
    - `DELETE /api/v1/cloudinary/delete-file`: Menghapus aset dari penyimpanan.
2. **Manajemen Avatar (Talking Head):**
    - `POST /api/v1/avatars/`: Membuat data avatar baru.
    - `GET /api/v1/avatars/`: Mengambil daftar avatar (mendukung filter `user_id`).
    - `DELETE /api/v1/avatars/{avatar_id}`: Menghapus avatar.
3. **Layanan Generasi Video (InfiniteTalk/Wan2.1):**
    - `POST /api/v1/projects/`: Endpoint utama untuk generasi video. Menerima parameter pipeline seperti `avatar_id` dan `audio_url`.
    - `GET /api/v1/projects/{project_id}`: Polling status pengerjaan (Progress tracking).
    - `GET /api/v1/projects/`: Mengambil riwayat proyek (Filter by `user_id` & `type`).
4. **Layanan Generasi Audio (Kokoro & Chatterbox):**
    - `POST /api/v1/tts/generate`: Generasi TTS standar (Kokoro-82M).
    - `POST /api/v1/audio/chatterbox/multilingual/generate`: Generasi TTS Multilingual kualitas tinggi.
    - `POST /api/v1/audio/voice-conversion/convert-upload`: Voice Conversion (Input Source Audio + Target Voice).
    - `GET /api/v1/tts/{tts_id}`: Polling status TTS standar.
    - `GET /api/v1/audio/chatterbox/projects/{project_id}`: Polling status proyek audio chatterbox.

### **3.9.2 Struktur Request & Response (JSON Schema)**

**Penjelasan:** Format data JSON yang dipertukarkan.

**Isi Outline:**

- **Request Body (Video):** Menyertakan metadata pipeline (stages) untuk pelacakan.
- **Response (Status):** Menyertakan **progress** (persentase) dan **status** (`queued`, `processing`, `finished`, `failed`).
- **Response (Error):** Format standar dengan kode error dan pesan deskriptif.

## **3.10 Flowchart Algoritma Utama**

**Penjelasan:** Logika detail (pseudocode/flowchart) dari dua pipeline utama yang independen.

**Isi Outline:**

- **Flowchart 1: Pipeline Generasi Audio (TTS/Voice Cloning)**
    - Input Text & Voice ID -> Load Model (Kokoro/Chatterbox) -> Inference -> Upload Audio -> Update DB Status.
- **Flowchart 2: Pipeline Generasi Video (Talking Head)**
    - Input Image & Audio URL -> Download Audio resource -> Preprocess -> Inference (Video Diffusion) -> Upload Video -> Update DB Status.
- **Keterangan:** Menegaskan bahwa Output Flowchart 1 menjadi salah satu Input (manual/by system frontend) untuk Flowchart 2.

## **3.11 Metode Implementasi**

**Penjelasan:** Bagaimana desain diterjemahkan menjadi kode nyata.

**Isi Outline:**

- **Lingkungan Pengembangan:** Setup Python Virtual Environment, Modal CLI authentication.
- **Struktur Kode:** Penerapan pola Router-Service-Repository pada folder **api/**, `services/`, **models/**.
- **Manajemen Dependensi:** Penggunaan **requirements.txt** dan image container definition.
- **Deployment:** Command `modal deploy app.py` untuk push ke cloud.

## **3.12 Metode Pengujian Sistem**

**Penjelasan:** Rencana validasi untuk memastikan backend berjalan sesuai spesifikasi.

**Isi Outline:**

- **Black Box Testing:** Pengujian fungsional input-output menggunakan Postman/cURL untuk memverifikasi setiap endpoint.
    - Skenario Positif (Data valid).
    - Skenario Negatif (Invalid file type, missing params).
- **Performance Testing:**
    - *Latency Testing:* Mengukur waktu respon API gateway.
    - *Processing Time:* Mengukur durasi generasi video (e.g., Target < 5 menit).
- **API Testing:** Validasi kode status HTTP (200, 201, 400, 422, 500) dan struktur JSON.