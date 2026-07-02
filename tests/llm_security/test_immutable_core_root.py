# [A_test] module_id: SRC-TST-1108 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.test_immutable_core
# [INVARIANTS] protected_paths_gte_22;always_blocked_gte_14;singleton_identity
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest_exit_0
# [TESTS] pytest tests/test_immutable_core.py -q
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

from pathlib import Path

from zephyr.security.access_control.immutable_core import (
    ALWAYS_BLOCKED_OPERATIONS,
    PROTECTED_PATHS,
    ImmutableCore,
    IntegrityResult,
    get_immutable_core,
)


class TestImmutableCoreInit:
    def test_default_project_root(self):
        core = ImmutableCore()
        assert core._project_root is not None

    def test_custom_project_root(self):
        root = Path("/tmp/fake_project")
        core = ImmutableCore(project_root=root)
        assert core._project_root == root

    def test_protected_paths_is_list(self):
        core = ImmutableCore()
        assert isinstance(core.protected_paths, list)

    def test_always_blocked_is_list(self):
        core = ImmutableCore()
        assert isinstance(core.always_blocked, list)

    def test_protected_paths_returns_copy(self):
        core = ImmutableCore()
        p1 = core.protected_paths
        p2 = core.protected_paths
        assert p1 is not p2
        assert p1 == p2

    def test_always_blocked_returns_copy(self):
        core = ImmutableCore()
        a1 = core.always_blocked
        a2 = core.always_blocked
        assert a1 is not a2
        assert a1 == a2


class TestIsProtectedPath:
    def test_git_pattern(self):
        core = ImmutableCore()
        assert core.is_protected_path(".git/config") is True

    def test_agent_rbac_pattern(self):
        core = ImmutableCore()
        assert core.is_protected_path("src/zephyr/agent-rbac/immutable_core.py") is True

    def test_agents_md(self):
        core = ImmutableCore()
        assert core.is_protected_path("AGENTS.md") is True

    def test_env_pattern(self):
        core = ImmutableCore()
        assert core.is_protected_path(".env") is True

    def test_unprotected_path(self):
        core = ImmutableCore()
        assert core.is_protected_path("some_random_file.txt") is False

    def test_empty_string_path(self):
        core = ImmutableCore()
        assert core.is_protected_path("") is False

    def test_path_object(self):
        core = ImmutableCore()
        assert core.is_protected_path(Path("AGENTS.md")) is True

    def test_pyproject_toml(self):
        core = ImmutableCore()
        assert core.is_protected_path("pyproject.toml") is True

    def test_trae_rules_pattern(self):
        core = ImmutableCore()
        assert core.is_protected_path(".trae/rules/project_rules.md") is True


class TestIsAlwaysBlocked:
    def test_modify_immutable_core(self):
        core = ImmutableCore()
        assert core.is_always_blocked("modify_immutable_core") is True

    def test_delete_audit_logs(self):
        core = ImmutableCore()
        assert core.is_always_blocked("delete_audit_logs") is True

    def test_case_insensitive(self):
        core = ImmutableCore()
        assert core.is_always_blocked("MODIFY_IMMUTABLE_CORE") is True

    def test_space_to_underscore(self):
        core = ImmutableCore()
        assert core.is_always_blocked("modify immutable core") is True

    def test_hyphen_to_underscore(self):
        core = ImmutableCore()
        assert core.is_always_blocked("modify-immutable-core") is True

    def test_allowed_operation(self):
        core = ImmutableCore()
        assert core.is_always_blocked("read_file") is False

    def test_empty_string(self):
        core = ImmutableCore()
        assert core.is_always_blocked("") is False

    def test_self_disable_sandbox(self):
        core = ImmutableCore()
        assert core.is_always_blocked("self_disable_sandbox") is True


class TestVerifyImmutableCoreIntegrity:
    def test_intact_on_fresh_instance(self):
        core = ImmutableCore()
        result = core.verify_immutable_core_integrity()
        assert isinstance(result, IntegrityResult)
        assert result.intact is True
        assert result.checksum != ""

    def test_result_has_no_tampered_items_when_intact(self):
        core = ImmutableCore()
        result = core.verify_immutable_core_integrity()
        assert result.intact is True
        assert result.tampered_items == []

    def test_result_type_fields(self):
        core = ImmutableCore()
        result = core.verify_immutable_core_integrity()
        assert isinstance(result.intact, bool)
        assert isinstance(result.checksum, str)
        assert isinstance(result.tampered_items, list)
        assert isinstance(result.detail, str)


class TestVerifyStaticConstantsIntegrity:
    def test_protected_paths_count_gte_22(self):
        assert len(PROTECTED_PATHS) >= 22

    def test_always_blocked_count_gte_14(self):
        assert len(ALWAYS_BLOCKED_OPERATIONS) >= 14

    def test_intact_on_default(self):
        core = ImmutableCore()
        result = core.verify_static_constants_integrity()
        assert isinstance(result, IntegrityResult)
        assert result.intact is True

    def test_tampered_when_protected_paths_reduced(self):
        core = ImmutableCore()
        core._protected_paths = ["one", "two"]
        result = core.verify_static_constants_integrity()
        assert result.intact is False
        assert len(result.tampered_items) > 0

    def test_tampered_when_always_blocked_reduced(self):
        core = ImmutableCore()
        core._always_blocked = ["op1"]
        result = core.verify_static_constants_integrity()
        assert result.intact is False
        assert len(result.tampered_items) > 0


class TestShouldColdStartLock:
    def test_returns_bool(self):
        core = ImmutableCore()
        result = core.should_cold_start_lock()
        assert isinstance(result, bool)

    def test_with_nonexistent_root(self):
        core = ImmutableCore(project_root=Path("/nonexistent_project_root_xyz"))
        assert core.should_cold_start_lock() is True


class TestGetImmutableCore:
    def test_singleton_identity(self):
        a = get_immutable_core()
        b = get_immutable_core()
        assert a is b

    def test_returns_immutable_core_instance(self):
        instance = get_immutable_core()
        assert isinstance(instance, ImmutableCore)


class TestIntegrityResult:
    def test_default_values(self):
        result = IntegrityResult(intact=True)
        assert result.intact is True
        assert result.checksum == ""
        assert result.tampered_items == []
        assert result.detail == ""

    def test_custom_values(self):
        result = IntegrityResult(
            intact=False,
            checksum="abc123",
            tampered_items=["item1"],
            detail="something wrong",
        )
        assert result.intact is False
        assert result.checksum == "abc123"
        assert result.tampered_items == ["item1"]
        assert result.detail == "something wrong"

    def test_intact_false(self):
        result = IntegrityResult(intact=False)
        assert result.intact is False
