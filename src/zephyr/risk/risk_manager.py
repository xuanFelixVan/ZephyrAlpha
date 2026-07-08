# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain-risk/risk-management-core/blueprint.md
# [MODULE] zephyr.risk.risk_manager
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.trading.trading_contracts.risk.risk_limit_violation_error; zephyr.trading.trading_contracts.risk.risk_dashboard_snapshot; zephyr.shared.contracts.risk_limits; zephyr.trading.trading_contracts.risk.risk_metrics
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_risk_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: risk
# category: risk_interface
# status: phase_b_skeleton
# created: "2026-05-05"
# ---
"""
ZephyrAlpha — D_RISK Risk Management Layer — 风控管理器接口

Phase B 骨架——定义风控层的公共接口。
跨层数据结构 MUST 仅来自 ``zephyr.shared.contracts``（SSoT）。

跨层契约：
  CTR-003  RiskLimits                  -> D_PORTFOLIO_CORE（生产者——风险限额约束）
  CTR-ERR-004  RiskLimitViolationError  -> D_PORTFOLIO_CORE, D_EXECUTION_CORE（硬错误——阻止交易）
  CTR-P1-008  RiskDashboardSnapshot     -> D_FRONTEND（生产者——风险仪表板快照）
  CTR-P1-011  RiskMetricsReport         -> D_PORTFOLIO_CORE, D_REPORTING, D_FRONTEND, D_COMPLIANCE（生产者——风险指标）

SSoT: cross_layer_contracts.yaml v3.0
"""

from __future__ import annotations

import abc
from decimal import Decimal
from typing import ClassVar

from zephyr.trading.trading_contracts.risk.risk_dashboard_snapshot import RiskDashboardSnapshot
from zephyr.trading.trading_contracts.risk.risk_limit_violation_error import RiskLimitViolationError
from zephyr.shared.contracts.risk_limits import RiskLimits
from zephyr.trading.trading_contracts.risk.risk_metrics import RiskMetricsReport


class RiskManagerBase(abc.ABC):
    """
    风控管理器抽象基类（OCP 扩展点）

    职责：
      - 从上游信号/持仓计算当前风险敞口
      - 产出 RiskLimits 供给 D_PORTFOLIO_CORE 组合优化器
      - 产出 RiskDashboardSnapshot 供给 D_FRONTEND 监控面板
      - 产出 RiskMetricsReport 供给 D_PORTFOLIO_CORE/D_REPORTING/D_FRONTEND/D_COMPLIANCE

    实现者要求：
      - validate_position(): 检查单仓位是否突破限额（返回 True = 合规）
      - check_portfolio(): 检查组合整体是否触发任何风控约束
      - generate_limits(): 产出当期 RiskLimits
      - idempotency_key（INV-007）：所有的风控检查操作必须关联幂等键
    """

    _registry: ClassVar[dict[str, type[RiskManagerBase]]] = {}

    @abc.abstractmethod
    def validate_position(
        self,
        symbol: str,
        weight: float,
        limits: RiskLimits,
    ) -> bool:
        """校验单标的权重是否合规。不通过时抛出 RiskLimitViolationError。"""
        ...

    @abc.abstractmethod
    def check_portfolio(
        self,
        holdings: dict[str, Decimal],
        market_values: dict[str, Decimal],
        limits: RiskLimits,
    ) -> list[str]:
        """全组合范围风控检查。返回违规项列表，空列表 = 全合规。"""
        ...

    @abc.abstractmethod
    def generate_limits(self, portfolio_id: str) -> RiskLimits:
        """产出当期 RiskLimits。"""
        ...

    def snapshot(self, portfolio_id: str) -> RiskDashboardSnapshot | None:
        """（可覆盖）产出风险仪表板快照。"""
        raise NotImplementedError("snapshot() 需要子类实现——风控度量基础设施就绪后方可激活")


__all__ = [
    "RiskDashboardSnapshot",
    "RiskLimitViolationError",
    "RiskLimits",
    "RiskManagerBase",
    "RiskMetricsReport",
]
