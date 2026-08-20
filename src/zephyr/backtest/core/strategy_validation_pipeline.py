# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.strategy_validation_pipeline
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.decision_gate; zephyr.backtest.core.overfitting_detector
# [CONSUMERS] 首批策略上线验证(52号§7①编排入口)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只编排不重造(过拟合检测/三阶段门控全委托既有模块);can_deploy=技术门控∧非过拟合,仍需人工审批
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] StrategyValidationError(ZA-BT-0035)
# [TESTS] tests/backtest/test_strategy_validation_pipeline.py
# [TTL] permanent
# [A_module] module_id=MOD-BT-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [ALGO_FLOW]
# I1: StrategyValidationRequest(strategy_id/is_sharpe/params/walk_forward_results/oos_sharpe + 可选扰动/泛化/DSR注入)
# I2: DecisionGate + OverfittingDetector 实例(可注入, 默认新建)
# A1: 过拟合三维+SIM-38样本内外对比(OverfittingDetector.detect)
# A2: IS→WFA→OOS三阶段门控(DecisionGate.evaluate, dsr可选判定器默认关闭)
# A3: 综合裁决 can_deploy = gate.can_deploy ∧ ¬is_overfitting
# O1: StrategyValidationVerdict(gate三阶段结果+过拟合结论+can_deploy+理由)
# [/ALGO_FLOW]
"""策略验证流水线编排入口模块(52号 §7①)

职责:
  - 统一"策略验证流水线"调用入口: 过拟合三维度检测 → IS→WFA→OOS 三阶段门控
    → 综合裁决, 供首批策略上线前验证使用
  - 只编排不重造: 过拟合检测委托 OverfittingDetector, 门控委托 DecisionGate,
    DSR 由调用方预计算后经 DecisionGate 可选判定器注入(默认关闭)

约束:
  - can_deploy 仅技术门控通过, 正式上线仍需人工审批(52号 §4 裁定)
  - 输入注入式: 各阶段回测产物(IS/OOS Sharpe、WF fold 结果、参数敏感性扫描)
    由调用方供给, 本模块不直接跑回测

SSoT: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/52_backtest_framework_docking.md §7①
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from zephyr.backtest.core.decision_gate import (
    DecisionGate,
    DecisionGateResult,
)
from zephyr.backtest.core.overfitting_detector import OverfittingDetector

__all__ = [
    "StrategyValidationError",
    "StrategyValidationRequest",
    "StrategyValidationVerdict",
    "run_strategy_validation",
]


class StrategyValidationError(Exception):
    """策略验证流水线错误(输入非法)"""

    error_code = "ZA-BT-0035"

    def __init__(self, *args, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


@dataclass(frozen=True)
class StrategyValidationRequest:
    """策略验证流水线输入(不可变, 输入注入式)

    Attributes:
        strategy_id: 策略标识
        is_sharpe: 样本内 Sharpe(同时作为参数敏感性基准)
        params: 最优参数字典
        walk_forward_results: Walk-Forward 各 fold 结果(门控与过拟合维度1共用)
        oos_sharpe: 样本外 Sharpe
        param_sensitivity: 参数敏感性扫描 {参数名: [(值, Sharpe)]}, None=跳过稳定性门控
        params_locked: OOS 阶段参数是否已锁定(默认 True)
        perturbed_results: 参数微调±10% 结果列表(过拟合维度2), None=跳过
        period_results: 跨时段/跨标的结果列表(过拟合维度3), None=跳过
        dsr: 调用方预计算的 DSR 值(metrics.calculate_dsr 产出), None=不注入;
            仅当 DecisionGateConfig.dsr_threshold 显式配置时参与 OOS 判定
    """

    strategy_id: str
    is_sharpe: float
    params: dict[str, Any]
    walk_forward_results: list[dict]
    oos_sharpe: float
    param_sensitivity: dict[str, list[tuple[Any, float]]] | None = None
    params_locked: bool = True
    perturbed_results: list[dict] | None = None
    period_results: list[dict] | None = None
    dsr: float | None = None


@dataclass(frozen=True)
class StrategyValidationVerdict:
    """策略验证流水线裁决(不可变)

    Attributes:
        strategy_id: 策略标识
        overfitting: OverfittingDetector.detect 综合结论
        gate: DecisionGate.evaluate 三阶段门控结果
        can_deploy: 技术门控通过且未检出过拟合(仍需人工审批)
        reasons: 综合判定理由
    """

    strategy_id: str
    overfitting: dict
    gate: DecisionGateResult
    can_deploy: bool
    reasons: tuple[str, ...] = field(default_factory=tuple)


def run_strategy_validation(
    request: StrategyValidationRequest,
    *,
    gate: DecisionGate | None = None,
    detector: OverfittingDetector | None = None,
) -> StrategyValidationVerdict:
    """策略验证流水线编排入口(过拟合检测 → 三阶段门控 → 综合裁决)

    Args:
        request: 验证请求(各阶段回测产物输入注入)
        gate: 决策门控实例(可注入自定义配置; None=默认 DecisionGate())
        detector: 过拟合检测器实例(可注入; None=默认 OverfittingDetector())

    Returns:
        StrategyValidationVerdict: 综合裁决

    Raises:
        StrategyValidationError: request 非法(非 StrategyValidationRequest / strategy_id 空)
        DecisionGateError: 门控输入非法(由 DecisionGate 抛出, 向上传递)
    """
    if not isinstance(request, StrategyValidationRequest):
        raise StrategyValidationError(f"request必须是StrategyValidationRequest: {type(request).__name__}")
    if not isinstance(request.strategy_id, str) or not request.strategy_id.strip():
        raise StrategyValidationError(f"strategy_id不能为空: {request.strategy_id!r}")

    gate = gate if gate is not None else DecisionGate()
    detector = detector if detector is not None else OverfittingDetector()

    # A1: 过拟合三维度 + SIM-38 样本内外对比
    overfitting = detector.detect(
        walk_forward_results=request.walk_forward_results,
        perturbed_results=request.perturbed_results,
        period_results=request.period_results,
        is_sharpe=request.is_sharpe,
        oos_sharpe=request.oos_sharpe,
    )

    # A2: IS→WFA→OOS 三阶段门控(dsr 可选判定器, gate 未配置阈值时忽略)
    gate_result = gate.evaluate(
        is_sharpe=request.is_sharpe,
        params=request.params,
        param_sensitivity=request.param_sensitivity,
        walk_forward_results=request.walk_forward_results,
        oos_sharpe=request.oos_sharpe,
        params_locked=request.params_locked,
        dsr=request.dsr,
    )

    # A3: 综合裁决——技术门控通过且未检出过拟合(SIM-56 语义)
    can_deploy = bool(gate_result.can_deploy) and not overfitting["is_overfitting"]
    reasons: list[str] = list(gate_result.reasons)
    if overfitting["is_overfitting"]:
        reasons.append("过拟合检测否决: " + "; ".join(overfitting["reasons"]))
    if can_deploy:
        reasons.append("流水线裁决: 技术门控通过且未检出过拟合(正式上线仍需人工审批)")
    else:
        reasons.append("流水线裁决: 不可上线")

    return StrategyValidationVerdict(
        strategy_id=request.strategy_id,
        overfitting=overfitting,
        gate=gate_result,
        can_deploy=can_deploy,
        reasons=tuple(reasons),
    )
