---
doc_type: domain_architecture_diagram
title: D-INTELLIGENCE 上下文管理架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 40_d_intelligence / 上下文管理 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示上下文管理（D-INTELLIGENCE）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 18:42:45
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 上下文管理（D-INTELLIGENCE）的模块分布。共 57 个模块 / 57 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (56 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/intelligence/__init__.py  [prototype]               │
│   src/zephyr/intelligence/_extensions/__init__.py  [prototype]   │
│   src/zephyr/intelligence/api/__init__.py  [prototype]           │
│   src/zephyr/intelligence/core/__init__.py  [prototype]          │
│   src/zephyr/intelligence/infrastructure/__init__.py  [protot... │
│   src/zephyr/intelligence/model_drift_detector.py  [prototype]   │
│   src/zephyr/intelligence/model_evaluation/__init__.py  [prot... │
│   src/zephyr/intelligence/model_evaluation/activate.py  [prod... │
│   src/zephyr/intelligence/model_evaluation/backtest_base.py  ... │
│   src/zephyr/intelligence/model_evaluation/experiment_tracker... │
│   src/zephyr/intelligence/model_evaluation/implementations/__... │
│   src/zephyr/intelligence/model_evaluation/implementations/de... │
│   src/zephyr/intelligence/model_evaluation/implementations/de... │
│   src/zephyr/intelligence/model_evaluation/inference_base.py ... │
│   src/zephyr/intelligence/model_evaluation/kb_repo.py  [produ... │
│   src/zephyr/intelligence/model_evaluation/notebook_integrati... │
│   src/zephyr/intelligence/model_evaluation/reranker.py  [prod... │
│   src/zephyr/intelligence/model_evaluation/sync_engine.py  [p... │
│   ...还有 38 个模块 / 38 more modules                            │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (1 modules)                 │
├──────────────────────────────────────────────────────────────────┤
│   F10-model-exam/  [design]                                      │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 57 个模块 / 57 modules）。

### L1 基础层 / Foundation Layer (56 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/intelligence/__init__.py | src/zephyr/intelligence/__init__.py | prototype | deprecated |
| 2 | src/zephyr/intelligence/_extensions/__init__.py | src/zephyr/intelligence/_extensions/_... | prototype | deprecated |
| 3 | src/zephyr/intelligence/api/__init__.py | src/zephyr/intelligence/api/__init__.py | prototype | deprecated |
| 4 | src/zephyr/intelligence/core/__init__.py | src/zephyr/intelligence/core/__init__.py | prototype | deprecated |
| 5 | src/zephyr/intelligence/infrastructure/__init__.py | src/zephyr/intelligence/infrastructur... | prototype | deprecated |
| 6 | src/zephyr/intelligence/model_drift_detector.py | src/zephyr/intelligence/model_drift_d... | prototype | generated |
| 7 | src/zephyr/intelligence/model_evaluation/__init__.py | src/zephyr/intelligence/model_evaluat... | prototype | generated |
| 8 | src/zephyr/intelligence/model_evaluation/activate.py | src/zephyr/intelligence/model_evaluat... | production | generated |
| 9 | src/zephyr/intelligence/model_evaluation/backtest_base.py | src/zephyr/intelligence/model_evaluat... | prototype | generated |
| 10 | src/zephyr/intelligence/model_evaluation/experiment_track... | src/zephyr/intelligence/model_evaluat... | prototype | generated |
| 11 | src/zephyr/intelligence/model_evaluation/implementations/... | src/zephyr/intelligence/model_evaluat... | prototype | generated |
| 12 | src/zephyr/intelligence/model_evaluation/implementations/... | src/zephyr/intelligence/model_evaluat... | prototype | generated |
| 13 | src/zephyr/intelligence/model_evaluation/implementations/... | src/zephyr/intelligence/model_evaluat... | production | generated |
| 14 | src/zephyr/intelligence/model_evaluation/inference_base.py | src/zephyr/intelligence/model_evaluat... | production | generated |
| 15 | src/zephyr/intelligence/model_evaluation/kb_repo.py | src/zephyr/intelligence/model_evaluat... | production | generated |
| 16 | src/zephyr/intelligence/model_evaluation/notebook_integra... | src/zephyr/intelligence/model_evaluat... | prototype | generated |
| 17 | src/zephyr/intelligence/model_evaluation/reranker.py | src/zephyr/intelligence/model_evaluat... | production | generated |
| 18 | src/zephyr/intelligence/model_evaluation/sync_engine.py | src/zephyr/intelligence/model_evaluat... | prototype | generated |
| 19 | src/zephyr/intelligence/model_evaluation/target_lib/__ini... | src/zephyr/intelligence/model_evaluat... | prototype | deprecated |
| 20 | src/zephyr/intelligence/model_evaluation/unified_memory_a... | src/zephyr/intelligence/model_evaluat... | production | generated |
| 21 | src/zephyr/intelligence/model_profiling/__init__.py | src/zephyr/intelligence/model_profili... | prototype | generated |
| 22 | src/zephyr/intelligence/model_profiling/benchmark_suite.py | src/zephyr/intelligence/model_profili... | prototype | generated |
| 23 | src/zephyr/intelligence/model_profiling/capability_passpo... | src/zephyr/intelligence/model_profili... | production | generated |
| 24 | src/zephyr/intelligence/model_profiling/cli.py | src/zephyr/intelligence/model_profili... | production | generated |
| 25 | src/zephyr/intelligence/model_profiling/deepseek_v4_chat.py | src/zephyr/intelligence/model_profili... | production | generated |
| 26 | src/zephyr/intelligence/model_profiling/exam_orchestrator.py | src/zephyr/intelligence/model_profili... | production | generated |
| 27 | src/zephyr/intelligence/model_profiling/exam_test_cases.py | src/zephyr/intelligence/model_profili... | production | generated |
| 28 | src/zephyr/intelligence/model_profiling/model_discovery.py | src/zephyr/intelligence/model_profili... | prototype | generated |
| 29 | src/zephyr/intelligence/model_profiling/pipeline/__init__.py | src/zephyr/intelligence/model_profili... | prototype | generated |
| 30 | src/zephyr/intelligence/model_profiling/pipeline/benchmar... | src/zephyr/intelligence/model_profili... | prototype | generated |
| 31 | src/zephyr/intelligence/model_profiling/pipeline/capabili... | src/zephyr/intelligence/model_profili... | prototype | generated |
| 32 | src/zephyr/intelligence/model_profiling/pipeline/cli.py | src/zephyr/intelligence/model_profili... | prototype | generated |
| 33 | src/zephyr/intelligence/model_profiling/pipeline/deepseek... | src/zephyr/intelligence/model_profili... | prototype | generated |
| 34 | src/zephyr/intelligence/model_profiling/pipeline/exam_orc... | src/zephyr/intelligence/model_profili... | prototype | generated |
| 35 | src/zephyr/intelligence/model_profiling/pipeline/exam_tes... | src/zephyr/intelligence/model_profili... | prototype | generated |
| 36 | src/zephyr/intelligence/model_profiling/pipeline/model_di... | src/zephyr/intelligence/model_profili... | prototype | generated |
| 37 | src/zephyr/intelligence/model_profiling/pipeline/profiler.py | src/zephyr/intelligence/model_profili... | prototype | generated |
| 38 | src/zephyr/intelligence/model_profiling/pipeline/results_... | src/zephyr/intelligence/model_profili... | prototype | generated |
| 39 | src/zephyr/intelligence/model_profiling/pipeline/task_mod... | src/zephyr/intelligence/model_profili... | prototype | generated |
| 40 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | prototype | generated |
| 41 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | production | generated |
| 42 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | production | generated |
| 43 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | prototype | generated |
| 44 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | prototype | generated |
| 45 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | prototype | generated |
| 46 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | prototype | generated |
| 47 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | production | generated |
| 48 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | production | generated |
| 49 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | production | generated |
| 50 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | production | generated |
| 51 | src/zephyr/intelligence/model_profiling/profiler.py | src/zephyr/intelligence/model_profili... | prototype | generated |
| 52 | src/zephyr/intelligence/model_profiling/provider_data.py | src/zephyr/intelligence/model_profili... | production | generated |
| 53 | src/zephyr/intelligence/model_profiling/results_writer.py | src/zephyr/intelligence/model_profili... | prototype | generated |
| 54 | src/zephyr/intelligence/model_profiling/task_model_learne... | src/zephyr/intelligence/model_profili... | prototype | generated |
| 55 | src/zephyr/intelligence/models/__init__.py | src/zephyr/intelligence/models/__init... | prototype | deprecated |
| 56 | src/zephyr/intelligence/services/__init__.py | src/zephyr/intelligence/services/__in... | prototype | deprecated |

### 未分类 / Unclassified (1 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | F10-model-exam/ | F10-model-exam/ | design | stable |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 45 条 / 45 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 45 条 / 45 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [import_depends]: 42 条 / edges                                │
│   [config_depends]: 3 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (42 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   activate.py → kb_repo.py                                       │
│   __init__.py → default_backtest_engine.py                       │
│   __init__.py → default_inference_engine.py                      │
│   exam_orchestrator.py → capability_passport.py                  │
│   exam_orchestrator.py → exam_test_cases.py                      │
│   cli.py → results_writer.py                                     │
│   cli.py → __init__.py                                           │
│   results_writer.py → profiler.py                                │
│   profiler.py → benchmark_suite.py                               │
│   profiler.py → model_discovery.py                               │
│   model_discovery.py → provider_data.py                          │
│   __init__.py → benchmark_suite.py                               │
│   __init__.py → profiler.py                                      │
│   __init__.py → model_discovery.py                               │
│   __init__.py → task_model_learner.py                            │
│   cli.py → model_discovery.py                                    │
│   cli.py → results_writer.py                                     │
│   cli.py → profiler.py                                           │
│   exam_orchestrator.py → capability_passport.py                  │
│   exam_orchestrator.py → exam_test_cases.py                      │
│   results_writer.py → profiler.py                                │
│   profiler.py → benchmark_suite.py                               │
│   profiler.py → model_discovery.py                               │
│   __init__.py → benchmark_suite.py                               │
│   __init__.py → cli.py                                           │
│   __init__.py → model_discovery.py                               │
│   __init__.py → profiler.py                                      │
│   __init__.py → task_model_learner.py                            │
│   cli.py → profiler.py                                           │
│   cli.py → model_discovery.py                                    │
│   cli.py → results_writer.py                                     │
│   profiler.py → benchmark_suite.py                               │
│   profiler.py → model_discovery.py                               │
│   __init__.py → cli.py                                           │
│   __init__.py → benchmark_suite.py                               │
│   __init__.py → profiler.py                                      │
│   __init__.py → model_discovery.py                               │
│   __init__.py → task_model_learner.py                            │
│   exam_orchestrator.py → capability_passport.py                  │
│   exam_orchestrator.py → exam_test_cases.py                      │
│   model_discovery.py → provider_data.py                          │
│   results_writer.py → profiler.py                                │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (3 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   backtest_base.py → __init__.py                                 │
│   deepseek_v4_chat.py → __init__.py                              │
│   deepseek_v4_chat.py → __init__.py                              │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `40_d_intelligence_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
