# [A_test] module_id: MOD-GOV_post_action | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_post_action
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""MOD-INF-018 test_post_action.py — L5 Post-Action Hook 测试."""

from __future__ import annotations


class TestPostActionHooks:
    def test_permission_hooks_post_action(self):
        from zephyr.security.access_control.permission_hooks import PermissionHooks

        hooks = PermissionHooks()
        assert hasattr(hooks, "register")

    def test_hook_registration(self):
        from zephyr.security.access_control.permission_hooks import PermissionHooks

        hooks = PermissionHooks()
        called = []

        def my_hook(**kwargs):
            called.append(True)

        hooks.register("post_check", "H99-test", my_hook)
        hooks.run("post_check", agent_id="test")
        assert len(called) == 1
