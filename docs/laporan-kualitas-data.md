# Laporan Audit Kualitas Data — Sebelum vs Sesudah Cleaning & Validasi Warehouse

**Penyusun:** Dame Sisri Rumapea (41426085 — Ketua Kelompok & Lead Data Analitik/Warehouse)  
**Sumber Audit Resmi:** `data/processed/01_ringkasan.json`, `data/processed/02_ringkasan.json`, `docs/log_cleaning.csv`, dan `warehouse/cabai_medan.db`

---

## 1. Profil Sumber Data Mentah & Penyelarasan Periode

Dataset terintegrasi proyek dibangun dari dua sumber data publik utama yang berada pada folder `data/raw/`:
1. **Data Harga Harian PIHPS Nasional — Bank Indonesia (4 berkas Excel):**
   - Mencakup empat tingkat rantai pasok di Kota Medan: **Produsen**, **Pedagang Besar**, **Pasar Tradisional**, dan **Pasar Modern**.
   - Dalam format *wide* mentah (`20-10-2016` s.d. `21-10-2026`), ketika digabungkan ke format *long* menghasilkan **10.437 baris mentah × 11 kolom**.
   - Ditemukan **1.970 sel bertanda strip `'-'` (`18,88%`)** pada kolom `Harga_Keriting_teks`, **1.995 sel strip `'-'`** pada `Harga_Agregat_teks`, **3 tanggal implisit** (kolom tanggal yang hanya ada pada berkas Produsen tetapi tidak ada pada berkas tiga pasar lainnya), **16.909 sel angka bertipe teks berkoma**, spasi berlebih pada label `Komoditas`, serta **1 kesalahan input (*spike error*)** pada `2023-05-29`.
2. **Data Cuaca Harian Kota Medan — Open-Meteo (`3,55° LU, 98,68° BT`):**
   - Berkas CSV asli (`open-meteo-3.55N98.68E28m (1).csv`) berisi **3.667 baris mentah** dan berkas cuaca terkurasi (`data/processed/01_cuaca_harian.csv`) memuat **2.402 baris** observasi harian dengan **0 nilai hilang (`100%` lengkap)**.
   - Ditemukan **1 kolom duplikat identik** (`rain_sum (mm)` sama persis 100% dengan `precipitation_sum (mm)` pada seluruh `3.667` baris).
3. **Penyelarasan Periode Irisan (*Intersection Window*):**
   - Pasar Modern baru mulai disurvei secara konsisten pada akhir Desember 2019, sedangkan Produsen berhenti dilaporkan setelah 29 Januari 2026. Untuk mencegah *missing* struktural di awal/akhir seri, sebanyak **4.085 baris** di luar rentang irisan (`31-12-2019` s.d. `29-01-2026`) dibuang, menyisakan **6.352 baris bersih (`1.588` hari kerja × `4` kategori pasar)**.

---

## 2. Ringkasan Perbandingan Sebelum vs Sesudah Cleaning

| Dimensi / Indikator Kualitas | Sebelum Cleaning (Mentah Terintegrasi) | Sesudah Cleaning (`01_clean.csv` & SQLite) | Tindakan & Dampak |
|---|---:|---:|---|
| **Jumlah Baris** | 10.437 baris | **6.352 baris** | 4.085 baris di luar periode irisan dibuang (missing struktural) |
| **Jumlah Kolom** | 11 kolom | **10 kolom** | Kolom duplikat `rain_sum (mm)` dihapus; ditambah `Is_Imputasi` |
| **Rentang Tanggal** | 20-10-2016 s.d. 21-10-2026 | **31-12-2019 s.d. 29-01-2026** | Irisan seragam 1.588 hari kerja Senin–Jumat di 4 pasar |
| **Sel Harga Keriting Kosong (`'-'`)** | 1.970 sel (**18,88%**) | **0 sel (0,00%)** | Diimputasi *forward-fill* per pasar + ditandai `Is_Imputasi` |
| **Sel Harga Agregat Kosong (`'-'`)** | 1.995 sel | **0 sel (0,00%)** | Diimputasi *forward-fill* per pasar |
| **Sel Angka Berformat Teks Koma** | 16.909 sel | **0 sel** | Dikonversi ke numerik `int64` bebas koma |
| **Kesalahan Input (*Spike* 1 Hari)** | 1 kasus (`2023-05-29`) | **0 kasus** | Dikoreksi dari `30.200` → `19.400` + `Is_Imputasi = 1` |
| **Pelanggaran Aturan Domain** | 0 pelanggaran | **0 pelanggaran** | Lolos 9 aturan validitas harga, cuaca, kode WMO, & hari kerja |

