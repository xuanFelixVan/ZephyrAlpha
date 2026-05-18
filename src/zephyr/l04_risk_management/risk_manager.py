# [BLUEPRINT] MOD-L04-001 | 03_modules/l04_risk_management/risk-management-core/blueprint.md | §

# [MODULE] zephyr.l04_risk_management.risk_manager

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
# status: phase_b_skeleton
# created: "2026-05-05"
# ---
"""
ZephyrAlpha — L04 Risk Management Layer — 风控管理器接口

Phase B 骨架——定义风控层的公共接口。
跨层数据结构 MUST 仅来自 ``zephyr.shared.contracts``（SSoT）。

跨层契约：
  CTR-003  RiskLimits                  → L05（生产者——风险限额约束）
  CTR-ERR-004  RiskLimitViolationError  → L05, L06（硬错误——阻止交易）
  CTR-P1-008  RiskDashboardSnapshot     → L08（生产者——风险仪表板快照）
  CTR-P1-011  RiskMetricsReport         → L05, L07, L08, L10（生产者——风险指标）

SSoT: cross-layer-contracts.yaml v3.0
"""

from __future__ import annotations

import abc
from decimal import Decimal
from typing import ClassVar, Dict, List, Optional

from zephyr.trading_contracts.risk.risk_limit_violation_error import RiskLimitViolationError
from zephyr.trading_contracts.risk.risk_dashboard_snapshot import RiskDashboardSnapshot
from zephyr.trading_contracts.risk.risk_limits import RiskLimits
from zephyr.trading_contracts.risk.risk_metrics import RiskMetricsReport


class RiskManagerBase(abc.ABC):
    """
    风控管理器抽象基类（OCP 扩展点）

    职责：
      - 从上游信号/持仓计算当前风险敞口
      - 产出 RiskLimits 供给 L05 组合优化器
      - 产出 RiskDashboardSnapshot 供给 L08 监控面板
      - 产出 RiskMetricsReport 供给 L05/L07/L08/L10

    实现者要求：
      - validate_position(): 检查单仓位是否突破限额（返回 True = 合规）
      - check_portfolio(): 检查组合整体是否触发任何风控约束
      - generate_limits(): 产出当期 RiskLimits
      - idempotency_key（INV-007）：所有的风控检查操作必须关联幂等键
    """
    _registry: ClassVar[dict[str, type["RiskManagerBase"]]] = {}

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
        holdings: Dict[str, Decimal],
        market_values: Dict[str, Decimal],
        limits: RiskLimits,
    ) -> List[str]:
        """全组合范围风控检查。返回违规项列表，空列表 = 全合规。"""
        ...

    @abc.abstractmethod
    def generate_limits(self, portfolio_id: str) -> RiskLimits:
        """产出当期 RiskLimits。"""
        ...

    def snapshot(self, portfolio_id: str) -> Optional[RiskDashboardSnapshot]:
        """（可覆盖）产出风险仪表板快照。"""
        raise NotImplementedError(
            "snapshot() 需要子类实现——风控度量基础设施就绪后方可激活"
        )


__all__ = [
    "RiskLimits",
    "RiskLimitViolationError",
    "RiskDashboardSnapshot",
    "RiskMetricsReport",
    "RiskManagerBase",
]
