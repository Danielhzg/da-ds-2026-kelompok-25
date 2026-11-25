"""Pelatihan, tuning, dan evaluasi 5 kandidat model prediksi harga cabai (Tahap D2).

Alur:
1. Muat data harga dari SQLite warehouse (`warehouse/cabai_medan.db`, view `v_harga_lengkap`)
   dengan auto-fallback ke `data/processed/01_clean.csv` + `01_cuaca_harian.csv`.
2. Rekonstruksi 12 fitur terpilih bebas leakage (`data/processed/05_fitur_final_uas.json`)
   dan fokuskan pemodelan pada `Pasar Tradisional` (Train <= 2024-12-31, Test >= 2025-01-01).
3. Evaluasi 5 kandidat pada target perubahan harga `dy_t = y_t - Harga_Lag1` (-> Rupiah):
   - Naive (Persistence: Harga_Lag1)
   - Ridge Regression (Baseline, 10 fitur bebas multikolinearitas)
   - Random Forest (12 fitur)
   - XGBoost (12 fitur)
   - LightGBM (12 fitur)
4. Pilih model ML terbaik berdasarkan CV MAE terendah (`TimeSeriesSplit` 5-fold),
   refit pada seluruh data historis, lalu simpan `best_model.joblib`, `baseline_ridge.joblib`,
   `metrics.json`, dan `test_predictions.csv` ke folder `models/`.

Jalankan dari root repo:
    python models/train.py
"""

from __future__ import annotations

import json
import sqlite3
import time
import warnings
from pathlib import Path

import holidays
import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, TimeSeriesSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
DB_PATH = ROOT / "warehouse" / "cabai_medan.db"
OUT_DIR = ROOT / "models"

RANDOM_STATE = 42
TARGET = "Harga_Cabai_Merah_Keriting"
PASAR_URUT = ["Produsen", "Pedagang Besar", "Pasar Tradisional", "Pasar Modern"]
PASAR_FOKUS = "Pasar Tradisional"
SPLIT_DATE = pd.Timestamp("2024-12-31")
NAIVE_NAME = "Naive (Persistence)"
BASELINE_NAME = "Ridge Regression (Baseline)"


def load_source_data() -> tuple[pd.DataFrame, pd.DataFrame, str]:
    """Muat data harga dari warehouse SQLite jika tersedia, fallback otomatis ke CSV bersih."""
    cuaca = (
        pd.read_csv(PROC / "01_cuaca_harian.csv", parse_dates=["Tanggal"])
        .sort_values("Tanggal")
        .set_index("Tanggal")
        .asfreq("D")
    )

    df_harga: pd.DataFrame | None = None
    source_label = ""
    if DB_PATH.is_file():
        try:
            with sqlite3.connect(DB_PATH) as con:
                cek = con.execute(
                    "SELECT name FROM sqlite_master WHERE type IN ('view','table') AND name='v_harga_lengkap'"
                ).fetchone()
                if cek:
                    raw_db = pd.read_sql("SELECT * FROM v_harga_lengkap", con)
                    rename_map = {
                        "tanggal": "Tanggal",
                        "kategori_pasar": "Kategori_Pasar",
                        "harga_cabai_keriting": TARGET,
                        "curah_hujan_mm": "Curah_Hujan_mm",
                    }
                    raw_db = raw_db.rename(
                        columns={k: v for k, v in rename_map.items() if k in raw_db.columns}
                    )
                    if {"Tanggal", "Kategori_Pasar", TARGET}.issubset(raw_db.columns):
                        raw_db["Tanggal"] = pd.to_datetime(raw_db["Tanggal"])
                        df_harga = raw_db
                        source_label = f"SQLite Warehouse ({DB_PATH.relative_to(ROOT).as_posix()})"
        except Exception as exc:
            print(f"[peringatan] Gagal membaca warehouse SQLite ({exc}); fallback ke CSV bersih.")

    if df_harga is None:
        df_harga = pd.read_csv(PROC / "01_clean.csv", parse_dates=["Tanggal"])
        source_label = f"Fallback CSV ({(PROC / '01_clean.csv').relative_to(ROOT).as_posix()})"

    df_harga = df_harga.sort_values(["Kategori_Pasar", "Tanggal"]).reset_index(drop=True)
    return df_harga, cuaca, source_label


