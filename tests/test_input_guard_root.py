# [A_test] module_id: SRC-TST-1129 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.guards.input_guard
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


from zephyr.security.access_control.immutable_core import ImmutableCore
from zephyr.security.access_control.guards.input_guard import (
    DANGEROUS_PATTERNS,
    PROJECT_SAFE_DIRS,
    TRUSTED_PACKAGES,
    InputDecision,
    InputGuard,
)


class TestInputDecision:
    def test_enum_values(self):
        assert InputDecision.ALLOW.value == "ALLOW"
        assert InputDecision.BLOCKED.value == "BLOCKED"
        assert InputDecision.SANITIZED.value == "SANITIZED"

    def test_enum_members(self):
        members = list(InputDecision)
        assert len(members) == 3


class TestDangerousPatterns:
    def test_not_empty(self):
        assert len(DANGEROUS_PATTERNS) > 0

    def test_each_pattern_is_tuple(self):
        for pattern, description in DANGEROUS_PATTERNS:
            assert isinstance(pattern, str)
            assert isinstance(description, str)
            assert pattern
            assert description


class TestTrustedPackages:
    def test_not_empty(self):
        assert len(TRUSTED_PACKAGES) > 0

    def test_contains_common_packages(self):
        assert "pytest" in TRUSTED_PACKAGES
        assert "pydantic" in TRUSTED_PACKAGES


class TestProjectSafeDirs:
    def test_not_empty(self):
        assert len(PROJECT_SAFE_DIRS) > 0

    def test_contains_src(self):
        assert "src/" in PROJECT_SAFE_DIRS
        assert "tests/" in PROJECT_SAFE_DIRS


