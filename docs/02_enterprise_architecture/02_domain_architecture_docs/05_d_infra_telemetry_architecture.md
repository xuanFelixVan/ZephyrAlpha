---
doc_type: architecture_view
title: D-INFRA_TELEMETRY observability_profiling架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 05_d_infra_telemetry / observability_profiling 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示observability_profiling（D-INFRA_TELEMETRY）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 20:00:20
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 observability_profiling（D-INFRA_TELEMETRY）的模块分布。共 51 个模块 / 51 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (51 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/infrastructure/model_capability_exam/__init__.py... │
│   src/zephyr/infrastructure/model_capability_exam/capability_... │
│   src/zephyr/infrastructure/model_capability_exam/exam_orches... │
│   src/zephyr/infrastructure/model_capability_exam/exam_test_c... │
│   src/zephyr/infrastructure/model_profiler/__init__.py  [prod... │
│   src/zephyr/infrastructure/model_profiler/benchmark_suite.py... │
│   src/zephyr/infrastructure/model_profiler/capability_passpor... │
│   src/zephyr/infrastructure/model_profiler/cli.py  [production]  │
│   src/zephyr/infrastructure/model_profiler/deepseek_v4_chat.p... │
│   src/zephyr/infrastructure/model_profiler/exam_orchestrator.... │
│   src/zephyr/infrastructure/model_profiler/exam_test_cases.py... │
│   src/zephyr/infrastructure/model_profiler/model_discovery.py... │
│   src/zephyr/infrastructure/model_profiler/profiler.py  [prod... │
│   src/zephyr/infrastructure/model_profiler/provider_data.py  ... │
│   src/zephyr/infrastructure/model_profiler/results_writer.py ... │
│   src/zephyr/infrastructure/model_profiler/task_model_learner... │
│   src/zephyr/infrastructure/observability/__init__.py  [produ... │
│   src/zephyr/infrastructure/observability/__init___from_infra... │
│   ...还有 33 个模块 / 33 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 51 个模块 / 51 modules）。

### L1 基础层 / Foundation Layer (51 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/infrastructure/model_capability_exam/__init__.py | src/zephyr/infrastructure/model_capab... | production | generated |
| 2 | src/zephyr/infrastructure/model_capability_exam/capabilit... | src/zephyr/infrastructure/model_capab... | production | generated |
| 3 | src/zephyr/infrastructure/model_capability_exam/exam_orch... | src/zephyr/infrastructure/model_capab... | production | generated |
| 4 | src/zephyr/infrastructure/model_capability_exam/exam_test... | src/zephyr/infrastructure/model_capab... | production | generated |
| 5 | src/zephyr/infrastructure/model_profiler/__init__.py | src/zephyr/infrastructure/model_profi... | production | generated |
| 6 | src/zephyr/infrastructure/model_profiler/benchmark_suite.py | src/zephyr/infrastructure/model_profi... | production | generated |
| 7 | src/zephyr/infrastructure/model_profiler/capability_passp... | src/zephyr/infrastructure/model_profi... | production | generated |
| 8 | src/zephyr/infrastructure/model_profiler/cli.py | src/zephyr/infrastructure/model_profi... | production | generated |
| 9 | src/zephyr/infrastructure/model_profiler/deepseek_v4_chat.py | src/zephyr/infrastructure/model_profi... | production | generated |
| 10 | src/zephyr/infrastructure/model_profiler/exam_orchestrato... | src/zephyr/infrastructure/model_profi... | production | generated |
| 11 | src/zephyr/infrastructure/model_profiler/exam_test_cases.py | src/zephyr/infrastructure/model_profi... | production | generated |
| 12 | src/zephyr/infrastructure/model_profiler/model_discovery.py | src/zephyr/infrastructure/model_profi... | production | generated |
| 13 | src/zephyr/infrastructure/model_profiler/profiler.py | src/zephyr/infrastructure/model_profi... | production | generated |
| 14 | src/zephyr/infrastructure/model_profiler/provider_data.py | src/zephyr/infrastructure/model_profi... | production | generated |
| 15 | src/zephyr/infrastructure/model_profiler/results_writer.py | src/zephyr/infrastructure/model_profi... | production | generated |
| 16 | src/zephyr/infrastructure/model_profiler/task_model_learn... | src/zephyr/infrastructure/model_profi... | production | generated |
| 17 | src/zephyr/infrastructure/observability/__init__.py | src/zephyr/infrastructure/observabili... | production | generated |
| 18 | src/zephyr/infrastructure/observability/__init___from_inf... | src/zephyr/infrastructure/observabili... | production | generated |
| 19 | src/zephyr/infrastructure/observability/contract_metrics.py | src/zephyr/infrastructure/observabili... | production | generated |
| 20 | src/zephyr/infrastructure/observability/health_probes.py | src/zephyr/infrastructure/observabili... | production | generated |
| 21 | src/zephyr/infrastructure/observability/notifier.py | src/zephyr/infrastructure/observabili... | production | generated |
| 22 | src/zephyr/infrastructure/observability/trace_decorator.py | src/zephyr/infrastructure/observabili... | production | generated |
| 23 | src/zephyr/infrastructure/quality/__init__.py | src/zephyr/infrastructure/quality/__i... | production | generated |
| 24 | src/zephyr/infrastructure/quality/quality_monitor.py | src/zephyr/infrastructure/quality/qua... | production | generated |
| 25 | src/zephyr/infrastructure/session/__init__.py | src/zephyr/infrastructure/session/__i... | production | generated |
| 26 | src/zephyr/infrastructure/sla/__init__.py | src/zephyr/infrastructure/sla/__init_... | production | generated |
| 27 | src/zephyr/infrastructure/sla/sla_monitor.py | src/zephyr/infrastructure/sla/sla_mon... | production | generated |
| 28 | src/zephyr/infrastructure/system_telemetry/__init__.py | src/zephyr/infrastructure/system_tele... | production | generated |
| 29 | src/zephyr/infrastructure/system_telemetry/_budget_teleme... | src/zephyr/infrastructure/system_tele... | production | generated |
| 30 | src/zephyr/infrastructure/system_telemetry/_trace_bridge.py | src/zephyr/infrastructure/system_tele... | production | generated |
| 31 | src/zephyr/infrastructure/system_telemetry/ai_behavior/__... | src/zephyr/infrastructure/system_tele... | production | generated |
| 32 | src/zephyr/infrastructure/system_telemetry/ai_behavior/ev... | src/zephyr/infrastructure/system_tele... | production | generated |
| 33 | src/zephyr/infrastructure/system_telemetry/alerts/__init_... | src/zephyr/infrastructure/system_tele... | production | deprecated |
| 34 | src/zephyr/infrastructure/system_telemetry/archive/__init... | src/zephyr/infrastructure/system_tele... | production | generated |
| 35 | src/zephyr/infrastructure/system_telemetry/archive/cold_s... | src/zephyr/infrastructure/system_tele... | production | generated |
| 36 | src/zephyr/infrastructure/system_telemetry/auto_bootstrap.py | src/zephyr/infrastructure/system_tele... | production | generated |
| 37 | src/zephyr/infrastructure/system_telemetry/contract_metri... | src/zephyr/infrastructure/system_tele... | production | generated |
| 38 | src/zephyr/infrastructure/system_telemetry/facade.py | src/zephyr/infrastructure/system_tele... | production | generated |
| 39 | src/zephyr/infrastructure/system_telemetry/health/__init_... | src/zephyr/infrastructure/system_tele... | production | deprecated |
| 40 | src/zephyr/infrastructure/system_telemetry/health_aggrega... | src/zephyr/infrastructure/system_tele... | production | generated |
| 41 | src/zephyr/infrastructure/system_telemetry/health_probes.py | src/zephyr/infrastructure/system_tele... | production | generated |
| 42 | src/zephyr/infrastructure/system_telemetry/logs/__init__.py | src/zephyr/infrastructure/system_tele... | production | generated |
| 43 | src/zephyr/infrastructure/system_telemetry/logs/structure... | src/zephyr/infrastructure/system_tele... | production | generated |
| 44 | src/zephyr/infrastructure/system_telemetry/metrics/__init... | src/zephyr/infrastructure/system_tele... | production | generated |
| 45 | src/zephyr/infrastructure/system_telemetry/metrics/bluepr... | src/zephyr/infrastructure/system_tele... | production | generated |
| 46 | src/zephyr/infrastructure/system_telemetry/metrics_bridge.py | src/zephyr/infrastructure/system_tele... | production | generated |
| 47 | src/zephyr/infrastructure/system_telemetry/profiles/__ini... | src/zephyr/infrastructure/system_tele... | production | deprecated |
| 48 | src/zephyr/infrastructure/system_telemetry/schema/__init_... | src/zephyr/infrastructure/system_tele... | production | deprecated |
| 49 | src/zephyr/infrastructure/system_telemetry/traces/__init_... | src/zephyr/infrastructure/system_tele... | production | generated |
| 50 | src/zephyr/infrastructure/system_telemetry/traces/span_st... | src/zephyr/infrastructure/system_tele... | production | generated |
| 51 | src/zephyr/infrastructure/system_telemetry/watchdog.py | src/zephyr/infrastructure/system_tele... | production | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 27 条 / 27 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 27 条 / 27 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [config_depends]: 22 条 / edges                                │
│   [import_depends]: 5 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (22 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   capability_passport.py → __init__.py                           │
│   exam_orchestrator.py → __init__.py                             │
│   exam_test_cases.py → __init__.py                               │
│   capability_passport.py → __init__.py                           │
│   cli.py → __init__.py                                           │
│   benchmark_suite.py → __init__.py                               │
│   deepseek_v4_chat.py → __init__.py                              │
│   exam_orchestrator.py → __init__.py                             │
│   model_discovery.py → __init__.py                               │
│   exam_test_cases.py → __init__.py                               │
│   profiler.py → __init__.py                                      │
│   task_model_learner.py → __init__.py                            │
│   results_writer.py → __init__.py                                │
│   provider_data.py → __init__.py                                 │
│   contract_metrics.py → __init__.py                              │
│   health_probes.py → __init__.py                                 │
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
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `05_d_infra_telemetry_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
