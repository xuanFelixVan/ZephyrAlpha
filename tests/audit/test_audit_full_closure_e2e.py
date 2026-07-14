# [A_test] module_id: SRC-TST-0352 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-027 | docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md | §test
# [MODULE] tests.test_audit_full_closure_e2e
# [INVARIANTS] e2e_tests_must_pass
# [MODIFY-GUARD] only_add_tests
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_audit_full_closure_e2e.py
# [TTL] task_bound

import json
from unittest.mock import patch

import pytest

finding_model = pytest.importorskip("zephyr.gov_audit.finding_model", reason="finding_model not available")
AuditFinding = finding_model.AuditFinding
FindingSeverity = finding_model.FindingSeverity
FindingDimension = finding_model.FindingDimension
generate_finding_id = finding_model.generate_finding_id

finding_ingest_mod = pytest.importorskip(
    "zephyr.gov_audit.finding_ingest", reason="finding_ingest not available"
)
FindingIngest = finding_ingest_mod.FindingIngest
IngestResult = finding_ingest_mod.IngestResult

pipeline_mod = pytest.importorskip(
    "zephyr.gov_audit.pipeline_runner", reason="pipeline_runner not available"
)
PipelineRunner = pipeline_mod.PipelineRunner
PipelineResult = pipeline_mod.PipelineResult

adapter_mod = pytest.importorskip(
    "zephyr.gov_audit.text_to_finding_adapter", reason="text_to_finding_adapter not available"
)
TextToFindingAdapter = adapter_mod.TextToFindingAdapter

phase_check_mod = pytest.importorskip(
    "zephyr.infrastructure.rollback.phase_check_registry", reason="phase_check_registry not available"
)
GateResult = phase_check_mod.GateResult
check_critical_findings = phase_check_mod.check_critical_findings

auto_fix_mod = pytest.importorskip(
    "zephyr.infrastructure.auto_fix_engine.engine", reason="auto-fix-engine not available"
)
AutoFixEngine = auto_fix_mod.AutoFixEngine


def _make_finding_jsonl(
    finding_id: str = "FIND-D5-20260526-closure001",
    dimension: str = "D5",
    severity: str = "HIGH",
    category: str = "架构合规",
    description: str = "test closure finding",
    file_path: str = "src/zephyr/closure_test.py",
) -> str:
    return json.dumps(
        {
            "finding_id": finding_id,
            "dimension": dimension,
            "severity": severity,
            "category": category,
            "target": {"file_path": file_path, "line_range": "1-10"},
            "description": description,
            "evidence": "test evidence",
            "impact": {"blast_radius": "file"},
            "remediation": {"action": "FIX", "priority": "P1"},
            "lifecycle": {"status": "OPEN"},
            "traceability": {"related_adr": [], "related_ke": [], "related_finding": []},
            "timestamp": "2026-05-26T12:00:00+00:00",
            "recommendation_block": {"recommendation": "", "recommendation_type": "", "recommended_action": ""},
        }
    )


