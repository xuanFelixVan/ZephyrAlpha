---
doc_type: domain_architecture_doc
title: D-PF_ALLOC 组合分配架构文档
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 44_d_pf_alloc / 组合分配

> **文档作用 / Purpose**: 展示 组合分配（D-PF_ALLOC）功能域的模块清单、域内依赖关系和跨域依赖关系，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-25 18:42:45
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 44 | Number | 44 |
| 域ID | D-PF_ALLOC | Domain ID | D-PF_ALLOC |
| 域名称 | 组合分配 | Domain Name | 组合分配 |
| 层级 | L2_domain | Layer | L2_domain |
| 模块数 | 15 | Module Count | 15 |
| 域内依赖 | 0 | Internal Dependencies | 0 |
| 跨域入边 | 1 | Cross-domain Incoming | 1 |
| 跨域出边 | 5 | Cross-domain Outgoing | 5 |
| 设计态模块 | 5 | Design Modules | 5 |
| 原型态模块 | 10 | Prototype Modules | 10 |
| 生产态模块 | 0 | Production Modules | 0 |
| 容量 | 0/150 (正常) | Capacity | 0/150 (正常) |
| 描述 | 资产组合分配优化 | Description | 资产组合分配优化 |

## 模块清单 / Module List

共 15 个模块（按路径排序，全部显示）

| 模块路径 / Module Path | 模块名称 / Module Name | 设计成熟度 / Maturity | 构建状态 / Build Status |
|---------|---------|-----------|---------|
| src/zephyr/pf_alloc/ | 组合分配域 | design | planned |
| src/zephyr/pf_alloc/__init__.py |  | prototype | generated |
| src/zephyr/pf_alloc/_extensions/__init__.py |  | prototype | deprecated |
| src/zephyr/pf_alloc/api/__init__.py |  | prototype | deprecated |
| src/zephyr/pf_alloc/constraint/ | 约束求解 | design | planned |
| src/zephyr/pf_alloc/core/__init__.py |  | prototype | deprecated |
| src/zephyr/pf_alloc/infrastructure/__init__.py |  | prototype | deprecated |
| src/zephyr/pf_alloc/models/__init__.py |  | prototype | deprecated |
| src/zephyr/pf_alloc/optimizer/ | 分配优化器 | design | planned |
| src/zephyr/pf_alloc/rebalance/ | 再平衡引擎 | design | planned |
| src/zephyr/pf_alloc/risk_budget/ | 风险预算 | design | planned |
| src/zephyr/pf_alloc/services/__init__.py |  | prototype | deprecated |
| src/zephyr/pf_alloc/strategy_lifecycle_event.py |  | prototype | generated |
| src/zephyr/pf_core/default_equity_strategy.py |  | prototype | generated |
| src/zephyr/pf_core/strategy_portfolio.py |  | prototype | generated |

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
    subgraph D_PF_ALLOC["D-PF_ALLOC 组合分配"]
        src_zephyr_pf_alloc["组合分配域 design"]
        src_zephyr_pf_alloc_init_py["src/zephyr/pf_alloc/__init__.py prototype"]
        src_zephyr_pf_alloc_extensions_init_py["src/zephyr/pf_alloc/_extensions/__init__.py prototype"]
        src_zephyr_pf_alloc_api_init_py["src/zephyr/pf_alloc/api/__init__.py prototype"]
        src_zephyr_pf_alloc_constraint["约束求解 design"]
        src_zephyr_pf_alloc_core_init_py["src/zephyr/pf_alloc/core/__init__.py prototype"]
        src_zephyr_pf_alloc_infrastructure_init_py["src/zephyr/pf_alloc/infrastructure/__init__.py prototype"]
        src_zephyr_pf_alloc_models_init_py["src/zephyr/pf_alloc/models/__init__.py prototype"]
        src_zephyr_pf_alloc_optimizer["分配优化器 design"]
        src_zephyr_pf_alloc_rebalance["再平衡引擎 design"]
        src_zephyr_pf_alloc_risk_budget["风险预算 design"]
        src_zephyr_pf_alloc_services_init_py["src/zephyr/pf_alloc/services/__init__.py prototype"]
        src_zephyr_pf_alloc_strategy_lifecycle_event_py["src/zephyr/pf_alloc/strategy_lifecycle_event.py prototype"]
        src_zephyr_pf_core_default_equity_strategy_py["src/zephyr/pf_core/default_equity_strategy.py prototype"]
        src_zephyr_pf_core_strategy_portfolio_py["src/zephyr/pf_core/strategy_portfolio.py prototype"]
    end
    D_SHARED["D-SHARED prototype"]
    src_zephyr_pf_alloc -.->|contract| D_SHARED
    D_GOVERNANCE["D-GOVERNANCE prototype"]
    src_zephyr_pf_core_default_equity_strategy_py -.->|import_depends| D_GOVERNANCE
    D_TRADING["D-TRADING production"]
    src_zephyr_pf_core_default_equity_strategy_py -.->|import_depends| D_TRADING
    src_zephyr_pf_core_strategy_portfolio_py -.->|config_depends| D_GOVERNANCE
    src_zephyr_pf_alloc_strategy_lifecycle_event_py -.->|import_depends| D_SHARED
    D_GOVERNANCE -.->|import_depends| src_zephyr_pf_core_default_equity_strategy_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_pf_alloc,src_zephyr_pf_alloc_init_py,src_zephyr_pf_alloc_extensions_init_py,src_zephyr_pf_alloc_api_init_py,src_zephyr_pf_alloc_constraint,src_zephyr_pf_alloc_core_init_py,src_zephyr_pf_alloc_infrastructure_init_py,src_zephyr_pf_alloc_models_init_py,src_zephyr_pf_alloc_optimizer,src_zephyr_pf_alloc_rebalance,src_zephyr_pf_alloc_risk_budget,src_zephyr_pf_alloc_services_init_py,src_zephyr_pf_alloc_strategy_lifecycle_event_py,src_zephyr_pf_core_default_equity_strategy_py,src_zephyr_pf_core_strategy_portfolio_py design
    class D_TRADING external_prod
    class D_SHARED,D_GOVERNANCE external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 / Target Domain | 依赖数 / Count | 依赖类型 / Type |
|--------|:---:|---------|
| D-SHARED | 2 | contract,import_depends |
| D-GOVERNANCE | 2 | import_depends,config_depends |
| D-TRADING | 1 | import_depends |

### 依赖本域的其他域（入边）/ Depended By

| 源域 / Source Domain | 依赖数 / Count | 依赖类型 / Type |
|------|:---:|---------|
| D-GOVERNANCE | 1 | import_depends |

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