---

## 3. Audit 4 Pilar Kualitas Data

### A. *Completeness* (Kelengkapan)
- **Mengapa Data Harga Kosong di Periode Irisan?** Audit pencocokan terhadap kalender hari libur nasional (`holidays` Indonesia) membuktikan bahwa kekosongan data harga bukanlah acak, melainkan bertepatan dengan hari libur nasional dan cuti bersama ($\le 2$ hari dari hari libur):
  - **Pasar Tradisional:** **98,2%** hari kosong terkait hari libur
  - **Produsen:** **75,0%** hari kosong terkait hari libur
  - **Pedagang Besar:** **58,3%** hari kosong terkait hari libur
  - **Pasar Modern:** **16,7%** hari kosong terkait hari libur
  - *(Pembanding: hanya **20,7%** dari seluruh hari kerja dalam periode yang berada $\le 2$ hari dari libur nasional).*
- **Data Cuaca:** Memiliki **0 nilai hilang** pada `Kode_Cuaca_WMO`, `Suhu_Rata2_C`, `Curah_Hujan_mm`, dan `Kecepatan_Angin_Maks_kmh`.

### B. *Consistency* (Konsistensi Format & Skema)
- Header tanggal pada berkas Excel PIHPS awalnya berformat teks berspasi (mis. `'20/ 10/ 2016'`) → dibersihkan dan di-parse menjadi tipe `datetime` standar ISO (`YYYY-MM-DD`).
- Nama komoditas yang mengandung spasi di akhir (`'Cabai Merah Keriting '`) diseragamkan dengan `.str.strip()` menjadi `'Cabai Merah Keriting'`.
- Nama kategori pasar dari 4 berkas Excel dengan penamaan tidak seragam diseragamkan menjadi tipe berurutan: `Produsen`, `Pedagang Besar`, `Pasar Tradisional`, `Pasar Modern`.
- Lima nama kolom cuaca disederhanakan dari format satuan/simbol (seperti `temperature_2m_mean (°C)`) menjadi pengenal bersih (`Suhu_Rata2_C`, `Curah_Hujan_mm`, `Kecepatan_Angin_Maks_kmh`, `Kode_Cuaca_WMO`).

### C. *Validity* (Validitas Domain)
Seluruh **6.352 baris** hasil pembersihan lolos 100% dari **9 aturan domain ekonomi & meteorologi**:
- `Harga_Cabai_Merah_Keriting > 0` dan `<= Rp250.000/kg` (0 pelanggaran)
- `Harga_Cabai_Merah_Agregat > 0` (0 pelanggaran)
- `Suhu_Rata2_C` antara `15–40 °C`, `Curah_Hujan_mm` antara `0–300 mm/hari`, `Kecepatan_Angin_Maks_kmh` antara `0–120 km/jam` (0 pelanggaran)
- `Kode_Cuaca_WMO` valid sesuai tabel WMO resmi dan seluruh tanggal merupakan hari kerja Senin–Jumat (0 pelanggaran).

### D. *Uniqueness* (Keunikan)
- Menghapus kolom `rain_sum (mm)` karena redundan 100% dengan `precipitation_sum (mm)`.
- Pemeriksaan kunci komposit `(Tanggal, Kategori_Pasar)` menemukan **0 duplikat baris** baik sebelum maupun sesudah normalisasi format tanggal.

---

## 4. Uji Empiris Strategi Imputasi & Kebijakan Outlier

### A. Perbandingan 4 Metode Imputasi (Simulasi *Masking* 5% Harga Diketahui)

