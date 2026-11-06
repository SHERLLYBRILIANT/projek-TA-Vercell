# DEBUGGING: Halaman "Informasi Model AI" tidak muncul

## Kemungkinan Penyebab

### 1. User belum login
- Route `/api/model_info` memerlukan `@login_required`
- Jika belum login, fetch akan dapat response redirect (bukan JSON)
- **Solusi:** Pastikan sudah login sebelum akses halaman

### 2. Browser console error
- JavaScript error akan menghentikan seluruh script
- **Solusi:** Buka DevTools (F12) → Console tab → lihat error merah

### 3. Race condition dalam rendering
- `renderOverviewTab()` dipanggil sebelum DOM siap
- **Solusi:** Sudah ditambahkan `setTimeout` di loadModelData()

### 4. File model_evaluation.json tidak ada
- Jika file tidak ada, Flask akan return 404
- **Solusi:** Cek file ada di `models/model_evaluation.json`

## Langkah-langkah Testing

### Step 1: Pastikan sudah login
1. Buka aplikasi SiGizi di `http://localhost:5000`
2. Login dengan username & password yang benar
3. Baru akses menu "Informasi Model AI"

### Step 2: Buka DevTools
1. Tekan **F12** untuk buka Developer Tools
2. Pergi ke tab **Console**
3. Harus TIDAK ada error merah

### Step 3: Periksa API response
1. Di tab **Network** (F12)
2. Reload halaman (Ctrl+R)
3. Cari request ke `/api/model_info` (atau `/api/model_info_test`)
4. Klik request tersebut
5. Lihat tab **Response** - harus `{"success": true, "data": {...}}`

### Step 4: Manual test API (gunakan test endpoint)
```bash
# Window CMD / PowerShell
curl http://localhost:5000/api/model_info_test
# Harus menampilkan JSON dengan success=true
```

Atau buka di browser:
```
http://localhost:5000/api/model_info_test
```

## Perubahan Terbaru

### app.py
- Tambah better error handling di `/api/model_info` (cek file exists, JSON decode error)
- Tambah test endpoint `/api/model_info_test` (tanpa login requirement)
- Gunakan `encoding='utf-8'` saat read file

### static/model_info.js
- Tambah extensive logging di semua fungsi (`console.log`)
- Tambah delay pada render (`setTimeout`) untuk ensure DOM ready
- Tambah error handling di Chart initialization (`try/catch`)
- Perbaiki DOMContentLoaded listener (remove event listener yang tidak ada)

### models/model_evaluation.json
- Sudah valid JSON ✓
- Sudah memiliki struktur `model_artifacts`, `training_info` ✓

## Debugging Console Output

Kalau berhasil, di browser console harus tampil log seperti ini:
```
[model_info.js] DOMContentLoaded fired
[model_info.js] Fetching /api/model_info...
[model_info.js] API response: {success: true, data: {...}}
[model_info.js] modelData loaded: {model_name: "TabNet", ...}
[renderOverviewTab] Starting render with modelData keys: [...]
[renderOverviewTab] Summary updated
[renderOverviewTab] Metric cards updated
[renderOverviewTab] chartParams created
[renderOverviewTab] chartEpochs created
[renderOverviewTab] chartAvgMetrics created
[renderOverviewTab] Render complete
```

Kalau ada error, log akan menunjukkan:
```
[ERROR] HTTP 401 Unauthorized
[renderOverviewTab] modelData is null/undefined
[renderOverviewTab] chartParams element or artifacts.outputs not found
```

## Quick Test: API Test Page

Buka di browser (saat sudah login):
```
http://localhost:5000/test_model_info.html
```

Halaman ini akan:
1. Fetch `/api/model_info`
2. Log semua response ke halaman
3. Tunjukkan jika ada error

## Next Steps Kalau Masih Error

1. **Cek console.log output** - lihat di mana dia berhenti
2. **Cek Network tab** - apa response dari API?
3. **Cek HTML structure** - apakah element id ada? (overviewSummary, chartParams, etc)
4. **Cek Chart.js** - apakah Canvas element terrender?

