# Model Card — Prediksi Harga Harian Cabai Merah Keriting Pasar Tradisional Kota Medan

**Penyusun:** Dame Sisri Rumapea (41426085 — Ketua Kelompok & Lead Data Analitik, Kontribusi Lintas Lapisan Data Science)  
**Sumber Metrik Resmi:** `models/metrics.json`, `models/test_predictions.csv`, `data/processed/04_ringkasan.json`, `data/processed/05_ringkasan.json`, dan `notebooks/07_evaluasi_dan_error_analysis.ipynb`

---

## 1. Detail & Tujuan Model

| Atribut | Spesifikasi |
|---|---|
| **Nama Model Produksi (`best_model`)** | **Random Forest Regressor** (`criterion="absolute_error"`, `n_estimators=300`, `max_depth=8`, `min_samples_leaf=50`, `max_features=0.5`) |
| **Pembanding Baseline** | **Naive (Persistence)** dan **Ridge Regression** (`ridge__alpha=5000.0`) |
| **Model Pembanding Lanjutan** | **XGBoost** (`objective="reg:pseudohubererror"`, `n_estimators=200`, `max_depth=2`, `learning_rate=0.015`, `min_child_weight=25`, `subsample=0.75`, `colsample_bytree=1.0`, `huber_slope=300.0`) dan **LightGBM** (`objective="mae"`, `n_estimators=200`, `num_leaves=7`, `max_depth=4`, `learning_rate=0.025`, `min_child_samples=30`, `subsample=1.0`, `subsample_freq=1`, `colsample_bytree=0.75`, `alpha=600.0`) |
| **Strategi Target** | Memprediksi perubahan harga harian ($\Delta y_t = y_t - \text{Harga\_Lag1}$), kemudian mengonversi kembali ke skala Rupiah ($\hat{y}_t = \text{Harga\_Lag1} + \widehat{\Delta y}_t$) agar model berbasis pohon tetap mampu melakukan ekstrapolasi pada rezim harga tinggi baru |
| **Pasar Fokus** | **Pasar Tradisional** Kota Medan |
| **Tujuan Penggunaan** | Memberikan estimasi harga cabai merah keriting pada hari kerja berikutnya ($t$) berdasarkan informasi hingga hari kerja sebelumnya ($t-1$) melalui halaman `app/pages/04_Prediksi_Harga.py` untuk mendukung intervensi dini TPID dan perencanaan stok pelaku pasar |

---

## 2. Pengguna Sasaran & Penggunaan di Luar Cakupan (*Out-of-Scope*)

- **Pengguna Sasaran:**
  1. **TPID & Dinas Ketahanan Pangan Kota Medan:** Pemantauan potensi gejolak harga harian serta pemicu operasi pasar ketika sinyal cuaca ekstrem aktif.
  2. **Pedagang Besar & Pedagang Eceran:** Perencanaan volume pengadaan dan pengendalian risiko perubahan margin jangka pendek (H+1).
  3. **Konsumen Rumah Tangga:** Edukasi pergerakan harga wajar antar-pasar dan pemilihan waktu belanja optimal.
- **Penggunaan di Luar Cakupan (*Out-of-Scope*):**
  - Tidak dirancang untuk meramalkan harga komoditas lain (mis. cabai rawit, bawang merah) atau pasar di luar Kota Medan tanpa kalibrasi ulang dan pelatihan ulang (*retraining*).
  - Tidak ditujukan untuk peramalan horizon panjang (>7 hari ke depan) karena seluruh fitur lag dan akumulasi cuaca dibangun untuk prediksi satu hari kerja berikutnya.
  - Tidak boleh digunakan sebagai dasar spekulasi atau penimbunan stok yang merugikan stabilitas pasokan pangan masyarakat.

---

## 3. Spesifikasi Data Latih, Data Uji, & Skema Validasi

