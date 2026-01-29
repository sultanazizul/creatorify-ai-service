# BAB III
METODOLOGI PENELITIAN

## 3.1 Waktu dan Tempat Penelitian

Penelitian ini disusun dan dilaksanakan di lingkungan akademik Universitas Udayana, tepatnya di Kampus Bukit Jimbaran, Fakultas Teknik, Program Studi Teknologi Informasi. Pemilihan lokasi ini didasarkan pada ketersediaan fasilitas penunjang akademik serta kemudahan akses terhadap literatur digital dan repositori jurnal yang relevan untuk mendukung studi teoritis. Rangkaian kegiatan penelitian dijadwalkan berlangsung selama periode sepuluh bulan, terhitung mulai dari bulan September 2024 hingga Juni 2025. Periode tersebut dialokasikan untuk menyelesaikan seluruh tahapan pengembangan sistem secara komprehensif, mulai dari studi literatur mendalam terkait teknologi *serverless* dan AI generatif, analisis kebutuhan sistem, perancangan arsitektur *backend* berbasis *microservices*, implementasi kode (*coding*), *deployment* ke infrastruktur *cloud* Modal.com, hingga tahap akhir berupa pengujian sistem (*testing*) dan evaluasi kinerja.

## 3.2 Jenis dan Pendekatan Penelitian

Jenis penelitian yang diterapkan dalam studi ini adalah **Penelitian Terapan (*Applied Research*)**. Menurut Sugiyono (2019), penelitian terapan adalah penelitian yang bertujuan untuk menerapkan, menguji, dan mengevaluasi kemampuan suatu teori dalam memecahkan masalah-masalah praktis. Sejalan dengan definisi tersebut, studi ini berfokus pada penerapan teori rekayasa perangkat lunak dan komputasi awan (*cloud computing*) untuk menyelesaikan permasalahan inefisiensi arsitektur *backend* konvensional. Tujuannya adalah membangun solusi nyata berupa sistem *backend* yang mampu mengorkestrasi model AI (seperti Wan2.1, InfiniteTalk, Kokoro, dan Chatterbox) secara efisien dan skalabel.

Pendekatan yang digunakan dalam penelitian ini bersifat **Deskriptif-Eksploratif** dengan komponen **Eksperimental**. Sifat *Deskriptif* digunakan untuk menjabarkan secara rinci spesifikasi arsitektur *serverless GPU* yang dirancang, termasuk mekanisme manajemen *container lifecycle* dan *volume* penyimpanan. Sifat *Eksploratif* diterapkan dalam tahap investigasi mendalam terhadap kapabilitas teknis *framework* Modal.com serta konfigurasi optimal untuk model AI yang dipilih, guna menemukan keseimbangan terbaik antara performa dan biaya. Selanjutnya, komponen *Eksperimental* dijalankan pada fase validasi sistem, di mana dilakukan pengukuran kuantitatif terhadap metrik kinerja seperti latensi respons API (*response time*) dan *throughput* pemrosesan video, untuk membuktikan efektivitas solusi yang diusulkan dibandingkan dengan pendekatan tradisional. Logika penelitian ini bergerak secara linear dari identifikasi masalah, analisis solusi, perancangan, implementasi, hingga validasi empiris.

## 3.3 Alur Penelitian

Pelaksanaan penelitian ini mengikuti kerangka kerja sistematis yang dirancang untuk menjamin keruntutan logis dan validitas ilmiah. Alur penelitian digambarkan dalam bentuk diagram alur (*flowchart*) pada Gambar 3.1 untuk memvisualisasikan urutan langkah-langkah serta mekanisme umpan balik (*feedback loop*) yang diterapkan.