def build_leakage_free_features(df_harga: pd.DataFrame, cuaca: pd.DataFrame) -> pd.DataFrame:
    """Rekonstruksi fitur final berbasis riwayat <= H-1 (konsisten dengan NB03, NB05, NB06)."""
    df = df_harga.copy()
    df["Bulan"] = df["Tanggal"].dt.month

    g = df.groupby("Kategori_Pasar")[TARGET]
    df["Harga_Lag1"] = g.shift(1)
    df["Harga_Lag5"] = g.shift(5)
    df["Harga_Lag20"] = g.shift(20)
    df["Harga_MA7"] = g.transform(lambda s: s.shift(1).rolling(7).mean())
    df["Harga_MA20"] = g.transform(lambda s: s.shift(1).rolling(20).mean())

    wide = df.pivot(index="Tanggal", columns="Kategori_Pasar", values=TARGET)
    hulu = wide[["Produsen", "Pedagang Besar"]].shift(1).rename(
        columns={"Produsen": "Harga_Produsen_Lag1", "Pedagang Besar": "Harga_PB_Lag1"}
    )
    df = df.merge(hulu, left_on="Tanggal", right_index=True, how="left")

    cal = pd.DataFrame(index=cuaca.index)
    cal["Akumulasi_Hujan_7H"] = cuaca["Curah_Hujan_mm"].shift(1).rolling(7).sum()
    df = df.merge(cal, left_on="Tanggal", right_index=True, how="left")

    libur = holidays.country_holidays("ID", years=range(2019, 2028))
    idul_fitri = sorted(
        pd.Timestamp(d) for d, n in libur.items() if "Hari Raya Idul Fitri" in n.split("; ")
    )
    df["Hari_Menuju_Idul_Fitri"] = df["Tanggal"].apply(
        lambda t: next(((d - t).days for d in idul_fitri if d >= t), np.nan)
    )
    df["Is_Musim_Hujan"] = df["Bulan"].isin([9, 10, 11, 12]).astype(int)
    df["Level_Rantai_Pasok"] = df["Kategori_Pasar"].map(dict(zip(PASAR_URUT, [1, 2, 3, 4])))
    df["Interaksi_Lag1_x_MusimHujan"] = df["Harga_Lag1"] * df["Is_Musim_Hujan"]

    df = (
        df.dropna(subset=["Harga_Lag20", "Harga_MA20", "Akumulasi_Hujan_7H", "Hari_Menuju_Idul_Fitri"])
        .sort_values(["Tanggal", "Kategori_Pasar"])
        .reset_index(drop=True)
    )
    return df


def apply_smoothed_te(
    tr_df: pd.DataFrame, target_df: pd.DataFrame, smoothing: int = 20
) -> tuple[pd.DataFrame, pd.DataFrame, dict[int, float], float]:
    """Hitung TE_Pasar_Bulan khusus dari tr_df untuk mencegah data leakage."""
    tr_out = tr_df.copy()
    te_out = target_df.copy()
    global_mean = float(tr_out[TARGET].mean())
    grp = tr_out.groupby("Bulan")[TARGET].agg(["count", "mean"])
    te_map = {
        int(bulan): float((row["count"] * row["mean"] + smoothing * global_mean) / (row["count"] + smoothing))
        for bulan, row in grp.iterrows()
    }
    tr_out["TE_Pasar_Bulan"] = tr_out["Bulan"].map(te_map).fillna(global_mean)
    te_out["TE_Pasar_Bulan"] = te_out["Bulan"].map(te_map).fillna(global_mean)
    return tr_out, te_out, te_map, global_mean


def compute_metrics(y_true: np.ndarray | pd.Series, y_pred: np.ndarray | pd.Series) -> dict[str, float]:
    """Hitung MAE, RMSE, MAPE, dan R2 pada skala Rupiah."""
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    return {
        "MAE": round(float(mean_absolute_error(yt, yp)), 2),
        "RMSE": round(float(root_mean_squared_error(yt, yp)), 2),
        "MAPE": round(float(np.mean(np.abs(yt - yp) / yt) * 100.0), 4),
        "R2": round(float(r2_score(yt, yp)), 5),
    }


def to_python_scalar(val: object) -> object:
    """Konversi tipe NumPy menjadi tipe dasar Python untuk serialisasi JSON."""
    if isinstance(val, np.generic):
        return val.item()
    return val


