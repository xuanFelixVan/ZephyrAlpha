# [A_test] module_id: SRC-TST-0159 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-316 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.infrastructure.test_rebound_detector
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for Reward Hacking Rebound Detector — §2.37-D, Blind spot #161."""

from __future__ import annotations

import time

from zephyr.gov_drift.reward_hacking_rebound_detector import (
    ReboundDetector,
    ReboundSeverity,
)


class TestReboundSeverityOrdering:
    def test_severity_ordering(self):
        assert ReboundSeverity.CRITICAL >= ReboundSeverity.HIGH
        assert ReboundSeverity.HIGH >= ReboundSeverity.MEDIUM
        assert ReboundSeverity.MEDIUM >= ReboundSeverity.LOW
        assert ReboundSeverity.CRITICAL >= ReboundSeverity.LOW

    def test_equal_severity(self):
        assert ReboundSeverity.HIGH >= ReboundSeverity.HIGH

    def test_lower_severity_not_gte(self):
        assert not (ReboundSeverity.LOW >= ReboundSeverity.HIGH)


class TestReboundDetectorBasic:
    def test_no_records_no_rebound(self):
        rd = ReboundDetector()
        assert not rd.detect_rebound("agent-1")

    def test_single_violation_no_rebound(self):
        rd = ReboundDetector()
        rd.record("agent-1", "violation", severity="high")
        assert not rd.detect_rebound("agent-1")

    def test_violation_plus_improvement_no_rebound(self):
        rd = ReboundDetector()
        rd.record("agent-1", "violation", severity="high")
        rd.record("agent-1", "improvement", severity="low")
        assert not rd.detect_rebound("agent-1")


class TestReboundDetectorThreePhase:
    def test_full_three_phase_rebound(self):
        rd = ReboundDetector(sliding_window_days=90, min_rebound_gap_days=30, max_rebound_gap_days=90)
        now = time.time()
        phase_i_time = now - 60 * 86400
        phase_ii_time = now - 30 * 86400
        phase_iii_time = now

        rd.record("agent-1", "violation", severity="high", timestamp=phase_i_time)
        rd.record("agent-1", "improvement", severity="low", timestamp=phase_ii_time)
        rd.record("agent-1", "rebound", severity="high", timestamp=phase_iii_time)

        assert rd.detect_rebound("agent-1")

    def test_rebound_with_higher_severity(self):
        rd = ReboundDetector(sliding_window_days=90, min_rebound_gap_days=30, max_rebound_gap_days=90)
        now = time.time()
        rd.record("agent-1", "violation", severity="medium", timestamp=now - 50 * 86400)
        rd.record("agent-1", "improvement", severity="low", timestamp=now - 25 * 86400)
        rd.record("agent-1", "rebound", severity="critical", timestamp=now)

        assert rd.detect_rebound("agent-1")

    def test_rebound_with_lower_severity_not_detected(self):
        rd = ReboundDetector(sliding_window_days=90, min_rebound_gap_days=30, max_rebound_gap_days=90)
        now = time.time()
        rd.record("agent-1", "violation", severity="critical", timestamp=now - 50 * 86400)
        rd.record("agent-1", "improvement", severity="low", timestamp=now - 25 * 86400)
        rd.record("agent-1", "rebound", severity="low", timestamp=now)

        assert not rd.detect_rebound("agent-1")


class TestReboundDetectorWindowConstraints:
    def test_rebound_too_soon_not_detected(self):
        rd = ReboundDetector(sliding_window_days=90, min_rebound_gap_days=30, max_rebound_gap_days=90)
        now = time.time()
        rd.record("agent-1", "violation", severity="high", timestamp=now - 10 * 86400)
        rd.record("agent-1", "improvement", severity="low", timestamp=now - 5 * 86400)
        rd.record("agent-1", "rebound", severity="high", timestamp=now)

        assert not rd.detect_rebound("agent-1")

    def test_rebound_too_late_not_detected(self):
        rd = ReboundDetector(sliding_window_days=90, min_rebound_gap_days=30, max_rebound_gap_days=90)
        now = time.time()
        rd.record("agent-1", "violation", severity="high", timestamp=now - 100 * 86400)
        rd.record("agent-1", "improvement", severity="low", timestamp=now - 50 * 86400)
        rd.record("agent-1", "rebound", severity="high", timestamp=now)

        assert not rd.detect_rebound("agent-1")

    def test_rebound_outside_sliding_window_pruned(self):
        rd = ReboundDetector(sliding_window_days=90, min_rebound_gap_days=30, max_rebound_gap_days=90)
        now = time.time()
        rd.record("agent-1", "violation", severity="high", timestamp=now - 120 * 86400)
        result = rd.analyze_rebound("agent-1")
        assert not result.detected


