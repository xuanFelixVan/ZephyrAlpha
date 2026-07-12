# [A_test] module_id: SRC-TST-0944 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_config_complexity_budget
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.config_complexity_budget
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_config_complexity_budget.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.config_complexity_budget import ConfigComplexityBudget


class TestConfigComplexityBudgetInstantiation:
    def test_default_construction(self):
        ccb = ConfigComplexityBudget()
        assert ccb.max_items == 200
        assert ccb.max_interaction_pairs == 500
        assert ccb.budget_pct == 0.0


class TestUpdate:
    def test_update_within_budget(self):
        ccb = ConfigComplexityBudget()
        result = ccb.update(total=100, dangerous=5, pairs=200)
        assert result is True
        assert ccb.budget_pct == 50.0

    def test_update_exceeds_items_budget(self):
        ccb = ConfigComplexityBudget()
        result = ccb.update(total=250, dangerous=5, pairs=100)
        assert result is False

    def test_update_exceeds_pairs_budget(self):
        ccb = ConfigComplexityBudget()
        result = ccb.update(total=100, dangerous=5, pairs=600)
        assert result is False


class TestAlert:
    def test_alert_below_threshold(self):
        ccb = ConfigComplexityBudget()
        ccb.update(total=100, dangerous=5, pairs=200)
        assert ccb.alert() == []

    def test_alert_above_80_percent_items(self):
        ccb = ConfigComplexityBudget()
        ccb.update(total=170, dangerous=5, pairs=100)
        alerts = ccb.alert()
        assert any("Config items" in a for a in alerts)

    def test_alert_above_80_percent_pairs(self):
        ccb = ConfigComplexityBudget()
        ccb.update(total=100, dangerous=5, pairs=450)
        alerts = ccb.alert()
        assert any("Interaction pairs" in a for a in alerts)


class TestBoundaries:
    def test_update_zero_values(self):
        ccb = ConfigComplexityBudget()
        result = ccb.update(total=0, dangerous=0, pairs=0)
        assert result is True
        assert ccb.budget_pct == 0.0