- **Sumber Data:** SQLite *Data Warehouse* `warehouse/cabai_medan.db` (*view* `v_harga_lengkap`) dengan mekanisme *auto-fallback* ke `data/processed/01_clean.csv` (`6.352` baris terkurasi: `1.588` hari kerja × `4` kategori pasar).
- **Pembagian Kronologis Murni (*Out-of-Time Split*, Bebas *Data Leakage*):**
  - **Data Latih (*Train Set*):** `2020-01-28` s.d. `2024-12-31` ($n = 1.286$ hari kerja Pasar Tradisional).
  - **Data Uji (*Test Set*):** `2025-01-01` s.d. `2026-01-29` ($n = 282$ hari kerja Pasar Tradisional).
- **Validasi Silang (*Cross-Validation*):** `TimeSeriesSplit(n_splits=5)` pada data latih dengan *out-of-fold target encoding* (`TE_Pasar_Bulan`) yang di-fit ulang di setiap *fold*.
- **Pencegahan Kebocoran Data:** Fitur `Harga_Cabai_Merah_Agregat` (99,92% identik dengan target pada Pasar Tradisional) dan kolom *quasi-konstan* `Is_Imputasi` (98,43% bernilai 0) telah dibuang sebelum pelatihan model.

---

## 4. Spesifikasi 12 Fitur Model Pohon & 10 Fitur Model Linear ($\text{VIF} \le 9,61$)

Untuk model linear (*Ridge Regression*), dua fitur *moving average* (`Harga_MA7` VIF awal = 147,7; `Harga_MA20` VIF saat dibuang = 35,6) dihapus secara iteratif hingga seluruh 10 fitur tersisa memiliki $\text{VIF} \le 9,61$. Model pohon (*Random Forest*, *XGBoost*, *LightGBM*) menggunakan seluruh 12 fitur konsensus.

| No | Nama Fitur | Deskripsi Singkat | Model Pohon (12) | Model Linear (10) | VIF Akhir (Linear) | Kontribusi Fitur RF (%) |
|---:|---|---|:---:|:---:|---:|---:|
| 1 | `Interaksi_Lag1_x_MusimHujan` | Interaksi harga kemarin × indikator musim hujan Sep–Des | Ya | Ya | 1,24 | **55,70%** |
| 2 | `Akumulasi_Hujan_7H` | Akumulasi curah hujan 7 hari terakhir hingga $t-1$ (mm) | Ya | Ya | 1,22 | **7,69%** |
| 3 | `Harga_Lag1` | Harga Pasar Tradisional 1 hari kerja sebelumnya (Rp/kg) | Ya | Ya | 9,61 | **6,98%** |
| 4 | `Hari_Menuju_Idul_Fitri` | Jarak hari kalender menuju Idul Fitri terdekat | Ya | Ya | 1,02 | **6,43%** |
| 5 | `Harga_MA7` | Rata-rata bergerak harga 7 hari kerja terakhir (Rp/kg) | Ya | Tidak | — | **6,10%** |
| 6 | `Harga_Lag20` | Harga Pasar Tradisional 20 hari kerja sebelumnya (Rp/kg) | Ya | Ya | 3,34 | **4,63%** |
| 7 | `Harga_Lag5` | Harga Pasar Tradisional 5 hari kerja sebelumnya (Rp/kg) | Ya | Ya | 8,89 | **4,31%** |
| 8 | `Harga_MA20` | Rata-rata bergerak harga 20 hari kerja terakhir (Rp/kg) | Ya | Tidak | — | **3,13%** |
| 9 | `Harga_PB_Lag1` | Harga Pedagang Besar 1 hari kerja sebelumnya (Rp/kg) | Ya | Ya | 4,87 | **2,79%** |
| 10 | `Harga_Produsen_Lag1` | Harga tingkat Produsen 1 hari kerja sebelumnya (Rp/kg) | Ya | Ya | 4,64 | **1,31%** |
| 11 | `TE_Pasar_Bulan` | *Target encoding* musiman rata-rata harga per pasar × bulan | Ya | Ya | 5,25 | **0,92%** |
| 12 | `Level_Rantai_Pasok` | Kode ordinal tingkat rantai pasok (konstan pada fokus Pasar Tradisional = 3) | Ya | Ya | 6,01 | **0,00%** |

