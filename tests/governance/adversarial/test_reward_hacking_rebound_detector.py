# [A_test] module_id: SRC-TST-1462 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_reward_hacking_rebound_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_reward_hacking_rebound_detector.py -q
# [TTL] task_bound

from __future__ import annotations

import time

from zephyr.gov_drift.reward_hacking_rebound_detector import (
    ReboundDetector,
    ReboundPhase,
    ReboundSeverity,
)


class TestReboundPhaseEnum:
    def test_violation_value(self):
        assert ReboundPhase.VIOLATION == "violation"

    def test_improvement_value(self):
        assert ReboundPhase.IMPROVEMENT == "improvement"

    def test_rebound_value(self):
        assert ReboundPhase.REBOUND == "rebound"


class TestReboundSeverityOrdering:
    def test_critical_greater_than_high(self):
        assert ReboundSeverity.CRITICAL >= ReboundSeverity.HIGH

    def test_high_greater_than_medium(self):
        assert ReboundSeverity.HIGH >= ReboundSeverity.MEDIUM

    def test_medium_greater_than_low(self):
        assert ReboundSeverity.MEDIUM >= ReboundSeverity.LOW

    def test_low_not_greater_than_medium(self):
        assert not (ReboundSeverity.LOW >= ReboundSeverity.MEDIUM)

    def test_equal_severity(self):
        assert ReboundSeverity.HIGH >= ReboundSeverity.HIGH

    def test_ge_with_non_severity_returns_not_implemented(self):
        result = ReboundSeverity.HIGH.__ge__("not_a_severity")
        assert result is NotImplemented


class TestReboundDetectorInit:
    def test_default_window_parameters(self):
        det = ReboundDetector()
        assert det._sliding_window_seconds == 90 * 86400
        assert det._min_gap_seconds == 30 * 86400
        assert det._max_gap_seconds == 90 * 86400

    def test_custom_window_parameters(self):
        det = ReboundDetector(sliding_window_days=60, min_rebound_gap_days=10, max_rebound_gap_days=50)
        assert det._sliding_window_seconds == 60 * 86400
        assert det._min_gap_seconds == 10 * 86400
        assert det._max_gap_seconds == 50 * 86400


class TestRecord:
    def test_record_adds_behavior(self):
        det = ReboundDetector()
        det.record("agent-1", "violation", "high", "bad behavior", "evt-1", timestamp=1000.0)
        records = det._records.get("agent-1", [])
        assert len(records) == 1
        assert records[0].agent_id == "agent-1"
        assert records[0].phase == ReboundPhase.VIOLATION
        assert records[0].severity == ReboundSeverity.HIGH

    def test_record_uses_current_time_when_timestamp_none(self):
        det = ReboundDetector()
        before = time.time()
        det.record("agent-1", "improvement", "low")
        after = time.time()
        records = det._records["agent-1"]
        assert before <= records[0].timestamp <= after

    def test_multiple_records_for_same_agent(self):
        det = ReboundDetector()
        det.record("agent-1", "violation", "high", timestamp=1000.0)
        det.record("agent-1", "improvement", "low", timestamp=2000.0)
        assert len(det._records["agent-1"]) == 2


