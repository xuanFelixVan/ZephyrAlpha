---
doc_type: architecture_view
title: D-FACTOR 因子架构图
version: "1.0"
status: active
date: 2026-06-27
owner: auto-generator
ttl: permanent
---

# 31_d_factor / 因子 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示因子（D-FACTOR）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-27 03:08:24
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 因子（D-FACTOR）的模块分布。共 17 个模块 / 17 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│             L1 基础层 / Foundation Layer (1 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/factor/bus_factor_defense.py  [prototype]           │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (16 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/factor/__init__.py  [prototype]                     │
│   src/zephyr/factor/_extensions/__init__.py  [prototype]         │
│   src/zephyr/factor/alpha_signal_pipeline.py  [prototype]        │
│   src/zephyr/factor/api/__init__.py  [prototype]                 │
│   src/zephyr/factor/base.py  [production]                        │
│   src/zephyr/factor/core/__init__.py  [prototype]                │
│   src/zephyr/factor/ctr_001_consumer/__init__.py  [prototype]    │
│   src/zephyr/factor/engine/__init__.py  [prototype]              │
│   src/zephyr/factor/factor_base.py  [production]                 │
│   src/zephyr/factor/factors/__init__.py  [prototype]             │
│   src/zephyr/factor/factors/momentum_factor.py  [prototype]      │
│   src/zephyr/factor/factors/value_factor.py  [prototype]         │
│   src/zephyr/factor/infrastructure/__init__.py  [prototype]      │
│   src/zephyr/factor/momentum_factor.py  [prototype]              │
│   src/zephyr/factor/services/__init__.py  [prototype]            │
│   src/zephyr/factor/value_factor.py  [prototype]                 │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 17 个模块 / 17 modules）。

### L1 基础层 / Foundation Layer (1 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/factor/bus_factor_defense.py | src/zephyr/factor/bus_factor_defense.py | prototype | generated |

### L2 领域层 / Domain Layer (16 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/factor/__init__.py | src/zephyr/factor/__init__.py | prototype | generated |
| 2 | src/zephyr/factor/_extensions/__init__.py | src/zephyr/factor/_extensions/__init_... | prototype | deprecated |
| 3 | src/zephyr/factor/alpha_signal_pipeline.py | src/zephyr/factor/alpha_signal_pipeli... | prototype | generated |
| 4 | src/zephyr/factor/api/__init__.py | src/zephyr/factor/api/__init__.py | prototype | deprecated |
| 5 | src/zephyr/factor/base.py | src/zephyr/factor/base.py | production | generated |
| 6 | src/zephyr/factor/core/__init__.py | src/zephyr/factor/core/__init__.py | prototype | deprecated |
| 7 | src/zephyr/factor/ctr_001_consumer/__init__.py | src/zephyr/factor/ctr_001_consumer/__... | prototype | deprecated |
| 8 | src/zephyr/factor/engine/__init__.py | src/zephyr/factor/engine/__init__.py | prototype | deprecated |
| 9 | src/zephyr/factor/factor_base.py | src/zephyr/factor/factor_base.py | production | generated |
| 10 | src/zephyr/factor/factors/__init__.py | src/zephyr/factor/factors/__init__.py | prototype | generated |
| 11 | src/zephyr/factor/factors/momentum_factor.py | src/zephyr/factor/factors/momentum_fa... | prototype | generated |
| 12 | src/zephyr/factor/factors/value_factor.py | src/zephyr/factor/factors/value_facto... | prototype | generated |
| 13 | src/zephyr/factor/infrastructure/__init__.py | src/zephyr/factor/infrastructure/__in... | prototype | deprecated |
| 14 | src/zephyr/factor/momentum_factor.py | src/zephyr/factor/momentum_factor.py | prototype | generated |
| 15 | src/zephyr/factor/services/__init__.py | src/zephyr/factor/services/__init__.py | prototype | deprecated |
| 16 | src/zephyr/factor/value_factor.py | src/zephyr/factor/value_factor.py | prototype | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 2 条 / 2 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│        依赖关系图 / Dependency Graph (共 2 条 / 2 edges)         │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 1                               │
│   [config_depends]: 2 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (2 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   __init__.py → alpha_signal_pipeline.py                         │
│   __init__.py → value_factor.py                                  │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `31_d_factor_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
