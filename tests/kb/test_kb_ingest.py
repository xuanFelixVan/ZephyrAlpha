# [A_test] module_id: SRC-TST-1168 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_ingest
# [INVARIANTS] IngestGate.ingest must return IngestResult; validates format/frontmatter/encoding/injection
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

from zephyr.gov_kb.ingest import (
    ALLOWED_EXTENSIONS,
    BLACKLIST_PATTERNS,
    MIN_CONTENT_CHARS,
    REQUIRED_FRONTMATTER_FIELDS,
    IngestGate,
    IngestResult,
)
from zephyr.gov_enforcement.rule_enforcement.gate_types import GateResult, GateViolation


def _mock_gate_engine(passed: bool = True) -> MagicMock:
    engine = MagicMock()
    if passed:
        engine.evaluate.return_value = GateResult(gate_id="G1", task_id="T-1", passed=True, violations=[])
    else:
        engine.evaluate.return_value = GateResult(
            gate_id="G1",
            task_id="T-1",
            passed=False,
            violations=[GateViolation(check_id="C1", check_name="c", severity="P0", message="fail")],
        )
    return engine


def _valid_markdown(**fm_overrides: object) -> str:
    fm = {
        "module_id": "KE-001",
        "title": "Test Knowledge Entry",
        "category": "general",
        "ttl": "permanent",
    }
    fm.update(fm_overrides)
    fm_yaml = yaml.dump(fm, allow_unicode=True, default_flow_style=False)
    body = "This is a valid knowledge entry body content that is long enough to pass the minimum character threshold requirement for the ingest gate validation process."
    return f"---\n{fm_yaml}---\n\n{body}\n"


class TestIngestResult:
    def test_default_values(self):
        r = IngestResult(passed=False)
        assert r.passed is False
        assert r.ke_id is None
        assert r.target_path is None
        assert r.violations == []
        assert r.details == {}

    def test_passed_result(self):
        r = IngestResult(passed=True, ke_id="KE-001")
        assert r.passed is True
        assert r.ke_id == "KE-001"


class TestConstants:
    def test_required_fields(self):
        assert "module_id" in REQUIRED_FRONTMATTER_FIELDS
        assert "title" in REQUIRED_FRONTMATTER_FIELDS
        assert "category" in REQUIRED_FRONTMATTER_FIELDS

    def test_allowed_extensions(self):
        assert ".md" in ALLOWED_EXTENSIONS
        assert ".yaml" in ALLOWED_EXTENSIONS
        assert ".yml" in ALLOWED_EXTENSIONS
        assert ".txt" not in ALLOWED_EXTENSIONS

    def test_blacklist_patterns(self):
        assert len(BLACKLIST_PATTERNS) > 0

    def test_min_content_chars(self):
        assert MIN_CONTENT_CHARS == 100


class TestIngestGate:
    def test_instantiation_creates_raw_intake_dir(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = IngestGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        assert (kb_root / "01_raw_intake").is_dir()

    def test_ingest_nonexistent_file(self, tmp_path: Path):
        gate = IngestGate(kb_root=tmp_path, gate_engine=_mock_gate_engine())
        result = gate.ingest(Path("/nonexistent/file.md"))
        assert result.passed is False
        assert any("文件不存在" in v for v in result.violations)

    def test_ingest_disallowed_extension(self, tmp_path: Path):
        gate = IngestGate(kb_root=tmp_path, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.txt"
        src.write_text("content", encoding="utf-8")
        result = gate.ingest(src)
        assert result.passed is False
        assert any("不允许的文件扩展名" in v for v in result.violations)

    def test_ingest_valid_markdown(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = IngestGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text(_valid_markdown(), encoding="utf-8")
        result = gate.ingest(src)
        assert result.passed is True
        assert result.ke_id == "KE-001"
        assert result.target_path is not None
        assert result.target_path.exists()

    def test_ingest_missing_frontmatter(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = IngestGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text("No frontmatter here, just plain text content that is long enough.\n" * 5, encoding="utf-8")
        result = gate.ingest(src)
        assert result.passed is False
        assert any("frontmatter" in v.lower() for v in result.violations)

    def test_ingest_missing_required_fields(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = IngestGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text(
            "---\nmodule_id: KE-001\n---\n\nBody content that is long enough to pass the minimum character threshold.\n",
            encoding="utf-8",
        )
        result = gate.ingest(src)
        assert result.passed is False
        assert any("缺少必填字段" in v for v in result.violations)

    def test_ingest_content_too_short(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = IngestGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text(
            "---\nmodule_id: KE-001\ntitle: Short\ncategory: g\nttl: permanent\n---\n\nShort.\n",
            encoding="utf-8",
        )
        result = gate.ingest(src)
        assert result.passed is False
        assert any("内容过短" in v for v in result.violations)

    def test_ingest_injection_detected(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = IngestGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text(
            _valid_markdown() + "\n{{template_injection}}\n",
            encoding="utf-8",
        )
        result = gate.ingest(src)
        assert result.passed is False
        assert any("黑名单模式" in v for v in result.violations)

    def test_ingest_bom_detected(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = IngestGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        content = _valid_markdown()
        src.write_bytes(b"\xef\xbb\xbf" + content.encode("utf-8"))
        result = gate.ingest(src)
        assert result.passed is False
        assert any("BOM" in v for v in result.violations)

    def test_ingest_gate_failure(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = IngestGate(kb_root=kb_root, gate_engine=_mock_gate_engine(passed=False))
        src = tmp_path / "source.md"
        src.write_text(_valid_markdown(), encoding="utf-8")
        result = gate.ingest(src)
        assert result.passed is False
        assert len(result.violations) > 0

    def test_ingest_yaml_file(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = IngestGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.yaml"
        data = {
            "module_id": "KE-002",
            "title": "YAML Entry",
            "category": "general",
            "ttl": "permanent",
        }
        body = "This is the content of a YAML knowledge entry that is long enough to pass validation."
        data["content"] = body
        src.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
        result = gate.ingest(src)
        assert result.ke_id == "KE-002"

    def test_ingest_with_content_parameter(self, tmp_path: Path):
        kb_root = tmp_path / "kb"
        gate = IngestGate(kb_root=kb_root, gate_engine=_mock_gate_engine())
        src = tmp_path / "source.md"
        src.write_text("placeholder", encoding="utf-8")
        content = _valid_markdown()
        result = gate.ingest(src, content=content)
        assert result.passed is True
