# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.state_machine
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.state_machine
# [CONSUMERS] engine.py;fix_reliability.py;fix_health_check.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 状态转换必须合法;DEAD_LETTER为终态;CLOSED为终态
# [MODIFY-GUARD] blueprint.md §3; _fixer-registry.yaml
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidFixTransitionError
# [TESTS] tests/auto-fix-engine/test_state_machine.py
# [A_module] module_id=MOD-INF_state_machine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from threading import RLock
from typing import Any

logger = logging.getLogger(__name__)


class FixState(str, Enum):
    DETECTED = "detected"
    DIAGNOSED = "diagnosed"
    TRIAGED = "triaged"
    ACKNOWLEDGED = "acknowledged"
    RESOLVING = "resolving"
    RESOLVED = "resolved"
    VERIFIED = "verified"
    CLOSED = "closed"
    DEAD_LETTER = "dead_letter"


_TERMINAL_STATES = {FixState.CLOSED, FixState.DEAD_LETTER}

_TRANSITIONS: dict[FixState, set[FixState]] = {
    FixState.DETECTED: {FixState.DIAGNOSED, FixState.DEAD_LETTER},
    FixState.DIAGNOSED: {FixState.TRIAGED, FixState.DEAD_LETTER},
    FixState.TRIAGED: {FixState.ACKNOWLEDGED, FixState.DEAD_LETTER},
    FixState.ACKNOWLEDGED: {
        FixState.RESOLVING,
        FixState.DEAD_LETTER,
        FixState.CANCELLED if hasattr(FixState, "CANCELLED") else FixState.DEAD_LETTER,
    },
    FixState.RESOLVING: {FixState.RESOLVED, FixState.DEAD_LETTER},
    FixState.RESOLVED: {FixState.VERIFIED, FixState.RESOLVING, FixState.DEAD_LETTER},
    FixState.VERIFIED: {FixState.CLOSED, FixState.RESOLVING},
    FixState.CLOSED: set(),
    FixState.DEAD_LETTER: set(),
}

_TRANSITIONS[FixState.ACKNOWLEDGED] = {FixState.RESOLVING, FixState.DEAD_LETTER}


class InvalidFixTransitionError(Exception):
    error_code = "ZA-IF-0005"

    def __init__(self, current: FixState, target: FixState, allowed: set[FixState] | None = None, error_code: str | None = None):
        self.current = current
        self.target = target
        self.allowed = allowed or set()
        super().__init__(
            f"Invalid fix transition: {current.value} -> {target.value} (allowed: {[s.value for s in self.allowed]})"
        )
        if error_code is not None:
            self.error_code = error_code


class FixStateMachine:
    def __init__(self, initial: FixState = FixState.DETECTED) -> None:
        self._current = initial
        self._lock = RLock()
        self._history: list[tuple[FixState, FixState, dict[str, Any] | None]] = []

    @property
    def current_state(self) -> FixState:
        with self._lock:
            return self._current

    @property
    def is_terminal(self) -> bool:
        with self._lock:
            return self._current in _TERMINAL_STATES

    @property
    def available_transitions(self) -> list[FixState]:
        with self._lock:
            return list(_TRANSITIONS.get(self._current, set()))

    @property
    def history(self) -> list[tuple[FixState, FixState, dict[str, Any] | None]]:
        with self._lock:
            return list(self._history)

    def can_transition(self, target: FixState) -> bool:
        with self._lock:
            return target in _TRANSITIONS.get(self._current, set())

    def transition(self, target: FixState, context: dict[str, Any] | None = None) -> FixState:
        with self._lock:
            allowed = _TRANSITIONS.get(self._current, set())
            if target not in allowed:
                raise InvalidFixTransitionError(self._current, target, allowed)
            previous = self._current
            self._current = target
            self._history.append((previous, target, context))
            logger.info("Fix state transition: %s -> %s", previous.value, target.value)
            return self._current

    def force_state(self, target: FixState) -> FixState:
        with self._lock:
            previous = self._current
            self._current = target
            self._history.append((previous, target, {"forced": True}))
            logger.warning("Forced fix state transition: %s -> %s", previous.value, target.value)
            return self._current

    def to_dead_letter(self, reason: str = "") -> FixState:
        with self._lock:
            previous = self._current
            self._current = FixState.DEAD_LETTER
            self._history.append((previous, FixState.DEAD_LETTER, {"reason": reason}))
            logger.error("Fix entered DEAD_LETTER from %s: %s", previous.value, reason)
            return self._current

    def reset(self) -> FixState:
        with self._lock:
            self._current = FixState.DETECTED
            self._history.clear()
            return self._current


