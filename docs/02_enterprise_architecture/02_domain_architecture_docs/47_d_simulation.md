---
doc_type: architecture_view
title: D_SIMULATION 仿真架构文档
version: "1.0"
status: active
date: 2026-07-05
owner: auto-generator
ttl: permanent
---

# 47_d_simulation / 仿真

> **文档作用 / Purpose**: 展示 仿真（D_SIMULATION）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-05 16:09:51
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 47 | Number | 47 |
| 域ID | D_SIMULATION | Domain ID | D_SIMULATION |
| 域名称 | 仿真 | Domain Name | 仿真 |
| 层级 | L2_domain | Layer | L2_domain |
| 模块数 | 11 | Module Count | 11 |
| 域内依赖 | 2 | Internal Dependencies | 2 |
| 跨域入边 | 3 | Cross-domain Incoming | 3 |
| 跨域出边 | 1 | Cross-domain Outgoing | 1 |
| 设计态模块 | 1 | Design Modules | 1 |
| 原型态模块 | 8 | Prototype Modules | 8 |
| 生产态模块 | 2 | Production Modules | 2 |
| 容量 | 2/150 (正常) | Capacity | 2/150 (正常) |
| 描述 | 仿真引擎、场景生成、蒙特卡洛、回测模拟。策略验证沙箱。 | Description | 仿真引擎、场景生成、蒙特卡洛、回测模拟。策略验证沙箱。 |

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
    subgraph D_SIMULATION["D_SIMULATION 仿真"]
        src_zephyr_simulation["仿真核心域 design"]
        src_zephyr_simulation_init_py["src/zephyr/simulation/__init__.py prototype"]
        src_zephyr_simulation_extensions_init_py["src/zephyr/simulation/_extensions/__init__.py prototype"]
        src_zephyr_simulation_api_init_py["src/zephyr/simulation/api/__init__.py prototype"]
        src_zephyr_simulation_core_init_py["src/zephyr/simulation/core/__init__.py prototype"]
        src_zephyr_simulation_implementations_init_py["src/zephyr/simulation/implementations/__init__.py prototype"]
        src_zephyr_simulation_implementations_default_experiment_pipeline_py["src/zephyr/simulation/implementations/default_e... production"]
        src_zephyr_simulation_infrastructure_init_py["src/zephyr/simulation/infrastructure/__init__.py prototype"]
        src_zephyr_simulation_models_init_py["src/zephyr/simulation/models/__init__.py prototype"]
        src_zephyr_simulation_pipeline_base_py["src/zephyr/simulation/pipeline_base.py production"]
        src_zephyr_simulation_services_init_py["src/zephyr/simulation/services/__init__.py prototype"]
    end
    src_zephyr_simulation_implementations_default_experiment_pipeline_py -->|import_depends| src_zephyr_simulation_pipeline_base_py
    src_zephyr_simulation_implementations_init_py -.->|config_depends| src_zephyr_simulation_implementations_default_experiment_pipeline_py
    D_SHARED["D_SHARED production"]
    src_zephyr_simulation_pipeline_base_py -->|import_depends| D_SHARED
    D_GOVERNANCE["D_GOVERNANCE prototype"]
    D_GOVERNANCE -.->|import_depends| src_zephyr_simulation_init_py
    D_AUDITTEST["D_AUDITTEST prototype"]
    D_AUDITTEST -.->|test_depends| src_zephyr_simulation_pipeline_base_py
    D_SHARED -.->|import_depends| src_zephyr_simulation_pipeline_base_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_simulation_implementations_default_experiment_pipeline_py,src_zephyr_simulation_pipeline_base_py production
    class src_zephyr_simulation,src_zephyr_simulation_init_py,src_zephyr_simulation_extensions_init_py,src_zephyr_simulation_api_init_py,src_zephyr_simulation_core_init_py,src_zephyr_simulation_implementations_init_py,src_zephyr_simulation_infrastructure_init_py,src_zephyr_simulation_models_init_py,src_zephyr_simulation_services_init_py design
    class D_SHARED external_prod
    class D_GOVERNANCE,D_AUDITTEST external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 / Target Domain | 依赖数 / Count | 依赖类型 / Type |
|--------|:---:|---------|
| D_SHARED | 1 | import_depends |

### 依赖本域的其他域（入边）/ Depended By

| 源域 / Source Domain | 依赖数 / Count | 依赖类型 / Type |
|------|:---:|---------|
| D_AUDITTEST | 1 | test_depends |
| D_GOVERNANCE | 1 | import_depends |
| D_SHARED | 1 | import_depends |

## 架构分层视图 / Architecture Overview

> 按 architecture_layer 分层显示 仿真（D_SIMULATION）的模块分布。共 11 个模块 / 11 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (11 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   仿真核心域  [design]                                           │
│   src/zephyr/simulation/__init__.py  [prototype]                 │
│   src/zephyr/simulation/_extensions/__init__.py  [prototype]     │
│   src/zephyr/simulation/api/__init__.py  [prototype]             │
│   src/zephyr/simulation/core/__init__.py  [prototype]            │
│   src/zephyr/simulation/implementations/__init__.py  [prototype] │
│   src/zephyr/simulation/implementations/default_experiment_pi... │
│   src/zephyr/simulation/infrastructure/__init__.py  [prototype]  │
│   src/zephyr/simulation/models/__init__.py  [prototype]          │
│   src/zephyr/simulation/pipeline_base.py  [production]           │
│   src/zephyr/simulation/services/__init__.py  [prototype]        │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 11 个模块 / 11 modules）。

### L2 领域层 / Domain Layer (11 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/simulation/ | 仿真核心域 | design | planned |
| 2 | src/zephyr/simulation/__init__.py | src/zephyr/simulation/__init__.py | prototype | generated |
| 3 | src/zephyr/simulation/_extensions/__init__.py | src/zephyr/simulation/_extensions/__i... | prototype | generated |
| 4 | src/zephyr/simulation/api/__init__.py | src/zephyr/simulation/api/__init__.py | prototype | generated |
| 5 | src/zephyr/simulation/core/__init__.py | src/zephyr/simulation/core/__init__.py | prototype | generated |
| 6 | src/zephyr/simulation/implementations/__init__.py | src/zephyr/simulation/implementations... | prototype | generated |
| 7 | src/zephyr/simulation/implementations/default_experiment_... | src/zephyr/simulation/implementations... | production | generated |
| 8 | src/zephyr/simulation/infrastructure/__init__.py | src/zephyr/simulation/infrastructure/... | prototype | generated |
| 9 | src/zephyr/simulation/models/__init__.py | src/zephyr/simulation/models/__init__.py | prototype | generated |
| 10 | src/zephyr/simulation/pipeline_base.py | src/zephyr/simulation/pipeline_base.py | production | generated |
| 11 | src/zephyr/simulation/services/__init__.py | src/zephyr/simulation/services/__init... | prototype | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 2 条 / 2 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│        依赖关系图 / Dependency Graph (共 2 条 / 2 edges)         │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [import_depends]: 1 条 / edges                                 │
│   [config_depends]: 1 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (1 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   default_experiment_pipeli... → pipeline_base.py                │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (1 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   __init__.py → default_experiment_pipeli...                     │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
