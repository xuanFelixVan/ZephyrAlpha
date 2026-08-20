# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [A_module] module_id=MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [A_test] module_id: MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.backtest.test_strategy_validation_pipeline
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_strategy_validation_pipeline.py
# [TTL] task_bound
"""策略验证流水线编排入口单元测试(52号 §7①).

覆盖: 全链路通过(IS→WFA→OOS+过拟合三维)、门控否决传播、过拟合否决传播
(SIM-56语义)、DSR 经门控可选判定器注入(默认关闭/启用)、输入校验、
可注入 gate/detector 实例。
"""
from __future__ import annotations

import pytest

from zephyr.backtest.core.decision_gate import DecisionGate, DecisionGateConfig
from zephyr.backtest.core.overfitting_detector import OverfittingDetector
from zephyr.backtest.core.strategy_validation_pipeline import (
    StrategyValidationError,
    StrategyValidationRequest,
    run_strategy_validation,
)


def _stable_sensitivity() -> dict:
    return {"window": [(9.0, 0.95), (10.0, 1.0), (11.0, 0.96)]}


def _wf_windows() -> list[dict]:
    return [{"sharpe": 0.8, "max_drawdown": 0.1} for _ in range(4)]


def _clean_request(**overrides) -> StrategyValidationRequest:
    base = {
        "strategy_id": "strat_mf_v1",
        "is_sharpe": 1.0,
        "params": {"window": 10},
        "walk_forward_results": _wf_windows(),
        "oos_sharpe": 0.85,
        "param_sensitivity": _stable_sensitivity(),
        "perturbed_results": [{"sharpe_ratio": 0.95}, {"sharpe_ratio": 1.02}],
        "period_results": [
            {"sharpe_ratio": 0.7}, {"sharpe_ratio": 0.8}, {"sharpe_ratio": 0.9},
        ],
    }
    base.update(overrides)
    return StrategyValidationRequest(**base)


class TestPipelineHappyPath:
    def test_full_pass_can_deploy(self):
        verdict = run_strategy_validation(_clean_request())
        assert verdict.can_deploy is True
        assert verdict.gate.overall_passed is True
        assert verdict.overfitting["is_overfitting"] is False
        assert any("人工审批" in x for x in verdict.reasons)

    def test_verdict_carries_strategy_id(self):
        verdict = run_strategy_validation(_clean_request())
        assert verdict.strategy_id == "strat_mf_v1"

    def test_minimal_request(self):
        # 可选维度全缺省: 仅必填字段, 过拟合维度默认稳定
        req = StrategyValidationRequest(
            strategy_id="s1",
            is_sharpe=1.0,
            params={"a": 1},
            walk_forward_results=_wf_windows(),
            oos_sharpe=0.9,
        )
        verdict = run_strategy_validation(req)
        assert verdict.can_deploy is True


class TestGateVetoPropagation:
    def test_is_fail_no_deploy(self):
        verdict = run_strategy_validation(_clean_request(is_sharpe=0.3, oos_sharpe=0.9))
        # IS 未过 → 门控否; 且 is_sharpe=0.3, perturbed 基准变化大 → 过拟合亦否决
        assert verdict.can_deploy is False
        assert verdict.gate.is_stage.passed is False

    def test_wfa_disaster_no_deploy(self):
        wf = _wf_windows()
        wf[0] = {"sharpe": 0.9, "max_drawdown": 0.6}
        verdict = run_strategy_validation(_clean_request(walk_forward_results=wf))
        assert verdict.can_deploy is False
        assert verdict.gate.wfa_stage.has_disaster is True

    def test_oos_ratio_fail_no_deploy(self):
        verdict = run_strategy_validation(_clean_request(oos_sharpe=0.5))
        assert verdict.can_deploy is False
        assert verdict.gate.oos_stage.passed is False

    def test_params_unlocked_no_deploy(self):
        verdict = run_strategy_validation(_clean_request(params_locked=False))
        assert verdict.can_deploy is False


class TestOverfittingVetoPropagation:
    def test_oos_is_veto_blocks_deploy(self):
        # oos/is=0.65 < 0.70 → SIM-38 硬否决(门控 OOS 同样不过, 双闸一致)
        verdict = run_strategy_validation(_clean_request(oos_sharpe=0.65))
        assert verdict.overfitting["is_overfitting"] is True
        assert verdict.can_deploy is False

    def test_param_unstable_blocks_deploy(self):
        verdict = run_strategy_validation(
            _clean_request(perturbed_results=[{"sharpe_ratio": 0.4}])
        )
        assert verdict.overfitting["parameter_stable"] is False
        assert verdict.can_deploy is False

    def test_overfitting_reason_recorded(self):
        verdict = run_strategy_validation(
            _clean_request(perturbed_results=[{"sharpe_ratio": 0.4}])
        )
        assert any("过拟合检测否决" in x for x in verdict.reasons)


class TestDSRInjection:
    def test_default_gate_ignores_dsr(self):
        # 默认门控未配置 dsr_threshold → 注入低 dsr 不影响裁决
        verdict = run_strategy_validation(_clean_request(dsr=0.0))
        assert verdict.can_deploy is True

    def test_custom_gate_with_dsr_threshold(self):
        gate = DecisionGate(DecisionGateConfig(dsr_threshold=0.5))
        verdict = run_strategy_validation(_clean_request(dsr=0.3), gate=gate)
        assert verdict.can_deploy is False
        assert verdict.gate.oos_stage.dsr == pytest.approx(0.3)

    def test_custom_gate_dsr_pass(self):
        gate = DecisionGate(DecisionGateConfig(dsr_threshold=0.5))
        verdict = run_strategy_validation(_clean_request(dsr=0.9), gate=gate)
        assert verdict.can_deploy is True

    def test_custom_detector_injection(self):
        detector = OverfittingDetector()
        verdict = run_strategy_validation(_clean_request(), detector=detector)
        assert verdict.can_deploy is True


class TestInputValidation:
    def test_non_request_raises(self):
        with pytest.raises(StrategyValidationError):
            run_strategy_validation({"strategy_id": "x"})

    def test_blank_strategy_id_raises(self):
        with pytest.raises(StrategyValidationError):
            run_strategy_validation(_clean_request(strategy_id="  "))

    def test_error_code(self):
        assert StrategyValidationError("x").error_code == "ZA-BT-0035"
