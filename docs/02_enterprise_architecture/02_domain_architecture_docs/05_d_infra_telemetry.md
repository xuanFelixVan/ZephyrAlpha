---
doc_type: architecture_view
title: D_INFRA_TELEMETRY 可观测性架构文档
version: "1.0"
status: active
date: 2026-06-29
owner: auto-generator
ttl: permanent
---

# 05_d_infra_telemetry / 可观测性

> **文档作用 / Purpose**: 展示 可观测性（D_INFRA_TELEMETRY）功能域的模块清单、域内依赖关系、跨域依赖关系、架构全景图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-29 16:06:28
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 05 | Number | 05 |
| 域ID | D_INFRA_TELEMETRY | Domain ID | D_INFRA_TELEMETRY |
| 域名称 | 可观测性 | Domain Name | 可观测性 |
| 层级 | L0_infrastructure | Layer | L0_infrastructure |
| 模块数 | 35 | Module Count | 35 |
| 域内依赖 | 11 | Internal Dependencies | 11 |
| 跨域入边 | 0 | Cross-domain Incoming | 0 |
| 跨域出边 | 18 | Cross-domain Outgoing | 18 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 0 | Prototype Modules | 0 |
| 生产态模块 | 35 | Production Modules | 35 |
| 容量 | 51/150 (正常) | Capacity | 51/150 (正常) |
| 描述 | 系统遥测采集(system_telemetry) | Description | 系统遥测采集(system_telemetry) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。每30个节点一组分页显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

### 第 1 页 / 共 2 页 / Page 1 of 2

