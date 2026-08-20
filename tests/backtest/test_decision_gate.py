# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [A_module] module_id=MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [A_test] module_id: MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.backtest.test_decision_gate
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_decision_gate.py
# [TTL] task_bound
"""DecisionGate 单元测试(52号 §7 新发现1 测试债清偿 + §7③ DSR可选判定器).

覆盖: IS准入/参数稳定性门控(高原/悬崖)、WFA多数通过/灾难否决、OOS比率/参数锁定、
evaluate 不可跳级、回测-实盘偏差监控(ok/warn/retire)、
DSR 可选判定器(默认关闭不破坏既有行为/启用后第四条件/未注入fail-closed)。
"""

from __future__ import annotations

import pytest

from zephyr.backtest.core.decision_gate import (
    DecisionGate,
    DecisionGateConfig,
    DecisionGateError,
)

# ============== 辅助构造 ==============


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


# ============== IS 阶段 ==============


class TestISStage:
    def test_sharpe_pass(self):
        gate = DecisionGate()
        r = gate.check_is_stage(0.6, {"a": 1})
        assert r.passed is True

    def test_sharpe_boundary_fail(self):
        gate = DecisionGate()
        # 0.5 不严格大于阈值0.5 → 不通过
        r = gate.check_is_stage(0.5, {"a": 1})
        assert r.passed is False

    def test_sharpe_non_numeric_raises(self):
        gate = DecisionGate()
        with pytest.raises(DecisionGateError):
            gate.check_is_stage("high", {"a": 1})

    def test_params_not_dict_raises(self):
        gate = DecisionGate()
        with pytest.raises(DecisionGateError):
            gate.check_is_stage(1.0, [1, 2])

    def test_no_sensitivity_skips_stability(self):
        gate = DecisionGate()
        r = gate.check_is_stage(1.0, {"a": 1}, param_sensitivity=None)
        assert r.passed is True
        assert r.is_plateau_stable is True
        assert any("跳过稳定性门控" in x for x in r.reasons)

    def test_stable_plateau_passes(self):
        gate = DecisionGate()
        r = gate.check_is_stage(1.0, {"window": 10}, _stable_sensitivity())
        assert r.passed is True
        assert r.is_plateau_stable is True

    def test_cliff_param_fails(self):
        gate = DecisionGate()
        # 相邻点Sharpe下降>50% → 悬崖型
        sensitivity = {"window": [(9.0, 0.1), (10.0, 1.0), (11.0, 0.95)]}
        r = gate.check_is_stage(1.0, {"window": 10}, sensitivity)
        assert r.passed is False
        assert r.is_plateau_stable is False

    def test_empty_scan_points_unstable(self):
        gate = DecisionGate()
        r = gate.check_is_stage(1.0, {"window": 10}, {"window": []})
        assert r.is_plateau_stable is False
        assert r.passed is False

    def test_sensitivity_not_dict_raises(self):
        gate = DecisionGate()
        with pytest.raises(DecisionGateError):
            gate.check_is_stage(1.0, {"a": 1}, param_sensitivity=[1, 2])


# ============== 参数稳定高原/悬崖判定 ==============


class TestStabilityPlateau:
    def test_plateau_detected(self):
        gate = DecisionGate()
        info = gate.check_stability_plateau("p", [(9.0, 0.95), (10.0, 1.0), (11.0, 0.96)])
        assert info["is_plateau"] is True
        assert info["is_cliff"] is False
        assert info["center_value"] == 10.0

    def test_cliff_detected(self):
        gate = DecisionGate()
        info = gate.check_stability_plateau("p", [(9.0, 0.2), (10.0, 1.0), (11.0, 0.95)])
        assert info["is_cliff"] is True

    def test_empty_points(self):
        gate = DecisionGate()
        info = gate.check_stability_plateau("p", [])
        assert info["is_plateau"] is False
        assert info["center_value"] is None

    def test_single_point_insufficient(self):
        gate = DecisionGate()
        info = gate.check_stability_plateau("p", [(10.0, 1.0)])
        assert info["is_plateau"] is False

    def test_invalid_structure_raises(self):
        gate = DecisionGate()
        with pytest.raises(DecisionGateError):
            gate.check_stability_plateau("p", "not_a_list")
        with pytest.raises(DecisionGateError):
            gate.check_stability_plateau("p", [(10.0, 1.0, 3.0)])
        with pytest.raises(DecisionGateError):
            gate.check_stability_plateau("p", [(10.0, "high")])

    def test_volatile_window_not_plateau(self):
        gate = DecisionGate()
        # ±10%窗口内Sharpe相对变化 (1.0-0.6)/1.0=40% > 容忍度20%
        info = gate.check_stability_plateau("p", [(9.5, 0.6), (10.0, 1.0), (10.5, 0.9)])
        assert info["is_plateau"] is False


