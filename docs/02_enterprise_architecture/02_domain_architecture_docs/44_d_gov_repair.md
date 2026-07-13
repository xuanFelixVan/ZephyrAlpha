---
doc_type: architecture_view
title: D_GOV_REPAIR 治理修复架构文档
version: "1.0"
status: active
date: 2026-07-13
owner: auto-generator
ttl: permanent
---

# 44_d_gov_repair / rollback / 治理修复 / Governance Repair

> **功能简介 / Overview**: 治理修复，负责治理问题自动修复和修复策略管理

> **文档作用 / Purpose**: 展示 治理修复（D_GOV_REPAIR）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-13 22:42:51
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 44 | Number | 44 |
| 域ID | D_GOV_REPAIR | Domain ID | D_GOV_REPAIR |
| 域名称 | 治理修复 | Domain Name | Governance Repair |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 20 | Module Count | 20 |
| 域内依赖 | 0 | Internal Dependencies | 0 |
| 跨域入边 | 2 | Cross-domain Incoming | 2 |
| 跨域出边 | 61 | Cross-domain Outgoing | 61 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 17 | Prototype Modules | 17 |
| 生产态模块 | 3 | Production Modules | 3 |
| 容量 | 3/150 (正常) | Capacity | 3/150 (正常) |
| 描述 | 双轨Checkpoint(git commit + SQLite JSONL dump) | Description | 双轨Checkpoint(git commit + SQLite JSONL dump) |

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 20 个模块 / 20 modules）。

### L2 领域层 / Domain Layer (20 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/governance/adapters/__init__.py | __init__.py | 原型态 / prototype |  |
| 2 | src/zephyr/governance/agent_spec/__init__.py | Agent Spec — MOD-INF-019 | 原型态 / prototype | [MOD-INF-019](../../03_modules/_domain_autonomy_core/agent_spec/blueprint.md) |
| 3 | src/zephyr/governance/architecture_governance/__init__.py | __init__.py | 原型态 / prototype |  |
| 4 | src/zephyr/governance/bridges/__init__.py | __init__.py | 原型态 / prototype |  |
| 5 | src/zephyr/governance/context_governance/__init__.py | __init__.py | 原型态 / prototype |  |
| 6 | src/zephyr/governance/data_governance/__init__.py | __init__.py | 原型态 / prototype |  |
| 7 | src/zephyr/governance/engine/__init__.py | D_FACTOR — Factors Package | 原型态 / prototype | [MOD-L02-001](../../03_modules/_domain_factor/blueprint.md) |
| 8 | src/zephyr/governance/financial_governance/__init__.py | __init__.py | 原型态 / prototype |  |
| 9 | src/zephyr/governance/financial_governance/budget_enforce... | budget_enforcement.py | 生产态 / production | [MOD-INF-024](../../03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md) |
| 10 | src/zephyr/governance/intelligence_governance/__init__.py | __init__.py | 原型态 / prototype |  |
| 11 | src/zephyr/governance/lifecycle_governance/__init__.py | __init__.py | 原型态 / prototype |  |
| 12 | src/zephyr/governance/observability_governance/__init__.py | __init__.py | 生产态 / production |  |
| 13 | src/zephyr/governance/persistence/__init__.py | __init__.py | 生产态 / production | [MOD-GOVERNANCE](../../03_modules/_domain_governance/blueprint.md) |
| 14 | src/zephyr/governance/services/__init__.py | __init__.py | 原型态 / prototype |  |
| 15 | src/zephyr/governance/strategies/__init__.py | Re-export wrapper: true source is zephyr.pf_cor... | 原型态 / prototype |  |
| 16 | src/zephyr/governance/trading_contracts/__init__.py | zephyr.trading.trading_contracts — trading-dom... | 原型态 / prototype | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 17 | src/zephyr/governance/trading_contracts/execution/__init_... | __init__.py | 原型态 / prototype |  |
| 18 | src/zephyr/governance/trading_contracts/market/__init__.py | __init__.py | 原型态 / prototype |  |
| 19 | src/zephyr/governance/trading_contracts/portfolio/contrac... | __init__.py | 原型态 / prototype |  |
| 20 | src/zephyr/governance/trading_contracts/risk/__init__.py | __init__.py | 原型态 / prototype |  |

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

