# Kamus Data (*Data Dictionary*) — Kelompok 25

Dokumen ini mendokumentasikan secara menyeluruh skema, sumber, aturan validasi, dan definisi seluruh atribut data pada empat lapisan arsitektur proyek **Dashboard Analitik & Model Prediksi Harga Cabai Merah Keriting Kota Medan**:

1. **Sumber Data Mentah (`data/raw/`)**
2. **Dataset Bersih Terintegrasi (`data/processed/01_clean.csv`)**
3. **Data Warehouse Skema Bintang SQLite (`warehouse/cabai_medan.db`)**
4. **Fitur Rekayasa & Fitur Terpilih Pemodelan (`data/processed/05_fitur_final_uas.json` & `models/train.py`)**

---

## 1. Ikhtisar Sumber & Cakupan Dataset

| Komponen | Sumber Resmi | Cakupan & Granularitas | Statistik Kualitas Data |
|---|---|---|---|
| **Harga Pangan Harian** | **PIHPS Nasional – Bank Indonesia** (`data/raw/*.xlsx`, 4 file tingkat pasar) | Kota Medan, komoditas **Cabai Merah Keriting** (serta agregat Cabai Merah), 4 level pasar (`Produsen`, `Pedagang Besar`, `Pasar Tradisional`, `Pasar Modern`), hari kerja | 10.437 baris mentah -> diselaraskan ke periode irisan lengkap **31-12-2019 s.d. 29-01-2026** (1.588 hari kerja × 4 pasar = **6.352 baris**). Nilai kosong teks `'-'` (1.970 baris mentah) pada hari libur/celah diatasi dengan pemangkasan awal & *forward-fill* terarah (**92 baris imputasi** / `1,45%` dari data bersih). |
| **Cuaca Harian Medan** | **Open-Meteo Historical Weather API** (`open-meteo-3.55N98.68E28m (1).csv`, lisensi CC BY 4.0) | Koordinat `3,55° LU, 98,68° BT`, elevasi `28 m`, harian kalender | 2.402 baris (`2019-07-04` s.d. `2026-01-29`), **0 missing value** di seluruh kolom cuaca. |
| **Dataset Pemodelan (`Pasar Tradisional`)** | Turunan dari `v_harga_lengkap` / `01_clean.csv` + `01_cuaca_harian.csv` | Focus target pada tingkat eceran **Pasar Tradisional** (`2020-01-28` s.d. `2026-01-29` setelah membuang 20 hari kerja awal untuk jendela lag) | **1.568 baris** (`1.286` baris latih `<= 2024-12-31`; `282` baris uji `>= 2025-01-01`). |

---

## 2. Kamus Kolom Dataset Bersih (`data/processed/01_clean.csv`)

Grain tabel: **1 baris = 1 pengamatan harian pada 1 kategori pasar** (`6.352` baris × `10` kolom).