@dataclass
class DriftEventRecord:
    """漂移事件记录——对齐 test_state_machine.py 契约（裁定#17 F1 治本）。

    旧桩实现仅含 record_id/drift_type/state/timestamp/details，与测试期望的
    event_id/state/created_at/updated_at/resolved_by/resolution_detail/resolved_at/
    auto_fixable/needs_human/suppressed_until 字段完全不符——这是 API 漂移导致的桩实现。

    治本（5.168 阶段0）：改用 @dataclass 消除 NO-LONG-PARAM-LIST 门禁违规
    （原 __init__ 10 参数 >7），通过 __post_init__ 保留 None 即当前时间 语义。
    """

    event_id: str | None = None
    state: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    resolved_by: str | None = None
    resolution_detail: str | None = None
    resolved_at: datetime | None = None
    auto_fixable: bool = False
    needs_human: bool = False
    suppressed_until: datetime | None = None

    def __post_init__(self) -> None:
        # 治本：created_at/updated_at 默认填当前时间（对齐 test_init_with_defaults）
        now = datetime.now(UTC)
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now


# DriftState 转换矩阵（对齐 test_state_machine.py TestValidateTransition）
_DRIFT_TRANSITIONS: dict = {
    "DETECTED": {"TRIAGED", "ACKNOWLEDGED", "FALSE_POSITIVE", "DEAD_LETTER"},
    "TRIAGED": {"RESOLVING", "ACKNOWLEDGED", "FALSE_POSITIVE", "DEAD_LETTER"},
    "ACKNOWLEDGED": {"RESOLVING", "DEAD_LETTER"},
    "RESOLVING": {"RESOLVED", "FIX_FAILED", "DEAD_LETTER"},
    "FIX_FAILED": {"ACKNOWLEDGED"},
    "RESOLVED": {"VERIFIED"},
    "VERIFIED": set(),
    "FALSE_POSITIVE": set(),
    "DEAD_LETTER": {"ACKNOWLEDGED"},
    "SUPPRESSED": {"DETECTED"},
}

# 漂移终态（对齐 test_state_machine.py TestTerminalStatesConstant——VERIFIED + FALSE_POSITIVE）
# 使用 DriftState 枚举成员，使 `DriftState.VERIFIED in TERMINAL_STATES` 为真
def _build_terminal_drift_states():
    from zephyr.gov_drift.drift_models import DriftState

    return {DriftState.VERIFIED, DriftState.FALSE_POSITIVE}


_TERMINAL_DRIFT_STATES = _build_terminal_drift_states()


class InvalidTransitionError(Exception):
    """漂移状态机非法转换异常（公开别名，对齐测试 import）。"""

    pass


# 公开别名：测试 import TERMINAL_STATES（漂移终态，非 FixState 终态）
TERMINAL_STATES = _TERMINAL_DRIFT_STATES


