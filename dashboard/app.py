"""
Full-featured Streamlit dashboard for EMA Strategy Backtester.

Covers the entire workflow via web UI:
  1. Data Download — choose dates, timeframe, download from Binance
  2. Backtest — configure parameters, launch grid search
  3. Analysis — tables, heatmaps, charts, equity curves

Supports English and Ukrainian.

Launch:  streamlit run dashboard/app.py
    or:  python run.py
"""
import os
import sys
import time
from datetime import date
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add project root to path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from config import (
    SYMBOL, COMMISSION_PCT, INITIAL_CAPITAL,
    RESULTS_DIR, PARQUET_DIR, ParameterGrid, VALID_TIMEFRAMES,
)
from data.downloader import download_range
from data.storage import csvs_to_parquet, load_parquet
from strategy.indicators import EMACache
from strategy.signals import crossover_signals, apply_volume_filter
from backtest.engine import run_backtest
from backtest.metrics import compute_metrics
from dashboard.i18n import t

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="EMA Strategy Backtester",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Language Selector ─────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "ua"

lang_options = {"English": "en", "Українська": "ua"}
selected_lang = st.sidebar.selectbox(
    "🌐 Language / Мова",
    list(lang_options.keys()),
    index=1 if st.session_state.lang == "ua" else 0,
)
L = lang_options[selected_lang]
st.session_state.lang = L


# Helper: short alias
def T(key, **kw):
    return t(key, L, **kw)


# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
st.sidebar.title(f"📈 {T('sidebar_title')}")

page = st.sidebar.radio(
    T("nav_label"),
    [T("nav_download"), T("nav_backtest"), T("nav_analysis")],
    index=0,
)

# Data status
st.sidebar.divider()
st.sidebar.subheader(T("data_status"))
for tf in VALID_TIMEFRAMES:
    pq = Path(PARQUET_DIR) / f"klines_{tf}.parquet"
    if pq.exists():
        size_mb = pq.stat().st_size / (1024 * 1024)
        st.sidebar.success(f"{tf}: {size_mb:.1f} MB")
    else:
        st.sidebar.warning(f"{tf}: {T('not_downloaded')}")

st.sidebar.subheader(T("results_status"))
for tf in VALID_TIMEFRAMES:
    rp = Path(RESULTS_DIR) / f"grid_results_{tf}.csv"
    if rp.exists():
        size_mb = rp.stat().st_size / (1024 * 1024)
        st.sidebar.success(f"{tf}: {size_mb:.1f} MB")
    else:
        st.sidebar.info(f"{tf}: {T('no_results_yet')}")


# ══════════════════════════════════════════════════════════════
#  PAGE 1: DOWNLOAD DATA
# ══════════════════════════════════════════════════════════════
if page == T("nav_download"):
    st.header(T("download_header"))
    st.markdown(T("download_desc", symbol=SYMBOL))

    col1, col2, col3 = st.columns(3)
    with col1:
        timeframe = st.selectbox(
            T("timeframe"), ["1m", "1s"], index=0,
            help=T("timeframe_help"),
        )
    with col2:
        start_date = st.date_input(
            T("start_date"), value=date(2024, 1, 1),
            help=T("date_help"),
        )
    with col3:
        end_date = st.date_input(
            T("end_date"), value=date(2024, 12, 31),
            help=T("date_help"),
        )

    if timeframe == "1s":
        days = (end_date - start_date).days + 1
        est_size_gb = days * 0.02
        st.info(T("1s_warning", days=days, size=est_size_gb))

    pq_path = Path(PARQUET_DIR) / f"klines_{timeframe}.parquet"
    if pq_path.exists():
        existing_df = pd.read_parquet(pq_path, columns=["open_time"], engine="pyarrow")
        st.success(T("existing_data",
                      count=len(existing_df),
                      start=existing_df["open_time"].min(),
                      end=existing_df["open_time"].max()))
        del existing_df

    if st.button(f"🚀 {T('btn_download')}", type="primary", use_container_width=True):
        progress_bar = st.progress(0, text=T("downloading"))

        try:
            with st.spinner(T("downloading")):
                files = download_range(
                    symbol=SYMBOL,
                    timeframe=timeframe,
                    start=start_date,
                    end=end_date,
                    use_monthly=(timeframe != "1s"),
                )

            progress_bar.progress(70, text=T("converting"))

            with st.spinner(T("converting")):
                pq = csvs_to_parquet(timeframe)

            progress_bar.progress(100, text="Done!")

            df_check = pd.read_parquet(pq, columns=["open_time"], engine="pyarrow")
            st.success(T("download_success",
                          files=len(files),
                          count=len(df_check),
                          start=df_check["open_time"].min(),
                          end=df_check["open_time"].max()))
            st.balloons()

        except Exception as e:
            progress_bar.progress(0, text="Error!")
            st.error(T("download_failed", error=e))


