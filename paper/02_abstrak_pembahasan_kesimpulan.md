# Draf Naskah Jurnal — Bagian Abstrak, Pembahasan, Kesimpulan, dan Daftar Pustaka Tambahan (K6)

> **Catatan Penyusunan (Minggu 12):** Dokumen ini merupakan kontribusi bagian *Abstrak, Pembahasan Lanjutan, Kesimpulan, Pernyataan Ketersediaan Data, dan Daftar Pustaka Tambahan* (Lead Data Analitik: **Dame Sisri Rumapea**, 41426085). Seluruh angka bersumber langsung dari `models/metrics.json`, `data/processed/02_ringkasan.json`, dan `warehouse/cabai_medan.db` serta selaras penuh dengan `paper/01_pendahuluan_metode_hasil.md` (Lead DS: Daniel Haganta Ginting). Kedua dokumen akan digabungkan menjadi draf utuh pada Minggu 13 (`paper/draf-lengkap.md`).

---

## Abstrak

Fluktuasi harga cabai merah keriting merupakan pemicu utama inflasi kelompok *volatile foods* di Kota Medan akibat sifat komoditas yang mudah rusak, sensitivitas terhadap curah hujan, serta rantai pasok empat tingkat. Penelitian ini mengembangkan sistem terintegrasi berbasis *Data Warehouse* skema bintang SQLite yang menggabungkan data harga harian Pusat Informasi Harga Pangan Strategis (PIHPS) Bank Indonesia pada empat tingkat pasar (Produsen, Pedagang Besar, Pasar Tradisional, dan Pasar Modern) dengan data cuaca historis Open-Meteo selama periode 2019–2026, menghasilkan 6.352 observasi bersih. Lima pendekatan pemodelan prediksi perubahan harga harian (*Naive Persistence*, *Ridge Regression*, *Random Forest*, *XGBoost*, dan *LightGBM*) dievaluasi secara kronologis menggunakan *TimeSeriesSplit* lima lipatan bebas kebocoran data pada set latih (*n* = 1.286) dan diuji pada data masa depan 2025–2026 (*n* = 282). *Random Forest* terpilih sebagai model terbaik berdasarkan CV MAE terendah sebesar Rp2.298,16/kg, mencapai Test MAE Rp3.335,39/kg dan MAPE 6,85%, sedangkan *LightGBM* mencatat Test MAE Rp3.322,42/kg dengan MAPE 6,78%. Analisis galat terpilah menunjukkan akurasi tinggi pada hari tenang dengan MAE Rp1.289,10/kg (MAPE 3,36%), namun meningkat pada periode hujan ekstrem September–Desember 2025 dengan MAE Rp5.995,07/kg (MAPE 9,49%). Seluruh analitik transmisi harga dan modul simulasi prediksi diintegrasikan ke dalam *dashboard* Streamlit untuk mendukung pengendalian inflasi daerah oleh TPID Kota Medan, pedagang, dan konsumen rumah tangga.

**Kata Kunci:** cabai merah keriting, *data warehouse* skema bintang, *random forest*, prediksi perubahan harga, inflasi pangan, Kota Medan, Streamlit

---

## Abstract

Price volatility of curly red chili is a primary driver of *volatile foods* inflation in Medan City due to its perishable nature, sensitivity to rainfall anomalies, and a four-tier supply chain. This study develops an integrated system built upon a SQLite star-schema Data Warehouse combining daily price records from Bank Indonesia's Strategic Food Price Information Center (PIHPS) across four market levels (Producer, Wholesaler, Traditional Market, and Modern Market) with Open-Meteo daily weather data from 2019 to 2026, yielding 6,352 clean rows. Five daily price-change forecasting models (*Naive Persistence*, *Ridge Regression*, *Random Forest*, *XGBoost*, and *LightGBM*) are evaluated chronologically using five-fold *TimeSeriesSplit* without data leakage on the training set (*n* = 1,286) and tested out-of-time on 2025–2026 data (*n* = 282). *Random Forest* is selected as the primary production model based on the lowest ML cross-validation MAE of IDR 2,298.16/kg, achieving a test MAE of IDR 3,335.39/kg and MAPE of 6.85%, while *LightGBM* records the lowest test MAE of IDR 3,322.42/kg (MAPE 6.78%). Stratified error analysis demonstrates strong accuracy on calm days (MAE IDR 1,289.10/kg; MAPE 3.36%) but higher errors during extreme rainfall in September–December 2025 (MAE IDR 5,995.07/kg; MAPE 9.49%). All supply-chain analytics and forecasting modules are deployed in a multipage Streamlit dashboard to support Medan City's regional inflation control team, traders, and household consumers.

