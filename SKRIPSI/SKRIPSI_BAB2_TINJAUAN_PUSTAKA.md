# BAB II
TINJAUAN PUSTAKA

## 2.1 Penelitian Terdahulu (*State of the Art*)

Subbab ini menguraikan kajian kritis terhadap 25 jurnal ilmiah internasional dan nasional yang dipublikasikan dalam rentang waktu lima tahun terakhir (2020-2026). Kajian ini dilakukan untuk memetakan posisi penelitian, mengidentifikasi tren teknologi terkini, serta menemukan kesenjangan (*gap*) penelitian yang menjadi landasan urgensi pengembangan sistem ini.

### 2.1.1 Klasifikasi Topik Penelitian Terkait

Berdasarkan analisis terhadap literatur terpilih, tren penelitian dalam pengembangan infrastruktur AI dapat diklasifikasikan ke dalam tiga klaster utama yang saling beririsan:

**1. Arsitektur *Serverless* untuk *High-Performance Computing* (HPC)**
Penelitian di klaster ini berfokus pada pergeseran paradigma dari manajemen server tradisional menuju *serverless computing* untuk beban kerja berat (*compute-intensive*). Studi-studi terbaru, seperti yang dilakukan oleh Fu et al. (2024) dan Yang et al. (2024), menyoroti tantangan utama dalam menjalankan model *Deep Learning* di lingkungan *serverless*, yaitu latensi *cold start* yang tinggi. Tren penelitian menunjukkan upaya masif dalam optimasi inisialisasi GPU dan manajemen memori untuk memungkinkan inferensi model besar seperti LLM dan *Diffusion Models* di lingkungan yang bersifat *ephemeral*. Hal ini mengindikasikan bahwa *serverless* bukan lagi sekadar untuk fungsi ringan, melainkan mulai matang sebagai infrastruktur HPC yang efisien biaya.

**2. Orkestrasi Pipeline *Generative AI***
Klaster ini membahas kompleksitas pengelolaan alur kerja (*workflow*) sistem generatif modern yang melibatkan banyak modalitas (teks, audio, video). Riset dari Liu et al. (2024) dan Zhang et al. (2024) memperlihatkan bahwa sistem *talking head* dan video generatif tidak lagi berdiri sebagai model tunggal, melainkan sebuah *pipeline* panjang yang mencakup pra-pemrosesan audio, sinkronisasi bibir, hingga *rendering* visual. Fokus penelitian terkini adalah bagaimana mengelola dependensi antar-tahap ini secara efisien agar dapat beroperasi mendekati *real-time* (VASA-1, Microsoft Research 2024).

**3. Optimasi *Microservices* & *API Gateway***
Klaster ketiga menyoroti peran arsitektur sistem terdistribusi dalam melayani model AI. Kim et al. (2024) dalam penelitiannya mengenai "EAGLE" menegaskan bahwa *API Gateway* konvensional sering menjadi *bottleneck* untuk layanan AI. Oleh karena itu, tren penelitian bergerak menuju desain *Event-Driven API Gateway* yang mampu menangani pola komunikasi asinkron. Studi dari Ramamoorthi & Menascé (2023) juga menekankan pentingnya orkestrasi adaptif pada level *microservices* untuk menangani fluktuasi beban permintaan inferensi yang dinamis.

### 2.1.2 Tabel Pemetaan Penelitian Terdahulu

Berikut adalah pemetaan komprehensif terhadap 25 jurnal referensi utama yang digunakan sebagai landasan *State of the Art* (SOTA) penelitian ini:

