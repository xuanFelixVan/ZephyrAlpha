# [A_test] module_id: SRC-TST-1157 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_activate
# [INVARIANTS] ActivateGate.activate must return ActivateResult; auto_activate when score >= 9.0 or force
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

import yaml

from zephyr.gov_enforcement.rule_enforcement.gate_types import GateResult, GateViolation
from zephyr.intelligence.model_evaluation.activate import (
    ACTIVE_DIR_NAME,
    FUTURE_DIR_NAME,
    ActivateGate,
    ActivateResult,
)


def _make_frontmatter(**kwargs: object) -> str:
    fm = {
        "module_id": "KE-001",
        "title": "Test KE",
        "category": "general",
        "ai_value_score": 9.5,
        "priority": "P1",
        "classification": "KNOWLEDGE_ENTRY",
    }
    fm.update(kwargs)
    fm_yaml = yaml.dump(fm, allow_unicode=True, default_flow_style=False)
    return f"---\n{fm_yaml}---\n\nSome body content that is long enough to be meaningful.\n"


def _mock_gate_engine(passed: bool = True) -> MagicMock:
    engine = MagicMock()
    if passed:
        engine.evaluate.return_value = GateResult(gate_id="G4", task_id="T-1", passed=True, violations=[])
    else:
        engine.evaluate.return_value = GateResult(
            gate_id="G4",
            task_id="T-1",
            passed=False,
            violations=[GateViolation(check_id="C1", check_name="c", severity="P0", message="fail")],
        )
    return engine


class TestActivateResult:
    def test_default_values(self):
        r = ActivateResult(passed=False)
        assert r.passed is False
        assert r.ke_id is None
        assert r.auto_activated is False
        assert r.target_dir == ""
        assert r.target_path is None
        assert r.proposal is None
        assert r.violations == []
        assert r.details == {}

    def test_passed_result(self):
        r = ActivateResult(passed=True, ke_id="KE-001", auto_activated=True, target_dir=ACTIVE_DIR_NAME)
        assert r.passed is True
        assert r.ke_id == "KE-001"
        assert r.auto_activated is True


class TestActivateGate:
    def test_instantiation_creates_dirs(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = ActivateGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        assert (kb_root / ACTIVE_DIR_NAME).is_dir()
        assert (kb_root / FUTURE_DIR_NAME).is_dir()

    def test_activate_nonexistent_file(self, tmp_path: Path):
        gate = ActivateGate(kb_root=tmp_path, gate_engine=_mock_gate_engine())
        result = gate.activate(Path("/nonexistent/file.md"))
        assert result.passed is False
        assert any("文件不存在" in v for v in result.violations)

    def test_activate_auto_with_high_score(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = ActivateGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text(_make_frontmatter(ai_value_score=9.5), encoding="utf-8")
        result = gate.activate(src)
        assert result.passed is True
        assert result.auto_activated is True
        assert result.target_path is not None
        assert result.target_path.exists()

    def test_activate_force_bypasses_score(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = ActivateGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text(_make_frontmatter(ai_value_score=3.0), encoding="utf-8")
        result = gate.activate(src, force=True)
        assert result.passed is True
        assert result.auto_activated is True

    def test_activate_low_score_returns_proposal(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = ActivateGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text(_make_frontmatter(ai_value_score=5.0), encoding="utf-8")
        result = gate.activate(src)
        assert result.passed is False
        assert result.proposal is not None
        assert "KE-001" in result.proposal

    def test_activate_gate_failure(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = ActivateGate(kb_root=kb_root, gate_engine=_mock_gate_engine(passed=False))
        src = tmp_path / "source.md"
        src.write_text(_make_frontmatter(ai_value_score=9.5), encoding="utf-8")
        result = gate.activate(src)
        assert result.passed is False
        assert len(result.violations) > 0

    def test_activate_p0_goes_to_active_dir(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = ActivateGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text(_make_frontmatter(priority="P0"), encoding="utf-8")
        result = gate.activate(src)
        assert result.passed is True
        assert result.target_dir == ACTIVE_DIR_NAME

    def test_activate_p2_goes_to_future_dir(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = ActivateGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text(
            _make_frontmatter(priority="P2", classification="FUTURE_CAPABILITY"),
            encoding="utf-8",
        )
        result = gate.activate(src)
        assert result.passed is True
        assert result.target_dir == FUTURE_DIR_NAME

    def test_activate_with_missing_dependencies(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = ActivateGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text(
            _make_frontmatter(ai_value_score=9.5, depends_on=["KE-999"]),
            encoding="utf-8",
        )
        result = gate.activate(src)
        assert result.passed is False
        assert any("依赖未就绪" in v for v in result.violations)

    def test_activate_invalid_target_path(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = ActivateGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text(
            _make_frontmatter(ai_value_score=9.5, target_path="invalid/path.md"),
            encoding="utf-8",
        )
        result = gate.activate(src)
        assert result.passed is False
        assert any("目标路径不符合规范" in v for v in result.violations)

    def test_activate_no_frontmatter(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = ActivateGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text("Just some content without frontmatter at all\n" * 10, encoding="utf-8")
        result = gate.activate(src, force=True)
        assert result.passed is True
