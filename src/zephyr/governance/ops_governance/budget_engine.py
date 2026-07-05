# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §2-4
# [MODULE] zephyr.governance.ops_governance.budget_engine
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.governance.ops_governance.budget_models; zephyr.governance.drift_detection.drift_infrastructure
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_budget_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Budget Enforcer core engine — MOD-INF-024

Pre-flight gate, model router, degradation manager, and budget consumption tracking.
3D budget system: Token/Cost/Time with seven-level escalation.
Blueprint: docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md §2-4
"""

from __future__ import annotations

import hashlib
import logging
import threading
from collections.abc import Callable
from datetime import UTC, datetime

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

logger = logging.getLogger(__name__)

DEFAULT_DEGRADATION_STEPS: list[DegradationStep] = [
    DegradationStep(
        0, "Normal operation — Premium models available", ModelTier.PREMIUM, BudgetLevel.L0_NORMAL, 32_000, 0
    ),
    DegradationStep(1, "Warning — Standard models only", ModelTier.STANDARD, BudgetLevel.L1_WARNING, 16_000, 120),
    DegradationStep(
        2, "Throttled — Economy models, reduced context", ModelTier.ECONOMY, BudgetLevel.L2_THROTTLED, 8_000, 300
    ),
    DegradationStep(
        3, "Degraded — Minimal models, essential only", ModelTier.MINIMAL, BudgetLevel.L3_DEGRADED, 4_000, 600
    ),
    DegradationStep(
        4, "Emergency — Read-only, no code generation", ModelTier.MINIMAL, BudgetLevel.L4_EMERGENCY, 2_000, 900
    ),
]


class BudgetEngine:
    _instance: "BudgetEngine | None" = None
    _instance_lock = threading.Lock()

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
        self._on_consumption_recorded: Callable[[str, int, float, float], None] | None = None
        self._ipi_defense = None
        self._spiral_ews = None
        self._closed = False
        self._init_consumption()

    @property
    def degradation_steps(self) -> list[DegradationStep]:
        """当前生效的降级阶梯（只读视图）。"""
        return self._degradation_steps

    @property
    def current_degradation_level(self) -> BudgetLevel:
        """当前降级等级（只读视图）。"""
        return self._current_degradation_level

    @classmethod
    def ensure_initialized(cls) -> "BudgetEngine":
        """确保 BudgetEngine 已初始化并返回实例（幂等）。"""
        if cls._instance is not None:
            return cls._instance
        with cls._instance_lock:
            if cls._instance is not None:
                return cls._instance
            engine = cls()
            engine.pre_flight_check("baseline", 0, 0.0)
            cls._instance = engine
            return cls._instance

    def get_snapshot(self) -> dict:
        """获取当前预算快照。不持有锁，由子方法各自加锁。"""
        return {
            "consumption": self.get_consumption_summary(),
            "degradation_level": self._current_degradation_level.value,
            "active_step_idx": self._active_step_idx,
            "hash": self.compute_hash(),
            "health": "HEALTHY" if self._active_step_idx == 0 else "DEGRADED",
        }

    def shutdown(self) -> dict:
        """关闭 BudgetEngine——资源清理+状态持久化+单例重置。幂等。"""
        import json
        import os

        if self._closed:
            return {"persisted_to": None, "snapshot": self.get_snapshot(), "cleaned_up": True}

        snapshot = self.get_snapshot()
        persist_path = os.path.join("data", "budget", "shutdown_snapshot.json")
        try:
            os.makedirs(os.path.dirname(persist_path), exist_ok=True)
            tmp_path = f"{persist_path}.{os.getpid()}.tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, persist_path)
        except Exception as e:
            logger.warning("BudgetEngine.shutdown: snapshot persist failed (%s: %s)", type(e).__name__, e)

        with self._lock:
            self._ipi_defense = None
            self._spiral_ews = None
            self._gate_history.clear()
            self._closed = True

        BudgetEngine._instance = None
        return {"persisted_to": persist_path, "snapshot": snapshot, "cleaned_up": True}

    @classmethod
    def recover_from_snapshot(cls, snapshot_path: str = "") -> "BudgetEngine":
        """从快照文件恢复 BudgetEngine 状态。

        读取 shutdown() 持久化的 JSON 快照，恢复消费数据和降级级别。
        用于 session 重启后恢复预算状态。
        """
        import json
        import os

        if not snapshot_path:
            snapshot_path = os.path.join("data", "budget", "shutdown_snapshot.json")

        engine = cls()
        try:
            with open(snapshot_path, encoding="utf-8") as f:
                snapshot = json.load(f)
            consumption = snapshot.get("consumption", {})
            for policy_id, data in consumption.items():
                cons = engine._consumption.get(policy_id)
                if cons and isinstance(data, dict):
                    cons.consumed_daily = data.get("daily", 0.0)
                    cons.consumed_hourly = data.get("hourly", 0.0)
            step_idx = snapshot.get("active_step_idx", 0)
            for _ in range(step_idx):
                engine.advance_degradation()
        except Exception as e:
            logger.warning("BudgetEngine.recover_from_snapshot: snapshot load failed (%s: %s)", type(e).__name__, e)
        return engine

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

    def try_claim_budget(
        self, provider_id: str, dimension: BudgetDimension, amount: float, expected_version: int | None = None
    ) -> tuple[bool, int, str]:
        with self._lock:
            policy = self._policies.get(dimension)
            if policy is None:
                return False, -1, "No policy defined"

            cons = self._consumption.get(policy.policy_id)
            if cons is None:
                return False, -1, "No consumption tracked"

            current_version = self._consumption_version.get(policy.policy_id, 0)
            if expected_version is not None and current_version != expected_version:
                return (
                    False,
                    current_version,
                    f"Version mismatch: expected={expected_version}, current={current_version}",
                )

            provider_claims = self._provider_claims.get(provider_id, {})
            already_claimed = provider_claims.get(policy.policy_id, 0.0)

            remaining_daily = policy.daily_limit - cons.consumed_daily - already_claimed
            remaining_hourly = policy.hourly_limit - cons.consumed_hourly - already_claimed

            if remaining_daily < amount:
                return (
                    False,
                    current_version,
                    f"Insufficient daily budget: remaining={remaining_daily:.2f}, requested={amount:.2f}",
                )
            if remaining_hourly < amount:
                return (
                    False,
                    current_version,
                    f"Insufficient hourly budget: remaining={remaining_hourly:.2f}, requested={amount:.2f}",
                )

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

            now = datetime.now(UTC)
            if (now - cons.last_reset_daily).days >= 1:
                cons.consumed_daily = 0.0
                cons.request_count_daily = 0
                cons.last_reset_daily = now
            if (now - cons.last_reset_hourly).total_seconds() >= 3600:
                cons.consumed_hourly = 0.0
                cons.last_reset_hourly = now

            committed = min(actual_amount, claimed) if claimed > 0 else actual_amount

            if (
                cons.dimension is BudgetDimension.TOKEN
                or cons.dimension is BudgetDimension.COST
                or cons.dimension is BudgetDimension.TIME
            ):
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

    def pre_flight_check(self, request_id: str, estimated_tokens: int = 0, estimated_cost: float = 0.0, prompt: str = "") -> GateResult:
        if self._closed:
            raise RuntimeError("BudgetEngine已关闭")

        # IPI 检查——若 prompt 含注入攻击，直接 DENY 并触发隔离
        if prompt:
            if self._check_ipi_attack(prompt):
                return GateResult(
                    request_id=request_id,
                    decision=GateDecision.DENY,
                    reason="IPI attack detected — request blocked and isolation triggered",
                    remaining_daily=0.0,
                    remaining_hourly=0.0,
                    estimated_tokens=estimated_tokens,
                    estimated_cost=estimated_cost,
                )

        with self._lock:
            token_result = self._check_dimension(BudgetDimension.TOKEN, request_id, estimated_tokens, estimated_cost)
            cost_result = self._check_dimension(BudgetDimension.COST, request_id, estimated_tokens, estimated_cost)

            worst = token_result
            if cost_result.decision is GateDecision.DENY or (
                cost_result.decision is GateDecision.DEGRADE and worst.decision is not GateDecision.DENY
            ):
                worst = cost_result

        try:
            from zephyr.governance.drift_detection.drift_infrastructure import check_budget_for_gate

            drift_result = check_budget_for_gate("MOD-INF-024", tier="P1")
            if not drift_result.get("allowed", True):
                with self._lock:
                    if worst.decision is not GateDecision.DENY:
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
        if self._closed:
            raise RuntimeError("BudgetEngine已关闭")

        with self._lock:
            cons = self._consumption.get(policy_id)
            if cons is None:
                return
            now = datetime.now(UTC)
            if (now - cons.last_reset_daily).days >= 1:
                cons.consumed_daily = 0.0
                cons.request_count_daily = 0
                cons.last_reset_daily = now
            if (now - cons.last_reset_hourly).total_seconds() >= 3600:
                cons.consumed_hourly = 0.0
                cons.last_reset_hourly = now

            if cons.dimension is BudgetDimension.TOKEN:
                cons.consumed_daily += tokens
                cons.consumed_hourly += tokens
                cons.consumed_per_request = tokens
            elif cons.dimension is BudgetDimension.COST:
                cons.consumed_daily += cost
                cons.consumed_hourly += cost
                cons.consumed_per_request = cost
            elif cons.dimension is BudgetDimension.TIME:
                cons.consumed_daily += time_minutes
                cons.consumed_hourly += time_minutes
                cons.consumed_per_request = time_minutes

            cons.request_count_daily += 1

        if self._on_consumption_recorded is not None:
            self._on_consumption_recorded(policy_id, tokens, cost, time_minutes)

        try:
            import importlib

            _mod = importlib.import_module("zephyr.infrastructure.system_telemetry._budget_telemetry_bridge")
            gt = _mod.get_telemetry()
            if gt is not None:
                gt.metrics.gauge(f"budget.{policy_id}.tokens_consumed", float(tokens))
                gt.metrics.gauge(f"budget.{policy_id}.cost_usd", cost)
        except Exception:
            pass

        # 事件驱动响应链 1: 预算超限 → 自动降级
        self._check_budget_exceeded()
        # 事件驱动响应链 3: 螺旋预警 → 自动告警/降级
        self._check_spiral_warning(tokens, cost)

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

    def get_active_policy(self, dimension: BudgetDimension) -> BudgetPolicy | None:
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

    def _check_dimension(
        self, dimension: BudgetDimension, request_id: str, estimated_tokens: int, estimated_cost: float
    ) -> GateResult:
        policy = self._policies.get(dimension)
        if policy is None:
            return GateResult(request_id=request_id, decision=GateDecision.ALLOW, reason="No policy defined")

        cons = self._consumption.get(policy.policy_id)
        if cons is None:
            return GateResult(request_id=request_id, decision=GateDecision.ALLOW, reason="No consumption tracked")

        remaining_daily = policy.daily_limit - cons.consumed_daily
        remaining_hourly = policy.hourly_limit - cons.consumed_hourly

        daily_ratio = cons.consumed_daily / policy.daily_limit if policy.daily_limit > 0 else 0.0

        consumption: float = (
            float(estimated_tokens)
            if dimension is BudgetDimension.TOKEN
            else (estimated_cost if dimension is BudgetDimension.COST else 0.0)
        )

        if consumption > policy.per_request_limit:
            return GateResult(
                request_id=request_id,
                decision=GateDecision.NARROW,
                reason=f"Per-request limit exceeded: {policy.per_request_limit}",
                remaining_daily=remaining_daily,
                remaining_hourly=remaining_hourly,
                estimated_tokens=estimated_tokens,
                estimated_cost=estimated_cost,
            )

        if daily_ratio >= policy.hard_stop_threshold:
            return GateResult(
                request_id=request_id,
                decision=GateDecision.DENY,
                reason=f"{dimension.name} hard stop: daily {daily_ratio:.0%}",
                remaining_daily=remaining_daily,
                remaining_hourly=remaining_hourly,
                estimated_tokens=estimated_tokens,
                estimated_cost=estimated_cost,
            )

        if daily_ratio >= policy.emergency_threshold:
            return GateResult(
                request_id=request_id,
                decision=GateDecision.DEGRADE,
                reason=f"{dimension.name} emergency: daily {daily_ratio:.0%}",
                remaining_daily=remaining_daily,
                remaining_hourly=remaining_hourly,
                estimated_tokens=estimated_tokens,
                estimated_cost=estimated_cost,
            )

        if daily_ratio >= policy.degrade_threshold:
            return GateResult(
                request_id=request_id,
                decision=GateDecision.BORROW,
                reason=f"{dimension.name} degraded: daily {daily_ratio:.0%}",
                remaining_daily=remaining_daily,
                remaining_hourly=remaining_hourly,
                estimated_tokens=estimated_tokens,
                estimated_cost=estimated_cost,
            )

        if remaining_hourly <= consumption:
            return GateResult(
                request_id=request_id,
                decision=GateDecision.BORROW,
                reason=f"{dimension.name} hourly exhausted",
                remaining_daily=remaining_daily,
                remaining_hourly=remaining_hourly,
                estimated_tokens=estimated_tokens,
                estimated_cost=estimated_cost,
            )

        return GateResult(
            request_id=request_id,
            decision=GateDecision.ALLOW,
            reason="OK",
            remaining_daily=remaining_daily,
            remaining_hourly=remaining_hourly,
            estimated_tokens=estimated_tokens,
            estimated_cost=estimated_cost,
        )

    def _compute_budget_level(self, result: GateResult) -> BudgetLevel:
        if result.decision is GateDecision.DENY:
            return BudgetLevel.L5_HARD_STOP
        if result.decision is GateDecision.DEGRADE:
            return BudgetLevel.L3_DEGRADED
        if result.decision is GateDecision.BORROW:
            return BudgetLevel.L2_THROTTLED
        if result.decision is GateDecision.NARROW:
            return BudgetLevel.L1_WARNING
        return BudgetLevel.L0_NORMAL

    # ── 事件驱动响应链 (DM-201503) ──────────────────────────────

    def subscribe_events(self) -> None:
        """订阅 EventBus 的 TASK_COMPLETED 和 TASK_FAILED 事件。

        幂等：重复调用安全。EventBus 不可用时静默跳过。
        """
        try:
            from zephyr.shared.events.event_bus import EventBus, EventType

            bus = EventBus.get_instance()
            bus.subscribe(EventType.TASK_COMPLETED, self._on_task_completed_budget)
            bus.subscribe(EventType.TASK_FAILED, self._on_task_failed_budget)
        except Exception:
            pass

    def _on_task_completed_budget(self, event: object) -> None:
        """TASK_COMPLETED 事件：检查预算状态。"""
        try:
            self._check_budget_exceeded()
        except Exception:
            pass

    def _on_task_failed_budget(self, event: object) -> None:
        """TASK_FAILED 事件：检查重试预算。"""
        try:
            self._check_budget_exceeded()
        except Exception:
            pass

    def _check_budget_exceeded(self) -> None:
        """响应链 1: 预算超限 → 自动降级。

        消费达到 hard_stop_threshold * 80% 或 emergency_threshold 时自动推进降级。
        """
        import uuid

        for dim, policy in self._policies.items():
            cons = self._consumption.get(policy.policy_id)
            if cons is None:
                continue
            ratio = cons.consumed_daily / policy.daily_limit if policy.daily_limit > 0 else 0.0

            if ratio >= policy.hard_stop_threshold * 0.8:
                while self._active_step_idx < 3:
                    if not self.advance_degradation():
                        break
                alert = BudgetAlert(
                    alert_id=f"BUDGET-EXCEEDED-{uuid.uuid4().hex[:8]}",
                    policy_id=policy.policy_id,
                    dimension=dim,
                    level=BudgetLevel.L3_DEGRADED,
                    message=f"Budget exceeded: {dim.name} daily ratio={ratio:.0%}",
                    triggered_at=datetime.now(UTC),
                    acknowledged=False,
                )
                with self._lock:
                    self._alerts.append(alert)
            elif ratio >= policy.emergency_threshold:
                while self._active_step_idx < 2:
                    if not self.advance_degradation():
                        break
                alert = BudgetAlert(
                    alert_id=f"BUDGET-EMERGENCY-{uuid.uuid4().hex[:8]}",
                    policy_id=policy.policy_id,
                    dimension=dim,
                    level=BudgetLevel.L2_THROTTLED,
                    message=f"Budget emergency: {dim.name} daily ratio={ratio:.0%}",
                    triggered_at=datetime.now(UTC),
                    acknowledged=False,
                )
                with self._lock:
                    self._alerts.append(alert)

    def _check_ipi_attack(self, prompt: str) -> bool:
        """响应链 2: IPI 攻击 → 自动隔离。

        检测到 IPI 攻击时，降级强制推进到 L4_EMERGENCY。
        返回 True 表示检测到攻击。
        """
        import uuid

        if self._ipi_defense is None:
            try:
                from zephyr.governance.security_governance.ipi_defense import IPIDefense

                self._ipi_defense = IPIDefense()
            except ImportError:
                return False

        report = self._ipi_defense.scan(prompt)
        if report.blocked:
            while self._active_step_idx < 4:
                if not self.advance_degradation():
                    break
            alert = BudgetAlert(
                alert_id=f"IPI-ATTACK-{uuid.uuid4().hex[:8]}",
                policy_id="BP-SECURITY-001",
                dimension=BudgetDimension.TOKEN,
                level=BudgetLevel.L4_EMERGENCY,
                message=f"IPI attack blocked: {report.attack_type} confidence={report.confidence:.0%}",
                triggered_at=datetime.now(UTC),
                acknowledged=False,
            )
            with self._lock:
                self._alerts.append(alert)
            return True
        return False

    def _check_spiral_warning(self, tokens: int, cost: float) -> None:
        """响应链 3: 螺旋预警 → 自动告警/降级。

        喂入消费数据到 SpiralEWS，检测到 WARNING/CRITICAL 时创建告警。
        """
        import uuid

        if self._spiral_ews is None:
            try:
                from zephyr.governance.drift_detection.spiral_ews import SpiralEarlyWarningSystem

                self._spiral_ews = SpiralEarlyWarningSystem()
            except ImportError:
                return

        self._spiral_ews.feed(tokens, cost, depth=1)
        signal = self._spiral_ews.check()

        if signal.level in ("WARNING", "CRITICAL"):
            level = BudgetLevel.L2_THROTTLED if signal.level == "WARNING" else BudgetLevel.L3_DEGRADED
            alert = BudgetAlert(
                alert_id=f"SPIRAL-{signal.level}-{uuid.uuid4().hex[:8]}",
                policy_id="BP-SPIRAL-001",
                dimension=BudgetDimension.TOKEN,
                level=level,
                message=f"Spiral {signal.level}: composite_score={signal.composite_score:.2f}",
                triggered_at=datetime.now(UTC),
                acknowledged=False,
            )
            with self._lock:
                self._alerts.append(alert)

            if signal.level == "CRITICAL" and self._spiral_ews.is_spiraling():
                self.advance_degradation()


# ── EventBusBackpressure 订阅 (DM-2507-B) ──────────────────────────────

_bus_subscribed = False


def subscribe_eventbus() -> None:
    """订阅 EventBusBackpressure 的 slo_violation 事件。

    幂等：重复调用安全。Backpressure 总线不可用时静默跳过。
    供 boot_hooks 统一调用。
    """
    global _bus_subscribed
    if _bus_subscribed:
        return
    try:
        from zephyr.shared.events.event_bus import EventBusBackpressure

        bus = EventBusBackpressure()
        bus.subscribe("slo_violation", _on_slo_violation)
        _bus_subscribed = True
    except Exception:
        pass


def _on_slo_violation(payload: object) -> None:
    """slo_violation 事件：SLO违规触发预算降级。轻量handler——日志+调用已有方法。"""
    try:
        engine = BudgetEngine.ensure_initialized()
        engine._check_budget_exceeded()
    except Exception:
        pass
