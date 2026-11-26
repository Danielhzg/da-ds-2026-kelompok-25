"""Halaman Modul Prediksi & Evaluasi Model ML (Tahap D3 - Sisi Data Science).

Menyediakan:
1. Form simulasi input baru untuk memprediksi harga cabai merah keriting esok hari
   di Pasar Tradisional Kota Medan menggunakan model ML terbaik & pembanding baseline.
2. Evaluasi terstruktur 5 skenario uji input baru (syarat Minggu 12).
3. Tabel & grafik perbandingan 5 model (Naive, Ridge, Random Forest, XGBoost, LightGBM).
4. Visual diagnostik (Aktual vs Prediksi, Scatter, Residual, Feature Importance, dan 10 galat terbesar).
"""

from __future__ import annotations

import datetime as dt
import json
import sqlite3
from pathlib import Path

import holidays
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    st.set_page_config(
        page_title="Prediksi Harga Cabai (AI) - Kelompok 25",
        page_icon="🌶️",
        layout="wide",
    )
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "warehouse" / "cabai_medan.db"
PROC_DIR = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"
PASAR_FOKUS = "Pasar Tradisional"


def format_rp(nilai: float) -> str:
    """Format angka ke format Rupiah Indonesia dengan titik ribuan."""
    return f"Rp{nilai:,.0f}".replace(",", ".")


@st.cache_resource(show_spinner=False)
def muat_artefak_model() -> tuple[dict, dict, dict, pd.DataFrame]:
    """Muat model terbaik, baseline Ridge, metrics.json, dan prediksi uji."""
    best_bundle = joblib.load(MODELS_DIR / "best_model.joblib")
    ridge_bundle = joblib.load(MODELS_DIR / "baseline_ridge.joblib")
    metrics = json.loads((MODELS_DIR / "metrics.json").read_text(encoding="utf-8"))
    preds_df = pd.read_csv(MODELS_DIR / "test_predictions.csv", parse_dates=["tanggal"])
    return best_bundle, ridge_bundle, metrics, preds_df


@st.cache_data(show_spinner=False)
def muat_konteks_historis() -> tuple[pd.DataFrame, str]:
    """Muat data harga historis terbaru dari warehouse SQLite dengan auto-fallback ke CSV."""
    cuaca = (
        pd.read_csv(PROC_DIR / "01_cuaca_harian.csv", parse_dates=["Tanggal"])
        .sort_values("Tanggal")
        .set_index("Tanggal")
        .asfreq("D")
    )
    df_harga: pd.DataFrame | None = None
    sumber = ""

    if DB_PATH.is_file():
        try:
            with sqlite3.connect(DB_PATH) as con:
                cek = con.execute(
                    "SELECT name FROM sqlite_master WHERE type IN ('view','table') AND name='v_harga_lengkap'"
                ).fetchone()
                if cek:
                    raw = pd.read_sql("SELECT * FROM v_harga_lengkap", con)
                    raw = raw.rename(
                        columns={
                            "tanggal": "Tanggal",
                            "kategori_pasar": "Kategori_Pasar",
                            "harga_cabai_keriting": "Harga_Cabai_Merah_Keriting",
                        }
                    )
                    if {"Tanggal", "Kategori_Pasar", "Harga_Cabai_Merah_Keriting"}.issubset(raw.columns):
                        raw["Tanggal"] = pd.to_datetime(raw["Tanggal"])
                        df_harga = raw
                        sumber = "Data Warehouse SQLite (`warehouse/cabai_medan.db`)"
        except Exception:
            df_harga = None

    if df_harga is None:
        df_harga = pd.read_csv(PROC_DIR / "01_clean.csv", parse_dates=["Tanggal"])
        sumber = "Fallback CSV (`data/processed/01_clean.csv`)"

    df_harga = df_harga.sort_values(["Kategori_Pasar", "Tanggal"]).reset_index(drop=True)
    wide = df_harga.pivot(index="Tanggal", columns="Kategori_Pasar", values="Harga_Cabai_Merah_Keriting")
    wide["Akumulasi_Hujan_7H"] = cuaca["Curah_Hujan_mm"].shift(1).rolling(7).sum().reindex(wide.index)
    wide = wide.dropna().sort_index()
    return wide, sumber


