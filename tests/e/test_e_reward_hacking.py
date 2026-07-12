# [A_test] module_id: SRC-TST-0818 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_reward_hacking
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import time

from zephyr.gov_drift.reward_hacking_rebound_detector import (
    BehaviorRecord,
    ReboundDetection,
    ReboundDetector,
    ReboundPhase,
    ReboundSeverity,
)


class TestReboundPhase:
    def test_three_phases(self):
        assert len(ReboundPhase) == 3

    def test_values(self):
        assert ReboundPhase.VIOLATION.value == "violation"
        assert ReboundPhase.IMPROVEMENT.value == "improvement"
        assert ReboundPhase.REBOUND.value == "rebound"


class TestReboundSeverity:
    def test_four_levels(self):
        assert len(ReboundSeverity) == 4

    def test_ordering(self):
        assert ReboundSeverity.CRITICAL >= ReboundSeverity.HIGH
        assert ReboundSeverity.HIGH >= ReboundSeverity.MEDIUM
        assert ReboundSeverity.MEDIUM >= ReboundSeverity.LOW
        assert ReboundSeverity.LOW >= ReboundSeverity.LOW


class TestBehaviorRecord:
    def test_instantiation(self):
        now = time.time()
        rec = BehaviorRecord(
            agent_id="agent-1",
            phase=ReboundPhase.VIOLATION,
            severity=ReboundSeverity.HIGH,
            timestamp=now,
            description="violated policy",
        )
        assert rec.agent_id == "agent-1"
        assert rec.phase == ReboundPhase.VIOLATION
        assert rec.severity == ReboundSeverity.HIGH
        assert rec.timestamp == now


class TestReboundDetection:
    def test_default_not_detected(self):
        rd = ReboundDetection()
        assert rd.detected is False


class TestReboundDetector:
    def test_record(self):
        rd = ReboundDetector()
        now = time.time()
        rd.record("agent-1", "violation", "high", timestamp=now)
        assert "agent-1" in rd._records
        assert len(rd._records["agent-1"]) == 1

    def test_detect_rebound_no_data(self):
        rd = ReboundDetector()
        assert rd.detect_rebound("agent-1") is False

    def test_analyze_rebound_incomplete_phases(self):
        rd = ReboundDetector()
        now = time.time()
        rd.record("agent-1", "violation", "high", timestamp=now)
        rd.record("agent-1", "improvement", "medium", timestamp=now + 86400)
        result = rd.analyze_rebound("agent-1")
        assert result.detected is False

    def test_mark_and_get_rebound_agents(self):
        rd = ReboundDetector()
        rd.mark_rebound_agent("agent-1")
        assert rd.is_rebound_agent("agent-1") is True
        assert rd.get_rebound_agents() == {"agent-1"}

    def test_unknown_agent_not_rebound(self):
        rd = ReboundDetector()
        assert rd.is_rebound_agent("unknown") is False