![Diagram Alir Tahapan Penelitian](file:///Users/macbaru/.gemini/antigravity/brain/43ec4672-1a4a-48e4-9efd-4673ffed5f06/diagram_alur_penelitian.png)

*Gambar 3.1 Diagram Alir Tahapan Penelitian*

Berdasarkan Gambar 3.1, tahapan penelitian dimulai dengan **Identifikasi Masalah** untuk merumuskan tantangan utama, yaitu *latency* dan biaya infrastruktur AI. Tahap selanjutnya adalah **Studi Literatur & Penentuan Solusi** untuk menetapkan landasan teori dan pemilihan teknologi *serverless GPU*. **Eksplorasi Teknis** dilakukan untuk menguji kelayakan model AI (Wan2.1 dan Kokoro-82M) pada lingkungan *serverless*. Setelah itu, tahap **Perancangan Sistem** mencakup desain arsitektur *microservices* dan basis data. **Implementasi Backend** merupakan tahapan penerjemahan desain menjadi kode program. Proses diakhiri dengan **Pengujian & Evaluasi**, dengan mekanisme umpan balik (*looping*) kembali ke tahap revisi jika hasil pengujian dinilai kurang memuaskan, atau berlanjut ke tahap **Selesai** jika sistem telah berjalan dengan baik. 

## 3.4 Alat dan Bahan Penelitian

Pemilihan infrastruktur perangkat keras dan lingkungan perangkat lunak merupakan faktor determinan dalam keberhasilan pengembangan sistem berbasis kecerdasan buatan yang menuntut komputasi intensif. Subbab ini menguraikan spesifikasi teknis alat dan bahan yang digunakan untuk menjamin reprodukabilitas dan kinerja optimal sistem.

### 3.4.1 Perangkat Keras

Perangkat keras (*hardware*) merupakan komponen fisik komputer yang digunakan untuk mendukung proses pengembangan sistem, mulai dari penulisan kode program, eksekusi komputasi, hingga penyimpanan data. Dalam penelitian ini, spesifikasi perangkat keras memegang peranan vital mengingat beban kerja sistem yang melibatkan pemrosesan model kecerdasan buatan (*Artificial Intelligence*) yang intensif. Kebutuhan perangkat keras dibagi menjadi dua kategori utama, yaitu lingkungan pengembangan lokal dan infrastruktur *cloud* untuk *deployment*. Berikut adalah rincian spesifikasi perangkat keras yang digunakan:

*   **Laptop Pengembang (Local Environment)**:
    Digunakan untuk penulisan kode, manajemen repositori, dan pengujian API lokal. Spesifikasi perangkat adalah sebagai berikut:
    *   Model: MacBook Pro (13-inch, 2020, Four Thunderbolt 3 ports)
    *   Processor: 2.3 GHz Quad-Core Intel Core i7
    *   RAM: 32 GB 3733 MHz LPDDR4X
    *   Graphics: Intel Iris Plus Graphics 1536 MB
    *   Storage: 1 TB SSD
    *   OS: macOS Tahoe 26.1

*   **Cloud Infrastructure (Deployment & Inference):**
    Infrastruktur *serverless* pada Modal.com menyediakan akses ke GPU *high-end* sesuai kebutuhan (*on-demand*). Spesifikasi GPU yang dipilih berdasarkan kebutuhan model adalah:
    *   **GPU Tier 1: NVIDIA H100 (80GB VRAM)**
        *Justifikasi:* GPU ini dipilih secara khusus untuk menjalankan model **Wan2.1-I2V-14B** yang menjadi *backbone* dari InfiniteTalk. Model dengan parameter 14 Miliar ini membutuhkan VRAM di atas 40GB untuk memuat bobot model dalam presisi `fp16` serta menyediakan ruang *buffer* yang cukup untuk proses inferensi video. GPU kelas konsumen seperti RTX 4090 (24GB) tidak mencukupi untuk beban kerja ini.
    *   **GPU Tier 2: NVIDIA A10G (24GB VRAM)**
        *Justifikasi:* GPU ini dialokasikan untuk model audio **Kokoro-82M** dan **Chatterbox**. Mengingat kedua model ini jauh lebih ringan dibandingkan model video, VRAM 24GB pada A10G sudah sangat memadai untuk menampung kedua model sekaligus dalam satu *container*. Pemilihan A10G didasarkan pada efisiensi biaya yang jauh lebih baik dibandingkan menggunakan H100 untuk tugas yang lebih ringan.
    *   **Storage:** Menggunakan **Modal Persistent Volume**, yaitu penyimpanan jaringan berkinerja tinggi yang dipasang (*mount*) ke *container*. Fungsinya adalah untuk menyimpan *cache* bobot model agar tidak perlu diuntuh ulang (*re-download*) setiap kali *container* baru dijalankan (mengurangi *cold-start*).

### 3.4.2 Perangkat Lunak

Perangkat lunak (*software*) adalah sekumpulan instruksi atau program komputer yang berfungsi untuk mengoperasikan perangkat keras dan menjalankan tugas-tugas tertentu. Pemilihan perangkat lunak yang tepat, termasuk bahasa pemrograman, *framework*, dan pustaka pendukung, sangat menentukan efisiensi, skalabilitas, dan kemudahan pemeliharaan sistem. Penelitian ini memanfaatkan berbagai teknologi modern yang mendukung arsitektur *microservices* dan pemrosesan asinkron. Tumpukan teknologi (*technology stack*) yang digunakan dalam implementasi *backend* meliputi:

*   **Bahasa Pemrograman**: **Python 3.10+** dipilih sebagai bahasa utama karena ekosistem *library* AI/ML yang sangat matang dan dukungan *native* dari Modal SDK.
*   **Framework**:
    *   **FastAPI**: Digunakan untuk membangun REST API karena performanya yang tinggi (asynchronous) dan kemudahan pembuatan dokumentasi otomatis.
    *   **Modal SDK**: *Library* inti untuk mendefinisikan infrastruktur *serverless*, fungsi GPU, dan orkestrasi *container* langsung dari kode Python.
*   **Database**: **PostgreSQL** yang dikelola melalui layanan **Supabase**. Layanan ini dipilih karena menyediakan fitur basis data relasional yang handal serta dukungan tipe data JSONB untuk menyimpan metadata pipeline yang kompleks.
*   **Storage & CDN**: **Cloudinary** digunakan sebagai *Media Asset Management* untuk menyimpan, mengoptimasi, dan mengirimkan hasil generasi video dan audio kepada pengguna melalui CDN global.
*   **AI Models**:
    *   **Video Generation**: Menggunakan modul **InfiniteTalk** (Talking Head Module) yang dibangun di atas *backbone* model **Wan2.1-I2V-14B**.
    *   **Audio Generation**: Menggunakan **Kokoro-82M** untuk *Text-to-Speech* (TTS) standar dan **Chatterbox** untuk fitur *Voice Cloning* dan TTS Multilingual.
*   **Tools Pendukung**: VS Code sebagai IDE utama, Git untuk kontrol versi kode, dan Postman untuk pengujian *endpoint* API.

## 3.5 Analisis Sistem

Tahap analisis sistem bertujuan untuk memahami secara mendalam kebutuhan, batasan, dan karakteristik sistem yang akan dibangun.

### 3.5.1 Analisis Masalah Sistem Konvensional

Untuk merancang solusi yang tepat, dilakukan analisis mendalam terhadap akar permasalahan pada pendekatan infrastruktur konvensional yang sering digunakan dalam pengembangan aplikasi berbasis AI. Analisis ini menggunakan bantuan **Diagram Fishbone** (Ishikawa Diagram) untuk memetakan hubungan sebab-akibat yang berkontribusi pada masalah utama, yaitu inefisiensi dan ketidakmampuan sistem untuk melakukan *scaling* secara efektif. Visualisasi analisis masalah disajikan dalam Gambar 3.2 berikut.

![Analisis Masalah Infrastruktur Backend Generative AI](file:///Users/macbaru/.gemini/antigravity/brain/43ec4672-1a4a-48e4-9efd-4673ffed5f06/diagram_fishbone.png)

*Gambar 3.2 Analisis Masalah Infrastruktur Generative AI*

Mengacu pada Gambar 3.2, akar permasalahan inefisiensi sistem dapat dipetakan ke dalam interaksi antar aspek teknis dan manajerial. Dari sisi **teknologi dan infrastruktur**, ketergantungan pada arsitektur monolitik dan alokasi server statis (VPS) menciptakan hambatan kinerja, seperti tingginya *latency* saat *cold start* dan sulitnya mendistribusikan model AI berukuran besar. Kondisi teknis ini berkorelasi langsung dengan pembengkakan **biaya** operasional akibat pembayaran sumber daya yang tidak terpakai (*idle cost*) dan *overprovisioning*. Lebih jauh, rigiditas infrastruktur tersebut membatasi **skalabilitas** sistem dalam menangani lonjakan beban kerja (*workload fluctuation*), sementara kompleksitas **manajemen** manual meningkatkan risiko kegagalan operasional (*human error*). Kombinasi faktor-faktor ini menegaskan bahwa pendekatan konvensional tidak lagi memadai untuk mendukung kebutuhan komputasi generatif yang dinamis.

Sebagai solusi komprehensif atas permasalahan multidimensi tersebut, penelitian ini mengusulkan penerapan arsitektur **Serverless GPU** yang mampu menangani beban kerja asinkron secara elastis dan hemat biaya.

### 3.5.2 Analisis Kebutuhan Sistem

Analisis kebutuhan sistem merupakan tahap krusial untuk mendefinisikan spesifikasi teknis yang harus dipenuhi oleh perangkat lunak. Kebutuhan ini diklasifikasikan menjadi dua kategori utama, yaitu kebutuhan fungsional dan non-fungsional.

#### 3.5.2.1 Kebutuhan Fungsional (*Functional Requirements*)

Kebutuhan fungsional mendefinisikan kemampuan atau fitur spesifik yang harus disediakan oleh sistem. Dalam konteks sistem *backend* generatif ini, kebutuhan fungsional mencakup kapabilitas API dalam menangani permintaan pembuatan video dan audio, manajemen antrian, serta distribusi aset media. Rincian kebutuhan fungsional sistem disajikan dalam Tabel 3.1 berikut:

| Kebutuhan Fungsional | Deskripsi |
| :--- | :--- |
| **Generasi Video Avatar** | Sistem mampu menerima input gambar wajah dan audio, lalu menghasilkan video *talking head* yang tersinkronisasi. |
| **Generasi Suara AI** | Sistem menyediakan layanan audio komprehensif menggunakan model **Kokoro-82M** untuk *Text-to-Speech* (TTS) multibahasa yang cepat, serta **Chatterbox** untuk kapabilitas *Voice Cloning* (meniru suara) dan *Voice Conversion* (modifikasi suara). |
| **Manajemen Antrian Asinkron** | Sistem harus dapat menampung permintaan dalam antrian (*task queue*) dan memprosesnya di latar belakang tanpa memblokir respon API. |
| **Monitoring Status Tugas** | Sistem menyediakan endpoint untuk memeriksa status terkini dari tugas yang sedang berjalan (*pending, processing, completed, failed*). |
| **Manajemen Output Media** | Sistem secara otomatis mengunggah hasil generasi ke Cloudinary dan menyediakan URL publik untuk akses aset. |

#### 3.5.2.2 Kebutuhan Non-Fungsional (*Non-Functional Requirements*)

Kebutuhan non-fungsional berkaitan dengan batasan kualitas (*quality constraints*) yang membatasi bagaimana sistem harus bekerja. Aspek ini mencakup performa dan skalabilitas sistem yang sangat vital untuk lingkungan produksi berbasis AI. Rincian kebutuhan non-fungsional sistem dijelaskan pada Tabel 3.2 berikut:

| Parameter | Deskripsi Kebutuhan |
| :--- | :--- |
| **Scalability** | Sistem harus mampu melakukan *auto-scaling* dari 0 ke N container secara otomatis berdasarkan volume permintaan yang masuk. |
| **Performance (Cold Start)** | Waktu inisialisasi awal (*cold-start*) container GPU harus dioptimalkan berada di bawah 30 detik menggunakan *persistent volume*. |
| **Response Time** | API Gateway harus memberikan respon awal (*acknowledgment*) dalam waktu kurang dari 200ms setelah permintaan diterima. |
| **Interoperability** | Pertukaran data harus menggunakan format JSON standar yang kompatibel dengan berbagai platform klien (Web/Mobile). |

Berdasarkan Tabel 3.2, prioritas non-fungsional utama adalah efisiensi operasional (*performance*) dan skalabilitas, mengingat karakteristik beban kerja AI yang bersifat fluktuatif dan intensif sumber daya.

### 3.5.3 Gambaran Arsitektur Sistem Usulan

Gambaran arsitektur sistem usulan mempresentasikan desain tingkat tinggi dari solusi yang dikembangkan untuk menjawab permasalahan dan kebutuhan yang telah dianalisis sebelumnya. Sistem backend usulan (yang dalam lingkungan pengembangan diberi nama **Creatorify**) dibangun dengan pendekatan arsitektur terpusat yang memanfaatkan teknologi *API Gateway* sebagai jembatan komunikasi utama. Visualisasi arsitektur umum sistem ditunjukkan pada Gambar 3.3.

![Gambaran Umum Arsitektur Sistem](file:///Users/macbaru/.gemini/antigravity/brain/43ec4672-1a4a-48e4-9efd-4673ffed5f06/gambaran_umum_sistem.png)

*Gambar 3.3 Gambaran Umum Arsitektur Sistem Backend*

Sebagaimana terlihat pada Gambar 3.3, sistem ini mengadopsi pola arsitektur *client-server* modern yang memisahkan tanggung jawab antara pengelolaan data, logika bisnis, dan komputasi intensif. Klien memulai interaksi dengan mengirimkan permintaan (*request*) berbasis JSON ke *Backend API* yang berfungsi sebagai *API Gateway*. Permintaan tersebut kemudian didistribusikan ke layanan terkait, baik itu operasi baca-tulis ke basis data Supabase PostgreSQL, manajemen berkas ke penyimpanan Cloudinary, maupun pemrosesan kecerdasan buatan (*AI Model Service*) yang berjalan di infrastruktur GPU. Hasil pemrosesan, baik berupa metadata maupun media (video/audio) yang telah digenerasi, kemudian dikembalikan ke klien melalui respons yang terstruktur. Pendekatan ini memastikan skalabilitas dan isolasi proses yang efisien antar komponen sistem.

## 3.6 Perancangan Arsitektur Sistem (High-Level Design)

Perancangan tingkat tinggi ini memberikan pandangan makro terhadap struktur sistem dan interaksi antar komponen utamanya.

### 3.6.1 Arsitektur Topologi Cloud (Deployment Diagram)

Diagram deployment menggambarkan tata letak fisik perangkat keras dan pemetaan komponen perangkat lunak pada infrastruktur tersebut. Untuk sistem backend ini, arsitektur *deployment* dirancang sepenuhnya berbasis *cloud* (*cloud-native*) dengan memanfaatkan paradigma *serverless*. Rancangan topologi fisik sistem disajikan dalam Gambar 3.4.

![Arsitektur Topologi Cloud Backend Sistem](file:///Users/macbaru/.gemini/antigravity/brain/43ec4672-1a4a-48e4-9efd-4673ffed5f06/diagram_deployment_final.jpg)

*Gambar 3.4 Arsitektur Topologi Cloud Backend Sistem*

Berdasarkan Gambar 3.4, arsitektur sistem terdiri dari empat komponen utama yang saling berinteraksi:

1.  **Client Tier**: Sisi klien (aplikasi *web* atau *mobile*) yang bertindak sebagai inisiator permintaan. Klien berkomunikasi dengan *backend* melalui protokol HTTP/HTTPS yang aman.
2.  **API Gateway Layer**: Lapisan ini diimplementasikan menggunakan **FastAPI** yang berjalan di atas instans CPU ringan pada platform Modal.com. Fungsinya adalah sebagai pintu gerbang tunggal yang menangani validasi permintaan, otentikasi pengguna, dan merutekan tugas (*routing*) ke *worker* yang sesuai.
3.  **Compute Layer (Modal.com Cloud)**: Lapisan komputasi inti yang bersifat *serverless* dan elastis. Terdiri dari *container* GPU yang terisolasi untuk tugas spesifik:
    *   **InfiniteTalk *Worker***: Menggunakan GPU **NVIDIA H100 (80GB VRAM)** untuk menjalankan model generasi video Wan2.1 yang membutuhkan memori besar.
    *   **Kokoro *Worker***: Menggunakan GPU **NVIDIA A10G (24GB VRAM)** untuk layanan *Text-to-Speech* yang cepat.
    *   **Chatterbox *Worker***: Menggunakan GPU **NVIDIA A10G** untuk layanan *Voice Cloning*.
    Mekanisme `Spawn Task (Async)` memungkinkan API Gateway untuk memicu *worker* ini secara asinkron tanpa memblokir koneksi klien.
    *   **Persistent Volume**: Penyimpanan blok bersama yang dipasang ke *container* untuk menyimpan bobot model (*cache model weights*), memastikan waktu pemuatan model (*cold start*) yang minimal.
4.  **External Services**: Layanan pihak ketiga yang dikelola penuh (*managed services*):
    *   **Supabase (PostgreSQL)**: Menyimpan data relasional persisten seperti profil pengguna, metadata proyek, dan status tugas.
    *   **Cloudinary**: Berfungsi sebagai *Content Delivery Network* (CDN) dan *Object Storage* untuk menyimpan dan menyajikan aset media (video, audio, gambar) yang dihasilkan oleh sistem.

Integrasi komponen-komponen ini membentuk ekosistem yang terkelola secara otomatis, di mana sumber daya komputasi (GPU) hanya diaktifkan saat ada permintaan (*on-demand*), memberikan efisiensi biaya yang signifikan dibandingkan arsitektur server tradisional.

### 3.6.2 Mekanisme Serverless & GPU Orchestration

Salah satu inovasi utama dalam penelitian ini adalah penggunaan mekanisme orkestrasi *serverless* dari Modal. Detail mekanisme kerja sistem adalah sebagai berikut:

1.  **Mekanisme `.spawn()`**: Fungsi ini memungkinkan pemisahan total antara proses HTTP yang cepat dengan proses GPU yang berat. Saat API menerima *request*, ia memanggil fungsi `.spawn()` yang secara asinkron "melahirkan" proses baru di *container* GPU terpisah dan segera mengembalikan respon "Pending" ke *user*. API tidak perlu menunggu inferensi selesai.
2.  **Lifecycle *Container***:
    *   *Start*: Container diinisialisasi hanya saat ada *request* masuk (atau disiapkan *warm pool* jika diperlukan).
    *   *Load Model*: Container memuat bobot model langsung dari *Persistent Volume* lokal (kecepatan disk tinggi), menghindari unduhan dari internet.
    *   *Inference*: Proses generasi video/audio berjalan.
    *   *Shutdown*: Setelah tugas selesai dan waktu *idle* terlampaui, container otomatis dimatikan (*scale-to-zero*) untuk menghentikan biaya.
3.  **Manajemen Volume**: *Persistent volume* digunakan sebagai *shared storage* yang persisten antar *lifecycle container*. Ini menyimpan file model Wan2.1 yang besar, memastikan bahwa *cold-start* hanya terjadi sekali saat volume pertama kali diisi, bukan setiap kali *request*.

## 3.7 Perancangan Perangkat Lunak (Detailed Design)

Bagian ini merinci struktur internal perangkat lunak backend, memodelkan bagaimana data mengalir dan bagaimana objek-objek dalam kode saling berinteraksi.

### 3.7.1 Diagram Konteks

Diagram Konteks digunakan untuk menggambarkan batasan sistem (*system boundary*) secara global serta memetakan interaksi antara sistem dengan entitas eksternal yang terlibat. Diagram ini menempatkan sistem sebagai satu kesatuan proses tunggal yang menerima input dari lingkungan luar dan menghasilkan output kembali ke lingkungan tersebut, tanpa merinci proses internal yang terjadi di dalamnya. Visualisasi interaksi tersebut disajikan dalam Gambar 3.5.

![Diagram Konteks Sistem Backend](file:///Users/macbaru/.gemini/antigravity/brain/43ec4672-1a4a-48e4-9efd-4673ffed5f06/diagram_context_final.png)

*Gambar 3.5 Diagram Konteks Sistem Backend*

Berdasarkan Gambar 3.5, sistem berinteraksi secara tunggal dengan entitas **Pengguna Akhir**. Alur kerja dimulai dengan aliran data masuk (*input flow*) di mana pengguna mengirimkan aset media (seperti gambar avatar dan sampel suara), data bahan baku (teks atau audio), serta serangkaian parameter konfigurasi untuk mengatur spesifikasi generasi video dan suara. Sebagai tanggapan atas masukan tersebut, sistem memproses permintaan dan menghasilkan aliran data keluar (*output flow*) yang mencakup URL untuk mengakses konten sintetik yang telah jadi (video avatar, audio TTS, hasil kloning suara), informasi status kemajuan pemrosesan, serta berbagai data referensi sistem seperti daftar avatar dan bahasa yang tersedia. Mekanisme pertukaran data dua arah ini menegaskan fungsi sistem sebagai mesin transformasi yang mengubah aset mentah pengguna menjadi konten multimedia baru.

### 3.7.2 Unified Modeling Language (UML)

### 3.7.2 Unified Modeling Language (UML)

Berdasarkan landasan teori yang telah dipaparkan pada Bab II, perancangan sistem ini menggunakan diagram UML untuk memvisualisasikan struktur dan perilaku *backend* secara teknis. Diagram-diagram berikut ini disusun untuk memberikan gambaran presisi mengenai arsitektur kode dan alur data sistem:

#### 3.7.2.1 Use Case Diagram
Use Case Diagram memodelkan fungsionalitas sistem backend yang tersedia bagi aktor utama, yaitu **Pengguna Akhir**. Gambar 3.6 menggambarkan tujuh kasus penggunaan (*use cases*) yang merepresentasikan kapabilitas sistem secara menyeluruh.

![Use Case Diagram Sistem Backend](file:///Users/macbaru/.gemini/antigravity/brain/43ec4672-1a4a-48e4-9efd-4673ffed5f06/diagram_usecase_final.png)

*Gambar 3.6 Use Case Diagram Sistem Backend*

Sebagaimana terlihat pada Gambar 3.6, pengguna memiliki akses ke fungsi manajemen aset, meliputi *Upload Aset Media* (Gambar/Audio), *Kelola Data Avatar* untuk mendaftarkan presenter digital, serta *Kelola Voice Library* untuk menyimpan sampel suara. Selain itu, fungsi inti AI mencakup *Generate Audio TTS* menggunakan model Kokoro, *Generate Voice Cloning* melalui layanan Chatterbox, dan *Generate Video Avatar* yang memanfaatkan model Wan2.1. Seluruh aktivitas ini dapat dipantau melalui fitur *Monitor Status Proyek*. Diagram ini menegaskan bahwa sistem dirancang sebagai platform layanan terpadu yang memfasilitasi siklus lengkap produksi konten, mulai dari input data, pemrosesan AI, hingga pemantauan hasil.

#### 3.7.2.2 Activity Diagram
Diagram aktivitas digunakan untuk memodelkan alur kerja prosedural dari sistem, menggambarkan urutan langkah logis yang terjadi selama pemrosesan permintaan. Pada sistem *backend* ini, terdapat tiga alur utama yang berjalan secara paralel dan asinkron, sebagaimana divisualisasikan pada Gambar 3.7.

![Activity Diagram Sistem Backend](file:///Users/macbaru/.gemini/antigravity/brain/43ec4672-1a4a-48e4-9efd-4673ffed5f06/diagram_activity_final.jpg)

*Gambar 3.7 Activity Diagram Sistem Backend*

Mengacu pada Gambar 3.7, alur **Video Generation** dimulai ketika sistem menerima permintaan berisi gambar dan audio. Setelah validasi input sukses, tugas akan antur (*queued*) ke dalam basis data dan dikirim ke *GPU Worker* secara asinkron. Proses komputasi berat, mulai dari pemuatan model Wan2.1, pengunduhan aset, sinkronisasi bibir (*lip-sync*), hingga *rendering frame-by-frame*, ditangani sepenuhnya oleh *worker* yang terisolasi. Sementara itu, alur **Audio Generation** memiliki percabangan logika berdasarkan tipe permintaan. Untuk *Text-to-Speech* (TTS), sistem memvalidasi teks dan parameter bahasa sebelum meneruskannya ke *Kokoro Worker* untuk sintesis gelombang suara. Sedangkan untuk *Voice Cloning*, sistem akan menangani ekstraksi karakteristik suara (*timbre extraction*) melalui *Chatterbox Worker* jika sampel suara tersedia. Seluruh hasil keluaran dari ketiga proses ini secara otomatis diunggah ke penyimpanan awan (Cloudinary) dan status terakhirnya diperbarui ke basis data agar dapat diakses oleh pengguna.

#### 3.7.2.3 Sequence Diagram
Diagram urutan memperjelas interaksi antar objek dalam sistem berdasarkan urutan waktu. Gambar 3.8 memvisualisasikan dua skenario utama dalam proses generasi konten AI.

![Sequence Diagram Sistem Backend](file:///Users/macbaru/.gemini/antigravity/brain/43ec4672-1a4a-48e4-9efd-4673ffed5f06/diagram_sequence_final.png)

*Gambar 3.8 Sequence Diagram Sistem Backend*

Berdasarkan Gambar 3.8, **Skenario A (Generate Audio)** menggambarkan alur ketika *Front-end* mengirimkan permintaan sintesis suara ke *API Gateway*. Setelah validasi berhasil, tugas diproses secara asinkron oleh *GPU Worker* yang memuat model Kokoro untuk menghasilkan fail audio, menyimpannya ke *Cloudinary*, dan memperbarui status di basis data agar dapat diambil kembali oleh klien melalui mekanisme *polling*. Selanjutnya, **Skenario B (Generate Video)** menunjukkan proses yang lebih kompleks di mana *API Gateway* menerima permintaan video yang menyertakan URL audio dari proses sebelumnya. *GPU Worker* kemudian mengunduh aset gambar dan audio yang diperlukan, menjalankan model Wan2.1 untuk menghasilkan *frame* video yang tersinkronisasi, melakukan *encoding*, dan mengunggah hasil akhirnya. Kedua skenario ini menunjukkan penerapan pola komunikasi asinkron yang efektif untuk menangani beban komputasi berat tanpa memblokir respons antarmuka pengguna.

#### 3.7.2.4 Class Diagram
Diagram kelas memvisualisasikan struktur statis perangkat lunak dengan mendefinisikan objek-objek sistem, atribut, metode, serta hubungan antar objek tersebut. Gambar 3.9 menyajikan pemodelan berorientasi objek dari sistem *backend*.

![Class Diagram Sistem Backend](file:///Users/macbaru/.gemini/antigravity/brain/43ec4672-1a4a-48e4-9efd-4673ffed5f06/diagram_class_final.png)

*Gambar 3.9 Class Diagram Sistem Backend*

Seperti yang terlihat pada Gambar 3.9, struktur sistem berpusat pada kelas `App` yang berfungsi sebagai titik masuk utama (*entry point*) aplikasi, mengelola konfigurasi volume penyimpanan dan inisialisasi layanan. Kelas ini mengorkestrasi tiga layanan inti: `KokoroService` untuk sintesis audio TTS, `ChatterboxService` untuk pemrosesan kloning suara, dan kelas `Model` yang menangani logika generasi video menggunakan algoritma difusi. Interaksi dengan klien difasilitasi oleh `APIRouter` yang menyediakan antarmuka metode HTTP seperti `create_project` dan `get_status`. Untuk mendukung persistensi dan manajemen aset, sistem menggunakan kelas utilitas `SupabaseService` yang menangani transaksi basis data, serta `CloudinaryService` yang mengelola operasi unggah dan unduh fail media. Hubungan antar kelas ini membentuk arsitektur modular yang memisahkan logika bisnis, antarmuka API, dan akses infrastruktur eksternal.

## 3.8 Perancangan Basis Data

Perancangan basis data adalah proses penentuan isi dan pengaturan data yang dibutuhkan untuk mendukung berbagai rancangan sistem. Tujuannya adalah untuk menghasilkan model data yang akurat, efisien, dan sesuai dengan kebutuhan bisnis serta teknis aplikasi. Dalam penelitian ini, perancangan basis data dilakukan untuk memastikan data proyek, aset, dan status sistem tersimpan secara terstruktur dan efisien melalui tahapan representasi logis (ERD), fisik (PDM), hingga detail kamus data.

### 3.8.1 Entity Relationship Diagram (ERD)

### 3.8.1 Entity Relationship Diagram (ERD)

Desain basis data relasional untuk sistem ini dimodelkan menggunakan *Entity Relationship Diagram* (ERD), yang merupakan implementasi dari konsep teoretis yang dijelaskan pada subbab 2.8.2. Diagram pada Gambar 3.10 berikut memvisualisasikan lima entitas utama beserta relasi antar tabel yang membentuk struktur penyimpanan data di Supabase (PostgreSQL).

![Entity Relationship Diagram Sistem Backend](file:///Users/macbaru/.gemini/antigravity/brain/43ec4672-1a4a-48e4-9efd-4673ffed5f06/diagram_erd_final.png)

*Gambar 3.10 Entity Relationship Diagram Sistem Backend*

Mengacu pada Gambar 3.10, perancangan data berpusat pada entitas pengguna (dikelola secara eksternal melalu `user_id`) yang memiliki relasi *one-to-many* terhadap seluruh entitas operasional. Entitas **projects** digunakan untuk menyimpan data pekerjaan generasi video, **tts_projects** untuk pekerjaan sintesis audio *text-to-speech*, dan **chatterbox_projects** untuk pekerjaan kloning suara. Selain itu, terdapat entitas manajemen aset yaitu **avatars** untuk menyimpan referensi visual presenter, dan **voice_samples** untuk menyimpan sampel suara referensi. Relasi khusus terbentuk antara `chatterbox_projects` dan `voice_samples`, di mana sebuah proyek kloning suara "menggunakan" satu sampel suara sebagai acuan, membentuk relasi fungsional yang menjamin integritas data proses generasi AI.

### 3.8.2 Physical Data Model (PDM)

*Physical Data Model* (PDM) merepresentasikan spesifikasi teknis basis data yang diimplementasikan menggunakan sistem manajemen basis data PostgreSQL. Berbeda dengan model konseptual, PDM mendefinisikan struktur tabel secara presisi, mencakup tipe data kolom, aturan integritas (*constraints*), dan kunci relasional untuk mendukung model AI spesifik seperti Wan2.1 dan Chatterbox. Implementasi fisik skema basis data ditampilkan pada Gambar 3.11.

![Physical Data Model Sistem Backend](file:///Users/macbaru/.gemini/antigravity/brain/43ec4672-1a4a-48e4-9efd-4673ffed5f06/diagram_pdm_final.png)

*Gambar 3.11 Physical Data Model Sistem Backend*

Gambar 3.11 memperlihatkan struktur tabel yang dioptimalkan untuk kinerja dan fleksibilitas. Seluruh tabel utama menggunakan tipe data `UUID` sebagai *Primary Key* untuk menjamin keunikan global dan keamanan identifikasi data. Kolom waktu seperti `created_at` menggunakan tipe `timestamptz` untuk akurasi zona waktu. Fitur unggulan PostgreSQL, yaitu tipe data `JSONB`, diterapkan pada kolom `metadata` dan `parameters` di tabel `projects` dan `tts_projects`, memungkinkan penyimpanan data semi-terstruktur yang dinamis tanpa perlu mengubah skema tabel secara berulang. Relasi antar tabel ditegakkan melalui *Foreign Key* yang menghubungkan tabel transaksi (seperti `chatterbox_projects`) dengan tabel master referensi (seperti `voice_samples`), memastikan konsistensi referensial di seluruh sistem.

### 3.8.3 Kamus Data

Kamus Data (*Data Dictionary*) adalah referensi terpusat yang memuat metadata atau informasi rinci mengenai data yang dikelola oleh sistem. Kamus data berfungsi untuk memastikan konsistensi interpretasi terhadap elemen-elemen data, mendefinisikan nama tabel, nama kolom, tipe data, serta deskripsi kegunaan dari setiap atribut. Berikut adalah penjabaran kamus data untuk tabel-tabel utama yang telah didesain dalam PDM:

#### 3.8.3.1 Kamus Data Tabel Projects

Tabel `projects` adalah entitas utama yang berfungsi untuk menyimpan data transaksi pembuatan video avatar. Tabel ini mencatat seluruh parameter konfigurasi generasi video serta melacak status eksekusi *pipeline* secara mendetail.

**Tabel 3.3 Kamus Data Tabel `projects`**

| Nama Kolom | Tipe Data | Keterangan |
| :--- | :--- | :--- |
| `id` | UUID | *Primary Key*. Identitas unik referensi proyek video. |
| `user_id` | Text | *Foreign Key*. Referensi ID pengguna pemilik proyek. |
| `title` | Text | Judul proyek untuk label identifikasi. |
| `description` | Text | Deskripsi singkat mengenai konten proyek. |
| `type` | Text | Tipe video: `single_person` (satu avatar) atau `multi_person`. |
| `image_url` | Text | URL gambar avatar yang digunakan sebagai sumber visual. |
| `audio_url` | Text | URL file audio utama untuk *lip-sync*. |
| `audio_url_2` | Text | URL file audio kedua (opsional, untuk tipe `multi_person`). |
| `audio_order` | Text | Urutan pemutaran audio (misal: `audio1_first`). |
| `prompt` | Text | Teks instruksi tambahan untuk model (jika ada). |
| `call_id` | Text | Identifier unik dari pemanggilan fungsi *serverless* Modal. |
| `status` | Text | Status global pengerjaan (`queued`, `processing`, `finished`, `failed`). |
| `progress` | Integer | Persentase kemajuan proses (0-100). |
| `current_stage` | Text | Tahapan aktif dalam pipeline (misal: `INFERENCE`, `UPLOADING`). |
| `parameters` | JSONB | Parameter teknis model video Wan2.1 (konfigurasi dimensi, fps, dsb). |
| `metadata` | JSONB | Metadata log status pipeline per tahap (*stage logging*). |
| `video_url` | Text | URL hasil video final (output) di Cloudinary. |
| `error_message` | Text | Pesan kesalahan jika status gagal. |
| `created_at` | Timestamptz | Waktu pembuatan data dengan zona waktu. |
| `updated_at` | Timestamptz | Waktu terakhir data diperbarui. |

Tabel 3.3 di atas mendefinisikan struktur penyimpanan untuk modul generasi video. Atribut `metadata` dan `parameters` memainkan peran krusial dalam mendukung fleksibilitas sistem, di mana `metadata` menyimpan riwayat tahapan eksekusi secara *real-time* untuk pemantauan progres, sedangkan `parameters` memungkinkan penyimpanan konfigurasi teknis yang dinamis tanpa perlu mengubah skema tabel utama ketika terjadi pembaruan model AI.

#### 3.8.3.2 Kamus Data Tabel TTS Projects

Tabel `tts_projects` mencatat transaksi layanan *Text-to-Speech* (TTS). Tabel ini menyimpan konfigurasi model suara (Kokoro-82M) dan parameter sintesis yang digunakan.

**Tabel 3.4 Kamus Data Tabel `tts_projects`**

| Nama Kolom | Tipe Data | Keterangan |
| :--- | :--- | :--- |
| `id` | UUID | *Primary Key*. Identitas unik proyek TTS. |
| `user_id` | Text | *Foreign Key*. ID pengguna pemilik proyek. |
| `text` | Text | Teks input yang akan disintesis menjadi suara. |
| `voice` | Text | Kode profil suara yang digunakan (misal: `af_sarah`). |
| `speed` | Float | Kecepatan pembacaan (default: 1.0). |
| `lang_code` | Text | Kode bahasa yang digunakan (misal: `en-us`, `id-id`). |
| `audio_url` | Text | URL hasil audio final (output). |
| `status` | Text | Status pengerjaan (`pending`, `processing`, `completed`). |
| `progress` | Integer | Persentase kemajuan proses. |
| `current_stage` | Text | Tahapan aktif dalam pipeline TTS (misal: `TEXT_ANALYSIS`). |
| `metadata` | JSONB | Metadata log proses internal. |
| `created_at` | Timestamptz | Waktu pembuatan data. |

Tabel 3.4 menjabarkan atribut untuk layanan sintesis suara sederhana. Selain menyimpan teks input, tabel ini menyediakan kolom `speed` dan `lang_code` untuk memberikan kontrol lebih detail kepada pengguna terkait karakteristik suara yang dihasilkan. Kolom `audio_url` akan terisi secara otomatis setelah proses inferensi model Kokoro-82M berhasil diselesaikan dan file audio diunggah ke penyimpanan awan.

#### 3.8.3.3 Kamus Data Tabel Chatterbox Projects

Tabel `chatterbox_projects` digunakan khusus untuk fitur lanjutan *Voice Cloning* atau TTS Multilingual yang kompleks. Tabel ini memiliki relasi ke `voice_samples` sebagai sumber referensi suara.

**Tabel 3.5 Kamus Data Tabel `chatterbox_projects`**

| Nama Kolom | Tipe Data | Keterangan |
| :--- | :--- | :--- |
| `id` | UUID | *Primary Key*. Identitas unik proyek Chatterbox. |
| `user_id` | Text | *Foreign Key*. ID pengguna. |
| `project_type` | Text | Jenis proyek audio (`voice_cloning`, `multilingual_tts`). |
| `text` | Text | Teks input yang akan diucapkan (jika TTS). |
| `voice_sample_id` | UUID | *Foreign Key* ke tabel `voice_samples`. Referensi suara target. |
| `source_audio_url` | Text | URL audio asli (jika mode *Voice Conversion*). |
| `language_id` | Text | Kode bahasa target. |
| `exaggeration` | Float | Parameter ekspresi suara (gaya bicara). |
| `temperature` | Float | Parameter variabilitas sampling AI. |
| `cfg_weight` | Float | Parameter konfigurasi bobot model. |
| `status` | Text | Status pengerjaan. |
| `progress` | Integer | Persentase kemajuan. |
| `current_stage` | Text | Tahapan pipeline Chatterbox. |
| `audio_url` | Text | URL output audio hasil kloning. |
| `error_message` | Text | Pesan error detail (jika ada). |
| `created_at` | Timestamptz | Waktu pembuatan data. |

Berdasarkan Tabel 3.5, entitas ini dirancang untuk mengakomodasi kompleksitas fitur *Voice Cloning*. Keberadaan *Foreign Key* `voice_sample_id` menegaskan relasi ketergantungan antara proyek kloning dengan sampel suara referensi. Parameter teknis seperti `temperature` dan `cfg_weight` disimpan secara eksplisit untuk memungkinkan eksperimentasi dan penyesuaian kualitas hasil generasi audio oleh pengguna tingkat lanjut.

#### 3.8.3.4 Kamus Data Tabel Avatars

Tabel `avatars` berfungsi sebagai tabel master untuk menyimpan referensi aset visual presenter digital. Data ini dapat bersifat publik (sistem) atau privat (milik user).

**Tabel 3.6 Kamus Data Tabel `avatars`**

| Nama Kolom | Tipe Data | Keterangan |
| :--- | :--- | :--- |
| `avatar_id` | UUID | *Primary Key*. Identik unik aset avatar. |
| `user_id` | Text | *Foreign Key*. ID pemilik avatar (`anonymous` jika global). |
| `name` | Text | Nama/Label tampilan avatar. |
| `image_url` | Text | URL file gambar asli di Cloudinary. |
| `is_public` | Boolean | Flag kepemilikan (`true` = global, `false` = privat). |
| `created_at` | Timestamptz | Waktu avatar didaftarkan. |

Tabel 3.6 menunjukkan struktur data untuk manajemen aset visual. Atribut `is_public` berfungsi sebagai mekanisme kontrol akses (RBAC) sederhana, yang memisahkan antara aset publik yang dapat digunakan oleh seluruh pengguna sistem dengan aset pribadi yang hanya dapat diakses oleh pemiliknya (`user_id` tertentu).

#### 3.8.3.5 Kamus Data Tabel Voice Samples

Tabel `voice_samples` menyimpan aset suara referensi untuk kebutuhan *Voice Cloning*. Tabel ini memastikan setiap sampel suara telah divalidasi dan tersimpan dengan metadata teknis yang benar.

**Tabel 3.7 Kamus Data Tabel `voice_samples`**

| Nama Kolom | Tipe Data | Keterangan |
| :--- | :--- | :--- |
| `id` | UUID | *Primary Key*. Identitas unik sampel suara. |
| `user_id` | Text | *Foreign Key*. ID pemilik sampel. |
| `name` | Text | Nama label sampel suara. |
| `audio_url` | Text | URL file rekaman suara referensi. |
| `duration_seconds` | Float | Durasi audio untuk validasi minimum sampel. |
| `sample_rate` | Integer | Frekuensi sampel audio (Hz) untuk kualitas input. |
| `language_hint` | Text | Bahasa dominan dalam rekaman (opsional). |
| `is_public` | Boolean | Flag aksesibilitas sampel suara. |
| `created_at` | Timestamptz | Waktu pengunggahan sampel. |


Tabel 3.7 menyimpan metadata teknis dari sampel suara yang diunggah. Atribut `duration_seconds` dan `sample_rate` dicatat secara otomatis saat pengunggahan untuk memastikan kualitas data latih. Validasi teknis ini penting karena kualitas model *Voice Cloning* (Chatterbox) sangat bergantung pada karakteristik audio (durasi dan kejernihan) dari sampel suara referensi yang digunakan.

### 3.8.4 Manajemen Penyimpanan Data (Cloudinary Storage Design)

Selain basis data relasional, desain penyimpanan aset media (*Cloud Storage*) diatur secara hierarkis pada Cloudinary untuk menjamin kerapian data (*Data Governance*) dan kemudahan akses.

*   **Root Directory**: `App Name/`

    Struktur folder dikalsifikasikan berdasarkan kategori fitur:
    1.  **Video Output**: `App Name/AI Video Output/Talking Video/Infinitalk/{Tipe}`
        *   Menyimpan hasil video *talking head*. `{Tipe}` memisahkan antara `Portrait` dan `Landscape`.
    2.  **Audio Output**: `App Name/AI Audio Output/`
        *   Sub-folder `TTS` untuk *Text-to-Speech* standar dan `Voice Cloning` untuk hasil kloning suara.
    3.  **Avatar Assets**: `App Name/Avatar Assets/{Public/Users}`. Folder `Public` untuk avatar bawaan sistem, `Users` untuk avatar unggahan pengguna pribadi.
    4.  **Voice Samples**: `App Name/Voice Sample/{Public/Users}`. Folder untuk sampel suara referensi *voice cloning*.
*   **Justifikasi Desain**: Pemisahan folder berdasarkan *Service Type* (Audio/Video) dan *Access Level* (Public/User) memudahkan pengelolaan hak akses, pembersihan data (*cleanup*), dan pencarian aset secara terprogram.

## 3.9 Perancangan Integrasi API

Integrasi API (*Application Programming Interface*) merupakan mekanisme perangkat lunak yang memfasilitasi pertukaran data antara aplikasi klien (*frontend*) dan layanan peladen (*backend*) secara terstruktur dan otomatis. Dalam konteks penelitian ini, arsitektur integrasi API dirancang secara terpusat menggunakan pola *API Gateway* untuk menghubungkan antarmuka pengguna dengan berbagai layanan mikro kecerdasan buatan (*AI Microservices*), manajemen data, dan penyimpanan awan eksternal. Pendekatan ini bertujuan untuk memastikan modularitas sistem, efisiensi distribusi beban kerja komputasi, serta keamanan akses data melalui satu pintu gerbang yang terkelola. Berikut merupakan hasil perancangan integrasi API pada sistem yang dikembangkan.

![Rancangan Integrasi API dan Alur Data Antar Modul](file:///Users/macbaru/.gemini/antigravity/brain/43ec4672-1a4a-48e4-9efd-4673ffed5f06/diagram_integrasi_api_final.jpg)

*Gambar 3.12 Rancangan Integrasi API Sistem Backend*

Gambar 3.12 mengilustrasikan rancangan integrasi API pada sistem usulan. Perancangan sistem ini menerapkan arsitektur *backend* yang melayani berbagai permintaan dari sisi klien melalui satu gerbang utama (*API Gateway*). Pengguna mengirimkan *request* berbentuk JSON (*JavaScript Object Notation*) melalui protokol HTTP untuk mengakses fitur-fitur spesifik seperti pembuatan video avatar, sintesis suara (*Text-to-Speech*), kloning suara, maupun manajemen aset media. *API Gateway* bertugas sebagai orkestrator yang memvalidasi setiap permintaan masuk, lalu meneruskannya ke enam modul layanan yang relevan: Modul *AI Video*, *AI Voice* (Kokoro & Chatterbox), *Avatar Management*, *Voice Library*, dan *Upload/Media*. Interaksi ini mencakup mekanisme pemrosesan sinkron untuk tugas ringan dan asinkron untuk beban kerja berat pada GPU *Worker*, dimana hasil pemrosesan dikembalikan kepada pengguna secara presisi sesuai dengan kontrak data yang telah disepakati.

## 3.10 Metode Implementasi

Implementasi sistem dilakukan dengan menerjemahkan rancangan arsitektur dan desain detail ke dalam kode program yang dapat dieksekusi. Tahapan ini mencakup konfigurasi lingkungan, strukturisasi kode, manajemen infrastruktur serverless, hingga mekanisme deployment.

### 3.10.1 Lingkungan Pengembangan & Konfigurasi
Proses implementasi sistem memerlukan spesifikasi lingkungan pengembangan yang memadai untuk mendukung komputasi berat dan integrasi layanan *cloud*. Spesifikasi ini dibagi menjadi dua aspek utama, yaitu perangkat keras dan perangkat lunak.

**A. Spesifikasi Perangkat Keras (*Hardware Requirements*)**
Pengembangan dilakukan dalam lingkungan hibrida yang melibatkan komputer lokal untuk penulisan kode dan instans *cloud* untuk eksekusi model AI:
1.  **Workstation Pengembang**: Komputer berbasis macOS dengan prosesor Intel Core i7 dan RAM 32GB digunakan untuk manajemen kode sumber dan pengujian API lokal.
2.  **Cloud GPU Instances**: Infrastruktur produksi menggunakan instans GPU NVIDIA H100 (80GB VRAM) untuk model video dan NVIDIA A10G (24GB VRAM) untuk model audio, yang disediakan oleh platform Modal.com.

**B. Spesifikasi Perangkat Lunak (*Software Requirements*)**
Perangkat lunak yang digunakan untuk membangun sistem backend meliputi:
1.  **Bahasa Pemrograman**: Python 3.10 sebagai bahasa inti.
2.  **Libraries & Framework**: FastAPI untuk antarmuka HTTP, Modal SDK untuk orkestrasi serverless, serta dependensi AI seperti `torch`, `diffusers`, dan `torchaudio`.
3.  **Layanan Pendukung**: Postman untuk validasi *endpoint*, Git untuk kontrol versi, dan Docker untuk kontainerisasi.

### 3.10.2 Arsitektur Kode & Pola Desain
Sistem dibangun di atas prinsip **Arsitektur Berlapis (*Layered Architecture*)** yang diadaptasi untuk lingkungan serverless terdistribusi. Struktur kode dirancang untuk memisahkan tanggung jawab (*Separation of Concerns*) menjadi tiga lapisan logis: lapisan antarmuka (*Interface Layer*) yang menangani validasi HTTP menggunakan Router FastAPI, lapisan logika bisnis (*Service Layer*) yang mengenkapsulasi algoritma inti dan orkestrasi model AI, serta lapisan data (*Data Layer*) yang mendefinisikan skema objek menggunakan Pydantic untuk menjamin integritas tipe data di seluruh sistem.

Implementasi kode menerapkan pola **Monorepo** (*Monolithic Repository*) untuk pengelolaan basis kode yang terpusat, meskipun arsitektur *deployment* bersifat mikro (*Microservices*). Pendekatan ini dipilih untuk memudahkan pembagian kode umum (*shared libraries*) antar layanan dan menjaga konsistensi versi dependensi. Selain itu, definisi infrastruktur (seperti alokasi GPU dan Volume) dilakukan menggunakan pola **Declarative Infrastructure** di dalam kode aplikasi utama (`app.py`), memungkinkan infrastruktur untuk dikelola dan di-versi selayaknya kode perangkat lunak (*Infrastructure as Code*).

### 3.10.3 Manajemen Infrastruktur Serverless
Berbeda dengan pendekatan penyewaan server konvensional, penelitian ini menerapkan konsep *Infrastructure as Code* (IaC). Definisi infrastruktur tidak dilakukan melalui konfigurasi manual pada panel kendali, melainkan dideklarasikan secara eksplisit dalam kode program Python. Konfigurasi ini mencakup:
1.  **Definisi Kontainer**: Spesifikasi *image* sistem operasi, instalasi dependensi level sistem (seperti FFmpeg dan Git), serta instalasi pustaka Python yang diperlukan untuk lingkungan *production*.
2.  **Alokasi Sumber Daya**: Penentuan jenis GPU dan batas memori yang dialokasikan untuk setiap fungsi.
3.  **Manajemen Volume Persisten**: Deklarasi *mounting point* untuk penyimpanan data model yang bersifat persisten lintas eksekusi fungsi.
4.  **Manajemen Siklus Hidup**: Konfigurasi batasan waktu eksekusi (*timeout*) dan aturan *scale-down* otomatis untuk menjaga efisiensi biaya.

### 3.10.4 Mekanisme Deployment Otomatis
Proses *deployment* ke lingkungan produksi dilakukan melalui mekanisme *Command Line Interface* (CLI) yang memicu serangkaian prosedur otomatis pada sisi penyedia layanan *cloud*. Alur kerja ini menjamin konsistensi antara kode lokal dan versi produksi. Tahapan *deployment* meliputi:
1.  **Container Building**: Sistem secara otomatis membangun *image* kontainer baru yang memuat seluruh dependensi dan kode terbaru.
2.  **Registry Push**: *Image* yang telah dibangun diunggah ke repositori privat kontainer yang aman.
3.  **Function Routing**: Pemetaan *endpoint* HTTPS publik ke fungsi serverless yang baru diperbarui.
4.  **Secret Injection**: Penyuntikan variabel lingkungan sensitif, seperti kunci API pihak ketiga, ke dalam *runtime* secara aman pada saat inisialisasi.

## 3.11 Metode Pengujian Sistem

Pengujian dilakukan untuk memastikan fungsionalitas dan kinerja sistem memenuhi spesifikasi yang telah ditetapkan. Pendekatan yang digunakan mencakup pengujian fungsional (*functional testing*) dan pengujian kinerja (*performance testing*).

### 3.11.1 Pengujian Fungsional (Black Box Testing)

Pengujian fungsional dilakukan dengan metode *Black Box Testing* berbasis spesifikasi (*specification-based testing*), di mana fokus utama adalah memvalidasi kesesuaian antara masukan (*input*) dan keluaran (*output*) sistem tanpa memeriksa struktur kode internalnya. Proses pengujian ini dilakukan dengan memanggil *endpoint* API secara langsung menggunakan parameter uji yang telah ditentukan untuk mensimulasikan interaksi pengguna nyata dan memverifikasi respon sistem.

Matriks pengujian dirancang untuk mencakup tiga modul utama: Manajemen Aset dan Pengguna, Layanan Video AI, dan Layanan Audio AI.

#### 3.11.1.1 Pengujian Manajemen Aset
Pengujian ini bertujuan untuk memastikan fungsi dasar pengelolaan file media berjalan dengan benar dan aman.

**Tabel 3.8 Rancangan Pengujian Fungsional Aset**
| No | Skenario Pengujian | Hasil yang Diharapkan |
| :--- | :--- | :--- |
| 1 | Menguji fungsionalitas pengunggahan file gambar valid (JPG/PNG). | Sistem menerima file, menyimpannya di folder `/Assets` Cloudinary, dan mengembalikan URL publik serta ID file yang valid. |
| 2 | Menguji fungsionalitas pengunggahan file audio valid (MP3/WAV). | Sistem menerima file audio, menyimpannya di folder `/Voice`, dan mengembalikan metadata file yang sesuai. |
| 3 | Menguji validasi sistem terhadap pengunggahan file kosong. | Sistem menolak permintaan dengan kode status 422 karena tidak ada *payload* data yang dikirimkan. |
| 4 | Menguji mekanisme keamanan terhadap file format terlarang (.exe). | Sistem mendeteksi ekstensi file berbahaya, menolak penyimpanan, dan mengembalikan kode error 400. |
| 5 | Menguji fitur penghapusan file aset dengan ID yang valid. | Sistem menghapus file dari penyimpanan awan dan mengembalikan konfirmasi penghapusan yang sukses. |
| 6 | Menguji respon sistem saat menghapus file dengan ID yang tidak ada. | Sistem menangani referensi aset yang hilang dengan bijak, mengembalikan kode error 404 tanpa menyebabkan *crash*. |

#### 3.11.1.2 Pengujian Manajemen Avatar
Pengujian ini memverifikasi siklus hidup data avatar pengguna, termasukan validasi input.

**Tabel 3.9 Rancangan Pengujian Fungsional Avatar**
| No | Skenario Pengujian | Hasil yang Diharapkan |
| :--- | :--- | :--- |
| 1 | Menguji pembuatan avatar baru dengan data lengkap dan valid. | Data avatar tersimpan di basis data Supabase, dan sistem mengembalikan objek avatar lengkap dengan ID baru. |
| 2 | Menguji validasi input saat membuat avatar tanpa menyertakan nama. | Sistem menolak permintaan pembuatan avatar karena melanggar batasan `not null` pada kolom nama. |
| 3 | Menguji pengambilan daftar seluruh avatar yang tersedia (Public). | Sistem mengembalikan daftar JSON *array* yang berisi seluruh objek avatar publik yang ada di sistem. |
| 4 | Menguji filter daftar avatar berdasarkan ID Pengguna tertentu. | Sistem hanya menampilkan avatar yang kepemilikannya (User ID) sesuai dengan parameter yang diminta. |
| 5 | Menguji penghapusan data avatar yang valid dari sistem. | Rekaman avatar dihapus dari basis data, dan sistem mengembalikan konfirmasi keberhasilan operasi. |

#### 3.11.1.3 Pengujian Layanan Video Generasi
Pengujian ini berfokus pada kestabilan proses *long-running* pembuatan video yang melibatkan GPU.

**Tabel 3.10 Rancangan Pengujian Fungsional Video**
| No | Skenario Pengujian | Hasil yang Diharapkan |
| :--- | :--- | :--- |
| 1 | Menguji inisiasi pembuatan proyek video dengan parameter valid. | Tugas pembuatan video berhasil didaftarkan ke antrian *Worker* GPU, dan sistem mengembalikan ID Proyek dengan status `Queued`. |
| 2 | Menguji validasi pembuatan proyek dengan parameter gambar yang hilang. | Sistem menolak permintaan karena kekurangan aset visual wajib, mencegah proses error di kemudian hari. |
| 3 | Menguji mekanisme pemantauan status (*polling*) proyek yang berjalan. | Endpoint status merefleksikan perubahan progres secara akurat dari `Queued`, `Processing`, hingga `Finished`. |
| 4 | Menguji pengambilan hasil akhir video setelah status `Finished`. | URL video hasil generasi tersedia dalam respons JSON dan file video dapat diakses secara publik. |
| 5 | Menguji fitur penyaringan daftar proyek berdasarkan tipe (Single/Batch). | Sistem mengembalikan daftar proyek yang hanya sesuai dengan kategori tipe yang diminta pada parameter *query*. |
| 6 | Menguji penghapusan proyek video beserta data terkaitnya. | Sistem menghapus entri proyek dari database dan membersihkan aset terkait untuk menjaga efisiensi. |

#### 3.11.1.4 Pengujian Layanan TTS (Kokoro)
Pengujian integrasi model Kokoro-82M untuk sintesis suara cepat.

**Tabel 3.11 Rancangan Pengujian Fungsional TTS Kokoro**
| No | Skenario Pengujian | Hasil yang Diharapkan |
| :--- | :--- | :--- |
| 1 | Menguji inisiasi sintesis suara (TTS) dengan teks dan parameter valid. | Tugas TTS diterima oleh sistem, ID pelacakan diberikan, dan proses sintesis dimulai secara asinkron. |
| 2 | Menguji validasi sistem terhadap input teks kosong untuk TTS. | Sistem menolak memproses permintaan tanpa konten teks, mencegah pembuangan sumber daya komputasi yang sia-sia. |
| 3 | Menguji respons sistem terhadap penggunaan ID suara yang tidak valid. | Sistem memverifikasi ketersediaan ID suara dan menolak permintaan jika ID tidak ditemukan dalam katalog model. |
| 4 | Menguji pengambilan daftar referensi kode bahasa yang didukung. | Sistem menyediakan daftar kode bahasa standar (ISO) yang didukung oleh model Kokoro-82M. |
| 5 | Menguji pengambilan katalog karakter suara (*Voices*) yang tersedia. | Sistem menampilkan daftar seluruh karakter suara beserta metadata gender dan bahasanya. |
| 6 | Menguji penghapusan riwayat proyek TTS tertentu. | Entri riwayat TTS dihapus dari sistem untuk manajemen data pengguna. |

#### 3.11.1.5 Pengujian Layanan Voice Library
Pengujian fitur manajemen sampel suara untuk keperluan *Voice Cloning*.

**Tabel 3.12 Rancangan Pengujian Voice Library**
| No | Skenario Pengujian | Hasil yang Diharapkan |
| :--- | :--- | :--- |
| 1 | Menguji pengunggahan sampel suara baru untuk referensi *cloning*. | File audio tersimpan, sistem menganalisis durasinya, dan mengembalikan ID sampel baru. |
| 2 | Menguji filter tipe file saat mengunggah sampel non-audio. | Sistem menolak file yang bukan format audio (misal dokumen teks) untuk menjaga integritas pustaka suara. |
| 3 | Menguji pengambilan detail metadata dari satu sampel suara. | Sistem mengembalikan informasi lengkap termasuk nama, deskripsi, dan URL pratinjau audio. |
| 4 | Menguji penanganan permintaan detail untuk ID sampel yang salah. | Sistem memberikan respons error standar 404 ketika aset yang diminta tidak ditemukan. |
| 5 | Menguji penghapusan permanen sampel suara dari pustaka. | Aset sampel suara dan seluruh metadatanya dihapus secara permanen dari sistem. |

#### 3.11.1.6 Pengujian Layanan Chatterbox
Pengujian fitur audio tingkat lanjut termasuk Multilingual TTS dan Voice Conversion.

**Tabel 3.13 Rancangan Pengujian Fungsional Chatterbox**
| No | Skenario Pengujian | Hasil yang Diharapkan |
| :--- | :--- | :--- |
| 1 | Menguji fitur Multilingual TTS dengan deteksi bahasa otomatis. | Sistem menerima teks dan kode bahasa, memulai proses generasi asinkron untuk bahasa target. |
| 2 | Menguji inisiasi *Voice Cloning* menggunakan sampel suara yang valid. | Sistem memvalidasi sampel referensi, dan memulai proses inferensi model untuk meniru gaya suara. |
| 3 | Menguji validasi ketergantungan ID sampel pada proses *cloning*. | Sistem menolak permintaan kloning jika ID sampel suara tidak disertakan atau tidak valid. |
| 4 | Menguji fitur *Voice Conversion* (Speech-to-Speech) dengan input audio. | Sistem menerima audio sumber dan target, memulai proses transformasi timbre suara. |
| 5 | Menguji integrasi riwayat proyek gabungan (TTS, Cloning, Conversion). | Sistem menampilkan daftar proyek yang mencakup semua jenis aktivitas audio dengan identifikasi tipe yang jelas. |
| 6 | Menguji pembersihan data proyek Chatterbox secara menyeluruh. | Menghapus proyek beserta hasil audio generasinya dari sistem penyimpanan. |

### 3.11.2 Pengujian Kinerja Berbasis Log Sistem

Pengujian kinerja tidak dilakukan menggunakan alat *load testing* eksternal, melainkan melalui **Analisis Telemetri Internal** menggunakan fitur *logging* dan pemantauan bawaan dari platform Modal.com. Data kinerja diekstraksi dari log eksekusi nyata selama proses pengujian fungsional untuk mengukur metrik berikut:

1.  ***Cold Start Latency***: Waktu yang dibutuhkan untuk *container* GPU melakukan inisialisasi dan memuat model AI (Kokoro-82M, Wan2.1, Chatterbox) ke dalam VRAM pertama kali. Dicatat dari selisih waktu antara permintaan masuk dan dimulainya inferensi pada log *container* baru.
2.  ***Execution Time***: Durasi bersih proses inferensi model, diukur dari log internal fungsi (`start_time` hingga `end_time` pemrosesan fungsi Python).
3.  ***Queue Time***: Waktu tunggu permintaan dalam antrean Modal sebelum dialokasikan ke *worker* yang tersedia.

Metode ini dipilih untuk memberikan gambaran realistis mengenai kinerja sistem dalam lingkungan *serverless* yang dinamis, di mana latensi infrastruktur dan waktu *booting* model merupakan faktor kritis yang perlu dianalisis secara akurat. Data yang terkumpul akan disajikan dalam bentuk tabel statistik kinerja pada Bab IV.

### 3.11.3 Analisis Biaya Generasi (*Cost Analysis*)
Analisis ini bertujuan untuk menjawab rumusan masalah ketiga, yaitu mengestimasi efisiensi biaya operasional sistem.
*   **Sumber Data**: Data primer diambil dari *Usage Logs* pada dashboard Modal.com, yang mencatat durasi aktif (*active time*) dari setiap kontainer GPU secara presisi hingga milidetik.
*   **Metode Perhitungan**: Biaya per transaksi dihitung menggunakan formula:
    
    $$Cost = \frac{T_{exec} \times R_{gpu}}{3600}$$
    
    Dimana:
    *   $T_{exec}$ : Durasi eksekusi total dalam detik (termasuk *cold start*).
    *   $R_{gpu}$ : Tarif sewa GPU per jam (misal: USD 5.76/jam untuk Nvidia H100).
    *   3600 : Faktor konversi detik ke jam.

*   **Metrik Evaluasi**: Hasil perhitungan akan dikonversi menjadi *Unit Economics* berupa "Biaya per 1 Menit Video Generasi" atau "Biaya per 1000 Karakter TTS", yang kemudian dibandingkan dengan harga layanan SaaS kompetitor (*benchmark*).

## DAFTAR PUSTAKA

Sugiyono. (2019). *Metode Penelitian Kuantitatif, Kualitatif, dan R&D*. Bandung: Alfabeta.
