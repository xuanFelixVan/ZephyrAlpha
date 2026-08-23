# [BLUEPRINT] MOD-SELL-018 | docs/03_modules/MOD-SELL-018/
# [MODULE] zephyr.sell_decision.core.t_trade_coordinator
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] D-EX-CORE(日内执行) ; MOD-POS-018(盘中仓位约束复核)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] T+1规则内生(两腿卖出量≤可卖底仓,当日买入不可卖); 日终仓位复原(买回量=卖出量); 净价差=预期价差−往返成本,>min_edge才viable; 成本含做T额外成本(宪章§3约束一); 计划量超可卖截断并留痕; 纯函数可单测
# [MODIFY-GUARD] docs/03_modules/MOD-SELL-018/
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidTTradeInputError(ZA-SELL-0024)
# [TESTS] tests/sell_decision/test_t_trade_coordinator.py
# [A_module] module_id=MOD-SELL-018 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""T Trade Coordinator — 做T 协调器 (MOD-SELL-018，T+1 规则内)

A 股 T+1 下的日内做T（利用底仓赚日内价差、日终仓位复原）：

  - REVERSE_T（倒T，先卖后买）：高位卖出可卖底仓，日内低位买回；
  - POSITIVE_T（正T，先买后卖）：低位先买，拉高后卖出——**卖出的
    只能是原可卖底仓**（当日买入部分 T+1 前冻结不可卖）。

内生约束：
  1. 两腿卖出量 ≤ T+1 可卖权重（计划量超出截断并留痕）；
  2. 买回量 = 卖出量（日终仓位复原，不留隔夜敞口变化）；
  3. 净价差 = 预期价差 − 往返成本（佣金+印花税+滑点+做T额外成本，
     宪章 §3 约束一），净价差 > min_edge 才 viable（不值得做的T不做）。

本模块只产出做T 计划（可行性+两腿权重），不执行；与选股策略零耦合
（三维解耦——做T 是执行层增强，不改 what）。

纪律：纯函数、无 IO；价差预期与成本由调用方注入。
Version: 1.0.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "InvalidTTradeInputError",
    "TTradeDirection",
    "TTradeInput",
    "TTradePlan",
    "plan_t_trade",
]


class TTradeDirection(str, Enum):
    """做T 方向。"""

    REVERSE_T = "REVERSE_T"  # 倒T：先卖后买（高位卖低位接回）
    POSITIVE_T = "POSITIVE_T"  # 正T：先买后卖（低位买，卖出用原底仓）


class InvalidTTradeInputError(ZephyrBaseError):
    """做T 规划输入非法（权重/成本/边际越界）。"""

    error_code = "ZA-SELL-0024"


@dataclass(frozen=True)
class TTradeInput:
    """做T 规划输入（>4 参数收 dataclass）。

    Attributes:
        symbol: 标的代码
        direction: 做T 方向（正T/倒T）
        sellable_weight: T+1 可卖底仓权重 ≥0
        planned_weight: 计划做T 权重 ≥0（超出可卖将截断）
        expected_spread_pct: 预期日内价差（倒T=卖价−买回价，正T=卖价−买价，相对比例）
        round_trip_cost_pct: 往返成本 ≥0（佣金+印花税+滑点+做T额外成本）
        min_edge_pct: 最小净价差 ≥0（低于此不值得做）
    """

    symbol: str
    direction: TTradeDirection
    sellable_weight: float
    planned_weight: float
    expected_spread_pct: float
    round_trip_cost_pct: float
    min_edge_pct: float


@dataclass(frozen=True)
class TTradePlan:
    """做T 计划（frozen 不可变）。

    Attributes:
        symbol: 标的
        direction: 方向
        viable: 是否值得做（净价差>min_edge 且有可卖量）
        sell_weight: 卖出腿权重（≤可卖）
        buyback_weight: 买回腿权重（=sell_weight，日终复原）
        expected_spread_pct: 预期价差
        round_trip_cost_pct: 往返成本
        net_edge_pct: 净价差
        constraints: 约束留痕（T+1 截断等）
    """

    symbol: str
    direction: TTradeDirection
    viable: bool
    sell_weight: float
    buyback_weight: float
    expected_spread_pct: float
    round_trip_cost_pct: float
    net_edge_pct: float
    constraints: tuple[str, ...] = field(default_factory=tuple)


def plan_t_trade(intent: TTradeInput) -> TTradePlan:
    """规划做T（纯函数，Fail-Closed：不值得做→viable=False）。

    Raises:
        InvalidTTradeInputError: 输入非法
    """
    if not intent.symbol:
        raise InvalidTTradeInputError("symbol 为空")
    if not isinstance(intent.direction, TTradeDirection):
        raise InvalidTTradeInputError(f"direction 非法，got {intent.direction!r}")
    for name, v in (
        ("sellable_weight", intent.sellable_weight),
        ("planned_weight", intent.planned_weight),
        ("round_trip_cost_pct", intent.round_trip_cost_pct),
        ("min_edge_pct", intent.min_edge_pct),
    ):
        if not math.isfinite(v) or v < 0.0:
            raise InvalidTTradeInputError(f"{name} 非法（须为有限非负值），got {v}")
    if not math.isfinite(intent.expected_spread_pct):
        raise InvalidTTradeInputError(
            f"expected_spread_pct 非法（须为有限值），got {intent.expected_spread_pct}"
        )

    constraints: list[str] = []

    # T+1 内生：卖出腿 ≤ 可卖底仓（正T的卖出腿同样受此限）
    sell_weight = min(intent.planned_weight, intent.sellable_weight)
    if intent.planned_weight > intent.sellable_weight + 1e-12:
        constraints.append(
            f"T+1 约束：计划做T {intent.planned_weight:.4f} 超可卖底仓 "
            f"{intent.sellable_weight:.4f}，截断至可卖量（当日买入不可卖）"
        )

    net_edge = intent.expected_spread_pct - intent.round_trip_cost_pct
    viable = sell_weight > 0.0 and net_edge > intent.min_edge_pct

    return TTradePlan(
        symbol=intent.symbol,
        direction=intent.direction,
        viable=viable,
        sell_weight=sell_weight,
        buyback_weight=sell_weight,  # 日终仓位复原
        expected_spread_pct=intent.expected_spread_pct,
        round_trip_cost_pct=intent.round_trip_cost_pct,
        net_edge_pct=net_edge,
        constraints=tuple(constraints),
    )
