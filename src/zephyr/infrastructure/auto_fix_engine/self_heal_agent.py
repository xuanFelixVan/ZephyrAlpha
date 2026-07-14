# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.self_heal_agent
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] OODA最大5轮;熔断器3次连续失败触发;不自动修复行为审计RED
# [MODIFY-GUARD] blueprint.md §3;_fixer-registry.yaml self_heal_agent段
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SelfHealMaxRoundsError;SelfHealCircuitOpenError
# [TESTS] tests/auto-fix-engine/test_self_heal_agent.py
# [A_module] module_id=MOD-INF_self_heal_agent | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from zephyr.infrastructure.auto_fix_engine.models import (
    FixAction,
    FixConfidence,
    FixLevel,
    FixStatus,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class SelfHealAgent:
    def __init__(self, max_rounds: int = 5, circuit_threshold: int = 3) -> None:
        self._max_rounds = max_rounds
        self._circuit_threshold = circuit_threshold
        self._consecutive_failures: int = 0
        self._circuit_open: bool = False
        self._round_history: list[dict[str, Any]] = []

    @property
    def circuit_open(self) -> bool:
        return self._circuit_open

    def heal(self, target: str, diagnose_fn: Callable[..., object], fix_fn: Callable[..., object], validate_fn: Callable[..., object]) -> FixAction:
        if self._circuit_open:
            return FixAction(
                action_type="self_heal",
                level=FixLevel.L3_AGENT,
                target=target,
                status=FixStatus.FAILED,
                confidence=FixConfidence.LOW,
                metadata={"error": "Circuit breaker open"},
            )
        action = FixAction(
            action_type="self_heal",
            level=FixLevel.L3_AGENT,
            target=target,
            confidence=FixConfidence.LOW,
        )
        for round_num in range(1, self._max_rounds + 1):
            round_record: dict[str, Any] = {"round": round_num, "phase": "observe"}
            observation = self._observe(target, diagnose_fn)
            round_record["observation"] = observation
            if not observation.get("issues"):
                action.status = FixStatus.COMPLETED
                action.metadata["rounds"] = round_num
                action.confidence = FixConfidence.HIGH
                self._consecutive_failures = 0
                self._round_history.append(round_record)
                return action
            round_record["phase"] = "orient"
            decision = self._orient(observation)
            round_record["decision"] = decision
            round_record["phase"] = "decide"
            fix_plan = self._decide(decision)
            round_record["fix_plan"] = fix_plan
            round_record["phase"] = "act"
            fix_result = self._act(target, fix_plan, fix_fn)
            round_record["fix_result"] = {"status": fix_result.status.value}
            validation = self._validate(target, validate_fn)
            round_record["validation"] = {"valid": validation.valid}
            self._round_history.append(round_record)
            if validation.valid:
                action.status = FixStatus.COMPLETED
                action.metadata["rounds"] = round_num
                action.confidence = FixConfidence.MEDIUM
                self._consecutive_failures = 0
                return action
            self._consecutive_failures += 1
            if self._consecutive_failures >= self._circuit_threshold:
                self._circuit_open = True
                action.status = FixStatus.FAILED
                action.metadata["error"] = (
                    f"Circuit breaker opened after {self._consecutive_failures} consecutive failures"
                )
                action.escalated = True
                return action
        action.status = FixStatus.FAILED
        action.metadata["error"] = f"Max rounds ({self._max_rounds}) exceeded"
        action.metadata["round_history"] = [{"round": r["round"], "phase": r["phase"]} for r in self._round_history]
        return action

    def _observe(self, target: str, diagnose_fn: Callable[..., object]) -> dict[str, Any]:
        try:
            result = diagnose_fn(target)
            if isinstance(result, dict):
                return result
            if isinstance(result, list):
                return {"issues": result}
            return {"issues": [], "raw": str(result)}
        except Exception as exc:
            return {"issues": [], "error": str(exc)}

    def _orient(self, observation: dict[str, Any]) -> dict[str, Any]:
        issues = observation.get("issues", [])
        if not issues:
            return {"action": "none", "reason": "No issues observed"}
        severity = "low"
        for issue in issues:
            if isinstance(issue, dict):
                issue_type = issue.get("type", "")
                if "security" in issue_type or "critical" in issue_type:
                    severity = "high"
                elif "drift" in issue_type or "config" in issue_type:
                    severity = "medium"
        return {"action": "fix", "severity": severity, "issue_count": len(issues)}

    def _decide(self, decision: dict[str, Any]) -> dict[str, Any]:
        if decision.get("action") == "none":
            return {"plan": "skip", "reason": decision.get("reason", "")}
        severity = decision.get("severity", "low")
        if severity == "high":
            return {"plan": "escalate", "reason": "High severity issue requires human review"}
        return {"plan": "auto_fix", "severity": severity}

    def _act(self, target: str, fix_plan: dict[str, Any], fix_fn: Callable[..., object]) -> FixAction:
        if fix_plan.get("plan") == "skip":
            return FixAction(action_type="self_heal", target=target, status=FixStatus.COMPLETED)
        if fix_plan.get("plan") == "escalate":
            return FixAction(action_type="self_heal", target=target, status=FixStatus.APPROVAL_PENDING, escalated=True)
        try:
            result = fix_fn(target)
            if isinstance(result, FixAction):
                return result
            return FixAction(action_type="self_heal", target=target, status=FixStatus.COMPLETED)
        except Exception as exc:
            return FixAction(
                action_type="self_heal", target=target, status=FixStatus.FAILED, metadata={"error": str(exc)}
            )

    def _validate(self, target: str, validate_fn: Callable[..., object]) -> ValidationResult:
        try:
            result = validate_fn(target)
            if isinstance(result, ValidationResult):
                return result
            return ValidationResult(valid=bool(result), check_name="self_heal_validation", evidence=str(result))
        except Exception as exc:
            return ValidationResult(valid=False, check_name="self_heal_validation", evidence="", error=str(exc))

    def reset_circuit(self) -> None:
        self._circuit_open = False
        self._consecutive_failures = 0
