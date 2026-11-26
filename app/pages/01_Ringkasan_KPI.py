"""Halaman 1: Ringkasan KPI Berpembanding & Deret Waktu Beranotasi."""

from pathlib import Path
import sys

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import WARNA_PASAR, format_rupiah, load_warehouse_data, render_filter_global

st.set_page_config(
    page_title="Ringkasan KPI | Cabai Merah Keriting Medan",
    page_icon="📊",
    layout="wide",
)

df, _ = load_warehouse_data()
df_filtered = render_filter_global(df)

st.title("📊 Ringkasan KPI & Tren Harga Harian")
st.caption(
    "Pemantauan indikator kinerja utama (KPI) harga Cabai Merah Keriting Kota Medan "
    "dibandingkan periode sebelumnya serta deret waktu beranotasi."
)

if df_filtered.empty:
    st.warning("Tidak ada data untuk kombinasi Filter Global saat ini. Silakan sesuaikan filter di sidebar.")
    st.stop()

# Fokus utama KPI pada Pasar Tradisional; jika tidak dipilih, gunakan pasar pertama yang aktif
pasar_aktif = df_filtered["kategori_pasar"].cat.remove_unused_categories().unique().tolist()
pasar_kpi = "Pasar Tradisional" if "Pasar Tradisional" in pasar_aktif else pasar_aktif[0]
df_kpi = df_filtered[df_filtered["kategori_pasar"] == pasar_kpi].sort_values("tanggal").copy()

