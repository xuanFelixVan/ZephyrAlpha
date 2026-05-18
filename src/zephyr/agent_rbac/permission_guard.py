# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.permission_guard

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
Permission Guard — 七层+六横切面统一编排核心API

MOD-INF-018 §2.14  D-018-all

单次check() < 1.8ms总预算(含全链检查).
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from zephyr.shared.contracts.identity.agent_identity import AgentIdentity
from zephyr.shared.contracts.identity.permission import GuardDecision, GuardResult
from zephyr.agent_rbac.immutable_core import ImmutableCore, get_immutable_core
from zephyr.agent_rbac.kill_switch import KillSwitch, get_kill_switch, TriggerEvent
from zephyr.agent_rbac.engine_degradation import EngineDegradationManager, DegradationLevel
from zephyr.agent_rbac.rbac_guard import RBACGuard, PermissionDecision, PermissionResult
from zephyr.agent_rbac.abac_guard import ABACGuard, ABACContext, TemporalCategory
from zephyr.agent_rbac.input_guard import InputGuard, InputDecision
from zephyr.agent_rbac.sequence_guard import SequenceGuard, SequenceEvent
from zephyr.agent_rbac.output_guard import OutputGuard
from zephyr.agent_rbac.decision_explainer import DecisionExplainer
from zephyr.agent_rbac.exceptions import PermissionDeniedError, ColdStartLockedError


L0_BUDGET_NS = 100_000
L1_BUDGET_NS = 300_000
L2_BUDGET_NS = 2_000_000
L3_BUDGET_NS = 3_000_000
L4_BUDGET_NS = 5_000_000
L5_BUDGET_NS = 1_000_000
L6_BUDGET_NS = 2_000_000
L7_BUDGET_NS = 3_000_000
TOTAL_BUDGET_NS = 18_000_000


class PermissionGuard:
    def __init__(self) -> None:
        self._l0 = get_immutable_core()
        self._ks = get_kill_switch()
        self._degradation = None
        self._l1 = RBACGuard(immutable_core=self._l0)
        self._l2 = ABACGuard()
        self._l3 = InputGuard(immutable_core=self._l0)
        self._l4 = SequenceGuard()
        self._l5 = OutputGuard()
        self._explainer = DecisionExplainer()
        self._dry_run = None

    def check(
        self,
        agent: AgentIdentity,
        operation: str,
        target_path: str = "",
        params: Optional[dict] = None,
    ) -> GuardResult:
        t0 = time.perf_counter_ns()

        if self._l0.should_cold_start_lock():
            raise ColdStartLockedError()

        if self._degradation and self._degradation.is_blocked:
            raise PermissionDeniedError(
                message="Engine degraded — all operations blocked",
                layer="L0",
                rule_id="DEG-001",
            )

        if self._ks.is_agent_blocked(agent.session_id):
            raise PermissionDeniedError(
                message="Agent blocked by kill switch",
                operation=operation,
                layer="L0",
                rule_id="KSW-001",
            )

        result = self._l1.check(agent, operation, target_path)
        if result.decision == PermissionDecision.BLOCKED:
            t1 = time.perf_counter_ns()
            return GuardResult(
                decision=GuardDecision.BLOCKED,
                layer="L1",
                reason=result.reason,
                rule_id="RBAC-001",
                timing_ns=t1 - t0,
            )

        if params:
            input_result = self._l3.check_params(operation, params)
            if input_result == InputDecision.BLOCKED:
                t1 = time.perf_counter_ns()
                return GuardResult(
                    decision=GuardDecision.BLOCKED,
                    layer="L3",
                    reason="Input params blocked",
                    rule_id="INPUT-001",
                    timing_ns=t1 - t0,
                )

        seq_event = SequenceEvent(session_id=agent.session_id, operation=operation, target=target_path)
        seq_result = self._l4.record(seq_event)
        if seq_result:
            self._ks.record_event(TriggerEvent(
                trigger="suspicious_sequence",
                agent_id=agent.session_id,
                context={"sequence": seq_result},
            ))
            t1 = time.perf_counter_ns()
            return GuardResult(
                decision=GuardDecision.BLOCKED,
                layer="L4",
                reason=seq_result,
                rule_id="SEQ-001",
                timing_ns=t1 - t0,
            )

        if result.decision == PermissionDecision.AUTO_GUARD:
            t1 = time.perf_counter_ns()
            return GuardResult(
                decision=GuardDecision.AUTO_GUARD,
                layer="L1",
                reason=result.reason,
                rule_id="AG-001",
                audit_context=result.audit_context,
                timing_ns=t1 - t0,
            )

        t1 = time.perf_counter_ns()
        return GuardResult(
            decision=GuardDecision.ALLOW,
            layer="L1",
            reason="Allowed",
            timing_ns=t1 - t0,
        )

    def is_blocked(self, result: GuardResult) -> bool:
        return result.decision == GuardDecision.BLOCKED

    def explain(self, result: GuardResult) -> dict:
        exp = self._explainer.structured_rejection(
            blocked_layer=result.layer,
            rule_id=result.rule_id,
            reason=result.reason,
        )
        return exp.to_dict()
