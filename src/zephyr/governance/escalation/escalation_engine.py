# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.escalation.escalation_engine
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__; zephyr.security.llm_defense.llm_security.gateway
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
# [A_module] module_id=MOD-RES_escalation_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Escalation Engine — MOD-INF-022

Core escalation engine: rule matching, level determination, auto-escalation with circuit breaker
and economic guard integration.
Blueprint: docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md §2
"""

from __future__ import annotations

import importlib
import logging
import threading
from datetime import UTC, datetime, timedelta
from typing import Any
from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界

logger = logging.getLogger(__name__)

from zephyr.governance.escalation.escalation_metrics import EscalationMetrics
from zephyr.governance.escalation.escalation_models import (
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
from zephyr.governance.resilience_governance.circuit_breaker import CircuitBreaker, CircuitState


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
        self._metrics = EscalationMetrics()
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
        start_time = __import__("time").monotonic()
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
            self._metrics.record("blocked", __import__("time").monotonic() - start_time)
            return event
        try:
            ab = self._extension_detectors.get("AntiAutomationBias")
            if ab and hasattr(ab, "evaluate"):
                result = ab.evaluate(
                    event.event_id,
                    is_autonomous=(event.level is EscalationLevel.L0_SELF_HEAL),
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
            self._metrics.record("blocked", __import__("time").monotonic() - start_time)
            return event
        matching_rule = self._find_best_rule(category)
        if matching_rule is None:
            event.state = EscalationState.REJECTED
            self._metrics.record("blocked", __import__("time").monotonic() - start_time)
            return event
        if not self._check_cooldown(matching_rule):
            event.state = EscalationState.REJECTED
            self._metrics.record("blocked", __import__("time").monotonic() - start_time)
            return event
        event.level = matching_rule.target_level
        event.state = EscalationState.EVALUATING
        with self._lock:
            self._recent_escalations.append(event)
            self._prune_old_escalations()
        latency = __import__("time").monotonic() - start_time
        self._metrics.record(event.level.name.lower(), latency)
        return event

    def escalate(self, event: EscalationEvent) -> EscalationResult:
        if event.state is EscalationState.REJECTED:
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
        if rule.delegate_strategy is not DelegationStrategy.NONE:
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

    def get_metrics(self) -> dict[str, object]:
        return {
            "total_evals": self._metrics._total_evals,
            "blocks": self._metrics._blocks,
            "auto_guards": self._metrics._auto_guards,
            "autonomous": self._metrics._autonomous,
            "escalation_rate": self._metrics.escalation_rate(),
            "avg_latency": self._metrics.avg_latency(),
            "false_positive_rate": self._metrics.false_positive_rate(),
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
            candidates = [r for r in self._rules.values() if r.category is RuleCategory.CUSTOM and r.enabled]
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
            ("zephyr.governance.security_governance.persuasion_detector", "PersuasionDetector"),
            ("zephyr.governance.resilience_governance.deadlock_detector", "DeadlockDetector"),
            ("zephyr.governance.drift_detection.drift_detector", "DriftDetector"),
            ("zephyr.governance.escalation.escalation_loop_detector", "EscalationLoopDetector"),
            ("zephyr.governance.resilience_governance.engine_sandbox", "EngineSandbox"),
            ("zephyr.governance.intelligence_governance.confidence_estimator", "ConfidenceEstimator"),
            ("zephyr.governance.drift_detection.vigil_runtime", "VigilRuntime"),
            ("zephyr.governance.architecture_governance.formal_verifier", "FormalVerifier"),
            ("zephyr.governance.intelligence_governance.provider_failover", "ProviderFailover"),
            ("zephyr.governance.security_governance.credential_guard", "CredentialGuard"),
            ("zephyr.governance.audit_trail.merkle_audit", "MerkleAudit"),
            ("zephyr.governance.security_governance.sbom_guard", "SBOMGuard"),
            ("zephyr.governance.ops_governance.clock_guard", "ClockGuard"),
            ("zephyr.governance.context_governance.command_chain_length_gate", "CommandChainGate"),
            ("zephyr.governance.security_governance.compositional_safety_tester", "CompositionalSafetyTester"),
            ("zephyr.governance.security_governance.anti_automation_bias", "AntiAutomationBias"),
            ("zephyr.governance.rule_enforcement.slo_contract", "SLOContractEngine"),
            ("zephyr.governance.drift_detection.reward_hacking_rebound_detector", "ReboundDetector"),
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
            if dd and event.category is RuleCategory.DEADLOCK:
                cycle = dd.detect_cycle()
                if cycle:
                    event.description += f" | deadlock_cycle={','.join(cycle)}"
                    if event.level.value < EscalationLevel.L3_CRITICAL.value:
                        event.level = EscalationLevel.L3_CRITICAL
        except Exception:
            pass

        try:
            cg = self._extension_detectors.get("CredentialGuard")
            if cg and event.category is RuleCategory.SECURITY_VIOLATION:
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
            dd = self._extension_detectors.get("DriftDetector")
            if dd and event.category is RuleCategory.DRIFT_DETECTED:
                if hasattr(dd, "is_drifting"):
                    metrics = {
                        "event_rate": float(len(self._recent_escalations)),
                        "category_code": float(event.category.value),
                    }
                    if dd.is_drifting(metrics):
                        event.description += " | behavioral_drift=True"
                        if event.level.value < EscalationLevel.L2_HUMAN_REVIEW.value:
                            event.level = EscalationLevel.L2_HUMAN_REVIEW
        except Exception:
            pass

        try:
            ma = self._extension_detectors.get("MerkleAudit")
            if ma and hasattr(ma, "record"):
                root_hash = ma.record(
                    {"event_id": event.event_id, "category": event.category.name, "level": event.level.name}
                )
                event.description += f" | merkle_root={root_hash[:12]}"
        except Exception:
            pass

        try:
            ab = self._extension_detectors.get("AntiAutomationBias")
            if ab and hasattr(ab, "evaluate"):
                result = ab.evaluate(
                    event.event_id,
                    is_autonomous=(event.level is EscalationLevel.L0_SELF_HEAL),
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
                if event.category is RuleCategory.SECURITY_VIOLATION:
                    rd.record(
                        owner, "violation", severity="high", description=event.description, event_id=event.event_id
                    )
                elif event.category is RuleCategory.REWARD_HACKING_REBOUND:
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

            from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway

            gateway = LSGSecurityGateway()
            result = run_sync(gateway.scan_input(description))
            if result.decision.value not in ("allow", "ALLOW"):
                raise ValueError(f"LSG blocked escalation input: {result.decision.value}")
        except ImportError:
            pass
