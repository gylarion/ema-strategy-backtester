"""
Grid search optimizer with multiprocessing.

Runs all valid parameter combinations in parallel and collects results.
Supports checkpointing (save/resume) for long-running optimizations.
"""
import csv
import os
import time
from dataclasses import asdict
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np
from tqdm import tqdm

from backtest.engine import run_backtest
from backtest.metrics import compute_metrics, PerformanceMetrics
from config import COMMISSION_PCT, INITIAL_CAPITAL, RESULTS_DIR
from strategy.indicators import EMACache
from strategy.signals import crossover_signals, apply_volume_filter


# Module-level data arrays (shared across worker processes via fork/spawn)
_close: np.ndarray | None = None
_open: np.ndarray | None = None
_high: np.ndarray | None = None
_low: np.ndarray | None = None
_volume: np.ndarray | None = None
_ema_cache_data: dict[int, np.ndarray] | None = None
_bars_per_year: int = 525_600


def _init_worker(close, open_, high, low, volume, ema_cache_data, bars_per_year):
    """Initialize worker process with shared data."""
    global _close, _open, _high, _low, _volume, _ema_cache_data, _bars_per_year
    _close = close
    _open = open_
    _high = high
    _low = low
    _volume = volume
    _ema_cache_data = ema_cache_data
    _bars_per_year = bars_per_year


def _run_single_combination(params: tuple) -> dict:
    """Run backtest for a single parameter combination. Called in worker process."""
    fast_period, slow_period, sl_pct, tp_pct, vol_filter = params

    fast_ema = _ema_cache_data[fast_period]
    slow_ema = _ema_cache_data[slow_period]

    signals = crossover_signals(fast_ema, slow_ema)

    if vol_filter:
        signals = apply_volume_filter(signals, _volume)

    trades, pnl_per_trade, equity_curve = run_backtest(
        open_prices=_open,
        high_prices=_high,
        low_prices=_low,
        close_prices=_close,
        signals=signals,
        stop_loss_pct=sl_pct,
        take_profit_pct=tp_pct,
        commission_pct=COMMISSION_PCT,
        initial_capital=INITIAL_CAPITAL,
    )

    metrics = compute_metrics(
        pnl_per_trade=pnl_per_trade,
        equity_curve=equity_curve,
        trades=trades,
        initial_capital=INITIAL_CAPITAL,
        bars_per_year=_bars_per_year,
    )

    return {
        "fast_ema": fast_period,
        "slow_ema": slow_period,
        "stop_loss_pct": sl_pct,
        "take_profit_pct": tp_pct,
        "volume_filter": vol_filter,
        **asdict(metrics),
    }


def run_grid_search(
    close: np.ndarray,
    open_: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    volume: np.ndarray,
    combinations: list[tuple],
    timeframe: str = "1m",
    n_workers: int | None = None,
    checkpoint_every: int = 1000,
) -> list[dict]:
    """
    Run grid search across all parameter combinations.

    Args:
        close/open_/high/low/volume: Price data arrays
        combinations: List of (fast, slow, sl, tp, vol_filter) tuples
        timeframe: For determining bars_per_year
        n_workers: Number of parallel workers (default: cpu_count - 1)
        checkpoint_every: Save intermediate results every N combinations

    Returns:
        List of result dicts with parameters + metrics
    """
    if n_workers is None:
        n_workers = max(1, cpu_count() - 1)

    bars_per_year = 31_536_000 if timeframe == "1s" else 525_600

    # Pre-compute all unique EMA periods
    all_periods = set()
    for fast, slow, _, _, _ in combinations:
        all_periods.add(fast)
        all_periods.add(slow)

    print(f"Pre-computing {len(all_periods)} unique EMA values...")
    cache = EMACache(close)
    cache.precompute(list(all_periods))
    ema_data = cache._cache

    print(f"Running {len(combinations):,} combinations on {n_workers} workers...")

    os.makedirs(RESULTS_DIR, exist_ok=True)
    results_path = Path(RESULTS_DIR) / f"grid_results_{timeframe}.csv"

    # Load existing checkpoint if available
    completed_keys = set()
    existing_results = []
    if results_path.exists():
        with open(results_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (
                    int(row["fast_ema"]), int(row["slow_ema"]),
                    float(row["stop_loss_pct"]), float(row["take_profit_pct"]),
                    row["volume_filter"] == "True",
                )
                completed_keys.add(key)
                existing_results.append(row)
        print(f"Resuming from checkpoint: {len(completed_keys):,} already completed")

    remaining = [c for c in combinations if c not in completed_keys]
    if not remaining:
        print("All combinations already computed!")
        return existing_results

    all_results = list(existing_results)
    start_time = time.time()

    with Pool(
        processes=n_workers,
        initializer=_init_worker,
        initargs=(close, open_, high, low, volume, ema_data, bars_per_year),
    ) as pool:
        results_iter = pool.imap_unordered(_run_single_combination, remaining, chunksize=50)

        batch = []
        for i, result in enumerate(tqdm(results_iter, total=len(remaining), desc="Grid search")):
            all_results.append(result)
            batch.append(result)

            if len(batch) >= checkpoint_every:
                _append_results_csv(results_path, batch)
                batch = []

        # Flush remaining
        if batch:
            _append_results_csv(results_path, batch)

    elapsed = time.time() - start_time
    print(f"\nCompleted {len(remaining):,} combinations in {elapsed:.1f}s "
          f"({len(remaining) / elapsed:.0f} combos/sec)")
    print(f"Results saved to: {results_path}")

    return all_results


def _append_results_csv(path: Path, results: list[dict]) -> None:
    """Append batch of results to CSV file."""
    write_header = not path.exists() or path.stat().st_size == 0
    with open(path, "a", newline="") as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            if write_header:
                writer.writeheader()
            writer.writerows(results)
