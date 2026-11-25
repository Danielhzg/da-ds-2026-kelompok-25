-- =============================================================================
-- Skema Bintang Data Warehouse Harga Cabai Merah Keriting Kota Medan
-- Kelompok 25 - DASI & DALIS (Lead Warehouse & ETL: Dame Sisri Rumapea)
-- Database: SQLite (warehouse/cabai_medan.db)
-- =============================================================================

PRAGMA foreign_keys = ON;

-- Hapus view & tabel lama jika membangun ulang skema
DROP VIEW IF EXISTS v_harga_lengkap;
DROP TABLE IF EXISTS fact_harga_harian;
DROP TABLE IF EXISTS dim_cuaca;
DROP TABLE IF EXISTS dim_pasar;
DROP TABLE IF EXISTS dim_tanggal;

-- -----------------------------------------------------------------------------
-- 1. Tabel Dimensi: dim_tanggal
-- Menyimpan atribut kalender harian, musim di Indonesia, dan hari libur nasional
-- -----------------------------------------------------------------------------
CREATE TABLE dim_tanggal (
    tanggal_key          INTEGER PRIMARY KEY,         -- Format YYYYMMDD (mis. 20200101)
    tanggal              TEXT    NOT NULL UNIQUE,     -- Format ISO YYYY-MM-DD
    tahun                INTEGER NOT NULL,
    kuartal              INTEGER NOT NULL CHECK (kuartal BETWEEN 1 AND 4),
    bulan                INTEGER NOT NULL CHECK (bulan BETWEEN 1 AND 12),
    nama_bulan           TEXT    NOT NULL,            -- Januari .. Desember
    hari                 INTEGER NOT NULL CHECK (hari BETWEEN 1 AND 31),
    hari_ke_dalam_minggu INTEGER NOT NULL CHECK (hari_ke_dalam_minggu BETWEEN 0 AND 6), -- 0=Senin .. 6=Minggu
    nama_hari            TEXT    NOT NULL,            -- Senin .. Minggu
    akhir_pekan          INTEGER NOT NULL DEFAULT 0 CHECK (akhir_pekan IN (0, 1)),
    musim                TEXT    NOT NULL,            -- Hujan / Kemarau
    is_hari_libur        INTEGER NOT NULL DEFAULT 0 CHECK (is_hari_libur IN (0, 1)),
    nama_libur           TEXT                         -- Nama hari libur nasional (NULL jika bukan libur)
);

-- -----------------------------------------------------------------------------
-- 2. Tabel Dimensi: dim_pasar
-- Menyimpan 4 tingkat rantai pasok pasar PIHPS Bank Indonesia di Kota Medan
-- -----------------------------------------------------------------------------
CREATE TABLE dim_pasar (
    pasar_key            INTEGER PRIMARY KEY,
    nama_pasar           TEXT    NOT NULL UNIQUE,     -- Produsen, Pedagang Besar, Pasar Tradisional, Pasar Modern
    tingkat_rantai_pasok TEXT    NOT NULL,            -- Hulu, Grosir, Eceran Tradisional, Eceran Modern
    urutan_rantai        INTEGER NOT NULL UNIQUE CHECK (urutan_rantai BETWEEN 1 AND 4),
    keterangan           TEXT
);

-- -----------------------------------------------------------------------------
-- 3. Tabel Dimensi: dim_cuaca
-- Menyimpan kondisi cuaca harian Kota Medan dari Open-Meteo
-- -----------------------------------------------------------------------------
CREATE TABLE dim_cuaca (
    cuaca_key                INTEGER PRIMARY KEY,     -- Format YYYYMMDD (selaras dengan tanggal_key)
    tanggal                  TEXT    NOT NULL UNIQUE, -- Format ISO YYYY-MM-DD
    kode_wmo                 INTEGER NOT NULL,
    deskripsi_cuaca          TEXT    NOT NULL,        -- Deskripsi kode WMO dalam Bahasa Indonesia
    suhu_rata2_c             REAL    NOT NULL,
    curah_hujan_mm           REAL    NOT NULL,
    kecepatan_angin_maks_kmh REAL    NOT NULL,
    kategori_hujan           TEXT    NOT NULL         -- Tidak Hujan, Hujan Ringan, Hujan Sedang, Hujan Lebat
);

