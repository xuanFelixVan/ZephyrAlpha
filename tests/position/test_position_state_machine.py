# [BLUEPRINT] MOD-POS-009 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""PositionStateMachine 单元测试 (MOD-POS-002)。

覆盖: 状态转换合法性 / 灰度发布4阶段 / 观察期规则 / 冷却期规则 / 事件产出。
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from zephyr.position.core.position_state_machine import (
    CooldownPeriodError,
    GraduationRegressionError,
    GraduationStage,
    InvalidTransitionError,
    ObservingReason,
    PositionState,
    PositionStateMachine,
    PositionStateMachineConfig,
    StateChangedEvent,
)

T0 = datetime(2026, 8, 1, 9, 30, tzinfo=timezone.utc)


def _mk(symbol: str = "000001.SZ", **cfg) -> PositionStateMachine:
    # 注入冻结时钟锚定 T0：is_in_cooldown 等无 now 参数的属性走 self._clock()，
    # 默认真实时钟会随日历漂移（T0=2026-08-01 硬编码）导致断言过期。
    return PositionStateMachine(symbol, PositionStateMachineConfig(**cfg) if cfg else None, clock=lambda: T0)


# ── 初始状态 ──────────────────────────────────────────────────────────────────


def test_initial_state_is_none():
    fsm = _mk()
    assert fsm.state == PositionState.NONE
    assert fsm.graduation_stage == GraduationStage.NONE
    assert fsm.graduation_weight == 0.0
    assert fsm.can_buy() is True
    assert fsm.is_observing is False
    assert fsm.is_in_cooldown is False


# ── 正常生命周期 ──────────────────────────────────────────────────────────────


def test_normal_lifecycle_full_path():
    fsm = _mk()
    fsm.start_building(now=T0)
    assert fsm.state == PositionState.BUILDING
    assert fsm.graduation_stage == GraduationStage.STAGE_1_5PCT

    fsm.activate(now=T0)
    assert fsm.state == PositionState.ACTIVE
    assert fsm.graduation_stage == GraduationStage.STAGE_4_100PCT
    assert fsm.graduation_weight == 1.0

    fsm.enter_observing(ObservingReason.SOFT_STOP, now=T0 + timedelta(hours=1))
    assert fsm.state == PositionState.OBSERVING
    assert fsm.can_buy() is False

    fsm.exit_observing(confirm=True, now=T0 + timedelta(hours=1, minutes=10))
    assert fsm.state == PositionState.REDUCING

    fsm.start_exiting(now=T0 + timedelta(hours=2))
    assert fsm.state == PositionState.EXITING

    fsm.close(now=T0 + timedelta(hours=3))
    assert fsm.state == PositionState.CLOSED
    assert fsm.is_in_cooldown is True


# ── 非法转换 ──────────────────────────────────────────────────────────────────


def test_invalid_transition_raises():
    fsm = _mk()
    # NONE 不能直接到 ACTIVE
    with pytest.raises(InvalidTransitionError):
        fsm.activate(now=T0)


# ── 灰度发布4阶段 ─────────────────────────────────────────────────────────────


def test_graduation_advancement_four_stages():
    cfg = PositionStateMachineConfig(graduation_stage_days=1)
    fsm = PositionStateMachine("000001.SZ", cfg)
    fsm.start_building(now=T0)
    assert fsm.graduation_weight == 0.05

    # 阶段1→2 (需满1天)
    fsm.advance_graduation(now=T0 + timedelta(days=1, seconds=1))
    assert fsm.graduation_stage == GraduationStage.STAGE_2_20PCT
    assert fsm.graduation_weight == 0.20

    # 阶段2→3
    fsm.advance_graduation(now=T0 + timedelta(days=2, seconds=2))
    assert fsm.graduation_stage == GraduationStage.STAGE_3_50PCT

    # 阶段3→4 满仓, 自动转 ACTIVE
    ev = fsm.advance_graduation(now=T0 + timedelta(days=3, seconds=3))
    assert fsm.graduation_stage == GraduationStage.STAGE_4_100PCT
    assert fsm.state == PositionState.ACTIVE
    assert ev.to_state == PositionState.ACTIVE


def test_graduation_too_fast_blocked():
    cfg = PositionStateMachineConfig(graduation_stage_days=5)
    fsm = PositionStateMachine("000001.SZ", cfg)
    fsm.start_building(now=T0)
    # 仅过1天, 要求5天
    with pytest.raises(GraduationRegressionError):
        fsm.advance_graduation(now=T0 + timedelta(days=1))


def test_graduation_regression_at_full_blocked():
    fsm = _mk()
    fsm.start_building(now=T0)
    fsm.activate(now=T0)  # 直接满仓
    # 已满仓, 不能再推进
    with pytest.raises(GraduationRegressionError):
        fsm.advance_graduation(now=T0 + timedelta(days=10))


