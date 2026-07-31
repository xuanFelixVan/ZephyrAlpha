---
doc_type: architecture_view
title: D_MKT_DATA 行情数据架构文档
version: "1.0"
status: active
date: 2026-07-31
owner: auto-generator
ttl: permanent
---

# 23_d_mkt_data / 行情数据 / Market Data

> **功能简介 / Overview**: 行情数据，负责市场行情数据的采集、分发和订阅管理

> **文档作用 / Purpose**: 展示 行情数据（D_MKT_DATA）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 23 | Number | 23 |
| 域ID | D_MKT_DATA | Domain ID | D_MKT_DATA |
| 域名称 | 行情数据 | Domain Name | Market Data |
| 层级 | L1 基础平台层 | Layer | L1 Foundation |
| 模块数 | 9 | Module Count | 9 |
| 域内依赖 | 1 | Internal Dependencies | 1 |
| 跨域入边 | 1 | Cross-domain Incoming | 1 |
| 跨域出边 | 7 | Cross-domain Outgoing | 7 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 9 | Production Modules | 9 |
| 容量 | 9/150 (正常) | Capacity | 9/150 (正常) |
| 描述 | 行情数据，负责市场行情数据的采集、分发和订阅管理 | Description | 行情数据，负责市场行情数据的采集、分发和订阅管理 |

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 9 个模块 / 9 modules）。

### L1 基础层 / Foundation Layer (9 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/market_data/__init__.py | __init__.py | 生产态 / production |  |
| 2 | src/zephyr/market_data/_extensions/__init__.py | __init__.py | 生产态 / production |  |
| 3 | src/zephyr/market_data/api/__init__.py | __init__.py | 生产态 / production |  |
| 4 | src/zephyr/market_data/core/__init__.py | __init__.py | 生产态 / production |  |
| 5 | src/zephyr/market_data/infrastructure/__init__.py | __init__.py | 生产态 / production |  |
| 6 | src/zephyr/market_data/models/__init__.py | __init__.py | 生产态 / production |  |
| 7 | src/zephyr/market_data/normalized_market_data_producer/__... | NormalizedMarketData 生产者包——D_MKT_DATA→D_... | 生产态 / production |  |
| 8 | src/zephyr/market_data/normalized_market_data_producer/pr... | NormalizedMarketData 生产者——D_MKT_DATA→D_FA... | 生产态 / production |  |
| 9 | src/zephyr/market_data/services/__init__.py | __init__.py | 生产态 / production |  |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。参考 decision_index.md 设计，分三个视图：合并全景图、运营态子图、设计态子图（按 design_maturity 实际值拆分）。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 合并全景图（全部模块，标签标注成熟度）