@st.cache_data(show_spinner=False)
def daftar_idul_fitri() -> list[pd.Timestamp]:
    """Daftar tanggal Idul Fitri di Indonesia (2019-2029) untuk perhitungan jarak hari."""
    libur = holidays.country_holidays("ID", years=range(2019, 2030))
    return sorted(pd.Timestamp(d) for d, n in libur.items() if "Hari Raya Idul Fitri" in n.split("; "))


def hitung_hari_ke_idul_fitri(tgl: dt.date | pd.Timestamp) -> int:
    """Hitung selisih hari dari tanggal target menuju Idul Fitri terdekat berikutnya."""
    ts = pd.Timestamp(tgl)
    for d in daftar_idul_fitri():
        if d >= ts:
            return int((d - ts).days)
    return 180


def bentuk_fitur_input(
    *,
    tanggal_prediksi: dt.date,
    harga_lag1: float,
    harga_lag5: float,
    harga_lag20: float,
    harga_ma7: float,
    harga_ma20: float,
    harga_produsen_lag1: float,
    harga_pb_lag1: float,
    akumulasi_hujan_7h: float,
    te_bulan_map: dict[int, float],
    te_global_mean: float,
    override_hari_idul_fitri: int | None = None,
) -> dict[str, float]:
    """Susun 12 fitur kandidat sesuai skema `models/train.py`."""
    bulan = int(pd.Timestamp(tanggal_prediksi).month)
    is_musim_hujan = 1 if bulan in (9, 10, 11, 12) else 0
    hari_fitri = (
        int(override_hari_idul_fitri)
        if override_hari_idul_fitri is not None
        else hitung_hari_ke_idul_fitri(tanggal_prediksi)
    )
    te_val = float(te_bulan_map.get(bulan, te_bulan_map.get(str(bulan), te_global_mean)))  # type: ignore[arg-type]
    return {
        "Harga_Lag1": float(harga_lag1),
        "Harga_MA7": float(harga_ma7),
        "Harga_Lag5": float(harga_lag5),
        "TE_Pasar_Bulan": te_val,
        "Harga_MA20": float(harga_ma20),
        "Harga_Lag20": float(harga_lag20),
        "Harga_Produsen_Lag1": float(harga_produsen_lag1),
        "Harga_PB_Lag1": float(harga_pb_lag1),
        "Interaksi_Lag1_x_MusimHujan": float(harga_lag1) * is_musim_hujan,
        "Level_Rantai_Pasok": 3.0,
        "Hari_Menuju_Idul_Fitri": float(hari_fitri),
        "Akumulasi_Hujan_7H": float(akumulasi_hujan_7h),
    }


def prediksi_dengan_bundle(bundle: dict, fitur_dict: dict[str, float]) -> tuple[float, float]:
    """Kembalikan (harga_prediksi_rp, delta_rp) dari bundle model delta."""
    cols = list(bundle["features"])
    X = pd.DataFrame([[fitur_dict[c] for c in cols]], columns=cols)
    delta_hat = float(bundle["model"].predict(X)[0])
    harga_hat = max(1000.0, float(fitur_dict["Harga_Lag1"]) + delta_hat)
    return harga_hat, harga_hat - float(fitur_dict["Harga_Lag1"])


def klasifikasi_gejolak(delta_pct: float) -> str:
    """Kategorikan sinyal perubahan harga harian untuk pengambil keputusan."""
    if delta_pct >= 5.0:
        return "Lonjakan Tinggi (>= +5%)"
    if delta_pct >= 1.5:
        return "Waspada Naik (+1,5% s.d. +5%)"
    if delta_pct <= -5.0:
        return "Turun Tajam (<= -5%)"
    if delta_pct <= -1.5:
        return "Melandai (-1,5% s.d. -5%)"
    return "Stabil (-1,5% s.d. +1,5%)"


