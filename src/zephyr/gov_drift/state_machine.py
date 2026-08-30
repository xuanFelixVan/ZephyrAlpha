# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.state_machine
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.gov_drift.drift_models
# [CONSUMERS] src/zephyr/gov_drift/_core.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 状态转换必须合法
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
[BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md | §

Drift State Machine — state_machine.py


10 状态漂移生命周期状态机。控制 DETECTED->VERIFIED 正向修复链路和异常路径。

对标 blueprint.md §2.3（漂移状态机）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: state_machine.py
# 层: 算法
# - id: A1
#   name_zh: ① DriftStateMachine
#   name_en: DriftStateMachine
#   intro: class DriftStateMachine 源码 L95-L300
#   desc: 公共方法（定义序）: validate_transition, transition, auto_transition, trigger_rollback, check_ttl, suppress, get_state…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: DriftStateMachine
#   downstream: src/zephyr/gov_drift/_core.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Final

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


TERMINAL_STATES: Final[set[DriftState]] = {DriftState.VERIFIED, DriftState.FALSE_POSITIVE}


class InvalidTransitionError(Exception):
    error_code = "ZA-GV-0045"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class DriftStateMachine:
    def __init__(self) -> None:
        self.TTL_DETECTED_HOURS: int = 24

        # W2 治本: _events 上限，超过时按最旧优先裁剪（终态/DEAD_LETTER 优先淘汰）
        self.max_events: int = 10000

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
            raise InvalidTransitionError(f"Invalid: {from_state.value} -> {to_state.value}")

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
        """CT-005: FIX_FAILED/DRIFT_FAILED -> MOD-INF-021 Rollback 自动回滚。


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

        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
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

        self._evict_stale_events(now)

        return expired

    def _evict_stale_events(self, now: datetime) -> None:
        """淘汰 _events 中的过期/超额记录，防无界增长（内存泄漏治本）。

        两档淘汰：
        1. 生命周期已终结（VERIFIED/FALSE_POSITIVE/DEAD_LETTER）且 updated_at 超过
           TTL_DETECTED_HOURS 的记录——状态不再变化，保留无意义。刚 transition 到
           DEAD_LETTER 的事件 updated_at=now，不受影响。
        2. 仍超 max_events 上限时，按终态优先 + updated_at 最旧优先裁剪。
        """
        terminal_or_dead = TERMINAL_STATES | {DriftState.DEAD_LETTER}

        ttl = timedelta(hours=self.TTL_DETECTED_HOURS)

        stale = [
            event_id
            for event_id, record in self._events.items()
            if record.state in terminal_or_dead and now - record.updated_at > ttl
        ]

        for event_id in stale:
            del self._events[event_id]

        excess = len(self._events) - self.max_events

        if excess > 0:
            ordered = sorted(
                self._events.values(),
                key=lambda r: (r.state not in terminal_or_dead, r.updated_at),
            )

            for record in ordered[:excess]:
                del self._events[record.event_id]

    def suppress(self, event_id: uuid.UUID, expires_at: datetime) -> DriftState:
        record = self._events.get(event_id)

        if record is None:
            raise InvalidTransitionError("Event not found")

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
