---
doc_type: architecture_view
title: D-DATA_SEC 数据安全与契约架构图
version: "1.0"
status: active
date: 2026-06-27
owner: auto-generator
ttl: permanent
---

# 11_d_data_sec / 数据安全与契约 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示数据安全与契约（D-DATA_SEC）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-27 03:08:24
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 数据安全与契约（D-DATA_SEC）的模块分布。共 10 个模块 / 10 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (10 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/data/persistence/__init__.py  [prototype]           │
│   src/zephyr/data/persistence/circuit_breaker_types.py  [prot... │
│   src/zephyr/data/persistence/sqlite_schema.py  [prototype]      │
│   src/zephyr/data_security/__init__.py  [prototype]              │
│   src/zephyr/data_security/_extensions/__init__.py  [prototype]  │
│   src/zephyr/data_security/api/__init__.py  [prototype]          │
│   src/zephyr/data_security/core/__init__.py  [prototype]         │
│   src/zephyr/data_security/infrastructure/__init__.py  [proto... │
│   src/zephyr/data_security/models/__init__.py  [prototype]       │
│   src/zephyr/data_security/services/__init__.py  [prototype]     │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 10 个模块 / 10 modules）。

### L2 领域层 / Domain Layer (10 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/data/persistence/__init__.py | src/zephyr/data/persistence/__init__.py | prototype | generated |
| 2 | src/zephyr/data/persistence/circuit_breaker_types.py | src/zephyr/data/persistence/circuit_b... | prototype | generated |
| 3 | src/zephyr/data/persistence/sqlite_schema.py | src/zephyr/data/persistence/sqlite_sc... | prototype | generated |
| 4 | src/zephyr/data_security/__init__.py | src/zephyr/data_security/__init__.py | prototype | deprecated |
| 5 | src/zephyr/data_security/_extensions/__init__.py | src/zephyr/data_security/_extensions/... | prototype | deprecated |
| 6 | src/zephyr/data_security/api/__init__.py | src/zephyr/data_security/api/__init__.py | prototype | deprecated |
| 7 | src/zephyr/data_security/core/__init__.py | src/zephyr/data_security/core/__init_... | prototype | deprecated |
| 8 | src/zephyr/data_security/infrastructure/__init__.py | src/zephyr/data_security/infrastructu... | prototype | deprecated |
| 9 | src/zephyr/data_security/models/__init__.py | src/zephyr/data_security/models/__ini... | prototype | deprecated |
| 10 | src/zephyr/data_security/services/__init__.py | src/zephyr/data_security/services/__i... | prototype | deprecated |

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
│   __init__.py → sqlite_schema.py                                 │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `11_d_data_sec_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