def main() -> None:
    st.title("Modul Prediksi Harga & Evaluasi Model ML")
    st.caption(
        "Lapisan Data Science — Prediksi perubahan harga harian Cabai Merah Keriting di "
        "**Pasar Tradisional Kota Medan** beserta uji input baru, perbandingan 5 model, dan analisis galat."
    )

    best_bundle, ridge_bundle, metrics, preds_df = muat_artefak_model()
    wide_hist, sumber_data = muat_konteks_historis()

    best_name = str(metrics["best_model"])
    best_res = next(r for r in metrics["results"] if r["model"] == best_name)
    best_test_mae = float(best_res["test"]["MAE"])
    best_test_mape = float(best_res["test"]["MAPE"])

    st.info(
        f"**Sumber data historis:** {sumber_data} | **Model terpilih:** `{best_name}` "
        f"(CV MAE **{format_rp(best_res['cv']['MAE'])}**, Test MAE **{format_rp(best_test_mae)}**, "
        f"MAPE **{best_test_mape:.2f}%**, $R^2$ **{best_res['test']['R2']:.4f}**; dilatih s.d. `{best_bundle['trained_until']}`)."
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Simulasi Prediksi Input Baru",
            "Uji Terstruktur Input Baru (M12)",
            "Perbandingan 5 Model",
            "Diagnostik & Analisis Galat",
        ]
    )

    # Nilai default dari hari terakhir dataset historis
    last_tgl = wide_hist.index[-1]
    default_pred_date = (last_tgl + pd.Timedelta(days=1)).date()
    default_lag1 = float(wide_hist["Pasar Tradisional"].iloc[-1])
    default_lag5 = float(wide_hist["Pasar Tradisional"].iloc[-5])
    default_lag20 = float(wide_hist["Pasar Tradisional"].iloc[-20])
    default_ma7 = float(wide_hist["Pasar Tradisional"].iloc[-7:].mean())
    default_ma20 = float(wide_hist["Pasar Tradisional"].iloc[-20:].mean())
    default_prod = float(wide_hist["Produsen"].iloc[-1])
    default_pb = float(wide_hist["Pedagang Besar"].iloc[-1])
    default_hujan7 = float(wide_hist["Akumulasi_Hujan_7H"].iloc[-1])

    # =========================================================================
    # TAB 1: SIMULASI PREDIKSI INPUT BARU
    # =========================================================================
    with tab1:
        st.subheader("Form Input Data Baru untuk Prediksi Harga Esok Hari")
        st.caption(
            "Nilai awal form otomatis terisi dari kondisi hari kerja terakhir di database. "
            "Ubah parameter di bawah untuk menguji skenario harga hulu, riwayat harga, atau curah hujan."
        )

        with st.form("form_prediksi_harga"):
            c1, c2, c3 = st.columns(3)
            with c1:
                in_tgl = st.date_input("Tanggal Target Prediksi", value=default_pred_date)
                in_lag1 = st.number_input(
                    "Harga Pasar Tradisional H-1 (Rp/kg)",
                    min_value=5000,
                    max_value=200000,
                    value=int(round(default_lag1)),
                    step=500,
                )
                in_lag5 = st.number_input(
                    "Harga Pasar Tradisional H-5 (Rp/kg)",
                    min_value=5000,
                    max_value=200000,
                    value=int(round(default_lag5)),
                    step=500,
                )
            with c2:
                in_ma7 = st.number_input(
                    "Rata-rata 7 Hari Terakhir MA7 (Rp/kg)",
                    min_value=5000,
                    max_value=200000,
                    value=int(round(default_ma7)),
                    step=500,
                )
                in_ma20 = st.number_input(
                    "Rata-rata 20 Hari Terakhir MA20 (Rp/kg)",
                    min_value=5000,
                    max_value=200000,
                    value=int(round(default_ma20)),
                    step=500,
                )
                in_lag20 = st.number_input(
                    "Harga Pasar Tradisional H-20 (Rp/kg)",
                    min_value=5000,
                    max_value=200000,
                    value=int(round(default_lag20)),
                    step=500,
                )
            with c3:
                in_prod = st.number_input(
                    "Harga Produsen / Petani H-1 (Rp/kg)",
                    min_value=3000,
                    max_value=150000,
                    value=int(round(default_prod)),
                    step=500,
                )
                in_pb = st.number_input(
                    "Harga Pedagang Besar / Grosir H-1 (Rp/kg)",
                    min_value=3000,
                    max_value=180000,
                    value=int(round(default_pb)),
                    step=500,
                )
                in_hujan7 = st.number_input(
                    "Akumulasi Curah Hujan 7 Hari Terakhir (mm)",
                    min_value=0.0,
                    max_value=600.0,
                    value=float(round(default_hujan7, 1)),
                    step=5.0,
                )

            st.form_submit_button("Hitung Prediksi Harga", type="primary")

        fitur_in = bentuk_fitur_input(
            tanggal_prediksi=in_tgl,
            harga_lag1=float(in_lag1),
            harga_lag5=float(in_lag5),
            harga_lag20=float(in_lag20),
            harga_ma7=float(in_ma7),
            harga_ma20=float(in_ma20),
            harga_produsen_lag1=float(in_prod),
            harga_pb_lag1=float(in_pb),
            akumulasi_hujan_7h=float(in_hujan7),
            te_bulan_map=best_bundle["te_bulan_map"],
            te_global_mean=float(best_bundle["te_global_mean"]),
        )
        pred_best_rp, delta_best_rp = prediksi_dengan_bundle(best_bundle, fitur_in)
        pred_ridge_rp, delta_ridge_rp = prediksi_dengan_bundle(ridge_bundle, fitur_in)
        delta_best_pct = (delta_best_rp / float(in_lag1)) * 100.0 if in_lag1 else 0.0
        delta_ridge_pct = (delta_ridge_rp / float(in_lag1)) * 100.0 if in_lag1 else 0.0

        k1, k2, k3, k4 = st.columns(4)
        k1.metric(
            f"Prediksi {best_name}",
            format_rp(pred_best_rp),
            delta=f"{delta_best_rp:+,.0f} Rp ({delta_best_pct:+.2f}%)".replace(",", "."),
        )
        k2.metric("Harga Acuan Kemarin (H-1)", format_rp(float(in_lag1)))
        k3.metric("Sinyal Pergerakan", klasifikasi_gejolak(delta_best_pct))
        k4.metric(
            "Rentang Wajar (± Test MAE)",
            f"{format_rp(max(1000.0, pred_best_rp - best_test_mae))} – {format_rp(pred_best_rp + best_test_mae)}",
        )

        st.markdown("##### Perbandingan Hasil Prediksi pada Input Baru Ini")
        df_sim_cmp = pd.DataFrame(
            [
                {
                    "Model": f"{best_name} (Model Terbaik)",
                    "Prediksi Harga (Rp/kg)": format_rp(pred_best_rp),
                    "Perubahan vs H-1 (Rp)": f"{delta_best_rp:+,.0f}".replace(",", "."),
                    "Perubahan (%)": f"{delta_best_pct:+.2f}%",
                    "Status": klasifikasi_gejolak(delta_best_pct),
                },
                {
                    "Model": "Ridge Regression (Baseline ML)",
                    "Prediksi Harga (Rp/kg)": format_rp(pred_ridge_rp),
                    "Perubahan vs H-1 (Rp)": f"{delta_ridge_rp:+,.0f}".replace(",", "."),
                    "Perubahan (%)": f"{delta_ridge_pct:+.2f}%",
                    "Status": klasifikasi_gejolak(delta_ridge_pct),
                },
                {
                    "Model": "Naive Persistence (Acuan Harga Kemarin)",
                    "Prediksi Harga (Rp/kg)": format_rp(float(in_lag1)),
                    "Perubahan vs H-1 (Rp)": "0",
                    "Perubahan (%)": "0.00%",
                    "Status": "Stabil (-1,5% s.d. +1,5%)",
                },
            ]
        )
        st.dataframe(df_sim_cmp, width="stretch", hide_index=True)

        with st.expander("Lihat 12 nilai fitur hasil transformasi yang dikirim ke model"):
            df_feat_view = pd.DataFrame(
                [{"Fitur": k, "Nilai": round(v, 2)} for k, v in fitur_in.items()]
            )
            st.dataframe(df_feat_view, width="stretch", hide_index=True)

    # =========================================================================
    # TAB 2: UJI TERSTRUKTUR INPUT BARU (SYARAT MINGGU 12)
    # =========================================================================
    with tab2:
        st.subheader("Laporan Uji Input Baru Terstruktur (5 Skenario Operasional)")
        st.caption(
            "Pengujian otomatis perilaku model terhadap 5 skenario masukan baru untuk memastikan "
            "respons model masuk akal secara domain sebelum dan sesudah deployment publik."
        )

        skenario_list = [
            {
                "Skenario": "1. Pasar Normal (Kondisi Terakhir)",
                "Ringkasan Input": f"Lag1={format_rp(default_lag1)}, Hujan7H={default_hujan7:.1f}mm",
                "tgl": default_pred_date,
                "lag1": default_lag1,
                "lag5": default_lag5,
                "lag20": default_lag20,
                "ma7": default_ma7,
                "ma20": default_ma20,
                "prod": default_prod,
                "pb": default_pb,
                "hujan7": default_hujan7,
                "fitri": None,
            },
            {
                "Skenario": "2. Musim Hujan Ekstrem (Nov)",
                "Ringkasan Input": "Hujan 7H=180mm (Musim Hujan Sep-Des), Lag1=Rp45.000",
                "tgl": dt.date(2026, 11, 15),
                "lag1": 45000.0,
                "lag5": 41000.0,
                "lag20": 37000.0,
                "ma7": 43200.0,
                "ma20": 39500.0,
                "prod": 32000.0,
                "pb": 39000.0,
                "hujan7": 180.0,
                "fitri": None,
            },
            {
                "Skenario": "3. Lonjakan Harga Hulu (+25%)",
                "Ringkasan Input": "Produsen=Rp40.000, Grosir=Rp48.000, Trad Lag1=Rp46.000",
                "tgl": dt.date(2026, 2, 10),
                "lag1": 46000.0,
                "lag5": 40000.0,
                "lag20": 35000.0,
                "ma7": 43500.0,
                "ma20": 38500.0,
                "prod": 40000.0,
                "pb": 48000.0,
                "hujan7": 65.0,
                "fitri": None,
            },
            {
                "Skenario": "4. H-5 Menjelang Idul Fitri",
                "Ringkasan Input": "Hari_Menuju_Idul_Fitri=5, Lag1=Rp55.000",
                "tgl": dt.date(2026, 3, 15),
                "lag1": 55000.0,
                "lag5": 52000.0,
                "lag20": 47000.0,
                "ma7": 53800.0,
                "ma20": 50200.0,
                "prod": 36000.0,
                "pb": 46000.0,
                "hujan7": 40.0,
                "fitri": 5,
            },
            {
                "Skenario": "5. Panen Raya Musim Kemarau (Jun)",
                "Ringkasan Input": "Bulan Juni, Hujan 7H=12mm, Harga Melandai Rp26.000",
                "tgl": dt.date(2026, 6, 15),
                "lag1": 26000.0,
                "lag5": 28500.0,
                "lag20": 32000.0,
                "ma7": 27100.0,
                "ma20": 29800.0,
                "prod": 17500.0,
                "pb": 21500.0,
                "hujan7": 12.0,
                "fitri": None,
            },
        ]

        uji_rows = []
        for sk in skenario_list:
            f_row = bentuk_fitur_input(
                tanggal_prediksi=sk["tgl"],
                harga_lag1=sk["lag1"],
                harga_lag5=sk["lag5"],
                harga_lag20=sk["lag20"],
                harga_ma7=sk["ma7"],
                harga_ma20=sk["ma20"],
                harga_produsen_lag1=sk["prod"],
                harga_pb_lag1=sk["pb"],
                akumulasi_hujan_7h=sk["hujan7"],
                te_bulan_map=best_bundle["te_bulan_map"],
                te_global_mean=float(best_bundle["te_global_mean"]),
                override_hari_idul_fitri=sk["fitri"],
            )
            p_best, d_best = prediksi_dengan_bundle(best_bundle, f_row)
            p_ridge, d_ridge = prediksi_dengan_bundle(ridge_bundle, f_row)
            uji_rows.append(
                {
                    "Skenario Uji": sk["Skenario"],
                    "Ringkasan Input": sk["Ringkasan Input"],
                    "Harga H-1 (Rp)": round(sk["lag1"], 0),
                    f"Prediksi {best_name} (Rp)": round(p_best, 0),
                    "Delta Model Terbaik (Rp)": round(d_best, 0),
                    "Delta (%)": round((d_best / sk["lag1"]) * 100.0, 2),
                    "Prediksi Ridge (Rp)": round(p_ridge, 0),
                    "Status": klasifikasi_gejolak((d_best / sk["lag1"]) * 100.0),
                }
            )
        df_uji = pd.DataFrame(uji_rows)
        st.dataframe(df_uji, width="stretch", hide_index=True)

        fig_uji = px.bar(
            df_uji,
            x="Delta Model Terbaik (Rp)",
            y="Skenario Uji",
            orientation="h",
            color="Delta Model Terbaik (Rp)",
            color_continuous_scale=["#0d9488", "#94a3b8", "#dc2626"],
            text="Delta Model Terbaik (Rp)",
            title=f"Respons Perubahan Harga Harian ({best_name}) pada 5 Skenario Input Baru",
        )
        fig_uji.update_traces(texttemplate="%{text:+,.0f} Rp", textposition="outside")
        fig_uji.update_layout(height=360, coloraxis_showscale=False, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_uji, width="stretch")

    # =========================================================================
    # TAB 3: PERBANDINGAN 5 MODEL
    # =========================================================================
    with tab3:
        st.subheader("Perbandingan Performa 5 Kandidat Model (`TimeSeriesSplit` & Data Uji 2025–2026)")
        st.caption(
            f"Strategi pemodelan: {metrics['strategi']} | "
            f"Train: `{metrics['split']['train']}` ({metrics['split']['n_train']} hari) · "
            f"Test: `{metrics['split']['test']}` ({metrics['split']['n_test']} hari)."
        )

        rows_cmp = []
        for r in metrics["results"]:
            rows_cmp.append(
                {
                    "Model": r["model"],
                    "Jumlah Fitur": r["n_fitur"],
                    "CV MAE (Rp)": r["cv"]["MAE"],
                    "CV RMSE (Rp)": r["cv"]["RMSE"],
                    "Test MAE (Rp)": r["test"]["MAE"],
                    "Test RMSE (Rp)": r["test"]["RMSE"],
                    "Test MAPE (%)": r["test"]["MAPE"],
                    "Test R²": r["test"]["R2"],
                    "Waktu Latih (detik)": r["waktu_latih_detik"],
                }
            )
        df_cmp = pd.DataFrame(rows_cmp)
        st.dataframe(df_cmp, width="stretch", hide_index=True)

        c_left, c_right = st.columns(2)
        with c_left:
            df_mae_melt = df_cmp.melt(
                id_vars="Model", value_vars=["CV MAE (Rp)", "Test MAE (Rp)"], var_name="Tahap", value_name="MAE"
            )
            fig_mae = px.bar(
                df_mae_melt,
                x="Model",
                y="MAE",
                color="Tahap",
                barmode="group",
                text="MAE",
                title="Perbandingan MAE: Cross-Validation vs Test",
                color_discrete_sequence=["#64748b", "#0f4c5c"],
            )
            fig_mae.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
            fig_mae.update_layout(height=400, xaxis_tickangle=-20)
            st.plotly_chart(fig_mae, width="stretch")

        with c_right:
            fig_rmse = px.bar(
                df_cmp,
                x="Model",
                y="Test RMSE (Rp)",
                color="Test RMSE (Rp)",
                text="Test RMSE (Rp)",
                title="Perbandingan Test RMSE (Semakin Rendah Semakin Baik)",
                color_continuous_scale="Teal",
            )
            fig_rmse.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
            fig_rmse.update_layout(height=400, xaxis_tickangle=-20, coloraxis_showscale=False)
            st.plotly_chart(fig_rmse, width="stretch")

        with st.expander("Lihat Hyperparameter Terbaik Hasil Tuning (RandomizedSearchCV / GridSearchCV)"):
            params_rows = [
                {
                    "Model": r["model"],
                    "Hyperparameter Terbaik": json.dumps(r["best_params"], ensure_ascii=False) or "-",
                }
                for r in metrics["results"]
            ]
            st.dataframe(pd.DataFrame(params_rows), width="stretch", hide_index=True)

    # =========================================================================
    # TAB 4: DIAGNOSTIK & ANALISIS GALAT
    # =========================================================================
    with tab4:
        st.subheader("Visualisasi Hasil Prediksi, Residual, Feature Importance & Error Analysis")

        # 1. Time Series Aktual vs Prediksi pada Data Uji
        fig_ts = go.Figure()
        fig_ts.add_trace(
            go.Scatter(
                x=preds_df["tanggal"],
                y=preds_df["aktual"],
                mode="lines",
                name="Harga Aktual",
                line=dict(color="#0f172a", width=2.4),
            )
        )
        fig_ts.add_trace(
            go.Scatter(
                x=preds_df["tanggal"],
                y=preds_df["prediksi_terbaik"],
                mode="lines",
                name=f"Prediksi {best_name}",
                line=dict(color="#0d9488", width=1.8, dash="dash"),
            )
        )
        fig_ts.add_trace(
            go.Scatter(
                x=preds_df["tanggal"],
                y=preds_df["pred_lightgbm"],
                mode="lines",
                name="Prediksi LightGBM",
                line=dict(color="#d97706", width=1.4, dash="dot"),
            )
        )
        fig_ts.update_layout(
            title=f"Aktual vs Prediksi pada Data Uji ({metrics['split']['test']}, n={len(preds_df)} hari)",
            xaxis_title="Tanggal",
            yaxis_title="Harga (Rp/kg)",
            hovermode="x unified",
            height=420,
        )
        st.plotly_chart(fig_ts, width="stretch")

        col_a, col_b = st.columns(2)
        with col_a:
            # 2. Scatter Actual vs Predicted
            fig_sc = px.scatter(
                preds_df,
                x="aktual",
                y="prediksi_terbaik",
                hover_data=["tanggal", "residual", "ape_persen"],
                title=f"Actual vs Predicted ({best_name})",
                labels={"aktual": "Harga Aktual (Rp/kg)", "prediksi_terbaik": "Harga Prediksi (Rp/kg)"},
                color_discrete_sequence=["#0f4c5c"],
            )
            min_v = float(min(preds_df["aktual"].min(), preds_df["prediksi_terbaik"].min()))
            max_v = float(max(preds_df["aktual"].max(), preds_df["prediksi_terbaik"].max()))
            fig_sc.add_shape(
                type="line", x0=min_v, y0=min_v, x1=max_v, y1=max_v, line=dict(color="#dc2626", dash="dash")
            )
            fig_sc.update_layout(height=380)
            st.plotly_chart(fig_sc, width="stretch")

        with col_b:
            # 3. Plot Residual terhadap Waktu
            fig_res = px.scatter(
                preds_df,
                x="tanggal",
                y="residual",
                color="abs_residual",
                color_continuous_scale="Reds",
                title="Residual Prediksi Sepanjang Waktu (Aktual - Prediksi)",
                labels={"tanggal": "Tanggal", "residual": "Residual (Rp/kg)", "abs_residual": "|Galat|"},
            )
            fig_res.add_hline(y=0, line_dash="dash", line_color="#334155")
            fig_res.update_layout(height=380, coloraxis_showscale=False)
            st.plotly_chart(fig_res, width="stretch")

        # 4. Feature Importance & 10 Residual Terbesar
        col_c, col_d = st.columns([1, 1.5])
        with col_c:
            st.markdown("##### Feature Importance Model Terbaik")
            fi_items = [
                {"Fitur": k, "Bobot (%)": round(v * 100.0, 2)}
                for k, v in metrics["feature_importance"].items()
            ]
            df_fi = pd.DataFrame(fi_items)
            fig_fi = px.bar(
                df_fi,
                x="Bobot (%)",
                y="Fitur",
                orientation="h",
                text="Bobot (%)",
                color="Bobot (%)",
                color_continuous_scale="Teal",
            )
            fig_fi.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_fi.update_layout(
                height=380,
                yaxis={"categoryorder": "total ascending"},
                coloraxis_showscale=False,
                margin=dict(t=20, b=20),
            )
            st.plotly_chart(fig_fi, width="stretch")

        with col_d:
            st.markdown("##### Error Analysis: 10 Hari dengan Residual Terbesar")
            df_err = pd.DataFrame(metrics["residual_terbesar"]).rename(
                columns={
                    "tanggal": "Tanggal",
                    "harga_lag1": "Lag1 (Rp)",
                    "aktual": "Aktual (Rp)",
                    "prediksi": "Prediksi (Rp)",
                    "residual": "Residual (Rp)",
                    "ape_persen": "APE (%)",
                    "akumulasi_hujan_7h": "Hujan 7H (mm)",
                    "hari_menuju_idul_fitri": "H-Idul Fitri",
                }
            )
            st.dataframe(
                df_err[
                    [
                        "Tanggal",
                        "Lag1 (Rp)",
                        "Aktual (Rp)",
                        "Prediksi (Rp)",
                        "Residual (Rp)",
                        "APE (%)",
                        "Hujan 7H (mm)",
                        "H-Idul Fitri",
                    ]
                ],
                width="stretch",
                hide_index=True,
                height=350,
            )


if __name__ == "__main__":
    main()
