---
module_id: MOD-014
title: "Governance Core 蓝图 — 治理核心模块"
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
construction_progress: completed
actual_disk_path: "src/zephyr/core/"
belongs_to: "MOD-INF-016"
summary: "治理核心模块 — 16 子目录 64 文件，从 MOD-INF-016 拆分"
tags: [core, governance, session-continuity, blueprint-decomposer, event-bus, lifecycle]
priority: P0
codification_level: L2
generation: 1
functional_domain: governance
parent_module: "MOD-INF-016"
scope: global
stability: evolving
verifiability: hybrid
depends_on:
  - {target: "MOD-INF-016-CONTRACTS", at: "全篇", why: "Contracts — core/models.py 继承 shared/schemas.py"}
  - {target: "MOD-INF-016-SHARED", at: "全篇", why: "Shared Infra — core/ 消费 event_bus/lifecycle/observer 等共享组件"}
responsibility_domain: 
design_maturity: production
build_status: generated
---

# Governance Core 蓝图 — 治理核心模块

> module_id: MOD-014 | version: 0.1.0 | status: Active | layer: cross_layer
> actual_disk_path: src/zephyr/core/ | generation: 1 | construction_progress: completed
> parent: MOD-INF-016 (拆分自 Shared+Core 蓝图，AD-002 触发条件达成)

**核心职责**: AI 治理核心——蓝图分解、会话连续性、任务生命周期管理、事件总线、影响分析、知识图谱接口、自适应调优、可靠性保障。

**负向责任**: 不涉及数据契约定义（→ MOD-INF-016-CONTRACTS）/ 不涉及通用基础设施（→ MOD-INF-016-SHARED）。

## §0 代码文件清单

| # | 子目录 | 文件数 | 关键文件 |
|---|--------|:---:|------|
| 1 | core/ (root) | 7 | `blueprint_decomposer`, `models`, `context_engine`, `healthcheck_service`, `session_continuity`, `blueprint_code_sync` |
| 2 | adaptation/ | 3 | `execution_tuner`, `prompt_version_manager` |
| 3 | compensation/ | 2 | `saga_compensator` |
| 4 | dependency/ | 2 | `dependency_graph` |
| 5 | draft/ | 2 | `draft_assistant` |
| 6 | events/ | 5 | `event_bus`, `event_reactor`, `event_store`, `hook_dispatcher` |
| 7 | impact/ | 3 | `impact_propagator`, `llm_impact_analyzer` |
| 8 | knowledge/ | 4 | `ke_linker`, `ke_structurer`, `kms_interface` |
| 9 | lifecycle/ | 8 | `daemon_registry`, `hooks`, `lazy_loader`, `resource_optimization_engine`, `resource_optimization_models`, `scope_guard`, `task_lifecycle_manager` |
| 10 | maintenance/ | 5 | `autonomy_monitor`, `dogfooding`, `handbook`, `zero_config` |
| 11 | observability/ | 6 | `cli_summary`, `cost_tracker`, `failure_matcher`, `notifier`, `trace_decorator` |
| 12 | quality/ | 2 | `quality_monitor` |
| 13 | queue/ | 3 | `task_queue`, `task_scheduler` |
| 14 | reliability/ | 5 | `circuit_breaker`, `context_guard`, `diff_planner`, `retry_handler` |
| 15 | session/ | 3 | `session_boundary`, `session_continuity` |
| 16 | sla/ | 2 | `sla_monitor` |
| 17 | sync/ | 2 | `blueprint_code_sync` |

**总计**: 64 个 .py 文件

## §1 核心子模块

| 子模块 | 职责 | 关键类 |
|--------|------|--------|
| BlueprintDecomposer | 蓝图 AST 分解 + 依赖图生成 | `BlueprintDecomposer` |
| SessionContinuity | AI session 跨轮次上下文恢复 | `SessionContinuity` |
| TaskLifecycle | 任务状态机管理 (10 状态) | `TaskLifecycleManager` |
| CoreEventBus | 核心事件总线 (AsyncIO 原生) | `EventBus`, `EventReactor` |
| DependencyGraph | 模块依赖图生成 | `DependencyGraph` |
| ImpactPropagator | 变更影响传播分析 | `ImpactPropagator` |
| QualityMonitor | 代码质量监控 | `QualityMonitor` |
| Reliability | 核心可靠性保障 | `CircuitBreaker`, `ContextGuard`, `DiffPlanner`, `RetryHandler` |

## §2 消费者

| 模块 | 消费的组件 | 用途 |
|------|---------|------|
| MOD-INF-035 (AutoRuntime) | SessionContinuity, EventBus | 大脑调度 |
| MOD-INF-009 (Pipeline) | TaskLifecycleManager | 管线编排 |
| MOD-GATE_ENGINE (Gate Engine) | BlueprintDecomposer | 蓝图门禁 |
| MOD-DATABASE (Database) | models.py (Task) | 持久化 |

## §3 关联

- 父蓝图: MOD-INF-016 (Shared+Core 集成蓝图)
- 兄弟蓝图: MOD-INF-016-CONTRACTS / MOD-INF-016-SHARED
- SSoT 映射: `architecture_model/layers/b_core.yaml`
