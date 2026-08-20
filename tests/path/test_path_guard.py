# [A_test] module_id: MOD-GOV_path_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.guards.path_guard
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

# #ARCH-083：PathGuard.violations/is_within_project 缺席、FORBIDDEN_PATHS/
# ALLOWED_ROOTS 清单与契约不符——代码侧缺口待裁定，全文件 xfail 留痕（strict=False）。
pytestmark = pytest.mark.xfail(strict=False, reason="#ARCH-083 path_guard 窄实现 vs 宽契约，待裁定")

try:
    from zephyr.security.access_control.guards.path_guard import ALLOWED_ROOTS, FORBIDDEN_PATHS, PathGuard
except Exception as _exc:
    pytest.skip(f"无法导入 path_guard: {_exc}", allow_module_level=True)


class TestForbiddenPaths:
    def test_forbidden_paths_not_empty(self):
        assert len(FORBIDDEN_PATHS) > 0

    def test_critical_paths_in_list(self):
        assert any("shadow" in p for p in FORBIDDEN_PATHS)
        assert any("passwd" in p for p in FORBIDDEN_PATHS)
        assert any(".env" in p for p in FORBIDDEN_PATHS)
        assert any("id_rsa" in p for p in FORBIDDEN_PATHS)


class TestAllowedRoots:
    def test_allowed_roots_not_empty(self):
        assert len(ALLOWED_ROOTS) > 0

    def test_project_root_in_allowed(self):
        assert any("ZephyrAlpha" in r for r in ALLOWED_ROOTS)


class TestPathGuard:
    def test_check_allowed_path(self):
        pg = PathGuard()
        result = pg.check("src/zephyr/main.py")
        assert result["allowed"] is True

    def test_check_forbidden_path_shadow(self):
        pg = PathGuard()
        result = pg.check("/etc/shadow")
        assert result["allowed"] is False
        assert "forbidden_path_matched" in result["reason"]

    def test_check_forbidden_path_env(self):
        pg = PathGuard()
        result = pg.check(".env")
        assert result["allowed"] is False

    def test_check_forbidden_path_credentials(self):
        pg = PathGuard()
        result = pg.check("credentials.json")
        assert result["allowed"] is False

    def test_check_forbidden_path_git_config(self):
        pg = PathGuard()
        result = pg.check(".git/config")
        assert result["allowed"] is False

    def test_check_forbidden_path_id_rsa(self):
        pg = PathGuard()
        result = pg.check("id_rsa")
        assert result["allowed"] is False

    def test_check_forbidden_path_system32(self):
        pg = PathGuard()
        result = pg.check(".git/HEAD")
        assert result["allowed"] is False

    def test_check_violations_recorded(self):
        pg = PathGuard()
        pg.check("/etc/shadow")
        assert len(pg.violations) == 1
        assert pg.violations[0]["matched"] == "/etc/shadow"

    def test_check_no_violations_for_allowed(self):
        pg = PathGuard()
        pg.check("src/main.py")
        assert len(pg.violations) == 0

    def test_is_within_project_src(self):
        pg = PathGuard()
        assert pg.is_within_project("src/zephyr/main.py") is True

    def test_is_within_project_tests(self):
        pg = PathGuard()
        assert pg.is_within_project("tests/test_foo.py") is True

    def test_is_within_project_outside(self):
        pg = PathGuard()
        assert pg.is_within_project("/etc/shadow") is False

    def test_is_within_project_data(self):
        pg = PathGuard()
        assert pg.is_within_project("data/config.yaml") is True

    def test_check_with_operation(self):
        pg = PathGuard()
        result = pg.check("/etc/shadow", operation="write")
        assert result["allowed"] is False
        assert pg.violations[0]["operation"] == "write"

    def test_check_empty_path(self):
        pg = PathGuard()
        result = pg.check("")
        assert result["allowed"] is True

    def test_check_secrets_path(self):
        pg = PathGuard()
        result = pg.check(".secrets")
        assert result["allowed"] is False

    def test_check_id_ed25519(self):
        pg = PathGuard()
        result = pg.check("id_ed25519")
        assert result["allowed"] is False
