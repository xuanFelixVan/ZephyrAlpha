# [A_test] module_id: SRC-TST-1792 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.guards.vibe_coding_guard
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
    from zephyr.security.access_control.guards.vibe_coding_guard import (
        VIBE_CODING_PATTERNS,
        VibeCodingAudit,
        VibeCodingGuard,
    )

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)


@pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)
class TestVibeCodingGuard:
    def setup_method(self):
        self.guard = VibeCodingGuard()

    def test_scan_clean_content(self):
        result = self.guard.scan("clean.py", "x = 1\ny = 2\n")
        assert result.file_path == "clean.py"
        assert result.detected == []
        assert result.risk_score == 0.0

    def test_scan_single_pattern(self):
        content = "allow_all = True\n"
        result = self.guard.scan("bad.py", content)
        assert len(result.detected) == 1
        assert result.risk_score > 0.0

    def test_scan_multiple_patterns(self):
        content = "allow_all = True\n# bypass permission check\nif debug_mode:\n    pass\n"
        result = self.guard.scan("bad.py", content)
        assert len(result.detected) >= 2

    def test_scan_empty_content(self):
        result = self.guard.scan("empty.py", "")
        assert result.lines_total == 0
        assert result.detected == []
        assert result.risk_score == 0.0

    def test_scan_lines_total(self):
        content = "line1\nline2\nline3\n"
        result = self.guard.scan("test.py", content)
        assert result.lines_total == 3

    def test_scan_ai_generated_lines(self):
        content = "# comment\ncode = 1\n# another comment\n"
        result = self.guard.scan("test.py", content)
        assert result.ai_generated_lines == 2

    def test_scan_risk_score_cap(self):
        patterns = "\n".join(VIBE_CODING_PATTERNS)
        result = self.guard.scan("worst.py", patterns)
        assert result.risk_score <= 100.0

    def test_scan_case_insensitive(self):
        content = "ALLOW_ALL = TRUE\n"
        result = self.guard.scan("upper.py", content)
        assert len(result.detected) == 1


@pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)
class TestVibeCodingAudit:
    def test_default_values(self):
        audit = VibeCodingAudit(file_path="test.py")
        assert audit.lines_total == 0
        assert audit.ai_generated_lines == 0
        assert audit.detected == []
        assert audit.risk_score == 0.0

    def test_custom_values(self):
        audit = VibeCodingAudit(
            file_path="test.py",
            lines_total=10,
            ai_generated_lines=3,
            detected=["L1: pattern"],
            risk_score=15.0,
        )
        assert audit.lines_total == 10
        assert audit.ai_generated_lines == 3
        assert len(audit.detected) == 1
        assert audit.risk_score == 15.0


@pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)
class TestVibeCodingPatterns:
    def test_patterns_non_empty(self):
        assert len(VIBE_CODING_PATTERNS) > 0

    def test_patterns_are_strings(self):
        for pattern in VIBE_CODING_PATTERNS:
            assert isinstance(pattern, str)
            assert len(pattern) > 0
