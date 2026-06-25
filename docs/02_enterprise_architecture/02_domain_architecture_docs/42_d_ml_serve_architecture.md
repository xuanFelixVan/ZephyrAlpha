---
doc_type: domain_architecture_diagram
title: D-ML_SERVE 推理架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 42_d_ml_serve / 推理 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示推理（D-ML_SERVE）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 20:00:20
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 推理（D-ML_SERVE）的模块分布。共 8 个模块 / 8 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│               L2 领域层 / Domain Layer (8 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/ml_serve/__init__.py  [prototype]                   │
│   src/zephyr/ml_serve/_extensions/__init__.py  [prototype]       │
│   src/zephyr/ml_serve/api/__init__.py  [prototype]               │
│   src/zephyr/ml_serve/core/__init__.py  [prototype]              │
│   src/zephyr/ml_serve/infrastructure/__init__.py  [prototype]    │
│   src/zephyr/ml_serve/models/__init__.py  [prototype]            │
│   src/zephyr/ml_serve/services/__init__.py  [prototype]          │
│   推理熔断器  [design]                                           │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 8 个模块 / 8 modules）。

### L2 领域层 / Domain Layer (8 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/ml_serve/__init__.py | src/zephyr/ml_serve/__init__.py | prototype | deprecated |
| 2 | src/zephyr/ml_serve/_extensions/__init__.py | src/zephyr/ml_serve/_extensions/__ini... | prototype | deprecated |
| 3 | src/zephyr/ml_serve/api/__init__.py | src/zephyr/ml_serve/api/__init__.py | prototype | deprecated |
| 4 | src/zephyr/ml_serve/core/__init__.py | src/zephyr/ml_serve/core/__init__.py | prototype | deprecated |
| 5 | src/zephyr/ml_serve/infrastructure/__init__.py | src/zephyr/ml_serve/infrastructure/__... | prototype | deprecated |
| 6 | src/zephyr/ml_serve/models/__init__.py | src/zephyr/ml_serve/models/__init__.py | prototype | deprecated |
| 7 | src/zephyr/ml_serve/services/__init__.py | src/zephyr/ml_serve/services/__init__.py | prototype | deprecated |
| 8 | 推理域/D-ML-136 | 推理熔断器 | design | planned |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 0 条 / 0 edges）。按依赖类型分组，使用 → 表示方向。

（无域内依赖 / No internal dependencies）


## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `42_d_ml_serve_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
