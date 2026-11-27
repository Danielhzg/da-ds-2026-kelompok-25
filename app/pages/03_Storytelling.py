"""Halaman 3: Data Storytelling, Temuan Model Prediksi, & Rekomendasi Kebijakan."""

import json
from pathlib import Path
import sys

APP_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import URUTAN_PASAR, WARNA_PASAR, format_rupiah, load_warehouse_data, render_filter_global

st.set_page_config(
    page_title="Storytelling & Rekomendasi | Cabai Merah Keriting Medan",
    page_icon="📖",
    layout="wide",
)

METRICS_PATH = ROOT_DIR / "models" / "metrics.json"


@st.cache_data(ttl=3600)
def load_metrics() -> dict:
    """Membaca ringkasan metrik dan feature importance dari models/metrics.json."""
    if not METRICS_PATH.exists():
        return {}
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))


df, _ = load_warehouse_data()
df_filtered = render_filter_global(df)
metrics = load_metrics()

st.title("📖 Data Storytelling & Rekomendasi Pendukung Keputusan")
st.markdown(
    "Sintesis temuan dari **6.352 observasi harga 4 tingkat pasar & cuaca Kota Medan (2019–2026)** "
    "untuk menjawab 3 pertanyaan analitik proposal serta merumuskan aksi konkret bagi pemangku kepentingan."
)

if df_filtered.empty:
    st.warning("Tidak ada data untuk kombinasi Filter Global saat ini. Silakan ubah filter di sidebar.")
    st.stop()

# -----------------------------------------------------------------------------
# Pertanyaan 1: Tren & Volatilitas Lintas 4 Level Pasar
# -----------------------------------------------------------------------------
st.header("1. Tren & Volatilitas Harga Lintas 4 Level Pasar")
st.info(
    "**Temuan Utama:** Median harga naik bertingkat dari hulu ke hilir: "
    "**Produsen Rp22.000/kg → Pedagang Besar Rp28.000/kg → Pasar Tradisional Rp33.700/kg → Pasar Modern Rp45.950/kg** "
    "(uji ANOVA $F = 662{,}2$). **Pasar Tradisional** paling responsif terhadap gejolak pasokan karena berubah pada "
    "**57,3% hari kerja** (553 hari mengalami perubahan harian >5%), jauh di atas Pedagang Besar (**17,8%**), "
    "Pasar Modern (**13,0%**), dan Produsen (**4,6%**, yang 70 dari 73 perubahannya terjadi pada tanggal 25–27 tiap bulan)."
)

vol_stats = (
    df_filtered.sort_values(["kategori_pasar", "tanggal"])
    .groupby("kategori_pasar", observed=True)
    .agg(
        Median_Harga=("harga_cabai_keriting", "median"),
        Mean_Harga=("harga_cabai_keriting", "mean"),
        Hari_Berubah_Pct=(
            "perubahan_harian",
            lambda s: float((s.dropna() != 0).mean() * 100.0) if len(s.dropna()) else 0.0,
        ),
    )
    .reset_index()
)
vol_stats["kategori_pasar"] = vol_stats["kategori_pasar"].astype(str)

c_q1a, c_q1b = st.columns(2)
with c_q1a:
    fig_q1_med = px.bar(
        vol_stats,
        x="kategori_pasar",
        y="Median_Harga",
        color="kategori_pasar",
        text_auto=",.0f",
        color_discrete_map=WARNA_PASAR,
        category_orders={"kategori_pasar": URUTAN_PASAR},
        labels={"kategori_pasar": "Tingkat Pasar", "Median_Harga": "Median Harga (Rp/kg)"},
        title="Median Harga Naik Bertingkat 2,09× dari Produsen ke Pasar Modern",
    )
    fig_q1_med.update_layout(showlegend=False, height=380, yaxis_tickformat=",.0f")
    st.plotly_chart(fig_q1_med, use_container_width=True)

