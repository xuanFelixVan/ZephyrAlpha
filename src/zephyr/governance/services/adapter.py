# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.services.adapter
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__; zephyr.shared.event_bus
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
# [A_module] module_id=MOD-RES_adapter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Escalation Adapter — MOD-INF-022 统一集成入口.

Provides a single import point for any module to integrate with the escalation protocol.
Handles: level determination, circuit breaker, economic guard, delegation, audit.

Blueprint: docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md §2

Usage:
    from zephyr.governance.services.adapter import escalate_if_needed, check_operation

    result = escalate_if_needed(
        operation_type="security_violation",
        description="rm -rf /critical/path",
        owner_id="session-20260508-013",
    )
    if result.should_block:
        raise EscalationBlocked(result.reason)
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

_logger = logging.getLogger(__name__)


class OperationType(str, Enum):
    SECURITY_VIOLATION = "security_violation"
    DEADLOCK = "deadlock"
    BUDGET_EXCEEDED = "budget_exceeded"
    TIMEOUT = "timeout"
    AUTO_GUARD_FAILURE = "auto_guard_failure"
    DRIFT_DETECTED = "drift_detected"
    QUALITY_DEGRADATION = "quality_degradation"
    OWNER_ABSENT = "owner_absent"
    CASCADE_FAILURE = "cascade_failure"
    CUSTOM = "custom"


@dataclass
class EscalationDecision:
    operation: str
    should_block: bool = False
    should_escalate: bool = False
    should_delegate: bool = False
    escalation_level: str = "L0_SELF_HEAL"
    reason: str = ""
    suggested_delegate: str = ""
    economic_status: dict[str, Any] = field(default_factory=dict)
    circuit_state: str = "CLOSED"


_OPERATION_TO_CATEGORY = {
    OperationType.SECURITY_VIOLATION: "SECURITY_VIOLATION",
    OperationType.DEADLOCK: "DEADLOCK",
    OperationType.BUDGET_EXCEEDED: "BUDGET_EXCEEDED",
    OperationType.TIMEOUT: "TIMEOUT",
    OperationType.AUTO_GUARD_FAILURE: "AUTO_GUARD_FAILURE",
    OperationType.DRIFT_DETECTED: "DRIFT_DETECTED",
    OperationType.QUALITY_DEGRADATION: "QUALITY_DEGRADATION",
    OperationType.OWNER_ABSENT: "OWNER_ABSENT",
    OperationType.CASCADE_FAILURE: "CASCADE_FAILURE",
    OperationType.CUSTOM: "CUSTOM",
}

BLOCK_LEVELS = {"L3_CRITICAL", "L4_EMERGENCY"}
DELEGATE_LEVELS = {"L2_HUMAN_REVIEW", "L3_CRITICAL", "L4_EMERGENCY"}

_engine_cache: dict[str, Any] = {}
_cache_lock: threading.Lock | None = None


def _get_engine(name: str = "adapter") -> Any:
    global _cache_lock
    if name in _engine_cache:
        return _engine_cache[name]

    try:
        from threading import Lock

        from zephyr.governance.escalation.escalation_engine import EscalationEngine

        if _cache_lock is None:
            _cache_lock = Lock()
        with _cache_lock:
            if name not in _engine_cache:
                _engine_cache[name] = EscalationEngine(name)
        return _engine_cache[name]
    except ImportError:
        return None


