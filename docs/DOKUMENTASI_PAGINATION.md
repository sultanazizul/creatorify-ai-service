# Dokumentasi Implementasi Cursor Pagination

Dokumen ini menjelaskan perubahan arsitektur API dari sistem **Limit-Based** (sedot semua/limit saja) menjadi **Cursor-Based Pagination** untuk mendukung *infinite scrolling* dan kinerja database yang lebih optimal.

## 1. Latar Belakang & Logika
Sebelumnya, endpoint list kita hanya menggunakan `limit`.
- **Masalah**: Frontend hanya bisa mengambil 20 item pertama. Tidak ada cara untuk mengambil item ke-21 dst.
- **Solusi**: Kita menggunakan **Cursor Pagination**.
- **Logika**:
    - Cursor adalah penanda posisi terakhir (dalam hal ini timestamp `created_at`).
    - Saat Client meminta Halaman 2, Client mengirim `cursor=TIMESTAMP_TERAKHIR`.
    - Backend mencari data: `WHERE created_at < cursor LIMIT 20`.
    - Ini jauh lebih cepat dan akurat daripada `OFFSET` page.

## 2. Perbedaan Struktur Response (Before vs After)

### SEBELUMNYA (Array List Biasa)
Response langsung mengembalikan Array. Tidak ada info apakah masih ada data selanjutnya.
```json
// GET /projects?limit=2
[
  { "id": "1", "title": "Video A" },
  { "id": "2", "title": "Video B" }
]
```

### SEKARANG (Enveloped Response)
Response dibungkus dalam object ("Envelope") yang berisi data dan metadata cursor.
```json
// GET /projects?limit=2
{
  "items": [
    { "id": "1", "title": "Video A", "created_at": "2024-01-01T12:00:00Z" },
    { "id": "2", "title": "Video B", "created_at": "2024-01-01T11:00:00Z" }
  ],
  "next_cursor": "2024-01-01T11:00:00Z", // Timestamp dari item terakhir (Video B)
  "has_more": true                       // Menandakan masih ada data lagi di DB
}
```

## 3. Daftar Endpoint yang Berubah
Endpoint berikut telah diubah menjadi format baru ini. Pastikan Frontend menyesuaikan pembacaan responsenya.

1.  **Video Projects**
    - `GET /api/v1/video/talking-head/projects/`
2.  **Chatterbox (TTS/Voice Cloning) Projects**
    - `GET /api/v1/audio/chatterbox/projects`
3.  **Kokoro TTS Projects**
    - `GET /api/v1/audio/kokoro/`
4.  **Avatars**
    - `GET /api/v1/avatars/`
5.  **Voice Library Samples**
    - `GET /api/v1/audio/voice-library/`

## 4. Panduan Penggunaan (Frontend Integration)

### Langkah 1: Request Halaman Pertama
Panggil endpoint tanpa cursor.
```http
GET /api/v1/video/talking-head/projects/?limit=20
```
**Response:** Simpan `items` ke state list Anda, dan simpan `next_cursor` ke variable state.

### Langkah 2: Cek Apakah Perlu Load More
Lihat value `has_more`.
- Jika `true`: Tampilkan tombol "Load More" atau aktifkan scroll listener.
- Jika `false`: Sembunyikan tombol, data sudah habis.

### Langkah 3: Request Halaman Berikutnya
Saat user scroll ke bawah, panggil endpoint lagi dengan parameter `cursor` yang didapat dari Langkah 1.
```http
GET /api/v1/video/talking-head/projects/?limit=20&cursor=2024-01-01T11:00:00Z
```
**Response:**
1. Gabungkan `items` baru ke list yang sudah ada (`previousList + newList`).
2. Update variable state `next_cursor` dengan nilai yang baru.
3. Update status `has_more`.

## 5. Contoh Implementasi Logic (Pseudo-Code)

```javascript
let allProjects = [];
let nextCursor = null;
let hasMore = true;

async function loadProjects() {
  if (!hasMore) return;

  // Bangun URL
  let url = "/api/v1/video/talking-head/projects/?limit=20";
  if (nextCursor) {
    url += `&cursor=${nextCursor}`;
  }

  // Fetch API
  const response = await fetch(url);
  const data = await response.json();

  // Update State
  allProjects = [...allProjects, ...data.items];
  nextCursor = data.next_cursor;
  hasMore = data.has_more;
  
  renderUI(allProjects);
}
```
