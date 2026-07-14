# [A_test] module_id: SRC-TST-0350 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-027 | docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md | §test
# [MODULE] tests.test_audit_dim_d9_d12_e2e
# [INVARIANTS] e2e_tests_must_pass
# [MODIFY-GUARD] only_add_tests
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_audit_dim_d9_d12_e2e.py
# [TTL] task_bound

import pytest

pipeline_mod = pytest.importorskip(
    "zephyr.gov_audit.pipeline_runner", reason="pipeline_runner not available"
)
PipelineRunner = pipeline_mod.PipelineRunner
PipelineResult = pipeline_mod.PipelineResult
DimensionResult = pipeline_mod.DimensionResult


@pytest.mark.e2e
class TestDimD9D12E2E:
    def test_d9_scripts_discovered(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        assert "D9" in runner._dimension_scripts
        assert len(runner._dimension_scripts["D9"]) > 0

    def test_d10_scripts_discovered(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        assert "D10" in runner._dimension_scripts
        assert len(runner._dimension_scripts["D10"]) > 0

    def test_d11_scripts_discovered(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        assert "D11" in runner._dimension_scripts
        assert len(runner._dimension_scripts["D11"]) > 0

    def test_d12_scripts_discovered(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        assert "D12" in runner._dimension_scripts
        assert len(runner._dimension_scripts["D12"]) > 0

    def test_d9_dry_run(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        result = runner.run(dimensions=["D9"], dry_run=True)
        assert isinstance(result, PipelineResult)
        assert result.total_scripts > 0
        assert "D9" in result.dimension_results
        assert result.dimension_results["D9"].scripts_run == 0

    def test_d9_d10_d11_d12_dry_run(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        result = runner.run(dimensions=["D9", "D10", "D11", "D12"], dry_run=True)
        assert isinstance(result, PipelineResult)
        assert result.total_scripts > 0
        for dim in ["D9", "D10", "D11", "D12"]:
            assert dim in result.dimension_results

    def test_d9_dry_run_dimension_result_type(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        result = runner.run(dimensions=["D9"], dry_run=True)
        dr = result.dimension_results["D9"]
        assert isinstance(dr, DimensionResult)
        assert dr.dimension == "D9"

    def test_d10_dry_run_no_findings(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        result = runner.run(dimensions=["D10"], dry_run=True)
        assert len(result.findings) == 0

    def test_d11_dry_run_skipped_equals_total(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        result = runner.run(dimensions=["D11"], dry_run=True)
        assert result.skipped == result.total_scripts

    def test_d12_dry_run_passed_zero(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        result = runner.run(dimensions=["D12"], dry_run=True)
        assert result.passed == 0
        assert result.failed == 0

    def test_chain_b_contains_d9_d11_d12(self):
        from zephyr.gov_audit.pipeline_runner import DEPENDENCY_CHAINS

        assert "D9" in DEPENDENCY_CHAINS["chain_b"]
        assert "D11" in DEPENDENCY_CHAINS["chain_b"]
        assert "D12" in DEPENDENCY_CHAINS["chain_b"]

    def test_chain_c_contains_d10(self):
        from zephyr.gov_audit.pipeline_runner import DEPENDENCY_CHAINS

        assert "D10" in DEPENDENCY_CHAINS["chain_c"]
