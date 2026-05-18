# [BLUEPRINT] MOD-L05-001 | 03_modules/l05_portfolio_construction/portfolio-core/blueprint.md | §
"""L05 Portfolio Construction
=====================================

14 层量化架构 · L05 组合构建层

职责
----
组合优化与订单生成：接收信号与风控约束，生成目标权重并转化为委托指令列表。

子模块
------
- strategy_base.py     : StrategyBase + StrategyMeta（OCP-002 扩展点）
- strategy_registry.py : StrategyRegistry（策略注册与自动发现）

CTR 契约依赖声明（承重墙标记）
------------------------------
本层是以下跨层数据契约的来源或目标。任何修改本层接口的行为 MUST 先通过 ContractImpactAnalyzer 评估影响范围。

作为消费者（Consumer）：
  - CTR-002  FactorSignal              ← L02
  - CTR-003  RiskLimits                ← L04
  - CTR-ERR-003  SignalDegradationWarning ← L03
  - CTR-ERR-004  RiskLimitViolationError  ← L04
  - CTR-ERR-005  ExecutionRejectionError  ← L06
  - CTR-P1-003  CapitalAllocationResult   ← L03
  - CTR-P1-004  ModelServingRequest       ← L11
  - CTR-P1-005  ModelServingResponse      ← L11
  - CTR-P1-011  RiskMetricsReport         ← L04
  - CTR-P1-015  SynthesizedSignal         ← L03

作为生产者（Producer）：
  - CTR-004  Order                      → L06
  - CTR-P1-006  StrategyLifecycleEvent  → L07, L10

作为全局配置消费者（Consumer）：
  - CTR-P1-010  SystemConfiguration    ← L01
  - CTR-P1-013  TelemetryEmitter       ← L12

SSoT: cross-layer-contracts.yaml v3.0

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策：ADR-0022 目录双轨治理
"""

# CODEGEN-GUARD: CTR-declarations-manual
# DO NOT regenerate: CTR declarations are manually curated SSoT annotations

from .strategy_base import *  # noqa: F403
from .strategy_registry import *  # noqa: F403

__all__ = ['strategy_base', 'strategy_registry']

