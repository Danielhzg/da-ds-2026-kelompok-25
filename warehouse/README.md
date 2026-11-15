# warehouse/

DDL skema bintang + ERD data warehouse (lead: Dame).

**Rancangan (draft):**
- `fact_harga_harian` — tanggal, pasar, harga, metrik turunan
- `dim_tanggal` — tanggal, bulan, tahun, musim, flag hari libur/hari besar
- `dim_pasar` — level pasar (Produsen, Pedagang Besar, Pasar Tradisional, Pasar Modern)
- `dim_cuaca` / `fact_cuaca_harian` — curah hujan, suhu, dsb. per tanggal

Output target: SQLite/Parquet yang dikonsumsi `app/` dan `notebooks/`.
Status: dijadwalkan sebagai bagian catch-up M9–M10 (deliverable CP2/M5).
