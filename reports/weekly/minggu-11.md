# Laporan Mingguan - Kelompok 25 - Minggu ke-11

Periode : 16/11 - 22/11/2026
Status  : Kuning *(persiapan sprint CP4 & sinkronisasi antar lapisan)*

## 1. Target vs capaian

| Target minggu ini | Status (selesai/sebagian/belum) | Bukti |
|---|---|---|
| Penyusunan kontrak data lintas modul (`v_harga_lengkap` <-> `models/train.py` & `app/`) | selesai | Kesepakatan skema 1 fakta + 3 dimensi & skema JSON evaluasi (`models/metrics.json`) |
| Pengisian issue, label (`DA`, `DS`, `Jurnal`, `Docs`), dan milestone GitHub | selesai | Issues `#1`–`#4` pada repositori `da-ds-2026-kelompok-25` |
| Implementasi kode penuh `etl/`, `warehouse/`, `models/`, dan `app/` | sebagian | Dialokasikan dalam paket *Pull Request* terstruktur pada pekan M12 |

## 2. Kontribusi anggota

| Nama | Tugas | Tautan commit/PR/issue | Jam kerja |
|---|---|---|---|
| Dame Sisri Rumapea | Penetapan spesifikasi DDL skema bintang (`dim_tanggal`, `dim_pasar`, `dim_cuaca`, `fact_harga_harian`) & rancangan 4 halaman dashboard Streamlit | Persiapan Issue `#3` & `#4` | 5 jam |
| Daniel Haganta Ginting | Perancangan strategi prediksi selisih harian ($\Delta y_t$), kontrak fallback CSV/SQLite, serta perapian identitas anggota repositori | Persiapan Issue `#1` & `#2` | 5 jam |

## 3. Metrik minggu ini

- Commit: `0` di `main` (fokus perancangan kontrak skema & pembagian issue sebelum eksekusi branch) | Issue aktif: `#1`, `#2`, `#3`, `#4`.
- Target teknis yang dikunci: eliminasi fitur bocor `Harga_Cabai_Merah_Agregat` ($r = 0{,}9998$), pemisahan kronologis `Train <= 2024` ($n = 1.286$) vs `Test 2025–2026` ($n = 282$).

## 4. Progres jurnal

| Bagian naskah | Penanggung jawab | % selesai |
|---|---|---|
| Penyusunan kerangka Pendahuluan, Metode *Reproducible*, dan pemilihan target SINTA | Dame + Daniel | 40% |

## 5. Kendala dan bantuan yang dibutuhkan

- Kedua anggota berfokus merapikan spesifikasi lintas lapisan agar tidak terjadi konflik file maupun ketidakcocokan nama kolom saat integrasi `warehouse/cabai_medan.db` dengan modul *Machine Learning* dan Dashboard Streamlit.
- Rencana pemulihan: pada pekan M12 seluruh modul (`etl/`, `warehouse/`, `models/`, `app/`, `notebooks/06-07`, serta draf jurnal di `paper/`) dieksekusi intensif melalui branch & PR terpisah beserta backfill tag `v0.1-cp1` s.d. `v0.4-cp4`.

## 6. Rencana minggu depan

| Nama | Rencana tugas | Issue |
|---|---|---|
| Dame Sisri Rumapea | Implementasi `warehouse/` + `etl/` (`#3`), Dashboard multipage (`#4`), `models/model-card.md`, `docs/laporan-kualitas-data.md`, dan verifikasi SINTA + draf pembahasan jurnal | `#3`, `#4` |
| Daniel Haganta Ginting | Implementasi `notebooks/06` & `models/train.py` (`#1`), halaman `04_Prediksi_Harga.py` (`#2`), `docs/data-dictionary.md`, `notebooks/07`, draf jurnal DS, dan deployment online | `#1`, `#2` |
