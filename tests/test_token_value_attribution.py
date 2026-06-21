# [A_test] module_id: SRC-TST-1751 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md | §test
# [MODULE] tests.test_token_value_attribution
# [INVARIANTS] tests_must_pass;no_todo_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_token_value_attribution.py

import pytest

mod = pytest.importorskip("zephyr.ops.capacity_assurance.token_value_attribution", reason="token_value_attribution not available")
TokenValueAttribution = mod.TokenValueAttribution


class TestTokenValueAttribution:
    def test_instantiation(self):
        tva = TokenValueAttribution()
        assert len(tva._records) == 0

    def test_attribute_high_value(self):
        tva = TokenValueAttribution()
        result = tva.attribute("task_1", 1000, 0.5, output_useful=True, complexity_resolved=True)
        assert result["tier"] == "HIGH_VALUE"
        assert result["roi"] >= 1.0
        assert result["suggestion"] == ""

    def test_attribute_low_value(self):
        tva = TokenValueAttribution()
        result = tva.attribute("task_2", 1000, 10.0, output_useful=False, complexity_resolved=False)
        assert result["tier"] == "LOW_VALUE"
        assert "replacing" in result["suggestion"]

    def test_attribute_acceptable(self):
        tva = TokenValueAttribution()
        result = tva.attribute("task_3", 1000, 1.0, output_useful=True, complexity_resolved=False)
        assert result["tier"] == "ACCEPTABLE"

    def test_attribute_zero_cost(self):
        tva = TokenValueAttribution()
        result = tva.attribute("task_4", 1000, 0.0, output_useful=True)
        assert result["roi"] == 1.0

    def test_attribute_zero_cost_not_useful(self):
        tva = TokenValueAttribution()
        result = tva.attribute("task_5", 1000, 0.0, output_useful=False)
        assert result["roi"] == 0.0

    def test_summary_empty(self):
        tva = TokenValueAttribution()
        result = tva.summary()
        assert result["total_records"] == 0

    def test_summary_with_records(self):
        tva = TokenValueAttribution()
        tva.attribute("task_1", 1000, 1.0, output_useful=True, complexity_resolved=True)
        tva.attribute("task_2", 500, 2.0, output_useful=True, complexity_resolved=True)
        result = tva.summary()
        assert result["total_records"] == 2
        assert result["total_cost_usd"] == 3.0

    def test_threshold_constants(self):
        assert TokenValueAttribution.LOW_ROI_THRESHOLD == 0.1
        assert TokenValueAttribution.HIGH_ROI_THRESHOLD == 1.0