# ============== WFA 阶段 ==============


class TestWFAStage:
    def test_empty_windows_fail(self):
        gate = DecisionGate()
        r = gate.check_wfa_stage([])
        assert r.passed is False
        assert r.windows_total == 0

    def test_majority_pass(self):
        gate = DecisionGate()
        r = gate.check_wfa_stage(_wf_windows(4, sharpe=0.8))
        assert r.passed is True
        assert r.windows_passed == 4

    def test_majority_boundary_fail(self):
        gate = DecisionGate()
        # 2/4=0.5 不严格大于0.5 → 不通过
        windows = [{"sharpe": 0.8}, {"sharpe": 0.8}, {"sharpe": -0.1}, {"sharpe": -0.1}]
        r = gate.check_wfa_stage(windows)
        assert r.passed is False
        assert r.windows_passed == 2

    def test_disaster_veto(self):
        gate = DecisionGate()
        windows = _wf_windows(4, sharpe=0.8)
        windows[1] = {"sharpe": 0.9, "max_drawdown": 0.6}  # >0.5 灾难回撤
        r = gate.check_wfa_stage(windows)
        assert r.passed is False
        assert r.has_disaster is True

    def test_disaster_negative_sign_compatible(self):
        gate = DecisionGate()
        windows = [{"sharpe": 0.8, "max_drawdown": -0.55}]  # 负号表达取绝对值
        r = gate.check_wfa_stage(windows)
        assert r.has_disaster is True

    def test_passed_field_preferred(self):
        gate = DecisionGate()
        windows = [{"passed": True, "sharpe": -5.0}, {"passed": True}, {"passed": False}]
        r = gate.check_wfa_stage(windows)
        assert r.windows_passed == 2

    def test_missing_fields_counted_fail(self):
        gate = DecisionGate()
        r = gate.check_wfa_stage([{}, {"sharpe": 0.8}])
        assert r.windows_passed == 1

    def test_invalid_window_structure_raises(self):
        gate = DecisionGate()
        with pytest.raises(DecisionGateError):
            gate.check_wfa_stage([["not_dict"]])
        with pytest.raises(DecisionGateError):
            gate.check_wfa_stage([{"sharpe": "bad"}])
        with pytest.raises(DecisionGateError):
            gate.check_wfa_stage([{"sharpe": 0.8, "max_drawdown": "bad"}])

    def test_not_list_raises(self):
        gate = DecisionGate()
        with pytest.raises(DecisionGateError):
            gate.check_wfa_stage("not_list")


# ============== OOS 阶段 ==============


class TestOOSStage:
    def test_pass(self):
        gate = DecisionGate()
        r = gate.check_oos_stage(1.0, 0.8, params_locked=True)
        assert r.passed is True
        assert r.oos_is_ratio == pytest.approx(0.8)

    def test_ratio_boundary(self):
        gate = DecisionGate()
        r = gate.check_oos_stage(1.0, 0.7, params_locked=True)
        assert r.passed is True  # >= 0.7 通过

    def test_ratio_fail(self):
        gate = DecisionGate()
        r = gate.check_oos_stage(1.0, 0.69, params_locked=True)
        assert r.passed is False

    def test_params_not_locked_fail(self):
        gate = DecisionGate()
        r = gate.check_oos_stage(1.0, 0.9, params_locked=False)
        assert r.passed is False

    def test_is_sharpe_non_positive_fail(self):
        gate = DecisionGate()
        r = gate.check_oos_stage(0.0, 0.9)
        assert r.passed is False
        assert r.oos_is_ratio == 0.0

    def test_non_numeric_raises(self):
        gate = DecisionGate()
        with pytest.raises(DecisionGateError):
            gate.check_oos_stage("a", 0.8)


# ============== DSR 可选判定器(52号 §7③) ==============


