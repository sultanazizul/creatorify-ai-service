# BAB IV HASIL DAN PEMBAHASAN

## 4.1 Lingkungan Implementasi dan Pengujian
Subbab ini mendeskripsikan spesifikasi lingkungan teknis aktual yang digunakan selama proses pengembangan dan pengujian sistem. Informasi ini penting untuk memastikan hasil pengujian dapat direproduksi (*reproducible*).

### 4.1.1 Perangkat Keras
Perangkat keras yang digunakan dalam penelitian ini terbagi menjadi dua kategori utama. Untuk pengembangan kode dan pengujian lokal, digunakan laptop **MacBook Pro (13-inch, 2020)** dengan prosesor **2.3 GHz Quad-Core Intel Core i7** dan memori (RAM) sebesar **32 GB**. Sedangkan untuk infrastruktur produksi dan inferensi model AI, digunakan **GPU Worker** pada platform Modal.com dengan spesifikasi **NVIDIA H100 (80GB VRAM)** untuk model video dan **NVIDIA A10G (24GB VRAM)** untuk model audio.

### 4.1.2 Perangkat Lunak
Perangkat lunak yang digunakan mencakup sistem operasi **macOS** sebagai lingkungan pengembangan lokal dan **Linux** (containerized) pada lingkungan *serverless*. Implementasi *backend* dibangun menggunakan bahasa pemrograman **Python 3.10** dengan kerangka kerja **FastAPI** dan library **Modal SDK**. Manajemen basis data dan penyimpanan aset media masing-masing menggunakan layanan **Supabase (PostgreSQL)** dan **Cloudinary**. Seluruh kode program ditulis menggunakan **Visual Studio Code (VS Code)**, dan verifikasi fungsionalitas API dilakukan menggunakan aplikasi **Postman**.

## 4.2 Hasil Implementasi Sistem Backend
Bagian ini memaparkan realisasi dari rancangan arsitektur yang telah didefinisikan pada Bab III. Fokus utama adalah pembuktian bahwa desain sistem telah berhasil diterjemahkan menjadi artefak perangkat lunak yang berfungsi.

### 4.2.1 Implementasi Arsitektur Serverless (Modal.com)
- Deskripsi struktur kode aktual: Pemisahan fungsi-fungsi *entrypoint* (`@app.function`) dan fungsi *web endpoint* (`@app.web_endpoint`).
- Bukti implementasi *Dependency Injection* global untuk model AI (mekanisme `image.imports()`).

### 4.2.2 Implementasi API Gateway (FastAPI)
- Realisasi *routing* modul (Assets, Project, Audio) menggunakan `APIRouter`.
- Implementasi mekanisme asinkron (`async def`) untuk menangani konkurensi permintaan.

### 4.2.3 Implementasi Manajemen Data (Supabase & Cloudinary)
- **Skema Database**: Tampilan struktur tabel aktual di Supabase (screenshot/deskripsi tabel `projects`, `users`, `assets`).
- **Penyimpanan Media**: Struktur folder yang terbentuk di Cloudinary (`Creatorify/Video`, `Creatorify/Audio`) sebagai bukti manajemen aset.

## 4.3 Dokumentasi API sebagai Hasil Implementasi
Daftar berikut adalah representasi titik akhir (*endpoints*) API yang telah berhasil dikembangkan dan siap digunakan. Dokumentasi ini berfungsi sebagai bukti penyelesaian lingkup pekerjaan backend.

### 4.3.1 Tabel Ringkasan Endpoint Terimplementasi
*(Tabel berisi daftar lengkap endpoint: Method, URL Path, dan Deskripsi Fungsi)*

### 4.3.2 Contoh Representasi Request & Response
*(Snippet JSON aktual dari pengujian untuk endpoint utama)*
- **Endpoint Project Create**: Contoh JSON Request & Response sukses.
- **Endpoint TTS Generate**: Contoh JSON Request & Response sukses.

