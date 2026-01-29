# Dokumentasi Multi-Stage Asynchronous Pipeline

Dokumen ini menjelaskan perubahan arsitektur sistem dari **Single-Status Model** menjadi **Multi-Stage Asynchronous Pipeline** untuk fitur-fitur AI Creatorify (Video, Chatterbox, dan Kokoro TTS).

## 1. Latar Belakang Perubahan

**Sebelumnya (Legacy):**
*   Hanya memiliki status sederhana: `processing`, `finished`, `failed`.
*   Progress bar seringkali tidak akurat (diam di 0% lama, lalu tiba-tiba 100%).
*   User tidak tahu apa yang sedang terjadi (sedang download model? sedang render? atau upload?).

**Sesudah (New Architecture):**
*   **Granular Stages**: Proses dibagi menjadi tahap-tahap kecil (Setup -> Inference -> Upload).
*   **Real-time Progress**: Progress bar berjalan mulus sesuai progress sebenarnya dari GPU.
*   **Transparansi**: Frontend bisa menampilkan label status yang spesifik (misal: "Menyiapkan Model...", "Sedang Membuat Video...").

---

## 2. Struktur Data Baru

Perubahan utama ada pada penambahan kolom `current_stage` dan penggunaan kolom `metadata` (JSONB) di database Supabase.

### Schema Database (Tabel: `projects`, `chatterbox_projects`, `tts_projects`)

| Kolom | Tipe | Deskripsi |
| :--- | :--- | :--- |
| `status` | `text` | Status global (`processing`, `finished`, `failed`). (Tetap ada untuk backward compatibility). |
| `progress` | `int` | Persentase global (0-100). |
| `current_stage` | `text` | **[BARU]** Key dari tahap yang sedang aktif (contoh: `INFERENCE`). |
| `metadata` | `jsonb` | **[BARU]** Menyimpan detail pipeline. |

### Struktur JSON Metadata

Objek `pipeline` disuntikkan ke dalam `metadata`:

```json
{
  "pipeline": {
    "stages": [
      {
        "key": "SETUP",
        "label": "Menyiapkan model...",
        "status": "completed",
        "completed_at": "2024-01-08T10:00:00Z"
      },
      {
        "key": "INFERENCE",
        "label": "Memproses AI...",
        "status": "active",
        "progress": 45
      },
      {
        "key": "UPLOADING",
        "label": "Menyimpan hasil...",
        "status": "pending"
      }
    ]
  }
}
```

---

## 3. Implementasi Per Fitur

### A. Video Generation (InfiniteTalk)
Fitur ini paling kompleks karena melibatkan durasi render yang lama.

*   **Pipa Proses (Pipeline Stages):**
    1.  `SETUP` (Bobot 20%): Download model, load LoRA, inisialisasi GPU.
    2.  `INFERENCE` (Bobot 50%): Proses denoising/generation frame-by-frame.
    3.  `POST_PROCESS` (Bobot 15%): Menggabungkan video + audio menggunakan FFmpeg.
    4.  `UPLOADING` (Bobot 15%): Upload ke Cloudinary dan update DB.

*   **Perbaikan Progress Real-time:**
    *   Sebelumnya: Progress stuck di 0% sampai selesai.
    *   Sekarang: Progress bar bergerak mulus berkat **Callback Injection** ke dalam loop `multitalk.py`.
    *   Logika: `Global Progress = (Frame Saat Ini / Total Frame) * 100%`.

### B. Chatterbox (Voice Cloning)
*   **Pipa Proses:**
    1.  `ANALYSIS` (Bobot: 10%): Menganalisa file audio referensi (durasi, noise).
    2.  `SYNTHESIS` (Bobot 60%): Generate suara menggunakan model XTTS/Chatterbox.
    3.  `UPLOADING` (Bobot 30%): Upload hasil wav ke Cloudinary.

### C. Kokoro TTS
*   **Pipa Proses:**
    1.  `TEXT_PROCESSING`: Normalisasi teks.
    2.  `GENERATION`: Generasi audio via model Kokoro.
    3.  `UPLOADING`: Simpan file.

---

## 4. Perubahan API Endpoint

Semua endpoint yang mengembalikan objek Project (`POST create`, `GET list`, `GET detail`) sekarang memiliki struktur respons baru.

### Response Structure

**Sebelumnya:**
```json
{
  "id": "123",
  "status": "processing",
  "progress": 0
}
```

**Sesudah (Standardized):**
API Router secara otomatis mengangkat objek `pipeline` dari `metadata` agar lebih mudah diakses frontend.

```json
{
  "id": "123",
  "status": "processing",
  "progress": 45,
  "current_stage": "INFERENCE",
  "pipeline": {
    "stages": [
      { "key": "SETUP", "label": "Selesai", "status": "completed" },
      { "key": "INFERENCE", "label": "Membuat video...", "status": "active" },
      ...
    ]
  }
}
```

### Affected Endpoints
1.  **Video Talking Head**:
    *   `POST /api/v1/projects/`
    *   `GET /api/v1/projects/{id}`
    *   `GET /api/v1/projects/` (List)
2.  **Chatterbox**:
    *   `POST /api/v1/audio/chatterbox/tts/generate`
    *   `GET /api/v1/audio/chatterbox/projects`
3.  **Kokoro TTS**:
    *   `POST /api/v1/audio/kokoro/generate`
    *   `GET /api/v1/audio/kokoro/`

---

## 5. Kesimpulan Teknis

Perubahan ini membuat aplikasi:
1.  **Lebih Responsif**: User mendapat feedback visual seketika.
2.  **Lebih Robust**: Jika error terjadi di tahap tertentu (misal `UPLOADING`), kita bisa tahu persis di mana macetnya dari `current_stage`.
3.  **Backward Compatible**: Field `status` lama tetap ada, sehingga aplikasi lama tidak langsung rusak, tapi disarankan migrasi ke UI berbasis `pipeline`.
