---
doc_type: architecture_view
title: D_REPORTING 报告架构文档
version: "1.0"
status: active
date: 2026-07-17
owner: auto-generator
ttl: permanent
---

# 23_d_reporting / 报告 / 报告 / Reporting

> **功能简介 / Overview**: 报告，负责投资报告、风险报告和合规报告的生成与分发

> **文档作用 / Purpose**: 展示 报告（D_REPORTING）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-17 03:12:24
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 23 | Number | 23 |
| 域ID | D_REPORTING | Domain ID | D_REPORTING |
| 域名称 | 报告 | Domain Name | Reporting |
| 层级 | L1 基础平台层 | Layer | L1 Foundation |
| 模块数 | 10 | Module Count | 10 |
| 域内依赖 | 3 | Internal Dependencies | 3 |
| 跨域入边 | 4 | Cross-domain Incoming | 4 |
| 跨域出边 | 9 | Cross-domain Outgoing | 9 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 9 | Prototype Modules | 9 |
| 生产态模块 | 1 | Production Modules | 1 |
| 容量 | 1/150 (正常) | Capacity | 1/150 (正常) |
| 描述 | 绩效报告、风险报告、合规报告、自定义报表。数据呈现层。 | Description | 绩效报告、风险报告、合规报告、自定义报表。数据呈现层。 |

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 10 个模块 / 10 modules）。

### L1 基础层 / Foundation Layer (10 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/reporting/__init__.py | D_REPORTING Post-Trade Analytics | 原型态 / prototype | [MOD-L07-001](../../03_modules/_domain_reporting/blueprint.md) |
| 2 | src/zephyr/reporting/_extensions/__init__.py | __init__.py | 原型态 / prototype |  |
| 3 | src/zephyr/reporting/analytics_base.py | D_REPORTING — Post-Trade Analytics Layer | 生产态 / production | [MOD-L07-001](../../03_modules/_domain_reporting/blueprint.md) |
| 4 | src/zephyr/reporting/api/__init__.py | __init__.py | 原型态 / prototype |  |
| 5 | src/zephyr/reporting/core/__init__.py | __init__.py | 原型态 / prototype |  |
| 6 | src/zephyr/reporting/default_attribution_engine.py | D_REPORTING — Default Attribution Engine | 原型态 / prototype | [MOD-L07-001](../../03_modules/_domain_reporting/blueprint.md) |
| 7 | src/zephyr/reporting/default_tca_engine.py | D_REPORTING — Default TCA Engine | 原型态 / prototype | [MOD-L07-001](../../03_modules/_domain_reporting/blueprint.md) |
| 8 | src/zephyr/reporting/infrastructure/__init__.py | __init__.py | 原型态 / prototype |  |
| 9 | src/zephyr/reporting/models/__init__.py | __init__.py | 原型态 / prototype |  |
| 10 | src/zephyr/reporting/services/__init__.py | __init__.py | 原型态 / prototype |  |

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

> 展示全部 10 个模块（生产态 1 + 设计态 0 + 原型态 9），标签标注成熟度。

