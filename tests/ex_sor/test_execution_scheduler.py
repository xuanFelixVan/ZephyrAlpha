# [BLUEPRINT] MOD-XS-004 | docs/03_modules/_domain_ex_sor/execution_scheduler/blueprint.md | §
# [TTL] permanent
"""ExecutionScheduler 单元测试 (MOD-XS-004)。时间切片+优先级队列+自适应降速+进度监控。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from zephyr.ex_sor.core.algo_trading_engine import (
    LOT_SIZE,
    AlgoParams,
    AlgoTradingEngine,
    AlgoType,
    MarketContext,
)
from zephyr.ex_sor.core.execution_scheduler import (
    EmptyPlanError,
    ExecutionSchedule,
    ExecutionScheduler,
    InvalidScheduleWindowError,
    OverParticipationError,
    PacingFeedback,
    ScheduledChildOrder,
    SchedulePriority,
    SchedulerError,
    SliceStatus,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.order import Order

NOW = datetime(2026, 8, 4, 9, 30, tzinfo=timezone.utc)
START = datetime(2026, 8, 4, 9, 30, tzinfo=timezone.utc)
END = START + timedelta(minutes=10)


# ── Fixtures ────────────────────────────────────────────────────────────────


def make_order(qty: Decimal = Decimal("1000"), order_id: str = "ORD-001") -> Order:
    return Order(
        order_id=order_id,
        idempotency_key=f"IDEMP-{order_id}",
        order_type=OrderType.LIMIT,
        quantity=qty,
        side=OrderSide.BUY,
        strategy_id="STRAT-1",
        symbol="000001.SZ",
        limit_price=Decimal("10.50"),
    )


def make_ctx() -> MarketContext:
    return MarketContext(
        symbol="000001.SZ",
        last_price=Decimal("10.50"),
        adv=Decimal("1000000"),
        bid_price=Decimal("10.49"),
        ask_price=Decimal("10.51"),
    )


def make_plan(
    qty: Decimal = Decimal("1000"),
    algo: AlgoType = AlgoType.TWAP,
    max_slices: int = 5,
):
    eng = AlgoTradingEngine()
    kw = {}
    if algo == AlgoType.ICEBERG:
        kw["display_quantity"] = Decimal("200")
    params = AlgoParams(
        algo_type=algo,
        time_horizon_minutes=10,
        max_slice_count=max_slices,
        **kw,
    )
    return eng.generate_plan(make_order(qty), params, make_ctx(), now=NOW)


def make_scheduler() -> ExecutionScheduler:
    return ExecutionScheduler(id_prefix="TEST")


# ── 枚举 ────────────────────────────────────────────────────────────────────


def test_priority_ordering():
    """P0 < P1 < P2 < P3 (IntEnum, 小值=高优先级)。"""
    assert SchedulePriority.P0_CRITICAL < SchedulePriority.P1_HIGH
    assert SchedulePriority.P1_HIGH < SchedulePriority.P2_NORMAL
    assert SchedulePriority.P2_NORMAL < SchedulePriority.P3_LOW


def test_slice_status_values():
    assert SliceStatus.SCHEDULED.value == "SCHEDULED"
    assert SliceStatus.FILLED.value == "FILLED"
    assert SliceStatus.CANCELLED.value == "CANCELLED"
    assert len(SliceStatus) == 6


# ── 调度 ────────────────────────────────────────────────────────────────────


def test_schedule_basic():
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=5)
    sch = sched.schedule(plan, START, END, now=NOW)
    assert sch.order_id == "ORD-001"
    assert sch.algo_type == AlgoType.TWAP
    assert sch.slice_count == 5
    assert sch.start_time == START
    assert sch.end_time == END


def test_schedule_conservation():
    """子订单量和 == 计划总量 (守恒)。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=5)
    sch = sched.schedule(plan, START, END, now=NOW)
    child_sum = sum((c.quantity for c in sch.child_orders), Decimal("0"))
    assert child_sum == plan.total_quantity
    assert sch.total_quantity == Decimal("1000")


