# [A_test] module_id: SRC-TST-0835 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §

# [MODULE] zephyr.gov_enforcement.rule_enforcement.end_to_end_walkthrough

# [INVARIANTS] WalkthroughScenario has 7 members; ScenarioResult.failures defaults to empty list; pass_rate returns 0.0 when no results

# [MODIFY-GUARD] do not change scenario enum values without updating all consumers

# [CONSUMERS] tests/test_end_to_end_walkthrough.py

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] run_all returns list[ScenarioResult]; pass_rate returns float >= 0.0 and <= 1.0

# [TESTS] tests/test_end_to_end_walkthrough.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.gov_enforcement.rule_enforcement.end_to_end_walkthrough import (
    EndToEndWalkthrough,
    ScenarioResult,
    WalkthroughScenario,
)


class TestWalkthroughScenario:
    def test_enum_has_seven_members(self):
        assert len(WalkthroughScenario) == 7

    def test_enum_values(self):
        expected = [
            "COLD_START",
            "FINDING_TO_TASK",
            "CIRCUIT_BREAKER",
            "HEALTH_DEGRADATION",
            "DLQ_REPLAY",
            "STARTUP_SEQUENCE",
            "TEARDOWN_CLEANUP",
        ]
        actual = [m.value for m in WalkthroughScenario]
        assert actual == expected

    def test_enum_is_str_subclass(self):
        for member in WalkthroughScenario:
            assert isinstance(member, str)

    def test_enum_access_by_name(self):
        assert WalkthroughScenario.COLD_START.value == "COLD_START"
        assert WalkthroughScenario.TEARDOWN_CLEANUP.value == "TEARDOWN_CLEANUP"

    def test_enum_invalid_name_raises(self):
        with pytest.raises(ValueError):
            WalkthroughScenario("NONEXISTENT")


class TestScenarioResult:
    def test_init_with_failures(self):
        result = ScenarioResult("COLD_START", True, ["err1", "err2"])
        assert result.scenario == "COLD_START"
        assert result.passed is True
        assert result.failures == ["err1", "err2"]

    def test_init_without_failures_defaults_to_empty(self):
        result = ScenarioResult("COLD_START", True)
        assert result.failures == []

    def test_init_failures_none_defaults_to_empty(self):
        result = ScenarioResult("COLD_START", False, None)
        assert result.failures == []

    def test_passed_false(self):
        result = ScenarioResult("DLQ_REPLAY", False, ["timeout"])
        assert result.passed is False
        assert result.failures == ["timeout"]

    def test_scenario_stores_string(self):
        result = ScenarioResult(WalkthroughScenario.COLD_START.value, True)
        assert result.scenario == "COLD_START"


class TestEndToEndWalkthroughInit:
    def test_instantiation(self):
        walker = EndToEndWalkthrough()
        assert walker is not None

    def test_initial_results_empty(self):
        walker = EndToEndWalkthrough()
        assert walker.results() == []

    def test_initial_pass_rate_zero(self):
        walker = EndToEndWalkthrough()
        assert walker.pass_rate() == 0.0


class TestEndToEndWalkthroughRunAll:
    def test_run_all_returns_list(self):
        walker = EndToEndWalkthrough()
        results = walker.run_all()
        assert isinstance(results, list)

    def test_run_all_returns_seven_results(self):
        walker = EndToEndWalkthrough()
        results = walker.run_all()
        assert len(results) == 7

    def test_run_all_all_passed(self):
        walker = EndToEndWalkthrough()
        results = walker.run_all()
        assert all(r.passed for r in results)

    def test_run_all_results_are_scenario_result_instances(self):
        walker = EndToEndWalkthrough()
        results = walker.run_all()
        for r in results:
            assert isinstance(r, ScenarioResult)

    def test_run_all_scenarios_match_enum(self):
        walker = EndToEndWalkthrough()
        results = walker.run_all()
        actual_scenarios = {r.scenario for r in results}
        expected_scenarios = {m.value for m in WalkthroughScenario}
        assert actual_scenarios == expected_scenarios

    def test_run_all_failures_empty_by_default(self):
        walker = EndToEndWalkthrough()
        results = walker.run_all()
        for r in results:
            assert r.failures == []

    def test_run_all_populates_internal_results(self):
        walker = EndToEndWalkthrough()
        walker.run_all()
        assert len(walker.results()) == 7

    def test_run_all_called_twice_accumulates(self):
        walker = EndToEndWalkthrough()
        walker.run_all()
        walker.run_all()
        assert len(walker.results()) == 14


class TestEndToEndWalkthroughResults:
    def test_results_returns_copy(self):
        walker = EndToEndWalkthrough()
        walker.run_all()
        r1 = walker.results()
        r2 = walker.results()
        assert r1 is not r2

    def test_results_returns_correct_count(self):
        walker = EndToEndWalkthrough()
        walker.run_all()
        assert len(walker.results()) == 7

    def test_results_empty_before_run(self):
        walker = EndToEndWalkthrough()
        assert walker.results() == []


class TestEndToEndWalkthroughPassRate:
    def test_pass_rate_after_run_all(self):
        walker = EndToEndWalkthrough()
        walker.run_all()
        assert walker.pass_rate() == 1.0

    def test_pass_rate_zero_before_run(self):
        walker = EndToEndWalkthrough()
        assert walker.pass_rate() == 0.0

    def test_pass_rate_with_mixed_results(self):
        walker = EndToEndWalkthrough()
        walker._results = [
            ScenarioResult("A", True),
            ScenarioResult("B", False, ["fail"]),
            ScenarioResult("C", True),
            ScenarioResult("D", False, ["err"]),
        ]
        assert walker.pass_rate() == 0.5

    def test_pass_rate_all_failed(self):
        walker = EndToEndWalkthrough()
        walker._results = [
            ScenarioResult("A", False, ["fail"]),
            ScenarioResult("B", False, ["err"]),
        ]
        assert walker.pass_rate() == 0.0

    def test_pass_rate_single_pass(self):
        walker = EndToEndWalkthrough()
        walker._results = [ScenarioResult("A", True)]
        assert walker.pass_rate() == 1.0

    def test_pass_rate_single_fail(self):
        walker = EndToEndWalkthrough()
        walker._results = [ScenarioResult("A", False, ["fail"])]
        assert walker.pass_rate() == 0.0

    def test_pass_rate_returns_float(self):
        walker = EndToEndWalkthrough()
        walker.run_all()
        assert isinstance(walker.pass_rate(), float)

    def test_pass_rate_between_zero_and_one(self):
        walker = EndToEndWalkthrough()
        walker._results = [
            ScenarioResult("A", True),
            ScenarioResult("B", False, ["fail"]),
        ]
        rate = walker.pass_rate()
        assert 0.0 <= rate <= 1.0
