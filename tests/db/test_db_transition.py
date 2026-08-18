# [A_test] module_id: MOD-GOV_db_transition | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-DATABASE | docs/03_modules/_cross_layer/database/blueprint.md
# [MODULE] tests.test_db_transition
# [INVARIANTS] 状态转换必须遵循有限状态机
# [MODIFY-GUARD] task_repo.py 组合入口; gates/task_types.py TaskStatus
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_db_transition.py
# [TTL] task_bound

import pytest

from zephyr.gov_enforcement.rule_enforcement.task_types import TaskStatus
from zephyr.governance.lifecycle_governance.transition import TransitionMixin
from zephyr.governance.persistence.task_repo import TaskNotFoundError


class TestTransitionMixinImport:
    def test_import(self):
        assert TransitionMixin is not None

    def test_has_transition_method(self):
        assert hasattr(TransitionMixin, "transition")

    def test_has_recalculate_dependent_status(self):
        assert hasattr(TransitionMixin, "_recalculate_dependent_status")


class TestTaskStatusEnum:
    def test_all_status_values(self):
        expected = {
            "PENDING",
            "CREATED",
            "LOCKED",
            "ASSIGNED",
            "IN_PROGRESS",
            "READY",
            "REVIEWING",
            "COMPLETED",
            "VERIFIED",
            "FAILED",
            "BLOCKED",
            "WAITING",
            "RETRY",
            "CANCELLED",
        }
        actual = {s.value for s in TaskStatus}
        assert actual == expected

    def test_member_count(self):
        assert len(TaskStatus) == 14

    def test_is_str_enum(self):
        assert isinstance(TaskStatus.PENDING, str)
        assert TaskStatus.PENDING == "PENDING"

    def test_from_string(self):
        assert TaskStatus("PENDING") == TaskStatus.PENDING
        assert TaskStatus("COMPLETED") == TaskStatus.COMPLETED

    def test_invalid_string_raises(self):
        with pytest.raises(ValueError):
            TaskStatus("INVALID")


class TestTransitionMixinViaTaskRepo:
    def test_transition_nonexistent_raises(self):
        from zephyr.governance.persistence.task_repo import TaskRepository

        repo = TaskRepository(enable_gate=False)
        with pytest.raises(TaskNotFoundError):
            repo.transition("NONEXISTENT-99999", TaskStatus.IN_PROGRESS)

    def test_transition_invalid_status_raises(self):
        from zephyr.governance.persistence.task_repo import TaskRepository

        repo = TaskRepository(enable_gate=False)
        with pytest.raises((ValueError, TaskNotFoundError)):
            repo.transition("NONEXISTENT-99999", "INVALID_STATUS")
