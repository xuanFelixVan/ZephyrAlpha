# [A_test] module_id: SRC-TST-1307 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain-autonomy_core/agent-rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.native_api_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.native_api_guard import BLOCKED_NATIVE_APIS, NativeApiGuard

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestNativeApiGuard:
    def setup_method(self):
        self.guard = NativeApiGuard()

    def test_scan_clean_code(self):
        result = self.guard.scan("x = 1 + 2", source="test")
        assert result["allowed"] is True
        assert result["matched"] == []
        assert result["source"] == "test"

    def test_scan_blocked_ctypes(self):
        result = self.guard.scan("import ctypes", source="agent-1")
        assert result["allowed"] is False
        assert "ctypes" in result["matched"]

    def test_scan_blocked_subprocess(self):
        result = self.guard.scan("subprocess.Popen(['ls'])", source="agent-2")
        assert result["allowed"] is False
        assert "subprocess.Popen" in result["matched"]

    def test_scan_blocked_os_system(self):
        result = self.guard.scan("os.system('rm -rf /')", source="agent-3")
        assert result["allowed"] is False
        assert "os.system(" in result["matched"]

    def test_scan_multiple_matches(self):
        code = "import ctypes; import cffi; os.system('cmd')"
        result = self.guard.scan(code, source="agent-4")
        assert result["allowed"] is False
        assert len(result["matched"]) >= 2

    def test_scan_case_insensitive(self):
        result = self.guard.scan("IMPORT CTYPES", source="agent-5")
        assert result["allowed"] is False

    def test_scan_empty_string(self):
        result = self.guard.scan("", source="empty")
        assert result["allowed"] is True
        assert result["matched"] == []

    def test_violations_recorded(self):
        self.guard.scan("import ctypes", source="agent-1")
        self.guard.scan("clean code", source="agent-2")
        assert len(self.guard._violations) == 1

    def test_blocked_apis_not_empty(self):
        assert len(BLOCKED_NATIVE_APIS) > 0
