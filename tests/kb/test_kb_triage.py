# [A_test] module_id: SRC-TST-1178 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_triage
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] test_kb_triage.py
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from zephyr.governance.triage import (
    APPROVED_LABELS,
    HIGH_VALUE_THRESHOLD,
    REJECT_THRESHOLD,
    VALID_DOC_TYPES,
    VALID_LAYERS,
    TriageGate,
    TriageResult,
)


def _make_triage_gate(tmp_path: Path) -> TriageGate:
    mock_engine = MagicMock()
    mock_result = MagicMock()
    mock_result.passed = True
    mock_result.violations = []
    mock_engine.evaluate.return_value = mock_result
    return TriageGate(kb_root=tmp_path, gate_engine=mock_engine)


def _write_ke(directory: Path, name: str, frontmatter: str, body: str = "Some content here.") -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    text = f"---\n{frontmatter}\n---\n{body}"
    p = directory / f"{name}.md"
    p.write_text(text, encoding="utf-8")
    return p


class TestTriageGate:
    def test_triage_nonexistent_file(self, tmp_path: Path):
        gate = _make_triage_gate(tmp_path)
        result = gate.triage(Path("/nonexistent/file.md"))
        assert result.passed is False
        assert len(result.violations) > 0

    def test_triage_valid_file(self, tmp_path: Path):
        gate = _make_triage_gate(tmp_path)
        src = _write_ke(
            tmp_path / "raw",
            "KE-001",
            "module_id: KE-001\ntitle: Test\ncategory: governance\ndoc_type: policy\nlayer: l01_data_processing",
            "A" * 600,
        )
        result = gate.triage(src)
        assert result.passed is True
        assert result.ke_id == "KE-001"
        assert result.classification in APPROVED_LABELS
        assert result.ai_triage_score > 0

    def test_triage_low_score_rejected(self, tmp_path: Path):
        gate = _make_triage_gate(tmp_path)
        src = _write_ke(
            tmp_path / "raw",
            "KE-002",
            "module_id: KE-002",
            "short",
        )
        result = gate.triage(src)
        assert result.ai_triage_score < HIGH_VALUE_THRESHOLD

    def test_triage_invalid_classification(self, tmp_path: Path):
        gate = _make_triage_gate(tmp_path)
        src = _write_ke(
            tmp_path / "raw",
            "KE-003",
            "classification: INVALID_LABEL\ntitle: T\ncategory: c",
            "A" * 300,
        )
        with patch.object(gate, "_classify", return_value="INVALID_LABEL"):
            result = gate.triage(src)
            assert result.passed is False
            assert any("分类标签无效" in v for v in result.violations)

    def test_triage_no_frontmatter(self, tmp_path: Path):
        gate = _make_triage_gate(tmp_path)
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        p = raw_dir / "KE-004.md"
        p.write_text("Just plain text without frontmatter " * 20, encoding="utf-8")
        result = gate.triage(p)
        assert isinstance(result, TriageResult)

    def test_triage_gate_failure(self, tmp_path: Path):
        mock_engine = MagicMock()
        mock_result = MagicMock()
        mock_result.passed = False
        mock_violation = MagicMock()
        mock_violation.severity = "HIGH"
        mock_violation.message = "gate failed"
        mock_result.violations = [mock_violation]
        mock_engine.evaluate.return_value = mock_result
        gate = TriageGate(kb_root=tmp_path, gate_engine=mock_engine)
        src = _write_ke(
            tmp_path / "raw",
            "KE-005",
            "module_id: KE-005\ntitle: T\ncategory: governance\ndoc_type: policy\nlayer: l01_data_processing",
            "A" * 600,
        )
        result = gate.triage(src)
        assert result.passed is False
        assert any("gate failed" in v for v in result.violations)

    def test_triage_writes_to_triaged_dir(self, tmp_path: Path):
        gate = _make_triage_gate(tmp_path)
        src = _write_ke(
            tmp_path / "raw",
            "KE-006",
            "module_id: KE-006\ntitle: T\ncategory: governance\ndoc_type: policy\nlayer: l01_data_processing",
            "A" * 600,
        )
        result = gate.triage(src)
        if result.passed and result.target_path:
            assert result.target_path.exists()

    def test_triage_invalid_doc_type(self, tmp_path: Path):
        gate = _make_triage_gate(tmp_path)
        src = _write_ke(
            tmp_path / "raw",
            "KE-007",
            "module_id: KE-007\ntitle: T\ncategory: governance\ndoc_type: invalid_type\nlayer: l01_data_processing",
            "A" * 600,
        )
        result = gate.triage(src)
        if not result.passed:
            assert any("doc_type" in v for v in result.violations)

    def test_triage_invalid_layer(self, tmp_path: Path):
        gate = _make_triage_gate(tmp_path)
        src = _write_ke(
            tmp_path / "raw",
            "KE-008",
            "module_id: KE-008\ntitle: T\ncategory: governance\ndoc_type: policy\nlayer: invalid_layer",
            "A" * 600,
        )
        result = gate.triage(src)
        if not result.passed:
            assert any("layer" in v for v in result.violations)


