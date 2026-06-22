# [A_test] module_id: SRC-TST-1167 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain-knowledge/knowledge-base/blueprint.md | §
# [MODULE] tests.test_kb_graph_validator
# [INVARIANTS] GraphValidator.validate returns ValidationReport; check_near_duplicate is standalone
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file

from __future__ import annotations

import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

from zephyr.governance.kb.graph_validator import (
    GraphValidator,
    ValidationIssue,
    ValidationReport,
    ValidationSeverity,
    _normalize,
)


def _create_test_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute(
        "CREATE TABLE IF NOT EXISTS knowledge ("
        "ke_id TEXT PRIMARY KEY, title TEXT, category TEXT, source_file TEXT, "
        "fingerprint_sha256 TEXT, status TEXT, created_at TEXT, updated_at TEXT)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS events ("
        "event_id TEXT PRIMARY KEY, event_type TEXT, ke_id TEXT, "
        "payload TEXT, created_at TEXT)"
    )
    conn.commit()
    conn.close()
    return db_path


def _insert_ke(
    db_path: Path,
    ke_id: str,
    title: str = "Test",
    category: str = "general",
    source_file: str = "test.md",
    fingerprint: str | None = None,
    status: str = "INDEXED",
) -> None:
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT OR REPLACE INTO knowledge (ke_id, title, category, source_file, fingerprint_sha256, status, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, '2026-01-01T00:00:00', '2026-01-01T00:00:00')",
        (ke_id, title, category, source_file, fingerprint, status),
    )
    conn.commit()
    conn.close()


def _make_validator(db_path: Path) -> GraphValidator:
    with patch("zephyr.data.vector_storage.kb.graph_validator.GraphValidator.__init__", lambda self, **kw: None):
        validator = GraphValidator.__new__(GraphValidator)
        validator._conn = sqlite3.connect(str(db_path))
        validator._conn.row_factory = sqlite3.Row
        validator._vector_dir = None
    return validator


def _mock_chromadb_no_collections():
    mock_client = MagicMock()
    mock_client.list_collections.return_value = []
    return mock_client


class TestValidationSeverity:
    def test_enum_values(self):
        assert ValidationSeverity.ERROR.value == "ERROR"
        assert ValidationSeverity.WARNING.value == "WARNING"
        assert ValidationSeverity.INFO.value == "INFO"


class TestValidationIssue:
    def test_creation(self):
        issue = ValidationIssue(
            check_id="GV-001",
            severity=ValidationSeverity.WARNING,
            description="Test issue",
            ke_id="KE-001",
        )
        assert issue.check_id == "GV-001"
        assert issue.severity == ValidationSeverity.WARNING
        assert issue.description == "Test issue"
        assert issue.details == {}


class TestValidationReport:
    def test_default_values(self):
        r = ValidationReport()
        assert r.total_checked == 0
        assert r.error_count == 0
        assert r.warning_count == 0
        assert r.info_count == 0
        assert r.issues == []
        assert r.passed is True

    def test_with_errors(self):
        r = ValidationReport(
            error_count=1,
            issues=[ValidationIssue(check_id="GV-001", severity=ValidationSeverity.ERROR, description="err")],
            passed=False,
        )
        assert r.passed is False


class TestNormalize:
    def test_basic(self):
        assert _normalize("Hello World") == "hello world"

    def test_punctuation_removed(self):
        result = _normalize("Hello, World! Test.")
        assert "," not in result
        assert "!" not in result

    def test_whitespace_normalized(self):
        result = _normalize("Hello   World")
        assert "  " not in result


class TestGraphValidator:
    def test_validate_empty_db(self, tmp_path: Path):
        db_path = _create_test_db(tmp_path)
        with patch("zephyr.knowledge.kb.chromadb_init.get_chroma_client", return_value=_mock_chromadb_no_collections()):
            validator = _make_validator(db_path)
            report = validator.validate()
        assert isinstance(report, ValidationReport)
        assert report.total_checked == 0
        assert report.passed is True

    def test_validate_with_records(self, tmp_path: Path):
        db_path = _create_test_db(tmp_path)
        _insert_ke(db_path, "KE-001", status="INDEXED")
        _insert_ke(db_path, "KE-002", status="VERIFIED")
        with patch("zephyr.knowledge.kb.chromadb_init.get_chroma_client", return_value=_mock_chromadb_no_collections()):
            validator = _make_validator(db_path)
            report = validator.validate()
        assert report.total_checked == 2

    def test_check_near_duplicate_identical_files(self, tmp_path: Path):
        file_a = tmp_path / "a.md"
        file_b = tmp_path / "b.md"
        content = "This is identical content for testing near duplicate detection in the graph validator module."
        file_a.write_text(content, encoding="utf-8")
        file_b.write_text(content, encoding="utf-8")
        db_path = _create_test_db(tmp_path)
        with patch("zephyr.knowledge.kb.chromadb_init.get_chroma_client", return_value=_mock_chromadb_no_collections()):
            validator = _make_validator(db_path)
            result = validator.check_near_duplicate(str(file_a), str(file_b))
        assert result["is_duplicate"] is True
        assert result["similarity"] >= 0.95

    def test_check_near_duplicate_different_files(self, tmp_path: Path):
        file_a = tmp_path / "a.md"
        file_b = tmp_path / "b.md"
        file_a.write_text("Completely different content about apples and oranges and bananas.", encoding="utf-8")
        file_b.write_text(
            "Totally unrelated text about quantum physics and mathematics and algorithms.", encoding="utf-8"
        )
        db_path = _create_test_db(tmp_path)
        with patch("zephyr.knowledge.kb.chromadb_init.get_chroma_client", return_value=_mock_chromadb_no_collections()):
            validator = _make_validator(db_path)
            result = validator.check_near_duplicate(str(file_a), str(file_b))
        assert result["is_duplicate"] is False

    def test_check_near_duplicate_empty_file(self, tmp_path: Path):
        file_a = tmp_path / "a.md"
        file_b = tmp_path / "b.md"
        file_a.write_text("", encoding="utf-8")
        file_b.write_text("Some content here.", encoding="utf-8")
        db_path = _create_test_db(tmp_path)
        with patch("zephyr.knowledge.kb.chromadb_init.get_chroma_client", return_value=_mock_chromadb_no_collections()):
            validator = _make_validator(db_path)
            result = validator.check_near_duplicate(str(file_a), str(file_b))
        assert result["is_duplicate"] is False
        assert result["similarity"] == 0.0

    def test_duplicate_fingerprints_detected(self, tmp_path: Path):
        db_path = _create_test_db(tmp_path)
        fp = "a" * 64
        _insert_ke(db_path, "KE-001", fingerprint=fp, status="INDEXED")
        _insert_ke(db_path, "KE-002", fingerprint=fp, status="INDEXED")
        with patch("zephyr.knowledge.kb.chromadb_init.get_chroma_client", return_value=_mock_chromadb_no_collections()):
            validator = _make_validator(db_path)
            report = validator.validate()
        dup_issues = [i for i in report.issues if i.check_id == "GV-005"]
        assert len(dup_issues) >= 1
