# [A_test] module_id: SRC-TST-1521 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-426 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_saga_compensator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/test_saga_compensator.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.shared.compensation.saga_compensator import (
    SagaCompensator,
    SagaContext,
    SagaStatus,
    SagaStep,
)


class TestSagaStatus:
    def test_enum_values(self):
        assert SagaStatus.PENDING == "pending"
        assert SagaStatus.RUNNING == "running"
        assert SagaStatus.COMPLETED == "completed"
        assert SagaStatus.COMPENSATING == "compensating"
        assert SagaStatus.FAILED == "failed"

    def test_is_str_enum(self):
        assert isinstance(SagaStatus.PENDING, str)


class TestSagaStep:
    def test_creation(self):
        step = SagaStep(step_id="s1", action=lambda: None, compensation=lambda: None)
        assert step.step_id == "s1"
        assert step.executed is False
        assert step.compensated is False
        assert step.error == ""

    def test_action_execution(self):
        result = []
        step = SagaStep(step_id="s1", action=lambda: result.append("acted"), compensation=lambda: None)
        step.action()
        assert result == ["acted"]
        step.executed = True
        assert step.executed is True


class TestSagaContext:
    def test_creation(self):
        ctx = SagaContext(saga_id="saga-1", steps=[])
        assert ctx.saga_id == "saga-1"
        assert ctx.steps == []
        assert ctx.status == SagaStatus.PENDING
        assert ctx.current_step == 0
        assert ctx.errors == []

    def test_with_steps(self):
        steps = [SagaStep(step_id="s1", action=lambda: None, compensation=lambda: None)]
        ctx = SagaContext(saga_id="saga-2", steps=steps)
        assert len(ctx.steps) == 1
        assert ctx.timestamp_utc != ""


class TestSagaCompensator:
    def test_instantiation(self):
        comp = SagaCompensator()
        assert comp._sagas == {}

    def test_create_saga(self):
        comp = SagaCompensator()
        steps = [SagaStep(step_id="s1", action=lambda: None, compensation=lambda: None)]
        ctx = comp.create_saga("saga-1", steps)
        assert ctx.saga_id == "saga-1"
        assert ctx.status == SagaStatus.PENDING
        assert len(ctx.steps) == 1

    def test_execute_success(self):
        comp = SagaCompensator()
        action_log = []
        steps = [
            SagaStep(
                step_id="s1", action=lambda: action_log.append("s1"), compensation=lambda: action_log.append("c1")
            ),
            SagaStep(
                step_id="s2", action=lambda: action_log.append("s2"), compensation=lambda: action_log.append("c2")
            ),
        ]
        comp.create_saga("saga-1", steps)
        success, ctx = comp.execute("saga-1")
        assert success is True
        assert ctx.status == SagaStatus.COMPLETED
        assert action_log == ["s1", "s2"]
        assert all(s.executed for s in ctx.steps)

    def test_execute_failure_triggers_compensation(self):
        comp = SagaCompensator()
        action_log = []

        def failing_action():
            raise RuntimeError("boom")

        steps = [
            SagaStep(
                step_id="s1", action=lambda: action_log.append("s1"), compensation=lambda: action_log.append("c1")
            ),
            SagaStep(step_id="s2", action=failing_action, compensation=lambda: action_log.append("c2")),
        ]
        comp.create_saga("saga-1", steps)
        success, ctx = comp.execute("saga-1")
        assert success is False
        assert ctx.status == SagaStatus.FAILED
        assert "s1" in action_log
        assert "c1" in action_log
        assert ctx.steps[0].compensated is True

    def test_execute_nonexistent_saga(self):
        comp = SagaCompensator()
        success, ctx = comp.execute("nonexistent")
        assert success is False
        assert ctx.saga_id == "NOT_FOUND"

    def test_compensate_all(self):
        comp = SagaCompensator()
        action_log = []
        steps = [
            SagaStep(
                step_id="s1", action=lambda: action_log.append("s1"), compensation=lambda: action_log.append("c1")
            ),
            SagaStep(
                step_id="s2", action=lambda: action_log.append("s2"), compensation=lambda: action_log.append("c2")
            ),
        ]
        comp.create_saga("saga-1", steps)
        comp.execute("saga-1")
        success, ctx = comp.compensate_all("saga-1")
        assert success is True
        assert ctx.steps[0].compensated is True
        assert ctx.steps[1].compensated is True
        assert "c1" in action_log
        assert "c2" in action_log

    def test_compensate_all_nonexistent(self):
        comp = SagaCompensator()
        success, ctx = comp.compensate_all("nonexistent")
        assert success is False
        assert ctx.saga_id == "NOT_FOUND"

    def test_compensate_all_with_failing_compensation(self):
        comp = SagaCompensator()
        action_log = []

        def failing_comp():
            raise RuntimeError("comp failed")

        steps = [
            SagaStep(step_id="s1", action=lambda: action_log.append("s1"), compensation=failing_comp),
        ]
        comp.create_saga("saga-1", steps)
        comp.execute("saga-1")
        success, ctx = comp.compensate_all("saga-1")
        assert success is False
        assert ctx.status == SagaStatus.FAILED
        assert len(ctx.errors) > 0

    def test_get_status(self):
        comp = SagaCompensator()
        steps = [SagaStep(step_id="s1", action=lambda: None, compensation=lambda: None)]
        comp.create_saga("saga-1", steps)
        ctx = comp.get_status("saga-1")
        assert ctx is not None
        assert ctx.saga_id == "saga-1"

    def test_get_status_nonexistent(self):
        comp = SagaCompensator()
        result = comp.get_status("nonexistent")
        assert result is None

    def test_execute_with_empty_steps(self):
        comp = SagaCompensator()
        comp.create_saga("saga-empty", [])
        success, ctx = comp.execute("saga-empty")
        assert success is True
        assert ctx.status == SagaStatus.COMPLETED
