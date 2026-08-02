---
doc_type: architecture_view
title: D_POSITION 仓位管理架构文档
version: "1.0"
status: active
date: 2026-08-02
owner: auto-generator
ttl: permanent
---

# 64_d_position / 仓位管理域 / Position Management

> **功能简介 / Overview**: 仓位管理，负责持仓跟踪、仓位计算和盈亏分析

> **文档作用 / Purpose**: 展示 仓位管理（D_POSITION）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/64_d_position.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 64 | Number | 64 |
| 域ID | D_POSITION | Domain ID | D_POSITION |
| 域名称 | 仓位管理 | Domain Name | Position Management |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 15 | Module Count | 15 |
| 域内依赖 | 19 | Internal Dependencies | 19 |
| 跨域入边 | 6 | Cross-domain Incoming | 6 |
| 跨域出边 | 15 | Cross-domain Outgoing | 15 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 15 | Production Modules | 15 |
| 容量 | 15/150 (正常) | Capacity | 15/150 (正常) |
| 描述 | 仓位管理，负责持仓跟踪、仓位计算和盈亏分析 | Description | 仓位管理，负责持仓跟踪、仓位计算和盈亏分析 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 15 个模块（生产态 15 + 设计态 0），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_position_core_position_limit_enforcer_py["core/position_limit_enforcer<br/>Position Limit Enforcer — 限仓执行器<br/>(MOD-POS-010)<br/>文件: core/position_limit_enforcer.py<br/>(生产态 / production)"]
    src_zephyr_position_core_sell_position_link_py["卖出持仓链接<br/>Sell-Position Bidirectional Link —<br/>卖出-仓位双向链接 (MOD-POS-016)<br/>sell_position_link<br/>文件: core/sell_position_link.py<br/>(生产态 / production)"]
    src_zephyr_position_position_reconciler_py["持仓协调器<br/>Position Reconciler — v0.10.1 持仓对账:<br/>execution report+book<br/>record+counterparty三方对账。<br/>position_reconciler<br/>文件: position/position_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_position_services_init_py["position/services 包入口<br/>管理position.services子包的加载和懒导入<br/>文件: services/__init__.py<br/>(生产态 / production)"]
    tests_position_test_position_audit_logger_py["position/test_position_audit_logger<br/>Position Audit Logger 测试 — MOD-POS-009<br/>文件: position/test_position_audit_logger.py<br/>(生产态 / production)"]
    tests_position_test_position_sizing_engine_py["position/test_position_sizing_engine<br/>Position Sizing Engine 测试 (MOD-POS-001<br/>阶段1)。<br/>文件: position/test_position_sizing_engine.py<br/>(生产态 / production)"]
    src_zephyr_position_core_position_limit_enforcer_py ~~~ src_zephyr_position_core_sell_position_link_py
    src_zephyr_position_core_sell_position_link_py ~~~ src_zephyr_position_position_reconciler_py
    src_zephyr_position_position_reconciler_py ~~~ src_zephyr_position_services_init_py
    src_zephyr_position_services_init_py ~~~ tests_position_test_position_audit_logger_py
    tests_position_test_position_audit_logger_py ~~~ tests_position_test_position_sizing_engine_py
    src_zephyr_position_services_position_audit_logger_py["持仓审计日志器<br/>持仓的日志器，记录运行日志<br/>position_audit_logger<br/>文件: services/position_audit_logger.py<br/>(生产态 / production)"]
    src_zephyr_position_core_rebalance_engine_py["rebalance引擎<br/>持仓的引擎，执行核心逻辑的处理引擎（rebalance）<br/>rebalance_engine<br/>文件: core/rebalance_engine.py<br/>(生产态 / production)"]
    src_zephyr_position_core_position_drift_monitor_py["持仓漂移监控<br/>持仓的监控器，持续监视某项指标，异常时上报<br/>position_drift_monitor<br/>文件: core/position_drift_monitor.py<br/>(生产态 / production)"]
    src_zephyr_position_core_position_state_machine_py["持仓状态machine<br/>持仓的状态机，管理状态流转<br/>position_state_machine<br/>文件: core/position_state_machine.py<br/>(生产态 / production)"]
    src_zephyr_position_core_position_sizing_engine_py["持仓sizing引擎<br/>持仓的引擎，执行核心逻辑的处理引擎（position<br/>sizing）<br/>position_sizing_engine<br/>文件: core/position_sizing_engine.py<br/>(生产态 / production)"]
    src_zephyr_position_core_calendar_position_constraint_py["日历持仓约束<br/>calendar持仓constraint，持仓的常量，定义模块级常<br/>量。<br/>calendar_position_constraint<br/>文件: core/calendar_position_constraint.py<br/>(生产态 / production)"]
    src_zephyr_position_core_capital_curve_manager_py["资本curve管理器<br/>持仓的管理器，统一管理一类资源的生命周期<br/>（capital curve）<br/>capital_curve_manager<br/>文件: core/capital_curve_manager.py<br/>(生产态 / production)"]
    src_zephyr_position_core_cash_manager_py["core/cash_manager<br/>Cash Manager — 资金管理器 (MOD-POS-006)<br/>文件: core/cash_manager.py<br/>(生产态 / production)"]
    src_zephyr_position_core_calendar_position_constraint_py ~~~ src_zephyr_position_core_capital_curve_manager_py
    src_zephyr_position_core_capital_curve_manager_py ~~~ src_zephyr_position_core_cash_manager_py
    src_zephyr_position_core_drawdown_controller_py["回撤控制器<br/>持仓的控制器，协调各组件按流程执行<br/>drawdown_controller<br/>文件: core/drawdown_controller.py<br/>(生产态 / production)"]
    src_zephyr_position_core_capital_curve_manager_py -->|runtime / runtime| src_zephyr_position_core_drawdown_controller_py
    src_zephyr_position_core_position_drift_monitor_py -->|runtime / runtime| src_zephyr_position_core_position_state_machine_py
    src_zephyr_position_core_position_sizing_engine_py -->|runtime / runtime| src_zephyr_position_core_capital_curve_manager_py
    src_zephyr_position_core_position_sizing_engine_py -->|runtime / runtime| src_zephyr_position_core_calendar_position_constraint_py
    src_zephyr_position_core_position_sizing_engine_py -->|runtime / runtime| src_zephyr_position_core_cash_manager_py
    src_zephyr_position_core_position_state_machine_py -->|runtime / runtime| src_zephyr_position_core_position_sizing_engine_py
    src_zephyr_position_core_rebalance_engine_py -->|event / event| src_zephyr_position_core_position_drift_monitor_py
    src_zephyr_position_core_rebalance_engine_py -->|导入依赖 / import_depends| src_zephyr_position_core_position_drift_monitor_py
    src_zephyr_position_services_init_py -->|导入依赖 / import_depends| src_zephyr_position_services_position_audit_logger_py
    src_zephyr_position_services_position_audit_logger_py -->|导入依赖 / import_depends| src_zephyr_position_core_position_drift_monitor_py
    src_zephyr_position_services_position_audit_logger_py -->|导入依赖 / import_depends| src_zephyr_position_core_position_sizing_engine_py
    src_zephyr_position_services_position_audit_logger_py -->|导入依赖 / import_depends| src_zephyr_position_core_position_state_machine_py
    src_zephyr_position_services_position_audit_logger_py -->|导入依赖 / import_depends| src_zephyr_position_core_rebalance_engine_py
    tests_position_test_position_audit_logger_py -->|测试依赖 / test_depends| src_zephyr_position_core_position_drift_monitor_py
    tests_position_test_position_audit_logger_py -->|测试依赖 / test_depends| src_zephyr_position_core_position_sizing_engine_py
    tests_position_test_position_audit_logger_py -->|测试依赖 / test_depends| src_zephyr_position_core_position_state_machine_py
    tests_position_test_position_audit_logger_py -->|测试依赖 / test_depends| src_zephyr_position_core_rebalance_engine_py
    tests_position_test_position_audit_logger_py -->|测试依赖 / test_depends| src_zephyr_position_services_position_audit_logger_py
    tests_position_test_position_sizing_engine_py -->|测试依赖 / test_depends| src_zephyr_position_core_position_sizing_engine_py
    D_RISK["风控<br/>风控，负责风险指标计算、风险限额管理和风险预警<br/>Risk Control<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_position_core_position_sizing_engine_py -->|runtime / runtime| D_RISK
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_position_services_position_audit_logger_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_position_core_position_state_machine_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_position_core_calendar_position_constraint_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_position_core_capital_curve_manager_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_position_core_position_state_machine_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_position_core_position_drift_monitor_py -->|导入依赖 / import_depends| D_SHARED
    D_INFRASTRUCTURE["跨层契约基础设施<br/>跨层契约基础设施，负责跨层契约定义、共享契约管理<br/>和契约校验<br/>Cross-Layer Contract Infrastructure<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    tests_position_test_position_sizing_engine_py -->|测试依赖 / test_depends| D_INFRASTRUCTURE
    src_zephyr_position_core_position_sizing_engine_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_position_core_cash_manager_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_position_core_position_sizing_engine_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_position_core_drawdown_controller_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_position_core_sell_position_link_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_position_core_rebalance_engine_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_position_core_position_limit_enforcer_py -->|导入依赖 / import_depends| D_SHARED
    D_RISK -->|runtime / runtime| src_zephyr_position_core_drawdown_controller_py
    D_TRADING["交易运营<br/>交易运营，负责交易生命周期管理、订单状态和成交处<br/>理<br/>Trading Operations<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_position_position_reconciler_py
    D_PF_CORE["组合核心<br/>组合核心，负责投资组合构建、持仓管理和组合优化<br/>Portfolio Core<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_PF_CORE -->|导入依赖 / import_depends| src_zephyr_position_position_reconciler_py
    D_SELL_DECISION["卖出决策<br/>卖出决策，负责卖出信号生成、卖出时机判断和退出策<br/>略<br/>Sell Decision<br/>跨域节点 / cross-domain<br/>(设计态 / design)"]
    D_SELL_DECISION -.->|runtime / runtime| src_zephyr_position_core_sell_position_link_py
    D_PF_CORE -->|导入依赖 / import_depends| src_zephyr_position_core_position_drift_monitor_py
    D_PF_CORE -->|导入依赖 / import_depends| src_zephyr_position_core_rebalance_engine_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_position_core_calendar_position_constraint_py,src_zephyr_position_core_capital_curve_manager_py,src_zephyr_position_core_cash_manager_py,src_zephyr_position_core_drawdown_controller_py,src_zephyr_position_core_position_drift_monitor_py,src_zephyr_position_core_position_limit_enforcer_py,src_zephyr_position_core_position_sizing_engine_py,src_zephyr_position_core_position_state_machine_py,src_zephyr_position_core_rebalance_engine_py,src_zephyr_position_core_sell_position_link_py,src_zephyr_position_position_reconciler_py,src_zephyr_position_services_init_py,src_zephyr_position_services_position_audit_logger_py,tests_position_test_position_audit_logger_py,tests_position_test_position_sizing_engine_py production
    class D_RISK,D_SHARED,D_INFRASTRUCTURE,D_TRADING,D_PF_CORE external_prod
    class D_SELL_DECISION external_design
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 15 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_position_core_position_limit_enforcer_py["core/position_limit_enforcer<br/>Position Limit Enforcer — 限仓执行器<br/>(MOD-POS-010)<br/>文件: core/position_limit_enforcer.py<br/>(生产态 / production)"]
    src_zephyr_position_core_sell_position_link_py["卖出持仓链接<br/>Sell-Position Bidirectional Link —<br/>卖出-仓位双向链接 (MOD-POS-016)<br/>sell_position_link<br/>文件: core/sell_position_link.py<br/>(生产态 / production)"]
    src_zephyr_position_position_reconciler_py["持仓协调器<br/>Position Reconciler — v0.10.1 持仓对账:<br/>execution report+book<br/>record+counterparty三方对账。<br/>position_reconciler<br/>文件: position/position_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_position_services_init_py["position/services 包入口<br/>管理position.services子包的加载和懒导入<br/>文件: services/__init__.py<br/>(生产态 / production)"]
    tests_position_test_position_audit_logger_py["position/test_position_audit_logger<br/>Position Audit Logger 测试 — MOD-POS-009<br/>文件: position/test_position_audit_logger.py<br/>(生产态 / production)"]
    tests_position_test_position_sizing_engine_py["position/test_position_sizing_engine<br/>Position Sizing Engine 测试 (MOD-POS-001<br/>阶段1)。<br/>文件: position/test_position_sizing_engine.py<br/>(生产态 / production)"]
    src_zephyr_position_core_position_limit_enforcer_py ~~~ src_zephyr_position_core_sell_position_link_py
    src_zephyr_position_core_sell_position_link_py ~~~ src_zephyr_position_position_reconciler_py
    src_zephyr_position_position_reconciler_py ~~~ src_zephyr_position_services_init_py
    src_zephyr_position_services_init_py ~~~ tests_position_test_position_audit_logger_py
    tests_position_test_position_audit_logger_py ~~~ tests_position_test_position_sizing_engine_py
    src_zephyr_position_services_position_audit_logger_py["持仓审计日志器<br/>持仓的日志器，记录运行日志<br/>position_audit_logger<br/>文件: services/position_audit_logger.py<br/>(生产态 / production)"]
    src_zephyr_position_core_rebalance_engine_py["rebalance引擎<br/>持仓的引擎，执行核心逻辑的处理引擎（rebalance）<br/>rebalance_engine<br/>文件: core/rebalance_engine.py<br/>(生产态 / production)"]
    src_zephyr_position_core_position_drift_monitor_py["持仓漂移监控<br/>持仓的监控器，持续监视某项指标，异常时上报<br/>position_drift_monitor<br/>文件: core/position_drift_monitor.py<br/>(生产态 / production)"]
    src_zephyr_position_core_position_state_machine_py["持仓状态machine<br/>持仓的状态机，管理状态流转<br/>position_state_machine<br/>文件: core/position_state_machine.py<br/>(生产态 / production)"]
    src_zephyr_position_core_position_sizing_engine_py["持仓sizing引擎<br/>持仓的引擎，执行核心逻辑的处理引擎（position<br/>sizing）<br/>position_sizing_engine<br/>文件: core/position_sizing_engine.py<br/>(生产态 / production)"]
    src_zephyr_position_core_calendar_position_constraint_py["日历持仓约束<br/>calendar持仓constraint，持仓的常量，定义模块级常<br/>量。<br/>calendar_position_constraint<br/>文件: core/calendar_position_constraint.py<br/>(生产态 / production)"]
    src_zephyr_position_core_capital_curve_manager_py["资本curve管理器<br/>持仓的管理器，统一管理一类资源的生命周期<br/>（capital curve）<br/>capital_curve_manager<br/>文件: core/capital_curve_manager.py<br/>(生产态 / production)"]
    src_zephyr_position_core_cash_manager_py["core/cash_manager<br/>Cash Manager — 资金管理器 (MOD-POS-006)<br/>文件: core/cash_manager.py<br/>(生产态 / production)"]
    src_zephyr_position_core_calendar_position_constraint_py ~~~ src_zephyr_position_core_capital_curve_manager_py
    src_zephyr_position_core_capital_curve_manager_py ~~~ src_zephyr_position_core_cash_manager_py
    src_zephyr_position_core_drawdown_controller_py["回撤控制器<br/>持仓的控制器，协调各组件按流程执行<br/>drawdown_controller<br/>文件: core/drawdown_controller.py<br/>(生产态 / production)"]
    src_zephyr_position_core_capital_curve_manager_py -->|runtime / runtime| src_zephyr_position_core_drawdown_controller_py
    src_zephyr_position_core_position_drift_monitor_py -->|runtime / runtime| src_zephyr_position_core_position_state_machine_py
    src_zephyr_position_core_position_sizing_engine_py -->|runtime / runtime| src_zephyr_position_core_capital_curve_manager_py
    src_zephyr_position_core_position_sizing_engine_py -->|runtime / runtime| src_zephyr_position_core_calendar_position_constraint_py
    src_zephyr_position_core_position_sizing_engine_py -->|runtime / runtime| src_zephyr_position_core_cash_manager_py
    src_zephyr_position_core_position_state_machine_py -->|runtime / runtime| src_zephyr_position_core_position_sizing_engine_py
    src_zephyr_position_core_rebalance_engine_py -->|event / event| src_zephyr_position_core_position_drift_monitor_py
    src_zephyr_position_core_rebalance_engine_py -->|导入依赖 / import_depends| src_zephyr_position_core_position_drift_monitor_py
    src_zephyr_position_services_init_py -->|导入依赖 / import_depends| src_zephyr_position_services_position_audit_logger_py
    src_zephyr_position_services_position_audit_logger_py -->|导入依赖 / import_depends| src_zephyr_position_core_position_drift_monitor_py
    src_zephyr_position_services_position_audit_logger_py -->|导入依赖 / import_depends| src_zephyr_position_core_position_sizing_engine_py
    src_zephyr_position_services_position_audit_logger_py -->|导入依赖 / import_depends| src_zephyr_position_core_position_state_machine_py
    src_zephyr_position_services_position_audit_logger_py -->|导入依赖 / import_depends| src_zephyr_position_core_rebalance_engine_py
    tests_position_test_position_audit_logger_py -->|测试依赖 / test_depends| src_zephyr_position_core_position_drift_monitor_py
    tests_position_test_position_audit_logger_py -->|测试依赖 / test_depends| src_zephyr_position_core_position_sizing_engine_py
    tests_position_test_position_audit_logger_py -->|测试依赖 / test_depends| src_zephyr_position_core_position_state_machine_py
    tests_position_test_position_audit_logger_py -->|测试依赖 / test_depends| src_zephyr_position_core_rebalance_engine_py
    tests_position_test_position_audit_logger_py -->|测试依赖 / test_depends| src_zephyr_position_services_position_audit_logger_py
    tests_position_test_position_sizing_engine_py -->|测试依赖 / test_depends| src_zephyr_position_core_position_sizing_engine_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_position_core_calendar_position_constraint_py,src_zephyr_position_core_capital_curve_manager_py,src_zephyr_position_core_cash_manager_py,src_zephyr_position_core_drawdown_controller_py,src_zephyr_position_core_position_drift_monitor_py,src_zephyr_position_core_position_limit_enforcer_py,src_zephyr_position_core_position_sizing_engine_py,src_zephyr_position_core_position_state_machine_py,src_zephyr_position_core_rebalance_engine_py,src_zephyr_position_core_sell_position_link_py,src_zephyr_position_position_reconciler_py,src_zephyr_position_services_init_py,src_zephyr_position_services_position_audit_logger_py,tests_position_test_position_audit_logger_py,tests_position_test_position_sizing_engine_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个），不含跨域外部节点。

> （无模块 / No modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 持仓sizing引擎 / position_sizing_engine (core/position_si... | → | D_INFRASTRUCTURE 跨层契约基础设施: 风险limits / risk_limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 2 | Position Sizing Engine 测试 (MOD-POS-001 阶段1)。 (positi... | → | D_INFRASTRUCTURE 跨层契约基础设施: 风险limits / risk_limits (contracts/risk_limits.py) | 测试依赖 / test_depends |
| 3 | 持仓sizing引擎 / position_sizing_engine (core/position_si... | → | D_RISK 风控: 风险limits / D_RISK — Risk Limits Calculator (risk/risk_... | runtime / runtime |
| 4 | 日历持仓约束 / calendar_position_constraint (core/calenda... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 5 | 资本curve管理器 / capital_curve_manager (core/capital_cur... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 6 | Cash Manager — 资金管理器 (MOD-POS-006) (core/cash_manag... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 7 | 回撤控制器 / drawdown_controller (core/drawdown_controlle... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 8 | 持仓漂移监控 / position_drift_monitor (core/position_drif... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 9 | Position Limit Enforcer — 限仓执行器 (MOD-POS-010) (core... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 10 | 持仓sizing引擎 / position_sizing_engine (core/position_si... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 11 | 持仓状态machine / position_state_machine (core/position_s... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 12 | 持仓状态machine / position_state_machine (core/position_s... | → | D_SHARED 共享服务: 状态machine / state_machine (lifecycle/state_machine.py) | 导入依赖 / import_depends |
| 13 | rebalance引擎 / rebalance_engine (core/rebalance_engine.py) | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 14 | 卖出持仓链接 / sell_position_link (core/sell_position_lin... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 15 | 持仓审计日志器 / position_audit_logger (services/position... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_PF_CORE 组合核心: Rebalance Scheduler — 再平衡调度器 (MOD-PF-003) (core/re... | → | 持仓漂移监控 / position_drift_monitor (core/position_drif... | 导入依赖 / import_depends |
| 2 | D_PF_CORE 组合核心: Rebalance Scheduler — 再平衡调度器 (MOD-PF-003) (core/re... | → | rebalance引擎 / rebalance_engine (core/rebalance_engine.py) | 导入依赖 / import_depends |
| 3 | D_PF_CORE 组合核心: Rebalance Scheduler — 再平衡调度器 (MOD-PF-003) (core/re... | → | 持仓协调器 / position_reconciler (position/position_recon... | 导入依赖 / import_depends |
| 4 | D_RISK 风控: 风险limits / D_RISK — Risk Limits Calculator (risk/risk_... | → | 回撤控制器 / drawdown_controller (core/drawdown_controlle... | runtime / runtime |
| 5 | D_SELL_DECISION 卖出决策: 卖信号融合引擎 / sell_signal_fusion_engine (core/sell_sig... | → | 卖出持仓链接 / sell_position_link (core/sell_position_lin... | runtime / runtime |
| 6 | D_TRADING 交易运营: D_TRADING — PnL Calculator (盈亏计算器) (trading/pnl_cal... | → | 持仓协调器 / position_reconciler (position/position_recon... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 6 个外部域直接连接（出边 15 条 + 入边 6 条 = 21 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_POSITION["D_POSITION<br/>仓位管理"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE<br/>跨层契约基础设施"]
    D_RISK["D_RISK<br/>风控"]
    D_PF_CORE["D_PF_CORE<br/>组合核心"]
    D_SELL_DECISION["D_SELL_DECISION<br/>卖出决策"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_POSITION -->|12条 导入依赖 / import_depends| D_SHARED
    D_POSITION -->|2条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INFRASTRUCTURE
    D_POSITION -->|1条 runtime / runtime| D_RISK
    D_PF_CORE -->|3条 导入依赖 / import_depends| D_POSITION
    D_RISK -->|1条 runtime / runtime| D_POSITION
    D_SELL_DECISION -->|1条 runtime / runtime| D_POSITION
    D_TRADING -->|1条 导入依赖 / import_depends| D_POSITION
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
