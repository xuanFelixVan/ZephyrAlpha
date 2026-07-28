# [A_test] module_id: MOD-GOV_rollback_context_restorer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_rollback_context_restorer
# [INVARIANTS] generate_restore_prompt writes file and returns str; inject_for_session returns dict with session_id/prompt/prompt_file/generated_at
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RestoreContext fields must be str/list[str]
# [TESTS] tests/test_rollback_context_restorer.py
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

from zephyr.infrastructure.rollback.rollback_context_restorer import (
    RestoreContext,
    RollbackContextRestorer,
)


class TestRestoreContext:
    def test_create_with_all_fields(self):
        ctx = RestoreContext(
            rollback_reason="test failure",
            reverted_commit="abc1234",
            files_affected=["a.py", "b.py"],
            session_id="session-001",
            action_plan="Re-run tests",
        )
        assert ctx.rollback_reason == "test failure"
        assert ctx.reverted_commit == "abc1234"
        assert ctx.files_affected == ["a.py", "b.py"]
        assert ctx.session_id == "session-001"
        assert ctx.action_plan == "Re-run tests"

    def test_empty_files_list(self):
        ctx = RestoreContext(
            rollback_reason="reason",
            reverted_commit="abc1234",
            files_affected=[],
            session_id="session-002",
            action_plan="Do nothing",
        )
        assert ctx.files_affected == []

    def test_many_files_affected(self):
        files = [f"file_{i}.py" for i in range(20)]
        ctx = RestoreContext(
            rollback_reason="reason",
            reverted_commit="abc1234",
            files_affected=files,
            session_id="session-003",
            action_plan="Check all",
        )
        assert len(ctx.files_affected) == 20


class TestRollbackContextRestorerInstantiation:
    def test_default_project_root(self):
        r = RollbackContextRestorer()
        assert r.project_root == Path.cwd()

    def test_custom_project_root(self, tmp_path: Path):
        r = RollbackContextRestorer(project_root=tmp_path)
        assert r.project_root == tmp_path

    def test_none_project_root(self):
        r = RollbackContextRestorer(project_root=None)
        assert r.project_root == Path.cwd()

    def test_prompt_path_set(self, tmp_path: Path):
        r = RollbackContextRestorer(project_root=tmp_path)
        assert r.prompt_path == tmp_path / r.PROMPT_FILE