**Keywords:** curly red chili, star-schema data warehouse, random forest, price-change forecasting, food inflation, Medan City, Streamlit

---

## 4. Pembahasan

### 4.1 Dinamika Transmisi Harga Hulu–Hilir Empat Tingkat Pasar Kota Medan

Integrasi 6.352 observasi bersih ke dalam model dimensional skema bintang (`1` tabel fakta dan `3` tabel dimensi sesuai prinsip pemodelan Kimball & Ross [16] serta teknik pembersihan ETL Kimball & Caserta [17]) memungkinkan penelusuran transmisi harga lintas empat simpul rantai pasok secara konsisten. Data historis menunjukkan eskalasi median harga yang tegas dari hulu ke hilir: **Produsen Rp22.000/kg → Pedagang Besar Rp28.000/kg → Pasar Tradisional Rp33.700/kg → Pasar Modern Rp45.950/kg** (ANOVA $F = 662{,}2$). Secara agregat, median harga Pasar Tradisional berada pada rasio **1,53×** tingkat Produsen dan **1,21×** tingkat Pedagang Besar.

Temuan penting lain adalah disparitas frekuensi penyesuaian harga harian. **Pasar Tradisional** mencatat perubahan harga pada **57,3% hari kerja** (dengan 553 hari kerja mengalami perubahan harian >5%), jauh melampaui Pedagang Besar (**17,8%**), Pasar Modern (**13,0%**), dan Produsen (**4,6%**, di mana 70 dari 73 kali perubahan harga terjadi secara periodik pada tanggal 25–27 setiap bulan). Pola ini memperlihatkan karakteristik *asymmetric price transmission* [19]: saat terjadi gangguan pasokan, harga eceran Pasar Tradisional langsung bereaksi harian dan melebarkan *markup* terhadap Produsen maupun Pedagang Besar, sementara penyesuaian turun pasca-puncak berlangsung lebih lambat atau memicu koreksi tajam.

### 4.2 Interpretasi Dominasi Fitur Interaksi Momentum Harga dan Musim Hujan

Evaluasi *permutation importance* pada model terpilih **Random Forest** menunjukkan bahwa dua fitur teratas menyumbang **63,39%** dari total kontribusi prediksi, yakni **`Interaksi_Lag1_x_MusimHujan` (55,70%)** dan **`Akumulasi_Hujan_7H` (7,69%)**, diikuti oleh `Harga_Lag1` (**6,98%**), `Hari_Menuju_Idul_Fitri` (**6,43%**), dan `Harga_MA7` (**6,10%**). Dominasi fitur interaksi tersebut menegaskan bahwa dinamika perubahan harga harian cabai merah keriting di Kota Medan bersifat *regime-dependent*: inersia harga harian sangat kuat (autokorelasi lag-1 $\rho = 0{,}961$), tetapi arah serta amplitudo guncangan hari berikutnya berubah drastis ketika harga tinggi bertemu periode musim hujan September–Desember (proporsi hari mahal **32,4%** dibanding **20,8%** di bulan lain). Penggabungan komponen cuaca kumulatif 7 hari memperkuat sinyal gangguan logistik dan penurunan mutu hasil panen cabai di lapangan.

### 4.3 Perbandingan Hasil dengan Studi Peramalan Komoditas Pangan Terdahulu

