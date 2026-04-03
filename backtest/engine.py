"""
Vectorized backtest engine for EMA Crossover strategy.

Handles:
  - Position tracking based on crossover signals
  - Stop-loss and take-profit exits (checked against candle high/low)
  - Commission calculation (per-trade)
  - Equity curve generation
"""
import numpy as np
from dataclasses import dataclass


@dataclass
class BacktestResult:
    """Container for a single backtest run result."""
    # Parameters
    fast_ema: int
    slow_ema: int
    stop_loss_pct: float
    take_profit_pct: float
    volume_filter: bool

    # Trade-level data
    trades: np.ndarray          # Nx5: [entry_idx, exit_idx, direction, entry_price, exit_price]
    pnl_per_trade: np.ndarray   # PnL for each trade (after commission)

    # Equity curve
    equity_curve: np.ndarray    # Equity value at each bar


def run_backtest(
    open_prices: np.ndarray,
    high_prices: np.ndarray,
    low_prices: np.ndarray,
    close_prices: np.ndarray,
    signals: np.ndarray,
    stop_loss_pct: float,
    take_profit_pct: float,
    commission_pct: float = 0.04,
    initial_capital: float = 10_000.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Run backtest with SL/TP exits.

    Since SL/TP requires checking each bar's high/low against entry price,
    this uses an optimized loop (unavoidable for path-dependent SL/TP logic).

    Returns:
        trades: Nx5 array [entry_idx, exit_idx, direction, entry_price, exit_price]
        pnl_per_trade: PnL array for each closed trade
        equity_curve: equity at each bar
    """
    n = len(close_prices)
    sl_mult = stop_loss_pct / 100.0
    tp_mult = take_profit_pct / 100.0
    comm_mult = commission_pct / 100.0

    equity_curve = np.full(n, initial_capital, dtype=np.float64)
    trades_list = []
    pnl_list = []

    position = 0        # +1 long, -1 short, 0 flat
    entry_price = 0.0
    entry_idx = 0
    equity = initial_capital

    for i in range(1, n):
        if position != 0:
            # Check SL/TP
            if position == 1:  # Long
                sl_price = entry_price * (1.0 - sl_mult)
                tp_price = entry_price * (1.0 + tp_mult)
                # SL hit? (low went below stop)
                if low_prices[i] <= sl_price:
                    exit_price = sl_price
                    pnl = (exit_price / entry_price - 1.0) * equity - 2 * comm_mult * equity
                    equity += pnl
                    trades_list.append([entry_idx, i, 1, entry_price, exit_price])
                    pnl_list.append(pnl)
                    position = 0
                # TP hit?
                elif high_prices[i] >= tp_price:
                    exit_price = tp_price
                    pnl = (exit_price / entry_price - 1.0) * equity - 2 * comm_mult * equity
                    equity += pnl
                    trades_list.append([entry_idx, i, 1, entry_price, exit_price])
                    pnl_list.append(pnl)
                    position = 0
            else:  # Short
                sl_price = entry_price * (1.0 + sl_mult)
                tp_price = entry_price * (1.0 - tp_mult)
                # SL hit? (high went above stop)
                if high_prices[i] >= sl_price:
                    exit_price = sl_price
                    pnl = (1.0 - exit_price / entry_price) * equity - 2 * comm_mult * equity
                    equity += pnl
                    trades_list.append([entry_idx, i, -1, entry_price, exit_price])
                    pnl_list.append(pnl)
                    position = 0
                # TP hit?
                elif low_prices[i] <= tp_price:
                    exit_price = tp_price
                    pnl = (1.0 - exit_price / entry_price) * equity - 2 * comm_mult * equity
                    equity += pnl
                    trades_list.append([entry_idx, i, -1, entry_price, exit_price])
                    pnl_list.append(pnl)
                    position = 0

        # Check for new signal (only if flat after SL/TP check, or reversing)
        if signals[i] != 0:
            if position != 0 and position != signals[i]:
                # Close existing position on reverse signal
                exit_price = close_prices[i]
                if position == 1:
                    pnl = (exit_price / entry_price - 1.0) * equity - 2 * comm_mult * equity
                else:
                    pnl = (1.0 - exit_price / entry_price) * equity - 2 * comm_mult * equity
                equity += pnl
                trades_list.append([entry_idx, i, position, entry_price, exit_price])
                pnl_list.append(pnl)
                position = 0

            if position == 0:
                # Open new position
                position = signals[i]
                entry_price = close_prices[i]
                entry_idx = i

        equity_curve[i] = equity

    # Close any open position at the end
    if position != 0:
        exit_price = close_prices[-1]
        if position == 1:
            pnl = (exit_price / entry_price - 1.0) * equity - 2 * comm_mult * equity
        else:
            pnl = (1.0 - exit_price / entry_price) * equity - 2 * comm_mult * equity
        equity += pnl
        trades_list.append([entry_idx, n - 1, position, entry_price, exit_price])
        pnl_list.append(pnl)
        equity_curve[-1] = equity

    trades = np.array(trades_list, dtype=np.float64) if trades_list else np.empty((0, 5))
    pnl_per_trade = np.array(pnl_list, dtype=np.float64) if pnl_list else np.empty(0)

    return trades, pnl_per_trade, equity_curve