```mermaid
graph TD
    subgraph D_REPORTING["D_REPORTING 报告"]
        src_zephyr_reporting_init_py["(原型态 / prototype) D_REPORTING Post-Trade Analytics<br/>文件: __init__.py"]
        src_zephyr_reporting_extensions_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_reporting_analytics_base_py["(生产态 / production) D_REPORTING — Post-Trade Analytics Layer<br/>文件: analytics_base.py"]
        src_zephyr_reporting_api_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_reporting_core_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_reporting_default_attribution_engine_py["(原型态 / prototype) D_REPORTING — Default Attribution Engine<br/>文件: default_attribution_engine.py"]
        src_zephyr_reporting_default_tca_engine_py["(原型态 / prototype) D_REPORTING — Default TCA Engine<br/>文件: default_tca_engine.py"]
        src_zephyr_reporting_infrastructure_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_reporting_models_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_reporting_services_init_py["(原型态 / prototype) __init__.py"]
    end
    src_zephyr_reporting_default_attribution_engine_py -.->|导入依赖 / import_depends| src_zephyr_reporting_analytics_base_py
    src_zephyr_reporting_default_tca_engine_py -.->|导入依赖 / import_depends| src_zephyr_reporting_analytics_base_py
    src_zephyr_reporting_init_py -.->|导入依赖 / import_depends| src_zephyr_reporting_analytics_base_py
    D_INFRASTRUCTURE["(生产态 / production) D_INFRASTRUCTURE"]
    src_zephyr_reporting_default_attribution_engine_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_reporting_analytics_base_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_reporting_analytics_base_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_reporting_analytics_base_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_reporting_analytics_base_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_reporting_default_tca_engine_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_reporting_default_tca_engine_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_reporting_default_tca_engine_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_reporting_init_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    D_GOV_AUDIT["(原型态 / prototype) D_GOV_AUDIT"]
    D_GOV_AUDIT -.->|导入依赖 / import_depends| src_zephyr_reporting_default_attribution_engine_py
    D_GOV_AUDIT -.->|导入依赖 / import_depends| src_zephyr_reporting_default_tca_engine_py
    D_GOVERNANCE["(原型态 / prototype) D_GOVERNANCE"]
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_reporting_analytics_base_py
    D_TRADING["(原型态 / prototype) D_TRADING"]
    D_TRADING -.->|测试依赖 / test_depends| src_zephyr_reporting_analytics_base_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_reporting_analytics_base_py production
    class src_zephyr_reporting_init_py,src_zephyr_reporting_extensions_init_py,src_zephyr_reporting_api_init_py,src_zephyr_reporting_core_init_py,src_zephyr_reporting_default_attribution_engine_py,src_zephyr_reporting_default_tca_engine_py,src_zephyr_reporting_infrastructure_init_py,src_zephyr_reporting_models_init_py,src_zephyr_reporting_services_init_py design
    class D_INFRASTRUCTURE external_prod
    class D_GOV_AUDIT,D_GOVERNANCE,D_TRADING external_design
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 仅展示已上线运行的模块（共 1 个，0 条域内依赖）。

```mermaid
graph TD
    subgraph D_REPORTING["D_REPORTING 报告"]
        src_zephyr_reporting_analytics_base_py["(生产态 / production) D_REPORTING — Post-Trade Analytics Layer<br/>文件: analytics_base.py"]
    end
    D_INFRASTRUCTURE["(生产态 / production) D_INFRASTRUCTURE"]
    src_zephyr_reporting_analytics_base_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_reporting_analytics_base_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_reporting_analytics_base_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_reporting_analytics_base_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    D_GOVERNANCE["(原型态 / prototype) D_GOVERNANCE"]
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_reporting_analytics_base_py
    D_TRADING["(原型态 / prototype) D_TRADING"]
    D_TRADING -.->|测试依赖 / test_depends| src_zephyr_reporting_analytics_base_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_reporting_analytics_base_py production
    class D_INFRASTRUCTURE external_prod
    class D_GOVERNANCE,D_TRADING external_design
