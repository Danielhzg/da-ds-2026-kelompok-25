# Prediksi Harga Cabai Merah Keriting di Pasar Tradisional Kota Medan

Proyek Terintegrasi Data Analitik & Data Science — **Kelompok 25** — IT Del

| NIM | Nama | Peran |
|---|---|---|
| 41426085 | **Dame Sisri Rumapea** | Ketua kelompok — lead sisi Data Analitik (ETL, warehouse, dashboard). DASI + DALIS |
| 41426090 | **Daniel Haganta Ginting** | Project Manager (laporan mingguan) — lead sisi Data Science (model, evaluasi). DASI |

## Tujuan proyek

Menyiapkan sistem analitik dan model prediksi harga harian **cabai merah keriting di Pasar Tradisional Kota Medan**.
Dashboard menyajikan KPI harga untuk pemangku kepentingan (TPID/Dinas, pedagang, konsumen); model memprediksi
harga/perubahan harga agar lonjakan (mis. Jul 2022, rata-rata Rp85.267/kg) dapat diantisipasi lebih awal.

## Dataset

| Item | Keterangan |
|---|---|
| Sumber harga | **PIHPS Nasional – Bank Indonesia** (https://www.bi.go.id/hargapangan): Kota Medan, Cabai Merah Keriting, 4 level pasar (Produsen, Pedagang Besar, Pasar Tradisional, Pasar Modern) |
| Sumber cuaca | **Open-Meteo Historical Weather API** (https://open-meteo.com), titik 3,55° LU 98,68° BT (Medan), harian — lisensi CC BY 4.0 |
| Ukuran bersih | 6.352 baris × 10 kolom (31-12-2019 s.d. 29-01-2026; 1.588 hari × 4 pasar) |
| Target | `Harga_Cabai_Merah_Keriting` (Rp/kg) — regresi; fokus baris `Kategori_Pasar = Pasar Tradisional` |

## Struktur folder

```
da-ds-2026-kelompok-25/
├── README.md             # dokumentasi utama proyek & cara menjalankan
├── CONTRIBUTING.md       # tata cara branch, commit, PR, review
├── requirements.txt      # dependensi Python (ETL, ML, Streamlit)
├── data/                 # data mentah & data bersih (<50 MB per file)
├── etl/                  # skrip extract-transform-load ke warehouse SQLite
├── warehouse/            # DDL skema bintang (1 fakta + 3 dimensi) & ERD
├── notebooks/            # notebook 01–07 (EDA, FE, pemodelan, error analysis)
├── models/               # pipeline train.py, artefak .joblib & metrics.json
├── app/                  # dashboard interaktif Streamlit & modul prediksi
├── paper/                # naskah jurnal & lembar jurnal target
├── reports/weekly/       # laporan mingguan perkembangan kelompok
└── docs/                 # proposal, kamus data, grafik & laporan analisis
```

## Cara menjalankan

```bash
pip install -r requirements.txt

# 1. Bangun Data Warehouse SQLite (opsional, database sudah tersedia di repo)
python etl/run_etl.py

# 2. Latih ulang model ML & perbarui artefak evaluasi
python models/train.py

# 3. Jalankan Dashboard Analitik & Modul Prediksi Streamlit
streamlit run app/app.py
```

Untuk mereproduksi seluruh alur riset dari pembersihan hingga *error analysis*, jalankan notebook di folder `notebooks/` **secara berurutan (`01` → `07`)** menggunakan `random_state = 42`.

## Alur kerja

Semua perubahan lewat **pull request** melalui branch fitur tersendiri (dilarang push langsung ke `main`), menggunakan format *Conventional Commits* + nomor issue serta wajib review oleh anggota tim sebelum merge. Panduan kontribusi lengkap: [CONTRIBUTING.md](CONTRIBUTING.md). Laporan mingguan: [reports/weekly/](reports/weekly/).