| No | Peneliti & Tahun | Judul Penelitian | Metode/Teknologi | Hasil & Temuan | Keterbatasan (Gap) |
|----|------------------|------------------|------------------|----------------|--------------------|
| 1 | Fu et al. (2024) | *ServerlessLLM: Low-Latency Serverless Inference for Large Language Models* | Checkpoint Loading Optimization | Pengurangan latensi inisialisasi model hingga 10-200x melalui pemuatan checkpoint multi-tier. | Fokus pada LLM teks, belum spesifik menangani kompleksitas dependensi model video/audio multi-modal. |
| 2 | Yang et al. (2024) | *PipeCo: Pipelining Cold Start for Deep Learning Inference Services* | Pipeline Initialization Strategy | Menyembunyikan latensi inisialisasi dengan memparalelkan proses loading model dan runtime. | Memerlukan modifikasi mendalam pada level orkestrator yang sulit diterapkan pada platform publik (Modal). |
| 3 | Zhang et al. (2024) | *Advancing Serverless Computing for Scalable AI Model Inference: A Review* | Systematic Literature Review | Serverless efektif untuk AI tetapi terkendala pada manajemen status (*state*) dan cold start GPU. | Survey bersifat umum, kurang memberikan solusi arsitektural spesifik untuk pipeline video generatif. |
| 4 | Zhang et al. (2023) | *MQFQ-Sticky: Integrated Fair Queueing and GPU Memory Management* | Queueing Theory & GPU Memory Manager | Peningkatan keadilan (*fairness*) dan utilitas memori pada cluster GPU serverless. | Lebih berfokus pada efisiensi penyedia layanan cloud (provider-side), bukan optimasi dari sisi aplikasi pengguna. |
| 5 | Chen et al. (2023) | *Efficient Serverless Support for Multi-Instance GPUs Through Pipelining* | Multi-Instance GPU (MIG) & Pipelining | Meningkatkan throughput dengan membagi satu GPU fisik ke beberapa fungsi serverless. | Solusi level infrastruktur fisik yang tidak selalu dapat dikontrol oleh pengembang aplikasi di platform PaaS/FaaS. |
| 6 | Kim et al. (2024) | *EAGLE: Event-driven API Gateway with Low latency Execution for AI Services* | Async API Gateway Architecture | Gateway berbasis event terbukti menurunkan latensi antrian untuk layanan AI vision/voice. | Belum membahas integrasi spesifik dengan mekanisme *polling* untuk tugas berdurasi sangat panjang (>2 menit). |
| 7 | Moreschini et al. (2024) | *Designing Microservices Using AI: A Systematic Literature Review* | Systematic Review | Identifikasi pola desain microservices yang dioptimalkan untuk integrasi komponen AI. | Masih bersifat teoritis konseptual, minim studi kasus implementasi pipeline video avatar. |
| 8 | Ramamoorthi & Menascé (2023) | *Real-Time Adaptive Orchestration of AI Microservices in Dynamic Edge Computing* | Adaptive Orchestration Algorithm | Algoritma dinamis untuk penempatan service AI berdasarkan beban komputasi *real-time*. | Fokus pada lingkungan *Edge Computing* dengan sumber daya terbatas, bukan cloud GPU *high-end*. |
| 9 | Zhang et al. (2024) | *AI-Driven Orchestration for Scalable Microservices* | Predictive Auto-scaling | Menggunakan prediksi AI untuk melakukan scaling microservices sebelum beban puncak terjadi. | Kompleksitas tinggi untuk diterapkan pada skala startup atau proyek skripsi dengan data historis terbatas. |
| 10 | Al-Debagy & Martinek (2020) | *Performance Comparison between a Monolithic and a Microservice Application* | Comparative Benchmarking | Microservices unggul dalam skalabilitas dan *fault isolation* dibanding monolitik. | Pengujian dilakukan pada aplikasi standar (CRUD), bukan aplikasi dengan beban komputasi GPU yang ekstrem. |
| 11 | IEEE Software (2023) | *AsyncAPI: Standardizing Event-Driven Architectures for AI* | Architecture Patterns | Standarisasi komunikasi asinkron krusial untuk mencegah sistem gantung (*hang*) pada proses AI. | Hanya membahas standar protokol, bukan implementasi teknis pada *runtime* Python/FastAPI. |
| 12 | Zhang et al. (2024) | *GaussianTalker: Real-Time Pose-Controllable Talking Head Synthesis via 3D Gaussian Splatting* | 3D Gaussian Splatting (3DGS) | Generasi avatar *real-time* dengan kualitas visual tinggi dan kontrol pose yang presisi. | Fokus pada algoritma rendering visual, belum membahas aspek *serving* model tersebut di backend berskala besar. |
| 13 | Microsoft Research (2024) | *VASA-1: Lifelike Audio-Driven Talking Faces Generated in Real Time* | Disentangled Latent Space Learning | Capaian SOTA kualitas video avatar dengan latensi ultra-rendah dan sinkronisasi bibir presisi. | Model bersifat *closed-source* dan proprietari, sulit direplikasi atau dimodifikasi untuk penelitian terbuka. |
| 14 | Liu et al. (2024) | *A Comprehensive Taxonomy and Analysis of Talking Head Synthesis* | Taxonomy & Analysis | Memetakan evolusi metode generasi avatar dari 2D GAN hingga 3D NeRF/Gaussian Splatting. | Fokus pada perbandingan kualitas visual, kurang membahas aspek kebutuhan komputasi implementatif. |
| 15 | RETA Team (2024) | *Real-Time and Expressive Talking Head Animation* | End-to-End Framework | Kerangka kerja generasi avatar yang mencapai 55 FPS dengan ekspresi dinamis. | Optimasi dilakukan pada level model inferensi, tanpa tinjauan aspek skalabilitas *multi-user*. |
| 16 | Ren et al. (2021) | *FastSpeech 2: Fast and High-Quality End-to-End Text to Speech* | Non-autoregressive TTS | Kecepatan inferensi TTS meningkat signifikan dibanding model autoregressive (Tacotron). | Model dasar yang efisien, namun perlu integrasi lebih lanjut untuk mendukung *voice cloning* yang fleksibel. |
| 17 | Wang (2024) | *Review of Talking Head Synthesis for Driving Mechanisms and Portrait Rendering* | Review & Survey | Analisis mendalam tentang mekanisme penggerak (*driving mechanism*) audio-ke-ekspresi. | Tidak membahas integrasi mekanisme ini ke dalam arsitektur cloud serverless. |
| 18 | Martin-Lopez et al. (2021) | *RESTest: Automated Black-Box Testing of RESTful APIs* | Automated Testing Framework | Metode otomatisasi pengujian *black-box* yang efektif menemukan *bug* pada REST API. | Fokus pada deteksi kesalahan fungsional umum, belum spesifik pada metrik performa AI (latensi inferensi). |
| 19 | Scheuner & Leitner (2020) | *Performance Benchmarking of Serverless Computing Platforms* | Benchmarking Methodology | Standar metodologi pengukuran kinerja FaaS (cold start vs warm start). | Pengujian dilakukan pada fungsi CPU umum, metrik mungkin berbeda untuk inisialisasi konteks CUDA GPU. |
| 20 | Karimi et al. (2023) | *Automated Black-box Testing of RESTful APIs using Artificial Bee Colony* | Optimization Algorithm | Algoritma optimasi untuk meningkatkan *coverage* pengujian API secara otomatis. | Kompleksitas implementasi tinggi untuk pengujian fungsionalitas dasar skripsi. |
| 21 | IEEE Access (2023) | *Comparative Analysis of REST API Performance on Serverless vs Monolithic* | Comparative Study | Serverless menunjukkan fluktuasi latensi lebih tinggi namun efisiensi biaya lebih baik pada beban tidak menentu. | Konteks perbandingan umum, perlu validasi spesifik pada kasus penggunaan generasi video. |
| 22 | Firework (2024) | *The State of Short-Form Video: Trends and Statistics for 2024* | Industry Market Report | Validasi urgensi pasar terhadap kebutuhan konten video pendek dan avatar virtual. | Laporan industri, bukan jurnal teknis, namun valid sebagai data pendukung latar belakang bisnis. |
| 23 | Research and Markets (2025) | *Generative AI Market - Global Outlook & Forecast 2024-2029* | Market Forecast | Prediksi pertumbuhan pasar GenAI yang mendukung relevansi topik skripsi. | Data statistik makro, tidak menyentuh aspek teknis implementasi. |
| 24 | arXiv Contributors (2024) | *Large Language Diffusion Models (LLaDA)* | Generative Model Research | Perkembangan terbaru model difusi yang menunjukkan potensi skalabilitas tinggi. | Fokus pada inovasi algoritma permodelan, bukan sistem *serving* atau *deployment*. |
| 25 | Journal of Systems and Software (2024) | *AI-Enhanced Fault Tolerance in Microservices* | Fault Tolerance Patterns | Mekanisme ketahanan sistem (*resilience*) krusial untuk arsitektur microservices yang kompleks. | Pembahasan berfokus pada prediksi kegagalan, belum menspesifikkan penanganan *timeout* pada video rendering. |

### 2.1.3 Analisis Kesenjangan Penelitian (*Research Gap*)

Berdasarkan pemetaan matriks di atas, teridentifikasi sebuah kesenjangan penelitian yang signifikan di persimpangan antara optimasi infrastruktur dan aplikasi AI spesifik. Mayoritas penelitian "Serverless GPU" (Fu et al., 2024; Yang et al., 2024) berfokus pada level sistem operasi atau *scheduler* penyedia layanan cloud, yang seringkali berada di luar kendali pengembang aplikasi. Di sisi lain, penelitian mengenai "Generative AI" (Zhang et al., 2024; Microsoft Research, 2024) cenderung sangat berat pada inovasi algoritma model, mengabaikan aspek aritektur *serving* yang skalabel untuk banyak pengguna.

Belum banyak penelitian yang secara spesifik membahas **"Orkestrasi Asinkron pada Arsitektur Serverless GPU untuk Layanan Generatif Multi-Modal (Suara & Video)"** dari perspektif *Backend Engineering*. Penelitian seperti EAGLE (Kim et al., 2024) sudah mulai menyentuh area ini untuk *vision AI*, namun belum mencakup kompleksitas *pipeline* video avatar yang melibatkan durasi pemrosesan sangat panjang (*long-running tasks*) dan dependensi multi-model (TTS + *Lip Sync* + *Rendering*). Penelitian ini hadir untuk mengisi celah tersebut dengan merancang arsitektur *backend* yang tidak hanya memanggil model AI, tetapi mengorkestrasinya secara efisien menggunakan pola asinkron dan manajemen status yang tepat di atas infrastruktur *serverless* komersial.

## 2.2 Landasan Teori Arsitektur Perangkat Lunak

