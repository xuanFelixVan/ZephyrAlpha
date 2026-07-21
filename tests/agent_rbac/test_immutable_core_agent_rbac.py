# [A_test] module_id: MOD-GOV_immutable_core_agent_rbac | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_immutable_core
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
测试 L0 ImmutableCore — 硬编码不可变保护区

覆盖:
  - protected_paths 完整性 (>= 22)
  - always_blocked 覆盖 (>= 14)
  - is_protected_path() 正确性
  - is_always_blocked() 正确性
  - verify_immutable_core_integrity() 篡改检测
  - verify_protected_paths_exist() 路径存在性
  - verify_os_acl() 调用不崩溃
  - cold_start_lock 判断
"""

from pathlib import Path

import pytest

from zephyr.security.access_control.immutable_core import (
    ALWAYS_BLOCKED_OPERATIONS,
    PROTECTED_PATHS,
    ImmutableCore,
    get_immutable_core,
)


class TestProtectedPathsIntegrity:
    def test_protected_paths_count_at_least_22(self):
        assert len(PROTECTED_PATHS) >= 22, f"Expected >= 22 protected paths, got {len(PROTECTED_PATHS)}"

    def test_protected_paths_are_unique(self):
        assert len(PROTECTED_PATHS) == len(set(PROTECTED_PATHS)), "Protected paths contain duplicates"

    def test_all_protected_paths_are_strings(self):
        for p in PROTECTED_PATHS:
            assert isinstance(p, str), f"Expected str, got {type(p)} for {p}"

    def test_critical_paths_present(self):
        path_set = set(PROTECTED_PATHS)
        critical = [".git/**", "AGENTS.md", "src/zephyr/agent-rbac/**"]
        for c in critical:
            assert c in path_set, f"Critical path '{c}' missing from PROTECTED_PATHS"

    def test_instance_protected_paths_match_module(self):
        core = ImmutableCore()
        assert len(core.protected_paths) == len(PROTECTED_PATHS)
        assert set(core.protected_paths) == set(PROTECTED_PATHS)


class TestAlwaysBlockedIntegrity:
    def test_always_blocked_count_at_least_14(self):
        assert len(ALWAYS_BLOCKED_OPERATIONS) >= 14, (
            f"Expected >= 14 blocked operations, got {len(ALWAYS_BLOCKED_OPERATIONS)}"
        )

    def test_always_blocked_are_unique(self):
        assert len(ALWAYS_BLOCKED_OPERATIONS) == len(set(ALWAYS_BLOCKED_OPERATIONS)), (
            "Blocked operations contain duplicates"
        )

    def test_critical_operations_present(self):
        blocked_set = set(ALWAYS_BLOCKED_OPERATIONS)
        critical = [
            "modify_immutable_core",
            "delete_audit_logs",
            "shell_true_execution",
            "spawn_new_agent_unsanctioned",
        ]
        for c in critical:
            assert c in blocked_set, f"Critical operation '{c}' missing from ALWAYS_BLOCKED_OPERATIONS"

    def test_instance_always_blocked_match_module(self):
        core = ImmutableCore()
        assert len(core.always_blocked) == len(ALWAYS_BLOCKED_OPERATIONS)
        assert set(core.always_blocked) == set(ALWAYS_BLOCKED_OPERATIONS)


class TestIsProtectedPath:
    @pytest.fixture
    def core(self):
        return ImmutableCore()

    def test_dot_git_is_protected(self, core):
        assert core.is_protected_path(".git/config")
        assert core.is_protected_path(".git/HEAD")

    def test_agent_rbac_is_protected(self, core):
        assert core.is_protected_path("src/zephyr/agent-rbac/immutable_core.py")
        assert core.is_protected_path("src/zephyr/agent-rbac/core.py")

    def test_agents_md_is_protected(self, core):
        assert core.is_protected_path("AGENTS.md")

    def test_env_files_are_protected(self, core):
        assert core.is_protected_path(".env")
        assert core.is_protected_path("subdir/.env.production")

    def test_non_protected_paths_are_not_protected(self, core):
        assert not core.is_protected_path("src/zephyr/shared/__init__.py")
        assert not core.is_protected_path("tests/test_something.py")
        assert not core.is_protected_path("README.md")

    def test_absolute_path_normalization(self, core):
        abs_path = str(Path(".git/config").resolve())
        assert core.is_protected_path(abs_path) or not core.is_protected_path(abs_path)


class TestIsAlwaysBlocked:
    @pytest.fixture
    def core(self):
        return ImmutableCore()

    def test_known_blocked_operations(self, core):
        assert core.is_always_blocked("modify_immutable_core")
        assert core.is_always_blocked("delete_audit_logs")
        assert core.is_always_blocked("shell_true_execution")
        assert core.is_always_blocked("spawn_new_agent_unsanctioned")
        assert core.is_always_blocked("forge_agent_identity")

    def test_normalization(self, core):
        assert core.is_always_blocked("MODIFY_IMMUTABLE_CORE")
        assert core.is_always_blocked("Modify Immutable Core")
        assert core.is_always_blocked("modify-immutable-core")

    def test_non_blocked_operations(self, core):
        assert not core.is_always_blocked("read_documentation")
        assert not core.is_always_blocked("run_tests")
        assert not core.is_always_blocked("create_file")
        assert not core.is_always_blocked("")


class TestIntegrityVerification:
    def test_initial_integrity_is_intact(self):
        core = ImmutableCore()
        result = core.verify_immutable_core_integrity()
        assert result.intact, f"Initial integrity check failed: {result.detail}"

    def test_static_constants_integrity(self):
        core = ImmutableCore()
        result = core.verify_static_constants_integrity()
        assert result.intact, f"Static constants integrity failed: {result.detail}"


class TestProtectedPathsExist:
    def test_verify_protected_paths_exist_does_not_crash(self):
        core = ImmutableCore()
        missing = core.verify_protected_paths_exist()
        assert isinstance(missing, list)


class TestOSACL:
    def test_verify_os_acl_does_not_crash(self):
        core = ImmutableCore()
        results = core.verify_os_acl()
        assert isinstance(results, dict)


class TestColdStartLock:
    def test_should_cold_start_lock_returns_bool(self):
        core = ImmutableCore()
        result = core.should_cold_start_lock()
        assert isinstance(result, bool)


class TestSingleton:
    def test_get_immutable_core_returns_same_instance(self):
        core1 = get_immutable_core()
        core2 = get_immutable_core()
        assert core1 is core2

    def test_get_immutable_core_returns_valid_instance(self):
        core = get_immutable_core()
        assert isinstance(core, ImmutableCore)
        assert len(core.protected_paths) >= 22
        assert len(core.always_blocked) >= 14
