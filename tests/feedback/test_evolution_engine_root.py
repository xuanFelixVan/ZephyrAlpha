# [A_test] module_id: SRC-TST-0872 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_evolution_engine
# [INVARIANTS] Q-learning update: Q(s,a) += lr*(reward+gamma*max_Q(s')-Q(s,a)); EWC penalty applied when fisher>0
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from zephyr.feedback_loop.evolution_engine import (
    EvolutionEngine,
    EvolutionProposal,
    EvolutionReport,
    EvolutionSignal,
    FeedbackLayer,
    Severity,
    evolve,
)


class TestEvolutionEngineInstantiation:
    def test_default_init(self):
        engine = EvolutionEngine()
        assert engine.learning_rate == 0.1
        assert engine.discount_factor == 0.9
        assert engine.epsilon == 0.1
        assert engine.ewc_lambda == 0.4
        assert engine.q_table == {}

    def test_init_with_custom_thresholds(self):
        engine = EvolutionEngine(thresholds={"low_score_threshold": 5})
        assert engine._thresholds["low_score_threshold"] == 5

    def test_init_with_now_fn(self):
        fixed = datetime(2026, 1, 1, 12, 0, 0)
        engine = EvolutionEngine(now=lambda: fixed)
        assert engine._now() == fixed


class TestEvolutionEngineQTable:
    def test_get_q_default_zero(self):
        engine = EvolutionEngine()
        assert engine.get_q("s1", "a1") == 0.0

    def test_set_q_and_get_q(self):
        engine = EvolutionEngine()
        engine.set_q("s1", "a1", 5.0)
        assert engine.get_q("s1", "a1") == 5.0

    def test_update_increments_q(self):
        engine = EvolutionEngine()
        engine.set_q("s1", "a1", 0.0)
        engine.update("s1", "a1", 1.0, "s2")
        assert engine.get_q("s1", "a1") > 0.0

    def test_update_with_no_next_state(self):
        engine = EvolutionEngine()
        engine.update("s1", "a1", 10.0, "s2")
        q_val = engine.get_q("s1", "a1")
        assert q_val == pytest.approx(1.0, abs=0.01)

    def test_update_with_existing_next_state(self):
        engine = EvolutionEngine()
        engine.set_q("s2", "a2", 5.0)
        engine.set_q("s1", "a1", 0.0)
        engine.update("s1", "a1", 1.0, "s2")
        q_val = engine.get_q("s1", "a1")
        assert q_val > 0.0


class TestEvolutionEngineSelectAction:
    def test_select_action_returns_valid_action(self):
        engine = EvolutionEngine()
        actions = ["a1", "a2", "a3"]
        selected = engine.select_action("s1", actions)
        assert selected in actions

    def test_select_action_prefers_high_q(self):
        engine = EvolutionEngine()
        engine.epsilon = 0.0
        engine.set_q("s1", "a1", 0.0)
        engine.set_q("s1", "a2", 10.0)
        selected = engine.select_action("s1", ["a1", "a2"])
        assert selected == "a2"


class TestEvolutionEngineConsolidateKnowledge:
    def test_consolidate_copies_q_to_optimal(self):
        engine = EvolutionEngine()
        engine.set_q("s1", "a1", 3.0)
        engine.consolidate_knowledge()
        assert engine.optimal_weights["s1"]["a1"] == 3.0
        assert engine.fisher_information["s1"]["a1"] == 1.0

    def test_consolidate_empty_q_table(self):
        engine = EvolutionEngine()
        engine.consolidate_knowledge()
        assert engine.optimal_weights == {}


class TestEvolutionEngineEvolve:
    def test_evolve_no_collector_returns_empty_report(self):
        engine = EvolutionEngine()
        report = engine.evolve()
        assert report.window_entry_count == 0
        assert report.proposals == []

    def test_evolve_with_empty_entries(self):
        collector = MagicMock()
        collector.get_entries.return_value = []
        engine = EvolutionEngine(collector=collector)
        report = engine.evolve()
        assert report.window_entry_count == 0

    def test_evolve_with_low_scores_triggers_l1(self):
        entry = MagicMock()
        entry.score = 1
        entry.tags = []
        entry.task_id = "T-001"
        collector = MagicMock()
        collector.get_entries.return_value = [entry]
        engine = EvolutionEngine(collector=collector)
        report = engine.evolve()
        assert report.l1_triggered == 1
        assert len(report.proposals) >= 1

    def test_evolve_with_high_scores_no_l1(self):
        entry = MagicMock()
        entry.score = 5
        entry.tags = []
        entry.task_id = "T-001"
        collector = MagicMock()
        collector.get_entries.return_value = [entry]
        engine = EvolutionEngine(collector=collector)
        report = engine.evolve()
        assert report.l1_triggered == 0

    def test_evolve_l3_score_drift(self):
        entry = MagicMock()
        entry.score = 1
        entry.tags = []
        entry.task_id = "T-001"
        collector = MagicMock()
        collector.get_entries.return_value = [entry]
        engine = EvolutionEngine(collector=collector)
        report = engine.evolve(baseline_avg_score=5.0)
        assert report.l3_triggered == 1

    def test_evolve_on_low_score_callback(self):
        called_with = []
        entry = MagicMock()
        entry.score = 1
        entry.tags = []
        entry.task_id = "T-001"
        collector = MagicMock()
        collector.get_entries.return_value = [entry]
        engine = EvolutionEngine(
            collector=collector,
            on_low_score=lambda e: called_with.append(e),
        )
        engine.evolve()
        assert len(called_with) == 1


class TestEvolveFunction:
    def test_module_level_evolve(self):
        collector = MagicMock()
        collector.get_entries.return_value = []
        report = evolve(collector)
        assert isinstance(report, EvolutionReport)
        assert report.window_entry_count == 0


class TestEvolutionProposal:
    def test_proposal_creation(self):
        p = EvolutionProposal(
            proposal_id="EP-001",
            signal=EvolutionSignal.ACCEPTANCE_DRIFT,
            layer=FeedbackLayer.L1_TASK,
            severity=Severity.HIGH,
            title="test",
            rationale="test rationale",
            recommended_action="do nothing",
            created_at=datetime.now(),
        )
        assert p.proposal_id == "EP-001"
        assert p.dry_run is True
        assert p.requires_owner_approval is False

    def test_proposal_frozen(self):
        p = EvolutionProposal(
            proposal_id="EP-002",
            signal=EvolutionSignal.HIGH_RETRY_RATE,
            layer=FeedbackLayer.L2_PATTERN,
            severity=Severity.MEDIUM,
            title="test",
            rationale="test",
            recommended_action="test",
            created_at=datetime.now(),
        )
        with pytest.raises(AttributeError):
            p.proposal_id = "changed"
