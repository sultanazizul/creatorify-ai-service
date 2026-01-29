# BAB I
PENDAHULUAN

## 1.1 Latar Belakang

Perkembangan teknologi kecerdasan buatan dalam lima tahun terakhir telah mengalami pergeseran paradigma yang signifikan, dari sistem klasifikasi dan prediksi menuju sistem generatif yang mampu menciptakan konten baru. Fenomena ini ditandai dengan pertumbuhan eksponensial pasar *Generative AI*. Data pasar menunjukkan bahwa valuasi pasar *Generative AI* global diproyeksikan mencapai USD 113,42 miliar pada tahun 2029 dengan *Compound Annual Growth Rate* (CAGR) sebesar 34,7% (Research and Markets, 2025). Secara spesifik, sektor *AI Video Generator* juga menunjukkan tren positif dengan estimasi pertumbuhan CAGR sebesar 20,3% dari tahun 2026 hingga 2033 (Grand View Research, 2025). Tren ini diperkuat oleh dominasi konten video pendek (*short-form video*) pada platform seperti TikTok dan Reels, di mana format *talking head* menjadi standar komunikasi pemasaran digital yang sangat efektif. Studi industri mencatat bahwa video pendek kini menyumbang porsi mayoritas lalu lintas internet global, dengan tingkat keterlibatan pengguna 2,5 kali lebih tinggi dibandingkan format tradisional (Firework, 2024). Dalam konteks ini, penggunaan *virtual presenter* atau video avatar AI yang dikombinasikan dengan suara sintetis menjadi solusi vital bagi industri untuk memproduksi konten video massal yang tetap personal tanpa kendala biaya produksi konvensional. Fenomena inilah yang menjadikan integrasi fitur generatif suara dan video avatar sebagai kebutuhan mendesak dalam ekosistem aplikasi modern. Guna mengakomodasi lonjakan kebutuhan tersebut, infrastruktur pendukung dituntut untuk memiliki kapabilitas adaptasi yang tinggi terhadap beban kerja dinamis.

Mengacu pada tuntutan tersebut, dalam tataran teoritis, arsitektur *backend* untuk layanan *Generative AI* idealnya harus memenuhi prinsip skalabilitas elastis, efisiensi sumber daya, dan responsivitas tinggi (Das Sollen). Hal ini dikarenakan model *Deep Learning* modern, seperti *Large Language Models* (LLM) dan *Diffusion Models*, membutuhkan daya komputasi GPU (*Graphics Processing Unit*) yang sangat intensif. Namun, realita di lapangan menunjukkan tantangan teknis yang kompleks (Das Sein). Infrastruktur konvensional sering kali menghadapi kendala *cold start latency*, alokasi sumber daya yang tidak efisien, dan biaya operasional yang tinggi akibat penyediaan server GPU yang statusnya *always-on* meskipun tidak ada permintaan (International Journal of Computer Trends and Technology, 2024). Kontradiksi antara kebutuhan performa tinggi dengan kendala efisiensi infrastruktur ini menjadi hambatan utama dalam pengembangan layanan AI yang *scalable* dan *cost-effective*. Dilema antara kebutuhan performa tinggi dan efisiensi biaya ini menjadi tantangan krusial yang sulit dipecahkan oleh pendekatan infrastruktur konvensional.

Hambatan struktural tersebut mempertegas adanya kesenjangan teknologi yang signifikan. Pendekatan arsitektur monolitik konvensional terbukti gagal menangani beban kerja inferensi model AI yang berat secara optimal. Studi komparatif menunjukkan bahwa arsitektur monolitik sering kali mengalami *bottleneck* pada pemrosesan permintaan konkuren yang tinggi, menyebabkan peningkatan latensi yang tidak dapat diterima untuk pengalaman pengguna yang interaktif (CEUR Workshop Proceedings, 2024). Selain itu, keterbatasan dalam manajemen pemrosesan sinkron membuat antrian permintaan (*queue*) menjadi panjang dan berpotensi *timeout*, terutama pada proses generasi video yang memakan waktu lama (*long-running tasks*). Kegagalan arsitektur konvensional dalam mengelola proses berat tersebut mengindikasikan perlunya intervensi teknis yang lebih mendalam pada lapisan infrastruktur.

