---
doc_type: architecture_view
title: D_MKT_DATA 行情数据架构文档
version: "1.0"
status: active
date: 2026-08-01
owner: auto-generator
ttl: permanent
---

# 23_d_mkt_data / 行情数据域 / Market Data

> **功能简介 / Overview**: 行情数据，负责市场行情数据的采集、分发和订阅管理

> **文档作用 / Purpose**: 展示 行情数据（D_MKT_DATA）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/23_d_mkt_data.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 23 | Number | 23 |
| 域ID | D_MKT_DATA | Domain ID | D_MKT_DATA |
| 域名称 | 行情数据 | Domain Name | Market Data |
| 层级 | L1 基础平台层 | Layer | L1 Foundation |
| 模块数 | 15 | Module Count | 15 |
| 域内依赖 | 5 | Internal Dependencies | 5 |
| 跨域入边 | 1 | Cross-domain Incoming | 1 |
| 跨域出边 | 7 | Cross-domain Outgoing | 7 |
| 设计态模块 | 6 | Design Modules | 6 |
| 生产态模块 | 9 | Production Modules | 9 |
| 容量 | 9/150 (正常) | Capacity | 9/150 (正常) |
| 描述 | 行情数据，负责市场行情数据的采集、分发和订阅管理 | Description | 行情数据，负责市场行情数据的采集、分发和订阅管理 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，共三个图：全景图、运营态图、设计态图。大图在 MD 预览可能渲染失败，请用可缩放 HTML 版查看（已放开渲染上限，浏览器可正常渲染 + Ctrl+滚轮缩放 + 拖动平移）。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块）

