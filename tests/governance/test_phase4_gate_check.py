"""Phase 4 门禁验证测试 — G-CT-007/008 全部通过."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def test_gct_007_spec_to_rbac():
    from zephyr.governance.agent_spec.registry import AgentCapability, SpecRegistry
    registry = SpecRegistry()
    cap = AgentCapability(
        agent_id="agent-spec-001",
        capabilities=["read_config", "write_log"],
        version="1.0.0",
        spec_hash="abc123",
    )
    registry.register(cap)
    result = registry.get("agent-spec-001")
    assert result is not None
    assert result.capabilities == ["read_config", "write_log"]


def test_gct_008_a2a_to_audit():
    from zephyr.governance.a2a.auditor import A2AAuditor
    auditor = A2AAuditor()
    record = auditor.log_message(
        from_agent="agent-a",
        to_agent="agent-b",
        message_type="capability_query",
        session_id="session-test",
    )
    assert record["agent_id"] == "agent-a"
    assert record["metadata"]["type"] == "capability_query"


def test_phase4_gate_all_contracts_exist():
    import importlib
    modules = [
        "zephyr.governance.agent_spec.registry",
        "zephyr.governance.a2a.auditor",
        "zephyr.governance.rollback.auditor",
        "zephyr.governance.rollback.budget_tracker",
        "zephyr.governance.escalation.rbac_bridge",
        "zephyr.governance.drift_detector.rollback_bridge",
        "zephyr.governance.budget_enforcer.rbac_bridge",
        "zephyr.governance.audit_trail.drift_bridge",
        "zephyr.governance.agent_rbac.contracts",
        "zephyr.governance.audit_trail.contracts",
        "zephyr.governance.audit_trail.anomaly",
        "zephyr.governance.rollback.contracts",
    ]
    for mod in modules:
        importlib.import_module(mod)
