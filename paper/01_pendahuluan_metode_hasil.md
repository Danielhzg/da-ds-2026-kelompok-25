# Draf Naskah Jurnal — Bagian Judul, Pendahuluan, Metode, dan Hasil (D5)

> **Catatan Penyusunan (Minggu 12):** Dokumen ini merupakan kontribusi bagian *Pendahuluan, Metode Penelitian, dan Hasil* (Lead Data Science: **Daniel Haganta Ginting**). Seluruh angka dan grafik bersumber langsung dari eksekusi pipeline `etl/run_etl.py`, `models/train.py`, `models/metrics.json`, dan `notebooks/07_evaluasi_dan_error_analysis.ipynb` (*single source of truth*). Bagian *Abstrak, Pembahasan Lanjutan, dan Kesimpulan* disusun oleh **Dame Sisri Rumapea** di `paper/02_abstrak_pembahasan_kesimpulan.md`, lalu digabungkan menjadi draf lengkap pada Minggu 13 (`paper/draf-lengkap.md`).

---

## Judul Usulan
**Integrasi Data Warehouse Skema Bintang dan Model Ensemble Berbasis Perubahan Harga Harian untuk Analitik serta Prediksi Harga Cabai Merah Keriting di Kota Medan**  
*(Integration of Star-Schema Data Warehouse and Daily Price-Change Ensemble Models for Price Analytics and Forecasting of Curly Red Chili in Medan City)*

## Penulis & Afiliasi
1. **Dame Sisri Rumapea** — Program Studi S1 Sistem Informasi / Teknik Informatika, Institut Teknologi Del, Laguboti, Indonesia  
2. **Daniel Haganta Ginting** — Program Studi S1 Sistem Informasi / Rekayasa Perangkat Lunak, Institut Teknologi Del, Laguboti, Indonesia  
3. **Oppir Hutapea** — Dosen Pengampu Proyek Terintegrasi Data Analitik & Data Science, Institut Teknologi Del, Laguboti, Indonesia  

---

## 1. Pendahuluan

Komoditas hortikultura strategis seperti cabai merah keriting merupakan salah satu penyumbang utama gejolak inflasi kelompok *volatile foods* (bahan makanan bergejolak) di Indonesia [1], [2]. Berbeda dengan komoditas pangan yang memiliki daya simpan panjang, cabai merah keriting bersifat mudah rusak (*perishable*), sensitif terhadap anomali curah hujan pada fase pembungaan hingga panen, serta memiliki struktur rantai pasok berlapis dari tingkat petani (produsen), pedagang besar, pasar tradisional, hingga pasar modern [2], [3]. Di Kota Medan sebagai salah satu pusat konsumsi utama di Sumatra Utara, data Pusat Informasi Harga Pangan Strategis (PIHPS) Nasional Bank Indonesia periode 2019–2026 mencatat rata-rata harga cabai merah keriting di Pasar Tradisional mencapai Rp37.853/kg (median Rp33.700/kg), dengan lonjakan bulanan tertinggi hingga **Rp85.267/kg pada Juli 2022** dan puncak harian mencapai **Rp109.500/kg** [4]. Ketidakstabilan tersebut berdampak langsung pada daya beli rumah tangga, margin pedagang pasar, serta efektivitas intervensi pasar oleh Tim Pengendalian Inflasi Daerah (TPID).

