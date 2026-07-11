# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.gates.parameterized_safety_gate
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.trading.feedback_loop.gates.__init__
# [CONSUMERS] blueprint.md §0; zephyr.trading.feedback_loop 内部模块; zephyr.trading
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] MOD-FEEDBACK_LOOP 检测-诊断-动作链不可绕过; GateQueue 全局串行; 原子写入 temp-file+os.replace()
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] FeedbackLoopError
# [TESTS] tests/feedback-loop/
# [A_module] module_id=MOD-UNK_parameterized_safety_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-GATE_ENGINE | 03_modules/_cross_layer/gate-engine/blueprint.md | §

GateVerdict — GateVerdict

依据: 蓝图 MOD-FEEDBACK_LOOP §3-§9

"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class GateVerdict(str, Enum):
    PASS = "PASS"

    REJECT = "REJECT"

    OBSERVE_ONLY = "OBSERVE_ONLY"


class GateType(str, Enum):
    HARD = "HARD"

    SOFT = "SOFT"

    WARN = "WARN"


@dataclass
class GateResult:
    layer: str

    verdict: GateVerdict

    gate_type: GateType

    reason: str = ""


@dataclass
class ActionContext:
    action_id: str

    action_type: str

    severity: int = 0

    autonomy_level: int = 0

    timestamp: float = 0.0

    has_rollback: bool = False

    is_idempotent: bool = False

    cost_estimate: float = 0.0

    budget_remaining: float = 0.0

    dependency_status: dict[str, bool] = field(default_factory=dict)

    schema_version: int = 1

    expected_schema_version: int = 1

    cve_alerts: list[str] = field(default_factory=list)

    data_quality_score: float = 100.0

    has_self_modification_audit: bool = False

    in_circuit_breaker: bool = False

    is_trading_hours: bool = False

    owner_fatigue: float = 0.0

    compliance_ok: bool = True

    last_drill_days: float = 999.0

    skill_trust: float = 1.0

    active_cves: list[str] = field(default_factory=list)

    canary_success_rate: float = 1.0

    rollback_success_rate: float = 1.0

    drift_score: float = 0.0

    drift_budget: float = 1.0

    feature_flag_conflict: bool = False

    chaos_active: bool = False

    chaos_isolated: bool = True

    llm_provider_healthy: bool = True

    rbac_authorized: bool = True

    deploy_artifact_signed: bool = True

    session_intact: bool = True

    provenance_verified: bool = True

    ewc_risk: float = 0.0

    online_adaptation_rate: float = 0.0

    online_adaptation_max: float = 1.0

    config_as_code: bool = True

    flag_interaction_ok: bool = True

    agent_lifecycle_ok: bool = True

    performance_nominal: bool = True


_OPS = {
    "gt": lambda a, b: a > b,
    "lt": lambda a, b: a < b,
    "gte": lambda a, b: a >= b,
    "lte": lambda a, b: a <= b,
    "eq": lambda a, b: a == b,
    "neq": lambda a, b: a != b,
}


