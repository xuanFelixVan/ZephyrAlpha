# [A_test] module_id: SRC-TST-1364 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md | §test
# [MODULE] tests.test_per_task_token_budget
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_per_task_token_budget.py

import pytest

mod = pytest.importorskip("zephyr.ops.capacity_assurance.per_task_token_budget", reason="per_task_token_budget not available")
PerTaskTokenBudget = mod.PerTaskTokenBudget
TaskBudget = mod.TaskBudget


class TestTaskBudget:
    def test_instantiation(self):
        tb = TaskBudget(task_id="t1")
        assert tb.input_limit == 8192
        assert tb.output_limit == 4096
        assert tb.input_used == 0
        assert tb.output_used == 0

    def test_custom_limits(self):
        tb = TaskBudget(task_id="t1", input_limit=4096, output_limit=2048)
        assert tb.input_limit == 4096


class TestPerTaskTokenBudget:
    def test_instantiation(self):
        ptb = PerTaskTokenBudget()
        assert len(ptb._budgets) == 0

    def test_create_budget(self):
        ptb = PerTaskTokenBudget()
        budget = ptb.create_budget("task_1")
        assert isinstance(budget, TaskBudget)
        assert budget.task_id == "task_1"

    def test_create_budget_custom_limits(self):
        ptb = PerTaskTokenBudget()
        budget = ptb.create_budget("task_1", input_limit=1000, output_limit=500)
        assert budget.input_limit == 1000

    def test_can_consume_within_limit(self):
        ptb = PerTaskTokenBudget()
        ptb.create_budget("task_1", input_limit=1000)
        assert ptb.can_consume("task_1", 500, is_input=True) is True

    def test_can_consume_exceeds_limit(self):
        ptb = PerTaskTokenBudget()
        ptb.create_budget("task_1", input_limit=1000)
        assert ptb.can_consume("task_1", 1500, is_input=True) is False

    def test_can_consume_output(self):
        ptb = PerTaskTokenBudget()
        ptb.create_budget("task_1", output_limit=500)
        assert ptb.can_consume("task_1", 600, is_input=False) is False

    def test_can_consume_unknown_task(self):
        ptb = PerTaskTokenBudget()
        assert ptb.can_consume("unknown", 100) is True

    def test_consume_and_get_remaining(self):
        ptb = PerTaskTokenBudget()
        ptb.create_budget("task_1", input_limit=1000, output_limit=500)
        ptb.consume("task_1", 300, is_input=True)
        remaining = ptb.get_remaining("task_1")
        assert remaining["input_remaining"] == 700
        assert remaining["output_remaining"] == 500

    def test_get_remaining_unknown_task(self):
        ptb = PerTaskTokenBudget()
        remaining = ptb.get_remaining("unknown")
        assert remaining["input_remaining"] == -1
        assert remaining["output_remaining"] == -1