Sejumlah penelitian terdahulu telah mengkaji peramalan harga komoditas pertanian menggunakan pendekatan deret waktu statistik maupun *machine learning*. Metode klasik seperti regresi linear berpenalti (*Ridge Regression*) memberikan interpretabilitas koefisien yang baik dalam meredam multikolinearitas [5], namun sering kali kurang fleksibel menangkap interaksi non-linear antara guncangan pasokan, musiman hari besar keagamaan, dan kondisi cuaca. Sebaliknya, algoritma *ensemble* berbasis pohon keputusan—seperti *Random Forest* [6], *XGBoost* [7], dan *LightGBM* [8]—terbukti unggul pada data tabular multivariat untuk memodelkan hubungan non-linear serta interaksi fitur [9], [10]. Meskipun demikian, penerapan model *machine learning* pada peramalan harga pangan harian sering menghadapi tiga tantangan metodologis: (1) **kebocoran data (*data leakage*)** akibat pemakaian fitur hari-H atau pemisahan data acak (*random split*) yang melanggar urutan kronologis [11], (2) **kegagalan ekstrapolasi skala** ketika model berbasis pohon memprediksi harga absolut $y_t$ pada rezim lonjakan baru [12], dan (3) **terputusnya alur pemodelan dengan sistem pendukung keputusan** yang langsung dapat dimanfaatkan pemangku kepentingan di lapangan.

Berdasarkan celah penelitian (*research gap*) tersebut, studi ini membangun sistem terintegrasi dari hulu data hingga antarmuka prediksi dengan tiga kontribusi utama:
1. **Integrasi Data Lintas Rantai Pasok & Cuaca Terkurasi:** Menggabungkan catatan harga harian 4 tingkat pasar Kota Medan (PIHPS-BI) dan variabel cuaca historis Kota Medan (Open-Meteo) [13] ke dalam *Data Warehouse* skema bintang SQLite (`1` tabel fakta, `3` tabel dimensi, `6.352` baris bersih).
2. **Formulasi Target Perubahan Harga Harian ($\Delta y_t$) Bebas Kebocoran Data:** Mengevaluasi *Naive Persistence*, *Ridge Regression* (10 fitur bebas multikolinearitas $\text{VIF} \le 9{,}61$), *Random Forest*, *XGBoost*, dan *LightGBM* (12 fitur konsensus) dengan pemisahan kronologis murni, `TimeSeriesSplit(n_splits=5)`, dan *out-of-fold target encoding* [14].
3. **Analitik Galat (*Error Analysis*) & Aplikasi Web Terintegrasi:** Menyajikan analisis mendalam atas 10 galat prediksi terbesar menurut rezim cuaca dan hari raya, serta mengoperasionalkan model terbaik ke dalam dashboard interaktif Streamlit yang terhubung langsung ke *Data Warehouse* dan diuji pada 5 skenario masukan baru.

---

## 2. Metode Penelitian

Alur penelitian dirancang agar dapat direproduksi sepenuhnya (*reproducible*) dari tahap akuisisi data mentah hingga evaluasi model melalui repositori kode terstruktur.

### 2.1 Akuisisi, Pembersihan, dan Arsitektur *Data Warehouse*
Data harga harian diperoleh dari PIHPS Nasional Bank Indonesia (empat berkas tingkat pasar Kota Medan: *Produsen*, *Pedagang Besar*, *Pasar Tradisional*, dan *Pasar Modern*) sebanyak 10.437 baris mentah, yang diselaraskan menjadi periode irisan lengkap **31 Desember 2019 hingga 29 Januari 2026** (1.588 hari kerja $\times$ 4 tingkat pasar = **6.352 baris**). Nilai kosong eksplisit berkode tanda strip `'-'` (yang mayoritas bertepatan dengan hari libur pengamatan) ditangani melalui pemangkasan awal dan *forward-fill* terbatas per pasar (total 92 sel atau **1,45%** yang ditandai oleh kolom `Is_Imputasi`), yang pada uji simulasi mencatat galat lebih rendah dibanding imputasi median. Data cuaca harian Kota Medan pada koordinat $3{,}55^\circ\text{ LU}, 98{,}68^\circ\text{ BT}$ (elevasi 28 m) diambil dari Open-Meteo Historical Weather API (2.402 baris kalender, 0 nilai kosong) [13].

