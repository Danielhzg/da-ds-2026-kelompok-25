"""Modul Transform untuk pembersihan, imputasi, dan pembentukan tabel skema bintang."""

import holidays
import numpy as np
import pandas as pd

URUTAN_PASAR = ["Produsen", "Pedagang Besar", "Pasar Tradisional", "Pasar Modern"]

META_PASAR = [
    (1, "Produsen", "Hulu", 1, "Harga tingkat petani/produsen cabai merah"),
    (2, "Pedagang Besar", "Grosir", 2, "Harga tingkat pedagang besar/grosir"),
    (3, "Pasar Tradisional", "Eceran Tradisional", 3, "Harga eceran pasar tradisional Kota Medan"),
    (4, "Pasar Modern", "Eceran Modern", 4, "Harga eceran pasar modern/ritel modern"),
]

NAMA_BULAN_ID = {
    1: "Januari",
    2: "Februari",
    3: "Maret",
    4: "April",
    5: "Mei",
    6: "Juni",
    7: "Juli",
    8: "Agustus",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Desember",
}

NAMA_HARI_ID = {
    0: "Senin",
    1: "Selasa",
    2: "Rabu",
    3: "Kamis",
    4: "Jumat",
    5: "Sabtu",
    6: "Minggu",
}

DESKRIPSI_WMO_ID = {
    0: "Cerah",
    1: "Cerah Berawan",
    2: "Berawan Sebagian",
    3: "Mendung",
    45: "Berkabut",
    48: "Kabut Beku",
    51: "Gerimis Ringan",
    53: "Gerimis Sedang",
    55: "Gerimis Lebat",
    61: "Hujan Ringan",
    63: "Hujan Sedang",
    65: "Hujan Lebat",
    80: "Hujan Lokal Ringan",
    81: "Hujan Lokal Sedang",
    82: "Hujan Lokal Lebat",
    95: "Badai Petir",
}


def _parse_harga(series: pd.Series) -> pd.Series:
    """Mengonversi teks harga berformat koma ribuan dan '-' menjadi numerik."""
    cleaned = series.astype(str).str.strip().str.replace(",", "", regex=False).replace("-", np.nan)
    return pd.to_numeric(cleaned, errors="coerce")


def _kategori_hujan(curah_hujan_mm: float) -> str:
    """Mengelompokkan intensitas curah hujan harian berdasarkan standar BMKG."""
    if curah_hujan_mm <= 0.0:
        return "Tidak Hujan"
    if curah_hujan_mm < 20.0:
        return "Hujan Ringan"
    if curah_hujan_mm < 50.0:
        return "Hujan Sedang"
    return "Hujan Lebat"


