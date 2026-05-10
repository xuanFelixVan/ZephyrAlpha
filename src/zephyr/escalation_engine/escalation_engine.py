"""
Escalation Engine — MOD-INF-022

Core escalation engine: rule matching, level determination, auto-escalation with circuit breaker
and economic guard integration.
Blueprint: docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md §2
"""

from __future__ import annotations

import importlib
import logging
import threading
from datetime import UTC, datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

from zephyr.escalation_engine.circuit_breaker import CircuitBreaker, CircuitState
from zephyr.escalation_engine.escalation_models import (
    DEFAULT_ESCALATION_RULES,
    DelegationStrategy,
    EconomicGuard,
    EscalationEvent,
    EscalationLevel,
    EscalationResult,
    EscalationRule,
    EscalationState,
    RuleCategory,
)


class EscalationEngine:
    MAX_ESCALATIONS_PER_HOUR = 100

    CATEGORY_COST: dict[RuleCategory, float] = {
        RuleCategory.AUTO_GUARD_FAILURE: 1.0,
        RuleCategory.BUDGET_EXCEEDED: 3.0,
        RuleCategory.DRIFT_DETECTED: 2.0,
        RuleCategory.DEADLOCK: 5.0,
        RuleCategory.TIMEOUT: 1.0,
        RuleCategory.QUALITY_DEGRADATION: 1.0,
        RuleCategory.SECURITY_VIOLATION: 10.0,
        RuleCategory.OWNER_ABSENT: 2.0,
        RuleCategory.CASCADE_FAILURE: 8.0,
        RuleCategory.REWARD_HACKING_REBOUND: 10.0,
        RuleCategory.CUSTOM: 0.5,
    }

    def __init__(self, name: str = "default", hooks_enabled: bool = True):
        self.name = name
        self._rules: dict[str, EscalationRule] = {}
        self._circuit_breaker = CircuitBreaker(f"escalation:{name}")
        self._economic_guard = EconomicGuard(f"econ:{name}")
        self._recent_escalations: list[EscalationEvent] = []
        self._lock = threading.Lock()
        self._hooks_enabled = hooks_enabled
        self._extension_detectors: dict[str, Any] = {}
        self._register_default_rules()
        if self._hooks_enabled:
            self._load_extension_detectors()

    def _register_default_rules(self) -> None:
        for rule in DEFAULT_ESCALATION_RULES:
            self.register_rule(rule)

    def register_rule(self, rule: EscalationRule) -> None:
        with self._lock:
            self._rules[rule.rule_id] = rule

    def remove_rule(self, rule_id: str) -> None:
        with self._lock:
            self._rules.pop(rule_id, None)

    def evaluate(
        self,
        category: RuleCategory,
        description: str = "",
        owner_id: str | None = None,
        source_event_id: str | None = None,
    ) -> EscalationEvent:
        self._lsg_scan_input(description)
        event = EscalationEvent(
            category=category,
            description=description,
            owner_id=owner_id,
            source_event_id=source_event_id,
        )
        event = self._run_extension_hooks(event)
        if not self._circuit_breaker.call():
            event.circuit_breaker_triggered = True
            event.state = EscalationState.REJECTED
        try:
            ab = self._extension_detectors.get("AntiAutomationBias")
            if ab and hasattr(ab, "evaluate"):
                result = ab.evaluate(
                    event.event_id,
                    is_autonomous=(event.level == EscalationLevel.L0_SELF_HEAL),
                    actor_identity=getattr(event, "actor", ""),
                    operation_content=event.description,
                )
                if result.forced_review:
                    event.description += " | forced_review=True"
        except Exception:
            pass

        try:
            slo = self._extension_detectors.get("SLOContractEngine")
            if slo and hasattr(slo, "get_recommended_scaling"):
                scaling = slo.get_recommended_scaling()
                event.description += f" | slo_tier={scaling['current_tier']}"
                if scaling["escalation_level_offset"] > 0:
                    new_level = min(
                        EscalationLevel.L4_EMERGENCY.value, event.level.value + scaling["escalation_level_offset"]
                    )
                    event.level = EscalationLevel(new_level)
        except Exception:
            pass

        if not self._economic_guard.can_proceed():
            event.economic_guard_passed = False
            event.state = EscalationState.REJECTED
            return event
        matching_rule = self._find_best_rule(category)
        if matching_rule is None:
            event.state = EscalationState.REJECTED
            return event
        if not self._check_cooldown(matching_rule):
            event.state = EscalationState.REJECTED
            return event
        event.level = matching_rule.target_level
        event.state = EscalationState.EVALUATING
        with self._lock:
            self._recent_escalations.append(event)
            self._prune_old_escalations()
        return event

    def escalate(self, event: EscalationEvent) -> EscalationResult:
        if event.state == EscalationState.REJECTED:
            return EscalationResult(event=event, escalated=False, new_level=event.level, message="Rejected by gate")
        rule = self._find_best_rule(event.category)
        if rule is None:
            return EscalationResult(event=event, escalated=False, new_level=event.level, message="No matching rule")
        escalated = rule.auto_escalate
        new_level = event.level
        if escalated and event.retry_count < event.max_retries:
            if event.level.value < EscalationLevel.L4_EMERGENCY.value:
                new_level = EscalationLevel(min(event.level.value + 1, EscalationLevel.L4_EMERGENCY.value))
        event.level = new_level
        event.state = EscalationState.ESCALATED if escalated else event.state
        event.updated_at = datetime.now(UTC)
        cost = self.CATEGORY_COST.get(event.category, 1.0)
        self._economic_guard.consume(cost)
        self._circuit_breaker.record_success()
        delegated_to: str | None = None
        if rule.delegate_strategy != DelegationStrategy.NONE:
            result_msg = f"Escalated to {new_level.name} — delegation needed"
            delegated_to = rule.delegate_strategy.name
            event.delegate_id = delegated_to
            event.state = EscalationState.DELEGATED
        else:
            result_msg = f"Escalated to {new_level.name}"
        return EscalationResult(
            event=event,
            escalated=escalated,
            new_level=new_level,
            delegated_to=delegated_to,
            circuit_broken=False,
            message=result_msg,
            suggestion=self._generate_suggestion(event, rule),
        )

    def record_resolution(self, event: EscalationEvent) -> None:
        event.state = EscalationState.RESOLVED
        event.resolved_at = datetime.now(UTC)
        event.updated_at = datetime.now(UTC)
        self._circuit_breaker.record_success()

    def record_failure(self, event: EscalationEvent) -> None:
        event.retry_count += 1
        self._circuit_breaker.record_failure()

    def get_circuit_state(self) -> CircuitState:
        return self._circuit_breaker.state

    def get_economic_status(self) -> dict[str, object]:
        return {
            "daily_budget": self._economic_guard.daily_budget,
            "consumed_today": self._economic_guard.consumed_today,
            "hard_limit_reached": self._economic_guard.hard_limit_reached,
        }

    def get_active_count(self) -> int:
        with self._lock:
            self._prune_old_escalations()
            active = [
                e
                for e in self._recent_escalations
                if e.state
                in (
                    EscalationState.DETECTED,
                    EscalationState.EVALUATING,
                    EscalationState.ESCALATED,
                    EscalationState.DELEGATED,
                )
            ]
            return len(active)

    def _find_best_rule(self, category: RuleCategory) -> EscalationRule | None:
        candidates = [r for r in self._rules.values() if r.category == category and r.enabled]
        if not candidates:
            candidates = [r for r in self._rules.values() if r.category == RuleCategory.CUSTOM and r.enabled]
        if not candidates:
            return None
        candidates.sort(key=lambda r: r.priority, reverse=True)
        return candidates[0]

    def _check_cooldown(self, rule: EscalationRule) -> bool:
        cutoff = datetime.now(UTC) - timedelta(seconds=rule.cooldown_seconds)
        recent_same = [e for e in self._recent_escalations if e.category == rule.category and e.created_at > cutoff]
        return len(recent_same) < rule.max_escalations_per_hour

    def _prune_old_escalations(self) -> None:
        cutoff = datetime.now(UTC) - timedelta(hours=1)
        self._recent_escalations = [e for e in self._recent_escalations if e.created_at > cutoff]

    @staticmethod
    def _generate_suggestion(event: EscalationEvent, rule: EscalationRule) -> str:
        suggestions: dict[EscalationLevel, str] = {
            EscalationLevel.L0_SELF_HEAL: "Self-healing deployed. Monitor for 5 minutes.",
            EscalationLevel.L1_AUTO_FIX: "Auto-fix triggered. Check audit log for fix details.",
            EscalationLevel.L2_HUMAN_REVIEW: "Human review required. See escalation details.",
            EscalationLevel.L3_CRITICAL: "CRITICAL: immediate attention. Deadlock/cascade detected.",
            EscalationLevel.L4_EMERGENCY: "EMERGENCY: security violation or system-wide failure. All hands.",
        }
        return suggestions.get(event.level, "Review escalation event.")

    def _load_extension_detectors(self):
        detector_modules = [
            ("zephyr.infrastructure.escalation_protocol.persuasion_detector", "PersuasionDetector"),
            ("zephyr.infrastructure.escalation_protocol.deadlock_detector", "DeadlockDetector"),
            ("zephyr.infrastructure.escalation_protocol.drift_detector", "DriftDetector"),
            ("zephyr.infrastructure.escalation_protocol.escalation_loop_detector", "EscalationLoopDetector"),
            ("zephyr.infrastructure.escalation_protocol.engine_sandbox", "EngineSandbox"),
            ("zephyr.infrastructure.escalation_protocol.confidence_estimator", "ConfidenceEstimator"),
            ("zephyr.infrastructure.escalation_protocol.vigil_runtime", "VigilRuntime"),
            ("zephyr.infrastructure.escalation_protocol.formal_verifier", "FormalVerifier"),
            ("zephyr.infrastructure.escalation_protocol.provider_failover", "ProviderFailover"),
            ("zephyr.infrastructure.escalation_protocol.credential_guard", "CredentialGuard"),
            ("zephyr.infrastructure.escalation_protocol.merkle_audit", "MerkleAudit"),
            ("zephyr.infrastructure.escalation_protocol.sbom_guard", "SBOMGuard"),
            ("zephyr.infrastructure.escalation_protocol.clock_guard", "ClockGuard"),
            ("zephyr.infrastructure.escalation_protocol.command_chain_length_gate", "CommandChainGate"),
            ("zephyr.infrastructure.escalation_protocol.compositional_safety_tester", "CompositionalSafetyTester"),
            ("zephyr.escalation_engine.anti_automation_bias", "AntiAutomationBias"),
            ("zephyr.escalation_engine.slo_contract", "SLOContractEngine"),
            ("zephyr.infrastructure.escalation_protocol.reward_hacking_rebound_detector", "ReboundDetector"),
        ]
        for module_path, class_name in detector_modules:
            try:
                mod = importlib.import_module(module_path)
                cls = getattr(mod, class_name, None)
                if cls:
                    self._extension_detectors[class_name] = cls()
            except ImportError:
                pass

    def _run_extension_hooks(self, event: EscalationEvent) -> EscalationEvent:
        if not self._hooks_enabled or not self._extension_detectors:
            return event

        try:
            loop_d = self._extension_detectors.get("EscalationLoopDetector")
            if loop_d:
                loop_d.record_transition(event.event_id, "incoming", event.level.name)
                if loop_d.detect_loop():
                    event.description += " | loop_detected=True"
                    if event.level.value < EscalationLevel.L2_HUMAN_REVIEW.value:
                        event.level = EscalationLevel.L2_HUMAN_REVIEW
        except Exception:
            pass

        try:
            pd = self._extension_detectors.get("PersuasionDetector")
            if pd and event.category in (RuleCategory.SECURITY_VIOLATION, RuleCategory.DEADLOCK):
                flagged, _ = pd.detect(event.description)
                if flagged:
                    event.description += " | persuasion_flagged=True"
        except Exception:
            pass

        try:
            dd = self._extension_detectors.get("DeadlockDetector")
            if dd and event.category == RuleCategory.DEADLOCK:
                cycle = dd.detect_cycle()
                if cycle:
                    event.description += f" | deadlock_cycle={','.join(cycle)}"
                    if event.level.value < EscalationLevel.L3_CRITICAL.value:
                        event.level = EscalationLevel.L3_CRITICAL
        except Exception:
            pass

        try:
            cg = self._extension_detectors.get("CredentialGuard")
            if cg and event.category == RuleCategory.SECURITY_VIOLATION:
                if hasattr(cg, "scan") and cg.scan(event.description):
                    event.description += " | credential_leak_detected=True"
        except Exception:
            pass

        try:
            cg2 = self._extension_detectors.get("ClockGuard")
            if cg2 and hasattr(cg2, "verify"):
                if not cg2.verify():
                    event.description += " | clock_integrity_failed=True"
        except Exception:
            pass

        try:
            cc = self._extension_detectors.get("CommandChainGate")
            if cc and hasattr(cc, "check"):
                ok, limit = cc.check(event.description)
                if not ok:
                    event.description += f" | command_chain_exceeded={limit}"
        except Exception:
            pass

        try:
            ce = self._extension_detectors.get("ConfidenceEstimator")
            if ce and hasattr(ce, "estimate"):
                conf = ce.estimate(event.description)
                event.description += f" | meta_confidence={conf:.2f}"
        except Exception:
            pass

        try:
            ma = self._extension_detectors.get("MerkleAudit")
            if ma and hasattr(ma, "hash_event"):
                audit_hash = ma.hash_event(event.description)
                event.description += f" | audit_hash={audit_hash[:12]}"
        except Exception:
            pass

        try:
            ab = self._extension_detectors.get("AntiAutomationBias")
            if ab and hasattr(ab, "evaluate"):
                result = ab.evaluate(
                    event.event_id,
                    is_autonomous=(event.level == EscalationLevel.L0_SELF_HEAL),
                    actor_identity=getattr(event, "actor", ""),
                    operation_content=event.description,
                )
                if result.forced_review:
                    event.description += " | forced_review=True"
        except Exception:
            pass

        try:
            slo = self._extension_detectors.get("SLOContractEngine")
            if slo and hasattr(slo, "get_recommended_scaling"):
                scaling = slo.get_recommended_scaling()
                event.description += f" | slo_tier={scaling['current_tier']}"
                if scaling["escalation_level_offset"] > 0:
                    new_level = min(
                        EscalationLevel.L4_EMERGENCY.value, event.level.value + scaling["escalation_level_offset"]
                    )
                    event.level = EscalationLevel(new_level)
        except Exception:
            pass

        try:
            rd = self._extension_detectors.get("ReboundDetector")
            if rd and event.category in (RuleCategory.SECURITY_VIOLATION, RuleCategory.REWARD_HACKING_REBOUND):
                owner = event.owner_id or "unknown"
                if event.category == RuleCategory.SECURITY_VIOLATION:
                    rd.record(
                        owner, "violation", severity="high", description=event.description, event_id=event.event_id
                    )
                elif event.category == RuleCategory.REWARD_HACKING_REBOUND:
                    rd.record(
                        owner, "rebound", severity="critical", description=event.description, event_id=event.event_id
                    )
                if rd.detect_rebound(owner):
                    event.description += " | reward_hacking_rebound=True"
                    event.level = EscalationLevel.L4_EMERGENCY
                    rd.mark_rebound_agent(owner)
        except Exception:
            pass

        return event

    def enable_hooks(self):
        self._hooks_enabled = True
        if not self._extension_detectors:
            self._load_extension_detectors()

    def disable_hooks(self):
        self._hooks_enabled = False

    def _lsg_scan_input(self, description: str) -> None:
        if not description:
            return
        try:
            import asyncio

            from zephyr.llm_security.gateway import LSGSecurityGateway

            gateway = LSGSecurityGateway()
            result = asyncio.run(gateway.scan_input(description))
            if result.decision.value not in ("allow", "ALLOW"):
                raise ValueError(f"LSG blocked escalation input: {result.decision.value}")
        except ImportError:
            pass