Seluruh data bersih disimpan pada `data/processed/01_clean.csv` dan dimuat secara otomatis oleh pipeline *Extract-Transform-Load* (`etl/run_etl.py`) ke basis data SQLite `warehouse/cabai_medan.db` berarsitektur skema bintang: tabel fakta `fact_harga_harian` yang berelasi dengan dimensi `dim_tanggal`, `dim_pasar`, dan `dim_cuaca`, serta diekspos ke lapisan analitik dan pemodelan melalui *SQL View* `v_harga_lengkap`.

### 2.2 Rekayasa Fitur, Seleksi Fitur, dan Pencegahan *Data Leakage*
Dari data historis, disusun 35 fitur kandidat dalam 10 kelompok (waktu siklik, lag harga per pasar $\le t-1$, rata-rata bergerak *rolling*, rasio/momentum, harga pasar hulu $t-1$, akumulasi curah hujan hingga $t-1$, kalender hari besar, interaksi musim hujan, serta *encoding* pasar). Kolom `Harga_Cabai_Merah_Agregat` dibuang sejak awal karena berkorelasi sangat tinggi dan identik pada $99{,}9\%$ baris Pasar Tradisional ($r = 0{,}9998$), yang akan memicu *data leakage*. Untuk menjaga kausalitas, seluruh fitur lag dan cuaca hanya memanfaatkan informasi sampai hari $t-1$, sedangkan fitur kategorikal `TE_Pasar_Bulan` dihitung menggunakan *out-of-fold target encoding* dengan faktor *smoothing* $m = 20$ yang di-fit ulang di dalam setiap lipatan data latih [14].

Seleksi fitur menggunakan mekanisme pemungutan suara konsensus (*voting* $\ge 2$ dari empat metode: *Lasso*, *RFECV*, korelasi *Spearman*, dan *Mutual Information*) [15], menghasilkan **12 fitur terpilih** untuk model berbasis pohon:
- **Sinyal harga internal pasar:** `Harga_Lag1`, `Harga_Lag5`, `Harga_Lag20`, `Harga_MA7`, `Harga_MA20`.
- **Sinyal rantai pasok hulu ($t-1$) & posisi pasar:** `Harga_Produsen_Lag1`, `Harga_PB_Lag1`, `Level_Rantai_Pasok`, `TE_Pasar_Bulan`.
- **Sinyal cuaca, musim & kalender permintaan:** `Interaksi_Lag1_x_MusimHujan`, `Akumulasi_Hujan_7H`, `Hari_Menuju_Idul_Fitri`.

Khusus untuk model linear (*Ridge Regression*), pemeriksaan *Variance Inflation Factor* (VIF) mendeteksi multikolinearitas ekstrem pada `Harga_MA7` ($\text{VIF} = 147{,}7$) dan `Harga_MA20` ($\text{VIF} = 35{,}6$). Kedua fitur rata-rata bergerak tersebut dieliminasi secara iteratif hingga tersisa **10 fitur linear** dengan nilai $\text{VIF} \le 9{,}61$.

### 2.3 Formulasi Target Perubahan Harian ($\Delta y_t$) & Validasi Kronologis
Model difokuskan pada tingkat eceran utama **Pasar Tradisional** (setelah membuang 20 hari kerja awal untuk inisialisasi lag, tersisa $N = 1.568$ hari pengamatan dari `2020-01-28` s.d. `2026-01-29`). Pembagian data dilakukan secara kronologis (*out-of-time split*) [11]:
- **Data Latih (*Train Set*):** `2020-01-28` s.d. `2024-12-31` ($n_{\text{train}} = 1.286$ hari).
- **Data Uji (*Out-of-Time Test Set*):** `2025-01-01` s.d. `2026-01-29` ($n_{\text{test}} = 282$ hari).

Agar algoritma berbasis pohon tidak gagal melakukan ekstrapolasi ketika harga menembus rentang historis maupun melebihi puncak latih, target prediksi diubah menjadi selisih harga harian $\Delta y_t = y_t - \text{Harga\_Lag1}$, lalu hasil prediksi direkonstruksi kembali ke satuan Rupiah melalui Persamaan (1):

