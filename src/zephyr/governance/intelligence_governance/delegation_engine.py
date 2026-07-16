# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.delegation_engine
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.escalation.escalation_models; zephyr.security.llm_defense.llm_security.gateway
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_delegation_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Delegation Engine — MOD-INF-022

Auto-delegation when owner absent, overloaded, or escalation rules demand it.
Supports load-balanced, expertise-match, round-robin, and priority-queue strategies.
Blueprint: docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md §4
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import threading
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界

from zephyr.governance.escalation.escalation_models import (
    DelegationRecord,
    DelegationStrategy,
    EscalationEvent,
    EscalationState,
)


class DelegationEngine:
    MAX_LOAD_PER_DELEGATE = 5
    DELEGATION_TIMEOUT_HOURS = 24
    MAX_DELEGATION_DEPTH = 3

    def __init__(self, deadlock_detector=None):
        self._delegate_load: dict[str, int] = defaultdict(int)
        self._delegate_expertise: dict[str, set[str]] = defaultdict(set)
        self._active_delegations: dict[str, DelegationRecord] = {}
        self._delegation_history: list[DelegationRecord] = []
        self._round_robin_index: int = 0
        self._lock = threading.Lock()
        self._deadlock_detector = deadlock_detector
        self._delegation_depth: dict[str, int] = {}

    def register_delegate(self, delegate_id: str, expertise: list[str] | None = None) -> None:
        with self._lock:
            self._delegate_load.setdefault(delegate_id, 0)
            if expertise:
                self._delegate_expertise[delegate_id] = set(expertise)

    def unregister_delegate(self, delegate_id: str) -> None:
        with self._lock:
            self._delegate_load.pop(delegate_id, None)
            self._delegate_expertise.pop(delegate_id, None)
            expired = [k for k, v in self._active_delegations.items() if v.to_delegate == delegate_id]
            for k in expired:
                self._active_delegations.pop(k, None)

    def delegate(
        self,
        event: EscalationEvent,
        strategy: DelegationStrategy = DelegationStrategy.LOAD_BALANCED,
        task_id: str | None = None,
    ) -> DelegationRecord:
        self._lsg_verify_delegation(event)

        depth_key = task_id or event.event_id or ""
        current_depth = self._delegation_depth.get(depth_key, 0)

        record = _check_depth_exceeded(self, current_depth, event, task_id, strategy)
        if record is not None:
            return record

        record = _check_deadlock(self, event, task_id, strategy)
        if record is not None:
            return record

        delegate_id = self._select_delegate(event, strategy)
        record = _handle_no_delegate(self, delegate_id, event, task_id, strategy)
        if record is not None:
            return record

        record = DelegationRecord(
            from_owner=event.owner_id or "",
            to_delegate=delegate_id,
            task_id=task_id,
            strategy=strategy,
            expires_at=datetime.now(UTC) + timedelta(hours=self.DELEGATION_TIMEOUT_HOURS),
        )

        with self._lock:
            self._delegate_load[delegate_id] += 1
            self._active_delegations[record.delegation_id] = record
            self._delegation_history.append(record)
            if depth_key:
                self._delegation_depth[depth_key] = current_depth + 1

        event.delegate_id = delegate_id
        event.state = EscalationState.DELEGATED
        return record

    def get_delegation_history(self) -> list[DelegationRecord]:
        with self._lock:
            return list(self._delegation_history)

    def get_delegation_depth(self, task_id: str) -> int:
        return self._delegation_depth.get(task_id, 0)

    def accept_delegation(self, delegation_id: str) -> bool:
        with self._lock:
            record = self._active_delegations.get(delegation_id)
            if record is None:
                return False
            if record.expires_at and datetime.now(UTC) > record.expires_at:
                self._active_delegations.pop(delegation_id, None)
                return False
            record.accepted = True
            return True

    def complete_delegation(self, delegation_id: str) -> bool:
        with self._lock:
            record = self._active_delegations.pop(delegation_id, None)
            if record is None:
                return False
            record.completed = True
            self._delegate_load[record.to_delegate] = max(0, self._delegate_load.get(record.to_delegate, 1) - 1)
            return True

    def reject_delegation(self, delegation_id: str) -> bool:
        with self._lock:
            record = self._active_delegations.pop(delegation_id, None)
            if record is None:
                return False
            self._delegate_load[record.to_delegate] = max(0, self._delegate_load.get(record.to_delegate, 1) - 1)
            return True

    def get_load(self, delegate_id: str) -> int:
        return self._delegate_load.get(delegate_id, 0)

    def get_available_delegates(self) -> list[str]:
        with self._lock:
            return [d for d, load in self._delegate_load.items() if load < self.MAX_LOAD_PER_DELEGATE]

    def get_pending_delegations(self) -> list[DelegationRecord]:
        with self._lock:
            now = datetime.now(UTC)
            return [
                r
                for r in self._active_delegations.values()
                if not r.accepted and (r.expires_at is None or now <= r.expires_at)
            ]

    def cleanup_expired(self) -> int:
        count = 0
        with self._lock:
            now = datetime.now(UTC)
            expired_ids = [
                k for k, v in self._active_delegations.items() if v.expires_at is not None and now > v.expires_at
            ]
            for k in expired_ids:
                record = self._active_delegations.pop(k)
                self._delegate_load[record.to_delegate] = max(0, self._delegate_load.get(record.to_delegate, 1) - 1)
                count += 1
        return count

    def _select_delegate(self, event: EscalationEvent, strategy: DelegationStrategy) -> str | None:
        available = self.get_available_delegates()
        if not available:
            return None

        owner_id = event.owner_id or ""
        available = [d for d in available if d != owner_id]
        if not available:
            return None

        if strategy is DelegationStrategy.EXPERTISE_MATCH:
            return self._select_expertise(event, available)
        elif strategy is DelegationStrategy.ROUND_ROBIN:
            return self._select_round_robin(available)
        elif strategy is DelegationStrategy.PRIORITY_QUEUE:
            return self._select_least_loaded(available)
        else:
            return self._select_least_loaded(available)

    def _select_least_loaded(self, available: list[str]) -> str | None:
        if not available:
            return None
        return min(available, key=lambda d: self._delegate_load.get(d, 0))

    def _select_round_robin(self, available: list[str]) -> str | None:
        if not available:
            return None
        with self._lock:
            idx = self._round_robin_index % len(available)
            self._round_robin_index += 1
            return available[idx]

    def _select_expertise(self, event: EscalationEvent, available: list[str]) -> str | None:
        category_key = event.category.value if hasattr(event.category, "value") else str(event.category)
        experts = [d for d in available if category_key in self._delegate_expertise.get(d, set())]
        if experts:
            return min(experts, key=lambda d: self._delegate_load.get(d, 0))
        return self._select_least_loaded(available)

    def _lsg_verify_delegation(self, event: EscalationEvent) -> None:
        try:
            import asyncio

            from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway

            gateway = LSGSecurityGateway()
            content = f"delegation:{event.description} from:{event.owner_id}"
            result = run_sync(gateway.scan_agent_action(content, tool_name="escalation_delegation"))
            if result.decision.value not in ("allow", "ALLOW"):
                raise PermissionError(f"LSG blocked delegation: {result.decision.value}")
        except ImportError:
            pass


