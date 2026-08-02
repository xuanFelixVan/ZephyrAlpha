# [BLUEPRINT] MOD-XS-004 | docs/03_modules/_domain-ex_sor/execution_scheduler/blueprint.md
# [MODULE] zephyr.ex_sor.core.execution_scheduler
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] zephyr.shared.contracts.order; zephyr.shared.foundation.errors; zephyr.ex_sor.core.algo_trading_engine
# [CONSUMERS] MOD-XS-001(Optimal Order Router,路由子订单); MOD-XS-002(Broker Adapter,提交子订单); D-EX-CORE(OMS,调度进度查询)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 子订单量和=计划总量(Decimal守恒); 参与率≤5%(§10.1自适应降速); 优先级队列P0>P1>P2>P3; 调度决策可审计; 下单零重试(HB-07)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SchedulerError; EmptyPlanError; InvalidScheduleWindowError; OverParticipationError
# [TESTS] tests/ex_sor/test_execution_scheduler.py
# [A_module] module_id=MOD-XS-004 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Execution Scheduler — 执行调度器 (MOD-XS-004)

D-EX-SOR §2.2 XS-04: 时间切片器 + TWAP/VWAP 调度器 + 自适应调度器 + 优先级队列 + 执行进度监控。

职责:
    - 消费 XS-05 的 AlgoExecutionPlan (切片方案)
    - 将切片分配到时间窗口 (send_at 时刻)
    - 按优先级队列调度 (P0 紧急 > P1 高 > P2 正常 > P3 低)
    - 自适应降速: 参与率逼近 5% (§10.1) → 延迟下一片
    - 执行进度监控 (sent / filled / remaining)

依赖 (depgraph edge 9745160: XS-004 → XS-005):
    本模块消费 XS-05 的 AlgoExecutionPlan / AlgoSlice / AlgoType / PriceStrategy,
    不重复算法逻辑; 调度结果 ScheduledChildOrder 供 XS-01 路由 / XS-02 提交。

边界 (与 XS-05 的分工):
    XS-05 = 算法逻辑 (切多少量、什么价格策略)
    XS-04 = 时间调度 (何时发每片、优先级、自适应节奏)

关键约束 (D-EX-SOR):
    §10.1  参与率 ≤5% (自适应降速, 逼近时延迟)
    §6.6   下单零重试 (HB-07, 单片提交失败不自动重试, 标记 CANCELLED)
    §13.2  时变参与率 (午盘收紧, 尾盘放松)

SSoT: depgraph MOD-XS-004
Version: 0.1.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from enum import Enum, IntEnum
from typing import Final, Optional
from uuid import uuid4

from zephyr.ex_sor.core.algo_trading_engine import (
    MAX_PARTICIPATION_RATE,
    AlgoExecutionPlan,
    AlgoType,
    PriceStrategy,
)
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    # 枚举
    "SchedulePriority",
    "SliceStatus",
    # 数据模型
    "ScheduledChildOrder",
    "ExecutionSchedule",
    "ScheduleProgress",
    "PacingFeedback",
    # 调度器
    "ExecutionScheduler",
    # 错误
    "SchedulerError",
    "EmptyPlanError",
    "InvalidScheduleWindowError",
    "OverParticipationError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class SchedulerError(ZephyrBaseError):
    """调度器错误。"""

    error_code = "ZA-XS-0004"


class EmptyPlanError(SchedulerError):
    """空计划——AlgoExecutionPlan 无切片。"""

    error_code = "ZA-XS-0004-EP"


class InvalidScheduleWindowError(SchedulerError):
    """调度窗口非法——end≤start 或窗口为零。"""

    error_code = "ZA-XS-0004-IW"


class OverParticipationError(SchedulerError):
    """参与率超限——实时参与率 > 5% (§10.1), 需降速或暂停。"""

    error_code = "ZA-XS-0004-OP"


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class SchedulePriority(IntEnum):
    """调度优先级——P0 最高 (队列优先出队)。"""

    P0_CRITICAL = 0  # 紧急 (ALT 激进吃单 / 风控减仓)
    P1_HIGH = 1  # 高 (首片建仓 / IS 前置)
    P2_NORMAL = 2  # 正常 (常规切片)
    P3_LOW = 3  # 低 (尾盘被动)


class SliceStatus(Enum):
    """子订单状态机。"""

    def __str__(self) -> str:
        return self.value

    PENDING = "PENDING"  # 待调度
    SCHEDULED = "SCHEDULED"  # 已调度 (有 send_at)
    SENT = "SENT"  # 已提交
    PARTIAL = "PARTIAL"  # 部分成交
    FILLED = "FILLED"  # 全部成交
    CANCELLED = "CANCELLED"  # 已取消 (HB-07 不重试)


