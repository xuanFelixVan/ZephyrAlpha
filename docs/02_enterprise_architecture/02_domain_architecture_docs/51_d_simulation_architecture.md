---
doc_type: domain_architecture_diagram
title: D-SIMULATION 仿真架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 51_d_simulation / 仿真 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示仿真（D-SIMULATION）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 20:00:21
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 仿真（D-SIMULATION）的模块分布。共 23 个模块 / 23 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (23 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   仿真核心域  [design]                                           │
│   src/zephyr/simulation/__init__.py  [prototype]                 │
│   src/zephyr/simulation/__init___from_resear.py  [prototype]     │
│   src/zephyr/simulation/_extensions/__init__.py  [prototype]     │
│   src/zephyr/simulation/api/__init__.py  [prototype]             │
│   src/zephyr/simulation/backtest_base.py  [production]           │
│   src/zephyr/simulation/backtest_base_from_resear.py  [protot... │
│   src/zephyr/simulation/core/__init__.py  [prototype]            │
│   src/zephyr/simulation/default_backtest_engine.py  [production] │
│   src/zephyr/simulation/default_backtest_engine_from_resear.p... │
│   仿真引擎  [design]                                             │
│   src/zephyr/simulation/implementations/__init__.py  [prototype] │
│   src/zephyr/simulation/implementations/__init___from_resear.... │
│   src/zephyr/simulation/implementations/default_experiment_pi... │
│   src/zephyr/simulation/implementations/default_experiment_pi... │
│   src/zephyr/simulation/infrastructure/__init__.py  [prototype]  │
│   市场仿真器  [design]                                           │
│   src/zephyr/simulation/models/__init__.py  [prototype]          │
│   ...还有 5 个模块 / 5 more modules                              │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 23 个模块 / 23 modules）。

### L2 领域层 / Domain Layer (23 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/simulation/ | 仿真核心域 | design | planned |
| 2 | src/zephyr/simulation/__init__.py | src/zephyr/simulation/__init__.py | prototype | generated |
| 3 | src/zephyr/simulation/__init___from_resear.py | src/zephyr/simulation/__init___from_r... | prototype | generated |
| 4 | src/zephyr/simulation/_extensions/__init__.py | src/zephyr/simulation/_extensions/__i... | prototype | deprecated |
| 5 | src/zephyr/simulation/api/__init__.py | src/zephyr/simulation/api/__init__.py | prototype | deprecated |
| 6 | src/zephyr/simulation/backtest_base.py | src/zephyr/simulation/backtest_base.py | production | generated |
| 7 | src/zephyr/simulation/backtest_base_from_resear.py | src/zephyr/simulation/backtest_base_f... | prototype | generated |
| 8 | src/zephyr/simulation/core/__init__.py | src/zephyr/simulation/core/__init__.py | prototype | deprecated |
| 9 | src/zephyr/simulation/default_backtest_engine.py | src/zephyr/simulation/default_backtes... | production | generated |
| 10 | src/zephyr/simulation/default_backtest_engine_from_resear.py | src/zephyr/simulation/default_backtes... | prototype | generated |
| 11 | src/zephyr/simulation/engine/ | 仿真引擎 | design | planned |
| 12 | src/zephyr/simulation/implementations/__init__.py | src/zephyr/simulation/implementations... | prototype | generated |
| 13 | src/zephyr/simulation/implementations/__init___from_resea... | src/zephyr/simulation/implementations... | prototype | generated |
| 14 | src/zephyr/simulation/implementations/default_experiment_... | src/zephyr/simulation/implementations... | production | generated |
| 15 | src/zephyr/simulation/implementations/default_experiment_... | src/zephyr/simulation/implementations... | prototype | generated |
| 16 | src/zephyr/simulation/infrastructure/__init__.py | src/zephyr/simulation/infrastructure/... | prototype | deprecated |
| 17 | src/zephyr/simulation/market_sim/ | 市场仿真器 | design | planned |
| 18 | src/zephyr/simulation/models/__init__.py | src/zephyr/simulation/models/__init__.py | prototype | deprecated |
| 19 | src/zephyr/simulation/pipeline_base.py | src/zephyr/simulation/pipeline_base.py | production | generated |
| 20 | src/zephyr/simulation/pipeline_base_from_resear.py | src/zephyr/simulation/pipeline_base_f... | prototype | generated |
| 21 | src/zephyr/simulation/result/ | 仿真结果分析 | design | planned |
| 22 | src/zephyr/simulation/scenario/ | 场景管理器 | design | planned |
| 23 | src/zephyr/simulation/services/__init__.py | src/zephyr/simulation/services/__init... | prototype | deprecated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 10 条 / 10 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 10 条 / 10 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [import_depends]: 7 条 / edges                                 │
│   [config_depends]: 3 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (7 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   default_backtest_engine.py → __init__.py                       │
│   default_backtest_engine_f... → __init__.py                     │
│   __init___from_resear.py → backtest_base.py                     │
│   __init___from_resear.py → default_backtest_engine.py           │
│   __init___from_resear.py → pipeline_base.py                     │
│   default_experiment_pipeli... → __init__.py                     │
│   default_experiment_pipeli... → __init__.py                     │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (3 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   backtest_base_from_resear.py → __init__.py                     │
│   __init__.py → default_experiment_pipeli...                     │
│   __init___from_resear.py → __init__.py                          │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `51_d_simulation_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
