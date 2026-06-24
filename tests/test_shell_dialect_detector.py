# [A_test] module_id: SRC-TST-1597 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §test
# [MODULE] tests.test_shell_dialect_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.security.access_control.shell_dialect_detector
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_shell_dialect_detector.py
from zephyr.security.access_control.shell_dialect_detector import (
    DANGEROUS_SHELL_PATTERNS,
    ShellDialectDetector,
    ShellDialectResult,
)


class TestShellDialectResult:
    def test_defaults(self):
        r = ShellDialectResult(command="ls")
        assert r.detected_dialect == "unknown"
        assert r.dangerous_patterns == []
        assert r.blocked is False


class TestDangerousPatterns:
    def test_all_dialects(self):
        assert "bash" in DANGEROUS_SHELL_PATTERNS
        assert "powershell" in DANGEROUS_SHELL_PATTERNS
        assert "cmd" in DANGEROUS_SHELL_PATTERNS
        assert "python" in DANGEROUS_SHELL_PATTERNS
        assert "perl" in DANGEROUS_SHELL_PATTERNS

    def test_bash_rm_rf(self):
        assert "rm -rf" in DANGEROUS_SHELL_PATTERNS["bash"]

    def test_powershell_iex(self):
        assert "Invoke-Expression" in DANGEROUS_SHELL_PATTERNS["powershell"]

    def test_python_eval(self):
        assert "eval(" in DANGEROUS_SHELL_PATTERNS["python"]


class TestShellDialectDetector:
    def test_instantiation(self):
        d = ShellDialectDetector()
        assert d is not None

    def test_detect_bash(self):
        d = ShellDialectDetector()
        r = d.detect("$(whoami)")
        assert r.detected_dialect == "bash"

    def test_detect_powershell(self):
        d = ShellDialectDetector()
        r = d.detect("Invoke-Expression 'cmd'")
        assert r.detected_dialect == "powershell"
        assert r.blocked is True

    def test_detect_cmd(self):
        d = ShellDialectDetector()
        r = d.detect("%SYSTEMROOT%\\system32")
        assert r.detected_dialect == "cmd"

    def test_detect_python(self):
        d = ShellDialectDetector()
        r = d.detect("eval('1+1')")
        assert r.detected_dialect == "python"
        assert r.blocked is True

    def test_detect_perl(self):
        d = ShellDialectDetector()
        r = d.detect("qx/ls/")
        assert r.detected_dialect == "perl"
        assert r.blocked is True

    def test_detect_unknown(self):
        d = ShellDialectDetector()
        r = d.detect("echo hello")
        assert r.detected_dialect == "unknown"
        assert r.blocked is False

    def test_bash_dangerous_rm_rf(self):
        d = ShellDialectDetector()
        r = d.detect("chmod +x script.sh && rm -rf /")
        assert r.detected_dialect == "bash"
        assert "rm -rf" in r.dangerous_patterns
        assert r.blocked is True

    def test_safe_command(self):
        d = ShellDialectDetector()
        r = d.detect("git status")
        assert r.blocked is False
        assert r.dangerous_patterns == []

    def test_result_preserves_command(self):
        d = ShellDialectDetector()
        r = d.detect("ls -la")
        assert r.command == "ls -la"

    def test_case_insensitive_detection(self):
        d = ShellDialectDetector()
        r = d.detect("IEX(malicious)")
        assert r.detected_dialect == "powershell"
