# [BLUEPRINT] 35_drawdown_protocol_impl | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/35_drawdown_protocol_impl.md | §3.5/§6.2
# [MODULE] zephyr.risk.core.drawdown_consecutive_loss
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] RiskOrchestrator(§6.5 接线位); position_sizing_engine(cap_multiplier消费)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 连续亏损定义=日pnl<0(pnl=0非亏损,重置连亏计数); 连亏≥5日→降仓50%(cap_multiplier=0.5); 未达阈值cap_multiplier=1.0; 盈利日即重置计数; 与日度熔断(§3.6)/周月限额(ashare引擎)正交叠加取最严
# [MODIFY-GUARD] tests/risk/test_drawdown_consecutive_loss.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidConsecutiveLossInputError(ZA-RK-0064)
# [TESTS] tests/risk/test_drawdown_consecutive_loss.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: 日PnL序列(list[float], 负=亏) 或 ConsecutiveLossTracker逐日update(trade_date+pnl)
# I2: ConsecutiveLossConfig(consecutive_days=5+reduction_pct=0.5, §6.2/§2.5.5表第3行)
# F1: check_consecutive_loss(纯函数: 序列末尾连续pnl<0计数≥阈值→触发)
# F2: ConsecutiveLossTracker.update(有状态: 逐日推进, pnl<0计数+1否则重置, 同日幂等)
# O1: ConsecutiveLossAlert(triggered+consecutive_loss_days+cap_multiplier+reason)
# [/ALGO_FLOW]
"""D_RISK — 连续亏损降仓触发器（35 号 memo §6.2 施工，§3.5 触发条件表第 3 行）。

痛点：§2.5.5 Kill Switch 表"连续 5 天亏损 → 降仓至 50%"代码无独立实现
（§6.2 P1）。连亏是"时间维度"风险信号——单日幅度都不大但持续阴亏，
日度熔断（§3.6 幅度维度）与周/月限额（ashare 引擎）均不一定触发。

本模块落地：
  - check_consecutive_loss：纯函数，日 PnL 序列末尾连续亏损天数 ≥ 阈值
    → cap_multiplier=0.5（未达阈值 1.0，调用方取最严乘性叠加）。
  - ConsecutiveLossTracker：有状态逐日推进版（盘前日更），盈利日/零 PnL
    重置计数，同日重复 update 幂等（以最新 pnl 为准）。
  - 语义对齐 §6.2：默认 5 日 / 降仓 50%（C 类可调参数）。

边界：pnl == 0 非亏损日（重置计数）；NaN 输入拒绝（fail-closed）。
SSoT: 35_drawdown_protocol_impl §3.5 触发条件表 + §6.2
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from datetime import date
from typing import Final, Sequence

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "InvalidConsecutiveLossInputError",
    "ConsecutiveLossConfig",
    "ConsecutiveLossAlert",
    "ConsecutiveLossTracker",
    "check_consecutive_loss",
]

_logger = logging.getLogger(__name__)


class InvalidConsecutiveLossInputError(ZephyrBaseError):
    """连续亏损检测输入非法（NaN/配置越界/日期倒退）。"""

    error_code = "ZA-RK-0064"


@dataclass(frozen=True)
class ConsecutiveLossConfig:
    """连续亏损降仓配置（C 类可调参数，默认值真源=§6.2/§2.5.5 表第 3 行）。

    Attributes:
        consecutive_days: 触发连亏天数（默认 5）
        reduction_pct: 降仓比例（默认 0.5=降仓 50% → cap_multiplier=0.5）
    """

    consecutive_days: int = 5
    reduction_pct: float = 0.5

    def __post_init__(self) -> None:
        if self.consecutive_days < 1:
            raise InvalidConsecutiveLossInputError(
                f"consecutive_days 须 >= 1, got {self.consecutive_days}"
            )
        if not 0 < self.reduction_pct < 1:
            raise InvalidConsecutiveLossInputError(
                f"reduction_pct 须在 (0,1), got {self.reduction_pct}"
            )


@dataclass(frozen=True)
class ConsecutiveLossAlert:
    """连续亏损检测结果。

    Attributes:
        triggered: 是否触发（连亏 ≥ consecutive_days）
        consecutive_loss_days: 当前连续亏损天数
        cap_multiplier: 仓位乘数（触发=1-reduction_pct；未触发=1.0）
        reason: 人类可读原因
    """

    triggered: bool
    consecutive_loss_days: int
    cap_multiplier: float
    reason: str


def _validate_pnl(pnl: float) -> None:
    if not isinstance(pnl, (int, float)) or math.isnan(pnl) or math.isinf(pnl):
        raise InvalidConsecutiveLossInputError(f"pnl 非法: {pnl!r}")


def check_consecutive_loss(
    daily_pnls: Sequence[float],
    config: ConsecutiveLossConfig | None = None,
) -> ConsecutiveLossAlert:
    """连续亏损检测（纯函数）：序列末尾连续 pnl<0 天数 ≥ 阈值 → 降仓。

    Args:
        daily_pnls: 日 PnL 序列（旧→新；负=亏损；0=非亏损重置连亏）
        config: 检测配置（None=默认 5 日/50%）

    Returns:
        ConsecutiveLossAlert（空序列 → 未触发）
    """
    cfg = config or ConsecutiveLossConfig()
    streak = 0
    for pnl in reversed(daily_pnls):
        _validate_pnl(pnl)
        if pnl < 0:
            streak += 1
        else:
            break
    triggered = streak >= cfg.consecutive_days
    multiplier = 1.0 - cfg.reduction_pct if triggered else 1.0
    reason = (
        f"连续 {streak} 天亏损 >= {cfg.consecutive_days} 天，降仓 {cfg.reduction_pct:.0%}"
        if triggered else f"连续亏损 {streak} 天未达 {cfg.consecutive_days} 天阈值"
    )
    if triggered:
        _logger.warning(
            "CONSECUTIVE_LOSS_TRIGGERED streak=%d threshold=%d multiplier=%.2f",
            streak, cfg.consecutive_days, multiplier,
        )
    return ConsecutiveLossAlert(
        triggered=triggered,
        consecutive_loss_days=streak,
        cap_multiplier=multiplier,
        reason=reason,
    )


class ConsecutiveLossTracker:
    """连续亏损有状态追踪器（盘前日更版）。

    用法:
        tracker = ConsecutiveLossTracker()
        alert = tracker.update(trade_date=d, pnl=-1200.0)
        if alert.triggered: ...  # 消费 alert.cap_multiplier

    同日重复 update 幂等（以最新 pnl 重算当日，不重复推进）；
    日期倒退抛 InvalidConsecutiveLossInputError。
    """

    def __init__(self, config: ConsecutiveLossConfig | None = None) -> None:
        self._config = config or ConsecutiveLossConfig()
        self._streak = 0
        self._prev_day_streak = 0  # 前一交易日收盘时的 streak（同日重推基准）
        self._last_date: date | None = None

    @property
    def consecutive_loss_days(self) -> int:
        return self._streak

    def update(self, trade_date: date, pnl: float) -> ConsecutiveLossAlert:
        """逐日推进。pnl<0 连亏+1；pnl>=0 重置。同日幂等（以前日 streak 重算当日）。"""
        _validate_pnl(pnl)
        if self._last_date is not None and trade_date < self._last_date:
            raise InvalidConsecutiveLossInputError(
                f"trade_date 倒退: {trade_date} < {self._last_date}"
            )
        is_loss = pnl < 0
        if trade_date != self._last_date:
            self._prev_day_streak = self._streak
        self._streak = self._prev_day_streak + 1 if is_loss else 0
        self._last_date = trade_date

        cfg = self._config
        triggered = self._streak >= cfg.consecutive_days
        multiplier = 1.0 - cfg.reduction_pct if triggered else 1.0
        reason = (
            f"连续 {self._streak} 天亏损 >= {cfg.consecutive_days} 天，降仓 {cfg.reduction_pct:.0%}"
            if triggered else f"连续亏损 {self._streak} 天未达 {cfg.consecutive_days} 天阈值"
        )
        if triggered:
            _logger.warning(
                "CONSECUTIVE_LOSS_TRIGGERED date=%s streak=%d multiplier=%.2f",
                trade_date, self._streak, multiplier,
            )
        return ConsecutiveLossAlert(
            triggered=triggered,
            consecutive_loss_days=self._streak,
            cap_multiplier=multiplier,
            reason=reason,
        )
