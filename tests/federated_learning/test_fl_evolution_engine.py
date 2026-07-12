# [A_test] module_id: SRC-TST-0959 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_evolution_engine
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.evolution_engine
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_evolution_engine.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock

from zephyr.feedback_loop.evolution_engine import (
    EvolutionEngine,
    EvolutionReport,
    evolve,
)


class TestEvolutionEngineInstantiation:
    def test_creates_with_defaults(self):
        engine = EvolutionEngine()
        assert engine.learning_rate == 0.1
        assert engine.discount_factor == 0.9
        assert engine.q_table == {}

    def test_creates_with_custom_thresholds(self):
        engine = EvolutionEngine(thresholds={"low_score_threshold": 5})
        assert engine._thresholds["low_score_threshold"] == 5


class TestQTableOperations:
    def test_get_q_default(self):
        engine = EvolutionEngine()
        assert engine.get_q("state1", "action1") == 0.0

    def test_set_and_get_q(self):
        engine = EvolutionEngine()
        engine.set_q("state1", "action1", 5.0)
        assert engine.get_q("state1", "action1") == 5.0

    def test_update_q_value(self):
        engine = EvolutionEngine()
        engine.set_q("s1", "a1", 1.0)
        engine.update("s1", "a1", 10.0, "s2")
        assert engine.get_q("s1", "a1") != 1.0


class TestSelectAction:
    def test_selects_from_available_actions(self):
        engine = EvolutionEngine()
        engine.epsilon = 0.0
        engine.set_q("s1", "a1", 1.0)
        engine.set_q("s1", "a2", 5.0)
        action = engine.select_action("s1", ["a1", "a2"])
        assert action in ["a1", "a2"]

    def test_boundary_single_action(self):
        engine = EvolutionEngine()
        engine.epsilon = 0.0
        action = engine.select_action("s1", ["only"])
        assert action == "only"


class TestConsolidateKnowledge:
    def test_consolidates_q_to_optimal(self):
        engine = EvolutionEngine()
        engine.set_q("s1", "a1", 3.0)
        engine.consolidate_knowledge()
        assert engine.optimal_weights["s1"]["a1"] == 3.0
        assert engine.fisher_information["s1"]["a1"] == 1.0


class TestEvolve:
    def test_returns_empty_report_without_collector(self):
        engine = EvolutionEngine()
        report = engine.evolve()
        assert report.window_entry_count == 0
        assert report.proposals == []

    def test_evolve_with_collector(self):
        mock_entry = MagicMock()
        mock_entry.score = 1
        mock_entry.tags = ["retry"]
        mock_entry.task_id = "T1"
        mock_collector = MagicMock()
        mock_collector.get_entries.return_value = [mock_entry]
        engine = EvolutionEngine(collector=mock_collector)
        report = engine.evolve(dry_run=True)
        assert report.window_entry_count == 1


class TestEvolveFunction:
    def test_module_level_evolve(self):
        mock_entry = MagicMock()
        mock_entry.score = 5
        mock_entry.tags = []
        mock_entry.task_id = "T1"
        mock_collector = MagicMock()
        mock_collector.get_entries.return_value = [mock_entry]
        report = evolve(mock_collector, dry_run=True)
        assert isinstance(report, EvolutionReport)
