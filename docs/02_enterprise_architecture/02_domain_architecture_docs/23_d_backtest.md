---
doc_type: architecture_view
title: D_BACKTEST 回测架构文档
version: "1.0"
status: active
date: 2026-07-06
owner: auto-generator
ttl: permanent
---

# 23_d_backtest / 回测

> **文档作用 / Purpose**: 展示 回测（D_BACKTEST）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-06 12:26:47
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 23 | Number | 23 |
| 域ID | D_BACKTEST | Domain ID | D_BACKTEST |
| 域名称 | 回测 | Domain Name | 回测 |
| 层级 | L2_domain | Layer | L2_domain |
| 模块数 | 33 | Module Count | 33 |
| 域内依赖 | 44 | Internal Dependencies | 44 |
| 跨域入边 | 20 | Cross-domain Incoming | 20 |
| 跨域出边 | 5 | Cross-domain Outgoing | 5 |
| 设计态模块 | 8 | Design Modules | 8 |
| 原型态模块 | 22 | Prototype Modules | 22 |
| 生产态模块 | 3 | Production Modules | 3 |
| 容量 | 3/150 (正常) | Capacity | 3/150 (正常) |
| 描述 | 历史回测、参数寻优、过拟合检测、绩效归因。策略验证引擎。 | Description | 历史回测、参数寻优、过拟合检测、绩效归因。策略验证引擎。 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。每30个节点一组分页显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

### 第 1 页 / 共 2 页 / Page 1 of 2

