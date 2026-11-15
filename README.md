# Prediksi Harga Cabai Merah Keriting di Pasar Tradisional Kota Medan

Proyek Terintegrasi Data Analitik & Data Science — **Kelompok 25** — IT Del
Dosen Pengampu: Oppir Hutapea

| NIM | Nama | Peran |
|---|---|---|
| 41426085 | **Dame Sisri Rumapea** | Ketua kelompok — lead sisi Data Analitik (ETL, warehouse, dashboard). Pengampu DASI + DALI |
| 41426090 | **Daniel Haganta Ginting** | Project Manager (laporan mingguan) — lead sisi Data Science (model, evaluasi). Pengampu DASI |

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
├── README.md             # file ini
├── RENCANA_PROYEK.md     # rencana kerja M1–M15 + aturan kontribusi
├── CONTRIBUTING.md       # tata cara branch, commit, PR, review
├── requirements.txt
├── data/                 # data mentah (sampel) + hasil olahan (<50 MB per file)
├── etl/                  # skrip extract-transform-load ke warehouse
├── warehouse/            # DDL skema bintang + ERD
├── notebooks/            # EDA, baseline, eksperimen model
├── models/               # model terbaik (.pkl/.joblib) + model card
├── app/                  # dashboard (Streamlit) + modul prediksi
├── paper/                # naskah jurnal + jurnal-target.md
├── reports/weekly/       # laporan mingguan minggu-01.md … minggu-14.md
└── docs/                 # proposal, data dictionary, laporan kualitas data
```

## Cara menjalankan

```bash
pip install -r requirements.txt
cd notebooks
jupyter notebook
```

Jalankan notebook **berurutan 01 → 05** (Kernel → Restart & Run All); tiap notebook membaca output
notebook sebelumnya dari `data/processed/`. Path relatif (`../data/...`), `random_state = 42`.

## Alur kerja

Semua perubahan lewat **pull request** (tidak ada push langsung ke `main`), dengan format commit
*Conventional Commits* + nomor issue. Detail: [CONTRIBUTING.md](CONTRIBUTING.md) dan
[RENCANA_PROYEK.md](RENCANA_PROYEK.md). Laporan mingguan: [reports/weekly/](reports/weekly/).
