# [BLUEPRINT] MOD-SOWNER-002 | docs/03_modules/_domain_ashare_signal/blueprint.md
# [MODULE] zephyr.strategy_factory.owner_regime_switcher.engine
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] dataclasses; numpy; pandas; typing; zephyr.strategy_factory.owner_regime_switcher.costs
# [CONSUMERS] zephyr.strategy_factory.owner_regime_switcher.exam; tests/strategy_factory/test_s_owner_002_engine.py
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 信号 ≤t 收盘判定（引擎内 shift(1)）、t+1 开盘成交（PIT 铁律）；滑点流动性输入=t-1 日该标的成交额；整数手 100 股/手；T+1 结构（t+1 开盘成交下同日回转结构性不存在）；desired_value 以前一日收盘 NAV 计（禁循环引用当日价）；两腿引擎逐参数同一实现（同池对照）
# [MODIFY-GUARD] 考试冻结文档 §5——冻结后语义变更=第二真源作弊
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(窗口/面板非法)； KeyError(调度表缺列)
# [TESTS] tests/strategy_factory/test_s_owner_002_engine.py
# [A_module] module_id=MOD-SOWNER-002 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""组合引擎——同一代理池在"启用集合+上限"调度下逐日盯市。

时序铁律（冻结 §5）:
  * 包目标仓位 = t-1 收盘判定（引擎统一 shift）→ t 日开盘成交；
  * 调度上限 = 调度表当日值（switcher 已按 trade_date 严格早于 t 构造）；
  * desired_value = 权重 × 前一日收盘 NAV（防循环引用）；100 股整数手向下取整。

对外语义: run_leg(sched_df, ...) -> LegResult（nav/exposure/指标/换手/交易次数）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final

import numpy as np
import pandas as pd

from zephyr.strategy_factory.owner_regime_switcher.costs import total_cost_yuan

TRADING_DAYS_PER_YEAR = 244
LOT_SIZE = 100

__all__: Final = ["EngineConfig", "LegResult", "run_leg", "compute_metrics"]


@dataclass(frozen=True)
class EngineConfig:
    """引擎参数（冻结：初始资金 100 万/整数手 100；slippage_scale 仅红蓝注入用）。"""

    initial_capital: float = 1_000_000.0
    lot_size: int = LOT_SIZE
    slippage_scale: float = 1.0

    def validate(self) -> None:
        if self.initial_capital <= 0:
            raise ValueError("initial_capital 须为正")
        if self.lot_size < 1:
            raise ValueError("lot_size 须>=1")
        if not 0.0 < self.slippage_scale:
            raise ValueError("slippage_scale 须为正")


@dataclass
class LegResult:
    """单腿回测产出（nav/exposure 为窗口内序列）。"""

    nav: pd.Series
    exposure: pd.Series
    metrics: dict[str, float] = field(default_factory=dict)
    trade_events: int = 0
    turnover_notional: float = 0.0
    per_symbol_trades: dict[str, int] = field(default_factory=dict)
    config_tag: str = ""


def compute_metrics(nav: pd.Series, exposure: pd.Series, trade_events: int, turnover_notional: float, initial_capital: float) -> dict[str, float]:
    """冻结 §5 指标族（Sharpe rf=0、244 交易日年化）。"""
    ret = nav.pct_change().dropna()
    if len(ret) < 2 or float(ret.std(ddof=1)) == 0.0:
        sharpe = 0.0
    else:
        sharpe = float(ret.mean() / ret.std(ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR))
    peak = nav.cummax()
    maxdd = float((nav / peak - 1.0).min())
    n_days = max(len(nav) - 1, 1)
    ann_return = float((nav.iloc[-1] / initial_capital) ** (TRADING_DAYS_PER_YEAR / n_days) - 1.0)
    years = n_days / TRADING_DAYS_PER_YEAR
    return {
        "sharpe": sharpe,
        "maxdd": maxdd,
        "ann_return": ann_return,
        "ann_turnover": float(turnover_notional / initial_capital / years),
        "avg_gross_exposure": float(exposure.mean()) if len(exposure) else 0.0,
        "trade_events": float(trade_events),
    }