def build_candidates(feat_linear: list[str], feat_tree: list[str]) -> list[dict[str, object]]:
    """Daftar 5 kandidat model beserta ruang tuning hyperparameter."""
    return [
        {
            "name": NAIVE_NAME,
            "features": feat_linear,
            "estimator": None,
            "search_type": None,
            "param_grid": {},
            "n_iter": 0,
        },
        {
            "name": BASELINE_NAME,
            "features": feat_linear,
            "estimator": make_pipeline(StandardScaler(), Ridge(random_state=RANDOM_STATE)),
            "search_type": "grid",
            "param_grid": {"ridge__alpha": [1.0, 10.0, 50.0, 100.0, 500.0, 1000.0, 5000.0]},
            "n_iter": 0,
        },
        {
            "name": "Random Forest",
            "features": feat_tree,
            "estimator": RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1),
            "search_type": "random",
            "param_grid": {
                "criterion": ["absolute_error"],
                "n_estimators": [200, 300, 400],
                "max_depth": [4, 6, 8, 10],
                "min_samples_leaf": [15, 25, 35, 50],
                "max_features": [0.5, 0.7, 1.0],
            },
            "n_iter": 8,
        },
        {
            "name": "XGBoost",
            "features": feat_tree,
            "estimator": XGBRegressor(random_state=RANDOM_STATE, n_jobs=-1, verbosity=0),
            "search_type": "random",
            "param_grid": {
                "objective": ["reg:absoluteerror", "reg:pseudohubererror"],
                "huber_slope": [300.0, 500.0, 1000.0],
                "n_estimators": [200, 300, 450],
                "max_depth": [2, 3, 4],
                "learning_rate": [0.015, 0.025, 0.04],
                "min_child_weight": [25, 40, 60],
                "subsample": [0.75, 0.85, 1.0],
                "colsample_bytree": [0.7, 0.85, 1.0],
            },
            "n_iter": 12,
        },
        {
            "name": "LightGBM",
            "features": feat_tree,
            "estimator": LGBMRegressor(random_state=RANDOM_STATE, n_jobs=-1, verbose=-1),
            "search_type": "random",
            "param_grid": {
                "objective": ["mae", "huber"],
                "alpha": [150.0, 300.0, 600.0],
                "n_estimators": [200, 300, 450],
                "num_leaves": [7, 15, 23],
                "max_depth": [3, 4, 5],
                "learning_rate": [0.015, 0.025, 0.04],
                "min_child_samples": [30, 45, 65],
                "subsample": [0.8, 1.0],
                "subsample_freq": [1],
                "colsample_bytree": [0.75, 0.9, 1.0],
            },
            "n_iter": 12,
        },
    ]


def evaluate_cv_folds(
    tr_df: pd.DataFrame,
    tscv: TimeSeriesSplit,
    estimator: object | None,
    features: list[str],
) -> dict[str, float]:
    """Hitung rata-rata metrik CV 5-fold tanpa leakage TE_Pasar_Bulan."""
    y_val_all: list[np.ndarray] = []
    p_val_all: list[np.ndarray] = []

    for tr_idx, va_idx in tscv.split(tr_df):
        f_tr, f_va, _, _ = apply_smoothed_te(tr_df.iloc[tr_idx], tr_df.iloc[va_idx])
        if estimator is None:
            pred_va = f_va["Harga_Lag1"].to_numpy()
        else:
            mdl = clone(estimator)
            y_tr_delta = f_tr[TARGET] - f_tr["Harga_Lag1"]
            mdl.fit(f_tr[features], y_tr_delta)
            pred_va = f_va["Harga_Lag1"].to_numpy() + mdl.predict(f_va[features])
        y_val_all.append(f_va[TARGET].to_numpy())
        p_val_all.append(pred_va)

    return compute_metrics(np.concatenate(y_val_all), np.concatenate(p_val_all))


