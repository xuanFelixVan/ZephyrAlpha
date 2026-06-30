# [A_test] module_id: SRC-TST-1366 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.permission_hooks
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
    from zephyr.security.access_control.permission_hooks import PermissionHooks
except Exception as _exc:
    pytest.skip(f"无法导入 permission_hooks: {_exc}", allow_module_level=True)


class TestPermissionHooks:
    def test_register_and_run(self):
        ph = PermissionHooks()
        ph.register("pre_check", "test-hook", lambda **kw: {"ok": True})
        results = ph.run("pre_check")
        assert len(results) == 1
        assert results[0]["hook"] == "test-hook"
        assert results[0]["result"]["ok"] is True

    def test_run_empty_hook_type(self):
        ph = PermissionHooks()
        results = ph.run("pre_check")
        assert results == []

    def test_run_nonexistent_hook_type(self):
        ph = PermissionHooks()
        results = ph.run("nonexistent")
        assert results == []

    def test_register_multiple_hooks(self):
        ph = PermissionHooks()
        ph.register("pre_check", "h1", lambda **kw: {"v": 1})
        ph.register("pre_check", "h2", lambda **kw: {"v": 2})
        results = ph.run("pre_check")
        assert len(results) == 2

    def test_hook_exception_captured(self):
        ph = PermissionHooks()

        def bad_hook(**kw):
            raise RuntimeError("boom")

        ph.register("pre_check", "bad", bad_hook)
        results = ph.run("pre_check")
        assert len(results) == 1
        assert "error" in results[0]
        assert "boom" in results[0]["error"]

    def test_register_defaults(self):
        ph = PermissionHooks()
        ph.register_defaults()
        pre_results = ph.run("pre_check")
        post_results = ph.run("post_check")
        blocked_results = ph.run("on_blocked")
        kill_results = ph.run("on_kill_switch")
        assert len(pre_results) == 3
        assert len(post_results) == 2
        assert len(blocked_results) == 2
        assert len(kill_results) == 2

    def test_hook_type_constants(self):
        assert PermissionHooks.PRE_CHECK == "pre_check"
        assert PermissionHooks.POST_CHECK == "post_check"
        assert PermissionHooks.ON_BLOCKED == "on_blocked"
        assert PermissionHooks.ON_KILL_SWITCH == "on_kill_switch"

    def test_run_with_kwargs(self):
        ph = PermissionHooks()
        ph.register("post_check", "kw-hook", lambda **kw: {"got": kw.get("x", 0)})
        results = ph.run("post_check", x=42)
        assert results[0]["result"]["got"] == 42

    def test_register_ignores_unknown_type(self):
        ph = PermissionHooks()
        ph.register("unknown_type", "h1", lambda **kw: {"v": 1})
        results = ph.run("unknown_type")
        assert results == []

    def test_default_hook_h01_rate_limit(self):
        ph = PermissionHooks()
        ph.register_defaults()
        results = ph.run("pre_check")
        h01 = [r for r in results if r["hook"] == "H01-RateLimit"]
        assert len(h01) == 1
        assert h01[0]["result"]["rate_limited"] is False

    def test_default_hook_h06_audit_log(self):
        ph = PermissionHooks()
        ph.register_defaults()
        results = ph.run("on_blocked")
        h06 = [r for r in results if r["hook"] == "H06-AuditLog"]
        assert len(h06) == 1
        assert h06[0]["result"]["logged"] is True

    def test_default_hook_h08_snapshot(self):
        ph = PermissionHooks()
        ph.register_defaults()
        results = ph.run("on_kill_switch")
        h08 = [r for r in results if r["hook"] == "H08-SnapshotState"]
        assert len(h08) == 1
        assert h08[0]["result"]["snapshot_taken"] is True

    def test_default_hook_h09_notify(self):
        ph = PermissionHooks()
        ph.register_defaults()
        results = ph.run("on_kill_switch")
        h09 = [r for r in results if r["hook"] == "H09-NotifyOwner"]
        assert len(h09) == 1
        assert h09[0]["result"]["notified"] is True