-- -----------------------------------------------------------------------------
-- 4. Tabel Fakta: fact_harga_harian
-- Grain: 1 baris = 1 komoditas (Cabai Merah Keriting) pada 1 tanggal & 1 pasar
-- -----------------------------------------------------------------------------
CREATE TABLE fact_harga_harian (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal_key           INTEGER NOT NULL,
    pasar_key             INTEGER NOT NULL,
    cuaca_key             INTEGER NOT NULL,
    harga_cabai_keriting  INTEGER NOT NULL CHECK (harga_cabai_keriting > 0),
    harga_cabai_agregat   INTEGER NOT NULL CHECK (harga_cabai_agregat > 0),
    perubahan_harian      REAL,                       -- Selisih harga vs hari kerja sebelumnya per pasar (Rp/kg)
    persen_perubahan      REAL,                       -- Persentase perubahan harian (%)
    markup_thd_produsen   REAL    NOT NULL,           -- Selisih harga pasar terhadap harga Produsen hari yang sama (Rp/kg)
    is_imputasi           INTEGER NOT NULL DEFAULT 0 CHECK (is_imputasi IN (0, 1)),
    FOREIGN KEY (tanggal_key) REFERENCES dim_tanggal (tanggal_key),
    FOREIGN KEY (pasar_key)   REFERENCES dim_pasar   (pasar_key),
    FOREIGN KEY (cuaca_key)   REFERENCES dim_cuaca   (cuaca_key),
    UNIQUE (tanggal_key, pasar_key)
);

-- Indeks untuk mempercepat query analitik & dashboard
CREATE INDEX idx_fact_tanggal ON fact_harga_harian (tanggal_key);
CREATE INDEX idx_fact_pasar   ON fact_harga_harian (pasar_key);
CREATE INDEX idx_fact_cuaca   ON fact_harga_harian (cuaca_key);

-- -----------------------------------------------------------------------------
-- 5. SQL View Analitik: v_harga_lengkap
-- Menggabungkan tabel fakta dengan ketiga tabel dimensi untuk konsumsi
-- Dashboard Streamlit (app/) dan Pipeline Modelling (models/train.py)
-- -----------------------------------------------------------------------------
CREATE VIEW v_harga_lengkap AS
SELECT
    f.id,
    f.tanggal_key,
    t.tanggal,
    t.tahun,
    t.kuartal,
    t.bulan,
    t.nama_bulan,
    t.hari,
    t.nama_hari,
    t.akhir_pekan,
    t.musim,
    t.is_hari_libur,
    t.nama_libur,
    f.pasar_key,
    p.nama_pasar             AS kategori_pasar,
    p.tingkat_rantai_pasok,
    p.urutan_rantai,
    f.cuaca_key,
    c.kode_wmo,
    c.deskripsi_cuaca,
    c.suhu_rata2_c,
    c.curah_hujan_mm,
    c.kecepatan_angin_maks_kmh,
    c.kategori_hujan,
    'Cabai Merah Keriting'   AS komoditas,
    f.harga_cabai_keriting,
    f.harga_cabai_agregat,
    f.perubahan_harian,
    f.persen_perubahan,
    f.markup_thd_produsen,
    f.is_imputasi
FROM fact_harga_harian f
JOIN dim_tanggal t ON f.tanggal_key = t.tanggal_key
JOIN dim_pasar   p ON f.pasar_key   = p.pasar_key
JOIN dim_cuaca   c ON f.cuaca_key   = c.cuaca_key;