def _check_depth_exceeded(engine, current_depth, event, task_id, strategy):
    if current_depth >= engine.MAX_DELEGATION_DEPTH:
        record = DelegationRecord(
            from_owner=event.owner_id or "",
            task_id=task_id,
            strategy=strategy,
            expires_at=datetime.now(UTC) + timedelta(hours=engine.DELEGATION_TIMEOUT_HOURS),
        )
        record.depth_exceeded = True
        return record
    return None


def _check_deadlock(engine, event, task_id, strategy):
    if engine._deadlock_detector is not None:
        try:
            cycle = engine._deadlock_detector.detect_cycle(event.owner_id or "", None)
            if cycle:
                record = DelegationRecord(
                    from_owner=event.owner_id or "",
                    task_id=task_id,
                    strategy=strategy,
                    expires_at=datetime.now(UTC) + timedelta(hours=engine.DELEGATION_TIMEOUT_HOURS),
                )
                record.deadlock_detected = True
                return record
        except Exception as e:
            logger.warning("suppressed error in delegation_engine", exc_info=True)
    return None


def _handle_no_delegate(engine, delegate_id, event, task_id, strategy):
    if delegate_id is None or delegate_id == event.owner_id:
        record = DelegationRecord(
            from_owner=event.owner_id or "",
            task_id=task_id,
            strategy=strategy,
            expires_at=datetime.now(UTC) + timedelta(hours=engine.DELEGATION_TIMEOUT_HOURS),
        )
        if delegate_id is not None and delegate_id == event.owner_id:
            record.to_delegate = ""
        return record
    return None
