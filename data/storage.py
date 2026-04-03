"""
Parquet storage layer for kline data.

Converts raw CSVs to a single Parquet file per timeframe for fast I/O.
"""
import os
from pathlib import Path

import pandas as pd

from config import DATA_DIR, PARQUET_DIR
from data.downloader import load_csv, KLINE_COLUMNS


def csvs_to_parquet(timeframe: str, csv_dir: str | None = None, out_dir: str | None = None) -> Path:
    """
    Merge all daily/monthly CSVs for a timeframe into one sorted Parquet file.
    Returns the path to the Parquet file.
    """
    if csv_dir is None:
        csv_dir = os.path.join(DATA_DIR, timeframe)
    if out_dir is None:
        out_dir = PARQUET_DIR
    os.makedirs(out_dir, exist_ok=True)

    csv_files = sorted(Path(csv_dir).glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {csv_dir}")

    frames = []
    for f in csv_files:
        frames.append(load_csv(f))

    df = pd.concat(frames, ignore_index=True)
    df.sort_values("open_time", inplace=True)
    df.drop_duplicates(subset=["open_time"], keep="first", inplace=True)
    df.reset_index(drop=True, inplace=True)

    parquet_path = Path(out_dir) / f"klines_{timeframe}.parquet"
    df.to_parquet(parquet_path, index=False, engine="pyarrow")
    print(f"Saved {len(df):,} rows to {parquet_path}")
    return parquet_path


def load_parquet(timeframe: str, parquet_dir: str | None = None) -> pd.DataFrame:
    """Load kline Parquet file into DataFrame."""
    if parquet_dir is None:
        parquet_dir = PARQUET_DIR
    path = Path(parquet_dir) / f"klines_{timeframe}.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"Parquet file not found: {path}. Run 'python main.py download' first."
        )
    df = pd.read_parquet(path, engine="pyarrow")
    return df
