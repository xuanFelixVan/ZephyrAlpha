# [A_test] module_id: SRC-TST-0348 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-027 | docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md | §test
# [MODULE] tests.test_audit_dim_d1_d4_e2e
# [INVARIANTS] e2e_tests_must_pass
# [MODIFY-GUARD] only_add_tests
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_audit_dim_d1_d4_e2e.py
# [TTL] task_bound

import pytest

pipeline_mod = pytest.importorskip(
    "zephyr.gov_audit.pipeline_runner", reason="pipeline_runner not available"
)
PipelineRunner = pipeline_mod.PipelineRunner
PipelineResult = pipeline_mod.PipelineResult
DimensionResult = pipeline_mod.DimensionResult


@pytest.mark.e2e
class TestDimD1D4E2E:
    def test_d1_scripts_discovered(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        assert "D1" in runner._dimension_scripts
        assert len(runner._dimension_scripts["D1"]) > 0

    def test_d2_scripts_discovered(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        assert "D2" in runner._dimension_scripts
        assert len(runner._dimension_scripts["D2"]) > 0

    def test_d3_scripts_discovered(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        assert "D3" in runner._dimension_scripts
        assert len(runner._dimension_scripts["D3"]) > 0

    def test_d4_scripts_discovered(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        assert "D4" in runner._dimension_scripts
        assert len(runner._dimension_scripts["D4"]) > 0

    def test_d1_dry_run(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        result = runner.run(dimensions=["D1"], dry_run=True)
        assert isinstance(result, PipelineResult)
        assert result.total_scripts > 0
        assert "D1" in result.dimension_results
        assert result.dimension_results["D1"].scripts_run == 0
        assert result.skipped > 0

    def test_d1_d2_d3_d4_dry_run(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        result = runner.run(dimensions=["D1", "D2", "D3", "D4"], dry_run=True)
        assert isinstance(result, PipelineResult)
        assert result.total_scripts > 0
        for dim in ["D1", "D2", "D3", "D4"]:
            assert dim in result.dimension_results

    def test_d1_dry_run_dimension_result_type(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        result = runner.run(dimensions=["D1"], dry_run=True)
        dr = result.dimension_results["D1"]
        assert isinstance(dr, DimensionResult)
        assert dr.dimension == "D1"

    def test_d2_dry_run_no_findings(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        result = runner.run(dimensions=["D2"], dry_run=True)
        assert len(result.findings) == 0

    def test_d3_dry_run_skipped_equals_total(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        result = runner.run(dimensions=["D3"], dry_run=True)
        assert result.skipped == result.total_scripts

    def test_d4_dry_run_passed_zero(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        result = runner.run(dimensions=["D4"], dry_run=True)
        assert result.passed == 0
        assert result.failed == 0

    def test_chain_a_contains_d1_d3(self):
        from zephyr.gov_audit.pipeline_runner import DEPENDENCY_CHAINS

        assert "D1" in DEPENDENCY_CHAINS["chain_a"]
        assert "D3" in DEPENDENCY_CHAINS["chain_a"]

    def test_chain_b_contains_d2_d4(self):
        from zephyr.gov_audit.pipeline_runner import DEPENDENCY_CHAINS

        assert "D2" in DEPENDENCY_CHAINS["chain_b"]
        assert "D4" in DEPENDENCY_CHAINS["chain_b"]
