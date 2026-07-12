# [A_test] module_id: SRC-TST-1770 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_trust_engine
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from zephyr.gov_audit.trust_engine import (
    TrustAdjustment,
    TrustRecord,
    TrustScoreEngine,
)


@pytest.fixture
def engine():
    return TrustScoreEngine(initial_score=0.5, decay_rate=0.005, floor=0.1, ceiling=1.0)


class TestTrustAdjustment:
    def test_default_values(self):
        adj = TrustAdjustment()
        assert adj.agent_id == ""
        assert adj.delta == 0.0
        assert adj.reason == ""

    def test_custom_values(self):
        adj = TrustAdjustment(agent_id="a1", delta=0.1, reason="good behavior")
        assert adj.agent_id == "a1"
        assert adj.delta == 0.1


class TestTrustRecord:
    def test_default_values(self):
        rec = TrustRecord()
        assert rec.score == 0.5
        assert rec.adjustment_count == 0
        assert rec.history == []

    def test_custom_values(self):
        rec = TrustRecord(agent_id="a1", score=0.8, adjustment_count=3)
        assert rec.score == 0.8
        assert rec.adjustment_count == 3


class TestTrustScoreEngine:
    def test_instantiation(self):
        eng = TrustScoreEngine()
        assert eng._initial_score == 0.5
        assert eng._decay_rate == 0.005

    def test_compute_score_new_agent(self, engine):
        score = engine.compute_score("agent-new")
        assert score == 0.5

    def test_adjust_positive(self, engine):
        new_score = engine.adjust("agent-1", 0.1, "good behavior")
        assert new_score == 0.6

    def test_adjust_negative(self, engine):
        new_score = engine.adjust("agent-1", -0.2, "bad behavior")
        assert new_score == 0.3

    def test_adjust_clamps_to_floor(self, engine):
        new_score = engine.adjust("agent-1", -0.5, "very bad")
        assert new_score == 0.1

    def test_adjust_clamps_to_ceiling(self, engine):
        new_score = engine.adjust("agent-1", 0.6, "very good")
        assert new_score == 1.0

    def test_get_score(self, engine):
        engine.adjust("agent-1", 0.1, "test")
        score = engine.get_score("agent-1")
        assert score == 0.6

    def test_get_record(self, engine):
        engine.adjust("agent-1", 0.05, "test")
        record = engine.get_record("agent-1")
        assert record is not None
        assert record.agent_id == "agent-1"
        assert record.adjustment_count == 1

    def test_get_record_nonexistent(self, engine):
        record = engine.get_record("nonexistent")
        assert record is None

    def test_adjust_records_history(self, engine):
        engine.adjust("agent-1", 0.1, "first")
        engine.adjust("agent-1", -0.05, "second")
        record = engine.get_record("agent-1")
        assert len(record.history) == 2

    def test_decay_all(self, engine):
        engine.adjust("agent-1", 0.3, "boost")
        engine.adjust("agent-2", 0.2, "boost")
        results = engine.decay_all()
        assert "agent-1" in results
        assert "agent-2" in results

    def test_decay_all_empty(self, engine):
        results = engine.decay_all()
        assert results == {}

    def test_compute_score_with_old_record(self, engine):
        record = engine._get_or_create("agent-old")
        record.last_adjusted_at = (datetime.now(UTC) - timedelta(days=10)).isoformat()
        record.score = 0.8
        engine._records["agent-old"] = record
        score = engine.compute_score("agent-old")
        assert score < 0.8

    def test_custom_initial_score(self):
        eng = TrustScoreEngine(initial_score=0.7)
        score = eng.compute_score("new-agent")
        assert score == 0.7

    def test_multiple_adjustments(self, engine):
        engine.adjust("agent-1", 0.1, "good")
        engine.adjust("agent-1", 0.1, "good")
        engine.adjust("agent-1", 0.1, "good")
        record = engine.get_record("agent-1")
        assert record.adjustment_count == 3