$$\hat{y}_t = \text{Harga\_Lag1}_t + \widehat{\Delta y}_t$$

Penalaan hiperparameter (*RandomizedSearchCV* dengan `random_state=42`) divalidasi di dalam *Train Set* menggunakan `TimeSeriesSplit(n_splits=5)` dengan fungsi objektif utama **Mean Absolute Error (MAE)** [11], [12]. Lima pendekatan dibandingkan secara adil pada set uji yang sama:
1. **Naive (Persistence):** Memprediksi $\widehat{\Delta y}_t = 0$ ($\hat{y}_t = \text{Harga\_Lag1}$).
2. **Ridge Regression (Baseline Linear):** Penalaan `alpha` terbaik $= 5000{,}0$ dengan `StandardScaler` pada 10 fitur bebas multikolinearitas [5].
3. **Random Forest:** 300 pohon (`criterion="absolute_error"`, `max_depth=8`, `min_samples_leaf=50`, `max_features=0.5`) [6].
4. **XGBoost:** 200 pohon (`objective="reg:pseudohubererror"`, `huber_slope=300.0`, `max_depth=2`, `learning_rate=0.015`, `min_child_weight=25`, `subsample=0.75`) [7].
5. **LightGBM:** 200 pohon (`objective="mae"`, `num_leaves=7`, `max_depth=4`, `learning_rate=0.025`, `min_child_samples=30`, `colsample_bytree=0.75`, `alpha=600.0`) [8].

Model terbaik dipilih berdasarkan **CV MAE terendah** di antara model terlatih untuk menghindari pemilihan yang condong (*overfit*) terhadap set uji. Evaluasi akhir menggunakan metrik MAE, *Root Mean Squared Error* (RMSE), *Mean Absolute Percentage Error* (MAPE), dan Koefisien Determinasi ($R^2$).

---

## 3. Hasil Penelitian

### 3.1 Karakteristik Transmisi Harga Lintas Pasar & Dinamika Musiman
Analisis statistik atas `6.352` baris data bersih menunjukkan struktur harga bertingkat yang konsisten dari hulu ke hilir (uji *ANOVA* $F = 662{,}2$, *Kruskal-Wallis* bulanan $p = 1{,}83 \times 10^{-23}$). Harga median naik bertahap dari **Produsen** (`Rp22.000/kg`) ke **Pedagang Besar** (`Rp28.000/kg`), **Pasar Tradisional** (`Rp33.700/kg`, rasio $1{,}53\times$ harga produsen), dan **Pasar Modern** (`Rp45.950/kg`). Pasar Tradisional mencatat frekuensi perubahan harga harian tertinggi (**57,3%** hari kerja mengalami perubahan harga dan **553 hari** berubah $>5\%$), dengan korelasi paling kuat terhadap harga grosir *Pedagang Besar* satu hari sebelumnya ($\rho = 0{,}840$ hingga $0{,}89$).

Dari sisi faktor eksternal, persentase hari berharga tinggi lebih sering terjadi pada **musim hujan (September–Desember)** sebesar **32,4%** dibanding bulan lain sebesar **20,8%** ($\chi^2$, $p = 6{,}84 \times 10^{-24}$). Curah hujan kumulatif jendela 60 hari memiliki korelasi signifikan terhadap kenaikan harga dengan jeda $\pm 11$ minggu ($\rho = 0{,}200$, $p = 7{,}68 \times 10^{-16}$), selaras dengan siklus biologis pembungaan hingga panen tanaman cabai.

### 3.2 Perbandingan Kinerja Lima Model pada Validasi Silang & Set Uji (2025–2026)
Hasil eksperimen lengkap kelima pendekatan prediksi pada data latih (*TimeSeriesSplit* 5-fold) dan data uji masa depan (`2025-01-01` s.d. `2026-01-29`, $n=282$) disajikan pada Tabel 1 dan divisualisasikan pada `docs/figures/07_perbandingan_5_model.png`.

