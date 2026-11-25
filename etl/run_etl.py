"""Entrypoint pipeline ETL otomatis dari data/raw/ ke warehouse/cabai_medan.db."""

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from etl.extract import extract_all
from etl.transform import transform_data
from etl.load import load_warehouse


def main() -> None:
    """Menjalankan pipeline Extract -> Transform -> Load secara penuh."""
    raw_dir = ROOT_DIR / "data" / "raw"
    schema_path = ROOT_DIR / "warehouse" / "schema.sql"
    db_path = ROOT_DIR / "warehouse" / "cabai_medan.db"

    print("[1/3] Extract: membaca data mentah PIHPS & Open-Meteo dari data/raw/...")
    df_pihps_raw, df_cuaca_raw = extract_all(raw_dir)
    print(f"      -> PIHPS mentah: {len(df_pihps_raw):,} baris | Cuaca mentah: {len(df_cuaca_raw):,} baris")

    print("[2/3] Transform: membersihkan data, imputasi forward-fill, & membentuk skema bintang...")
    tables = transform_data(df_pihps_raw, df_cuaca_raw)

    print("[3/3] Load: membangun skema dan memuat data ke warehouse/cabai_medan.db...")
    counts = load_warehouse(tables, db_path=db_path, schema_path=schema_path)

    print("\nPipeline ETL selesai tanpa error! Ringkasan baris di warehouse/cabai_medan.db:")
    for nama, jumlah in counts.items():
        print(f"  - {nama:<20}: {jumlah:,} baris")


if __name__ == "__main__":
    main()