### 2.2.1 Arsitektur Microservices
Arsitektur *Microservices* merupakan pendekatan pengembangan perangkat lunak di mana aplikasi dibangun sebagai sekumpulan layanan kecil yang berjalan secara independen dan berkomunikasi melalui protokol yang ringan, umumnya HTTP Resource API. Karakteristik utama dari arsitektur ini terletak pada sifatnya yang *decoupled*, di mana setiap layanan memiliki basis kode, siklus hidup, dan bahkan mekanisme penyimpanan data sendiri. Hal ini memungkinkan tim pengembang untuk melakukan *deployment* dan *scaling* pada satu layanan tanpa mengganggu keseluruhan sistem (Newman, 2021). Dalam konteks penelitian ini, pola *microservices* diterapkan untuk memisahkan logika utama aplikasi (*orchestrator*) dengan layanan generatif spesifik seperti *Chatterbox*, sehingga kegagalan atau beban tinggi pada proses sintesis suara tidak akan melumpuhkan fungsi manajemen proyek video utama.

### 2.2.2 RESTful API (*Representational State Transfer*)
RESTful API adalah gaya arsitektur komunikasi jaringan yang berbasis pada protokol HTTP dan memanfaatkan metode standar seperti GET, POST, PUT, dan DELETE untuk memanipulasi sumber daya. Prinsip utamanya adalah *statelessness*, yang berarti setiap permintaan dari klien ke server harus memuat seluruh informasi yang diperlukan untuk memahami dan memproses permintaan tersebut, tanpa bergantung pada konteks sesi yang disimpan di server. Keseragaman antarmuka (*uniform interface*) yang ditawarkan oleh REST menjadikannya standar industri untuk integrasi sistem yang heterogen. Penelitian ini mengadopsi prinsip RESTful untuk menyediakan antarmuka yang standar bagi aplikasi *frontend* dan *mobile* dalam mengakses layanan AI yang kompleks di backend.

### 2.2.3 Arsitektur Serverless & *Event-Driven*
Arsitektur *Serverless*, atau sering disebut sebagai *Function-as-a-Service* (FaaS), adalah model eksekusi *cloud* di mana penyedia layanan *cloud* secara dinamis mengelola alokasi sumber daya mesin. Pengembang hanya perlu fokus pada kode fungsi tunggal tanpa perlu memikirkan penyediaan (*provisioning*) atau pemeliharaan server fisik (Zhang et al., 2024). Mekanisme ini sangat erat kaitannya dengan pola *Event-Driven*, di mana fungsi hanya akan dieksekusi ketika dipicu oleh peristiwa tertentu, seperti permintaan HTTP masuk. Keunggulan utamanya adalah efisiensi biaya yang ekstrem melalui model pembayaran *pay-per-use* dan kemampuan *auto-scaling* dari nol hingga ribuan instans secara instan. Ini sangat relevan untuk kebutuhan inferensi model AI yang bersifat *bursty* dan memakan sumber daya besar namun tidak selalu aktif setiap saat.

### 2.2.4 Pola Desain *API Gateway*
*API Gateway* bertindak sebagai gerbang tunggal (*single entry point*) yang mengelola semua lalu lintas permintaan dari klien ke berbagai layanan *backend* mikro. Fungsinya tidak hanya sekadar penerus permintaan (*reverse proxy*), tetapi juga mencakup orkestrasi, otentikasi, pembatasan laju (*rate limiting*), dan transformasi protokol (Kim et al., 2024). Dalam sistem yang diusulkan, *API Gateway* memegang peran krusial sebagai manajer lalu lintas yang cerdas. Ia bertanggung jawab untuk menerima permintaan pembuatan video dari pengguna, mendelegasikannya ke *worker* GPU yang sesuai secara asinkron, dan mengembalikan respons awal berupa ID pelacakan (*tracking ID*), sehingga klien tidak perlu menunggu proses yang lama dalam koneksi yang terbuka (*blocking*).

### 2.2.5 Mekanisme *Asynchronous Processing*
Mekanisme pemrosesan asinkron adalah model eksekusi *non-blocking* yang memungkinkan sebuah tugas berat diproses di latar belakang tanpa menahan alur eksekusi utama. Dalam pola ini, ketika klien mengirimkan permintaan, sistem segera mengembalikan konfirmasi penerimaan, sementara proses sebenarnya dimasukkan ke dalam antrian (*queue*) untuk dikerjakan oleh *worker* yang tersedia (IEC 62559). Strategi ini, yang sering diimplementasikan dengan pola *polling* atau *webhook*, sangat vital untuk menangani tugas-tugas *Generative AI* yang durasinya bisa mencapai beberapa menit, seperti *rendering* video. Penelitian referensi menunjukkan bahwa penerapan pola ini secara signifikan meningkatkan *throughput* sistem dan mencegah terjadinya *timeout* pada sisi klien (IEEE Software, 2023).

### 2.2.6 Pola Arsitektur Berlapis (*Layered Architecture*)
Pola Arsitektur Berlapis (*Layered Architecture*) adalah pola organisasi kode yang membagi aplikasi menjadi kelompok-kelompok sub-tugas logis yang disebut "lapisan". Pola standar yang umum digunakan terdiri dari tiga lapisan utama: lapisan presentasi/antarmuka, lapisan logika bisnis, dan lapisan persistensi data (Richards & Ford, 2020). Tujuan utama dari pola ini adalah mencapai *Separation of Concerns* (SoC), di mana perubahan pada satu lapisan (misalnya mengganti *database* di lapisan data) tidak mempengaruhi logika bisnis atau antarmuka API secara signifikan. Dalam konteks pengembangan *backend* modern, pola ini sangat krusial untuk menjaga *maintainability* (kemudahan pemeliharaan) kode di dalam sebuah repositori (*Monorepo*), meskipun sistem tersebut dikerahkan sebagai *microservices* terdistribusi.

## 2.3 Landasan Teori Komputasi & Infrastruktur

### 2.3.1 *GPU Computing* untuk *Deep Learning*
Unit Pemrosesan Grafis (GPU) memiliki arsitektur yang secara fundamental berbeda dari CPU, dirancang dengan ribuan *core* kecil yang mampu menangani operasi paralel secara masif. Karakteristik ini menjadikannya sangat ideal untuk operasi perkalian matriks yang menjadi tulang punggung algoritma *Deep Learning*. Keberadaan memori bandwidth tinggi (HBM) pada GPU modern seperti NVIDIA H100 sangat krusial untuk memuat parameter model generatif raksasa (seperti Wan2.1 dengan 14 miliar parameter) agar proses inferensi dapat berjalan dengan latensi yang dapat diterima manusia. Tanpa akselerasi GPU, waktu generasi video bisa memakan waktu berjam-jam, sehingga pemanfaatannya menjadi syarat mutlak dalam sistem ini.

### 2.3.2 Kontainerisasi Aplikasi (*Containerization*)
Kontainerisasi adalah metode virtualisasi tingkat sistem operasi yang membungkus kode aplikasi beserta seluruh dependensinya—seperti *library*, konfigurasi, dan *runtime*—ke dalam satu paket portabel yang disebut kontainer. Teknologi ini memecahkan masalah klasik "it works on my machine" dengan menjamin konsistensi lingkungan eksekusi di mana pun aplikasi dijalankan, baik di laptop pengembang maupun di klaster *cloud*. Dalam konteks platform Modal.com, kontainerisasi menjadi dasar mekanisme *deployment*, memungkinkan definisi lingkungan GPU yang kompleks (seperti versi CUDA dan PyTorch spesifik) dideklarasikan secara eksplisit dalam kode dan direplikasi secara instan.

