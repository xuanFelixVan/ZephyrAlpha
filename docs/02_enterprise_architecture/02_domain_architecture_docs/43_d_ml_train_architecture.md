---
doc_type: architecture_view
title: D-ML_TRAIN 训练架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 43_d_ml_train / 训练 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示训练（D-ML_TRAIN）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 20:00:20
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 训练（D-ML_TRAIN）的模块分布。共 13 个模块 / 13 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│             L1 基础层 / Foundation Layer (1 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   docs__03_modules___cross_layer__model_profiler__blueprint_m... │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (12 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/ml_train/__init__.py  [prototype]                   │
│   src/zephyr/ml_train/_extensions/__init__.py  [prototype]       │
│   src/zephyr/ml_train/api/__init__.py  [prototype]               │
│   src/zephyr/ml_train/core/__init__.py  [prototype]              │
│   src/zephyr/ml_train/implementations/__init__.py  [prototype]   │
│   src/zephyr/ml_train/implementations/default_inference_engin... │
│   src/zephyr/ml_train/inference_base.py  [prototype]             │
│   src/zephyr/ml_train/infrastructure/__init__.py  [prototype]    │
│   src/zephyr/ml_train/models/__init__.py  [prototype]            │
│   src/zephyr/ml_train/services/__init__.py  [prototype]          │
│   src/zephyr/ml_train/trainer_base.py  [prototype]               │
│   Barra Risk Factor Model  [design]                              │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 13 个模块 / 13 modules）。

### L1 基础层 / Foundation Layer (1 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | docs__03_modules___cross_layer__model... | design | planned |

### L2 领域层 / Domain Layer (12 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/ml_train/__init__.py | src/zephyr/ml_train/__init__.py | prototype | generated |
| 2 | src/zephyr/ml_train/_extensions/__init__.py | src/zephyr/ml_train/_extensions/__ini... | prototype | deprecated |
| 3 | src/zephyr/ml_train/api/__init__.py | src/zephyr/ml_train/api/__init__.py | prototype | deprecated |
| 4 | src/zephyr/ml_train/core/__init__.py | src/zephyr/ml_train/core/__init__.py | prototype | deprecated |
| 5 | src/zephyr/ml_train/implementations/__init__.py | src/zephyr/ml_train/implementations/_... | prototype | generated |
| 6 | src/zephyr/ml_train/implementations/default_inference_eng... | src/zephyr/ml_train/implementations/d... | prototype | generated |
| 7 | src/zephyr/ml_train/inference_base.py | src/zephyr/ml_train/inference_base.py | prototype | generated |
| 8 | src/zephyr/ml_train/infrastructure/__init__.py | src/zephyr/ml_train/infrastructure/__... | prototype | deprecated |
| 9 | src/zephyr/ml_train/models/__init__.py | src/zephyr/ml_train/models/__init__.py | prototype | deprecated |
| 10 | src/zephyr/ml_train/services/__init__.py | src/zephyr/ml_train/services/__init__.py | prototype | deprecated |
| 11 | src/zephyr/ml_train/trainer_base.py | src/zephyr/ml_train/trainer_base.py | prototype | generated |
| 12 | 训练域/D-ML-106 | Barra Risk Factor Model | design | planned |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 5 条 / 5 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│        依赖关系图 / Dependency Graph (共 5 条 / 5 edges)         │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [import_depends]: 4 条 / edges                                 │
│   [config_depends]: 1 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (4 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   inference_base.py → trainer_base.py                            │
│   default_inference_engine.py → trainer_base.py                  │
│   default_inference_engine.py → inference_base.py                │
│   __init__.py → default_inference_engine.py                      │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (1 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   __init__.py → trainer_base.py                                  │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `43_d_ml_train_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