with c_q1b:
    fig_q1_freq = px.bar(
        vol_stats,
        x="kategori_pasar",
        y="Hari_Berubah_Pct",
        color="kategori_pasar",
        text_auto=".1f",
        color_discrete_map=WARNA_PASAR,
        category_orders={"kategori_pasar": URUTAN_PASAR},
        labels={"kategori_pasar": "Tingkat Pasar", "Hari_Berubah_Pct": "Hari Kerja Harga Berubah (%)"},
        title="Pasar Tradisional Berubah pada 57,3% Hari Kerja — Paling Volatil",
    )
    fig_q1_freq.update_layout(showlegend=False, height=380, yaxis_range=[0, 100])
    st.plotly_chart(fig_q1_freq, use_container_width=True)

# -----------------------------------------------------------------------------
# Pertanyaan 2: Pola Musiman, Musim Hujan, dan Hari Besar
# -----------------------------------------------------------------------------
st.divider()
st.header("2. Pola Musiman, Curah Hujan, & Dinamika Hari Besar")
st.info(
    "**Temuan Utama:** Terdapat pola musiman yang nyata: **Juni** mencatat median harga terendah (**Rp22.900/kg**), "
    "sedangkan **Februari** tertinggi (**Rp39.600/kg**, Kruskal-Wallis $p = 1{,}83 \\times 10^{-23}$). "
    "Pada puncak musim hujan **September–Desember**, proporsi hari mahal mencapai **32,4%** dibanding **20,8%** di bulan lain "
    "($\\chi^2$ $p = 6{,}84 \\times 10^{-24}$). Lonjakan historis bulanan tertinggi terjadi pada **Juli 2022 (Rp85.267/kg)**, "
    "sementara menjelang **Idul Fitri** harga historis 2020–2024 rata-rata turun -28,7% pada H-7 akibat panen, "
    "namun pada **Idul Fitri 2025** justru berbalik naik (+7,6%, lonjakan satu hari H-5 `2025-03-26` ke Rp58.300/kg)."
)

df_trad = df_filtered[df_filtered["kategori_pasar"].astype(str) == "Pasar Tradisional"].copy()
if df_trad.empty:
    df_trad = df_filtered.copy()

df_trad["bulan_num"] = df_trad["tanggal"].dt.month
nama_bulan = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun",
    7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des",
}
bulanan = (
    df_trad.groupby("bulan_num")
    .agg(
        Median_Harga=("harga_cabai_keriting", "median"),
        Rata_Hujan=("curah_hujan_mm", "mean"),
    )
    .reset_index()
)
bulanan["Bulan"] = bulanan["bulan_num"].map(nama_bulan)

