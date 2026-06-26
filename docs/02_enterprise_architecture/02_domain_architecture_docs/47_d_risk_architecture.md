---
doc_type: architecture_view
title: D-RISK 风控架构图
version: "1.0"
status: active
date: 2026-06-27
owner: auto-generator
ttl: permanent
---

# 47_d_risk / 风控 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示风控（D-RISK）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-27 03:08:24
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 风控（D-RISK）的模块分布。共 25 个模块 / 25 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│             L1 基础层 / Foundation Layer (1 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/risk/oms_risk_engine.py  [prototype]                │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (24 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/risk/__init__.py  [prototype]                       │
│   src/zephyr/risk/_extensions/__init__.py  [prototype]           │
│   src/zephyr/risk/api/__init__.py  [prototype]                   │
│   src/zephyr/risk/core/__init__.py  [prototype]                  │
│   src/zephyr/risk/cross_asset/__init__.py  [prototype]           │
│   src/zephyr/risk/cross_asset/cross_asset_risk_decomposer/__i... │
│   src/zephyr/risk/cross_asset/cross_market_data_adapter/__ini... │
│   src/zephyr/risk/cross_asset/cross_market_data_adapter/ml_ex... │
│   src/zephyr/risk/cross_asset/currency_hedger_and_fixed_incom... │
│   src/zephyr/risk/cross_asset/risk_manager.py  [prototype]       │
│   src/zephyr/risk/cross_asset/risk_manager_base.py  [prototype]  │
│   src/zephyr/risk/implementations/__init__.py  [prototype]       │
│   src/zephyr/risk/implementations/default_position_limit_chec... │
│   src/zephyr/risk/implementations/default_risk_limits_calcula... │
│   src/zephyr/risk/implementations/default_risk_manager_orches... │
│   src/zephyr/risk/implementations/default_risk_validator.py  ... │
│   src/zephyr/risk/implementations/default_stop_loss_engine.py... │
│   src/zephyr/risk/infrastructure/__init__.py  [prototype]        │
│   ...还有 6 个模块 / 6 more modules                              │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 25 个模块 / 25 modules）。

### L1 基础层 / Foundation Layer (1 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/risk/oms_risk_engine.py | src/zephyr/risk/oms_risk_engine.py | prototype | generated |

### L2 领域层 / Domain Layer (24 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/risk/__init__.py | src/zephyr/risk/__init__.py | prototype | generated |
| 2 | src/zephyr/risk/_extensions/__init__.py | src/zephyr/risk/_extensions/__init__.py | prototype | deprecated |
| 3 | src/zephyr/risk/api/__init__.py | src/zephyr/risk/api/__init__.py | prototype | deprecated |
| 4 | src/zephyr/risk/core/__init__.py | src/zephyr/risk/core/__init__.py | prototype | deprecated |
| 5 | src/zephyr/risk/cross_asset/__init__.py | src/zephyr/risk/cross_asset/__init__.py | prototype | generated |
| 6 | src/zephyr/risk/cross_asset/cross_asset_risk_decomposer/_... | src/zephyr/risk/cross_asset/cross_ass... | prototype | deprecated |
| 7 | src/zephyr/risk/cross_asset/cross_market_data_adapter/__i... | src/zephyr/risk/cross_asset/cross_mar... | prototype | generated |
| 8 | src/zephyr/risk/cross_asset/cross_market_data_adapter/ml_... | src/zephyr/risk/cross_asset/cross_mar... | prototype | generated |
| 9 | src/zephyr/risk/cross_asset/currency_hedger_and_fixed_inc... | src/zephyr/risk/cross_asset/currency_... | prototype | deprecated |
| 10 | src/zephyr/risk/cross_asset/risk_manager.py | src/zephyr/risk/cross_asset/risk_mana... | prototype | generated |
| 11 | src/zephyr/risk/cross_asset/risk_manager_base.py | src/zephyr/risk/cross_asset/risk_mana... | prototype | generated |
| 12 | src/zephyr/risk/implementations/__init__.py | src/zephyr/risk/implementations/__ini... | prototype | generated |
| 13 | src/zephyr/risk/implementations/default_position_limit_ch... | src/zephyr/risk/implementations/defau... | production | generated |
| 14 | src/zephyr/risk/implementations/default_risk_limits_calcu... | src/zephyr/risk/implementations/defau... | production | generated |
| 15 | src/zephyr/risk/implementations/default_risk_manager_orch... | src/zephyr/risk/implementations/defau... | production | generated |
| 16 | src/zephyr/risk/implementations/default_risk_validator.py | src/zephyr/risk/implementations/defau... | production | generated |
| 17 | src/zephyr/risk/implementations/default_stop_loss_engine.py | src/zephyr/risk/implementations/defau... | production | generated |
| 18 | src/zephyr/risk/infrastructure/__init__.py | src/zephyr/risk/infrastructure/__init... | prototype | deprecated |
| 19 | src/zephyr/risk/risk_limits.py | src/zephyr/risk/risk_limits.py | prototype | generated |
| 20 | src/zephyr/risk/risk_manager.py | src/zephyr/risk/risk_manager.py | production | generated |
| 21 | src/zephyr/risk/risk_manager_base.py | src/zephyr/risk/risk_manager_base.py | production | generated |
| 22 | src/zephyr/risk/risk_validator.py | src/zephyr/risk/risk_validator.py | production | generated |
| 23 | src/zephyr/risk/services/__init__.py | src/zephyr/risk/services/__init__.py | prototype | deprecated |
| 24 | src/zephyr/risk/stop_loss.py | src/zephyr/risk/stop_loss.py | production | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 16 条 / 16 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 16 条 / 16 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [import_depends]: 14 条 / edges                                │
│   [config_depends]: 2 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (14 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   __init__.py → risk_manager.py                                  │
│   __init__.py → risk_manager_base.py                             │
│   default_position_limit_ch... → risk_manager.py                 │
│   default_position_limit_ch... → risk_manager_base.py            │
│   default_stop_loss_engine.py → risk_manager_base.py             │
│   default_risk_manager_orch... → risk_manager.py                 │
│   default_risk_manager_orch... → risk_manager_base.py            │
│   default_risk_manager_orch... → default_position_limit_ch...    │
│   default_risk_manager_orch... → default_stop_loss_engine.py     │
│   default_risk_manager_orch... → default_risk_validator.py       │
│   default_risk_manager_orch... → default_risk_limits_calcu...    │
│   default_risk_validator.py → risk_manager.py                    │
│   default_risk_validator.py → risk_validator.py                  │
│   default_risk_limits_calcu... → risk_manager.py                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (2 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   __init__.py → ml_experiment_pipeline.py                        │
│   __init__.py → default_position_limit_ch...                     │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `47_d_risk_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
