"""Halaman 2: Analisis Mendalam dengan Visualisasi Lanjutan, Cross-Filter, & Drill-Down."""

from pathlib import Path
import sys

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import URUTAN_PASAR, WARNA_PASAR, format_rupiah, load_warehouse_data, render_filter_global

st.set_page_config(
    page_title="Analisis Mendalam | Cabai Merah Keriting Medan",
    page_icon="🔬",
    layout="wide",
)

df, _ = load_warehouse_data()
df_filtered = render_filter_global(df)

st.title("🔬 Analisis Mendalam Dinamika Harga, Rantai Pasok, & Cuaca")
st.caption(
    "Eksplorasi multi-dimensi harga Cabai Merah Keriting Kota Medan melalui 7 visualisasi interaktif Plotly, "
    "panel Cross-Filter lintas grafik, serta Drill-Down 3 tingkat (Tahun → Kuartal → Bulan/Harian)."
)

if df_filtered.empty:
    st.warning("Tidak ada data untuk kombinasi Filter Global saat ini. Silakan ubah filter di sidebar.")
    st.stop()

# -----------------------------------------------------------------------------
# Panel Cross-Filter Interaktif Lintas Grafik
# -----------------------------------------------------------------------------
URUTAN_HUJAN = ["Tidak Hujan", "Hujan Ringan", "Hujan Sedang", "Hujan Lebat"]
pasar_tersedia = [p for p in URUTAN_PASAR if p in df_filtered["kategori_pasar"].astype(str).unique()]
opsi_musim_cf = ["Semua Musim"] + sorted(df_filtered["musim"].dropna().astype(str).unique().tolist())
opsi_hujan_tersedia = (
    [h for h in URUTAN_HUJAN if h in df_filtered["kategori_hujan"].dropna().astype(str).unique()]
    if "kategori_hujan" in df_filtered.columns
    else []
)

with st.expander("🎛️ Panel Cross-Filter & Pengaturan Eksplorasi", expanded=True):
    cf1, cf2, cf3, cf4 = st.columns([1.1, 1.0, 1.4, 1.0])
    with cf1:
        pasar_fokus = st.selectbox(
            "Pasar Fokus (Heatmap & Drill-Down)",
            options=pasar_tersedia,
            index=pasar_tersedia.index("Pasar Tradisional") if "Pasar Tradisional" in pasar_tersedia else 0,
        )
    with cf2:
        musim_cf = st.selectbox("Cross-Filter Musim", options=opsi_musim_cf)
    with cf3:
        hujan_cf = st.multiselect(
            "Cross-Filter Kategori Hujan",
            options=opsi_hujan_tersedia,
            default=opsi_hujan_tersedia,
        )
    with cf4:
        jenis_hierarki = st.radio(
            "Visual Hierarki Cuaca × Pasar",
            options=["Treemap", "Sunburst"],
            horizontal=True,
        )

df_cf = df_filtered.copy()
if musim_cf != "Semua Musim":
    df_cf = df_cf[df_cf["musim"].astype(str) == musim_cf]
if opsi_hujan_tersedia and "kategori_hujan" in df_cf.columns:
    if not hujan_cf:
        st.warning("Pilih minimal satu Kategori Hujan pada panel Cross-Filter.")
        st.stop()
    df_cf = df_cf[df_cf["kategori_hujan"].astype(str).isin(hujan_cf)]

if df_cf.empty:
    st.warning("Tidak ada observasi yang memenuhi kombinasi Filter Global & Cross-Filter saat ini.")
    st.stop()

st.caption(
    f"Cakupan Cross-Filter aktif: **{len(df_cf):,}** baris observasi | "
    f"Fokus Heatmap/Drill-Down: **{pasar_fokus}** | Musim: **{musim_cf}**".replace(",", ".")
)

# -----------------------------------------------------------------------------
# 1. Heatmap Kalender Tahun x Bulan
# -----------------------------------------------------------------------------
st.subheader(f"1. Heatmap Kalender Harga Bulanan — {pasar_fokus}")
metrik_heat = st.radio(
    "Agregasi Nilai Heatmap",
    options=["Rata-rata", "Median"],
    horizontal=True,
    key="heat_agg",
)