def test_schedule_default_end_from_horizon():
    """end_time=None → 用 start + plan.params.time_horizon_minutes。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=5)
    sch = sched.schedule(plan, START, now=NOW)
    assert sch.end_time == START + timedelta(minutes=10)


def test_schedule_invalid_window():
    """end <= start → InvalidScheduleWindowError。"""
    sched = make_scheduler()
    plan = make_plan()
    with pytest.raises(InvalidScheduleWindowError, match="窗口"):
        sched.schedule(plan, START, START, now=NOW)


def test_schedule_empty_plan():
    sched = make_scheduler()
    # 构造空 slices 的 plan 通过 __post_init__ 会抛 AlgoError, 用 mock 替代
    from zephyr.ex_sor.core.algo_trading_engine import AlgoExecutionPlan, AlgoParams

    # 直接构造空 plan 会触发 AlgoError, 改为验证 schedule 对空 slices 的处理
    plan = make_plan()
    # 模拟空: 移除所有 slices
    plan_with_empty = object.__new__(AlgoExecutionPlan)

    # 用真实 plan 测试 schedule 的空检查: 让 plan.slices 为空
    class FakePlan:
        order_id = "X"
        algo_type = AlgoType.TWAP
        slices = []
        total_quantity = Decimal("0")
        params = AlgoParams(algo_type=AlgoType.TWAP)

    with pytest.raises(EmptyPlanError, match="无切片"):
        sched.schedule(FakePlan(), START, END, now=NOW)


def test_schedule_send_times_evenly_spaced():
    """等距分配 send_at。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=4)
    sch = sched.schedule(plan, START, END, now=NOW)
    # 4 片, 10 分钟窗口 → 间隔 2.5 分钟
    times = [c.send_at for c in sch.child_orders]
    assert times[0] == START
    gap = (times[1] - times[0]).total_seconds()
    expected_gap = (END - START).total_seconds() / 4
    assert abs(gap - expected_gap) < 1


def test_schedule_single_slice_at_start():
    """单片 → send_at = start。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=1)
    sch = sched.schedule(plan, START, END, now=NOW)
    assert sch.slice_count == 1
    assert sch.child_orders[0].send_at == START


# ── 优先级赋值 ──────────────────────────────────────────────────────────────


def test_priority_twap_first_high_last_low():
    """TWAP: 首片 P1, 末片 P3, 中间 P2。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), AlgoType.TWAP, max_slices=5)
    sch = sched.schedule(plan, START, END, now=NOW)
    prios = [c.priority for c in sch.child_orders]
    assert prios[0] == SchedulePriority.P1_HIGH
    assert prios[-1] == SchedulePriority.P3_LOW
    for p in prios[1:-1]:
        assert p == SchedulePriority.P2_NORMAL


def test_priority_alt_all_critical():
    """ALT: 全部 P0_CRITICAL。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), AlgoType.ALT, max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    for c in sch.child_orders:
        assert c.priority == SchedulePriority.P0_CRITICAL


def test_priority_vwap_middle_normal():
    """VWAP (非 TWAP/IS): 首片 P1, 其余 P2 (末片不 P3)。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), AlgoType.VWAP, max_slices=4)
    sch = sched.schedule(plan, START, END, now=NOW)
    assert sch.child_orders[0].priority == SchedulePriority.P1_HIGH
    assert sch.child_orders[-1].priority == SchedulePriority.P2_NORMAL


def test_priority_is_last_low():
    """IS: 末片 P3 (被动收尾)。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), AlgoType.IS, max_slices=5)
    sch = sched.schedule(plan, START, END, now=NOW)
    assert sch.child_orders[-1].priority == SchedulePriority.P3_LOW


# ── next_due (优先级队列) ────────────────────────────────────────────────────


def test_next_due_returns_highest_priority():
    """多片到期时, 返回最高优先级。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), AlgoType.ALT, max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    # 所有 ALT 片 P0, 都到期 → 返回最早的
    n = sch.next_due(START + timedelta(seconds=60))
    assert n is not None
    assert n.priority == SchedulePriority.P0_CRITICAL


def test_next_due_none_when_not_due():
    """未到 send_at → None。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=5)
    sch = sched.schedule(plan, START, END, now=NOW)
    # 第二片在 START + 2min, 查 START 之前 → None (但首片@START 到期)
    # 用 end 之前查所有到期
    before_start = START - timedelta(seconds=1)
    assert sch.next_due(before_start) is None


def test_next_due_skips_sent():
    """已发送的子订单不再返回。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=5)
    sch = sched.schedule(plan, START, END, now=NOW)
    sched.mark_sent(sch, 0, now=START)
    # slice 1 在 START + 2min, 查 START + 3min → slice 1 到期
    n = sch.next_due(START + timedelta(minutes=3))
    assert n is not None
    assert n.slice_index != 0  # 跳过已发送


def test_next_due_none_when_all_sent():
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=2)
    sch = sched.schedule(plan, START, END, now=NOW)
    sched.mark_sent(sch, 0, now=START)
    sched.mark_sent(sch, 1, now=START)
    assert sch.next_due(START + timedelta(seconds=60)) is None


