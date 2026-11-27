# Proposal Proyek — Kelompok 25 (CP1)

## Judul sementara

**Dashboard Analitik dan Model Prediksi Harga Cabai Merah Keriting di Pasar Tradisional Kota Medan**

## Latar belakang

Harga cabai merah keriting sangat volatil dan berdampak langsung pada inflasi pangan. Kota Medan pernah
mengalami lonjakan hingga rata-rata **Rp85.267/kg pada Juli 2022**. Pemangku kepentingan (TPID/Dinas,
pedagang, konsumen) membutuhkan alat untuk memantau harga lintas level pasar dan mengantisipasi lonjakan
lebih awal.

## Pertanyaan analitik (sisi DA)

1. Bagaimana tren dan volatilitas harga cabai di 4 level pasar (Produsen → Pedagang Besar → Pasar
   Tradisional → Pasar Modern)?
2. Bagaimana pola musiman (bulan, musim hujan, hari besar) memengaruhi harga?
3. Berapa selisih/mark-up antar level pasar dan kapan melebar?

**KPI dashboard:** harga harian per level pasar, mark-up terhadap harga produsen, volatilitas (rolling std),
indikator lonjakan, dan akurasi prediksi model (MAE/MAPE) pada periode terbaru.

## Tugas pemodelan (sisi DS)

- **Tugas:** regresi harga (dan/atau perubahan harga) cabai di **Pasar Tradisional**.
- **Baseline:** naif "harga kemarin" (CV MAE Rp1.244 pada tahap eksplorasi awal) — seluruh model diuji berbasis pemisahan waktu terhadap tolok ukur naif tersebut.
- **Metrik:** MAE (utama), RMSE, MAPE; validasi berbasis waktu (train ≤2024, test 2025–2026).

## Data

- Harga harian: **PIHPS Nasional – Bank Indonesia**, 4 level pasar, 10 tahun (data publik, sumber dicantumkan).
- Cuaca harian: **Open-Meteo** (CC BY 4.0), titik 3,55° LU 98,68° BT (Medan).
- Tahap eksplorasi awal: 6.352 baris bersih, 35 fitur kandidat → 12 fitur model pohon & 10 fitur model linear (VIF ≤ 9,61).

## Kebaruan / kontribusi yang direncanakan

1. Dataset lokal terintegrasi (harga 4 level pasar Medan + cuaca) yang dapat direproduksi dari repo ini.
2. Perbandingan model prediksi perubahan harga pada konteks pasar Indonesia.
3. Sistem terintegrasi: warehouse skema bintang → dashboard KPI + modul prediksi.

## Jadwal ringkas

Mengikuti timeline resmi M1–M15 dengan checkpoint CP1 (M2), CP2 (M5), CP3 (M8), CP4 (M11), dan
CP5 (M15). Pemantauan progres mingguan: [../reports/weekly/](../reports/weekly/).
