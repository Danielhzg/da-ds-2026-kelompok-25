"""Modul Load untuk membangun skema dan memuat data ke SQLite warehouse/cabai_medan.db."""

from pathlib import Path
import sqlite3
import pandas as pd

LOAD_ORDER = ["dim_tanggal", "dim_pasar", "dim_cuaca", "fact_harga_harian"]


def load_warehouse(
    tables: dict[str, pd.DataFrame],
    db_path: Path,
    schema_path: Path,
) -> dict[str, int]:
    """Membangun ulang skema SQLite dari schema.sql dan memuat seluruh tabel fakta & dimensi."""
    if not schema_path.exists():
        raise FileNotFoundError(f"File skema DDL tidak ditemukan: {schema_path}")

    db_path.parent.mkdir(parents=True, exist_ok=True)
    ddl_sql = schema_path.read_text(encoding="utf-8")

    counts: dict[str, int] = {}
    with sqlite3.connect(db_path) as conn:
        conn.executescript(ddl_sql)
        conn.execute("PRAGMA foreign_keys = ON;")

        for table_name in LOAD_ORDER:
            df = tables[table_name]
            df.to_sql(table_name, conn, if_exists="append", index=False)
            jumlah = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            counts[table_name] = int(jumlah)

        jumlah_view = conn.execute("SELECT COUNT(*) FROM v_harga_lengkap").fetchone()[0]
        counts["v_harga_lengkap"] = int(jumlah_view)

    return counts