def test_next_due_priority_over_time():
    """高优先级后到点 > 低优先级先到点。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), AlgoType.TWAP, max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    # slice 0: P1 @ START; slice 1: P2 @ +3.3min; slice 2: P3 @ +6.6min
    # 在 START 查 → slice 0 (P1, 最早)
    n = sch.next_due(START)
    assert n.slice_index == 0


# ── 状态转换 ────────────────────────────────────────────────────────────────


def test_mark_sent():
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    c = sched.mark_sent(sch, 0, now=START)
    assert c.status == SliceStatus.SENT
    assert c.sent_at == START


def test_mark_sent_with_child_order_id():
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    sched.mark_sent(sch, 0, child_order_id="BROKER-123", now=START)
    assert sch.get_child(0).child_order_id == "BROKER-123"


def test_mark_sent_invalid_state():
    """非 SCHEDULED 状态不可标记 SENT。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    sched.mark_sent(sch, 0, now=START)
    with pytest.raises(SchedulerError, match="不可标记 SENT"):
        sched.mark_sent(sch, 0, now=START)


def test_mark_filled_full():
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    sched.mark_sent(sch, 0, now=START)
    q0 = sch.get_child(0).quantity  # 实际切片量 (lot 对齐后)
    sched.mark_filled(sch, 0, q0, fully=True)
    assert sch.get_child(0).status == SliceStatus.FILLED
    assert sch.get_child(0).filled_quantity == q0


def test_mark_filled_partial():
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    sched.mark_sent(sch, 0, now=START)
    q0 = sch.get_child(0).quantity
    sched.mark_filled(sch, 0, Decimal("100"), fully=False)
    assert sch.get_child(0).status == SliceStatus.PARTIAL
    assert sch.get_child(0).remaining_quantity == q0 - Decimal("100")


def test_mark_filled_accumulates():
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    sched.mark_sent(sch, 0, now=START)
    sched.mark_filled(sch, 0, Decimal("100"), fully=False)
    sched.mark_filled(sch, 0, Decimal("50"), fully=False)
    assert sch.get_child(0).filled_quantity == Decimal("150")


def test_mark_filled_caps_at_quantity():
    """成交超填 → 截断到 quantity。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    sched.mark_sent(sch, 0, now=START)
    q = sch.get_child(0).quantity
    sched.mark_filled(sch, 0, q + Decimal("100"), fully=True)
    assert sch.get_child(0).filled_quantity == q  # 不超填


def test_mark_filled_invalid_state():
    """非 SENT/PARTIAL 不可标记成交。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    with pytest.raises(SchedulerError, match="不可标记成交"):
        sched.mark_filled(sch, 0, Decimal("100"))


def test_mark_filled_zero_quantity():
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    sched.mark_sent(sch, 0, now=START)
    with pytest.raises(SchedulerError, match="必须为正"):
        sched.mark_filled(sch, 0, Decimal("0"))


def test_mark_cancelled_from_scheduled():
    """HB-07: 发送失败→取消, 不重试。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    sched.mark_cancelled(sch, 0, reason="HB-07 提交失败")
    assert sch.get_child(0).status == SliceStatus.CANCELLED


def test_mark_cancelled_from_sent():
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    sched.mark_sent(sch, 0, now=START)
    sched.mark_cancelled(sch, 0, reason="撤单")
    assert sch.get_child(0).status == SliceStatus.CANCELLED


def test_mark_cancelled_terminal_raises():
    """终态不可取消。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    sched.mark_cancelled(sch, 0)
    with pytest.raises(SchedulerError, match="终态"):
        sched.mark_cancelled(sch, 0)


def test_get_child_not_found():
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    with pytest.raises(SchedulerError, match="未找到"):
        sch.get_child(99)


# ── 进度监控 ────────────────────────────────────────────────────────────────


def test_progress_initial():
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=5)
    sch = sched.schedule(plan, START, END, now=NOW)
    p = sch.progress()
    assert p.total_slices == 5
    assert p.scheduled == 5
    assert p.sent == 0
    assert p.filled == 0
    assert p.cancelled == 0
    assert p.remaining == 5
    assert p.completion_rate == 0.0
    assert not p.is_complete


def test_progress_after_fill():
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=5)
    sch = sched.schedule(plan, START, END, now=NOW)
    sched.mark_sent(sch, 0, now=START)
    sched.mark_filled(sch, 0, Decimal("200"), fully=True)
    p = sch.progress()
    assert p.sent == 0  # FILLED 不计入 sent
    assert p.filled == 1
    assert p.filled_quantity == Decimal("200")
    assert p.completion_rate == pytest.approx(0.2)


