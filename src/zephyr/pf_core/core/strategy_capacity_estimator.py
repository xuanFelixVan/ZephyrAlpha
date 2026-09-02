# [BLUEPRINT] MOD-PF-012 | docs/03_modules/_domain_portfolio_core/strategy_capacity_estimator/blueprint.md
# [MODULE] zephyr.pf_core.core.strategy_capacity_estimator
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 运行时装配批（策略容量复核/扩容评审）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 冲击模型 impact_bps=coef×√participation; effective_participation=min(participation_max,(tolerance/coef)²); capacity=Σadv×effective/turnover; utilization=current/capacity; ≥1.0→BREACH, ≥warn_ratio(0.8)→WARNING; 建议按绑定约束结构化产出(BREACH追加DELEVERAGE); 报告frozen; 非法输入Fail-Closed
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CapacityEstimationError
# [TESTS] tests/pf_core/test_strategy_capacity_estimator.py
# [A_module] module_id=MOD-PF-012 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Strategy Capacity Estimator — PC-08 策略容量估算器 (MOD-PF-012, CAND-PF004-005, B3-05544)

ADV/参与率上限/换手率/冲击成本容忍度四约束合成策略容量（AUM 上限）：
  - 参与率约束：AUM × daily_turnover ≤ Σ adv × participation_max
  - 冲击容忍：impact_bps = coef_bps × √participation ≤ tolerance_bps
    → participation ≤ (tolerance/coef)²（平方根冲击模型 MVP）
  - capacity = Σ adv × effective_participation / daily_turnover
输出容量利用率 + 80% 预警线告警 + 结构化扩容建议。

与既有件分工（蓝图 §0 查重裁定，TSV onsite=无）：multifactor_constraint_arbitration
的 C5_ADV_PARTICIPATION_MAX=单票成交裁决常量；default_tca_engine（MOD-L07-001）=
事后成本分析；liquidity_crisis_manager=盘中应急处置。本件=策略级事前容量估算器。

纪律：纯函数无 IO；ADV 等流动性微观结构数据调用方注入（D_DATA 前置，不越域取数）。

依据: blueprint.md（MOD-PF-012）§1 规则
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 标的 ADV 表
#   fields: adv_values {symbol: 日成交额>0}
# - id: I2
#   name: 策略参数
#   fields: daily_turnover>0; participation_max; impact_tolerance_bps; current_aum≥0
# 层: 算法
# - id: A1
#   name_zh: ① 有效参与率
#   name_en: _effective_participation
#   intro: p_impact=(tolerance/coef)²; effective=min(p_max,p_impact); 记录绑定约束
# - id: A2
#   name_zh: ② 容量与利用率
#   name_en: estimate
#   intro: capacity=Σadv×effective/turnover; utilization=current/capacity
# - id: A3
#   name_zh: ③ 预警与扩容建议
#   name_en: _alert_advice
#   intro: ≥1.0 BREACH(+DELEVERAGE), ≥0.8 WARNING; 建议按绑定约束枚举产出
# 层: 输出
# - id: O1
#   name: StrategyCapacityReport
#   fields: capacity_aum/binding/effective_participation/utilization/alert/advice（frozen）
# 边:
# I1 --> A2
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
# [/ALGO_FLOW]
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "BindingConstraint",
    "CapacityAlertLevel",
    "CapacityConfig",
    "CapacityEstimationError",
    "ExpansionAdvice",
    "StrategyCapacityEstimator",
    "StrategyCapacityReport",
]


class CapacityEstimationError(ZephyrBaseError):
    """策略容量估算输入/配置非法（Fail-Closed）。

    错误码：ZA-PF-0084（2026-08-26 对账批转正）。
    """

    error_code = "ZA-PF-0084"


class BindingConstraint(str, Enum):
    """容量绑定约束。"""

    PARTICIPATION = "PARTICIPATION"  # 参与率上限绑定
    IMPACT_TOLERANCE = "IMPACT_TOLERANCE"  # 冲击成本容忍绑定


class CapacityAlertLevel(str, Enum):
    """容量利用率告警级别。"""

    OK = "OK"
    WARNING = "WARNING"  # ≥ 80% 预警线
    BREACH = "BREACH"  # ≥ 100%


class ExpansionAdvice(str, Enum):
    """扩容建议（结构化枚举）。"""

    EXPAND_UNIVERSE = "EXPAND_UNIVERSE"  # 扩充标的池（抬 Σadv）
    REDUCE_TURNOVER = "REDUCE_TURNOVER"  # 降换手率
    RELAX_IMPACT_TOLERANCE = "RELAX_IMPACT_TOLERANCE"  # 放宽冲击容忍（评审）
    DELEVERAGE = "DELEVERAGE"  # 超容先降杠杆


