# [A_test] module_id: SRC-TST-0055 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain-autonomy_core/agent-rbac/blueprint.md | §
# [MODULE] tests.agent_rbac.test_risk_mitigation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""风险缓解测试."""
from __future__ import annotations

import pytest
from zephyr.security.access_control.risk_mitigation import RiskMitigation


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
