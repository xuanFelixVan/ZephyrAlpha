---
doc_type: architecture_view
title: D_BACKTEST 回测架构文档
version: "1.0"
status: active
date: 2026-07-03
owner: auto-generator
ttl: permanent
---

# 24_d_backtest / 回测

> **文档作用 / Purpose**: 展示 回测（D_BACKTEST）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-03 15:23:28
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 24 | Number | 24 |
| 域ID | D_BACKTEST | Domain ID | D_BACKTEST |
| 域名称 | 回测 | Domain Name | 回测 |
| 层级 | L2_domain | Layer | L2_domain |
| 模块数 | 10 | Module Count | 10 |
| 域内依赖 | 5 | Internal Dependencies | 5 |
| 跨域入边 | 3 | Cross-domain Incoming | 3 |
| 跨域出边 | 1 | Cross-domain Outgoing | 1 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 10 | Prototype Modules | 10 |
| 生产态模块 | 0 | Production Modules | 0 |
| 容量 | 0/150 (正常) | Capacity | 0/150 (正常) |
| 描述 | 历史回测、参数寻优、过拟合检测、绩效归因。策略验证引擎。 | Description | 历史回测、参数寻优、过拟合检测、绩效归因。策略验证引擎。 |

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
    subgraph D_BACKTEST["D_BACKTEST 回测"]
        src_zephyr_backtest_init_py["src/zephyr/backtest/__init__.py prototype"]
        src_zephyr_backtest_extensions_init_py["src/zephyr/backtest/_extensions/__init__.py prototype"]
        src_zephyr_backtest_api_init_py["src/zephyr/backtest/api/__init__.py prototype"]
        src_zephyr_backtest_core_init_py["src/zephyr/backtest/core/__init__.py prototype"]
        src_zephyr_backtest_core_engine_base_py["src/zephyr/backtest/core/engine_base.py prototype"]
        src_zephyr_backtest_implementations_init_py["src/zephyr/backtest/implementations/__init__.py prototype"]
        src_zephyr_backtest_implementations_vectorized_engine_py["src/zephyr/backtest/implementations/vectorized_... prototype"]
        src_zephyr_backtest_infrastructure_init_py["src/zephyr/backtest/infrastructure/__init__.py prototype"]
        src_zephyr_backtest_models_init_py["src/zephyr/backtest/models/__init__.py prototype"]
        src_zephyr_backtest_services_init_py["src/zephyr/backtest/services/__init__.py prototype"]
    end
    src_zephyr_backtest_init_py -.->|import_depends| src_zephyr_backtest_core_engine_base_py
    src_zephyr_backtest_init_py -.->|import_depends| src_zephyr_backtest_implementations_vectorized_engine_py
    src_zephyr_backtest_core_init_py -.->|import_depends| src_zephyr_backtest_core_engine_base_py
    src_zephyr_backtest_implementations_init_py -.->|import_depends| src_zephyr_backtest_implementations_vectorized_engine_py
    src_zephyr_backtest_implementations_vectorized_engine_py -.->|import_depends| src_zephyr_backtest_core_engine_base_py
    D_SHARED["D_SHARED production"]
    src_zephyr_backtest_core_engine_base_py -.->|import_depends| D_SHARED
    D_INTELLIGENCE["D_INTELLIGENCE prototype"]
    D_INTELLIGENCE -.->|import_depends| src_zephyr_backtest_implementations_vectorized_engine_py
    D_INTELLIGENCE -.->|import_depends| src_zephyr_backtest_implementations_vectorized_engine_py
    D_INTELLIGENCE -.->|import_depends| src_zephyr_backtest_core_engine_base_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_backtest_init_py,src_zephyr_backtest_extensions_init_py,src_zephyr_backtest_api_init_py,src_zephyr_backtest_core_init_py,src_zephyr_backtest_core_engine_base_py,src_zephyr_backtest_implementations_init_py,src_zephyr_backtest_implementations_vectorized_engine_py,src_zephyr_backtest_infrastructure_init_py,src_zephyr_backtest_models_init_py,src_zephyr_backtest_services_init_py design
    class D_SHARED external_prod
    class D_INTELLIGENCE external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 / Target Domain | 依赖数 / Count | 依赖类型 / Type |
|--------|:---:|---------|
| D_SHARED | 1 | import_depends |

### 依赖本域的其他域（入边）/ Depended By

| 源域 / Source Domain | 依赖数 / Count | 依赖类型 / Type |
|------|:---:|---------|
| D_INTELLIGENCE | 3 | import_depends |

## 架构分层视图 / Architecture Overview

> 按 architecture_layer 分层显示 回测（D_BACKTEST）的模块分布。共 10 个模块 / 10 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (10 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/backtest/__init__.py  [prototype]                   │
│   src/zephyr/backtest/_extensions/__init__.py  [prototype]       │
│   src/zephyr/backtest/api/__init__.py  [prototype]               │
│   src/zephyr/backtest/core/__init__.py  [prototype]              │
│   src/zephyr/backtest/core/engine_base.py  [prototype]           │
│   src/zephyr/backtest/implementations/__init__.py  [prototype]   │
│   src/zephyr/backtest/implementations/vectorized_engine.py  [... │
│   src/zephyr/backtest/infrastructure/__init__.py  [prototype]    │
│   src/zephyr/backtest/models/__init__.py  [prototype]            │
│   src/zephyr/backtest/services/__init__.py  [prototype]          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 10 个模块 / 10 modules）。

### L2 领域层 / Domain Layer (10 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/backtest/__init__.py | src/zephyr/backtest/__init__.py | prototype | generated |
| 2 | src/zephyr/backtest/_extensions/__init__.py | src/zephyr/backtest/_extensions/__ini... | prototype | generated |
| 3 | src/zephyr/backtest/api/__init__.py | src/zephyr/backtest/api/__init__.py | prototype | generated |
| 4 | src/zephyr/backtest/core/__init__.py | src/zephyr/backtest/core/__init__.py | prototype | generated |
| 5 | src/zephyr/backtest/core/engine_base.py | src/zephyr/backtest/core/engine_base.py | prototype | generated |
| 6 | src/zephyr/backtest/implementations/__init__.py | src/zephyr/backtest/implementations/_... | prototype | generated |
| 7 | src/zephyr/backtest/implementations/vectorized_engine.py | src/zephyr/backtest/implementations/v... | prototype | generated |
| 8 | src/zephyr/backtest/infrastructure/__init__.py | src/zephyr/backtest/infrastructure/__... | prototype | generated |
| 9 | src/zephyr/backtest/models/__init__.py | src/zephyr/backtest/models/__init__.py | prototype | generated |
| 10 | src/zephyr/backtest/services/__init__.py | src/zephyr/backtest/services/__init__.py | prototype | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 5 条 / 5 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│        依赖关系图 / Dependency Graph (共 5 条 / 5 edges)         │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 1                               │
│   [import_depends]: 5 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (5 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   __init__.py → engine_base.py                                   │
│   __init__.py → vectorized_engine.py                             │
│   __init__.py → engine_base.py                                   │
│   __init__.py → vectorized_engine.py                             │
│   vectorized_engine.py → engine_base.py                          │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
