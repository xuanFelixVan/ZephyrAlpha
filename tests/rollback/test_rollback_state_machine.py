# [A_test] module_id: MOD-GOV_rollback_state_machine | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §7
# [MODULE] tests.test_rollback_state_machine
# [INVARIANTS] RollbackStateMachine.STEPS order must not change; StepStatus/StepType enums must remain stable
# [MODIFY-GUARD] Do not change test data without updating source module
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError on invalid StepStatus in from_in_flight_data
# [TESTS] pytest tests/test_rollback_state_machine.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.rollback.rollback_state_machine import (
    RollbackStateMachine,
    RollbackStep,
    StepStatus,
    StepType,
)


class TestStepStatusEnum:
    def test_values(self):
        assert StepStatus.PENDING.value == "PENDING"
        assert StepStatus.SUCCESS.value == "SUCCESS"
        assert StepStatus.FAILED.value == "FAILED"
        assert StepStatus.RETRYING.value == "RETRYING"

    def test_from_value(self):
        assert StepStatus("PENDING") is StepStatus.PENDING
        assert StepStatus("SUCCESS") is StepStatus.SUCCESS


class TestStepTypeEnum:
    def test_values(self):
        assert StepType.REVERSIBLE.value == "reversible"
        assert StepType.IRREVERSIBLE.value == "irreversible"


class TestRollbackStep:
    def test_defaults(self):
        step = RollbackStep(name="test", step_type=StepType.REVERSIBLE)
        assert step.status == StepStatus.PENDING
        assert step.retry_count == 0
        assert step.max_retries == 3
        assert step.started_at == ""
        assert step.completed_at == ""
        assert step.error == ""

    def test_custom_values(self):
        step = RollbackStep(
            name="git_revert",
            step_type=StepType.IRREVERSIBLE,
            max_retries=1,
            error="boom",
        )
        assert step.step_type == StepType.IRREVERSIBLE
        assert step.max_retries == 1
        assert step.error == "boom"


class TestRollbackStateMachineInstantiation:
    def test_default_execution_id(self):
        sm = RollbackStateMachine()
        assert sm.execution_id == ""

    def test_custom_execution_id(self):
        sm = RollbackStateMachine(execution_id="exec-001")
        assert sm.execution_id == "exec-001"

    def test_steps_initialized(self):
        sm = RollbackStateMachine()
        assert len(sm.steps) == 6
        assert sm.steps[0].name == "preflight"
        assert sm.steps[2].name == "git_revert"
        assert sm.steps[2].step_type == StepType.IRREVERSIBLE

    def test_current_step_is_first(self):
        sm = RollbackStateMachine()
        assert sm.current_step is not None
        assert sm.current_step.name == "preflight"

    def test_not_complete_on_init(self):
        sm = RollbackStateMachine()
        assert sm.is_complete() is False


class TestMarkCurrent:
    def test_mark_success_advances(self):
        sm = RollbackStateMachine()
        sm.mark_current(StepStatus.SUCCESS)
        assert sm.current_step_idx == 1
        assert sm.current_step.name == "acquire_lock"

    def test_mark_failed_no_advance(self):
        sm = RollbackStateMachine()
        sm.mark_current(StepStatus.FAILED, error="timeout")
        assert sm.current_step_idx == 0
        assert sm.steps[0].status == StepStatus.FAILED
        assert sm.steps[0].error == "timeout"
        assert sm.steps[0].completed_at != ""

    def test_mark_success_sets_completed_at(self):
        sm = RollbackStateMachine()
        sm.mark_current(StepStatus.SUCCESS)
        assert sm.steps[0].completed_at != ""

    def test_mark_on_completed_machine(self):
        sm = RollbackStateMachine()
        for _ in range(6):
            sm.mark_current(StepStatus.SUCCESS)
        assert sm.is_complete()
        assert sm.current_step is None
        sm.mark_current(StepStatus.SUCCESS)

    def test_mark_pending_no_advance(self):
        sm = RollbackStateMachine()
        sm.mark_current(StepStatus.PENDING)
        assert sm.current_step_idx == 0


