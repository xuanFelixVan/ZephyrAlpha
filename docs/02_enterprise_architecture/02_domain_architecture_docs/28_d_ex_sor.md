---
doc_type: architecture_view
title: D_EX_SOR 执行路由架构文档
version: "1.0"
status: active
date: 2026-07-06
owner: auto-generator
ttl: permanent
---

# 28_d_ex_sor / 执行路由

> **文档作用 / Purpose**: 展示 执行路由（D_EX_SOR）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-06 12:55:05
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 28 | Number | 28 |
| 域ID | D_EX_SOR | Domain ID | D_EX_SOR |
| 域名称 | 执行路由 | Domain Name | 执行路由 |
| 层级 | L2_domain | Layer | L2_domain |
| 模块数 | 7 | Module Count | 7 |
| 域内依赖 | 0 | Internal Dependencies | 0 |
| 跨域入边 | 0 | Cross-domain Incoming | 0 |
| 跨域出边 | 0 | Cross-domain Outgoing | 0 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 7 | Prototype Modules | 7 |
| 生产态模块 | 0 | Production Modules | 0 |
| 容量 | 0/150 (正常) | Capacity | 0/150 (正常) |
| 描述 | 执行路由域。负责智能订单路由(SOR)，包括多交易通道选择、流动性聚合、最优执行路径规划。 | Description | 执行路由域。负责智能订单路由(SOR)，包括多交易通道选择、流动性聚合、最优执行路径规划。 |

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
    subgraph D_EX_SOR["D_EX_SOR 执行路由"]
        src_zephyr_ex_sor_init_py["src/zephyr/ex_sor/__init__.py prototype"]
        src_zephyr_ex_sor_extensions_init_py["src/zephyr/ex_sor/_extensions/__init__.py prototype"]
        src_zephyr_ex_sor_api_init_py["src/zephyr/ex_sor/api/__init__.py prototype"]
        src_zephyr_ex_sor_core_init_py["src/zephyr/ex_sor/core/__init__.py prototype"]
        src_zephyr_ex_sor_infrastructure_init_py["src/zephyr/ex_sor/infrastructure/__init__.py prototype"]
        src_zephyr_ex_sor_models_init_py["src/zephyr/ex_sor/models/__init__.py prototype"]
        src_zephyr_ex_sor_services_init_py["src/zephyr/ex_sor/services/__init__.py prototype"]
    end
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_ex_sor_init_py,src_zephyr_ex_sor_extensions_init_py,src_zephyr_ex_sor_api_init_py,src_zephyr_ex_sor_core_init_py,src_zephyr_ex_sor_infrastructure_init_py,src_zephyr_ex_sor_models_init_py,src_zephyr_ex_sor_services_init_py design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

无跨域出边依赖 / No cross-domain outgoing dependencies

### 依赖本域的其他域（入边）/ Depended By

无跨域入边依赖 / No cross-domain incoming dependencies

## 架构分层视图 / Architecture Overview

> 按 architecture_layer 分层显示 执行路由（D_EX_SOR）的模块分布。共 7 个模块 / 7 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│               L2 领域层 / Domain Layer (7 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/ex_sor/__init__.py  [prototype]                     │
│   src/zephyr/ex_sor/_extensions/__init__.py  [prototype]         │
│   src/zephyr/ex_sor/api/__init__.py  [prototype]                 │
│   src/zephyr/ex_sor/core/__init__.py  [prototype]                │
│   src/zephyr/ex_sor/infrastructure/__init__.py  [prototype]      │
│   src/zephyr/ex_sor/models/__init__.py  [prototype]              │
│   src/zephyr/ex_sor/services/__init__.py  [prototype]            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 7 个模块 / 7 modules）。

### L2 领域层 / Domain Layer (7 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/ex_sor/__init__.py | src/zephyr/ex_sor/__init__.py | prototype | generated |
| 2 | src/zephyr/ex_sor/_extensions/__init__.py | src/zephyr/ex_sor/_extensions/__init_... | prototype | generated |
| 3 | src/zephyr/ex_sor/api/__init__.py | src/zephyr/ex_sor/api/__init__.py | prototype | generated |
| 4 | src/zephyr/ex_sor/core/__init__.py | src/zephyr/ex_sor/core/__init__.py | prototype | generated |
| 5 | src/zephyr/ex_sor/infrastructure/__init__.py | src/zephyr/ex_sor/infrastructure/__in... | prototype | generated |
| 6 | src/zephyr/ex_sor/models/__init__.py | src/zephyr/ex_sor/models/__init__.py | prototype | generated |
| 7 | src/zephyr/ex_sor/services/__init__.py | src/zephyr/ex_sor/services/__init__.py | prototype | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 0 条 / 0 edges）。按依赖类型分组，使用 → 表示方向。

（无域内依赖 / No internal dependencies）


## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
