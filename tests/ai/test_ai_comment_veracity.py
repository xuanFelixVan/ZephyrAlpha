# [A_test] module_id: SRC-TST-0299 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_ai_comment_veracity
# [INVARIANTS] suspicious_patterns default=["always returns","never fails","guaranteed to","will never"]
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_ai_comment_veracity.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.feedback_loop.verifiers.ai_comment_veracity import (
    AICommentVeracity,
    VeracityLevel,
)


class TestAICommentVeracityInstantiation:
    def test_default_construction(self):
        acv = AICommentVeracity()
        assert len(acv.suspicious_patterns) == 4
        assert acv.total_comments == 0
        assert acv.flagged_comments == 0

    def test_custom_patterns(self):
        acv = AICommentVeracity(suspicious_patterns=["custom pattern"])
        assert len(acv.suspicious_patterns) == 1


class TestCheckComment:
    def test_verified_clean_comment(self):
        acv = AICommentVeracity()
        result = acv.check_comment("file.py", 10, "Returns the computed value")
        assert result == VeracityLevel.VERIFIED
        assert acv.total_comments == 1
        assert acv.flagged_comments == 0

    def test_suspicious_always_returns(self):
        acv = AICommentVeracity()
        result = acv.check_comment("file.py", 20, "This always returns True")
        assert result == VeracityLevel.SUSPICIOUS
        assert acv.flagged_comments == 1

    def test_suspicious_never_fails(self):
        acv = AICommentVeracity()
        result = acv.check_comment("file.py", 30, "This never fails")
        assert result == VeracityLevel.SUSPICIOUS

    def test_suspicious_guaranteed_to(self):
        acv = AICommentVeracity()
        result = acv.check_comment("file.py", 40, "Guaranteed to work")
        assert result == VeracityLevel.SUSPICIOUS

    def test_suspicious_will_never(self):
        acv = AICommentVeracity()
        result = acv.check_comment("file.py", 50, "This will never break")
        assert result == VeracityLevel.SUSPICIOUS

    def test_case_insensitive(self):
        acv = AICommentVeracity()
        result = acv.check_comment("file.py", 60, "ALWAYS RETURNS valid data")
        assert result == VeracityLevel.SUSPICIOUS

    def test_empty_comment(self):
        acv = AICommentVeracity()
        result = acv.check_comment("file.py", 70, "")
        assert result == VeracityLevel.VERIFIED

    def test_finding_recorded(self):
        acv = AICommentVeracity()
        acv.check_comment("file.py", 80, "always returns True")
        assert len(acv.findings) == 1
        assert acv.findings[0]["file"] == "file.py"
        assert acv.findings[0]["line"] == 80


class TestGetVeracityScore:
    def test_no_comments(self):
        acv = AICommentVeracity()
        assert acv.get_veracity_score() == pytest.approx(1.0)

    def test_all_verified(self):
        acv = AICommentVeracity()
        acv.check_comment("f.py", 1, "normal comment")
        acv.check_comment("f.py", 2, "another comment")
        assert acv.get_veracity_score() == pytest.approx(1.0)

    def test_mixed(self):
        acv = AICommentVeracity()
        acv.check_comment("f.py", 1, "always returns True")
        acv.check_comment("f.py", 2, "normal comment")
        assert acv.get_veracity_score() == pytest.approx(0.5)


class TestGetSuspiciousFiles:
    def test_no_suspicious(self):
        acv = AICommentVeracity()
        assert acv.get_suspicious_files() == []

    def test_single_suspicious_file(self):
        acv = AICommentVeracity()
        acv.check_comment("bad.py", 1, "always returns True")
        assert acv.get_suspicious_files() == ["bad.py"]

    def test_deduplication(self):
        acv = AICommentVeracity()
        acv.check_comment("bad.py", 1, "always returns True")
        acv.check_comment("bad.py", 2, "never fails here")
        files = acv.get_suspicious_files()
        assert len(files) == 1
        assert files[0] == "bad.py"

    def test_multiple_files(self):
        acv = AICommentVeracity()
        acv.check_comment("a.py", 1, "always returns True")
        acv.check_comment("b.py", 1, "never fails")
        assert len(acv.get_suspicious_files()) == 2
