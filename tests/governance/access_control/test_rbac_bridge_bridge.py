# [A_test] module_id: SRC-TST-1429 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_rbac_bridge_bridge
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.agent_spec.rbac_bridge import BudgetRBACBridge


class TestBudgetRBACBridgeInit:
    def test_creation(self):
        bridge = BudgetRBACBridge()
        assert bridge is not None


class TestCheckBudget:
    def test_within_budget(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent1", 50, 100)
        assert result["agent_id"] == "agent1"
        assert result["token_used"] == 50
        assert result["token_limit"] == 100
        assert result["exceeded"] is False
        assert result["action"] == "ALLOW"

    def test_exceeded_budget(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent2", 150, 100)
        assert result["exceeded"] is True
        assert result["action"] == "REVOKE_WRITE"

    def test_exact_limit(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent3", 100, 100)
        assert result["exceeded"] is False
        assert result["action"] == "ALLOW"

    def test_zero_usage(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent4", 0, 100)
        assert result["exceeded"] is False
        assert result["action"] == "ALLOW"

    def test_zero_limit_zero_usage(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent5", 0, 0)
        assert result["exceeded"] is False
        assert result["action"] == "ALLOW"

    def test_zero_limit_nonzero_usage(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent6", 1, 0)
        assert result["exceeded"] is True
        assert result["action"] == "REVOKE_WRITE"

    def test_result_has_all_keys(self):
        bridge = BudgetRBACBridge()
        result = bridge.evaluate_budget("agent7", 10, 50)
        expected_keys = {"agent_id", "token_used", "token_limit", "exceeded", "action"}
        assert set(result.keys()) == expected_keys

    def test_different_agents_independent(self):
        bridge = BudgetRBACBridge()
        r1 = bridge.evaluate_budget("a1", 50, 100)
        r2 = bridge.evaluate_budget("a2", 200, 100)
        assert r1["action"] == "ALLOW"
        assert r2["action"] == "REVOKE_WRITE"