# ══════════════════════════════════════════════════════════════
#  PAGE 2: RUN BACKTEST
# ══════════════════════════════════════════════════════════════
elif page == T("nav_backtest"):
    st.header(T("backtest_header"))
    st.markdown(T("backtest_desc"))

    timeframe = st.selectbox(
        T("timeframe"), ["1m", "1s"], index=0,
        help=T("timeframe_help"),
    )

    pq_path = Path(PARQUET_DIR) / f"klines_{timeframe}.parquet"
    if not pq_path.exists():
        st.error(T("no_data_error", tf=timeframe))
        st.stop()

    # ── Parameter Configuration ───────────────────────────────
    st.subheader(T("param_ranges"))
    st.markdown(T("param_ranges_desc"))

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{T('ema_periods')}**")
        fast_min, fast_max = st.slider(
            T("fast_ema_range"), 2, 100, (3, 50),
            help=T("fast_ema_help"),
        )
        fast_step = st.number_input(T("fast_ema_step"), 1, 10, 1)
        slow_min, slow_max = st.slider(
            T("slow_ema_range"), 5, 500, (10, 200),
            help=T("slow_ema_help"),
        )
        slow_step = st.number_input(T("slow_ema_step"), 1, 20, 5)

    with col2:
        st.markdown(f"**{T('risk_management')}**")
        sl_min, sl_max = st.slider(
            T("sl_range"), 0.1, 10.0, (0.3, 3.0), 0.1,
            help=T("sl_help"),
        )
        sl_step = st.number_input(T("sl_step"), 0.05, 1.0, 0.1, format="%.2f")
        tp_min, tp_max = st.slider(
            T("tp_range"), 0.1, 15.0, (0.5, 5.0), 0.1,
            help=T("tp_help"),
        )
        tp_step = st.number_input(T("tp_step"), 0.05, 1.0, 0.25, format="%.2f")

    use_volume_filter = st.checkbox(
        T("volume_filter_label"), value=True,
        help=T("volume_filter_help"),
    )

    # Build grid
    grid = ParameterGrid()
    grid.fast_ema_periods = list(range(fast_min, fast_max + 1, fast_step))
    grid.slow_ema_periods = list(range(slow_min, slow_max + 1, slow_step))
    grid.stop_loss_pcts = list(np.round(np.arange(sl_min, sl_max + sl_step / 2, sl_step), 2))
    grid.take_profit_pcts = list(np.round(np.arange(tp_min, tp_max + tp_step / 2, tp_step), 2))
    grid.volume_filter = [False, True] if use_volume_filter else [False]

    total_combos = grid.total_valid()

    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(T("fast_ema_values"), len(grid.fast_ema_periods))
    col2.metric(T("slow_ema_values"), len(grid.slow_ema_periods))
    col3.metric(T("sltp_combos"), f"{len(grid.stop_loss_pcts)} x {len(grid.take_profit_pcts)}")
    col4.metric(T("total_combinations"), f"{total_combos:,}")

    est_speed = 500
    est_time_sec = total_combos / est_speed
    if est_time_sec < 60:
        est_str = f"~{est_time_sec:.0f} sec"
    elif est_time_sec < 3600:
        est_str = f"~{est_time_sec/60:.0f} min"
    else:
        est_str = f"~{est_time_sec/3600:.1f} hours"
    st.info(T("estimated_time", time=est_str))

    quick_mode = st.checkbox(
        T("quick_test"), value=False,
        help=T("quick_test_help"),
    )
    if quick_mode:
        grid.fast_ema_periods = [5, 10, 20]
        grid.slow_ema_periods = [20, 50, 100]
        grid.stop_loss_pcts = [0.5, 1.0, 2.0]
        grid.take_profit_pcts = [1.0, 2.0, 3.0]
        grid.volume_filter = [False]
        total_combos = grid.total_valid()
        st.success(T("quick_mode_info", n=total_combos))

    # ── Run ───────────────────────────────────────────────────
    if st.button(f"🚀 {T('btn_run_backtest')}", type="primary", use_container_width=True):
        combinations = list(grid.valid_combinations())
        total = len(combinations)

        st.markdown(T("running_combos", n=total))
        progress_bar = st.progress(0, text=T("loading_data"))
        status_text = st.empty()

        try:
            df = load_parquet(timeframe)
            status_text.text(T("loaded_candles", n=len(df)))

            close = df["close"].values.astype(np.float64)
            open_ = df["open"].values.astype(np.float64)
            high = df["high"].values.astype(np.float64)
            low = df["low"].values.astype(np.float64)
            volume = df["volume"].values.astype(np.float64)
            bars_per_year = 31_536_000 if timeframe == "1s" else 525_600

            progress_bar.progress(5, text=T("precomputing_ema"))
            all_periods = set()
            for fast, slow, _, _, _ in combinations:
                all_periods.add(fast)
                all_periods.add(slow)

            cache = EMACache(close)
            cache.precompute(list(all_periods))
            ema_data = cache._cache

            os.makedirs(RESULTS_DIR, exist_ok=True)
            results_path = Path(RESULTS_DIR) / f"grid_results_{timeframe}.csv"

            all_results = []
            start_time = time.time()

            for i, (fast, slow, sl, tp, vf) in enumerate(combinations):
                fast_ema = ema_data[fast]
                slow_ema = ema_data[slow]

                signals = crossover_signals(fast_ema, slow_ema)
                if vf:
                    signals = apply_volume_filter(signals, volume)

                trades, pnl_per_trade, equity_curve = run_backtest(
                    open_prices=open_, high_prices=high, low_prices=low,
                    close_prices=close, signals=signals,
                    stop_loss_pct=sl, take_profit_pct=tp,
                    commission_pct=COMMISSION_PCT, initial_capital=INITIAL_CAPITAL,
                )

                metrics = compute_metrics(
                    pnl_per_trade=pnl_per_trade, equity_curve=equity_curve,
                    trades=trades, initial_capital=INITIAL_CAPITAL,
                    bars_per_year=bars_per_year,
                )

                all_results.append({
                    "fast_ema": fast, "slow_ema": slow,
                    "stop_loss_pct": sl, "take_profit_pct": tp,
                    "volume_filter": vf, **asdict(metrics),
                })

                if (i + 1) % max(1, total // 100) == 0 or i == total - 1:
                    pct = (i + 1) / total
                    elapsed = time.time() - start_time
                    speed = (i + 1) / elapsed if elapsed > 0 else 0
                    eta = (total - i - 1) / speed if speed > 0 else 0
                    progress_bar.progress(
                        min(pct, 1.0),
                        text=f"{i+1:,}/{total:,} ({pct*100:.1f}%) — "
                             f"{speed:.0f} combos/sec — ETA: {eta:.0f}s"
                    )

            progress_bar.progress(1.0, text=T("saving_results"))
            results_df = pd.DataFrame(all_results)
            results_df.to_csv(results_path, index=False)

            elapsed = time.time() - start_time
            st.success(T("backtest_success", n=total, time=elapsed, speed=total/elapsed))
            st.balloons()

            top5 = results_df.sort_values("sharpe_ratio", ascending=False).head(5)
            st.subheader(T("top5_title"))
            st.dataframe(top5[[
                "fast_ema", "slow_ema", "stop_loss_pct", "take_profit_pct",
                "volume_filter", "total_pnl_pct", "sharpe_ratio",
                "max_drawdown_pct", "win_rate", "total_trades",
            ]], use_container_width=True)

        except FileNotFoundError as e:
            st.error(str(e))
        except Exception as e:
            st.error(T("backtest_failed", error=e))
            import traceback
            st.code(traceback.format_exc())


# ══════════════════════════════════════════════════════════════
#  PAGE 3: ANALYSIS
# ══════════════════════════════════════════════════════════════
elif page == T("nav_analysis"):
    st.header(T("analysis_header"))
    st.markdown(T("analysis_desc"))

    timeframe = st.selectbox(T("timeframe"), ["1m", "1s"], key="analysis_tf",
                             help=T("timeframe_help"))
    results_path = Path(RESULTS_DIR) / f"grid_results_{timeframe}.csv"

    if not results_path.exists():
        st.warning(T("no_results_warning", tf=timeframe))
        st.stop()

    @st.cache_data
    def load_results(path: str) -> pd.DataFrame:
        df = pd.read_csv(path)
        numeric_cols = [
            "fast_ema", "slow_ema", "stop_loss_pct", "take_profit_pct",
            "total_pnl", "total_pnl_pct", "sharpe_ratio", "max_drawdown",
            "max_drawdown_pct", "win_rate", "profit_factor", "total_trades",
            "avg_trade_pnl", "avg_trade_duration_bars", "calmar_ratio",
            "avg_win", "avg_loss", "max_consecutive_losses",
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        if "volume_filter" in df.columns:
            df["volume_filter"] = df["volume_filter"].astype(str).map(
                {"True": True, "False": False, "1": True, "0": False}
            )
        return df

    df = load_results(str(results_path))
    st.markdown(T("loaded_combinations", n=len(df)))

    # ── Filters ───────────────────────────────────────────────
    with st.expander(f"🔍 {T('filters')}", expanded=True):
        fcol1, fcol2, fcol3, fcol4 = st.columns(4)
        with fcol1:
            min_trades = st.number_input(T("min_trades"), 0, 10000, 10,
                                         help=T("min_trades_help"))
        with fcol2:
            min_sharpe = st.number_input(T("min_sharpe"), -10.0, 50.0, 0.0, 0.1,
                                         help=T("min_sharpe_help"))
        with fcol3:
            max_dd = st.number_input(T("max_dd"), 0.0, 100.0, 50.0, 1.0,
                                     help=T("max_dd_help"))
        with fcol4:
            vol_options = [T("vol_all"), T("vol_on"), T("vol_off")]
            vol_filter = st.selectbox(T("vol_filter"), vol_options, key="vf_analysis",
                                      help=T("vol_filter_help"))

    mask = (
        (df["total_trades"] >= min_trades) &
        (df["sharpe_ratio"] >= min_sharpe) &
        (df["max_drawdown_pct"] <= max_dd)
    )
    if vol_filter == T("vol_on"):
        mask &= df["volume_filter"] == True
    elif vol_filter == T("vol_off"):
        mask &= df["volume_filter"] == False

    filtered = df[mask].copy()
    st.markdown(T("after_filters", n=len(filtered)))

    if filtered.empty:
        st.warning(T("no_results_filters"))
        st.stop()

    sort_by = st.selectbox(T("sort_by"), [
        "sharpe_ratio", "total_pnl_pct", "calmar_ratio", "profit_factor", "win_rate",
    ], index=0, key="sort_analysis", help=T("sort_help"))

    # ── KPIs ──────────────────────────────────────────────────
    best = filtered.sort_values(sort_by, ascending=False).iloc[0]

    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    kpi1.metric(T("best_sharpe"), f"{best['sharpe_ratio']:.2f}",
                help=T("min_sharpe_help"))
    kpi2.metric(T("best_pnl"), f"{best['total_pnl_pct']:.1f}%")
    kpi3.metric(T("max_dd_label"), f"{best['max_drawdown_pct']:.1f}%",
                help=T("max_dd_help"))
    kpi4.metric(T("win_rate_label"), f"{best['win_rate']:.1f}%")
    kpi5.metric(T("profit_factor_label"), f"{best['profit_factor']:.2f}")
    kpi6.metric(T("trades_label"), f"{int(best['total_trades'])}")

    vf_str = T("vol_on") if best.get("volume_filter") else T("vol_off")
    st.info(T("best_params",
              fast=int(best["fast_ema"]), slow=int(best["slow_ema"]),
              sl=best["stop_loss_pct"], tp=best["take_profit_pct"], vf=vf_str))

    # ── Top Results Table ─────────────────────────────────────
    st.subheader(T("top_combinations"))
    top_n = st.slider(T("show_top_n"), 10, 200, 30, key="top_n_analysis")

    display_cols = [
        "fast_ema", "slow_ema", "stop_loss_pct", "take_profit_pct",
        "volume_filter", "total_pnl_pct", "sharpe_ratio", "max_drawdown_pct",
        "win_rate", "profit_factor", "total_trades", "calmar_ratio",
        "avg_trade_pnl", "avg_win", "avg_loss", "max_consecutive_losses",
    ]
    existing_cols = [c for c in display_cols if c in filtered.columns]
    top_df = filtered.sort_values(sort_by, ascending=False).head(top_n)
    st.dataframe(top_df[existing_cols], use_container_width=True, height=450)

    csv_data = top_df[existing_cols].to_csv(index=False)
    st.download_button(f"📥 {T('download_csv')}", csv_data,
                       f"top_{top_n}_results_{timeframe}.csv", "text/csv")

    # ── Equity Curve ──────────────────────────────────────────
    st.subheader(T("equity_curve_title"))
    st.markdown(T("equity_curve_desc"))

    pq_path = Path(PARQUET_DIR) / f"klines_{timeframe}.parquet"
    has_data = pq_path.exists()

    if has_data:
        combo_options = []
        for idx, row in top_df.head(20).iterrows():
            label = (
                f"Fast={int(row['fast_ema'])}, Slow={int(row['slow_ema'])}, "
                f"SL={row['stop_loss_pct']:.1f}%, TP={row['take_profit_pct']:.2f}% "
                f"→ PnL={row['total_pnl_pct']:.1f}%, Sharpe={row['sharpe_ratio']:.2f}"
            )
            combo_options.append((label, row))

        if combo_options:
            selected_label = st.selectbox(
                T("select_combination"),
                [c[0] for c in combo_options],
                key="equity_combo",
            )
            selected_row = next(c[1] for c in combo_options if c[0] == selected_label)

            if st.button(f"📊 {T('btn_generate_equity')}"):
                with st.spinner(T("computing_equity")):
                    data_df = load_parquet(timeframe)
                    close = data_df["close"].values.astype(np.float64)
                    open_ = data_df["open"].values.astype(np.float64)
                    high = data_df["high"].values.astype(np.float64)
                    low = data_df["low"].values.astype(np.float64)
                    vol = data_df["volume"].values.astype(np.float64)
                    timestamps = data_df["open_time"].values

                    cache = EMACache(close)
                    fast_ema = cache.get(int(selected_row["fast_ema"]))
                    slow_ema = cache.get(int(selected_row["slow_ema"]))

                    signals = crossover_signals(fast_ema, slow_ema)
                    if selected_row.get("volume_filter"):
                        signals = apply_volume_filter(signals, vol)

                    trades, pnl_arr, equity = run_backtest(
                        open_, high, low, close, signals,
                        selected_row["stop_loss_pct"],
                        selected_row["take_profit_pct"],
                        COMMISSION_PCT, INITIAL_CAPITAL,
                    )

                step = max(1, len(equity) // 5000)

                eq_df = pd.DataFrame({
                    "time": pd.to_datetime(timestamps[::step]),
                    "equity": equity[::step],
                })
                fig_eq = px.line(eq_df, x="time", y="equity",
                                 title="Equity Curve",
                                 labels={"equity": "Equity ($)", "time": ""})
                fig_eq.add_hline(y=INITIAL_CAPITAL, line_dash="dash", line_color="gray",
                                 annotation_text="Initial Capital")
                fig_eq.update_layout(height=400)
                st.plotly_chart(fig_eq, use_container_width=True)

                running_max = np.maximum.accumulate(equity)
                dd_pct = (running_max - equity) / running_max * 100
                dd_df = pd.DataFrame({
                    "time": pd.to_datetime(timestamps[::step]),
                    "drawdown": dd_pct[::step],
                })
                fig_dd = px.area(dd_df, x="time", y="drawdown",
                                 title="Drawdown %",
                                 labels={"drawdown": "Drawdown %", "time": ""})
                fig_dd.update_traces(line_color="red", fillcolor="rgba(255,0,0,0.2)")
                fig_dd.update_layout(height=300, yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig_dd, use_container_width=True)

                if len(pnl_arr) > 0:
                    fig_trades = px.histogram(
                        x=pnl_arr, nbins=50,
                        title=f"PnL Distribution ({len(pnl_arr)} trades)",
                        labels={"x": "Trade PnL ($)"},
                    )
                    fig_trades.add_vline(x=0, line_dash="dash", line_color="red")
                    st.plotly_chart(fig_trades, use_container_width=True)
    else:
        st.warning(T("no_parquet_warning"))

    # ── Heatmap ───────────────────────────────────────────────
    st.subheader(T("ema_heatmap"))
    st.caption(T("ema_heatmap_help"))

    heatmap_metric = st.selectbox(T("heatmap_metric"), [
        "sharpe_ratio", "total_pnl_pct", "calmar_ratio", "win_rate", "profit_factor",
    ], key="hm_metric")

    heatmap_data = (
        filtered.groupby(["fast_ema", "slow_ema"])[heatmap_metric]
        .max().reset_index()
    )
    pivot = heatmap_data.pivot(index="slow_ema", columns="fast_ema", values=heatmap_metric)

    if not pivot.empty:
        fig_hm = px.imshow(
            pivot,
            labels=dict(x="Fast EMA", y="Slow EMA", color=heatmap_metric),
            aspect="auto", color_continuous_scale="RdYlGn",
            title=f"Best {heatmap_metric} per EMA pair",
        )
        fig_hm.update_layout(height=500)
        st.plotly_chart(fig_hm, use_container_width=True)

    # ── Distributions ─────────────────────────────────────────
    st.subheader(T("distribution_analysis"))
    st.caption(T("distribution_help"))

    dist_left, dist_right = st.columns(2)
    with dist_left:
        fig_pnl = px.histogram(filtered, x="total_pnl_pct", nbins=50,
                               title="Distribution of Total PnL %")
        fig_pnl.add_vline(x=0, line_dash="dash", line_color="red")
        st.plotly_chart(fig_pnl, use_container_width=True)

    with dist_right:
        fig_sharpe = px.histogram(filtered, x="sharpe_ratio", nbins=50,
                                  title="Distribution of Sharpe Ratio")
        fig_sharpe.add_vline(x=0, line_dash="dash", line_color="red")
        st.plotly_chart(fig_sharpe, use_container_width=True)

    # ── Risk vs Return ────────────────────────────────────────
    st.subheader(T("risk_vs_return"))
    st.caption(T("risk_vs_return_help"))

    fig_scatter = px.scatter(
        filtered, x="max_drawdown_pct", y="total_pnl_pct",
        color="sharpe_ratio", size="total_trades",
        hover_data=["fast_ema", "slow_ema", "stop_loss_pct", "take_profit_pct"],
        title="Max Drawdown vs Total PnL",
        labels={"max_drawdown_pct": "Max Drawdown %", "total_pnl_pct": "Total PnL %"},
        color_continuous_scale="RdYlGn",
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # ── Parameter Impact ──────────────────────────────────────
    st.subheader(T("param_impact"))
    st.caption(T("param_impact_help"))

    imp_col1, imp_col2 = st.columns(2)
    with imp_col1:
        param_col = st.selectbox(
            T("parameter"),
            ["fast_ema", "slow_ema", "stop_loss_pct", "take_profit_pct"],
            key="impact_param",
        )
    with imp_col2:
        impact_metric = st.selectbox(
            T("impact_on"),
            ["sharpe_ratio", "total_pnl_pct", "win_rate", "profit_factor"],
            key="impact_metric",
        )

    impact_data = (
        filtered.groupby(param_col)[impact_metric]
        .agg(["mean", "median", "std"]).reset_index()
    )
    fig_impact = go.Figure()
    fig_impact.add_trace(go.Bar(
        x=impact_data[param_col], y=impact_data["mean"], name="Mean",
        marker_color="steelblue",
    ))
    fig_impact.add_trace(go.Scatter(
        x=impact_data[param_col], y=impact_data["median"],
        mode="lines+markers", name="Median", line=dict(color="orange", width=2),
    ))
    fig_impact.update_layout(
        title=f"Impact of {param_col} on {impact_metric}",
        xaxis_title=param_col, yaxis_title=impact_metric, height=400,
    )
    st.plotly_chart(fig_impact, use_container_width=True)

    # ── SL/TP Heatmap ────────────────────────────────────────
    st.subheader(T("sltp_heatmap"))
    st.caption(T("sltp_heatmap_help"))

    sltp_metric = st.selectbox(T("metric"), [
        "sharpe_ratio", "total_pnl_pct", "win_rate",
    ], key="sltp_metric")

    sltp_data = (
        filtered.groupby(["stop_loss_pct", "take_profit_pct"])[sltp_metric]
        .max().reset_index()
    )
    sltp_pivot = sltp_data.pivot(
        index="take_profit_pct", columns="stop_loss_pct", values=sltp_metric,
    )
    if not sltp_pivot.empty:
        fig_sltp = px.imshow(
            sltp_pivot,
            labels=dict(x="Stop Loss %", y="Take Profit %", color=sltp_metric),
            aspect="auto", color_continuous_scale="RdYlGn",
            title=f"Best {sltp_metric} per SL/TP pair",
        )
        fig_sltp.update_layout(height=450)
        st.plotly_chart(fig_sltp, use_container_width=True)

    # ── Footer ────────────────────────────────────────────────
    st.divider()
    st.caption(T("footer", symbol=SYMBOL, capital=INITIAL_CAPITAL,
                  comm=COMMISSION_PCT, tf=timeframe))