```mermaid
graph TD
    subgraph D_BACKTEST["D_BACKTEST 回测"]
        src_zephyr_backtest_init_py["src/zephyr/backtest/__init__.py prototype"]
        src_zephyr_backtest_extensions_init_py["src/zephyr/backtest/_extensions/__init__.py prototype"]
        src_zephyr_backtest_api_init_py["src/zephyr/backtest/api/__init__.py prototype"]
        src_zephyr_backtest_core_init_py["src/zephyr/backtest/core/__init__.py prototype"]
        src_zephyr_backtest_core_data_handler_py["src/zephyr/backtest/core/data_handler.py prototype"]
        src_zephyr_backtest_core_data_handler_py_1["src/zephyr/backtest/core/data_handler.py/ design"]
        src_zephyr_backtest_core_decision_gate_py["src/zephyr/backtest/core/decision_gate.py prototype"]
        src_zephyr_backtest_core_engine_base_py["src/zephyr/backtest/core/engine_base.py production"]
        src_zephyr_backtest_core_matching_engine_py["src/zephyr/backtest/core/matching_engine.py prototype"]
        src_zephyr_backtest_core_matching_engine_py_1["src/zephyr/backtest/core/matching_engine.py/ design"]
        src_zephyr_backtest_core_matching_logic_py["src/zephyr/backtest/core/matching_logic.py prototype"]
        src_zephyr_backtest_core_matching_logic_py_1["src/zephyr/backtest/core/matching_logic.py/ design"]
        src_zephyr_backtest_core_metrics_py["src/zephyr/backtest/core/metrics.py prototype"]
        src_zephyr_backtest_core_metrics_py_1["src/zephyr/backtest/core/metrics.py/ design"]
        src_zephyr_backtest_core_overfitting_detector_py["src/zephyr/backtest/core/overfitting_detector.py prototype"]
        src_zephyr_backtest_core_pit_manager_py["src/zephyr/backtest/core/pit_manager.py prototype"]
        src_zephyr_backtest_core_portfolio_py["src/zephyr/backtest/core/portfolio.py prototype"]
        src_zephyr_backtest_core_portfolio_py_1["src/zephyr/backtest/core/portfolio.py/ design"]
        src_zephyr_backtest_core_tick_replay_py["src/zephyr/backtest/core/tick_replay.py prototype"]
        src_zephyr_backtest_core_tick_replay_py_1["src/zephyr/backtest/core/tick_replay.py/ design"]
        src_zephyr_backtest_core_walk_forward_py["src/zephyr/backtest/core/walk_forward.py prototype"]
        src_zephyr_backtest_implementations_init_py["src/zephyr/backtest/implementations/__init__.py prototype"]
        src_zephyr_backtest_implementations_event_driven_engine_py["src/zephyr/backtest/implementations/event_drive... prototype"]
        src_zephyr_backtest_implementations_vectorized_engine_py["src/zephyr/backtest/implementations/vectorized_... production"]
        src_zephyr_backtest_infrastructure_init_py["src/zephyr/backtest/infrastructure/__init__.py prototype"]
        src_zephyr_backtest_io_init_py["src/zephyr/backtest/io/__init__.py prototype"]
        src_zephyr_backtest_io_backtest_result_sink_py["src/zephyr/backtest/io/backtest_result_sink.py prototype"]
        src_zephyr_backtest_io_backtest_result_sink_py_1["src/zephyr/backtest/io/backtest_result_sink.py/ design"]
        src_zephyr_backtest_io_decisiongraph_adapter_py["src/zephyr/backtest/io/decisiongraph_adapter.py production"]
        src_zephyr_backtest_io_result_repository_py["src/zephyr/backtest/io/result_repository.py prototype"]
    end
    src_zephyr_backtest_core_portfolio_py_1 -.->|import_depends| src_zephyr_backtest_core_data_handler_py_1
    src_zephyr_backtest_core_matching_engine_py_1 -.->|import_depends| src_zephyr_backtest_core_portfolio_py_1
    src_zephyr_backtest_core_matching_engine_py_1 -.->|import_depends| src_zephyr_backtest_core_matching_logic_py_1
    src_zephyr_backtest_init_py -.->|import_depends| src_zephyr_backtest_core_engine_base_py
    src_zephyr_backtest_init_py -.->|import_depends| src_zephyr_backtest_implementations_vectorized_engine_py
    src_zephyr_backtest_init_py -.->|import_depends| src_zephyr_backtest_io_init_py
    src_zephyr_backtest_core_data_handler_py -.->|import_depends| src_zephyr_backtest_core_pit_manager_py
    src_zephyr_backtest_core_tick_replay_py -.->|import_depends| src_zephyr_backtest_core_matching_logic_py
    src_zephyr_backtest_core_matching_engine_py -.->|import_depends| src_zephyr_backtest_core_matching_logic_py
    src_zephyr_backtest_core_matching_engine_py -.->|import_depends| src_zephyr_backtest_core_portfolio_py
    src_zephyr_backtest_io_backtest_result_sink_py -.->|import_depends| src_zephyr_backtest_core_engine_base_py
    src_zephyr_backtest_implementations_vectorized_engine_py -->|import_depends| src_zephyr_backtest_core_engine_base_py
    src_zephyr_backtest_implementations_vectorized_engine_py -.->|import_depends| src_zephyr_backtest_core_decision_gate_py
    src_zephyr_backtest_implementations_vectorized_engine_py -.->|import_depends| src_zephyr_backtest_core_matching_engine_py
    src_zephyr_backtest_implementations_vectorized_engine_py -.->|import_depends| src_zephyr_backtest_core_metrics_py
    src_zephyr_backtest_implementations_vectorized_engine_py -.->|import_depends| src_zephyr_backtest_core_walk_forward_py
    src_zephyr_backtest_implementations_vectorized_engine_py -.->|import_depends| src_zephyr_backtest_core_overfitting_detector_py
    src_zephyr_backtest_implementations_vectorized_engine_py -.->|import_depends| src_zephyr_backtest_core_portfolio_py
    src_zephyr_backtest_core_init_py -.->|import_depends| src_zephyr_backtest_core_engine_base_py
    src_zephyr_backtest_core_init_py -.->|import_depends| src_zephyr_backtest_core_decision_gate_py
    src_zephyr_backtest_core_init_py -.->|import_depends| src_zephyr_backtest_core_data_handler_py
    src_zephyr_backtest_core_init_py -.->|import_depends| src_zephyr_backtest_core_matching_engine_py
    src_zephyr_backtest_core_init_py -.->|import_depends| src_zephyr_backtest_core_metrics_py
    src_zephyr_backtest_core_init_py -.->|import_depends| src_zephyr_backtest_core_walk_forward_py
    src_zephyr_backtest_core_init_py -.->|import_depends| src_zephyr_backtest_core_overfitting_detector_py
    src_zephyr_backtest_core_init_py -.->|import_depends| src_zephyr_backtest_core_pit_manager_py
    src_zephyr_backtest_core_init_py -.->|import_depends| src_zephyr_backtest_core_portfolio_py
    src_zephyr_backtest_implementations_event_driven_engine_py -.->|import_depends| src_zephyr_backtest_core_engine_base_py
    src_zephyr_backtest_implementations_event_driven_engine_py -.->|import_depends| src_zephyr_backtest_core_decision_gate_py
    src_zephyr_backtest_implementations_event_driven_engine_py -.->|import_depends| src_zephyr_backtest_core_tick_replay_py
    src_zephyr_backtest_implementations_event_driven_engine_py -.->|import_depends| src_zephyr_backtest_core_matching_engine_py
    src_zephyr_backtest_implementations_event_driven_engine_py -.->|import_depends| src_zephyr_backtest_core_metrics_py
    src_zephyr_backtest_implementations_event_driven_engine_py -.->|import_depends| src_zephyr_backtest_core_walk_forward_py
    src_zephyr_backtest_implementations_event_driven_engine_py -.->|import_depends| src_zephyr_backtest_core_overfitting_detector_py
    src_zephyr_backtest_implementations_event_driven_engine_py -.->|import_depends| src_zephyr_backtest_core_portfolio_py
    src_zephyr_backtest_implementations_event_driven_engine_py -.->|import_depends| src_zephyr_backtest_implementations_vectorized_engine_py
    src_zephyr_backtest_implementations_init_py -.->|import_depends| src_zephyr_backtest_implementations_vectorized_engine_py
    src_zephyr_backtest_implementations_init_py -.->|import_depends| src_zephyr_backtest_implementations_event_driven_engine_py
    src_zephyr_backtest_io_decisiongraph_adapter_py -->|import_depends| src_zephyr_backtest_core_engine_base_py
    src_zephyr_backtest_io_result_repository_py -.->|import_depends| src_zephyr_backtest_io_backtest_result_sink_py
    src_zephyr_backtest_io_init_py -.->|import_depends| src_zephyr_backtest_io_backtest_result_sink_py
    src_zephyr_backtest_io_init_py -.->|import_depends| src_zephyr_backtest_io_decisiongraph_adapter_py
    src_zephyr_backtest_io_init_py -.->|import_depends| src_zephyr_backtest_io_result_repository_py
    D_GOVERNANCE["D_GOVERNANCE design"]
    src_zephyr_backtest_core_tick_replay_py_1 -.->|import_depends| D_GOVERNANCE
    src_zephyr_backtest_core_data_handler_py_1 -.->|import_depends| D_GOVERNANCE
    src_zephyr_backtest_io_decisiongraph_adapter_py -->|import_depends| D_GOVERNANCE
    D_INFRA_RUNTIME["D_INFRA_RUNTIME prototype"]
    src_zephyr_backtest_core_data_handler_py -.->|import_depends| D_INFRA_RUNTIME
    D_SHARED["D_SHARED production"]
    src_zephyr_backtest_core_engine_base_py -->|import_depends| D_SHARED
    D_EX_CORE["D_EX_CORE design"]
    D_EX_CORE -.->|import_depends| src_zephyr_backtest_core_matching_logic_py_1
    D_FRONTEND["D_FRONTEND design"]
    D_FRONTEND -.->|import_depends| src_zephyr_backtest_core_tick_replay_py_1
    D_GOVERNANCE -.->|import_depends| src_zephyr_backtest_core_data_handler_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_backtest_core_matching_logic_py
    D_AUDITTEST["D_AUDITTEST prototype"]
    D_AUDITTEST -.->|test_depends| src_zephyr_backtest_core_engine_base_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_backtest_core_matching_logic_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_backtest_core_portfolio_py
    D_INTELLIGENCE["D_INTELLIGENCE prototype"]
    D_INTELLIGENCE -.->|import_depends| src_zephyr_backtest_implementations_vectorized_engine_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_backtest_implementations_vectorized_engine_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_backtest_core_tick_replay_py
    D_AUDITTEST -.->|test_depends| src_zephyr_backtest_io_decisiongraph_adapter_py
    D_INTELLIGENCE -.->|import_depends| src_zephyr_backtest_core_engine_base_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_backtest_core_engine_base_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_backtest_core_matching_engine_py
    D_INTELLIGENCE -.->|import_depends| src_zephyr_backtest_implementations_vectorized_engine_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_backtest_core_engine_base_py,src_zephyr_backtest_implementations_vectorized_engine_py,src_zephyr_backtest_io_decisiongraph_adapter_py production
    class src_zephyr_backtest_init_py,src_zephyr_backtest_extensions_init_py,src_zephyr_backtest_api_init_py,src_zephyr_backtest_core_init_py,src_zephyr_backtest_core_data_handler_py,src_zephyr_backtest_core_data_handler_py_1,src_zephyr_backtest_core_decision_gate_py,src_zephyr_backtest_core_matching_engine_py,src_zephyr_backtest_core_matching_engine_py_1,src_zephyr_backtest_core_matching_logic_py,src_zephyr_backtest_core_matching_logic_py_1,src_zephyr_backtest_core_metrics_py,src_zephyr_backtest_core_metrics_py_1,src_zephyr_backtest_core_overfitting_detector_py,src_zephyr_backtest_core_pit_manager_py,src_zephyr_backtest_core_portfolio_py,src_zephyr_backtest_core_portfolio_py_1,src_zephyr_backtest_core_tick_replay_py,src_zephyr_backtest_core_tick_replay_py_1,src_zephyr_backtest_core_walk_forward_py,src_zephyr_backtest_implementations_init_py,src_zephyr_backtest_implementations_event_driven_engine_py,src_zephyr_backtest_infrastructure_init_py,src_zephyr_backtest_io_init_py,src_zephyr_backtest_io_backtest_result_sink_py,src_zephyr_backtest_io_backtest_result_sink_py_1,src_zephyr_backtest_io_result_repository_py design
    class D_SHARED external_prod
    class D_GOVERNANCE,D_INFRA_RUNTIME,D_EX_CORE,D_FRONTEND,D_AUDITTEST,D_INTELLIGENCE external_design
```

