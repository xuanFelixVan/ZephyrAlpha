---
doc_type: architecture_view
title: D_TRADING 交易运营架构文档
version: "1.0"
status: active
date: 2026-07-18
owner: auto-generator
ttl: permanent
---

# 58_d_trading / 交易运营 / 交易运营 / Trading Operations

> **功能简介 / Overview**: 交易运营，负责交易生命周期管理、订单状态和成交处理

> **文档作用 / Purpose**: 展示 交易运营（D_TRADING）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 58 | Number | 58 |
| 域ID | D_TRADING | Domain ID | D_TRADING |
| 域名称 | 交易运营 | Domain Name | Trading Operations |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 32 | Module Count | 32 |
| 域内依赖 | 9 | Internal Dependencies | 9 |
| 跨域入边 | 24 | Cross-domain Incoming | 24 |
| 跨域出边 | 36 | Cross-domain Outgoing | 36 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 11 | Prototype Modules | 11 |
| 生产态模块 | 21 | Production Modules | 21 |
| 容量 | 21/150 (正常) | Capacity | 21/150 (正常) |
| 描述 | 交易会话、交易接口、交易日志、交易复盘。交易运营中枢。合规检查由D-GOV_ENFORCEMENT门禁层执行。 | Description | 交易会话、交易接口、交易日志、交易复盘。交易运营中枢。合规检查由D-GOV_ENFORCEMENT门禁层执行。 |

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 32 个模块 / 32 modules）。

### L0 基础设施层 / Infrastructure Layer (4 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/trading/trading_contracts/broker_interface.py | D_EXECUTION_CORE — BrokerInterface | 生产态 / production | [MOD-L06-001](../../03_modules/_domain_execution_core/blueprint.md) |
| 2 | src/zephyr/trading/trading_contracts/portfolio/contracts/... | money.py | 生产态 / production | [MOD-L00-001](../../03_modules/_domain_data/blueprint.md) |
| 3 | src/zephyr/trading/trading_contracts/portfolio/contracts/... | Re-export shim — 真源已收敛至 zephyr.shared.co... | 原型态 / prototype | [MOD-L00-001](../../03_modules/_domain_data/blueprint.md) |
| 4 | src/zephyr/trading/trading_contracts/portfolio/contracts/... | strategy_lifecycle_event.py | 原型态 / prototype | [MOD-L00-001](../../03_modules/_domain_data/blueprint.md) |

### L2 领域层 / Domain Layer (28 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/trading/admission_controller.py | admission_controller.py | 生产态 / production | [MOD-INF-033](../../03_modules/_cross_layer/behavioral_auditor/blueprint.md) |
| 2 | src/zephyr/trading/auto_dispatcher.py | AutoDispatcher — 守护进程内的轻量 PipelineDisp... | 原型态 / prototype | [MOD-INF-039](../../03_modules/_cross_layer/agent_orchestrator/blueprint.md) |
| 3 | src/zephyr/trading/autopilot.py | AutoPilot — AI session 自动找活干、认领任务。 | 生产态 / production | [SH-DB-001](../../03_modules/_cross_layer/database/blueprint.md) |
| 4 | src/zephyr/trading/conductor.py | Conductor — AI session 全自动指挥官。 | 生产态 / production | [SH-DB-001](../../03_modules/_cross_layer/database/blueprint.md) |
| 5 | src/zephyr/trading/gpu_consensus_scheduler.py | gpu_consensus_scheduler.py | 生产态 / production | [MOD-INF-033](../../03_modules/_cross_layer/behavioral_auditor/blueprint.md) |
| 6 | src/zephyr/trading/gpu_monitor.py | gpu_monitor.py — NVIDIA GPU 状态采集器 | 原型态 / prototype | [MOD-RESOURCE_OPTIMIZATION_ENGINE](../../03_modules/_cross_layer/resource_optimization_engine/blueprint.md) |
| 7 | src/zephyr/trading/ide_health_daemon.py | ide_health_daemon.py — TRAE IDE 幽灵窗口守护线程 | 生产态 / production | [MOD-RESOURCE_OPTIMIZATION_ENGINE](../../03_modules/_cross_layer/resource_optimization_engine/blueprint.md) |
| 8 | src/zephyr/trading/protection_index.py | protection_index.py | 生产态 / production | [MOD-INF-033](../../03_modules/_cross_layer/behavioral_auditor/blueprint.md) |
| 9 | src/zephyr/trading/runtime/async_runtime.py | async_runtime.py | 生产态 / production | [MOD-INF-035](../../03_modules/_cross_layer/auto_runtime_core/blueprint.md) |
| 10 | src/zephyr/trading/speed_baseline_checker.py | speed_baseline_checker.py | 原型态 / prototype | [MOD-RESOURCE_OPTIMIZATION_ENGINE](../../03_modules/_cross_layer/resource_optimization_engine/blueprint.md) |
| 11 | src/zephyr/trading/trading_contracts/execution/capital_al... | capital_allocation_result.py | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 12 | src/zephyr/trading/trading_contracts/execution/execution_... | execution_rejection_error.py | 原型态 / prototype | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 13 | src/zephyr/trading/trading_contracts/execution/execution_... | execution_report.py | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 14 | src/zephyr/trading/trading_contracts/execution/fill.py | fill.py | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 15 | src/zephyr/trading/trading_contracts/execution/model_serv... | model_serving_request.py | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 16 | src/zephyr/trading/trading_contracts/execution/order.py | Re-export wrapper: Order 真源在 zephyr.shared.c... | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 17 | src/zephyr/trading/trading_contracts/execution/position.py | position.py | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 18 | src/zephyr/trading/trading_contracts/factories.py | trading-contracts/factories.py — 交易域数据契... | 原型态 / prototype |  |
| 19 | src/zephyr/trading/trading_contracts/market/instrument.py | instrument.py | 原型态 / prototype | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 20 | src/zephyr/trading/trading_contracts/market/signal_degrad... | signal_degradation_warning.py | 原型态 / prototype | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 21 | src/zephyr/trading/trading_contracts/risk/compliance_rule.py | compliance_rule.py | 原型态 / prototype | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 22 | src/zephyr/trading/trading_contracts/risk/risk_dashboard_... | risk_dashboard_snapshot.py | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 23 | src/zephyr/trading/trading_contracts/risk/risk_limit_viol... | risk_limit_violation_error.py | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 24 | src/zephyr/trading/trading_contracts/risk/risk_limits.py | risk_limits.py | 原型态 / prototype | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 25 | src/zephyr/trading/trading_contracts/risk/risk_metrics.py | risk_metrics.py | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 26 | src/zephyr/trading/trading_contracts/risk/risk_validator_... | risk_validator_protocol.py | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 27 | src/zephyr/trading/trading_contracts/risk/trading_kill_sw... | trading_kill_switch.py | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 28 | src/zephyr/trading/verdict_engine.py | verdict_engine.py | 生产态 / production | [MOD-INF-033](../../03_modules/_cross_layer/behavioral_auditor/blueprint.md) |

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

