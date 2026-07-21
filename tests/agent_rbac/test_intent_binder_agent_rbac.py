# [A_test] module_id: MOD-GOV_intent_binder_agent_rbac | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_intent_binder
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""测试 IntentBinder — 意图绑定与连续验证"""

from zephyr.security.access_control.intent_binder import IntentBinder, IntentState


class TestIntentDeclaration:
    def test_basic_declaration(self):
        binder = IntentBinder()
        intent = binder.declare(
            "agent-i1",
            "test.py",
            "add feature X",
            ["read:docs", "write:src", "run:tests"],
        )
        assert intent.state == IntentState.ACTIVE
        assert intent.agent_id == "agent-i1"

    def test_verify_expected_operation(self):
        binder = IntentBinder()
        binder.declare("agent-i2", "f.py", "do A", ["read:docs", "write:src"])
        assert binder.verify("agent-i2", "read:docs")

    def test_verify_unexpected_operation(self):
        binder = IntentBinder()
        binder.declare("agent-i3", "f.py", "do B", ["read:docs"])
        assert not binder.verify("agent-i3", "delete:file")

    def test_drift_detection(self):
        binder = IntentBinder()
        binder.declare("agent-i4", "f.py", "do C", ["read:docs"])
        for _ in range(5):
            binder.verify("agent-i4", "delete:something")
        assert binder.check_drift("agent-i4")

    def test_close_intent(self):
        binder = IntentBinder()
        binder.declare("agent-i5", "f.py", "do D", ["read:docs"])
        binder.close("agent-i5")
        intent = binder.get_active_intent("agent-i5")
        assert intent.state == IntentState.COMPLETED
