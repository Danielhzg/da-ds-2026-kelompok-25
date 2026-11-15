# notebooks/

Jalankan **berurutan** (Kernel → Restart & Run All); tiap notebook membaca output sebelumnya dari
`data/processed/`. Path relatif `../data/...`, `random_state = 42`.

| Notebook | Tahap |
|---|---|
| `01_preprocessing.ipynb` | Integrasi 5 sumber, cleaning, imputasi → `01_clean.csv` (6.352 baris) |
| `02_eda.ipynb` | EDA uni/bi/multivariat, musiman, event study |
| `03_feature_engineering.ipynb` | 35 fitur baru + split waktu (train ≤2024 / test 2025) |
| `04_feature_selection.ipynb` | Voting 4 metode → 12 fitur (MAE CV Rp1.694) |
| `05_correlation.ipynb` | Korelasi, VIF → 10 fitur final untuk model |

Notebook berikutnya (rencana): `06_baseline.ipynb` (M7–M8), `07_model_lanjutan.ipynb` (M9),
`08_evaluasi.ipynb` (M10).
