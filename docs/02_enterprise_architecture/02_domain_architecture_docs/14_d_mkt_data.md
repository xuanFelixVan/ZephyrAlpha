---
doc_type: architecture_view
title: D_MKT_DATA 行情数据架构文档
version: "1.0"
status: active
date: 2026-07-06
owner: auto-generator
ttl: permanent
---

# 14_d_mkt_data / 行情数据 / Market Data

> **文档作用 / Purpose**: 展示 行情数据（D_MKT_DATA）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-06 20:48:02
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 14 | Number | 14 |
| 域ID | D_MKT_DATA | Domain ID | D_MKT_DATA |
| 域名称 | 行情数据 | Domain Name | Market Data |
| 层级 | L1 基础平台层 | Layer | L1 Foundation |
| 模块数 | 7 | Module Count | 7 |
| 域内依赖 | 0 | Internal Dependencies | 0 |
| 跨域入边 | 0 | Cross-domain Incoming | 0 |
| 跨域出边 | 1 | Cross-domain Outgoing | 1 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 7 | Prototype Modules | 7 |
| 生产态模块 | 0 | Production Modules | 0 |
| 容量 | 0/150 (正常) | Capacity | 0/150 (正常) |
| 描述 | 行情数据接入与存储域。负责市场行情数据的接入、存储与分发，包括实时行情、历史行情、多市场数据源的统一接入层。拆分自原D-DATA域。 | Description | 行情数据接入与存储域。负责市场行情数据的接入、存储与分发，包括实时行情、历史行情、多市场数据源的统一接入层。拆分自原D-DATA域。 |

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
    subgraph D_MKT_DATA["D_MKT_DATA 行情数据"]
        src_zephyr_market_data_init_py["src/zephyr/market_data/__init__.py prototype"]
        src_zephyr_market_data_extensions_init_py["src/zephyr/market_data/_extensions/__init__.py prototype"]
        src_zephyr_market_data_api_init_py["src/zephyr/market_data/api/__init__.py prototype"]
        src_zephyr_market_data_core_init_py["src/zephyr/market_data/core/__init__.py prototype"]
        src_zephyr_market_data_infrastructure_init_py["src/zephyr/market_data/infrastructure/__init__.py prototype"]
        src_zephyr_market_data_models_init_py["src/zephyr/market_data/models/__init__.py prototype"]
        src_zephyr_market_data_services_init_py["src/zephyr/market_data/services/__init__.py prototype"]
    end
    D_SHARED["D_SHARED prototype"]
    src_zephyr_market_data_init_py -.->|import_depends| D_SHARED
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_market_data_init_py,src_zephyr_market_data_extensions_init_py,src_zephyr_market_data_api_init_py,src_zephyr_market_data_core_init_py,src_zephyr_market_data_infrastructure_init_py,src_zephyr_market_data_models_init_py,src_zephyr_market_data_services_init_py design
    class D_SHARED external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 / Target Domain | 依赖数 / Count | 依赖类型 / Type |
|--------|:---:|---------|
| D_SHARED | 1 | import_depends |

### 依赖本域的其他域（入边）/ Depended By

无跨域入边依赖 / No cross-domain incoming dependencies

## 架构分层视图 / Architecture Overview

> 按 architecture_layer 分层显示 行情数据（D_MKT_DATA）的模块分布。共 7 个模块 / 7 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│             L1 基础层 / Foundation Layer (7 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/market_data/__init__.py  [prototype]                │
│   src/zephyr/market_data/_extensions/__init__.py  [prototype]    │
│   src/zephyr/market_data/api/__init__.py  [prototype]            │
│   src/zephyr/market_data/core/__init__.py  [prototype]           │
│   src/zephyr/market_data/infrastructure/__init__.py  [prototype] │
│   src/zephyr/market_data/models/__init__.py  [prototype]         │
│   src/zephyr/market_data/services/__init__.py  [prototype]       │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 7 个模块 / 7 modules）。

### L1 基础层 / Foundation Layer (7 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 功能简介 / Description | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|---------|:---:|:---:|
| 1 | src/zephyr/market_data/__init__.py | src/zephyr/market_data/__init__.py |  | prototype | generated |
| 2 | src/zephyr/market_data/_extensions/__init__.py | src/zephyr/market_data/_extensions/__... |  | prototype | generated |
| 3 | src/zephyr/market_data/api/__init__.py | src/zephyr/market_data/api/__init__.py |  | prototype | generated |
| 4 | src/zephyr/market_data/core/__init__.py | src/zephyr/market_data/core/__init__.py |  | prototype | generated |
| 5 | src/zephyr/market_data/infrastructure/__init__.py | src/zephyr/market_data/infrastructure... |  | prototype | generated |
| 6 | src/zephyr/market_data/models/__init__.py | src/zephyr/market_data/models/__init_... |  | prototype | generated |
| 7 | src/zephyr/market_data/services/__init__.py | src/zephyr/market_data/services/__ini... |  | prototype | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 0 条 / 0 edges）。按依赖类型分组，使用 → 表示方向。

（无域内依赖 / No internal dependencies）


## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
