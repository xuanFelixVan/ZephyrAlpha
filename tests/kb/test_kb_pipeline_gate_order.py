# [A_test] module_id: SRC-TST-0170 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-327 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.integration.test_kb_pipeline_gate_order
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""KB 知识流水线：五阶段各调用 GateEngine.evaluate 的预期 gate_id（Mock 引擎）。"""

from __future__ import annotations

from pathlib import Path

from zephyr.gov_kb.ingest import IngestGate
from zephyr.gov_kb.pipeline.analyze import AnalyzeGate
from zephyr.gov_kb.pipeline.extract import ExtractGate
from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_engine import GateResult
from zephyr.governance.escalation.triage import TriageGate
from zephyr.intelligence.model_evaluation.activate import ActivateGate


class _RecordingGateBackend:
    """duck-type GateEngine：仅实现 evaluate，记录 gate_id 调用序。"""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def evaluate(self, task: object, gate_id: str) -> GateResult:
        self.calls.append(gate_id)
        tid = getattr(task, "task_id", "unknown")
        return GateResult(gate_id=gate_id, task_id=str(tid), passed=True, violations=[], details={})


def test_kb_five_stages_run_gate_evaluates_g1_through_g5_in_order(tmp_path: Path) -> None:
    rec = _RecordingGateBackend()
    sample = tmp_path / "sample.md"
    sample.write_text("x" * 200 + "\n", encoding="utf-8")

    IngestGate(tmp_path, gate_engine=rec)._run_gate(sample)
    TriageGate(tmp_path, gate_engine=rec)._run_gate(sample)
    AnalyzeGate(tmp_path, gate_engine=rec)._run_gate(sample)
    ActivateGate(tmp_path, gate_engine=rec)._run_gate(sample)
    ExtractGate(tmp_path, gate_engine=rec)._run_gate(sample)

    assert rec.calls == ["G1", "G2", "G3", "G4", "G5"]
