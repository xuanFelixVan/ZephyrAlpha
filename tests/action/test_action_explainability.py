# [A_test] module_id: SRC-TST-0264 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_action_explainability
# [INVARIANTS] explain returns formatted string from action dict
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_action_explainability.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.verifiers.action_explainability import ActionExplainability


class TestActionExplainabilityInstantiation:
    def test_default_construction(self):
        ae = ActionExplainability()
        assert ae is not None


class TestExplain:
    def test_explain_with_type_and_reason(self):
        ae = ActionExplainability()
        action = {"type": "restart", "reason": "high latency"}
        result = ae.explain(action)
        assert "restart" in result
        assert "high latency" in result

    def test_explain_empty_action(self):
        ae = ActionExplainability()
        result = ae.explain({})
        assert "None" in result

    def test_explain_missing_type(self):
        ae = ActionExplainability()
        action = {"reason": "some reason"}
        result = ae.explain(action)
        assert "some reason" in result

    def test_explain_missing_reason(self):
        ae = ActionExplainability()
        action = {"type": "scale"}
        result = ae.explain(action)
        assert "scale" in result

    def test_explain_none_values(self):
        ae = ActionExplainability()
        action = {"type": None, "reason": None}
        result = ae.explain(action)
        assert isinstance(result, str)
