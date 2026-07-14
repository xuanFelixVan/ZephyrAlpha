# [A_test] module_id: SRC-TST-0353 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-027 | docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md | §test
# [MODULE] tests.test_audit_full_pipeline_e2e
# [INVARIANTS] e2e_tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_audit_full_pipeline_e2e.py
# [TTL] task_bound

import json
from unittest.mock import patch

import pytest

finding_model = pytest.importorskip("zephyr.gov_audit.finding_model", reason="finding_model not available")
AuditFinding = finding_model.AuditFinding
FindingSeverity = finding_model.FindingSeverity
FindingDimension = finding_model.FindingDimension
FindingStatus = finding_model.FindingStatus
FindingTarget = finding_model.FindingTarget
FindingRemediation = finding_model.RemediationAction
RemediationPriority = finding_model.RemediationPriority
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
    finding_id: str = "FIND-D1-20260526-abc123def456",
    dimension: str = "D1",
    severity: str = "HIGH",
    category: str = "结构完整性",
    description: str = "missing field",
    file_path: str = "src/zephyr/foo.py",
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


class TestFindingIngestE2E:
    def test_ingest_string_creates_finding(self, tmp_path):
        ingest = FindingIngest(audit_dir=str(tmp_path / "audit"))
        jsonl_line = _make_finding_jsonl()
        result = ingest.ingest_string(jsonl_line)
        assert result.ingested == 1
        assert result.errors == 0

    def test_ingest_string_emits_event(self, tmp_path):
        ingest = FindingIngest(audit_dir=str(tmp_path / "audit"))
        jsonl_line = _make_finding_jsonl()
        received_events = []

        with patch.object(finding_ingest_mod, "bus", create=True) as mock_bus_module:
            with patch("zephyr.gov_audit.finding_ingest.FindingIngest._emit_event") as mock_emit:
                mock_emit.side_effect = lambda f: received_events.append(f)
                result = ingest.ingest_string(jsonl_line)

        assert result.ingested == 1
        assert len(received_events) == 1
        emitted_finding = received_events[0]
        assert emitted_finding.finding_id == "FIND-D1-20260526-abc123def456"

    def test_ingest_file_from_temp(self, tmp_path):
        jsonl_file = tmp_path / "findings.jsonl"
        jsonl_file.write_text(_make_finding_jsonl() + "\n", encoding="utf-8")

        ingest = FindingIngest(audit_dir=str(tmp_path / "audit"))
        result = ingest.ingest_file(str(jsonl_file))
        assert result.ingested >= 1

    def test_ingest_malformed_line_skipped(self, tmp_path):
        ingest = FindingIngest(audit_dir=str(tmp_path / "audit"))
        valid_line = _make_finding_jsonl()
        malformed_line = "NOT VALID JSON {{{"
        combined = valid_line + "\n" + malformed_line
        result = ingest.ingest_string(combined)
        assert result.ingested == 1
        assert result.errors == 1


class TestTextToFindingAdapterE2E:
    def setup_method(self):
        self.adapter = TextToFindingAdapter()

    def test_parse_p1_tag(self):
        findings = self.adapter.parse("[P1] src/zephyr/foo.py:42 missing field", dimension="D1")
        assert len(findings) == 1
        assert findings[0].severity == FindingSeverity.HIGH
        assert findings[0].target.file_path == "src/zephyr/foo.py"
        assert findings[0].target.line_range == "42"

    def test_parse_error_line(self):
        findings = self.adapter.parse("ERROR: src/zephyr/bar.py has invalid format", dimension="D5")
        assert len(findings) == 1
        assert findings[0].severity == FindingSeverity.HIGH

    def test_parse_cross_emoji(self):
        findings = self.adapter.parse("❌ src/zephyr/baz.py: blueprint not found", dimension="D5")
        assert len(findings) == 1
        assert findings[0].severity == FindingSeverity.HIGH

    def test_parse_warning(self):
        findings = self.adapter.parse("WARNING: deprecated path detected", dimension="D5")
        assert len(findings) == 1
        assert findings[0].severity == FindingSeverity.LOW

    def test_parse_fail(self):
        findings = self.adapter.parse("FAIL: check failed", dimension="D5")
        assert len(findings) == 1
        assert findings[0].severity == FindingSeverity.MEDIUM

    def test_parse_skip_pass(self):
        findings = self.adapter.parse("PASS: all checks passed", dimension="D5")
        assert len(findings) == 0

    def test_parse_mixed_output(self):
        text = (
            "[P1] src/zephyr/foo.py:10 missing field\n"
            "ERROR: src/zephyr/bar.py invalid format\n"
            "PASS: all checks passed\n"
            "WARNING: deprecated path detected\n"
            "FAIL: check failed\n"
            "❌ src/zephyr/baz.py: blueprint not found\n"
        )
        findings = self.adapter.parse(text, dimension="D5")
        assert len(findings) == 5
        severities = [f.severity for f in findings]
        assert severities.count(FindingSeverity.HIGH) == 3
        assert severities.count(FindingSeverity.LOW) == 1
        assert severities.count(FindingSeverity.MEDIUM) == 1


