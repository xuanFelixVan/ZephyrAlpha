---
doc_type: architecture_view
title: D_SIGQC signal_quality架构文档
version: "1.0"
status: active
date: 2026-07-06
owner: auto-generator
ttl: permanent
---

# 46_d_sigqc / signal_quality

> **文档作用 / Purpose**: 展示 signal_quality（D_SIGQC）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-06 13:27:25
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 46 | Number | 46 |
| 域ID | D_SIGQC | Domain ID | D_SIGQC |
| 域名称 | signal_quality | Domain Name | signal_quality |
| 层级 | L2_domain | Layer | L2_domain |
| 模块数 | 8 | Module Count | 8 |
| 域内依赖 | 1 | Internal Dependencies | 1 |
| 跨域入边 | 0 | Cross-domain Incoming | 0 |
| 跨域出边 | 2 | Cross-domain Outgoing | 2 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 8 | Prototype Modules | 8 |
| 生产态模块 | 0 | Production Modules | 0 |
| 容量 | 0/150 (正常) | Capacity | 0/150 (正常) |
| 描述 | 信号质量评估 | Description | 信号质量评估 |

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
    subgraph D_SIGQC["D_SIGQC signal_quality"]
        src_zephyr_signal_quality_init_py["src/zephyr/signal_quality/__init__.py prototype"]
        src_zephyr_signal_quality_extensions_init_py["src/zephyr/signal_quality/_extensions/__init__.py prototype"]
        src_zephyr_signal_quality_api_init_py["src/zephyr/signal_quality/api/__init__.py prototype"]
        src_zephyr_signal_quality_core_init_py["src/zephyr/signal_quality/core/__init__.py prototype"]
        src_zephyr_signal_quality_degradation_monitor_base_py["src/zephyr/signal_quality/degradation_monitor_b... prototype"]
        src_zephyr_signal_quality_infrastructure_init_py["src/zephyr/signal_quality/infrastructure/__init... prototype"]
        src_zephyr_signal_quality_models_init_py["src/zephyr/signal_quality/models/__init__.py prototype"]
        src_zephyr_signal_quality_services_init_py["src/zephyr/signal_quality/services/__init__.py prototype"]
    end
    src_zephyr_signal_quality_init_py -.->|import_depends| src_zephyr_signal_quality_degradation_monitor_base_py
    D_TRADING["D_TRADING production"]
    src_zephyr_signal_quality_degradation_monitor_base_py -.->|import_depends| D_TRADING
    src_zephyr_signal_quality_degradation_monitor_base_py -.->|import_depends| D_TRADING
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_signal_quality_init_py,src_zephyr_signal_quality_extensions_init_py,src_zephyr_signal_quality_api_init_py,src_zephyr_signal_quality_core_init_py,src_zephyr_signal_quality_degradation_monitor_base_py,src_zephyr_signal_quality_infrastructure_init_py,src_zephyr_signal_quality_models_init_py,src_zephyr_signal_quality_services_init_py design
    class D_TRADING external_prod
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 / Target Domain | 依赖数 / Count | 依赖类型 / Type |
|--------|:---:|---------|
| D_TRADING | 2 | import_depends |

### 依赖本域的其他域（入边）/ Depended By

无跨域入边依赖 / No cross-domain incoming dependencies

## 架构分层视图 / Architecture Overview

> 按 architecture_layer 分层显示 signal_quality（D_SIGQC）的模块分布。共 8 个模块 / 8 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│               L2 领域层 / Domain Layer (8 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/signal_quality/__init__.py  [prototype]             │
│   src/zephyr/signal_quality/_extensions/__init__.py  [prototype] │
│   src/zephyr/signal_quality/api/__init__.py  [prototype]         │
│   src/zephyr/signal_quality/core/__init__.py  [prototype]        │
│   src/zephyr/signal_quality/degradation_monitor_base.py  [pro... │
│   src/zephyr/signal_quality/infrastructure/__init__.py  [prot... │
│   src/zephyr/signal_quality/models/__init__.py  [prototype]      │
│   src/zephyr/signal_quality/services/__init__.py  [prototype]    │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 8 个模块 / 8 modules）。

### L2 领域层 / Domain Layer (8 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/signal_quality/__init__.py | src/zephyr/signal_quality/__init__.py | prototype | generated |
| 2 | src/zephyr/signal_quality/_extensions/__init__.py | src/zephyr/signal_quality/_extensions... | prototype | generated |
| 3 | src/zephyr/signal_quality/api/__init__.py | src/zephyr/signal_quality/api/__init_... | prototype | generated |
| 4 | src/zephyr/signal_quality/core/__init__.py | src/zephyr/signal_quality/core/__init... | prototype | generated |
| 5 | src/zephyr/signal_quality/degradation_monitor_base.py | src/zephyr/signal_quality/degradation... | prototype | generated |
| 6 | src/zephyr/signal_quality/infrastructure/__init__.py | src/zephyr/signal_quality/infrastruct... | prototype | generated |
| 7 | src/zephyr/signal_quality/models/__init__.py | src/zephyr/signal_quality/models/__in... | prototype | generated |
| 8 | src/zephyr/signal_quality/services/__init__.py | src/zephyr/signal_quality/services/__... | prototype | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 1 条 / 1 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│        依赖关系图 / Dependency Graph (共 1 条 / 1 edges)         │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 1                               │
│   [import_depends]: 1 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (1 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   __init__.py → degradation_monitor_base.py                      │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