@dataclass(frozen=True)
class CapacityConfig:
    """容量估算配置（C 类可调）。"""

    participation_max: float = 0.05  # 参与率上限（对齐 C5 单票 ≤ 日成交 5% 口径）
    impact_coef_bps: float = 50.0  # 平方根冲击系数（100% 参与率 ≈ 50bps 量级）
    impact_tolerance_bps: float = 50.0  # 冲击成本容忍度
    warn_ratio: float = 0.8  # 预警线（利用率 80%）

    def __post_init__(self) -> None:
        p = float(self.participation_max)
        if not math.isfinite(p) or not 0.0 < p <= 1.0:
            raise CapacityEstimationError(f"participation_max 必须 ∈(0,1]: {p}")
        c = float(self.impact_coef_bps)
        if not math.isfinite(c) or c <= 0:
            raise CapacityEstimationError(f"impact_coef_bps 必须为正有限值: {c}")
        t = float(self.impact_tolerance_bps)
        if not math.isfinite(t) or t <= 0:
            raise CapacityEstimationError(f"impact_tolerance_bps 必须为正有限值: {t}")
        w = float(self.warn_ratio)
        if not math.isfinite(w) or not 0.0 < w < 1.0:
            raise CapacityEstimationError(f"warn_ratio 必须 ∈(0,1): {w}")


@dataclass(frozen=True)
class StrategyCapacityReport:
    """策略容量报告（frozen）。"""

    capacity_aum: float
    binding: BindingConstraint
    effective_participation: float
    utilization: float
    alert: CapacityAlertLevel
    advice: tuple[ExpansionAdvice, ...]
    adv_total: float
    daily_turnover: float


def _require_finite(name: str, value: float) -> float:
    v = float(value)
    if not math.isfinite(v):
        raise CapacityEstimationError(f"{name} 必须为有限值: {value}")
    return v


class StrategyCapacityEstimator:
    """PC-08 策略容量估算器（确定性纯函数）。"""

    def __init__(self, config: CapacityConfig | None = None) -> None:
        self._config = config or CapacityConfig()

    @property
    def config(self) -> CapacityConfig:
        return self._config

    def estimate(
        self,
        *,
        adv_values: Mapping[str, float],
        daily_turnover: float,
        current_aum: float = 0.0,
        participation_max: float | None = None,
        impact_tolerance_bps: float | None = None,
    ) -> StrategyCapacityReport:
        """估算策略容量 + 利用率 + 预警 + 扩容建议。"""
        if not adv_values:
            raise CapacityEstimationError("adv_values 不能为空（流动性微观结构数据前置 D-DATA）")
        adv_total = 0.0
        for sym, adv in adv_values.items():
            if not sym:
                raise CapacityEstimationError("adv_values 标的名不能为空")
            v = _require_finite(f"adv_values[{sym}]", adv)
            if v <= 0:
                raise CapacityEstimationError(f"ADV 必须为正: {sym}={adv}")
            adv_total += v
        turnover = _require_finite("daily_turnover", daily_turnover)
        if turnover <= 0:
            raise CapacityEstimationError(f"daily_turnover 必须为正: {daily_turnover}")
        aum = _require_finite("current_aum", current_aum)
        if aum < 0:
            raise CapacityEstimationError(f"current_aum 必须 ≥0: {current_aum}")

        cfg = self._config
        p_max = (
            cfg.participation_max
            if participation_max is None
            else _require_finite("participation_max", participation_max)
        )
        if not 0.0 < p_max <= 1.0:
            raise CapacityEstimationError(f"participation_max 必须 ∈(0,1]: {p_max}")
        tolerance = (
            cfg.impact_tolerance_bps
            if impact_tolerance_bps is None
            else _require_finite("impact_tolerance_bps", impact_tolerance_bps)
        )
        if tolerance <= 0:
            raise CapacityEstimationError(f"impact_tolerance_bps 必须为正: {tolerance}")

        # ① 有效参与率（平方根冲击：impact=coef×√p ≤ tolerance → p ≤ (tolerance/coef)²）
        p_impact = (tolerance / cfg.impact_coef_bps) ** 2
        effective = min(p_max, p_impact)
        binding = BindingConstraint.PARTICIPATION if p_max <= p_impact else BindingConstraint.IMPACT_TOLERANCE

        # ② 容量与利用率
        capacity = adv_total * effective / turnover
        utilization = aum / capacity if capacity > 0 else math.inf

        # ③ 预警与扩容建议
        if utilization >= 1.0:
            alert = CapacityAlertLevel.BREACH
        elif utilization >= cfg.warn_ratio:
            alert = CapacityAlertLevel.WARNING
        else:
            alert = CapacityAlertLevel.OK
        advice: list[ExpansionAdvice] = []
        if alert is CapacityAlertLevel.BREACH:
            advice.append(ExpansionAdvice.DELEVERAGE)
        if alert is not CapacityAlertLevel.OK:
            if binding is BindingConstraint.PARTICIPATION:
                advice += [ExpansionAdvice.EXPAND_UNIVERSE, ExpansionAdvice.REDUCE_TURNOVER]
            else:
                advice += [ExpansionAdvice.REDUCE_TURNOVER, ExpansionAdvice.RELAX_IMPACT_TOLERANCE]

        return StrategyCapacityReport(
            capacity_aum=capacity,
            binding=binding,
            effective_participation=effective,
            utilization=utilization,
            alert=alert,
            advice=tuple(advice),
            adv_total=adv_total,
            daily_turnover=turnover,
        )
