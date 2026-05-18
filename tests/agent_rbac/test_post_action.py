# [BLUEPRINT] MOD-INF-018 | docs/03_modules/l01_infrastructure/agent-rbac/blueprint.md | §
# [MODULE] tests.agent_rbac.test_post_action
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""MOD-INF-018 test_post_action.py — L5 Post-Action Hook 测试."""
from __future__ import annotations

import pytest


class TestPostActionHooks:
    def test_permission_hooks_post_action(self):
        from zephyr.agent_rbac.permission_hooks import PermissionHooks
        hooks = PermissionHooks()
        assert hasattr(hooks, "register")

    def test_hook_registration(self):
        from zephyr.agent_rbac.permission_hooks import PermissionHooks
        hooks = PermissionHooks()
        called = []

        def my_hook(**kwargs):
            called.append(True)

        hooks.register("post_check", "H99-test", my_hook)
        hooks.run("post_check", agent_id="test")
        assert len(called) == 1
