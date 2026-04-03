"""
Configuration for EMA Strategy Backtester.
All parameter ranges and constants are defined here.
"""
from dataclasses import dataclass, field
from typing import List
import numpy as np


# ── Trading pair ──────────────────────────────────────────────
SYMBOL = "BTCUSDT"
ASSET_TYPE = "um"  # USD-M futures on Binance Data Vision

# ── Data paths ────────────────────────────────────────────────
DATA_DIR = "data/raw"
PARQUET_DIR = "data/parquet"
RESULTS_DIR = "results"

# ── Commission (Binance Futures) ──────────────────────────────
COMMISSION_PCT = 0.04  # 0.04% per side (maker/taker avg)

# ── Default backtest capital ──────────────────────────────────
INITIAL_CAPITAL = 10_000.0  # USD


@dataclass
class ParameterGrid:
    """Defines ranges for grid search optimization."""

    fast_ema_periods: List[int] = field(
        default_factory=lambda: list(range(3, 51))          # 3..50, step 1
    )
    slow_ema_periods: List[int] = field(
        default_factory=lambda: list(range(10, 201, 5))     # 10..200, step 5
    )
    stop_loss_pcts: List[float] = field(
        default_factory=lambda: list(np.round(np.arange(0.3, 3.05, 0.1), 2))
    )
    take_profit_pcts: List[float] = field(
        default_factory=lambda: list(np.round(np.arange(0.5, 5.05, 0.25), 2))
    )
    volume_filter: List[bool] = field(
        default_factory=lambda: [False, True]
    )

    def valid_combinations(self):
        """Yield only valid (fast < slow) parameter tuples."""
        count = 0
        for fast in self.fast_ema_periods:
            for slow in self.slow_ema_periods:
                if fast >= slow:
                    continue
                for sl in self.stop_loss_pcts:
                    for tp in self.take_profit_pcts:
                        for vf in self.volume_filter:
                            yield (fast, slow, sl, tp, vf)
                            count += 1

    def total_valid(self) -> int:
        """Count valid combinations without generating them all."""
        total = 0
        for fast in self.fast_ema_periods:
            valid_slow = sum(1 for s in self.slow_ema_periods if s > fast)
            total += valid_slow
        return total * len(self.stop_loss_pcts) * len(self.take_profit_pcts) * len(self.volume_filter)


# ── Timeframes supported ──────────────────────────────────────
VALID_TIMEFRAMES = ("1s", "1m")

# ── Binance Data Vision base URL ──────────────────────────────
BINANCE_DATA_VISION_BASE = "https://data.binance.vision/data/futures"
