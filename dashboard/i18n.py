"""
Internationalization (i18n) strings for EN / UA.
"""

STRINGS = {
    # ── General ──────────────────────────────────────────────
    "app_title": {
        "en": "EMA Crossover Strategy Backtester",
        "ua": "Бектестер стратегії EMA Crossover",
    },
    "sidebar_title": {
        "en": "EMA Backtester",
        "ua": "EMA Бектестер",
    },
    "nav_label": {
        "en": "Navigation",
        "ua": "Навігація",
    },
    "nav_download": {
        "en": "1. Download Data",
        "ua": "1. Завантажити дані",
    },
    "nav_backtest": {
        "en": "2. Run Backtest",
        "ua": "2. Запустити бектест",
    },
    "nav_analysis": {
        "en": "3. Analysis",
        "ua": "3. Аналіз",
    },
    "language": {
        "en": "Language",
        "ua": "Мова",
    },
    "data_status": {
        "en": "Data Status",
        "ua": "Стан даних",
    },
    "results_status": {
        "en": "Results Status",
        "ua": "Стан результатів",
    },
    "not_downloaded": {
        "en": "not downloaded",
        "ua": "не завантажено",
    },
    "no_results_yet": {
        "en": "no results yet",
        "ua": "результатів немає",
    },

    # ── Page 1: Download ─────────────────────────────────────
    "download_header": {
        "en": "Download Historical Data",
        "ua": "Завантаження історичних даних",
    },
    "download_desc": {
        "en": "Download kline (candlestick) data for **{symbol}** from [Binance Data Vision](https://data.binance.vision/). "
              "This is free bulk historical data for crypto futures.",
        "ua": "Завантаження свічкових даних для **{symbol}** з [Binance Data Vision](https://data.binance.vision/). "
              "Це безкоштовні історичні дані для крипто-ф'ючерсів.",
    },
    "timeframe": {
        "en": "Timeframe",
        "ua": "Таймфрейм",
    },
    "timeframe_help": {
        "en": "1m = one candle per minute (recommended to start). 1s = one candle per second (very large dataset, ~31M rows/year).",
        "ua": "1m = одна свічка за хвилину (рекомендовано для початку). 1s = одна свічка за секунду (дуже великий датасет, ~31М рядків/рік).",
    },
    "start_date": {
        "en": "Start date",
        "ua": "Дата початку",
    },
    "end_date": {
        "en": "End date",
        "ua": "Дата кінця",
    },
    "date_help": {
        "en": "Select the period for historical data. 1 year is recommended for meaningful backtest results.",
        "ua": "Оберіть період для історичних даних. 1 рік рекомендовано для якісних результатів бектесту.",
    },
    "1s_warning": {
        "en": "1-second data: ~{days} daily files. Estimated size: ~{size:.1f} GB. This may take a while.",
        "ua": "1-секундні дані: ~{days} файлів. Орієнтовний розмір: ~{size:.1f} ГБ. Це може зайняти час.",
    },
    "existing_data": {
        "en": "Existing data: **{count:,}** candles ({start} to {end})",
        "ua": "Наявні дані: **{count:,}** свічок ({start} до {end})",
    },
    "btn_download": {
        "en": "Download & Convert",
        "ua": "Завантажити та конвертувати",
    },
    "downloading": {
        "en": "Downloading from Binance Data Vision...",
        "ua": "Завантаження з Binance Data Vision...",
    },
    "converting": {
        "en": "Converting to Parquet...",
        "ua": "Конвертація у Parquet...",
    },
    "download_success": {
        "en": "Downloaded **{files}** files, **{count:,}** candles saved. Period: {start} — {end}",
        "ua": "Завантажено **{files}** файлів, **{count:,}** свічок збережено. Період: {start} — {end}",
    },
    "download_failed": {
        "en": "Download failed: {error}",
        "ua": "Помилка завантаження: {error}",
    },

    # ── Page 2: Backtest ─────────────────────────────────────
    "backtest_header": {
        "en": "Run Grid Search Backtest",
        "ua": "Запуск Grid Search бектесту",
    },
    "backtest_desc": {
        "en": "Configure parameter ranges and run all valid combinations. "
              "The optimizer tests every possible EMA + SL/TP combination to find the best ones.",
        "ua": "Налаштуйте діапазони параметрів і запустіть перебір усіх комбінацій. "
              "Оптимізатор тестує кожну можливу комбінацію EMA + SL/TP, щоб знайти найкращі.",
    },
    "no_data_error": {
        "en": "No {tf} data found. Go to **1. Download Data** first.",
        "ua": "Дані {tf} не знайдено. Спочатку перейдіть до **1. Завантажити дані**.",
    },
    "param_ranges": {
        "en": "Parameter Ranges",
        "ua": "Діапазони параметрів",
    },
    "param_ranges_desc": {
        "en": "Configure the ranges for grid search optimization.",
        "ua": "Налаштуйте діапазони для оптимізації через повний перебір.",
    },
    "ema_periods": {
        "en": "EMA Periods",
        "ua": "Періоди EMA",
    },
    "fast_ema_range": {
        "en": "Fast EMA range",
        "ua": "Діапазон швидкої EMA",
    },
    "fast_ema_help": {
        "en": "Fast (short-period) EMA reacts quickly to price changes. Typical values: 5-50.",
        "ua": "Швидка (короткоперіодна) EMA реагує швидко на зміни ціни. Типові значення: 5-50.",
    },
    "fast_ema_step": {
        "en": "Fast EMA step",
        "ua": "Крок швидкої EMA",
    },
    "slow_ema_range": {
        "en": "Slow EMA range",
        "ua": "Діапазон повільної EMA",
    },
    "slow_ema_help": {
        "en": "Slow (long-period) EMA shows the overall trend. Must be larger than fast EMA. Typical: 20-200.",
        "ua": "Повільна (довгоперіодна) EMA показує загальний тренд. Має бути більшою за швидку. Типово: 20-200.",
    },
    "slow_ema_step": {
        "en": "Slow EMA step",
        "ua": "Крок повільної EMA",
    },
    "risk_management": {
        "en": "Risk Management",
        "ua": "Управління ризиком",
    },
    "sl_range": {
        "en": "Stop Loss % range",
        "ua": "Діапазон стоп-лосу %",
    },
    "sl_help": {
        "en": "Stop Loss closes the position at a loss to limit downside. E.g., 1% means exit if price moves 1% against you.",
        "ua": "Стоп-лос закриває позицію зі збитком для обмеження втрат. Напр., 1% — вихід, якщо ціна пішла на 1% проти вас.",
    },
    "sl_step": {
        "en": "SL step %",
        "ua": "Крок SL %",
    },
    "tp_range": {
        "en": "Take Profit % range",
        "ua": "Діапазон тейк-профіту %",
    },
    "tp_help": {
        "en": "Take Profit closes the position at a profit. E.g., 2% means exit when price moves 2% in your favor.",
        "ua": "Тейк-профіт закриває позицію з прибутком. Напр., 2% — вихід, коли ціна пішла на 2% у вашу сторону.",
    },
    "tp_step": {
        "en": "TP step %",
        "ua": "Крок TP %",
    },
    "volume_filter_label": {
        "en": "Include volume filter variants",
        "ua": "Включити варіанти з фільтром об'єму",
    },
    "volume_filter_help": {
        "en": "When enabled, also tests versions where signals are only taken when volume is above average (confirms the move).",
        "ua": "Якщо увімкнено, також тестує варіанти, де сигнали приймаються тільки при об'ємі вище середнього (підтвердження руху).",
    },
    "fast_ema_values": {
        "en": "Fast EMA values",
        "ua": "Значень швидкої EMA",
    },
    "slow_ema_values": {
        "en": "Slow EMA values",
        "ua": "Значень повільної EMA",
    },
    "sltp_combos": {
        "en": "SL/TP combos",
        "ua": "Комбінацій SL/TP",
    },
    "total_combinations": {
        "en": "Total combinations",
        "ua": "Всього комбінацій",
    },
    "estimated_time": {
        "en": "Estimated time: **{time}** (depends on CPU and data size)",
        "ua": "Орієнтовний час: **{time}** (залежить від CPU та об'єму даних)",
    },
    "quick_test": {
        "en": "Quick test (small subset)",
        "ua": "Швидкий тест (мала підмножина)",
    },
    "quick_test_help": {
        "en": "Runs only ~72 combinations instead of thousands. Good for checking that everything works before a full run.",
        "ua": "Запускає лише ~72 комбінації замість тисяч. Добре для перевірки працездатності перед повним запуском.",
    },
    "quick_mode_info": {
        "en": "Quick mode: only **{n}** combinations",
        "ua": "Швидкий режим: лише **{n}** комбінацій",
    },
    "btn_run_backtest": {
        "en": "Run Backtest",
        "ua": "Запустити бектест",
    },
    "running_combos": {
        "en": "Running **{n:,}** parameter combinations...",
        "ua": "Обробляється **{n:,}** комбінацій параметрів...",
    },
    "loading_data": {
        "en": "Loading data...",
        "ua": "Завантаження даних...",
    },
    "loaded_candles": {
        "en": "Loaded {n:,} candles",
        "ua": "Завантажено {n:,} свічок",
    },
    "precomputing_ema": {
        "en": "Pre-computing EMAs...",
        "ua": "Попередній розрахунок EMA...",
    },
    "saving_results": {
        "en": "Saving results...",
        "ua": "Збереження результатів...",
    },
    "backtest_success": {
        "en": "Completed **{n:,}** combinations in **{time:.1f}s** ({speed:.0f} combos/sec). Results saved!",
        "ua": "Завершено **{n:,}** комбінацій за **{time:.1f}с** ({speed:.0f} комб/сек). Результати збережено!",
    },
    "top5_title": {
        "en": "Top 5 Results (by Sharpe)",
        "ua": "Топ 5 результатів (за Sharpe)",
    },
    "backtest_failed": {
        "en": "Backtest failed: {error}",
        "ua": "Помилка бектесту: {error}",
    },

    # ── Page 3: Analysis ─────────────────────────────────────
    "analysis_header": {
        "en": "Backtest Results Analysis",
        "ua": "Аналіз результатів бектесту",
    },
    "analysis_desc": {
        "en": "Explore backtest results with interactive charts, heatmaps, and filters.",
        "ua": "Досліджуйте результати бектесту з інтерактивними графіками, тепловими картами та фільтрами.",
    },
    "no_results_warning": {
        "en": "No results for **{tf}**. Go to **2. Run Backtest** first.",
        "ua": "Результатів для **{tf}** немає. Спочатку перейдіть до **2. Запустити бектест**.",
    },
    "loaded_combinations": {
        "en": "Loaded **{n:,}** parameter combinations",
        "ua": "Завантажено **{n:,}** комбінацій параметрів",
    },
    "filters": {
        "en": "Filters",
        "ua": "Фільтри",
    },
    "min_trades": {
        "en": "Min trades",
        "ua": "Мін. угод",
    },
    "min_trades_help": {
        "en": "Filter out combinations with too few trades — they may not be statistically significant.",
        "ua": "Відфільтрувати комбінації з малою к-стю угод — вони можуть бути статистично незначущими.",
    },
    "min_sharpe": {
        "en": "Min Sharpe",
        "ua": "Мін. Sharpe",
    },
    "min_sharpe_help": {
        "en": "Sharpe Ratio measures risk-adjusted return. > 1 is good, > 2 is very good, < 0 means losing money.",
        "ua": "Sharpe Ratio вимірює дохідність з урахуванням ризику. > 1 — добре, > 2 — дуже добре, < 0 — збиток.",
    },
    "max_dd": {
        "en": "Max Drawdown %",
        "ua": "Макс. просадка %",
    },
    "max_dd_help": {
        "en": "Maximum drawdown — the biggest peak-to-trough drop. Lower is safer. 50% means you lost half your capital at the worst point.",
        "ua": "Максимальна просадка — найбільше падіння від піку до дна. Менше = безпечніше. 50% = втратили половину капіталу в найгіршій точці.",
    },
    "vol_filter": {
        "en": "Volume filter",
        "ua": "Фільтр об'єму",
    },
    "vol_filter_help": {
        "en": "Filter results by whether volume filter was used. 'On' = only show combos with volume confirmation.",
        "ua": "Фільтр за використанням фільтру об'єму. 'Увімк.' = показати лише комбінації з підтвердженням об'ємом.",
    },
    "vol_all": {"en": "All", "ua": "Усі"},
    "vol_on": {"en": "On", "ua": "Увімк."},
    "vol_off": {"en": "Off", "ua": "Вимк."},
    "after_filters": {
        "en": "**{n:,}** combinations after filters",
        "ua": "**{n:,}** комбінацій після фільтрів",
    },
    "no_results_filters": {
        "en": "No results match the current filters. Try relaxing them.",
        "ua": "Жодна комбінація не відповідає фільтрам. Спробуйте послабити їх.",
    },
    "sort_by": {
        "en": "Sort by",
        "ua": "Сортувати за",
    },
    "sort_help": {
        "en": "Choose which metric determines the 'best' result. Sharpe Ratio is the most balanced choice.",
        "ua": "Оберіть метрику для визначення 'найкращого' результату. Sharpe Ratio — найбільш збалансований вибір.",
    },
    "best_params": {
        "en": "**Best params:** Fast EMA = **{fast}**, Slow EMA = **{slow}**, "
              "SL = **{sl:.1f}%**, TP = **{tp:.2f}%**, Volume Filter = **{vf}**",
        "ua": "**Найкращі параметри:** Швидка EMA = **{fast}**, Повільна EMA = **{slow}**, "
              "SL = **{sl:.1f}%**, TP = **{tp:.2f}%**, Фільтр об'єму = **{vf}**",
    },
    "top_combinations": {
        "en": "Top Parameter Combinations",
        "ua": "Найкращі комбінації параметрів",
    },
    "show_top_n": {
        "en": "Show top N",
        "ua": "Показати топ N",
    },
    "download_csv": {
        "en": "Download Top Results CSV",
        "ua": "Завантажити топ результати CSV",
    },
    "equity_curve_title": {
        "en": "Equity Curve — Single Combination",
        "ua": "Крива капіталу — одна комбінація",
    },
    "equity_curve_desc": {
        "en": "Select a combination from the top results to visualize how your capital would change over time.",
        "ua": "Оберіть комбінацію з топ-результатів, щоб побачити, як змінювався б ваш капітал з часом.",
    },
    "select_combination": {
        "en": "Select combination",
        "ua": "Оберіть комбінацію",
    },
    "btn_generate_equity": {
        "en": "Generate Equity Curve",
        "ua": "Побудувати криву капіталу",
    },
    "computing_equity": {
        "en": "Computing equity curve...",
        "ua": "Розрахунок кривої капіталу...",
    },
    "no_parquet_warning": {
        "en": "Parquet data not found — equity curve requires raw candle data. Download data first.",
        "ua": "Parquet-дані не знайдено — для кривої капіталу потрібні свічкові дані. Спочатку завантажте дані.",
    },
    "ema_heatmap": {
        "en": "EMA Period Heatmap",
        "ua": "Теплова карта періодів EMA",
    },
    "ema_heatmap_help": {
        "en": "Shows the best metric value for each Fast/Slow EMA pair. Green = better, Red = worse.",
        "ua": "Показує найкраще значення метрики для кожної пари швидка/повільна EMA. Зелений = краще, Червоний = гірше.",
    },
    "heatmap_metric": {
        "en": "Heatmap metric",
        "ua": "Метрика теплової карти",
    },
    "distribution_analysis": {
        "en": "Distribution Analysis",
        "ua": "Аналіз розподілу",
    },
    "distribution_help": {
        "en": "Histograms show how results are distributed. A good strategy has most results shifted to the right (positive).",
        "ua": "Гістограми показують розподіл результатів. Гарна стратегія має більшість результатів зміщеними вправо (позитивних).",
    },
    "risk_vs_return": {
        "en": "Risk vs Return",
        "ua": "Ризик vs Дохідність",
    },
    "risk_vs_return_help": {
        "en": "Scatter plot: each dot is one parameter combination. Best results are in the top-left (high return, low drawdown).",
        "ua": "Scatter plot: кожна точка — одна комбінація параметрів. Найкращі результати — зверху-зліва (висока дохідність, низька просадка).",
    },
    "param_impact": {
        "en": "Parameter Impact Analysis",
        "ua": "Аналіз впливу параметрів",
    },
    "param_impact_help": {
        "en": "Shows how each parameter value affects the chosen metric on average. Helps identify which values work best.",
        "ua": "Показує, як кожне значення параметра впливає на обрану метрику в середньому. Допомагає знайти найкращі значення.",
    },
    "parameter": {
        "en": "Parameter",
        "ua": "Параметр",
    },
    "impact_on": {
        "en": "Impact on",
        "ua": "Вплив на",
    },
    "sltp_heatmap": {
        "en": "Stop Loss / Take Profit Heatmap",
        "ua": "Теплова карта стоп-лос / тейк-профіт",
    },
    "sltp_heatmap_help": {
        "en": "Shows which SL/TP combinations perform best. Helps find the optimal risk/reward ratio.",
        "ua": "Показує, які комбінації SL/TP працюють найкраще. Допомагає знайти оптимальне співвідношення ризик/прибуток.",
    },
    "metric": {
        "en": "Metric",
        "ua": "Метрика",
    },

    # ── Metric labels (for KPIs, tooltips) ────────────────────
    "best_sharpe": {"en": "Best Sharpe", "ua": "Найкращий Sharpe"},
    "best_pnl": {"en": "Best PnL %", "ua": "Найкращий PnL %"},
    "max_dd_label": {"en": "Max DD %", "ua": "Макс. просадка %"},
    "win_rate_label": {"en": "Win Rate", "ua": "% прибуткових"},
    "profit_factor_label": {"en": "Profit Factor", "ua": "Profit Factor"},
    "trades_label": {"en": "Trades", "ua": "Угод"},

    # ── Footer ────────────────────────────────────────────────
    "footer": {
        "en": "Symbol: {symbol} | Initial capital: ${capital:,.0f} | Commission: {comm}% | Data: {tf} candles",
        "ua": "Символ: {symbol} | Початковий капітал: ${capital:,.0f} | Комісія: {comm}% | Дані: {tf} свічки",
    },
}


def t(key: str, lang: str = "en", **kwargs) -> str:
    """Get translated string. Falls back to English if key/lang missing."""
    entry = STRINGS.get(key, {})
    text = entry.get(lang, entry.get("en", f"[{key}]"))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text
