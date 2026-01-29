# BAB II
TINJAUAN PUSTAKA

## 2.1 Penelitian Terdahulu (*State of the Art*)

Subbab ini akan menguraikan kajian kritis terhadap minimal **25 jurnal ilmiah internasional dan nasional** (5 tahun terakhir: 2021-2026) yang relevan dengan topik penelitian.

### 2.1.1 Klasifikasi Topik Penelitian Terkait
Penelitian terdahulu akan dikelompokkan ke dalam tiga klaster utama untuk mempermudah pemetaan posisi penelitian:
1.  **Arsitektur *Serverless* untuk *High-Performance Computing* (HPC)**: Studi mengenai penggunaan platform serverless (AWS Lambda, Modal, Google Cloud Run) untuk beban kerja berat.
2.  **Orkestrasi Pipeline *Generative AI***: Studi tentang manajemen alur kerja model AI (TTS, Voice Cloning, Video Diffusion) dalam lingkungan produksi.
3.  **Optimasi *Microservices* & *API Gateway***: Studi tentang pola desain sistem terdistribusi untuk meminimalkan latensi dan memaksimalkan *throughput*.

### 2.1.2 Tabel Pemetaan Penelitian Terdahulu
(Format tabel yang akan diisi dengan 25 jurnal)
| No | Peneliti & Tahun | Judul Penelitian | Metode/Teknologi | Hasil & Temuan | Keterbatasan (Gap) |
|----|------------------|------------------|------------------|----------------|--------------------|
| 1  | [Contoh] Walia (2024) | *Challenges of Serverless for LLMs* | Serverless AWS | Tantangan cold-start pada model besar | Belum membahas solusi spesifik untuk GPU-intensive tasks |
| ...| ... | ... | ... | ... | ... |

### 2.1.3 Analisis Kesenjangan Penelitian (*Research Gap*)
Menjelaskan posisi penelitian ini di antara penelitian-penelitian sebelumnya. Fokus utama adalah mengisi celah mengenai **"Orkestrasi Asinkron pada Arsitektur Serverless GPU untuk Layanan Generatif Multi-Modal (Suara & Video)"** yang belum banyak dibahas secara komprehensif oleh satu penelitian spesifik.

## 2.2 Landasan Teori Arsitektur Perangkat Lunak

Menjelaskan paradigma arsitektur yang mendasari perancangan sistem backend.

### 2.2.1 Arsitektur Microservices
*   **Definisi Konseptual**: Pendekatan pengembangan perangkat lunak sebagai suite layanan kecil yang independen.
*   **Karakteristik Utama**: *Decoupled services*, komunikasi via API, dan manajemen database terpisah.
*   **Relevansi**: Dasar pemisahan antara layanan orkestra utama (`app.py`) dan layanan TTS spesifik (`chatterbox_app.py`).

### 2.2.2 RESTful API (*Representational State Transfer*)
*   **Prinsip Desain**: *Statelessness*, *Client-Server architecture*, dan keseragaman antarmuka.
*   **HTTP Methods & Status Codes**: Standar komunikasi data (GET, POST, PUT, DELETE) yang digunakan dalam endpoints sistem.

### 2.2.3 Arsitektur Serverless & *Event-Driven*
*   **Konsep FaaS** (*Function as a Service*): Model eksekusi di mana alokasi sumber daya dikelola sepenuhnya oleh penyedia cloud secara *ephemeral*.
*   **Event-Driven Mechanism**: Pemicu eksekusi berdasarkan peristiwa (request masuk) dan pola *asynchronous polling* untuk tugas berdurasi panjang.

### 2.2.4 Pola Desain *API Gateway*
*   **Definisi & Fungsi**: Pola arsitektur yang bertindak sebagai gerbang tunggal (*single entry point*) untuk semua klien.
*   **Peran dalam Orkestrasi**: Menangani *routing*, agregasi respons, dan pendelegasian tugas ke layanan backend yang sesuai (User Service vs AI Service).

### 2.2.5 Mekanisme *Asynchronous Processing*
*   **Konsep Dasar**: Model eksekusi non-blocking di mana klien tidak perlu menunggu proses selesai untuk mendapatkan respons awal (*Fire-and-Forget* atau *Polling*).
*   **Message Queues & Polling**: Teori tentang penggunaan antrian tugas dan mekanisme status check untuk menangani pekerjaan berat (*long-running tasks*) seperti generasi video AI.

## 2.3 Landasan Teori Komputasi & Infrastruktur

Teori mengenai infrastruktur keras dan lunak yang mendukung beban kerja AI.

### 2.3.1 *GPU Computing* untuk *Deep Learning*
*   **Arsitektur GPU**: Perbedaan mendasar CPU vs GPU (*Parallel Processing*).
*   **Peran CUDA Cores & VRAM**: Pentingnya memori bandwidth tinggi (HBM) untuk memuat model *Large Generative Models* seperti Wan2.1.