> 展示全部 32 个模块（生产态 21 + 设计态 0 + 原型态 11），标签标注成熟度。

#### 第 1 页 / 共 2 页

```mermaid
graph TD
    subgraph D_TRADING["D_TRADING 交易运营"]
        src_zephyr_trading_admission_controller_py["(生产态 / production) admission_controller.py"]
        src_zephyr_trading_auto_dispatcher_py["(原型态 / prototype) AutoDispatcher — 守护进程内的轻量 PipelineDisp...<br/>文件: auto_dispatcher.py"]
        src_zephyr_trading_autopilot_py["(生产态 / production) AutoPilot — AI session 自动找活干、认领任务。<br/>文件: autopilot.py"]
        src_zephyr_trading_conductor_py["(生产态 / production) Conductor — AI session 全自动指挥官。<br/>文件: conductor.py"]
        src_zephyr_trading_gpu_consensus_scheduler_py["(生产态 / production) gpu_consensus_scheduler.py"]
        src_zephyr_trading_gpu_monitor_py["(原型态 / prototype) gpu_monitor.py — NVIDIA GPU 状态采集器<br/>文件: gpu_monitor.py"]
        src_zephyr_trading_ide_health_daemon_py["(生产态 / production) ide_health_daemon.py — TRAE IDE 幽灵窗口守护线程<br/>文件: ide_health_daemon.py"]
        src_zephyr_trading_protection_index_py["(生产态 / production) protection_index.py"]
        src_zephyr_trading_runtime_async_runtime_py["(生产态 / production) async_runtime.py"]
        src_zephyr_trading_speed_baseline_checker_py["(原型态 / prototype) speed_baseline_checker.py"]
        src_zephyr_trading_trading_contracts_broker_interface_py["(生产态 / production) D_EXECUTION_CORE — BrokerInterface<br/>文件: broker_interface.py"]
        src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py["(生产态 / production) capital_allocation_result.py"]
        src_zephyr_trading_trading_contracts_execution_execution_rejection_error_py["(原型态 / prototype) execution_rejection_error.py"]
        src_zephyr_trading_trading_contracts_execution_execution_report_py["(生产态 / production) execution_report.py"]
        src_zephyr_trading_trading_contracts_execution_fill_py["(生产态 / production) fill.py"]
        src_zephyr_trading_trading_contracts_execution_model_serving_request_py["(生产态 / production) model_serving_request.py"]
        src_zephyr_trading_trading_contracts_execution_order_py["(生产态 / production) Re-export wrapper: Order 真源在 zephyr.shared.c...<br/>文件: order.py"]
        src_zephyr_trading_trading_contracts_execution_position_py["(生产态 / production) position.py"]
        src_zephyr_trading_trading_contracts_factories_py["(原型态 / prototype) trading-contracts/factories.py — 交易域数据契...<br/>文件: factories.py"]
        src_zephyr_trading_trading_contracts_market_instrument_py["(原型态 / prototype) instrument.py"]
        src_zephyr_trading_trading_contracts_market_signal_degradation_warning_py["(原型态 / prototype) signal_degradation_warning.py"]
        src_zephyr_trading_trading_contracts_portfolio_contracts_money_py["(生产态 / production) money.py"]
        src_zephyr_trading_trading_contracts_portfolio_contracts_performance_attribution_report_py["(原型态 / prototype) Re-export shim — 真源已收敛至 zephyr.shared.co...<br/>文件: performance_attribution_report.py"]
        src_zephyr_trading_trading_contracts_portfolio_contracts_strategy_lifecycle_event_py["(原型态 / prototype) strategy_lifecycle_event.py"]
        src_zephyr_trading_trading_contracts_risk_compliance_rule_py["(原型态 / prototype) compliance_rule.py"]
        src_zephyr_trading_trading_contracts_risk_risk_dashboard_snapshot_py["(生产态 / production) risk_dashboard_snapshot.py"]
        src_zephyr_trading_trading_contracts_risk_risk_limit_violation_error_py["(生产态 / production) risk_limit_violation_error.py"]
        src_zephyr_trading_trading_contracts_risk_risk_limits_py["(原型态 / prototype) risk_limits.py"]
        src_zephyr_trading_trading_contracts_risk_risk_metrics_py["(生产态 / production) risk_metrics.py"]
        src_zephyr_trading_trading_contracts_risk_risk_validator_protocol_py["(生产态 / production) risk_validator_protocol.py"]
    end
    src_zephyr_trading_conductor_py -->|导入依赖 / import_depends| src_zephyr_trading_autopilot_py
    src_zephyr_trading_trading_contracts_factories_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_order_py
    src_zephyr_trading_trading_contracts_factories_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_limits_py
    src_zephyr_trading_trading_contracts_factories_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_dashboard_snapshot_py
    src_zephyr_trading_trading_contracts_factories_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_metrics_py
    src_zephyr_trading_trading_contracts_portfolio_contracts_money_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_market_instrument_py
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_trading_auto_dispatcher_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_ide_health_daemon_py -->|导入依赖 / import_depends| D_SHARED
    D_INFRASTRUCTURE["(原型态 / prototype) D_INFRASTRUCTURE"]
    src_zephyr_trading_trading_contracts_risk_risk_limit_violation_error_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_trading_gpu_consensus_scheduler_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_ide_health_daemon_py -.->|导入依赖 / import_depends| D_SHARED
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    src_zephyr_trading_ide_health_daemon_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_trading_ide_health_daemon_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_trading_trading_contracts_portfolio_contracts_strategy_lifecycle_event_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_trading_speed_baseline_checker_py -.->|导入依赖 / import_depends| D_SHARED
    D_ORCHESTRATOR["(原型态 / prototype) D_ORCHESTRATOR"]
    src_zephyr_trading_auto_dispatcher_py -.->|导入依赖 / import_depends| D_ORCHESTRATOR
    src_zephyr_trading_auto_dispatcher_py -.->|导入依赖 / import_depends| D_ORCHESTRATOR
    src_zephyr_trading_autopilot_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_autopilot_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_trading_contracts_risk_risk_validator_protocol_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_trading_auto_dispatcher_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    D_ML_TRAIN["(原型态 / prototype) D_ML_TRAIN"]
    D_ML_TRAIN -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_model_serving_request_py
    D_FUNDAMENTAL_SIGNAL["(原型态 / prototype) D_FUNDAMENTAL_SIGNAL"]
    D_FUNDAMENTAL_SIGNAL -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py
    D_FUNDAMENTAL_SIGNAL -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py
    D_RISK["(生产态 / production) D_RISK"]
    D_RISK -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_limit_violation_error_py
    D_FUNDAMENTAL_SIGNAL -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py
    D_EX_CORE["(原型态 / prototype) D_EX_CORE"]
    D_EX_CORE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_position_py
    D_FUNDAMENTAL_SIGNAL -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_broker_interface_py
    D_INTEGRATION["(生产态 / production) D_INTEGRATION"]
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_trading_admission_controller_py
    D_RISK -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_dashboard_snapshot_py
    D_RISK -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_metrics_py
    D_EX_CORE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_broker_interface_py
    D_FUNDAMENTAL_SIGNAL -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_market_signal_degradation_warning_py
    D_SIGQC["(原型态 / prototype) D_SIGQC"]
    D_SIGQC -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_market_signal_degradation_warning_py
    D_EX_CORE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_broker_interface_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_admission_controller_py,src_zephyr_trading_autopilot_py,src_zephyr_trading_conductor_py,src_zephyr_trading_gpu_consensus_scheduler_py,src_zephyr_trading_ide_health_daemon_py,src_zephyr_trading_protection_index_py,src_zephyr_trading_runtime_async_runtime_py,src_zephyr_trading_trading_contracts_broker_interface_py,src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py,src_zephyr_trading_trading_contracts_execution_execution_report_py,src_zephyr_trading_trading_contracts_execution_fill_py,src_zephyr_trading_trading_contracts_execution_model_serving_request_py,src_zephyr_trading_trading_contracts_execution_order_py,src_zephyr_trading_trading_contracts_execution_position_py,src_zephyr_trading_trading_contracts_portfolio_contracts_money_py,src_zephyr_trading_trading_contracts_risk_risk_dashboard_snapshot_py,src_zephyr_trading_trading_contracts_risk_risk_limit_violation_error_py,src_zephyr_trading_trading_contracts_risk_risk_metrics_py,src_zephyr_trading_trading_contracts_risk_risk_validator_protocol_py production
    class src_zephyr_trading_auto_dispatcher_py,src_zephyr_trading_gpu_monitor_py,src_zephyr_trading_speed_baseline_checker_py,src_zephyr_trading_trading_contracts_execution_execution_rejection_error_py,src_zephyr_trading_trading_contracts_factories_py,src_zephyr_trading_trading_contracts_market_instrument_py,src_zephyr_trading_trading_contracts_market_signal_degradation_warning_py,src_zephyr_trading_trading_contracts_portfolio_contracts_performance_attribution_report_py,src_zephyr_trading_trading_contracts_portfolio_contracts_strategy_lifecycle_event_py,src_zephyr_trading_trading_contracts_risk_compliance_rule_py,src_zephyr_trading_trading_contracts_risk_risk_limits_py design
    class D_SHARED,D_INFRA_RUNTIME,D_GOVERNANCE,D_RISK,D_INTEGRATION external_prod
    class D_INFRASTRUCTURE,D_ORCHESTRATOR,D_ML_TRAIN,D_FUNDAMENTAL_SIGNAL,D_EX_CORE,D_SIGQC external_design
```

