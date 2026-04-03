"""
Signal generation for EMA Crossover strategy.

Signal rules:
  - Long  (+1): fast EMA crosses above slow EMA
  - Short (-1): fast EMA crosses below slow EMA
  - Flat   (0): no position change

Optional volume filter: only take signals when volume > rolling average volume.
"""
import numpy as np


def crossover_signals(fast_ema: np.ndarray, slow_ema: np.ndarray) -> np.ndarray:
    """
    Generate raw crossover signals (vectorized).

    Returns array of:
      +1 = long entry (fast crossed above slow)
      -1 = short entry (fast crossed below slow)
       0 = no signal
    """
    # Position: +1 when fast > slow, -1 when fast < slow
    position = np.where(fast_ema > slow_ema, 1, -1)

    # Signal fires only when position changes
    signals = np.zeros(len(position), dtype=np.int8)
    changes = np.diff(position)
    # +2 means went from -1 to +1 (long signal)
    # -2 means went from +1 to -1 (short signal)
    signals[1:] = np.where(changes > 0, 1, np.where(changes < 0, -1, 0))

    return signals


def apply_volume_filter(
    signals: np.ndarray,
    volume: np.ndarray,
    lookback: int = 20,
) -> np.ndarray:
    """
    Zero out signals where current volume < rolling average volume.
    High volume confirms the crossover move.
    """
    if lookback >= len(volume):
        return signals

    # Rolling mean of volume
    cumsum = np.cumsum(volume)
    rolling_avg = np.empty_like(volume)
    rolling_avg[:lookback] = cumsum[lookback - 1] / lookback
    rolling_avg[lookback:] = (cumsum[lookback:] - cumsum[:-lookback]) / lookback

    filtered = signals.copy()
    low_volume = volume < rolling_avg
    filtered[low_volume] = 0

    return filtered
