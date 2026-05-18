# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.governance.test_phase4_gate_check
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""Phase 4 门禁验证测试 — G-CT-007/008 全部通过."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def test_gct_007_spec_to_rbac():
    from zephyr.agent_spec.registry import AgentCapability, SpecRegistry
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
    from zephyr.l01_infrastructure.a2a_protocol import A2AAuditor
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
        "zephyr.agent_spec.registry",
        "zephyr.l01_infrastructure.a2a_protocol.legacy_auditor",
        "zephyr.rollback.auditor",
        "zephyr.rollback.budget_tracker",
        "zephyr.escalation_engine.rbac_bridge",
        "zephyr.behavioral_auditor.rollback_bridge",
        "zephyr.budget_enforcer.rbac_bridge",
        "zephyr.audit_trail.drift_bridge",
        "zephyr.agent_rbac.contracts",
        "zephyr.audit_trail.contracts",
        "zephyr.audit_trail.anomaly",
        "zephyr.rollback.contracts",
    ]
    for mod in modules:
        importlib.import_module(mod)
