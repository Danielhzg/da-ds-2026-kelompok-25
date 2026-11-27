# Laporan Mingguan - Kelompok 25 - Minggu ke-8

Periode : 26/10 - 01/11/2026
Status  : Hijau *(rekap konsolidasi CP3 Checkpoint Tengah / UTS)*

## 1. Target vs capaian

| Target minggu ini | Status (selesai/sebagian/belum) | Bukti |
|---|---|---|
| Dashboard v1 terhubung penuh ke *Data Warehouse* SQLite (`cabai_medan.db`) & Filter Global | selesai | `app/app.py`, `app/utils.py`, `app/pages/01_Ringkasan_KPI.py` ([PR #8](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/8)), tag [`v0.3-cp3`](https://github.com/Danielhzg/da-ds-2026-kelompok-25/releases/tag/v0.3-cp3) |
| Laporan *baseline* pemodelan (Naive Persistence vs Ridge Regression pada strategi $\Delta y_t$) | selesai | `notebooks/06_baseline_dan_pemodelan.ipynb` ([PR #5](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/5)) |
| Draf 1 bagian Pendahuluan & Metode naskah jurnal | selesai | `paper/01_pendahuluan_metode_hasil.md` ([PR #10](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/10)) |

## 2. Kontribusi anggota

| Nama | Tugas | Tautan commit/PR/issue | Jam kerja |
|---|---|---|---|
| Dame Sisri Rumapea | Menghubungkan kerangka Dashboard v1 & halaman KPI (`01_Ringkasan_KPI.py`) langsung ke SQL View `v_harga_lengkap`, serta merangkum evaluasi tengah sisi DA | [PR #8](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/8) (`Closes #4`), tag [`v0.3-cp3`](https://github.com/Danielhzg/da-ds-2026-kelompok-25/releases/tag/v0.3-cp3) | 6 jam |
| Daniel Haganta Ginting | Menyelesaikan perbandingan `Naive (Persistence)` (CV MAE `Rp2.297,01`, Test MAE `Rp3.340,43`) vs `Ridge Regression` (Test RMSE `Rp5.532,61`, $R^2=0{,}9101$) pada `notebooks/06` serta menyusun draf 1 Pendahuluan & Metode | [PR #5](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/5) (`a3848b1`), [PR #10](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/10) | 6 jam |

## 3. Metrik minggu ini

- Checkpoint tercapai: **CP3 Checkpoint Tengah / UTS** (tag [`v0.3-cp3`](https://github.com/Danielhzg/da-ds-2026-kelompok-25/releases/tag/v0.3-cp3)).
- Tolok ukur *baseline* Pasar Tradisional (`Train <= 2024` $n=1.286$, `Test 2025–2026` $n=282$):
  - `Naive (Persistence)`: CV MAE **Rp2.297,01** | Test MAE **Rp3.340,43**, Test RMSE **Rp5.561,93**, Test MAPE **6,87%**.
  - `Ridge Regression (Baseline, alpha=5000)`: CV MAE **Rp2.329,81** | Test MAE **Rp3.353,21**, Test RMSE **Rp5.532,61**, $R^2 = 0{,}9101$.

## 4. Progres jurnal

| Bagian naskah | Penanggung jawab | % selesai |
|---|---|---|
| Draf 1 Pendahuluan, Metode *Reproducible*, & pemetaan jurnal target SINTA | Dame + Daniel | 35% |

## 5. Kendala dan bantuan yang dibutuhkan

- Seluruh deliverable pra-UTS s.d. CP3 telah tuntas dan disiapkan untuk konsolidasi penuh ke dalam repositori GitHub kelompok mulai Minggu ke-9/10.

## 6. Rencana minggu depan

| Nama | Rencana tugas | Issue |
|---|---|---|
| Dame Sisri Rumapea | Mempersiapkan rancangan visualisasi advance (drill-down & cross-filter) dan draf awal Lembar Jurnal Target SINTA | `#3`, `#4` |
| Daniel Haganta Ginting | Menyiapkan desain eksperimen model *ensemble* lanjutan (Random Forest, XGBoost, LightGBM) serta persiapan repositori terstruktur `da-ds-2026-kelompok-25` | `#1` |