class TestRetryCurrent:
    def test_retry_increments_count(self):
        sm = RollbackStateMachine()
        sm.mark_current(StepStatus.FAILED)
        result = sm.retry_current()
        assert result is True
        assert sm.steps[0].retry_count == 1
        assert sm.steps[0].status == StepStatus.RETRYING

    def test_retry_up_to_max(self):
        sm = RollbackStateMachine()
        sm.mark_current(StepStatus.FAILED)
        for _ in range(3):
            sm.retry_current()
        result = sm.retry_current()
        assert result is False
        assert sm.steps[0].retry_count == 3

    def test_retry_on_completed_machine(self):
        sm = RollbackStateMachine()
        for _ in range(6):
            sm.mark_current(StepStatus.SUCCESS)
        assert sm.retry_current() is False


class TestIsCurrentReversible:
    def test_preflight_is_reversible(self):
        sm = RollbackStateMachine()
        assert sm.is_current_reversible() is True

    def test_git_revert_is_irreversible(self):
        sm = RollbackStateMachine()
        sm.mark_current(StepStatus.SUCCESS)
        sm.mark_current(StepStatus.SUCCESS)
        assert sm.current_step.name == "git_revert"
        assert sm.is_current_reversible() is False

    def test_completed_machine_returns_true(self):
        sm = RollbackStateMachine()
        for _ in range(6):
            sm.mark_current(StepStatus.SUCCESS)
        assert sm.is_current_reversible() is True


class TestGetResult:
    def test_all_pending(self):
        sm = RollbackStateMachine()
        result = sm.get_result()
        assert result.success is False
        assert result.overall_status == StepStatus.PENDING
        assert result.failed_step == ""

    def test_all_success(self):
        sm = RollbackStateMachine()
        for _ in range(6):
            sm.mark_current(StepStatus.SUCCESS)
        result = sm.get_result()
        assert result.success is True
        assert result.overall_status == StepStatus.SUCCESS
        assert result.failed_step == ""

    def test_first_failed(self):
        sm = RollbackStateMachine()
        sm.mark_current(StepStatus.FAILED, error="err")
        result = sm.get_result()
        assert result.success is False
        assert result.overall_status == StepStatus.FAILED
        assert result.failed_step == "preflight"


class TestSerialization:
    def test_to_in_flight_data(self):
        sm = RollbackStateMachine(execution_id="exec-42")
        data = sm.to_in_flight_data()
        assert data["execution_id"] == "exec-42"
        assert data["current_step_idx"] == 0
        assert len(data["steps"]) == 6
        assert data["steps"][0]["name"] == "preflight"

    def test_from_in_flight_data_roundtrip(self):
        sm = RollbackStateMachine(execution_id="exec-99")
        sm.mark_current(StepStatus.SUCCESS)
        sm.mark_current(StepStatus.FAILED, error="lock busy")
        sm.retry_current()
        data = sm.to_in_flight_data()
        restored = RollbackStateMachine.from_in_flight_data(data)
        assert restored.execution_id == "exec-99"
        assert restored.current_step_idx == 1
        assert restored.steps[0].status == StepStatus.SUCCESS
        assert restored.steps[1].status == StepStatus.RETRYING
        assert restored.steps[1].retry_count == 1

    def test_from_in_flight_data_empty(self):
        restored = RollbackStateMachine.from_in_flight_data({})
        assert restored.execution_id == ""
        assert restored.current_step_idx == 0

    def test_from_in_flight_data_partial_steps(self):
        data = {
            "execution_id": "e1",
            "current_step_idx": 2,
            "steps": [
                {"status": "SUCCESS", "retry_count": 0},
                {"status": "SUCCESS", "retry_count": 0},
            ],
        }
        restored = RollbackStateMachine.from_in_flight_data(data)
        assert restored.current_step_idx == 2
        assert len(restored.steps) == 6
        assert restored.steps[0].status == StepStatus.SUCCESS