def _resolve_window_index(daily: dict[str, pd.DataFrame], exec_symbols: list[str], start: str, end: str) -> pd.DatetimeIndex:
    """交易窗口=全标的日线索引交集 × [start, end] 切片（过短即失败）。"""
    idx = pd.DatetimeIndex(sorted(set(daily[exec_symbols[0]].index)))
    for sym in exec_symbols:
        idx = pd.DatetimeIndex(sorted(set(idx) & set(daily[sym].index)))
    idx = idx[(idx >= pd.Timestamp(start)) & (idx <= pd.Timestamp(end))]
    if len(idx) < 10:
        raise ValueError(f"交易窗口过短: {start}~{end} -> {len(idx)} 日")
    return idx


def _build_price_panels(daily: dict[str, pd.DataFrame], exec_symbols: list[str], idx: pd.DatetimeIndex) -> tuple[dict[str, pd.Series], dict[str, pd.Series], dict[str, pd.Series]]:
    """按窗口对齐 收盘/开盘/t-1 成交额三面板（滑点流动性输入=t-1 日该标的成交额）。"""
    close = {s: daily[s]["close"].reindex(idx) for s in exec_symbols}
    open_ = {s: daily[s]["open"].reindex(idx) for s in exec_symbols}
    prev_amount = {s: daily[s]["amount"].shift(1).reindex(idx) for s in exec_symbols}  # PIT: t-1 额
    return close, open_, prev_amount


def _day_desired_weights(
    exec_symbols: list[str],
    pkg_a_symbol: str,
    cap_a_t: float,
    a_target_t: float,
    cap_b_t: float,
    b_row: pd.Series,
) -> dict[str, float]:
    """当日 desired 权重（包目标 × 调度上限；同标的跨包叠加=两本独立账的净执行）。"""
    desired_w: dict[str, float] = {s: 0.0 for s in exec_symbols}
    wa = float(cap_a_t) * float(a_target_t) if not np.isnan(cap_a_t) else 0.0
    wb = float(cap_b_t) if not np.isnan(cap_b_t) else 0.0
    desired_w[pkg_a_symbol] = wa  # 包 A 固定标的（冻结 §3）
    for sym in b_row.index:
        desired_w[sym] = desired_w.get(sym, 0.0) + wb * float(b_row[sym])
    return desired_w


def _execute_day(  # noqa: long-param-list  冻结考试引擎逐日执行签名，绑定方=本文件 run_leg 单点调用；参数对象重构按 COORDINATION_LEDGER R-037 改裁属独立批（须同输入改前改后逐位数值回归）
    i: int,
    exec_symbols: list[str],
    open_: dict[str, pd.Series],
    prev_amount: dict[str, pd.Series],
    desired_w: dict[str, float],
    prev_close_nav: float,
    cfg: EngineConfig,
    shares: dict[str, int],
    per_symbol_trades: dict[str, int],
    cash: float,
    trade_events: int,
    turnover_notional: float,
) -> tuple[float, int, float]:
    """逐标的按 t 日开盘执行净差额（shares/per_symbol_trades 原地更新；返回更新后 cash/trade_events/turnover_notional）。"""
    for s in exec_symbols:
        px = open_[s].iloc[i]
        if pd.isna(px) or px <= 0:
            continue  # 当日无价=禁交易（防御）
        desired_value = desired_w[s] * prev_close_nav
        desired_shares = int(desired_value / (float(px) * cfg.lot_size)) * cfg.lot_size
        delta = desired_shares - shares[s]
        if delta == 0:
            continue
        notional = abs(delta) * float(px)
        liq = prev_amount[s].iloc[i]
        cost = total_cost_yuan(notional, None if pd.isna(liq) else float(liq), slippage_scale=cfg.slippage_scale)
        cash -= delta * float(px) + cost  # delta>0 买入流出；delta<0 卖出流入再扣费
        shares[s] = desired_shares
        trade_events += 1
        per_symbol_trades[s] = per_symbol_trades.get(s, 0) + 1
        turnover_notional += notional
    return cash, trade_events, turnover_notional