class TestDetectRebound:
    def test_no_rebound_with_insufficient_phases(self):
        det = ReboundDetector()
        det.record("agent-1", "violation", "high", timestamp=1000.0)
        assert det.detect_rebound("agent-1") is False

    def test_detects_full_three_phase_rebound(self):
        det = ReboundDetector(min_rebound_gap_days=1, max_rebound_gap_days=90)
        base = time.time() - 40 * 86400
        det.record("agent-1", "violation", "medium", timestamp=base)
        det.record("agent-1", "improvement", "low", timestamp=base + 10 * 86400)
        det.record("agent-1", "rebound", "high", timestamp=base + 40 * 86400)
        assert det.detect_rebound("agent-1") is True

    def test_no_rebound_when_severity_does_not_escalate(self):
        det = ReboundDetector(min_rebound_gap_days=1, max_rebound_gap_days=90)
        base = time.time() - 40 * 86400
        det.record("agent-2", "violation", "high", timestamp=base)
        det.record("agent-2", "improvement", "low", timestamp=base + 10 * 86400)
        det.record("agent-2", "rebound", "low", timestamp=base + 40 * 86400)
        assert det.detect_rebound("agent-2") is False

    def test_no_rebound_when_gap_too_short(self):
        det = ReboundDetector(min_rebound_gap_days=30, max_rebound_gap_days=90)
        base = time.time() - 10 * 86400
        det.record("agent-3", "violation", "medium", timestamp=base)
        det.record("agent-3", "improvement", "low", timestamp=base + 2 * 86400)
        det.record("agent-3", "rebound", "high", timestamp=base + 5 * 86400)
        assert det.detect_rebound("agent-3") is False

    def test_no_rebound_when_gap_too_long(self):
        det = ReboundDetector(min_rebound_gap_days=30, max_rebound_gap_days=90)
        base = time.time() - 200 * 86400
        det.record("agent-4", "violation", "medium", timestamp=base)
        det.record("agent-4", "improvement", "low", timestamp=base + 10 * 86400)
        det.record("agent-4", "rebound", "high", timestamp=base + 150 * 86400)
        assert det.detect_rebound("agent-4") is False


class TestAnalyzeRebound:
    def test_returns_detection_with_evidence(self):
        det = ReboundDetector(min_rebound_gap_days=1, max_rebound_gap_days=90)
        base = time.time() - 40 * 86400
        det.record("agent-1", "violation", "medium", timestamp=base)
        det.record("agent-1", "improvement", "low", timestamp=base + 10 * 86400)
        det.record("agent-1", "rebound", "high", timestamp=base + 40 * 86400)
        result = det.analyze_rebound("agent-1")
        assert result.detected is True
        assert result.agent_id == "agent-1"
        assert len(result.evidence) == 3
        assert result.window_days > 0

    def test_returns_empty_detection_for_unknown_agent(self):
        det = ReboundDetector()
        result = det.analyze_rebound("unknown")
        assert result.detected is False
        assert result.agent_id == "unknown"


class TestReboundAgentManagement:
    def test_mark_and_check_rebound_agent(self):
        det = ReboundDetector()
        det.mark_rebound_agent("agent-x")
        assert det.is_rebound_agent("agent-x") is True

    def test_unmarked_agent_not_rebound(self):
        det = ReboundDetector()
        assert det.is_rebound_agent("agent-y") is False

    def test_get_rebound_agents_returns_set(self):
        det = ReboundDetector()
        det.mark_rebound_agent("a1")
        det.mark_rebound_agent("a2")
        agents = det.get_rebound_agents()
        assert isinstance(agents, set)
        assert "a1" in agents
        assert "a2" in agents

    def test_get_rebound_agents_returns_copy(self):
        det = ReboundDetector()
        det.mark_rebound_agent("a1")
        agents = det.get_rebound_agents()
        agents.add("injected")
        assert det.is_rebound_agent("injected") is False


class TestReboundDetectorBoundary:
    def test_prune_old_records_removes_expired(self):
        det = ReboundDetector(sliding_window_days=10)
        now = time.time()
        det.record("agent-1", "violation", "high", timestamp=now - 20 * 86400)
        det.record("agent-1", "improvement", "low", timestamp=now)
        records = det._records["agent-1"]
        assert all(r.timestamp >= now - 10 * 86400 for r in records)

    def test_empty_agent_records_returns_no_detection(self):
        det = ReboundDetector()
        result = det.analyze_rebound("nonexistent")
        assert result.detected is False

    def test_rebound_with_equal_severity_detected(self):
        det = ReboundDetector(min_rebound_gap_days=1, max_rebound_gap_days=90)
        base = time.time() - 40 * 86400
        det.record("agent-eq", "violation", "high", timestamp=base)
        det.record("agent-eq", "improvement", "low", timestamp=base + 10 * 86400)
        det.record("agent-eq", "rebound", "high", timestamp=base + 40 * 86400)
        assert det.detect_rebound("agent-eq") is True
