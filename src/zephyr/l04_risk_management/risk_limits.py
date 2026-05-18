# [BLUEPRINT] MOD-L04-001 | 03_modules/l04_risk_management/risk-management-core/blueprint.md | §

# [MODULE] zephyr.l04_risk_management.risk_limits

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

# ---
# layer: l04_risk_management
# category: risk_interface
# status: active
# created: "2026-05-05"
# ---

"""L04 — Risk Limits Calculator

风险限额计算引擎。根据持仓和信号计算风险约束集，输出给 L05 组合优化器强制执行。

核心职责：
  - 单标的仓位上限/下限计算
  - 总杠杆上限计算
  - 行业集中度上限计算
  - VaR / 最大回撤限额
  - 个股特殊限制覆盖
  - 产出 RiskLimits（CTR-003）

CTR 契约：
  消费者 — CTR-002 (FactorSignal) ← L02
  消费者 — CTR-006 (PositionSnapshot) ← L06
  生产者 — CTR-003 (RiskLimits) → L05

依赖方向：L02 + L06 → L04 → L05
"""
from __future__ import annotations

import abc
from decimal import Decimal
from typing import ClassVar, Dict, Optional

from zephyr.trading_contracts.risk.risk_limits import RiskLimits


class RiskLimitsCalculator(abc.ABC):
    """风险限额计算器抽象基类（OCP 扩展点）

    实现者要求：
      - calculate(): 输入当前持仓快照 + 因子信号，输出风险限额集合
      - 单标的权重上限默认 10%，可通过 symbol_overrides 覆盖
      - max_drawdown_limit 触发时，应级联触发 kill_switch 评估
      - 幂等键（INV-007）：每个计算操作必须关联 idempotency_key

    风控层级：
      L1（硬限制）：max_single_position / max_gross_leverage —— 不可突破
      L2（软限制）：max_sector_concentration —— 触发告警但不硬阻断
      L3（熔断线）：max_drawdown_limit —— 触发全仓暂停
    """
    _registry: ClassVar[dict[str, type["RiskLimitsCalculator"]]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not abc.ABC in cls.__bases__ and hasattr(cls, "__calculator_id__"):
            RiskLimitsCalculator._registry[cls.__calculator_id__] = cls

    @abc.abstractmethod
    def calculate(
        self,
        positions: Dict[str, float],
        market_values: Dict[str, float],
        total_nav: Decimal,
        factor_signals: Optional[Dict[str, float]] = None,
    ) -> RiskLimits:
        """计算当前的风险限额约束集"""
        ...


__all__ = [
    "RiskLimits",
    "RiskLimitsCalculator",
]
