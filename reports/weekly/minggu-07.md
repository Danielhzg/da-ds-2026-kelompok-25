# Laporan Mingguan - Kelompok 25 - Minggu ke-7

Periode : 19/10 - 25/10/2026
Status  : Hijau *(rekap konsolidasi tahap Seleksi Fitur & Baseline)*

## 1. Target vs capaian

| Target minggu ini | Status (selesai/sebagian/belum) | Bukti |
|---|---|---|
| Seleksi fitur konsensus (membuang leakage `Harga_Cabai_Merah_Agregat` & quasi-konstan `Is_Imputasi`) menjadi 12 fitur pohon | selesai | `notebooks/04_feature_selection.ipynb`, `data/processed/04_ringkasan.json`, `docs/figures/04_*.png` |
| Uji korelasi Spearman, Eta-squared, Cramer's V, & reduksi multikolinearitas VIF ($\le 9{,}61$) menjadi 10 fitur linear | selesai | `notebooks/05_correlation.ipynb`, `data/processed/05_ringkasan.json`, `05_fitur_final_uas.json` |
| Pemodelan *baseline* Naive (Persistence) vs pembanding linear Ridge Regression | selesai | `notebooks/06_baseline_dan_pemodelan.ipynb` ([PR #5](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/5)) |

## 2. Kontribusi anggota

| Nama | Tugas | Tautan commit/PR/issue | Jam kerja |
|---|---|---|---|
| Dame Sisri Rumapea | Merancang sketsa grafik analitik lanjutan lintas rantai pasok & cuaca, serta menguji kueri agregasi pada `warehouse/cabai_medan.db` | Persiapan modul `app/pages/` & kontrak data `v_harga_lengkap` ([PR #6](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/6), [PR #11](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/11)) | 5 jam |
| Daniel Haganta Ginting | Menjalankan `04_feature_selection.ipynb` & `05_correlation.ipynb` (eliminasi `Harga_MA7` VIF `147,7` & `Harga_MA20` VIF `35,6` -> 10 fitur `VIF <= 9,61`), serta merancang pipeline *baseline* Ridge pada `notebooks/06` | `notebooks/04`–`06` ([f2c52b0](https://github.com/Danielhzg/da-ds-2026-kelompok-25/commit/f2c52b0), [PR #5](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/5)) | 6 jam |

## 3. Metrik minggu ini

- Fitur tervalidasi: **`12` fitur model pohon** (`fitur_terpilih_tahap4`, CV MAE seleksi turun dari `Rp2.041` ke `Rp1.694`) dan **`10` fitur model linear** (`fitur_untuk_model_linear`, `VIF maks = 9,61`).
- Uji *data leakage* terbuktikan: `Harga_Cabai_Merah_Agregat` memiliki korelasi $r = 0{,}9998$ (identik `99,92%`) di Pasar Tradisional dan wajib dibuang sebelum pelatihan.

## 4. Progres jurnal

| Bagian naskah | Penanggung jawab | % selesai |
|---|---|---|
| Draf bagian Metode (protokol seleksi fitur, anti-leakage, dan skema validasi waktu) | Dame + Daniel | 32% |

## 5. Kendala dan bantuan yang dibutuhkan

- Penanganan berkas `04_train_selected.csv` & `03_train_fe_unscaled.csv` yang berformat pemisah titik koma korup di Excel diatasi dengan membangun ulang fitur secara langsung dari sumber bersih (`warehouse/cabai_medan.db` / `01_clean.csv`).

## 6. Rencana minggu depan

| Nama | Rencana tugas | Issue |
|---|---|---|
| Dame Sisri Rumapea | Mengintegrasikan Dashboard v1 (`01_Ringkasan_KPI.py`) dengan warehouse SQLite & evaluasi capaian tengah CP3 | `#4`, `v0.3-cp3` |
| Daniel Haganta Ginting | Menyusun laporan evaluasi *baseline* Naive vs Ridge (`notebooks/06`), draf 1 Pendahuluan + Metode jurnal, serta desain tuning RF/XGBoost/LightGBM | `#1`, `v0.3-cp3` |
