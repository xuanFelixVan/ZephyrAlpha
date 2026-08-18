# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.cancel_rate_guard
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib
# [CONSUMERS] zephyr.ex_core.order_manager ; zephyr.ex_core.trading_session
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 撤单率>15%冻结新下单;>12%禁止撤单;限频15笔/秒;日申报(报单+撤单)>5000预警/>=10000阻断
# [MODIFY-GUARD] 40_execution_broker.md §决策⑫ + 43_compliance_discipline.md §8（#ARCH-COMPLIANCE-001 方案A：日申报笔数硬计数器并入本守卫）
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_core/test_cancel_rate_guard.py
# [TTL] permanent

"""

撤单率滚动监控降级（40_execution_broker §决策⑫ gap 7 施工）。

程序化交易监管合规生存项（《程序化交易管理实施细则》2025-07-07 全面实施）：
- 滚动 500 笔窗口监控撤单率
- >12% 预警线 → 降级"只挂不撤"（禁止撤单重挂，等成交或收盘）
- >15% 硬线 → 冻结全账户新下单，告警人工介入
- 内部限频 15 笔/秒（报单+撤单，保守安全垫，远低于法定 300 笔/秒）

为何 12% 预警而非等到 15%：滚动窗口有滞后性，等看到 15% 时实际可能已超，
留 3% 缓冲是合规安全垫。

日申报笔数硬计数器（2026-08-15 AI-ASM-001 装配批接入，43_compliance_discipline §8 /
#ARCH-COMPLIANCE-001 方案 A 裁定）：2026-06-08 程序化新规——单账户单日申报
>5000 笔预警 / >1 万笔限交易。申报口径含报单+撤单（与 24 号 §3.7 高频认定
"申报、撤单笔数"口径一致）。计数复用本守卫既有 record_submit/record_cancel
事件流（40 号决策⑫），不重复实现；按自然日自动滚动清零。
读数检查嵌入 C-002（OrderManager.submit_order 前置，本批接线）。

依据：40_execution_broker.md v2.3.0 §决策⑫
      43_compliance_discipline.md §8（#ARCH-COMPLIANCE-001 方案 A）
Version: 1.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 报单事件流水（提交/成交/撤单）
#   fields: record_submit 提交时间戳 / record_fill 成交 / record_cancel 撤单
#   code: record_submit/record_fill/record_cancel L167-L183
# - id: I2
#   name: 守卫配置参数 4项
#   fields: window_size=500笔 / warn_threshold=0.12 / freeze_threshold=0.15 / rate_limit_per_sec=15
#   code: CancelRateGuard dataclass L55-L72
# 层: 算法
# - id: A1
#   name_zh: ① 滚动撤单率计算
#   name_en: cancel_rate
#   intro: 数最近500笔已完结报单里有多少是撤单，算出滚动撤单率
#   desc: deque(maxlen=500) 存 "cancel"/"fill" → cancel_rate = cancels/len(resolved)；空窗口返回0.0
#   inputs: I1 I2
#   outputs: cancel_rate float（0~1）
# - id: A2
#   name_zh: ② 三档状态降级
#   name_en: status
#   intro: 撤单率过12%只挂不撤，过15%冻结全账户新下单
#   desc: rate>freeze→FROZEN；rate>warn→WARN_ONLY_PLACE；否则NORMAL；12%预警留3%缓冲防滚动窗口滞后
#   inputs: A1 I2
#   outputs: CancelRateStatus（NORMAL/WARN_ONLY_PLACE/FROZEN）
#   invariant: 撤单率>15%冻结新下单；>12%禁止撤单
# - id: A3
#   name_zh: ③ 下单/撤单许可判定
#   name_en: can_place_order / can_cancel_order
#   intro: 冻结状态不让下单，预警和冻结状态都不让撤单
#   desc: FROZEN→can_place_order=False（告警人工介入）；FROZEN/WARN_ONLY_PLACE→can_cancel_order=False；判定失败均记日志
#   inputs: A2
#   outputs: bool 许可
# - id: A4
#   name_zh: ④ 每秒限频检查
#   name_en: can_submit_now
#   intro: 最近1秒内报单+撤单到15笔就不让再发，远低于法定300笔/秒
#   desc: _submit_ts deque 清理1秒前时间戳 → len>=rate_limit_per_sec→False；撤单也消耗限频额度
#   inputs: I1 I2
#   outputs: bool 许可
#   invariant: 内部限频15笔/秒（保守安全垫）
# 层: 输出
# - id: O1
#   name_zh: 下单/撤单/限频许可 bool
#   name_en: can_place_order / can_cancel_order / can_submit_now
#   intro: 下单撤单前的三道许可闸门返回值
#   downstream: ex_core.order_manager / ex_core.trading_session（提交与撤单前置调用）
# - id: O2
#   name_zh: 降级状态与告警日志
#   name_en: CancelRateStatus
#   intro: 当前监控状态，触发预警/冻结时打告警日志
#   downstream: 人工介入告警 / 审计日志（D_EX_CORE）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# I2 --> A2
# A2 --> A3
# I1 --> A4
# I2 --> A4
# A3 --> O1
# A4 --> O1
# A2 --> O2
"""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import date
from enum import Enum

