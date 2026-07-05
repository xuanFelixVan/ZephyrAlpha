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
    def __init__(self, current: FixState, target: FixState, allowed: set[FixState] | None = None):
        self.current = current
        self.target = target
        self.allowed = allowed or set()
        super().__init__(
            f"Invalid fix transition: {current.value} -> {target.value} (allowed: {[s.value for s in self.allowed]})"
        )


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


class DriftEventRecord:
    def __init__(self, record_id="", drift_type="", state="detected", timestamp=None, details=None):
        self.record_id = record_id
        self.drift_type = drift_type
        self.state = state
        self.timestamp = timestamp
        self.details = details or {}


class DriftStateMachine:
    def __init__(self, initial_state="detected"):
        self.state = initial_state
        self.history = []

    def transition(self, new_state):
        self.history.append(self.state)
        self.state = new_state

    def can_transition(self, target):
        return True
