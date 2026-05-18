"""
Budget Enforcer core engine — MOD-INF-024

Pre-flight gate, model router, degradation manager, and budget consumption tracking.
3D budget system: Token/Cost/Time with seven-level escalation.
Blueprint: docs/03_modules/l01_infrastructure/budget-enforcer/blueprint.md §2-4
"""
from __future__ import annotations

import hashlib
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional, Callable

from .budget_models import (
    BudgetAlert,
    BudgetConsumption,
    BudgetDimension,
    BudgetLevel,
    BudgetPolicy,
    DegradationStep,
    GateDecision,
    GateResult,
    ModelTier,
)


DEFAULT_DEGRADATION_STEPS: list[DegradationStep] = [
    DegradationStep(0, "Normal operation — Premium models available", ModelTier.PREMIUM, BudgetLevel.L0_NORMAL, 32_000, 0),
    DegradationStep(1, "Warning — Standard models only", ModelTier.STANDARD, BudgetLevel.L1_WARNING, 16_000, 120),
    DegradationStep(2, "Throttled — Economy models, reduced context", ModelTier.ECONOMY, BudgetLevel.L2_THROTTLED, 8_000, 300),
    DegradationStep(3, "Degraded — Minimal models, essential only", ModelTier.MINIMAL, BudgetLevel.L3_DEGRADED, 4_000, 600),
    DegradationStep(4, "Emergency — Read-only, no code generation", ModelTier.MINIMAL, BudgetLevel.L4_EMERGENCY, 2_000, 900),
]


