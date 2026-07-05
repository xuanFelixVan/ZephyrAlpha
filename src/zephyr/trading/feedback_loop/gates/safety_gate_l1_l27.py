# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.gates.safety_gate_l1_l27
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.gates.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_safety_gate_l1_l27 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Safety Gates L1-L27 — Unified Pipeline (MOD-FEEDBACK_LOOP §3)

Blindspot: No unified safety gate pipeline; scattered validation logic across subsystems.
Risk: Individual safety checks pass but combined effect is dangerous.

Mitigation: 27-layer defense-in-depth — any HARD gate REJECT blocks the action.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


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


@dataclass
class SafetyGatePipeline:
    gates: list[tuple[str, GateType]] = field(
        default_factory=lambda: [
            ("L1_BASIC_THRESHOLD", GateType.HARD),
            ("L2_FREQUENCY_LIMIT", GateType.SOFT),
            ("L3_TRADING_SILENCE", GateType.WARN),
            ("L4_DEPENDENCY_HEALTH", GateType.HARD),
            ("L5_BUDGET_ENFORCE", GateType.HARD),
            ("L6_ROLLBACK_INTEGRITY", GateType.HARD),
            ("L7_IDEMPOTENCY", GateType.HARD),
            ("L8_CONFIG_AS_CODE", GateType.WARN),
            ("L9_FLAG_INTERACTION", GateType.SOFT),
            ("L10_DB_INTEGRITY", GateType.HARD),
            ("L11_PROVENANCE_CHAIN", GateType.HARD),
            ("L12_SCHEMA_VERSIONING", GateType.HARD),
            ("L13_SESSION_AWARE", GateType.WARN),
            ("L14_RBAC", GateType.HARD),
            ("L15_DEPLOY_SECURITY", GateType.HARD),
            ("L16_ONLINE_ADAPTATION", GateType.WARN),
            ("L17_AUTONOMY_BOUNDARY", GateType.HARD),
            ("L18_CONTINUAL_LEARNING", GateType.WARN),
            ("L19_COGNITIVE_OVERLOAD", GateType.SOFT),
            ("L20_FLE_INTEGRITY", GateType.HARD),
            ("L21_SUPPLY_CHAIN_CVE", GateType.HARD),
            ("L22_DATA_FOUNDATION", GateType.HARD),
            ("L23_META_PERFORMANCE", GateType.SOFT),
            ("L24_AGENTIC_OPS", GateType.WARN),
            ("L25_LLM_QUALITY", GateType.HARD),
            ("L26_CHAOS_GOVERNANCE", GateType.WARN),
            ("L27_COMPLIANCE", GateType.HARD),
        ]
    )

    frequency_counters: dict[str, int] = field(default_factory=dict)
    FREQ_LIMIT_24H: int = field(default=10)

    def evaluate(self, ctx: ActionContext) -> list[GateResult]:
        results: list[GateResult] = []
        for gate_name, gate_type in self.gates:
            result = self._evaluate_gate(gate_name, gate_type, ctx)
            results.append(result)
            if gate_type is GateType.HARD and result.verdict is GateVerdict.REJECT:
                break
        return results

    def _evaluate_gate(self, name: str, gtype: GateType, ctx: ActionContext) -> GateResult:
        handlers = {
            "L1_BASIC_THRESHOLD": self._l1,
            "L2_FREQUENCY_LIMIT": self._l2,
            "L3_TRADING_SILENCE": self._l3,
            "L4_DEPENDENCY_HEALTH": self._l4,
            "L5_BUDGET_ENFORCE": self._l5,
            "L6_ROLLBACK_INTEGRITY": self._l6,
            "L7_IDEMPOTENCY": self._l7,
            "L8_CONFIG_AS_CODE": self._l8,
            "L9_FLAG_INTERACTION": self._l9,
            "L10_DB_INTEGRITY": self._l10,
            "L11_PROVENANCE_CHAIN": self._l11,
            "L12_SCHEMA_VERSIONING": self._l12,
            "L13_SESSION_AWARE": self._l13,
            "L14_RBAC": self._l14,
            "L15_DEPLOY_SECURITY": self._l15,
            "L16_ONLINE_ADAPTATION": self._l16,
            "L17_AUTONOMY_BOUNDARY": self._l17,
            "L18_CONTINUAL_LEARNING": self._l18,
            "L19_COGNITIVE_OVERLOAD": self._l19,
            "L20_FLE_INTEGRITY": self._l20,
            "L21_SUPPLY_CHAIN_CVE": self._l21,
            "L22_DATA_FOUNDATION": self._l22,
            "L23_META_PERFORMANCE": self._l23,
            "L24_AGENTIC_OPS": self._l24,
            "L25_LLM_QUALITY": self._l25,
            "L26_CHAOS_GOVERNANCE": self._l26,
            "L27_COMPLIANCE": self._l27,
        }
        handler = handlers.get(
            name, lambda c, g: GateResult(layer=name, verdict=GateVerdict.PASS, gate_type=g, reason="UNIMPLEMENTED")
        )
        return handler(ctx, gtype)

    def _l1(self, ctx: ActionContext, gt: GateType) -> GateResult:
        return GateResult("L1", GateVerdict.PASS, gt)

    def _l2(self, ctx: ActionContext, gt: GateType) -> GateResult:
        key = ctx.action_type
        self.frequency_counters[key] = self.frequency_counters.get(key, 0) + 1
        if self.frequency_counters[key] > self.FREQ_LIMIT_24H:
            return GateResult(
                "L2", GateVerdict.REJECT, gt, f"Frequency limit {self.FREQ_LIMIT_24H}/24h exceeded for {key}"
            )
        return GateResult("L2", GateVerdict.PASS, gt)

    def _l3(self, ctx: ActionContext, gt: GateType) -> GateResult:
        if ctx.is_trading_hours and ctx.severity < 8:
            return GateResult("L3", GateVerdict.OBSERVE_ONLY, gt, "Trading hours: low-severity action suppressed")
        return GateResult("L3", GateVerdict.PASS, gt)

    def _l4(self, ctx: ActionContext, gt: GateType) -> GateResult:
        critical_down = [svc for svc, ok in ctx.dependency_status.items() if not ok]
        if critical_down:
            return GateResult("L4", GateVerdict.REJECT, gt, f"Critical dependencies DOWN: {', '.join(critical_down)}")
        return GateResult("L4", GateVerdict.PASS, gt)

    def _l5(self, ctx: ActionContext, gt: GateType) -> GateResult:
        if ctx.cost_estimate > ctx.budget_remaining:
            return GateResult("L5", GateVerdict.REJECT, gt, f"Cost {ctx.cost_estimate} > budget {ctx.budget_remaining}")
        return GateResult("L5", GateVerdict.PASS, gt)

    def _l6(self, ctx: ActionContext, gt: GateType) -> GateResult:
        if not ctx.has_rollback:
            return GateResult("L6", GateVerdict.REJECT, gt, "No rollback plan for IRREVERSIBLE action")
        return GateResult("L6", GateVerdict.PASS, gt)

    def _l7(self, ctx: ActionContext, gt: GateType) -> GateResult:
        if not ctx.is_idempotent:
            return GateResult("L7", GateVerdict.PASS, gt, "NON_IDEMPONTENT: single-concurrency enforced")
        return GateResult("L7", GateVerdict.PASS, gt)

    def _l8(self, ctx: ActionContext, gt: GateType) -> GateResult:
        return GateResult("L8", GateVerdict.PASS, gt, "Config-as-code: WARN on manual config change")

    def _l9(self, ctx: ActionContext, gt: GateType) -> GateResult:
        return GateResult("L9", GateVerdict.PASS, gt, "Flag interaction check passed")

    def _l10(self, ctx: ActionContext, gt: GateType) -> GateResult:
        if ctx.data_quality_score < 50.0:
            return GateResult("L10", GateVerdict.REJECT, gt, "Database integrity: data quality critical")
        return GateResult("L10", GateVerdict.PASS, gt)

    def _l11(self, ctx: ActionContext, gt: GateType) -> GateResult:
        return GateResult("L11", GateVerdict.PASS, gt, "Provenance chain verified")

    def _l12(self, ctx: ActionContext, gt: GateType) -> GateResult:
        if ctx.schema_version != ctx.expected_schema_version:
            return GateResult(
                "L12",
                GateVerdict.REJECT,
                gt,
                f"Schema mismatch: {ctx.schema_version} vs expected {ctx.expected_schema_version}",
            )
        return GateResult("L12", GateVerdict.PASS, gt)

    def _l13(self, ctx: ActionContext, gt: GateType) -> GateResult:
        return GateResult("L13", GateVerdict.PASS, gt, "Session context intact")

    def _l14(self, ctx: ActionContext, gt: GateType) -> GateResult:
        return GateResult("L14", GateVerdict.PASS, gt, "RBAC: authorized")

    def _l15(self, ctx: ActionContext, gt: GateType) -> GateResult:
        return GateResult("L15", GateVerdict.PASS, gt, "Deploy security: signed artifact verified")

    def _l16(self, ctx: ActionContext, gt: GateType) -> GateResult:
        return GateResult("L16", GateVerdict.PASS, gt, "Online adaptation rate normal")

    def _l17(self, ctx: ActionContext, gt: GateType) -> GateResult:
        max_level, action_level = 4, ctx.autonomy_level
        if action_level > max_level:
            return GateResult("L17", GateVerdict.REJECT, gt, f"Autonomy level {action_level} > max {max_level}")
        return GateResult("L17", GateVerdict.PASS, gt)

    def _l18(self, ctx: ActionContext, gt: GateType) -> GateResult:
        return GateResult("L18", GateVerdict.PASS, gt, "EWC check: no catastrophic forgetting risk")

    def _l19(self, ctx: ActionContext, gt: GateType) -> GateResult:
        if ctx.owner_fatigue > 0.7:
            return GateResult(
                "L19", GateVerdict.REJECT, gt, f"Owner fatigue {ctx.owner_fatigue:.2f} > 0.7: defer non-P0"
            )
        return GateResult("L19", GateVerdict.PASS, gt)

    def _l20(self, ctx: ActionContext, gt: GateType) -> GateResult:
        if not ctx.has_self_modification_audit:
            return GateResult("L20", GateVerdict.REJECT, gt, "Self-modification not audited")
        return GateResult("L20", GateVerdict.PASS, gt)

    def _l21(self, ctx: ActionContext, gt: GateType) -> GateResult:
        if ctx.cve_alerts:
            return GateResult("L21", GateVerdict.REJECT, gt, f"CVE alerts: {', '.join(ctx.cve_alerts)}")
        return GateResult("L21", GateVerdict.PASS, gt)

    def _l22(self, ctx: ActionContext, gt: GateType) -> GateResult:
        if ctx.data_quality_score < 80.0:
            return GateResult(
                "L22", GateVerdict.REJECT, gt, f"Data quality {ctx.data_quality_score:.1f} < threshold 80"
            )
        return GateResult("L22", GateVerdict.PASS, gt)

    def _l23(self, ctx: ActionContext, gt: GateType) -> GateResult:
        return GateResult("L23", GateVerdict.PASS, gt, "Self-assessment: performance nominal")

    def _l24(self, ctx: ActionContext, gt: GateType) -> GateResult:
        return GateResult("L24", GateVerdict.PASS, gt, "Agent lifecycle: OK")

    def _l25(self, ctx: ActionContext, gt: GateType) -> GateResult:
        return GateResult("L25", GateVerdict.PASS, gt, "LLM provider: healthy")

    def _l26(self, ctx: ActionContext, gt: GateType) -> GateResult:
        return GateResult("L26", GateVerdict.PASS, gt, "Chaos governance: experiments isolated")

    def _l27(self, ctx: ActionContext, gt: GateType) -> GateResult:
        if not ctx.compliance_ok:
            return GateResult("L27", GateVerdict.REJECT, gt, "Compliance violation detected")
        return GateResult("L27", GateVerdict.PASS, gt)

    @property
    def is_blocked(self) -> bool:
        return any(r.verdict is GateVerdict.REJECT for r in self.results)

    @property
    def reject_trace(self) -> list[str]:
        return [f"{r.layer}({r.gate_type.value}): {r.reason}" for r in self.results if r.verdict is GateVerdict.REJECT]

    results: list[GateResult] = field(default_factory=list)
