# [A_test] module_id: MOD-GOV_context_playground | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_context_playground
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_context_playground.py -q
# [TTL] task_bound
from __future__ import annotations

from zephyr.autonomy_core.context.context_playground import (
    ContextPlayground,
    DryRunResult,
    playground_cli,
)


class TestDryRunResult:
    def test_default_values(self):
        result = DryRunResult(
            task_summary="test task",
            ke_ids_selected=["KE-001"],
            total_tokens=100,
            decision_trace=["step1"],
        )
        assert result.task_summary == "test task"
        assert result.ke_ids_selected == ["KE-001"]
        assert result.total_tokens == 100
        assert result.decision_trace == ["step1"]

    def test_empty_collections(self):
        result = DryRunResult(
            task_summary="",
            ke_ids_selected=[],
            total_tokens=0,
            decision_trace=[],
        )
        assert result.ke_ids_selected == []
        assert result.decision_trace == []


class TestContextPlaygroundInit:
    def test_instantiation(self):
        pg = ContextPlayground()
        assert hasattr(pg, "dry_run")


class TestContextPlaygroundDryRun:
    def test_dry_run_returns_result(self):
        pg = ContextPlayground()
        result = pg.dry_run("analyze logs")
        assert isinstance(result, DryRunResult)

    def test_dry_run_task_summary(self):
        pg = ContextPlayground()
        result = pg.dry_run("analyze logs")
        assert result.task_summary == "analyze logs"

    def test_dry_run_default_ke_ids(self):
        pg = ContextPlayground()
        result = pg.dry_run("any task")
        assert result.ke_ids_selected == []

    def test_dry_run_default_tokens(self):
        pg = ContextPlayground()
        result = pg.dry_run("any task")
        assert result.total_tokens == 0

    def test_dry_run_default_trace(self):
        pg = ContextPlayground()
        result = pg.dry_run("any task")
        assert result.decision_trace == []

    def test_dry_run_empty_string(self):
        pg = ContextPlayground()
        result = pg.dry_run("")
        assert result.task_summary == ""

    def test_dry_run_unicode_task(self):
        pg = ContextPlayground()
        result = pg.dry_run("分析日志")
        assert result.task_summary == "分析日志"

    def test_dry_run_long_task_description(self):
        pg = ContextPlayground()
        long_task = "x" * 10000
        result = pg.dry_run(long_task)
        assert result.task_summary == long_task


class TestPlaygroundCli:
    def test_cli_returns_dry_run_result(self):
        result = playground_cli("test task")
        assert isinstance(result, DryRunResult)

    def test_cli_delegates_to_playground(self):
        result = playground_cli("delegate test")
        assert result.task_summary == "delegate test"
        assert result.total_tokens == 0
