# data/

| Folder | Isi |
|---|---|
| `raw/` | File asli tidak diubah: 4 file PIHPS-BI (`.xlsx`, per level pasar) + 1 file cuaca Open-Meteo (`.csv`) |
| `processed/` | Output tiap notebook: `01_clean.csv`, `03_train_fe.csv`/`03_test_fe.csv`, `04_*_selected.csv`, `*_ringkasan.json`, `05_fitur_final_uas.json` |

**Sumber:** PIHPS Nasional — Bank Indonesia (https://www.bi.go.id/hargapangan) • Open-Meteo Historical
Weather API (https://open-meteo.com, CC BY 4.0).

**Aturan:** jangan commit file >50 MB — untuk data lengkap gunakan sampel + tautan sumber di atas.
