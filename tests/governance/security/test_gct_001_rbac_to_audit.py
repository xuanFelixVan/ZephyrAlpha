# [A_test] module_id: SRC-TST-0124 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-281 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_gct_001_rbac_to_audit
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""G-CT-001 集成测试 — RBAC→Audit 端到端数据流通."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def test_audit_write_basic():
    from zephyr.gov_audit.contracts import AuditWriter

    record = AuditWriter.write(
        agent_id="agent-001",
        permission="read",
        resource="/data/config.yaml",
        decision_basis="RBAC: agent-001 perm=read res=/data/config.yaml",
        session_id="session-20260507-test",
        granted=True,
    )
    assert record["agent_id"] == "agent-001"
    assert record["permission"] == "read"
    assert record["granted"] is True
    assert record["session_id"] == "session-20260507-test"


def test_rbac_to_audit_bridge():
    from zephyr.security.access_control.contracts import RBACAuditBridge

    bridge = RBACAuditBridge()
    result = bridge.check_and_log(
        agent_id="agent-001",
        permission="read",
        resource="/data/config.yaml",
        session_id="session-test",
    )
    assert "granted" in result
    assert "audit_record" in result
    assert result["audit_record"]["agent_id"] == "agent-001"


def test_denied_permission_logged():
    from zephyr.security.access_control.contracts import RBACAuditBridge

    bridge = RBACAuditBridge()
    result = bridge.check_and_log(
        agent_id="agent-002",
        permission="delete",
        resource="/data/secrets.yaml",
    )
    assert result["granted"] is False
    assert result["audit_record"]["granted"] is False
