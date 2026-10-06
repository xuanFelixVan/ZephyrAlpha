# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [A_test] module_id: MOD-GOV_governance_engine | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.factor.test_governance_engine
# [DOMAIN] D_FACTOR
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/factor/test_governance_engine.py
# [TTL] task_bound
"""D-FACTOR-GOV-05 因子治理引擎测试——纯逻辑模块（无 IO 依赖）。

覆盖：
- submit_factor: 提交后返回 research / 重复提交
- evaluate: 返回 FactorStatus / 未提交因子状态为空
- promote: 推进到 development / 到 grayscale 自动初始化灰度
  / 未提交 promote 报错 / grayscale 中推进阶梯 / 门禁未过保持
  / 完整流程走通到 production
"""

from __future__ import annotations

import pytest

from zephyr.factor.core.evaluation.backtest import EvaluationResult
from zephyr.factor.governance.engine import (
    FactorGovernanceEngine,
    FactorStatus,
)


def _passing_result(factor_id: str = "f1") -> EvaluationResult:
    """构造通过 ABS001 门禁的评估结果。"""
    return EvaluationResult(factor_id, 0.05, 0.1, 0.6, 0.55, False, 50)


def _failing_result(factor_id: str = "f1") -> EvaluationResult:
    """构造不通过 ABS001 门禁的评估结果。"""
    return EvaluationResult(factor_id, 0.01, 0.1, 0.3, 0.4, True, 50)


class TestSubmitFactor:
    def test_submit_returns_research(self):
        engine = FactorGovernanceEngine()
        state = engine.submit_factor("f1")
        assert state == "research"

    def test_submit_twice_keeps_research(self):
        engine = FactorGovernanceEngine()
        engine.submit_factor("f1")
        state = engine.submit_factor("f1")
        assert state == "research"


class TestEvaluate:
    def test_returns_factor_status(self):
        engine = FactorGovernanceEngine()
        engine.submit_factor("f1")
        status = engine.evaluate("f1")
        assert isinstance(status, FactorStatus)
        assert status.factor_id == "f1"
        assert status.flow_status is not None
        assert status.flow_status.current_step == "research"
        assert status.grayscale_status is None

    def test_evaluate_unsubmitted(self):
        engine = FactorGovernanceEngine()
        status = engine.evaluate("unknown")
        assert isinstance(status, FactorStatus)
        assert status.flow_status is None
        assert status.grayscale_status is None


class TestPromote:
    def test_promote_to_development(self):
        engine = FactorGovernanceEngine()
        engine.submit_factor("f1")
        new_step, msg = engine.promote("f1", _passing_result())
        assert new_step == "development"
        assert "推进" in msg

    def test_promote_unsubmitted_returns_error(self):
        engine = FactorGovernanceEngine()
        new_step, msg = engine.promote("unknown", _passing_result())
        assert new_step == ""
        assert "未提交" in msg

    def test_promote_to_grayscale_inits_rollout(self):
        engine = FactorGovernanceEngine()
        engine.submit_factor("f1")
        engine.promote("f1", _passing_result())  # → development
        engine.promote("f1", _passing_result())  # → backtest
        engine.promote("f1", _passing_result())  # → paper
        new_step, msg = engine.promote("f1", _passing_result())  # → grayscale
        assert new_step == "grayscale"
        assert "初始化" in msg
        status = engine.evaluate("f1")
        assert status.grayscale_status is not None
        assert status.grayscale_status.current_ratio == pytest.approx(0.1)
        assert status.grayscale_status.stage_index == 0

    def test_promote_in_grayscale_advances_ratio(self):
        engine = FactorGovernanceEngine()
        engine.submit_factor("f1")
        engine.promote("f1", _passing_result())  # → development
        engine.promote("f1", _passing_result())  # → backtest
        engine.promote("f1", _passing_result())  # → paper
        engine.promote("f1", _passing_result())  # → grayscale (init 0.1)
        new_step, msg = engine.promote("f1", _passing_result())  # 0.1 → 0.3
        assert new_step == "grayscale"
        status = engine.evaluate("f1")
        assert status.grayscale_status.current_ratio == pytest.approx(0.3)

    def test_promote_in_grayscale_gate_fails_keeps_ratio(self):
        engine = FactorGovernanceEngine()
        engine.submit_factor("f1")
        engine.promote("f1", _passing_result())  # → development
        engine.promote("f1", _passing_result())  # → backtest
        engine.promote("f1", _passing_result())  # → paper
        engine.promote("f1", _passing_result())  # → grayscale (init 0.1)
        new_step, msg = engine.promote("f1", _failing_result())  # 门禁未过
        assert new_step == "grayscale"
        assert "门禁未通过" in msg
        status = engine.evaluate("f1")
        assert status.grayscale_status.current_ratio == pytest.approx(0.1)


class TestFullFlow:
    def test_complete_flow_to_production(self):
        """完整治理流程：research → ... → grayscale(0.1→0.3→1.0) → production。"""
        engine = FactorGovernanceEngine()
        engine.submit_factor("f1")
        engine.promote("f1", _passing_result())  # → development
        engine.promote("f1", _passing_result())  # → backtest
        engine.promote("f1", _passing_result())  # → paper
        engine.promote("f1", _passing_result())  # → grayscale (init 0.1)
        assert engine.evaluate("f1").grayscale_status.current_ratio == pytest.approx(0.1)

        engine.promote("f1", _passing_result())  # grayscale 0.1 → 0.3
        assert engine.evaluate("f1").grayscale_status.current_ratio == pytest.approx(0.3)

        new_step, msg = engine.promote("f1", _passing_result())  # 0.3 → 1.0 → production
        assert new_step == "production"

        status = engine.evaluate("f1")
        assert status.flow_status.current_step == "production"
        assert status.flow_status.can_advance is False

    def test_grayscale_rollback_path(self):
        """grayscale 中门禁未过时保持当前比例，可重试。"""
        engine = FactorGovernanceEngine()
        engine.submit_factor("f1")
        for _ in range(4):
            engine.promote("f1", _passing_result())  # → grayscale (0.1)
        # 门禁未过 → 保持 0.1
        engine.promote("f1", _failing_result())
        assert engine.evaluate("f1").grayscale_status.current_ratio == pytest.approx(0.1)
        # 门禁通过 → 推进到 0.3
        engine.promote("f1", _passing_result())
        assert engine.evaluate("f1").grayscale_status.current_ratio == pytest.approx(0.3)