> 展示全部 20 个模块（生产态 3 + 设计态 0 + 原型态 17），标签标注成熟度。

```mermaid
graph TD
    subgraph D_GOV_REPAIR["D_GOV_REPAIR 治理修复"]
        src_zephyr_governance_adapters_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_agent_spec_init_py["(原型态 / prototype) Agent Spec — MOD-INF-019<br/>文件: __init__.py"]
        src_zephyr_governance_architecture_governance_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_bridges_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_context_governance_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_data_governance_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_engine_init_py["(原型态 / prototype) D_FACTOR — Factors Package<br/>文件: __init__.py"]
        src_zephyr_governance_financial_governance_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_financial_governance_budget_enforcement_py["(生产态 / production) budget_enforcement.py"]
        src_zephyr_governance_intelligence_governance_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_lifecycle_governance_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_observability_governance_init_py["(生产态 / production) __init__.py"]
        src_zephyr_governance_persistence_init_py["(生产态 / production) __init__.py"]
        src_zephyr_governance_services_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_strategies_init_py["(原型态 / prototype) Re-export wrapper: true source is zephyr.pf_cor...<br/>文件: __init__.py"]
        src_zephyr_governance_trading_contracts_init_py["(原型态 / prototype) zephyr.trading.trading_contracts — trading-dom...<br/>文件: __init__.py"]
        src_zephyr_governance_trading_contracts_execution_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_trading_contracts_market_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_trading_contracts_portfolio_contracts_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_trading_contracts_risk_init_py["(原型态 / prototype) __init__.py"]
    end
    D_GOVERNANCE["(原型态 / prototype) D_GOVERNANCE"]
    src_zephyr_governance_agent_spec_init_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_governance_adapters_init_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_governance_adapters_init_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_governance_adapters_init_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_governance_bridges_init_py -.->|config_depends / config_depends| D_GOVERNANCE
    src_zephyr_governance_context_governance_init_py -.->|config_depends / config_depends| D_GOVERNANCE
    src_zephyr_governance_engine_init_py -.->|config_depends / config_depends| D_GOVERNANCE
    D_AUTONOMY_CORE["(生产态 / production) D_AUTONOMY_CORE"]
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_AUTONOMY_CORE
    D_OPS["(生产态 / production) D_OPS"]
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_OPS
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_OPS
    D_GOV_OPS_RESILIENCE["(生产态 / production) D_GOV_OPS_RESILIENCE"]
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_OPS
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_governance_financial_governance_budget_enforcement_py
    D_DATA["(原型态 / prototype) D_DATA"]
    D_DATA -.->|测试依赖 / test_depends| src_zephyr_governance_observability_governance_init_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_governance_financial_governance_budget_enforcement_py,src_zephyr_governance_observability_governance_init_py,src_zephyr_governance_persistence_init_py production
    class src_zephyr_governance_adapters_init_py,src_zephyr_governance_agent_spec_init_py,src_zephyr_governance_architecture_governance_init_py,src_zephyr_governance_bridges_init_py,src_zephyr_governance_context_governance_init_py,src_zephyr_governance_data_governance_init_py,src_zephyr_governance_engine_init_py,src_zephyr_governance_financial_governance_init_py,src_zephyr_governance_intelligence_governance_init_py,src_zephyr_governance_lifecycle_governance_init_py,src_zephyr_governance_services_init_py,src_zephyr_governance_strategies_init_py,src_zephyr_governance_trading_contracts_init_py,src_zephyr_governance_trading_contracts_execution_init_py,src_zephyr_governance_trading_contracts_market_init_py,src_zephyr_governance_trading_contracts_portfolio_contracts_init_py,src_zephyr_governance_trading_contracts_risk_init_py design
    class D_AUTONOMY_CORE,D_OPS,D_GOV_OPS_RESILIENCE external_prod
    class D_GOVERNANCE,D_DATA external_design
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 仅展示已上线运行的模块（共 3 个，0 条域内依赖）。

```mermaid
graph TD
    subgraph D_GOV_REPAIR["D_GOV_REPAIR 治理修复"]
        src_zephyr_governance_financial_governance_budget_enforcement_py["(生产态 / production) budget_enforcement.py"]
        src_zephyr_governance_observability_governance_init_py["(生产态 / production) __init__.py"]
        src_zephyr_governance_persistence_init_py["(生产态 / production) __init__.py"]
    end
    D_OPS["(生产态 / production) D_OPS"]
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_OPS
    D_GOV_OPS_RESILIENCE["(生产态 / production) D_GOV_OPS_RESILIENCE"]
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_OPS
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_OPS
    D_AUTONOMY_CORE["(生产态 / production) D_AUTONOMY_CORE"]
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_AUTONOMY_CORE
    src_zephyr_governance_persistence_init_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_governance_financial_governance_budget_enforcement_py
    D_DATA["(原型态 / prototype) D_DATA"]
    D_DATA -.->|测试依赖 / test_depends| src_zephyr_governance_observability_governance_init_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_governance_financial_governance_budget_enforcement_py,src_zephyr_governance_observability_governance_init_py,src_zephyr_governance_persistence_init_py production
    class D_OPS,D_GOV_OPS_RESILIENCE,D_GOVERNANCE,D_AUTONOMY_CORE external_prod
    class D_DATA external_design
