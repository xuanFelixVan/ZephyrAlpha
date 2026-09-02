# [BLUEPRINT] MOD-BT-001 | src/zephyr/backtest/core/decision_gate.py | §test
# [MODULE] tests.backtest.test_decision_gate_regime
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_decision_gate_regime.py
# [TTL] task_bound
"""DecisionGate Phase5 后置双闸测试(11号文⑨ BM-BT-07)

覆盖: 无注入零行为变化 / regime 不适配降格 / shrinkage 超阈降格 /
双闸同触发 / 正常通过 / checker 启用但上下文缺失 fail-closed。
"""

from __future__ import annotations

import pytest

from zephyr.backtest.core.decision_gate import (
    DecisionGate,
    DecisionGateConfig,
    DecisionGateContext,
    DecisionGateError,
    default_regime_suitability_checker,
    default_shrinkage_stability_checker,
)


def _stable_sensitivity(center: float = 10.0, sharpe: float = 1.0) -> dict:
    """构造稳定高原参数敏感性扫描(±10%内Sharpe变化<20%)"""
    return {
        "window": [
            (center * 0.9, sharpe * 0.95),
            (center, sharpe),
            (center * 1.1, sharpe * 0.96),
        ]
    }


def _wf_windows(n: int = 4, sharpe: float = 0.8, mdd: float = 0.1) -> list[dict]:
    return [{"sharpe": sharpe, "max_drawdown": mdd} for _ in range(n)]


class TestPhase5NoInjection:
    """无注入零行为变化: config 中两个 checker 均为 None 时,evaluate 结果与原有逻辑完全一致"""

    def test_no_phase5_context_pass(self):
        gate = DecisionGate()
        result = gate.evaluate(
            is_sharpe=1.0,
            params={"window": 10},
            param_sensitivity=_stable_sensitivity(),
            walk_forward_results=_wf_windows(4),
            oos_sharpe=0.85,
        )
        assert result.overall_passed is True
        assert result.can_deploy is True
        assert result.downgraded is False
        assert result.manual_review_required is False

    def test_no_phase5_context_fail_is(self):
        gate = DecisionGate()
        result = gate.evaluate(
            is_sharpe=0.3,
            params={"a": 1},
            param_sensitivity=None,
            walk_forward_results=_wf_windows(4),
            oos_sharpe=0.9,
        )
        assert result.overall_passed is False
        assert result.can_deploy is False
        assert result.downgraded is False
        assert result.manual_review_required is False

    def test_phase5_context_but_no_checker(self):
        """传了 phase5_context 但 config 中 checker 为 None -> 跳过不阻断"""
        gate = DecisionGate()
        ctx = DecisionGateContext(strategy_type="daban", current_regime="r1", oos_params={"window": 12})
        result = gate.evaluate(
            is_sharpe=1.0,
            params={"window": 10},
            param_sensitivity=_stable_sensitivity(),
            walk_forward_results=_wf_windows(4),
            oos_sharpe=0.85,
            phase5_context=ctx,
        )
        assert result.overall_passed is True
        assert result.can_deploy is True
        assert result.downgraded is False


