# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.signal_providers
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.factor.core.evaluation.backtest; zephyr.factor.analysis.multifactor_synthesis; zephyr.factor.factor_base
# [CONSUMERS] zephyr.ex_core.trading_session
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] signal_provider/price_provider 均为 callable 注入，TradingSession 不耦合具体数据源
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_core/test_trading_session.py
# [A_module] module_id=MOD-L06-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_EXECUTION_CORE — 信号源 / 价格源 callable 工厂

为 TradingSession 提供可注入的 signal_provider 和 price_provider。
用 callable 注入实现开闭原则——新增信号源只需写新 provider 函数，不改 TradingSession。

提供的工厂：
  - make_clickhouse_signal_provider: 从 ClickHouse 加载历史 → 计算因子 → 合成信号 → 返回最新日信号
  - make_mock_signal_provider: 测试用——返回固定信号
  - make_mock_price_provider: 测试用——返回固定价格

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 标的池 universe + 因子配置 factor_ids
#   fields: list[str] 标的代码 + 因子ID元组/合成方法/回看天数/pit_shift
#   code: make_clickhouse_signal_provider(factor_ids, ...) (signal_providers.py)
# 层: 算法
# - id: A1
#   name_zh: ① ClickHouse 信号管线
#   name_en: _provider（闭包）
#   intro: 加载历史→逐因子算面板→截面合成→PIT平移→取最后非NaN截面
#   desc: load_history → compute_factor_panel → synthesize(equal_weight等) → panel.shift(pit_shift) → _extract_latest_signals
#   inputs: I1
#   outputs: dict[symbol, signal]（最新日信号）
#   invariant: PIT 无前瞻（pit_shift≥1 今日决策用昨日因子）
# - id: A2
#   name_zh: ② Mock 源工厂
#   name_en: make_mock_signal_provider / make_mock_price_provider
#   intro: 测试用固定信号/价格闭包，忽略 universe 入参
#   desc: 返回 dict(signals)/dict(prices) 副本的 callable
#   inputs: I1
#   outputs: 固定信号/价格 dict
# 层: 输出
# - id: O1
#   name_zh: SignalProvider / PriceProvider callable
#   name_en: provider 闭包
#   intro: 可注入 TradingSession 的信号源/价格源，与具体数据源解耦
#   downstream: ex_core.trading_session（构造注入）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# A1 --> O1
# A2 --> O1
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pandas as pd

from zephyr.factor.analysis.multifactor_synthesis import synthesize
from zephyr.factor.core.evaluation.backtest import compute_factor_panel, load_history
from zephyr.factor.factor_base import FactorRegistry, autodiscover_factors

_logger = logging.getLogger(__name__)

SignalProvider = Callable[[list[str]], dict[str, float]]
PriceProvider = Callable[[list[str]], dict[str, Decimal]]


def make_mock_signal_provider(signals: dict[str, float]) -> SignalProvider:
    """测试用——返回固定信号（忽略 universe 参数）。"""

    def _provider(_universe: list[str]) -> dict[str, float]:
        return dict(signals)

    return _provider


def make_mock_price_provider(prices: dict[str, Decimal]) -> PriceProvider:
    """测试用——返回固定价格。"""

    def _provider(_universe: list[str]) -> dict[str, Decimal]:
        return dict(prices)

    return _provider