```

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个，0 条域内依赖）。

> （无设计态模块 / No design modules）

### 原型态子图（仅 design_maturity=prototype 的模块和依赖）

> 仅展示代码已写、验证中未稳定上线的原型态模块（共 17 个，0 条域内依赖）。

```mermaid
graph TD
    subgraph D_GOV_REPAIR["D_GOV_REPAIR 治理修复"]
        src_zephyr_governance_adapters_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_agent_spec_init_py["(原型态 / prototype) Agent Spec — MOD-INF-019<br/>文件: __init__.py"]
        src_zephyr_governance_architecture_governance_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_bridges_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_context_governance_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_data_governance_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_engine_init_py["(原型态 / prototype) D_FACTOR — Factors Package<br/>文件: __init__.py"]
        src_zephyr_governance_financial_governance_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_intelligence_governance_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_lifecycle_governance_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_services_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_strategies_init_py["(原型态 / prototype) Re-export wrapper: true source is zephyr.pf_cor...<br/>文件: __init__.py"]
        src_zephyr_governance_trading_contracts_init_py["(原型态 / prototype) zephyr.trading.trading_contracts — trading-dom...<br/>文件: __init__.py"]
        src_zephyr_governance_trading_contracts_execution_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_trading_contracts_market_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_trading_contracts_portfolio_contracts_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_governance_trading_contracts_risk_init_py["(原型态 / prototype) __init__.py"]
    end
    D_GOVERNANCE["(原型态 / prototype) D_GOVERNANCE"]
    src_zephyr_governance_agent_spec_init_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_governance_adapters_init_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_governance_adapters_init_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_governance_adapters_init_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_governance_bridges_init_py -.->|config_depends / config_depends| D_GOVERNANCE
    src_zephyr_governance_context_governance_init_py -.->|config_depends / config_depends| D_GOVERNANCE
    src_zephyr_governance_engine_init_py -.->|config_depends / config_depends| D_GOVERNANCE
    src_zephyr_governance_financial_governance_init_py -.->|config_depends / config_depends| D_GOVERNANCE
    src_zephyr_governance_services_init_py -.->|config_depends / config_depends| D_GOVERNANCE
    src_zephyr_governance_strategies_init_py -.->|config_depends / config_depends| D_GOVERNANCE
    D_GOV_ENFORCEMENT["(原型态 / prototype) D_GOV_ENFORCEMENT"]
    src_zephyr_governance_trading_contracts_init_py -.->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_TRADING["(原型态 / prototype) D_TRADING"]
    src_zephyr_governance_trading_contracts_init_py -.->|导入依赖 / import_depends| D_TRADING
    D_INFRASTRUCTURE["(原型态 / prototype) D_INFRASTRUCTURE"]
    src_zephyr_governance_trading_contracts_init_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    D_SHARED["(原型态 / prototype) D_SHARED"]
    src_zephyr_governance_trading_contracts_init_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_governance_trading_contracts_init_py -.->|导入依赖 / import_depends| D_SHARED
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_governance_adapters_init_py,src_zephyr_governance_agent_spec_init_py,src_zephyr_governance_architecture_governance_init_py,src_zephyr_governance_bridges_init_py,src_zephyr_governance_context_governance_init_py,src_zephyr_governance_data_governance_init_py,src_zephyr_governance_engine_init_py,src_zephyr_governance_financial_governance_init_py,src_zephyr_governance_intelligence_governance_init_py,src_zephyr_governance_lifecycle_governance_init_py,src_zephyr_governance_services_init_py,src_zephyr_governance_strategies_init_py,src_zephyr_governance_trading_contracts_init_py,src_zephyr_governance_trading_contracts_execution_init_py,src_zephyr_governance_trading_contracts_market_init_py,src_zephyr_governance_trading_contracts_portfolio_contracts_init_py,src_zephyr_governance_trading_contracts_risk_init_py design
    class D_GOVERNANCE,D_GOV_ENFORCEMENT,D_TRADING,D_INFRASTRUCTURE,D_SHARED external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | budget_enforcement.py | → | D_AUTONOMY_CORE 自治核心: skill_executor.py | 导入依赖 / import_depends |
