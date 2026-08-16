# [A_module] module_id=MOD-UNK-reporting | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L07-001 | docs/03_modules/_domain_reporting/blueprint.md
# [MODULE] zephyr.reporting
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""

D_REPORTING Post-Trade Analytics
=====================================

14 层量化架构 · D_REPORTING 盘后分析层

职责
----
盘后分析报告：PnL 归因、交易成本分析、执行质量评估、持仓风险评估。
[N/A — 骨架占位，尚未实现]

CTR 契约依赖声明（承重墙标记）
------------------------------
本层是以下跨层数据契约的来源或目标——Phase B 实现前 MUST 阅读对应 YAML 定义。
任何修改本层接口的行为 MUST 先通过 ContractImpactAnalyzer 评估影响范围。

作为消费者（Consumer）：
  - CTR-005  Fill                      ← D_EXECUTION_CORE
  - CTR-006  PositionSnapshot          ← D_EXECUTION_CORE
  - CTR-ERR-005  ExecutionRejectionError ← D_EXECUTION_CORE
  - CTR-P1-001  FactorMonitorReport    ← D_FACTOR
  - CTR-P1-006  StrategyLifecycleEvent ← D_PORTFOLIO_CORE
  - CTR-P1-007  ExecutionReport        ← D_EXECUTION_CORE
  - CTR-P1-011  RiskMetricsReport      ← D_RISK
  - CTR-P1-013  TelemetryEmitter       ← 遥测

作为生产者（Producer）：
  - CTR-P1-009  PerformanceAttributionReport -> D_FRONTEND, D_GOV_ENFORCEMENT

SSoT: cross_layer_contracts.yaml v3.0

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策： 目录双轨治理

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 成交回报 Fill 契约数据
#   fields: fill_price/filled_quantity/commission/fill_timestamp（CTR-005 ← D_EXECUTION_CORE）
#   code: zephyr.shared.contracts.fill（__init__.py docstring L29 契约声明）
# - id: I2
#   name: 关联委托 Order 契约数据
#   fields: limit_price/quantity/side（CTR-004 委托单）
#   code: zephyr.shared.contracts.order（analytics_base.py L51 import）
# - id: I3
#   name: 持仓快照 PositionSnapshot 契约数据
#   fields: 持仓历史（CTR-006 ← D_EXECUTION_CORE）
#   code: __init__.py docstring L30 契约声明
# 层: 算法
# - id: A1
#   name_zh: ① TCA交易成本分析引擎
#   name_en: TCAEngineBase / DefaultTCAEngine
#   intro: 拿成交回报对比委托限价，算滑点bps和佣金，出执行分析报告
#   desc: 抽象基类定扩展点（analytics_base.py L54-75）；默认实现 slippage_bps=(fill_price-intended_price)/intended_price×10000，银行家舍入取整数量（default_tca_engine.py L60-88）
#   inputs: I1 I2
#   outputs: ExecutionReport（CTR-P1-007）
# - id: A2
#   name_zh: ② Brinson绩效归因引擎（骨架占位）
#   name_en: AttributionEngineBase / DefaultAttributionEngine
#   intro: 持仓快照做Brinson三因子分解出归因报告，但三个效应计算器目前都返回0.0
#   desc: 抽象基类定扩展点（analytics_base.py L78起）；默认实现 attribute() 汇总 allocation+selection+interaction（default_attribution_engine.py L57-80），但_calc_allocation/selection/interaction_effect 均 return 0.0 骨架占位（L82-92）
#   inputs: I3
#   outputs: PerformanceAttributionReport（CTR-P1-009，效应值全0）
#   is_break: true
# 层: 输出
# - id: O1
#   name_zh: 执行分析报告 ExecutionReport
#   name_en: execution report
#   intro: 单笔成交的滑点/佣金/执行质量报告
#   downstream: D_FRONTEND Dashboard + D_GOV_ENFORCEMENT 合规（CTR-P1-007 契约声明）
# - id: O2
#   name_zh: 绩效归因报告 PerformanceAttributionReport
#   name_en: performance attribution report
#   intro: Brinson配置/选择/交互三效应归因报告（当前为0值骨架）
#   downstream: D_FRONTEND + D_GOV_ENFORCEMENT（CTR-P1-009 契约声明）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 -.->|断点| A2
# A1 --> O1
# A2 --> O2
"""

from __future__ import annotations

from zephyr.reporting.analytics_base import (
    AttributionEngineBase,
    TCAEngineBase,
)
from zephyr.reporting.review_orchestrator import (
    DailyReviewResult,
    MonthlyReviewResult,
    ReviewOrchestrator,
    WeeklyReviewResult,
)
from zephyr.shared.contracts.performance_attribution_report import PerformanceAttributionReport

__all__ = [
    "AttributionEngineBase",
    "DailyReviewResult",
    "MonthlyReviewResult",
    "PerformanceAttributionReport",
    "ReviewOrchestrator",
    "TCAEngineBase",
    "WeeklyReviewResult",
    "analytics_base",
    "default_attribution_engine",
    "default_tca_engine",
    "review_orchestrator",
]