def extract_feature_importance(estimator: object, features: list[str]) -> dict[str, float]:
    """Ekstrak bobot pentingnya fitur ternormalisasi untuk dashboard dan model card."""
    if hasattr(estimator, "feature_importances_"):
        raw = np.asarray(estimator.feature_importances_, dtype=float)
    elif hasattr(estimator, "named_steps") and "ridge" in estimator.named_steps:
        raw = np.abs(np.asarray(estimator.named_steps["ridge"].coef_, dtype=float))
    else:
        return {}

    total = float(raw.sum())
    if total <= 0:
        return {f: 0.0 for f in features}
    norm = raw / total
    paired = sorted(zip(features, norm), key=lambda kv: kv[1], reverse=True)
    return {k: round(float(v), 6) for k, v in paired}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fitur_cfg = json.loads((PROC / "05_fitur_final_uas.json").read_text(encoding="utf-8"))
    feat_linear = list(fitur_cfg["fitur_untuk_model_linear"])
    feat_tree = list(fitur_cfg["fitur_terpilih_tahap4"])

    df_raw, cuaca_df, source_label = load_source_data()
    df_panel = build_leakage_free_features(df_raw, cuaca_df)
    df_trad = (
        df_panel[df_panel["Kategori_Pasar"] == PASAR_FOKUS]
        .sort_values("Tanggal")
        .reset_index(drop=True)
    )

    tr_raw = df_trad[df_trad["Tanggal"] <= SPLIT_DATE].reset_index(drop=True)
    te_raw = df_trad[df_trad["Tanggal"] > SPLIT_DATE].reset_index(drop=True)
    tr_full, te_full, _, _ = apply_smoothed_te(tr_raw, te_raw)
    y_tr_delta = tr_full[TARGET] - tr_full["Harga_Lag1"]

    tscv = TimeSeriesSplit(n_splits=5)
    print(f"[sumber] {source_label}")
    print(
        f"[data]   {PASAR_FOKUS}: total={len(df_trad)} hari | "
        f"train={len(tr_full)} ({tr_full['Tanggal'].min().date()}..{tr_full['Tanggal'].max().date()}) | "
        f"test={len(te_full)} ({te_full['Tanggal'].min().date()}..{te_full['Tanggal'].max().date()})"
    )

    results: list[dict[str, object]] = []
    tuned_specs: dict[str, tuple[object, dict[str, object], list[str]]] = {}
    pred_df = pd.DataFrame({
        "tanggal": te_full["Tanggal"].dt.strftime("%Y-%m-%d"),
        "aktual": te_full[TARGET].to_numpy(dtype=float),
        "harga_lag1": te_full["Harga_Lag1"].to_numpy(dtype=float),
    })

    for spec in build_candidates(feat_linear, feat_tree):
        name = str(spec["name"])
        feats = list(spec["features"])  # type: ignore[arg-type]
        est = spec["estimator"]
        search_type = spec["search_type"]
        param_grid = spec["param_grid"]
        n_iter = int(spec["n_iter"])  # type: ignore[arg-type]

        t0 = time.time()
        if est is None:
            best_est = None
            best_params: dict[str, object] = {}
            pred_test = te_full["Harga_Lag1"].to_numpy(dtype=float)
        else:
            if search_type == "grid":
                search = GridSearchCV(
                    est,
                    param_grid=param_grid,
                    cv=tscv,
                    scoring="neg_mean_absolute_error",
                    n_jobs=1,
                )
            else:
                search = RandomizedSearchCV(
                    est,
                    param_distributions=param_grid,
                    n_iter=n_iter,
                    cv=tscv,
                    random_state=RANDOM_STATE,
                    scoring="neg_mean_absolute_error",
                    n_jobs=1,
                )
            search.fit(tr_full[feats], y_tr_delta)
            best_params = {k: to_python_scalar(v) for k, v in search.best_params_.items()}
            best_est = clone(est).set_params(**search.best_params_)
            best_est.fit(tr_full[feats], y_tr_delta)
            pred_test = te_full["Harga_Lag1"].to_numpy(dtype=float) + best_est.predict(te_full[feats])
            tuned_specs[name] = (clone(est).set_params(**search.best_params_), best_params, feats)

        cv_m = evaluate_cv_folds(tr_raw, tscv, best_est, feats)
        test_m = compute_metrics(te_full[TARGET], pred_test)
        elapsed = round(time.time() - t0, 2)

        pred_col = name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        pred_df[f"pred_{pred_col}"] = np.round(pred_test, 1)

        results.append({
            "model": name,
            "n_fitur": len(feats),
            "best_params": best_params,
            "cv": cv_m,
            "test": test_m,
            "waktu_latih_detik": elapsed,
        })
        print(
            f"[model]  {name:27s} | CV MAE=Rp{cv_m['MAE']:7,.1f} | "
            f"Test MAE=Rp{test_m['MAE']:7,.1f} RMSE=Rp{test_m['RMSE']:7,.1f} "
            f"MAPE={test_m['MAPE']:.2f}% R2={test_m['R2']:.4f} ({elapsed:.1f}s)"
        )

    ml_results = [r for r in results if r["model"] != NAIVE_NAME]
    best_entry = min(ml_results, key=lambda r: float(r["cv"]["MAE"]))  # type: ignore[index]
    best_name = str(best_entry["model"])
    print(f"[pilih]  Model ML terbaik (CV MAE terendah): {best_name}")

    best_pred_col = "pred_" + best_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
    pred_df["prediksi_terbaik"] = pred_df[best_pred_col]
    pred_df["residual"] = np.round(pred_df["aktual"] - pred_df["prediksi_terbaik"], 1)
    pred_df["abs_residual"] = np.round(pred_df["residual"].abs(), 1)
    pred_df["ape_persen"] = np.round(pred_df["abs_residual"] / pred_df["aktual"] * 100.0, 3)

    # Susun 10 residual terbesar beserta konteks fitur cuaca/hulu/kalender untuk error analysis
    err_df = pred_df.copy()
    err_df["akumulasi_hujan_7h"] = np.round(te_full["Akumulasi_Hujan_7H"].to_numpy(dtype=float), 1)
    err_df["harga_produsen_lag1"] = np.round(te_full["Harga_Produsen_Lag1"].to_numpy(dtype=float), 1)
    err_df["harga_pb_lag1"] = np.round(te_full["Harga_PB_Lag1"].to_numpy(dtype=float), 1)
    err_df["hari_menuju_idul_fitri"] = te_full["Hari_Menuju_Idul_Fitri"].to_numpy(dtype=int)
    err_df["is_musim_hujan"] = te_full["Is_Musim_Hujan"].to_numpy(dtype=int)
    top10_err = (
        err_df.sort_values("abs_residual", ascending=False)
        .head(10)[
            [
                "tanggal",
                "harga_lag1",
                "aktual",
                "prediksi_terbaik",
                "residual",
                "abs_residual",
                "ape_persen",
                "akumulasi_hujan_7h",
                "harga_produsen_lag1",
                "harga_pb_lag1",
                "hari_menuju_idul_fitri",
                "is_musim_hujan",
            ]
        ]
        .rename(columns={"prediksi_terbaik": "prediksi"})
        .to_dict(orient="records")
    )

    # Refit model terbaik & baseline Ridge pada seluruh data historis untuk deployment
    full_df, _, te_bulan_full, te_global_full = apply_smoothed_te(df_trad, df_trad)
    y_full_delta = full_df[TARGET] - full_df["Harga_Lag1"]

    best_est_cls, _, best_feats = tuned_specs[best_name]
    final_best = clone(best_est_cls).fit(full_df[best_feats], y_full_delta)

    ridge_est_cls, _, ridge_feats = tuned_specs[BASELINE_NAME]
    final_ridge = clone(ridge_est_cls).fit(full_df[ridge_feats], y_full_delta)

    feat_imp = extract_feature_importance(final_best, best_feats)

    common_meta = {
        "target_mode": "delta",
        "pasar_fokus": PASAR_FOKUS,
        "te_bulan_map": te_bulan_full,
        "te_global_mean": te_global_full,
        "trained_until": str(full_df["Tanggal"].max().date()),
    }
    joblib.dump({"model": final_best, "name": best_name, "features": best_feats, **common_meta}, OUT_DIR / "best_model.joblib")
    joblib.dump({"model": final_ridge, "name": BASELINE_NAME, "features": ridge_feats, **common_meta}, OUT_DIR / "baseline_ridge.joblib")
    pred_df.to_csv(OUT_DIR / "test_predictions.csv", index=False)

    metrics_payload = {
        "best_model": best_name,
        "baseline_model": BASELINE_NAME,
        "naive_model": NAIVE_NAME,
        "pasar_fokus": PASAR_FOKUS,
        "strategi": "Target perubahan harga harian (dy_t = y_t - Harga_Lag1), dikonversi ke Rupiah (Harga_Lag1 + dy_hat)",
        "sumber_data": source_label,
        "split": {
            "train": f"{tr_full['Tanggal'].min().date()} s.d. {tr_full['Tanggal'].max().date()}",
            "test": f"{te_full['Tanggal'].min().date()} s.d. {te_full['Tanggal'].max().date()}",
            "n_train": int(len(tr_full)),
            "n_test": int(len(te_full)),
        },
        "cv": "TimeSeriesSplit(n_splits=5) dengan target encoding di-fit ulang per fold",
        "fitur_pohon": feat_tree,
        "fitur_linear": feat_linear,
        "results": results,
        "feature_importance": feat_imp,
        "residual_terbesar": top10_err,
    }
    (OUT_DIR / "metrics.json").write_text(
        json.dumps(metrics_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        "[simpan] models/best_model.joblib, models/baseline_ridge.joblib, "
        "models/metrics.json, models/test_predictions.csv"
    )


if __name__ == "__main__":
    main()
