# [A_test] module_id: SRC-TST-0564 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_config_complexity_budget
# [INVARIANTS] Budget percentage must reflect total/max_items ratio
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.config_complexity_budget import ConfigComplexityBudget, ConfigMetric


class TestConfigMetric:
    def test_default_values(self):
        cm = ConfigMetric()
        assert cm.total_items == 0
        assert cm.items_with_default == 0
        assert cm.items_flagged_dangerous == 0
        assert cm.interaction_pairs == 0


class TestConfigComplexityBudgetInstantiation:
    def test_default_values(self):
        ccb = ConfigComplexityBudget()
        assert ccb.max_items == 200
        assert ccb.max_interaction_pairs == 500
        assert ccb.budget_pct == 0.0

    def test_custom_values(self):
        ccb = ConfigComplexityBudget(max_items=100, max_interaction_pairs=200)
        assert ccb.max_items == 100


class TestUpdate:
    def test_within_budget_returns_true(self):
        ccb = ConfigComplexityBudget()
        result = ccb.update(total=100, dangerous=5, pairs=200)
        assert result is True
        assert ccb.budget_pct == 50.0

    def test_exceeds_items_returns_false(self):
        ccb = ConfigComplexityBudget(max_items=100)
        result = ccb.update(total=150, dangerous=0, pairs=10)
        assert result is False

    def test_exceeds_pairs_returns_false(self):
        ccb = ConfigComplexityBudget(max_interaction_pairs=100)
        result = ccb.update(total=50, dangerous=0, pairs=200)
        assert result is False

    def test_zero_items_within_budget(self):
        ccb = ConfigComplexityBudget()
        result = ccb.update(total=0, dangerous=0, pairs=0)
        assert result is True
        assert ccb.budget_pct == 0.0

    def test_updates_metrics(self):
        ccb = ConfigComplexityBudget()
        ccb.update(total=50, dangerous=3, pairs=100)
        assert ccb.metrics.total_items == 50
        assert ccb.metrics.items_flagged_dangerous == 3
        assert ccb.metrics.interaction_pairs == 100


class TestAlert:
    def test_no_alert_when_below_80_pct(self):
        ccb = ConfigComplexityBudget(max_items=200, max_interaction_pairs=500)
        ccb.update(total=100, dangerous=0, pairs=200)
        assert ccb.alert() == []

    def test_alert_when_items_above_80_pct(self):
        ccb = ConfigComplexityBudget(max_items=100, max_interaction_pairs=500)
        ccb.update(total=90, dangerous=0, pairs=10)
        alerts = ccb.alert()
        assert len(alerts) >= 1
        assert "90/100" in alerts[0]

    def test_alert_when_pairs_above_80_pct(self):
        ccb = ConfigComplexityBudget(max_items=200, max_interaction_pairs=100)
        ccb.update(total=10, dangerous=0, pairs=90)
        alerts = ccb.alert()
        assert len(alerts) >= 1

    def test_both_alerts(self):
        ccb = ConfigComplexityBudget(max_items=100, max_interaction_pairs=100)
        ccb.update(total=90, dangerous=0, pairs=90)
        alerts = ccb.alert()
        assert len(alerts) == 2
