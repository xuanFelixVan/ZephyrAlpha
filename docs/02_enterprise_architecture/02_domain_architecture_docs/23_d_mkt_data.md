---
doc_type: architecture_view
title: D_MKT_DATA 行情数据架构文档
version: "1.0"
status: active
date: 2026-08-02
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

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 15 个模块（生产态 9 + 设计态 6），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_market_data_init_py["zephyr/market_data 包入口<br/>行情数据域market_<br/>data包入口，归集子模块按需懒加载<br/>文件: market_data/__init__.py<br/>(生产态 / production)"]
    src_zephyr_market_data_extensions_init_py["market_data/_extensions 包入口<br/>行情数据域扩展层包入口，归集该层子模块按需懒加载<br/>文件: _extensions/__init__.py<br/>(生产态 / production)"]
    src_zephyr_market_data_api_init_py["market_data/api 包入口<br/>行情数据域API接口层包入口，归集该层子模块按需懒<br/>加载<br/>文件: api/__init__.py<br/>(生产态 / production)"]
    src_zephyr_market_data_autoload_py["自动加载<br/>数据的加载器，读取并加载配置/数据到内存<br/>⛔ 行情数据域，设计已就绪，等待开发排期<br/>autoload<br/>文件: market_data/autoload.py<br/>(设计态 / design)"]
    src_zephyr_market_data_connectors["连接器<br/>连接器的子目录，归集相关子模块<br/>⛔ 行情数据域，设计已就绪，等待开发排期<br/>文件: connectors/<br/>(设计态 / design)"]
    src_zephyr_market_data_core_init_py["market_data/core 包入口<br/>行情数据域核心层包入口，归集该层子模块按需懒加载<br/>文件: core/__init__.py<br/>(生产态 / production)"]
    src_zephyr_market_data_failover["故障切换<br/>故障切换的子目录，归集相关子模块<br/>⛔ 行情数据域，设计已就绪，等待开发排期<br/>文件: failover/<br/>(设计态 / design)"]
    src_zephyr_market_data_infrastructure_init_py["market_data/infrastructure 包入口<br/>行情数据域基础设施层包入口，归集该层子模块按需懒<br/>加载<br/>文件: infrastructure/__init__.py<br/>(生产态 / production)"]
    src_zephyr_market_data_models_init_py["market_data/models 包入口<br/>行情数据域模型层包入口，归集该层子模块按需懒加载<br/>文件: models/__init__.py<br/>(生产态 / production)"]
    src_zephyr_market_data_normalized_market_data_producer_init_py["market_data/normalized_market_data_producer<br/>包入口<br/>NormalizedMarketData 生产者包——D_MKT_DATA→D_<br/>FACTOR 数据供给<br/>文件: normalized_market_data_producer/__init__<br/>.py<br/>(生产态 / production)"]
    src_zephyr_market_data_services_init_py["market_data/services 包入口<br/>行情数据域服务层包入口，归集该层子模块按需懒加载<br/>文件: services/__init__.py<br/>(生产态 / production)"]
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
    src_zephyr_market_data_normalized_market_data_producer_producer_py["生产者<br/>NormalizedMarketData 生产者——D_MKT_DATA→D_<br/>FACTOR 数据供给<br/>producer<br/>文件: normalized_market_data_producer<br/>/producer.py<br/>(生产态 / production)"]
    src_zephyr_market_data_vendor_registry_py["vendor注册表<br/>数据的注册表，登记和查询已注册的条目<br/>⛔ 行情数据域，设计已就绪，等待开发排期<br/>vendor_registry<br/>文件: market_data/vendor_registry.py<br/>(设计态 / design)"]
    src_zephyr_market_data_normalized_market_data_producer_producer_py ~~~ src_zephyr_market_data_vendor_registry_py
    src_zephyr_market_data_raw_data_cache["raw数据缓存<br/>数据的子目录，归集相关子模块<br/>⛔ 行情数据域，设计已就绪，等待开发排期<br/>文件: raw_data_cache/<br/>(设计态 / design)"]
    src_zephyr_market_data_vendor_base_py["vendor基类<br/>数据的基类，定义抽象接口供子类实现<br/>⛔ 行情数据域，设计已就绪，等待开发排期<br/>vendor_base<br/>文件: market_data/vendor_base.py<br/>(设计态 / design)"]
    src_zephyr_market_data_raw_data_cache ~~~ src_zephyr_market_data_vendor_base_py
    src_zephyr_market_data_vendor_registry_py -.->|import / import| src_zephyr_market_data_vendor_base_py
    src_zephyr_market_data_connectors -.->|import / import| src_zephyr_market_data_vendor_base_py
    src_zephyr_market_data_autoload_py -.->|runtime / runtime| src_zephyr_market_data_vendor_registry_py
    src_zephyr_market_data_normalized_market_data_producer_init_py -->|导入依赖 / import_depends| src_zephyr_market_data_normalized_market_data_producer_producer_py
    src_zephyr_market_data_normalized_market_data_producer_producer_py -.->|data / data| src_zephyr_market_data_raw_data_cache
    D_DATA["数据接入层<br/>数据接入层，负责数据源接入、数据集成和数据标准化<br/>Data Access Layer<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_market_data_raw_data_cache -.->|data / data| D_DATA
    src_zephyr_market_data_autoload_py -.->|runtime / runtime| D_DATA
    src_zephyr_market_data_normalized_market_data_producer_producer_py -->|导入依赖 / import_depends| D_DATA
    src_zephyr_market_data_normalized_market_data_producer_producer_py -->|导入依赖 / import_depends| D_DATA
    src_zephyr_market_data_normalized_market_data_producer_producer_py -->|导入依赖 / import_depends| D_DATA
    D_INFRASTRUCTURE["跨层契约基础设施<br/>跨层契约基础设施，负责跨层契约定义、共享契约管理<br/>和契约校验<br/>Cross-Layer Contract Infrastructure<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_market_data_normalized_market_data_producer_producer_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_market_data_init_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    D_EX_SOR["执行路由<br/>执行路由，负责订单路由、智能拆单和执行场所选择<br/>Execution Routing<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_EX_SOR -.->|runtime / runtime| src_zephyr_market_data_failover
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_market_data_init_py,src_zephyr_market_data_extensions_init_py,src_zephyr_market_data_api_init_py,src_zephyr_market_data_core_init_py,src_zephyr_market_data_infrastructure_init_py,src_zephyr_market_data_models_init_py,src_zephyr_market_data_normalized_market_data_producer_init_py,src_zephyr_market_data_normalized_market_data_producer_producer_py,src_zephyr_market_data_services_init_py production
    class src_zephyr_market_data_autoload_py,src_zephyr_market_data_connectors,src_zephyr_market_data_failover,src_zephyr_market_data_raw_data_cache,src_zephyr_market_data_vendor_base_py,src_zephyr_market_data_vendor_registry_py design
    class D_DATA,D_INFRASTRUCTURE,D_EX_SOR external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 9 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_market_data_init_py["zephyr/market_data 包入口<br/>行情数据域market_<br/>data包入口，归集子模块按需懒加载<br/>文件: market_data/__init__.py<br/>(生产态 / production)"]
    src_zephyr_market_data_extensions_init_py["market_data/_extensions 包入口<br/>行情数据域扩展层包入口，归集该层子模块按需懒加载<br/>文件: _extensions/__init__.py<br/>(生产态 / production)"]
    src_zephyr_market_data_api_init_py["market_data/api 包入口<br/>行情数据域API接口层包入口，归集该层子模块按需懒<br/>加载<br/>文件: api/__init__.py<br/>(生产态 / production)"]
    src_zephyr_market_data_core_init_py["market_data/core 包入口<br/>行情数据域核心层包入口，归集该层子模块按需懒加载<br/>文件: core/__init__.py<br/>(生产态 / production)"]
    src_zephyr_market_data_infrastructure_init_py["market_data/infrastructure 包入口<br/>行情数据域基础设施层包入口，归集该层子模块按需懒<br/>加载<br/>文件: infrastructure/__init__.py<br/>(生产态 / production)"]
    src_zephyr_market_data_models_init_py["market_data/models 包入口<br/>行情数据域模型层包入口，归集该层子模块按需懒加载<br/>文件: models/__init__.py<br/>(生产态 / production)"]
    src_zephyr_market_data_normalized_market_data_producer_init_py["market_data/normalized_market_data_producer<br/>包入口<br/>NormalizedMarketData 生产者包——D_MKT_DATA→D_<br/>FACTOR 数据供给<br/>文件: normalized_market_data_producer/__init__<br/>.py<br/>(生产态 / production)"]
    src_zephyr_market_data_services_init_py["market_data/services 包入口<br/>行情数据域服务层包入口，归集该层子模块按需懒加载<br/>文件: services/__init__.py<br/>(生产态 / production)"]
    src_zephyr_market_data_init_py ~~~ src_zephyr_market_data_extensions_init_py
    src_zephyr_market_data_extensions_init_py ~~~ src_zephyr_market_data_api_init_py
    src_zephyr_market_data_api_init_py ~~~ src_zephyr_market_data_core_init_py
    src_zephyr_market_data_core_init_py ~~~ src_zephyr_market_data_infrastructure_init_py
    src_zephyr_market_data_infrastructure_init_py ~~~ src_zephyr_market_data_models_init_py
    src_zephyr_market_data_models_init_py ~~~ src_zephyr_market_data_normalized_market_data_producer_init_py
    src_zephyr_market_data_normalized_market_data_producer_init_py ~~~ src_zephyr_market_data_services_init_py
    src_zephyr_market_data_normalized_market_data_producer_producer_py["生产者<br/>NormalizedMarketData 生产者——D_MKT_DATA→D_<br/>FACTOR 数据供给<br/>producer<br/>文件: normalized_market_data_producer<br/>/producer.py<br/>(生产态 / production)"]
    src_zephyr_market_data_normalized_market_data_producer_init_py -->|导入依赖 / import_depends| src_zephyr_market_data_normalized_market_data_producer_producer_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_market_data_init_py,src_zephyr_market_data_extensions_init_py,src_zephyr_market_data_api_init_py,src_zephyr_market_data_core_init_py,src_zephyr_market_data_infrastructure_init_py,src_zephyr_market_data_models_init_py,src_zephyr_market_data_normalized_market_data_producer_init_py,src_zephyr_market_data_normalized_market_data_producer_producer_py,src_zephyr_market_data_services_init_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 6 个），不含跨域外部节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_market_data_autoload_py["自动加载<br/>数据的加载器，读取并加载配置/数据到内存<br/>⛔ 行情数据域，设计已就绪，等待开发排期<br/>autoload<br/>文件: market_data/autoload.py<br/>(设计态 / design)"]
    src_zephyr_market_data_connectors["连接器<br/>连接器的子目录，归集相关子模块<br/>⛔ 行情数据域，设计已就绪，等待开发排期<br/>文件: connectors/<br/>(设计态 / design)"]
    src_zephyr_market_data_failover["故障切换<br/>故障切换的子目录，归集相关子模块<br/>⛔ 行情数据域，设计已就绪，等待开发排期<br/>文件: failover/<br/>(设计态 / design)"]
    src_zephyr_market_data_raw_data_cache["raw数据缓存<br/>数据的子目录，归集相关子模块<br/>⛔ 行情数据域，设计已就绪，等待开发排期<br/>文件: raw_data_cache/<br/>(设计态 / design)"]
    src_zephyr_market_data_autoload_py ~~~ src_zephyr_market_data_connectors
    src_zephyr_market_data_connectors ~~~ src_zephyr_market_data_failover
    src_zephyr_market_data_failover ~~~ src_zephyr_market_data_raw_data_cache
    src_zephyr_market_data_vendor_registry_py["vendor注册表<br/>数据的注册表，登记和查询已注册的条目<br/>⛔ 行情数据域，设计已就绪，等待开发排期<br/>vendor_registry<br/>文件: market_data/vendor_registry.py<br/>(设计态 / design)"]
    src_zephyr_market_data_vendor_base_py["vendor基类<br/>数据的基类，定义抽象接口供子类实现<br/>⛔ 行情数据域，设计已就绪，等待开发排期<br/>vendor_base<br/>文件: market_data/vendor_base.py<br/>(设计态 / design)"]
    src_zephyr_market_data_vendor_registry_py -.->|import / import| src_zephyr_market_data_vendor_base_py
    src_zephyr_market_data_connectors -.->|import / import| src_zephyr_market_data_vendor_base_py
    src_zephyr_market_data_autoload_py -.->|runtime / runtime| src_zephyr_market_data_vendor_registry_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_market_data_autoload_py,src_zephyr_market_data_connectors,src_zephyr_market_data_failover,src_zephyr_market_data_raw_data_cache,src_zephyr_market_data_vendor_base_py,src_zephyr_market_data_vendor_registry_py design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 自动加载 / autoload (market_data/autoload.py) | → | D_DATA 数据接入层: table注册表 / table_registry (data/table_registry.py) | runtime / runtime |
| 2 | 生产者 / producer (normalized_market_data_producer/produc... | → | D_DATA 数据接入层: 包入口 / __init__ (data/__init__.py) | 导入依赖 / import_depends |
| 3 | 生产者 / producer (normalized_market_data_producer/produc... | → | D_DATA 数据接入层: ch读取器 / ch_reader (data/ch_reader.py) | 导入依赖 / import_depends |
| 4 | 生产者 / producer (normalized_market_data_producer/produc... | → | D_DATA 数据接入层: table注册表 / table_registry (data/table_registry.py) | 导入依赖 / import_depends |
| 5 | raw数据缓存 (raw_data_cache/) | → | D_DATA 数据接入层: 提供器基类 / provider_base (data/provider_base.py) | data / data |
| 6 | 包入口 / __init__ (market_data/__init__.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: 市场数据 / market_data (contracts/market_data.py) | 导入依赖 / import_depends |
| 7 | 生产者 / producer (normalized_market_data_producer/produc... | → | D_INFRASTRUCTURE 跨层契约基础设施: 市场数据 / market_data (contracts/market_data.py) | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_EX_SOR 执行路由: 包入口 / __init__ (core/__init__.py) | → | 故障切换 (failover/) | runtime / runtime |

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