#### 第 2 页 / 共 2 页

```mermaid
graph TD
    subgraph D_TRADING["D_TRADING 交易运营"]
        src_zephyr_trading_trading_contracts_risk_trading_kill_switch_py["(生产态 / production) trading_kill_switch.py"]
        src_zephyr_trading_verdict_engine_py["(生产态 / production) verdict_engine.py"]
    end
    D_INTEGRATION["(生产态 / production) D_INTEGRATION"]
    src_zephyr_trading_verdict_engine_py -->|导入依赖 / import_depends| D_INTEGRATION
    D_GOV_AUDIT["(生产态 / production) D_GOV_AUDIT"]
    src_zephyr_trading_verdict_engine_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_trading_contracts_risk_trading_kill_switch_py,src_zephyr_trading_verdict_engine_py production
    class D_INTEGRATION,D_GOV_AUDIT external_prod
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 仅展示已上线运行的模块（共 21 个，4 条域内依赖）。

```mermaid
graph TD
    subgraph D_TRADING["D_TRADING 交易运营"]
        src_zephyr_trading_admission_controller_py["(生产态 / production) admission_controller.py"]
        src_zephyr_trading_autopilot_py["(生产态 / production) AutoPilot — AI session 自动找活干、认领任务。<br/>文件: autopilot.py"]
        src_zephyr_trading_conductor_py["(生产态 / production) Conductor — AI session 全自动指挥官。<br/>文件: conductor.py"]
        src_zephyr_trading_gpu_consensus_scheduler_py["(生产态 / production) gpu_consensus_scheduler.py"]
        src_zephyr_trading_ide_health_daemon_py["(生产态 / production) ide_health_daemon.py — TRAE IDE 幽灵窗口守护线程<br/>文件: ide_health_daemon.py"]
        src_zephyr_trading_protection_index_py["(生产态 / production) protection_index.py"]
        src_zephyr_trading_runtime_async_runtime_py["(生产态 / production) async_runtime.py"]
        src_zephyr_trading_trading_contracts_broker_interface_py["(生产态 / production) D_EXECUTION_CORE — BrokerInterface<br/>文件: broker_interface.py"]
        src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py["(生产态 / production) capital_allocation_result.py"]
        src_zephyr_trading_trading_contracts_execution_execution_report_py["(生产态 / production) execution_report.py"]
        src_zephyr_trading_trading_contracts_execution_fill_py["(生产态 / production) fill.py"]
        src_zephyr_trading_trading_contracts_execution_model_serving_request_py["(生产态 / production) model_serving_request.py"]
        src_zephyr_trading_trading_contracts_execution_order_py["(生产态 / production) Re-export wrapper: Order 真源在 zephyr.shared.c...<br/>文件: order.py"]
        src_zephyr_trading_trading_contracts_execution_position_py["(生产态 / production) position.py"]
        src_zephyr_trading_trading_contracts_portfolio_contracts_money_py["(生产态 / production) money.py"]
        src_zephyr_trading_trading_contracts_risk_risk_dashboard_snapshot_py["(生产态 / production) risk_dashboard_snapshot.py"]
        src_zephyr_trading_trading_contracts_risk_risk_limit_violation_error_py["(生产态 / production) risk_limit_violation_error.py"]
        src_zephyr_trading_trading_contracts_risk_risk_metrics_py["(生产态 / production) risk_metrics.py"]
        src_zephyr_trading_trading_contracts_risk_risk_validator_protocol_py["(生产态 / production) risk_validator_protocol.py"]
        src_zephyr_trading_trading_contracts_risk_trading_kill_switch_py["(生产态 / production) trading_kill_switch.py"]
        src_zephyr_trading_verdict_engine_py["(生产态 / production) verdict_engine.py"]
    end
    src_zephyr_trading_conductor_py -->|导入依赖 / import_depends| src_zephyr_trading_autopilot_py
    src_zephyr_trading_gpu_consensus_scheduler_py -->|导入依赖 / import_depends| src_zephyr_trading_verdict_engine_py
    src_zephyr_trading_protection_index_py -->|导入依赖 / import_depends| src_zephyr_trading_verdict_engine_py
    src_zephyr_trading_verdict_engine_py -->|导入依赖 / import_depends| src_zephyr_trading_protection_index_py
    D_INFRASTRUCTURE["(原型态 / prototype) D_INFRASTRUCTURE"]
    src_zephyr_trading_trading_contracts_broker_interface_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_trading_trading_contracts_broker_interface_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_trading_trading_contracts_broker_interface_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_trading_autopilot_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_autopilot_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_trading_autopilot_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_trading_autopilot_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_autopilot_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_conductor_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_conductor_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_conductor_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_trading_gpu_consensus_scheduler_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_ide_health_daemon_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_ide_health_daemon_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_ide_health_daemon_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_ML_TRAIN["(原型态 / prototype) D_ML_TRAIN"]
    D_ML_TRAIN -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_model_serving_request_py
    D_FUNDAMENTAL_SIGNAL["(原型态 / prototype) D_FUNDAMENTAL_SIGNAL"]
    D_FUNDAMENTAL_SIGNAL -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py
    D_FUNDAMENTAL_SIGNAL -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py
    D_RISK["(生产态 / production) D_RISK"]
    D_RISK -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_limit_violation_error_py
    D_FUNDAMENTAL_SIGNAL -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py
    D_EX_CORE["(原型态 / prototype) D_EX_CORE"]
    D_EX_CORE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_position_py
    D_FUNDAMENTAL_SIGNAL -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_broker_interface_py
    D_INTEGRATION["(生产态 / production) D_INTEGRATION"]
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_trading_admission_controller_py
    D_RISK -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_dashboard_snapshot_py
    D_RISK -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_metrics_py
    D_EX_CORE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_broker_interface_py
    D_EX_CORE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_broker_interface_py
    D_EX_CORE -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_broker_interface_py
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_trading_ide_health_daemon_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_admission_controller_py,src_zephyr_trading_autopilot_py,src_zephyr_trading_conductor_py,src_zephyr_trading_gpu_consensus_scheduler_py,src_zephyr_trading_ide_health_daemon_py,src_zephyr_trading_protection_index_py,src_zephyr_trading_runtime_async_runtime_py,src_zephyr_trading_trading_contracts_broker_interface_py,src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py,src_zephyr_trading_trading_contracts_execution_execution_report_py,src_zephyr_trading_trading_contracts_execution_fill_py,src_zephyr_trading_trading_contracts_execution_model_serving_request_py,src_zephyr_trading_trading_contracts_execution_order_py,src_zephyr_trading_trading_contracts_execution_position_py,src_zephyr_trading_trading_contracts_portfolio_contracts_money_py,src_zephyr_trading_trading_contracts_risk_risk_dashboard_snapshot_py,src_zephyr_trading_trading_contracts_risk_risk_limit_violation_error_py,src_zephyr_trading_trading_contracts_risk_risk_metrics_py,src_zephyr_trading_trading_contracts_risk_risk_validator_protocol_py,src_zephyr_trading_trading_contracts_risk_trading_kill_switch_py,src_zephyr_trading_verdict_engine_py production
    class D_SHARED,D_GOVERNANCE,D_RISK,D_INTEGRATION,D_INFRA_RUNTIME external_prod
    class D_INFRASTRUCTURE,D_ML_TRAIN,D_FUNDAMENTAL_SIGNAL,D_EX_CORE external_design
