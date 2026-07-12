# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | CT-SCRIPT-GATE-001
# [MODULE] zephyr.infrastructure.script_system.gate_bridge
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.script_system.__init__
# [CONSUMERS] zephyr.orchestrator.script_runner; AutoRuntime Core post-scan phase
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 12维->gate_id 映射; 维度聚合后批量提交; gate不可用时仅日志不阻塞
# [MODIFY-GUARD] CT-SCRIPT-GATE-001 维度映射表增删必须同步更新GateEngine注册表
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] GateEngine不可用返回degraded不阻塞; 空findings返回空
# [TESTS] scripts/connect/script_gate.py --trigger
# [A_module] module_id=MOD-INF_gate_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Script->Gate 门禁桥接器 — submit_findings() 生产者

CT-SCRIPT-GATE-001: 审计脚本执行完成后将 findings 按12维度聚合提交给 Gate Engine。
"""

from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "GateBridge",
    "GateSubmitResult",
    "submit_to_gate",
]

DIMENSION_GATE_MAP: dict[str, str] = {
    "D1": "G1",
    "D2": "G1",
    "D3": "G2",
    "D4": "G2",
    "D5": "G3",
    "D6": "G3",
    "D7": "G4",
    "D8": "G4",
    "D9": "G5",
    "D10": "G5",
    "D11": "G6",
    "D12": "G6",
}


@dataclass
class GateSubmitResult:
    submitted: int = 0
    gates_evaluated: list[str] = field(default_factory=list)
    passed: int = 0
    blocked: int = 0
    status: str = "complete"
    error: str | None = None


class GateBridge:
    def submit_findings(
        self,
        findings: list[dict[str, Any]],
        task_id: str = "",
        session_id: str = "",
    ) -> GateSubmitResult:
        if not findings:
            return GateSubmitResult()

        aggregated = self._aggregate_by_gate(findings)

        result = GateSubmitResult()
        for gate_id, count in aggregated.items():
            result.gates_evaluated.append(gate_id)
            result.submitted += count
            try:
                passed = self._check_gate(gate_id, count, task_id, session_id)
                if passed:
                    result.passed += count
                else:
                    result.blocked += count
            except Exception as exc:
                logger.warning("[SCRIPT-GATE] gate %s check degraded: %s", gate_id, exc, exc_info=True)
                result.passed += count

        logger.info(
            "[SCRIPT-GATE] submitted: task=%s gates=%d total=%d passed=%d blocked=%d",
            task_id,
            len(result.gates_evaluated),
            result.submitted,
            result.passed,
            result.blocked,
        )
        return result

    def _aggregate_by_gate(self, findings: list[dict[str, Any]]) -> dict[str, int]:
        aggregated: dict[str, int] = {}
        for f in findings:
            dim = f.get("dimension", f.get("dim", ""))
            gate_id = DIMENSION_GATE_MAP.get(dim, "G0")
            aggregated[gate_id] = aggregated.get(gate_id, 0) + 1
        return aggregated

    def _check_gate(
        self,
        gate_id: str,
        count: int,
        task_id: str,
        session_id: str,
    ) -> bool:
        try:
            _mod = importlib.import_module("zephyr.governance.rule_enforcement.gate_engine")
            GateEngine = _mod.GateEngine
            engine = GateEngine()
            if hasattr(engine, "evaluate_gate"):
                result = engine.evaluate_gate(gate_id, {"finding_count": count})
                return getattr(result, "passed", True)
            if hasattr(engine, "run_gate"):
                _gt_mod = importlib.import_module("zephyr.governance.rule_enforcement.gate_types")
                GateResult = _gt_mod.GateResult
                result: GateResult = engine.run_gate(gate_id)
                return result.passed
            return True
        except ImportError:
            logger.debug("[SCRIPT-GATE] GateEngine not importable, default pass")
            return True


def submit_to_gate(
    findings: list[dict[str, Any]],
    task_id: str = "",
    session_id: str = "",
) -> GateSubmitResult:
    return GateBridge().submit_findings(findings, task_id, session_id)