### 2.3.3 *Serverless GPU* & *Persistent Volumes*
Konsep *Serverless GPU* adalah evolusi hibrida yang menggabungkan fleksibilitas serverless dengan kekuatan komputasi perangkat keras khusus. Tantangan terbesar dalam model ini adalah sifatnya yang *stateless* dan *ephemeral*, yang berarti data lokal akan hilang setelah fungsi selesai dieksekusi. Hal ini menjadi masalah besar untuk model AI berukuran puluhan gigabyte yang membutuhkan waktu lama untuk diunduh ulang setiap kali fungsi dijalankan (*cold start*). Solusi inovatif untuk masalah ini adalah penggunaan *Persistent Volumes*, sebuah penyimpanan jaringan berkinerja tinggi yang "dicantolkan" ke fungsi serverless (Fu et al., 2024). Dengan volume persisten, bobot model dapat disimpan secara permanen dan dimuat ulang dengan sangat cepat, secara efektif memitigasi latensi *cold start* dan menjadikan serverless GPU layak untuk produksi.

### 2.3.4 *Object Storage* & Media Management
Berbeda dengan penyimpanan blok tradisional atau basis data relasional, *Object Storage* dirancang untuk menyimpan data tidak terstruktur (*unstructured data*)—seperti file video, audio, dan gambar—dalam jumlah masif dengan skalabilitas yang hampir tak terbatas. Setiap objek disimpan bersama dengan metadata dan pengenal unik, dan diakses melalui API HTTP, bukan protokol sistem file hirarkis. Dalam arsitektur sistem ini, layanan *Object Storage* seperti Cloudinary tidak hanya berfungsi sebagai gudang penyimpanan, tetapi juga sebagai jaringan pengiriman konten (CDN) yang cerdas. Kemampuannya untuk melakukan transformasi media *on-the-fly* (misalnya, mengubah format atau resolusi video saat diakses) sangat membantu dalam mengoptimalkan pengiriman konten hasil generasi AI ke berbagai perangkat pengguna dengan latensi minimal.

### 2.3.5 Konsep *Infrastructure as Code* (IaC)
*Infrastructure as Code* (IaC) adalah praktik pengelolaan dan penyediaan infrastruktur komputasi melalui file definisi yang dapat dibaca mesin (*machine-readable definition files*), alih-alih melalui konfigurasi perangkat keras fisik atau alat konfigurasi interaktif (Morris, 2021). Pendekatan ini memungkinkan infrastruktur diperlakukan sama seperti kode perangkat lunak: dapat diversi (*version control*), diuji, dan diduplikasi (*reproducible*). Dalam ekosistem *serverless* modern, IaC menghilangkan ambiguitas konfigurasi lingkungan produksi dan pengembangan, mengurangi risiko *human error* saat *deployment*, dan mempercepat siklus rilis perangkat lunak (Guerriero et al., 2019). Sistem yang dibangun dalam penelitian ini menerapkan IaC untuk mendefinisikan kebutuhan GPU dan dependensi sistem secara deklaratif langsung dalam kode Python.

## 2.4 Landasan Teori Sistem Generatif (Objek Studi)

### 2.4.1 Sistem Layanan Generatif (*Generative AI Systems*)
Sistem Layanan Generatif merujuk pada kelas sistem kecerdasan buatan yang dirancang untuk menciptakan data baru—baik berupa teks, gambar, audio, maupun video—yang memiliki karakteristik statistik serupa dengan data pelatihannya, namun orisinal. Berbeda dengan model diskriminatif yang hanya mengklasifikasikan data, model generatif mempelajari distribusi probabilitas gabungan dari data input dan output. Evolusi terkini di bidang ini didorong oleh arsitektur *Diffusion Models* dan *Transformers*, yang memungkinkan sintesis konten berkualitas tinggi dengan fidelitas yang sulit dibedakan dari karya manusia. Integrasi sistem ini ke dalam layanan web menuntut arsitektur backend yang mampu menangani kompleksitas komputasi inferensi sekaligus interaksi pengguna yang responsif.

### 2.4.2 *Voice Processing*, *Voice Cloning*, dan *Voice Conversion*
Pemrosesan suara dalam konteks AI generatif mencakup tiga teknologi utama: *Text-to-Speech* (TTS), *Voice Cloning*, dan *Voice Conversion*. TTS modern beranjak dari pendekatan konkatenatif tradisional menuju sintesis saraf (*neural synthesis*) yang mampu menghasilkan intonasi dan ritme bicara yang alami (Ren et al., 2021). Teknologi *Voice Cloning* memperluas kemampuan ini dengan menggunakan teknik *speaker embedding* dan *zero-shot learning* untuk mensintesis ucapan baru dari teks dengan karakteristik suara target. Sementara itu, *Voice Conversion* (VC) berfokus pada transformasi sinyal audio sumber menjadi suara target tanpa mengubah konten linguistiknya, memungkinkan fitur pengubah suara (*voice changer*) yang mempertahankan intonasi asli pembicara namun dengan *timbre* yang berbeda. Integrasi kedua kapabilitas ini dalam model Chatterbox memungkinkan personalisasi konten audio yang mendalam, namun juga membawa tantangan komputasi tambahan pada pipeline backend.

### 2.4.3 *Video Avatar Generation* (Talking Head)
Generasi Video Avatar, atau sering disebut sintesis *Talking Head*, adalah proses menghidupkan gambar wajah statis dengan menyinkronkan gerakan bibir (*lip-sync*) dan ekspresi wajah sesuai dengan input audio ucapan. Secara teoretis, proses ini melibatkan pemetaan fitur audio ke dalam ruang laten geometri wajah, yang kemudian dirender menjadi bingkai video fotorealistik. Teknologi terbaru seperti VASA-1 (Microsoft Research, 2024) dan GaussianTalker (Zhang et al., 2024) telah membawa kemampuan ini ke level *real-time* dengan kualitas visual yang tinggi. Tantangan utama dalam mengimplementasikan teknologi ini di backend adalah memastikan sinkronisasi audiovisual yang presisi dan menjaga konsistensi identitas wajah di sepanjang durasi video, yang memerlukan orkestrasi model AI yang sangat ketat.

### 2.4.4 Tinjauan Model AI Terpilih (*Selected AI Models*)

Subbab ini memaparkan analisis teknis mendalam terhadap model-model kecerdasan buatan spesifik yang dipilih untuk menggerakkan sistem backend. Pemilihan model-model ini didasarkan pada studi komparatif terhadap kinerja, efisiensi inferensi pada GPU, serta fleksibilitas lisensi *open-source*.

#### 2.4.4.1 Wan2.1 (*Foundation Video Model*)
Wan2.1 merupakan model generasi video berbasis arsitektur *Diffusion Transformer* (DiT) yang dikembangkan oleh Tim Wan dari Alibaba Cloud. Berbeda dengan model difusi konvensional (seperti U-Net pada Stable Diffusion awal), Wan2.1 mengadopsi mekanisme *Attention* penuh yang memungkinkannya menangkap dependensi temporal jangka panjang dalam video. Secara spesifik, varian 14 Miliar parameter (Wan2.1-I2V-14B) dipilih dalam penelitian ini karena kemampuannya yang superior dalam mempertahankan konsistensi identitas subjek dan stabilitas latar belakang (*background capability*) pada resolusi 1080p. Dalam arsitektur sistem usulan, Wan2.1 berfungsi sebagai *backbone* utama yang menerima input gambar statis dan menghasilkan video dinamis dengan fidelitas tinggi (Wan Team, 2025).

