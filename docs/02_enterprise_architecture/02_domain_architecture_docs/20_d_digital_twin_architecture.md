---
doc_type: domain_architecture_diagram
title: D-DIGITAL_TWIN 数字孪生架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 20_d_digital_twin / 数字孪生 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示数字孪生（D-DIGITAL_TWIN）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 21:40:10
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 数字孪生（D-DIGITAL_TWIN）的模块分布。共 13 个模块 / 13 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (12 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   数字孪生域  [design]                                           │
│   src/zephyr/digital_twin/__init__.py  [prototype]               │
│   src/zephyr/digital_twin/_extensions/__init__.py  [scaffold_... │
│   智能体仿真  [design]                                           │
│   src/zephyr/digital_twin/api/__init__.py  [scaffold_placehol... │
│   src/zephyr/digital_twin/core/__init__.py  [scaffold_placeho... │
│   src/zephyr/digital_twin/infrastructure/__init__.py  [scaffo... │
│   虚拟市场仿真  [design]                                         │
│   src/zephyr/digital_twin/models/__init__.py  [scaffold_place... │
│   订单簿仿真  [design]                                           │
│   场景引擎  [design]                                             │
│   src/zephyr/digital_twin/services/__init__.py  [scaffold_pla... │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│            L3 应用层 / Application Layer (1 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   数字孪生  [design]                                             │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 13 个模块 / 13 modules）。

### L2 领域层 / Domain Layer (12 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/digital_twin/ | 数字孪生域 | design | design_only |
| 2 | src/zephyr/digital_twin/__init__.py | src/zephyr/digital_twin/__init__.py | prototype | orphan |
| 3 | src/zephyr/digital_twin/_extensions/__init__.py | src/zephyr/digital_twin/_extensions/_... | scaffold_placeholder | orphan |
| 4 | src/zephyr/digital_twin/agent_sim/ | 智能体仿真 | design | design_only |
| 5 | src/zephyr/digital_twin/api/__init__.py | src/zephyr/digital_twin/api/__init__.py | scaffold_placeholder | orphan |
| 6 | src/zephyr/digital_twin/core/__init__.py | src/zephyr/digital_twin/core/__init__.py | scaffold_placeholder | orphan |
| 7 | src/zephyr/digital_twin/infrastructure/__init__.py | src/zephyr/digital_twin/infrastructur... | scaffold_placeholder | orphan |
| 8 | src/zephyr/digital_twin/market_sim/ | 虚拟市场仿真 | design | design_only |
| 9 | src/zephyr/digital_twin/models/__init__.py | src/zephyr/digital_twin/models/__init... | scaffold_placeholder | orphan |
| 10 | src/zephyr/digital_twin/orderbook_sim/ | 订单簿仿真 | design | design_only |
| 11 | src/zephyr/digital_twin/scenario/ | 场景引擎 | design | design_only |
| 12 | src/zephyr/digital_twin/services/__init__.py | src/zephyr/digital_twin/services/__in... | scaffold_placeholder | orphan |

### L3 应用层 / Application Layer (1 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/digital_twin/ | 数字孪生 | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 0 条 / 0 edges）。按依赖类型分组，使用 → 表示方向。

（无域内依赖 / No internal dependencies）


## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `20_d_digital_twin_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
