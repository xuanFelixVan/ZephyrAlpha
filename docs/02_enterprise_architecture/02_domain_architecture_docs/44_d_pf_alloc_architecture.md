---
doc_type: architecture_view
title: D-PF_ALLOC 组合分配架构图
version: "1.0"
status: active
date: 2026-06-27
owner: auto-generator
ttl: permanent
---

# 44_d_pf_alloc / 组合分配 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示组合分配（D-PF_ALLOC）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-27 03:08:24
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 组合分配（D-PF_ALLOC）的模块分布。共 11 个模块 / 11 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│             L1 基础层 / Foundation Layer (2 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/pf_core/default_equity_strategy.py  [prototype]     │
│   src/zephyr/pf_core/strategy_portfolio.py  [prototype]          │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               L2 领域层 / Domain Layer (9 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   组合分配域  [design]                                           │
│   src/zephyr/pf_alloc/__init__.py  [prototype]                   │
│   src/zephyr/pf_alloc/_extensions/__init__.py  [prototype]       │
│   src/zephyr/pf_alloc/api/__init__.py  [prototype]               │
│   src/zephyr/pf_alloc/core/__init__.py  [prototype]              │
│   src/zephyr/pf_alloc/infrastructure/__init__.py  [prototype]    │
│   src/zephyr/pf_alloc/models/__init__.py  [prototype]            │
│   src/zephyr/pf_alloc/services/__init__.py  [prototype]          │
│   src/zephyr/pf_alloc/strategy_lifecycle_event.py  [prototype]   │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 11 个模块 / 11 modules）。

### L1 基础层 / Foundation Layer (2 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/pf_core/default_equity_strategy.py | src/zephyr/pf_core/default_equity_str... | prototype | generated |
| 2 | src/zephyr/pf_core/strategy_portfolio.py | src/zephyr/pf_core/strategy_portfolio.py | prototype | generated |

### L2 领域层 / Domain Layer (9 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/pf_alloc/ | 组合分配域 | design | planned |
| 2 | src/zephyr/pf_alloc/__init__.py | src/zephyr/pf_alloc/__init__.py | prototype | generated |
| 3 | src/zephyr/pf_alloc/_extensions/__init__.py | src/zephyr/pf_alloc/_extensions/__ini... | prototype | deprecated |
| 4 | src/zephyr/pf_alloc/api/__init__.py | src/zephyr/pf_alloc/api/__init__.py | prototype | deprecated |
| 5 | src/zephyr/pf_alloc/core/__init__.py | src/zephyr/pf_alloc/core/__init__.py | prototype | deprecated |
| 6 | src/zephyr/pf_alloc/infrastructure/__init__.py | src/zephyr/pf_alloc/infrastructure/__... | prototype | deprecated |
| 7 | src/zephyr/pf_alloc/models/__init__.py | src/zephyr/pf_alloc/models/__init__.py | prototype | deprecated |
| 8 | src/zephyr/pf_alloc/services/__init__.py | src/zephyr/pf_alloc/services/__init__.py | prototype | deprecated |
| 9 | src/zephyr/pf_alloc/strategy_lifecycle_event.py | src/zephyr/pf_alloc/strategy_lifecycl... | prototype | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 0 条 / 0 edges）。按依赖类型分组，使用 → 表示方向。

（无域内依赖 / No internal dependencies）


## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `44_d_pf_alloc_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
