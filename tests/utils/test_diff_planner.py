# [A_test] module_id: MOD-GOV_diff_planner | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-378 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_diff_planner
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/test_diff_planner.py
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

from zephyr.shared.reliability.diff_planner import (
    ChangePlan,
    DiffHunk,
    DiffPlanner,
    FileDiff,
)


class TestDiffPlannerInstantiation:
    def test_default_construction(self):
        planner = DiffPlanner()
        assert planner._project_root == Path.cwd()

    def test_custom_project_root(self, tmp_path):
        planner = DiffPlanner(project_root=tmp_path)
        assert planner._project_root == tmp_path


class TestComputeDiff:
    def test_nonexistent_file_returns_create_diff(self, tmp_path):
        planner = DiffPlanner(project_root=tmp_path)
        diff = planner.compute_diff("new_file.py", "print('hello')\n")
        assert diff.exists is False
        assert diff.file_path == "new_file.py"
        assert len(diff.hunks) == 1
        assert diff.hunks[0].old_count == 0
        assert diff.added_lines > 0

    def test_existing_file_returns_modify_diff(self, tmp_path):
        p = tmp_path / "existing.py"
        p.write_text("old line\n", encoding="utf-8")

        planner = DiffPlanner(project_root=tmp_path)
        diff = planner.compute_diff("existing.py", "new line\n")
        assert diff.exists is True
        assert len(diff.hunks) > 0

    def test_identical_content_no_hunks(self, tmp_path):
        content = "same line\n"
        p = tmp_path / "same.py"
        p.write_text(content, encoding="utf-8")

        planner = DiffPlanner(project_root=tmp_path)
        diff = planner.compute_diff("same.py", content)
        assert diff.exists is True
        assert len(diff.hunks) == 0

    def test_empty_new_content_for_existing_file(self, tmp_path):
        p = tmp_path / "has_content.py"
        p.write_text("line1\nline2\n", encoding="utf-8")

        planner = DiffPlanner(project_root=tmp_path)
        diff = planner.compute_diff("has_content.py", "")
        assert diff.exists is True
        assert len(diff.hunks) > 0
        assert diff.removed_lines > 0

    def test_empty_new_content_for_nonexistent_file(self, tmp_path):
        planner = DiffPlanner(project_root=tmp_path)
        diff = planner.compute_diff("ghost.py", "")
        assert diff.exists is False
        assert len(diff.hunks) == 1
        assert diff.hunks[0].new_count == 0

    def test_multiline_diff_hunks(self, tmp_path):
        old = "line1\nline2\nline3\n"
        new = "line1\nchanged\nline3\n"
        p = tmp_path / "multi.py"
        p.write_text(old, encoding="utf-8")

        planner = DiffPlanner(project_root=tmp_path)
        diff = planner.compute_diff("multi.py", new)
        assert diff.exists is True
        assert any(h.old_lines != h.new_lines for h in diff.hunks)


class TestPlanChanges:
    def test_all_new_files(self, tmp_path):
        planner = DiffPlanner(project_root=tmp_path)
        outputs = [
            {"path": "new_a.py"},
            {"path": "new_b.py"},
        ]
        plan = planner.plan_changes(outputs)
        assert len(plan.files_to_create) == 2
        assert len(plan.files_to_modify) == 0
        assert plan.recommendation == "ALL_CREATE"
        assert plan.total_changes == 2

    def test_all_existing_files(self, tmp_path):
        (tmp_path / "exist_a.py").write_text("x", encoding="utf-8")
        (tmp_path / "exist_b.py").write_text("y", encoding="utf-8")

        planner = DiffPlanner(project_root=tmp_path)
        outputs = [
            {"path": "exist_a.py"},
            {"path": "exist_b.py"},
        ]
        plan = planner.plan_changes(outputs)
        assert len(plan.files_to_create) == 0
        assert len(plan.files_to_modify) == 2
        assert plan.recommendation == "ALL_MODIFY"

    def test_mixed_create_and_modify(self, tmp_path):
        (tmp_path / "exist.py").write_text("x", encoding="utf-8")

        planner = DiffPlanner(project_root=tmp_path)
        outputs = [
            {"path": "exist.py"},
            {"path": "new.py"},
        ]
        plan = planner.plan_changes(outputs)
        assert len(plan.files_to_create) == 1
        assert len(plan.files_to_modify) == 1
        assert plan.recommendation == "MIXED"

    def test_empty_downstream_outputs(self, tmp_path):
        planner = DiffPlanner(project_root=tmp_path)
        plan = planner.plan_changes([])
        assert plan.total_changes == 0
        assert plan.recommendation == "ALL_CREATE"

    def test_output_with_empty_path(self, tmp_path):
        planner = DiffPlanner(project_root=tmp_path)
        outputs = [{"path": ""}]
        plan = planner.plan_changes(outputs)
        assert plan.total_changes == 1
        assert len(plan.files_to_modify) == 1


class TestDiffHunkDataclass:
    def test_fields(self):
        hunk = DiffHunk(
            old_start=1,
            old_count=2,
            new_start=1,
            new_count=3,
            old_lines=["a\n", "b\n"],
            new_lines=["a\n", "c\n", "d\n"],
        )
        assert hunk.old_start == 1
        assert hunk.old_count == 2
        assert hunk.new_count == 3
        assert len(hunk.old_lines) == 2
        assert len(hunk.new_lines) == 3


class TestFileDiffDataclass:
    def test_default_values(self):
        fd = FileDiff(file_path="a.py", exists=True, hunks=[])
        assert fd.added_lines == 0
        assert fd.removed_lines == 0
        assert fd.changed_lines == 0


class TestChangePlanDataclass:
    def test_fields(self):
        plan = ChangePlan(
            files_to_create=["a.py"],
            files_to_modify=[],
            total_changes=1,
            recommendation="ALL_CREATE",
        )
        assert plan.total_changes == 1
        assert plan.recommendation == "ALL_CREATE"