Beranjak dari urgensi perbaikan infrastruktur tersebut, penelitian ini memfokuskan kajian utama pada disiplin *Backend Engineering*. Masalah yang akan dibedah dibatasi pada optimalisasi penanganan komputasi untuk fitur generatif suara dan video avatar. Fokus penelitian tidak akan melebar ke aspek antarmuka pengguna (*frontend*) maupun fitur manajerial aplikasi lainnya, melainkan mendalam pada mekanisme orkestrasi tugas di sisi server untuk memastikan reliabilitas dan performa sistem. Upaya penjaminan kualitas sistem tersebut menuntut adanya pergeseran paradigma dari manajemen server statis menuju orkestrasi sumber daya yang lebih fleksibel.

Merespons kebutuhan orkestrasi yang fleksibel tersebut, penelitian ini mengusulkan penerapan arsitektur berbasis *Serverless GPU* yang dikombinasikan dengan mekanisme *Asynchronous Processing* dan *API Gateway*. Pendekatan *serverless* memungkinkan alokasi sumber daya GPU secara dinamis sesuai permintaan (*on-demand*), sehingga dapat mengeliminasi biaya *idle time*. Sementara itu, pola pemrosesan asinkron diharapkan mampu menangani tugas-tugas berat tanpa memblokir alur utama aplikasi. Integrasi kedua pendekatan ini melalui desain arsitektur yang tepat menjadi kunci untuk menjawab tantangan skalabilitas dan efisiensi layanan *Generative AI*. Oleh karena itu, diperlukan kajian mendalam untuk merumuskan bagaimana perancangan dan implementasi solusi teknis tersebut dapat berjalan efektif.

## 1.2 Rumusan Masalah

Berdasarkan latar belakang yang telah diuraikan, rumusan masalah dalam penelitian ini adalah sebagai berikut:

1.  Bagaimana merancang arsitektur backend berbasis Serverless GPU untuk mendukung layanan generatif video avatar dan suara yang efisien dan responsif?
2.  Bagaimana implementasi mekanisme pemrosesan asinkron pada API Gateway dalam menangani antrian tugas berat dari model AI generatif?
3.  Bagaimana hasil pengujian fungsionalitas dan kinerja response time API menggunakan metode Black Box Testing untuk memvalidasi alur proses generasi video avatar dan suara?
4.  Bagaimana estimasi biaya komputasi yang diperlukan untuk satu siklus generasi video avatar dan suara menggunakan model harga *pay-per-use* pada infrastruktur serverless?

## 1.3 Tujuan Penelitian

Mengacu pada rumusan masalah di atas, tujuan dari penelitian ini adalah:

1.  Merancang arsitektur backend yang memanfaatkan teknologi *Serverless GPU* guna mendukung operasional layanan generatif yang efisien secara sumber daya dan responsif.
2.  Mengimplementasikan mekanisme orkestrasi asinkron yang mampu menangani *long-running tasks* tanpa memblokir responsivitas API.
3.  Melakukan pengujian fungsionalitas dan pengukuran kinerja *response time* API menggunakan metode *Black Box Testing* untuk memvalidasi keberhasilan alur proses generasi video avatar dan suara.
4.  Menganalisis efisiensi biaya operasional sistem berdasarkan log durasi eksekusi GPU dan tarif komputasi awan.

## 1.4 Manfaat Penelitian

Penelitian ini diharapkan dapat memberikan manfaat sebagai berikut:

**1.4.1 Manfaat Teoritis**
Hasil penelitian ini diharapkan dapat memperkaya literatur akademik di bidang *Software Engineering* dan *Cloud Computing Economics*. Secara spesifik, penelitian ini memberikan wawasan mengenai:
1.  Penerapan pola desain *Serverless*, *Asynchronous*, dan *Black Box Testing* untuk aplikasi AI.
2.  Analisis biaya (FinOps) pada arsitektur *Serverless AI* sebagai studi komparatif model *on-demand*.

**1.4.2 Manfaat Praktis**
*   **Bagi Pengembang:** Memberikan panduan teknis dalam mengestimasi anggaran infrastruktur untuk proyek AI generatif agar tidak mengalami *budget overrun*.
*   **Bagi Industri:** Menawarkan kerangka kerja evaluasi biaya yang dapat diadopsi untuk pengambilan keputusan strategis dalam pemilihan penyedia layanan cloud GPU.