| 2 | __init__.py | → | D_GOVERNANCE 生命周期管理: D_EXECUTION_CORE — Risk Validation Bridge (DW-... | 导入依赖 / import_depends |
| 3 | __init__.py | → | D_GOVERNANCE 生命周期管理: D_EXECUTION_CORE — Simulation Broker Adapter (... | 导入依赖 / import_depends |
| 4 | __init__.py | → | D_GOVERNANCE 生命周期管理: D_EXECUTION_CORE — BrokerInterface (broker_int... | 导入依赖 / import_depends |
| 5 | Agent Spec — MOD-INF-019 (__init__.py) | → | D_GOVERNANCE 生命周期管理: G-CT-003 契约：Agent Spec -> RBAC 能力检查. (re... | 导入依赖 / import_depends |
| 6 | __init__.py | → | D_GOVERNANCE 生命周期管理: G-CT-006 — BudgetAlert re-exported from shared... | config_depends / config_depends |
| 7 | __init__.py | → | D_GOVERNANCE 生命周期管理: Command Chain Length Gate — v0.13.0 命令体积De... | config_depends / config_depends |
| 8 | D_FACTOR — Factors Package (__init__.py) | → | D_GOVERNANCE 生命周期管理: 实验 — Experimentation Pipeline Layer (pipelin... | config_depends / config_depends |
| 9 | __init__.py | → | D_GOVERNANCE 生命周期管理: Arbitrage Asymmetry Detector — v0.11.0 跨交易.... | config_depends / config_depends |
| 10 | budget_enforcement.py | → | D_GOVERNANCE 生命周期管理: model_router.py | 导入依赖 / import_depends |
| 11 | __init__.py | → | D_GOVERNANCE 生命周期管理: dataflowgraph Schema DDL + 连接入口 (dataflowgr... | 导入依赖 / import_depends |
| 12 | __init__.py | → | D_GOVERNANCE 生命周期管理: Memory Provenance — v0.9.0 记忆溯源追踪: 每条m... | config_depends / config_depends |
| 13 | Re-export wrapper: true source is zephyr.pf_cor... | → | D_GOVERNANCE 生命周期管理: StrategyRegistry 卫星模块（OCP-002） (strategy_... | config_depends / config_depends |
| 14 | __init__.py | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源已合并至 zephyr.trading.t... | 导入依赖 / import_depends |
| 15 | __init__.py | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源已合并至 zephyr.trading.t... | 导入依赖 / import_depends |
| 16 | __init__.py | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源已合并至 zephyr.trading.t... | 导入依赖 / import_depends |
| 17 | __init__.py | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源已合并至 zephyr.trading.t... | 导入依赖 / import_depends |
| 18 | __init__.py | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源已合并至 zephyr.trading.t... | 导入依赖 / import_depends |
| 19 | __init__.py | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源已合并至 zephyr.trading.t... | 导入依赖 / import_depends |
| 20 | __init__.py | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源已合并至 zephyr.trading.t... | 导入依赖 / import_depends |
| 21 | __init__.py | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源已合并至 zephyr.trading.t... | 导入依赖 / import_depends |
| 22 | __init__.py | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源已合并至 zephyr.trading.t... | 导入依赖 / import_depends |
| 23 | __init__.py | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源已合并至 zephyr.trading.t... | 导入依赖 / import_depends |
| 24 | __init__.py | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源已合并至 zephyr.trading.t... | 导入依赖 / import_depends |
| 25 | __init__.py | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源已合并至 zephyr.trading.t... | 导入依赖 / import_depends |
| 26 | __init__.py | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源已合并至 zephyr.trading.t... | 导入依赖 / import_depends |
| 27 | __init__.py | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源已合并至 zephyr.trading.t... | 导入依赖 / import_depends |
| 28 | __init__.py | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源已合并至 zephyr.trading.t... | 导入依赖 / import_depends |
| 29 | __init__.py | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源已合并至 zephyr.trading.t... | 导入依赖 / import_depends |
| 30 | __init__.py | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源已合并至 zephyr.trading.t... | 导入依赖 / import_depends |
| 31 | __init__.py | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源已合并至 zephyr.trading.t... | 导入依赖 / import_depends |
| 32 | __init__.py | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源已合并至 zephyr.trading.t... | 导入依赖 / import_depends |
| 33 | __init__.py | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源已合并至 zephyr.trading.t... | 导入依赖 / import_depends |
| 34 | zephyr.trading.trading_contracts — trading-dom... | → | D_GOV_ENFORCEMENT 规则执行: Re-export shim — ComplianceRule 真源已合并至 z... | 导入依赖 / import_depends |
| 35 | budget_enforcement.py | → | D_GOV_OPS_RESILIENCE 运维弹性治理: Burn Rate Monitor — MOD-INF-024 (burn_rate_mon... | 导入依赖 / import_depends |
| 36 | budget_enforcement.py | → | D_GOV_OPS_RESILIENCE 运维弹性治理: degradation_manager.py | 导入依赖 / import_depends |
| 37 | budget_enforcement.py | → | D_GOV_OPS_RESILIENCE 运维弹性治理: timeout_guard.py | 导入依赖 / import_depends |
| 38 | zephyr.trading.trading_contracts — trading-dom... | → | D_INFRASTRUCTURE: capital_allocation_result.py | 导入依赖 / import_depends |
| 39 | zephyr.trading.trading_contracts — trading-dom... | → | D_INFRASTRUCTURE: execution_report.py | 导入依赖 / import_depends |
| 40 | zephyr.trading.trading_contracts — trading-dom... | → | D_INFRASTRUCTURE: fill.py | 导入依赖 / import_depends |
| 41 | zephyr.trading.trading_contracts — trading-dom... | → | D_INFRASTRUCTURE: model_serving_request.py | 导入依赖 / import_depends |
| 42 | zephyr.trading.trading_contracts — trading-dom... | → | D_INFRASTRUCTURE: order.py | 导入依赖 / import_depends |
| 43 | zephyr.trading.trading_contracts — trading-dom... | → | D_INFRASTRUCTURE: position.py | 导入依赖 / import_depends |
| 44 | budget_enforcement.py | → | D_OPS 反馈循环: Budget Enforcer core engine — MOD-INF-024 (bud... | 导入依赖 / import_depends |
| 45 | budget_enforcement.py | → | D_OPS 反馈循环: Budget Enforcer data models — MOD-INF-024 (bud... | 导入依赖 / import_depends |
| 46 | budget_enforcement.py | → | D_OPS 反馈循环: budget_tracker.py | 导入依赖 / import_depends |
| 47 | zephyr.trading.trading_contracts — trading-dom... | → | D_SHARED 共享服务: OrderSide/OrderStatus/OrderType — 交易枚举真源... | 导入依赖 / import_depends |
| 48 | zephyr.trading.trading_contracts — trading-dom... | → | D_SHARED 共享服务: execution_rejection_error.py | 导入依赖 / import_depends |
| 49 | zephyr.trading.trading_contracts — trading-dom... | → | D_TRADING 交易运营: zephyr.trading.trading_contracts — trading-dom... | 导入依赖 / import_depends |
| 50 | zephyr.trading.trading_contracts — trading-dom... | → | D_TRADING 交易运营: factor_monitor_report.py | 导入依赖 / import_depends |
| 51 | zephyr.trading.trading_contracts — trading-dom... | → | D_TRADING 交易运营: factor_signal.py | 导入依赖 / import_depends |
| 52 | zephyr.trading.trading_contracts — trading-dom... | → | D_TRADING 交易运营: instrument.py | 导入依赖 / import_depends |
| 53 | zephyr.trading.trading_contracts — trading-dom... | → | D_TRADING 交易运营: macro_factor_signal.py | 导入依赖 / import_depends |
| 54 | zephyr.trading.trading_contracts — trading-dom... | → | D_TRADING 交易运营: market_data.py | 导入依赖 / import_depends |
| 55 | zephyr.trading.trading_contracts — trading-dom... | → | D_TRADING 交易运营: signal_degradation_warning.py | 导入依赖 / import_depends |
| 56 | zephyr.trading.trading_contracts — trading-dom... | → | D_TRADING 交易运营: synthesized_signal.py | 导入依赖 / import_depends |
| 57 | zephyr.trading.trading_contracts — trading-dom... | → | D_TRADING 交易运营: risk_dashboard_snapshot.py | 导入依赖 / import_depends |
| 58 | zephyr.trading.trading_contracts — trading-dom... | → | D_TRADING 交易运营: risk_limit_violation_error.py | 导入依赖 / import_depends |
| 59 | zephyr.trading.trading_contracts — trading-dom... | → | D_TRADING 交易运营: risk_limits.py | 导入依赖 / import_depends |
| 60 | zephyr.trading.trading_contracts — trading-dom... | → | D_TRADING 交易运营: risk_metrics.py | 导入依赖 / import_depends |
| 61 | zephyr.trading.trading_contracts — trading-dom... | → | D_TRADING 交易运营: risk_validator_protocol.py | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_DATA: test_db_query.py | → | __init__.py | 测试依赖 / test_depends |
| 2 | D_GOVERNANCE 生命周期管理: [INVARIANTS] 预算健康检查不可跳过;检查结果必须.... | → | budget_enforcement.py | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 9 个外部域直接连接（出边 61 条 + 入边 2 条 = 63 条）。只显示直接连接的域，不展开具体节点。

```mermaid
graph LR
    D_GOV_REPAIR["D_GOV_REPAIR<br/>治理修复"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE"]
    D_GOV_OPS_RESILIENCE["D_GOV_OPS_RESILIENCE<br/>运维弹性治理"]
    D_OPS["D_OPS<br/>反馈循环"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_DATA["D_DATA"]
    D_GOV_REPAIR -->|32条 config_depends / config_depends, 导入依赖 / import_depends| D_GOVERNANCE
    D_GOV_REPAIR -->|13条 导入依赖 / import_depends| D_TRADING
    D_GOV_REPAIR -->|6条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_GOV_REPAIR -->|3条 导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_GOV_REPAIR -->|3条 导入依赖 / import_depends| D_OPS
    D_GOV_REPAIR -->|2条 导入依赖 / import_depends| D_SHARED
    D_GOV_REPAIR -->|1条 导入依赖 / import_depends| D_AUTONOMY_CORE
    D_GOV_REPAIR -->|1条 导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_DATA -->|1条 测试依赖 / test_depends| D_GOV_REPAIR
    D_GOVERNANCE -->|1条 导入依赖 / import_depends| D_GOV_REPAIR
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
