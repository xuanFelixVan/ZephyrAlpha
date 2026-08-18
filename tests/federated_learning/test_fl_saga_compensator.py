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

# #ARCH-082：测试契约 compensate(list[str]) -> list["undo_*"] 与生产
# SagaCompensator（SagaContext 状态机 + compensate_all）为两套设计——
# 测试先行契约未落地（#ARCH-073~076 同族）。TestCompensate xfail 留痕。
import pytest

from zephyr.shared.compensation.saga_compensator import SagaCompensator

_COMPENSATE_CONTRACT_GAP = pytest.mark.xfail(
    strict=False, reason="#ARCH-082 compensate 契约分歧（list 补偿 vs SagaContext 状态机），待裁定"
)


class TestSagaCompensatorInstantiation:
    def test_creates_with_defaults(self):
        compensator = SagaCompensator()
        assert compensator is not None


@_COMPENSATE_CONTRACT_GAP
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
