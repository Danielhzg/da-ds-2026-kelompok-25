# Laporan Mingguan - Kelompok 25 - Minggu ke-9

Periode : 02/11 - 08/11/2026
Status  : Kuning *(rencana pemulihan di bagian 5)*

## 1. Target vs capaian

| Target minggu ini | Status (selesai/sebagian/belum) | Bukti |
|---|---|---|
| Perancangan arsitektur skema bintang *Data Warehouse* & pipeline ETL | selesai | Rancangan DDL & kontrak view `v_harga_lengkap` (diimplementasikan di [PR #6](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/6)) |
| Finalisasi seleksi fitur bebas multikolinearitas & desain eksperimen model lanjutan | selesai | `data/processed/05_fitur_final_uas.json`, `notebooks/04_feature_selection.ipynb`, `notebooks/05_correlation.ipynb` |
| Penyusunan daftar topik jurnal target SINTA 1–3 & pengumpulan referensi awal | sebagian | Draf awal `paper/jurnal-target.md` |

## 2. Kontribusi anggota

| Nama | Tugas | Tautan commit/PR/issue | Jam kerja |
|---|---|---|---|
| Dame Sisri Rumapea | Perancangan skema bintang 1 fakta + 3 dimensi, desain dashboard multipage KPI, penelusuran awal jurnal target | Persiapan struktur `warehouse/` & `paper/jurnal-target.md` (dimigrasikan pada [f2c52b0](https://github.com/Danielhzg/da-ds-2026-kelompok-25/commit/f2c52b0)) | 6 jam |
| Daniel Haganta Ginting | Finalisasi 12 fitur pohon & 10 fitur linear (`VIF <= 9,61`), penyusunan desain validasi `TimeSeriesSplit` & target perubahan harian | `data/processed/05_fitur_final_uas.json`, `notebooks/04_feature_selection.ipynb`, `notebooks/05_correlation.ipynb` | 6 jam |

## 3. Metrik minggu ini

- Commit: pekerjaan disiapkan secara lokal sebelum migrasi ke repositori terpusat pada pekan M10.
- Metrik acuan awal: `6.352` baris bersih (`1.588` hari kerja × `4` level pasar), `35` fitur kandidat → `12` fitur model pohon & `10` fitur model linear (`VIF <= 9,61`).

## 4. Progres jurnal

| Bagian naskah | Penanggung jawab | % selesai |
|---|---|---|
| Pemetaan jurnal target nasional SINTA 1–3 & ide kebaruan | Dame + Daniel | 30% |

## 5. Kendala dan bantuan yang dibutuhkan

- Pekerjaan kelompok masih berjalan pada workspace terpisah sebelum pembentukan repositori terpadu `da-ds-2026-kelompok-25`.
- Rencana pemulihan: segera melakukan inisialisasi repositori privat terstruktur di GitHub, mengundang dosen & seluruh anggota, dan memigrasikan seluruh artefak fondasi M1–M9 secara bertahap dengan bukti commit & tag rilis yang terukur.

## 6. Rencana minggu depan

| Nama | Rencana tugas | Issue |
|---|---|---|
| Dame Sisri Rumapea | Menyiapkan struktur Issues/Labels/Milestones & rencana implementasi `etl/` + `warehouse/` | Setup Repo & `#3` |
| Daniel Haganta Ginting | Inisialisasi repositori `da-ds-2026-kelompok-25`, migrasi artefak `data/`, `notebooks/01-05`, dan `docs/proposal.md` | Setup Repo & `#1` |
