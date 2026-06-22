# [A_test] module_id: SRC-TST-1702 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md | §test
# [MODULE] tests.test_sunk_cost_intervention
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_sunk_cost_intervention.py

import pytest

mod = pytest.importorskip(
    "zephyr.ops.capacity_assurance.sunk_cost_intervention", reason="sunk_cost_intervention not available"
)
SunkCostIntervention = mod.SunkCostIntervention


class TestSunkCostIntervention:
    def test_instantiation(self):
        sci = SunkCostIntervention()
        assert len(sci._module_costs) == 0

    def test_analyze_empty(self):
        sci = SunkCostIntervention()
        result = sci.analyze()
        assert result["interventions"] == []

    def test_record_and_analyze_no_intervention(self):
        sci = SunkCostIntervention()
        sci.record("module_a", 200, 0.5)
        sci.record("module_b", 200, 0.3)
        sci.record("module_c", 200, 0.2)
        sci.record("module_d", 200, 0.1)
        sci.record("module_e", 200, 0.1)
        result = sci.analyze()
        assert result["interventions"] == []
        assert result["total_tokens"] == 1000

    def test_record_and_analyze_with_intervention(self):
        sci = SunkCostIntervention()
        sci.record("module_a", 800, 1.0)
        sci.record("module_b", 200, 0.3)
        result = sci.analyze()
        assert len(result["interventions"]) == 1
        assert result["interventions"][0]["module"] == "module_a"
        assert result["interventions"][0]["token_share"] == 0.8

    def test_threshold_constant(self):
        assert SunkCostIntervention.TOKEN_SHARE_THRESHOLD == 0.30

    def test_window_hours_constant(self):
        assert SunkCostIntervention.WINDOW_HOURS == 48
