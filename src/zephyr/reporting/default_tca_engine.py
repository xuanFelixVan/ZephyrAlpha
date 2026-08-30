# [BLUEPRINT] MOD-L07-001 | docs/03_modules/_domain_reporting/blueprint.md
# [MODULE] zephyr.reporting.default_tca_engine
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.reporting.analytics_base; zephyr.shared.contracts.execution_report; zephyr.shared.contracts.fill; zephyr.shared.contracts.order
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] IS=commission+spread+market_impact+timing_risk四桶分解;DECISION基准(决策价)为主滑点基准;BUY正=买贵成本/SELL正=卖便宜成本
# [MODIFY-GUARD] 40_execution_broker.md §2.4 决策③
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L07-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: Fill(成交回报: fill_price/filled_quantity/commission/fill_timestamp) + Order(原始委托: limit_price/quantity/side)
# I2: benchmark_price_source(DECISION/ARRIVAL/VWAP/TWAP/PREV_CLOSE，默认DECISION)
# F1: _calc_slippage_bps(方向感知滑点: BUY=(fill-intended)/intended, SELL=(intended-fill)/intended, ×10000)
# F2: _calc_is_decomposition(IS四桶: commission+spread+market_impact+timing_risk)
# A1: analyze(单笔TCA: 滑点+佣金+IS四桶分解→ExecutionReport)
# A2: analyze_batch(批量TCA: 逐笔analyze→list[ExecutionReport])
# O1: ExecutionReport(slippage_bps/commission/is_decomposition/algo_type)
# [/ALGO_FLOW]

# ---
# domain: reporting
# category: analytics_implementation
# status: active
# created: "2026-05-05"
# ---

