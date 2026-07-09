---
doc_type: architecture_view
title: D_DATA_ENG 数据工程架构文档
version: "1.0"
status: active
date: 2026-07-09
owner: auto-generator
ttl: permanent
---

# 08_d_data_eng / 数据工程 / 数据工程 / Data Engineering

> **功能简介 / Overview**: 数据工程，负责数据管道编排、ETL 流程和数据质量监控

> **文档作用 / Purpose**: 展示 数据工程（D_DATA_ENG）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-09 17:54:19
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 08 | Number | 08 |
| 域ID | D_DATA_ENG | Domain ID | D_DATA_ENG |
| 域名称 | 数据工程 | Domain Name | Data Engineering |
| 层级 | L1 基础平台层 | Layer | L1 Foundation |
| 模块数 | 7 | Module Count | 7 |
| 域内依赖 | 0 | Internal Dependencies | 0 |
| 跨域入边 | 0 | Cross-domain Incoming | 0 |
| 跨域出边 | 0 | Cross-domain Outgoing | 0 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 7 | Prototype Modules | 7 |
| 生产态模块 | 0 | Production Modules | 0 |
| 容量 | 0/150 (正常) | Capacity | 0/150 (正常) |
| 描述 | 数据工程域。负责数据增值处理、多源数据融合与知识提取，包括ETL管线、特征工程、数据融合引擎、知识图谱构建。拆分自原D-DATA域。 | Description | 数据工程域。负责数据增值处理、多源数据融合与知识提取，包括ETL管线、特征工程、数据融合引擎、知识图谱构建。拆分自原D-DATA域。 |

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 7 个模块 / 7 modules）。

### L1 基础层 / Foundation Layer (7 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/data_eng/__init__.py | __init__.py | 原型态 / prototype |  |
| 2 | src/zephyr/data_eng/_extensions/__init__.py | __init__.py | 原型态 / prototype |  |
| 3 | src/zephyr/data_eng/api/__init__.py | __init__.py | 原型态 / prototype |  |
| 4 | src/zephyr/data_eng/core/__init__.py | __init__.py | 原型态 / prototype |  |
| 5 | src/zephyr/data_eng/infrastructure/__init__.py | __init__.py | 原型态 / prototype |  |
| 6 | src/zephyr/data_eng/models/__init__.py | __init__.py | 原型态 / prototype |  |
| 7 | src/zephyr/data_eng/services/__init__.py | __init__.py | 原型态 / prototype |  |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。参考 decision_index.md 设计，分四个视图：合并全景图、运营态子图、设计态子图、原型态子图（按 design_maturity 实际值拆分）。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，蓝图阶段，代码未写）
> - **虚线边框 = 原型态模块**（prototype，代码已写，验证中未稳定上线）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 合并全景图（全部模块，标签标注成熟度）

> 展示全部 7 个模块（生产态 0 + 设计态 0 + 原型态 7），标签标注成熟度。

```mermaid
graph TD
    subgraph D_DATA_ENG["D_DATA_ENG 数据工程"]
        src_zephyr_data_eng_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_data_eng_extensions_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_data_eng_api_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_data_eng_core_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_data_eng_infrastructure_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_data_eng_models_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_data_eng_services_init_py["(原型态 / prototype) __init__.py"]
    end
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_data_eng_init_py,src_zephyr_data_eng_extensions_init_py,src_zephyr_data_eng_api_init_py,src_zephyr_data_eng_core_init_py,src_zephyr_data_eng_infrastructure_init_py,src_zephyr_data_eng_models_init_py,src_zephyr_data_eng_services_init_py design
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 仅展示已上线运行的模块（共 0 个，0 条域内依赖）。

> （无运营态模块 / No production modules）

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个，0 条域内依赖）。

> （无设计态模块 / No design modules）

### 原型态子图（仅 design_maturity=prototype 的模块和依赖）

> 仅展示代码已写、验证中未稳定上线的原型态模块（共 7 个，0 条域内依赖）。

```mermaid
graph TD
    subgraph D_DATA_ENG["D_DATA_ENG 数据工程"]
        src_zephyr_data_eng_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_data_eng_extensions_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_data_eng_api_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_data_eng_core_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_data_eng_infrastructure_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_data_eng_models_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_data_eng_services_init_py["(原型态 / prototype) __init__.py"]
    end
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_data_eng_init_py,src_zephyr_data_eng_extensions_init_py,src_zephyr_data_eng_api_init_py,src_zephyr_data_eng_core_init_py,src_zephyr_data_eng_infrastructure_init_py,src_zephyr_data_eng_models_init_py,src_zephyr_data_eng_services_init_py design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

无跨域出边依赖 / No cross-domain outgoing dependencies

### 依赖本域的其他域（入边）/ Depended By

无跨域入边依赖 / No cross-domain incoming dependencies

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 0 个外部域直接连接（出边 0 条 + 入边 0 条 = 0 条）。只显示直接连接的域，不展开具体节点。

> （无跨域依赖 / No cross-domain dependencies）

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
