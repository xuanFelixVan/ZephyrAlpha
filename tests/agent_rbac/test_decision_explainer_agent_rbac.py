# [A_test] module_id: MOD-GOV_decision_explainer_agent_rbac | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_decision_explainer
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""测试 DecisionExplainer — 结构化拒绝原因"""

from zephyr.security.access_control.decision_explainer import DecisionExplainer, Explanation


class TestStructuredRejection:
    def test_returns_explanation(self):
        explainer = DecisionExplainer()
        exp = explainer.structured_rejection("L0", "IMMUTABLE-001", "Test block")
        assert exp.blocked_layer == "L0"
        assert exp.rule_id == "IMMUTABLE-001"
        assert len(exp.causal_chain) > 0

    def test_auto_generated_suggestion(self):
        explainer = DecisionExplainer()
        exp = explainer.structured_rejection("L1", "RBAC-001", "No permission")
        assert exp.correction_suggestion

    def test_to_dict(self):
        exp = Explanation(
            blocked_layer="L2",
            rule_id="ABAC-001",
            reason="TLB exceeded",
            correction_suggestion="Wait for reset",
            causal_chain=["L2", "ABAC", "TLB"],
        )
        d = exp.to_dict()
        assert d["blocked_layer"] == "L2"
        assert d["rule_id"] == "ABAC-001"

    def test_explain_auto_guard(self):
        explainer = DecisionExplainer()
        exp = explainer.explain_auto_guard("write:src", 300)
        assert exp.rule_id == "AUTO_GUARD"
        assert "300s" in exp.reason
