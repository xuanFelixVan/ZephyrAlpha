"""风险缓解测试."""
from __future__ import annotations

import pytest
from zephyr.agent_rbac.risk_mitigation import RiskMitigation


class TestRiskMitigation:
    def test_critical_risk(self):
        result = RiskMitigation.assess("data_breach", likelihood=0.9, impact=0.9)
        assert result.risk_level == "CRITICAL"

    def test_low_risk(self):
        result = RiskMitigation.assess("minor_config_change", likelihood=0.1, impact=0.1)
        assert result.risk_level == "LOW"

    def test_playbook_critical(self):
        playbook = RiskMitigation.get_mitigation_playbook("CRITICAL")
        assert playbook["action"] == "BLOCK_AND_ESCALATE"

    def test_playbook_low(self):
        playbook = RiskMitigation.get_mitigation_playbook("LOW")
        assert playbook["action"] == "ALLOW_WITH_METRICS"