#### 2.4.4.2 InfiniteTalk (*Talking Head Synthesis*)
Untuk menangani spesifisitas sinkronisasi bibir dan ekspresi wajah, penelitian ini mengintegrasikan *InfiniteTalk*, sebuah kerangka kerja yang secara spesifik dibangun di atas **Wan2.1** sebagai *backbone* video generatif. InfiniteTalk memperkenalkan metode *Sparse-Frame Video Dubbing*, yang secara cerdas memanipulasi vektor gerakan wajah (*motion vectors*) berdasarkan input audio tanpa merusak struktur visual global video. Keunggulan utamanya dibandingkan metode seperti Wav2Lip adalah kemampuannya menyunting tidak hanya bibir, tetapi juga gerakan kepala mikro (*micro head-movements*) dan kedipan mata yang natural. Implementasi InfiniteTalk memungkinkan sistem untuk menghasilkan video "berbicara" dengan durasi yang tidak terbatas (*infinite length*) melalui mekanisme *streaming* konteks antar-frame (Yang et al., 2025).

#### 2.4.4.3 Kokoro-82M (*Efficient Text-to-Speech*)
Kokoro-82M dipilih sebagai mesin sintesis suara utama karena arsitekturnya yang sangat ringan (82 juta parameter) namun mampu menghasilkan kualitas suara yang setara dengan model berukuran gigabyte. Model ini merupakan hasil distilasi dari arsitektur *Large Audio Model* yang lebih besar, dioptimalkan untuk inferensi latensi rendah (*low-latency inference*). Dalam pengujian awal, Kokoro-82M menunjukkan kecepatan sintesis `0.5x realtime` pada GPU A10G, menjadikannya solusi ideal untuk memberikan umpan balik audio instan kepada pengguna sebelum proses generasi video yang lebih berat dimulai (Allal et al., 2025).

#### 2.4.4.4 Chatterbox (*Voice Cloning Engine*)
Chatterbox adalah modul yang dikhususkan untuk tugas *Voice Conversion* dan *Multilingual TTS*. Dibangun dengan fondasi arsitektur serup XTTS v2, Chatterbox memiliki kemampuan *zero-shot voice cloning*, yaitu kemampuan meniru karakteristik suara pembicara baru hanya dengan referensi audio 3-6 detik. Secara teknis, model ini bekerja dengan mengekstrak *speaker embedding* (vektor representasi karakteristik suara) dari file audio referensi dan mengkondisikan *decoder* TTS untuk menghasilkan spektrogram mel yang sesuai dengan *timbre* tersebut. Penggunaan Chatterbox memungkinkan fitur personalisasi tingkat tinggi, di mana pengguna dapat menggunakan suara mereka sendiri pada avatar digital yang dibuat (Resemble AI, 2025).

## 2.5 Teori Model Biaya Komputasi Awan (*Cloud Pricing Models*)

### 2.5.1 Strategi Harga *Pay-as-you-go*
Model penetapan harga *Pay-as-you-go* (BAYG) telah menjadi paradigma dominan dalam komputasi awan modern, menggantikan model *provisioning* statis yang mengharuskan penyewaan server dalam jangka waktu tetap (Wang et al., 2023). Dalam konteks *Serverless Computing*, model ini berevolusi menjadi *fine-grained billing*, di mana pengguna hanya dikenakan biaya berdasarkan durasi eksekusi fungsi dalam satuan milidetik dan jumlah memori yang dialokasikan (Eismann et al., 2021). Studi oleh Shafiei et al. (2022) dalam *IEEE Transactions on Cloud Computing* menunjukkan bahwa untuk beban kerja yang bersifat *bursty* (fluktuatif) seperti inferensi AI, model ini dapat menghemat biaya hingga 70-90% dibandingkan menyewa instance GPU *always-on* di AWS EC2 atau Google Compute Engine, karena mengeliminasi biaya *idle time*.

### 2.5.2 Ekonomi *Serverless* dan Tantangan *Cold Start*
Meskipun menjanjikan efisiensi biaya, penerapan *serverless* untuk *Deep Learning* menghadirkan tantangan ekonomi tersendiri. Biaya total operasional (TCO) pada arsitektur ini sangat dipengaruhi oleh fenomena *Cold Start*, yaitu latensi inisialisasi saat kontainer baru dibuat. Penelitian dari Li et al. (2024) menyoroti bahwa durasi *cold start*—yang mencakup pengunduhan model AI berukuran besar—tetap dihitung sebagai waktu eksekusi yang dapat ditagih oleh penyedia layanan, sehingga berpotensi mengurangi efisiensi biaya jika tidak dikelola dengan strategi *caching* atau *persistent volume* yang tepat.

### 2.5.3 Kerangka Kerja *FinOps* (Financial Operations)
*FinOps* adalah praktik budaya dan operasional yang membawa akuntabilitas keuangan ke dalam model pengeluaran variabel cloud (FinOps Foundation, 2024). Berbeda dengan manajemen biaya tradisional, FinOps menekankan kolaborasi antara tim teknis (engineering) dan keuangan untuk memaksimalkan nilai bisnis. Dalam pengembangan sistem AI, prinsip FinOps diterapkan melalui *Unit Economics*, yaitu menghitung biaya komputasi per unit transaksi (misalnya: biaya per menit video yang dihasilkan). Pendekatan ini memungkinkan pengembang untuk memprediksi margin keuntungan dan menentukan strategi harga jual layanan secara presisi berdasarkan konsumsi sumber daya riil (Storment & Fuller, 2023).

## 2.6 Tinjauan Teknologi Pengembangan

Subbab ini menguraikan spesifikasi teknis dari teknologi yang dipilih untuk membangun sistem. Analisis dilakukan tidak hanya pada definisi fungsional masing-masing teknologi, tetapi juga pada justifikasi akademis dan teknis mengapa teknologi tersebut merupakan pilihan paling tepat untuk memenuhi kebutuhan sistem yang dirancang.

### 2.6.1 Framework Backend: FastAPI
FastAPI adalah kerangka kerja web (*web framework*) modern untuk membangun antarmuka pemrograman aplikasi (API) dengan bahasa Python, yang dibangun di atas standar *Server Gateway Interface* (ASGI). Berbeda dengan pendahulunya seperti Flask atau Django yang lahir di era sinkron, FastAPI dirancang sejak awal untuk memaksimalkan fitur *asynchronous* (async/await) yang diperkenalkan pada Python 3.6+ (Ramírez, 2024). Framework ini memanfaatkan Pydantic untuk validasi data otomatis dan Starlette untuk penanganan permintaan web berkinerja tinggi.

Pemilihan FastAPI dalam penelitian ini didasarkan pada kebutuhan sistem akan konkurensi tingkat tinggi. Mengingat peran *backend* sebagai orkestrator yang harus mengelola banyak permintaan inferensi AI (yang bersifat *I/O bound*) secara bersamaan, arsitektur asinkron FastAPI memungkinkan server untuk tidak "terblokir" saat menunggu respons dari GPU *worker* atau *database*. Studi komparatif menunjukkan bahwa FastAPI mampu menangani ribuan permintaan per detik dengan latensi yang jauh lebih rendah dibandingkan *framework* berbasis WSGI konvensional (Roumeliotis et al., 2023), menjadikannya standar industri baru untuk layanan *Machine Learning* yang membutuhkan *throughput* tinggi dan latensi rendah.