---

## 5. Tabel Evaluasi Metrik Lengkap 5 Model (CV & Data Uji 2025–2026)

Pemilihan `best_model` ditentukan berdasarkan **CV MAE terendah** di antara model *machine learning* pada `TimeSeriesSplit(n_splits=5)` untuk menghindari kebocoran seleksi dari data uji.

| Model | Fitur | CV MAE (Rp) | CV RMSE (Rp) | CV MAPE (%) | CV $R^2$ | Test MAE (Rp) | Test RMSE (Rp) | Test MAPE (%) | Test $R^2$ | Waktu Latih (dtk) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Naive (Persistence)** | 10 | 2.297,01 | 4.680,30 | 5,62% | 0,9181 | 3.340,43 | 5.561,93 | 6,87% | 0,9091 | 0,01 |
| **Ridge Regression (Baseline)** | 10 | 2.329,81 | 4.662,23 | 5,75% | 0,9187 | 3.353,21 | 5.532,61 | 6,95% | 0,9101 | 0,22 |
| **Random Forest (`best_model`)** | 12 | **2.298,16** | 4.679,74 | **5,63%** | 0,9181 | 3.335,39 | 5.558,99 | 6,85% | 0,9092 | 33,29 |
| **XGBoost** | 12 | 2.322,79 | 4.667,59 | 5,70% | 0,9185 | 3.325,29 | 5.541,36 | 6,82% | 0,9098 | 14,69 |
| **LightGBM** | 12 | 2.304,08 | 4.669,43 | 5,64% | 0,9185 | **3.322,42** | 5.535,51 | **6,78%** | 0,9100 | 9,75 |

**Ringkasan Perbandingan:** Ketiga model *tree-based* (**Random Forest**, **XGBoost**, dan **LightGBM**) berhasil mengungguli *baseline* **Naive Persistence** (`Rp3.340,43`) maupun **Ridge Regression** (`Rp3.353,21`) pada **Test MAE** dan **Test MAPE** data uji *out-of-time* 2025–2026.

---

## 6. Analisis Kinerja Terpilah per Rezim & 10 Residual Terbesar

### A. Kinerja Model Terpilih (*Random Forest*) per Rezim (n = 282 Hari Uji)

| Dimensi Segmentasi | Sub-Rezim | Jumlah Hari | Rata-rata Aktual (Rp) | MAE (Rp) | MAPE (%) |
|---|---|---:|---:|---:|---:|
| **Rezim Gejolak Harian** | **Hari Tenang** ($\|\Delta y_t\| \le \text{Rp5.000}$) | 212 | — | **1.289,10** | **3,36%** |
| **Rezim Gejolak Harian** | **Hari Lonjakan** ($\|\Delta y_t\| > \text{Rp5.000}$) | 70 | — | 9.532,72 | 17,42% |
| **Rezim Musim** | **Bulan Lain** (Januari–Agustus) | 194 | 36.279,90 | **2.128,93** | **5,66%** |
| **Rezim Musim** | **Musim Hujan Puncak** (September–Desember) | 88 | 63.913,64 | **5.995,07** | **9,49%** |
| **Rezim Level Harga** | **Normal** ($< \text{Rp50.000/kg}$) | 182 | — | **1.963,36** | **5,76%** |
| **Rezim Level Harga** | **Tinggi** ($\ge \text{Rp50.000/kg}$) | 100 | — | 5.832,48 | 8,85% |

### B. Sepuluh Residual Absolut Terbesar pada Data Uji (`models/metrics.json`)

