"""
Performance metrics for backtest results.
"""
import numpy as np
from dataclasses import dataclass


@dataclass
class PerformanceMetrics:
    """All key performance indicators for a backtest run."""
    total_pnl: float
    total_pnl_pct: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_pct: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_trade_pnl: float
    avg_trade_duration_bars: float
    calmar_ratio: float
    avg_win: float
    avg_loss: float
    max_consecutive_losses: int


def compute_metrics(
    pnl_per_trade: np.ndarray,
    equity_curve: np.ndarray,
    trades: np.ndarray,
    initial_capital: float = 10_000.0,
    bars_per_year: int = 525_600,  # 1-minute bars in a year
) -> PerformanceMetrics:
    """Compute all performance metrics from backtest results."""
    total_trades = len(pnl_per_trade)

    if total_trades == 0:
        return PerformanceMetrics(
            total_pnl=0.0, total_pnl_pct=0.0, sharpe_ratio=0.0,
            max_drawdown=0.0, max_drawdown_pct=0.0, win_rate=0.0,
            profit_factor=0.0, total_trades=0, avg_trade_pnl=0.0,
            avg_trade_duration_bars=0.0, calmar_ratio=0.0,
            avg_win=0.0, avg_loss=0.0, max_consecutive_losses=0,
        )

    # Total PnL
    total_pnl = equity_curve[-1] - initial_capital
    total_pnl_pct = (total_pnl / initial_capital) * 100.0

    # Win rate
    wins = pnl_per_trade[pnl_per_trade > 0]
    losses = pnl_per_trade[pnl_per_trade <= 0]
    win_rate = len(wins) / total_trades * 100.0 if total_trades > 0 else 0.0

    # Avg win / avg loss
    avg_win = float(np.mean(wins)) if len(wins) > 0 else 0.0
    avg_loss = float(np.mean(losses)) if len(losses) > 0 else 0.0

    # Profit factor
    gross_profit = float(np.sum(wins)) if len(wins) > 0 else 0.0
    gross_loss = float(np.abs(np.sum(losses))) if len(losses) > 0 else 0.0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

    # Sharpe ratio (annualized, based on per-trade returns)
    trade_returns = pnl_per_trade / initial_capital
    if len(trade_returns) > 1 and np.std(trade_returns) > 0:
        avg_bars_per_trade = np.mean(trades[:, 1] - trades[:, 0]) if len(trades) > 0 else 1
        trades_per_year = bars_per_year / max(avg_bars_per_trade, 1)
        sharpe_ratio = (np.mean(trade_returns) / np.std(trade_returns)) * np.sqrt(trades_per_year)
    else:
        sharpe_ratio = 0.0

    # Max drawdown
    running_max = np.maximum.accumulate(equity_curve)
    drawdown = running_max - equity_curve
    max_drawdown = float(np.max(drawdown))
    max_drawdown_pct = float(np.max(drawdown / running_max)) * 100.0 if np.max(running_max) > 0 else 0.0

    # Calmar ratio
    calmar_ratio = (total_pnl_pct / max_drawdown_pct) if max_drawdown_pct > 0 else 0.0

    # Average trade PnL
    avg_trade_pnl = float(np.mean(pnl_per_trade))

    # Average trade duration (in bars)
    avg_trade_duration = float(np.mean(trades[:, 1] - trades[:, 0])) if len(trades) > 0 else 0.0

    # Max consecutive losses
    max_consec_losses = _max_consecutive_losses(pnl_per_trade)

    return PerformanceMetrics(
        total_pnl=round(total_pnl, 2),
        total_pnl_pct=round(total_pnl_pct, 2),
        sharpe_ratio=round(float(sharpe_ratio), 4),
        max_drawdown=round(max_drawdown, 2),
        max_drawdown_pct=round(max_drawdown_pct, 2),
        win_rate=round(win_rate, 2),
        profit_factor=round(profit_factor, 4),
        total_trades=total_trades,
        avg_trade_pnl=round(avg_trade_pnl, 2),
        avg_trade_duration_bars=round(avg_trade_duration, 1),
        calmar_ratio=round(calmar_ratio, 4),
        avg_win=round(avg_win, 2),
        avg_loss=round(avg_loss, 2),
        max_consecutive_losses=max_consec_losses,
    )


def _max_consecutive_losses(pnl: np.ndarray) -> int:
    """Count the longest streak of consecutive losing trades."""
    if len(pnl) == 0:
        return 0
    is_loss = (pnl <= 0).astype(int)
    max_streak = 0
    current = 0
    for val in is_loss:
        if val == 1:
            current += 1
            max_streak = max(max_streak, current)
        else:
            current = 0
    return max_streak
