# [A_test] module_id: MOD-GOV_isolation | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] tests.llm_security.test_isolation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

from zephyr.security.llm_defense.llm_security.self_protection.isolation import (
    AccessPattern,
    IsolationLevel,
    IsolationPolicy,
    LSGIsolation,
)


class TestLSGIsolationInit:
    def test_default_level(self):
        iso = LSGIsolation()
        assert iso.level == IsolationLevel.PROCESS

    def test_custom_level(self):
        iso = LSGIsolation(level=IsolationLevel.STRICT)
        assert iso.level == IsolationLevel.STRICT

    def test_policy_available(self):
        iso = LSGIsolation()
        assert isinstance(iso.policy, IsolationPolicy)


class TestFileAccess:
    def test_llm_security_dir_allowed(self):
        iso = LSGIsolation()
        result = iso.check_file_access("src/zephyr/llm-security/layers/l1_input.py", AccessPattern.FILE_READ)
        assert result is True

    def test_tmp_dir_allowed(self):
        iso = LSGIsolation()
        result = iso.check_file_access("/tmp/test.log", AccessPattern.FILE_WRITE)
        assert result is True

    def test_random_dir_blocked(self):
        iso = LSGIsolation()
        result = iso.check_file_access("/etc/shadow", AccessPattern.FILE_READ)
        assert result is False

    def test_journals_dir_allowed(self):
        iso = LSGIsolation()
        result = iso.check_file_access("_journals/daily.md", AccessPattern.FILE_READ)
        assert result is True

    def test_windows_tmp_allowed(self):
        iso = LSGIsolation()
        result = iso.check_file_access("C:\\tmp\\test.log", AccessPattern.FILE_WRITE)
        assert result is True


class TestNetworkAccess:
    def test_localhost_allowed(self):
        iso = LSGIsolation()
        result = iso.check_network_access("localhost:8080")
        assert result is True

    def test_127_allowed(self):
        iso = LSGIsolation()
        result = iso.check_network_access("127.0.0.1:3000")
        assert result is True

    def test_external_blocked(self):
        iso = LSGIsolation()
        result = iso.check_network_access("evil.example.com")
        assert result is False


class TestSubprocessCheck:
    def test_subprocess_always_blocked(self):
        iso = LSGIsolation()
        result = iso.check_subprocess("python -c 'import os'")
        assert result is False

    def test_subprocess_benign_blocked(self):
        iso = LSGIsolation()
        result = iso.check_subprocess("echo hello")
        assert result is False


class TestModuleImport:
    def test_whitelisted_module_allowed(self):
        iso = LSGIsolation()
        result = iso.check_module_import("asyncio")
        assert result is True

    def test_llm_security_submodule_allowed(self):
        iso = LSGIsolation()
        result = iso.check_module_import("src.zephyr.security.llm_defense.llm_security.layers.l1_input")
        assert result is True

    def test_forbidden_module_blocked(self):
        iso = LSGIsolation()
        result = iso.check_module_import("subprocess")
        assert result is False

    def test_socket_blocked(self):
        iso = LSGIsolation()
        result = iso.check_module_import("socket")
        assert result is False

    def test_requests_blocked(self):
        iso = LSGIsolation()
        result = iso.check_module_import("requests")
        assert result is False

    def test_unknown_module_blocked(self):
        iso = LSGIsolation()
        result = iso.check_module_import("sklearn")
        assert result is False


class TestAuditLog:
    def test_audit_log_records_denials(self):
        iso = LSGIsolation()
        iso.check_subprocess("rm -rf /")
        iso.check_network_access("evil.com")
        log = iso.audit_log
        assert len(log) >= 2
        denied = [e for e in log if not e.allowed]
        assert len(denied) >= 2

    def test_audit_log_records_file_access(self):
        iso = LSGIsolation()
        iso.check_file_access("src/zephyr/llm-security/test.py", AccessPattern.FILE_READ)
        log = iso.audit_log
        assert len(log) >= 1
