# [A_test] module_id: SRC-TST-0871 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_evidence_pack
# [INVARIANTS] EvidencePackExporter export_json/fca produce valid files
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass; exit non-zero on fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path

from zephyr.gov_audit.evidence_pack import (
    EvidencePackExporter,
    EvidencePackMetadata,
    ExportResult,
)


class TestEvidencePackMetadata:
    def test_default_values(self):
        meta = EvidencePackMetadata()
        assert meta.pack_id == ""
        assert meta.format == ""
        assert meta.entry_count == 0
        assert meta.filters == {}
        assert meta.checksum == ""


class TestExportResult:
    def test_default_values(self):
        result = ExportResult()
        assert result.success is True
        assert result.output_path == ""
        assert result.format == ""
        assert result.entry_count == 0
        assert result.file_size_bytes == 0
        assert result.checksum == ""


class TestEvidencePackExporterInstantiation:
    def test_default_dirs(self, tmp_path):
        data_dir = tmp_path / "audit"
        exporter = EvidencePackExporter(data_dir=data_dir)
        assert exporter._data_dir == data_dir
        assert exporter._output_dir == data_dir / "evidence_packs"

    def test_custom_output_dir(self, tmp_path):
        data_dir = tmp_path / "audit"
        output_dir = tmp_path / "output"
        exporter = EvidencePackExporter(data_dir=data_dir, output_dir=output_dir)
        assert exporter._output_dir == output_dir

    def test_output_dir_created(self, tmp_path):
        data_dir = tmp_path / "audit"
        output_dir = tmp_path / "new_output"
        exporter = EvidencePackExporter(data_dir=data_dir, output_dir=output_dir)
        assert output_dir.exists()


class TestEvidencePackExporterExportJson:
    def test_export_json_basic(self, tmp_path):
        exporter = EvidencePackExporter(data_dir=tmp_path, output_dir=tmp_path / "out")
        events = [
            {"timestamp": "2026-05-22T10:00:00Z", "event_type": "write", "agent_id": "a1"},
            {"timestamp": "2026-05-22T11:00:00Z", "event_type": "read", "agent_id": "a2"},
        ]
        result = exporter.export_json(events, pack_id="TEST-PACK-001")
        assert result.success is True
        assert result.format == "json"
        assert result.entry_count == 2
        assert result.file_size_bytes > 0
        assert result.checksum != ""

    def test_export_json_file_created(self, tmp_path):
        exporter = EvidencePackExporter(data_dir=tmp_path, output_dir=tmp_path / "out")
        events = [{"event_type": "test"}]
        result = exporter.export_json(events, pack_id="FILE-CHECK")
        output_path = Path(result.output_path)
        assert output_path.exists()
        with open(output_path, encoding="utf-8") as f:
            pack = json.load(f)
        assert "metadata" in pack
        assert "events" in pack
        assert pack["metadata"]["pack_id"] == "FILE-CHECK"

    def test_export_json_empty_events(self, tmp_path):
        exporter = EvidencePackExporter(data_dir=tmp_path, output_dir=tmp_path / "out")
        result = exporter.export_json([], pack_id="EMPTY-PACK")
        assert result.success is True
        assert result.entry_count == 0

    def test_export_json_auto_pack_id(self, tmp_path):
        exporter = EvidencePackExporter(data_dir=tmp_path, output_dir=tmp_path / "out")
        result = exporter.export_json([{"event_type": "test"}])
        assert result.output_path != ""
        assert "EVID-" in Path(result.output_path).name

    def test_export_json_with_filters(self, tmp_path):
        exporter = EvidencePackExporter(data_dir=tmp_path, output_dir=tmp_path / "out")
        events = [{"event_type": "test"}]
        result = exporter.export_json(events, pack_id="FILTER-PACK", filters={"agent": "a1"})
        output_path = Path(result.output_path)
        with open(output_path, encoding="utf-8") as f:
            pack = json.load(f)
        assert pack["metadata"]["filters"] == {"agent": "a1"}


class TestEvidencePackExporterExportFca:
    def test_export_fca_basic(self, tmp_path):
        exporter = EvidencePackExporter(data_dir=tmp_path, output_dir=tmp_path / "out")
        events = [
            {"timestamp": "2026-05-22T10:00:00Z", "event_type": "write", "agent_id": "a1", "operation": "create"},
        ]
        result = exporter.export_fca(events, pack_id="FCA-TEST-001", firm_reference="FIRM123")
        assert result.success is True
        assert result.format == "fca"
        assert result.entry_count == 1
        assert result.file_size_bytes > 0

    def test_export_fca_file_structure(self, tmp_path):
        exporter = EvidencePackExporter(data_dir=tmp_path, output_dir=tmp_path / "out")
        events = [
            {"timestamp": "2026-05-22T10:00:00Z", "event_type": "write", "agent_id": "a1"},
        ]
        result = exporter.export_fca(events, pack_id="FCA-STRUCT")
        output_path = Path(result.output_path)
        assert output_path.exists()
        with open(output_path, encoding="utf-8") as f:
            fca_data = json.load(f)
        assert "header" in fca_data
        assert "records" in fca_data
        assert fca_data["header"]["firm_reference"] == ""
        assert len(fca_data["records"]) == 1

    def test_export_fca_empty_events(self, tmp_path):
        exporter = EvidencePackExporter(data_dir=tmp_path, output_dir=tmp_path / "out")
        result = exporter.export_fca([], pack_id="FCA-EMPTY")
        assert result.success is True
        assert result.entry_count == 0

    def test_export_fca_auto_pack_id(self, tmp_path):
        exporter = EvidencePackExporter(data_dir=tmp_path, output_dir=tmp_path / "out")
        result = exporter.export_fca([{"event_type": "test"}])
        assert "FCA-" in Path(result.output_path).name