fig_q2 = go.Figure()
fig_q2.add_trace(
    go.Bar(
        x=bulanan["Bulan"],
        y=bulanan["Median_Harga"],
        name="Median Harga (Rp/kg)",
        marker_color="#c62828",
        yaxis="y",
    )
)
fig_q2.add_trace(
    go.Scatter(
        x=bulanan["Bulan"],
        y=bulanan["Rata_Hujan"],
        name="Rata-rata Curah Hujan Harian (mm)",
        mode="lines+markers",
        line=dict(color="#1565c0", width=2.5),
        yaxis="y2",
    )
)
fig_q2.update_layout(
    title="Juni Paling Murah (Rp22.900/kg) & Musim Hujan Sep–Des Memicu Hari Mahal 32,4%",
    yaxis=dict(title="Median Harga (Rp/kg)", tickformat=",.0f"),
    yaxis2=dict(title="Curah Hujan Harian (mm)", overlaying="y", side="right"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=410,
)
st.plotly_chart(fig_q2, use_container_width=True)

# -----------------------------------------------------------------------------
# Pertanyaan 3: Selisih / Markup Antar Level Pasar & Kapan Margin Melebar
# -----------------------------------------------------------------------------
st.divider()
st.header("3. Selisih / Markup Antar Level Pasar & Momen Pelebaran Margin")
st.info(
    "**Temuan Utama:** Rasio median **Pasar Tradisional mencapai 1,53× harga Produsen** dan **1,21× harga Pedagang Besar** "
    "(rentang bulanan 0,99×–1,55×). Margin antar tingkat melebar tajam saat terjadi guncangan pasokan musim hujan "
    "(eceran langsung melonjak harian sementara harga kontrak produsen menyesuaikan lambat) serta ketika terjadi "
    "keterlambatan transmisi penurunan harga dari tingkat grosir ke pengecer pasca-puncak."
)

if "markup_thd_produsen" in df_filtered.columns:
    df_mk_bulanan = (
        df_filtered[df_filtered["kategori_pasar"].astype(str) != "Produsen"]
        .assign(
            periode_bulan=lambda d: d["tanggal"].dt.to_period("M").astype(str),
            kategori_pasar=lambda d: d["kategori_pasar"].astype(str),
        )
        .groupby(["periode_bulan", "kategori_pasar"], observed=True)["markup_thd_produsen"]
        .mean()
        .reset_index()
    )
    fig_q3 = px.line(
        df_mk_bulanan,
        x="periode_bulan",
        y="markup_thd_produsen",
        color="kategori_pasar",
        color_discrete_map=WARNA_PASAR,
        labels={
            "periode_bulan": "Bulan",
            "markup_thd_produsen": "Rata-rata Markup vs Produsen (Rp/kg)",
            "kategori_pasar": "Kategori Pasar",
        },
        title="Margin terhadap Produsen Melebar Tajam Saat Krisis Pasokan 2022 & Hujan Ekstrem 2025",
    )
    fig_q3.update_layout(height=390, yaxis_tickformat=",.0f", hovermode="x unified")
    st.plotly_chart(fig_q3, use_container_width=True)

# -----------------------------------------------------------------------------
# Seksi Khusus: Ringkasan Temuan Model Prediksi & Feature Importance
# -----------------------------------------------------------------------------
st.divider()
st.header("4. Ringkasan Temuan Model Prediksi & Feature Importance")

if metrics:
    best_model = metrics.get("best_model", "Random Forest")
    results = metrics.get("results", [])
    res_map = {r["model"]: r for r in results}
    rf_res = res_map.get(best_model, {})
    lgb_res = res_map.get("LightGBM", {})

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            label=f"Model Produksi ({best_model})",
            value=format_rupiah(rf_res.get("cv", {}).get("MAE", 2298.16)),
            delta="CV MAE terendah (TimeSeriesSplit 5-fold)",
            delta_color="off",
        )
    with m2:
        st.metric(
            label="Test MAE & MAPE (Random Forest)",
            value=format_rupiah(rf_res.get("test", {}).get("MAE", 3335.39)),
            delta=f"MAPE {rf_res.get('test', {}).get('MAPE', 6.85):.2f}% | R² {rf_res.get('test', {}).get('R2', 0.9092):.4f}",
            delta_color="off",
        )
    with m3:
        st.metric(
            label="Test MAE Terbaik (LightGBM)",
            value=format_rupiah(lgb_res.get("test", {}).get("MAE", 3322.42)),
            delta=f"MAPE {lgb_res.get('test', {}).get('MAPE', 6.78):.2f}% pada 282 hari uji",
            delta_color="off",
        )
    with m4:
        st.metric(
            label="Akurasi Hari Tenang vs Hujan Sep–Des",
            value="Rp1.289 (3,36%)",
            delta="vs Rp5.995 (9,49%) di musim hujan Sep–Des",
            delta_color="off",
        )

    c_ml1, c_ml2 = st.columns([1.25, 1])
    with c_ml1:
        fi_dict = metrics.get("feature_importance", {})
        if fi_dict:
            df_fi = (
                pd.DataFrame(
                    [{"Fitur": k, "Kontribusi (%)": v * 100.0} for k, v in fi_dict.items()]
                )
                .sort_values("Kontribusi (%)", ascending=True)
            )
            fig_fi = px.bar(
                df_fi,
                x="Kontribusi (%)",
                y="Fitur",
                orientation="h",
                text_auto=".1f",
                color="Kontribusi (%)",
                color_continuous_scale="Reds",
                title=f"Interaksi Harga×Musim Hujan (55,7%) & Hujan 7H (7,7%) Mendominasi {best_model}",
            )
            fig_fi.update_layout(showlegend=False, height=440, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_fi, use_container_width=True)

    with c_ml2:
        if results:
            rows_res = []
            for r in results:
                rows_res.append(
                    {
                        "Model": r["model"],
                        "CV MAE": format_rupiah(r["cv"]["MAE"]),
                        "Test MAE": format_rupiah(r["test"]["MAE"]),
                        "Test MAPE": f"{r['test']['MAPE']:.2f}%",
                        "Test R²": f"{r['test']['R2']:.4f}",
                    }
                )
            st.subheader("Perbandingan Kinerja 5 Model")
            st.dataframe(pd.DataFrame(rows_res), use_container_width=True, hide_index=True)
            st.caption(
                "Seluruh model pohon mengalahkan baseline Naive Persistence (Test MAE Rp3.340,43) dan "
                "Ridge Regression (Test MAE Rp3.353,21). Sembilan dari 10 galat terbesar muncul pada Sep–Des 2025 "
                "saat curah hujan 7 hari menembus >100 mm hingga 368,5 mm."
            )