@pytest.mark.e2e
class TestFullClosureE2E:
    def test_adapter_to_ingest_pipeline(self, tmp_path):
        adapter = TextToFindingAdapter()
        text = "[P1] src/zephyr/test.py:1 test finding"
        findings = adapter.parse(text, dimension="D5")
        assert len(findings) == 1

        ingest = FindingIngest(audit_dir=str(tmp_path / "audit"))
        result = ingest.ingest_findings(findings)
        assert result.ingested == 1
        assert result.errors == 0

    def test_adapter_to_ingest_multiple_findings(self, tmp_path):
        adapter = TextToFindingAdapter()
        text = (
            "[P1] src/zephyr/foo.py:10 missing field\n"
            "ERROR: src/zephyr/bar.py invalid format\n"
            "WARNING: deprecated path detected\n"
        )
        findings = adapter.parse(text, dimension="D5")
        assert len(findings) == 3

        ingest = FindingIngest(audit_dir=str(tmp_path / "audit"))
        result = ingest.ingest_findings(findings)
        assert result.ingested == 3

    def test_pipeline_dry_run_to_ingest(self, tmp_path):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        result = runner.run(dimensions=["D1"], dry_run=True)
        assert isinstance(result, PipelineResult)
        assert result.total_scripts > 0

        ingest = FindingIngest(audit_dir=str(tmp_path / "audit"))
        ingest_result = ingest.ingest_findings(result.findings)
        assert ingest_result.total == 0
        assert ingest_result.errors == 0

    def test_ingest_string_to_jsonl_file(self, tmp_path):
        ingest = FindingIngest(audit_dir=str(tmp_path / "audit"))
        ingest._writer = None
        ingest._writer_initialized = True
        jsonl_line = _make_finding_jsonl()
        result = ingest.ingest_string(jsonl_line)
        assert result.ingested == 1

        fallback_file = tmp_path / "audit" / "findings.jsonl"
        assert fallback_file.exists()
        content = fallback_file.read_text(encoding="utf-8")
        parsed = json.loads(content.strip())
        assert parsed["finding_id"] == "FIND-D5-20260526-closure001"

    def test_auto_fix_closes_finding(self, tmp_path, monkeypatch):
        db_data = {
            "findings": {
                "FIND-D5-20260526-closure001": {
                    "severity": "HIGH",
                    "status": "OPEN",
                    "target": {"file_path": "src/zephyr/closure_test.py"},
                    "description": "test closure finding",
                }
            }
        }
        db_dir = tmp_path / "scripts" / "governance" / "meta"
        db_dir.mkdir(parents=True, exist_ok=True)
        db_file = db_dir / "finding-state-db.json"
        db_file.write_text(json.dumps(db_data), encoding="utf-8")

        monkeypatch.chdir(tmp_path)
        engine = AutoFixEngine()
        engine._close_related_finding("zombie_cleanup", "src/zephyr/closure_test.py")

        updated = json.loads(db_file.read_text(encoding="utf-8"))
        assert updated["findings"]["FIND-D5-20260526-closure001"]["status"] == "FIXED"

    def test_finding_closed_gate_green(self, tmp_path):
        db_data = {
            "findings": {
                "FIND-D5-20260526-closure001": {
                    "severity": "HIGH",
                    "status": "FIXED",
                    "target": {"file_path": "src/zephyr/closure_test.py"},
                    "description": "test closure finding",
                }
            }
        }
        db_dir = tmp_path / "scripts" / "governance" / "meta"
        db_dir.mkdir(parents=True, exist_ok=True)
        (db_dir / "finding-state-db.json").write_text(json.dumps(db_data), encoding="utf-8")

        with patch("zephyr.infrastructure.rollback.phase_check_registry._PROJECT_ROOT", tmp_path):
            result = check_critical_findings()

        assert result == GateResult.GREEN

    def test_finding_open_critical_gate_red(self, tmp_path):
        db_data = {
            "findings": {
                "FIND-D5-20260526-crit001": {
                    "severity": "CRITICAL",
                    "status": "OPEN",
                    "target": {"file_path": "src/zephyr/critical.py"},
                    "description": "critical issue",
                }
            }
        }
        db_dir = tmp_path / "scripts" / "governance" / "meta"
        db_dir.mkdir(parents=True, exist_ok=True)
        (db_dir / "finding-state-db.json").write_text(json.dumps(db_data), encoding="utf-8")

        with patch("zephyr.infrastructure.rollback.phase_check_registry._PROJECT_ROOT", tmp_path):
            result = check_critical_findings()

        assert result == GateResult.RED

    def test_end_to_end_adapter_ingest_fix_gate(self, tmp_path, monkeypatch):
        adapter = TextToFindingAdapter()
        text = "[P1] src/zephyr/e2e_target.py:42 e2e closure test"
        findings = adapter.parse(text, dimension="D5")
        assert len(findings) == 1

        ingest = FindingIngest(audit_dir=str(tmp_path / "audit"))
        ingest_result = ingest.ingest_findings(findings)
        assert ingest_result.ingested == 1

        db_data = {
            "findings": {
                findings[0].finding_id: {
                    "severity": findings[0].severity.value,
                    "status": "OPEN",
                    "target": {"file_path": findings[0].target.file_path},
                    "description": findings[0].description,
                }
            }
        }
        db_dir = tmp_path / "scripts" / "governance" / "meta"
        db_dir.mkdir(parents=True, exist_ok=True)
        db_file = db_dir / "finding-state-db.json"
        db_file.write_text(json.dumps(db_data), encoding="utf-8")

        with patch("zephyr.infrastructure.rollback.phase_check_registry._PROJECT_ROOT", tmp_path):
            gate_result_before = check_critical_findings()
        assert gate_result_before == GateResult.GREEN

        db_data["findings"][findings[0].finding_id]["severity"] = "CRITICAL"
        db_file.write_text(json.dumps(db_data), encoding="utf-8")

        with patch("zephyr.infrastructure.rollback.phase_check_registry._PROJECT_ROOT", tmp_path):
            gate_result_critical = check_critical_findings()
        assert gate_result_critical == GateResult.RED

        monkeypatch.chdir(tmp_path)
        engine = AutoFixEngine()
        engine._close_related_finding("zombie_cleanup", findings[0].target.file_path)

        updated = json.loads(db_file.read_text(encoding="utf-8"))
        assert updated["findings"][findings[0].finding_id]["status"] == "FIXED"

        with patch("zephyr.infrastructure.rollback.phase_check_registry._PROJECT_ROOT", tmp_path):
            gate_result_after = check_critical_findings()
        assert gate_result_after == GateResult.GREEN

    def test_registry_scan_produces_findings(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        if hasattr(runner, "scan_registries"):
            findings = runner.scan_registries()
            assert isinstance(findings, list)
            for f in findings:
                assert isinstance(f, AuditFinding)
