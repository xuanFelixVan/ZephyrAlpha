# [A_test] module_id: SRC-TST-1221 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infra_ops/a2a_protocol/blueprint.md | §3
# [MODULE] tests.test_legacy_governance_adapter
# [INVARIANTS] Tests must not modify production state; All imports guarded by pytest.importorskip
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError → skip; AttributeError → fail
# [TESTS] self

from __future__ import annotations

from unittest.mock import patch

import pytest

legacy_ga = pytest.importorskip(
    "zephyr.infrastructure.a2a_protocol.legacy_governance_adapter",
    reason="legacy_governance_adapter module not available",
)


class TestGovernanceAdapter:
    def test_instantiation(self):
        obj = legacy_ga.GovernanceAdapter()
        assert obj is not None

    def test_verify_pair_allowed(self):
        obj = legacy_ga.GovernanceAdapter()
        record = obj.verify_pair("orchestrator", "worker")
        assert record.granted is True
        assert record.agent_pair == ("orchestrator", "worker")

    def test_verify_pair_reverse_allowed(self):
        obj = legacy_ga.GovernanceAdapter()
        record = obj.verify_pair("worker", "orchestrator")
        assert record.granted is True

    def test_verify_pair_denied(self):
        obj = legacy_ga.GovernanceAdapter()
        record = obj.verify_pair("unknown_a", "unknown_b")
        assert record.granted is False

    def test_escalate_if_needed_granted(self):
        obj = legacy_ga.GovernanceAdapter()
        record = legacy_ga.A2AGovernanceRecord(agent_pair=("a", "b"), action="test", granted=True)
        result = obj.escalate_if_needed(record, "WARN")
        assert result.escalation_level == ""

    def test_escalate_if_needed_not_granted(self):
        obj = legacy_ga.GovernanceAdapter()
        record = legacy_ga.A2AGovernanceRecord(agent_pair=("a", "b"), action="test", granted=False)
        result = obj.escalate_if_needed(record, "CRITICAL")
        assert result.escalation_level == "CRITICAL"

    def test_audit_communication_sets_audit_id(self):
        obj = legacy_ga.GovernanceAdapter()
        record = legacy_ga.A2AGovernanceRecord(agent_pair=("a", "b"), action="test", granted=True)
        result = obj.audit_communication(record, "session_1")
        assert result.audit_id != ""
        assert "session_1" in result.audit_id

    def test_verify_pair_with_content_lsg_unavailable(self):
        obj = legacy_ga.GovernanceAdapter()
        with patch.object(legacy_ga, "_get_lsg", return_value=None):
            record = obj.verify_pair("orchestrator", "worker", "hello")
            assert record.granted is True

    def test_verify_pair_empty_agents(self):
        obj = legacy_ga.GovernanceAdapter()
        record = obj.verify_pair("", "")
        assert record.granted is False


class TestA2AGovernanceRecord:
    def test_default_fields(self):
        rec = legacy_ga.A2AGovernanceRecord(agent_pair=("a", "b"), action="test")
        assert rec.granted is False
        assert rec.escalation_level == ""
        assert rec.audit_id == ""
        assert rec.metadata == {}