def escalate_if_needed(
    operation_type: str,
    description: str,
    owner_id: str = "",
    source_event_id: str = "",
) -> EscalationDecision:
    engine = _get_engine()
    if engine is None:
        return EscalationDecision(
            operation=operation_type,
            should_block=False,
            reason="Escalation engine not available — pass-through",
        )

    try:
        from zephyr.governance.escalation.escalation_models import RuleCategory

        cat_name = _OPERATION_TO_CATEGORY.get(OperationType(operation_type), "CUSTOM")
        category = getattr(RuleCategory, cat_name, RuleCategory.CUSTOM)

        ev = engine.evaluate(category, description, owner_id, source_event_id)
        level_name = ev.level.name
        should_block = level_name in BLOCK_LEVELS
        should_escalate = ev.level.value > 0 or ev.state.name == "REJECTED"
        should_delegate = level_name in DELEGATE_LEVELS

        economic = engine.get_economic_status()
        circuit = engine.get_circuit_state().name

        reason = f"Level={level_name}"
        if ev.circuit_breaker_triggered:
            reason += " | circuit_breaker=TRIGGERED"
        if not ev.economic_guard_passed:
            reason += " | economic_guard=FAILED"

        return EscalationDecision(
            operation=operation_type,
            should_block=should_block,
            should_escalate=should_escalate,
            should_delegate=should_delegate,
            escalation_level=level_name,
            reason=reason,
            economic_status=economic,
            circuit_state=circuit,
        )

    except Exception as exc:
        _logger.warning("escalation check failed: %s", exc)
        return EscalationDecision(
            operation=operation_type,
            should_block=False,
            reason=f"Escalation check error: {exc} — pass-through",
        )


def check_operation(
    operation: str,
    target_path: str = "",
    session_id: str = "",
) -> EscalationDecision:
    op_type = OperationType.CUSTOM
    dangerous_patterns = [
        ("rm -rf", OperationType.SECURITY_VIOLATION),
        ("DROP", OperationType.SECURITY_VIOLATION),
        ("force_push", OperationType.SECURITY_VIOLATION),
        ("delete_from", OperationType.SECURITY_VIOLATION),
        ("shutdown", OperationType.SECURITY_VIOLATION),
        ("deadlock", OperationType.DEADLOCK),
        ("circular", OperationType.DEADLOCK),
        ("budget:", OperationType.BUDGET_EXCEEDED),
        ("timeout", OperationType.TIMEOUT),
        ("stuck", OperationType.TIMEOUT),
        ("owner absent", OperationType.OWNER_ABSENT),
        ("cascade", OperationType.CASCADE_FAILURE),
    ]
    for pattern, ot in dangerous_patterns:
        if pattern.lower() in operation.lower():
            op_type = ot
            break

    return escalate_if_needed(
        operation_type=op_type.value,
        description=f"{operation} | path={target_path}",
        owner_id=session_id,
    )


_EVENT_TYPE_TO_OPERATION = {
    "GATE_FAILED": OperationType.AUTO_GUARD_FAILURE,
    "SCOPE_DRIFT": OperationType.DRIFT_DETECTED,
    "TASK_FAILED": OperationType.CASCADE_FAILURE,
}

_auto_subscribed = False


def auto_subscribe_eventbus() -> None:
    global _auto_subscribed
    if _auto_subscribed:
        return

    try:
        from zephyr.shared.events.event_bus import EventBus, EventType

        bus = EventBus.get_instance()

        def _on_event(event: object) -> None:
            try:
                etype = getattr(event, "event_type", None)
                if etype is None:
                    return
                op_type = _EVENT_TYPE_TO_OPERATION.get(etype.name if hasattr(etype, "name") else str(etype))
                if op_type is None:
                    return
                task_id = getattr(event, "task_id", "unknown")
                payload = getattr(event, "payload", {})
                description = payload.get("description", f"EventBus auto: {etype}")
                escalate_if_needed(
                    operation_type=op_type.value,
                    description=description,
                    owner_id=task_id,
                )
            except Exception as e:
                _logger.warning("auto_subscribe_eventbus._on_event: event handling failed (%s: %s)", type(e).__name__, e)

        for et in (EventType.GATE_FAILED, EventType.SCOPE_DRIFT, EventType.TASK_FAILED):
            bus.subscribe(et, _on_event)

        _auto_subscribed = True
        _logger.info("EscalationEngine auto-subscribed to EventBus (GATE_FAILED, SCOPE_DRIFT, TASK_FAILED)")
    except ImportError:
        _logger.debug("EventBus not available — escalation auto-subscribe skipped")
    except Exception:
        _logger.debug("EventBus auto-subscribe failed — escalation remains manual")
