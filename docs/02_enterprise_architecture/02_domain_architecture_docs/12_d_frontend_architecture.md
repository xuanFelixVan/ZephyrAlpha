---
doc_type: domain_architecture_diagram
title: D-FRONTEND 前端架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 12_d_frontend / 前端 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示前端（D-FRONTEND）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 20:00:20
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 前端（D-FRONTEND）的模块分布。共 33 个模块 / 33 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│         L0 基础设施层 / Infrastructure Layer (7 modules)         │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/frontend/dashboard/app.py  [prototype]              │
│   src/zephyr/frontend/dashboard/components/fitness_functions.... │
│   src/zephyr/frontend/dashboard/components/gate_statistics.py... │
│   src/zephyr/frontend/dashboard/components/knowledge_overview... │
│   src/zephyr/frontend/dashboard/components/olap_trend.py  [pr... │
│   src/zephyr/frontend/dashboard/components/task_progress.py  ... │
│   src/zephyr/frontend/interface_base.py  [prototype]             │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (16 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/frontend/__init__.py  [prototype]                   │
│   src/zephyr/frontend/_extensions/__init__.py  [prototype]       │
│   src/zephyr/frontend/api/__init__.py  [prototype]               │
│   src/zephyr/frontend/core/__init__.py  [prototype]              │
│   src/zephyr/frontend/dashboard/__init__.py  [prototype]         │
│   src/zephyr/frontend/dashboard/app.py  [production]             │
│   src/zephyr/frontend/dashboard/components/__init__.py  [prot... │
│   src/zephyr/frontend/dashboard/components/fitness_functions.... │
│   src/zephyr/frontend/dashboard/components/gate_statistics.py... │
│   src/zephyr/frontend/dashboard/components/knowledge_overview... │
│   src/zephyr/frontend/dashboard/components/olap_trend.py  [pr... │
│   src/zephyr/frontend/dashboard/components/task_progress.py  ... │
│   src/zephyr/frontend/infrastructure/__init__.py  [prototype]    │
│   src/zephyr/frontend/interface_base.py  [production]            │
│   src/zephyr/frontend/models/__init__.py  [prototype]            │
│   src/zephyr/frontend/services/__init__.py  [prototype]          │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│            L3 应用层 / Application Layer (10 modules)            │
├──────────────────────────────────────────────────────────────────┤
│   Report Visualization  [design]                                 │
│   Alert Visualization  [design]                                  │
│   Custom Chart Builder  [design]                                 │
│   Approval Workflow UI  [design]                                 │
│   Mobile Dashboard  [design]                                     │
│   Collaborative Workspace  [design]                              │
│   Trading Chatbot  [design]                                      │
│   One-Click Quant Interface  [design]                            │
│   API Gateway Proxy  [design]                                    │
│   Feishu Bot  [design]                                           │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 33 个模块 / 33 modules）。

### L0 基础设施层 / Infrastructure Layer (7 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/frontend/dashboard/app.py | src/zephyr/frontend/dashboard/app.py | prototype | generated |
| 2 | src/zephyr/frontend/dashboard/components/fitness_function... | src/zephyr/frontend/dashboard/compone... | prototype | generated |
| 3 | src/zephyr/frontend/dashboard/components/gate_statistics.py | src/zephyr/frontend/dashboard/compone... | prototype | generated |
| 4 | src/zephyr/frontend/dashboard/components/knowledge_overvi... | src/zephyr/frontend/dashboard/compone... | prototype | generated |
| 5 | src/zephyr/frontend/dashboard/components/olap_trend.py | src/zephyr/frontend/dashboard/compone... | prototype | generated |
| 6 | src/zephyr/frontend/dashboard/components/task_progress.py | src/zephyr/frontend/dashboard/compone... | prototype | generated |
| 7 | src/zephyr/frontend/interface_base.py | src/zephyr/frontend/interface_base.py | prototype | generated |

### L1 基础层 / Foundation Layer (16 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/frontend/__init__.py | src/zephyr/frontend/__init__.py | prototype | generated |
| 2 | src/zephyr/frontend/_extensions/__init__.py | src/zephyr/frontend/_extensions/__ini... | prototype | deprecated |
| 3 | src/zephyr/frontend/api/__init__.py | src/zephyr/frontend/api/__init__.py | prototype | deprecated |
| 4 | src/zephyr/frontend/core/__init__.py | src/zephyr/frontend/core/__init__.py | prototype | deprecated |
| 5 | src/zephyr/frontend/dashboard/__init__.py | src/zephyr/frontend/dashboard/__init_... | prototype | generated |
| 6 | src/zephyr/frontend/dashboard/app.py | src/zephyr/frontend/dashboard/app.py | production | generated |
| 7 | src/zephyr/frontend/dashboard/components/__init__.py | src/zephyr/frontend/dashboard/compone... | prototype | generated |
| 8 | src/zephyr/frontend/dashboard/components/fitness_function... | src/zephyr/frontend/dashboard/compone... | production | generated |
| 9 | src/zephyr/frontend/dashboard/components/gate_statistics.py | src/zephyr/frontend/dashboard/compone... | production | generated |
| 10 | src/zephyr/frontend/dashboard/components/knowledge_overvi... | src/zephyr/frontend/dashboard/compone... | production | generated |
| 11 | src/zephyr/frontend/dashboard/components/olap_trend.py | src/zephyr/frontend/dashboard/compone... | production | generated |
| 12 | src/zephyr/frontend/dashboard/components/task_progress.py | src/zephyr/frontend/dashboard/compone... | production | generated |
| 13 | src/zephyr/frontend/infrastructure/__init__.py | src/zephyr/frontend/infrastructure/__... | prototype | deprecated |
| 14 | src/zephyr/frontend/interface_base.py | src/zephyr/frontend/interface_base.py | production | generated |
| 15 | src/zephyr/frontend/models/__init__.py | src/zephyr/frontend/models/__init__.py | prototype | deprecated |
| 16 | src/zephyr/frontend/services/__init__.py | src/zephyr/frontend/services/__init__.py | prototype | deprecated |

### L3 应用层 / Application Layer (10 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | 前端域/D-FRONTEND-06 | Report Visualization | design | planned |
| 2 | 前端域/D-FRONTEND-08 | Alert Visualization | design | planned |
| 3 | 前端域/D-FRONTEND-10 | Custom Chart Builder | design | planned |
| 4 | 前端域/D-FRONTEND-12 | Approval Workflow UI | design | planned |
| 5 | 前端域/D-FRONTEND-14 | Mobile Dashboard | design | planned |
| 6 | 前端域/D-FRONTEND-16 | Collaborative Workspace | design | planned |
| 7 | 前端域/D-FRONTEND-18 | Trading Chatbot | design | planned |
| 8 | 前端域/D-FRONTEND-20 | One-Click Quant Interface | design | planned |
| 9 | 前端域/D-FRONTEND-22 | API Gateway Proxy | design | planned |
| 10 | 前端域/D-FRONTEND-24 | Feishu Bot | design | planned |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 13 条 / 13 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 13 条 / 13 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [config_depends]: 8 条 / edges                                 │
│   [import_depends]: 5 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (8 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   __init__.py → interface_base.py                                │
│   __init__.py → app.py                                           │
│   __init__.py → fitness_functions.py                             │
│   knowledge_overview.py → fitness_functions.py                   │
│   olap_trend.py → fitness_functions.py                           │
│   interface_base.py → fitness_functions.py                       │
│   gate_statistics.py → fitness_functions.py                      │
│   task_progress.py → fitness_functions.py                        │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (5 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   app.py → fitness_functions.py                                  │
│   app.py → knowledge_overview.py                                 │
│   app.py → gate_statistics.py                                    │
│   app.py → olap_trend.py                                         │
│   app.py → task_progress.py                                      │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `12_d_frontend_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