```mermaid
graph TD
    subgraph D_INFRA_TELEMETRY["D_INFRA_TELEMETRY 可观测性"]
        src_zephyr_infrastructure_model_capability_exam_init_py["src/zephyr/infrastructure/model_capability_exam... production"]
        src_zephyr_infrastructure_model_profiler_init_py["src/zephyr/infrastructure/model_profiler/__init... production"]
        src_zephyr_infrastructure_observability_init_py["src/zephyr/infrastructure/observability/__init_... production"]
        src_zephyr_infrastructure_observability_init_from_infra_py["src/zephyr/infrastructure/observability/__init_... production"]
        src_zephyr_infrastructure_observability_notifier_py["src/zephyr/infrastructure/observability/notifie... production"]
        src_zephyr_infrastructure_observability_trace_decorator_py["src/zephyr/infrastructure/observability/trace_d... production"]
        src_zephyr_infrastructure_quality_init_py["src/zephyr/infrastructure/quality/__init__.py production"]
        src_zephyr_infrastructure_quality_quality_monitor_py["src/zephyr/infrastructure/quality/quality_monit... production"]
        src_zephyr_infrastructure_session_init_py["src/zephyr/infrastructure/session/__init__.py production"]
        src_zephyr_infrastructure_sla_init_py["src/zephyr/infrastructure/sla/__init__.py production"]
        src_zephyr_infrastructure_sla_sla_monitor_py["src/zephyr/infrastructure/sla/sla_monitor.py production"]
        src_zephyr_infrastructure_system_telemetry_init_py["src/zephyr/infrastructure/system_telemetry/__in... production"]
        src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py["src/zephyr/infrastructure/system_telemetry/_bud... production"]
        src_zephyr_infrastructure_system_telemetry_trace_bridge_py["src/zephyr/infrastructure/system_telemetry/_tra... production"]
        src_zephyr_infrastructure_system_telemetry_ai_behavior_init_py["src/zephyr/infrastructure/system_telemetry/ai_b... production"]
        src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py["src/zephyr/infrastructure/system_telemetry/ai_b... production"]
        src_zephyr_infrastructure_system_telemetry_alerts_init_py["src/zephyr/infrastructure/system_telemetry/aler... production"]
        src_zephyr_infrastructure_system_telemetry_archive_init_py["src/zephyr/infrastructure/system_telemetry/arch... production"]
        src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py["src/zephyr/infrastructure/system_telemetry/arch... production"]
        src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py["src/zephyr/infrastructure/system_telemetry/auto... production"]
        src_zephyr_infrastructure_system_telemetry_contract_metrics_py["src/zephyr/infrastructure/system_telemetry/cont... production"]
        src_zephyr_infrastructure_system_telemetry_facade_py["src/zephyr/infrastructure/system_telemetry/faca... production"]
        src_zephyr_infrastructure_system_telemetry_health_init_py["src/zephyr/infrastructure/system_telemetry/heal... production"]
        src_zephyr_infrastructure_system_telemetry_health_aggregator_py["src/zephyr/infrastructure/system_telemetry/heal... production"]
        src_zephyr_infrastructure_system_telemetry_health_probes_py["src/zephyr/infrastructure/system_telemetry/heal... production"]
        src_zephyr_infrastructure_system_telemetry_logs_init_py["src/zephyr/infrastructure/system_telemetry/logs... production"]
        src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py["src/zephyr/infrastructure/system_telemetry/logs... production"]
        src_zephyr_infrastructure_system_telemetry_metrics_init_py["src/zephyr/infrastructure/system_telemetry/metr... production"]
        src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py["src/zephyr/infrastructure/system_telemetry/metr... production"]
        src_zephyr_infrastructure_system_telemetry_metrics_bridge_py["src/zephyr/infrastructure/system_telemetry/metr... production"]
    end
    src_zephyr_infrastructure_observability_init_from_infra_py -->|import_depends| src_zephyr_infrastructure_observability_notifier_py
    src_zephyr_infrastructure_observability_init_from_infra_py -->|import_depends| src_zephyr_infrastructure_observability_init_py
    src_zephyr_infrastructure_observability_init_from_infra_py -->|import_depends| src_zephyr_infrastructure_observability_trace_decorator_py
    src_zephyr_infrastructure_quality_init_py -->|import_depends| src_zephyr_infrastructure_quality_quality_monitor_py
    src_zephyr_infrastructure_sla_init_py -->|import_depends| src_zephyr_infrastructure_sla_sla_monitor_py
    src_zephyr_infrastructure_system_telemetry_trace_bridge_py -->|config_depends| src_zephyr_infrastructure_system_telemetry_init_py
    src_zephyr_infrastructure_system_telemetry_health_probes_py -->|config_depends| src_zephyr_infrastructure_system_telemetry_init_py
    src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py -->|config_depends| src_zephyr_infrastructure_system_telemetry_init_py
    src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py -->|config_depends| src_zephyr_infrastructure_system_telemetry_archive_init_py
    src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py -->|config_depends| src_zephyr_infrastructure_system_telemetry_metrics_init_py
    D_INFRA_RUNTIME["D_INFRA_RUNTIME production"]
    src_zephyr_infrastructure_session_init_py -->|import_depends| D_INFRA_RUNTIME
    D_GOVERNANCE["D-GOVERNANCE production"]
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py -->|import_depends| D_GOVERNANCE
    D_SHARED["D-SHARED production"]
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py -->|import_depends| D_SHARED
    src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_system_telemetry_health_aggregator_py -.->|import_depends| D_SHARED
    D_OPS["D-OPS prototype"]
    src_zephyr_infrastructure_system_telemetry_health_aggregator_py -.->|import_depends| D_OPS
    src_zephyr_infrastructure_system_telemetry_health_aggregator_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_system_telemetry_facade_py -->|import_depends| D_INFRA_RUNTIME
    D_BEHAVIORAL_AUDIT["D-BEHAVIORAL_AUDIT production"]
    src_zephyr_infrastructure_system_telemetry_contract_metrics_py -->|import_depends| D_BEHAVIORAL_AUDIT
    src_zephyr_infrastructure_system_telemetry_metrics_bridge_py -->|import_depends| D_SHARED
    src_zephyr_infrastructure_system_telemetry_init_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_system_telemetry_ai_behavior_init_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_system_telemetry_archive_init_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py -->|import_depends| D_INFRA_RUNTIME
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_infrastructure_model_capability_exam_init_py,src_zephyr_infrastructure_model_profiler_init_py,src_zephyr_infrastructure_observability_init_py,src_zephyr_infrastructure_observability_init_from_infra_py,src_zephyr_infrastructure_observability_notifier_py,src_zephyr_infrastructure_observability_trace_decorator_py,src_zephyr_infrastructure_quality_init_py,src_zephyr_infrastructure_quality_quality_monitor_py,src_zephyr_infrastructure_session_init_py,src_zephyr_infrastructure_sla_init_py,src_zephyr_infrastructure_sla_sla_monitor_py,src_zephyr_infrastructure_system_telemetry_init_py,src_zephyr_infrastructure_system_telemetry_budget_telemetry_bridge_py,src_zephyr_infrastructure_system_telemetry_trace_bridge_py,src_zephyr_infrastructure_system_telemetry_ai_behavior_init_py,src_zephyr_infrastructure_system_telemetry_ai_behavior_event_sink_py,src_zephyr_infrastructure_system_telemetry_alerts_init_py,src_zephyr_infrastructure_system_telemetry_archive_init_py,src_zephyr_infrastructure_system_telemetry_archive_cold_stub_py,src_zephyr_infrastructure_system_telemetry_auto_bootstrap_py,src_zephyr_infrastructure_system_telemetry_contract_metrics_py,src_zephyr_infrastructure_system_telemetry_facade_py,src_zephyr_infrastructure_system_telemetry_health_init_py,src_zephyr_infrastructure_system_telemetry_health_aggregator_py,src_zephyr_infrastructure_system_telemetry_health_probes_py,src_zephyr_infrastructure_system_telemetry_logs_init_py,src_zephyr_infrastructure_system_telemetry_logs_structured_sink_py,src_zephyr_infrastructure_system_telemetry_metrics_init_py,src_zephyr_infrastructure_system_telemetry_metrics_blueprint_metrics_py,src_zephyr_infrastructure_system_telemetry_metrics_bridge_py production
    class D_INFRA_RUNTIME,D_GOVERNANCE,D_SHARED,D_BEHAVIORAL_AUDIT external_prod
    class D_OPS external_design
```