## 4.4 Hasil Pengujian Sistem
Subbab ini menyajikan data hasil pengujian yang dilakukan berdasarkan metode yang telah dirancang pada Bab III Subbab 3.12.

### 4.4.1 Hasil Pengujian Fungsional (Black Box Testing)
Pengujian ini mengacu pada skenario yang ditetapkan di **Tabel 3.12, 3.13, dan 3.14** pada Bab III.

#### 4.4.1.1 Hasil Pengujian Manajemen Aset dan Pengguna
- **Objek Uji**: API Upload Cloudinary, Voice Library.
- **Hasil Pengujian**:
    - Tabel hasil eksekusi uji (Skenario vs Hasil Aktual vs Status [Berhasil/Gagal]).
    - Pembahasan singkat mengenai penanganan validasi input (misal: penolakan file .exe).

#### 4.4.1.2 Hasil Pengujian Layanan Video AI
- **Objek Uji**: API Project (Create, Polling, Retrieve).
- **Hasil Pengujian**:
    - Tabel hasil eksekusi simulasi siklus hidup proyek (Start -> Processing -> Completed).
    - Bukti keberhasilan integrasi *polling* status asinkron.

#### 4.4.1.3 Hasil Pengujian Layanan Audio AI
- **Objek Uji**: API TTS (Kokoro/Chatterbox), Voice Cloning.
- **Hasil Pengujian**:
    - Tabel hasil eksekusi generasi audio.
    - Verifikasi output audio (durasi, format file).

### 4.4.2 Hasil Pengujian Kinerja Berbasis Log Sistem
Hasil pengukuran metrik kinerja yang diekstraksi dari telemetri internal Modal.com, sesuai rencana di Bab III Subbab 3.12.2.

**Tabel 4.X Data Kinerja Rata-Rata (Sampel n=X Eksekusi)**
| Layanan (Model) | Cold Start (detik) | Execution Time (detik) | Queue Time (detik) |
| :--- | :--- | :--- | :--- |
| Video Gen (Wan2.1) | [Data Aktual] | [Data Aktual] | [Data Aktual] |
| Audio Gen (Kokoro) | [Data Aktual] | [Data Aktual] | [Data Aktual] |

### 4.4.3 Hasil Analisis Biaya Generasi (*Cost Analysis*)
Realisasi perhitungan ekonomi sesuai rumus di Bab III Subbab 3.12.3.
- **Biaya Komputasi**: Perhitungan biaya riil untuk 1x transaksi generasi video/audio berdasarkan durasi eksekusi dan tarif GPU Modal.com.
- **Unit Economics**: Konversi menjadi "Biaya per menit video" atau "Biaya per request".

## 4.5 Pembahasan Hasil Pengujian

### 4.5.1 Analisis Kinerja Arsitektur Serverless
- Pembahasan mengenai dampak *Cold Start* terhadap pengalaman pengguna (UX).
- Efektivitas mekanisme *scale-to-zero* dalam penghematan biaya saat *idle*.

### 4.5.2 Evaluasi Keandalan Sistem Asinkron
- Analisis mengenai stabilitas mekanisme *polling* vs *webhook* (jika ada).
- Kehandalan sistem antrean Modal dalam menangani tugas berdurasi panjang (*long-running tasks*).

### 4.5.3 Komparasi Biaya vs Solusi Konvensional (FinOps)
- Perbandingan *Head-to-head*: Biaya infrastruktur "Pay-as-you-go" Creatorify vs Estimasi biaya sewa GPU Dedicated (AWS EC2 g5.xlarge) untuk beban kerja yang sama.
- Pembuktian efisiensi biaya arsitektur terpilih.

## 4.6 Keterbatasan Penelitian
Menguraikan batasan-batasan teknis atau metodologis yang ditemukan selama proses implementasi dan pengujian, yang dapat menjadi peluang pengembangan di masa depan (misal: limitasi durasi video, ketergantungan pada *availability* GPU H100).
