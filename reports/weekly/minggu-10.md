# Laporan Mingguan - Kelompok 25 - Minggu ke-10

Periode : 09/11 - 15/11/2026
Status  : Kuning *(proses konsolidasi repositori terpadu)*

## 1. Target vs capaian

| Target minggu ini | Status (selesai/sebagian/belum) | Bukti |
|---|---|---|
| Pendirian repositori privat `da-ds-2026-kelompok-25` dengan struktur folder wajib | selesai | Commit [f2c52b0](https://github.com/Danielhzg/da-ds-2026-kelompok-25/commit/f2c52b0) |
| Migrasi dataset bersih, kamus fitur, dan `notebooks/01-05` + `docs/proposal.md` | selesai | `data/processed/`, `notebooks/01_preprocessing.ipynb`–`05_correlation.ipynb`, `docs/proposal.md` |
| Penyusunan `README.md`, `CONTRIBUTING.md`, dan template laporan mingguan | selesai | `README.md`, `CONTRIBUTING.md`, `reports/weekly/_template.md` |
| Pengisian lengkap evaluasi lanjutan & `models/model-card.md` | sebagian | Dilanjutkan bertahap pada sprint integrasi berikutnya |

## 2. Kontribusi anggota

| Nama | Tugas | Tautan commit/PR/issue | Jam kerja |
|---|---|---|---|
| Dame Sisri Rumapea | Peninjauan struktur repositori, penyusunan template `paper/jurnal-target.md`, penyiapan definisi KPI & metrik rantai pasok | Template awal pada [f2c52b0](https://github.com/Danielhzg/da-ds-2026-kelompok-25/commit/f2c52b0) | 5 jam |
| Daniel Haganta Ginting | Inisialisasi repositori `da-ds-2026-kelompok-25`, migrasi 6.352 baris bersih + `notebooks/01-05`, penyusunan `docs/proposal.md` & `README.md` | Commit [f2c52b0](https://github.com/Danielhzg/da-ds-2026-kelompok-25/commit/f2c52b0) | 7 jam |

## 3. Metrik minggu ini

- Commit: `1` commit inisialisasi & migrasi fondasi | PR di-merge: `0` (inisialisasi awal repo) | Issue disiapkan: `#1`–`#4`.
- Metrik dataset tervalidasi: `6.352` baris bersih (`2019-12-31` s.d. `2026-01-29`), rasio *imputasi* `1,45%` (92 sel *forward-fill*).

## 4. Progres jurnal

| Bagian naskah | Penanggung jawab | % selesai |
|---|---|---|
| Kerangka Lembar Jurnal Target (`paper/jurnal-target.md`) & pemetaan literatur awal | Dame + Daniel | 35% |

## 5. Kendala dan bantuan yang dibutuhkan

- Konsolidasi repositori efektif dimulai pada 15 November 2026 sehingga seluruh riwayat awal perlu dipetakan ulang ke *Issues*, *Labels*, *Milestones*, dan *tag checkpoint* (`v0.1-cp1` s.d. `v0.3-cp3`).
- Rencana tindak lanjut: seluruh pekerjaan lanjutan (ETL, *Data Warehouse*, *Modelling*, Dashboard, dan Naskah Jurnal) wajib dikerjakan melalui *feature branch* terpisah dengan *Pull Request* yang saling direview antar anggota.

## 6. Rencana minggu depan

| Nama | Rencana tugas | Issue |
|---|---|---|
| Dame Sisri Rumapea | Memfinalkan spesifikasi DDL skema bintang SQLite, pipeline ETL Python, dan wireframe dashboard KPI | `#3`, `#4` |
| Daniel Haganta Ginting | Menyiapkan skrip baseline Ridge Regression, pipeline tuning ensemble (`models/train.py`), dan halaman prediksi Streamlit | `#1`, `#2` |
