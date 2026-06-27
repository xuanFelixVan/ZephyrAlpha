# [A_module] module_id=MOD-PRT_performance_attribution_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L07-001 | docs/03_modules/_domain-reporting/analytics-core/blueprint.md
# [MODULE] zephyr.pf_core
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""L07 Post-Trade Analytics
=====================================

14 层量化架构 · L07 盘后分析层

职责
----
盘后分析报告：PnL 归因、交易成本分析、执行质量评估、持仓风险评估。
[N/A — 骨架占位，尚未实现]

CTR 契约依赖声明（承重墙标记）
------------------------------
本层是以下跨层数据契约的来源或目标——Phase B 实现前 MUST 阅读对应 YAML 定义。
任何修改本层接口的行为 MUST 先通过 ContractImpactAnalyzer 评估影响范围。

作为消费者（Consumer）：
  - CTR-005  Fill                      ← L06
  - CTR-006  PositionSnapshot          ← L06
  - CTR-ERR-005  ExecutionRejectionError ← L06
  - CTR-P1-001  FactorMonitorReport    ← L02
  - CTR-P1-006  StrategyLifecycleEvent ← L05
  - CTR-P1-007  ExecutionReport        ← L06
  - CTR-P1-011  RiskMetricsReport      ← L04
  - CTR-P1-013  TelemetryEmitter       ← L12

作为生产者（Producer）：
  - CTR-P1-009  PerformanceAttributionReport → L08, L10

SSoT: cross_layer_contracts.yaml v3.0

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策： 目录双轨治理
"""

from __future__ import annotations

# MIGRATED: from zephyr.ops.analytics_base import (  # removed by TC-7-2
# AttributionEngineBase,  # removed by TC-7-2
# PerformanceAttributionReport,  # removed by TC-7-2
# TCAEngineBase,  # removed by TC-7-2
# )  # removed by TC-7-2
#
__all__ = ["AttributionEngineBase", "PerformanceAttributionReport", "TCAEngineBase", "analytics_base"]
#
