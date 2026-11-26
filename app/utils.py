"""Utilitas koneksi data warehouse SQLite dan Filter Global untuk Dashboard Streamlit."""

from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "warehouse" / "cabai_medan.db"
FALLBACK_CSV_PATH = ROOT_DIR / "data" / "processed" / "01_clean.csv"

URUTAN_PASAR = ["Produsen", "Pedagang Besar", "Pasar Tradisional", "Pasar Modern"]

WARNA_PASAR = {
    "Produsen": "#2e7d32",
    "Pedagang Besar": "#f9a825",
    "Pasar Tradisional": "#c62828",
    "Pasar Modern": "#1565c0",
}


def format_rupiah(nilai: float | int) -> str:
    """Memformat angka menjadi string Rupiah dengan pemisah ribuan titik."""
    if pd.isna(nilai):
        return "-"
    return f"Rp{nilai:,.0f}".replace(",", ".")


@st.cache_data(ttl=3600)
def load_warehouse_data() -> tuple[pd.DataFrame, str]:
    """Memuat data terintegrasi dari SQLite warehouse/cabai_medan.db (atau fallback CSV)."""
    if DB_PATH.exists():
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query(
                "SELECT * FROM v_harga_lengkap ORDER BY tanggal, urutan_rantai",
                conn,
            )
        sumber = f"SQLite Warehouse (`{DB_PATH.name}` · view `v_harga_lengkap`)"
    elif FALLBACK_CSV_PATH.exists():
        raw = pd.read_csv(FALLBACK_CSV_PATH)
        df = raw.rename(
            columns={
                "Tanggal": "tanggal",
                "Kategori_Pasar": "kategori_pasar",
                "Komoditas": "komoditas",
                "Harga_Cabai_Merah_Keriting": "harga_cabai_keriting",
                "Harga_Cabai_Merah_Agregat": "harga_cabai_agregat",
                "Kode_Cuaca_WMO": "kode_wmo",
                "Suhu_Rata2_C": "suhu_rata2_c",
                "Curah_Hujan_mm": "curah_hujan_mm",
                "Kecepatan_Angin_Maks_kmh": "kecepatan_angin_maks_kmh",
                "Is_Imputasi": "is_imputasi",
            }
        )
        df["tahun"] = pd.to_datetime(df["tanggal"]).dt.year
        df["bulan"] = pd.to_datetime(df["tanggal"]).dt.month
        df["musim"] = df["bulan"].map(lambda m: "Hujan" if m in (10, 11, 12, 1, 2, 3) else "Kemarau")
        df["is_hari_libur"] = 0
        sumber = f"Fallback CSV (`{FALLBACK_CSV_PATH.name}`)"
    else:
        raise FileNotFoundError(
            "Sumber data tidak ditemukan. Jalankan `python3 etl/run_etl.py` terlebih dahulu."
        )

    df["tanggal"] = pd.to_datetime(df["tanggal"])
    df["kategori_pasar"] = pd.Categorical(
        df["kategori_pasar"], categories=URUTAN_PASAR, ordered=True
    )
    return df, sumber


def render_filter_global(df: pd.DataFrame) -> pd.DataFrame:
    """Menampilkan Filter Global di sidebar dan mengembalikan DataFrame terfilter."""
    st.sidebar.header("Filter Global")

    tgl_min = df["tanggal"].min().date()
    tgl_max = df["tanggal"].max().date()

    if "filter_rentang_tanggal" not in st.session_state:
        st.session_state["filter_rentang_tanggal"] = (tgl_min, tgl_max)
    if "filter_pasar" not in st.session_state:
        st.session_state["filter_pasar"] = URUTAN_PASAR.copy()
    if "filter_musim" not in st.session_state:
        st.session_state["filter_musim"] = ["Hujan", "Kemarau"]
    if "filter_libur" not in st.session_state:
        st.session_state["filter_libur"] = "Semua Hari"

    rentang_tgl = st.sidebar.date_input(
        "Rentang Tanggal",
        min_value=tgl_min,
        max_value=tgl_max,
        key="filter_rentang_tanggal",
    )

    if isinstance(rentang_tgl, tuple) and len(rentang_tgl) == 2:
        tgl_awal, tgl_akhir = rentang_tgl
    else:
        tgl_awal = tgl_akhir = rentang_tgl[0] if isinstance(rentang_tgl, tuple) else rentang_tgl

    pasar_pilihan = st.sidebar.multiselect(
        "Kategori Pasar",
        options=URUTAN_PASAR,
        key="filter_pasar",
    )

    musim_opsi = sorted(df["musim"].dropna().unique().tolist())
    musim_pilihan = st.sidebar.multiselect(
        "Musim",
        options=musim_opsi,
        key="filter_musim",
    )

    status_libur = st.sidebar.radio(
        "Filter Hari Libur Nasional",
        options=["Semua Hari", "Hari Kerja Non-Libur", "Hari Libur Nasional"],
        key="filter_libur",
    )

    if st.sidebar.button("Reset Filter Global", use_container_width=True):
        st.session_state["filter_rentang_tanggal"] = (tgl_min, tgl_max)
        st.session_state["filter_pasar"] = URUTAN_PASAR.copy()
        st.session_state["filter_musim"] = musim_opsi
        st.session_state["filter_libur"] = "Semua Hari"
        st.rerun()

    mask = (
        (df["tanggal"].dt.date >= tgl_awal)
        & (df["tanggal"].dt.date <= tgl_akhir)
        & (df["kategori_pasar"].isin(pasar_pilihan))
        & (df["musim"].isin(musim_pilihan))
    )

    if status_libur == "Hari Kerja Non-Libur":
        mask &= df["is_hari_libur"] == 0
    elif status_libur == "Hari Libur Nasional":
        mask &= df["is_hari_libur"] == 1

    df_filtered = df.loc[mask].copy()

    st.sidebar.divider()
    st.sidebar.caption(
        f"Data aktif: **{len(df_filtered):,}** dari **{len(df):,}** baris "
        f"({tgl_awal:%d-%m-%Y} s.d. {tgl_akhir:%d-%m-%Y})".replace(",", ".")
    )
    return df_filtered
