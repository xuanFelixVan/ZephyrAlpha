# [A_test] module_id: MOD-GOV_rule_injection_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.guards.rule_injection_guard
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
    from zephyr.security.access_control.guards.rule_injection_guard import (
        INJECTION_PATTERNS,
        RuleInjectionCheck,
        RuleInjectionGuard,
    )

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestRuleInjectionGuard:
    def setup_method(self):
        self.guard = RuleInjectionGuard()

    def test_check_clean_rule(self):
        result = self.guard.check("rule-1", "allow agent-1 read resource-A")
        assert isinstance(result, RuleInjectionCheck)
        assert result.injection_detected is False
        assert result.sanitized == "allow agent-1 read resource-A"
        assert result.injection_type == ""

    def test_check_import_os(self):
        result = self.guard.check("rule-2", "import os")
        assert result.injection_detected is True
        assert result.injection_type == "import os"

    def test_check_eval(self):
        result = self.guard.check("rule-3", "eval('malicious code')")
        assert result.injection_detected is True
        assert result.injection_type == "eval("

    def test_check_exec(self):
        result = self.guard.check("rule-4", "exec('dangerous')")
        assert result.injection_detected is True

    def test_check_subprocess(self):
        result = self.guard.check("rule-5", "import subprocess")
        assert result.injection_detected is True
        assert result.injection_type == "import subprocess"

    def test_check_case_insensitive(self):
        result = self.guard.check("rule-6", "IMPORT OS")
        assert result.injection_detected is True

    def test_check_empty_content(self):
        result = self.guard.check("rule-7", "")
        assert result.injection_detected is False
        assert result.sanitized == ""

    def test_check_shell_true(self):
        result = self.guard.check("rule-8", "subprocess.run(cmd, shell=True)")
        assert result.injection_detected is True

    def test_injection_patterns_not_empty(self):
        assert len(INJECTION_PATTERNS) > 0

    def test_check_globals_access(self):
        result = self.guard.check("rule-9", "globals()")
        assert result.injection_detected is True

    def test_check_open_file(self):
        result = self.guard.check("rule-10", "open('/etc/passwd')")
        assert result.injection_detected is True

    def test_check_rule_id_preserved(self):
        result = self.guard.check("my-rule-id", "clean content")
        assert result.rule_id == "my-rule-id"