else:
    st.info("File `models/metrics.json` belum tersedia.")

# -----------------------------------------------------------------------------
# Panel Rekomendasi Kebijakan & Aksi Konkret (3 Pihak)
# -----------------------------------------------------------------------------
st.divider()
st.header("5. Rekomendasi Kebijakan & Aksi Konkret")

rec1, rec2, rec3 = st.columns(3)
with rec1:
    st.success(
        "### 🏛️ TPID & Dinas Ketahanan Pangan Medan\n"
        "- **Peringatan Dini Cuaca Ekstrem:** Aktifkan operasi pasar & kerja sama pasokan antar-daerah "
        "saat `Akumulasi_Hujan_7H > 100 mm` di periode September–Desember.\n"
        "- **Buffer Stok H-14 Hari Besar:** Antisipasi anomali permintaan seperti Idul Fitri 2025 (+7,6% H-7).\n"
        "- **Audit Margin Rantai Pasok:** Lakukan inspeksi distribusi bila rasio Pasar Tradisional/Produsen melampaui **1,80×**."
    )
with rec2:
    st.warning(
        "### 🚚 Pedagang Besar & Eceran\n"
        "- **Simulasi Pengadaan H+1:** Gunakan modul **Prediksi Harga** untuk menakar arah perubahan esok hari saat musim hujan.\n"
        "- **Diversifikasi Sentra Pasok:** Kurangi ketergantungan pada satu pemasok tunggal saat intensitas hujan tinggi.\n"
        "- **Antisipasi Koreksi Tajam:** Hindari penumpukan stok berlebih ketika harga eceran menembus >Rp70.000/kg karena rawan *mean reversion*."
    )
with rec3:
    st.info(
        "### 🛒 Konsumen Rumah Tangga\n"
        "- **Manfaatkan Periode Panen Murah:** Lakukan pembelian lebih besar atau pengolahan cabai giling/kering sekitar **Juni** (median Rp22.900/kg).\n"
        "- **Bandingkan Pasar Tradisional vs Modern:** Saat gejolak harian di pasar tradisional meningkat tajam (>5%/hari), "
        "cek harga di pasar modern yang penyesuaiannya lebih lambat (hanya berubah pada 13,0% hari kerja)."
    )
