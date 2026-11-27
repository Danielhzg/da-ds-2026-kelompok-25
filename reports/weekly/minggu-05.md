# Laporan Mingguan - Kelompok 25 - Minggu ke-5

Periode : 05/10 - 11/10/2026
Status  : Hijau *(rekap konsolidasi CP2 Data Readiness)*

## 1. Target vs capaian

| Target minggu ini | Status (selesai/sebagian/belum) | Bukti |
|---|---|---|
| Perancangan & DDL Skema Bintang *Data Warehouse* (`fact_harga_harian`, `dim_tanggal`, `dim_pasar`, `dim_cuaca`, `v_harga_lengkap`) & ERD | selesai | `warehouse/schema.sql`, `warehouse/erd.md` ([PR #6](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/6)), tag [`v0.2-cp2`](https://github.com/Danielhzg/da-ds-2026-kelompok-25/releases/tag/v0.2-cp2) |
| Perancangan pipeline ETL terstruktur PIHPS-BI & Open-Meteo menuju SQLite `warehouse/cabai_medan.db` | selesai | `etl/extract.py`, `etl/transform.py`, `etl/load.py`, `etl/run_etl.py` ([PR #6](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/6)) |
| Perumusan 35 fitur kandidat (10 kelompok) dan struktur draf awal bagian Pendahuluan | selesai | `data/processed/03_kamus_fitur.csv`, `paper/01_pendahuluan_metode_hasil.md` |

## 2. Kontribusi anggota

| Nama | Tugas | Tautan commit/PR/issue | Jam kerja |
|---|---|---|---|
| Dame Sisri Rumapea | Menyusun DDL skema bintang SQLite (`v_harga_lengkap`), diagram relasi ERD (`warehouse/erd.md`), dan modul ETL otomatis ke `warehouse/cabai_medan.db` | [PR #6](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/6) (`Closes #3`, commits `2b50dd6`, `8630ba7`), tag [`v0.2-cp2`](https://github.com/Danielhzg/da-ds-2026-kelompok-25/releases/tag/v0.2-cp2) | 6 jam |
| Daniel Haganta Ginting | Merumuskan daftar 35 fitur kandidat lintas-pasar, cuaca jeda $\le t-1$, dan kalender hari besar (`03_kamus_fitur.csv`) serta draf awal latar belakang Pendahuluan | `data/processed/03_kamus_fitur.csv`, `paper/01_pendahuluan_metode_hasil.md` | 5 jam |

## 3. Metrik minggu ini

- Checkpoint tercapai: **CP2 Data Readiness** (tag [`v0.2-cp2`](https://github.com/Danielhzg/da-ds-2026-kelompok-25/releases/tag/v0.2-cp2)).
- Integritas warehouse: **4 tabel inti (`fact_harga_harian` + `dim_tanggal` + `dim_pasar` + `dim_cuaca`)** dan **1 SQL View (`v_harga_lengkap`)** memuat tepat `6.352` baris fakta dengan **0 pelanggaran *foreign key***.

## 4. Progres jurnal

| Bagian naskah | Penanggung jawab | % selesai |
|---|---|---|
| Draf awal Pendahuluan & justifikasi arsitektur integrasi data | Dame + Daniel | 28% |

## 5. Kendala dan bantuan yang dibutuhkan

- Penyelarasan nama kolom antara SQL View `v_harga_lengkap` (*snake_case*) dan skrip pemodelan (*PascalCase* di `01_clean.csv`) diselesaikan melalui peta translasi eksplisit serta mekanisme *auto-fallback* CSV.

## 6. Rencana minggu depan

| Nama | Rencana tugas | Issue |
|---|---|---|
| Dame Sisri Rumapea | Merancang wireframe & kerangka multipage dashboard Streamlit (`app/app.py`, `utils.py`, Filter Global) beserta definisi 5 kartu KPI | `#4` (`app/`) |
| Daniel Haganta Ginting | Mengimplementasikan `03_feature_engineering.ipynb` (`35` fitur, transformasi Yeo-Johnson, split kronologis `Train <= 2024` vs `Test >= 2025`) | `notebooks/03_feature_engineering.ipynb` |
