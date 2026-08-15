# [A_test] module_id: MOD-GOV_semantic_rollback_tag | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §6.12
# [MODULE] tests.test_semantic_rollback_tag
# [INVARIANTS] tag format: rollback/{type}-{id}:{phase}; returns None on git failure
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 = all pass
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from zephyr.infrastructure.rollback.semantic_rollback_tag import (
    RollbackTag,
    SemanticRollbackTag,
    TagType,
)


class TestTagType:
    def test_enum_values(self):
        assert TagType.TASK.value == "task"
        assert TagType.REFACTOR.value == "refactor"
        assert TagType.MIGRATION.value == "migration"

    def test_str_enum_comparison(self):
        assert TagType.TASK == "task"


class TestRollbackTag:
    def test_creation(self):
        tag = RollbackTag(
            tag_name="rollback/task-001:before",
            tag_type=TagType.TASK,
            target_id="001",
            phase="before",
            commit_sha="abc1234",
            created_at="2026-01-01T00:00:00+00:00",
        )
        assert tag.tag_name == "rollback/task-001:before"
        assert tag.tag_type == TagType.TASK
        assert tag.phase == "before"


class TestSemanticRollbackTagInit:
    def test_default_project_root(self):
        mgr = SemanticRollbackTag()
        assert mgr.project_root == Path.cwd()

    def test_custom_project_root(self, tmp_path):
        mgr = SemanticRollbackTag(project_root=tmp_path)
        assert mgr.project_root == tmp_path


