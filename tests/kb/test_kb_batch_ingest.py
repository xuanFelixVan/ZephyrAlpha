# [A_test] module_id: SRC-TST-1159 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_batch_ingest
# [INVARIANTS] BatchIngestor must process candidates and return BatchIngestReport
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

from zephyr.gov_kb.batch_ingest import BatchIngestEntry, BatchIngestor, BatchIngestReport
from zephyr.gov_kb.ingest import IngestResult


def _mock_ingest_gate(passed: bool = True) -> MagicMock:
    gate = MagicMock()
    if passed:
        gate.ingest.return_value = IngestResult(passed=True, ke_id="KE-001")
    else:
        gate.ingest.return_value = IngestResult(passed=False, violations=["some violation"])
    return gate


class TestBatchIngestEntry:
    def test_default_values(self):
        e = BatchIngestEntry(ke_id="KE-001", title="Test", category="general", source_file="test.md")
        assert e.priority == "P2"
        assert e.status == "pending"
        assert e.error is None

    def test_custom_values(self):
        e = BatchIngestEntry(
            ke_id="KE-002",
            title="Test2",
            category="adr",
            source_file="a.md",
            priority="P0",
            status="succeeded",
            error="err",
        )
        assert e.priority == "P0"
        assert e.status == "succeeded"
        assert e.error == "err"


class TestBatchIngestReport:
    def test_default_values(self):
        r = BatchIngestReport()
        assert r.total == 0
        assert r.succeeded == 0
        assert r.failed == 0
        assert r.skipped == 0
        assert r.success_rate == 0.0
        assert r.entries == []

    def test_to_markdown(self):
        r = BatchIngestReport(
            total=3,
            succeeded=2,
            failed=1,
            skipped=0,
            success_rate=2 / 3,
            entries=[
                BatchIngestEntry(ke_id="KE-001", title="T1", category="g", source_file="a.md", status="succeeded"),
                BatchIngestEntry(
                    ke_id="KE-002", title="T2", category="g", source_file="b.md", status="failed", error="bad"
                ),
            ],
        )
        md = r.to_markdown()
        assert "批量入库报告" in md
        assert "KE-001" in md
        assert "KE-002" in md


class TestBatchIngestor:
    def test_ingest_from_yaml_nonexistent(self, tmp_path: Path):
        gate = _mock_ingest_gate()
        ingestor = BatchIngestor(ingest_gate=gate, repo_root=tmp_path)
        result = ingestor.ingest_from_yaml(tmp_path / "nonexistent.yaml")
        assert result.failed == 1
        assert result.total == 0

    def test_ingest_from_yaml_invalid_content(self, tmp_path: Path):
        gate = _mock_ingest_gate()
        ingestor = BatchIngestor(ingest_gate=gate, repo_root=tmp_path)
        bad_yaml = tmp_path / "bad.yaml"
        bad_yaml.write_text("{{invalid yaml", encoding="utf-8")
        result = ingestor.ingest_from_yaml(bad_yaml)
        assert result.failed == 1

    def test_ingest_from_yaml_with_candidates(self, tmp_path: Path):
        gate = _mock_ingest_gate(passed=True)
        src = tmp_path / "doc.md"
        src.write_text("---\nmodule_id: KE-001\ntitle: Test\ncategory: g\n---\n\nBody text.\n", encoding="utf-8")
        yaml_path = tmp_path / "candidates.yaml"
        data = {
            "candidates": [
                {"module_id": "KE-001", "title": "Test", "category": "g", "source_file": "doc.md", "priority": "P0"},
            ]
        }
        yaml_path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
        ingestor = BatchIngestor(ingest_gate=gate, repo_root=tmp_path)
        result = ingestor.ingest_from_yaml(yaml_path)
        assert result.total >= 1
        assert result.succeeded >= 1

    def test_ingest_from_list(self, tmp_path: Path):
        gate = _mock_ingest_gate(passed=True)
        src = tmp_path / "doc.md"
        src.write_text("---\nmodule_id: KE-001\ntitle: Test\ncategory: g\n---\n\nBody text.\n", encoding="utf-8")
        ingestor = BatchIngestor(ingest_gate=gate, repo_root=tmp_path)
        result = ingestor.ingest_from_list(
            [
                {"module_id": "KE-001", "title": "Test", "category": "g", "source_file": "doc.md", "priority": "P0"},
            ]
        )
        assert result.total >= 1

    def test_ingest_from_list_skips_empty_ke_id(self, tmp_path: Path):
        gate = _mock_ingest_gate()
        ingestor = BatchIngestor(ingest_gate=gate, repo_root=tmp_path)
        result = ingestor.ingest_from_list(
            [
                {"module_id": "", "title": "No ID", "category": "g", "source_file": ""},
            ]
        )
        assert result.skipped >= 1

    def test_ingest_from_list_skips_missing_source(self, tmp_path: Path):
        gate = _mock_ingest_gate()
        ingestor = BatchIngestor(ingest_gate=gate, repo_root=tmp_path)
        result = ingestor.ingest_from_list(
            [
                {"module_id": "KE-001", "title": "No Source", "category": "g", "source_file": "nonexistent.md"},
            ]
        )
        assert result.skipped >= 1

    def test_ingest_from_list_failure(self, tmp_path: Path):
        gate = _mock_ingest_gate(passed=False)
        src = tmp_path / "doc.md"
        src.write_text("---\nmodule_id: KE-001\ntitle: Test\ncategory: g\n---\n\nBody text.\n", encoding="utf-8")
        ingestor = BatchIngestor(ingest_gate=gate, repo_root=tmp_path)
        result = ingestor.ingest_from_list(
            [
                {"module_id": "KE-001", "title": "Test", "category": "g", "source_file": "doc.md", "priority": "P0"},
            ]
        )
        assert result.failed >= 1

    def test_ingest_from_yaml_list_format(self, tmp_path: Path):
        gate = _mock_ingest_gate(passed=True)
        src = tmp_path / "doc.md"
        src.write_text("---\nmodule_id: KE-001\ntitle: Test\ncategory: g\n---\n\nBody text.\n", encoding="utf-8")
        yaml_path = tmp_path / "list.yaml"
        data = [
            {"module_id": "KE-001", "title": "Test", "category": "g", "source_file": "doc.md", "priority": "P0"},
        ]
        yaml_path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
        ingestor = BatchIngestor(ingest_gate=gate, repo_root=tmp_path)
        result = ingestor.ingest_from_yaml(yaml_path)
        assert result.total >= 1
