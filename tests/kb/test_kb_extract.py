# [A_test] module_id: SRC-TST-1163 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_extract
# [INVARIANTS] ExtractGate.extract must return ExtractResult; extraction routes by category
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

from zephyr.gov_kb.pipeline.extract import (
    BEST_PRACTICES_DIR_NAME,
    EXTRACTION_TEMPLATES,
    LESSONS_DIR_NAME,
    ExtractGate,
    ExtractResult,
)
from zephyr.gov_enforcement.rule_enforcement.gate_types import GateResult, GateViolation


def _mock_gate_engine(passed: bool = True) -> MagicMock:
    engine = MagicMock()
    if passed:
        engine.evaluate.return_value = GateResult(gate_id="G5", task_id="T-1", passed=True, violations=[])
    else:
        engine.evaluate.return_value = GateResult(
            gate_id="G5",
            task_id="T-1",
            passed=False,
            violations=[GateViolation(check_id="C1", check_name="c", severity="P0", message="fail")],
        )
    return engine


def _make_source(category: str = "blueprint", extra_text: str = "", **fm_kwargs: object) -> str:
    fm = {
        "module_id": "KE-001",
        "title": "Test KE",
        "category": category,
        "classification": "KNOWLEDGE_ENTRY",
    }
    fm.update(fm_kwargs)
    fm_yaml = yaml.dump(fm, allow_unicode=True, default_flow_style=False)
    body = (
        "## Design Decisions\n\nWe chose this approach for the architecture.\n\n"
        "## Interfaces\n\nThe interface definition is clear.\n\n"
        "## Constraints\n\nMust follow governance rules.\n\n"
        "## Dependencies\n\nDepends on MOD-INF-001.\n\n"
    )
    if extra_text:
        body += extra_text
    return f"---\n{fm_yaml}---\n\n{body}"


class TestExtractResult:
    def test_default_values(self):
        r = ExtractResult(passed=False)
        assert r.passed is False
        assert r.ke_id is None
        assert r.extract_type == ""
        assert r.target_path is None
        assert r.adr_path is None
        assert r.violations == []
        assert r.details == {}

    def test_passed_result(self):
        r = ExtractResult(passed=True, ke_id="KE-001", extract_type="lesson_learned")
        assert r.passed is True
        assert r.extract_type == "lesson_learned"


class TestExtractGate:
    def test_instantiation_creates_dirs(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = ExtractGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        assert (kb_root / LESSONS_DIR_NAME).is_dir()
        assert (kb_root / BEST_PRACTICES_DIR_NAME).is_dir()

    def test_extract_nonexistent_file(self, tmp_path: Path):
        gate = ExtractGate(kb_root=tmp_path, gate_engine=_mock_gate_engine())
        result = gate.extract(Path("/nonexistent/file.md"))
        assert result.passed is False
        assert any("文件不存在" in v for v in result.violations)

    def test_extract_blueprint_category(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = ExtractGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text(_make_source(category="blueprint"), encoding="utf-8")
        result = gate.extract(src)
        assert result.passed is True
        assert result.extract_type in ("design_decision", "best_practice", "lesson_learned")
        assert result.target_path is not None

    def test_extract_lesson_learned_category(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = ExtractGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text(
            _make_source(
                category="lesson_learned",
                extra_text="This was a lesson learned from a postmortem incident. The root cause was identified.\n",
            ),
            encoding="utf-8",
        )
        result = gate.extract(src)
        assert result.passed is True
        assert result.extract_type == "lesson_learned"
        assert result.target_path is not None
        assert LESSONS_DIR_NAME in str(result.target_path)

    def test_extract_best_practice_category(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = ExtractGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text(_make_source(category="best_practice"), encoding="utf-8")
        result = gate.extract(src)
        assert result.passed is True
        assert result.target_path is not None

    def test_extract_unknown_category_fails(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = ExtractGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text(_make_source(category="nonexistent_category"), encoding="utf-8")
        result = gate.extract(src)
        assert result.passed is False
        assert any("无提取模板匹配" in v for v in result.violations)

    def test_extract_gate_failure(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = ExtractGate(kb_root=kb_root, gate_engine=_mock_gate_engine(passed=False))
        src = tmp_path / "source.md"
        src.write_text(_make_source(category="blueprint"), encoding="utf-8")
        result = gate.extract(src)
        assert result.passed is False
        assert len(result.violations) > 0

    def test_extract_with_adr_dir(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        adr_dir = tmp_path / "adr"
        gate = ExtractGate(kb_root=kb_root, gate_engine=_mock_gate_engine(), adr_dir=adr_dir)
        src = tmp_path / "source.md"
        src.write_text(_make_source(category="blueprint"), encoding="utf-8")
        result = gate.extract(src)
        assert result.passed is True
        if result.extract_type == "design_decision":
            assert result.adr_path is not None
            assert result.adr_path.exists()

    def test_extraction_templates_have_fields(self):
        for name, tmpl in EXTRACTION_TEMPLATES.items():
            assert "fields" in tmpl
            assert len(tmpl["fields"]) > 0