### 2.3.2 Kontainerisasi Aplikasi (*Containerization*)
*   **Definisi**: Metode virtualisasi tingkat sistem operasi yang membungkus aplikasi dan dependensinya dalam wadah terisolasi (kontainer).
*   **Relevansi**: Dasar teknologi di balik *deployable images* pada platform Modal.com yang memastikan konsistensi lingkungan eksekusi.

### 2.3.3 *Serverless GPU* & *Persistent Volumes*
*   **Konsep Hibrida**: Penggabungan fleksibilitas *serverless* dengan kekuatan komputasi GPU.
*   **Manajemen Persistensi**: Penggunaan volume persisten (*network-attached storage*) untuk mengatasi sifat *stateless/ephemeral* dari fungsi serverless, hal ini krusial untuk menyimpan model AI besar (>50GB) agar tidak perlu diunduh ulang setiap eksekusi (*Cold Start Mitigation*).

### 2.3.4 *Object Storage* & Media Management
*   **Konsep Penyimpanan Objek**: Perbedaan menyimpan data media (BLOB) di *Object Storage* vs Database Relasional.
*   **Content Delivery Network (CDN)**: Peran CDN dalam mendistribusikan hasil generasi video/audio kepada pengguna akhir dengan latensi rendah.

## 2.4 Landasan Teori Sistem Generatif (Objek Studi)

Menjelaskan konsep-konsep teoretis objek spesifik yang dibangun.

### 2.4.1 Sistem Layanan Generatif (*Generative AI Systems*)
*   **Definisi & Konsep**: Sistem yang membangkitkan data baru, bukan sekadar prediksi.
*   **Komponen Pembentuk**: Arsitektur model generatif (Input -> Model -> Output).

### 2.4.2 *Voice Processing* dan *Voice Cloning*
*   **Text-to-Speech (TTS)**: Teori konversi teks ke sinyal audio.
*   **Voice Cloning**: Konsep *speaker embedding* dan *zero-shot learning* pada model suara.

### 2.4.3 *Video Avatar Generation* (Talking Head)
*   **Konsep Talking Head**: Sinkronisasi *lip-sync* dan ekspresi wajah.
*   **Pipeline Generasi**: Alur standar pemrosesan dari input gambar+audio menjadi video.

## 2.5 Tinjauan Teknologi Pengembangan

Kajian akademis terhadap teknologi spesifik yang dipilih (bukan tutorial).

### 2.5.1 Framework Backend: FastAPI
*   Landasan pemilihan: Dukungan *Asynchronous I/O* (ASGI) standar industri Python modern.

### 2.5.2 Platform Komputasi: Modal.com
*   Analisis teknologi: Kontainerisasi berbasis kode (*Cloud Functions*) dengan akses GPU langsung.

### 2.5.3 Basis Data Relasional: PostgreSQL (Supabase)
*   Peran dalam sistem: Manajemen status transaksional (*ACID*) dan integritas data pengguna.

### 2.5.4 Manajemen Media: Cloudinary
*   Peran dalam sistem: Layanan *Object Storage* terkelola dan optimasi polimorfik aset media.

## 2.6 Kerangka Berpikir dan Metode Pengujian

### 2.6.1 Kerangka Berpikir Penelitian
Visualisasi alur logika penelitian dari Identifikasi Masalah -> Solusi Arsitektural -> Hasil Sistem Skalabel.

### 2.6.2 Metode Pengujian Sistem (*Black Box Testing*)
*   **Equivalence Partitioning**: Validasi kelas input valid/invalid.
*   **Boundary Value Analysis**: Pengujian batas parameter API.

### 2.6.3 Pengujian & Tooling API
*   **API Testing Principles**: Validasi struktur respons JSON, Header, dan latensi.
*   **Tooling**: Peran alat seperti Postman/cURL dalam simulasi permintaan klien.

### 2.6.4 Metrik Pengukuran Performa
*   **Response Time (Time-to-First-Byte)**: Latensi jaringan dan pemrosesan awal.
*   **Task Completion Time**: Durasi total generasi konten (End-to-End).
*   **Throughput**: Kapasitas penanganan permintaan per satuan waktu.

## 2.7 Alat Pemodelan Sistem

Menjelaskan standar diagram yang digunakan untuk merancang arsitektur dan alur data sistem pada Bab III.

### 2.7.1 *Unified Modeling Language* (UML)
*   **Relevansi**: Standar visualisasi untuk sistem berorientasi objek modern.
*   **Use Case Diagram**: Menggambarkan fungsionalitas sistem dari perspektif aktor eksternal (Frontend/User) dan batasan sistem.
*   **Activity Diagram**: Digunakan untuk memodelkan alur kerja (*workflow*) logika bisnis secara prosedural (Sequential Algorithm).
*   **Sequence Diagram**: Krusial untuk memodelkan interaksi pertukaran pesan antar objek (*Frontend* -> *API Gateway* -> *Worker*) dalam sistem terdistribusi.

### 2.7.2 *Entity Relationship Diagram* (ERD)
*   **Definisi**: Model data konseptual untuk menggambarkan struktur basis data relasional.
*   **Relevansi**: Dasar perancangan skema tabel User, Project, dan Metadata pada PostgreSQL.

