---
doc_type: architecture_view
title: D_REPORTING 报告架构文档
version: "1.0"
status: active
date: 2026-07-05
owner: auto-generator
ttl: permanent
---

# 16_d_reporting / 报告

> **文档作用 / Purpose**: 展示 报告（D_REPORTING）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-05 22:59:51
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 16 | Number | 16 |
| 域ID | D_REPORTING | Domain ID | D_REPORTING |
| 域名称 | 报告 | Domain Name | 报告 |
| 层级 | L1_foundation | Layer | L1_foundation |
| 模块数 | 10 | Module Count | 10 |
| 域内依赖 | 0 | Internal Dependencies | 0 |
| 跨域入边 | 3 | Cross-domain Incoming | 3 |
| 跨域出边 | 9 | Cross-domain Outgoing | 9 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 9 | Prototype Modules | 9 |
| 生产态模块 | 1 | Production Modules | 1 |
| 容量 | 1/150 (正常) | Capacity | 1/150 (正常) |
| 描述 | 绩效报告、风险报告、合规报告、自定义报表。数据呈现层。 | Description | 绩效报告、风险报告、合规报告、自定义报表。数据呈现层。 |

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
    subgraph D_REPORTING["D_REPORTING 报告"]
        src_zephyr_reporting_init_py["src/zephyr/reporting/__init__.py prototype"]
        src_zephyr_reporting_extensions_init_py["src/zephyr/reporting/_extensions/__init__.py prototype"]
        src_zephyr_reporting_analytics_base_py["src/zephyr/reporting/analytics_base.py production"]
        src_zephyr_reporting_api_init_py["src/zephyr/reporting/api/__init__.py prototype"]
        src_zephyr_reporting_core_init_py["src/zephyr/reporting/core/__init__.py prototype"]
        src_zephyr_reporting_default_attribution_engine_py["src/zephyr/reporting/default_attribution_engine.py prototype"]
        src_zephyr_reporting_default_tca_engine_py["src/zephyr/reporting/default_tca_engine.py prototype"]
        src_zephyr_reporting_infrastructure_init_py["src/zephyr/reporting/infrastructure/__init__.py prototype"]
        src_zephyr_reporting_models_init_py["src/zephyr/reporting/models/__init__.py prototype"]
        src_zephyr_reporting_services_init_py["src/zephyr/reporting/services/__init__.py prototype"]
    end
    D_GOVERNANCE["D_GOVERNANCE prototype"]
    src_zephyr_reporting_default_attribution_engine_py -.->|import_depends| D_GOVERNANCE
    D_TRADING["D_TRADING production"]
    src_zephyr_reporting_analytics_base_py -->|import_depends| D_TRADING
    src_zephyr_reporting_default_tca_engine_py -.->|import_depends| D_TRADING
    src_zephyr_reporting_default_tca_engine_py -.->|import_depends| D_TRADING
    src_zephyr_reporting_default_tca_engine_py -.->|import_depends| D_TRADING
    src_zephyr_reporting_analytics_base_py -->|import_depends| D_TRADING
    src_zephyr_reporting_default_tca_engine_py -.->|import_depends| D_GOVERNANCE
    src_zephyr_reporting_init_py -.->|import_depends| D_GOVERNANCE
    src_zephyr_reporting_analytics_base_py -->|import_depends| D_TRADING
    D_GOVERNANCE -->|import_depends| src_zephyr_reporting_analytics_base_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_reporting_analytics_base_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_reporting_analytics_base_py production
    class src_zephyr_reporting_init_py,src_zephyr_reporting_extensions_init_py,src_zephyr_reporting_api_init_py,src_zephyr_reporting_core_init_py,src_zephyr_reporting_default_attribution_engine_py,src_zephyr_reporting_default_tca_engine_py,src_zephyr_reporting_infrastructure_init_py,src_zephyr_reporting_models_init_py,src_zephyr_reporting_services_init_py design
    class D_TRADING external_prod
    class D_GOVERNANCE external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 / Target Domain | 依赖数 / Count | 依赖类型 / Type |
|--------|:---:|---------|
| D_TRADING | 6 | import_depends |
| D_GOVERNANCE | 3 | import_depends |

### 依赖本域的其他域（入边）/ Depended By

| 源域 / Source Domain | 依赖数 / Count | 依赖类型 / Type |
|------|:---:|---------|
| D_GOVERNANCE | 2 | import_depends |
| D_AUDITTEST | 1 | test_depends |

## 架构分层视图 / Architecture Overview

> 按 architecture_layer 分层显示 报告（D_REPORTING）的模块分布。共 10 个模块 / 10 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (10 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/reporting/__init__.py  [prototype]                  │
│   src/zephyr/reporting/_extensions/__init__.py  [prototype]      │
│   src/zephyr/reporting/analytics_base.py  [production]           │
│   src/zephyr/reporting/api/__init__.py  [prototype]              │
│   src/zephyr/reporting/core/__init__.py  [prototype]             │
│   src/zephyr/reporting/default_attribution_engine.py  [protot... │
│   src/zephyr/reporting/default_tca_engine.py  [prototype]        │
│   src/zephyr/reporting/infrastructure/__init__.py  [prototype]   │
│   src/zephyr/reporting/models/__init__.py  [prototype]           │
│   src/zephyr/reporting/services/__init__.py  [prototype]         │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 10 个模块 / 10 modules）。

### L1 基础层 / Foundation Layer (10 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/reporting/__init__.py | src/zephyr/reporting/__init__.py | prototype | generated |
| 2 | src/zephyr/reporting/_extensions/__init__.py | src/zephyr/reporting/_extensions/__in... | prototype | generated |
| 3 | src/zephyr/reporting/analytics_base.py | src/zephyr/reporting/analytics_base.py | production | generated |
| 4 | src/zephyr/reporting/api/__init__.py | src/zephyr/reporting/api/__init__.py | prototype | generated |
| 5 | src/zephyr/reporting/core/__init__.py | src/zephyr/reporting/core/__init__.py | prototype | generated |
| 6 | src/zephyr/reporting/default_attribution_engine.py | src/zephyr/reporting/default_attribut... | prototype | generated |
| 7 | src/zephyr/reporting/default_tca_engine.py | src/zephyr/reporting/default_tca_engi... | prototype | generated |
| 8 | src/zephyr/reporting/infrastructure/__init__.py | src/zephyr/reporting/infrastructure/_... | prototype | generated |
| 9 | src/zephyr/reporting/models/__init__.py | src/zephyr/reporting/models/__init__.py | prototype | generated |
| 10 | src/zephyr/reporting/services/__init__.py | src/zephyr/reporting/services/__init_... | prototype | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 0 条 / 0 edges）。按依赖类型分组，使用 → 表示方向。

（无域内依赖 / No internal dependencies）


## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