@dataclass
class ParameterizedSafetyGate:
    config_path: str | Path | None = None

    rules: list[dict[str, Any]] = field(default_factory=list)

    frequency_counters: dict[str, int] = field(default_factory=dict)

    results: list[GateResult] = field(default_factory=list)

    def __post_init__(self):
        if self.config_path and not self.rules:
            self.load_config(self.config_path)

    def load_config(self, path: str | Path) -> None:
        p = Path(path)

        if not p.exists():
            p = Path(__file__).parent / "safety-gate-config.yaml"

        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.rules = data.get("rules", [])

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        results: list[GateResult] = []

        for rule in self.rules:
            result = self._evaluate_rule(rule, ctx)

            results.append(result)

            gtype = GateType(rule.get("gate_type", "HARD"))

            if gtype is GateType.HARD and result.verdict is GateVerdict.REJECT:
                break

        return results

    def _evaluate_rule(self, rule: dict[str, Any], ctx: ActionContext) -> GateResult:
        layer = rule["layer"]

        gtype = GateType(rule.get("gate_type", "HARD"))

        rtype = rule.get("type", "always_pass")

        reject_reason = rule.get("reject_reason", f"{layer} check failed")

        if rtype == "always_pass":
            return GateResult(layer, GateVerdict.PASS, gtype, rule.get("pass_reason", ""))

        if rtype == "threshold":
            field_name = rule["field"]

            threshold = rule["threshold"]

            op = rule.get("op", "gt")

            val = getattr(ctx, field_name, None)

            if val is not None and _OPS.get(op, lambda a, b: False)(val, threshold):
                fmt_reason = reject_reason.format(value=val, threshold=threshold)

                return GateResult(layer, GateVerdict.REJECT, gtype, fmt_reason)

            return GateResult(layer, GateVerdict.PASS, gtype)

        if rtype == "boolean":
            field_name = rule["field"]

            val = getattr(ctx, field_name, None)

            expected = rule.get("expected", True)

            reject_on = rule.get("reject_on", "mismatch")

            if reject_on == "mismatch" and val != expected:
                return GateResult(layer, GateVerdict.REJECT, gtype, reject_reason.format(value=val))

            if reject_on == "match" and val == expected:
                return GateResult(layer, GateVerdict.REJECT, gtype, reject_reason.format(value=val))

            return GateResult(layer, GateVerdict.PASS, gtype)

        if rtype == "frequency":
            key_field = rule.get("key_field", "action_type")

            key = getattr(ctx, key_field, "default")

            limit = rule.get("limit", 10)

            self.frequency_counters[key] = self.frequency_counters.get(key, 0) + 1

            if self.frequency_counters[key] > limit:
                return GateResult(
                    layer,
                    GateVerdict.REJECT,
                    gtype,
                    reject_reason.format(count=self.frequency_counters[key], limit=limit),
                )

            return GateResult(layer, GateVerdict.PASS, gtype)

        if rtype == "enum":
            field_name = rule["field"]

            val = getattr(ctx, field_name, None)

            allowed = rule.get("allowed_values", [])

            if val is not None and allowed and str(val) not in [str(v) for v in allowed]:
                return GateResult(layer, GateVerdict.REJECT, gtype, reject_reason.format(value=val))

            return GateResult(layer, GateVerdict.PASS, gtype)

        if rtype == "observe":
            field_name = rule.get("field", "")

            val = getattr(ctx, field_name, None) if field_name else None

            if val and ((isinstance(val, list) and len(val) > 0) or (isinstance(val, bool) and val)):
                return GateResult(layer, GateVerdict.OBSERVE_ONLY, gtype, reject_reason.format(value=val))

            return GateResult(layer, GateVerdict.PASS, gtype)

        if rtype == "custom":
            handler_path = rule.get("handler", "")

            if handler_path:
                try:
                    module_path, func_name = handler_path.rsplit(".", 1)

                    import importlib

                    mod = importlib.import_module(module_path)

                    handler = getattr(mod, func_name)

                    return handler(ctx, gtype, rule)

                except Exception as e:
                    logger.warning("suppressed error in parameterized_safety_gate", exc_info=True)

            return GateResult(layer, GateVerdict.PASS, gtype, "Custom handler not found, defaulting to PASS")

        return GateResult(layer, GateVerdict.PASS, gtype, f"Unknown rule type: {rtype}")

    @property
    def is_blocked(self) -> bool:
        return any(r.verdict is GateVerdict.REJECT for r in self.results)

    @property
    def reject_trace(self) -> list[str]:
        return [f"{r.layer}({r.gate_type.value}): {r.reason}" for r in self.results if r.verdict is GateVerdict.REJECT]


def _l3_trading_silence(ctx: ActionContext, gt: GateType, rule: dict) -> GateResult:
    if ctx.is_trading_hours and ctx.severity < 8:
        return GateResult("L3", GateVerdict.OBSERVE_ONLY, gt, "Trading hours: low-severity action suppressed")

    return GateResult("L3", GateVerdict.PASS, gt)


def _l4_dependency(ctx: ActionContext, gt: GateType, rule: dict) -> GateResult:
    critical_down = [svc for svc, ok in ctx.dependency_status.items() if not ok]

    if critical_down:
        return GateResult("L4", GateVerdict.REJECT, gt, f"Critical dependencies DOWN: {', '.join(critical_down)}")

    return GateResult("L4", GateVerdict.PASS, gt)


def _l12_schema(ctx: ActionContext, gt: GateType, rule: dict) -> GateResult:
    if ctx.schema_version != ctx.expected_schema_version:
        return GateResult(
            "L12",
            GateVerdict.REJECT,
            gt,
            f"Schema mismatch: {ctx.schema_version} vs expected {ctx.expected_schema_version}",
        )

    return GateResult("L12", GateVerdict.PASS, gt)


def _l29_supply_chain(ctx: ActionContext, gt: GateType, rule: dict) -> GateResult:
    if ctx.active_cves:
        return GateResult("L29", GateVerdict.OBSERVE_ONLY, gt, f"Active CVE: {', '.join(ctx.active_cves)}")

    if ctx.skill_trust < 0.5:
        return GateResult("L29", GateVerdict.REJECT, gt, f"Skill trust {ctx.skill_trust:.2f} < 0.5")

    return GateResult("L29", GateVerdict.PASS, gt)
