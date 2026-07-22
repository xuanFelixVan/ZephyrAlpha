# [A_test] module_id: MOD-GOV_utils_diff_utils | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_utils_diff_utils

# [INVARIANTS] compute_diff无变更返回空串;apply_patch严格模式行号匹配;similarity_ratio 0-1

# [MODIFY-GUARD] diff_utils.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] PatchConflictError

# [TESTS] pytest tests/test_utils_diff_utils.py -q
# [TTL] task_bound

import pytest

from zephyr.shared.utils.diff_utils import (
    PatchConflictError,
    apply_patch,
    compute_diff,
    similarity_ratio,
    try_apply_patch,
)


class TestComputeDiff:
    def test_no_change_returns_empty(self):
        result = compute_diff("hello\n", "hello\n")
        assert result == ""

    def test_change_produces_diff(self):
        original = "line1\nline2\nline3\n"
        modified = "line1\nchanged\nline3\n"
        result = compute_diff(original, modified)
        assert "-line2" in result
        assert "+changed" in result

    def test_custom_file_names(self):
        result = compute_diff("a\n", "b\n", from_file="old.txt", to_file="new.txt")
        assert "old.txt" in result
        assert "new.txt" in result

    def test_empty_original(self):
        result = compute_diff("", "new line\n")
        assert "+new line" in result

    def test_empty_modified(self):
        result = compute_diff("old line\n", "")
        assert "-old line" in result


class TestApplyPatch:
    def test_simple_patch(self):
        original = "line1\nline2\nline3\n"
        diff = compute_diff(original, "line1\nchanged\nline3\n")
        result = apply_patch(original, diff)
        assert result == "line1\nchanged\nline3\n"

    def test_add_line(self):
        original = "line1\nline3\n"
        modified = "line1\nline2\nline3\n"
        diff = compute_diff(original, modified)
        result = apply_patch(original, diff)
        assert result == modified

    def test_remove_line(self):
        original = "line1\nline2\nline3\n"
        modified = "line1\nline3\n"
        diff = compute_diff(original, modified)
        result = apply_patch(original, diff)
        assert result == modified

    def test_strict_mode_line_mismatch_raises(self):
        patch = "@@ -5,1 +5,1 @@\n-old\n+new\n"
        with pytest.raises(PatchConflictError, match="Line mismatch"):
            apply_patch("original\n", patch, strict=True)

    def test_non_strict_mode_tolerant(self):
        original = "line1\nline2\nline3\n"
        modified = "line1\nchanged\nline3\n"
        diff = compute_diff(original, modified)
        result = apply_patch(original, diff, strict=False)
        assert "changed" in result


class TestTryApplyPatch:
    def test_success(self):
        original = "hello\n"
        modified = "world\n"
        diff = compute_diff(original, modified)
        ok, result = try_apply_patch(original, diff)
        assert ok is True
        assert result == modified

    def test_strict_conflict_raises_patch_conflict_error(self):
        original = "hello\n"
        bad_patch = "@@ -5,1 +5,1 @@\n-old\n+new\n"
        with pytest.raises(PatchConflictError):
            apply_patch(original, bad_patch, strict=True)

    def test_nonstrict_applies_what_it_can(self):
        original = "hello\n"
        patch = "@@ -1,1 +1,1 @@\n-hello\n+world\n"
        ok, result = try_apply_patch(original, patch)
        assert ok is True
        assert "world" in result


class TestSimilarityRatio:
    def test_identical(self):
        assert similarity_ratio("abc", "abc") == 1.0

    def test_completely_different(self):
        assert similarity_ratio("abc", "xyz") == 0.0

    def test_partial(self):
        ratio = similarity_ratio("hello world", "hello earth")
        assert 0.0 < ratio < 1.0

    def test_empty_strings(self):
        assert similarity_ratio("", "") == 1.0

    def test_one_empty(self):
        assert similarity_ratio("abc", "") == 0.0
