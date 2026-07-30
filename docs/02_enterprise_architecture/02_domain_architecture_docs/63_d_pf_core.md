---
doc_type: architecture_view
title: D_PF_CORE 组合核心架构文档
version: "1.0"
status: active
date: 2026-07-30
owner: auto-generator
ttl: permanent
---

# 63_d_pf_core / 组合核心 / Portfolio Core

> **功能简介 / Overview**: 组合核心，负责投资组合构建、持仓管理和组合优化

> **文档作用 / Purpose**: 展示 组合核心（D_PF_CORE）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 63 | Number | 63 |
| 域ID | D_PF_CORE | Domain ID | D_PF_CORE |
| 域名称 | 组合核心 | Domain Name | Portfolio Core |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 3 | Module Count | 3 |
| 域内依赖 | 0 | Internal Dependencies | 0 |
| 跨域入边 | 1 | Cross-domain Incoming | 1 |
| 跨域出边 | 3 | Cross-domain Outgoing | 3 |
| 设计态模块 | 2 | Design Modules | 2 |
| 生产态模块 | 1 | Production Modules | 1 |
| 容量 | 1/150 (正常) | Capacity | 1/150 (正常) |
| 描述 | 组合核心，负责投资组合构建、持仓管理和组合优化 | Description | 组合核心，负责投资组合构建、持仓管理和组合优化 |

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 3 个模块 / 3 modules）。

### L0 基础设施层 / Infrastructure Layer (1 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/pf_core/strategy_engine/__init__.py | D_PORTFOLIO_CORE — Portfolio Construction Stra... | 生产态 / production |  |

### L2 领域层 / Domain Layer (2 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/pf_core/strategy_engine/strategy_runner.py | D_PORTFOLIO_CORE — StrategyRunner 策略运行器（... | 设计态 / design |  |
| 2 | src/zephyr/pf_core/topn_momentum_strategy.py | D_PORTFOLIO_CORE — TopN 动量等权策略 | 设计态 / design |  |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。参考 decision_index.md 设计，分三个视图：合并全景图、运营态子图、设计态子图（按 design_maturity 实际值拆分）。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 合并全景图（全部模块，标签标注成熟度）

> 展示全部 3 个模块（生产态 1 + 设计态 2），标签标注成熟度。

```mermaid
graph TD
    subgraph D_PF_CORE["D_PF_CORE 组合核心"]
        src_zephyr_pf_core_strategy_engine_init_py["(生产态 / production) D_PORTFOLIO_CORE — Portfolio Construction Stra...<br/>文件: __init__.py"]
        src_zephyr_pf_core_strategy_engine_strategy_runner_py["(设计态 / design) D_PORTFOLIO_CORE — StrategyRunner 策略运行器（...<br/>文件: strategy_runner.py"]
        src_zephyr_pf_core_topn_momentum_strategy_py["(设计态 / design) D_PORTFOLIO_CORE — TopN 动量等权策略<br/>文件: topn_momentum_strategy.py"]
    end
    D_PF_ALLOC["(生产态 / production) D_PF_ALLOC"]
    src_zephyr_pf_core_strategy_engine_init_py -->|导入依赖 / import_depends| D_PF_ALLOC
    D_EX_CORE["(设计态 / design) D_EX_CORE"]
    D_EX_CORE -.->|导入依赖 / import_depends| src_zephyr_pf_core_strategy_engine_strategy_runner_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_pf_core_strategy_engine_init_py production
    class src_zephyr_pf_core_strategy_engine_strategy_runner_py,src_zephyr_pf_core_topn_momentum_strategy_py design
    class D_PF_ALLOC external_prod
    class D_EX_CORE external_design
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 仅展示已上线运行的模块（共 1 个，0 条域内依赖）。

```mermaid
graph TD
    subgraph D_PF_CORE["D_PF_CORE 组合核心"]
        src_zephyr_pf_core_strategy_engine_init_py["(生产态 / production) D_PORTFOLIO_CORE — Portfolio Construction Stra...<br/>文件: __init__.py"]
    end
    D_PF_ALLOC["(生产态 / production) D_PF_ALLOC"]
    src_zephyr_pf_core_strategy_engine_init_py -->|导入依赖 / import_depends| D_PF_ALLOC
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_pf_core_strategy_engine_init_py production
    class D_PF_ALLOC external_prod
```

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 2 个，0 条域内依赖）。

```mermaid
graph TD
    subgraph D_PF_CORE["D_PF_CORE 组合核心"]
        src_zephyr_pf_core_strategy_engine_strategy_runner_py["(设计态 / design) D_PORTFOLIO_CORE — StrategyRunner 策略运行器（...<br/>文件: strategy_runner.py"]
        src_zephyr_pf_core_topn_momentum_strategy_py["(设计态 / design) D_PORTFOLIO_CORE — TopN 动量等权策略<br/>文件: topn_momentum_strategy.py"]
    end
    D_EX_CORE["(设计态 / design) D_EX_CORE"]
    D_EX_CORE -.->|导入依赖 / import_depends| src_zephyr_pf_core_strategy_engine_strategy_runner_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_pf_core_strategy_engine_strategy_runner_py,src_zephyr_pf_core_topn_momentum_strategy_py design
    class D_EX_CORE external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_PORTFOLIO_CORE — Portfolio Construction Stra... | → | D_PF_ALLOC 组合分配: D_PORTFOLIO_CORE — Default Equity Long-Only St... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_EX_CORE 执行核心: D_EXECUTION_CORE — TradingSession 盘中实时调仓... | → | D_PORTFOLIO_CORE — StrategyRunner 策略运行器（... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 4 个外部域直接连接（出边 3 条 + 入边 1 条 = 4 条）。只显示直接连接的域，不展开具体节点。

```mermaid
graph LR
    D_PF_CORE["D_PF_CORE<br/>组合核心"]
    D_PF_ALLOC["D_PF_ALLOC<br/>组合分配"]
    D_POSITION["D_POSITION<br/>仓位管理"]
    D_RISK["D_RISK<br/>风控"]
    D_EX_CORE["D_EX_CORE<br/>执行核心"]
    D_PF_CORE -->|1条 导入依赖 / import_depends| D_PF_ALLOC
    D_PF_CORE -->|1条 导入依赖 / import_depends| D_POSITION
    D_PF_CORE -->|1条 导入依赖 / import_depends| D_RISK
    D_EX_CORE -->|1条 导入依赖 / import_depends| D_PF_CORE
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
