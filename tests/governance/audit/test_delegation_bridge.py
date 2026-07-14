# [A_test] module_id: SRC-TST-0730 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_delegation_bridge
# [INVARIANTS] AuditDelegationBridge depth anomaly detection; chain integrity
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass; exit non-zero on fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import patch

from zephyr.gov_audit.bridges.audit_delegation_bridge import AuditDelegationBridge


class TestAuditDelegationBridgeInstantiation:
    def test_creation(self):
        bridge = AuditDelegationBridge()
        assert bridge is not None


class TestRecordDelegation:
    def test_record_returns_dict(self):
        bridge = AuditDelegationBridge()
        with patch("zephyr.gov_audit.delegation_bridge.AuditWriter", create=True):
            with patch("zephyr.gov_audit.writer.AuditWriter", create=True):
                result = bridge.record_delegation(
                    from_agent="a0",
                    to_agent="a1",
                    task_id="task-1",
                    capability="write",
                    depth=1,
                )
        assert result["from_agent"] == "a0"
        assert result["to_agent"] == "a1"
        assert result["task_id"] == "task-1"
        assert result["capability"] == "write"
        assert result["delegation_depth"] == 1
        assert result["event_type"] == "delegation_create"
        assert "timestamp" in result

    def test_record_delegation_handles_writer_failure(self):
        bridge = AuditDelegationBridge()
        with patch(
            "zephyr.gov_audit.delegation_bridge.AuditWriter", side_effect=Exception("fail"), create=True
        ):
            result = bridge.record_delegation(
                from_agent="a0",
                to_agent="a1",
                task_id="task-1",
            )
        assert result["from_agent"] == "a0"
        assert "chain_hash" not in result


class TestCheckDepthAnomaly:
    def test_normal_depth_returns_none(self):
        bridge = AuditDelegationBridge()
        result = bridge.check_depth_anomaly(depth=3, agent_id="a1")
        assert result is None

    def test_warning_depth(self):
        bridge = AuditDelegationBridge()
        result = bridge.check_depth_anomaly(depth=4, agent_id="a1")
        assert result is not None
        assert result["severity"] == "HIGH"
        assert result["details"]["anomaly"] == "delegation_depth_warning"

    def test_critical_depth(self):
        bridge = AuditDelegationBridge()
        result = bridge.check_depth_anomaly(depth=5, agent_id="a1")
        assert result is not None
        assert result["severity"] == "CRITICAL"
        assert result["details"]["anomaly"] == "delegation_depth_exceeded"

    def test_zero_depth_returns_none(self):
        bridge = AuditDelegationBridge()
        result = bridge.check_depth_anomaly(depth=0)
        assert result is None


class TestAuditDelegationChain:
    def test_valid_chain_no_anomalies(self):
        bridge = AuditDelegationBridge()
        chain = [
            {
                "from_agent": "a0",
                "to_agent": "a1",
                "depth": 1,
                "from_capabilities": ["read", "write"],
                "to_capabilities": ["read"],
            },
            {
                "from_agent": "a1",
                "to_agent": "a2",
                "depth": 2,
                "from_capabilities": ["read"],
                "to_capabilities": ["read"],
            },
        ]
        anomalies = bridge.audit_delegation_chain(chain)
        assert len(anomalies) == 0

    def test_depth_exceeded_anomaly(self):
        bridge = AuditDelegationBridge()
        chain = [
            {"from_agent": "a0", "to_agent": "a1", "depth": 5},
        ]
        anomalies = bridge.audit_delegation_chain(chain)
        depth_anomalies = [a for a in anomalies if a["details"]["anomaly"] == "delegation_depth_exceeded"]
        assert len(depth_anomalies) >= 1

    def test_privilege_escalation_anomaly(self):
        bridge = AuditDelegationBridge()
        chain = [
            {
                "from_agent": "a0",
                "to_agent": "a1",
                "depth": 1,
                "from_capabilities": ["read"],
                "to_capabilities": ["read", "write", "admin"],
            },
        ]
        anomalies = bridge.audit_delegation_chain(chain)
        priv_anomalies = [a for a in anomalies if a["details"]["anomaly"] == "privilege_escalation_via_delegation"]
        assert len(priv_anomalies) == 1

    def test_empty_chain_no_anomalies(self):
        bridge = AuditDelegationBridge()
        anomalies = bridge.audit_delegation_chain([])
        assert len(anomalies) == 0


class TestVerifyDelegationIntegrity:
    def test_valid_records(self):
        bridge = AuditDelegationBridge()
        records = [
            {"from_agent": "a0", "to_agent": "a1", "delegation_depth": 1},
            {"from_agent": "a1", "to_agent": "a2", "delegation_depth": 2},
        ]
        result = bridge.verify_delegation_integrity(records)
        assert result["valid"] is True
        assert len(result["issues"]) == 0

    def test_duplicate_delegation(self):
        bridge = AuditDelegationBridge()
        records = [
            {"from_agent": "a0", "to_agent": "a1", "delegation_depth": 1},
            {"from_agent": "a0", "to_agent": "a1", "delegation_depth": 1},
        ]
        result = bridge.verify_delegation_integrity(records)
        assert result["valid"] is False
        assert any("重复委托" in issue for issue in result["issues"])

    def test_depth_exceeded_in_records(self):
        bridge = AuditDelegationBridge()
        records = [
            {"from_agent": "a0", "to_agent": "a1", "delegation_depth": 5},
        ]
        result = bridge.verify_delegation_integrity(records)
        assert result["valid"] is False
        assert any("委托深度超限" in issue for issue in result["issues"])

    def test_empty_records_valid(self):
        bridge = AuditDelegationBridge()
        result = bridge.verify_delegation_integrity([])
        assert result["valid"] is True
