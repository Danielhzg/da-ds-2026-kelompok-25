# Laporan Mingguan - Kelompok 25 - Minggu ke-12

Periode : 23/11 - 29/11/2026
Status  : Hijau

## 1. Target vs capaian

| Target minggu ini | Status (selesai/sebagian/belum) | Bukti |
|---|---|---|
| Pipeline *Data Warehouse* SQLite (`1` fakta, `3` dimensi, `v_harga_lengkap`) & ETL otomatis PIHPS + cuaca | selesai | [PR #6](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/6) (`Closes #3`, commits `2b50dd6`, `8630ba7`), tag `v0.2-cp2` |
| Pemodelan baseline Ridge (`VIF <= 9,61`), tuning RF/XGBoost/LightGBM (`TimeSeriesSplit`) & artefak `.joblib` | selesai | [PR #5](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/5) (`Closes #1`, commits `a3848b1`, `91e44b7`) |
| Integrasi Dashboard multipage 4 halaman (`app.py`, KPI, Analisis Mendalam, Storytelling, Prediksi + Uji 5 Skenario Input Baru) | selesai | [PR #8](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/8), [PR #7](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/7) (`Closes #2`), [PR #11](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/11) (`Closes #4`), tag `v0.4-cp4` |
| *Data Dictionary* terpadu (lintas DA) & Notebook 07 *Error Analysis* + 4 grafik diagnostik | selesai | [PR #9](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/9) (commits `f2c5dad`, `80ef890`) |
| *Model Card* (lintas DS) & Laporan Kualitas Data | selesai | [PR #12](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/12) (commit `ededfc5`) |
| Penetapan Jurnal Target SINTA 2 (Jurnal RESTI) & Draf Lengkap Bagian Pendahuluan, Metode, Hasil, Abstrak, Pembahasan, Kesimpulan | selesai | [PR #10](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/10) (`bac51f9`) & [PR #13](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/13) (`7fc8abc`) |
| Pemasangan tag checkpoint `v0.1-cp1` s.d. `v0.4-cp4` & GitHub Projects Board 5 kolom | selesai | Tag rilis GitHub & `Board Proyek Kelompok 25` |
| Deployment aplikasi ke Streamlit Community Cloud (`.streamlit.app`) & uji kegunaan 3–5 pengguna | proses | PR `D6` (`docs/deploy-dan-laporan-m12`) disiapkan; uji kegunaan (`K7`) berjalan setelah URL publik aktif |

## 2. Kontribusi anggota

| Nama | Tugas | Tautan commit/PR/issue | Jam kerja |
|---|---|---|---|
| Dame Sisri Rumapea | Warehouse SQLite + ETL (`#3`), Dashboard kerangka & KPI (`01`), Analisis Mendalam 7 chart (`02`), Storytelling (`03`), `models/model-card.md` (lintas DS), `docs/laporan-kualitas-data.md`, Verifikasi Jurnal RESTI SINTA 2 & Draf Abstrak/Pembahasan/Kesimpulan, Review PR `#5`, `#7`, `#9`, `#10` | [PR #6](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/6), [PR #8](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/8), [PR #11](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/11), [PR #12](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/12), [PR #13](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/13) (`2b50dd6`, `8630ba7`, `899c618`, `7673fe7`, `ededfc5`, `7fc8abc`) | 16 jam |
| Daniel Haganta Ginting | Baseline Ridge (`nb 06`), `models/train.py` (5 model + `TimeSeriesSplit`), halaman prediksi & uji 5 skenario input baru (`04_Prediksi_Harga.py`), `docs/data-dictionary.md` (lintas DA), `nb 07` Error Analysis + 4 grafik, Draf Jurnal Pendahuluan/Metode/Hasil, Laporan M9–M12, Tag `v0.1-cp1`–`v0.4-cp4`, Review PR `#6`, `#8`, `#11`, `#12`, `#13` | [PR #5](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/5), [PR #7](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/7), [PR #9](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/9), [PR #10](https://github.com/Danielhzg/da-ds-2026-kelompok-25/pull/10) (`e14e62e`, `a3848b1`, `91e44b7`, `89fe38c`, `f2c5dad`, `80ef890`, `bac51f9`) | 16 jam |

## 3. Metrik minggu ini

- Commit non-merge pada `main`: **13 commit bermakna** (Daniel: **7**, Dame: **6**) | PR di-merge: **9 PR** (`#5`–`#13`) | Issue ditutup: `#1`, `#2`, `#3`, `#4`.
- Tag rilis terpasang: `v0.1-cp1`, `v0.2-cp2`, `v0.3-cp3`, `v0.4-cp4`.
- Uji integrasi penuh 5 halaman Streamlit (`AppTest` pada `app/app.py` dan `01` s.d. `04`): **0 exception**.
- Metrik model terbaru (*Pasar Tradisional*, uji *out-of-time* `2025-01-01` s.d. `2026-01-29`, $n=282$):
  - **Random Forest** *(Model Terpilih via CV MAE)*: CV MAE **Rp2.298,16** ($R^2 = 0{,}9181$) | Test MAE **Rp3.335,39**, RMSE **Rp5.558,99**, MAPE **6,85%**, $R^2 = 0{,}9092$ (hari tenang MAE **Rp1.289,10**, MAPE **3,36%**).
  - **LightGBM**: Test MAE **Rp3.322,42**, RMSE **Rp5.535,51**, MAPE **6,78%**, $R^2 = 0{,}9100$.
  - **XGBoost**: Test MAE **Rp3.325,29**, RMSE **Rp5.541,36**, MAPE **6,82%**, $R^2 = 0{,}9098$.
  - **Ridge Regression (Baseline)**: Test MAE **Rp3.353,21**, RMSE **Rp5.532,61**, MAPE **6,95%**, $R^2 = 0{,}9101$.
  - **Naive (Persistence)**: CV MAE **Rp2.297,01** | Test MAE **Rp3.340,43**, RMSE **Rp5.561,93**, MAPE **6,87%**, $R^2 = 0{,}9091$.

## 4. Progres jurnal

| Bagian naskah | Penanggung jawab | % selesai |
|---|---|---|
| Lembar Jurnal Target SINTA 2 — **Jurnal RESTI** (`paper/jurnal-target.md`) | Dame Sisri Rumapea | 100% |
| Pendahuluan, Metode *Reproducible*, & Hasil Eksperimen (`paper/01_pendahuluan_metode_hasil.md`, `[1]`–`[15]`) | Daniel Haganta Ginting | 90% |
| Abstrak ID/EN, Pembahasan, Kesimpulan, Etika AI & Pustaka (`paper/02_abstrak_pembahasan_kesimpulan.md`, `[16]`–`[25]`) | Dame Sisri Rumapea | 90% |

## 5. Kendala dan bantuan yang dibutuhkan

- Seluruh komponen integrasi (warehouse, ETL, model ML, 5 halaman Streamlit, *Model Card*, *Data Dictionary*, *Error Analysis*, dan draf jurnal terpisah) telah menyatu di `main` dan lolos uji headless; saat ini tinggal menyelesaikan publikasi URL Streamlit Community Cloud serta pengujian kegunaan dengan 3–5 calon pengguna (`docs/laporan-uji-pengguna.md`).
- Rencana lanjutan M13: mengonsolidasikan `paper/01_...` dan `paper/02_...` menjadi `paper/draf-lengkap.md` untuk dikonsultasikan dengan dosen pengampu.

## 6. Rencana minggu depan

| Nama | Rencana tugas | Issue |
|---|---|---|
| Dame Sisri Rumapea | Uji kegunaan URL publik bersama 3–5 pengguna (`docs/laporan-uji-pengguna.md`), perbaikan UI pasca-uji (`width="stretch"`), serta lengkapi `paper/checklist-submission.md` | M12–M13 (`K7`, `K8`) |
| Daniel Haganta Ginting | Eksperimen penyempurnaan model (fitur koreksi pasca-lonjakan) & konsolidasi draf lengkap jurnal `paper/draf-lengkap.md` (25+ referensi Zotero) ke dosen | M13 (`D7`) |
