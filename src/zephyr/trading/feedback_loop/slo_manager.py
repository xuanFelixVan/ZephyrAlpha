from typing import Final

# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.slo_manager
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_slo_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""SLO/SLI 管理器（CT-SLO-001）——14条CT-* p95/p99目标 + Error Budget。"""


SLO_MATRIX: Final[dict[str, dict]] = {
    "CT-ORC-SCRIPT-001": {"slos": [("p95", 3600.0)], "metric": "duration_s"},
    "CT-ORC-CE-001": {"slos": [("p95", 3.0)], "metric": "duration_s"},
    "CT-ORC-VMS-001": {"slos": [("p99", 1.0)], "metric": "duration_s"},
    "CT-ORC-GATE-001": {"slos": [("p99", 0.05)], "metric": "duration_s"},
    "CT-SCRIPT-KB-001": {"slos": [("p95", 30.0)], "metric": "duration_s"},
    "CT-SCRIPT-GATE-001": {"slos": [("p95", 30.0)], "metric": "duration_s"},
    "CT-CE-VMS-001": {"slos": [("p99", 0.5)], "metric": "duration_s"},
    "CT-CE-LSG-001": {"slos": [("p99", 0.1), ("false_positive_pct", 5.0)], "metric": "duration_s"},
    "CT-KB-VMS-001": {"slos": [("p99", 5.0)], "metric": "duration_s"},
    "CT-FLE-ORC-001": {"slos": [("p95", 30.0), ("false_positive_pct", 10.0)], "metric": "duration_s"},
    "CT-FLE-DB-001": {"slos": [("p95", 10.0)], "metric": "duration_s"},
    "CT-TELE-FLE-001": {"slos": [("p95", 5.0)], "metric": "duration_s"},
    "CT-PIPE-ORC-001": {"slos": [("p95", 2.0)], "metric": "duration_s"},
    "CT-ORC-DB-001": {"slos": [("p95", 0.5)], "metric": "duration_s"},
}


class SLOManager:
    def get_slos(self, contract_id: str) -> dict | None:
        return SLO_MATRIX.get(contract_id)

    def list_contracts(self) -> list[str]:
        return list(SLO_MATRIX.keys())

    def check(self, contract_id: str, p95: float) -> tuple[bool, str]:
        slo = SLO_MATRIX.get(contract_id)
        if slo is None:
            return True, "NO_SLO_DEFINED"
        for percentile, threshold in slo["slos"]:
            if percentile == "p95" and p95 > threshold:
                return False, f"p95 {p95}s > {threshold}s"
            if percentile == "p99" and p95 > threshold:
                return False, f"p99 {p95}s > {threshold}s"
        return True, "OK"