class TestPhase5RegimeDowngrade:
    """regime 不适配降格"""

    def test_daban_in_r1_downgraded(self):
        cfg = DecisionGateConfig(
            regime_suitability_checker=default_regime_suitability_checker,
        )
        gate = DecisionGate(cfg)
        ctx = DecisionGateContext(strategy_type="daban", current_regime="r1")
        result = gate.evaluate(
            is_sharpe=1.0,
            params={"window": 10},
            param_sensitivity=_stable_sensitivity(),
            walk_forward_results=_wf_windows(4),
            oos_sharpe=0.85,
            phase5_context=ctx,
        )
        assert result.overall_passed is True
        assert result.can_deploy is False
        assert result.downgraded is True
        assert result.manual_review_required is True
        assert any("不适配" in r for r in result.reasons)

    def test_trend_in_r2_downgraded(self):
        cfg = DecisionGateConfig(
            regime_suitability_checker=default_regime_suitability_checker,
        )
        gate = DecisionGate(cfg)
        ctx = DecisionGateContext(strategy_type="trend", current_regime="r2")
        result = gate.evaluate(
            is_sharpe=1.0,
            params={"a": 1},
            param_sensitivity=_stable_sensitivity(),
            walk_forward_results=_wf_windows(4),
            oos_sharpe=0.85,
            phase5_context=ctx,
        )
        assert result.downgraded is True
        assert result.can_deploy is False

    def test_multifactor_in_r3_pass(self):
        cfg = DecisionGateConfig(
            regime_suitability_checker=default_regime_suitability_checker,
        )
        gate = DecisionGate(cfg)
        ctx = DecisionGateContext(strategy_type="multifactor", current_regime="r3")
        result = gate.evaluate(
            is_sharpe=1.0,
            params={"a": 1},
            param_sensitivity=_stable_sensitivity(),
            walk_forward_results=_wf_windows(4),
            oos_sharpe=0.85,
            phase5_context=ctx,
        )
        assert result.overall_passed is True
        assert result.can_deploy is True
        assert result.downgraded is False
        assert result.manual_review_required is False

    def test_unknown_strategy_downgraded(self):
        """未知策略类型在默认矩阵中未登记 -> 保守降格"""
        cfg = DecisionGateConfig(
            regime_suitability_checker=default_regime_suitability_checker,
        )
        gate = DecisionGate(cfg)
        ctx = DecisionGateContext(strategy_type="alpha_arb", current_regime="r3")
        result = gate.evaluate(
            is_sharpe=1.0,
            params={"a": 1},
            param_sensitivity=_stable_sensitivity(),
            walk_forward_results=_wf_windows(4),
            oos_sharpe=0.85,
            phase5_context=ctx,
        )
        assert result.downgraded is True
        assert any("未登记" in r for r in result.reasons)

    def test_unknown_regime_fail_closed(self):
        """未知 regime -> fail-closed 降格"""
        cfg = DecisionGateConfig(
            regime_suitability_checker=default_regime_suitability_checker,
        )
        gate = DecisionGate(cfg)
        ctx = DecisionGateContext(strategy_type="daban", current_regime="rx99")
        result = gate.evaluate(
            is_sharpe=1.0,
            params={"a": 1},
            param_sensitivity=_stable_sensitivity(),
            walk_forward_results=_wf_windows(4),
            oos_sharpe=0.85,
            phase5_context=ctx,
        )
        assert result.downgraded is True
        assert any("未知regime" in r for r in result.reasons)

    def test_regime_checker_missing_context_raises(self):
        """checker 启用但 phase5_context 为 None -> raise"""
        cfg = DecisionGateConfig(
            regime_suitability_checker=default_regime_suitability_checker,
        )
        gate = DecisionGate(cfg)
        with pytest.raises(DecisionGateError) as exc_info:
            gate.evaluate(
                is_sharpe=1.0,
                params={"a": 1},
                param_sensitivity=_stable_sensitivity(),
                walk_forward_results=_wf_windows(4),
                oos_sharpe=0.85,
                phase5_context=None,
            )
        assert exc_info.value.error_code == "ZA-BT-0038"


class TestPhase5ShrinkageDowngrade:
    """shrinkage 超阈降格"""

    def test_shrinkage_over_threshold_downgraded(self):
        cfg = DecisionGateConfig(
            shrinkage_stability_checker=default_shrinkage_stability_checker,
        )
        gate = DecisionGate(cfg)
        is_params = {"window": 10, "threshold": 0.5}
        # window 从 10 -> 6, 相对收缩 40% > 默认阈值 30%
        oos_params = {"window": 6, "threshold": 0.5}
        ctx = DecisionGateContext(oos_params=oos_params)
        result = gate.evaluate(
            is_sharpe=1.0,
            params=is_params,
            param_sensitivity=_stable_sensitivity(),
            walk_forward_results=_wf_windows(4),
            oos_sharpe=0.85,
            phase5_context=ctx,
        )
        assert result.overall_passed is True
        assert result.can_deploy is False
        assert result.downgraded is True
        assert result.manual_review_required is True
        assert any("收缩" in r for r in result.reasons)

    def test_shrinkage_under_threshold_pass(self):
        cfg = DecisionGateConfig(
            shrinkage_stability_checker=default_shrinkage_stability_checker,
        )
        gate = DecisionGate(cfg)
        is_params = {"window": 10}
        oos_params = {"window": 9}  # 收缩 10% < 30%
        ctx = DecisionGateContext(oos_params=oos_params)
        result = gate.evaluate(
            is_sharpe=1.0,
            params=is_params,
            param_sensitivity=_stable_sensitivity(),
            walk_forward_results=_wf_windows(4),
            oos_sharpe=0.85,
            phase5_context=ctx,
        )
        assert result.overall_passed is True
        assert result.can_deploy is True
        assert result.downgraded is False

    def test_no_common_numeric_params_skips(self):
        cfg = DecisionGateConfig(
            shrinkage_stability_checker=default_shrinkage_stability_checker,
        )
        gate = DecisionGate(cfg)
        is_params = {"flag": True}
        oos_params = {"flag": False}
        ctx = DecisionGateContext(oos_params=oos_params)
        result = gate.evaluate(
            is_sharpe=1.0,
            params=is_params,
            param_sensitivity=None,
            walk_forward_results=_wf_windows(4),
            oos_sharpe=0.85,
            phase5_context=ctx,
        )
        assert result.overall_passed is True
        assert result.can_deploy is True
        assert result.downgraded is False
        assert any("跳过" in r or "可比" in r for r in result.reasons)

    def test_shrinkage_checker_missing_context_raises(self):
        cfg = DecisionGateConfig(
            shrinkage_stability_checker=default_shrinkage_stability_checker,
        )
        gate = DecisionGate(cfg)
        with pytest.raises(DecisionGateError) as exc_info:
            gate.evaluate(
                is_sharpe=1.0,
                params={"a": 1},
                param_sensitivity=_stable_sensitivity(),
                walk_forward_results=_wf_windows(4),
                oos_sharpe=0.85,
                phase5_context=None,
            )
        assert exc_info.value.error_code == "ZA-BT-0039"