class TestReboundDetectorAnalyzeRebound:
    def test_analyze_returns_detection_details(self):
        rd = ReboundDetector(sliding_window_days=90, min_rebound_gap_days=30, max_rebound_gap_days=90)
        now = time.time()
        phase_i_time = now - 60 * 86400
        phase_ii_time = now - 30 * 86400
        phase_iii_time = now

        rd.record("agent-1", "violation", severity="high", description="Phase I", timestamp=phase_i_time)
        rd.record("agent-1", "improvement", severity="low", description="Phase II", timestamp=phase_ii_time)
        rd.record("agent-1", "rebound", severity="critical", description="Phase III", timestamp=phase_iii_time)

        result = rd.analyze_rebound("agent-1")
        assert result.detected
        assert result.agent_id == "agent-1"
        assert result.phase_i_severity == ReboundSeverity.HIGH
        assert result.phase_iii_severity == ReboundSeverity.CRITICAL
        assert 55 < result.window_days < 65
        assert len(result.evidence) == 3

    def test_analyze_no_rebound_returns_empty(self):
        rd = ReboundDetector()
        result = rd.analyze_rebound("unknown")
        assert not result.detected


class TestReboundAgentTracking:
    def test_mark_and_check_rebound_agent(self):
        rd = ReboundDetector()
        rd.mark_rebound_agent("agent-1")
        assert rd.is_rebound_agent("agent-1")
        assert not rd.is_rebound_agent("agent-2")

    def test_get_rebound_agents(self):
        rd = ReboundDetector()
        rd.mark_rebound_agent("agent-1")
        rd.mark_rebound_agent("agent-2")
        assert rd.get_rebound_agents() == {"agent-1", "agent-2"}


class TestReboundDetectorMultipleAgents:
    def test_independent_agent_tracking(self):
        rd = ReboundDetector(sliding_window_days=90, min_rebound_gap_days=30, max_rebound_gap_days=90)
        now = time.time()
        rd.record("agent-1", "violation", severity="high", timestamp=now - 50 * 86400)
        rd.record("agent-1", "improvement", severity="low", timestamp=now - 25 * 86400)
        rd.record("agent-1", "rebound", severity="high", timestamp=now)

        assert rd.detect_rebound("agent-1")
        assert not rd.detect_rebound("agent-2")


class TestReboundDetectorIntegration:
    def test_engine_hook_with_rebound_detector(self):
        from zephyr.governance.escalation.escalation_engine import EscalationEngine

        engine = EscalationEngine("rebound-test", hooks_enabled=True)
        rd = engine._extension_detectors.get("ReboundDetector")
        assert rd is not None, "ReboundDetector should be loaded as extension detector"

    def test_rebound_category_triggers_l4(self):
        from zephyr.governance.escalation.escalation_engine import EscalationEngine
        from zephyr.governance.escalation.escalation_models import RuleCategory

        engine = EscalationEngine("rebound-test", hooks_enabled=False)
        event = engine.evaluate(RuleCategory.REWARD_HACKING_REBOUND, "reward hacking rebound detected")
        assert event.level.value >= 4

    def test_backward_compat_detect_rebound_method(self):
        rd = ReboundDetector(sliding_window_days=90, min_rebound_gap_days=30, max_rebound_gap_days=90)
        now = time.time()
        rd.record("agent-1", "violation", severity="high", timestamp=now - 50 * 86400)
        rd.record("agent-1", "improvement", severity="low", timestamp=now - 25 * 86400)
        rd.record("agent-1", "rebound", severity="high", timestamp=now)
        assert rd.detect_rebound("agent-1")
