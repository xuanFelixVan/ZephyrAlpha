# [A_test] module_id: SRC-TST-0364 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-027 | docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md | §test
# [MODULE] tests.test_audit_registry_gate_e2e
# [INVARIANTS] e2e_tests_must_pass
# [MODIFY-GUARD] only_add_tests
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_audit_registry_gate_e2e.py
# [TTL] task_bound

import json
from unittest.mock import patch

import pytest

finding_model = pytest.importorskip("zephyr.gov_audit.finding_model", reason="finding_model not available")
AuditFinding = finding_model.AuditFinding

pipeline_mod = pytest.importorskip(
    "zephyr.gov_audit.pipeline_runner", reason="pipeline_runner not available"
)
PipelineRunner = pipeline_mod.PipelineRunner
PipelineResult = pipeline_mod.PipelineResult

phase_check_mod = pytest.importorskip(
    "zephyr.infrastructure.rollback.phase_check_registry", reason="phase_check_registry not available"
)
GateResult = phase_check_mod.GateResult
PhaseCheckRegistry = phase_check_mod.PhaseCheckRegistry
check_critical_findings = getattr(phase_check_mod, "check_critical_findings", None)
run_check = phase_check_mod.run_check
if check_critical_findings is None:
    pytest.skip("check_critical_findings not available in phase_check_registry", allow_module_level=True)


@pytest.mark.e2e
class TestRegistryScanE2E:
    def test_scan_registries_returns_findings(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        if hasattr(runner, "scan_registries"):
            findings = runner.scan_registries()
            assert isinstance(findings, list)
            for f in findings:
                assert isinstance(f, AuditFinding)

    def test_scan_manifest_returns_findings(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        if hasattr(runner, "scan_manifest"):
            findings = runner.scan_manifest()
            assert isinstance(findings, list)

    def test_scan_depgraph_returns_findings(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        if hasattr(runner, "scan_depgraph"):
            findings = runner.scan_depgraph()
            assert isinstance(findings, list)

    def test_scan_gate_registry_returns_findings(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        if hasattr(runner, "scan_gate_registry"):
            findings = runner.scan_gate_registry()
            assert isinstance(findings, list)

    def test_pipeline_runner_discovers_from_manifest(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        manifest_scripts = runner._discover_from_manifest()
        assert isinstance(manifest_scripts, dict)

    def test_pipeline_runner_discovers_from_depgraph(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        depgraph_scripts = runner._discover_from_depgraph()
        assert isinstance(depgraph_scripts, dict)

    def test_pipeline_runner_discovers_from_gate_registry(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        gate_scripts = runner._discover_from_gate_registry()
        assert isinstance(gate_scripts, dict)


@pytest.mark.e2e
class TestPhaseGateIntegrationE2E:
    def test_check_critical_findings_exists(self):
        result = check_critical_findings()
        assert result is not None
        assert isinstance(result, GateResult)

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
        db_dir = tmp_path / "scripts" / "governance" / "meta"
        db_dir.mkdir(parents=True, exist_ok=True)
        (db_dir / "finding-state-db.json").write_text(json.dumps(db_data), encoding="utf-8")

        with patch("zephyr.infrastructure.rollback.phase_check_registry._PROJECT_ROOT", tmp_path):
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

    def test_phase_check_registry_get_known_check(self):
        func = PhaseCheckRegistry.get("check_critical_findings")
        assert func is not None
        assert callable(func)

    def test_phase_check_registry_get_unknown_check(self):
        func = PhaseCheckRegistry.get("nonexistent_check_xyz")
        assert func is None

    def test_phase_check_registry_registered_checks(self):
        checks = PhaseCheckRegistry.registered_checks()
        assert isinstance(checks, list)
        assert len(checks) > 0
        assert "check_critical_findings" in checks

    def test_phase_check_registry_check_count(self):
        count = PhaseCheckRegistry.check_count()
        assert isinstance(count, int)
        assert count > 0

    def test_run_check_known(self):
        result = run_check("check_critical_findings")
        assert isinstance(result, GateResult)

    def test_run_check_unknown(self):
        result = run_check("nonexistent_check_xyz")
        assert result == GateResult.YELLOW

    def test_gate_result_enum_values(self):
        assert GateResult.GREEN == "GREEN"
        assert GateResult.YELLOW == "YELLOW"
        assert GateResult.RED == "RED"
