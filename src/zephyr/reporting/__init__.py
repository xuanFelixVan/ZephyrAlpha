# [A_module] module_id=MOD-UNK_reporting | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
"""D_REPORTING Post-Trade Analytics
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
"""

from __future__ import annotations

from zephyr.reporting.analytics_base import (
    AttributionEngineBase,
    TCAEngineBase,
)
from zephyr.shared.contracts.performance_attribution_report import PerformanceAttributionReport

__all__ = [
    "AttributionEngineBase",
    "PerformanceAttributionReport",
    "TCAEngineBase",
    "analytics_base",
    "default_attribution_engine",
    "default_tca_engine",
]
