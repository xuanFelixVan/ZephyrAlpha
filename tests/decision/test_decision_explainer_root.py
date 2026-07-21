# [A_test] module_id: MOD-GOV_decision_explainer_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.decision_explainer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.decision_explainer import DecisionExplainer, Explanation

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as e:
    _IMPORT_OK = False
    _IMPORT_REASON = str(e)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestExplanation:
    def test_to_dict_returns_all_fields(self):
        exp = Explanation(
            blocked_layer="L1",
            rule_id="R001",
            reason="unauthorized",
            correction_suggestion="request owner",
            causal_chain=["L1", "R001", "unauthorized"],
        )
        d = exp.to_dict()
        assert d["blocked_layer"] == "L1"
        assert d["rule_id"] == "R001"
        assert d["reason"] == "unauthorized"
        assert d["correction_suggestion"] == "request owner"
        assert d["causal_chain"] == ["L1", "R001", "unauthorized"]

    def test_to_dict_default_causal_chain(self):
        exp = Explanation(
            blocked_layer="L2",
            rule_id="R002",
            reason="timeout",
            correction_suggestion="retry",
        )
        d = exp.to_dict()
        assert d["causal_chain"] == []

    def test_explanation_with_empty_strings(self):
        exp = Explanation(
            blocked_layer="",
            rule_id="",
            reason="",
            correction_suggestion="",
        )
        d = exp.to_dict()
        assert d["blocked_layer"] == ""
        assert d["causal_chain"] == []


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestDecisionExplainer:
    def test_structured_rejection_with_suggestion(self):
        de = DecisionExplainer()
        exp = de.structured_rejection(
            blocked_layer="L1",
            rule_id="R001",
            reason="unauthorized",
            correction_suggestion="contact admin",
        )
        assert exp.blocked_layer == "L1"
        assert exp.rule_id == "R001"
        assert exp.reason == "unauthorized"
        assert exp.correction_suggestion == "contact admin"
        assert exp.causal_chain == ["L1", "R001", "unauthorized"]

    def test_structured_rejection_auto_suggestion_l0(self):
        de = DecisionExplainer()
        exp = de.structured_rejection(
            blocked_layer="L0",
            rule_id="R100",
            reason="immutable",
        )
        assert (
            "immutable" in exp.correction_suggestion.lower()
            or "hard" in exp.correction_suggestion.lower()
            or "No workaround" in exp.correction_suggestion
        )

    def test_structured_rejection_auto_suggestion_l1(self):
        de = DecisionExplainer()
        exp = de.structured_rejection(
            blocked_layer="L1",
            rule_id="R200",
            reason="denied",
        )
        assert "owner" in exp.correction_suggestion.lower() or "permission" in exp.correction_suggestion.lower()

    def test_structured_rejection_custom_causal_chain(self):
        de = DecisionExplainer()
        exp = de.structured_rejection(
            blocked_layer="L3",
            rule_id="R300",
            reason="schema error",
            causal_chain=["A", "B", "C"],
        )
        assert exp.causal_chain == ["A", "B", "C"]

    def test_structured_rejection_empty_correction_generates_suggestion(self):
        de = DecisionExplainer()
        exp = de.structured_rejection(
            blocked_layer="L5",
            rule_id="R500",
            reason="PII detected",
        )
        assert exp.correction_suggestion != ""

    def test_structured_rejection_unknown_layer_fallback(self):
        de = DecisionExplainer()
        exp = de.structured_rejection(
            blocked_layer="UNKNOWN",
            rule_id="R999",
            reason="unknown reason",
        )
        assert exp.correction_suggestion == "Contact the system owner for assistance."

    def test_explain_auto_guard(self):
        de = DecisionExplainer()
        exp = de.explain_auto_guard(operation="write_file", timeout=30)
        assert exp.blocked_layer == "N/A"
        assert exp.rule_id == "AUTO_GUARD"
        assert "write_file" in exp.reason
        assert "30" in exp.correction_suggestion
        assert "L1 RBAC" in exp.causal_chain

    def test_explain_auto_guard_zero_timeout(self):
        de = DecisionExplainer()
        exp = de.explain_auto_guard(operation="read", timeout=0)
        assert exp.rule_id == "AUTO_GUARD"
        assert "0" in exp.correction_suggestion
