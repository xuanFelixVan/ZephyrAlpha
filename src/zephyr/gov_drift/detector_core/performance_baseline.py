# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-governance/drift-detector/blueprint.md
# [MODULE] zephyr.gov_drift.detector_core.performance_baseline
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] MOD-GATE_ENGINE;MOD-INF-021;MOD-INF-020
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] docs/03_modules/_domain-governance/drift-detector/blueprint.md;src/zephyr/behavioral-auditor/__init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_behavioral_auditor/
# [A_module] module_id=MOD-SEC_performance_baseline | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
from dataclasses import dataclass


@dataclass(frozen=True)
class LatencySegment:
    name: str
    max_ms: int
    description: str


PERFORMANCE_BASELINE: Final[list[LatencySegment]] = [
    LatencySegment(name="market_to_signal", max_ms=200, description="行情->信号"),
    LatencySegment(name="signal_to_risk", max_ms=10, description="信号->风控"),
    LatencySegment(name="risk_to_order", max_ms=50, description="风控->订单"),
]

E2E_MAX_MS: Final[int] = 500
E2E_BUDGET_BREAKDOWN: Final[dict[str, int]] = {
    "market_to_signal": 200,
    "signal_to_risk": 10,
    "risk_to_order": 50,
    "network_overhead": 100,
    "remaining_slack": 140,
}


def get_segment(name: str) -> LatencySegment | None:
    for seg in PERFORMANCE_BASELINE:
        if seg.name == name:
            return seg
    return None


def validate_e2e(segments: dict[str, int]) -> tuple[bool, str]:
    total = sum(segments.values())
    if total > E2E_MAX_MS:
        return False, f"E2E {total}ms > {E2E_MAX_MS}ms"
    for name, val in segments.items():
        seg = get_segment(name)
        if seg and val > seg.max_ms:
            return False, f"{name}: {val}ms > {seg.max_ms}ms"
    return True, f"E2E {total}ms ≤ {E2E_MAX_MS}ms — PASS"
