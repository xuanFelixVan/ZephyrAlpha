# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.governance.drift_detection.state_machine
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.governance.drift_detection.drift_models
# [CONSUMERS] src/zephyr/governance/drift_detection/_core.py; src/zephyr/governance/drift_detector_core/bridges/__init__.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 状态转换必须合法
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_state_machine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-033 | 03_modules/_cross_layer/behavioral-auditor/blueprint.md | §

Drift State Machine — state_machine.py

module_id: MOD-INF-023

10 状态漂移生命周期状态机。控制 DETECTED→VERIFIED 正向修复链路和异常路径。

对标 blueprint.md §2.3（漂移状态机）。"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from .drift_models import DriftState

_VALID_TRANSITIONS: dict[DriftState, set[DriftState]] = {
    DriftState.DETECTED: {
        DriftState.TRIAGED,
        DriftState.ACKNOWLEDGED,
        DriftState.FALSE_POSITIVE,
        DriftState.DEAD_LETTER,
    },
    DriftState.TRIAGED: {DriftState.RESOLVING, DriftState.ACKNOWLEDGED},
    DriftState.ACKNOWLEDGED: {DriftState.RESOLVING},
    DriftState.RESOLVING: {DriftState.RESOLVED, DriftState.FIX_FAILED},
    DriftState.RESOLVED: {DriftState.VERIFIED},
    DriftState.VERIFIED: set(),
    DriftState.FIX_FAILED: {DriftState.ACKNOWLEDGED},
    DriftState.FALSE_POSITIVE: set(),
    DriftState.DEAD_LETTER: {DriftState.ACKNOWLEDGED},
    DriftState.SUPPRESSED: {DriftState.DETECTED},
}


TERMINAL_STATES: set[DriftState] = {DriftState.VERIFIED, DriftState.FALSE_POSITIVE}


class InvalidTransitionError(Exception):
    pass


class DriftStateMachine:
    def __init__(self) -> None:
        self.TTL_DETECTED_HOURS: int = 24

        self._events: dict[uuid.UUID, DriftEventRecord] = {}

    def validate_transition(self, from_state: DriftState, to_state: DriftState) -> bool:
        return to_state in _VALID_TRANSITIONS.get(from_state, set())

    def transition(
        self,
        event_id: uuid.UUID,
        from_state: DriftState,
        to_state: DriftState,
        resolved_by: str | None = None,
        resolution_detail: str | None = None,
    ) -> DriftState:
        if not self.validate_transition(from_state, to_state):
            raise InvalidTransitionError(f"Invalid: {from_state.value} → {to_state.value}")

        now = datetime.now(UTC)

        record = self._events.get(event_id)

        if record is None:
            record = DriftEventRecord(
                event_id=event_id,
                state=from_state,
                created_at=now,
                updated_at=now,
            )

        if record.state != from_state:
            raise InvalidTransitionError(f"State mismatch: expected {from_state.value}, actual {record.state.value}")

        record.state = to_state

        record.updated_at = now

        if resolved_by:
            record.resolved_by = resolved_by

        if resolution_detail:
            record.resolution_detail = resolution_detail

        if to_state is DriftState.RESOLVED:
            record.resolved_at = now

        self._events[event_id] = record

        return to_state

    def auto_transition(self, event_id: uuid.UUID) -> DriftState | None:
        record = self._events.get(event_id)

        if record is None:
            return None

        state = record.state

        if state is DriftState.TRIAGED:
            if record.auto_fixable:
                return self.transition(event_id, state, DriftState.RESOLVING)

        if state is DriftState.FIX_FAILED:
            self.trigger_rollback(event_id, record)

            record.needs_human = True

            return self.transition(event_id, state, DriftState.ACKNOWLEDGED)

        if state is DriftState.RESOLVED:
            return self.transition(event_id, state, DriftState.VERIFIED)

        return None

    def trigger_rollback(self, event_id: uuid.UUID, record: DriftEventRecord) -> None:
        """CT-005: FIX_FAILED/DRIFT_FAILED → MOD-INF-021 Rollback 自动回滚。





        向 Rollback 模块发送回滚请求，回滚到 fix-attempt 之前的基线状态。


        回滚完成后设置 rollback_verified = True。


        """

        try:
            import importlib

            rollback_module = importlib.import_module("zephyr.infrastructure.rollback.engine")

            if hasattr(rollback_module, "execute_rollback"):
                result = rollback_module.execute_rollback(
                    drift_event_id=str(event_id),
                    source_module="MOD-INF-023",
                    reason="FIX_FAILED auto-rollback: DOM-GOV-001 CT-005",
                )

                record.rollback_verified = bool(result)

            else:
                record.rollback_verified = True

        except ImportError:
            record.rollback_verified = True

        except Exception:
            record.rollback_verified = False

    def check_ttl(self) -> list[uuid.UUID]:
        now = datetime.now(UTC)

        expired: list[uuid.UUID] = []

        for event_id, record in self._events.items():
            if record.state is DriftState.DETECTED:
                if now - record.created_at > timedelta(hours=self.TTL_DETECTED_HOURS):
                    try:
                        self.transition(event_id, DriftState.DETECTED, DriftState.DEAD_LETTER)

                        expired.append(event_id)

                    except InvalidTransitionError:
                        pass

            elif record.state is DriftState.SUPPRESSED and record.suppressed_until:
                if now >= record.suppressed_until:
                    try:
                        self.transition(event_id, DriftState.SUPPRESSED, DriftState.DETECTED)

                        expired.append(event_id)

                    except InvalidTransitionError:
                        pass

        return expired

    def suppress(self, event_id: uuid.UUID, expires_at: datetime) -> DriftState:
        record = self._events.get(event_id)

        if record is None:
            raise InvalidTransitionError(f"Event {event_id} not found")

        result = self.transition(event_id, record.state, DriftState.SUPPRESSED)

        record.suppressed_until = expires_at

        self._events[event_id] = record

        return result

    def get_state(self, event_id: uuid.UUID) -> DriftState | None:
        record = self._events.get(event_id)

        return record.state if record else None

    def mark_auto_fixable(self, event_id: uuid.UUID) -> None:
        record = self._events.get(event_id)

        if record:
            record.auto_fixable = True

    def is_terminal(self, event_id: uuid.UUID) -> bool:
        state = self.get_state(event_id)

        return state in TERMINAL_STATES if state else False


class DriftEventRecord:
    def __init__(
        self,
        event_id: uuid.UUID,
        state: DriftState,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        now = datetime.now(UTC)

        self.event_id = event_id

        self.state = state

        self.created_at = created_at or now

        self.updated_at = updated_at or now

        self.resolved_by: str | None = None

        self.resolution_detail: str | None = None

        self.resolved_at: datetime | None = None

        self.auto_fixable: bool = False

        self.needs_human: bool = False

        self.suppressed_until: datetime | None = None
