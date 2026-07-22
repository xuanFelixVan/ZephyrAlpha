# [A_test] module_id: MOD-GOV_hooks_integrity_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §

# [MODULE] tests.test_hooks_integrity_guard

# [INVARIANTS] 测试必须覆盖register和verify的边界条件

# [MODIFY-GUARD] src/zephyr/escalation-engine/hooks_integrity_guard.py

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 测试失败必须包含断言信息

# [TESTS] tests/test_hooks_integrity_guard.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.security_governance.hooks_integrity_guard import HooksIntegrityGuard


class TestHooksIntegrityGuardInit:
    def test_init_creates_empty_hashes(self):
        guard = HooksIntegrityGuard()
        assert guard._hooks_hashes == {}


class TestHooksIntegrityGuardRegister:
    def test_register_stores_hash(self):
        guard = HooksIntegrityGuard()
        guard.register("hook_a", "abc123")
        assert guard._hooks_hashes["hook_a"] == "abc123"

    def test_register_overwrites_existing(self):
        guard = HooksIntegrityGuard()
        guard.register("hook_a", "abc123")
        guard.register("hook_a", "def456")
        assert guard._hooks_hashes["hook_a"] == "def456"

    def test_register_multiple_hooks(self):
        guard = HooksIntegrityGuard()
        guard.register("hook_a", "hash_a")
        guard.register("hook_b", "hash_b")
        assert len(guard._hooks_hashes) == 2
        assert guard._hooks_hashes["hook_a"] == "hash_a"
        assert guard._hooks_hashes["hook_b"] == "hash_b"

    def test_register_empty_path(self):
        guard = HooksIntegrityGuard()
        guard.register("", "some_hash")
        assert guard._hooks_hashes[""] == "some_hash"

    def test_register_empty_hash_value(self):
        guard = HooksIntegrityGuard()
        guard.register("hook_a", "")
        assert guard._hooks_hashes["hook_a"] == ""


class TestHooksIntegrityGuardVerify:
    def test_verify_unregistered_hook_returns_true(self):
        guard = HooksIntegrityGuard()
        assert guard.verify("unknown_hook", "any_hash") is True

    def test_verify_matching_hash_returns_true(self):
        guard = HooksIntegrityGuard()
        guard.register("hook_a", "abc123")
        assert guard.verify("hook_a", "abc123") is True

    def test_verify_mismatched_hash_returns_false(self):
        guard = HooksIntegrityGuard()
        guard.register("hook_a", "abc123")
        assert guard.verify("hook_a", "wrong_hash") is False

    def test_verify_empty_string_hash_registered(self):
        guard = HooksIntegrityGuard()
        guard.register("hook_a", "")
        assert guard.verify("hook_a", "") is True
        assert guard.verify("hook_a", "nonempty") is False

    def test_verify_none_hash_value_registered_always_true(self):
        guard = HooksIntegrityGuard()
        guard.register("hook_a", None)
        assert guard.verify("hook_a", None) is True
        assert guard.verify("hook_a", "something") is True

    def test_verify_after_overwrite(self):
        guard = HooksIntegrityGuard()
        guard.register("hook_a", "old_hash")
        guard.register("hook_a", "new_hash")
        assert guard.verify("hook_a", "new_hash") is True
        assert guard.verify("hook_a", "old_hash") is False

    def test_verify_empty_path(self):
        guard = HooksIntegrityGuard()
        guard.register("", "hash_for_empty")
        assert guard.verify("", "hash_for_empty") is True
        assert guard.verify("", "wrong") is False

    def test_verify_unregistered_empty_path_returns_true(self):
        guard = HooksIntegrityGuard()
        assert guard.verify("", "any") is True