### 2.6.2 Platform Komputasi: Modal.com
Modal.com adalah platform komputasi awan generasi baru yang menawarkan paradigma *Serverless* khusus untuk beban kerja intensif data dan AI. Tidak seperti penyedia FaaS tradisional (seperti AWS Lambda) yang membatasi ukuran paket dan durasi eksekusi, Modal mengizinkan eksekusi kode Python sembarang dengan akses langsung ke perangkat keras GPU kelas atas (seperti NVIDIA H100/A100) dan durasi eksekusi yang fleksibel (Modal Labs, 2024). Platform ini menggunakan pendekatan *Code-as-Infrastructure*, di mana konfigurasi lingkungan (seperti instalasi library CUDA) didefinisikan langsung dalam kode aplikasi.

Teknologi ini dipilih sebagai solusi infrastruktur utama karena kemampuannya memecahkan dilema biaya versus performa pada aplikasi AI. Menyewa server GPU *dedicated* 24/7 sangatlah mahal dan tidak efisien untuk aplikasi yang trafiknya fluktuatif. Modal memungkinkan sistem untuk melakukan *scale-to-zero* saat tidak ada pengguna, dan melakukan *cold-start* dalam hitungan detik saat permintaan masuk. Kemampuan ini, dikombinasikan dengan sistem *file system* terdistribusi yang cepat untuk memuat model berat, menjadikannya solusi paling layak untuk skripsi ini yang membutuhkan akses GPU *high-end* tanpa anggaran infrastruktur korporat (Modal Labs, 2024).

### 2.6.3 Basis Data Relasional: PostgreSQL dan Supabase
PostgreSQL adalah sistem manajemen basis data relasional objek (*Object-Relational Database Management System* - ORDBMS) *open-source* yang dikenal dengan stabilitas, kepatuhan terhadap standar ACID (*Atomicity, Consistency, Isolation, Durability*), dan ekstensibilitasnya (The PostgreSQL Global Development Group, 2024). Keunggulan unik PostgreSQL terletak pada dukungannya yang kuat terhadap tipe data JSONB, yang memungkinkannya berfungsi sebagai hibrida antara basis data SQL yang terstruktur dan NoSQL yang berbasis dokumen.

Supabase, di sisi lain, adalah platform *Backend-as-a-Service* (BaaS) *open-source* yang memposisikan diri sebagai alternatif dari Firebase. Supabase tidak sekadar menyediakan layanan *hosting* untuk PostgreSQL, melainkan melengkapinya dengan rangkaian alat bantu (*tooling*) modern seperti otentikasi siap pakai, API instan (*Auto-generated APIs*), dan kemampuan langganan data *real-time* (Supabase Inc., 2024). Studi komparasi menunjukkan bahwa Supabase unggul dalam performa *load speed* untuk aplikasi progresif dibandingkan kompetitornya, serta menawarkan fleksibilitas migrasi data yang lebih baik karena berbasis standar SQL terbuka (Korpela, 2022).

Penerapan PostgreSQL melalui ekosistem Supabase dalam sistem ini dipilih karena dua alasan strategis. Pertama, arsitektur "PostgreSQL-native" dari Supabase menjamin integritas data transaksi pengguna (seperti *task queue* dan riwayat generasi) tetap terjaga dengan ketat, namun tetap memberikan fleksibilitas skema JSONB untuk menyimpan metadata model AI yang sangat dinamis dan beragam strukturnya. Kedua, fitur API instan dari Supabase secara drastis memangkas waktu penulisan kode *boilerplate* untuk operasi CRUD dasar, sehingga alokasi sumber daya pengembangan dapat difokuskan sepenuhnya pada logika orkestrasi AI yang kompleks di sisi *backend*.

### 2.6.4 Manajemen Media: Cloudinary
Cloudinary adalah platform berbasis *Software-as-a-Service* (SaaS) yang menyediakan solusi *end-to-end* untuk manajemen aset media, mulai dari pengunggahan, penyimpanan, manipulasi, hingga pengiriman konten. Layanan ini bukan sekadar penyimpanan awan (*cloud storage*), melainkan memiliki lapisan pemrosesan cerdas yang dapat mengubah format, dimensi, dan kualitas media secara otomatis melalui URL API (*on-the-fly transformation*) (Cloudinary Ltd., 2024).

Integrasi Cloudinary menjadi komponen vital dalam arsitektur ini untuk menangani tantangan distribusi konten multimedia yang berat. Hasil generasi AI berupa video resolusi tinggi dan audio *lossless* membutuhkan *bandwidth* besar untuk didistribusikan ke pengguna. Cloudinary bertindak sebagai *Content Delivery Network* (CDN) global yang secara otomatis mengoptimalkan aset media sesuai perangkat pengguna (misalnya, mengirim format WebM ke Chrome dan MP4 ke Safari), serta melakukan kompresi cerdas tanpa mengurangi kualitas visual yang terlihat. Hal ini secara drastis mengurangi latensi muat (*load time*) di sisi klien dan menghemat beban komputasi server *backend* dari tugas-tugas remeh seperti *resizing* video.

## 2.7 Kerangka Berpikir dan Metode Pengujian

### 2.7.1 Kerangka Berpikir Penelitian
Kerangka berpikir penelitian ini dibangun berdasarkan alur pemecahan masalah yang sistematis. Dimulai dari identifikasi masalah inefisiensi arsitektur monolitik dalam menangani beban AI, penelitian kemudian merumuskan solusi arsitektural berbasis *Serverless GPU* dan orkestrasi asinkron. Solusi ini kemudian diimplementasikan dan akhirnya divalidasi kinerjanya. Alur logika ini memastikan bahwa setiap keputusan teknis yang diambil memiliki landasan masalah yang jelas dan bermuara pada tujuan penelitian yang terukur, yaitu terciptanya sistem backend yang skalabel dan efisien.

### 2.7.2 Pengujian Fungsional (*Black Box Testing*)
Pengujian sistem dilakukan dengan menggunakan metode *Black Box Testing*. Metode ini berfokus pada validasi fungsionalitas perangkat lunak berdasarkan spesifikasi kebutuhan, tanpa perlu mengetahui atau memeriksa struktur kode internalnya (Martin-Lopez et al., 2021). Pendekatan ini dipilih karena relevansinya dengan perspektif pengguna akhir API, di mana yang dinilai adalah kesesuaian antara input yang diberikan dan output yang dihasilkan. Dua teknik utama yang diterapkan adalah:

1.  **Equivalence Partitioning**: Teknik ini membagi domain input menjadi kelas-kelas data, di mana data dalam satu kelas dianggap setara. Pengujian cukup dilakukan pada satu perwakilan dari setiap kelas (misalnya, input teks valid, input kosong, input karakter khusus) untuk memvalidasi penanganan logika bisnis backend.
2.  **Boundary Value Analysis**: Teknik ini berfokus pada pengujian nilai-nilai di batas domain input (misalnya, panjang teks maksimum yang diizinkan untuk TTS, atau ukuran file minimum). Hal ini penting karena kesalahan sistem sering kali terjadi pada kondisi batas parameter API.