class DriftStateMachine:
    """漂移状态机——对齐 test_state_machine.py 契约（裁定#17 F1 治本）。

    旧桩实现仅 state/history 两个字段 + transition/can_transition 两方法，与测试期望的
    validate_transition/transition(eid,from,to)/auto_transition/check_ttl/suppress/
    get_state/mark_auto_fixable/is_terminal 完全不符——这是 API 漂移导致的桩实现。
    """

    TTL_DETECTED_HOURS: int = 24

    def __init__(self) -> None:
        self._events: dict = {}

    @staticmethod
    def _state_value(state) -> str:
        """归一化 DriftState 枚举或字符串为字符串值。"""
        return state.value if hasattr(state, "value") else str(state)

    def validate_transition(self, from_state, to_state) -> bool:
        from_val = self._state_value(from_state)
        to_val = self._state_value(to_state)
        if from_val == to_val:
            return False
        allowed = _DRIFT_TRANSITIONS.get(from_val, set())
        return to_val in allowed

    def transition(
        self,
        event_id,
        from_state,
        to_state,
        resolved_by=None,
        resolution_detail=None,
    ):
        if event_id not in self._events:
            # 首次转换：创建记录
            if self._state_value(from_state) != "DETECTED" and from_state is not None:
                raise InvalidTransitionError(
                    f"Event not found and from_state={from_state} is not DETECTED"
                )
            from datetime import UTC, datetime

            self._events[event_id] = DriftEventRecord(
                event_id=event_id,
                state=from_state,
                created_at=datetime.now(UTC),
            )
        else:
            rec = self._events[event_id]
            if self._state_value(rec.state) != self._state_value(from_state):
                raise InvalidTransitionError(
                    f"State mismatch: expected {from_state}, got {rec.state}"
                )
            from datetime import UTC, datetime

            rec.updated_at = datetime.now(UTC)

        if not self.validate_transition(from_state, to_state):
            raise InvalidTransitionError(
                f"Invalid transition: {from_state} -> {to_state}"
            )

        from datetime import UTC, datetime

        rec = self._events[event_id]
        rec.state = to_state
        rec.updated_at = datetime.now(UTC)

        to_val = self._state_value(to_state)
        if to_val == "RESOLVED":
            rec.resolved_at = datetime.now(UTC)
            # 治本：空字符串视为未设置（对齐 test_transition_with_empty_resolved_by_not_set）
            if resolved_by:
                rec.resolved_by = resolved_by
            if resolution_detail:
                rec.resolution_detail = resolution_detail
        else:
            if resolved_by:
                rec.resolved_by = resolved_by
            if resolution_detail:
                rec.resolution_detail = resolution_detail

        return to_state

    def auto_transition(self, event_id):
        if event_id not in self._events:
            return None
        rec = self._events[event_id]
        state_val = self._state_value(rec.state)

        from datetime import UTC, datetime

        if state_val == "RESOLVED":
            self.transition(event_id, rec.state, _drift_state_value("VERIFIED"))
            return _drift_state_value("VERIFIED")
        if state_val == "TRIAGED":
            if rec.auto_fixable:
                self.transition(event_id, rec.state, _drift_state_value("RESOLVING"))
                return _drift_state_value("RESOLVING")
            return None
        if state_val == "FIX_FAILED":
            self.transition(event_id, rec.state, _drift_state_value("ACKNOWLEDGED"))
            rec.needs_human = True
            return _drift_state_value("ACKNOWLEDGED")
        return None

    def check_ttl(self) -> list:
        from datetime import UTC, datetime, timedelta

        now = datetime.now(UTC)
        expired = []
        for eid, rec in self._events.items():
            state_val = self._state_value(rec.state)
            if state_val == "DETECTED" and rec.created_at is not None:
                if now - rec.created_at > timedelta(hours=self.TTL_DETECTED_HOURS):
                    self.transition(eid, rec.state, _drift_state_value("DEAD_LETTER"))
                    expired.append(eid)
            elif state_val == "SUPPRESSED" and rec.suppressed_until is not None:
                if now > rec.suppressed_until:
                    self.transition(eid, rec.state, _drift_state_value("DETECTED"))
                    expired.append(eid)
        return expired

    def suppress(self, event_id, until):
        if event_id not in self._events:
            raise InvalidTransitionError(f"Event not found")
        rec = self._events[event_id]
        if not self.validate_transition(rec.state, _drift_state_value("SUPPRESSED")):
            raise InvalidTransitionError(
                f"No valid transition to SUPPRESSED from {rec.state}"
            )
        self.transition(event_id, rec.state, _drift_state_value("SUPPRESSED"))
        rec.suppressed_until = until

    def get_state(self, event_id):
        if event_id not in self._events:
            return None
        return self._events[event_id].state

    def mark_auto_fixable(self, event_id) -> None:
        if event_id in self._events:
            self._events[event_id].auto_fixable = True

    def is_terminal(self, event_id) -> bool:
        if event_id not in self._events:
            return False
        return self._events[event_id].state in _TERMINAL_DRIFT_STATES


def _drift_state_value(name: str):
    """从状态名字符串获取 DriftState 枚举值（延迟 import 避免循环依赖）。"""
    from zephyr.gov_drift.drift_models import DriftState

    return getattr(DriftState, name)