def test_graduation_advance_only_in_building():
    fsm = _mk()
    fsm.start_building(now=T0)
    fsm.activate(now=T0)
    with pytest.raises(GraduationRegressionError):
        fsm.advance_graduation(now=T0 + timedelta(days=10))


# ── 观察期 ────────────────────────────────────────────────────────────────────


def test_observing_blocks_buy():
    fsm = _mk()
    fsm.start_building(now=T0)
    fsm.activate(now=T0)
    fsm.enter_observing(ObservingReason.PLUNGE, now=T0 + timedelta(hours=1))
    assert fsm.can_buy() is False
    assert fsm.is_observing is True


def test_observing_clear_returns_to_active():
    fsm = _mk()
    fsm.start_building(now=T0)
    fsm.activate(now=T0)
    fsm.enter_observing(ObservingReason.ABNORMAL_OPEN, now=T0)
    ev = fsm.exit_observing(confirm=False, now=T0 + timedelta(minutes=5))
    assert fsm.state == PositionState.ACTIVE
    assert fsm.can_buy() is True
    assert ev.reason == "observing_cleared"


def test_observing_confirm_goes_to_reducing():
    fsm = _mk()
    fsm.start_building(now=T0)
    fsm.activate(now=T0)
    fsm.enter_observing(ObservingReason.SOFT_STOP, now=T0)
    ev = fsm.exit_observing(confirm=True, now=T0 + timedelta(minutes=14))
    assert fsm.state == PositionState.REDUCING
    assert ev.reason == "observing_confirmed"


# ── 冷却期 ────────────────────────────────────────────────────────────────────


def test_cooldown_blocks_rebuild():
    fsm = _mk()
    fsm.start_building(now=T0)
    fsm.activate(now=T0)
    fsm.start_exiting(now=T0 + timedelta(hours=1))
    cooldown_until = T0 + timedelta(days=5)
    fsm.close(cooldown_until=cooldown_until, now=T0 + timedelta(hours=2))
    assert fsm.is_in_cooldown is True
    assert fsm.can_rebuild(now=T0 + timedelta(hours=3)) is False
    with pytest.raises(CooldownPeriodError):
        fsm.start_building(now=T0 + timedelta(hours=3))


def test_cooldown_expired_allows_rebuild():
    fsm = _mk()
    fsm.start_building(now=T0)
    fsm.activate(now=T0)
    fsm.start_exiting(now=T0 + timedelta(hours=1))
    cooldown_until = T0 + timedelta(days=5)
    fsm.close(cooldown_until=cooldown_until, now=T0 + timedelta(hours=2))
    # 冷却期过后
    after = T0 + timedelta(days=6)
    assert fsm.can_rebuild(now=after) is True
    ev = fsm.start_building(now=after)
    assert fsm.state == PositionState.BUILDING
    assert fsm.graduation_stage == GraduationStage.STAGE_1_5PCT
    assert ev.from_state == PositionState.CLOSED


def test_close_default_cooldown():
    fsm = _mk()
    fsm.start_building(now=T0)
    fsm.start_exiting(now=T0)
    fsm.close(now=T0)  # 不传 cooldown_until, 默认5自然日
    assert fsm.context.cooldown_until == T0 + timedelta(days=5)


# ── 事件 ──────────────────────────────────────────────────────────────────────


def test_state_changed_event_emitted():
    fsm = _mk()
    events: list[StateChangedEvent] = []
    fsm.on_state_changed(events.append)
    fsm.start_building(now=T0)
    assert len(events) == 1
    ev = events[0]
    assert ev.symbol == "000001.SZ"
    assert ev.from_state == PositionState.NONE
    assert ev.to_state == PositionState.BUILDING
    assert ev.reason == "start_building"
    assert ev.context_snapshot["graduation_stage"] == GraduationStage.STAGE_1_5PCT.value


def test_listener_exception_does_not_block():
    fsm = _mk()

    def bad(_ev: StateChangedEvent) -> None:
        raise RuntimeError("boom")

    fsm.on_state_changed(bad)
    # 不应抛
    fsm.start_building(now=T0)
    assert fsm.state == PositionState.BUILDING


# ── 历史记录 ──────────────────────────────────────────────────────────────────


def test_history_records_transitions():
    fsm = _mk()
    fsm.start_building(now=T0)
    fsm.activate(now=T0)
    hist = fsm.history
    assert len(hist) == 2
    assert hist[0][0] == PositionState.NONE
    assert hist[0][1] == PositionState.BUILDING
    assert hist[1][1] == PositionState.ACTIVE


# ── reset ─────────────────────────────────────────────────────────────────────


def test_reset_clears_state():
    fsm = _mk()
    fsm.start_building(now=T0)
    fsm.activate(now=T0)
    fsm.reset(now=T0)
    assert fsm.state == PositionState.NONE
    assert fsm.graduation_stage == GraduationStage.NONE
