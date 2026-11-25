"""Modul Extract untuk mengambil data mentah PIHPS dan cuaca Open-Meteo."""

from pathlib import Path
import pandas as pd

PIHPS_FILES = {
    "Produsen": "Tabel Harga cabe produsen 10 tahun.xlsx",
    "Pedagang Besar": "Tabel Harga cabe pedagang besar 10 tahun .xlsx",
    "Pasar Tradisional": "Tabel harga cabe pedagang tradisional 10 tahun .xlsx",
    "Pasar Modern": "tabel cabe pasar modern 10n tahun.xlsx",
}

WEATHER_FILE = "open-meteo-3.55N98.68E28m (1).csv"


def extract_pihps(raw_dir: Path) -> pd.DataFrame:
    """Membaca 4 file Excel PIHPS Bank Indonesia dan mengubahnya ke format long."""
    bagian = []
    for kategori_pasar, nama_file in PIHPS_FILES.items():
        path_file = raw_dir / nama_file
        if not path_file.exists():
            raise FileNotFoundError(f"File PIHPS tidak ditemukan: {path_file}")

        df_raw = pd.read_excel(path_file, header=None, dtype=str)
        header_tanggal = df_raw.iloc[0, 2:].values
        part = pd.DataFrame(
            {
                "Tanggal_teks": header_tanggal,
                "Kategori_Pasar": kategori_pasar,
                "Komoditas_teks": df_raw.iloc[2, 1],
                "Harga_Keriting_teks": df_raw.iloc[2, 2:].values,
                "Harga_Agregat_teks": df_raw.iloc[1, 2:].values,
            }
        )
        bagian.append(part)

    return pd.concat(bagian, ignore_index=True)


def extract_cuaca(raw_dir: Path) -> pd.DataFrame:
    """Membaca data cuaca harian Kota Medan dari CSV Open-Meteo."""
    path_cuaca = raw_dir / WEATHER_FILE
    if not path_cuaca.exists():
        raise FileNotFoundError(f"File cuaca Open-Meteo tidak ditemukan: {path_cuaca}")

    return pd.read_csv(path_cuaca, skiprows=3)


def extract_all(raw_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Menjalankan ekstraksi seluruh sumber data mentah dari data/raw/."""
    df_pihps = extract_pihps(raw_dir)
    df_cuaca = extract_cuaca(raw_dir)
    return df_pihps, df_cuaca
