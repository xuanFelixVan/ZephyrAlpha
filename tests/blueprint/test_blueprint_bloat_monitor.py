# [A_test] module_id: MOD-GOV_blueprint_bloat_monitor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_blueprint_bloat_monitor
# [INVARIANTS] MAX_BLUEPRINT_LINES=5000;MAX_TASK_CARDS=50;should_refactor_when_over_limit
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.ExitCode
# [TESTS] test_blueprint_bloat_monitor.py
# [TTL] task_bound

from zephyr.governance.architecture_governance.blueprint_bloat_monitor import BlueprintBloatMonitor


class TestBlueprintBloatMonitorConstants:
    def test_max_blueprint_lines(self):
        assert BlueprintBloatMonitor.MAX_BLUEPRINT_LINES == 5000

    def test_max_task_cards(self):
        assert BlueprintBloatMonitor.MAX_TASK_CARDS == 50


class TestCheckBloat:
    def test_within_limits(self):
        mon = BlueprintBloatMonitor()
        result = mon.check_bloat(blueprint_lines=100, task_cards=10)
        assert result["blueprint_ok"] is True
        assert result["task_cards_ok"] is True

    def test_blueprint_over_limit(self):
        mon = BlueprintBloatMonitor()
        result = mon.check_bloat(blueprint_lines=6000, task_cards=10)
        assert result["blueprint_ok"] is False
        assert result["task_cards_ok"] is True

    def test_task_cards_over_limit(self):
        mon = BlueprintBloatMonitor()
        result = mon.check_bloat(blueprint_lines=100, task_cards=60)
        assert result["blueprint_ok"] is True
        assert result["task_cards_ok"] is False

    def test_both_over_limit(self):
        mon = BlueprintBloatMonitor()
        result = mon.check_bloat(blueprint_lines=6000, task_cards=60)
        assert result["blueprint_ok"] is False
        assert result["task_cards_ok"] is False

    def test_exact_blueprint_limit(self):
        mon = BlueprintBloatMonitor()
        result = mon.check_bloat(blueprint_lines=5000, task_cards=10)
        assert result["blueprint_ok"] is True

    def test_exact_task_card_limit(self):
        mon = BlueprintBloatMonitor()
        result = mon.check_bloat(blueprint_lines=100, task_cards=50)
        assert result["task_cards_ok"] is True

    def test_returns_lines_and_cards(self):
        mon = BlueprintBloatMonitor()
        result = mon.check_bloat(blueprint_lines=42, task_cards=7)
        assert result["lines"] == 42
        assert result["cards"] == 7

    def test_zero_values(self):
        mon = BlueprintBloatMonitor()
        result = mon.check_bloat(blueprint_lines=0, task_cards=0)
        assert result["blueprint_ok"] is True
        assert result["task_cards_ok"] is True


class TestShouldRefactor:
    def test_below_limit(self):
        mon = BlueprintBloatMonitor()
        assert mon.should_refactor(100) is False

    def test_at_limit(self):
        mon = BlueprintBloatMonitor()
        assert mon.should_refactor(5000) is False

    def test_over_limit(self):
        mon = BlueprintBloatMonitor()
        assert mon.should_refactor(5001) is True
