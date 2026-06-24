# [A_test] module_id: SRC-TST-1172 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_pipeline_activate
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from zephyr.intelligence.model_evaluation.activate import (
    ACTIVE_DIR_NAME,
    AUTO_ACTIVATE_THRESHOLD,
    FUTURE_DIR_NAME,
    ActivateGate,
    ActivateResult,
)


def _make_ke_file(
    tmp_path: Path,
    module_id: str = "KE-001",
    ai_value_score: float = 9.5,
    priority: str = "P0",
    classification: str = "KNOWLEDGE_ENTRY",
    depends_on: list | None = None,
    target_path: str = "",
) -> Path:
    fm_lines = [
        "---",
        f"module_id: {module_id}",
        f"ai_value_score: {ai_value_score}",
        f"priority: {priority}",
        f"classification: {classification}",
    ]
    if depends_on is not None:
        fm_lines.append(f"depends_on: {depends_on}")
    if target_path:
        fm_lines.append(f"target_path: {target_path}")
    fm_lines.append("---")
    fm_lines.append("Body content of the knowledge entry.")
    content = "\n".join(fm_lines)
    p = tmp_path / "source" / f"{module_id}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


class TestActivateResult:
    def test_create_passed(self):
        ar = ActivateResult(passed=True, ke_id="KE-001", auto_activated=True)
        assert ar.passed is True
        assert ar.auto_activated is True

    def test_create_failed(self):
        ar = ActivateResult(passed=False, violations=["error"])
        assert ar.passed is False
        assert len(ar.violations) == 1

    def test_default_values(self):
        ar = ActivateResult(passed=False)
        assert ar.ke_id is None
        assert ar.auto_activated is False
        assert ar.target_dir == ""
        assert ar.target_path is None
        assert ar.proposal is None
        assert ar.violations == []
        assert ar.details == {}


class TestActivateGate:
    def test_init_creates_dirs(self, tmp_path):
        gate = ActivateGate(kb_root=tmp_path)
        assert (tmp_path / ACTIVE_DIR_NAME).exists()
        assert (tmp_path / FUTURE_DIR_NAME).exists()

    def test_activate_nonexistent_file(self, tmp_path):
        gate = ActivateGate(kb_root=tmp_path)
        result = gate.activate(source_path=tmp_path / "nonexistent.md")
        assert result.passed is False
        assert len(result.violations) > 0

    def test_activate_high_score_auto(self, tmp_path):
        gate = ActivateGate(kb_root=tmp_path, gate_engine=MagicMock(), kb_repo=None)
        source = _make_ke_file(tmp_path, ai_value_score=9.5)
        result = gate.activate(source_path=source)
        assert result.passed is True
        assert result.auto_activated is True
        assert result.ke_id == "KE-001"

    def test_activate_low_score_needs_approval(self, tmp_path):
        gate = ActivateGate(kb_root=tmp_path, gate_engine=MagicMock(), kb_repo=None)
        source = _make_ke_file(tmp_path, ai_value_score=5.0)
        result = gate.activate(source_path=source)
        assert result.passed is False
        assert result.auto_activated is False
        assert result.proposal is not None

    def test_activate_force_bypasses_score(self, tmp_path):
        gate = ActivateGate(kb_root=tmp_path, gate_engine=MagicMock(), kb_repo=None)
        source = _make_ke_file(tmp_path, ai_value_score=1.0)
        result = gate.activate(source_path=source, force=True)
        assert result.passed is True
        assert result.auto_activated is True

    def test_activate_target_path_invalid(self, tmp_path):
        gate = ActivateGate(kb_root=tmp_path, gate_engine=MagicMock(), kb_repo=None)
        source = _make_ke_file(tmp_path, ai_value_score=9.5, target_path="invalid/path.md")
        result = gate.activate(source_path=source)
        assert result.passed is False
        assert any("目标路径不符合规范" in v for v in result.violations)

    def test_activate_target_path_valid(self, tmp_path):
        gate = ActivateGate(kb_root=tmp_path, gate_engine=MagicMock(), kb_repo=None)
        source = _make_ke_file(tmp_path, ai_value_score=9.5, target_path="docs/08_knowledge/some-module/ke-001-test.md")
        result = gate.activate(source_path=source)
        assert result.passed is True

    def test_activate_writes_to_active_dir_for_p0(self, tmp_path):
        gate = ActivateGate(kb_root=tmp_path, gate_engine=MagicMock(), kb_repo=None)
        source = _make_ke_file(tmp_path, priority="P0")
        result = gate.activate(source_path=source)
        assert result.passed is True
        assert result.target_dir == ACTIVE_DIR_NAME
        assert result.target_path is not None
        assert result.target_path.exists()

    def test_activate_writes_to_future_dir_for_low_priority(self, tmp_path):
        gate = ActivateGate(kb_root=tmp_path, gate_engine=MagicMock(), kb_repo=None)
        source = _make_ke_file(tmp_path, priority="P3", classification="GENERAL")
        result = gate.activate(source_path=source)
        assert result.passed is True
        assert result.target_dir == FUTURE_DIR_NAME

    def test_activate_no_frontmatter(self, tmp_path):
        gate = ActivateGate(kb_root=tmp_path, gate_engine=MagicMock(), kb_repo=None)
        source = tmp_path / "source" / "no_fm.md"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("Just plain text without frontmatter.", encoding="utf-8")
        result = gate.activate(source_path=source)
        assert result.auto_activated is False

    def test_activate_unreadable_file(self, tmp_path):
        gate = ActivateGate(kb_root=tmp_path)
        source = tmp_path / "source" / "unreadable.md"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("content", encoding="utf-8")
        source.chmod(0o000)
        try:
            result = gate.activate(source_path=source)
            assert result.passed is False
        finally:
            source.chmod(0o644)

    def test_auto_activate_threshold_constant(self):
        assert AUTO_ACTIVATE_THRESHOLD == 9.0


class TestActivateGateDependencies:
    def test_missing_dependencies_blocks(self, tmp_path):
        mock_repo = MagicMock()
        mock_repo.get.return_value = None
        gate = ActivateGate(kb_root=tmp_path, gate_engine=MagicMock(), kb_repo=mock_repo)
        source = _make_ke_file(tmp_path, ai_value_score=9.5, depends_on=["KE-999"])
        result = gate.activate(source_path=source)
        assert result.passed is False
        assert any("依赖未就绪" in v for v in result.violations)

    def test_missing_dependencies_force_bypasses(self, tmp_path):
        mock_repo = MagicMock()
        mock_repo.get.return_value = None
        gate = ActivateGate(kb_root=tmp_path, gate_engine=MagicMock(), kb_repo=mock_repo)
        source = _make_ke_file(tmp_path, ai_value_score=9.5, depends_on=["KE-999"])
        result = gate.activate(source_path=source, force=True)
        assert result.passed is True
