# [A_test] module_id: MOD-GOV_fl_saga_compensator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_saga_compensator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.infrastructure.shared_services.compensation.saga_compensator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_saga_compensator.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.shared.compensation.saga_compensator import SagaCompensator


class TestSagaCompensatorInstantiation:
    def test_creates_with_defaults(self):
        compensator = SagaCompensator()
        assert compensator is not None


class TestCompensate:
    def test_compensate_reverses_steps(self):
        compensator = SagaCompensator()
        result = compensator.compensate(["step1", "step2", "step3"])
        assert result == ["undo_step3", "undo_step2", "undo_step1"]

    def test_compensate_single_step(self):
        compensator = SagaCompensator()
        result = compensator.compensate(["step1"])
        assert result == ["undo_step1"]

    def test_boundary_empty_steps(self):
        compensator = SagaCompensator()
        result = compensator.compensate([])
        assert result == []

    def test_compensate_preserves_order(self):
        compensator = SagaCompensator()
        result = compensator.compensate(["a", "b"])
        assert result[0] == "undo_b"
        assert result[1] == "undo_a"