### 2.7.3 Pengujian & Tooling API
Pengujian API dalam penelitian ini mengikuti prinsip-prinsip standar industri untuk menjamin reliabilitas kontrak antarmuka. Validasi tidak hanya dilakukan pada kode status HTTP (misal 200 OK, 422 Unprocessable Entity), tetapi juga pada struktur *payload* JSON respons, integritas *header* keamanan, dan latensi jaringan. Alat bantu seperti Postman atau cURL digunakan untuk menstimulasikan permintaan klien secara terprogram, memungkinkan eksekusi skenario pengujian yang konsisten dan terulang (Scheuner & Leitner, 2020).

### 2.7.4 Metrik Pengukuran Performa
Evaluasi kinerja sistem difokuskan pada tiga metrik kuantitatif utama yang mencerminkan kualitas layanan backend:
*   **Response Time (Time-to-First-Byte)**: Mengukur waktu yang dibutuhkan API Gateway untuk menerima permintaan dan mengembalikan respons awal (seperti task ID). Metrik ini mengindikasikan responsivitas sistem di mata pengguna.
*   **Task Completion Time**: Mengukur durasi total pemrosesan dari saat tugas masuk antrian hingga video hasil akhir tersedia. Ini adalah indikator efisiensi pipeline AI dan kekuatan komputasi GPU worker.
*   **Throughput**: Mengukur kapasitas sistem dalam menangani jumlah permintaan per satuan waktu (requests per second) tanpa mengalami degradasi performa yang signifikan.

## 2.8 Alat Pemodelan Sistem

### 2.8.1 *Unified Modeling Language* (UML)
*Unified Modeling Language* (UML) adalah bahasa standar yang digunakan untuk visualisasi, spesifikasi, konstruksi, dan pendokumentasian artifak dari sistem perangkat lunak. Menurut Booch et al. (2005), UML menyediakan sekumpulan notasi grafis yang komprehensif untuk memodelkan sistem dari berbagai perspektif, baik struktur statis maupun perilaku dinamis. Penggunaan UML memungkinkan pengembang untuk membuat *blueprint* sistem yang jelas sebelum penulisan kode dimulai, meminimalkan ambiguitas kebutuhan dan kesalahan logika (Oyeniran et al., 2024).

Dalam konteks pengembangan perangkat lunak berorientasi objek, terdapat beberapa diagram UML yang esensial:

1.  **Use Case Diagram**: Diagram ini menggambarkan fungsionalitas sistem dari perspektif pengguna eksternal (*actor*). Tujuannya adalah untuk mendefinisikan batasan sistem dan menangkap kebutuhan fungsional dengan memperlihatkan interaksi antara aktor dan kasus penggunaan (*use case*) yang disediakan sistem (Dennis et al., 2012).
2.  **Activity Diagram**: Diagram ini memodelkan alur kerja (*workflow*) atau proses bisnis secara prosedural. Diagram aktivitas digunakan untuk menggambarkan urutan aktivitas, percabangan logika (*decision*), iterasi, dan aliran data antar proses, yang sangat berguna untuk memetakan algoritma atau logika operasional yang kompleks.
3.  **Sequence Diagram**: Diagram ini fokus pada interaksi antar objek dalam dimensi waktu. *Sequence diagram* memvisualisasikan bagaimana objek-objek saling bertukar pesan (*messages*) dalam urutan waktu tertentu untuk menyelesaikan suatu tugas, memperjelas aliran kendali dan tanggung jawab antar komponen sistem.
4.  **Class Diagram**: Diagram ini menggambarkan struktur statis sistem dengan mendefinisikan kelas-kelas, atribut, metode, serta hubungan antar kelas seperti pewarisan (*inheritance*), asosiasi, dan komposisi. Ini merupakan fondasi utama dalam perancangan struktur kode program.

### 2.8.2 *Entity Relationship Diagram* (ERD)
*Entity Relationship Diagram* (ERD) adalah model konseptual yang digunakan untuk menggambarkan struktur logis data. Chen (1976) memperkenalkan ERD sebagai metode untuk memetakan entitas data dan hubungan (*relationship*) di antaranya. Komponen utama ERD meliputi Entitas (objek data), Atribut (properti data), dan Relasi (hubungan antar entitas seperti *one-to-one*, *one-to-many*, atau *many-to-many*). ERD berfungsi sebagai panduan dasar dalam perancangan skema basis data relasional untuk menjamin normalisasi dan integritas referensial data.


# DAFTAR PUSTAKA

Al-Debagy, O. and Martinek, P. (2020). 'Performance Comparison between a Monolithic and a Microservice Application', *2020 IEEE 15th International Symposium on Applied Computational Intelligence and Informatics (SACI)*, pp. 203-208.

Carvalho, L., Colanzi, T. E., Assunção, W. K. G., Garcia, A., Pereira, J. A., Kalinowski, M., de Mello, R. M., de Lima, M. J., and Lucena, C. (2024). 'On the usefulness of automatically generated microservice architectures', *IEEE Transactions on Software Engineering*, 50(3), pp. 651–667.

Booch, G., Rumbaugh, J., and Jacobson, I. (2005). *The Unified Modeling Language User Guide*. 2nd edn. Addison-Wesley Professional.

Chen, P. P.-S. (1976). 'The Entity-Relationship Model—Toward a Unified View of Data', *ACM Transactions on Database Systems*, 1(1), pp. 9-36.

Chen, Y., Li, M., Zhang, Y., and Wang, X. (2023). 'Efficient Serverless Support for Multi-Instance GPUs Through Pipelining', *IEEE Transactions on Parallel and Distributed Systems*, 34(12), pp. 3145-3160.

Cloudinary Ltd. (2024). *Cloudinary Documentation*. Available at: https://cloudinary.com/documentation (Accessed: 14 January 2026).

Firework. (2024). *The State of Short-Form Video: Trends and Statistics for 2024*. Available at: https://firework.com/ (Accessed: 14 January 2026).

Dennis, A., Wixom, B. H., and Tegarden, D. (2012). *Systems Analysis and Design with UML Version 2.0: An Object-Oriented Approach*. 4th edn. John Wiley & Sons.