df_heat = df_cf[df_cf["kategori_pasar"].astype(str) == pasar_fokus].copy()
if not df_heat.empty:
    df_heat["bulan_num"] = df_heat["tanggal"].dt.month
    df_heat["tahun_num"] = df_heat["tanggal"].dt.year
    nama_bulan_singkat = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun",
        7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des",
    }
    agg_fn = "mean" if metrik_heat == "Rata-rata" else "median"
    piv_heat = (
        df_heat.pivot_table(
            index="tahun_num",
            columns="bulan_num",
            values="harga_cabai_keriting",
            aggfunc=agg_fn,
        )
        .reindex(columns=range(1, 13))
    )
    piv_heat.columns = [nama_bulan_singkat[m] for m in piv_heat.columns]

    fig_heat = px.imshow(
        piv_heat,
        text_auto=",.0f",
        aspect="auto",
        color_continuous_scale="YlOrRd",
        labels=dict(x="Bulan", y="Tahun", color=f"{metrik_heat} Harga (Rp/kg)"),
        title=f"Peta Panas {metrik_heat} Harga {pasar_fokus} per Tahun × Bulan",
    )
    fig_heat.update_layout(height=390, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_heat, use_container_width=True)
else:
    st.info(f"Tidak ada data untuk {pasar_fokus} pada kombinasi Cross-Filter saat ini.")

# -----------------------------------------------------------------------------
# 2. Violin + Box Plot & 3. Treemap / Sunburst Hierarki
# -----------------------------------------------------------------------------
col_v, col_h = st.columns(2)

