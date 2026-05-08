"""cybersec 2026 独立测试."""
from __future__ import annotations

import pytest
from zephyr.agent_rbac.cybersec_2026_guard import Cybersec2026Guard


class TestCybersec2026:
    def test_no_threat(self):
        guard = Cybersec2026Guard()
        result = guard.scan({"safe": True})
        assert result.detected is False

    def test_agent_supply_chain(self):
        guard = Cybersec2026Guard()
        result = guard.scan({"unsigned_agent_package": True})
        assert result.detected is True

    def test_multi_threat_high_severity(self):
        guard = Cybersec2026Guard()
        result = guard.scan({"untrusted_hub": True, "hidden_training_trigger": True})
        assert result.severity == "HIGH"
