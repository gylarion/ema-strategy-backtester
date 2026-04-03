"""
CLI entry point for EMA Strategy Backtester.

Usage:
    python main.py download --timeframe 1m --start 2024-01-01 --end 2024-12-31
    python main.py backtest --timeframe 1m
    python main.py dashboard
"""
import argparse
import os
import sys
from datetime import date, datetime

import numpy as np
import pandas as pd


def cmd_download(args):
    """Download historical kline data from Binance Data Vision."""
    from data.downloader import download_range
    from data.storage import csvs_to_parquet
    from config import SYMBOL

    start = datetime.strptime(args.start, "%Y-%m-%d").date()
    end = datetime.strptime(args.end, "%Y-%m-%d").date()

    print(f"Downloading {SYMBOL} {args.timeframe} data from {start} to {end}...")
    download_range(
        symbol=SYMBOL,
        timeframe=args.timeframe,
        start=start,
        end=end,
        use_monthly=(args.timeframe != "1s"),
    )

    print("Converting to Parquet...")
    csvs_to_parquet(args.timeframe)
    print("Done!")


def cmd_backtest(args):
    """Run grid search backtest."""
    from data.storage import load_parquet
    from config import ParameterGrid, RESULTS_DIR
    from optimizer.grid_search import run_grid_search

    print(f"Loading {args.timeframe} data...")
    df = load_parquet(args.timeframe)
    print(f"Loaded {len(df):,} candles ({df['open_time'].min()} to {df['open_time'].max()})")

    close = df["close"].values.astype(np.float64)
    open_ = df["open"].values.astype(np.float64)
    high = df["high"].values.astype(np.float64)
    low = df["low"].values.astype(np.float64)
    volume = df["volume"].values.astype(np.float64)

    grid = ParameterGrid()

    if args.quick:
        # Quick test: small parameter range
        grid.fast_ema_periods = [5, 10, 20]
        grid.slow_ema_periods = [20, 50, 100]
        grid.stop_loss_pcts = [0.5, 1.0, 2.0]
        grid.take_profit_pcts = [1.0, 2.0, 3.0]
        grid.volume_filter = [False]

    combinations = list(grid.valid_combinations())
    total = len(combinations)
    print(f"Total valid combinations: {total:,}")

    if total > 10_000 and not args.yes:
        response = input(f"This will run {total:,} backtests. Continue? [y/N] ")
        if response.lower() != "y":
            print("Aborted.")
            return

    results = run_grid_search(
        close=close,
        open_=open_,
        high=high,
        low=low,
        volume=volume,
        combinations=combinations,
        timeframe=args.timeframe,
        n_workers=args.workers,
    )

    # Print top results
    _print_top_results(results, n=args.top)


def cmd_dashboard(args):
    """Launch Streamlit dashboard."""
    import subprocess
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard", "app.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path], check=True)


def _print_top_results(results: list[dict], n: int = 20):
    """Print top N results sorted by Sharpe ratio."""
    df = pd.DataFrame(results)

    # Convert types if loaded from CSV
    for col in ["sharpe_ratio", "total_pnl_pct", "max_drawdown_pct", "win_rate",
                 "profit_factor", "calmar_ratio"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df_sorted = df.sort_values("sharpe_ratio", ascending=False).head(n)

    print(f"\n{'='*100}")
    print(f"TOP {n} PARAMETER COMBINATIONS (sorted by Sharpe Ratio)")
    print(f"{'='*100}")

    display_cols = [
        "fast_ema", "slow_ema", "stop_loss_pct", "take_profit_pct",
        "volume_filter", "total_pnl_pct", "sharpe_ratio", "max_drawdown_pct",
        "win_rate", "profit_factor", "total_trades", "calmar_ratio",
    ]
    existing_cols = [c for c in display_cols if c in df_sorted.columns]
    print(df_sorted[existing_cols].to_string(index=False))
    print()


def main():
    parser = argparse.ArgumentParser(description="EMA Strategy Backtester")
    sub = parser.add_subparsers(dest="command", help="Command to run")

    # Download
    dl = sub.add_parser("download", help="Download historical data")
    dl.add_argument("--timeframe", "-t", default="1m", choices=["1s", "1m"])
    dl.add_argument("--start", "-s", default="2024-01-01", help="Start date (YYYY-MM-DD)")
    dl.add_argument("--end", "-e", default="2024-12-31", help="End date (YYYY-MM-DD)")

    # Backtest
    bt = sub.add_parser("backtest", help="Run grid search backtest")
    bt.add_argument("--timeframe", "-t", default="1m", choices=["1s", "1m"])
    bt.add_argument("--workers", "-w", type=int, default=None, help="Number of parallel workers")
    bt.add_argument("--quick", "-q", action="store_true", help="Quick test with small parameter range")
    bt.add_argument("--top", type=int, default=20, help="Show top N results")
    bt.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")

    # Dashboard
    sub.add_parser("dashboard", help="Launch Streamlit dashboard")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    commands = {
        "download": cmd_download,
        "backtest": cmd_backtest,
        "dashboard": cmd_dashboard,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