```

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个，0 条域内依赖）。

> （无设计态模块 / No design modules）

### 原型态子图（仅 design_maturity=prototype 的模块和依赖）

> 仅展示代码已写、验证中未稳定上线的原型态模块（共 11 个，1 条域内依赖）。

```mermaid
graph TD
    subgraph D_TRADING["D_TRADING 交易运营"]
        src_zephyr_trading_auto_dispatcher_py["(原型态 / prototype) AutoDispatcher — 守护进程内的轻量 PipelineDisp...<br/>文件: auto_dispatcher.py"]
        src_zephyr_trading_gpu_monitor_py["(原型态 / prototype) gpu_monitor.py — NVIDIA GPU 状态采集器<br/>文件: gpu_monitor.py"]
        src_zephyr_trading_speed_baseline_checker_py["(原型态 / prototype) speed_baseline_checker.py"]
        src_zephyr_trading_trading_contracts_execution_execution_rejection_error_py["(原型态 / prototype) execution_rejection_error.py"]
        src_zephyr_trading_trading_contracts_factories_py["(原型态 / prototype) trading-contracts/factories.py — 交易域数据契...<br/>文件: factories.py"]
        src_zephyr_trading_trading_contracts_market_instrument_py["(原型态 / prototype) instrument.py"]
        src_zephyr_trading_trading_contracts_market_signal_degradation_warning_py["(原型态 / prototype) signal_degradation_warning.py"]
        src_zephyr_trading_trading_contracts_portfolio_contracts_performance_attribution_report_py["(原型态 / prototype) Re-export shim — 真源已收敛至 zephyr.shared.co...<br/>文件: performance_attribution_report.py"]
        src_zephyr_trading_trading_contracts_portfolio_contracts_strategy_lifecycle_event_py["(原型态 / prototype) strategy_lifecycle_event.py"]
        src_zephyr_trading_trading_contracts_risk_compliance_rule_py["(原型态 / prototype) compliance_rule.py"]
        src_zephyr_trading_trading_contracts_risk_risk_limits_py["(原型态 / prototype) risk_limits.py"]
    end
    src_zephyr_trading_trading_contracts_factories_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_limits_py
    D_INFRASTRUCTURE["(生产态 / production) D_INFRASTRUCTURE"]
    src_zephyr_trading_trading_contracts_portfolio_contracts_performance_attribution_report_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_trading_trading_contracts_portfolio_contracts_strategy_lifecycle_event_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    D_ORCHESTRATOR["(原型态 / prototype) D_ORCHESTRATOR"]
    src_zephyr_trading_auto_dispatcher_py -.->|导入依赖 / import_depends| D_ORCHESTRATOR
    D_SHARED["(原型态 / prototype) D_SHARED"]
    src_zephyr_trading_auto_dispatcher_py -.->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_trading_auto_dispatcher_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_trading_auto_dispatcher_py -.->|导入依赖 / import_depends| D_ORCHESTRATOR
    src_zephyr_trading_auto_dispatcher_py -.->|导入依赖 / import_depends| D_ORCHESTRATOR
    src_zephyr_trading_auto_dispatcher_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_speed_baseline_checker_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_trading_contracts_factories_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_trading_trading_contracts_factories_py -.->|导入依赖 / import_depends| D_INFRASTRUCTURE
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    D_INFRA_RUNTIME -.->|导入依赖 / import_depends| src_zephyr_trading_gpu_monitor_py
    D_SIGQC["(原型态 / prototype) D_SIGQC"]
    D_SIGQC -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_market_signal_degradation_warning_py
    D_FUNDAMENTAL_SIGNAL["(原型态 / prototype) D_FUNDAMENTAL_SIGNAL"]
    D_FUNDAMENTAL_SIGNAL -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_market_signal_degradation_warning_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_auto_dispatcher_py,src_zephyr_trading_gpu_monitor_py,src_zephyr_trading_speed_baseline_checker_py,src_zephyr_trading_trading_contracts_execution_execution_rejection_error_py,src_zephyr_trading_trading_contracts_factories_py,src_zephyr_trading_trading_contracts_market_instrument_py,src_zephyr_trading_trading_contracts_market_signal_degradation_warning_py,src_zephyr_trading_trading_contracts_portfolio_contracts_performance_attribution_report_py,src_zephyr_trading_trading_contracts_portfolio_contracts_strategy_lifecycle_event_py,src_zephyr_trading_trading_contracts_risk_compliance_rule_py,src_zephyr_trading_trading_contracts_risk_risk_limits_py design
    class D_INFRASTRUCTURE,D_GOVERNANCE,D_INFRA_RUNTIME external_prod
    class D_ORCHESTRATOR,D_SHARED,D_SIGQC,D_FUNDAMENTAL_SIGNAL external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | AutoDispatcher — 守护进程内的轻量 PipelineDisp... | → | D_GOVERNANCE 生命周期管理: TaskRepository — 任务登记表 CRUD + 状态机（T-1... | 导入依赖 / import_depends |
