# [A_test] module_id: MOD-GOV_ce_playground_v2 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_ce_playground_v2
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_ce_playground_v2.py
# [TTL] task_bound

import pytest

from zephyr.autonomy_core.context.ce_playground_v2 import (
    PlaygroundV2,
    PlaygroundV2Result,
)


class TestPlaygroundV2Result:
    def test_instantiation_defaults(self):
        result = PlaygroundV2Result(task="test", selected_ke_ids=["KE-001"])
        assert result.task == "test"
        assert result.selected_ke_ids == ["KE-001"]
        assert result.decision_trace == []
        assert result.excluded_ke_ids == []

    def test_instantiation_custom(self):
        result = PlaygroundV2Result(
            task="task2",
            selected_ke_ids=["KE-010"],
            decision_trace=["step1", "step2"],
            excluded_ke_ids=["KE-001"],
        )
        assert result.decision_trace == ["step1", "step2"]
        assert result.excluded_ke_ids == ["KE-001"]

    def test_missing_required_field_raises(self):
        with pytest.raises(TypeError):
            PlaygroundV2Result()


class TestPlaygroundV2:
    def test_instantiation(self):
        pg = PlaygroundV2()
        assert pg is not None

    def test_dry_run(self):
        pg = PlaygroundV2()
        result = pg.dry_run("my task")
        assert isinstance(result, PlaygroundV2Result)
        assert result.task == "my task"
        assert len(result.selected_ke_ids) > 0

    def test_dry_run_returns_result_with_task(self):
        pg = PlaygroundV2()
        result = pg.dry_run("another task")
        assert result.task == "another task"

    def test_dry_run_excluding(self):
        pg = PlaygroundV2()
        result = pg.dry_run_excluding("task", exclude_ids=["KE-001", "KE-002"])
        assert isinstance(result, PlaygroundV2Result)
        assert result.excluded_ke_ids == ["KE-001", "KE-002"]

    def test_dry_run_excluding_empty_list(self):
        pg = PlaygroundV2()
        result = pg.dry_run_excluding("task", exclude_ids=[])
        assert result.excluded_ke_ids == []

    def test_dry_run_excluding_returns_different_selection(self):
        pg = PlaygroundV2()
        normal = pg.dry_run("task")
        excluded = pg.dry_run_excluding("task", exclude_ids=normal.selected_ke_ids)
        assert excluded.selected_ke_ids != normal.selected_ke_ids