Dari sisi performa prediktif pada set uji *out-of-time* 2025–2026 ($n = 282$), seluruh model *ensemble* berbasis pohon (**LightGBM** Test MAE Rp3.322,42/kg, MAPE 6,78%; **XGBoost** Test MAE Rp3.325,29/kg, MAPE 6,82%; **Random Forest** Test MAE Rp3.335,39/kg, MAPE 6,85%) berhasil mengungguli *baseline* **Naive Persistence** (Test MAE Rp3.340,43/kg, MAPE 6,87%) maupun model linear **Ridge Regression** (Test MAE Rp3.353,21/kg, MAPE 6,95%). Keunggulan metode *tree-based ensemble* atas model linear sejalan dengan temuan komparatif pada literatur peramalan berbasis data tabular dan komoditas pangan mutakhir [9], [10], [20]–[24].

Secara khusus, studi Rahmah et al. [20] dan Afandi & Supriyanto [21] pada *Jurnal RESTI* memperlihatkan keandalan *Random Forest* dan *XGBoost* ketika memadukan riwayat deret waktu dengan indikator cuaca. Sementara itu, Lestari et al. [22], Riando & Afiyati [23], serta Erissafilla & Sulistyono [24] melaporkan capaian MAPE di kisaran 5–10% pada peramalan harga cabai dan komoditas hortikultura menggunakan *Random Forest* dan *gradient boosting*. Dengan memformulasi target sebagai perubahan harga harian ($\Delta y_t$) yang diintegrasikan kembali ke $\hat{y}_t = \text{Harga\_Lag1} + \widehat{\Delta y}_t$, penelitian ini menjaga akurasi di bawah ambang MAPE 7% sekaligus menghindari kegagalan ekstrapolasi harga absolut pada periode lonjakan tinggi.

### 4.4 Bedah Akar Masalah Galat Besar pada Hujan Ekstrem Sep–Des dan H-5 Idul Fitri

Pemetaan kinerja terpilah mengungkap bahwa akurasi **Random Forest** sangat tajam pada **hari tenang** ($|\Delta y_t| \le \text{Rp5.000}$, $n = 212$) dengan **MAE Rp1.289,10/kg (MAPE 3,36%)** serta pada periode **Januari–Agustus** ($n = 194$) dengan **MAE Rp2.128,93/kg (MAPE 5,66%)**. Sebaliknya, pada **musim hujan puncak September–Desember** ($n = 88$), galat meningkat menjadi **MAE Rp5.995,07/kg (MAPE 9,49%)**. Penelusuran 10 residual terbesar pada `models/metrics.json` mengonfirmasi tiga akar masalah utama:

1. **Guncangan Pasokan Hujan Ekstrem September–Desember 2025:** Sembilan dari sepuluh galat terbesar terjadi pada periode ini ketika `Akumulasi_Hujan_7H` menembus 111,6 mm hingga 368,5 mm (seperti pada `2025-10-20` dengan residual `+Rp23.863,3` saat hujan 7H `131,2 mm`, `2025-11-26` `+Rp21.766,3` saat `189,9 mm`, dan `2025-12-01` `+Rp17.566,3` saat `368,5 mm`).
2. **Pembalikan Tajam Pasca-Puncak (*Mean Reversion*):** Tiga galat negatif terbesar (`2025-12-03` `-Rp18.833,7`, `2025-12-08` `-Rp18.733,7`, dan `2025-09-09` `-Rp16.619,0`) terjadi tepat sehari setelah harga menembus Rp71.500–Rp81.300/kg lalu terkoreksi cepat ketika pasokan susulan masuk ke pasar.
3. **Lonjakan Permintaan H-5 Idul Fitri:** Satu galat besar di luar musim hujan muncul pada `2025-03-26` (H-5 Idul Fitri 2025, residual `+Rp18.501,8`, lonjakan harian Rp39.800 → Rp58.300/kg). Berbeda dari tren Idul Fitri 2020–2024 yang rata-rata turun -28,7% pada H-7 akibat panen raya, Ramadan–Idul Fitri 2025 justru mencatat kenaikan +7,6% sehingga pola historis berbasis lag gagal mengantisipasi lonjakan satu hari tersebut.

### 4.5 Implikasi Kebijakan Peringatan Dini bagi TPID, Pedagang, & Konsumen