# Pembanding periode: paruh akhir vs paruh awal dalam rentang filter (minimal 2 hari)
titik_tengah = max(1, len(df_kpi) // 2)
paruh_awal = df_kpi.iloc[:titik_tengah]
paruh_akhir = df_kpi.iloc[titik_tengah:]

harga_terakhir = float(df_kpi["harga_cabai_keriting"].iloc[-1])
harga_sebelumnya = float(df_kpi["harga_cabai_keriting"].iloc[-2]) if len(df_kpi) >= 2 else harga_terakhir
delta_harian = harga_terakhir - harga_sebelumnya
delta_harian_pct = (delta_harian / harga_sebelumnya * 100.0) if harga_sebelumnya else 0.0

rata_periode = float(df_kpi["harga_cabai_keriting"].mean())
rata_paruh_awal = float(paruh_awal["harga_cabai_keriting"].mean())
rata_paruh_akhir = float(paruh_akhir["harga_cabai_keriting"].mean())
delta_rata = rata_paruh_akhir - rata_paruh_awal
delta_rata_pct = (delta_rata / rata_paruh_awal * 100.0) if rata_paruh_awal else 0.0

std_awal = float(paruh_awal["harga_cabai_keriting"].std()) if len(paruh_awal) > 1 else 0.0
std_akhir = float(paruh_akhir["harga_cabai_keriting"].std()) if len(paruh_akhir) > 1 else 0.0
cv_periode = (float(df_kpi["harga_cabai_keriting"].std()) / rata_periode * 100.0) if len(df_kpi) > 1 and rata_periode else 0.0
delta_std = std_akhir - std_awal

rata_markup = float(df_kpi["markup_thd_produsen"].mean()) if "markup_thd_produsen" in df_kpi.columns else 0.0
markup_awal = float(paruh_awal["markup_thd_produsen"].mean()) if "markup_thd_produsen" in paruh_awal.columns else 0.0
markup_akhir = float(paruh_akhir["markup_thd_produsen"].mean()) if "markup_thd_produsen" in paruh_akhir.columns else 0.0
delta_markup = markup_akhir - markup_awal

persen_asli = (1.0 - float(df_filtered["is_imputasi"].mean())) * 100.0
jumlah_imputasi = int(df_filtered["is_imputasi"].sum())

st.subheader(f"Indikator Utama — Fokus: {pasar_kpi}")
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.metric(
        label=f"Harga Terakhir ({df_kpi['tanggal'].iloc[-1]:%d %b %Y})",
        value=format_rupiah(harga_terakhir),
        delta=f"{delta_harian:+,.0f} ({delta_harian_pct:+.1f}%) vs hari sblm".replace(",", "."),
        delta_color="inverse",
    )
with k2:
    st.metric(
        label="Rata-rata Periode Terpilih",
        value=format_rupiah(rata_periode),
        delta=f"{delta_rata:+,.0f} ({delta_rata_pct:+.1f}%) paruh akhir vs awal".replace(",", "."),
        delta_color="inverse",
    )
with k3:
    st.metric(
        label="Volatilitas (Std. Dev / CV)",
        value=f"{format_rupiah(df_kpi['harga_cabai_keriting'].std() if len(df_kpi) > 1 else 0)} ({cv_periode:.1f}%)",
        delta=f"{delta_std:+,.0f} paruh akhir vs awal".replace(",", "."),
        delta_color="inverse",
    )
with k4:
    st.metric(
        label=f"Rata-rata Markup vs Produsen",
        value=format_rupiah(rata_markup),
        delta=f"{delta_markup:+,.0f} paruh akhir vs awal".replace(",", "."),
        delta_color="inverse",
    )
with k5:
    st.metric(
        label="Kelengkapan Data Asli PIHPS",
        value=f"{persen_asli:.1f}%",
        delta=f"{jumlah_imputasi:,} baris imputasi libur".replace(",", "."),
        delta_color="off",
    )

st.divider()
st.subheader("Deret Waktu Harga Harian Beranotasi")

opsi_col1, opsi_col2, opsi_col3 = st.columns(3)
with opsi_col1:
    tampil_ma30 = st.checkbox("Tampilkan Moving Average 30 Hari (MA-30)", value=True)
with opsi_col2:
    tampil_rata_hist = st.checkbox(f"Tampilkan Garis Rata-rata {pasar_kpi}", value=True)
with opsi_col3:
    tampil_anotasi = st.checkbox("Tampilkan Anotasi Puncak & Lembah Harga", value=True)

fig = go.Figure()

for pasar in pasar_aktif:
    sub = df_filtered[df_filtered["kategori_pasar"] == pasar].sort_values("tanggal")
    lebar_garis = 2.6 if pasar == "Pasar Tradisional" else 1.7
    fig.add_trace(
        go.Scatter(
            x=sub["tanggal"],
            y=sub["harga_cabai_keriting"],
            mode="lines",
            name=str(pasar),
            line=dict(color=WARNA_PASAR.get(str(pasar), "#555555"), width=lebar_garis),
            hovertemplate=(
                f"<b>{pasar}</b><br>"
                "Tanggal: %{x|%d %b %Y}<br>"
                "Harga: Rp%{y:,.0f}/kg<extra></extra>"
            ),
        )
    )

    if tampil_ma30 and pasar == pasar_kpi and len(sub) >= 7:
        ma30 = sub["harga_cabai_keriting"].rolling(window=30, min_periods=5).mean()
        fig.add_trace(
            go.Scatter(
                x=sub["tanggal"],
                y=ma30,
                mode="lines",
                name=f"MA-30 ({pasar})",
                line=dict(color="#212121", width=2, dash="dash"),
                hovertemplate="<b>MA-30</b><br>Tanggal: %{x|%d %b %Y}<br>Rp%{y:,.0f}/kg<extra></extra>",
            )
        )

if tampil_rata_hist:
    fig.add_hline(
        y=rata_periode,
        line_dash="dot",
        line_color="#616161",
        annotation_text=f"Rata-rata {pasar_kpi}: {format_rupiah(rata_periode)}",
        annotation_position="top left",
    )

if tampil_anotasi and not df_kpi.empty:
    idx_max = df_kpi["harga_cabai_keriting"].idxmax()
    idx_min = df_kpi["harga_cabai_keriting"].idxmin()
    row_max = df_kpi.loc[idx_max]
    row_min = df_kpi.loc[idx_min]

    fig.add_annotation(
        x=row_max["tanggal"],
        y=row_max["harga_cabai_keriting"],
        text=f"Puncak: {format_rupiah(row_max['harga_cabai_keriting'])}<br>({row_max['tanggal']:%d %b %Y})",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#b71c1c",
        bgcolor="#ffebee",
        bordercolor="#b71c1c",
        font=dict(size=11, color="#b71c1c"),
        ay=-40,
    )
    fig.add_annotation(
        x=row_min["tanggal"],
        y=row_min["harga_cabai_keriting"],
        text=f"Terendah: {format_rupiah(row_min['harga_cabai_keriting'])}<br>({row_min['tanggal']:%d %b %Y})",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#1b5e20",
        bgcolor="#e8f5e9",
        bordercolor="#1b5e20",
        font=dict(size=11, color="#1b5e20"),
        ay=40,
    )

fig.update_layout(
    height=500,
    hovermode="x unified",
    xaxis_title="Tanggal",
    yaxis_title="Harga Cabai Merah Keriting (Rp/kg)",
    yaxis_tickformat=",.0f",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=20, r=20, t=50, b=20),
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Perbandingan Ringkas Antar Pasar")
perbandingan = (
    df_filtered.groupby("kategori_pasar", observed=True)
    .agg(
        Rata_Harga=("harga_cabai_keriting", "mean"),
        Harga_Min=("harga_cabai_keriting", "min"),
        Harga_Maks=("harga_cabai_keriting", "max"),
        Rata_Markup=("markup_thd_produsen", "mean") if "markup_thd_produsen" in df_filtered.columns else ("harga_cabai_keriting", "count"),
        Hari_Imputasi=("is_imputasi", "sum"),
    )
    .reset_index()
)
perbandingan.columns = [
    "Kategori Pasar",
    "Rata-rata Harga",
    "Harga Minimum",
    "Harga Maksimum",
    "Rata-rata Markup vs Produsen",
    "Jumlah Hari Imputasi",
]
for kol in ["Rata-rata Harga", "Harga Minimum", "Harga Maksimum", "Rata-rata Markup vs Produsen"]:
    perbandingan[kol] = perbandingan[kol].map(format_rupiah)

st.dataframe(perbandingan, use_container_width=True, hide_index=True)