def run_leg(  # noqa: long-param-list  冻结考试引擎公共签名，契约绑定方=exam.py 3 处+tests/strategy_factory 6 处调用；参数对象重构按 R-037 改裁属独立批（须同输入逐位数值回归）
    sched_df: pd.DataFrame,
    pkg_a_targets: pd.Series,
    pkg_b_targets: pd.DataFrame,
    daily: dict[str, pd.DataFrame],
    exec_symbols: list[str],
    start: str,
    end: str,
    config: EngineConfig | None = None,
    config_tag: str = "",
    pkg_a_symbol: str = "510300",
) -> LegResult:
    """单腿回测（IS/OOS 同一实现，窗口切片在此完成；NAV 每窗口重置）。

    :param sched_df: 调度表（cap_A/cap_B 列；index=trade_date；PIT 语义由构造方保证）。
    :param pkg_a_targets: 包 A 目标仓位（全历史，{0,1}；t 收盘判定）。
    :param pkg_b_targets: 包 B 目标仓位（全历史，篮子 one-hot；t 收盘判定）。
    :param daily: 标的 → 聚合日线（open/close/amount；index=trade_date）。
    :param exec_symbols: 全部可交易标的（包 A 标的 ∪ 篮子）。
    :param pkg_a_symbol: 包 A 固定标的（冻结 §3=510300）。
    """
    cfg = config or EngineConfig()
    cfg.validate()
    required = {"cap_A", "cap_B"}
    if not required.issubset(sched_df.columns):
        raise KeyError(f"调度表缺列: {required - set(sched_df.columns)}")
    idx = _resolve_window_index(daily, exec_symbols, start, end)

    close, open_, prev_amount = _build_price_panels(daily, exec_symbols, idx)

    a_t = pkg_a_targets.shift(1).reindex(idx).fillna(0.0)  # t-1 收盘判定
    b_t = pkg_b_targets.shift(1).reindex(idx).fillna(0.0)
    cap_a = sched_df["cap_A"].reindex(idx).astype(float)
    cap_b = sched_df["cap_B"].reindex(idx).astype(float)

    cash = cfg.initial_capital
    shares = {s: 0 for s in exec_symbols}
    navs: list[float] = []
    exposures: list[float] = []
    trade_events = 0
    turnover_notional = 0.0
    per_symbol_trades = {s: 0 for s in exec_symbols}

    for i, day in enumerate(idx):
        prev_close_nav = cash + sum(shares[s] * float(close[s].iloc[i - 1]) for s in exec_symbols) if i > 0 else cfg.initial_capital
        desired_w = _day_desired_weights(exec_symbols, pkg_a_symbol, cap_a.iloc[i], a_t.iloc[i], cap_b.iloc[i], b_t.iloc[i])
        cash, trade_events, turnover_notional = _execute_day(
            i, exec_symbols, open_, prev_amount, desired_w, prev_close_nav,
            cfg, shares, per_symbol_trades, cash, trade_events, turnover_notional,
        )
        nav_t = cash + sum(shares[s] * float(close[s].iloc[i]) for s in exec_symbols)
        gross = sum(shares[s] * float(close[s].iloc[i]) for s in exec_symbols)
        navs.append(nav_t)
        exposures.append(0.0 if nav_t <= 0 else gross / nav_t)
    nav = pd.Series(navs, index=idx, name="nav")
    exposure = pd.Series(exposures, index=idx, name="exposure")
    return LegResult(
        nav=nav,
        exposure=exposure,
        metrics=compute_metrics(nav, exposure, trade_events, turnover_notional, cfg.initial_capital),
        trade_events=trade_events,
        turnover_notional=turnover_notional,
        per_symbol_trades=per_symbol_trades,
        config_tag=config_tag,
    )
