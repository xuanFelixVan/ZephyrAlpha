# [MODULE] zephyr.ex_core.cancel_rate_guard
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib
# [CONSUMERS] ex_core.order_manager ; ex_core.trading_session
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 撤单率>15%冻结新下单;>12%禁止撤单;限频15笔/秒
# [MODIFY-GUARD] 40_execution_broker.md §决策⑫
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_core/test_cancel_rate_guard.py
# [TTL] permanent

"""撤单率滚动监控降级（40_execution_broker §决策⑫ gap 7 施工）。

程序化交易监管合规生存项（《程序化交易管理实施细则》2025-07-07 全面实施）：
- 滚动 500 笔窗口监控撤单率
- >12% 预警线 → 降级"只挂不撤"（禁止撤单重挂，等成交或收盘）
- >15% 硬线 → 冻结全账户新下单，告警人工介入
- 内部限频 15 笔/秒（报单+撤单，保守安全垫，远低于法定 300 笔/秒）

为何 12% 预警而非等到 15%：滚动窗口有滞后性，等看到 15% 时实际可能已超，
留 3% 缓冲是合规安全垫。

依据：40_execution_broker.md v2.3.0 §决策⑫
Version: 1.0.0
"""

from __future__ import annotations

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum

__all__ = [
    "CancelRateStatus",
    "CancelRateGuard",
]

_logger = logging.getLogger(__name__)


class CancelRateStatus(str, Enum):
    """撤单率监控状态。"""

    NORMAL = "normal"                  # 正常：可挂可撤
    WARN_ONLY_PLACE = "warn_only_place"  # 预警：只挂不撤（撤单率 >12%）
    FROZEN = "frozen"                  # 冻结：禁止新下单（撤单率 >15%）


@dataclass
class CancelRateGuard:
    """撤单率滚动监控降级守卫。

    维护最近 window_size 笔已完结报单（成交或撤单）的记录，计算滚动撤单率，
    按阈值降级。同时维护每秒提交计数实现 15 笔/秒限频。

    Attributes:
        window_size: 滚动窗口大小（已完结报单数），默认 500
        warn_threshold: 预警线（只挂不撤），默认 0.12
        freeze_threshold: 冻结线（禁止新下单），默认 0.15
        rate_limit_per_sec: 每秒报单+撤单上限，默认 15
    """

    window_size: int = 500
    warn_threshold: float = 0.12
    freeze_threshold: float = 0.15
    rate_limit_per_sec: int = 15
    # 已完结报单结果窗口："cancel" or "fill"
    _resolved: deque = field(default_factory=lambda: deque(maxlen=500), repr=False)
    # 最近 1 秒的提交时间戳（限频）
    _submit_ts: deque = field(default_factory=deque, repr=False)

    def __post_init__(self) -> None:
        # 同步 maxlen 与 window_size
        if self._resolved.maxlen != self.window_size:
            self._resolved = deque(self._resolved, maxlen=self.window_size)

    # ── 状态查询 ──

    @property
    def cancel_rate(self) -> float:
        """当前滚动撤单率 = 撤单数 / 已完结报单数。"""
        if not self._resolved:
            return 0.0
        cancels = sum(1 for e in self._resolved if e == "cancel")
        return cancels / len(self._resolved)

    @property
    def status(self) -> CancelRateStatus:
        """当前监控状态。"""
        rate = self.cancel_rate
        if rate > self.freeze_threshold:
            return CancelRateStatus.FROZEN
        if rate > self.warn_threshold:
            return CancelRateStatus.WARN_ONLY_PLACE
        return CancelRateStatus.NORMAL

    @property
    def total_resolved(self) -> int:
        """已完结报单总数（窗口内）。"""
        return len(self._resolved)

    @property
    def total_cancels(self) -> int:
        """撤单总数（窗口内）。"""
        return sum(1 for e in self._resolved if e == "cancel")

    # ── 决策接口 ──

    def can_place_order(self) -> bool:
        """是否允许新下单（FROZEN 状态禁止）。"""
        if self.status is CancelRateStatus.FROZEN:
            _logger.error(
                "CancelRateGuard FROZEN: cancel_rate=%.2f%% > %.0f%%, "
                "全账户冻结新下单，需人工介入",
                self.cancel_rate * 100,
                self.freeze_threshold * 100,
            )
            return False
        return True

    def can_cancel_order(self) -> bool:
        """是否允许撤单（WARN_ONLY_PLACE / FROZEN 状态禁止）。"""
        status = self.status
        if status is CancelRateStatus.FROZEN:
            _logger.error(
                "CancelRateGuard FROZEN: 禁止撤单（账户已冻结）"
            )
            return False
        if status is CancelRateStatus.WARN_ONLY_PLACE:
            _logger.warning(
                "CancelRateGuard WARN_ONLY_PLACE: cancel_rate=%.2f%% > %.0f%%, "
                "只挂不撤模式，禁止撤单重挂",
                self.cancel_rate * 100,
                self.warn_threshold * 100,
            )
            return False
        return True

    def can_submit_now(self) -> bool:
        """限频检查：是否允许现在提交报单/撤单（15 笔/秒）。

        检查最近 1 秒内的提交次数是否已达上限。注意：此方法仅检查限频，
        不检查撤单率状态（can_place_order/can_cancel_order 分别检查）。
        """
        now = time.monotonic()
        # 清理 1 秒前的记录
        cutoff = now - 1.0
        while self._submit_ts and self._submit_ts[0] < cutoff:
            self._submit_ts.popleft()
        if len(self._submit_ts) >= self.rate_limit_per_sec:
            _logger.warning(
                "CancelRateGuard rate limit: %d submits in last 1s >= %d",
                len(self._submit_ts),
                self.rate_limit_per_sec,
            )
            return False
        return True

    # ── 事件记录 ──

    def record_submit(self) -> None:
        """记录一笔报单提交（用于限频计数）。

        注意：报单提交时尚未完结（可能成交或撤单），不计入撤单率窗口。
        撤单率仅在 record_fill / record_cancel 时更新。
        """
        self._submit_ts.append(time.monotonic())

    def record_fill(self) -> None:
        """记录一笔报单成交（计入撤单率窗口分母）。"""
        self._resolved.append("fill")

    def record_cancel(self) -> None:
        """记录一笔报单撤单（计入撤单率窗口分子）。"""
        self._resolved.append("cancel")
        # 撤单也消耗限频额度
        self._submit_ts.append(time.monotonic())
        status = self.status
        if status is CancelRateStatus.WARN_ONLY_PLACE:
            _logger.warning(
                "撤单后撤单率=%.2f%% 进入只挂不撤模式",
                self.cancel_rate * 100,
            )
        elif status is CancelRateStatus.FROZEN:
            _logger.error(
                "撤单后撤单率=%.2f%% 触发冻结！全账户禁止新下单",
                self.cancel_rate * 100,
            )

    def reset(self) -> None:
        """重置监控（盘前或人工介入后）。"""
        self._resolved.clear()
        self._submit_ts.clear()
        _logger.info("CancelRateGuard reset")