### 第 2 页 / 共 2 页 / Page 2 of 2

```mermaid
graph TD
    subgraph D_BACKTEST["D_BACKTEST 回测"]
        src_zephyr_backtest_io_result_repository_py["src/zephyr/backtest/io/result_repository.py/ design"]
        src_zephyr_backtest_models_init_py["src/zephyr/backtest/models/__init__.py prototype"]
        src_zephyr_backtest_services_init_py["src/zephyr/backtest/services/__init__.py prototype"]
    end
    D_FRONTEND["D_FRONTEND design"]
    D_FRONTEND -.->|import| src_zephyr_backtest_io_result_repository_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_backtest_io_result_repository_py,src_zephyr_backtest_models_init_py,src_zephyr_backtest_services_init_py design
    class D_FRONTEND external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 / Target Domain | 依赖数 / Count | 依赖类型 / Type |
|--------|:---:|---------|
| D_GOVERNANCE | 3 | import_depends |
| D_INFRA_RUNTIME | 1 | import_depends |
| D_SHARED | 1 | import_depends |

### 依赖本域的其他域（入边）/ Depended By

| 源域 / Source Domain | 依赖数 / Count | 依赖类型 / Type |
|------|:---:|---------|
| D_GOVERNANCE | 11 | import_depends |
| D_INTELLIGENCE | 3 | import_depends |
| D_AUDITTEST | 2 | test_depends |
| D_EX_CORE | 2 | import_depends |
| D_FRONTEND | 2 | import,import_depends |

## 架构分层视图 / Architecture Overview

> 按 architecture_layer 分层显示 回测（D_BACKTEST）的模块分布。共 33 个模块 / 33 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (33 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/backtest/__init__.py  [prototype]                   │
│   src/zephyr/backtest/_extensions/__init__.py  [prototype]       │
│   src/zephyr/backtest/api/__init__.py  [prototype]               │
│   src/zephyr/backtest/core/__init__.py  [prototype]              │
│   src/zephyr/backtest/core/data_handler.py  [prototype]          │
│   src/zephyr/backtest/core/data_handler.py/  [design]            │
│   src/zephyr/backtest/core/decision_gate.py  [prototype]         │
│   src/zephyr/backtest/core/engine_base.py  [production]          │
│   src/zephyr/backtest/core/matching_engine.py  [prototype]       │
│   src/zephyr/backtest/core/matching_engine.py/  [design]         │
│   src/zephyr/backtest/core/matching_logic.py  [prototype]        │
│   src/zephyr/backtest/core/matching_logic.py/  [design]          │
│   src/zephyr/backtest/core/metrics.py  [prototype]               │
│   src/zephyr/backtest/core/metrics.py/  [design]                 │
│   src/zephyr/backtest/core/overfitting_detector.py  [prototype]  │
│   src/zephyr/backtest/core/pit_manager.py  [prototype]           │
│   src/zephyr/backtest/core/portfolio.py  [prototype]             │
│   src/zephyr/backtest/core/portfolio.py/  [design]               │
│   ...还有 15 个模块 / 15 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 33 个模块 / 33 modules）。

### L2 领域层 / Domain Layer (33 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/backtest/__init__.py | src/zephyr/backtest/__init__.py | prototype | generated |
| 2 | src/zephyr/backtest/_extensions/__init__.py | src/zephyr/backtest/_extensions/__ini... | prototype | generated |
| 3 | src/zephyr/backtest/api/__init__.py | src/zephyr/backtest/api/__init__.py | prototype | generated |
| 4 | src/zephyr/backtest/core/__init__.py | src/zephyr/backtest/core/__init__.py | prototype | generated |
| 5 | src/zephyr/backtest/core/data_handler.py | src/zephyr/backtest/core/data_handler.py | prototype | generated |
| 6 | src/zephyr/backtest/core/data_handler.py/ | src/zephyr/backtest/core/data_handler... | design | generated |
| 7 | src/zephyr/backtest/core/decision_gate.py | src/zephyr/backtest/core/decision_gat... | prototype | generated |
| 8 | src/zephyr/backtest/core/engine_base.py | src/zephyr/backtest/core/engine_base.py | production | generated |
| 9 | src/zephyr/backtest/core/matching_engine.py | src/zephyr/backtest/core/matching_eng... | prototype | generated |
| 10 | src/zephyr/backtest/core/matching_engine.py/ | src/zephyr/backtest/core/matching_eng... | design | generated |
| 11 | src/zephyr/backtest/core/matching_logic.py | src/zephyr/backtest/core/matching_log... | prototype | generated |
| 12 | src/zephyr/backtest/core/matching_logic.py/ | src/zephyr/backtest/core/matching_log... | design | stable |
| 13 | src/zephyr/backtest/core/metrics.py | src/zephyr/backtest/core/metrics.py | prototype | generated |
| 14 | src/zephyr/backtest/core/metrics.py/ | src/zephyr/backtest/core/metrics.py/ | design | generated |
| 15 | src/zephyr/backtest/core/overfitting_detector.py | src/zephyr/backtest/core/overfitting_... | prototype | generated |
| 16 | src/zephyr/backtest/core/pit_manager.py | src/zephyr/backtest/core/pit_manager.py | prototype | generated |
| 17 | src/zephyr/backtest/core/portfolio.py | src/zephyr/backtest/core/portfolio.py | prototype | generated |
| 18 | src/zephyr/backtest/core/portfolio.py/ | src/zephyr/backtest/core/portfolio.py/ | design | generated |
| 19 | src/zephyr/backtest/core/tick_replay.py | src/zephyr/backtest/core/tick_replay.py | prototype | generated |
| 20 | src/zephyr/backtest/core/tick_replay.py/ | src/zephyr/backtest/core/tick_replay.py/ | design | stable |
| 21 | src/zephyr/backtest/core/walk_forward.py | src/zephyr/backtest/core/walk_forward.py | prototype | generated |
| 22 | src/zephyr/backtest/implementations/__init__.py | src/zephyr/backtest/implementations/_... | prototype | generated |
| 23 | src/zephyr/backtest/implementations/event_driven_engine.py | src/zephyr/backtest/implementations/e... | prototype | generated |
| 24 | src/zephyr/backtest/implementations/vectorized_engine.py | src/zephyr/backtest/implementations/v... | production | generated |
| 25 | src/zephyr/backtest/infrastructure/__init__.py | src/zephyr/backtest/infrastructure/__... | prototype | generated |
| 26 | src/zephyr/backtest/io/__init__.py | src/zephyr/backtest/io/__init__.py | prototype | generated |
| 27 | src/zephyr/backtest/io/backtest_result_sink.py | src/zephyr/backtest/io/backtest_resul... | prototype | generated |
| 28 | src/zephyr/backtest/io/backtest_result_sink.py/ | src/zephyr/backtest/io/backtest_resul... | design | generated |
| 29 | src/zephyr/backtest/io/decisiongraph_adapter.py | src/zephyr/backtest/io/decisiongraph_... | production | generated |
| 30 | src/zephyr/backtest/io/result_repository.py | src/zephyr/backtest/io/result_reposit... | prototype | generated |
| 31 | src/zephyr/backtest/io/result_repository.py/ | src/zephyr/backtest/io/result_reposit... | design | generated |
| 32 | src/zephyr/backtest/models/__init__.py | src/zephyr/backtest/models/__init__.py | prototype | generated |
| 33 | src/zephyr/backtest/services/__init__.py | src/zephyr/backtest/services/__init__.py | prototype | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 44 条 / 44 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 44 条 / 44 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [import_depends]: 43 条 / edges                                │
│   [import]: 1 条 / edges                                         │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (43 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│    →                                                             │
│    →                                                             │
│    →                                                             │
│   __init__.py → engine_base.py                                   │
│   __init__.py → vectorized_engine.py                             │
│   __init__.py → __init__.py                                      │
│   data_handler.py → pit_manager.py                               │
│   tick_replay.py → matching_logic.py                             │
│   matching_engine.py → matching_logic.py                         │
│   matching_engine.py → portfolio.py                              │
│   backtest_result_sink.py → engine_base.py                       │
│   vectorized_engine.py → engine_base.py                          │
│   vectorized_engine.py → decision_gate.py                        │
│   vectorized_engine.py → matching_engine.py                      │
│   vectorized_engine.py → metrics.py                              │
│   vectorized_engine.py → walk_forward.py                         │
│   vectorized_engine.py → overfitting_detector.py                 │
│   vectorized_engine.py → portfolio.py                            │
│   __init__.py → engine_base.py                                   │
│   __init__.py → decision_gate.py                                 │
│   __init__.py → data_handler.py                                  │
│   __init__.py → matching_engine.py                               │
│   __init__.py → metrics.py                                       │
│   __init__.py → walk_forward.py                                  │
│   __init__.py → overfitting_detector.py                          │
│   __init__.py → pit_manager.py                                   │
│   __init__.py → portfolio.py                                     │
│   event_driven_engine.py → engine_base.py                        │
│   event_driven_engine.py → decision_gate.py                      │
│   event_driven_engine.py → tick_replay.py                        │
│   event_driven_engine.py → matching_engine.py                    │
│   event_driven_engine.py → metrics.py                            │
│   event_driven_engine.py → walk_forward.py                       │
│   event_driven_engine.py → overfitting_detector.py               │
│   event_driven_engine.py → portfolio.py                          │
│   event_driven_engine.py → vectorized_engine.py                  │
│   __init__.py → vectorized_engine.py                             │
│   __init__.py → event_driven_engine.py                           │
│   decisiongraph_adapter.py → engine_base.py                      │
│   result_repository.py → backtest_result_sink.py                 │
│   __init__.py → backtest_result_sink.py                          │
│   __init__.py → decisiongraph_adapter.py                         │
│   __init__.py → result_repository.py                             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                     [import] (1 条 / edges)                      │
├──────────────────────────────────────────────────────────────────┤
│    →                                                             │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
