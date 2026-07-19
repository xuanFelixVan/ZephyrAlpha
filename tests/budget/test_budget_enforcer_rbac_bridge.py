# [A_test] module_id: SRC-TST-0463 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §12
# [MODULE] tests.test_budget_enforcer_rbac_bridge
# [INVARIANTS] RBAC配额降级规则不可绕过;权限降级必须审计
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/budget-enforcer/blueprint.md
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试异常必须包含 budget_context 和 operation_id
# [TESTS] tests/test_budget_enforcer_rbac_bridge.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.governance.agent_spec.rbac_bridge import BudgetRBACBridge


class TestBudgetRBACBridgeInstantiation:
    def test_creates_instance_without_args(self):
        bridge = BudgetRBACBridge()
        assert bridge is not None

    def test_instance_is_correct_type(self):
        bridge = BudgetRBACBridge()
        assert isinstance(bridge, BudgetRBACBridge)

    def test_multiple_instances_are_distinct(self):
        a = BudgetRBACBridge()
        b = BudgetRBACBridge()
        assert a is not b


class TestCheckBudgetWithinLimit:
    def test_returns_allow_when_under_limit(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent-1", token_used=50, token_limit=100)
        assert result["action"] == "ALLOW"

    def test_returns_allow_when_at_exact_limit(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent-1", token_used=100, token_limit=100)
        assert result["action"] == "ALLOW"

    def test_returns_correct_fields(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent-1", token_used=50, token_limit=100)
        assert result["agent_id"] == "agent-1"
        assert result["token_used"] == 50
        assert result["token_limit"] == 100
        assert result["exceeded"] is False
        assert result["action"] == "ALLOW"

    def test_zero_usage_within_limit(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent-1", token_used=0, token_limit=100)
        assert result["exceeded"] is False
        assert result["action"] == "ALLOW"


class TestCheckBudgetExceeded:
    def test_returns_revoke_write_when_over_limit(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent-1", token_used=150, token_limit=100)
        assert result["action"] == "REVOKE_WRITE"

    def test_returns_exceeded_true_when_over_limit(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent-1", token_used=150, token_limit=100)
        assert result["exceeded"] is True

    def test_returns_correct_fields_when_exceeded(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent-1", token_used=200, token_limit=100)
        assert result["agent_id"] == "agent-1"
        assert result["token_used"] == 200
        assert result["token_limit"] == 100
        assert result["exceeded"] is True
        assert result["action"] == "REVOKE_WRITE"

    def test_one_over_limit(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent-1", token_used=101, token_limit=100)
        assert result["exceeded"] is True
        assert result["action"] == "REVOKE_WRITE"


class TestCheckBudgetBoundaryCases:
    def test_empty_agent_id(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("", token_used=50, token_limit=100)
        assert result["agent_id"] == ""
        assert result["action"] == "ALLOW"

    def test_zero_token_limit_with_zero_usage(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent-1", token_used=0, token_limit=0)
        assert result["exceeded"] is False
        assert result["action"] == "ALLOW"

    def test_zero_token_limit_with_nonzero_usage(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent-1", token_used=1, token_limit=0)
        assert result["exceeded"] is True
        assert result["action"] == "REVOKE_WRITE"

    def test_large_token_values(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent-1", token_used=999999999, token_limit=1000000000)
        assert result["exceeded"] is False
        assert result["action"] == "ALLOW"

    def test_negative_token_used(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent-1", token_used=-1, token_limit=100)
        assert result["exceeded"] is False
        assert result["action"] == "ALLOW"

    def test_negative_token_limit(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent-1", token_used=0, token_limit=-1)
        assert result["exceeded"] is True
        assert result["action"] == "REVOKE_WRITE"

    def test_none_agent_id_stored_as_none(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget(None, token_used=50, token_limit=100)
        assert result["agent_id"] is None
        assert result["action"] == "ALLOW"

    def test_none_token_used_raises(self):
        bridge = BudgetRBACBridge()
        with pytest.raises(TypeError):
            bridge.evaluate_budget("agent-1", token_used=None, token_limit=100)

    def test_none_token_limit_raises(self):
        bridge = BudgetRBACBridge()
        with pytest.raises(TypeError):
            bridge.evaluate_budget("agent-1", token_used=50, token_limit=None)


class TestCheckBudgetReturnStructure:
    def test_result_has_five_keys(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent-1", token_used=50, token_limit=100)
        expected_keys = {"agent_id", "token_used", "token_limit", "exceeded", "action"}
        assert set(result.keys()) == expected_keys

    def test_exceeded_is_bool(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent-1", token_used=50, token_limit=100)
        assert isinstance(result["exceeded"], bool)

    def test_action_is_string(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent-1", token_used=50, token_limit=100)
        assert isinstance(result["action"], str)

    def test_agent_id_preserved(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("special-agent-42", token_used=10, token_limit=100)
        assert result["agent_id"] == "special-agent-42"
