# [BLUEPRINT] 35_drawdown_protocol_impl | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/35_drawdown_protocol_impl.md | §3.5.1/§6.14
# [MODULE] zephyr.risk.core.drawdown_liquidation_guard
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] stop_loss.execute_kill_switch_liquidation调用方(撤单前预检/全清轮询超时); RiskOrchestrator(§6.5 接线位)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 撤单率=cancelled/total(分母0→0率不预警); ≥12%预警留3%buffer(§6.14,新规红线15%); ≥15%硬上限blocked(剩余撤单额度=max(0,floor(15%×total)-cancelled)); 全清超时默认30秒未清零→告警人工介入(不自动强平,A股T+1); 已清零不告警; 负输入抛错
# [MODIFY-GUARD] tests/risk/test_drawdown_liquidation_guard.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidLiquidationGuardInputError(ZA-RK-0066)
# [TESTS] tests/risk/test_drawdown_liquidation_guard.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: 撤单计数对(cancelled_count+total_order_count) + 阈值对(warn12%/hard15%, A股2026新规)
# I2: 全清计时对(started_monotonic+now_monotonic, 秒) + remaining_positions残余持仓 + timeout_seconds=30
# F1: check_cancel_rate(撤单率三档: <12%正常 / 12-15%预警留buffer / ≥15% blocked+剩余额度)
# F2: check_liquidation_timeout(elapsed>30s且残余非空→LiquidationTimeoutAlert人工介入; 否则None)
# O1: CancelRatePrecheck(rate+warning+blocked+remaining_budget) / LiquidationTimeoutAlert|None
# [/ALGO_FLOW]
"""D_RISK — Kill Switch 全清执行守卫（35 号 memo §6.14 施工，§3.5.1 A 股 2026 新规适配）。

痛点（§6.14 P0）：15 笔/秒分片平仓已施工（v1.39.0），剩余两项未落——
① 撤单率预检：Kill Switch 触发后大量撤单可能撞单日撤单率 15% 新规红线；
② 全清超时告警：分片平仓窗口内持仓仍暴露（Ghost 风险窗口扩大），
   超时未全清需告警人工介入。

本模块落地（函数级，对齐 §3.5.1 裁决"撤单前检查日撤单率，超 12% 预警留 3%
buffer；30 秒未全清即告警人工介入"）：
  - check_cancel_rate：撤单率 = 已撤/总委托；≥ 12% 预警（留 3% buffer），
    ≥ 15% blocked（剩余撤单额度 = ⌊15%×total⌋ − cancelled，负数归零）——
    调用方据此"优先撤关键挂单，放弃小额挂单让其自然到期"（§3.5.1）。
  - check_liquidation_timeout：全清轮询守卫——残余持仓非空且耗时超阈值
    （默认 30s）→ 告警人工介入；已清零或未超时 → None。
    告警不自动强平（A 股 T+1 + 可能误判，对齐 Ghost 检测处置原则）。

时间口径：单调节拍秒（time.monotonic 对），测试可注入，无墙钟依赖。
SSoT: 35_drawdown_protocol_impl §3.5.1 + §6.14
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Final, Mapping

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "InvalidLiquidationGuardInputError",
    "CancelRatePrecheck",
    "LiquidationTimeoutAlert",
    "check_cancel_rate",
    "check_liquidation_timeout",
]

_logger = logging.getLogger(__name__)

#: A 股 2026 新规：单日撤单率红线 15%（§3.5.1）
DEFAULT_HARD_CANCEL_RATE: Final = 0.15
#: 预警阈值 12%（留 3% buffer，§6.14）
DEFAULT_WARN_CANCEL_RATE: Final = 0.12
#: 全清超时默认 30 秒（§6.14）
DEFAULT_LIQUIDATION_TIMEOUT_SECONDS: Final = 30.0


class InvalidLiquidationGuardInputError(ZephyrBaseError):
    """清算守卫输入非法（计数为负/阈值越界/时间对倒置）。"""

    error_code = "ZA-RK-0066"


@dataclass(frozen=True)
class CancelRatePrecheck:
    """撤单率预检结果（§6.14 ①）。

    Attributes:
        cancel_rate: 当前日撤单率（cancelled/total；total=0 → 0.0）
        warning: ≥ 预警阈值（12%）——留 3% buffer，提示优先撤关键挂单
        blocked: ≥ 硬上限（15%）——禁止继续撤单（小额挂单留自然到期）
        remaining_cancel_budget: 剩余撤单额度（笔；blocked 时 0）
        reason: 人类可读说明
    """

    cancel_rate: float
    warning: bool
    blocked: bool
    remaining_cancel_budget: int
    reason: str


@dataclass(frozen=True)
class LiquidationTimeoutAlert:
    """全清超时告警（§6.14 ②，人工介入信号，不自动强平）。

    Attributes:
        elapsed_seconds: 全清已耗时（秒）
        timeout_seconds: 超时阈值（秒）
        remaining_symbols: 未清零标的列表
        reason: 人类可读说明
    """

    elapsed_seconds: float
    timeout_seconds: float
    remaining_symbols: tuple[str, ...] = field(default_factory=tuple)
    reason: str = ""


def check_cancel_rate(
    cancelled_count: int,
    total_order_count: int,
    *,
    warn_threshold: float = DEFAULT_WARN_CANCEL_RATE,
    hard_limit: float = DEFAULT_HARD_CANCEL_RATE,
) -> CancelRatePrecheck:
    """撤单率预检（撤挂单前调用）：超 12% 预警留 3% buffer，超 15% 禁止续撤。

    Args:
        cancelled_count: 当日已撤单笔数（≥0）
        total_order_count: 当日总委托笔数（≥0；0=无撤单率概念，不预警）
        warn_threshold: 预警阈值（默认 0.12，留 3% buffer）
        hard_limit: 新规红线（默认 0.15）

    Returns:
        CancelRatePrecheck
    """
    if cancelled_count < 0 or total_order_count < 0:
        raise InvalidLiquidationGuardInputError(f"计数须 >= 0: cancelled={cancelled_count} total={total_order_count}")
    if cancelled_count > total_order_count:
        raise InvalidLiquidationGuardInputError(f"已撤 {cancelled_count} 不可超过总委托 {total_order_count}")
    if not 0 < warn_threshold < hard_limit < 1:
        raise InvalidLiquidationGuardInputError(f"阈值须满足 0 < warn < hard < 1: {warn_threshold}/{hard_limit}")
    if total_order_count == 0:
        return CancelRatePrecheck(
            cancel_rate=0.0,
            warning=False,
            blocked=False,
            remaining_cancel_budget=0,
            reason="当日无委托，无撤单率约束",
        )
    rate = cancelled_count / total_order_count
    budget = max(0, math.floor(hard_limit * total_order_count) - cancelled_count)
    blocked = rate >= hard_limit or budget <= 0
    warning = rate >= warn_threshold
    if blocked:
        reason = f"撤单率 {rate:.1%} 剩余额度 0（红线 {hard_limit:.0%}），禁止继续撤单（小额挂单留自然到期，§3.5.1）"
        _logger.critical("CANCEL_RATE_BLOCKED rate=%.3f budget=%d", rate, budget)
    elif warning:
        reason = (
            f"撤单率 {rate:.1%} 超预警 {warn_threshold:.0%}（红线 {hard_limit:.0%} "
            f"留 buffer），优先撤关键挂单，剩余额度 {budget} 笔"
        )
        _logger.warning("CANCEL_RATE_WARNING rate=%.3f budget=%d", rate, budget)
    else:
        reason = f"撤单率 {rate:.1%} 正常（预警 {warn_threshold:.0%}）"
    return CancelRatePrecheck(
        cancel_rate=rate,
        warning=warning,
        blocked=blocked,
        remaining_cancel_budget=0 if blocked else budget,
        reason=reason,
    )


def check_liquidation_timeout(
    *,
    started_monotonic: float,
    now_monotonic: float,
    remaining_positions: Mapping[str, Any],
    timeout_seconds: float = DEFAULT_LIQUIDATION_TIMEOUT_SECONDS,
) -> LiquidationTimeoutAlert | None:
    """全清超时告警（全清轮询守卫）：残余非空且超时 → 告警人工介入。

    Args:
        started_monotonic: 全清开始节拍（time.monotonic 秒）
        now_monotonic: 当前节拍（同口径秒）
        remaining_positions: 残余持仓 {symbol: qty/info}（空=已全清）
        timeout_seconds: 超时阈值（默认 30 秒，§6.14）

    Returns:
        LiquidationTimeoutAlert（超时且残余非空）；否则 None
    """
    if timeout_seconds <= 0:
        raise InvalidLiquidationGuardInputError(f"timeout_seconds 须 > 0, got {timeout_seconds}")
    elapsed = now_monotonic - started_monotonic
    if elapsed < 0:
        raise InvalidLiquidationGuardInputError(f"时间对倒置: now({now_monotonic}) < started({started_monotonic})")
    remaining = tuple(
        sym
        for sym, info in remaining_positions.items()
        if (info.get("qty", 0) if isinstance(info, Mapping) else info) != 0
    )
    if not remaining or elapsed <= timeout_seconds:
        return None
    reason = (
        f"全清 {elapsed:.1f}s 超 {timeout_seconds:.0f}s 仍未清零"
        f"（残余 {len(remaining)} 只: {list(remaining)}），人工介入"
    )
    _logger.critical(
        "LIQUIDATION_TIMEOUT elapsed=%.1f timeout=%.0f remaining=%s",
        elapsed,
        timeout_seconds,
        list(remaining),
    )
    return LiquidationTimeoutAlert(
        elapsed_seconds=elapsed,
        timeout_seconds=timeout_seconds,
        remaining_symbols=remaining,
        reason=reason,
    )