Mengikuti prinsip pelaporan transparan ala *Model Cards* [18] dan kerangka ketahanan pasokan hortikultura [25], temuan analitik dan prediksi diterjemahkan menjadi aksi operasional bagi tiga pemangku kepentingan utama di Kota Medan:
- **TPID & Dinas Ketahanan Pangan Kota Medan:** Mengaktifkan protokol operasi pasar dan kerja sama pasokan antar-daerah secara proaktif setiap kali indikator `Akumulasi_Hujan_7H > 100 mm` muncul pada periode September–Desember, menyiapkan stok *buffer* minimal H-14 menjelang Idul Fitri, serta melakukan audit distribusi apabila rasio harga Pasar Tradisional terhadap Produsen melampaui **1,80×**.
- **Pedagang Besar & Pedagang Eceran:** Memanfaatkan halaman `04_Prediksi_Harga.py` untuk simulasi pengadaan 1 hari ke depan, mendiversifikasi sumber pasokan dari beberapa kabupaten sentra saat curah hujan tinggi, dan menahan pembelian berlebih saat harga eceran menembus >Rp70.000/kg untuk menghindari kerugian akibat *mean reversion*.
- **Konsumen Rumah Tangga:** Memanfaatkan periode pasokan melimpah pada Mei–Juli (median terendah pada **Juni Rp22.900/kg**) untuk pembelian atau pengolahan cabai awet, serta membandingkan kestabilan harga di Pasar Modern saat Pasar Tradisional mengalami lonjakan harian ekstrem.

---

## 5. Kesimpulan dan Saran Pengembangan

### 5.1 Kesimpulan

Penelitian ini berhasil membangun sistem analitik dan prediksi harga cabai merah keriting Kota Medan yang terintegrasi penuh dari ekstraksi data mentah hingga antarmuka web pendukung keputusan:
1. **Data Warehouse & Pipeline ETL Terotomatisasi:** Pipeline `etl/run_etl.py` mengintegrasikan data PIHPS Bank Indonesia dan cuaca Open-Meteo ke dalam skema bintang SQLite `warehouse/cabai_medan.db` berisi `6.352` baris bersih (`1` fakta, `3` dimensi, `1` *view* analitik `v_harga_lengkap`) dengan integritas referensial 100% tanpa pelanggaran kunci asing.
2. **Pemodelan Bebas Kebocoran Data:** Formulasi target perubahan harga harian ($\Delta y_t$) yang dievaluasi dengan `TimeSeriesSplit(n_splits=5)` menempatkan **Random Forest** sebagai model produksi terbaik (CV MAE **Rp2.298,16/kg**, Test MAE **Rp3.335,39/kg**, MAPE **6,85%**) bersama **LightGBM** (Test MAE **Rp3.322,42/kg**, MAPE **6,78%**), mengungguli *Naive Persistence* maupun *Ridge Regression* pada set uji 2025–2026 serta mencapai akurasi sangat presisi pada hari tenang (MAE **Rp1.289,10/kg**, MAPE **3,36%**).
3. **Analitik Transmisi Harga & Dashboard Interaktif:** Aplikasi Streamlit multipage (halaman utama serta 4 halaman khusus: `01_Ringkasan_KPI`, `02_Analisis_Mendalam`, `03_Storytelling`, dan `04_Prediksi_Harga`) menyajikan kartu KPI, 7 visualisasi lanjutan dengan *drill-down* dan *cross-filter*, narasi 3 pertanyaan analitik, dan form simulasi prediksi input baru.

### 5.2 Saran Pengembangan

1. **Integrasi Data Eksogen Sentra Produksi:** Menambahkan data curah hujan, luas tanam, dan perkiraan panen dari daerah pemasok utama (seperti Kabupaten Karo, Simalungun, dan Aceh) serta prakiraan cuaca prospektif (+72 jam) untuk menekan galat pada periode guncangan hujan ekstrem September–Desember.
2. **Perluasan Horizon Prediksi Multi-Step:** Mengembangkan prediksi horizon 3–7 hari ke depan dengan interval kepercayaan (*quantile regression* pada LightGBM) guna mendukung perencanaan logistik mingguan pedagang dan TPID.
3. **Otomasi Pembaruan Harian & Pemantauan Drift:** Menghubungkan `etl/run_etl.py` ke penjadwal berkala serta menerapkan pemantauan pergeseran distribusi galat (*concept drift*) setiap kuartal sebelum pelatihan ulang model.