| Strategi Imputasi | MAE (Rp/kg) | Memakai Data Masa Depan? | Keputusan |
|---|---:|:---:|---|
| **Forward-fill per pasar** | **1.469** | Tidak | **Dipilih** (bebas *data leakage* kronologis) |
| Interpolasi linear per pasar | 1.189 | Ya (nilai sesudahnya) | Ditolak (berisiko bocor masa depan) |
| Median per pasar | 12.010 | Ya (seluruh periode) | Ditolak (galat terlalu besar) |
| Median global | 13.817 | Ya (seluruh periode) | Ditolak (mengabaikan perbedaan pasar) |

Implementasi *forward-fill* per pasar (ditambah koreksi 1 *spike error*) menghasilkan **92 baris berstatus `Is_Imputasi = 1` (`1,45%` dari 6.352 baris)**, terdiri atas **4** baris Produsen, **12** Pedagang Besar, **58** Pasar Tradisional (57 hari libur + 1 *spike*), dan **18** Pasar Modern.

### B. Penanganan Outlier (Kesalahan Input vs Ekstrem Nyata)
1. **1 *Spike Error* (`2023-05-29`, Pasar Tradisional):** Terdeteksi lonjakan satu hari >40% (`Rp19.400 → Rp30.200 → Rp19.400`) lalu langsung kembali ke level semula (<10% selisih hari sebelum dan sesudah). Dikoreksi menggunakan nilai hari sebelumnya (`Rp19.400`) dan ditandai `Is_Imputasi = 1`.
2. **Outlier Ekstrem Riil Dipertahankan (*No Capping*):** Terdapat **372 outlier IQR harga** (`Produsen` 108, `Pedagang Besar` 100, `Pasar Tradisional` 94, `Pasar Modern` 70) serta **86 outlier IQR cuaca**. Nilai ekstrem ini **sengaja tidak dipangkas** karena bertahan berminggu-minggu dan terjadi serentak lintas pasar (seperti krisis Juli 2022 Rp85.267/kg dan hujan ekstrem 2025), yang justru menjadi pola gejolak utama yang harus diprediksi oleh model *machine learning*.

---

## 5. Ringkasan Log Cleaning (`docs/log_cleaning.csv`)

Seluruh proses pembersihan terekam dalam **16 entri log resmi** di `docs/log_cleaning.csv` mencakup tahap **2a–2b** (*missing* struktural & hari libur), tahap **3** (penghapusan kolom duplikat & verifikasi duplikat kunci), tahap **4** (standardisasi 5 tipe & format kolom), tahap **5** (validasi 9 aturan domain & pembuangan tanggal tunggal `21/10/2026`), serta tahap **6** (koreksi 1 *spike* salah ketik dan preservasi 372 outlier harga serta 86 outlier cuaca).

---

## 6. Validasi Integritas Skema Bintang & Kunci Asing di SQLite (`warehouse/cabai_medan.db`)

Pipeline otomatis `etl/run_etl.py` mereplikasi seluruh langkah transformasi dari `data/raw/` dan memuat hasilnya ke `warehouse/cabai_medan.db` dengan `PRAGMA foreign_keys = ON`:

| Objek Database | Jenis | Jumlah Baris | Hasil Validasi Integritas |
|---|---|---:|---|
| `dim_tanggal` | Dimensi | 1.588 | `tanggal_key` unik (YYYYMMDD), 0 NULL pada kolom wajib |
| `dim_pasar` | Dimensi | 4 | `urutan_rantai` 1–4 lengkap & unik |
| `dim_cuaca` | Dimensi | 1.588 | `cuaca_key` unik, 0 NULL pada variabel cuaca |
| `fact_harga_harian` | Fakta | 6.352 | `PRAGMA foreign_key_check` = **0 pelanggaran**, `UNIQUE(tanggal_key, pasar_key)` terpenuhi |
| `v_harga_lengkap` | SQL View | 6.352 | **100% identik** (harga, cuaca, `is_imputasi`) dengan `data/processed/01_clean.csv` |
