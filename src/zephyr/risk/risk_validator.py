# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain-risk/risk-management-core/blueprint.md
# [MODULE] zephyr.risk.risk_validator
# [DOMAIN] D_RISK
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_risk_validator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: risk
# category: risk_interface
# status: active
# created: "2026-05-05"
# ---

"""D_RISK — Risk Validator

风险校验引擎。在交易执行前校验订单和持仓是否符合风险限额。

核心职责：
  - Pre-trade 风控校验（订单是否符合 RiskLimits）
  - 持仓突破检测（当前持仓是否触发风控线）
  - 熔断判定（drawdown / VaR breach → kill_switch）
  - 产出 RiskLimitViolationError（CTR-ERR-004）

CTR 契约：
  消费者 — CTR-003 (RiskLimits) ← D_RISK（本层产出，内部消费）
  消费者 — CTR-002 (FactorSignal) ← D_FACTOR
  消费者 — CTR-006 (PositionSnapshot) ← D_EXECUTION_CORE
  生产者 — CTR-ERR-004 (RiskLimitViolationError) → D_PORTFOLIO_CORE, D_EXECUTION_CORE

依赖方向：D_FACTOR + D_EXECUTION_CORE → D_RISK → D_PORTFOLIO_CORE/D_EXECUTION_CORE
"""

from __future__ import annotations

import abc
import inspect
from dataclasses import dataclass
from decimal import Decimal
from typing import ClassVar


class ViolatedConstraint(str):
    POSITION_LIMIT = "position_limit"
    LEVERAGE_LIMIT = "leverage_limit"
    VAR_BREACH = "var_breach"
    DRAWDOWN_TRIGGER = "drawdown_trigger"
    SECTOR_CONCENTRATION = "sector_concentration"
    CONCENTRATION_LIMIT = "concentration_limit"


@dataclass(frozen=True)
class ViolationDetail:
    """单条违规详情"""

    constraint: str
    description: str
    limit_value: Decimal
    actual_value: Decimal
    severity: str = "HALT"  # HALT | WARNING


class RiskValidator(abc.ABC):
    """风险校验器抽象基类（OCP 扩展点）

    实现者要求：
      - validate_order(): 单笔订单的 pre-trade 校验
      - validate_portfolio(): 全组合的风控状态校验
      - 任何 HALT 级别违规 MUST 抛出 RiskLimitViolationError（CTR-ERR-004）
      - WARNING 级别违规记录日志但不断交易

    安全约束：
      - 禁止降级 HALT → WARNING——如果这是代码逻辑导致的，降级等于资金安全风险
      - position_limit / leverage_limit / drawdown_trigger 均为 HALT 级别
      - kill_switch 触发后 MUST 阻断所有订单，直到人工确认恢复
    """

    _registry: ClassVar[dict[str, type[RiskValidator]]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not inspect.isabstract(cls) and "__validator_id__" in cls.__dict__:
            RiskValidator._registry[cls.__validator_id__] = cls

    @abc.abstractmethod
    def validate_order(
        self,
        symbol: str,
        target_weight: float,
        current_holdings: dict[str, float],
        limits: dict,
    ) -> list[ViolationDetail]:
        """对单笔订单做 pre-trade 风控校验"""
        ...

    @abc.abstractmethod
    def validate_portfolio(
        self,
        holdings: dict[str, float],
        market_values: dict[str, float],
        total_nav: Decimal,
        limits: dict,
    ) -> list[ViolationDetail]:
        """对全组合做风控状态校验"""
        ...

    @staticmethod
    def is_kill_switch_triggered(violations: list[ViolationDetail]) -> bool:
        """判断是否应触发 kill_switch"""
        halt_violations = [v for v in violations if v.severity == "HALT"]
        return len(halt_violations) > 0


__all__ = [
    "RiskValidator",
    "ViolatedConstraint",
    "ViolationDetail",
]
