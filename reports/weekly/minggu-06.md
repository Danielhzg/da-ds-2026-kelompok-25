# Laporan Mingguan - Kelompok 25 - Minggu ke-6

Periode : 12/10 - 18/10/2026
Status  : Hijau *(rekap konsolidasi tahap Dashboard v1 & Feature Engineering)*

## 1. Target vs capaian

| Target minggu ini | Status (selesai/sebagian/belum) | Bukti |
|---|---|---|
| Implementasi *Feature Engineering* 35 fitur bebas *leakage*, transformasi *power* & pembagian data kronologis | selesai | `notebooks/03_feature_engineering.ipynb`, `data/processed/03_ringkasan.json`, `docs/figures/03_transformasi_skewness.png` |
| Desain wireframe Dashboard v1, struktur navigasi multipage & spesifikasi Filter Global + Kartu KPI | selesai | `app/app.py`, `app/utils.py`, `app/pages/01_Ringkasan_KPI.py` ([PR #8](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/8)) |
| Draf Metode penelitian (bagian akuisisi data, warehouse & *feature engineering*) | selesai | `paper/01_pendahuluan_metode_hasil.md` ([PR #10](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/10)) |

## 2. Kontribusi anggota

| Nama | Tugas | Tautan commit/PR/issue | Jam kerja |
|---|---|---|---|
| Dame Sisri Rumapea | Merancang tata letak dashboard multipage, desain Filter Global sidebar (tanggal, pasar, musim, hari libur), serta formulasi 5 kartu KPI berpembanding paruh periode | `app/app.py`, `app/utils.py`, `01_Ringkasan_KPI.py` ([PR #8](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/8)) | 5 jam |
| Daniel Haganta Ginting | Membangun `03_feature_engineering.ipynb` (`6.272` baris pasca-buang 20 lag awal/pasar -> `5.144` train `<= 2024` & `1.128` test `>= 2025`), transformasi 5 fitur *skewed*, & *out-of-fold target encoding* | `notebooks/03_feature_engineering.ipynb`, `03_ringkasan.json` (migrasi [f2c52b0](https://github.com/Danielhzg/da-ds-2026-kelompok-25/commit/f2c52b0)) | 6 jam |

## 3. Metrik minggu ini

- Pembagian kronologis panel (`4` pasar): `5.144` baris latih (`2020-01-28` s.d. `2024-12-31`) dan `1.128` baris uji (`2025-01-01` s.d. `2026-01-29`).
- Peningkatan kekuatan sinyal fitur: `Harga_Lag1` ($\rho = 0{,}980$), `Harga_MA7` ($\rho = 0{,}944$), `Harga_PB_Lag1` ($\rho = 0{,}657$), dan `Akumulasi_Hujan_60H_Lag11Mgg` ($\rho = 0{,}220$ vs $0{,}049$ curah hujan hari-H).

## 4. Progres jurnal

| Bagian naskah | Penanggung jawab | % selesai |
|---|---|---|
| Draf bagian Metode (akuisisi, skema bintang, dan rekayasa 35 fitur) | Dame + Daniel | 30% |

## 5. Kendala dan bantuan yang dibutuhkan

- Pemeriksaan kebocoran pada tahap *feature engineering* menunjukkan perlunya pembuktian kuantitatif bahwa fitur `Harga_Cabai_Merah_Agregat` tidak layak dimasukkan ke model karena nyaris identik dengan target.

## 6. Rencana minggu depan

| Nama | Rencana tugas | Issue |
|---|---|---|
| Dame Sisri Rumapea | Merancang visualisasi analisis mendalam (heatmap, violin, treemap, small multiples, bubble transmisi) yang terhubung ke `v_harga_lengkap` | `#4` (`app/pages/02_Analisis_Mendalam.py`) |
| Daniel Haganta Ginting | Menjalankan seleksi fitur multi-metode (`04_feature_selection.ipynb`), uji VIF/korelasi (`05_correlation.ipynb`), & membangun model *baseline* Ridge vs Naif | `notebooks/04`–`06` (`#1`) |