__all__ = [
    "CancelRateStatus",
    "DailyDeclarationStatus",
    "CancelRateGuard",
]

_logger = logging.getLogger(__name__)


class CancelRateStatus(str, Enum):
    """撤单率监控状态。"""

    NORMAL = "normal"                  # 正常：可挂可撤
    WARN_ONLY_PLACE = "warn_only_place"  # 预警：只挂不撤（撤单率 >12%）
    FROZEN = "frozen"                  # 冻结：禁止新下单（撤单率 >15%）


class DailyDeclarationStatus(str, Enum):
    """日申报笔数监控状态（43 号 §8 / #ARCH-COMPLIANCE-001 方案 A）。"""

    NORMAL = "normal"      # < 5000 笔
    WARNING = "warning"    # >= 5000 笔（预警，不阻断）
    BLOCKED = "blocked"    # >= 10000 笔（限交易，阻断新申报）


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
    # 日申报笔数硬计数器阈值（43 号 §8 方案 A：5000 预警 / 1 万阻断）
    daily_warn_threshold: int = 5000
    daily_block_threshold: int = 10000
    # 已完结报单结果窗口："cancel" or "fill"
    _resolved: deque = field(default_factory=lambda: deque(maxlen=500), repr=False)
    # 最近 1 秒的提交时间戳（限频）
    _submit_ts: deque = field(default_factory=deque, repr=False)
    # 当日申报计数（报单+撤单）与所属自然日
    _daily_count: int = field(default=0, repr=False)
    _daily_date: date | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        # 同步 maxlen 与 window_size
        if self._resolved.maxlen != self.window_size:
            self._resolved = deque(self._resolved, maxlen=self.window_size)
        self._daily_date = date.today()
        # RLock：_count_declaration 持锁后会再经 daily_declaration_status 重入
        self._daily_lock = threading.RLock()

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

    # ── 日申报笔数硬计数器（43 号 §8 方案 A：5000 预警 / 1 万阻断）──

    @property
    def daily_declaration_count(self) -> int:
        """当日申报笔数（报单+撤单，自然日口径，跨日自动清零）。"""
        with self._daily_lock:
            self._rollover_if_new_day()
            return self._daily_count

    @property
    def daily_declaration_status(self) -> DailyDeclarationStatus:
        """当日申报笔数监控状态（C-002 读数检查消费）。"""
        count = self.daily_declaration_count
        if count >= self.daily_block_threshold:
            return DailyDeclarationStatus.BLOCKED
        if count >= self.daily_warn_threshold:
            return DailyDeclarationStatus.WARNING
        return DailyDeclarationStatus.NORMAL

    def _rollover_if_new_day(self) -> None:
        """自然日跨天自动清零（申报笔数为交易日口径，隔日作废）。"""
        today = date.today()
        if self._daily_date != today:
            self._daily_count = 0
            self._daily_date = today

    def _count_declaration(self) -> None:
        """记一笔申报（报单或撤单），阈值穿越时告警（仅穿越瞬间各一次）。"""
        with self._daily_lock:
            self._rollover_if_new_day()
            prev_status = self.daily_declaration_status
            self._daily_count += 1
            new_status = self.daily_declaration_status
            if new_status is prev_status:
                return
            if new_status is DailyDeclarationStatus.WARNING:
                _logger.warning(
                    "日申报笔数预警: count=%d >= %d（2026-06-08 程序化新规 5000 笔预警线）",
                    self._daily_count,
                    self.daily_warn_threshold,
                )
            elif new_status is DailyDeclarationStatus.BLOCKED:
                _logger.error(
                    "日申报笔数阻断: count=%d >= %d（2026-06-08 程序化新规 1 万笔限交易线），"
                    "C-002 将拒绝新申报",
                    self._daily_count,
                    self.daily_block_threshold,
                )

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
        """记录一笔报单提交（用于限频计数 + 日申报笔数）。

        注意：报单提交时尚未完结（可能成交或撤单），不计入撤单率窗口。
        撤单率仅在 record_fill / record_cancel 时更新。
        """
        self._submit_ts.append(time.monotonic())
        self._count_declaration()

    def record_fill(self) -> None:
        """记录一笔报单成交（计入撤单率窗口分母）。"""
        self._resolved.append("fill")

    def record_cancel(self) -> None:
        """记录一笔报单撤单（计入撤单率窗口分子 + 日申报笔数）。"""
        self._resolved.append("cancel")
        # 撤单也消耗限频额度
        self._submit_ts.append(time.monotonic())
        # 撤单同属申报口径（24 号 §3.7 高频认定"申报、撤单笔数"）
        self._count_declaration()
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
        """重置监控（仅盘前/人工介入后调用，盘中调用记 critical）。"""
        with self._daily_lock:
            if self._daily_count > 0:
                _logger.critical(
                    "盘中 reset CancelRateGuard（daily_count=%d）——可能绕过 C-002 日申报限制",
                    self._daily_count,
                )
            self._resolved.clear()
            self._submit_ts.clear()
            self._daily_count = 0
            self._daily_date = date.today()
        _logger.info("CancelRateGuard reset")
