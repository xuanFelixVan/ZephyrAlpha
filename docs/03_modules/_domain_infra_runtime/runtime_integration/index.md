---
doc_type: index
status: active
title: "runtime_integration — 目录索引"
module_id: MOD-INF-002
blueprint_id: MOD-INF-002
version: "6.1.1"
created: "2026-05-01"
updated: "2026-06-22"
ttl: permanent
---

# runtime_integration

> 本文件由 `generate_missing_index_md.py` 自动生成（后经手动校正）
> 生成日期：2026-06-22

## 责任声明（Single Responsibility）

本目录存放：**L01 infrastructure 层 / infra 功能域 — Runtime Integration 模块蓝图**。
代码承载分布在 `src/zephyr/shared/` + `src/zephyr/infrastructure/` + `src/zephyr/governance/lifecycle_manager/`。

## 模块概览

| 维度 | 详情 |
|------|------|
| 蓝图路径 | [blueprint.md](./blueprint.md) |
| 蓝图版本 | v6.1.1 |
| 代码承载 | `src/zephyr/shared/` + `src/zephyr/infrastructure/` + `src/zephyr/governance/lifecycle_manager/` |
| 功能域 | infra |
| 层级 | L01 infrastructure |
| 施工进度 | completed |
| 父模块 | MOD-MASTER_BLUEPRINT |

## 15 核心 RI 模块（与 MOD-INF-016 Shared Core 承载关系）

| RI 模块 | 代码承载 | 承载文件 |
|---------|:---:|------|
| RI-01 EventBus | **MOD-INF-016** | `shared/observer.py` + `shared/events/` + `shared/events/dlq.py` |
| RI-02 ModuleLifecycle | **MOD-INF-016** | `lifecycle_manager/hooks.py` |
| RI-03 ConfigCenter | **MOD-INF-016** | `shared/config/` + `shared/flags.py` |
| RI-04 DependencyInjector | **MOD-INF-016** (planned) | `shared/production/di_container.py`（待施工） |
| RI-05 ResilienceGuard | **MOD-INF-016** | `shared/resilience/` |
| RI-06 IdempotencyGuard | **MOD-INF-016** | `shared/production/idempotency.py` |
| RI-07 SecretsManager | **MOD-INF-016** | `shared/production/secrets.py` |
| RI-08 ErrorHandler | **MOD-INF-016** | `shared/errors.py` + `shared/logging.py` |
| RI-09 HealthCheck | **MOD-INF-016** | `shared/health.py` |
| RI-10 TelemetryCollector | **MOD-INF-016** | `shared/production/metrics.py` |
| RI-11 CacheLayer | **MOD-INF-016** | `shared/production/cache.py` |
| RI-12 AutoDiagnostics | **独立落地** | `infra_ops/auto_diagnostics.py` |
| RI-13 EventStore | **独立落地** | `infra_ops/event_store.py` |
| RI-14 DryRunSimulator | **独立落地** | `infra_ops/dry_run_simulator.py` |
| RI-15 CostTracker | **独立落地** | `infra_ops/cost_tracker.py` |

> **职责准则**：MOD-INF-002 定义"运行时集成体系需要什么"（WHAT + WHY），MOD-INF-016 承载"公共实现"（HOW）。

## 目录内容

| 文件/目录 | 类型 | 说明 |
|-----------|------|------|
| `blueprint.md` | 蓝图 | Runtime Integration 蓝图 v6.1.1——15 核心 RI 模块 + 48 Cross-Layer 缺口填补 + 交易基础设施 + 模块通信模式 + AI 施工模式库 |
| `changes/` | 目录 | 变更记录 |

## 导航

- [上级目录](../index.md)