> 展示全部 15 个模块（生产态 9 + 设计态 6），节点含成熟度+中英文名+大白话+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_market_data_init_py["(生产态 / production)<br/>文件: market_data/__init__.py"]
    src_zephyr_market_data_extensions_init_py["(生产态 / production)<br/>文件: _extensions/__init__.py"]
    src_zephyr_market_data_api_init_py["(生产态 / production)<br/>文件: api/__init__.py"]
    src_zephyr_market_data_autoload_py["(设计态 / design)<br/>文件: market_data/autoload.py"]
    src_zephyr_market_data_connectors["(设计态 / design)<br/>文件: connectors/"]
    src_zephyr_market_data_core_init_py["(生产态 / production)<br/>文件: core/__init__.py"]
    src_zephyr_market_data_failover["(设计态 / design)<br/>文件: failover/"]
    src_zephyr_market_data_infrastructure_init_py["(生产态 / production)<br/>文件: infrastructure/__init__.py"]
    src_zephyr_market_data_models_init_py["(生产态 / production)<br/>文件: models/__init__.py"]
    src_zephyr_market_data_normalized_market_data_producer_init_py["(生产态 / production) NormalizedMarketData 生产者包——D_MKT_DATA→D_FACTOR 数据供给。<br/>NormalizedMarketData 生产者包——D_MKT_DATA→D_FACTOR 数据供给。<br/>文件: normalized_market_data_producer/__init__.py"]
    src_zephyr_market_data_services_init_py["(生产态 / production)<br/>文件: services/__init__.py"]
    src_zephyr_market_data_init_py ~~~ src_zephyr_market_data_extensions_init_py
    src_zephyr_market_data_extensions_init_py ~~~ src_zephyr_market_data_api_init_py
    src_zephyr_market_data_api_init_py ~~~ src_zephyr_market_data_autoload_py
    src_zephyr_market_data_autoload_py ~~~ src_zephyr_market_data_connectors
    src_zephyr_market_data_connectors ~~~ src_zephyr_market_data_core_init_py
    src_zephyr_market_data_core_init_py ~~~ src_zephyr_market_data_failover
    src_zephyr_market_data_failover ~~~ src_zephyr_market_data_infrastructure_init_py
    src_zephyr_market_data_infrastructure_init_py ~~~ src_zephyr_market_data_models_init_py
    src_zephyr_market_data_models_init_py ~~~ src_zephyr_market_data_normalized_market_data_producer_init_py
    src_zephyr_market_data_normalized_market_data_producer_init_py ~~~ src_zephyr_market_data_services_init_py
    src_zephyr_market_data_normalized_market_data_producer_producer_py["(生产态 / production) NormalizedMarketData 生产者——D_MKT_DATA→D_FACTOR 数据供给。<br/>NormalizedMarketData 生产者——D_MKT_DATA→D_FACTOR 数据供给。<br/>文件: normalized_market_data_producer/producer.py"]
    src_zephyr_market_data_vendor_registry_py["(设计态 / design)<br/>文件: market_data/vendor_registry.py"]
    src_zephyr_market_data_normalized_market_data_producer_producer_py ~~~ src_zephyr_market_data_vendor_registry_py
    src_zephyr_market_data_raw_data_cache["(设计态 / design)<br/>文件: raw_data_cache/"]
    src_zephyr_market_data_vendor_base_py["(设计态 / design)<br/>文件: market_data/vendor_base.py"]
    src_zephyr_market_data_raw_data_cache ~~~ src_zephyr_market_data_vendor_base_py
    src_zephyr_market_data_vendor_registry_py -.->|import / import| src_zephyr_market_data_vendor_base_py
    src_zephyr_market_data_connectors -.->|import / import| src_zephyr_market_data_vendor_base_py
    src_zephyr_market_data_autoload_py -.->|runtime / runtime| src_zephyr_market_data_vendor_registry_py
    src_zephyr_market_data_normalized_market_data_producer_init_py -->|导入依赖 / import_depends| src_zephyr_market_data_normalized_market_data_producer_producer_py
    src_zephyr_market_data_normalized_market_data_producer_producer_py -.->|data / data| src_zephyr_market_data_raw_data_cache
    D_DATA["(生产态 / production) 数据接入层 / Data Access Layer<br/>数据接入层，负责数据源接入、数据集成和数据标准化<br/>跨域节点 / cross-domain"]
    src_zephyr_market_data_raw_data_cache -.->|data / data| D_DATA
    src_zephyr_market_data_autoload_py -.->|runtime / runtime| D_DATA
    src_zephyr_market_data_normalized_market_data_producer_producer_py -->|导入依赖 / import_depends| D_DATA
    src_zephyr_market_data_normalized_market_data_producer_producer_py -->|导入依赖 / import_depends| D_DATA
    src_zephyr_market_data_normalized_market_data_producer_producer_py -->|导入依赖 / import_depends| D_DATA
    D_INFRASTRUCTURE["(生产态 / production) 跨层契约基础设施 / Cross-Layer Contract Infrastructure<br/>跨层契约基础设施，负责跨层契约定义、共享契约管理和契约校验<br/>跨域节点 / cross-domain"]
    src_zephyr_market_data_normalized_market_data_producer_producer_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_market_data_init_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    D_EX_SOR["(生产态 / production) 执行路由 / Execution Routing<br/>执行路由，负责订单路由、智能拆单和执行场所选择<br/>跨域节点 / cross-domain"]
    D_EX_SOR -.->|runtime / runtime| src_zephyr_market_data_failover
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_market_data_init_py,src_zephyr_market_data_extensions_init_py,src_zephyr_market_data_api_init_py,src_zephyr_market_data_core_init_py,src_zephyr_market_data_infrastructure_init_py,src_zephyr_market_data_models_init_py,src_zephyr_market_data_normalized_market_data_producer_init_py,src_zephyr_market_data_normalized_market_data_producer_producer_py,src_zephyr_market_data_services_init_py production
    class src_zephyr_market_data_autoload_py,src_zephyr_market_data_connectors,src_zephyr_market_data_failover,src_zephyr_market_data_raw_data_cache,src_zephyr_market_data_vendor_base_py,src_zephyr_market_data_vendor_registry_py design
    class D_DATA,D_INFRASTRUCTURE,D_EX_SOR external_prod
