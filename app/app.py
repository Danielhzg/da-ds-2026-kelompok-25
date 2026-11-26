"""Halaman utama Dashboard Analitik & Prediksi Harga Cabai Merah Keriting Kota Medan."""

from pathlib import Path
import sys

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import streamlit as st
from utils import format_rupiah, load_warehouse_data, render_filter_global

st.set_page_config(
    page_title="Dashboard Cabai Merah Keriting Medan",
    page_icon="🌶️",
    layout="wide",
    initial_sidebar_state="expanded",
)

df, sumber_data = load_warehouse_data()
df_filtered = render_filter_global(df)

st.title("🌶️ Dashboard Analitik & Prediksi Harga Cabai Merah Keriting Kota Medan")
st.markdown(
    "Sistem pendukung keputusan berbasis *Data Warehouse* SQLite dan *Machine Learning* "
    "untuk memantau dinamika harga Cabai Merah Keriting di 4 tingkat rantai pasok Kota Medan "
    "(**Produsen**, **Pedagang Besar**, **Pasar Tradisional**, dan **Pasar Modern**) serta keterkaitannya dengan cuaca."
)

col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.info(f"**Sumber Data**\n\n{sumber_data}")
with col_info2:
    tgl_mulai = df["tanggal"].min().strftime("%d %b %Y")
    tgl_selesai = df["tanggal"].max().strftime("%d %b %Y")
    st.info(f"**Cakupan Periode**\n\n{tgl_mulai} s.d. {tgl_selesai} ({df['tanggal'].nunique():,} hari kerja)".replace(",", "."))
with col_info3:
    st.info("**Tim Pengembang**\n\nKelompok 25 — Dame Sisri Rumapea (DALIS/DASI) & Daniel Haganta Ginting (DASI/PM)")

st.divider()
st.subheader("Navigasi Halaman Dashboard")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("**1. Ringkasan KPI**\n\nKartu KPI berpembanding dan deret waktu beranotasi per tingkat pasar.")
with c2:
    st.markdown("**2. Analisis Mendalam**\n\nEksplorasi visualisasi lanjutan (heatmap, violin, treemap, scatter, dll.).")
with c3:
    st.markdown("**3. Storytelling**\n\nTemuan utama menjawab pertanyaan analitik & rekomendasi TPID/pedagang/konsumen.")
with c4:
    st.markdown("**4. Prediksi Harga**\n\nSimulasi prediksi harga cabai harian dengan model ML terbaik.")

st.divider()
st.subheader("Ringkasan Harga per Kategori Pasar (Sesuai Filter Global)")

if df_filtered.empty:
    st.warning("Tidak ada data yang cocok dengan kombinasi Filter Global saat ini. Silakan ubah filter di sidebar.")
else:
    ringkas = (
        df_filtered.groupby("kategori_pasar", observed=True)["harga_cabai_keriting"]
        .agg(
            Jumlah_Hari="count",
            Rata_Rata="mean",
            Median="median",
            Minimum="min",
            Maksimum="max",
            Std_Dev="std",
        )
        .reset_index()
    )
    ringkas_tampil = ringkas.copy()
    ringkas_tampil.columns = [
        "Kategori Pasar",
        "Jumlah Hari",
        "Rata-rata (Rp/kg)",
        "Median (Rp/kg)",
        "Minimum (Rp/kg)",
        "Maksimum (Rp/kg)",
        "Std. Deviasi (Rp/kg)",
    ]
    for kolom in ["Rata-rata (Rp/kg)", "Median (Rp/kg)", "Minimum (Rp/kg)", "Maksimum (Rp/kg)", "Std. Deviasi (Rp/kg)"]:
        ringkas_tampil[kolom] = ringkas_tampil[kolom].map(format_rupiah)

    st.dataframe(ringkas_tampil, use_container_width=True, hide_index=True)
