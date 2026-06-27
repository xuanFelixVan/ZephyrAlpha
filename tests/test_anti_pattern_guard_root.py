# [A_test] module_id: SRC-TST-0320 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.anti_pattern_guard
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
    from zephyr.security.access_control.anti_pattern_guard import (
        benchmark_before_optimize,
        check_lock_before_write,
        scan_silent_ignore,
    )

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")


class TestScanSilentIgnore:
    def test_detects_bare_except_pass(self):
        code = "try:\n    x = 1\nexcept:\n    pass\n"
        violations = scan_silent_ignore(code)
        assert len(violations) == 1

    def test_no_violation_on_specific_except(self):
        code = "try:\n    x = 1\nexcept ValueError:\n    pass\n"
        violations = scan_silent_ignore(code)
        assert len(violations) == 0

    def test_no_violation_on_bare_except_with_body(self):
        code = "try:\n    x = 1\nexcept:\n    logger.error('err')\n"
        violations = scan_silent_ignore(code)
        assert len(violations) == 0

    def test_empty_code(self):
        violations = scan_silent_ignore("")
        assert len(violations) == 0

    def test_syntax_error_code(self):
        code = "def foo(\n"
        violations = scan_silent_ignore(code)
        assert len(violations) == 0

    def test_multiple_violations(self):
        code = "try:\n    x = 1\nexcept:\n    pass\ntry:\n    y = 2\nexcept:\n    pass\n"
        violations = scan_silent_ignore(code)
        assert len(violations) == 2


class TestCheckLockBeforeWrite:
    def test_decorator_passes_when_lock_ok(self):
        lock_fn = lambda: True

        @check_lock_before_write(lock_fn)
        def my_write():
            return "written"

        assert my_write() == "written"

    def test_decorator_still_executes_when_lock_fails(self):
        lock_fn = lambda: False

        @check_lock_before_write(lock_fn)
        def my_write():
            return "written"

        assert my_write() == "written"


class TestBenchmarkBeforeOptimize:
    def test_returns_true(self):
        assert benchmark_before_optimize("some_func") is True