---

## Pernyataan Ketersediaan Data & Etika Penggunaan AI

- **Ketersediaan Data & Kode:** Data harga pangan publik bersumber dari PIHPS Nasional Bank Indonesia (`https://www.bi.go.id/hargapangan`) dan data meteorologi historis bersumber dari Open-Meteo (`https://open-meteo.com`, lisensi CC BY 4.0). Seluruh skrip ETL, DDL *warehouse*, *notebook* eksperimen, *model card*, dan aplikasi Streamlit tersedia pada repositori `da-ds-2026-kelompok-25`.
- **Etika Penggunaan AI:** Perangkat bantu AI generatif digunakan secara terbatas untuk membantu penyusunan kerangka teks, verifikasi konsistensi sitasi, dan penulisan kode pembantu antarmuka; seluruh rancangan metodologi, eksekusi eksperimen, validasi statistik, interpretasi hasil, dan pertanggungjawaban ilmiah sepenuhnya dilakukan serta diverifikasi oleh tim penulis.

---

## Daftar Pustaka Tambahan (`[16]` s.d. `[25]`)

> *Referensi `[1]`–`[15]` tercantum pada `paper/01_pendahuluan_metode_hasil.md`. Daftar berikut melengkapi total pustaka menjadi 25 referensi untuk penggabungan `paper/draf-lengkap.md`.*

- [16] R. Kimball and M. Ross, *The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling*, 3rd ed. Indianapolis, IN, USA: John Wiley & Sons, 2013.
- [17] R. Kimball and J. Caserta, *The Data Warehouse ETL Toolkit: Practical Techniques for Extracting, Cleaning, Conforming, and Delivering Data*. Indianapolis, IN, USA: Wiley Publishing, 2004.
- [18] M. Mitchell et al., "Model Cards for Model Reporting," in *Proc. Conf. Fairness, Accountability, and Transparency (FAT\*)*, Atlanta, GA, USA, 2019, pp. 220–229.
- [19] J. Meyer and S. von Cramon-Taubadel, "Asymmetric Price Transmission: A Survey," *Journal of Agricultural Economics*, vol. 55, no. 3, pp. 581–611, 2004.
- [20] N. D. A. Rahmah, B. Handoko, and A. A. Pravitasari, "Machine Learning Methods for Forecasting Intermittent Tin Ore Production," *Jurnal RESTI (Rekayasa Sistem dan Teknologi Informasi)*, vol. 8, no. 5, 2024. [Daring]. Tersedia: https://jurnal.iaii.or.id/index.php/RESTI/article/view/6462
- [21] A. Afandi and A. Supriyanto, "Thermal Comfort Projection on Northern Coast of Central Java Using Machine Learning," *Jurnal RESTI (Rekayasa Sistem dan Teknologi Informasi)*, vol. 9, no. 4, 2025. [Daring]. Tersedia: https://jurnal.iaii.or.id/index.php/RESTI
- [22] D. R. Lestari, E. A. S. Bangun, F. L. Gaol, and T. Matsuo, "Machine Learning-Based Forecasting of Agricultural Commodity Prices Using Ensemble Models," *Journal of Human, Earth, and Future*, 2025.
- [23] D. Riando and A. Afiyati, "Implementation of XGBoost Algorithm to Predict the Selling Price of Cayenne Peppers in DKI Jakarta," *Eduvest – Journal of Universal Studies*, 2024.
- [24] M. A. Erissafilla and M. Y. Sulistyono, "Data-Driven Model for Predicting Essential Commodity Demand: A Comparative Study of Weekend–Weekday Patterns in Chili Commodities Using Decision Tree and Random Forest Regression," *Journal of Applied Informatics and Computing*, 2026.
- [25] Kementerian Pertanian Republik Indonesia, *Outlook Komoditas Pertanian Subsektor Hortikultura: Cabai Merah*, Jakarta: Pusat Data dan Sistem Informasi Pertanian (Pusdatin) Kementan RI, 2024.