class TestPhase5BothGates:
    """双闸同触发 + 正常通过"""

    def test_both_gates_trigger_downgraded(self):
        """regime 不适配 + shrinkage 超阈同时触发"""
        cfg = DecisionGateConfig(
            regime_suitability_checker=default_regime_suitability_checker,
            shrinkage_stability_checker=default_shrinkage_stability_checker,
        )
        gate = DecisionGate(cfg)
        is_params = {"window": 10}
        oos_params = {"window": 5}  # 收缩 50% > 30%
        ctx = DecisionGateContext(strategy_type="daban", current_regime="r1", oos_params=oos_params)
        result = gate.evaluate(
            is_sharpe=1.0,
            params=is_params,
            param_sensitivity=_stable_sensitivity(),
            walk_forward_results=_wf_windows(4),
            oos_sharpe=0.85,
            phase5_context=ctx,
        )
        assert result.overall_passed is True
        assert result.can_deploy is False
        assert result.downgraded is True
        assert result.manual_review_required is True
        # 两个原因都应在 reasons 中
        assert any("不适配" in r for r in result.reasons)
        assert any("收缩" in r for r in result.reasons)

    def test_both_gates_pass(self):
        """regime 适配 + shrinkage 稳定,正常通过"""
        cfg = DecisionGateConfig(
            regime_suitability_checker=default_regime_suitability_checker,
            shrinkage_stability_checker=default_shrinkage_stability_checker,
        )
        gate = DecisionGate(cfg)
        is_params = {"window": 10}
        oos_params = {"window": 10}  # 无收缩
        ctx = DecisionGateContext(strategy_type="daban", current_regime="r3", oos_params=oos_params)
        result = gate.evaluate(
            is_sharpe=1.0,
            params=is_params,
            param_sensitivity=_stable_sensitivity(),
            walk_forward_results=_wf_windows(4),
            oos_sharpe=0.85,
            phase5_context=ctx,
        )
        assert result.overall_passed is True
        assert result.can_deploy is True
        assert result.downgraded is False
        assert result.manual_review_required is False

    def test_downgrade_not_skip_when_oos_fail(self):
        """OOS 未通过时 Phase5 不应执行(因三阶段未全部通过)"""
        cfg = DecisionGateConfig(
            regime_suitability_checker=default_regime_suitability_checker,
            shrinkage_stability_checker=default_shrinkage_stability_checker,
        )
        gate = DecisionGate(cfg)
        ctx = DecisionGateContext(strategy_type="daban", current_regime="r1", oos_params={"window": 5})
        result = gate.evaluate(
            is_sharpe=1.0,
            params={"window": 10},
            param_sensitivity=_stable_sensitivity(),
            walk_forward_results=_wf_windows(4),
            oos_sharpe=0.5,  # 比率 0.5 < 0.7, OOS 失败
            phase5_context=ctx,
        )
        assert result.overall_passed is False
        assert result.can_deploy is False
        assert result.downgraded is False
        assert result.manual_review_required is False
        # Phase5 原因不应出现
        assert not any("Phase5" in r for r in result.reasons)


class TestPhase5CustomMatrix:
    """自定义适配矩阵覆盖"""

    def test_custom_matrix_override(self):
        custom_matrix = {"daban": frozenset({"r3"})}
        cfg = DecisionGateConfig(
            regime_suitability_checker=lambda st, cr: default_regime_suitability_checker(st, cr, matrix=custom_matrix),
        )
        gate = DecisionGate(cfg)
        # 默认规则 daban 在 r1 降格,但自定义矩阵只降格 r3
        ctx = DecisionGateContext(strategy_type="daban", current_regime="r1")
        result = gate.evaluate(
            is_sharpe=1.0,
            params={"a": 1},
            param_sensitivity=_stable_sensitivity(),
            walk_forward_results=_wf_windows(4),
            oos_sharpe=0.85,
            phase5_context=ctx,
        )
        assert result.downgraded is False
        assert result.can_deploy is True

        # 自定义矩阵在 r3 降格
        ctx2 = DecisionGateContext(strategy_type="daban", current_regime="r3")
        result2 = gate.evaluate(
            is_sharpe=1.0,
            params={"a": 1},
            param_sensitivity=_stable_sensitivity(),
            walk_forward_results=_wf_windows(4),
            oos_sharpe=0.85,
            phase5_context=ctx2,
        )
        assert result2.downgraded is True