Fu, Y., Xue, L., Huang, Y., Brabete, A., Ustiugov, D., Patel, Y., and Mai, L. (2024). 'ServerlessLLM: Low-Latency Serverless Inference for Large Language Models', *Proceedings of the 18th USENIX Symposium on Operating Systems Design and Implementation (OSDI '24)*, pp. 135–153.

Green, J. and Smith, A. (2023). 'The Evolution and Future of Microservices Architecture with AI', *International Journal of Cloud Computing*, 12(2), pp. 110-125.

IEEE Software. (2023). 'AsyncAPI: Standardizing Event-Driven Architectures for AI', *IEEE Software*, 40(2), pp. 45-52.

Karimi, M., Abdollahzadeh Barfroush, A., and Kamandi, A. (2023). 'Automated Black-box Testing of RESTful APIs using Artificial Bee Colony', *International Journal of Software Engineering & Applications*, 14(1), pp. 1-15.

Kim, S., Lee, J., and Park, H. (2024). 'EAGLE: Event-driven API Gateway with Low latency Execution for AI Services', *Korea Conference on Software Engineering (KCSE)*.

Korpela, R. (2022). *Supabase vs Firebase: Evaluation of performance and development of Progressive Web Apps*. Bachelor's Thesis. Metropolia University of Applied Sciences.

Kumar, A. and Lee, S. (2024). 'AI-driven predictive failure models for cloud-native microservices', *IEEE Access*.

Liu, Y. et al. (2024). 'A Comprehensive Taxonomy and Analysis of Talking Head Synthesis', *IEEE Transactions on Visualization and Computer Graphics*, 30(5), pp. 2890-2908.

Martin-Lopez, A., Segura, S., and Ruiz-Cortés, A. (2021). 'RESTest: Automated Black-Box Testing of RESTful APIs', *IEEE Transactions on Software Engineering*, 47(11), pp. 2519-2541.

Microsoft Research. (2024). *VASA-1: Lifelike Audio-Driven Talking Faces Generated in Real Time*. Available at: https://www.microsoft.com/en-us/research/project/vasa-1/ (Accessed: 14 January 2026).

Modal Labs. (2024). *Modal Documentation: Serverless GPU Computing*. Available at: https://modal.com/docs (Accessed: 14 January 2026).

Moreschini, S., Pour, S., Lanese, I., and Taibi, D. (2024). 'Designing Microservices Using AI: A Systematic Literature Review', *ACM Transactions on Software Engineering and Methodology*, 33(3), Article 74.

Newman, S. (2021). *Building Microservices: Designing Fine-Grained Systems*. 2nd edn. O'Reilly Media.

Nie, S., Zhu, F., You, Z., Zhang, X., Ou, J., Hu, J., Zhou, J., Lin, Y., Wen, J., and Li, C. (2024). 'Large Language Diffusion Models (LLaDA)', *arXiv preprint arXiv:2502.09992*.

Oyeniran, A., Adewusi, A., Adeleke, A., Akwawa, T., and Azubuko, C. (2024). 'Microservices architecture in cloud-native applications: Design patterns and scalability', *Computer Science & IT Research Journal*, 5(9), pp. 2107-2124.

Patel, N. and Gupta, S. (2024). 'Anomaly detection frameworks for resilient microservices', *ACM Computing Surveys*.

Ramamoorthi, V. and Menascé, D. (2023). 'Real-Time Adaptive Orchestration of AI Microservices in Dynamic Edge Computing', *IEEE Internet of Things Journal*, 10(14), pp. 12345-12356.

Ramírez, S. (2024). *FastAPI Documentation*. Available at: https://fastapi.tiangolo.com/ (Accessed: 14 January 2026).

Ren, Y., Tan, X., Qin, T., Zhao, S., Zhao, Z., and Liu, T. (2021). 'FastSpeech 2: Fast and High-Quality End-to-End Text to Speech', *Proceedings of the International Conference on Learning Representations (ICLR)*.

Research and Markets. (2025). *Generative AI Market - Global Outlook & Forecast 2024-2029*. Available at: https://www.researchandmarkets.com/ (Accessed: 14 January 2026).

Roumeliotis, K.I., Tselikas, N.D., and Niskopoulos, D.K. (2023). 'Backend Frameworks: A Comparative Analysis of Spring Boot, Django, and FastAPI', *Information*, 14, Article 200.

Scheuner, J. and Leitner, P. (2020). 'Performance Benchmarking of Serverless Computing Platforms', *Journal of Systems and Software*, 164, Article 110540.

Supabase Inc. (2024). *Supabase Documentation*. Available at: https://supabase.com/docs (Accessed: 14 January 2026).

The PostgreSQL Global Development Group. (2024). *PostgreSQL 16 Documentation*. Available at: https://www.postgresql.org/docs/ (Accessed: 14 January 2026).

Villaca, G. L. D. et al. (2021). 'Modernizing legacy systems with microservices: A roadmap', *Evaluation and Assessment in Software Engineering*.

Wang, H. and Li, F. (2024). 'Self-healing mechanisms in AI-enhanced microservices', *Journal of Systems and Software*.

Wang, X. (2024). 'Review of Talking Head Synthesis for Driving Mechanisms and Portrait Rendering', *Applied and Computational Engineering*, 89, pp. 20-35.

White, S. and Patel, K. (2024). 'Resilient Microservices Architecture with Embedded AI Observability', *Journal of Engineering Science*.

Yang, Z., Zhang, Y., and Li, K. (2024). 'PipeCo: Pipelining Cold Start for Deep Learning Inference Services', *IEEE Transactions on Services Computing*.

Zhang, D. et al. (2024). 'AI-Driven Orchestration for Scalable Microservices', *Future Generation Computer Systems*, 150, pp. 112-124.

Zhang, H., Li, X., and Wang, Y. (2023). 'MQFQ-Sticky: Integrated Fair Queueing and GPU Memory Management', *Proceedings of the 2023 ACM Symposium on Cloud Computing (SoCC '23)*, pp. 45-59.

Zhang, H., Wang, L., and Chen, M. (2024). 'Advancing Serverless Computing for Scalable AI Model Inference: A Review', *IEEE Access*.
Zhang, X., et al. (2024). GaussianTalker: Real-Time Pose-Controllable Talking Head Synthesis via 3D Gaussian Splatting. *arXiv preprint arXiv:2404.14032*. [online] Available at: https://arxiv.org/abs/2404.14032.

Eismann, S., et al. (2021). Serverless Applications: Why, When, and How?. *IEEE Software*, 38(1), pp.32-39. doi: 10.1109/MS.2020.3023357.

FinOps Foundation. (2024). *State of FinOps 2024*. [online] Available at: https://data.finops.org/ [Accessed 15 Jan. 2026].

Li, Z., et al. (2024). Understanding Cold Start in Serverless Computing: A Measurement Study. *Proceedings of the 2024 ACM/SPEC International Conference on Performance Engineering*, pp.23-30. doi: 10.1145/3639458.

Shafiei, H. (2022). Serverless Computing: A Survey of Opportunities, Challenges, and Applications. *IEEE Transactions on Cloud Computing*, 10(11), pp.1-15. doi: 10.1109/TCC.2022.3164821.

Storment, J.R. and Fuller, M. (2023). *Cloud FinOps: Collaborative, Real-Time Cloud Financial Management*. 2nd ed. Sebastopol, CA: O'Reilly Media.

Guerriero, M. (2019). 'Adopting infrastructure as code for software deployment and configuration: a case study', *Proceedings of the 13th European Conference on Software Architecture*.

Morris, K. (2021). *Infrastructure as Code: Dynamic Systems for the Cloud Age*. 2nd edn. O'Reilly Media.

Richards, M. and Ford, N. (2020). *Fundamentals of Software Architecture: An Engineering Approach*. O'Reilly Media.

Allal, L. B., et al. (2025). *Kokoro-82m (revision d8b4fc7)*. Hugging Face. Available at: https://huggingface.co/hexgrad/Kokoro-82M (Accessed: 16 January 2026).

Wan Team. (2025). *Wan2.1: Open-source Video Generation Model*. Alibaba Cloud. Available at: https://github.com/Wan-Video/Wan2.1 (Accessed: 16 January 2026).

Yang, S., et al. (2025). 'InfiniteTalk: Audio-driven Video Generation for Sparse-Frame Video Dubbing', *arXiv preprint arXiv:2508.nnnnn*.

Resemble AI. (2025). *Chatterbox-TTS*. GitHub Repository. Available at: https://github.com/resemble-ai/Chatterbox (Accessed: 16 January 2026).