class TestInputGuard:
    def test_init_default(self):
        guard = InputGuard()
        assert guard._immutable_core is not None

    def test_init_custom_immutable_core(self):
        core = ImmutableCore()
        guard = InputGuard(immutable_core=core)
        assert guard._immutable_core is core

    def test_check_params_clean(self):
        guard = InputGuard()
        result = guard.check_params("read", {"path": "src/main.py"})
        assert result == InputDecision.ALLOW

    def test_check_params_dangerous_command(self):
        guard = InputGuard()
        result = guard.check_params("execute", {"command": "rm -rf /"})
        assert result == InputDecision.BLOCKED

    def test_check_params_dangerous_eval(self):
        guard = InputGuard()
        result = guard.check_params("execute", {"command": "eval('os.system')"})
        assert result == InputDecision.BLOCKED

    def test_check_params_empty_dict(self):
        guard = InputGuard()
        result = guard.check_params("read", {})
        assert result == InputDecision.ALLOW

    def test_check_params_subprocess_blocked(self):
        guard = InputGuard()
        result = guard.check_params("execute", {"command": "subprocess.run(['ls'])"})
        assert result == InputDecision.BLOCKED

    def test_check_path_safe_relative(self):
        guard = InputGuard()
        decision, msg = guard.check_path("src/main.py")
        assert decision == InputDecision.ALLOW
        assert msg == ""

    def test_check_path_tests_dir(self):
        guard = InputGuard()
        decision, msg = guard.check_path("tests/test_foo.py")
        assert decision == InputDecision.ALLOW

    def test_check_path_docs_dir(self):
        guard = InputGuard()
        decision, msg = guard.check_path("docs/readme.md")
        assert decision == InputDecision.ALLOW

    def test_check_path_absolute_blocked(self):
        guard = InputGuard()
        decision, msg = guard.check_path("/etc/passwd")
        assert decision == InputDecision.BLOCKED
        assert "Absolute" in msg

    def test_check_path_windows_absolute_blocked(self):
        guard = InputGuard()
        decision, msg = guard.check_path("C:\\Windows\\System32")
        assert decision == InputDecision.BLOCKED

    def test_check_path_traversal_blocked(self):
        guard = InputGuard()
        decision, msg = guard.check_path("../../etc/passwd")
        assert decision == InputDecision.BLOCKED
        assert "traversal" in msg.lower()

    def test_check_path_protected_path_blocked(self):
        guard = InputGuard()
        decision, msg = guard.check_path("src/zephyr/agent-rbac/kill_switch.py")
        assert decision == InputDecision.BLOCKED

    def test_check_path_unsafe_dir_blocked(self):
        guard = InputGuard()
        decision, msg = guard.check_path("random_dir/file.txt")
        assert decision == InputDecision.BLOCKED

    def test_check_path_temp_file_allowed(self):
        guard = InputGuard()
        decision, msg = guard.check_path("_temp_output.py")
        assert decision == InputDecision.ALLOW

    def test_check_path_dotfile_allowed(self):
        guard = InputGuard()
        decision, msg = guard.check_path(".gitignore")
        assert decision == InputDecision.ALLOW

    def test_check_path_empty_string(self):
        guard = InputGuard()
        decision, msg = guard.check_path("")
        assert decision == InputDecision.BLOCKED

    def test_check_package_install_trusted(self):
        guard = InputGuard()
        for pkg in ["pytest", "pydantic", "pyyaml"]:
            decision, msg = guard.check_package_install(pkg)
            assert decision == InputDecision.ALLOW, f"{pkg} should be trusted"

    def test_check_package_install_untrusted(self):
        guard = InputGuard()
        decision, msg = guard.check_package_install("malicious-pkg")
        assert decision == InputDecision.BLOCKED
        assert "not in trusted" in msg

    def test_check_package_install_with_version(self):
        guard = InputGuard()
        decision, msg = guard.check_package_install("pytest==7.0.0")
        assert decision == InputDecision.ALLOW

    def test_check_package_install_untrusted_with_version(self):
        guard = InputGuard()
        decision, msg = guard.check_package_install("evil-pkg>=1.0")
        assert decision == InputDecision.BLOCKED

    def test_check_package_install_empty(self):
        guard = InputGuard()
        decision, msg = guard.check_package_install("")
        assert decision == InputDecision.BLOCKED

    def test_check_network_target_localhost(self):
        guard = InputGuard()
        decision, msg = guard.check_network_target("http://localhost:8080/api")
        assert decision == InputDecision.ALLOW

    def test_check_network_target_127(self):
        guard = InputGuard()
        decision, msg = guard.check_network_target("http://127.0.0.1:3000")
        assert decision == InputDecision.ALLOW

    def test_check_network_target_google(self):
        guard = InputGuard()
        decision, msg = guard.check_network_target("https://google.com/search")
        assert decision == InputDecision.ALLOW

    def test_check_network_target_github(self):
        guard = InputGuard()
        decision, msg = guard.check_network_target("https://github.com/org/repo")
        assert decision == InputDecision.ALLOW

    def test_check_network_target_pypi(self):
        guard = InputGuard()
        decision, msg = guard.check_network_target("https://pypi.org/project/pytest")
        assert decision == InputDecision.ALLOW

    def test_check_network_target_untrusted(self):
        guard = InputGuard()
        decision, msg = guard.check_network_target("https://evil-phishing.com/steal")
        assert decision == InputDecision.BLOCKED
        assert "not in trusted" in msg

    def test_check_network_target_empty(self):
        guard = InputGuard()
        decision, msg = guard.check_network_target("")
        assert decision == InputDecision.BLOCKED

    def test_check_params_with_path_param(self):
        guard = InputGuard()
        result = guard.check_params("write", {"path": "src/new_file.py"})
        assert result == InputDecision.ALLOW

    def test_check_params_with_dangerous_path(self):
        guard = InputGuard()
        result = guard.check_params("write", {"path": "/etc/passwd"})
        assert result == InputDecision.BLOCKED

    def test_check_params_with_package_param(self):
        guard = InputGuard()
        result = guard.check_params("install", {"package": "pytest"})
        assert result == InputDecision.ALLOW

    def test_check_params_with_untrusted_package(self):
        guard = InputGuard()
        result = guard.check_params("install", {"package": "evil-pkg"})
        assert result == InputDecision.BLOCKED

    def test_check_params_with_url_param(self):
        guard = InputGuard()
        result = guard.check_params("fetch", {"url": "https://google.com/api"})
        assert result == InputDecision.ALLOW

    def test_check_params_with_untrusted_url(self):
        guard = InputGuard()
        result = guard.check_params("fetch", {"url": "https://evil.com/api"})
        assert result == InputDecision.BLOCKED

    def test_check_params_backtick_injection(self):
        guard = InputGuard()
        result = guard.check_params("execute", {"command": "`rm -rf /`"})
        assert result == InputDecision.BLOCKED

    def test_check_params_dollar_paren_injection(self):
        guard = InputGuard()
        result = guard.check_params("execute", {"command": "$(rm -rf /)"})
        assert result == InputDecision.BLOCKED

    def test_check_params_os_system_blocked(self):
        guard = InputGuard()
        result = guard.check_params("execute", {"command": "os.system('ls')"})
        assert result == InputDecision.BLOCKED

    def test_check_params_data_dir_allowed(self):
        guard = InputGuard()
        result = guard.check_params("read", {"path": "data/config.yaml"})
        assert result == InputDecision.ALLOW

    def test_check_params_scripts_dir_allowed(self):
        guard = InputGuard()
        result = guard.check_params("read", {"path": "scripts/run.py"})
        assert result == InputDecision.ALLOW

    def test_check_path_backslash_normalization(self):
        guard = InputGuard()
        decision, msg = guard.check_path("src\\main.py")
        assert decision == InputDecision.ALLOW