def make_clickhouse_signal_provider(
    factor_ids: tuple[str, ...],
    synthesis_method: str = "equal_weight",
    lookback_days: int = 30,
    pit_shift: int = 1,
    synthesis_kwargs: dict | None = None,
) -> SignalProvider:
    """从 ClickHouse 加载最近 N 日历史 → 计算因子 → 合成信号 → 返回最新日信号。

    复用 StrategyRunner 的 load_history + compute_factor_panel + synthesize 管线。
    PIT 原理：实时场景下 load_history 只返回已收盘的历史数据，天然 PIT。
    pit_shift > 0 时对信号面板做 shift，取最后一个非 NaN 截面。

    Args:
        factor_ids: 参与合成的因子 ID 元组（如 ("momentum_20d",)）
        synthesis_method: 合成方法 "equal_weight"|"ic_weighted"|"regression"
        lookback_days: 回看天数（加 10 天 buffer 确保因子窗口覆盖）
        pit_shift: 信号 PIT 平移天数（默认 1，今日决策用昨日因子）
        synthesis_kwargs: 合成方法特定参数
    """

    def _provider(universe: list[str]) -> dict[str, float]:
        if not universe or not factor_ids:
            return {}
        start, end = _calc_date_range(lookback_days)
        history = load_history(universe, start, end)
        if history.empty:
            _logger.warning("signal_provider: load_history 返回空 (symbols=%d)", len(universe))
            return {}
        factor_panels = _compute_factors(list(factor_ids), history)
        if not factor_panels:
            return {}
        signal_panel = _build_signal_panel(factor_panels, synthesis_method, synthesis_kwargs or {}, pit_shift)
        if signal_panel.empty:
            return {}
        return _extract_latest_signals(signal_panel)

    return _provider


def _calc_date_range(lookback_days: int) -> tuple[str, str]:
    """计算 (start, end) 日期字符串，end=今天，start=今天-lookback_days-buffer。"""
    today = datetime.now(timezone.utc).date()
    buffer = 10  # 因子窗口 buffer（如 momentum_20d 需要 20+ 天数据）
    start = today - timedelta(days=lookback_days + buffer)
    return start.isoformat(), today.isoformat()


def _compute_factors(
    factor_ids: list[str],
    history: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """逐因子计算面板，返回 {factor_id: DataFrame(date×symbol)}。"""
    panels: dict[str, pd.DataFrame] = {}
    for fid in factor_ids:
        factor_cls = _ensure_factor(fid)
        if factor_cls is None:
            continue
        panel = compute_factor_panel(factor_cls, history)
        if panel.empty:
            _logger.warning("因子 %s 面板为空，跳过", fid)
            continue
        panels[fid] = panel
    return panels


def _ensure_factor(factor_id: str):
    """确保因子已注册（未注册时触发 autodiscover_factors 一次）。"""
    try:
        return FactorRegistry.get(factor_id)
    except KeyError:
        _logger.info("因子 %s 未注册，触发 autodiscover_factors", factor_id)
        autodiscover_factors()
        try:
            return FactorRegistry.get(factor_id)
        except KeyError:
            _logger.error("因子 %s autodiscover 后仍未注册", factor_id)
            return None


def _build_signal_panel(
    factor_panels: dict[str, pd.DataFrame],
    method: str,
    kwargs: dict,
    pit_shift: int,
) -> pd.DataFrame:
    """逐截面合成信号 + PIT 平移。返回 DataFrame(date×symbol)。"""
    first = next(iter(factor_panels.values()))
    dates = first.index
    symbols = first.columns
    rows: dict = {}
    for as_of in dates:
        factor_values = {
            fid: fp.loc[as_of]
            for fid, fp in factor_panels.items()
            if as_of in fp.index
        }
        if not factor_values:
            continue
        rows[as_of] = synthesize(factor_values, method=method, **kwargs)
    if not rows:
        return pd.DataFrame(index=dates, columns=symbols, dtype=float)
    panel = pd.DataFrame(rows).T.reindex(index=dates, columns=symbols)
    if pit_shift > 0:
        panel = panel.shift(pit_shift)
    return panel


def _extract_latest_signals(panel: pd.DataFrame) -> dict[str, float]:
    """取信号面板最后一个非全 NaN 截面，返回 {symbol: signal}。"""
    for as_of in reversed(panel.index):
        row = panel.loc[as_of]
        valid = row.dropna()
        if not valid.empty:
            return {str(s): float(v) for s, v in valid.items()}
    return {}


__all__ = [
    "SignalProvider",
    "PriceProvider",
    "make_clickhouse_signal_provider",
    "make_mock_signal_provider",
    "make_mock_price_provider",
]
