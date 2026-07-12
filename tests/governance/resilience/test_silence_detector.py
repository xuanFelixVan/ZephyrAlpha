# [A_test] module_id: SRC-TST-1599 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_silence_detector
# [INVARIANTS] test_coverage>=2_public_methods;boundary_tests_included
# [MODIFY-GUARD] sync_with_source_on_refactor
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest_exit_0_on_pass
# [TESTS] tests/test_silence_detector.py
# [TTL] task_bound

from __future__ import annotations

import time

from zephyr.gov_drift.silence_detector import SilenceDetector


class TestSilenceDetector:
    def setup_method(self):
        self.detector = SilenceDetector()

    def test_record_activity_creates_entry(self):
        self.detector.record_activity("agent-1")
        assert "agent-1" in self.detector._last_activity

    def test_record_activity_updates_timestamp(self):
        self.detector.record_activity("agent-1")
        t1 = self.detector._last_activity["agent-1"]
        time.sleep(0.01)
        self.detector.record_activity("agent-1")
        t2 = self.detector._last_activity["agent-1"]
        assert t2 > t1

    def test_detect_silence_no_agents(self):
        result = self.detector.detect_silence()
        assert result == []

    def test_detect_silence_recent_activity(self):
        self.detector.record_activity("agent-1")
        result = self.detector.detect_silence()
        assert result == []

    def test_detect_silence_expired_activity(self):
        past = time.time() - 2000
        self.detector._last_activity["agent-1"] = past
        result = self.detector.detect_silence()
        assert "agent-1" in result

    def test_detect_silence_mixed(self):
        self.detector.record_activity("active-agent")
        self.detector._last_activity["silent-agent"] = time.time() - 2000
        result = self.detector.detect_silence()
        assert "silent-agent" in result
        assert "active-agent" not in result

    def test_is_silent_no_record(self):
        assert self.detector.is_silent("unknown") is True

    def test_is_silent_recent_activity(self):
        self.detector.record_activity("agent-1")
        assert self.detector.is_silent("agent-1") is False

    def test_is_silent_expired_activity(self):
        self.detector._last_activity["agent-1"] = time.time() - 2000
        assert self.detector.is_silent("agent-1") is True

    def test_timeout_default(self):
        assert self.detector._timeout_s == 1800

    def test_multiple_agents_independent(self):
        self.detector.record_activity("a1")
        self.detector._last_activity["a2"] = time.time() - 2000
        assert self.detector.is_silent("a1") is False
        assert self.detector.is_silent("a2") is True