def test_progress_is_complete():
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=2)
    sch = sched.schedule(plan, START, END, now=NOW)
    sched.mark_sent(sch, 0, now=START)
    sched.mark_filled(sch, 0, Decimal("500"), fully=True)
    sched.mark_cancelled(sch, 1, reason="尾盘")
    p = sch.progress()
    assert p.is_complete  # 1 filled + 1 cancelled = 2 = total


def test_progress_remaining_quantity():
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=5)
    sch = sched.schedule(plan, START, END, now=NOW)
    sched.mark_sent(sch, 0, now=START)
    sched.mark_filled(sch, 0, Decimal("100"), fully=False)
    p = sch.progress()
    assert p.remaining_quantity == Decimal("900")


def test_pending():
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    sched.mark_sent(sch, 0, now=START)
    pending = sch.pending()
    assert len(pending) == 2
    assert all(c.status == SliceStatus.SCHEDULED for c in pending)


# ── 自适应降速 ──────────────────────────────────────────────────────────────


def test_adjust_pacing_over_limit_raises():
    """参与率 >5% → OverParticipationError + 延迟。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    fb = PacingFeedback(current_participation=Decimal("0.06"))
    with pytest.raises(OverParticipationError, match="5%"):
        sched.adjust_pacing(sch, fb, START)


def test_adjust_pacing_over_limit_delays():
    """超限时未发送子订单 send_at 推迟 60s。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    original_times = [c.send_at for c in sch.child_orders]
    fb = PacingFeedback(current_participation=Decimal("0.06"))
    with pytest.raises(OverParticipationError):
        sched.adjust_pacing(sch, fb, START + timedelta(seconds=30))
    # 至少一片被推迟
    new_times = [c.send_at for c in sch.child_orders]
    assert any(nt > ot for ot, nt in zip(original_times, new_times, strict=True))


def test_adjust_pacing_near_limit_delays_one():
    """参与率 4-5% → 延迟下一片 30s (不抛异常)。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    fb = PacingFeedback(current_participation=Decimal("0.045"))
    delayed = sched.adjust_pacing(sch, fb, START + timedelta(seconds=10))
    assert delayed == 1


def test_adjust_pacing_normal_no_change():
    """参与率 <4% → 不调整。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=3)
    sch = sched.schedule(plan, START, END, now=NOW)
    original = [c.send_at for c in sch.child_orders]
    fb = PacingFeedback(current_participation=Decimal("0.02"))
    delayed = sched.adjust_pacing(sch, fb, START)
    assert delayed == 0
    assert [c.send_at for c in sch.child_orders] == original


def test_pacing_feedback_over_limit():
    fb = PacingFeedback(current_participation=Decimal("0.06"))
    assert fb.is_over_limit
    assert fb.is_near_limit


def test_pacing_feedback_near_limit():
    fb = PacingFeedback(current_participation=Decimal("0.045"))
    assert not fb.is_over_limit
    assert fb.is_near_limit


def test_pacing_feedback_normal():
    fb = PacingFeedback(current_participation=Decimal("0.03"))
    assert not fb.is_over_limit
    assert not fb.is_near_limit


# ── ExecutionSchedule 守恒 ──────────────────────────────────────────────────


def test_schedule_conservation_violation_raises():
    """构造时子订单和≠总量 → SchedulerError。"""
    child = ScheduledChildOrder(
        child_order_id="C1",
        slice_index=0,
        quantity=Decimal("100"),
        price_strategy=None,
        reference_price=None,  # type: ignore
        send_at=START,
        priority=SchedulePriority.P2_NORMAL,
    )
    with pytest.raises(SchedulerError, match="守恒"):
        ExecutionSchedule(
            order_id="X",
            algo_type=AlgoType.TWAP,
            child_orders=[child],
            start_time=START,
            end_time=END,
            total_quantity=Decimal("1000"),  # != 100
            created_at=NOW,
        )


def test_schedule_empty_children_raises():
    with pytest.raises(EmptyPlanError):
        ExecutionSchedule(
            order_id="X",
            algo_type=AlgoType.TWAP,
            child_orders=[],
            start_time=START,
            end_time=END,
            total_quantity=Decimal("0"),
            created_at=NOW,
        )