# 终态 (不可回退)
_TERMINAL_STATUSES: Final[frozenset] = frozenset(
    {
        SliceStatus.FILLED,
        SliceStatus.CANCELLED,
    }
)


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class ScheduledChildOrder:
    """调度后的子订单——AlgoSlice + 时间 + 优先级。

    Attributes:
        child_order_id: 子订单 ID (调度时生成)
        slice_index: 对应 AlgoSlice 序号
        quantity: 数量
        price_strategy: 价格策略
        reference_price: 参考价
        send_at: 计划发送时刻
        priority: 优先级
        status: 状态
        rationale: 调度理由 (审计)
        sent_at: 实际发送时刻
        filled_quantity: 已成交数量
    """

    child_order_id: str
    slice_index: int
    quantity: Decimal
    price_strategy: PriceStrategy
    reference_price: Decimal | None
    send_at: datetime
    priority: SchedulePriority
    status: SliceStatus = SliceStatus.SCHEDULED
    rationale: str = ""
    sent_at: datetime | None = None
    filled_quantity: Decimal = field(default_factory=lambda: Decimal("0"))

    @property
    def is_terminal(self) -> bool:
        return self.status in _TERMINAL_STATUSES

    @property
    def remaining_quantity(self) -> Decimal:
        return self.quantity - self.filled_quantity

    def to_dict(self) -> dict[str, object]:
        return {
            "child_order_id": self.child_order_id,
            "slice_index": self.slice_index,
            "quantity": str(self.quantity),
            "price_strategy": self.price_strategy.value,
            "reference_price": str(self.reference_price) if self.reference_price else None,
            "send_at": self.send_at.isoformat(),
            "priority": self.priority.name,
            "status": self.status.value,
            "filled_quantity": str(self.filled_quantity),
            "rationale": self.rationale,
        }


@dataclass
class ScheduleProgress:
    """调度进度报告。

    Attributes:
        total_slices: 总切片数
        scheduled: 已调度
        sent: 已发送
        filled: 已成交
        cancelled: 已取消
        remaining: 待发送
        total_quantity: 总量
        filled_quantity: 已成交总量
        remaining_quantity: 剩余量
        completion_rate: 完成率 [0,1]
    """

    total_slices: int
    scheduled: int
    sent: int
    filled: int
    cancelled: int
    remaining: int
    total_quantity: Decimal
    filled_quantity: Decimal
    remaining_quantity: Decimal

    @property
    def completion_rate(self) -> float:
        if self.total_quantity <= 0:
            return 0.0
        return float(self.filled_quantity / self.total_quantity)

    @property
    def is_complete(self) -> bool:
        """所有切片终态 (FILLED 或 CANCELLED)。"""
        return (self.filled + self.cancelled) >= self.total_slices

    def to_dict(self) -> dict[str, object]:
        return {
            "total_slices": self.total_slices,
            "scheduled": self.scheduled,
            "sent": self.sent,
            "filled": self.filled,
            "cancelled": self.cancelled,
            "remaining": self.remaining,
            "total_quantity": str(self.total_quantity),
            "filled_quantity": str(self.filled_quantity),
            "remaining_quantity": str(self.remaining_quantity),
            "completion_rate": round(self.completion_rate, 6),
            "is_complete": self.is_complete,
        }


@dataclass(frozen=True)
class PacingFeedback:
    """自适应节奏反馈——市场实时参与率。

    Attributes:
        current_participation: 当前实时参与率 (本策略成交量/市场成交量)
        window_volume: 当前时间窗口市场成交量
        strategy_filled_window: 本策略窗口内已成交量
    """

    current_participation: Decimal
    window_volume: Decimal = Decimal("0")
    strategy_filled_window: Decimal = Decimal("0")

    @property
    def is_over_limit(self) -> bool:
        """是否超 §10.1 5% 上限。"""
        return self.current_participation > MAX_PARTICIPATION_RATE

    @property
    def is_near_limit(self) -> bool:
        """是否逼近上限 (>4%, 需降速)。"""
        return self.current_participation > Decimal("0.04")


