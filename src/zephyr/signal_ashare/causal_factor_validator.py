# [BLUEPRINT] MOD-SIG-054 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/25_multifactor_strategy_detail.md §3.1
# [MODULE] zephyr.signal_ashare.causal_factor_validator
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.causal_inference_engine; numpy
# [CONSUMERS] (待因子池治理层 factor_pool_manager / 盘前因子全量评估接线)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 加权乘子仅三档离散映射（提升/中性/降权）；样本不足 → degraded 中性乘子不抛错；纯函数无副作用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 批量评估单因子失败不阻断其他因子（该因子记 degraded）
# [TESTS] tests/signal_ashare/test_causal_factor_validator.py
# [A_module] module_id=MOD-SIG-054 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: 候选因子值序列 + 前瞻收益序列 + 市场控制序列（可空）+ 因子名
# A1: 调 MOD-SIG-042 assess_causality（lead-lag 双 IC + 偏 IC）→ 因果/相关/伪相关/不显著裁定
# A2: 加权映射——CAUSAL_CANDIDATE ×1.2（因果加权提升 proposed）/ CORRELATED ×1.0 / SPURIOUS ×0.5 / INSIGNIFICANT ×1.0
# A3: 降级——样本不足等 ValueError → degraded=True 中性乘子（仅统计评估口径，跳过因果加权）
# O1: FactorCausalReport（单因子）/ list[FactorCausalReport]（批量）
# [/ALGO_FLOW]
"""因果因子验证器（BM-SEL-02-M，MOD-SIG-054）。

新因子入库前 + 盘前因子全量评估时做因果验证：消费 MOD-SIG-042 因果推演引擎的
lead-lag 双 IC + 偏 IC 裁定，区分相关因子 vs 因果因子，因果因子加权提升
（×1.2 proposed，25 号 memo §3.1 BM-SEL-02-M 契约）。

降级路径（memo 既定）：因果证据不足（样本不够/控制序列缺失致判定失败）→
degraded=True + 中性乘子 1.0，等价"仅统计评估（IC/IR），跳过因果加权"。

边界：本模块只产出验证报告与建议乘子，不直接改因子池——池治理（休眠/淘汰/
权重生效）归 factor_pool_manager（MOD-L02-018）决策。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Iterable, Mapping

from zephyr.signal_ashare.causal_inference_engine import CausalVerdict, assess_causality

__all__: Final = [
    "CausalValidatorConfig",
    "FactorCausalReport",
    "validate_factor",
    "validate_factors",
]

#: 裁定 → 建议加权乘子（25 号 memo：因果加权提升 proposed；伪相关降权防数据挖掘产物）
_VERDICT_MULTIPLIER: Final = {
    CausalVerdict.CAUSAL_CANDIDATE: 1.2,
    CausalVerdict.CORRELATED: 1.0,
    CausalVerdict.SPURIOUS: 0.5,
    CausalVerdict.INSIGNIFICANT: 1.0,
}


@dataclass(frozen=True)
class CausalValidatorConfig:
    """验证参数（透传 042 判定阈值 + 乘子覆盖）。

    Attributes:
        min_samples: 最小样本数（透传 042）
        ic_floor: IC 显著性下限（0.02 与因子库有效线一致）
        causal_boost: 因果候选加权乘子（默认 1.2，memo proposed 值）
        spurious_discount: 伪相关降权乘子（默认 0.5）
    """

    min_samples: int = 30
    ic_floor: float = 0.02
    causal_boost: float = 1.2
    spurious_discount: float = 0.5


@dataclass(frozen=True)
class FactorCausalReport:
    """单因子因果验证报告。"""

    factor_name: str
    forward_ic: float  # 因子领先 IC（degraded 时尽力而为，无法计算为 0.0）
    backward_ic: float
    partial_ic: float
    verdict: CausalVerdict | None  # None=degraded（证据不足未裁定）
    weight_multiplier: float  # 建议加权乘子
    n_samples: int
    degraded: bool = False  # True=降级（仅统计评估口径，跳过因果加权）


def validate_factor(
    factor_name: str,
    factor_values: Iterable[float],
    forward_returns: Iterable[float],
    *,
    control_values: Iterable[float] | None = None,
    config: CausalValidatorConfig | None = None,
) -> FactorCausalReport:
    """单因子因果验证：因果裁定 → 建议加权乘子。

    样本不足/序列非法（042 抛 ValueError）→ degraded 报告（verdict=None，
    乘子 1.0 中性）——不阻断评估流程，与 memo 降级路径一致。
    """
    cfg = config or CausalValidatorConfig()
    try:
        a = assess_causality(
            factor_values,
            forward_returns,
            control_values=control_values,
            min_samples=cfg.min_samples,
            ic_floor=cfg.ic_floor,
        )
    except ValueError:
        return FactorCausalReport(
            factor_name=factor_name,
            forward_ic=0.0,
            backward_ic=0.0,
            partial_ic=0.0,
            verdict=None,
            weight_multiplier=1.0,
            n_samples=max(0, len(list(factor_values)) - 1),
            degraded=True,
        )
    multiplier = _VERDICT_MULTIPLIER[a.verdict]
    if a.verdict is CausalVerdict.CAUSAL_CANDIDATE:
        multiplier = cfg.causal_boost
    elif a.verdict is CausalVerdict.SPURIOUS:
        multiplier = cfg.spurious_discount
    return FactorCausalReport(
        factor_name=factor_name,
        forward_ic=a.forward_ic,
        backward_ic=a.backward_ic,
        partial_ic=a.partial_ic,
        verdict=a.verdict,
        weight_multiplier=multiplier,
        n_samples=a.n_samples,
        degraded=False,
    )


def validate_factors(
    factors: Mapping[str, tuple[Iterable[float], Iterable[float]]],
    *,
    control_values: Iterable[float] | None = None,
    config: CausalValidatorConfig | None = None,
) -> list[FactorCausalReport]:
    """批量因果验证（盘前全量评估入口）。

    factors: {factor_name: (factor_values, forward_returns)}。单因子失败不阻断
    其他因子（该因子记 degraded，见 validate_factor）。
    """
    return [
        validate_factor(name, f, r, control_values=control_values, config=config)
        for name, (f, r) in factors.items()
    ]
