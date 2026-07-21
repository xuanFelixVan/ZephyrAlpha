# [A_test] module_id: MOD-GOV_a2a_governance_adapter | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] tests.test_a2a_governance_adapter
# [INVARIANTS] Tests must not modify production state; All imports guarded by pytest.importorskip
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError → skip; AttributeError → fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import patch

import pytest

mod = pytest.importorskip(
    "zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_governance_adapter",
    reason="a2a_governance_adapter module not available",
)


class TestA2AGovernanceAdapter:
    def test_instantiation(self):
        obj = mod.A2AGovernanceAdapter()
        assert obj is not None

    def test_scan(self):
        obj = mod.A2AGovernanceAdapter()
        with patch.object(mod, "_get_lsg", return_value=None):
            result = obj.scan("agent_a", "agent_b", "msg_1", "hello")
            assert isinstance(result, list)

    def test_apply_policy(self):
        obj = mod.A2AGovernanceAdapter()
        results = [mod.GovernanceCheckResult(check_id="c1", passed=True)]
        result = obj.apply_policy(results)
        assert result is not None

    def test_scan_empty_content(self):
        obj = mod.A2AGovernanceAdapter()
        with patch.object(mod, "_get_lsg", return_value=None):
            result = obj.scan("a", "b", "m1", "")
            assert isinstance(result, list)


class TestGovernanceCheckResult:
    def test_instantiation(self):
        result = mod.GovernanceCheckResult(check_id="c1", passed=True)
        assert result is not None
        assert result.passed is True
