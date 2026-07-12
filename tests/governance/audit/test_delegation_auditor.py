# [A_test] module_id: SRC-TST-0729 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_delegation_auditor
# [INVARIANTS] DelegationChainAuditor detects depth/escalation/broken chain
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass; exit non-zero on fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.gov_audit.delegation_auditor import (
    DelegationAuditResult,
    DelegationChainAuditor,
    DelegationNode,
    EscalationType,
)


class TestEscalationType:
    def test_enum_values(self):
        assert EscalationType.DEPTH_EXCEEDED == "depth_exceeded"
        assert EscalationType.PRIVILEGE_ESCALATION == "privilege_escalation"
        assert EscalationType.BROKEN_CHAIN == "broken_chain"
        assert EscalationType.UNAUTHORIZED_DELEGATOR == "unauthorized_delegator"
        assert EscalationType.SELF_DELEGATION == "self_delegation"


class TestDelegationNode:
    def test_default_values(self):
        node = DelegationNode()
        assert node.agent_id == ""
        assert node.permission_level == 0
        assert node.delegated_by == ""

    def test_custom_values(self):
        node = DelegationNode(
            agent_id="agent-1",
            permission_level=5,
            delegated_by="agent-0",
            delegated_at="2026-05-22T10:00:00Z",
            signature="sig123",
        )
        assert node.agent_id == "agent-1"
        assert node.permission_level == 5


class TestDelegationAuditResult:
    def test_default_values(self):
        result = DelegationAuditResult()
        assert result.is_valid is True
        assert result.chain_depth == 0
        assert result.escalations == []
        assert result.escalation_types == []


class TestDelegationChainAuditor:
    def test_valid_chain(self):
        auditor = DelegationChainAuditor()
        chain = [
            DelegationNode(agent_id="a0", permission_level=5, delegated_by=""),
            DelegationNode(agent_id="a1", permission_level=3, delegated_by="a0"),
            DelegationNode(agent_id="a2", permission_level=1, delegated_by="a1"),
        ]
        result = auditor.audit_chain(chain)
        assert result.is_valid is True
        assert result.chain_depth == 3
        assert len(result.escalations) == 0

    def test_depth_exceeded(self):
        auditor = DelegationChainAuditor(max_depth=3)
        chain = [
            DelegationNode(agent_id=f"a{i}", permission_level=5 - i, delegated_by=f"a{i - 1}" if i > 0 else "")
            for i in range(5)
        ]
        result = auditor.audit_chain(chain)
        assert result.is_valid is False
        assert EscalationType.DEPTH_EXCEEDED in result.escalation_types

    def test_privilege_escalation(self):
        auditor = DelegationChainAuditor()
        chain = [
            DelegationNode(agent_id="a0", permission_level=2, delegated_by=""),
            DelegationNode(agent_id="a1", permission_level=5, delegated_by="a0"),
        ]
        result = auditor.audit_chain(chain)
        assert result.is_valid is False
        assert EscalationType.PRIVILEGE_ESCALATION in result.escalation_types

    def test_broken_chain(self):
        auditor = DelegationChainAuditor()
        chain = [
            DelegationNode(agent_id="a0", permission_level=5, delegated_by=""),
            DelegationNode(agent_id="a1", permission_level=3, delegated_by="a_other"),
        ]
        result = auditor.audit_chain(chain)
        assert result.is_valid is False
        assert EscalationType.BROKEN_CHAIN in result.escalation_types

    def test_self_delegation(self):
        auditor = DelegationChainAuditor()
        chain = [
            DelegationNode(agent_id="a0", permission_level=5, delegated_by=""),
            DelegationNode(agent_id="a1", permission_level=3, delegated_by="a1"),
        ]
        result = auditor.audit_chain(chain)
        assert result.is_valid is False
        assert EscalationType.SELF_DELEGATION in result.escalation_types

    def test_empty_chain(self):
        auditor = DelegationChainAuditor()
        result = auditor.audit_chain([])
        assert result.is_valid is True
        assert result.chain_depth == 0

    def test_single_node_chain(self):
        auditor = DelegationChainAuditor()
        chain = [DelegationNode(agent_id="a0", permission_level=5, delegated_by="")]
        result = auditor.audit_chain(chain)
        assert result.is_valid is True
        assert result.chain_depth == 1

    def test_audit_chain_with_dicts(self):
        auditor = DelegationChainAuditor()
        chain = [
            {"agent_id": "a0", "permission_level": 5, "delegated_by": ""},
            {"agent_id": "a1", "permission_level": 3, "delegated_by": "a0"},
        ]
        result = auditor.audit_chain(chain)
        assert result.is_valid is True

    def test_audit_chain_invalid_type_raises(self):
        auditor = DelegationChainAuditor()
        with pytest.raises(TypeError):
            auditor.audit_chain(["not_a_dict_or_node"])


class TestDelegationChainAuditorDetectEscalation:
    def test_detect_escalation_valid(self):
        auditor = DelegationChainAuditor()
        chain = [
            DelegationNode(agent_id="a0", permission_level=5, delegated_by=""),
            DelegationNode(agent_id="a1", permission_level=3, delegated_by="a0"),
        ]
        escalations = auditor.detect_escalation(chain)
        assert len(escalations) == 0

    def test_detect_escalation_depth_exceeded(self):
        auditor = DelegationChainAuditor(max_depth=2)
        chain = [
            DelegationNode(agent_id=f"a{i}", permission_level=5 - i, delegated_by=f"a{i - 1}" if i > 0 else "")
            for i in range(4)
        ]
        escalations = auditor.detect_escalation(chain)
        depth_escalations = [e for e in escalations if e[1] == EscalationType.DEPTH_EXCEEDED]
        assert len(depth_escalations) > 0

    def test_detect_escalation_returns_tuples(self):
        auditor = DelegationChainAuditor()
        chain = [
            DelegationNode(agent_id="a0", permission_level=2, delegated_by=""),
            DelegationNode(agent_id="a1", permission_level=5, delegated_by="a0"),
        ]
        escalations = auditor.detect_escalation(chain)
        assert len(escalations) == 1
        idx, etype, desc = escalations[0]
        assert isinstance(idx, int)
        assert isinstance(etype, EscalationType)
        assert isinstance(desc, str)
