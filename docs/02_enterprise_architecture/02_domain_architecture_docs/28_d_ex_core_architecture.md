---
doc_type: architecture_view
title: D-EX_CORE 执行核心架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 28_d_ex_core / 执行核心 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示执行核心（D-EX_CORE）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 20:00:20
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 执行核心（D-EX_CORE）的模块分布。共 14 个模块 / 14 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│             L1 基础层 / Foundation Layer (3 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/ex_core/execution_engine.py  [prototype]            │
│   src/zephyr/ex_core/order_manager.py  [prototype]               │
│   src/zephyr/ex_core/order_state_escalator.py  [prototype]       │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (11 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/ex_core/__init__.py  [production]                   │
│   src/zephyr/ex_core/_extensions/__init__.py  [prototype]        │
│   src/zephyr/ex_core/adapters/__init__.py  [prototype]           │
│   src/zephyr/ex_core/adapters/broker_interface.py  [production]  │
│   src/zephyr/ex_core/adapters/risk_validation_bridge.py  [pro... │
│   src/zephyr/ex_core/adapters/simulation_broker.py  [production] │
│   src/zephyr/ex_core/api/__init__.py  [prototype]                │
│   src/zephyr/ex_core/broker_interface.py  [prototype]            │
│   src/zephyr/ex_core/core/__init__.py  [prototype]               │
│   src/zephyr/ex_core/infrastructure/__init__.py  [prototype]     │
│   src/zephyr/ex_core/services/__init__.py  [prototype]           │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 14 个模块 / 14 modules）。

### L1 基础层 / Foundation Layer (3 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/ex_core/execution_engine.py | src/zephyr/ex_core/execution_engine.py | prototype | generated |
| 2 | src/zephyr/ex_core/order_manager.py | src/zephyr/ex_core/order_manager.py | prototype | generated |
| 3 | src/zephyr/ex_core/order_state_escalator.py | src/zephyr/ex_core/order_state_escala... | prototype | generated |

### L2 领域层 / Domain Layer (11 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/ex_core/__init__.py | src/zephyr/ex_core/__init__.py | production | generated |
| 2 | src/zephyr/ex_core/_extensions/__init__.py | src/zephyr/ex_core/_extensions/__init... | prototype | deprecated |
| 3 | src/zephyr/ex_core/adapters/__init__.py | src/zephyr/ex_core/adapters/__init__.py | prototype | generated |
| 4 | src/zephyr/ex_core/adapters/broker_interface.py | src/zephyr/ex_core/adapters/broker_in... | production | generated |
| 5 | src/zephyr/ex_core/adapters/risk_validation_bridge.py | src/zephyr/ex_core/adapters/risk_vali... | prototype | generated |
| 6 | src/zephyr/ex_core/adapters/simulation_broker.py | src/zephyr/ex_core/adapters/simulatio... | production | generated |
| 7 | src/zephyr/ex_core/api/__init__.py | src/zephyr/ex_core/api/__init__.py | prototype | deprecated |
| 8 | src/zephyr/ex_core/broker_interface.py | src/zephyr/ex_core/broker_interface.py | prototype | generated |
| 9 | src/zephyr/ex_core/core/__init__.py | src/zephyr/ex_core/core/__init__.py | prototype | deprecated |
| 10 | src/zephyr/ex_core/infrastructure/__init__.py | src/zephyr/ex_core/infrastructure/__i... | prototype | deprecated |
| 11 | src/zephyr/ex_core/services/__init__.py | src/zephyr/ex_core/services/__init__.py | prototype | deprecated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 1 条 / 1 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│        依赖关系图 / Dependency Graph (共 1 条 / 1 edges)         │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 1                               │
│   [import_depends]: 1 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (1 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   execution_engine.py → order_manager.py                         │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `28_d_ex_core_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