"""
D_REPORTING — Default TCA Engine

交易成本分析引擎具体实现。成交回报 -> 执行分析报告。

CTR 契约：
  消费者 — CTR-005 (Fill) ← D_EXECUTION_CORE
  消费者 — CTR-004 (Order) ← D_PORTFOLIO_CORE（关联委托）
  生产者 — CTR-P1-007 (ExecutionReport) -> D_FRONTEND, D_GOV_ENFORCEMENT

SSoT: cross_layer_contracts.yaml -> CTR-005 + CTR-P1-007

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: benchmark_price_source 参数
#   fields: 参数 benchmark_price_source（无注解）
#   code: default_tca_engine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① DefaultTCAEngine
#   name_en: DefaultTCAEngine
#   intro: 默认 TCA 引擎——滑点/佣金/冲击成本分析
#   desc: 默认 TCA 引擎——滑点/佣金/冲击成本分析；公共方法（定义序）: analyze, analyze_batch；源码 L88-L203
#   inputs: benchmark_price_source
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: DefaultTCAEngine
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from decimal import ROUND_HALF_EVEN, Decimal

from zephyr.reporting.analytics_base import TCAEngineBase
from zephyr.shared.contracts.execution_report import ExecutionReport
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order

_logger = logging.getLogger(__name__)

__tca_id__ = "default-tca-engine"


class DefaultTCAEngine(TCAEngineBase):
    """默认 TCA 引擎——滑点/佣金/冲击成本分析"""

    __tca_id__ = __tca_id__

    def __init__(self, benchmark_price_source: str = "decision"):
        self._benchmark_source = benchmark_price_source

    def analyze(self, fill: Fill, order: Order, idempotency_key: str) -> ExecutionReport:
        intended_price = order.limit_price or Decimal("100")
        fill_price = fill.fill_price

        # 方向感知滑点（40_execution_broker §2.4 决策③）
        # BUY 正 = 买贵了 = 成本 / SELL 正 = 卖便宜了 = 成本
        slippage_bps = self._calc_slippage_bps(fill_price, intended_price, order.side)

        commission = fill.commission or Decimal("0")

        direction = "BUY" if (order.side and order.side.name == "BUY") else "SELL"

        # IS 4 桶分解（40_execution_broker §2.4 决策③）
        is_decomposition = self._calc_is_decomposition(fill, order, slippage_bps)

        return ExecutionReport(
            order_id=order.order_id,
            symbol=fill.symbol,
            direction=direction,
            # 5.105.3 修复: int(Decimal) 向零截断而非四舍五入,执行报告数量被低估
            # 改用 to_integral_value(rounding=ROUND_HALF_EVEN) 银行家舍入
            intended_quantity=int(order.quantity.to_integral_value(rounding=ROUND_HALF_EVEN)),
            actual_quantity=int(fill.filled_quantity.to_integral_value(rounding=ROUND_HALF_EVEN)),
            intended_price=intended_price,
            vwap_price=fill.fill_price,
            slippage_bps=float(slippage_bps),
            commission=commission,
            execution_start=fill.fill_timestamp.isoformat() if fill.fill_timestamp else "",
            execution_end=fill.fill_timestamp.isoformat() if fill.fill_timestamp else "",
            broker_id=fill.broker_fill_id or "unknown",
            idempotency_key=idempotency_key,
        )

    def analyze_batch(
        self,
        fills: list[Fill],
        orders: dict[str, Order],
        idempotency_key: str,
    ) -> list[ExecutionReport]:
        reports = []
        for fill in fills:
            order = orders.get(fill.order_id)
            if order:
                report = self.analyze(fill, order, idempotency_key)
                reports.append(report)
        _logger.info("Batch TCA: %d fills -> %d reports", len(fills), len(reports))
        return reports

    def _calc_slippage_bps(
        self,
        fill_price: Decimal,
        intended_price: Decimal,
        side: object,
    ) -> Decimal:
        """方向感知滑点计算（40_execution_broker §2.4 决策③）。

        BUY 正 = 买贵了 = 成本 / SELL 正 = 卖便宜了 = 成本。
        """
        if intended_price <= 0:
            return Decimal("0")
        raw = (fill_price - intended_price) / intended_price * Decimal("10000")
        # SELL 侧取反：卖便宜了 → (intended - fill) / intended > 0
        if side and getattr(side, "name", "") == "SELL":
            return -raw
        return raw

    def _calc_is_decomposition(
        self,
        fill: Fill,
        order: Order,
        slippage_bps: Decimal,
    ) -> dict[str, Decimal]:
        """IS 4 桶分解（40_execution_broker §2.4 决策③，Perold 1988）。

        IS = commission + spread + market_impact + timing_risk
        当前 MVP 口径：
          - commission: 券商佣金+印花税+过户费（Fill.commission 已含）
          - spread: half-spread 估计（MVP 用 0，Phase 1.5 接盘口数据）
          - market_impact: 市场冲击（MVP 归入 slippage_bps 总额）
          - timing_risk: 时机风险 = slippage_bps - market_impact（MVP 为残差）

        Phase 1.5 应将 delay cost 从 timing_risk 独立报告（Plexus: delay 占 IS 54%）。
        """
        commission = fill.commission or Decimal("0")
        # MVP: spread 无法从 Fill 获取，置 0；Phase 1.5 接盘口 half-spread
        spread = Decimal("0")
        # MVP: market_impact 归入总 slippage，timing_risk 为残差
        market_impact = slippage_bps  # 简化：全部滑点视为冲击
        timing_risk = slippage_bps - market_impact  # 残差（MVP=0）

        return {
            "commission": commission,
            "spread": spread,
            "market_impact": market_impact,
            "timing_risk": timing_risk,
            "total_is_bps": slippage_bps,
        }

    def _calc_shortfall(self, fill: Fill, order: Order) -> Decimal:
        """计算 Implementation Shortfall（DECISION 基准）"""
        decision_price = order.limit_price or Decimal("0")
        if decision_price == 0:
            return Decimal("0")

        fill_value = fill.filled_quantity * fill.fill_price
        paper_value = fill.filled_quantity * decision_price

        return (paper_value - fill_value - (fill.commission or Decimal("0"))) / paper_value


__all__ = ["DefaultTCAEngine"]