```

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个，0 条域内依赖）。

> （无设计态模块 / No design modules）

### 原型态子图（仅 design_maturity=prototype 的模块和依赖）

> 仅展示代码已写、验证中未稳定上线的原型态模块（共 9 个，0 条域内依赖）。

```mermaid
graph TD
    subgraph D_REPORTING["D_REPORTING 报告"]
        src_zephyr_reporting_init_py["(原型态 / prototype) D_REPORTING Post-Trade Analytics<br/>文件: __init__.py"]
        src_zephyr_reporting_extensions_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_reporting_api_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_reporting_core_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_reporting_default_attribution_engine_py["(原型态 / prototype) D_REPORTING — Default Attribution Engine<br/>文件: default_attribution_engine.py"]
        src_zephyr_reporting_default_tca_engine_py["(原型态 / prototype) D_REPORTING — Default TCA Engine<br/>文件: default_tca_engine.py"]
        src_zephyr_reporting_infrastructure_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_reporting_models_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_reporting_services_init_py["(原型态 / prototype) __init__.py"]
    end
    D_INFRASTRUCTURE["(生产态 / production) D_INFRASTRUCTURE"]
    src_zephyr_reporting_default_attribution_engine_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_reporting_default_tca_engine_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_reporting_default_tca_engine_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_reporting_default_tca_engine_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_reporting_init_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    D_GOV_AUDIT["(原型态 / prototype) D_GOV_AUDIT"]
    D_GOV_AUDIT -.->|导入依赖 / import_depends| src_zephyr_reporting_default_attribution_engine_py
    D_GOV_AUDIT -.->|导入依赖 / import_depends| src_zephyr_reporting_default_tca_engine_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_reporting_init_py,src_zephyr_reporting_extensions_init_py,src_zephyr_reporting_api_init_py,src_zephyr_reporting_core_init_py,src_zephyr_reporting_default_attribution_engine_py,src_zephyr_reporting_default_tca_engine_py,src_zephyr_reporting_infrastructure_init_py,src_zephyr_reporting_models_init_py,src_zephyr_reporting_services_init_py design
    class D_INFRASTRUCTURE external_prod
    class D_GOV_AUDIT external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_REPORTING Post-Trade Analytics (__init__.py) | → | D_INFRASTRUCTURE: performance_attribution_report.py | 导入依赖 / import_depends |
| 2 | D_REPORTING — Post-Trade Analytics Layer (anal... | → | D_INFRASTRUCTURE: execution_report.py | 导入依赖 / import_depends |
| 3 | D_REPORTING — Post-Trade Analytics Layer (anal... | → | D_INFRASTRUCTURE: fill.py | 导入依赖 / import_depends |
| 4 | D_REPORTING — Post-Trade Analytics Layer (anal... | → | D_INFRASTRUCTURE: order.py | 导入依赖 / import_depends |
| 5 | D_REPORTING — Post-Trade Analytics Layer (anal... | → | D_INFRASTRUCTURE: performance_attribution_report.py | 导入依赖 / import_depends |
| 6 | D_REPORTING — Default Attribution Engine (defa... | → | D_INFRASTRUCTURE: performance_attribution_report.py | 导入依赖 / import_depends |
| 7 | D_REPORTING — Default TCA Engine (default_tca_... | → | D_INFRASTRUCTURE: execution_report.py | 导入依赖 / import_depends |
| 8 | D_REPORTING — Default TCA Engine (default_tca_... | → | D_INFRASTRUCTURE: fill.py | 导入依赖 / import_depends |
| 9 | D_REPORTING — Default TCA Engine (default_tca_... | → | D_INFRASTRUCTURE: order.py | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_GOVERNANCE 生命周期管理: Re-export wrapper: analytics_base canonical at ... | → | D_REPORTING — Post-Trade Analytics Layer (anal... | 导入依赖 / import_depends |
| 2 | D_GOV_AUDIT 审计追踪: Re-export wrapper: default_attribution_engine c... | → | D_REPORTING — Default Attribution Engine (defa... | 导入依赖 / import_depends |
| 3 | D_GOV_AUDIT 审计追踪: Re-export wrapper: default_tca_engine canonical... | → | D_REPORTING — Default TCA Engine (default_tca_... | 导入依赖 / import_depends |
| 4 | D_TRADING 交易运营: test_l07_post_trade_analytics.py | → | D_REPORTING — Post-Trade Analytics Layer (anal... | 测试依赖 / test_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 4 个外部域直接连接（出边 9 条 + 入边 4 条 = 13 条）。只显示直接连接的域，不展开具体节点。

```mermaid
graph LR
    D_REPORTING["D_REPORTING<br/>报告"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE"]
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_REPORTING -->|9条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_GOV_AUDIT -->|2条 导入依赖 / import_depends| D_REPORTING
    D_GOVERNANCE -->|1条 导入依赖 / import_depends| D_REPORTING
    D_TRADING -->|1条 测试依赖 / test_depends| D_REPORTING
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
