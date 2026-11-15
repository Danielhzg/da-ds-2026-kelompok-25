# models/

Model terbaik (`.pkl`/`.joblib`) + **model card**.

**Rencana:**
- `model-card.md` — deskripsi model, data latih, metrik (MAE/RMSE/MAPE), batasan, cara pakai
- `baseline_naif` — acuan: prediksi = harga kemarin (CV MAE Rp1.244)
- Model kandidat: regresi linear (10 fitur terpilih), Random Forest / Gradient Boosting
- Target: mengalahkan baseline naif pada test 2025 dengan validasi berbasis waktu

Lead model: Daniel; `model-card.md` dikerjakan Dame (lintas lapisan).
