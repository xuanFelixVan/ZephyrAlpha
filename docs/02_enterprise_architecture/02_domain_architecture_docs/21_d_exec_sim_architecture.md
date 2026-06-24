---
doc_type: domain_architecture_diagram
title: D-EXEC_SIM 执行仿真架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 21_d_exec_sim / 执行仿真 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示执行仿真（D-EXEC_SIM）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:01:56
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 执行仿真（D-EXEC_SIM）的模块分布。共 8 个模块 / 8 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│               L2 领域层 / Domain Layer (7 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/execution_simulation/__init__.py  [prototype]       │
│   src/zephyr/execution_simulation/_extensions/__init__.py  [s... │
│   src/zephyr/execution_simulation/api/__init__.py  [scaffold_... │
│   src/zephyr/execution_simulation/core/__init__.py  [scaffold... │
│   src/zephyr/execution_simulation/infrastructure/__init__.py ... │
│   src/zephyr/execution_simulation/models/__init__.py  [scaffo... │
│   src/zephyr/execution_simulation/services/__init__.py  [scaf... │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│            L3 应用层 / Application Layer (1 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   执行仿真  [design]                                             │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 8 个模块 / 8 modules）。

### L2 领域层 / Domain Layer (7 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/execution_simulation/__init__.py | src/zephyr/execution_simulation/__ini... | prototype | orphan |
| 2 | src/zephyr/execution_simulation/_extensions/__init__.py | src/zephyr/execution_simulation/_exte... | scaffold_placeholder | orphan |
| 3 | src/zephyr/execution_simulation/api/__init__.py | src/zephyr/execution_simulation/api/_... | scaffold_placeholder | orphan |
| 4 | src/zephyr/execution_simulation/core/__init__.py | src/zephyr/execution_simulation/core/... | scaffold_placeholder | orphan |
| 5 | src/zephyr/execution_simulation/infrastructure/__init__.py | src/zephyr/execution_simulation/infra... | scaffold_placeholder | orphan |
| 6 | src/zephyr/execution_simulation/models/__init__.py | src/zephyr/execution_simulation/model... | scaffold_placeholder | orphan |
| 7 | src/zephyr/execution_simulation/services/__init__.py | src/zephyr/execution_simulation/servi... | scaffold_placeholder | orphan |

### L3 应用层 / Application Layer (1 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/execution_simulation/ | 执行仿真 | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 0 条 / 0 edges）。按依赖类型分组，使用 → 表示方向。

（无域内依赖 / No internal dependencies）


## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `21_d_exec_sim_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