class BudgetEngine:
    DEFAULT_POLICIES = {
        BudgetDimension.TOKEN: BudgetPolicy(
            policy_id="BP-TOKEN-001",
            name="Token Budget (Agent)",
            dimension=BudgetDimension.TOKEN,
            daily_limit=1_000_000,
            hourly_limit=100_000,
            per_request_limit=16_000,
        ),
        BudgetDimension.COST: BudgetPolicy(
            policy_id="BP-COST-001",
            name="Cost Budget (Dollar)",
            dimension=BudgetDimension.COST,
            daily_limit=50.0,
            hourly_limit=10.0,
            per_request_limit=1.0,
        ),
        BudgetDimension.TIME: BudgetPolicy(
            policy_id="BP-TIME-001",
            name="Time Budget (Minutes)",
            dimension=BudgetDimension.TIME,
            daily_limit=480.0,
            hourly_limit=60.0,
            per_request_limit=5.0,
        ),
    }

    def __init__(self):
        self._policies: dict[BudgetDimension, BudgetPolicy] = dict(self.DEFAULT_POLICIES)
        self._consumption: dict[str, BudgetConsumption] = {}
        self._alerts: list[BudgetAlert] = []
        self._gate_history: list[GateResult] = []
        self._degradation_steps: list[DegradationStep] = list(DEFAULT_DEGRADATION_STEPS)
        self._current_degradation_level: BudgetLevel = BudgetLevel.L0_NORMAL
        self._active_step_idx: int = 0
        self._lock = threading.Lock()
        self._consumption_version: dict[str, int] = {}
        self._provider_claims: dict[str, dict[str, float]] = {}
        self._on_consumption_recorded: Optional[Callable[[str, int, float, float], None]] = None
        self._init_consumption()

    def _init_consumption(self) -> None:
        for policy in self._policies.values():
            self._consumption[policy.policy_id] = BudgetConsumption(
                policy_id=policy.policy_id,
                dimension=policy.dimension,
            )
            self._consumption_version[policy.policy_id] = 0

    def register_policy(self, policy: BudgetPolicy) -> None:
        with self._lock:
            self._policies[policy.dimension] = policy
            cons = BudgetConsumption(policy_id=policy.policy_id, dimension=policy.dimension)
            self._consumption[policy.policy_id] = cons
            self._consumption_version[policy.policy_id] = 0

    def try_claim_budget(self, provider_id: str, dimension: BudgetDimension, amount: float, expected_version: int | None = None) -> tuple[bool, int, str]:
        with self._lock:
            policy = self._policies.get(dimension)
            if policy is None:
                return False, -1, "No policy defined"

            cons = self._consumption.get(policy.policy_id)
            if cons is None:
                return False, -1, "No consumption tracked"

            current_version = self._consumption_version.get(policy.policy_id, 0)
            if expected_version is not None and current_version != expected_version:
                return False, current_version, f"Version mismatch: expected={expected_version}, current={current_version}"

            provider_claims = self._provider_claims.get(provider_id, {})
            already_claimed = provider_claims.get(policy.policy_id, 0.0)

            remaining_daily = policy.daily_limit - cons.consumed_daily - already_claimed
            remaining_hourly = policy.hourly_limit - cons.consumed_hourly - already_claimed

            if remaining_daily < amount:
                return False, current_version, f"Insufficient daily budget: remaining={remaining_daily:.2f}, requested={amount:.2f}"
            if remaining_hourly < amount:
                return False, current_version, f"Insufficient hourly budget: remaining={remaining_hourly:.2f}, requested={amount:.2f}"

            if provider_id not in self._provider_claims:
                self._provider_claims[provider_id] = {}
            self._provider_claims[provider_id][policy.policy_id] = already_claimed + amount

            new_version = current_version + 1
            self._consumption_version[policy.policy_id] = new_version

            return True, new_version, "OK"

    def commit_claim(self, provider_id: str, dimension: BudgetDimension, actual_amount: float) -> bool:
        with self._lock:
            policy = self._policies.get(dimension)
            if policy is None:
                return False

            cons = self._consumption.get(policy.policy_id)
            if cons is None:
                return False

            provider_claims = self._provider_claims.get(provider_id, {})
            claimed = provider_claims.pop(policy.policy_id, 0.0)

            now = datetime.now(timezone.utc)
            if (now - cons.last_reset_daily).days >= 1:
                cons.consumed_daily = 0.0
                cons.request_count_daily = 0
                cons.last_reset_daily = now
            if (now - cons.last_reset_hourly).total_seconds() >= 3600:
                cons.consumed_hourly = 0.0
                cons.last_reset_hourly = now

            committed = min(actual_amount, claimed) if claimed > 0 else actual_amount

            if cons.dimension == BudgetDimension.TOKEN:
                cons.consumed_daily += committed
                cons.consumed_hourly += committed
                cons.consumed_per_request = committed
            elif cons.dimension == BudgetDimension.COST:
                cons.consumed_daily += committed
                cons.consumed_hourly += committed
                cons.consumed_per_request = committed
            elif cons.dimension == BudgetDimension.TIME:
                cons.consumed_daily += committed
                cons.consumed_hourly += committed
                cons.consumed_per_request = committed

            cons.request_count_daily += 1
            return True

    def rollback_claim(self, provider_id: str, dimension: BudgetDimension) -> bool:
        with self._lock:
            policy = self._policies.get(dimension)
            if policy is None:
                return False

            provider_claims = self._provider_claims.get(provider_id, {})
            provider_claims.pop(policy.policy_id, None)
            return True

    def get_consumption_version(self, dimension: BudgetDimension) -> int:
        with self._lock:
            policy = self._policies.get(dimension)
            if policy is None:
                return -1
            return self._consumption_version.get(policy.policy_id, 0)

    def pre_flight_check(self, request_id: str, estimated_tokens: int = 0, estimated_cost: float = 0.0) -> GateResult:
        with self._lock:
            token_result = self._check_dimension(BudgetDimension.TOKEN, request_id, estimated_tokens, estimated_cost)
            cost_result = self._check_dimension(BudgetDimension.COST, request_id, estimated_tokens, estimated_cost)

            worst = token_result
            if cost_result.decision == GateDecision.DENY:
                worst = cost_result
            elif cost_result.decision == GateDecision.DEGRADE and worst.decision != GateDecision.DENY:
                worst = cost_result

        try:
            from zephyr.behavioral_auditor.drift_infrastructure import check_budget_for_gate
            drift_result = check_budget_for_gate("MOD-INF-024", tier="P1")
            if not drift_result.get("allowed", True):
                with self._lock:
                    if worst.decision != GateDecision.DENY:
                        worst = GateResult(
                            request_id=request_id,
                            decision=GateDecision.NARROW,
                            reason=f"drift budget exhausted: {drift_result.get('reason', 'unknown')}",
                            remaining_daily=worst.remaining_daily,
                            remaining_hourly=worst.remaining_hourly,
                            estimated_tokens=estimated_tokens,
                            estimated_cost=estimated_cost,
                        )
        except ImportError:
            pass
        except Exception:
            pass

        with self._lock:
            worst.budget_level = self._compute_budget_level(worst)
            self._gate_history.append(worst)
            if len(self._gate_history) > 1000:
                self._gate_history = self._gate_history[-500:]
            return worst

    def record_consumption(self, policy_id: str, tokens: int, cost: float, time_minutes: float) -> None:
        with self._lock:
            cons = self._consumption.get(policy_id)
            if cons is None:
                return
            now = datetime.now(timezone.utc)
            if (now - cons.last_reset_daily).days >= 1:
                cons.consumed_daily = 0.0
                cons.request_count_daily = 0
                cons.last_reset_daily = now
            if (now - cons.last_reset_hourly).total_seconds() >= 3600:
                cons.consumed_hourly = 0.0
                cons.last_reset_hourly = now

            if cons.dimension == BudgetDimension.TOKEN:
                cons.consumed_daily += tokens
                cons.consumed_hourly += tokens
                cons.consumed_per_request = tokens
            elif cons.dimension == BudgetDimension.COST:
                cons.consumed_daily += cost
                cons.consumed_hourly += cost
                cons.consumed_per_request = cost
            elif cons.dimension == BudgetDimension.TIME:
                cons.consumed_daily += time_minutes
                cons.consumed_hourly += time_minutes
                cons.consumed_per_request = time_minutes

            cons.request_count_daily += 1

        if self._on_consumption_recorded is not None:
            self._on_consumption_recorded(policy_id, tokens, cost, time_minutes)

        try:
            from zephyr.l01_infrastructure.system_telemetry._budget_telemetry_bridge import get_telemetry
            gt = get_telemetry()
            if gt is not None:
                gt.metrics.gauge(f"budget.{policy_id}.tokens_consumed", float(tokens))
                gt.metrics.gauge(f"budget.{policy_id}.cost_usd", cost)
        except Exception:
            pass

    def get_model_router_recommendation(self) -> tuple[ModelTier, int]:
        step = self._degradation_steps[self._active_step_idx]
        return step.model_tier, step.max_tokens_per_request

    def advance_degradation(self) -> bool:
        with self._lock:
            if self._active_step_idx >= len(self._degradation_steps) - 1:
                return False
            self._active_step_idx += 1
            step = self._degradation_steps[self._active_step_idx]
            self._current_degradation_level = step.auto_trigger_level
            return True

    def retreat_degradation(self) -> bool:
        with self._lock:
            if self._active_step_idx <= 0:
                return False
            self._active_step_idx -= 1
            self._current_degradation_level = self._degradation_steps[self._active_step_idx].auto_trigger_level
            return True

    def get_alerts(self, unacknowledged_only: bool = True) -> list[BudgetAlert]:
        with self._lock:
            if unacknowledged_only:
                return [a for a in self._alerts if not a.acknowledged]
            return list(self._alerts)

    def acknowledge_alert(self, alert_id: str) -> bool:
        with self._lock:
            for a in self._alerts:
                if a.alert_id == alert_id:
                    a.acknowledged = True
                    return True
            return False

    def get_consumption_summary(self) -> dict[str, dict[str, float]]:
        with self._lock:
            return {
                policy_id: {
                    "daily": cons.consumed_daily,
                    "hourly": cons.consumed_hourly,
                }
                for policy_id, cons in self._consumption.items()
            }

    def get_active_policy(self, dimension: BudgetDimension) -> Optional[BudgetPolicy]:
        return self._policies.get(dimension)

    def compute_hash(self) -> str:
        with self._lock:
            canonical = ""
            for dim in sorted(self._policies.keys(), key=lambda d: d.value):
                pol = self._policies[dim]
                cons = self._consumption.get(pol.policy_id)
                canonical += f"{pol.policy_id}:{pol.daily_limit}:{pol.hourly_limit}:"
                if cons:
                    canonical += f"{cons.consumed_daily}:{cons.consumed_hourly}:{cons.request_count_daily}:"
                canonical += f"{self._current_degradation_level.value}:{self._active_step_idx}|"
            return hashlib.sha256(canonical.encode()).hexdigest()

    def _check_dimension(self, dimension: BudgetDimension, request_id: str, estimated_tokens: int, estimated_cost: float) -> GateResult:
        policy = self._policies.get(dimension)
        if policy is None:
            return GateResult(request_id=request_id, decision=GateDecision.ALLOW, reason="No policy defined")

        cons = self._consumption.get(policy.policy_id)
        if cons is None:
            return GateResult(request_id=request_id, decision=GateDecision.ALLOW, reason="No consumption tracked")

        remaining_daily = policy.daily_limit - cons.consumed_daily
        remaining_hourly = policy.hourly_limit - cons.consumed_hourly

        daily_ratio = cons.consumed_daily / policy.daily_limit if policy.daily_limit > 0 else 0.0

        consumption: float = float(estimated_tokens) if dimension == BudgetDimension.TOKEN else (estimated_cost if dimension == BudgetDimension.COST else 0.0)

        if consumption > policy.per_request_limit:
            return GateResult(request_id=request_id, decision=GateDecision.NARROW, reason=f"Per-request limit exceeded: {policy.per_request_limit}", remaining_daily=remaining_daily, remaining_hourly=remaining_hourly, estimated_tokens=estimated_tokens, estimated_cost=estimated_cost)

        if daily_ratio >= policy.hard_stop_threshold:
            return GateResult(request_id=request_id, decision=GateDecision.DENY, reason=f"{dimension.name} hard stop: daily {daily_ratio:.0%}", remaining_daily=remaining_daily, remaining_hourly=remaining_hourly, estimated_tokens=estimated_tokens, estimated_cost=estimated_cost)

        if daily_ratio >= policy.emergency_threshold:
            return GateResult(request_id=request_id, decision=GateDecision.DEGRADE, reason=f"{dimension.name} emergency: daily {daily_ratio:.0%}", remaining_daily=remaining_daily, remaining_hourly=remaining_hourly, estimated_tokens=estimated_tokens, estimated_cost=estimated_cost)

        if daily_ratio >= policy.degrade_threshold:
            return GateResult(request_id=request_id, decision=GateDecision.BORROW, reason=f"{dimension.name} degraded: daily {daily_ratio:.0%}", remaining_daily=remaining_daily, remaining_hourly=remaining_hourly, estimated_tokens=estimated_tokens, estimated_cost=estimated_cost)

        if remaining_hourly <= consumption:
            return GateResult(request_id=request_id, decision=GateDecision.BORROW, reason=f"{dimension.name} hourly exhausted", remaining_daily=remaining_daily, remaining_hourly=remaining_hourly, estimated_tokens=estimated_tokens, estimated_cost=estimated_cost)

        return GateResult(request_id=request_id, decision=GateDecision.ALLOW, reason="OK", remaining_daily=remaining_daily, remaining_hourly=remaining_hourly, estimated_tokens=estimated_tokens, estimated_cost=estimated_cost)

    def _compute_budget_level(self, result: GateResult) -> BudgetLevel:
        if result.decision == GateDecision.DENY:
            return BudgetLevel.L5_HARD_STOP
        if result.decision == GateDecision.DEGRADE:
            return BudgetLevel.L3_DEGRADED
        if result.decision == GateDecision.BORROW:
            return BudgetLevel.L2_THROTTLED
        if result.decision == GateDecision.NARROW:
            return BudgetLevel.L1_WARNING
        return BudgetLevel.L0_NORMAL