| Peringkat | Tanggal | Harga $t-1$ (Rp) | Aktual (Rp) | Prediksi (Rp) | Residual (Rp) | APE (%) | Hujan 7H (mm) | Musim Hujan | Akar Masalah Dominan |
|---:|---|---:|---:|---:|---:|---:|---:|:---:|---|
| 1 | `2025-10-20` | 69.600 | 93.300 | 69.436,7 | +23.863,3 | 25,58% | 131,2 | Ya | Guncangan pasokan hujan ekstrem |
| 2 | `2025-09-01` | 40.300 | 62.100 | 40.293,3 | +21.806,7 | 35,12% | 67,6 | Ya | Lonjakan awal musim hujan |
| 3 | `2025-11-26` | 51.100 | 72.700 | 50.933,7 | +21.766,3 | 29,94% | 189,9 | Ya | Guncangan pasokan hujan ekstrem |
| 4 | `2025-09-08` | 61.800 | 81.300 | 61.627,3 | +19.672,7 | 24,20% | 65,1 | Ya | Volatilitas awal musim hujan |
| 5 | `2025-12-03` | 81.200 | 62.200 | 81.033,7 | -18.833,7 | 30,28% | 267,1 | Ya | Koreksi tajam (*mean reversion*) pasca-puncak |
| 6 | `2025-12-08` | 71.500 | 52.600 | 71.333,7 | -18.733,7 | 35,62% | 120,5 | Ya | Koreksi tajam (*mean reversion*) pasca-puncak |
| 7 | `2025-03-26` | 39.800 | 58.300 | 39.798,2 | +18.501,8 | 31,74% | 60,8 | Tidak | Lonjakan permintaan mendadak H-5 Idul Fitri |
| 8 | `2025-12-01` | 72.600 | 90.000 | 72.433,7 | +17.566,3 | 19,52% | 368,5 | Ya | Hujan ekstrem >368 mm dalam 7 hari |
| 9 | `2025-09-09` | 81.300 | 64.500 | 81.119,0 | -16.619,0 | 25,77% | 56,1 | Ya | Koreksi tajam pasca-puncak sehari sebelumnya |
| 10 | `2025-09-17` | 71.500 | 86.400 | 71.338,3 | +15.061,7 | 17,43% | 111,6 | Ya | Guncangan pasokan hujan lebat |

---

## 7. Keterbatasan Teknis, Pertimbangan Etika, & Rencana Pemeliharaan

1. **Keterbatasan Teknis:**
   - Model hanya membaca cuaca di titik koordinat Kota Medan (`3,55° LU, 98,68° BT`), belum mencakup data cuaca atau luas panen langsung di sentra produksi pemasok utama (mis. Kabupaten Karo, Simalungun, Aceh, dan Pulau Jawa).
   - Karena mengandalkan pemodelan perubahan harian berbasis inersia harga ($\rho = 0,961$), prediksi cenderung konservatif ketika terjadi kejutan ekstrem satu hari ($|\Delta y_t| > \text{Rp15.000/kg}$) atau pembalikan arah mendadak (*mean reversion*).
2. **Pertimbangan Etika & Transparansi:**
   - Seluruh angka kinerja dan residual ekstrem disajikan terbuka apa adanya agar pengguna memahami batas kepercayaan prediksi, terutama saat `Akumulasi_Hujan_7H > 100 mm` atau H-7 hari besar keagamaan.
3. **Rencana Pemeliharaan Berkala:**
   - Jalankan `python3 etl/run_etl.py` setiap pembaruan data PIHPS & Open-Meteo untuk menyegarkan `warehouse/cabai_medan.db`.
   - Lakukan pelatihan ulang (`python3 models/train.py`) setiap kuartal (3 bulan sekali) serta pantau pergeseran (*drift*) MAE bulanan di periode September–Desember; jika MAE melampaui Rp4.000/kg selama dua bulan berturut-turut, evaluasi penambahan fitur eksogen sentra produksi.