```

### 运营态图（仅 production 模块）

> 仅展示已上线运行的模块（共 9 个，1 条域内依赖）。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_market_data_init_py["(生产态 / production)<br/>文件: market_data/__init__.py"]
    src_zephyr_market_data_extensions_init_py["(生产态 / production)<br/>文件: _extensions/__init__.py"]
    src_zephyr_market_data_api_init_py["(生产态 / production)<br/>文件: api/__init__.py"]
    src_zephyr_market_data_core_init_py["(生产态 / production)<br/>文件: core/__init__.py"]
    src_zephyr_market_data_infrastructure_init_py["(生产态 / production)<br/>文件: infrastructure/__init__.py"]
    src_zephyr_market_data_models_init_py["(生产态 / production)<br/>文件: models/__init__.py"]
    src_zephyr_market_data_normalized_market_data_producer_init_py["(生产态 / production) NormalizedMarketData 生产者包——D_MKT_DATA→D_FACTOR 数据供给。<br/>NormalizedMarketData 生产者包——D_MKT_DATA→D_FACTOR 数据供给。<br/>文件: normalized_market_data_producer/__init__.py"]
    src_zephyr_market_data_services_init_py["(生产态 / production)<br/>文件: services/__init__.py"]
    src_zephyr_market_data_init_py ~~~ src_zephyr_market_data_extensions_init_py
    src_zephyr_market_data_extensions_init_py ~~~ src_zephyr_market_data_api_init_py
    src_zephyr_market_data_api_init_py ~~~ src_zephyr_market_data_core_init_py
    src_zephyr_market_data_core_init_py ~~~ src_zephyr_market_data_infrastructure_init_py
    src_zephyr_market_data_infrastructure_init_py ~~~ src_zephyr_market_data_models_init_py
    src_zephyr_market_data_models_init_py ~~~ src_zephyr_market_data_normalized_market_data_producer_init_py
    src_zephyr_market_data_normalized_market_data_producer_init_py ~~~ src_zephyr_market_data_services_init_py
    src_zephyr_market_data_normalized_market_data_producer_producer_py["(生产态 / production) NormalizedMarketData 生产者——D_MKT_DATA→D_FACTOR 数据供给。<br/>NormalizedMarketData 生产者——D_MKT_DATA→D_FACTOR 数据供给。<br/>文件: normalized_market_data_producer/producer.py"]
    src_zephyr_market_data_normalized_market_data_producer_init_py -->|导入依赖 / import_depends| src_zephyr_market_data_normalized_market_data_producer_producer_py
    D_DATA["(生产态 / production) 数据接入层 / Data Access Layer<br/>数据接入层，负责数据源接入、数据集成和数据标准化<br/>跨域节点 / cross-domain"]
    src_zephyr_market_data_normalized_market_data_producer_producer_py -->|导入依赖 / import_depends| D_DATA
    src_zephyr_market_data_normalized_market_data_producer_producer_py -->|导入依赖 / import_depends| D_DATA
    src_zephyr_market_data_normalized_market_data_producer_producer_py -->|导入依赖 / import_depends| D_DATA
    D_INFRASTRUCTURE["(生产态 / production) 跨层契约基础设施 / Cross-Layer Contract Infrastructure<br/>跨层契约基础设施，负责跨层契约定义、共享契约管理和契约校验<br/>跨域节点 / cross-domain"]
    src_zephyr_market_data_normalized_market_data_producer_producer_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_market_data_init_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_market_data_init_py,src_zephyr_market_data_extensions_init_py,src_zephyr_market_data_api_init_py,src_zephyr_market_data_core_init_py,src_zephyr_market_data_infrastructure_init_py,src_zephyr_market_data_models_init_py,src_zephyr_market_data_normalized_market_data_producer_init_py,src_zephyr_market_data_normalized_market_data_producer_producer_py,src_zephyr_market_data_services_init_py production
    class D_DATA,D_INFRASTRUCTURE external_prod
```

### 设计态图（仅 design 模块）