def test_schedule_invalid_window_raises():
    child = ScheduledChildOrder(
        child_order_id="C1",
        slice_index=0,
        quantity=Decimal("100"),
        price_strategy=None,
        reference_price=None,  # type: ignore
        send_at=START,
        priority=SchedulePriority.P2_NORMAL,
    )
    with pytest.raises(InvalidScheduleWindowError):
        ExecutionSchedule(
            order_id="X",
            algo_type=AlgoType.TWAP,
            child_orders=[child],
            start_time=END,
            end_time=START,  # end < start
            total_quantity=Decimal("100"),
            created_at=NOW,
        )


# ── 审计查询 ────────────────────────────────────────────────────────────────


def test_get_schedule():
    sched = make_scheduler()
    plan = make_plan()
    sch = sched.schedule(plan, START, END, now=NOW)
    assert sched.get_schedule("ORD-001") is sch
    assert sched.get_schedule("NONEXIST") is None


def test_active_schedules():
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=2)
    sch = sched.schedule(plan, START, END, now=NOW)
    assert len(sched.active_schedules) == 1
    # 完成后不再 active
    sched.mark_sent(sch, 0, now=START)
    sched.mark_filled(sch, 0, Decimal("500"), fully=True)
    sched.mark_cancelled(sch, 1)
    assert len(sched.active_schedules) == 0


def test_clear_history():
    sched = make_scheduler()
    plan = make_plan()
    sched.schedule(plan, START, END, now=NOW)
    sched.clear_history()
    assert sched.get_schedule("ORD-001") is None


# ── to_dict ─────────────────────────────────────────────────────────────────


def test_child_to_dict():
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=2)
    sch = sched.schedule(plan, START, END, now=NOW)
    d = sch.child_orders[0].to_dict()
    assert d["quantity"] == "500"
    assert d["priority"] == "P1_HIGH"
    assert d["status"] == "SCHEDULED"


def test_schedule_to_dict():
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=2)
    sch = sched.schedule(plan, START, END, now=NOW)
    d = sch.to_dict()
    assert d["order_id"] == "ORD-001"
    assert d["algo_type"] == "TWAP"
    assert d["slice_count"] == 2
    assert "progress" in d
    assert len(d["child_orders"]) == 2


def test_progress_to_dict():
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), max_slices=2)
    sch = sched.schedule(plan, START, END, now=NOW)
    d = sch.progress().to_dict()
    assert d["total_slices"] == 2
    assert "completion_rate" in d
    assert d["is_complete"] is False


# ── ScheduledChildOrder 属性 ────────────────────────────────────────────────


def test_child_remaining_quantity():
    from zephyr.ex_sor.core.algo_trading_engine import PriceStrategy

    c = ScheduledChildOrder(
        child_order_id="C1",
        slice_index=0,
        quantity=Decimal("500"),
        price_strategy=PriceStrategy.LIMIT,
        reference_price=Decimal("10.50"),
        send_at=START,
        priority=SchedulePriority.P2_NORMAL,
        filled_quantity=Decimal("200"),
    )
    assert c.remaining_quantity == Decimal("300")


def test_child_is_terminal():
    from zephyr.ex_sor.core.algo_trading_engine import PriceStrategy

    c = ScheduledChildOrder(
        child_order_id="C1",
        slice_index=0,
        quantity=Decimal("500"),
        price_strategy=PriceStrategy.LIMIT,
        reference_price=Decimal("10.50"),
        send_at=START,
        priority=SchedulePriority.P2_NORMAL,
        status=SliceStatus.FILLED,
    )
    assert c.is_terminal
    c2 = ScheduledChildOrder(
        child_order_id="C2",
        slice_index=1,
        quantity=Decimal("500"),
        price_strategy=PriceStrategy.LIMIT,
        reference_price=Decimal("10.50"),
        send_at=START,
        priority=SchedulePriority.P2_NORMAL,
        status=SliceStatus.SCHEDULED,
    )
    assert not c2.is_terminal


# ── 集成: 计划→调度→发送→成交 ──────────────────────────────────────────────


def test_integration_full_lifecycle():
    """端到端: 生成计划→调度→逐片发送成交→完成。"""
    sched = make_scheduler()
    plan = make_plan(Decimal("1000"), AlgoType.TWAP, max_slices=5)
    sch = sched.schedule(plan, START, END, now=NOW)

    # 模拟时间推进, 逐片发送
    t = START
    for i in range(5):
        child = sch.next_due(t)
        assert child is not None
        sched.mark_sent(sch, child.slice_index, now=t)
        sched.mark_filled(sch, child.slice_index, child.quantity, fully=True)
        t += timedelta(minutes=2)

    p = sch.progress()
    assert p.is_complete
    assert p.filled == 5
    assert p.completion_rate == 1.0
    assert p.filled_quantity == Decimal("1000")
