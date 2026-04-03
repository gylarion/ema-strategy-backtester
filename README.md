# EMA Strategy Backtester

A high-performance backtesting engine for **EMA Crossover** trading strategy on BTC Futures (Binance). Runs exhaustive grid search across all parameter combinations on 1-minute and 1-second candlestick data, with an interactive Streamlit dashboard for analysis.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

- **Automated data download** from [Binance Data Vision](https://data.binance.vision/) (free historical futures data)
- **Vectorized EMA calculation** with caching — computes each unique period only once
- **Full grid search** across all parameter combinations (EMA periods, Stop Loss, Take Profit, volume filter)
- **Backtest engine** with Stop Loss / Take Profit exits, commission handling
- **Interactive Streamlit dashboard** — no console needed:
  - Download data, run backtests, analyze results — all via web UI
  - Heatmaps, equity curves, drawdown charts, scatter plots
  - Bilingual interface (English / Ukrainian)
- **Checkpoint system** — pause and resume long-running optimizations
- **Parquet storage** — 10x compression vs CSV, fast I/O

## Strategy: EMA Crossover

| Signal | Condition |
|--------|-----------|
| **Long** | Fast EMA crosses above Slow EMA |
| **Short** | Fast EMA crosses below Slow EMA |
| **Exit** | Stop Loss, Take Profit, or reverse signal |

### Optimized Parameters

| Parameter | Default Range | Step |
|-----------|--------------|------|
| Fast EMA period | 3–50 | 1 |
| Slow EMA period | 10–200 | 5 |
| Stop Loss % | 0.3–3.0 | 0.1 |
| Take Profit % | 0.5–5.0 | 0.25 |
| Volume filter | On / Off | — |

> Constraint: fast EMA < slow EMA (invalid pairs are skipped automatically)

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Launch the dashboard

```bash
python run.py
```

Or directly:

```bash
streamlit run dashboard/app.py
```

### 3. Use the web interface

1. **Download Data** — select timeframe and date range, click download
2. **Run Backtest** — configure parameter ranges, launch grid search
3. **Analysis** — explore results with interactive charts

## CLI Usage (alternative)

```bash
# Download 1-minute data for 2024
python main.py download --timeframe 1m --start 2024-01-01 --end 2024-12-31

# Run full grid search
python main.py backtest --timeframe 1m

# Quick test (72 combinations)
python main.py backtest --timeframe 1m --quick

# Open dashboard
python main.py dashboard
```

## Project Structure

```
├── config.py              # Parameters, ranges, constants
├── main.py                # CLI entry point
├── run.py                 # One-click dashboard launcher
├── requirements.txt
├── data/
│   ├── downloader.py      # Binance Data Vision downloader
│   └── storage.py         # Parquet storage layer
├── strategy/
│   ├── indicators.py      # Vectorized EMA with caching
│   └── signals.py         # Crossover signals + volume filter
├── backtest/
│   ├── engine.py          # Backtest engine with SL/TP
│   └── metrics.py         # Sharpe, Drawdown, Win Rate, Calmar...
├── optimizer/
│   └── grid_search.py     # Multiprocessing grid search
└── dashboard/
    ├── app.py             # Streamlit dashboard (full UI)
    └── i18n.py            # English / Ukrainian translations
```

## Performance Metrics

| Metric | Description |
|--------|-------------|
| Total PnL % | Overall profit/loss percentage |
| Sharpe Ratio | Risk-adjusted return (annualized). >1 good, >2 excellent |
| Max Drawdown % | Largest peak-to-trough decline |
| Win Rate % | Percentage of profitable trades |
| Profit Factor | Gross profit / gross loss |
| Calmar Ratio | Return / max drawdown |

## Dashboard Screenshots

The dashboard includes:
- **EMA Heatmap** — best metric for each fast/slow EMA pair
- **SL/TP Heatmap** — optimal risk/reward combinations
- **Equity Curve** — capital growth over time for selected parameters
- **Drawdown Chart** — visualize risk periods
- **Risk vs Return Scatter** — all combinations at a glance
- **Parameter Impact** — which values work best

## Technical Notes

- **Data volume**: 1-minute data for 1 year ≈ 525K candles (~40MB Parquet). 1-second ≈ 31.5M candles (~600MB).
- **EMA caching**: Only ~87 unique EMA calculations instead of millions (48 fast periods + 39 slow periods).
- **Grid search**: ~1.8M valid combinations at default ranges. Supports multiprocessing for CLI mode.
- **Commission**: 0.04% per trade (Binance Futures average).

## License

MIT