### 第 2 页 / 共 2 页 / Page 2 of 2

```mermaid
graph TD
    subgraph D_INFRA_TELEMETRY["D_INFRA_TELEMETRY 可观测性"]
        src_zephyr_infrastructure_system_telemetry_profiles_init_py["src/zephyr/infrastructure/system_telemetry/prof... production"]
        src_zephyr_infrastructure_system_telemetry_schema_init_py["src/zephyr/infrastructure/system_telemetry/sche... production"]
        src_zephyr_infrastructure_system_telemetry_traces_init_py["src/zephyr/infrastructure/system_telemetry/trac... production"]
        src_zephyr_infrastructure_system_telemetry_traces_span_stub_py["src/zephyr/infrastructure/system_telemetry/trac... production"]
        src_zephyr_infrastructure_system_telemetry_watchdog_py["src/zephyr/infrastructure/system_telemetry/watc... production"]
    end
    D_INFRA_RUNTIME["D_INFRA_RUNTIME production"]
    src_zephyr_infrastructure_system_telemetry_traces_init_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_infrastructure_system_telemetry_traces_span_stub_py -->|import_depends| D_INFRA_RUNTIME
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_infrastructure_system_telemetry_profiles_init_py,src_zephyr_infrastructure_system_telemetry_schema_init_py,src_zephyr_infrastructure_system_telemetry_traces_init_py,src_zephyr_infrastructure_system_telemetry_traces_span_stub_py,src_zephyr_infrastructure_system_telemetry_watchdog_py production
    class D_INFRA_RUNTIME external_prod
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 / Target Domain | 依赖数 / Count | 依赖类型 / Type |
|--------|:---:|---------|
| D_INFRA_RUNTIME | 12 | import_depends |
| D-SHARED | 3 | import_depends |
| D-BEHAVIORAL_AUDIT | 1 | import_depends |
| D-GOVERNANCE | 1 | import_depends |
| D-OPS | 1 | import_depends |

### 依赖本域的其他域（入边）/ Depended By

无跨域入边依赖 / No cross-domain incoming dependencies

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 可观测性（D_INFRA_TELEMETRY）的模块分布。共 35 个模块 / 35 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (35 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/infrastructure/model_capability_exam/__init__.py... │
│   src/zephyr/infrastructure/model_profiler/__init__.py  [prod... │
│   src/zephyr/infrastructure/observability/__init__.py  [produ... │
│   src/zephyr/infrastructure/observability/__init___from_infra... │
│   src/zephyr/infrastructure/observability/notifier.py  [produ... │
│   src/zephyr/infrastructure/observability/trace_decorator.py ... │
│   src/zephyr/infrastructure/quality/__init__.py  [production]    │
│   src/zephyr/infrastructure/quality/quality_monitor.py  [prod... │
│   src/zephyr/infrastructure/session/__init__.py  [production]    │
│   src/zephyr/infrastructure/sla/__init__.py  [production]        │
│   src/zephyr/infrastructure/sla/sla_monitor.py  [production]     │
│   src/zephyr/infrastructure/system_telemetry/__init__.py  [pr... │
│   src/zephyr/infrastructure/system_telemetry/_budget_telemetr... │
│   src/zephyr/infrastructure/system_telemetry/_trace_bridge.py... │
│   src/zephyr/infrastructure/system_telemetry/ai_behavior/__in... │
│   src/zephyr/infrastructure/system_telemetry/ai_behavior/even... │
│   src/zephyr/infrastructure/system_telemetry/alerts/__init__.... │
│   src/zephyr/infrastructure/system_telemetry/archive/__init__... │
│   ...还有 17 个模块 / 17 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 35 个模块 / 35 modules）。

### L1 基础层 / Foundation Layer (35 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/infrastructure/model_capability_exam/__init__.py | src/zephyr/infrastructure/model_capab... | production | generated |
| 2 | src/zephyr/infrastructure/model_profiler/__init__.py | src/zephyr/infrastructure/model_profi... | production | generated |
| 3 | src/zephyr/infrastructure/observability/__init__.py | src/zephyr/infrastructure/observabili... | production | generated |
| 4 | src/zephyr/infrastructure/observability/__init___from_inf... | src/zephyr/infrastructure/observabili... | production | generated |
| 5 | src/zephyr/infrastructure/observability/notifier.py | src/zephyr/infrastructure/observabili... | production | generated |
| 6 | src/zephyr/infrastructure/observability/trace_decorator.py | src/zephyr/infrastructure/observabili... | production | generated |
| 7 | src/zephyr/infrastructure/quality/__init__.py | src/zephyr/infrastructure/quality/__i... | production | generated |
| 8 | src/zephyr/infrastructure/quality/quality_monitor.py | src/zephyr/infrastructure/quality/qua... | production | generated |
| 9 | src/zephyr/infrastructure/session/__init__.py | src/zephyr/infrastructure/session/__i... | production | generated |
| 10 | src/zephyr/infrastructure/sla/__init__.py | src/zephyr/infrastructure/sla/__init_... | production | generated |
| 11 | src/zephyr/infrastructure/sla/sla_monitor.py | src/zephyr/infrastructure/sla/sla_mon... | production | generated |
| 12 | src/zephyr/infrastructure/system_telemetry/__init__.py | src/zephyr/infrastructure/system_tele... | production | generated |
| 13 | src/zephyr/infrastructure/system_telemetry/_budget_teleme... | src/zephyr/infrastructure/system_tele... | production | generated |
| 14 | src/zephyr/infrastructure/system_telemetry/_trace_bridge.py | src/zephyr/infrastructure/system_tele... | production | generated |
| 15 | src/zephyr/infrastructure/system_telemetry/ai_behavior/__... | src/zephyr/infrastructure/system_tele... | production | generated |
| 16 | src/zephyr/infrastructure/system_telemetry/ai_behavior/ev... | src/zephyr/infrastructure/system_tele... | production | generated |
| 17 | src/zephyr/infrastructure/system_telemetry/alerts/__init_... | src/zephyr/infrastructure/system_tele... | production | deprecated |
| 18 | src/zephyr/infrastructure/system_telemetry/archive/__init... | src/zephyr/infrastructure/system_tele... | production | generated |
| 19 | src/zephyr/infrastructure/system_telemetry/archive/cold_s... | src/zephyr/infrastructure/system_tele... | production | generated |
| 20 | src/zephyr/infrastructure/system_telemetry/auto_bootstrap.py | src/zephyr/infrastructure/system_tele... | production | generated |
| 21 | src/zephyr/infrastructure/system_telemetry/contract_metri... | src/zephyr/infrastructure/system_tele... | production | generated |
| 22 | src/zephyr/infrastructure/system_telemetry/facade.py | src/zephyr/infrastructure/system_tele... | production | generated |
| 23 | src/zephyr/infrastructure/system_telemetry/health/__init_... | src/zephyr/infrastructure/system_tele... | production | deprecated |
| 24 | src/zephyr/infrastructure/system_telemetry/health_aggrega... | src/zephyr/infrastructure/system_tele... | production | generated |
| 25 | src/zephyr/infrastructure/system_telemetry/health_probes.py | src/zephyr/infrastructure/system_tele... | production | generated |
| 26 | src/zephyr/infrastructure/system_telemetry/logs/__init__.py | src/zephyr/infrastructure/system_tele... | production | generated |
| 27 | src/zephyr/infrastructure/system_telemetry/logs/structure... | src/zephyr/infrastructure/system_tele... | production | generated |
| 28 | src/zephyr/infrastructure/system_telemetry/metrics/__init... | src/zephyr/infrastructure/system_tele... | production | generated |
| 29 | src/zephyr/infrastructure/system_telemetry/metrics/bluepr... | src/zephyr/infrastructure/system_tele... | production | generated |
| 30 | src/zephyr/infrastructure/system_telemetry/metrics_bridge.py | src/zephyr/infrastructure/system_tele... | production | generated |
| 31 | src/zephyr/infrastructure/system_telemetry/profiles/__ini... | src/zephyr/infrastructure/system_tele... | production | deprecated |
| 32 | src/zephyr/infrastructure/system_telemetry/schema/__init_... | src/zephyr/infrastructure/system_tele... | production | deprecated |
| 33 | src/zephyr/infrastructure/system_telemetry/traces/__init_... | src/zephyr/infrastructure/system_tele... | production | generated |
| 34 | src/zephyr/infrastructure/system_telemetry/traces/span_st... | src/zephyr/infrastructure/system_tele... | production | generated |
| 35 | src/zephyr/infrastructure/system_telemetry/watchdog.py | src/zephyr/infrastructure/system_tele... | production | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 11 条 / 11 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 11 条 / 11 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [config_depends]: 6 条 / edges                                 │
│   [import_depends]: 5 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (6 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   _trace_bridge.py → __init__.py                                 │
│   health_probes.py → __init__.py                                 │
│   watchdog.py → __init__.py                                      │
│   _budget_telemetry_bridge.py → __init__.py                      │
│   cold_stub.py → __init__.py                                     │
│   blueprint_metrics.py → __init__.py                             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (5 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   __init___from_infra.py → notifier.py                           │
│   __init___from_infra.py → __init__.py                           │
│   __init___from_infra.py → trace_decorator.py                    │
│   __init__.py → quality_monitor.py                               │
│   __init__.py → sla_monitor.py                                   │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
