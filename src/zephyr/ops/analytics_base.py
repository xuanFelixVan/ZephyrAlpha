# [BLUEPRINT] MOD-L07-001 | docs/03_modules/_domain-reporting/analytics-core/blueprint.md
# [MODULE] zephyr.observability.analytics_base
# [DOMAIN] D-OPS
# [DEPENDENCIES] zephyr.trading.trading_contracts.execution.execution_report; zephyr.trading.trading_contracts.execution.fill; zephyr.trading.trading_contracts.execution.order; zephyr.governance.performance_attribution_report
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
# [A_module] module_id=MOD-UNK_analytics_base | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

# ---
# domain: reporting
# category: analytics_interface
# status: active
# created: "2026-05-05"
# ---

"""
L07 — Post-Trade Analytics Layer

盘后分析层。负责交易执行后的绩效评估与归因分析。

核心职责：
  - TCA（Transaction Cost Analysis）：成交回报 Fill → 执行分析报告 ExecutionReport
  - 绩效归因（Brinson）：持仓快照 + 因子暴露 → 归因报告 PerformanceAttributionReport
  - P&L 分解（方向性 vs 波动性收益）
  - 日终报告生成 → L08 Dashboard / L10 Compliance

扩展点：
  - TCAEngineBase        : OCP L07-TCA — Fill + Order → ExecutionReport
  - AttributionEngineBase : OCP L07-ATTR — PositionSnapshot → PerformanceAttributionReport

依赖方向：L06 → L07 → L08 / L09 / L10
"""

from __future__ import annotations

import abc
from typing import ClassVar

from zephyr.governance.performance_attribution_report import PerformanceAttributionReport
from zephyr.trading.trading_contracts.execution.execution_report import ExecutionReport
from zephyr.trading.trading_contracts.execution.fill import Fill
from zephyr.trading.trading_contracts.execution.order import Order


class TCAEngineBase(abc.ABC):
    """
    交易成本分析引擎（OCP 扩展点 L07-TCA）

    契约对齐：CTR-005（Fill 入站）+ CTR-004（Order 入站）→ CTR-P1-007（ExecutionReport 出站）

    实现者要求：
      - analyze(): 接收成交回报 Fill + 原委托 Order，计算滑点/佣金/TCA
      - slippage_bps = (vwap_price - intended_price) / intended_price × 10000
      - 所有价格字段使用 Decimal 类型
    """

    _registry: ClassVar[dict[str, type[TCAEngineBase]]] = {}

    @abc.abstractmethod
    def analyze(self, fill: Fill, order: Order, idempotency_key: str) -> ExecutionReport:
        """单笔成交的 TCA 分析，返回执行报告"""
        ...

    def analyze_batch(self, fills: list[Fill], orders: dict[str, Order], idempotency_key: str) -> list[ExecutionReport]:
        """批量成交分析（可选覆盖）"""
        raise NotImplementedError


class AttributionEngineBase(abc.ABC):
    """
    绩效归因引擎（OCP 扩展点 L07-ATTR）

    契约对齐：CTR-P1-009（PerformanceAttributionReport 出站）→ L08, L10

    实现者要求：
      - attribute(): 给定持仓和因子暴露，按 Brinson 模型拆解收益
      - total_return = allocation_effect + selection_effect + interaction_effect
    """

    _registry: ClassVar[dict[str, type[AttributionEngineBase]]] = {}

    @abc.abstractmethod
    def attribute(
        self, portfolio_id: str, period_start: str, period_end: str, idempotency_key: str
    ) -> PerformanceAttributionReport:
        """按期间归因分析，返回绩效归因报告"""
        ...


__all__ = [
    "AttributionEngineBase",
    "TCAEngineBase",
]