> 仅展示蓝图阶段、代码未写的设计态模块（共 6 个，3 条域内依赖）。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_market_data_autoload_py["(设计态 / design)<br/>文件: market_data/autoload.py"]
    src_zephyr_market_data_connectors["(设计态 / design)<br/>文件: connectors/"]
    src_zephyr_market_data_failover["(设计态 / design)<br/>文件: failover/"]
    src_zephyr_market_data_raw_data_cache["(设计态 / design)<br/>文件: raw_data_cache/"]
    src_zephyr_market_data_autoload_py ~~~ src_zephyr_market_data_connectors
    src_zephyr_market_data_connectors ~~~ src_zephyr_market_data_failover
    src_zephyr_market_data_failover ~~~ src_zephyr_market_data_raw_data_cache
    src_zephyr_market_data_vendor_registry_py["(设计态 / design)<br/>文件: market_data/vendor_registry.py"]
    src_zephyr_market_data_vendor_base_py["(设计态 / design)<br/>文件: market_data/vendor_base.py"]
    src_zephyr_market_data_vendor_registry_py -.->|import / import| src_zephyr_market_data_vendor_base_py
    src_zephyr_market_data_connectors -.->|import / import| src_zephyr_market_data_vendor_base_py
    src_zephyr_market_data_autoload_py -.->|runtime / runtime| src_zephyr_market_data_vendor_registry_py
    D_DATA["(生产态 / production) 数据接入层 / Data Access Layer<br/>数据接入层，负责数据源接入、数据集成和数据标准化<br/>跨域节点 / cross-domain"]
    src_zephyr_market_data_autoload_py -.->|runtime / runtime| D_DATA
    src_zephyr_market_data_raw_data_cache -.->|data / data| D_DATA
    D_EX_SOR["(生产态 / production) 执行路由 / Execution Routing<br/>执行路由，负责订单路由、智能拆单和执行场所选择<br/>跨域节点 / cross-domain"]
    D_EX_SOR -.->|runtime / runtime| src_zephyr_market_data_failover
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_market_data_autoload_py,src_zephyr_market_data_connectors,src_zephyr_market_data_failover,src_zephyr_market_data_raw_data_cache,src_zephyr_market_data_vendor_base_py,src_zephyr_market_data_vendor_registry_py design
    class D_DATA,D_EX_SOR external_prod
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | NormalizedMarketData 生产者——D_MKT_DATA→D_FACTOR 数据... | → | D_DATA 数据接入层: zephyr.data — 数据源集成器（MOD-L00-004）。 (data/__init... | 导入依赖 / import_depends |
| 2 | NormalizedMarketData 生产者——D_MKT_DATA→D_FACTOR 数据... | → | D_DATA 数据接入层: ClickHouse 统一读取层（裁定 #ARCH-CH-007）。 (data/ch_rea... | 导入依赖 / import_depends |
| 3 | NormalizedMarketData 生产者——D_MKT_DATA→D_FACTOR 数据... | → | D_DATA 数据接入层: 表名/品类注册表消费层（裁定 #ARCH-CH-024 Phase 2）。 (dat... | 导入依赖 / import_depends |
| 4 | market_data/__init__.py | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/market_data.py | 导入依赖 / import_depends |
| 5 | NormalizedMarketData 生产者——D_MKT_DATA→D_FACTOR 数据... | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/market_data.py | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

无跨域入边依赖 / No cross-domain incoming dependencies

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 3 个外部域直接连接（出边 7 条 + 入边 1 条 = 8 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_MKT_DATA["D_MKT_DATA<br/>行情数据"]
    D_DATA["D_DATA<br/>数据接入层"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE<br/>跨层契约基础设施"]
    D_EX_SOR["D_EX_SOR<br/>执行路由"]
    D_MKT_DATA -->|5条 data / data, 导入依赖 / import_depends, runtime / runtime| D_DATA
    D_MKT_DATA -->|2条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_EX_SOR -->|1条 runtime / runtime| D_MKT_DATA
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
