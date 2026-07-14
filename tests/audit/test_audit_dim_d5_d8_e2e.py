# [A_test] module_id: SRC-TST-0349 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-027 | docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md | §test
# [MODULE] tests.test_audit_dim_d5_d8_e2e
# [INVARIANTS] e2e_tests_must_pass
# [MODIFY-GUARD] only_add_tests
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_audit_dim_d5_d8_e2e.py
# [TTL] task_bound

import pytest

pipeline_mod = pytest.importorskip(
    "zephyr.gov_audit.pipeline_runner", reason="pipeline_runner not available"
)
PipelineRunner = pipeline_mod.PipelineRunner
PipelineResult = pipeline_mod.PipelineResult
DimensionResult = pipeline_mod.DimensionResult


@pytest.mark.e2e
class TestDimD5D8E2E:
    def test_d5_scripts_discovered(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        assert "D5" in runner._dimension_scripts
        assert len(runner._dimension_scripts["D5"]) > 10

    def test_d6_scripts_discovered(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        assert "D6" in runner._dimension_scripts
        assert len(runner._dimension_scripts["D6"]) > 0

    def test_d7_scripts_discovered(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        assert "D7" in runner._dimension_scripts
        assert len(runner._dimension_scripts["D7"]) > 0

    def test_d8_scripts_discovered(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        assert "D8" in runner._dimension_scripts
        assert len(runner._dimension_scripts["D8"]) > 0

    def test_d5_is_largest_dimension(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        d5_count = len(runner._dimension_scripts.get("D5", []))
        for dim in ["D6", "D7", "D8"]:
            dim_count = len(runner._dimension_scripts.get(dim, []))
            assert d5_count >= dim_count

    def test_d5_dry_run(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        result = runner.run(dimensions=["D5"], dry_run=True)
        assert isinstance(result, PipelineResult)
        assert result.total_scripts > 0
        assert "D5" in result.dimension_results
        assert result.dimension_results["D5"].scripts_run == 0

    def test_d5_d6_d7_d8_dry_run(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        result = runner.run(dimensions=["D5", "D6", "D7", "D8"], dry_run=True)
        assert isinstance(result, PipelineResult)
        assert result.total_scripts > 0
        for dim in ["D5", "D6", "D7", "D8"]:
            assert dim in result.dimension_results

    def test_d5_dry_run_dimension_result_type(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        result = runner.run(dimensions=["D5"], dry_run=True)
        dr = result.dimension_results["D5"]
        assert isinstance(dr, DimensionResult)
        assert dr.dimension == "D5"

    def test_d6_dry_run_no_findings(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        result = runner.run(dimensions=["D6"], dry_run=True)
        assert len(result.findings) == 0

    def test_d7_dry_run_skipped_equals_total(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        result = runner.run(dimensions=["D7"], dry_run=True)
        assert result.skipped == result.total_scripts

    def test_d8_dry_run_passed_zero(self):
        runner = PipelineRunner(scripts_dir="scripts/governance")
        result = runner.run(dimensions=["D8"], dry_run=True)
        assert result.passed == 0
        assert result.failed == 0

    def test_chain_a_contains_d5_d8(self):
        from zephyr.gov_audit.pipeline_runner import DEPENDENCY_CHAINS

        assert "D5" in DEPENDENCY_CHAINS["chain_a"]
        assert "D8" in DEPENDENCY_CHAINS["chain_a"]

    def test_chain_c_contains_d6_d7(self):
        from zephyr.gov_audit.pipeline_runner import DEPENDENCY_CHAINS

        assert "D6" in DEPENDENCY_CHAINS["chain_c"]
        assert "D7" in DEPENDENCY_CHAINS["chain_c"]