| No | Nama Kolom | Tipe Data | Satuan / Domain | Deskripsi & Aturan Validasi |
|---|---|---|---|---|
| 1 | `Tanggal` | `date` (`YYYY-MM-DD`) | Tanggal kalender hari kerja | Tanggal pengamatan harga (`2019-12-31` s.d. `2026-01-29`, 1.588 hari kerja unik). Tidak boleh duplikat untuk pasangan `(Tanggal, Kategori_Pasar)`. |
| 2 | `Kategori_Pasar` | `string` (kategorikal berurutan) | `Produsen`, `Pedagang Besar`, `Pasar Tradisional`, `Pasar Modern` | Posisi pelaku dalam rantai pasok Kota Medan. Median harga bertingkat naik: Produsen `Rp22.000`, Pedagang Besar `Rp28.000`, Pasar Tradisional `Rp33.700`, Pasar Modern `Rp45.950`. |
| 3 | `Komoditas` | `string` | `Cabai Merah Keriting` | Label komoditas terstandarisasi setelah normalisasi penulisan teks dari file mentah PIHPS. |
| 4 | `Harga_Cabai_Merah_Keriting` | `float64` / `int` | Rupiah per kg (`Rp/kg`) | **Variabel target utama ($y_t$)**. Rentang aktual: `Rp7.500`–`Rp115.500/kg` (Pasar Tradisional: `Rp14.900`–`Rp109.500/kg`, rata-rata `Rp37.853/kg`). Wajib bernilai `> 0`. |
| 5 | `Harga_Cabai_Merah_Agregat` | `float64` | Rupiah per kg (`Rp/kg`) | Harga agregat kategori Cabai Merah di PIHPS pada hari yang sama. **Dilarang dipakai sebagai fitur model** karena $99{,}9\%$ identik/bocor dengan target ($r = 0{,}9998$ di Pasar Tradisional). |
| 6 | `Kode_Cuaca_WMO` | `int64` | Kode WMO (`0`–`99`) | Klasifikasi kondisi cuaca harian Kota Medan dari Open-Meteo (dominan hujan ringan–lebat dan berawan). |
| 7 | `Suhu_Rata2_C` | `float64` | Derajat Celsius (`°C`) | Suhu udara harian rata-rata pada ketinggian 2 meter di Kota Medan. |
| 8 | `Curah_Hujan_mm` | `float64` | Milimeter (`mm/hari`) | Total curah hujan kalender harian (`precipitation_sum`). Bernilai `>= 0`. |
| 9 | `Kecepatan_Angin_Maks_kmh` | `float64` | `km/jam` | Kecepatan angin maksimum harian pada ketinggian 10 meter. Bernilai `>= 0`. |
| 10 | `Is_Imputasi` | `int64` (`0` / `1`) | Flag biner | `1` jika `Harga_Cabai_Merah_Keriting` hari tersebut diisi melalui *forward-fill* per pasar (total 92 baris / `1,45%`: Produsen 4, Pedagang Besar 12, Pasar Tradisional 57, Pasar Modern 18); `0` jika data asli PIHPS. |

---

## 3. Kamus Skema Bintang Data Warehouse (`warehouse/cabai_medan.db`)

Database SQLite dibangun oleh pipeline ETL (`etl/run_etl.py`) sesuai DDL [warehouse/schema.sql](../warehouse/schema.sql) dengan arsitektur **1 Tabel Fakta + 3 Tabel Dimensi + 1 SQL View Analitik**.

### 3.1 Tabel Dimensi `dim_tanggal` (13 kolom)

| Kolom | Tipe SQL | Keterangan |
|---|---|---|
| `tanggal_key` | `INTEGER PRIMARY KEY` | Surrogate key berformat `YYYYMMDD` (contoh: `20250102`). |
| `tanggal` | `TEXT UNIQUE NOT NULL` | Format ISO `YYYY-MM-DD`. |
| `tahun`, `kuartal`, `bulan`, `hari` | `INTEGER NOT NULL` | Atribut numerik kalender (`kuartal` 1–4, `bulan` 1–12, `hari` 1–31). |
| `nama_bulan` | `TEXT NOT NULL` | Nama bulan dalam Bahasa Indonesia (`Januari` .. `Desember`). |
| `hari_ke_dalam_minggu` | `INTEGER NOT NULL` | Indeks hari `0` (Senin) sampai `6` (Minggu). |
| `nama_hari` | `TEXT NOT NULL` | Nama hari dalam Bahasa Indonesia (`Senin` .. `Minggu`). |
| `akhir_pekan` | `INTEGER` (`0`/`1`) | Penanda Sabtu/Minggu (`1`) vs hari kerja (`0`). |
| `musim` | `TEXT NOT NULL` | Klasifikasi musim wilayah Medan (`Hujan` / `Kemarau`). |
| `is_hari_libur` | `INTEGER` (`0`/`1`) | Penanda hari libur nasional / hari raya keagamaan. |
| `nama_libur` | `TEXT` | Keterangan nama hari libur (`NULL` bila hari kerja biasa). |

### 3.2 Tabel Dimensi `dim_pasar` (5 kolom)

| Kolom | Tipe SQL | Keterangan |
|---|---|---|
| `pasar_key` | `INTEGER PRIMARY KEY` | Kunci dimensi kategori pasar (`1`..`4`). |
| `nama_pasar` | `TEXT UNIQUE NOT NULL` | `Produsen`, `Pedagang Besar`, `Pasar Tradisional`, atau `Pasar Modern`. |
| `tingkat_rantai_pasok` | `TEXT NOT NULL` | Deskripsi peran rantai distribusi (`Hulu`, `Grosir`, `Eceran Tradisional`, `Eceran Modern`). |
| `urutan_rantai` | `INTEGER UNIQUE NOT NULL` | Peringkat aliran distribusi dari hulu ke hilir (`1`..`4`). |
| `keterangan` | `TEXT` | Catatan pelaporan sumber PIHPS-BI untuk pasar terkait. |

