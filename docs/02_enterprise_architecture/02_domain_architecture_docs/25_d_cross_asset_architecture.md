---
doc_type: domain_architecture_diagram
title: D-CROSS_ASSET 跨资产架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 25_d_cross_asset / 跨资产 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示跨资产（D-CROSS_ASSET）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 18:42:45
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 跨资产（D-CROSS_ASSET）的模块分布。共 15 个模块 / 15 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (15 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   跨资产域  [design]                                             │
│   src/zephyr/cross_asset/__init__.py  [prototype]                │
│   src/zephyr/cross_asset/_extensions/__init__.py  [prototype]    │
│   跨资产分配器  [design]                                         │
│   src/zephyr/cross_asset/api/__init__.py  [prototype]            │
│   src/zephyr/cross_asset/core/__init__.py  [prototype]           │
│   跨资产相关性  [design]                                         │
│   跨资产对冲  [design]                                           │
│   src/zephyr/cross_asset/infrastructure/__init__.py  [prototype] │
│   src/zephyr/cross_asset/models/__init__.py  [prototype]         │
│   src/zephyr/cross_asset/services/__init__.py  [prototype]       │
│   跨资产策略引擎  [design]                                       │
│   src/zephyr/risk/cross_asset/cross_market_data_adapter/ml_ex... │
│   src/zephyr/risk/risk_manager.py  [prototype]                   │
│   src/zephyr/risk/risk_manager_base.py  [prototype]              │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 15 个模块 / 15 modules）。

### L2 领域层 / Domain Layer (15 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/cross_asset/ | 跨资产域 | design | planned |
| 2 | src/zephyr/cross_asset/__init__.py | src/zephyr/cross_asset/__init__.py | prototype | generated |
| 3 | src/zephyr/cross_asset/_extensions/__init__.py | src/zephyr/cross_asset/_extensions/__... | prototype | deprecated |
| 4 | src/zephyr/cross_asset/allocator/ | 跨资产分配器 | design | planned |
| 5 | src/zephyr/cross_asset/api/__init__.py | src/zephyr/cross_asset/api/__init__.py | prototype | deprecated |
| 6 | src/zephyr/cross_asset/core/__init__.py | src/zephyr/cross_asset/core/__init__.py | prototype | deprecated |
| 7 | src/zephyr/cross_asset/correlation/ | 跨资产相关性 | design | planned |
| 8 | src/zephyr/cross_asset/hedger/ | 跨资产对冲 | design | planned |
| 9 | src/zephyr/cross_asset/infrastructure/__init__.py | src/zephyr/cross_asset/infrastructure... | prototype | deprecated |
| 10 | src/zephyr/cross_asset/models/__init__.py | src/zephyr/cross_asset/models/__init_... | prototype | deprecated |
| 11 | src/zephyr/cross_asset/services/__init__.py | src/zephyr/cross_asset/services/__ini... | prototype | deprecated |
| 12 | src/zephyr/cross_asset/strategy/ | 跨资产策略引擎 | design | planned |
| 13 | src/zephyr/risk/cross_asset/cross_market_data_adapter/ml_... | src/zephyr/risk/cross_asset/cross_mar... | production | generated |
| 14 | src/zephyr/risk/risk_manager.py | src/zephyr/risk/risk_manager.py | prototype | generated |
| 15 | src/zephyr/risk/risk_manager_base.py | src/zephyr/risk/risk_manager_base.py | prototype | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 1 条 / 1 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│        依赖关系图 / Dependency Graph (共 1 条 / 1 edges)         │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 1                               │
│   [config_depends]: 1 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (1 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   risk_manager_base.py → __init__.py                             │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `25_d_cross_asset_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
