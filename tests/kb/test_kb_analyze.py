# [A_test] module_id: SRC-TST-1158 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_analyze
# [INVARIANTS] AnalyzeGate.analyze must return AnalyzeResult; score >= 7.0 passes
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from zephyr.gov_kb.pipeline.analyze import (
    SCORING_DIMENSIONS,
    VALUE_SCORE_THRESHOLD,
    AnalyzeGate,
    AnalyzeResult,
)
from zephyr.governance.rule_enforcement.gate_types import GateResult, GateViolation


def _high_score_text() -> str:
    return (
        "---\n"
        "module_id: KE-100\n"
        "title: Architecture Decision\n"
        "category: general\n"
        "layer: L1\n"
        "depends_on:\n"
        "  - MOD-INF-001\n"
        "---\n\n"
        "# Architecture Decision Record\n\n"
        "This document describes the  design decision for ChromaDB persistent client. "
        "We chose ChromaDB because of trade-off analysis. The rationale for this design decision "
        "is that we need a reusable cross-layer shared component. This is critical and irreplaceable. "
        "The interface definition includes function signatures with parameter configuration. "
        "The data flow uses ```python code blocks and ```yaml configuration. "
        "This is a unique core module that is irreplaceable for the system. "
        "We made a design decision to adopt this approach. 选择 ChromaDB 因为权衡了性能与一致性。"
        "不采用 Redis 因为原因是不支持向量搜索。 "
        "This is a critical and unique component that is irreplaceable. "
        "The reuse potential is high as a cross-layer shared utility. "
        "This cross-module component provides shared functionality. "
        "```python\ndef process_data(params):\n    return result\n```\n"
        "```yaml\nconfig:\n  key: value\n```\n"
        "The class DataProcessor handles the core logic. "
        "This is a unique, irreplaceable, critical design decision with high reuse potential.\n"
    )


def _low_score_text() -> str:
    return "---\nmodule_id: KE-101\ntitle: Simple Note\ncategory: general\n---\n\nHello world.\n"


def _mock_gate_engine(passed: bool = True) -> MagicMock:
    engine = MagicMock()
    if passed:
        engine.evaluate.return_value = GateResult(gate_id="G3", task_id="T-1", passed=True, violations=[])
    else:
        engine.evaluate.return_value = GateResult(
            gate_id="G3",
            task_id="T-1",
            passed=False,
            violations=[GateViolation(check_id="C1", check_name="c", severity="P0", message="fail")],
        )
    return engine


class TestAnalyzeResult:
    def test_default_values(self):
        r = AnalyzeResult(passed=False)
        assert r.passed is False
        assert r.ke_id is None
        assert r.ai_value_score == 0.0
        assert r.activation_conditions == []
        assert r.implementation_complexity == "medium"
        assert r.target_path is None
        assert r.violations == []
        assert r.details == {}

    def test_passed_result(self):
        r = AnalyzeResult(passed=True, ai_value_score=8.5, implementation_complexity="high")
        assert r.passed is True
        assert r.ai_value_score == 8.5
        assert r.implementation_complexity == "high"


class TestAnalyzeGate:
    def test_instantiation_creates_analyzed_dir(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = AnalyzeGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        assert (kb_root / "03_analyzed").is_dir()

    def test_analyze_nonexistent_file(self, tmp_path: Path):
        gate = AnalyzeGate(kb_root=tmp_path, gate_engine=_mock_gate_engine())
        result = gate.analyze(Path("/nonexistent/file.md"))
        assert result.passed is False
        assert any("文件不存在" in v for v in result.violations)

    def test_analyze_high_score_passes(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = AnalyzeGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text(_high_score_text(), encoding="utf-8")
        result = gate.analyze(src)
        assert result.ai_value_score >= VALUE_SCORE_THRESHOLD
        assert result.passed is True
        assert result.target_path is not None

    def test_analyze_low_score_fails(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = AnalyzeGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text(_low_score_text(), encoding="utf-8")
        result = gate.analyze(src)
        assert result.passed is False
        assert result.ai_value_score < VALUE_SCORE_THRESHOLD

    def test_analyze_gate_failure(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = AnalyzeGate(kb_root=kb_root, gate_engine=_mock_gate_engine(passed=False))
        src = tmp_path / "source.md"
        src.write_text(_high_score_text(), encoding="utf-8")
        result = gate.analyze(src)
        assert result.passed is False
        assert len(result.violations) > 0

    def test_analyze_activation_conditions_derived(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = AnalyzeGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text(_high_score_text(), encoding="utf-8")
        result = gate.analyze(src)
        assert len(result.activation_conditions) > 0

    def test_analyze_complexity_assessment(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = AnalyzeGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text(_high_score_text(), encoding="utf-8")
        result = gate.analyze(src)
        assert result.implementation_complexity in ("low", "medium", "high")

    def test_analyze_no_frontmatter(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = AnalyzeGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text("Just content without frontmatter\n" * 20, encoding="utf-8")
        result = gate.analyze(src)
        assert isinstance(result, AnalyzeResult)

    def test_scoring_dimensions_weights_sum_to_one(self):
        total = sum(SCORING_DIMENSIONS.values())
        assert abs(total - 1.0) < 1e-9
