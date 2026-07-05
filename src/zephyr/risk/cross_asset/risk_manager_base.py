# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain-risk/risk-management-core/blueprint.md
# [MODULE] zephyr.risk.cross_asset.risk_manager_base
# [DOMAIN] D_RISK
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_risk_manager_base | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: risk
# category: risk_interface
# status: active
# created: "2026-05-05"
# ---

"""
D_RISK — Risk Management Layer Skeleton

风险管理层抽象基类。定义事前/事后风控、限额检查、止损与熔断的核心接口。

OCP 扩展点：
  - RiskManagerBase            — 风险总管（事前 + 事后 + 熔断编排）
  - StopLossEngineBase         — 止损策略引擎
  - PositionLimitCheckerBase   — 仓位限额检查

依赖方向：
  消费者：CTR-002(FactorSignal) ← D_FACTOR, CTR-003(RiskLimits), CTR-004(Order), CTR-006(PositionSnapshot)
  生产者：CTR-003(RiskLimits) → D_PORTFOLIO_CORE, RiskDashboard → D_FRONTEND

INV-001: Kill Switch 延迟 < 1ms
INV-004: 每日亏损硬限
INV-007: 所有跨层调用携带 idempotency_key
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, ClassVar


@dataclass(frozen=True)
class RiskCheckResult:
    """单次风控检查结果"""

    check_id: str
    rule_name: str
    passed: bool
    limit_value: Decimal
    actual_value: Decimal
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    severity: str = "info"


@dataclass(frozen=True)
class RiskReport:
    """风控综合报告"""

    as_of_timestamp: datetime
    portfolio_id: str
    checks: list[RiskCheckResult] = field(default_factory=list)
    overall_pass: bool = True
    active_alerts: list[str] = field(default_factory=list)
    kill_switch_active: bool = False

    @property
    def failed_checks(self) -> list[RiskCheckResult]:
        return [c for c in self.checks if not c.passed]


class RiskManagerOrchestratorBase(abc.ABC):
    """风险总管（OCP 扩展点）

    实现者要求：
      - pre_trade_check(order): 事前风控——订单发出前检查限额
      - post_trade_check(fill): 事后风控——成交后检查风险敞口
      - daily_pnl_check(): 日终盈亏检查——触发 INV-004 硬限
      - aggregate_report(): 综合风控报告

    调用顺序：pre_trade → (emit order) → post_trade → daily_pnl → aggregate
    """

    _registry: ClassVar[dict[str, type[RiskManagerOrchestratorBase]]] = {}

    @abc.abstractmethod
    def pre_trade_check(self, order: Any, limits: Any, positions: Any) -> RiskCheckResult:
        """事前风控：订单级限额检查（CTR-003 + CTR-004）"""
        ...

    @abc.abstractmethod
    def post_trade_check(self, fill: Any, positions: Any) -> RiskCheckResult:
        """事后风控：成交后风险敞口检查（CTR-005 + CTR-006）"""
        ...

    @abc.abstractmethod
    def daily_pnl_check(self, daily_pnl: Decimal, loss_limit: Decimal) -> RiskCheckResult:
        """日终盈亏检查（INV-004：每日亏损硬限）"""
        ...

    @abc.abstractmethod
    def aggregate_report(self) -> RiskReport:
        """综合所有检查结果，生成统一风控报告"""
        ...


class StopLossEngineBase(abc.ABC):
    """止损策略引擎（OCP 扩展点）

    实现者要求：
      - evaluate(position, current_price, rules): 判断是否触发止损
      - 支持多种止损策略：固定比例 / 移动止损 / 时间止损 / 波动率止损
    """

    _registry: ClassVar[dict[str, type[StopLossEngineBase]]] = {}

    @abc.abstractmethod
    def evaluate(
        self, symbol: str, entry_price: Decimal, current_price: Decimal, position_qty: Decimal, rules: dict[str, Any]
    ) -> RiskCheckResult:
        """评估持仓是否触发止损条件"""
        ...

    @abc.abstractmethod
    def get_stop_price(self, symbol: str) -> Decimal | None:
        """返回当前止损价（None 表示无止损保护）"""
        ...


class PositionLimitCheckerBase(abc.ABC):
    """仓位限额检查器（OCP 扩展点）

    实现者要求：
      - check_single_position(symbol, weight, limit): 单仓限额
      - check_sector_concentration(sector, weight, limit): 行业集中度
      - check_gross_leverage(current, limit): 总杠杆
    """

    _registry: ClassVar[dict[str, type[PositionLimitCheckerBase]]] = {}

    @abc.abstractmethod
    def check_single_position(self, symbol: str, weight: float, limit: float) -> RiskCheckResult:
        """检查单仓是否超过权重上限"""
        ...

    @abc.abstractmethod
    def check_sector_concentration(self, sector: str, weight: float, limit: float) -> RiskCheckResult:
        """检查行业集中度"""
        ...

    @abc.abstractmethod
    def check_gross_leverage(self, current_leverage: float, limit: float) -> RiskCheckResult:
        """检查总杠杆"""
        ...


__all__ = [
    "PositionLimitCheckerBase",
    "RiskCheckResult",
    "RiskManagerOrchestratorBase",
    "RiskReport",
    "StopLossEngineBase",
]
