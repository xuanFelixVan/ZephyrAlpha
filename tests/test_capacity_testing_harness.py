# [A_test] module_id: SRC-TST-0495 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infra_ops/capacity_assurance/blueprint.md | §test
# [MODULE] tests.test_capacity_testing_harness
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_capacity_testing_harness.py
# [TTL] task_bound

import pytest

mod = pytest.importorskip(
    "zephyr.ops.capacity_assurance.capacity_testing_harness", reason="capacity_testing_harness not available"
)
CapacityTestingHarness = mod.CapacityTestingHarness


class MockKillSwitch:
    def __init__(self):
        self._active = False

    def activate(self, reason):
        self._active = True

    def deactivate(self):
        self._active = False

    def is_active(self):
        return self._active


class MockSandbox:
    class ResultEnum:
        def __init__(self, value):
            self.value = value

    def sandbox_file_delete(self, path, confirmed=False):
        return (self.ResultEnum("dry_run"), None)


class TestCapacityTestingHarness:
    def test_instantiation(self):
        harness = CapacityTestingHarness()
        assert harness._test_results == []

    def test_test_live_kill_switch(self):
        harness = CapacityTestingHarness()
        ks = MockKillSwitch()
        result = harness.test_live_kill_switch(ks)
        assert result["test"] == "test_live_kill_switch"
        assert result["passed"] is True

    def test_test_live_kill_switch_exception(self):
        harness = CapacityTestingHarness()

        class BadKillSwitch:
            def activate(self, reason):
                raise RuntimeError("broken")

            def deactivate(self):
                raise RuntimeError("broken")

            def is_active(self):
                raise RuntimeError("broken")

        result = harness.test_live_kill_switch(BadKillSwitch())
        assert result["passed"] is False
        assert "error" in result

    def test_test_sandbox_isolation(self):
        harness = CapacityTestingHarness()
        sandbox = MockSandbox()
        result = harness.test_sandbox_isolation(sandbox)
        assert result["test"] == "test_sandbox_isolation"
        assert result["passed"] is True

    def test_run_all_with_kill_switch(self):
        harness = CapacityTestingHarness()
        ks = MockKillSwitch()
        results = harness.run_all(kill_switch=ks)
        assert "kill_switch" in results
        assert results["kill_switch"]["passed"] is True

    def test_run_all_with_sandbox(self):
        harness = CapacityTestingHarness()
        sandbox = MockSandbox()
        results = harness.run_all(sandbox=sandbox)
        assert "sandbox" in results

    def test_run_all_empty(self):
        harness = CapacityTestingHarness()
        results = harness.run_all()
        assert results == {}