class TestGenerateRestorePrompt:
    def test_returns_string(self, tmp_path: Path):
        r = RollbackContextRestorer(project_root=tmp_path)
        ctx = RestoreContext(
            rollback_reason="test failure",
            reverted_commit="abc1234",
            files_affected=["a.py"],
            session_id="session-001",
            action_plan="Re-run tests",
        )
        result = r.generate_restore_prompt(ctx)
        assert isinstance(result, str)

    def test_contains_reason(self, tmp_path: Path):
        r = RollbackContextRestorer(project_root=tmp_path)
        ctx = RestoreContext(
            rollback_reason="pipeline broke",
            reverted_commit="abc1234",
            files_affected=["a.py"],
            session_id="session-001",
            action_plan="Re-run tests",
        )
        result = r.generate_restore_prompt(ctx)
        assert "pipeline broke" in result

    def test_contains_commit(self, tmp_path: Path):
        r = RollbackContextRestorer(project_root=tmp_path)
        ctx = RestoreContext(
            rollback_reason="test",
            reverted_commit="deadbeef",
            files_affected=["a.py"],
            session_id="session-001",
            action_plan="Re-run tests",
        )
        result = r.generate_restore_prompt(ctx)
        assert "deadbeef" in result

    def test_contains_session_id(self, tmp_path: Path):
        r = RollbackContextRestorer(project_root=tmp_path)
        ctx = RestoreContext(
            rollback_reason="test",
            reverted_commit="abc1234",
            files_affected=["a.py"],
            session_id="session-20260522-006",
            action_plan="Re-run tests",
        )
        result = r.generate_restore_prompt(ctx)
        assert "session-20260522-006" in result

    def test_contains_action_plan(self, tmp_path: Path):
        r = RollbackContextRestorer(project_root=tmp_path)
        ctx = RestoreContext(
            rollback_reason="test",
            reverted_commit="abc1234",
            files_affected=["a.py"],
            session_id="session-001",
            action_plan="Verify and re-apply changes",
        )
        result = r.generate_restore_prompt(ctx)
        assert "Verify and re-apply changes" in result

    def test_limits_files_to_10(self, tmp_path: Path):
        r = RollbackContextRestorer(project_root=tmp_path)
        files = [f"file_{i}.py" for i in range(20)]
        ctx = RestoreContext(
            rollback_reason="test",
            reverted_commit="abc1234",
            files_affected=files,
            session_id="session-001",
            action_plan="Check",
        )
        result = r.generate_restore_prompt(ctx)
        assert "file_0.py" in result
        assert "file_9.py" in result

    def test_writes_prompt_file(self, tmp_path: Path):
        r = RollbackContextRestorer(project_root=tmp_path)
        ctx = RestoreContext(
            rollback_reason="test",
            reverted_commit="abc1234",
            files_affected=["a.py"],
            session_id="session-001",
            action_plan="Re-run",
        )
        r.generate_restore_prompt(ctx)
        assert r.prompt_path.exists()
        content = r.prompt_path.read_text(encoding="utf-8")
        assert "abc1234" in content

    def test_empty_files_list(self, tmp_path: Path):
        r = RollbackContextRestorer(project_root=tmp_path)
        ctx = RestoreContext(
            rollback_reason="test",
            reverted_commit="abc1234",
            files_affected=[],
            session_id="session-001",
            action_plan="Re-run",
        )
        result = r.generate_restore_prompt(ctx)
        assert isinstance(result, str)
        assert "abc1234" in result

    def test_empty_strings(self, tmp_path: Path):
        r = RollbackContextRestorer(project_root=tmp_path)
        ctx = RestoreContext(
            rollback_reason="",
            reverted_commit="",
            files_affected=[],
            session_id="",
            action_plan="",
        )
        result = r.generate_restore_prompt(ctx)
        assert isinstance(result, str)


class TestInjectForSession:
    def test_returns_dict_with_required_keys(self, tmp_path: Path):
        r = RollbackContextRestorer(project_root=tmp_path)
        ctx = RestoreContext(
            rollback_reason="test",
            reverted_commit="abc1234",
            files_affected=["a.py"],
            session_id="session-001",
            action_plan="Re-run",
        )
        result = r.inject_for_session(ctx)
        assert "session_id" in result
        assert "restore_prompt" in result
        assert "prompt_file" in result
        assert "generated_at" in result

    def test_session_id_matches(self, tmp_path: Path):
        r = RollbackContextRestorer(project_root=tmp_path)
        ctx = RestoreContext(
            rollback_reason="test",
            reverted_commit="abc1234",
            files_affected=["a.py"],
            session_id="session-001",
            action_plan="Re-run",
        )
        result = r.inject_for_session(ctx)
        assert result["session_id"] == "session-001"

    def test_prompt_file_is_str(self, tmp_path: Path):
        r = RollbackContextRestorer(project_root=tmp_path)
        ctx = RestoreContext(
            rollback_reason="test",
            reverted_commit="abc1234",
            files_affected=["a.py"],
            session_id="session-001",
            action_plan="Re-run",
        )
        result = r.inject_for_session(ctx)
        assert isinstance(result["prompt_file"], str)

    def test_generated_at_is_iso_format(self, tmp_path: Path):
        r = RollbackContextRestorer(project_root=tmp_path)
        ctx = RestoreContext(
            rollback_reason="test",
            reverted_commit="abc1234",
            files_affected=["a.py"],
            session_id="session-001",
            action_plan="Re-run",
        )
        result = r.inject_for_session(ctx)
        assert "T" in result["generated_at"]

    def test_restore_prompt_contains_commit(self, tmp_path: Path):
        r = RollbackContextRestorer(project_root=tmp_path)
        ctx = RestoreContext(
            rollback_reason="test",
            reverted_commit="deadbeef",
            files_affected=["a.py"],
            session_id="session-001",
            action_plan="Re-run",
        )
        result = r.inject_for_session(ctx)
        assert "deadbeef" in result["restore_prompt"]
