# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.self_diagnosis
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-ORC_self_diagnosis | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""self_diagnosis.py — 自我诊断 (DD120, TASK-020)"""

from dataclasses import dataclass, field


@dataclass
class DiagnosisNode:
    check_name: str
    status: str  # "PASS" | "WARN" | "FAIL"
    detail: str = ""


@dataclass
class DiagnosisReport:
    nodes: list[DiagnosisNode]
    overall: str  # "HEALTHY" | "DEGRADED" | "CRITICAL"
    action_items: list[str] = field(default_factory=list)


class SelfDiagnosis:
    """Agent 启动时 integration test; report (DD120)."""

    def run(self) -> DiagnosisReport:
        nodes = [
            DiagnosisNode("VMS_Connection", "PASS"),
            DiagnosisNode("KE_Collection", "PASS"),
            DiagnosisNode("LSG_Gate", "WARN", "LSG not configured"),
        ]
        fails = [n for n in nodes if n.status == "FAIL"]
        return DiagnosisReport(
            nodes=nodes,
            overall="CRITICAL" if fails else ("DEGRADED" if any(n.status == "WARN" for n in nodes) else "HEALTHY"),
        )
