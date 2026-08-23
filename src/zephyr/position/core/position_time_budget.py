# [BLUEPRINT] MOD-POS-015 | docs/03_modules/MOD-POS-015/
# [MODULE] zephyr.position.core.position_time_budget
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] D-SELL-DECISION(时间止损信号源) ; MOD-SELL-013(离场情景规划)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 持有天数=自然日差(as_of−entry_date); 三态单调划分(WITHIN<warn_ratio≤APPROACHING,持有>预算→EXPIRED); 预算当天不算到期; 交易日历换算归调用方(本模块不认交易日,只认自然日); 纯函数可单测
# [MODIFY-GUARD] docs/03_modules/MOD-POS-015/
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidTimeBudgetInputError(ZA-POS-0024)
# [TESTS] tests/position/test_position_time_budget.py
# [A_module] module_id=MOD-POS-015 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Position Time Budget — 持仓时间预算 (MOD-POS-015)

时间止损的仓位侧落点：每个持仓带最大持有时间预算（按策略/标的类别由
调用方给定），按持有比例划分三态：

  - WITHIN（held/max < warn_ratio）：预算内；
  - APPROACHING（warn_ratio ≤ held/max ≤ 1）：临近到期，预警；
  - EXPIRED（held > max）：超出时间预算——时间止损信号源（喂卖出域，
    本模块只标记不执行，三维解耦）。

口径声明：持有天数按**自然日**差计算；交易日换算（如"持有 20 个交易
日"→自然日预算）是调用方职责（本模块不依赖交易日历真源）。

纪律：纯函数、无 IO；entry_date/as_of 由调用方注入（可测试替换）。
Version: 1.0.0
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "InvalidTimeBudgetInputError",
    "PositionTimeStatus",
    "TimeBudgetPosition",
    "TimeBudgetReport",
    "TimeBudgetStatus",
    "check_time_budgets",
]

_DEFAULT_WARN_RATIO: Final = 0.8


class TimeBudgetStatus(str, Enum):
    """时间预算三态。"""

    WITHIN = "WITHIN"  # 预算内
    APPROACHING = "APPROACHING"  # 临近到期（≥warn_ratio）
    EXPIRED = "EXPIRED"  # 超出预算


class InvalidTimeBudgetInputError(ZephyrBaseError):
    """时间预算输入非法（预算<1/入场晚于基准日/预警比例越界）。"""

    error_code = "ZA-POS-0024"


@dataclass(frozen=True)
class TimeBudgetPosition:
    """单持仓时间预算。

    Attributes:
        entry_date: 入场日（自然日）
        max_holding_days: 最大持有天数预算（自然日，≥1）
        label: 可选标签（策略/类别留痕，不参与计算）
    """

    entry_date: date
    max_holding_days: int
    label: str = ""


@dataclass(frozen=True)
class PositionTimeStatus:
    """单持仓时间预算状态。

    Attributes:
        days_held: 已持有自然日数
        max_holding_days: 预算
        ratio: 持有比例（days_held / max_holding_days）
        status: 三态判定
    """

    days_held: int
    max_holding_days: int
    ratio: float
    status: TimeBudgetStatus


@dataclass(frozen=True)
class TimeBudgetReport:
    """时间预算巡检报告（frozen 不可变）。

    Attributes:
        positions: {symbol: PositionTimeStatus}
        expired: 到期标的（按代码排序）
        approaching: 临近到期标的（按代码排序）
        any_expired: 是否存在到期持仓
    """

    positions: dict[str, PositionTimeStatus]
    expired: tuple[str, ...]
    approaching: tuple[str, ...]
    any_expired: bool
    warnings: tuple[str, ...] = field(default_factory=tuple)


def check_time_budgets(
    positions: Mapping[str, TimeBudgetPosition],
    *,
    as_of: date,
    warn_ratio: float = _DEFAULT_WARN_RATIO,
) -> TimeBudgetReport:
    """检查持仓时间预算（纯函数）。

    Args:
        positions: {symbol: TimeBudgetPosition}
        as_of: 基准日（注入可测试替换）
        warn_ratio: 临近到期预警比例 ∈(0,1)（默认 0.8）

    Returns:
        TimeBudgetReport

    Raises:
        InvalidTimeBudgetInputError: 预算<1/入场晚于基准日/预警比例越界
    """
    if not math.isfinite(warn_ratio) or warn_ratio <= 0.0 or warn_ratio >= 1.0:
        raise InvalidTimeBudgetInputError(f"warn_ratio 非法（须 ∈(0,1)），got {warn_ratio}")

    detail: dict[str, PositionTimeStatus] = {}
    expired: list[str] = []
    approaching: list[str] = []
    warnings: list[str] = []

    for sym in sorted(positions):
        pos = positions[sym]
        if pos.max_holding_days < 1:
            raise InvalidTimeBudgetInputError(
                f"标的 {sym} 时间预算非法（须 ≥1 天），got {pos.max_holding_days}"
            )
        held = (as_of - pos.entry_date).days
        if held < 0:
            raise InvalidTimeBudgetInputError(
                f"标的 {sym} 入场日 {pos.entry_date} 晚于基准日 {as_of}（数据异常）"
            )
        ratio = held / pos.max_holding_days
        if held > pos.max_holding_days:
            status = TimeBudgetStatus.EXPIRED
            expired.append(sym)
            warnings.append(
                f"标的 {sym} 持有 {held} 天超时间预算 {pos.max_holding_days} 天（时间止损候选）"
            )
        elif ratio >= warn_ratio:
            status = TimeBudgetStatus.APPROACHING
            approaching.append(sym)
        else:
            status = TimeBudgetStatus.WITHIN
        detail[sym] = PositionTimeStatus(
            days_held=held,
            max_holding_days=pos.max_holding_days,
            ratio=ratio,
            status=status,
        )

    return TimeBudgetReport(
        positions=detail,
        expired=tuple(expired),
        approaching=tuple(approaching),
        any_expired=bool(expired),
        warnings=tuple(warnings),
    )