class TestTagTask:
    @patch("zephyr.infrastructure.rollback.semantic_rollback_tag.run_subprocess_hidden")
    def test_tag_task_before(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(stdout="abc1234", returncode=0)
        mgr = SemanticRollbackTag(project_root=tmp_path)
        tag = mgr.tag_task("TASK-042", "before")
        assert tag is not None
        assert isinstance(tag, RollbackTag)
        assert tag.tag_name == "rollback/task-TASK-042:before"
        assert tag.tag_type == TagType.TASK
        assert tag.target_id == "TASK-042"
        assert tag.phase == "before"

    @patch("zephyr.infrastructure.rollback.semantic_rollback_tag.run_subprocess_hidden")
    def test_tag_task_after(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(stdout="def5678", returncode=0)
        mgr = SemanticRollbackTag(project_root=tmp_path)
        tag = mgr.tag_task("TASK-099", "after")
        assert tag is not None
        assert tag.tag_name == "rollback/task-TASK-099:after"
        assert tag.phase == "after"

    @patch("zephyr.infrastructure.rollback.semantic_rollback_tag.run_subprocess_hidden")
    def test_tag_task_git_failure_returns_none(self, mock_run, tmp_path):
        mock_run.side_effect = subprocess.SubprocessError("git not found")
        mgr = SemanticRollbackTag(project_root=tmp_path)
        tag = mgr.tag_task("TASK-001", "before")
        assert tag is None

    @patch("zephyr.infrastructure.rollback.semantic_rollback_tag.run_subprocess_hidden")
    def test_tag_task_empty_sha_returns_none(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(stdout="", returncode=0)
        mgr = SemanticRollbackTag(project_root=tmp_path)
        tag = mgr.tag_task("TASK-001", "before")
        assert tag is None


class TestTagRefactor:
    @patch("zephyr.infrastructure.rollback.semantic_rollback_tag.run_subprocess_hidden")
    def test_tag_refactor_before(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(stdout="abc1234", returncode=0)
        mgr = SemanticRollbackTag(project_root=tmp_path)
        tag = mgr.tag_refactor("auth", "before")
        assert tag is not None
        assert tag.tag_name == "rollback/refactor/auth:before"
        assert tag.tag_type == TagType.REFACTOR
        assert tag.target_id == "auth"

    @patch("zephyr.infrastructure.rollback.semantic_rollback_tag.run_subprocess_hidden")
    def test_tag_refactor_after(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(stdout="abc1234", returncode=0)
        mgr = SemanticRollbackTag(project_root=tmp_path)
        tag = mgr.tag_refactor("budget", "after")
        assert tag is not None
        assert tag.tag_name == "rollback/refactor/budget:after"


class TestTagMigration:
    @patch("zephyr.infrastructure.rollback.semantic_rollback_tag.run_subprocess_hidden")
    def test_tag_migration_before(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(stdout="abc1234", returncode=0)
        mgr = SemanticRollbackTag(project_root=tmp_path)
        tag = mgr.tag_migration("MIG-001", "before")
        assert tag is not None
        assert tag.tag_name == "rollback/migration/MIG-001:before"
        assert tag.tag_type == TagType.MIGRATION

    @patch("zephyr.infrastructure.rollback.semantic_rollback_tag.run_subprocess_hidden")
    def test_tag_migration_git_failure(self, mock_run, tmp_path):
        mock_run.side_effect = Exception("no git")
        mgr = SemanticRollbackTag(project_root=tmp_path)
        tag = mgr.tag_migration("MIG-001", "before")
        assert tag is None


class TestListTags:
    @patch("zephyr.infrastructure.rollback.semantic_rollback_tag.run_subprocess_hidden")
    def test_list_all_tags(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(
            stdout="rollback/task-001:before\nrollback/refactor/auth:after\n", returncode=0
        )
        mgr = SemanticRollbackTag(project_root=tmp_path)
        tags = mgr.list_tags()
        assert len(tags) == 2

    @patch("zephyr.infrastructure.rollback.semantic_rollback_tag.run_subprocess_hidden")
    def test_list_tags_filtered_by_type_prefix_mismatch(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(
            stdout="rollback/task-001:before\nrollback/refactor/auth:after\n", returncode=0
        )
        mgr = SemanticRollbackTag(project_root=tmp_path)
        tags = mgr.list_tags(TagType.TASK)
        assert len(tags) == 0

    @patch("zephyr.infrastructure.rollback.semantic_rollback_tag.run_subprocess_hidden")
    def test_list_tags_git_failure(self, mock_run, tmp_path):
        mock_run.side_effect = Exception("git error")
        mgr = SemanticRollbackTag(project_root=tmp_path)
        tags = mgr.list_tags()
        assert tags == []

    @patch("zephyr.infrastructure.rollback.semantic_rollback_tag.run_subprocess_hidden")
    def test_list_tags_empty(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(stdout="", returncode=0)
        mgr = SemanticRollbackTag(project_root=tmp_path)
        tags = mgr.list_tags()
        assert tags == []


class TestResolveTag:
    @patch("zephyr.infrastructure.rollback.semantic_rollback_tag.run_subprocess_hidden")
    def test_resolve_existing_tag(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(stdout="full_sha_here\n", returncode=0)
        mgr = SemanticRollbackTag(project_root=tmp_path)
        sha = mgr.resolve_tag("rollback/task-001:before")
        assert sha == "full_sha_here"

    @patch("zephyr.infrastructure.rollback.semantic_rollback_tag.run_subprocess_hidden")
    def test_resolve_nonexistent_tag(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(stdout="", returncode=128)
        mgr = SemanticRollbackTag(project_root=tmp_path)
        sha = mgr.resolve_tag("rollback/task-999:before")
        assert sha is None

    @patch("zephyr.infrastructure.rollback.semantic_rollback_tag.run_subprocess_hidden")
    def test_resolve_tag_exception(self, mock_run, tmp_path):
        mock_run.side_effect = Exception("error")
        mgr = SemanticRollbackTag(project_root=tmp_path)
        sha = mgr.resolve_tag("rollback/task-001:before")
        assert sha is None


class TestDeleteTagSafe:
    @patch("zephyr.infrastructure.rollback.semantic_rollback_tag.run_subprocess_hidden")
    def test_delete_success(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(returncode=0)
        mgr = SemanticRollbackTag(project_root=tmp_path)
        assert mgr.delete_tag_safe("rollback/task-001:before") is True

    @patch("zephyr.infrastructure.rollback.semantic_rollback_tag.run_subprocess_hidden")
    def test_delete_failure(self, mock_run, tmp_path):
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")
        mgr = SemanticRollbackTag(project_root=tmp_path)
        assert mgr.delete_tag_safe("rollback/task-001:before") is False


class TestFindTaskTags:
    @patch("zephyr.infrastructure.rollback.semantic_rollback_tag.run_subprocess_hidden")
    def test_find_matching_task_tags_prefix_mismatch(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(
            stdout="rollback/task-001:before\nrollback/task-001:after\nrollback/task-002:before\n",
            returncode=0,
        )
        mgr = SemanticRollbackTag(project_root=tmp_path)
        tags = mgr.find_task_tags("001")
        assert len(tags) == 0

    @patch("zephyr.infrastructure.rollback.semantic_rollback_tag.run_subprocess_hidden")
    def test_find_no_matching_tags(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(stdout="rollback/task-001:before\n", returncode=0)
        mgr = SemanticRollbackTag(project_root=tmp_path)
        tags = mgr.find_task_tags("999")
        assert tags == []