### 3.3 Tabel Dimensi `dim_cuaca` (8 kolom)

| Kolom | Tipe SQL | Keterangan |
|---|---|---|
| `cuaca_key` | `INTEGER PRIMARY KEY` | Kunci harian cuaca berformat `YYYYMMDD`. |
| `tanggal` | `TEXT UNIQUE NOT NULL` | Tanggal ISO `YYYY-MM-DD` (berelasi 1:1 dengan `dim_tanggal`). |
| `kode_wmo` | `INTEGER NOT NULL` | Kode cuaca standar WMO dari Open-Meteo. |
| `deskripsi_cuaca` | `TEXT NOT NULL` | Terjemahan deskripsi WMO dalam Bahasa Indonesia (Berawan, Gerimis, Hujan Ringan, Hujan Sedang, Hujan Lebat). |
| `suhu_rata2_c` | `REAL NOT NULL` | Suhu rata-rata harian Kota Medan (`°C`). |
| `curah_hujan_mm` | `REAL NOT NULL` | Curah hujan harian (`mm`). |
| `kecepatan_angin_maks_kmh` | `REAL NOT NULL` | Kecepatan angin maksimum (`km/jam`). |
| `kategori_hujan` | `TEXT NOT NULL` | Diskretisasi intensitas hujan: `Tidak Hujan`, `Hujan Ringan`, `Hujan Sedang`, `Hujan Lebat`. |

### 3.4 Tabel Fakta `fact_harga_harian` (11 kolom) & View `v_harga_lengkap`

