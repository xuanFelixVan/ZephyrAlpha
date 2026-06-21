---
module_id: KE-1410
status: active
title: 1.3 与 Shared Core (MOD-INF-016) 的承载关系
category: module_blueprint
---

# 1.3 与 Shared Core (MOD-INF-016) 的承载关系

1.3 与 Shared Core (MOD-INF-016) 的承载关系

> **v3.0.0 新增**：MOD-INF-016 Shared Core（v0.14.0，49文件，施工completed）已实现大量RI模块的代码承载。下表声明明确的职责分工。

| RI 模块 | 蓝图设计归属 | 代码承载归属 | 承载文件 | 备注 |
|---------|:--:|:--:|------|------|
| RI-01 EventBus | MOD-INF-002 | **MOD-INF-016** | `shared/observer.py` + `shared/events/` + `shared/events/dlq.py` | shared 版为基类实现；MOD-INF-002 蓝图定义增强需求（PriorityQueue/背压传导链），在 shared 层扩展 |
| RI-02 ModuleLifecycle | MOD-INF-002 | **MOD-INF-016** | `shared/lifecycle/hooks.py` | shared 版定义 LifecycleAware Protocol；MOD-INF-002蓝图扩展优雅关闭协议+预热期 |
| RI-03 ConfigCenter | MOD-INF-002 | **MOD-INF-016** | `shared/config/` + `shared/flags.py` | shared 版提供加载+校验+FeatureFlag；MOD-INF-002蓝图定义渐进推出+交互矩阵 |
| RI-04 DependencyInjector | MOD-INF-002 | **MOD-INF-016** (planned) | `shared/production/di_container.py` (待施工) | 统一由 shared 承载，不做独立 `infra_ops/dependency_injector.py` |
| RI-05 ResilienceGuard | MOD-INF-002 | **MOD-INF-016** | `shared/resilience/` | shared 版提供 CircuitBreaker/Retry/Fallback；MOD-INF-002蓝图扩展Bulkhead/LoadShedder/RetryBudget |
| RI-06 IdempotencyGuard | MOD-INF-002 | **MOD-INF-016** | `shared/production/idempotency.py` | shared 版为基础实现；MOD-INF-002蓝图定义TTL分级策略 |
| RI-07 SecretsManager | MOD-INF-002 | **MOD-INF-016** | `shared/production/secrets.py` | — |
| RI-08 ErrorHandler | MOD-INF-002 | **MOD-INF-016** | `shared/errors.py` + `shared/logging.py` | shared 版提供异常树+trace_id；MOD-INF-002蓝图扩展W3C Trace Context |
| RI-09 HealthCheck | MOD-INF-002 | **MOD-INF-016** | `shared/health.py` | shared 版提供 AggregateHealth；MOD-INF-002蓝图定义具体SLI阈值+Reconciliation |
| RI-10 TelemetryCollector | MOD-INF-002 | **MOD-INF-016** | `shared/production/metrics.py` | shared 版提供基础metrics；MOD-INF-002蓝图扩展PromptFingerprint+DeadModuleDetector |
| RI-11 CacheLayer | MOD-INF-002 | **MOD-INF-016** | `shared/production/cache.py` | shared 版为基础实现；MOD-INF-002蓝图扩展Data Locality |
| RI-12 AutoDiagnostics | MOD-INF-002 | **独立落地** | `infra_ops/auto_diagnostics.py` | 共享核心无对应实现——100%新施工 |
| RI-13 EventStore | MOD-INF-002 | **独立落地** | `infra_ops/event_store.py` | 共享核心无对应实现——Phase 3 触发式落地 |
| RI-14 DryRunSimulator | MOD-INF-002 | **独立落地** | `infra_ops/dry_run_simulator.py` | 共享核心无对应实现——Phase 2b |
| RI-15 CostTracker | MOD-INF-002 | **独立落地** | `infra_ops/cost_tracker.py` | 共享核心无对应实现——Phase 2b |

> **职责准则**：MOD-INF-002 定义"运行时集成体系需要什么"（WHAT + WHY），MOD-INF-016 承载"公共实现"（HOW）。若 shared 版已足够，RI 模块直接消费 shared；若需要增强，在 shared 层扩展而非独立重写。仅 RI-12/13/14/15 因 shared 无对应能力，独立落地 `infra_ops/`。

---
