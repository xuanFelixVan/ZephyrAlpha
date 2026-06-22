# [A_test] module_id: SRC-TST-0052 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain-autonomy_core/agent-rbac/blueprint.md | §
# [MODULE] tests.agent_rbac.test_post_action
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
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
