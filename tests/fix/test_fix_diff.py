# [A_test] module_id: MOD-GOV_fix_diff | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] tests.test_fix_diff
# [INVARIANTS] diff MUST show before/after; MUST be reversible
# [MODIFY-GUARD] blueprint.md §3; fix_diff.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assertion errors on invariant violation
# [TESTS] tests/test_fix_diff.py
# [TTL] task_bound

from __future__ import annotations

import hashlib

from zephyr.infrastructure.auto_fix_engine.fix_diff import FixDiff
from zephyr.infrastructure.auto_fix_engine.models import FixAction


class TestFixDiffCompute:
    def test_compute_with_changes(self):
        action = FixAction(
            action_type="test",
            target="file.py",
            before="line1\nline2\n",
            after="line1\nline3\n",
        )
        result = FixDiff.compute(action)
        assert result["has_changes"] is True
        assert "unified_diff" in result
        assert result["stats"]["before_hash"] != result["stats"]["after_hash"]

    def test_compute_no_changes(self):
        action = FixAction(
            action_type="test",
            target="file.py",
            before="same\n",
            after="same\n",
        )
        result = FixDiff.compute(action)
        assert result["has_changes"] is False
        assert result["stats"]["before_hash"] == result["stats"]["after_hash"]

    def test_compute_empty_before_and_after(self):
        action = FixAction(action_type="test", target="file.py", before="", after="")
        result = FixDiff.compute(action)
        assert result["has_changes"] is False
        assert result["unified_diff"] == ""
        assert result["stats"] == {}

    def test_compute_addition_only(self):
        action = FixAction(
            action_type="test",
            target="file.py",
            before="",
            after="new_line\n",
        )
        result = FixDiff.compute(action)
        assert result["has_changes"] is True
        assert result["stats"]["added"] >= 1

    def test_compute_deletion_only(self):
        action = FixAction(
            action_type="test",
            target="file.py",
            before="old_line\n",
            after="",
        )
        result = FixDiff.compute(action)
        assert result["has_changes"] is True
        assert result["stats"]["removed"] >= 1

    def test_compute_stats_hashes(self):
        action = FixAction(
            action_type="test",
            target="file.py",
            before="abc",
            after="def",
        )
        result = FixDiff.compute(action)
        expected_before = hashlib.sha256(b"abc").hexdigest()[:16]
        expected_after = hashlib.sha256(b"def").hexdigest()[:16]
        assert result["stats"]["before_hash"] == expected_before
        assert result["stats"]["after_hash"] == expected_after

    def test_compute_multiline_diff(self):
        before = "import os\nimport sys\n"
        after = "import os\nimport pathlib\n"
        action = FixAction(action_type="import_fix", target="mod.py", before=before, after=after)
        result = FixDiff.compute(action)
        assert result["has_changes"] is True
        assert "import sys" in result["unified_diff"] or "-import sys" in result["unified_diff"]


class TestFixDiffComputeText:
    def test_compute_text_with_changes(self):
        result = FixDiff.compute_text("old\n", "new\n", "test_file")
        assert result["has_changes"] is True
        assert "unified_diff" in result

    def test_compute_text_no_changes(self):
        result = FixDiff.compute_text("same\n", "same\n", "test_file")
        assert result["has_changes"] is False

    def test_compute_text_empty_strings(self):
        result = FixDiff.compute_text("", "", "test_file")
        assert result["has_changes"] is False

    def test_compute_text_label_in_diff(self):
        result = FixDiff.compute_text("a\n", "b\n", "my_module")
        assert "my_module" in result["unified_diff"]

    def test_compute_text_stats(self):
        result = FixDiff.compute_text("line1\n", "line2\n", "f")
        assert "added" in result["stats"]
        assert "removed" in result["stats"]


class TestFixDiffReverse:
    def test_reverse_swaps_before_after(self):
        action = FixAction(
            action_type="test",
            target="file.py",
            before="old_content",
            after="new_content",
        )
        reversed_action = FixDiff.reverse(action)
        assert reversed_action.before == "new_content"
        assert reversed_action.after == "old_content"

    def test_reverse_preserves_target(self):
        action = FixAction(action_type="test", target="some/path.py", before="a", after="b")
        reversed_action = FixDiff.reverse(action)
        assert reversed_action.target == "some/path.py"

    def test_reverse_preserves_action_type(self):
        action = FixAction(action_type="drift_fix", target="f.py", before="x", after="y")
        reversed_action = FixDiff.reverse(action)
        assert reversed_action.action_type == "drift_fix"

    def test_reverse_double_reverse_restores_original(self):
        action = FixAction(action_type="test", target="f.py", before="original", after="modified")
        reversed_once = FixDiff.reverse(action)
        reversed_twice = FixDiff.reverse(reversed_once)
        assert reversed_twice.before == "original"
        assert reversed_twice.after == "modified"

    def test_reverse_empty_strings(self):
        action = FixAction(action_type="test", target="f.py", before="", after="content")
        reversed_action = FixDiff.reverse(action)
        assert reversed_action.before == "content"
        assert reversed_action.after == ""