## 1.5 Batasan Masalah

Agar penelitian tetap terarah dan fokus pada tujuan yang ingin dicapai, maka ditetapkan batasan masalah sebagai berikut:

1.  Penelitian hanya berfokus pada pengembangan dan analisis sisi *backend*, tidak mencakup antarmuka pengguna (*frontend*).
2.  Lingkup fitur AI terbatas pada video avatar generatif dan pemrosesan suara yang diimplementasikan menggunakan model spesifik: **Wan2.1** dan **InfiniteTalk** untuk video, serta **Kokoro-82M** dan **Chatterbox** untuk sintesis suara (*Text-to-Speech* & *Voice Cloning*).
3.  Analisis biaya dilakukan berdasarkan model tarif publik dari platform Modal.com (USD/jam) dan data durasi eksekusi riil, tidak mencakup biaya lisensi software pihak ketiga atau biaya trafik jaringan (*egress cost*).
4.  Pengujian kinerja berfokus pada metrik *response time* dan *resource utilization* untuk keperluan perhitungan biaya, bukan pada validasi subjektif kualitas estetika video/audio (MOS).
5.  Sistem tidak membahas optimasi model AI itu sendiri (seperti *quantization* atau *pruning*), melainkan optimasi orkestrasinya.


## 1.6 Sistematika Penulisan

Sistematika penulisan laporan skripsi ini disusun sebagai berikut:

**BAB I PENDAHULUAN**
Bab ini menjelaskan latar belakang masalah, identifikasi kesenjangan teknologi, rumusan masalah, tujuan penelitian, manfaat penelitian, batasan masalah, dan sistematika penulisan.

**BAB II TINJAUAN PUSTAKA**
Bab ini memuat teori-teori pendukung dan tinjauan literatur terkait arsitektur *Serverless*, *Generative AI*, *API Gateway*, serta penelitian terdahulu yang relevan dengan topik penelitian.

**BAB III METODOLOGI PENELITIAN**
Bab ini menguraikan tahapan penelitian, mulai dari analisis kebutuhan, perancangan sistem, implementasi arsitektur, hingga skenario pengujian yang akan dilakukan.

**BAB IV HASIL DAN PEMBAHASAN**
Bab ini menyajikan hasil dari perancangan dan implementasi sistem backend, serta analisis data hasil pengujian fungsionalitas dan performa sistem untuk menjawab rumusan masalah.

**BAB V PENUTUP**
Bab ini berisi kesimpulan yang diperoleh dari seluruh rangkaian penelitian serta saran-saran untuk pengembangan penelitian selanjutnya.

## DAFTAR PUSTAKA

CEUR Workshop Proceedings. (2024). *Performance Comparison between a Monolithic and a Microservice Application*. [online] Available at: http://ceur-ws.org/ [Accessed 13 Jan. 2026].

Eismann, S., Joel, Scheuner, J., et al. (2021). A Review of Serverless Use Cases and Their Characteristics. *IEEE Transactions on Software Engineering*, 48(9), pp.1-23. doi: 10.1109/TSE.2021.3081292.

FinOps Foundation. (2024). *State of FinOps 2024*. [online] Available at: https://data.finops.org/ [Accessed 15 Jan. 2026].

Firework. (2024). *The State of Short-Form Video: Trends and Statistics for 2024*. [online] Available at: https://firework.com/ [Accessed 13 Jan. 2026].

Grand View Research. (2025). *AI Video Generator Market Size, Share & Trends Analysis Report 2026 - 2033*. [online] Available at: https://www.grandviewresearch.com/industry-analysis/ai-video-generator-market-report [Accessed 13 Jan. 2026].

Research and Markets. (2025). *Generative AI Market - Global Outlook & Forecast 2024-2029*. [online] Available at: https://www.researchandmarkets.com/ [Accessed 13 Jan. 2026].

Walia, K. (2024). Exploring the Challenges of Serverless Computing in Training Large Language Models. *International Journal of Computer Trends and Technology*, 72(4), pp.71-76. [online] Available at: https://ijcttjournal.org/archives/ijctt-v72i4p111 [Accessed 13 Jan. 2026].