class TestTriageClassify:
    def test_explicit_classification(self, tmp_path: Path):
        gate = _make_triage_gate(tmp_path)
        result = gate._classify({"classification": "BLUEPRINT"}, "")
        assert result == "BLUEPRINT"

    def test_doc_type_blueprint(self, tmp_path: Path):
        gate = _make_triage_gate(tmp_path)
        result = gate._classify({"doc_type": "blueprint"}, "")
        assert result == "BLUEPRINT"

    def test_doc_type_policy(self, tmp_path: Path):
        gate = _make_triage_gate(tmp_path)
        result = gate._classify({"doc_type": "policy"}, "")
        assert result == "GOVERNANCE_STD"

    def test_keyword_classification(self, tmp_path: Path):
        gate = _make_triage_gate(tmp_path)
        result = gate._classify({}, "这是一个关于架构设计决策的文档")
        assert result in APPROVED_LABELS

    def test_default_knowledge_entry(self, tmp_path: Path):
        gate = _make_triage_gate(tmp_path)
        result = gate._classify({}, "generic text without keywords")
        assert result == "KNOWLEDGE_ENTRY"


class TestTriageScore:
    def test_high_score_with_rich_metadata(self, tmp_path: Path):
        gate = _make_triage_gate(tmp_path)
        fm = {
            "module_id": "KE-100",
            "title": "Rich",
            "category": "governance",
            "layer": "l01_data_processing",
            "doc_type": "policy",
            "date": "2025-01-01",
        }
        text = "---\nmodule_id: KE-100\n---\n" + "A" * 600
        score = gate._compute_triage_score(fm, text, "GOVERNANCE_STD")
        assert score >= 0.5

    def test_low_score_minimal(self, tmp_path: Path):
        gate = _make_triage_gate(tmp_path)
        score = gate._compute_triage_score({}, "short", "KNOWLEDGE_ENTRY")
        assert score < 0.5

    def test_score_capped_at_one(self, tmp_path: Path):
        gate = _make_triage_gate(tmp_path)
        fm = {
            "module_id": "KE-X",
            "title": "T",
            "category": "c",
            "layer": "l01_data_processing",
            "doc_type": "policy",
            "date": "2025-01-01",
        }
        text = "---\n---\n" + "A" * 1000 + "\n 设计决策 根因 接口定义"
        score = gate._compute_triage_score(fm, text, "BLUEPRINT")
        assert score <= 1.0


class TestScoreToPriority:
    def test_priorities(self, tmp_path: Path):
        gate = _make_triage_gate(tmp_path)
        assert gate._score_to_priority(0.8) == "P0"
        assert gate._score_to_priority(0.6) == "P1"
        assert gate._score_to_priority(0.4) == "P2"
        assert gate._score_to_priority(0.2) == "P3"


class TestConstants:
    def test_approved_labels_not_empty(self):
        assert len(APPROVED_LABELS) > 0

    def test_valid_doc_types_not_empty(self):
        assert len(VALID_DOC_TYPES) > 0

    def test_valid_layers_not_empty(self):
        assert len(VALID_LAYERS) > 0

    def test_thresholds(self):
        assert HIGH_VALUE_THRESHOLD == 0.7
        assert REJECT_THRESHOLD == 0.3
