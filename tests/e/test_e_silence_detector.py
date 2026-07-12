# [A_test] module_id: SRC-TST-0822 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_silence_detector
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

from zephyr.gov_drift.silence_detector import SilenceDetector


class TestSilenceDetectorInit:
    def test_default_state(self):
        sd = SilenceDetector()
        assert sd._last_activity == {}
        assert sd._timeout_s == 1800


class TestSilenceDetectorRecordActivity:
    def test_sets_timestamp(self):
        sd = SilenceDetector()
        sd.record_activity("agent-1")
        assert "agent-1" in sd._last_activity
        assert sd._last_activity["agent-1"] > 0

    def test_multiple_agents(self):
        sd = SilenceDetector()
        sd.record_activity("agent-1")
        sd.record_activity("agent-2")
        assert len(sd._last_activity) == 2

    def test_overwrite_existing(self):
        sd = SilenceDetector()
        sd.record_activity("agent-1")
        first = sd._last_activity["agent-1"]
        time.sleep(0.01)
        sd.record_activity("agent-1")
        assert sd._last_activity["agent-1"] > first


class TestSilenceDetectorDetectSilence:
    def test_empty_no_silence(self):
        sd = SilenceDetector()
        assert sd.detect_silence() == []

    def test_active_agent_not_silent(self):
        sd = SilenceDetector()
        sd.record_activity("agent-1")
        assert sd.detect_silence() == []


class TestSilenceDetectorIsSilent:
    def test_unknown_agent_is_silent(self):
        sd = SilenceDetector()
        assert sd.is_silent("unknown") is True

    def test_recorded_agent_not_silent(self):
        sd = SilenceDetector()
        sd.record_activity("agent-1")
        assert sd.is_silent("agent-1") is False