@dataclass
class ExecutionSchedule:
    """执行调度方案——一个订单的全部子订单时间表。

    Attributes:
        order_id: 订单 ID
        algo_type: 算法类型
        child_orders: 子订单列表 (按 slice_index 排序)
        start_time: 窗口开始
        end_time: 窗口结束
        total_quantity: 总量 (== plan.total_quantity, 守恒)
        created_at: 创建时间
    """

    order_id: str
    algo_type: AlgoType
    child_orders: list[ScheduledChildOrder]
    start_time: datetime
    end_time: datetime
    total_quantity: Decimal
    created_at: datetime

    def __post_init__(self) -> None:
        if not self.child_orders:
            raise EmptyPlanError(
                "调度方案子订单不能为空",
                details={"order_id": self.order_id},
            )
        if self.end_time <= self.start_time:
            raise InvalidScheduleWindowError(
                "调度窗口结束必须晚于开始",
                details={
                    "start": self.start_time.isoformat(),
                    "end": self.end_time.isoformat(),
                },
            )
        # 守恒: 子订单量和 == total
        child_sum = sum((c.quantity for c in self.child_orders), Decimal("0"))
        if child_sum != self.total_quantity:
            raise SchedulerError(
                "子订单量和≠总量 (违反守恒)",
                details={
                    "order_id": self.order_id,
                    "child_sum": str(child_sum),
                    "total": str(self.total_quantity),
                },
            )

    # ── 查询 ──

    @property
    def slice_count(self) -> int:
        return len(self.child_orders)

    def get_child(self, slice_index: int) -> ScheduledChildOrder:
        for c in self.child_orders:
            if c.slice_index == slice_index:
                return c
        raise SchedulerError(
            f"未找到 slice_index={slice_index}",
            details={"order_id": self.order_id, "slice_index": slice_index},
        )

    def next_due(self, now: datetime) -> ScheduledChildOrder | None:
        """返回下一个应发送的子订单 (优先级队列)。

        选择规则:
            1. 状态为 SCHEDULED (未发送)
            2. send_at <= now (已到点)
            3. 按 (priority, send_at) 升序 → 最高优先级 + 最早到点
        """
        candidates = [c for c in self.child_orders if c.status == SliceStatus.SCHEDULED and c.send_at <= now]
        if not candidates:
            return None
        return min(candidates, key=lambda c: (c.priority, c.send_at))

    def pending(self) -> list[ScheduledChildOrder]:
        """所有未发送的子订单 (SCHEDULED 状态)。"""
        return [c for c in self.child_orders if c.status == SliceStatus.SCHEDULED]

    def progress(self) -> ScheduleProgress:
        """计算调度进度。"""
        total = len(self.child_orders)
        scheduled = sum(1 for c in self.child_orders if c.status == SliceStatus.SCHEDULED)
        sent = sum(1 for c in self.child_orders if c.status in (SliceStatus.SENT, SliceStatus.PARTIAL))
        filled = sum(1 for c in self.child_orders if c.status == SliceStatus.FILLED)
        cancelled = sum(1 for c in self.child_orders if c.status == SliceStatus.CANCELLED)
        remaining = scheduled  # 待发送 = SCHEDULED
        filled_qty = sum((c.filled_quantity for c in self.child_orders), Decimal("0"))
        return ScheduleProgress(
            total_slices=total,
            scheduled=scheduled,
            sent=sent,
            filled=filled,
            cancelled=cancelled,
            remaining=remaining,
            total_quantity=self.total_quantity,
            filled_quantity=filled_qty,
            remaining_quantity=self.total_quantity - filled_qty,
        )

    def to_dict(self) -> dict[str, object]:
        p = self.progress()
        return {
            "order_id": self.order_id,
            "algo_type": self.algo_type.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "total_quantity": str(self.total_quantity),
            "slice_count": self.slice_count,
            "progress": p.to_dict(),
            "child_orders": [c.to_dict() for c in self.child_orders],
        }


# ──────────────────────────────────────────────────────────────────────────────
# 执行调度器
# ──────────────────────────────────────────────────────────────────────────────


