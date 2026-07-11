---
module_id: MOD-015
title: "Shared Infrastructure 蓝图 — 跨层共享基础设施"
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
actual_disk_path: "src/zephyr/shared/ (不含 contracts/)"
belongs_to: "MOD-INF-016"
summary: "跨层共享基础设施 — 14 子目录 ~115 文件，从 MOD-INF-016 拆分"
tags: [shared, infrastructure, cross-layer, event-bus, resilience, lifecycle, observability]
priority: P0
codification_level: L2
generation: 1
functional_domain: infrastructure
parent_module: "MOD-INF-016"
scope: global
stability: evolving
verifiability: hybrid
depends_on:
  - {target: "MOD-INF-016-CONTRACTS", at: "全篇", why: "Contracts — 所有 shared 组件消费 contracts 数据模型"}
responsibility_domain: 
design_maturity: design
build_status: stable
---

# Shared Infrastructure 蓝图 — 跨层共享基础设施

> module_id: MOD-015 | version: 0.1.0 | status: Active | layer: cross_layer
> actual_disk_path: src/zephyr/shared/ (不含 contracts/) | generation: 1 | construction_progress: completed
> parent: MOD-INF-016 (拆分自 Shared+Core 蓝图，AD-002 触发条件达成)

**核心职责**: 提供跨层共享基础设施——事件总线、配置管理、韧性组件、模块生命周期、可观测性、生产基础设施（缓存/限流/幂等/分布式锁/Outbox）、Schema 管理、安全守卫。

**负向责任**: 不涉及应用层业务逻辑 / 数据库 Schema 设计（→ MOD-DATABASE）/ 契约定义（→ MOD-INF-016-CONTRACTS）。

## §0 代码文件清单

| # | 子目录 | 文件数 | 关键文件 |
|---|--------|:---:|------|
| 1 | shared/ (root) | 43 | `schemas.py`, `observer.py`, `ssot_guard.py`, `paths.py`, `logging.py`, `testing.py`, `migration.py`, `deprecation.py`, `constants.py`, `errors.py`, `types.py`, `diff_utils.py`, `file_utils.py`, `flags.py`, `frontmatter_utils.py`, `token_utils.py`, `time_utils.py`, `health.py`, `API_INDEX.py`, `capability.py`, `content_fingerprint.py`, `dos_launcher.py`, `shared_quickref.yaml`, `contract_bus.py`, `event_bus.py`, `blueprint_scorer.py`, `__version__.py`, `tracing.py`, `serialization.py`, `api_client.py`, `secrets.py`, `cache.py`, `limiter.py`, `idempotency.py`, `context.py`, `metrics.py`, `pagination.py`, `env.py`, `lock.py`, `outbox.py`, `schema_registry.py`, `cost_budget.py`, `context_budget.py`, ... |
| 2 | api/ | 4 | `api_client`, `api_index`, `dos_launcher` |
| 3 | config/ | 2 | `loader` |
| 4 | events/ | 6 | `event_schemas`, `dlq`, `dlq_bridge`, `event_bus_upgrade`, `upgrade_strategy` |
| 5 | foundation/ | 7 | `constants`, `deprecation`, `env`, `errors`, `flags`, `types` |
| 6 | infra/ | 9 | `cache`, `idempotency`, `limiter`, `lock`, `observer`, `outbox`, `process_pool`, `process_lifecycle_gateway` |
| 7 | io/ | 8 | `content_fingerprint`, `file_utils`, `frontmatter_utils`, `io_cache`, `paths`, `serialization`, `streaming_reader` |
| 8 | lifecycle/ | 6 | `hooks`, `daemon_registry`, `lazy_loader`, `resource_optimization_engine`, `resource_optimization_models` |
| 9 | observability/ | 8 | `health`, `health_discovery`, `logging`, `metrics`, `token_utils`, `tracing`, `session_audit` |
| 10 | resilience/ | 4 | `circuit_breaker`, `fallback`, `retry` |
| 11 | schema/ | 5 | `schemas`, `schema_registry`, `base_config`, `severity_types` |
| 12 | security/ | 4 | `capability`, `secrets`, `ssot_guard` |
| 13 | utils/ | 9 | `context`, `db_utils`, `diff_utils`, `migration`, `pagination`, `testing`, `time_utils`, `blueprint_scorer` |
| 14 | (root orphans) | ~30 | `ai_audit_guard`, `alert_escalation`, `alert_manager`, `capacity_*`, `code_economy_analyzer`, `combinatorial_gate`, `config_validator`, `contract_tester`, `core_integrity_guard`, `cost_estimator`, `degradation_chain`, `dependency_capacity_guard`, `dual_channel_alert`, `error_budget_tracker`, `fault_isolator`, `heartbeat_server`, `kill_switch`, `longevity_monitor`, `model_capacity_probe`, `module_birth_registry`, `owner_trust_gauge`, `pydantic_v2_migrator`, `reasoning_spans`, `sandbox_executor`, `semantic_cache`, `slo_review_assistant`, `task_heartbeat`, `ttl_cleanup_engine`, `vibe_experiment_tracker`, `warm_hot_gate`, `zephyr_logger`, ... |

**总计**: ~115 个 .py 文件

## §1 核心子模块

| 子模块 | 职责 | 关键类/函数 |
|--------|------|------------|
| EventBus | 异步 Pub/Sub 事件分发 | `Observer`, `EventEmitter`, `DLQ` |
| ConfigCenter | YAML 配置加载 + Pydantic 校验 | `load_yaml_config()`, `ConfigLoader` |
| Resilience | 熔断/重试/降级 | `CircuitBreaker`, `async_retry`, `FallbackChain` |
| Lifecycle | 模块 init/startup/shutdown/health | `LifecycleAware`, `LifecycleManager` |
| FeatureFlags | AI 行为开关 | `FeatureFlag`, `FlagRegistry` |
| ProductionInfra | 缓存/限流/幂等/锁/Outbox | `TokenBucket`, `IdempotencyGuard`, `DistributedLock` |
| Observability | 结构化日志/Metrics/追踪 | `ZephyrLogger`, `MetricsRegistry`, `TraceContext` |
| SSoT Guard | 单一定义守卫 | `SSoTGuard` |
| Contracts Bus | 契约路由总线 | `ContractBus` |

## §2 消费者

所有 基础设施-实验 模块均直接消费 shared/ 基础设施。详见 MOD-INF-016 集成蓝图 §7 反向依赖索引。

## §3 关联

- 父蓝图: MOD-INF-016 (Shared+Core 集成蓝图)
- 兄弟蓝图: MOD-INF-016-CONTRACTS / MOD-INF-016-CORE
- SSoT 映射: `architecture_model/layers/b_shared.yaml`
