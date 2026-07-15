---
module_id: MOD-INF-016
title: "Shared Contracts 蓝图 — 跨层数据契约 SSoT"
doc_type: blueprint
status: Active
version: "0.1.0"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent_session-20260519-001
date: "2026-05-18"
last_updated: "2026-05-18"
valid_from: "2026-05-18"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/shared/contracts/"
belongs_to: "MOD-INF-016"
summary: "跨层数据契约 SSoT — 11 子域 64 文件，从 MOD-INF-016 拆分"
tags: [contracts, shared, cross-layer, ssot, pydantic-v2]
priority: P0
codification_level: L2
generation: 1
functional_domain: data
parent_module: "MOD-INF-016"
scope: global
stability: stable
verifiability: hybrid
depends_on:
  - {target: "MOD-INF-016-SHARED", at: "全篇", why: "Shared Infrastructure — BaseEvent/schemas 基类依赖"}
responsibility_domain: 
design_maturity: design
build_status: planned
---

# Shared Contracts 蓝图 — 跨层数据契约 SSoT

> module_id: MOD-013 | version: 0.1.0 | status: Active | layer: cross_layer
> actual_disk_path: src/zephyr/shared/contracts/ | generation: 1 | construction_progress: partially_implemented
> parent: MOD-INF-016 (拆分自 Shared+Core 蓝图，AD-002 触发条件达成)

**核心职责**: 定义跨层传递的 Pydantic V2 数据模型，作为所有 基础设施-实验 模块的契约 SSoT。

**负向责任**: 不涉及业务逻辑 / 数据库操作 / 基础设施实现。

## §0 代码文件清单

| # | 子域 | 文件数 | 说明 |
|---|------|:---:|------|
| 1 | contracts/core/ | 10 | 核心契约——BaseEvent / Timestamp / RuntimePlaneTag / Enforcer / GateTypes / Registry / SystemConfiguration / TelemetryEmitter / TraceContext（Factories已迁移至trading_contracts/） |
| 2 | contracts/market/ | 7 | 市场数据契约——Instrument / MarketData / FactorSignal / MacroFactorSignal / SynthesizedSignal / FactorMonitorReport |
| 3 | contracts/portfolio/ | 5 | 组合管理契约——Money / Position / PerformanceAttributionReport / StrategyLifecycleEvent |
| 4 | contracts/execution/ | 6 | 执行契约——Order / Fill / ExecutionReport / CapitalAllocationResult / ModelServingRequest |
| 5 | contracts/risk/ | 6 | 风险管理契约——RiskMetrics / RiskLimits / ComplianceRule / RiskDashboardSnapshot / RiskValidatorProtocol |
| 6 | contracts/errors/ | 4 | 错误契约——ContractViolationError / DataQualityError / FactorComputationError（ExecutionRejectionError/RiskLimitViolationError/SignalDegradationWarning已迁移至trading_contracts/） |
| 7 | contracts/experiment/ | 3 | 实验契约——ExperimentResult / ModelServingResponse |
| 8 | contracts/external/ | 5 | 外部接口契约——ext_001~004 |
| 9 | contracts/escalation/ | 2 | 升级契约——BudgetAlert |
| 10 | contracts/gate/ | 2 | 门禁契约——GateResult |
| 11 | contracts/identity/ | 3 | 身份契约——AgentIdentity / Permission |
| 12 | contracts/backpressure/ | 4 | 背压契约——Pause / Resume / Throttle |
| 13 | contracts/security/ | 2 | 安全契约——SecurityDecision |

**总计**: 57 个 .py 文件 + 1 个 __init__.py = 58 文件（DW-261迁移6个至trading_contracts/）

## §1 消费者

| 模块 | 消费的契约 | 用途 |
|------|---------|------|
| MOD-INF-011 (ML Platform) | ModelServingRequest/Response, ExperimentResult | ML 推理与实验 |
| MOD-DATABASE (Signal Gen) | MarketData, FactorSignal, MacroFactorSignal, FactorMonitorReport | 信号生成 |
| MOD-INF-013 (Risk Mgmt) | RiskMetrics, RiskLimits, RiskDashboardSnapshot | 风险管理 |
| MOD-LLM_SECURITY (Portfolio) | Position, PerformanceAttributionReport, CapitalAllocationResult | 组合管理 |
| MOD-INF-015 (Execution) | Order, Fill, ExecutionReport, ExecutionRejectionError | 交易执行 |
| MOD-INF-016 (Compliance) | ComplianceRule, ContractViolationError | 合规检查 |

## §2 架构惯例

- 所有模型 MUST 继承 `pydantic.BaseModel`
- 所有模型 MUST 使用 `frozen=True` (不可变)
- 字段类型 MUST 使用 Python 原生类型 + Pydantic 约束注解
- 跨模块传递 MUST 通过 `model_dump()` / `model_validate()` 序列化

## §3 关联

- 父蓝图: MOD-INF-016 (Shared+Core 集成蓝图)
- 兄弟蓝图: MOD-INF-016-SHARED / MOD-INF-016-CORE
- SSoT 映射: `architecture_model/layers/b_shared.yaml`