> 展示全部 9 个模块（生产态 9 + 设计态 0），标签标注成熟度。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_market_data_init_py["(生产态 / production) __init__.py"]
    src_zephyr_market_data_extensions_init_py["(生产态 / production) __init__.py"]
    src_zephyr_market_data_api_init_py["(生产态 / production) __init__.py"]
    src_zephyr_market_data_core_init_py["(生产态 / production) __init__.py"]
    src_zephyr_market_data_infrastructure_init_py["(生产态 / production) __init__.py"]
    src_zephyr_market_data_models_init_py["(生产态 / production) __init__.py"]
    src_zephyr_market_data_normalized_market_data_producer_init_py["(生产态 / production) NormalizedMarketData 生产者包——D_MKT_DATA→D_...<br/>文件: __init__.py"]
    src_zephyr_market_data_services_init_py["(生产态 / production) __init__.py"]
    src_zephyr_market_data_init_py ~~~ src_zephyr_market_data_extensions_init_py
    src_zephyr_market_data_extensions_init_py ~~~ src_zephyr_market_data_api_init_py
    src_zephyr_market_data_api_init_py ~~~ src_zephyr_market_data_core_init_py
    src_zephyr_market_data_core_init_py ~~~ src_zephyr_market_data_infrastructure_init_py
    src_zephyr_market_data_infrastructure_init_py ~~~ src_zephyr_market_data_models_init_py
    src_zephyr_market_data_models_init_py ~~~ src_zephyr_market_data_normalized_market_data_producer_init_py
    src_zephyr_market_data_normalized_market_data_producer_init_py ~~~ src_zephyr_market_data_services_init_py
    src_zephyr_market_data_normalized_market_data_producer_producer_py["(生产态 / production) NormalizedMarketData 生产者——D_MKT_DATA→D_FA...<br/>文件: producer.py"]
    src_zephyr_market_data_normalized_market_data_producer_init_py -->|导入依赖 / import_depends| src_zephyr_market_data_normalized_market_data_producer_producer_py
    D_INFRASTRUCTURE["(生产态 / production) D_INFRASTRUCTURE 跨层契约基础设施"]
    src_zephyr_market_data_normalized_market_data_producer_producer_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    D_DATA["(生产态 / production) D_DATA 数据接入层"]
    src_zephyr_market_data_normalized_market_data_producer_producer_py -->|导入依赖 / import_depends| D_DATA
    src_zephyr_market_data_normalized_market_data_producer_producer_py -->|导入依赖 / import_depends| D_DATA
    src_zephyr_market_data_normalized_market_data_producer_producer_py -->|导入依赖 / import_depends| D_DATA
    src_zephyr_market_data_init_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    classDef production fill:#e8edf2,stroke:#0277bd,stroke-width:2px,color:#1a1a1a
    classDef design fill:#f0ebe3,stroke:#bf360c,stroke-width:2px,color:#1a1a1a,stroke-dasharray: 5 5
    classDef external_prod fill:#e8efe9,stroke:#1b5e20,stroke-width:1px,color:#1a1a1a
    classDef external_design fill:#efe5ea,stroke:#880e4f,stroke-width:1px,color:#1a1a1a,stroke-dasharray: 5 5
    class src_zephyr_market_data_init_py,src_zephyr_market_data_extensions_init_py,src_zephyr_market_data_api_init_py,src_zephyr_market_data_core_init_py,src_zephyr_market_data_infrastructure_init_py,src_zephyr_market_data_models_init_py,src_zephyr_market_data_normalized_market_data_producer_init_py,src_zephyr_market_data_normalized_market_data_producer_producer_py,src_zephyr_market_data_services_init_py production
    class D_INFRASTRUCTURE,D_DATA external_prod
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 仅展示已上线运行的模块（共 9 个，1 条域内依赖）。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_market_data_init_py["(生产态 / production) __init__.py"]
    src_zephyr_market_data_extensions_init_py["(生产态 / production) __init__.py"]
    src_zephyr_market_data_api_init_py["(生产态 / production) __init__.py"]
    src_zephyr_market_data_core_init_py["(生产态 / production) __init__.py"]
    src_zephyr_market_data_infrastructure_init_py["(生产态 / production) __init__.py"]
    src_zephyr_market_data_models_init_py["(生产态 / production) __init__.py"]
    src_zephyr_market_data_normalized_market_data_producer_init_py["(生产态 / production) NormalizedMarketData 生产者包——D_MKT_DATA→D_...<br/>文件: __init__.py"]
    src_zephyr_market_data_services_init_py["(生产态 / production) __init__.py"]
    src_zephyr_market_data_init_py ~~~ src_zephyr_market_data_extensions_init_py
    src_zephyr_market_data_extensions_init_py ~~~ src_zephyr_market_data_api_init_py
    src_zephyr_market_data_api_init_py ~~~ src_zephyr_market_data_core_init_py
    src_zephyr_market_data_core_init_py ~~~ src_zephyr_market_data_infrastructure_init_py
    src_zephyr_market_data_infrastructure_init_py ~~~ src_zephyr_market_data_models_init_py
    src_zephyr_market_data_models_init_py ~~~ src_zephyr_market_data_normalized_market_data_producer_init_py
    src_zephyr_market_data_normalized_market_data_producer_init_py ~~~ src_zephyr_market_data_services_init_py
    src_zephyr_market_data_normalized_market_data_producer_producer_py["(生产态 / production) NormalizedMarketData 生产者——D_MKT_DATA→D_FA...<br/>文件: producer.py"]
    src_zephyr_market_data_normalized_market_data_producer_init_py -->|导入依赖 / import_depends| src_zephyr_market_data_normalized_market_data_producer_producer_py
    D_INFRASTRUCTURE["(生产态 / production) D_INFRASTRUCTURE 跨层契约基础设施"]
    src_zephyr_market_data_normalized_market_data_producer_producer_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    D_DATA["(生产态 / production) D_DATA 数据接入层"]
    src_zephyr_market_data_normalized_market_data_producer_producer_py -->|导入依赖 / import_depends| D_DATA
    src_zephyr_market_data_normalized_market_data_producer_producer_py -->|导入依赖 / import_depends| D_DATA
    src_zephyr_market_data_normalized_market_data_producer_producer_py -->|导入依赖 / import_depends| D_DATA
    src_zephyr_market_data_init_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    classDef production fill:#e8edf2,stroke:#0277bd,stroke-width:2px,color:#1a1a1a
    classDef design fill:#f0ebe3,stroke:#bf360c,stroke-width:2px,color:#1a1a1a,stroke-dasharray: 5 5
    classDef external_prod fill:#e8efe9,stroke:#1b5e20,stroke-width:1px,color:#1a1a1a
    classDef external_design fill:#efe5ea,stroke:#880e4f,stroke-width:1px,color:#1a1a1a,stroke-dasharray: 5 5
    class src_zephyr_market_data_init_py,src_zephyr_market_data_extensions_init_py,src_zephyr_market_data_api_init_py,src_zephyr_market_data_core_init_py,src_zephyr_market_data_infrastructure_init_py,src_zephyr_market_data_models_init_py,src_zephyr_market_data_normalized_market_data_producer_init_py,src_zephyr_market_data_normalized_market_data_producer_producer_py,src_zephyr_market_data_services_init_py production
    class D_INFRASTRUCTURE,D_DATA external_prod
```

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个，0 条域内依赖）。

> （无设计态模块 / No design modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | NormalizedMarketData 生产者——D_MKT_DATA→D_FA... | → | D_DATA 数据接入层: zephyr.data — 数据源集成器（MOD-L00-004）。 (_... | 导入依赖 / import_depends |
| 2 | NormalizedMarketData 生产者——D_MKT_DATA→D_FA... | → | D_DATA 数据接入层: ClickHouse 统一读取层（裁定 #ARCH-CH-007）。 (c... | 导入依赖 / import_depends |
| 3 | NormalizedMarketData 生产者——D_MKT_DATA→D_FA... | → | D_DATA 数据接入层: 表名/品类注册表消费层（裁定 #ARCH-CH-024 Phase ... | 导入依赖 / import_depends |
| 4 | __init__.py | → | D_INFRASTRUCTURE 跨层契约基础设施: market_data.py | 导入依赖 / import_depends |
| 5 | NormalizedMarketData 生产者——D_MKT_DATA→D_FA... | → | D_INFRASTRUCTURE 跨层契约基础设施: market_data.py | 导入依赖 / import_depends |

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
