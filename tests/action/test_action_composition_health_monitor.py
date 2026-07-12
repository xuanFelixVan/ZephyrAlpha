# [A_test] module_id: SRC-TST-0261 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_action_composition_health_monitor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.action_composition_health_monitor
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_action_composition_health_monitor.py
# [TTL] task_bound

from zephyr.feedback_loop.diagnosers.action_composition_health_monitor import (
    ActionComposition,
    ActionCompositionHealthMonitor,
    IndependentActionStats,
)


class TestActionComposition:
    def test_default_construction(self):
        ac = ActionComposition(composition_id="c1", action_sequence=("a", "b"))
        assert ac.composition_id == "c1"
        assert ac.action_sequence == ("a", "b")
        assert ac.outcomes == []
        assert ac.max_outcomes == 50

    def test_custom_max_outcomes(self):
        ac = ActionComposition(composition_id="c2", action_sequence=("x",), max_outcomes=10)
        assert ac.max_outcomes == 10

    def test_empty_action_sequence(self):
        ac = ActionComposition(composition_id="c3", action_sequence=())
        assert ac.action_sequence == ()


class TestIndependentActionStats:
    def test_default_construction(self):
        stats = IndependentActionStats(action_type="scan")
        assert stats.action_type == "scan"
        assert stats.outcomes == []
        assert stats.max_outcomes == 50

    def test_outcomes_truncation(self):
        stats = IndependentActionStats(action_type="scan", max_outcomes=5)
        for i in range(10):
            stats.outcomes.append(True)
            if len(stats.outcomes) > stats.max_outcomes:
                stats.outcomes = stats.outcomes[-stats.max_outcomes :]
        assert len(stats.outcomes) == 5


class TestActionCompositionHealthMonitor:
    def test_instantiation_default(self):
        mon = ActionCompositionHealthMonitor()
        assert mon.compositions == {}
        assert mon.independent_stats == {}
        assert mon.negative_synergy_threshold == 0.1

    def test_instantiation_custom_threshold(self):
        mon = ActionCompositionHealthMonitor(negative_synergy_threshold=0.2)
        assert mon.negative_synergy_threshold == 0.2

    def test_record_composition_outcome_creates_entry(self):
        mon = ActionCompositionHealthMonitor()
        mon.record_composition_outcome("c1", ("a", "b"), True)
        assert "c1" in mon.compositions
        assert mon.compositions["c1"].outcomes == [True]

    def test_record_composition_outcome_appends(self):
        mon = ActionCompositionHealthMonitor()
        mon.record_composition_outcome("c1", ("a",), True)
        mon.record_composition_outcome("c1", ("a",), False)
        assert mon.compositions["c1"].outcomes == [True, False]

    def test_record_composition_outcome_truncates_at_max(self):
        mon = ActionCompositionHealthMonitor()
        for i in range(60):
            mon.record_composition_outcome("c1", ("a",), True)
        assert len(mon.compositions["c1"].outcomes) == 50

    def test_record_independent_outcome_creates_entry(self):
        mon = ActionCompositionHealthMonitor()
        mon.record_independent_outcome("scan", True)
        assert "scan" in mon.independent_stats
        assert mon.independent_stats["scan"].outcomes == [True]

    def test_record_independent_outcome_appends(self):
        mon = ActionCompositionHealthMonitor()
        mon.record_independent_outcome("scan", True)
        mon.record_independent_outcome("scan", False)
        assert mon.independent_stats["scan"].outcomes == [True, False]

    def test_record_independent_outcome_truncates_at_max(self):
        mon = ActionCompositionHealthMonitor()
        for i in range(60):
            mon.record_independent_outcome("scan", True)
        assert len(mon.independent_stats["scan"].outcomes) == 50

    def test_detect_negative_synergy_empty(self):
        mon = ActionCompositionHealthMonitor()
        result = mon.detect_negative_synergy()
        assert result["degraded_compositions"] == []
        assert result["findings"] == {}
        assert result["total_compositions"] == 0

    def test_detect_negative_synergy_insufficient_samples(self):
        mon = ActionCompositionHealthMonitor()
        mon.record_composition_outcome("c1", ("a",), True)
        result = mon.detect_negative_synergy()
        assert result["total_compositions"] == 0

    def test_detect_negative_synergy_healthy(self):
        mon = ActionCompositionHealthMonitor()
        for _ in range(10):
            mon.record_composition_outcome("c1", ("a",), True)
            mon.record_independent_outcome("a", True)
        result = mon.detect_negative_synergy()
        assert "c1" in result["findings"]
        assert result["findings"]["c1"]["severity"] == "healthy"

    def test_detect_negative_synergy_negative_detected(self):
        mon = ActionCompositionHealthMonitor(negative_synergy_threshold=0.05)
        for _ in range(10):
            mon.record_independent_outcome("a", True)
        for _ in range(10):
            mon.record_composition_outcome("c1", ("a",), False)
        result = mon.detect_negative_synergy()
        assert "c1" in result["degraded_compositions"]
        assert result["findings"]["c1"]["negative_synergy"] is True

    def test_detect_negative_synergy_critical_severity(self):
        mon = ActionCompositionHealthMonitor(negative_synergy_threshold=0.05)
        for _ in range(10):
            mon.record_independent_outcome("a", True)
        for _ in range(10):
            mon.record_composition_outcome("c1", ("a",), False)
        result = mon.detect_negative_synergy()
        assert result["findings"]["c1"]["severity"] == "critical"

    def test_detect_negative_synergy_no_independent_stats(self):
        mon = ActionCompositionHealthMonitor()
        for _ in range(10):
            mon.record_composition_outcome("c1", ("a",), True)
        result = mon.detect_negative_synergy()
        assert result["total_compositions"] == 0

    def test_detect_negative_synergy_sample_count(self):
        mon = ActionCompositionHealthMonitor()
        for _ in range(7):
            mon.record_composition_outcome("c1", ("a",), True)
            mon.record_independent_outcome("a", True)
        result = mon.detect_negative_synergy()
        assert result["findings"]["c1"]["sample_count"] == 7
