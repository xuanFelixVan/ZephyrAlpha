# [A_test] module_id: SRC-TST-0456 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_bridges_delegation_bridge
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

from unittest.mock import MagicMock, patch

import pytest

from zephyr.gov_audit.bridges.audit_delegation_bridge import _MAX_DELEGATION_DEPTH, AuditDelegationBridge


@pytest.fixture
def bridge():
    return AuditDelegationBridge()


class TestAuditDelegationBridge:
    def test_instantiation(self):
        b = AuditDelegationBridge()
        assert _MAX_DELEGATION_DEPTH == 5

    def test_record_delegation(self, bridge):
        with patch("zephyr.gov_audit.writer.AuditWriter") as mock_cls:
            mock_writer = MagicMock()
            mock_writer.write.return_value = "hash123"
            mock_cls.return_value = mock_writer
            result = bridge.record_delegation(
                from_agent="agent-a",
                to_agent="agent-b",
                task_id="task-1",
                capability="read",
                depth=1,
            )
            assert result["event_type"] == "delegation_create"
            assert result["from_agent"] == "agent-a"
            assert result["to_agent"] == "agent-b"
            assert result["task_id"] == "task-1"
            assert result["delegation_depth"] == 1
            assert "chain_hash" in result

    def test_record_delegation_write_failure(self, bridge):
        with patch("zephyr.gov_audit.writer.AuditWriter") as mock_cls:
            mock_cls.side_effect = Exception("write failed")
            result = bridge.record_delegation(
                from_agent="a",
                to_agent="b",
                task_id="t1",
            )
            assert result["event_type"] == "delegation_create"
            assert "chain_hash" not in result

    def test_check_depth_anomaly_normal(self, bridge):
        result = bridge.check_depth_anomaly(depth=2, agent_id="a1")
        assert result is None

    def test_check_depth_anomaly_warning(self, bridge):
        result = bridge.check_depth_anomaly(depth=4, agent_id="a1")
        assert result is not None
        assert result["severity"] == "HIGH"
        assert result["details"]["anomaly"] == "delegation_depth_warning"

    def test_check_depth_anomaly_critical(self, bridge):
        result = bridge.check_depth_anomaly(depth=5, agent_id="a1")
        assert result is not None
        assert result["severity"] == "CRITICAL"
        assert result["details"]["anomaly"] == "delegation_depth_exceeded"

    def test_check_depth_anomaly_zero(self, bridge):
        result = bridge.check_depth_anomaly(depth=0)
        assert result is None

    def test_audit_delegation_chain_clean(self, bridge):
        chain = [
            {
                "from_agent": "a",
                "to_agent": "b",
                "depth": 0,
                "from_capabilities": ["read"],
                "to_capabilities": ["read"],
            },
            {
                "from_agent": "b",
                "to_agent": "c",
                "depth": 1,
                "from_capabilities": ["read"],
                "to_capabilities": ["read"],
            },
        ]
        anomalies = bridge.audit_delegation_chain(chain)
        assert len(anomalies) == 0

    def test_audit_delegation_chain_depth_exceeded(self, bridge):
        chain = [
            {
                "from_agent": "a",
                "to_agent": "b",
                "depth": 5,
                "from_capabilities": ["read"],
                "to_capabilities": ["read"],
            },
        ]
        anomalies = bridge.audit_delegation_chain(chain)
        assert len(anomalies) >= 1
        assert any(a["details"]["anomaly"] == "delegation_depth_exceeded" for a in anomalies)

    def test_audit_delegation_chain_privilege_escalation(self, bridge):
        chain = [
            {
                "from_agent": "a",
                "to_agent": "b",
                "depth": 0,
                "from_capabilities": ["read"],
                "to_capabilities": ["read", "write", "delete"],
            },
        ]
        anomalies = bridge.audit_delegation_chain(chain)
        assert len(anomalies) >= 1
        assert any(a["details"]["anomaly"] == "privilege_escalation_via_delegation" for a in anomalies)

    def test_audit_delegation_chain_empty(self, bridge):
        anomalies = bridge.audit_delegation_chain([])
        assert anomalies == []

    def test_verify_delegation_integrity_valid(self, bridge):
        records = [
            {"from_agent": "a", "to_agent": "b", "delegation_depth": 1},
            {"from_agent": "b", "to_agent": "c", "delegation_depth": 2},
        ]
        result = bridge.verify_delegation_integrity(records)
        assert result["valid"] is True
        assert result["issues"] == []

    def test_verify_delegation_integrity_duplicate(self, bridge):
        records = [
            {"from_agent": "a", "to_agent": "b", "delegation_depth": 1},
            {"from_agent": "a", "to_agent": "b", "delegation_depth": 2},
        ]
        result = bridge.verify_delegation_integrity(records)
        assert result["valid"] is False
        assert any("重复委托" in i for i in result["issues"])

    def test_verify_delegation_integrity_depth_exceeded(self, bridge):
        records = [
            {"from_agent": "a", "to_agent": "b", "delegation_depth": 5},
        ]
        result = bridge.verify_delegation_integrity(records)
        assert result["valid"] is False
        assert any("深度超限" in i for i in result["issues"])

    def test_verify_delegation_integrity_empty(self, bridge):
        result = bridge.verify_delegation_integrity([])
        assert result["valid"] is True