| 2 | AutoPilot — AI session 自动找活干、认领任务。 ... | → | D_GOVERNANCE 生命周期管理: TaskRepository — 任务登记表 CRUD + 状态机（T-1... | 导入依赖 / import_depends |
| 3 | Conductor — AI session 全自动指挥官。 (conduct... | → | D_GOVERNANCE 生命周期管理: TaskRepository — 任务登记表 CRUD + 状态机（T-1... | 导入依赖 / import_depends |
| 4 | ide_health_daemon.py — TRAE IDE 幽灵窗口守护线... | → | D_GOVERNANCE 生命周期管理: TaskRepository — 任务登记表 CRUD + 状态机（T-1... | 导入依赖 / import_depends |
| 5 | verdict_engine.py | → | D_GOV_AUDIT 审计追踪: models.py | 导入依赖 / import_depends |
| 6 | D_EXECUTION_CORE — BrokerInterface (broker_int... | → | D_INFRASTRUCTURE: fill.py | 导入依赖 / import_depends |
| 7 | D_EXECUTION_CORE — BrokerInterface (broker_int... | → | D_INFRASTRUCTURE: order.py | 导入依赖 / import_depends |
| 8 | D_EXECUTION_CORE — BrokerInterface (broker_int... | → | D_INFRASTRUCTURE: position.py | 导入依赖 / import_depends |
| 9 | Re-export wrapper: Order 真源在 zephyr.shared.c... | → | D_INFRASTRUCTURE: order.py | 导入依赖 / import_depends |
| 10 | trading-contracts/factories.py — 交易域数据契.... | → | D_INFRASTRUCTURE: factor_signal.py | 导入依赖 / import_depends |
| 11 | trading-contracts/factories.py — 交易域数据契.... | → | D_INFRASTRUCTURE: synthesized_signal.py | 导入依赖 / import_depends |
| 12 | Re-export shim — 真源已收敛至 zephyr.shared.co... | → | D_INFRASTRUCTURE: performance_attribution_report.py | 导入依赖 / import_depends |
| 13 | strategy_lifecycle_event.py | → | D_INFRASTRUCTURE: strategy_lifecycle_event.py | 导入依赖 / import_depends |
| 14 | risk_limit_violation_error.py | → | D_INFRASTRUCTURE: trace_context.py | 导入依赖 / import_depends |
| 15 | risk_validator_protocol.py | → | D_INFRASTRUCTURE: risk_limits.py | 导入依赖 / import_depends |
| 16 | ide_health_daemon.py — TRAE IDE 幽灵窗口守护线... | → | D_INFRA_RUNTIME 运行时集成: daemon_registry.py - unified daemon thread regi... | 导入依赖 / import_depends |
| 17 | verdict_engine.py | → | D_INTEGRATION 管线路由: LocalModelScheduler — L2 本地模型 24/7 调度循... | 导入依赖 / import_depends |
| 18 | AutoDispatcher — 守护进程内的轻量 PipelineDisp... | → | D_ORCHESTRATOR 代理编排器: ActiveTaskQueue — 后台任务轮询与自动分发 (task... | 导入依赖 / import_depends |
| 19 | AutoDispatcher — 守护进程内的轻量 PipelineDisp... | → | D_ORCHESTRATOR 代理编排器: Orc->CE 上下文桥接 — request_context() 生产者 ... | 导入依赖 / import_depends |
| 20 | AutoDispatcher — 守护进程内的轻量 PipelineDisp... | → | D_ORCHESTRATOR 代理编排器: Orc->Script 脚本执行器 — run_audit() 生产者 (s... | 导入依赖 / import_depends |
| 21 | AutoDispatcher — 守护进程内的轻量 PipelineDisp... | → | D_SHARED 共享服务: TaskRepositoryProtocol — TaskRepository 的 Pro... | 导入依赖 / import_depends |
| 22 | AutoDispatcher — 守护进程内的轻量 PipelineDisp... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export... | 导入依赖 / import_depends |
| 23 | AutoPilot — AI session 自动找活干、认领任务。 ... | → | D_SHARED 共享服务: TaskRepositoryProtocol — TaskRepository 的 Pro... | 导入依赖 / import_depends |
| 24 | AutoPilot — AI session 自动找活干、认领任务。 ... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (event... | 导入依赖 / import_depends |
| 25 | AutoPilot — AI session 自动找活干、认领任务。 ... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export... | 导入依赖 / import_depends |
| 26 | AutoPilot — AI session 自动找活干、认领任务。 ... | → | D_SHARED 共享服务: ZephyrAlpha 任务系统核心数据模型 (models.py) | 导入依赖 / import_depends |
| 27 | Conductor — AI session 全自动指挥官。 (conduct... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export... | 导入依赖 / import_depends |
| 28 | Conductor — AI session 全自动指挥官。 (conduct... | → | D_SHARED 共享服务: ZephyrAlpha 任务系统核心数据模型 (models.py) | 导入依赖 / import_depends |
| 29 | gpu_consensus_scheduler.py | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export... | 导入依赖 / import_depends |
| 30 | ide_health_daemon.py — TRAE IDE 幽灵窗口守护线... | → | D_SHARED 共享服务: TaskRepositoryProtocol — TaskRepository 的 Pro... | 导入依赖 / import_depends |
| 31 | ide_health_daemon.py — TRAE IDE 幽灵窗口守护线... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (event... | 导入依赖 / import_depends |
| 32 | ide_health_daemon.py — TRAE IDE 幽灵窗口守护线... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export... | 导入依赖 / import_depends |
| 33 | ide_health_daemon.py — TRAE IDE 幽灵窗口守护线... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 34 | async_runtime.py | → | D_SHARED 共享服务: async_utils.py — async/sync 边界桥接（5.12.8 .... | 导入依赖 / import_depends |
| 35 | speed_baseline_checker.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 36 | Re-export wrapper: Order 真源在 zephyr.shared.c... | → | D_SHARED 共享服务: OrderSide/OrderStatus/OrderType — 交易枚举真源... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_EX_CORE 执行核心: D_EX_CORE adapters — 券商/风控适配器 re-export... | → | D_EXECUTION_CORE — BrokerInterface (broker_int... | 导入依赖 / import_depends |
| 2 | D_EX_CORE 执行核心: MiniQMT 实盘券商适配器（对接 xttrader，A股实盘.... | → | D_EXECUTION_CORE — BrokerInterface (broker_int... | 导入依赖 / import_depends |
| 3 | D_EX_CORE 执行核心: MiniQMT 实盘券商适配器（对接 xttrader，A股实盘.... | → | fill.py | 导入依赖 / import_depends |
| 4 | D_EX_CORE 执行核心: MiniQMT 实盘券商适配器（对接 xttrader，A股实盘.... | → | Re-export wrapper: Order 真源在 zephyr.shared.c... | 导入依赖 / import_depends |
| 5 | D_EX_CORE 执行核心: MiniQMT 实盘券商适配器（对接 xttrader，A股实盘.... | → | position.py | 导入依赖 / import_depends |
| 6 | D_EX_CORE 执行核心: D_EXECUTION_CORE — Order Manager (order_manage... | → | D_EXECUTION_CORE — BrokerInterface (broker_int... | 导入依赖 / import_depends |
| 7 | D_FRONTEND 前端: trade_panel · 实盘交易面板组件（v3.0.0 Panel+H... | → | Re-export wrapper: Order 真源在 zephyr.shared.c... | 导入依赖 / import_depends |
| 8 | D_FUNDAMENTAL_SIGNAL 基本面信号: D_FUNDAMENTAL_SIGNAL — CapitalAllocationResult... | → | capital_allocation_result.py | 导入依赖 / import_depends |
| 9 | D_FUNDAMENTAL_SIGNAL 基本面信号: D_SIGNAL — Signal Generation Layer (aggregator... | → | capital_allocation_result.py | 导入依赖 / import_depends |
| 10 | D_FUNDAMENTAL_SIGNAL 基本面信号: D_SIGNAL — Signal Generation Layer (aggregator... | → | signal_degradation_warning.py | 导入依赖 / import_depends |
| 11 | D_FUNDAMENTAL_SIGNAL 基本面信号: D_FUNDAMENTAL_SIGNAL — Capital Allocator（兼容... | → | capital_allocation_result.py | 导入依赖 / import_depends |
| 12 | D_FUNDAMENTAL_SIGNAL 基本面信号: D_SIGNAL — Default Capital Allocator (default_... | → | capital_allocation_result.py | 导入依赖 / import_depends |
| 13 | D_GOVERNANCE 生命周期管理: D_EXECUTION_CORE — Simulation Broker Adapter (... | → | D_EXECUTION_CORE — BrokerInterface (broker_int... | 导入依赖 / import_depends |
| 14 | D_INFRA_RUNTIME 运行时集成: boot_hooks.py | → | ide_health_daemon.py — TRAE IDE 幽灵窗口守护线... | 导入依赖 / import_depends |
| 15 | D_INFRA_RUNTIME 运行时集成: resource_optimization.py - MAPE-K autonomic res... | → | gpu_monitor.py — NVIDIA GPU 状态采集器 (gpu_mo... | 导入依赖 / import_depends |
| 16 | D_INFRA_RUNTIME 运行时集成: resource_optimization.py - MAPE-K autonomic res... | → | ide_health_daemon.py — TRAE IDE 幽灵窗口守护线... | 导入依赖 / import_depends |
| 17 | D_INTEGRATION 管线路由: admission_response.py | → | admission_controller.py | 导入依赖 / import_depends |
| 18 | D_INTELLIGENCE 上下文管理: D_ML_TRAIN — Default Inference Engine (default... | → | model_serving_request.py | 导入依赖 / import_depends |
| 19 | D_ML_TRAIN 训练: D_ML_TRAIN — Default Inference Engine (default... | → | model_serving_request.py | 导入依赖 / import_depends |
| 20 | D_ML_TRAIN 训练: D_ML_TRAIN — ML Inference Base (inference_base.py) | → | model_serving_request.py | 导入依赖 / import_depends |
| 21 | D_RISK 风控: ZephyrAlpha — D_RISK Risk Management Layer — ... | → | risk_dashboard_snapshot.py | 导入依赖 / import_depends |
| 22 | D_RISK 风控: ZephyrAlpha — D_RISK Risk Management Layer — ... | → | risk_limit_violation_error.py | 导入依赖 / import_depends |
| 23 | D_RISK 风控: ZephyrAlpha — D_RISK Risk Management Layer — ... | → | risk_metrics.py | 导入依赖 / import_depends |
| 24 | D_SIGQC 信号质量控制: D_SIGQC — Signal Quality Degradation Monitor B... | → | signal_degradation_warning.py | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 14 个外部域直接连接（出边 36 条 + 入边 24 条 = 60 条）。只显示直接连接的域，不展开具体节点。

```mermaid
graph LR
    D_TRADING["D_TRADING<br/>交易运营"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_ORCHESTRATOR["D_ORCHESTRATOR<br/>代理编排器"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_EX_CORE["D_EX_CORE<br/>执行核心"]
    D_FUNDAMENTAL_SIGNAL["D_FUNDAMENTAL_SIGNAL<br/>基本面信号"]
    D_RISK["D_RISK<br/>风控"]
    D_ML_TRAIN["D_ML_TRAIN<br/>训练"]
    D_SIGQC["D_SIGQC<br/>信号质量控制"]
    D_FRONTEND["D_FRONTEND<br/>前端"]
    D_INTELLIGENCE["D_INTELLIGENCE<br/>上下文管理"]
    D_TRADING -->|16条 导入依赖 / import_depends| D_SHARED
    D_TRADING -->|10条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_TRADING -->|4条 导入依赖 / import_depends| D_GOVERNANCE
    D_TRADING -->|3条 导入依赖 / import_depends| D_ORCHESTRATOR
    D_TRADING -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_TRADING -->|1条 导入依赖 / import_depends| D_GOV_AUDIT
    D_TRADING -->|1条 导入依赖 / import_depends| D_INTEGRATION
    D_EX_CORE -->|6条 导入依赖 / import_depends| D_TRADING
    D_FUNDAMENTAL_SIGNAL -->|5条 导入依赖 / import_depends| D_TRADING
    D_INFRA_RUNTIME -->|3条 导入依赖 / import_depends| D_TRADING
    D_RISK -->|3条 导入依赖 / import_depends| D_TRADING
    D_ML_TRAIN -->|2条 导入依赖 / import_depends| D_TRADING
    D_SIGQC -->|1条 导入依赖 / import_depends| D_TRADING
    D_FRONTEND -->|1条 导入依赖 / import_depends| D_TRADING
    D_GOVERNANCE -->|1条 导入依赖 / import_depends| D_TRADING
    D_INTEGRATION -->|1条 导入依赖 / import_depends| D_TRADING
    D_INTELLIGENCE -->|1条 导入依赖 / import_depends| D_TRADING
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
