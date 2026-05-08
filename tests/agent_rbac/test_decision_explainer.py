"""测试 DecisionExplainer — 结构化拒绝原因"""
import pytest
from zephyr.agent_rbac.decision_explainer import DecisionExplainer, Explanation


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
