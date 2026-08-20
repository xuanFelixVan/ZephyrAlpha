# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [A_test] module_id: MOD-GOV_grayscale_rollout | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.factor.test_grayscale_rollout
# [DOMAIN] D_FACTOR
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/factor/test_grayscale_rollout.py
# [TTL] task_bound
"""D-FACTOR-GOV-03 灰度发布测试——纯逻辑模块（无 IO 依赖）。

覆盖：
- init_factor: 初始比例 0.1 / 状态字段
- get_status: 未初始化返回 None / 已初始化返回 GrayscaleStatus
- advance: 门禁通过推进 / 门禁未过保持当前 / 推进到 100% / 100%后无法推进
  / 未初始化自动初始化
- check_promotion: 通过 / 失败
- stages 属性: 默认阶梯 / 返回副本
"""

from __future__ import annotations

import pytest

from zephyr.factor.core.evaluation.backtest import EvaluationResult
from zephyr.factor.governance.grayscale_rollout import (
    GrayscaleRollout,
    GrayscaleStatus,
)


def _passing_result(factor_id: str = "f1") -> EvaluationResult:
    """构造通过 ABS001 门禁的评估结果。"""
    return EvaluationResult(factor_id, 0.05, 0.1, 0.6, 0.55, False, 50)


def _failing_result(factor_id: str = "f1") -> EvaluationResult:
    """构造不通过 ABS001 门禁的评估结果（多项不达标）。"""
    return EvaluationResult(factor_id, 0.01, 0.1, 0.3, 0.4, True, 50)


class TestInitFactor:
    def test_initial_ratio(self):
        rollout = GrayscaleRollout()
        ratio = rollout.init_factor("f1")
        assert ratio == pytest.approx(0.1)

    def test_status_after_init(self):
        rollout = GrayscaleRollout()
        rollout.init_factor("f1")
        status = rollout.get_status("f1")
        assert status is not None
        assert status.factor_id == "f1"
        assert status.current_ratio == pytest.approx(0.1)
        assert status.stage_index == 0
        assert status.can_advance is True


class TestGetStatus:
    def test_uninitialized_returns_none(self):
        rollout = GrayscaleRollout()
        assert rollout.get_status("unknown") is None

    def test_returns_grayscale_status_instance(self):
        rollout = GrayscaleRollout()
        rollout.init_factor("f1")
        status = rollout.get_status("f1")
        assert isinstance(status, GrayscaleStatus)

    def test_can_advance_false_at_last_stage(self):
        rollout = GrayscaleRollout()
        rollout.init_factor("f1")
        rollout.advance("f1", _passing_result())  # 0.1 → 0.3
        rollout.advance("f1", _passing_result())  # 0.3 → 1.0
        status = rollout.get_status("f1")
        assert status is not None
        assert status.can_advance is False
        assert status.stage_index == 2


class TestAdvance:
    def test_advance_with_passing_gate(self):
        rollout = GrayscaleRollout()
        rollout.init_factor("f1")
        new_ratio, msg = rollout.advance("f1", _passing_result())
        assert new_ratio == pytest.approx(0.3)
        assert "推进" in msg

    def test_advance_with_failing_gate_keeps_current(self):
        rollout = GrayscaleRollout()
        rollout.init_factor("f1")
        new_ratio, msg = rollout.advance("f1", _failing_result())
        assert new_ratio == pytest.approx(0.1)
        assert "门禁未通过" in msg

    def test_advance_to_full(self):
        rollout = GrayscaleRollout()
        rollout.init_factor("f1")
        rollout.advance("f1", _passing_result())  # 0.1 → 0.3
        new_ratio, msg = rollout.advance("f1", _passing_result())  # 0.3 → 1.0
        assert new_ratio == pytest.approx(1.0)

    def test_advance_at_full_cannot_advance(self):
        rollout = GrayscaleRollout()
        rollout.init_factor("f1")
        rollout.advance("f1", _passing_result())  # 0.1 → 0.3
        rollout.advance("f1", _passing_result())  # 0.3 → 1.0
        new_ratio, msg = rollout.advance("f1", _passing_result())
        assert new_ratio == pytest.approx(1.0)
        assert "无法" in msg

    def test_advance_uninitialized_auto_inits(self):
        rollout = GrayscaleRollout()
        new_ratio, msg = rollout.advance("f1", _passing_result())
        assert new_ratio == pytest.approx(0.1)
        assert "初始化" in msg

    def test_full_lifecycle_progression(self):
        rollout = GrayscaleRollout()
        rollout.init_factor("f1")
        assert rollout.get_status("f1").current_ratio == pytest.approx(0.1)
        r1, _ = rollout.advance("f1", _passing_result())
        assert r1 == pytest.approx(0.3)
        r2, _ = rollout.advance("f1", _passing_result())
        assert r2 == pytest.approx(1.0)


class TestCheckPromotion:
    def test_passing(self):
        rollout = GrayscaleRollout()
        passed, detail = rollout.check_promotion(_passing_result())
        assert passed is True
        assert detail == ""

    def test_failing(self):
        rollout = GrayscaleRollout()
        passed, detail = rollout.check_promotion(_failing_result())
        assert passed is False
        assert detail != ""


class TestStagesProperty:
    def test_default_stages(self):
        rollout = GrayscaleRollout()
        stages = rollout.stages
        assert stages == [0.1, 0.3, 1.0]

    def test_stages_returns_copy(self):
        rollout = GrayscaleRollout()
        stages = rollout.stages
        stages.append(2.0)
        # 修改返回值不影响内部状态
        assert rollout.stages == [0.1, 0.3, 1.0]