class ExecutionScheduler:
    """执行调度器——时间切片 + 优先级队列 + 自适应降速。

    用法:
        scheduler = ExecutionScheduler()
        schedule = scheduler.schedule(plan, start, end)
        # 运行时循环:
        child = schedule.next_due(now)
        if child: scheduler.mark_sent(schedule, child.slice_index, broker_id)
        # 自适应:
        scheduler.adjust_pacing(schedule, feedback, now)

    调度算法:
        1. 等距分配 send_at (start + i × step, step = (end-start)/n)
        2. 优先级赋值: ALT→P0, 首片→P1, 尾片→P3, 其余→P2
        3. next_due: 优先级队列 (priority asc, send_at asc)
    """

    def __init__(self, id_prefix: str = "CHD") -> None:
        self._id_prefix = id_prefix
        self._schedules: dict[str, ExecutionSchedule] = {}  # order_id → schedule (审计)

    # ── 调度入口 ──

    def schedule(
        self,
        plan: AlgoExecutionPlan,
        start_time: datetime,
        end_time: datetime | None = None,
        now: datetime | None = None,
    ) -> ExecutionSchedule:
        """将 AlgoExecutionPlan 调度到时间窗口。

        Args:
            plan: 算法执行计划 (来自 XS-05)
            start_time: 窗口开始
            end_time: 窗口结束 (默认 start + plan.params.time_horizon_minutes)
            now: 创建时间戳 (测试用)

        Returns:
            ExecutionSchedule: 调度方案

        Raises:
            EmptyPlanError: 计划无切片
            InvalidScheduleWindowError: 窗口非法
        """
        now = now or datetime.now(timezone.utc)
        if not plan.slices:
            raise EmptyPlanError(
                "执行计划无切片",
                details={"order_id": plan.order_id},
            )
        if end_time is None:
            end_time = start_time + timedelta(minutes=plan.params.time_horizon_minutes)
        if end_time <= start_time:
            raise InvalidScheduleWindowError(
                "调度窗口结束必须晚于开始",
                details={
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                },
            )

        slices = plan.slices
        n = len(slices)
        total_span = (end_time - start_time).total_seconds()

        child_orders: list[ScheduledChildOrder] = []
        for i, sl in enumerate(slices):
            # 等距 send_at (n=1 时放 start)
            if n == 1:
                offset = 0.0
            else:
                offset = total_span * (i / n)
            send_at = start_time + timedelta(seconds=offset)
            priority = self._assign_priority(plan.algo_type, i, n)
            child = ScheduledChildOrder(
                child_order_id=self._gen_id(),
                slice_index=sl.slice_index,
                quantity=sl.quantity,
                price_strategy=sl.price_strategy,
                reference_price=sl.reference_price,
                send_at=send_at,
                priority=priority,
                status=SliceStatus.SCHEDULED,
                rationale=f"{sl.rationale} | 调度 {i + 1}/{n} @ {send_at:%H:%M:%S} prio={priority.name}",
            )
            child_orders.append(child)

        schedule = ExecutionSchedule(
            order_id=plan.order_id,
            algo_type=plan.algo_type,
            child_orders=child_orders,
            start_time=start_time,
            end_time=end_time,
            total_quantity=plan.total_quantity,
            created_at=now,
        )
        self._schedules[plan.order_id] = schedule
        logger.info(
            "Schedule: order=%s algo=%s slices=%d window=%s→%s",
            plan.order_id,
            plan.algo_type.value,
            n,
            start_time.strftime("%H:%M"),
            end_time.strftime("%H:%M"),
        )
        return schedule

    def _assign_priority(self, algo_type: AlgoType, idx: int, total: int) -> SchedulePriority:
        """按算法类型 + 切片位置赋优先级。"""
        # ALT 全部 P0 (激进, 紧急)
        if algo_type == AlgoType.ALT:
            return SchedulePriority.P0_CRITICAL
        # 首片 P1 (建仓)
        if idx == 0:
            return SchedulePriority.P1_HIGH
        # 尾片 P3 (被动收尾) — 仅 TWAP/IS
        if idx == total - 1 and algo_type in (AlgoType.TWAP, AlgoType.IS):
            return SchedulePriority.P3_LOW
        return SchedulePriority.P2_NORMAL

    def _gen_id(self) -> str:
        return f"{self._id_prefix}-{uuid4().hex[:12].upper()}"

    # ── 状态转换 ──

    def mark_sent(
        self,
        schedule: ExecutionSchedule,
        slice_index: int,
        child_order_id: str | None = None,
        now: datetime | None = None,
    ) -> ScheduledChildOrder:
        """标记子订单已发送 (状态 SCHEDULED → SENT)。

        HB-07 零重试: 发送失败不调用此方法, 而是调用 mark_cancelled。
        """
        now = now or datetime.now(timezone.utc)
        child = schedule.get_child(slice_index)
        if child.status != SliceStatus.SCHEDULED:
            raise SchedulerError(
                f"子订单状态 {child.status.value} 不可标记 SENT (需 SCHEDULED)",
                details={
                    "order_id": schedule.order_id,
                    "slice_index": slice_index,
                    "current_status": child.status.value,
                },
            )
        child.status = SliceStatus.SENT
        child.sent_at = now
        if child_order_id:
            child.child_order_id = child_order_id
        logger.info(
            "Sent: order=%s slice=%d qty=%s prio=%s",
            schedule.order_id,
            slice_index,
            str(child.quantity),
            child.priority.name,
        )
        return child

    def mark_filled(
        self,
        schedule: ExecutionSchedule,
        slice_index: int,
        filled_quantity: Decimal,
        fully: bool = True,
    ) -> ScheduledChildOrder:
        """标记子订单成交 (SENT → PARTIAL/FILLED)。

        Args:
            filled_quantity: 本次成交数量 (累加)
            fully: 是否全部成交 (True→FILLED, False→PARTIAL)
        """
        child = schedule.get_child(slice_index)
        if child.status not in (SliceStatus.SENT, SliceStatus.PARTIAL):
            raise SchedulerError(
                f"子订单状态 {child.status.value} 不可标记成交 (需 SENT/PARTIAL)",
                details={
                    "order_id": schedule.order_id,
                    "slice_index": slice_index,
                    "current_status": child.status.value,
                },
            )
        if filled_quantity <= 0:
            raise SchedulerError(
                "成交数量必须为正",
                details={"filled_quantity": str(filled_quantity)},
            )
        child.filled_quantity += filled_quantity
        # 防止超填
        if child.filled_quantity > child.quantity:
            child.filled_quantity = child.quantity
        child.status = SliceStatus.FILLED if fully else SliceStatus.PARTIAL
        return child

    def mark_cancelled(
        self,
        schedule: ExecutionSchedule,
        slice_index: int,
        reason: str = "",
    ) -> ScheduledChildOrder:
        """标记子订单取消 (HB-07 零重试: 发送失败→取消, 不重试)。

        允许从 SCHEDULED/SENT/PARTIAL 取消 (终态不可取消)。
        """
        child = schedule.get_child(slice_index)
        if child.is_terminal:
            raise SchedulerError(
                f"子订单已终态 {child.status.value} 不可取消",
                details={
                    "order_id": schedule.order_id,
                    "slice_index": slice_index,
                    "current_status": child.status.value,
                },
            )
        child.status = SliceStatus.CANCELLED
        logger.warning(
            "Cancelled: order=%s slice=%d reason=%s (HB-07 不重试)",
            schedule.order_id,
            slice_index,
            reason,
        )
        return child

    # ── 自适应降速 ──

    def adjust_pacing(
        self,
        schedule: ExecutionSchedule,
        feedback: PacingFeedback,
        now: datetime,
    ) -> int:
        """自适应降速——根据实时参与率调整未发送子订单的 send_at。

        §10.1 参与率限制:
            - 超限 (>5%): 延迟所有未发送子订单 60s + 告警 (OverParticipationError)
            - 逼近 (>4%): 延迟下一片 30s (降速)
            - 正常: 不调整

        Returns:
            被延迟的子订单数
        """
        if feedback.is_over_limit:
            # 超限: 延迟所有未发送 + 抛 OverParticipationError
            delayed = 0
            for c in schedule.child_orders:
                if c.status == SliceStatus.SCHEDULED and c.send_at < now + timedelta(seconds=60):
                    c.send_at = now + timedelta(seconds=60)
                    delayed += 1
            logger.warning(
                "Over-participation %.4f > 5%%: delayed %d slices 60s (§10.1)",
                float(feedback.current_participation),
                delayed,
            )
            raise OverParticipationError(
                f"实时参与率 {float(feedback.current_participation):.4f} 超 5% 上限 (§10.1)",
                details={
                    "order_id": schedule.order_id,
                    "participation": str(feedback.current_participation),
                    "delayed_slices": delayed,
                },
            )
        if feedback.is_near_limit:
            # 逼近: 延迟下一片 30s
            next_child = schedule.next_due(now)
            if next_child is not None:
                next_child.send_at = now + timedelta(seconds=30)
                logger.info(
                    "Near-limit %.4f: delayed next slice %d 30s",
                    float(feedback.current_participation),
                    next_child.slice_index,
                )
                return 1
        return 0

    # ── 审计查询 ──

    def get_schedule(self, order_id: str) -> ExecutionSchedule | None:
        return self._schedules.get(order_id)

    @property
    def active_schedules(self) -> list[ExecutionSchedule]:
        """所有未完成的调度方案。"""
        return [s for s in self._schedules.values() if not s.progress().is_complete]

    def clear_history(self) -> None:
        self._schedules.clear()
