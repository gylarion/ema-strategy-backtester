"""
Download historical kline data from Binance Data Vision.

Binance Data Vision provides bulk CSV downloads for futures klines:
  https://data.binance.vision/data/futures/um/daily/klines/BTCUSDT/1s/
  https://data.binance.vision/data/futures/um/daily/klines/BTCUSDT/1m/

Each daily ZIP contains a CSV with columns:
  open_time, open, high, low, close, volume, close_time,
  quote_volume, count, taker_buy_volume, taker_buy_quote_volume, ignore
"""
import io
import os
import zipfile
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm

from config import BINANCE_DATA_VISION_BASE, SYMBOL, ASSET_TYPE, DATA_DIR

KLINE_COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_volume", "count",
    "taker_buy_volume", "taker_buy_quote_volume", "ignore",
]


def _daily_url(symbol: str, timeframe: str, day: date) -> str:
    """Build URL for a single daily klines ZIP on Binance Data Vision."""
    date_str = day.strftime("%Y-%m-%d")
    return (
        f"{BINANCE_DATA_VISION_BASE}/{ASSET_TYPE}/daily/klines/"
        f"{symbol}/{timeframe}/{symbol}-{timeframe}-{date_str}.zip"
    )


def _monthly_url(symbol: str, timeframe: str, year: int, month: int) -> str:
    """Build URL for a monthly klines ZIP on Binance Data Vision."""
    return (
        f"{BINANCE_DATA_VISION_BASE}/{ASSET_TYPE}/monthly/klines/"
        f"{symbol}/{timeframe}/{symbol}-{timeframe}-{year}-{month:02d}.zip"
    )


def download_day(symbol: str, timeframe: str, day: date, out_dir: str) -> Path | None:
    """Download one daily klines ZIP and extract CSV. Returns CSV path or None."""
    url = _daily_url(symbol, timeframe, day)
    csv_name = f"{symbol}-{timeframe}-{day.strftime('%Y-%m-%d')}.csv"
    csv_path = Path(out_dir) / csv_name

    if csv_path.exists():
        return csv_path

    resp = requests.get(url, timeout=30)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        names = zf.namelist()
        csv_in_zip = [n for n in names if n.endswith(".csv")][0]
        zf.extract(csv_in_zip, out_dir)
        extracted = Path(out_dir) / csv_in_zip
        if extracted != csv_path:
            extracted.rename(csv_path)

    return csv_path


def download_month(symbol: str, timeframe: str, year: int, month: int, out_dir: str) -> Path | None:
    """Download one monthly klines ZIP and extract CSV."""
    url = _monthly_url(symbol, timeframe, year, month)
    csv_name = f"{symbol}-{timeframe}-{year}-{month:02d}.csv"
    csv_path = Path(out_dir) / csv_name

    if csv_path.exists():
        return csv_path

    resp = requests.get(url, timeout=60)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        names = zf.namelist()
        csv_in_zip = [n for n in names if n.endswith(".csv")][0]
        zf.extract(csv_in_zip, out_dir)
        extracted = Path(out_dir) / csv_in_zip
        if extracted != csv_path:
            extracted.rename(csv_path)

    return csv_path


def download_range(
    symbol: str,
    timeframe: str,
    start: date,
    end: date,
    out_dir: str | None = None,
    use_monthly: bool = True,
) -> list[Path]:
    """
    Download kline data for a date range.

    For 1m data, monthly files are preferred (fewer requests).
    For 1s data, only daily files are available on Data Vision.
    """
    if out_dir is None:
        out_dir = os.path.join(DATA_DIR, timeframe)
    os.makedirs(out_dir, exist_ok=True)

    downloaded: list[Path] = []

    if use_monthly and timeframe != "1s":
        # Download full months, then remaining days
        current = start.replace(day=1)
        while current <= end:
            year, month = current.year, current.month
            month_end = (current.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

            if current.day == 1 and month_end <= end:
                path = download_month(symbol, timeframe, year, month, out_dir)
                if path:
                    downloaded.append(path)
                    print(f"  Downloaded monthly: {path.name}")
                current = month_end + timedelta(days=1)
            else:
                # Download remaining days individually
                day = current
                day_end = min(month_end, end)
                while day <= day_end:
                    path = download_day(symbol, timeframe, day, out_dir)
                    if path:
                        downloaded.append(path)
                    day += timedelta(days=1)
                current = day_end + timedelta(days=1)
    else:
        # Daily download (required for 1s)
        total_days = (end - start).days + 1
        for i in tqdm(range(total_days), desc=f"Downloading {timeframe}"):
            day = start + timedelta(days=i)
            path = download_day(symbol, timeframe, day, out_dir)
            if path:
                downloaded.append(path)

    print(f"Downloaded {len(downloaded)} files for {symbol} {timeframe}")
    return downloaded


def load_csv(path: Path) -> pd.DataFrame:
    """Load a single klines CSV into a DataFrame.

    Handles both header and headerless CSVs from Binance Data Vision
    (monthly files have headers, daily files may not).
    """
    # Peek at the first field to detect a header row
    with open(path, "r") as f:
        first_char = f.read(20)
    has_header = first_char.startswith("open_time")

    if has_header:
        df = pd.read_csv(path, header=0)
        df.columns = KLINE_COLUMNS[: len(df.columns)]
    else:
        df = pd.read_csv(path, header=None, names=KLINE_COLUMNS)

    # Drop any rows where open_time is not numeric (extra header rows)
    df = df[pd.to_numeric(df["open_time"], errors="coerce").notna()].copy()

    df["open_time"] = pd.to_datetime(df["open_time"].astype(float).astype(int), unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"].astype(float).astype(int), unit="ms")
    for col in ["open", "high", "low", "close", "volume", "quote_volume",
                 "taker_buy_volume", "taker_buy_quote_volume"]:
        df[col] = df[col].astype(float)
    df["count"] = df["count"].astype(int)
    return df