with col_v:
    st.subheader("2. Violin & Box Plot Sebaran Harga per Pasar")
    df_violin = df_cf.assign(kategori_pasar=df_cf["kategori_pasar"].astype(str))
    fig_violin = px.violin(
        df_violin,
        x="kategori_pasar",
        y="harga_cabai_keriting",
        color="kategori_pasar",
        box=True,
        points="outliers",
        color_discrete_map=WARNA_PASAR,
        category_orders={"kategori_pasar": URUTAN_PASAR},
        labels={
            "kategori_pasar": "Kategori Pasar",
            "harga_cabai_keriting": "Harga Cabai Merah Keriting (Rp/kg)",
        },
        title="Distribusi, Median, IQR, & Outlier Lintas 4 Tingkat Pasar",
    )
    fig_violin.update_layout(
        showlegend=False,
        height=450,
        yaxis_tickformat=",.0f",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    st.plotly_chart(fig_violin, use_container_width=True)

with col_h:
    st.subheader("3. Hierarki Musim → Kategori Hujan → Pasar")
    if "kategori_hujan" in df_cf.columns:
        agg_hier = (
            df_cf.groupby(["musim", "kategori_hujan", "kategori_pasar"], observed=True)
            .agg(
                jumlah_hari=("harga_cabai_keriting", "count"),
                rata_harga=("harga_cabai_keriting", "mean"),
            )
            .reset_index()
        )
        for kol_str in ["musim", "kategori_hujan", "kategori_pasar"]:
            agg_hier[kol_str] = agg_hier[kol_str].astype(str)
        agg_hier = agg_hier[agg_hier["jumlah_hari"] > 0]

        if not agg_hier.empty:
            if jenis_hierarki == "Treemap":
                fig_hier = px.treemap(
                    agg_hier,
                    path=["musim", "kategori_hujan", "kategori_pasar"],
                    values="jumlah_hari",
                    color="rata_harga",
                    color_continuous_scale="RdYlGn_r",
                    labels={"rata_harga": "Rata-rata Harga (Rp/kg)", "jumlah_hari": "Jumlah Observasi"},
                    title="Treemap Proporsi Observasi & Rata-rata Harga (Musim × Hujan × Pasar)",
                )
            else:
                fig_hier = px.sunburst(
                    agg_hier,
                    path=["musim", "kategori_hujan", "kategori_pasar"],
                    values="jumlah_hari",
                    color="rata_harga",
                    color_continuous_scale="RdYlGn_r",
                    labels={"rata_harga": "Rata-rata Harga (Rp/kg)", "jumlah_hari": "Jumlah Observasi"},
                    title="Sunburst Proporsi Observasi & Rata-rata Harga (Musim × Hujan × Pasar)",
                )
            fig_hier.update_layout(height=450, margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig_hier, use_container_width=True)
        else:
            st.info("Data hierarki kosong untuk filter saat ini.")

# -----------------------------------------------------------------------------
# 4. Small Multiples (Faceted Chart): Kategori Hujan vs Harga per Pasar
# -----------------------------------------------------------------------------
st.subheader("4. Small Multiples: Sensitivitas Harga terhadap Intensitas Hujan per Pasar")
if "kategori_hujan" in df_cf.columns:
    df_facet = df_cf.assign(
        kategori_pasar=df_cf["kategori_pasar"].astype(str),
        kategori_hujan=df_cf["kategori_hujan"].astype(str),
    )
    fig_facet = px.box(
        df_facet,
        x="kategori_hujan",
        y="harga_cabai_keriting",
        color="kategori_pasar",
        facet_col="kategori_pasar",
        facet_col_wrap=2,
        color_discrete_map=WARNA_PASAR,
        category_orders={
            "kategori_pasar": URUTAN_PASAR,
            "kategori_hujan": URUTAN_HUJAN,
        },
        labels={
            "kategori_hujan": "Kategori Hujan Harian",
            "harga_cabai_keriting": "Harga (Rp/kg)",
            "kategori_pasar": "Pasar",
        },
        title="Perbandingan Distribusi Harga menurut Kategori Hujan di Setiap Tingkat Pasar",
    )
    fig_facet.update_layout(
        showlegend=False,
        height=520,
        yaxis_tickformat=",.0f",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(fig_facet, use_container_width=True)

# -----------------------------------------------------------------------------
# 5. Bubble Chart Transmisi Harga & 6. Tren Markup + Rolling Volatility
# -----------------------------------------------------------------------------
col_b, col_m = st.columns(2)

with col_b:
    st.subheader("5. Bubble Chart Transmisi Harga (Grosir vs Eceran)")
    piv_trans = (
        df_cf.assign(kategori_pasar=df_cf["kategori_pasar"].astype(str))
        .pivot_table(
            index=["tanggal", "musim", "curah_hujan_mm"],
            columns="kategori_pasar",
            values="harga_cabai_keriting",
            aggfunc="mean",
        )
        .reset_index()
    )

    if {"Pedagang Besar", "Pasar Tradisional"}.issubset(piv_trans.columns):
        df_bubble = piv_trans.dropna(subset=["Pedagang Besar", "Pasar Tradisional"]).copy()
        if not df_bubble.empty:
            df_bubble["musim"] = df_bubble["musim"].astype(str)
            df_bubble["selisih_pb_trad"] = df_bubble["Pasar Tradisional"] - df_bubble["Pedagang Besar"]
            df_bubble["ukuran_hujan"] = df_bubble["curah_hujan_mm"].clip(lower=0.0) + 2.0

            fig_bubble = px.scatter(
                df_bubble,
                x="Pedagang Besar",
                y="Pasar Tradisional",
                color="musim",
                size="ukuran_hujan",
                hover_data={
                    "tanggal": "|%d %b %Y",
                    "curah_hujan_mm": ":.1f",
                    "selisih_pb_trad": ":,.0f",
                    "ukuran_hujan": False,
                },
                opacity=0.68,
                color_discrete_map={"Hujan": "#1565c0", "Kemarau": "#ef6c00"},
                labels={
                    "Pedagang Besar": "Harga Pedagang Besar (Rp/kg)",
                    "Pasar Tradisional": "Harga Pasar Tradisional (Rp/kg)",
                    "musim": "Musim",
                    "curah_hujan_mm": "Curah Hujan (mm)",
                    "selisih_pb_trad": "Margin PB→Trad (Rp/kg)",
                },
                title="Transmisi Harga Pedagang Besar → Pasar Tradisional (Ukuran = Curah Hujan)",
            )
            batas_maks = float(max(df_bubble["Pedagang Besar"].max(), df_bubble["Pasar Tradisional"].max()))
            fig_bubble.add_trace(
                go.Scatter(
                    x=[0, batas_maks],
                    y=[0, batas_maks],
                    mode="lines",
                    name="Garis Paritas (1:1)",
                    line=dict(color="#616161", dash="dash", width=1.5),
                )
            )
            fig_bubble.update_layout(
                height=460,
                xaxis_tickformat=",.0f",
                yaxis_tickformat=",.0f",
                margin=dict(l=20, r=20, t=50, b=20),
            )
            st.plotly_chart(fig_bubble, use_container_width=True)
        else:
            st.info("Tidak ada tanggal berpasangan untuk Pedagang Besar & Pasar Tradisional pada filter ini.")
    else:
        st.info(
            "Aktifkan kategori pasar **Pedagang Besar** dan **Pasar Tradisional** di Filter Global "
            "untuk melihat Bubble Chart transmisi harga hulu–hilir."
        )

with col_m:
    st.subheader("6. Tren Markup & Volatilitas Bergulir 30 Hari")
    tab_mk, tab_vol = st.tabs(["📈 Tren Markup vs Produsen", "🌊 Rolling Volatility 30 Hari"])

    with tab_mk:
        if "markup_thd_produsen" in df_cf.columns:
            df_markup = df_cf[df_cf["kategori_pasar"].astype(str) != "Produsen"].copy()
            df_markup["kategori_pasar"] = df_markup["kategori_pasar"].astype(str)
            if not df_markup.empty:
                fig_mk = px.line(
                    df_markup.sort_values("tanggal"),
                    x="tanggal",
                    y="markup_thd_produsen",
                    color="kategori_pasar",
                    color_discrete_map=WARNA_PASAR,
                    labels={
                        "tanggal": "Tanggal",
                        "markup_thd_produsen": "Markup vs Produsen (Rp/kg)",
                        "kategori_pasar": "Pasar",
                    },
                    title="Dinamika Margin Harga terhadap Tingkat Produsen",
                )
                fig_mk.update_layout(
                    height=405,
                    yaxis_tickformat=",.0f",
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(l=20, r=20, t=50, b=20),
                )
                st.plotly_chart(fig_mk, use_container_width=True)
            else:
                st.info("Pilih selain Produsen pada Filter Global untuk menampilkan grafik markup.")

    with tab_vol:
        df_roll = df_cf.sort_values(["kategori_pasar", "tanggal"]).copy()
        df_roll["kategori_pasar"] = df_roll["kategori_pasar"].astype(str)
        df_roll["vol_30h"] = (
            df_roll.groupby("kategori_pasar")["harga_cabai_keriting"]
            .transform(lambda s: s.rolling(30, min_periods=5).std())
        )
        df_roll_valid = df_roll.dropna(subset=["vol_30h"])
        if not df_roll_valid.empty:
            fig_vol = px.line(
                df_roll_valid,
                x="tanggal",
                y="vol_30h",
                color="kategori_pasar",
                color_discrete_map=WARNA_PASAR,
                labels={
                    "tanggal": "Tanggal",
                    "vol_30h": "Std. Deviasi Bergulir 30 Hari (Rp/kg)",
                    "kategori_pasar": "Pasar",
                },
                title="Volatilitas Bergulir 30 Hari — Deteksi Episode Gejolak Ekstrem",
            )
            fig_vol.update_layout(
                height=405,
                yaxis_tickformat=",.0f",
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=20, r=20, t=50, b=20),
            )
            st.plotly_chart(fig_vol, use_container_width=True)
        else:
            st.info("Rentang data terlalu pendek (< 5 hari) untuk menghitung volatilitas bergulir 30 hari.")

# -----------------------------------------------------------------------------
# 7. Fitur Interaktif Drill-Down 3 Level: Tahun -> Kuartal -> Bulan / Harian
# -----------------------------------------------------------------------------
st.divider()
st.subheader(f"7. Drill-Down Interaktif (Tahun → Kuartal → Bulan & Harian) — {pasar_fokus}")

df_dd_base = df_cf[df_cf["kategori_pasar"].astype(str) == pasar_fokus].sort_values("tanggal").copy()
if not df_dd_base.empty:
    df_dd_base["tahun_dd"] = df_dd_base["tanggal"].dt.year
    df_dd_base["kuartal_dd"] = "Q" + df_dd_base["tanggal"].dt.quarter.astype(str)
    df_dd_base["bulan_dd"] = df_dd_base["tanggal"].dt.strftime("%Y-%m (%b)")

    d1, d2, d3 = st.columns(3)
    tahun_opsi = sorted(df_dd_base["tahun_dd"].unique().tolist(), reverse=True)
    with d1:
        tahun_pilih = st.selectbox("Level 1 — Pilih Tahun", options=tahun_opsi)
    df_dd_tahun = df_dd_base[df_dd_base["tahun_dd"] == tahun_pilih]

    kuartal_opsi = ["Semua Kuartal"] + sorted(df_dd_tahun["kuartal_dd"].unique().tolist())
    with d2:
        kuartal_pilih = st.selectbox("Level 2 — Pilih Kuartal", options=kuartal_opsi)
    df_dd_kuartal = (
        df_dd_tahun if kuartal_pilih == "Semua Kuartal"
        else df_dd_tahun[df_dd_tahun["kuartal_dd"] == kuartal_pilih]
    )

    bulan_opsi = ["Semua Bulan"] + df_dd_kuartal["bulan_dd"].drop_duplicates().tolist()
    with d3:
        bulan_pilih = st.selectbox("Level 3 — Pilih Bulan", options=bulan_opsi)

    df_dd_detail = (
        df_dd_kuartal if bulan_pilih == "Semua Bulan"
        else df_dd_kuartal[df_dd_kuartal["bulan_dd"] == bulan_pilih]
    )

    if bulan_pilih == "Semua Bulan":
        ringkas_dd = (
            df_dd_detail.groupby("bulan_dd", sort=False)
            .agg(
                Rata_Harga=("harga_cabai_keriting", "mean"),
                Harga_Maks=("harga_cabai_keriting", "max"),
                Harga_Min=("harga_cabai_keriting", "min"),
                Total_Hujan_mm=("curah_hujan_mm", "sum"),
            )
            .reset_index()
        )
        fig_dd = go.Figure()
        fig_dd.add_trace(
            go.Bar(
                x=ringkas_dd["bulan_dd"],
                y=ringkas_dd["Rata_Harga"],
                name="Rata-rata Harga Bulanan",
                marker_color=WARNA_PASAR.get(pasar_fokus, "#c62828"),
                hovertemplate="<b>%{x}</b><br>Rata-rata: Rp%{y:,.0f}/kg<extra></extra>",
            )
        )
        fig_dd.add_trace(
            go.Scatter(
                x=ringkas_dd["bulan_dd"],
                y=ringkas_dd["Harga_Maks"],
                mode="lines+markers",
                name="Harga Maksimum",
                line=dict(color="#212121", width=2, dash="dot"),
            )
        )
        fig_dd.update_layout(
            title=f"Drill-Down Bulanan {pasar_fokus} — {tahun_pilih} ({kuartal_pilih})",
            xaxis_title="Bulan",
            yaxis_title="Harga (Rp/kg)",
            yaxis_tickformat=",.0f",
            height=360,
            margin=dict(l=20, r=20, t=50, b=20),
        )
    else:
        fig_dd = px.line(
            df_dd_detail,
            x="tanggal",
            y="harga_cabai_keriting",
            markers=True,
            color_discrete_sequence=[WARNA_PASAR.get(pasar_fokus, "#c62828")],
            labels={"tanggal": "Tanggal", "harga_cabai_keriting": "Harga Harian (Rp/kg)"},
            title=f"Drill-Down Harian {pasar_fokus} — {bulan_pilih}",
        )
        fig_dd.update_layout(height=360, yaxis_tickformat=",.0f", margin=dict(l=20, r=20, t=50, b=20))

    st.plotly_chart(fig_dd, use_container_width=True)

    with st.expander("Lihat Tabel Rincian Harian (Level 3 Drill-Down)"):
        kolom_tampil = [
            k for k in [
                "tanggal",
                "harga_cabai_keriting",
                "perubahan_harian",
                "markup_thd_produsen",
                "curah_hujan_mm",
                "suhu_rata2_c",
                "deskripsi_cuaca",
                "is_imputasi",
            ] if k in df_dd_detail.columns
        ]
        tampil_dd = df_dd_detail[kolom_tampil].copy()
        tampil_dd["tanggal"] = tampil_dd["tanggal"].dt.strftime("%Y-%m-%d")
        label_kolom = {
            "tanggal": "Tanggal",
            "harga_cabai_keriting": "Harga (Rp/kg)",
            "perubahan_harian": "Perubahan Harian",
            "markup_thd_produsen": "Markup vs Produsen",
            "curah_hujan_mm": "Curah Hujan (mm)",
            "suhu_rata2_c": "Suhu (°C)",
            "deskripsi_cuaca": "Cuaca",
            "is_imputasi": "Imputasi",
        }
        tampil_dd = tampil_dd.rename(columns=label_kolom)
        st.dataframe(tampil_dd, use_container_width=True, hide_index=True)