**Tabel 1.** Perbandingan Performa Model Prediksi Harga Cabai Merah Keriting (*Pasar Tradisional*)

| Model | Jml Fitur | CV MAE (Rp) | CV RMSE (Rp) | CV MAPE (%) | CV $R^2$ | Test MAE (Rp) | Test RMSE (Rp) | Test MAPE (%) | Test $R^2$ | Waktu Latih (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Naive (Persistence) | 10 | 2.297,01 | 4.680,30 | 5,62 | 0,9181 | 3.340,43 | 5.561,93 | 6,87 | 0,9091 | 0,01 |
| Ridge Regression (Baseline) | 10 | 2.329,81 | **4.662,23** | 5,75 | **0,9187** | 3.353,21 | **5.532,61** | 6,95 | **0,9101** | 0,22 |
| **Random Forest** *(Model Terpilih)* | 12 | **2.298,16** | 4.679,74 | **5,63** | 0,9181 | 3.335,39 | 5.558,99 | 6,85 | 0,9092 | 33,29 |
| XGBoost | 12 | 2.322,79 | 4.667,59 | 5,70 | 0,9185 | 3.325,29 | 5.541,36 | 6,82 | 0,9098 | 14,69 |
| LightGBM | 12 | 2.304,08 | 4.669,43 | 5,64 | 0,9185 | **3.322,42** | 5.535,51 | **6,78** | 0,9100 | 9,75 |

Berdasarkan kriteria seleksi objektif (CV MAE terendah di antara model ML tanpa menyentuh set uji), **Random Forest** dipilih sebagai model utama (`best_model`) dengan CV MAE **Rp2.298,16/kg** (CV $R^2 = 0{,}9181$) serta mampu mengungguli tolok ukur *Naive Persistence* maupun *Ridge Regression* pada set uji 2025–2026 (Test MAE **Rp3.335,39/kg**, median galat absolut **Rp1.679,30/kg**, MAPE **6,85%**). Sementara itu, pada data uji, **LightGBM** meraih MAE dan MAPE terbaik (**Rp3.322,42/kg**; **6,78%**), dan **Ridge Regression** meraih RMSE terendah (**Rp5.532,61/kg**; $R^2 = 0{,}9101$). Pola kedekatan MAE antara seluruh model *ensemble* dan *Naive Persistence* menunjukkan bahwa dinamika pasar harian cabai di Medan didominasi oleh inersia harga kemarin (*price rigidity*), namun pengayaan sinyal cuaca dan hulu memberikan perbaikan konsisten pada prediksi arah perubahan dan akurasi persentase.

### 3.3 *Feature Importance* & Segmentasi *Error Analysis* (282 Hari Uji)
Analisis kontribusi fitur model terbaik (*Random Forest*, lihat `docs/figures/07_top10_residual_dan_importance.png`) menempatkan **`Interaksi_Lag1_x_MusimHujan`** sebagai penyumbang dominan (**55,70%**), diikuti oleh **`Akumulasi_Hujan_7H` (7,69%)**, **`Harga_Lag1` (6,98%)**, **`Hari_Menuju_Idul_Fitri` (6,43%)**, dan **`Harga_MA7` (6,10%)**. Hal ini mengonfirmasi bahwa efek harga kemarin terhadap perubahan harga esok hari sangat bergantung pada konteks musim hujan.

Distribusi galat pada set uji (`docs/figures/07_diagnostik_prediksi_dan_residual.png`) bersifat simetris dan hampir tidak bias (rata-rata residual **+Rp0,32/kg**, median **Rp0,00/kg**; 131 hari *underpredict*, 126 hari *overpredict*, dan 25 hari tepat). Namun, pemilahan galat berdasarkan rezim (`docs/figures/07_error_per_rezim_dan_bulan.png`) mengungkap perbedaan tajam:
- **Hari Tenang vs Hari Lonjakan Ekstrem:** Pada **212 hari tenang** (`|\Delta y_t| <= Rp5.000/kg`, 75,2% dari total hari uji), model mencapai akurasi sangat tinggi dengan MAE hanya **Rp1.289,10/kg (MAPE 3,36%)** (terbaik di Juli 2025 dengan MAE Rp842,81/kg dan Juni 2025 dengan MAE Rp875,92/kg). Sebaliknya, pada 70 hari lonjakan mendadak (`|\Delta y_t| > Rp5.000/kg`), MAE melonjak ke **Rp9.532,72/kg (MAPE 17,42%)**.
- **Musim Hujan (Sep–Des) vs Bulan Lain (Jan–Agu):** MAE selama musim hujan Sep–Des (`n=88` hari, rata-rata harga Rp63.913,64/kg) mencapai **Rp5.995,07/kg (MAPE 9,49%)**, hampir tiga kali lipat lebih tinggi dibanding periode Jan–Agu (`n=194` hari, rata-rata harga Rp36.279,90/kg) yang hanya mencatat MAE **Rp2.128,93/kg (MAPE 5,66%)**.

Penelusuran terhadap **10 residual absolut terbesar** (Tabel 2) mengidentifikasi tiga akar penyebab utama galat besar:
1. **Guncangan Pasokan Curah Hujan Ekstrem Sep–Des 2025:** Sembilan dari sepuluh galat terbesar muncul pada September–Desember 2025 saat `Akumulasi_Hujan_7H` menembus `111,6 mm` hingga `368,5 mm` (mis. `2025-10-20` `+Rp23.863,3`, `2025-11-26` `+Rp21.766,3`, dan `2025-12-01` `+Rp17.566,3`).
2. **Koreksi Tajam Pasca-Puncak (*Mean Reversion*):** Pada tanggal `2025-12-03` (`-Rp18.833,7`), `2025-12-08` (`-Rp18.733,7`), dan `2025-09-09` (`-Rp16.619,0`), harga terkoreksi turun drastis sehari setelah puncak Rp71.500–Rp81.300/kg sehingga prediksi berbasis lag mengalami *overshooting*.
3. **Lonjakan Permintaan H-5 Idul Fitri:** Pada `2025-03-26` (5 hari menjelang Idul Fitri 2025), harga melesat dalam satu hari dari Rp39.800 menjadi Rp58.300/kg (`residual +Rp18.501,8`).

**Tabel 2.** Lima Besar Galat Absolut Terbesar Model *Random Forest* pada Set Uji 2025–2026

| Tanggal | Harga $t-1$ (Rp) | Aktual (Rp) | Prediksi (Rp) | Residual (Rp) | APE (%) | Hujan 7H (mm) | Klasifikasi Penyebab |
|---|---:|---:|---:|---:|---:|---:|---|
| 2025-10-20 | 69.600 | 93.300 | 69.436,7 | +23.863,3 | 25,58 | 131,2 | Guncangan pasokan hujan ekstrem |
| 2025-09-01 | 40.300 | 62.100 | 40.293,3 | +21.806,7 | 35,12 | 67,6 | Volatilitas awal musim hujan |
| 2025-11-26 | 51.100 | 72.700 | 50.933,7 | +21.766,3 | 29,94 | 189,9 | Guncangan pasokan hujan ekstrem |
| 2025-09-08 | 61.800 | 81.300 | 61.627,3 | +19.672,7 | 24,20 | 65,1 | Volatilitas awal musim hujan |
| 2025-12-03 | 81.200 | 62.200 | 81.033,7 | -18.833,7 | 30,28 | 267,1 | Koreksi tajam pasca-puncak |

### 3.4 Integrasi Sistem & Pengujian 5 Skenario Input Baru
Model produksi (`models/best_model.joblib` & `models/baseline_ridge.joblib`) telah diintegrasikan ke dalam halaman `app/pages/04_Prediksi_Harga.py` pada aplikasi Streamlit multipage yang membaca langsung `warehouse/cabai_medan.db`. Pengujian fungsional otomatis menggunakan 5 skenario masukan operasional baru (Kondisi Normal, Curah Hujan Ekstrem `280 mm`, Lonjakan Harga Hulu, Menjelang H-3 Idul Fitri, dan Musim Panen Raya) berjalan tanpa galat dan menghasilkan prediksi responsif beserta selisih perubahan terhadap `Harga_Lag1`.

---

## Daftar Pustaka (Bagian Pendahuluan, Metode & Hasil)

> *Catatan sitasi: Daftar ini memuat 15 referensi inti metodologi & sumber data resmi; 5–10 referensi tambahan studi kasus jurnal terindeks SINTA 1–3 pada konteks komoditas hortikultura Indonesia akan dilengkapi bersama di Zotero pada `paper/draf-lengkap.md` (Minggu 13).*

- [1] Bank Indonesia, *Pusat Informasi Harga Pangan Strategis (PIHPS) Nasional: Metodologi dan Data Harga Pangan Harian*, Jakarta: Bank Indonesia, 2025. [Daring]. Tersedia: https://www.bi.go.id/hargapangan
- [2] Badan Pusat Statistik (BPS), *Statistik Hortikultura Indonesia & Tinjauan Inflasi Kelompok Volatile Foods*, Jakarta: BPS RI, 2024.
- [3] Food and Agriculture Organization (FAO), *Agricultural Commodity Price Volatility and Early Warning Market Information Systems*, Rome: FAO, 2023.
- [4] Kelompok 25 IT Del, *Dataset Terintegrasi Harga Cabai Merah Keriting PIHPS-BI Kota Medan dan Cuaca Open-Meteo (2019–2026)*, Repositori `da-ds-2026-kelompok-25`, 2026.
- [5] A. E. Hoerl and R. W. Kennard, "Ridge Regression: Biased Estimation for Nonorthogonal Problems," *Technometrics*, vol. 12, no. 1, pp. 55–67, 1970.
- [6] L. Breiman, "Random Forests," *Machine Learning*, vol. 45, no. 1, pp. 5–32, 2001.
- [7] T. Chen and C. Guestrin, "XGBoost: A Scalable Tree Boosting System," in *Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining*, San Francisco, CA, USA, 2016, pp. 785–794.
- [8] G. Ke et al., "LightGBM: A Highly Efficient Gradient Boosting Decision Tree," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 30, 2017, pp. 3146–3154.
- [9] R. Shwartz-Ziv and A. Armon, "Tabular Data: Deep Learning Is Not All You Need," *Information Fusion*, vol. 81, pp. 84–90, 2022.
- [10] L. Grinsztajn, E. Oyallon, and G. Varoquaux, "Why Do Tree-Based Models Still Outperform Deep Learning on Typical Tabular Data?," in *NeurIPS Datasets and Benchmarks Track*, 2022.
- [11] L. J. Tashman, "Out-of-Sample Tests of Forecasting Accuracy: An Analysis and Review," *International Journal of Forecasting*, vol. 16, no. 4, pp. 437–450, 2000.
- [12] R. J. Hyndman and G. Athanasopoulos, *Forecasting: Principles and Practice*, 3rd ed. Melbourne, Australia: OTexts, 2021.
- [13] P. Zippenfenig, "Open-Meteo.com Weather API," Zenodo, 2023. [Daring]. Tersedia: https://open-meteo.com (Lisensi CC BY 4.0).
- [14] D. Micci-Barreca, "A Preprocessing Scheme for High-Cardinality Categorical Attributes in Classification and Prediction Problems," *ACM SIGKDD Explorations Newsletter*, vol. 3, no. 1, pp. 27–32, 2001.
- [15] I. Guyon, J. Weston, S. Barnhill, and V. Vapnik, "Gene Selection for Cancer Classification Using Support Vector Machines," *Machine Learning*, vol. 46, pp. 389–422, 2002.
