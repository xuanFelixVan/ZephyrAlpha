# [A_test] module_id: SRC-TST-1082 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_guard_complexity_budget
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.forensic.guard_complexity_budget
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_guard_complexity_budget.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.forensic.guard_complexity_budget import GuardComplexityBudget


class TestGuardComplexityBudget:
    def test_instantiation_defaults(self):
        gcb = GuardComplexityBudget()
        assert gcb.active_guard_count == 0
        assert gcb.guard_complexity_history == []
        assert gcb.max_history == 100
        assert gcb.maintainability_threshold == 120
        assert gcb.marginal_value_threshold == 0.005

    def test_instantiation_custom(self):
        gcb = GuardComplexityBudget(
            active_guard_count=10,
            guard_complexity_history=[],
            max_history=50,
            maintainability_threshold=80,
            marginal_value_threshold=0.01,
        )
        assert gcb.active_guard_count == 10
        assert gcb.maintainability_threshold == 80

    def test_register_guard_addition_healthy(self):
        gcb = GuardComplexityBudget()
        result = gcb.register_guard_addition("guard-1", 0.5)
        assert result["status"] == "healthy"
        assert result["total_guards"] == 1
        assert result["recommendation"] == "CONTINUE"

    def test_register_guard_addition_warning_count(self):
        gcb = GuardComplexityBudget(maintainability_threshold=100)
        for i in range(80):
            gcb.register_guard_addition(f"guard-{i}", 0.1)
        result = gcb.register_guard_addition("guard-80", 0.1)
        assert result["status"] == "warning"
        assert "Approaching maintainability limit" in str(result["warnings"])

    def test_register_guard_addition_critical_count(self):
        gcb = GuardComplexityBudget(maintainability_threshold=10)
        for i in range(10):
            gcb.register_guard_addition(f"guard-{i}", 0.1)
        result = gcb.register_guard_addition("guard-10", 0.1)
        assert result["status"] == "critical"
        assert result["recommendation"] == "STOP_ADDING"

    def test_register_guard_addition_low_marginal_value(self):
        gcb = GuardComplexityBudget()
        result = gcb.register_guard_addition("guard-1", 0.001)
        assert result["status"] == "warning"
        assert any("Marginal value" in w for w in result["warnings"])

    def test_register_guard_addition_consolidation_warning(self):
        gcb = GuardComplexityBudget()
        for i in range(5):
            gcb.register_guard_addition(f"guard-{i}", 0.001)
        result = gcb.register_guard_addition("guard-5", 0.001)
        assert any("consolidation" in w.lower() for w in result["warnings"])

    def test_get_complexity_report(self):
        gcb = GuardComplexityBudget()
        gcb.register_guard_addition("g1", 0.5)
        gcb.register_guard_addition("g2", 0.3)
        report = gcb.get_complexity_report()
        assert report["active_guard_count"] == 2
        assert report["maintainability_threshold"] == 120
        assert report["utilization_ratio"] == round(2 / 120, 2)
        assert len(report["recent_marginal_values"]) == 2
        assert report["total_historical_additions"] == 2

    def test_get_complexity_report_empty(self):
        gcb = GuardComplexityBudget()
        report = gcb.get_complexity_report()
        assert report["active_guard_count"] == 0
        assert report["utilization_ratio"] == 0.0

    def test_max_history_truncation(self):
        gcb = GuardComplexityBudget(max_history=5)
        for i in range(10):
            gcb.register_guard_addition(f"guard-{i}", 0.1)
        assert len(gcb.guard_complexity_history) <= 5

    def test_utilization_ratio_calculation(self):
        gcb = GuardComplexityBudget(maintainability_threshold=100)
        for i in range(50):
            gcb.register_guard_addition(f"guard-{i}", 0.1)
        report = gcb.get_complexity_report()
        assert report["utilization_ratio"] == 0.5