class TestPipelineRunnerE2E:
    def test_discover_all_dimensions(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        discovered = set(runner._dimension_scripts.keys())
        all_dims = {f"D{i}" for i in range(1, 13)}
        assert discovered == all_dims

    def test_dry_run_returns_result(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        result = runner.run(dimensions=["D1"], dry_run=True)
        assert isinstance(result, PipelineResult)
        assert "D1" in result.dimension_results

    def test_adapter_used_for_text_output(self, tmp_path):
        mock_script = tmp_path / "mock_check.py"
        mock_script.write_text(
            'import sys\nprint("[P1] src/zephyr/mock.py:1 test finding")\nsys.exit(0)\n',
            encoding="utf-8",
        )

        adapter = TextToFindingAdapter()
        text_output = "[P1] src/zephyr/mock.py:1 test finding"
        findings = adapter.parse(text_output, dimension="D5", script_name="mock_check")
        assert len(findings) == 1
        assert findings[0].severity == FindingSeverity.HIGH
        assert findings[0].target.file_path == "src/zephyr/mock.py"


class TestAutoFixFindingClosureE2E:
    def test_close_related_finding(self, tmp_path, monkeypatch):
        db_data = {
            "findings": {
                "FIND-D1-20260526-test001": {
                    "severity": "HIGH",
                    "status": "OPEN",
                    "target": {"file_path": "src/zephyr/target_file.py"},
                    "description": "test finding",
                }
            }
        }
        db_dir = tmp_path / "scripts" / "governance" / "meta"
        db_dir.mkdir(parents=True, exist_ok=True)
        db_file = db_dir / "finding-state-db.json"
        db_file.write_text(json.dumps(db_data), encoding="utf-8")

        monkeypatch.chdir(tmp_path)
        engine = AutoFixEngine()
        engine._close_related_finding("zombie_cleanup", "src/zephyr/target_file.py")

        updated = json.loads(db_file.read_text(encoding="utf-8"))
        assert updated["findings"]["FIND-D1-20260526-test001"]["status"] == "FIXED"


class TestPhaseGateCriticalFindingsE2E:
    def test_check_critical_findings_green(self, tmp_path):
        db_data = {
            "findings": {
                "FIND-D1-20260526-ok001": {
                    "severity": "HIGH",
                    "status": "FIXED",
                    "target": {"file_path": "src/zephyr/fixed.py"},
                    "description": "already fixed",
                }
            }
        }
        db_file = tmp_path / "finding-state-db.json"
        db_file.write_text(json.dumps(db_data), encoding="utf-8")

        with patch("zephyr.infrastructure.rollback.phase_check_registry._PROJECT_ROOT", tmp_path):
            db_dir = tmp_path / "scripts" / "governance" / "meta"
            db_dir.mkdir(parents=True, exist_ok=True)
            (db_dir / "finding-state-db.json").write_text(json.dumps(db_data), encoding="utf-8")
            result = check_critical_findings()

        assert result == GateResult.GREEN

    def test_check_critical_findings_red(self, tmp_path):
        db_data = {
            "findings": {
                "FIND-D1-20260526-crit001": {
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
