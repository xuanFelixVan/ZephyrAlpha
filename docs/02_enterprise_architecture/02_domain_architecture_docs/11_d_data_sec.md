---
doc_type: architecture_view
title: D_DATA_SEC 数据安全与契约架构文档
version: "1.0"
status: active
date: 2026-06-29
owner: auto-generator
ttl: permanent
---

# 11_d_data_sec / 数据安全与契约

> **文档作用 / Purpose**: 展示 数据安全与契约（D_DATA_SEC）功能域的模块清单、域内依赖关系、跨域依赖关系、架构全景图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-29 17:42:20
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 11 | Number | 11 |
| 域ID | D_DATA_SEC | Domain ID | D_DATA_SEC |
| 域名称 | 数据安全与契约 | Domain Name | 数据安全与契约 |
| 层级 | L1_foundation | Layer | L1_foundation |
| 模块数 | 10 | Module Count | 10 |
| 域内依赖 | 1 | Internal Dependencies | 1 |
| 跨域入边 | 0 | Cross-domain Incoming | 0 |
| 跨域出边 | 2 | Cross-domain Outgoing | 2 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 10 | Prototype Modules | 10 |
| 生产态模块 | 0 | Production Modules | 0 |
| 容量 | 0/150 (正常) | Capacity | 0/150 (正常) |
| 描述 | 数据安全与契约域。负责数据安全策略、数据契约定义与执行，包括数据加密、访问控制、数据脱敏、数据契约验证。拆分自原D-DATA域。 | Description | 数据安全与契约域。负责数据安全策略、数据契约定义与执行，包括数据加密、访问控制、数据脱敏、数据契约验证。拆分自原D-DATA域。 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。每30个节点一组分页显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

```mermaid
graph TD
    subgraph D_DATA_SEC["D_DATA_SEC 数据安全与契约"]
        src_zephyr_data_persistence_init_py["src/zephyr/data/persistence/__init__.py prototype"]
        src_zephyr_data_persistence_circuit_breaker_types_py["src/zephyr/data/persistence/circuit_breaker_typ... prototype"]
        src_zephyr_data_persistence_sqlite_schema_py["src/zephyr/data/persistence/sqlite_schema.py prototype"]
        src_zephyr_data_security_init_py["src/zephyr/data_security/__init__.py prototype"]
        src_zephyr_data_security_extensions_init_py["src/zephyr/data_security/_extensions/__init__.py prototype"]
        src_zephyr_data_security_api_init_py["src/zephyr/data_security/api/__init__.py prototype"]
        src_zephyr_data_security_core_init_py["src/zephyr/data_security/core/__init__.py prototype"]
        src_zephyr_data_security_infrastructure_init_py["src/zephyr/data_security/infrastructure/__init_... prototype"]
        src_zephyr_data_security_models_init_py["src/zephyr/data_security/models/__init__.py prototype"]
        src_zephyr_data_security_services_init_py["src/zephyr/data_security/services/__init__.py prototype"]
    end
    src_zephyr_data_persistence_init_py -.->|config_depends| src_zephyr_data_persistence_sqlite_schema_py
    D_GOVERNANCE["D_GOVERNANCE prototype"]
    src_zephyr_data_persistence_sqlite_schema_py -.->|import_depends| D_GOVERNANCE
    D_OPS["D_OPS prototype"]
    src_zephyr_data_persistence_circuit_breaker_types_py -.->|import_depends| D_OPS
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_data_persistence_init_py,src_zephyr_data_persistence_circuit_breaker_types_py,src_zephyr_data_persistence_sqlite_schema_py,src_zephyr_data_security_init_py,src_zephyr_data_security_extensions_init_py,src_zephyr_data_security_api_init_py,src_zephyr_data_security_core_init_py,src_zephyr_data_security_infrastructure_init_py,src_zephyr_data_security_models_init_py,src_zephyr_data_security_services_init_py design
    class D_GOVERNANCE,D_OPS external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 / Target Domain | 依赖数 / Count | 依赖类型 / Type |
|--------|:---:|---------|
| D_GOVERNANCE | 1 | import_depends |
| D_OPS | 1 | import_depends |

### 依赖本域的其他域（入边）/ Depended By

无跨域入边依赖 / No cross-domain incoming dependencies

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 数据安全与契约（D_DATA_SEC）的模块分布。共 10 个模块 / 10 modules。

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
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