| Kolom | Tipe SQL | Keterangan |
|---|---|---|
| `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | Kunci primer surrogate fakta. |
| `tanggal_key`, `pasar_key`, `cuaca_key` | `INTEGER NOT NULL (FK)` | Foreign key ke ketiga tabel dimensi (kombinasi `(tanggal_key, pasar_key)` dijamin `UNIQUE`). |
| `harga_cabai_keriting` | `INTEGER NOT NULL` | Harga Cabai Merah Keriting (`Rp/kg`, `> 0`). |
| `harga_cabai_agregat` | `INTEGER NOT NULL` | Harga agregat Cabai Merah PIHPS (`Rp/kg`, `> 0`). |
| `perubahan_harian` | `REAL` | Selisih harga terhadap hari kerja sebelumnya pada pasar yang sama (`Rp/kg`). |
| `persen_perubahan` | `REAL` | Persentase perubahan harian per pasar (`%`). |
| `markup_thd_produsen` | `REAL NOT NULL` | Selisih harga pasar terkait terhadap harga `Produsen` pada tanggal yang sama (`Rp/kg`). |
| `is_imputasi` | `INTEGER` (`0`/`1`) | Indikator nilai hasil *forward-fill*. |

Seluruh halaman Dashboard Streamlit (`app/`) dan skrip pemodelan (`models/train.py`) membaca gabungan fakta dan dimensi melalui SQL View **`v_harga_lengkap`** (dengan *auto-fallback* ke `data/processed/01_clean.csv` bila file `.db` tidak tersedia).

---

## 4. Kamus Fitur Pemodelan & Protokol Anti-Leakage (`notebooks/` & `models/`)

Dari `35` fitur kandidat hasil *feature engineering* (dibuang 2 kolom non-fitur: `Harga_Cabai_Merah_Agregat` karena kebocoran target dan `Is_Imputasi` karena variansi *quasi-konstan* `98,43%`), proses seleksi konsensus (`voting >= 2` dari Lasso, RFECV, Korelasi Spearman, dan Mutual Information) menghasilkan **12 fitur model pohon** (`fitur_terpilih_tahap4`) dan **10 fitur model linear** (`fitur_untuk_model_linear`, bebas multikolinearitas dengan $\text{VIF} \le 9{,}61$ setelah membuang `Harga_MA7` VIF `147,7` dan `Harga_MA20` VIF `35,6`).

### 4.1 Daftar 12 Fitur Terpilih Pemodelan

| Fitur | Tipe & Paket | Rumus / Definisi | $\rho$ Spearman (vs Harga) | VIF Akhir (Linear) | Importance (RF) |
|---|---|---|---|---|---|
| `Harga_Lag1` | Numerik (Pohon & Linear) | $y_{t-1}$ pada kategori pasar yang sama | `0,9796` | `9,61` | `0,0698` |
| `Harga_MA7` | Numerik (**Khusus Pohon**) | $\frac{1}{7}\sum_{k=1}^{7} y_{t-k}$ per pasar | `0,9437` | *(Dibuang, 147,7)* | `0,0610` |
| `Harga_Lag5` | Numerik (Pohon & Linear) | $y_{t-5}$ (harga 1 minggu kerja lalu) | `0,9028` | `8,89` | `0,0431` |
| `TE_Pasar_Bulan` | Numerik (Pohon & Linear) | Out-of-fold Target Encoding `(Kategori_Pasar, Bulan)` dengan *smoothing* $m=20$ (di-fit ulang di tiap fold `TimeSeriesSplit`) | `0,6023` | `5,25` | `0,0092` |
| `Harga_MA20` | Numerik (**Khusus Pohon**) | $\frac{1}{20}\sum_{k=1}^{20} y_{t-k}$ per pasar | `0,8775` | *(Dibuang, 35,6)* | `0,0313` |
| `Harga_Lag20` | Numerik (Pohon & Linear) | $y_{t-20}$ (harga 1 bulan kerja lalu) | `0,6896` | `3,34` | `0,0463` |
| `Harga_Produsen_Lag1` | Numerik (Pohon & Linear) | Harga `Produsen` pada $t-1$ (sinyal pasokan hulu) | `0,5747` | `4,64` | `0,0131` |
| `Harga_PB_Lag1` | Numerik (Pohon & Linear) | Harga `Pedagang Besar` pada $t-1$ (sinyal modal grosir) | `0,6571` | `4,87` | `0,0279` |
| `Interaksi_Lag1_x_MusimHujan` | Interaksi (Pohon & Linear) | $\text{Harga\_Lag1} \times \mathbb{I}(\text{Bulan} \in \{9,10,11,12\})$ | — | `1,24` | **`0,5570`** |
| `Level_Rantai_Pasok` | Ordinal (Pohon & Linear) | `Produsen=1`, `Pedagang Besar=2`, `Pasar Tradisional=3`, `Pasar Modern=4` | `0,5798` | `6,01` | `0,0000` |
| `Hari_Menuju_Idul_Fitri` | Kalender (Pohon & Linear) | Jumlah hari kalender menuju tanggal Idul Fitri terdekat | — | `1,02` | `0,0643` |
| `Akumulasi_Hujan_7H` | Cuaca (Pohon & Linear) | $\sum_{d=1}^{7} \text{Curah\_Hujan}_{t-d}$ (7 hari kalender sebelum $t$, mm) | — | `1,22` | `0,0769` |

### 4.2 Protokol Pencegahan *Data Leakage*
1. **Batas Kausalitas Waktu ($\le t-1$):** Seluruh fitur lag harga, harga hulu, rata-rata bergerak, dan akumulasi curah hujan dihitung secara ketat menggunakan pengamatan hingga hari $t-1$ sebelum target $y_t$ terbentuk.
2. **Pemisahan Kronologis Ketat:** Latih murni pada `2020-01-28` s.d. `2024-12-31` ($n=1.286$ hari Pasar Tradisional) dan uji *hold-out* masa depan `2025-01-01` s.d. `2026-01-29` ($n=282$), tanpa pengocokan acak.
3. ***Target Encoding* di Dalam Lipatan CV:** Statistik `TE_Pasar_Bulan` dihitung hanya dari partisi *train* di setiap fold `TimeSeriesSplit(n_splits=5)` pada `models/train.py`.
4. **Target Perubahan Harian ($\Delta y_t$):** Seluruh model memprediksi selisih harian $\Delta y_t = y_t - \text{Harga\_Lag1}$ lalu dikonversi kembali ke satuan Rupiah ($\hat{y}_t = \text{Harga\_Lag1} + \widehat{\Delta y}_t$) untuk mencegah efek pembalikan skala (*scaling artifact*) saat tren harga menembus batas historis.