def _build_dim_tanggal(tanggal_unik: pd.DatetimeIndex) -> pd.DataFrame:
    """Membentuk tabel dimensi dim_tanggal lengkap dengan atribut musim dan hari libur."""
    tahun_min = int(tanggal_unik.min().year)
    tahun_max = int(tanggal_unik.max().year)
    libur_id = holidays.country_holidays("ID", years=range(tahun_min, tahun_max + 1))

    rows = []
    for dt in sorted(tanggal_unik):
        tgl_date = dt.date()
        nama_libur = libur_id.get(tgl_date)
        rows.append(
            {
                "tanggal_key": int(dt.strftime("%Y%m%d")),
                "tanggal": dt.strftime("%Y-%m-%d"),
                "tahun": int(dt.year),
                "kuartal": int((dt.month - 1) // 3 + 1),
                "bulan": int(dt.month),
                "nama_bulan": NAMA_BULAN_ID[int(dt.month)],
                "hari": int(dt.day),
                "hari_ke_dalam_minggu": int(dt.dayofweek),
                "nama_hari": NAMA_HARI_ID[int(dt.dayofweek)],
                "akhir_pekan": int(dt.dayofweek >= 5),
                "musim": "Hujan" if dt.month in (10, 11, 12, 1, 2, 3) else "Kemarau",
                "is_hari_libur": int(tgl_date in libur_id),
                "nama_libur": str(nama_libur) if nama_libur else None,
            }
        )
    return pd.DataFrame(rows)


def _build_dim_pasar() -> pd.DataFrame:
    """Membentuk tabel dimensi dim_pasar."""
    return pd.DataFrame(
        META_PASAR,
        columns=["pasar_key", "nama_pasar", "tingkat_rantai_pasok", "urutan_rantai", "keterangan"],
    )


def _build_dim_cuaca(df_cuaca_clean: pd.DataFrame, tanggal_unik: pd.DatetimeIndex) -> pd.DataFrame:
    """Membentuk tabel dimensi dim_cuaca untuk seluruh tanggal pada periode irisan."""
    sub = df_cuaca_clean[df_cuaca_clean["Tanggal"].isin(tanggal_unik)].copy()
    sub = sub.sort_values("Tanggal").drop_duplicates(subset=["Tanggal"])

    sub["cuaca_key"] = sub["Tanggal"].dt.strftime("%Y%m%d").astype(int)
    sub["tanggal"] = sub["Tanggal"].dt.strftime("%Y-%m-%d")
    sub["kode_wmo"] = sub["Kode_Cuaca_WMO"].astype(int)
    sub["deskripsi_cuaca"] = sub["kode_wmo"].map(lambda k: DESKRIPSI_WMO_ID.get(k, f"Kode WMO {k}"))
    sub["suhu_rata2_c"] = sub["Suhu_Rata2_C"].astype(float)
    sub["curah_hujan_mm"] = sub["Curah_Hujan_mm"].astype(float)
    sub["kecepatan_angin_maks_kmh"] = sub["Kecepatan_Angin_Maks_kmh"].astype(float)
    sub["kategori_hujan"] = sub["curah_hujan_mm"].map(_kategori_hujan)

    return sub[
        [
            "cuaca_key",
            "tanggal",
            "kode_wmo",
            "deskripsi_cuaca",
            "suhu_rata2_c",
            "curah_hujan_mm",
            "kecepatan_angin_maks_kmh",
            "kategori_hujan",
        ]
    ].reset_index(drop=True)


def transform_data(df_pihps_raw: pd.DataFrame, df_cuaca_raw: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Menjalankan pembersihan data mentah dan menghasilkan tabel fakta & dimensi."""
    df_pihps = df_pihps_raw.copy()
    df_pihps["Tanggal"] = pd.to_datetime(
        df_pihps["Tanggal_teks"].astype(str).str.replace(" ", "", regex=False),
        format="%d/%m/%Y",
    )
    df_pihps["Harga_num"] = _parse_harga(df_pihps["Harga_Keriting_teks"])
    df_pihps["Harga_Agregat_num"] = _parse_harga(df_pihps["Harga_Agregat_teks"])

    # Tentukan periode irisan agar seluruh 4 pasar memiliki rentang tanggal yang konsisten
    wide = df_pihps.pivot(index="Tanggal", columns="Kategori_Pasar", values="Harga_num")[URUTAN_PASAR]
    awal = wide.notna().all(axis=1).idxmax()
    akhir = wide.notna().all(axis=1)[::-1].idxmax()

    df_periode = df_pihps.loc[(df_pihps["Tanggal"] >= awal) & (df_pihps["Tanggal"] <= akhir)].copy()
    df_periode = df_periode.sort_values(["Kategori_Pasar", "Tanggal"]).reset_index(drop=True)

    # Tandai dan imputasi missing hari libur/cuti bersama dengan forward-fill per pasar
    df_periode["is_imputasi"] = df_periode["Harga_num"].isna().astype(int)
    df_periode["Harga_num"] = df_periode.groupby("Kategori_Pasar")["Harga_num"].ffill()
    df_periode["Harga_Agregat_num"] = df_periode.groupby("Kategori_Pasar")["Harga_Agregat_num"].ffill()

    df_periode["harga_cabai_keriting"] = df_periode["Harga_num"].round().astype("int64")
    df_periode["harga_cabai_agregat"] = df_periode["Harga_Agregat_num"].round().astype("int64")

    # Koreksi kesalahan input (lonjakan 1 hari >40% lalu kembali ke level semula)
    for _, grp in df_periode.groupby("Kategori_Pasar"):
        s = grp["harga_cabai_keriting"].astype(float)
        prev_s, next_s = s.shift(1), s.shift(-1)
        spike_mask = (
            ((s / prev_s - 1).abs() > 0.4)
            & ((s / next_s - 1).abs() > 0.4)
            & ((next_s / prev_s - 1).abs() < 0.10)
        )
        for idx in grp.index[spike_mask]:
            df_periode.loc[idx, "harga_cabai_keriting"] = int(prev_s.loc[idx])
            df_periode.loc[idx, "is_imputasi"] = 1

    # Bersihkan data cuaca (hapus kolom rain_sum yang identik 100% dengan precipitation_sum)
    cuaca = df_cuaca_raw.drop(columns=["rain_sum (mm)"], errors="ignore").rename(
        columns={
            "time": "Tanggal",
            "weather_code (wmo code)": "Kode_Cuaca_WMO",
            "temperature_2m_mean (°C)": "Suhu_Rata2_C",
            "precipitation_sum (mm)": "Curah_Hujan_mm",
            "wind_speed_10m_max (km/h)": "Kecepatan_Angin_Maks_kmh",
        }
    )
    cuaca["Tanggal"] = pd.to_datetime(cuaca["Tanggal"])

    tanggal_unik = pd.DatetimeIndex(sorted(df_periode["Tanggal"].unique()))
    dim_tanggal = _build_dim_tanggal(tanggal_unik)
    dim_pasar = _build_dim_pasar()
    dim_cuaca = _build_dim_cuaca(cuaca, tanggal_unik)

    # Hitung metrik turunan pada tabel fakta
    pasar_map = dict(zip(dim_pasar["nama_pasar"], dim_pasar["pasar_key"]))
    df_periode["tanggal_key"] = df_periode["Tanggal"].dt.strftime("%Y%m%d").astype(int)
    df_periode["pasar_key"] = df_periode["Kategori_Pasar"].map(pasar_map).astype(int)
    df_periode["cuaca_key"] = df_periode["tanggal_key"]

    df_periode = df_periode.sort_values(["pasar_key", "Tanggal"]).reset_index(drop=True)
    prev_harga = df_periode.groupby("pasar_key")["harga_cabai_keriting"].shift(1)
    df_periode["perubahan_harian"] = (df_periode["harga_cabai_keriting"] - prev_harga).astype(float)
    df_periode["persen_perubahan"] = ((df_periode["perubahan_harian"] / prev_harga) * 100.0).round(4)

    harga_produsen = (
        df_periode.loc[df_periode["Kategori_Pasar"] == "Produsen", ["tanggal_key", "harga_cabai_keriting"]]
        .rename(columns={"harga_cabai_keriting": "_harga_produsen"})
    )
    df_periode = df_periode.merge(harga_produsen, on="tanggal_key", how="left")
    df_periode["markup_thd_produsen"] = (
        df_periode["harga_cabai_keriting"] - df_periode["_harga_produsen"]
    ).astype(float)

    fact_harga_harian = df_periode[
        [
            "tanggal_key",
            "pasar_key",
            "cuaca_key",
            "harga_cabai_keriting",
            "harga_cabai_agregat",
            "perubahan_harian",
            "persen_perubahan",
            "markup_thd_produsen",
            "is_imputasi",
        ]
    ].sort_values(["tanggal_key", "pasar_key"]).reset_index(drop=True)

    return {
        "dim_tanggal": dim_tanggal,
        "dim_pasar": dim_pasar,
        "dim_cuaca": dim_cuaca,
        "fact_harga_harian": fact_harga_harian,
    }
