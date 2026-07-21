# [A_test] module_id: MOD-GOV_context_value_attribution | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_context_value_attribution
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_context_value_attribution.py -q
# [TTL] task_bound
from __future__ import annotations

from zephyr.autonomy_core.context.context_value_attribution import (
    KEAttribution,
    ValueAttributor,
)


class TestKEAttribution:
    def test_default_roi(self):
        attr = KEAttribution(ke_id="KE-001", task_success_rate=0.8, token_cost=100)
        assert attr.roi == 0.0

    def test_custom_roi(self):
        attr = KEAttribution(ke_id="KE-002", task_success_rate=0.9, token_cost=50, roi=1.5)
        assert attr.roi == 1.5


class TestValueAttributorInit:
    def test_instantiation(self):
        va = ValueAttributor()
        assert hasattr(va, "attribute")
        assert hasattr(va, "rank_ke")


class TestValueAttributorAttribute:
    def test_attribute_basic(self):
        va = ValueAttributor()
        attr = va.attribute("KE-100", 0.8, 100)
        assert attr.ke_id == "KE-100"
        assert attr.task_success_rate == 0.8
        assert attr.token_cost == 100

    def test_attribute_roi_calculation(self):
        va = ValueAttributor()
        attr = va.attribute("KE-101", 1.0, 100)
        import math

        expected_roi = round(1.0 / math.log(100), 4)
        assert attr.roi == expected_roi

    def test_attribute_roi_rounded_to_four_decimals(self):
        va = ValueAttributor()
        attr = va.attribute("KE-102", 0.75, 200)
        decimal_str = str(attr.roi).split(".")
        if len(decimal_str) == 2:
            assert len(decimal_str[1]) <= 4

    def test_attribute_low_token_cost_clamped(self):
        va = ValueAttributor()
        attr = va.attribute("KE-103", 0.5, 1)
        import math

        expected_roi = round(0.5 / math.log(2), 4)
        assert attr.roi == expected_roi

    def test_attribute_zero_success_rate(self):
        va = ValueAttributor()
        attr = va.attribute("KE-104", 0.0, 100)
        assert attr.roi == 0.0

    def test_attribute_high_success_low_cost(self):
        va = ValueAttributor()
        attr_high = va.attribute("KE-110", 1.0, 10)
        attr_low = va.attribute("KE-111", 1.0, 1000)
        assert attr_high.roi > attr_low.roi

    def test_attribute_token_cost_boundary_at_two(self):
        va = ValueAttributor()
        attr = va.attribute("KE-105", 1.0, 2)
        import math

        expected_roi = round(1.0 / math.log(2), 4)
        assert attr.roi == expected_roi


class TestValueAttributorRankKe:
    def test_rank_ke_sorted_by_roi_desc(self):
        va = ValueAttributor()
        a1 = KEAttribution(ke_id="KE-200", task_success_rate=0.5, token_cost=100, roi=0.1)
        a2 = KEAttribution(ke_id="KE-201", task_success_rate=0.9, token_cost=50, roi=0.5)
        a3 = KEAttribution(ke_id="KE-202", task_success_rate=0.7, token_cost=200, roi=0.2)
        ranked = va.rank_ke([a1, a2, a3])
        assert ranked[0].ke_id == "KE-201"
        assert ranked[1].ke_id == "KE-202"
        assert ranked[2].ke_id == "KE-200"

    def test_rank_ke_empty_list(self):
        va = ValueAttributor()
        ranked = va.rank_ke([])
        assert ranked == []

    def test_rank_ke_single_item(self):
        va = ValueAttributor()
        a = KEAttribution(ke_id="KE-300", task_success_rate=0.8, token_cost=100, roi=0.3)
        ranked = va.rank_ke([a])
        assert len(ranked) == 1
        assert ranked[0].ke_id == "KE-300"

    def test_rank_ke_equal_roi(self):
        va = ValueAttributor()
        a1 = KEAttribution(ke_id="KE-400", task_success_rate=0.5, token_cost=100, roi=0.2)
        a2 = KEAttribution(ke_id="KE-401", task_success_rate=0.5, token_cost=100, roi=0.2)
        ranked = va.rank_ke([a1, a2])
        assert len(ranked) == 2
