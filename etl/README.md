# etl/

Skrip extract-transform-load dari sumber mentah (`data/raw/`) ke warehouse (`warehouse/`).

**Rencana isi (lead: Dame):**
- `extract_pihps.py` — baca 4 file `.xlsx` PIHPS → format long
- `extract_cuaca.py` — baca `.csv` Open-Meteo
- `transform.py` — cleaning + konsolidasi (porting dari `notebooks/01_preprocessing.ipynb`)
- `load.py` — isi `fact_harga_harian` + tabel dimensi (skema di `warehouse/`)

Status: dijadwalkan sebagai bagian catch-up M9–M10 (deliverable CP2/M5).
