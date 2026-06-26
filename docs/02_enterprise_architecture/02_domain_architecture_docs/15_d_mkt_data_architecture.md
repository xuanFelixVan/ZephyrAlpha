---
doc_type: architecture_view
title: D-MKT_DATA 行情数据架构图
version: "1.0"
status: active
date: 2026-06-27
owner: auto-generator
ttl: permanent
---

# 15_d_mkt_data / 行情数据 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示行情数据（D-MKT_DATA）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-27 03:08:24
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 行情数据（D-MKT_DATA）的模块分布。共 9 个模块 / 9 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│             L1 基础层 / Foundation Layer (2 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/market_data/market_data.py  [prototype]             │
│   src/zephyr/market_data/market_data_pipeline.py  [prototype]    │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               L2 领域层 / Domain Layer (7 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/market_data/__init__.py  [production]               │
│   src/zephyr/market_data/_extensions/__init__.py  [prototype]    │
│   src/zephyr/market_data/api/__init__.py  [prototype]            │
│   src/zephyr/market_data/core/__init__.py  [prototype]           │
│   src/zephyr/market_data/infrastructure/__init__.py  [prototype] │
│   src/zephyr/market_data/models/__init__.py  [prototype]         │
│   src/zephyr/market_data/services/__init__.py  [prototype]       │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 9 个模块 / 9 modules）。

### L1 基础层 / Foundation Layer (2 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/market_data/market_data.py | src/zephyr/market_data/market_data.py | prototype | generated |
| 2 | src/zephyr/market_data/market_data_pipeline.py | src/zephyr/market_data/market_data_pi... | prototype | generated |

### L2 领域层 / Domain Layer (7 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/market_data/__init__.py | src/zephyr/market_data/__init__.py | production | generated |
| 2 | src/zephyr/market_data/_extensions/__init__.py | src/zephyr/market_data/_extensions/__... | prototype | deprecated |
| 3 | src/zephyr/market_data/api/__init__.py | src/zephyr/market_data/api/__init__.py | prototype | deprecated |
| 4 | src/zephyr/market_data/core/__init__.py | src/zephyr/market_data/core/__init__.py | prototype | deprecated |
| 5 | src/zephyr/market_data/infrastructure/__init__.py | src/zephyr/market_data/infrastructure... | prototype | deprecated |
| 6 | src/zephyr/market_data/models/__init__.py | src/zephyr/market_data/models/__init_... | prototype | deprecated |
| 7 | src/zephyr/market_data/services/__init__.py | src/zephyr/market_data/services/__ini... | prototype | deprecated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 0 条 / 0 edges）。按依赖类型分组，使用 → 表示方向。

（无域内依赖 / No internal dependencies）


## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `15_d_mkt_data_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