class TestDSROptionalJudge:
    def test_default_off_dsr_ignored(self):
        """默认关闭: dsr_threshold=None 时即使注入低dsr也不参与判定"""
        gate = DecisionGate()
        r = gate.check_oos_stage(1.0, 0.9, params_locked=True, dsr=0.0)
        assert r.passed is True
        assert r.dsr is None

    def test_enabled_pass(self):
        gate = DecisionGate(DecisionGateConfig(dsr_threshold=0.5))
        r = gate.check_oos_stage(1.0, 0.9, params_locked=True, dsr=0.6)
        assert r.passed is True
        assert r.dsr == pytest.approx(0.6)
        assert any("DSR判定通过" in x for x in r.reasons)

    def test_enabled_below_threshold_fail(self):
        gate = DecisionGate(DecisionGateConfig(dsr_threshold=0.5))
        r = gate.check_oos_stage(1.0, 0.9, params_locked=True, dsr=0.49)
        assert r.passed is False
        assert any("DSR判定未通过" in x for x in r.reasons)

    def test_enabled_no_injection_fail_closed(self):
        gate = DecisionGate(DecisionGateConfig(dsr_threshold=0.5))
        r = gate.check_oos_stage(1.0, 0.9, params_locked=True, dsr=None)
        assert r.passed is False
        assert any("fail-closed" in x for x in r.reasons)

    def test_enabled_non_numeric_dsr_raises(self):
        gate = DecisionGate(DecisionGateConfig(dsr_threshold=0.5))
        with pytest.raises(DecisionGateError):
            gate.check_oos_stage(1.0, 0.9, params_locked=True, dsr="bad")

    def test_evaluate_passes_dsr_through(self):
        gate = DecisionGate(DecisionGateConfig(dsr_threshold=0.5))
        result = gate.evaluate(
            is_sharpe=1.0,
            params={"window": 10},
            param_sensitivity=_stable_sensitivity(),
            walk_forward_results=_wf_windows(4),
            oos_sharpe=0.9,
            dsr=0.4,
        )
        assert result.overall_passed is False
        assert result.can_deploy is False
        assert result.oos_stage.dsr == pytest.approx(0.4)


# ============== evaluate 编排(不可跳级) ==============


class TestEvaluate:
    def test_full_pass(self):
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
        assert result.is_stage.passed and result.wfa_stage.passed and result.oos_stage.passed

    def test_is_fail_skips_wfa_oos(self):
        gate = DecisionGate()
        result = gate.evaluate(
            is_sharpe=0.3,
            params={"a": 1},
            param_sensitivity=None,
            walk_forward_results=_wf_windows(4),
            oos_sharpe=0.9,
        )
        assert result.overall_passed is False
        assert result.wfa_stage.windows_total == 0
        assert any("跳过" in x for x in result.wfa_stage.reasons)
        assert any("跳过" in x for x in result.oos_stage.reasons)

    def test_wfa_fail_skips_oos(self):
        gate = DecisionGate()
        result = gate.evaluate(
            is_sharpe=1.0,
            params={"window": 10},
            param_sensitivity=_stable_sensitivity(),
            walk_forward_results=[{"sharpe": -0.5, "max_drawdown": 0.6}],
            oos_sharpe=0.9,
        )
        assert result.overall_passed is False
        assert result.wfa_stage.passed is False
        assert any("跳过" in x for x in result.oos_stage.reasons)

    def test_oos_fail_no_deploy(self):
        gate = DecisionGate()
        result = gate.evaluate(
            is_sharpe=1.0,
            params={"window": 10},
            param_sensitivity=_stable_sensitivity(),
            walk_forward_results=_wf_windows(4),
            oos_sharpe=0.5,  # 比率0.5 < 0.7
        )
        assert result.overall_passed is False
        assert result.can_deploy is False


# ============== 回测-实盘偏差监控 ==============


class TestDeviationMonitor:
    def test_ok(self):
        gate = DecisionGate()
        r = gate.monitor_backtest_live_deviation(1.0, 0.8)  # 偏差20%
        assert r["action"] == "ok"
        assert r["deviation"] == pytest.approx(0.2)

    def test_warn(self):
        gate = DecisionGate()
        r = gate.monitor_backtest_live_deviation(1.0, 0.6)  # 偏差40% > 30%
        assert r["action"] == "warn"

    def test_retire(self):
        gate = DecisionGate()
        r = gate.monitor_backtest_live_deviation(1.0, 0.4)  # 偏差60% > 50%
        assert r["action"] == "retire"

    def test_zero_backtest_raises(self):
        gate = DecisionGate()
        with pytest.raises(DecisionGateError):
            gate.monitor_backtest_live_deviation(0.0, 0.5)

    def test_non_numeric_raises(self):
        gate = DecisionGate()
        with pytest.raises(DecisionGateError):
            gate.monitor_backtest_live_deviation("a", 0.5)

    def test_registry_defaults(self):
        cfg = DecisionGateConfig()
        assert cfg.backtest_live_deviation_warn == pytest.approx(0.30)
        assert cfg.backtest_live_deviation_retire == pytest.approx(0.50)
