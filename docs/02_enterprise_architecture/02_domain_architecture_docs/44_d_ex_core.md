---
doc_type: architecture_view
title: D_EX_CORE 执行核心架构文档
version: "1.0"
status: active
date: 2026-08-02
owner: auto-generator
ttl: permanent
---

# 44_d_ex_core / 执行核心域 / Execution Core

> **功能简介 / Overview**: 执行核心，负责订单执行引擎、执行策略和执行管理

> **文档作用 / Purpose**: 展示 执行核心（D_EX_CORE）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/44_d_ex_core.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 44 | Number | 44 |
| 域ID | D_EX_CORE | Domain ID | D_EX_CORE |
| 域名称 | 执行核心 | Domain Name | Execution Core |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 25 | Module Count | 25 |
| 域内依赖 | 22 | Internal Dependencies | 22 |
| 跨域入边 | 8 | Cross-domain Incoming | 8 |
| 跨域出边 | 43 | Cross-domain Outgoing | 43 |
| 设计态模块 | 16 | Design Modules | 16 |
| 生产态模块 | 9 | Production Modules | 9 |
| 容量 | 9/150 (正常) | Capacity | 9/150 (正常) |
| 描述 | 执行核心，负责订单执行引擎、执行策略和执行管理 | Description | 执行核心，负责订单执行引擎、执行策略和执行管理 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 25 个模块（生产态 9 + 设计态 16），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_ex_core_adapters_init_py["ex_core/adapters 包入口<br/>D_EX_CORE adapters — 券商/风控适配器 re-export<br/>wrapper<br/>文件: adapters/__init__.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_adapters_risk_validation_bridge_py["adapters/risk_validation_bridge<br/>Re-export wrapper: risk_validation_bridge<br/>真源在 zephyr.governance.adapters.r...<br/>文件: adapters/risk_validation_bridge.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_auction_deviation_executor_py["ex_core/auction_deviation_executor<br/>ex core包的auction_deviation_executor模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/auction_deviation_executor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_batch_executor_py["ex_core/batch_executor<br/>ex core包的batch_executor模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/batch_executor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_batch_take_profit_executor_py["ex_core/batch_take_profit_executor<br/>ex core包的batch_take_profit_executor模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/batch_take_profit_executor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_conditional_order_manager_py["ex_core/conditional_order_manager<br/>ex core包的conditional_order_manager模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/conditional_order_manager.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_execution_engine_py["ex_core/execution_engine<br/>D_EXECUTION_CORE — Execution Engine<br/>文件: ex_core/execution_engine.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_execution_mcp_server_py["ex_core/execution_mcp_server<br/>ex core包的execution_mcp_server模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/execution_mcp_server.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_fill_handler_py["ex_core/fill_handler<br/>ex core包的fill_handler模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/fill_handler.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_fill_processor_py["ex_core/fill_processor<br/>ex core包的fill_processor模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/fill_processor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_live_simulation_switcher_py["ex_core/live_simulation_switcher<br/>ex core包的live_simulation_switcher模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/live_simulation_switcher.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_order_splitter_py["ex_core/order_splitter<br/>ex core包的order_splitter模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/order_splitter.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_redis_idempotency["ex_core/redis_idempotency<br/>ex core包的redis_idempotency模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: redis_idempotency/<br/>(设计态 / design)"]
    src_zephyr_ex_core_sell_priority_scheduler_py["ex_core/sell_priority_scheduler<br/>ex core包的sell_priority_scheduler模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/sell_priority_scheduler.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_services_live_portfolio_py["services/live_portfolio<br/>服务包的live_portfolio模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: services/live_portfolio.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_signal_providers_py["ex_core/signal_providers<br/>D_EXECUTION_CORE — 信号源 / 价格源 callable 工厂<br/>文件: ex_core/signal_providers.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_stop_loss_take_profit_executor_py["ex_core/stop_loss_take_profit_executor<br/>ex core包的stop_loss_take_profit_executor模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/stop_loss_take_profit_executor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_trading_session_py["ex_core/trading_session<br/>D_EXECUTION_CORE — TradingSession<br/>盘中实时调仓编排器<br/>文件: ex_core/trading_session.py<br/>(生产态 / production)"]
    src_zephyr_governance_escalation_order_state_escalator_py["escalation/order_state_escalator<br/>Order State Escalator — v0.10.0<br/>订单状态机升级器。<br/>文件: escalation/order_state_escalator.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_adapters_init_py ~~~ src_zephyr_ex_core_adapters_risk_validation_bridge_py
    src_zephyr_ex_core_adapters_risk_validation_bridge_py ~~~ src_zephyr_ex_core_auction_deviation_executor_py
    src_zephyr_ex_core_auction_deviation_executor_py ~~~ src_zephyr_ex_core_batch_executor_py
    src_zephyr_ex_core_batch_executor_py ~~~ src_zephyr_ex_core_batch_take_profit_executor_py
    src_zephyr_ex_core_batch_take_profit_executor_py ~~~ src_zephyr_ex_core_conditional_order_manager_py
    src_zephyr_ex_core_conditional_order_manager_py ~~~ src_zephyr_ex_core_execution_engine_py
    src_zephyr_ex_core_execution_engine_py ~~~ src_zephyr_ex_core_execution_mcp_server_py
    src_zephyr_ex_core_execution_mcp_server_py ~~~ src_zephyr_ex_core_fill_handler_py
    src_zephyr_ex_core_fill_handler_py ~~~ src_zephyr_ex_core_fill_processor_py
    src_zephyr_ex_core_fill_processor_py ~~~ src_zephyr_ex_core_live_simulation_switcher_py
    src_zephyr_ex_core_live_simulation_switcher_py ~~~ src_zephyr_ex_core_order_splitter_py
    src_zephyr_ex_core_order_splitter_py ~~~ src_zephyr_ex_core_redis_idempotency
    src_zephyr_ex_core_redis_idempotency ~~~ src_zephyr_ex_core_sell_priority_scheduler_py
    src_zephyr_ex_core_sell_priority_scheduler_py ~~~ src_zephyr_ex_core_services_live_portfolio_py
    src_zephyr_ex_core_services_live_portfolio_py ~~~ src_zephyr_ex_core_signal_providers_py
    src_zephyr_ex_core_signal_providers_py ~~~ src_zephyr_ex_core_stop_loss_take_profit_executor_py
    src_zephyr_ex_core_stop_loss_take_profit_executor_py ~~~ src_zephyr_ex_core_trading_session_py
    src_zephyr_ex_core_trading_session_py ~~~ src_zephyr_governance_escalation_order_state_escalator_py
    src_zephyr_ex_core_adapters_miniqmt_broker_py["adapters/miniqmt_broker<br/>MiniQMT 实盘券商适配器（对接<br/>xttrader，A股实盘交易）<br/>文件: adapters/miniqmt_broker.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_adapters_simulation_broker_py["adapters/simulation_broker<br/>Re-export wrapper: simulation_broker 真源在<br/>zephyr.governance.adapters.simula...<br/>文件: adapters/simulation_broker.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_execution_report_py["ex_core/execution_report<br/>ex core包的execution_report模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/execution_report.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_order_manager_py["ex_core/order_manager<br/>D_EXECUTION_CORE — Order Manager<br/>文件: ex_core/order_manager.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_position_tracker["ex_core/position_tracker<br/>ex core包的position_tracker模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: position_tracker/<br/>(设计态 / design)"]
    src_zephyr_ex_core_adapters_miniqmt_broker_py ~~~ src_zephyr_ex_core_adapters_simulation_broker_py
    src_zephyr_ex_core_adapters_simulation_broker_py ~~~ src_zephyr_ex_core_execution_report_py
    src_zephyr_ex_core_execution_report_py ~~~ src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_order_manager_py ~~~ src_zephyr_ex_core_position_tracker
    src_zephyr_ex_core_audit_journal["ex_core/audit_journal<br/>ex core包的audit_journal模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: audit_journal/<br/>(设计态 / design)"]
    src_zephyr_ex_core_fill_handler_py -.->|runtime / runtime| src_zephyr_ex_core_position_tracker
    src_zephyr_ex_core_fill_handler_py -.->|event / event| src_zephyr_ex_core_audit_journal
    src_zephyr_ex_core_fill_handler_py -.->|导入依赖 / import_depends| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_position_tracker -.->|event / event| src_zephyr_ex_core_audit_journal
    src_zephyr_ex_core_redis_idempotency -.->|event / event| src_zephyr_ex_core_audit_journal
    src_zephyr_ex_core_services_live_portfolio_py -.->|导入依赖 / import_depends| src_zephyr_ex_core_adapters_miniqmt_broker_py
    src_zephyr_ex_core_fill_processor_py -.->|runtime / runtime| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_order_splitter_py -.->|runtime / runtime| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_stop_loss_take_profit_executor_py -.->|runtime / runtime| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_batch_executor_py -.->|runtime / runtime| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_batch_take_profit_executor_py -.->|runtime / runtime| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_auction_deviation_executor_py -.->|runtime / runtime| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_sell_priority_scheduler_py -.->|runtime / runtime| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_live_simulation_switcher_py -.->|runtime / runtime| src_zephyr_ex_core_adapters_simulation_broker_py
    src_zephyr_ex_core_live_simulation_switcher_py -.->|runtime / runtime| src_zephyr_ex_core_adapters_miniqmt_broker_py
    src_zephyr_ex_core_conditional_order_manager_py -.->|runtime / runtime| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_execution_mcp_server_py -.->|runtime / runtime| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_execution_engine_py -.->|runtime / runtime| src_zephyr_ex_core_execution_report_py
    src_zephyr_ex_core_execution_engine_py -->|导入依赖 / import_depends| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_adapters_init_py -->|导入依赖 / import_depends| src_zephyr_ex_core_adapters_miniqmt_broker_py
    src_zephyr_ex_core_trading_session_py -->|导入依赖 / import_depends| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_trading_session_py -->|导入依赖 / import_depends| src_zephyr_ex_core_order_manager_py
    D_SELL_DECISION["卖出决策<br/>卖出决策，负责卖出信号生成、卖出时机判断和退出策<br/>略<br/>Sell Decision<br/>跨域节点 / cross-domain<br/>(设计态 / design)"]
    src_zephyr_ex_core_stop_loss_take_profit_executor_py -.->|runtime / runtime| D_SELL_DECISION
    src_zephyr_ex_core_sell_priority_scheduler_py -.->|runtime / runtime| D_SELL_DECISION
    D_PF_CORE["组合核心<br/>组合核心，负责投资组合构建、持仓管理和组合优化<br/>Portfolio Core<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_ex_core_trading_session_py -->|导入依赖 / import_depends| D_PF_CORE
    D_BACKTEST["回测<br/>回测，负责历史数据回测、回测引擎和回测报告<br/>Backtest<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_ex_core_services_live_portfolio_py -.->|导入依赖 / import_depends| D_BACKTEST
    D_TRADING["交易运营<br/>交易运营，负责交易生命周期管理、订单状态和成交处<br/>理<br/>Trading Operations<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_ex_core_services_live_portfolio_py -.->|导入依赖 / import_depends| D_TRADING
    src_zephyr_ex_core_services_live_portfolio_py -.->|导入依赖 / import_depends| D_BACKTEST
    src_zephyr_ex_core_services_live_portfolio_py -.->|导入依赖 / import_depends| D_TRADING
    src_zephyr_ex_core_trading_session_py -->|contract / contract| D_TRADING
    D_GOVERNANCE["生命周期管理<br/>生命周期管理，负责蓝图/模块<br/>/任务的声明周期管理和元数据治理<br/>Lifecycle Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_ex_core_trading_session_py -->|contract / contract| D_GOVERNANCE
    src_zephyr_ex_core_trading_session_py -->|contract / contract| D_GOVERNANCE
    D_REPORTING["报告<br/>报告，负责投资报告、风险报告和合规报告的生成与分<br/>发<br/>Reporting<br/>跨域节点 / cross-domain<br/>(设计态 / design)"]
    src_zephyr_ex_core_execution_report_py -.->|data / data| D_REPORTING
    src_zephyr_ex_core_stop_loss_take_profit_executor_py -.->|runtime / runtime| D_SELL_DECISION
    src_zephyr_ex_core_sell_priority_scheduler_py -.->|runtime / runtime| D_SELL_DECISION
    D_RISK["风控<br/>风控，负责风险指标计算、风险限额管理和风险预警<br/>Risk Control<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_ex_core_live_simulation_switcher_py -.->|runtime / runtime| D_RISK
    src_zephyr_ex_core_trading_session_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_TRADING -.->|import / import| src_zephyr_ex_core_fill_handler_py
    D_BACKTEST -->|导入依赖 / import_depends| src_zephyr_ex_core_adapters_simulation_broker_py
    D_BACKTEST -->|导入依赖 / import_depends| src_zephyr_ex_core_adapters_miniqmt_broker_py
    D_TRADING -.->|runtime / runtime| src_zephyr_ex_core_order_manager_py
    D_EX_SOR["执行路由<br/>执行路由，负责订单路由、智能拆单和执行场所选择<br/>Execution Routing<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_EX_SOR -->|导入依赖 / import_depends| src_zephyr_ex_core_execution_engine_py
    D_EX_SOR -.->|data / data| src_zephyr_ex_core_execution_report_py
    D_EX_SOR -.->|data / data| src_zephyr_ex_core_execution_report_py
    D_EX_SOR -.->|data / data| src_zephyr_ex_core_execution_report_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_ex_core_adapters_init_py,src_zephyr_ex_core_adapters_miniqmt_broker_py,src_zephyr_ex_core_adapters_risk_validation_bridge_py,src_zephyr_ex_core_adapters_simulation_broker_py,src_zephyr_ex_core_execution_engine_py,src_zephyr_ex_core_order_manager_py,src_zephyr_ex_core_signal_providers_py,src_zephyr_ex_core_trading_session_py,src_zephyr_governance_escalation_order_state_escalator_py production
    class src_zephyr_ex_core_auction_deviation_executor_py,src_zephyr_ex_core_audit_journal,src_zephyr_ex_core_batch_executor_py,src_zephyr_ex_core_batch_take_profit_executor_py,src_zephyr_ex_core_conditional_order_manager_py,src_zephyr_ex_core_execution_mcp_server_py,src_zephyr_ex_core_execution_report_py,src_zephyr_ex_core_fill_handler_py,src_zephyr_ex_core_fill_processor_py,src_zephyr_ex_core_live_simulation_switcher_py,src_zephyr_ex_core_order_splitter_py,src_zephyr_ex_core_position_tracker,src_zephyr_ex_core_redis_idempotency,src_zephyr_ex_core_sell_priority_scheduler_py,src_zephyr_ex_core_services_live_portfolio_py,src_zephyr_ex_core_stop_loss_take_profit_executor_py design
    class D_PF_CORE,D_BACKTEST,D_TRADING,D_GOVERNANCE,D_RISK,D_EX_SOR external_prod
    class D_SELL_DECISION,D_REPORTING external_design
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 9 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_ex_core_adapters_init_py["ex_core/adapters 包入口<br/>D_EX_CORE adapters — 券商/风控适配器 re-export<br/>wrapper<br/>文件: adapters/__init__.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_adapters_risk_validation_bridge_py["adapters/risk_validation_bridge<br/>Re-export wrapper: risk_validation_bridge<br/>真源在 zephyr.governance.adapters.r...<br/>文件: adapters/risk_validation_bridge.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_adapters_simulation_broker_py["adapters/simulation_broker<br/>Re-export wrapper: simulation_broker 真源在<br/>zephyr.governance.adapters.simula...<br/>文件: adapters/simulation_broker.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_execution_engine_py["ex_core/execution_engine<br/>D_EXECUTION_CORE — Execution Engine<br/>文件: ex_core/execution_engine.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_signal_providers_py["ex_core/signal_providers<br/>D_EXECUTION_CORE — 信号源 / 价格源 callable 工厂<br/>文件: ex_core/signal_providers.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_trading_session_py["ex_core/trading_session<br/>D_EXECUTION_CORE — TradingSession<br/>盘中实时调仓编排器<br/>文件: ex_core/trading_session.py<br/>(生产态 / production)"]
    src_zephyr_governance_escalation_order_state_escalator_py["escalation/order_state_escalator<br/>Order State Escalator — v0.10.0<br/>订单状态机升级器。<br/>文件: escalation/order_state_escalator.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_adapters_init_py ~~~ src_zephyr_ex_core_adapters_risk_validation_bridge_py
    src_zephyr_ex_core_adapters_risk_validation_bridge_py ~~~ src_zephyr_ex_core_adapters_simulation_broker_py
    src_zephyr_ex_core_adapters_simulation_broker_py ~~~ src_zephyr_ex_core_execution_engine_py
    src_zephyr_ex_core_execution_engine_py ~~~ src_zephyr_ex_core_signal_providers_py
    src_zephyr_ex_core_signal_providers_py ~~~ src_zephyr_ex_core_trading_session_py
    src_zephyr_ex_core_trading_session_py ~~~ src_zephyr_governance_escalation_order_state_escalator_py
    src_zephyr_ex_core_adapters_miniqmt_broker_py["adapters/miniqmt_broker<br/>MiniQMT 实盘券商适配器（对接<br/>xttrader，A股实盘交易）<br/>文件: adapters/miniqmt_broker.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_order_manager_py["ex_core/order_manager<br/>D_EXECUTION_CORE — Order Manager<br/>文件: ex_core/order_manager.py<br/>(生产态 / production)"]
    src_zephyr_ex_core_adapters_miniqmt_broker_py ~~~ src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_execution_engine_py -->|导入依赖 / import_depends| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_adapters_init_py -->|导入依赖 / import_depends| src_zephyr_ex_core_adapters_miniqmt_broker_py
    src_zephyr_ex_core_trading_session_py -->|导入依赖 / import_depends| src_zephyr_ex_core_order_manager_py
    src_zephyr_ex_core_trading_session_py -->|导入依赖 / import_depends| src_zephyr_ex_core_order_manager_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_ex_core_adapters_init_py,src_zephyr_ex_core_adapters_miniqmt_broker_py,src_zephyr_ex_core_adapters_risk_validation_bridge_py,src_zephyr_ex_core_adapters_simulation_broker_py,src_zephyr_ex_core_execution_engine_py,src_zephyr_ex_core_order_manager_py,src_zephyr_ex_core_signal_providers_py,src_zephyr_ex_core_trading_session_py,src_zephyr_governance_escalation_order_state_escalator_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 16 个），不含跨域外部节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_ex_core_auction_deviation_executor_py["ex_core/auction_deviation_executor<br/>ex core包的auction_deviation_executor模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/auction_deviation_executor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_batch_executor_py["ex_core/batch_executor<br/>ex core包的batch_executor模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/batch_executor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_batch_take_profit_executor_py["ex_core/batch_take_profit_executor<br/>ex core包的batch_take_profit_executor模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/batch_take_profit_executor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_conditional_order_manager_py["ex_core/conditional_order_manager<br/>ex core包的conditional_order_manager模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/conditional_order_manager.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_execution_mcp_server_py["ex_core/execution_mcp_server<br/>ex core包的execution_mcp_server模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/execution_mcp_server.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_execution_report_py["ex_core/execution_report<br/>ex core包的execution_report模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/execution_report.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_fill_handler_py["ex_core/fill_handler<br/>ex core包的fill_handler模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/fill_handler.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_fill_processor_py["ex_core/fill_processor<br/>ex core包的fill_processor模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/fill_processor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_live_simulation_switcher_py["ex_core/live_simulation_switcher<br/>ex core包的live_simulation_switcher模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/live_simulation_switcher.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_order_splitter_py["ex_core/order_splitter<br/>ex core包的order_splitter模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/order_splitter.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_redis_idempotency["ex_core/redis_idempotency<br/>ex core包的redis_idempotency模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: redis_idempotency/<br/>(设计态 / design)"]
    src_zephyr_ex_core_sell_priority_scheduler_py["ex_core/sell_priority_scheduler<br/>ex core包的sell_priority_scheduler模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/sell_priority_scheduler.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_services_live_portfolio_py["services/live_portfolio<br/>服务包的live_portfolio模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: services/live_portfolio.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_stop_loss_take_profit_executor_py["ex_core/stop_loss_take_profit_executor<br/>ex core包的stop_loss_take_profit_executor模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: ex_core/stop_loss_take_profit_executor.py<br/>(设计态 / design)"]
    src_zephyr_ex_core_auction_deviation_executor_py ~~~ src_zephyr_ex_core_batch_executor_py
    src_zephyr_ex_core_batch_executor_py ~~~ src_zephyr_ex_core_batch_take_profit_executor_py
    src_zephyr_ex_core_batch_take_profit_executor_py ~~~ src_zephyr_ex_core_conditional_order_manager_py
    src_zephyr_ex_core_conditional_order_manager_py ~~~ src_zephyr_ex_core_execution_mcp_server_py
    src_zephyr_ex_core_execution_mcp_server_py ~~~ src_zephyr_ex_core_execution_report_py
    src_zephyr_ex_core_execution_report_py ~~~ src_zephyr_ex_core_fill_handler_py
    src_zephyr_ex_core_fill_handler_py ~~~ src_zephyr_ex_core_fill_processor_py
    src_zephyr_ex_core_fill_processor_py ~~~ src_zephyr_ex_core_live_simulation_switcher_py
    src_zephyr_ex_core_live_simulation_switcher_py ~~~ src_zephyr_ex_core_order_splitter_py
    src_zephyr_ex_core_order_splitter_py ~~~ src_zephyr_ex_core_redis_idempotency
    src_zephyr_ex_core_redis_idempotency ~~~ src_zephyr_ex_core_sell_priority_scheduler_py
    src_zephyr_ex_core_sell_priority_scheduler_py ~~~ src_zephyr_ex_core_services_live_portfolio_py
    src_zephyr_ex_core_services_live_portfolio_py ~~~ src_zephyr_ex_core_stop_loss_take_profit_executor_py
    src_zephyr_ex_core_position_tracker["ex_core/position_tracker<br/>ex core包的position_tracker模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: position_tracker/<br/>(设计态 / design)"]
    src_zephyr_ex_core_audit_journal["ex_core/audit_journal<br/>ex core包的audit_journal模块<br/>⛔ 交易执行核心域，设计已就绪，等待开发排期<br/>文件: audit_journal/<br/>(设计态 / design)"]
    src_zephyr_ex_core_fill_handler_py -.->|runtime / runtime| src_zephyr_ex_core_position_tracker
    src_zephyr_ex_core_fill_handler_py -.->|event / event| src_zephyr_ex_core_audit_journal
    src_zephyr_ex_core_position_tracker -.->|event / event| src_zephyr_ex_core_audit_journal
    src_zephyr_ex_core_redis_idempotency -.->|event / event| src_zephyr_ex_core_audit_journal
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_ex_core_auction_deviation_executor_py,src_zephyr_ex_core_audit_journal,src_zephyr_ex_core_batch_executor_py,src_zephyr_ex_core_batch_take_profit_executor_py,src_zephyr_ex_core_conditional_order_manager_py,src_zephyr_ex_core_execution_mcp_server_py,src_zephyr_ex_core_execution_report_py,src_zephyr_ex_core_fill_handler_py,src_zephyr_ex_core_fill_processor_py,src_zephyr_ex_core_live_simulation_switcher_py,src_zephyr_ex_core_order_splitter_py,src_zephyr_ex_core_position_tracker,src_zephyr_ex_core_redis_idempotency,src_zephyr_ex_core_sell_priority_scheduler_py,src_zephyr_ex_core_services_live_portfolio_py,src_zephyr_ex_core_stop_loss_take_profit_executor_py design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | MiniQMT 实盘券商适配器（对接 xttrader，A股实盘交易） (ada... | → | D_BACKTEST 回测: 共享撮合逻辑模块（回测=实盘一致性核心） (core/matching_lo... | 导入依赖 / import_depends |
| 2 | services/live_portfolio.py | → | D_BACKTEST 回测: 共享撮合逻辑模块（回测=实盘一致性核心） (core/matching_lo... | 导入依赖 / import_depends |
| 3 | services/live_portfolio.py | → | D_BACKTEST 回测: 回测持仓管理模块 (core/portfolio.py) | 导入依赖 / import_depends |
| 4 | D_EXECUTION_CORE — 信号源 / 价格源 callable 工厂 (ex_cor... | → | D_FACTOR 因子: D-FACTOR-ANA-10 多因子合成——将多个因子值合成为综合信号... | 导入依赖 / import_depends |
| 5 | D_EXECUTION_CORE — 信号源 / 价格源 callable 工厂 (ex_cor... | → | D_FACTOR 因子: D-FACTOR-03 因子评估回测运行器——端到端因子评估。 (evalu... | 导入依赖 / import_depends |
| 6 | D_EXECUTION_CORE — 信号源 / 价格源 callable 工厂 (ex_cor... | → | D_FACTOR 因子: ZephyrAlpha — D_FACTOR Alpha Factor Layer (factor/factor... | 导入依赖 / import_depends |
| 7 | D_EX_CORE adapters — 券商/风控适配器 re-export wrapper (... | → | D_GOVERNANCE 生命周期管理: D_EXECUTION_CORE — Risk Validation Bridge (DW-239) (adap... | 导入依赖 / import_depends |
| 8 | D_EX_CORE adapters — 券商/风控适配器 re-export wrapper (... | → | D_GOVERNANCE 生命周期管理: D_EXECUTION_CORE — Simulation Broker Adapter (adapters/s... | 导入依赖 / import_depends |
| 9 | Re-export wrapper: risk_validation_bridge 真源在 zephyr.g... | → | D_GOVERNANCE 生命周期管理: D_EXECUTION_CORE — Risk Validation Bridge (DW-239) (adap... | 导入依赖 / import_depends |
| 10 | Re-export wrapper: simulation_broker 真源在 zephyr.govern... | → | D_GOVERNANCE 生命周期管理: D_EXECUTION_CORE — Simulation Broker Adapter (adapters/s... | 导入依赖 / import_depends |
| 11 | D_EXECUTION_CORE — Execution Engine (ex_core/execution_e... | → | D_GOVERNANCE 生命周期管理: D_EXECUTION_CORE — Risk Validation Bridge (DW-239) (adap... | 导入依赖 / import_depends |
| 12 | D_EXECUTION_CORE — TradingSession 盘中实时调仓编排器 (ex... | → | D_GOVERNANCE 生命周期管理: D_EXECUTION_CORE — Risk Validation Bridge (DW-239) (adap... | contract / contract |
| 13 | D_EXECUTION_CORE — TradingSession 盘中实时调仓编排器 (ex... | → | D_GOVERNANCE 生命周期管理: D_EXECUTION_CORE — Risk Validation Bridge (DW-239) (adap... | 导入依赖 / import_depends |
| 14 | D_EXECUTION_CORE — TradingSession 盘中实时调仓编排器 (ex... | → | D_GOVERNANCE 生命周期管理: D_PORTFOLIO_CORE — StrategyBase + StrategyMeta + Strateg... | contract / contract |
| 15 | D_EXECUTION_CORE — TradingSession 盘中实时调仓编排器 (ex... | → | D_GOVERNANCE 生命周期管理: D_PORTFOLIO_CORE — StrategyBase + StrategyMeta + Strateg... | 导入依赖 / import_depends |
| 16 | D_EXECUTION_CORE — Execution Engine (ex_core/execution_e... | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/order.py | 导入依赖 / import_depends |
| 17 | D_EXECUTION_CORE — Execution Engine (ex_core/execution_e... | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/risk_limits.py | 导入依赖 / import_depends |
| 18 | D_EXECUTION_CORE — Order Manager (ex_core/order_manager.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/fill.py | 导入依赖 / import_depends |
| 19 | D_EXECUTION_CORE — Order Manager (ex_core/order_manager.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/order.py | 导入依赖 / import_depends |
| 20 | D_EXECUTION_CORE — TradingSession 盘中实时调仓编排器 (ex... | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/fill.py | 导入依赖 / import_depends |
| 21 | D_EXECUTION_CORE — TradingSession 盘中实时调仓编排器 (ex... | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/order.py | 导入依赖 / import_depends |
| 22 | D_EXECUTION_CORE — TradingSession 盘中实时调仓编排器 (ex... | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/position.py | 导入依赖 / import_depends |
| 23 | D_EXECUTION_CORE — TradingSession 盘中实时调仓编排器 (ex... | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/risk_limits.py | 导入依赖 / import_depends |
| 24 | D_EXECUTION_CORE — TradingSession 盘中实时调仓编排器 (ex... | → | D_PF_CORE 组合核心: D_PORTFOLIO_CORE — StrategyRunner 策略运行器（胶水层） (... | 导入依赖 / import_depends |
| 25 | ex_core/execution_report.py | → | D_REPORTING 报告: reporting/report_publisher.py | data / data |
| 26 | ex_core/live_simulation_switcher.py | → | D_RISK 风控: D_RISK — Risk Validator (risk/risk_validator.py) | runtime / runtime |
| 27 | ex_core/sell_priority_scheduler.py | → | D_SELL_DECISION 卖出决策: core/position_triage.py | runtime / runtime |
| 28 | ex_core/sell_priority_scheduler.py | → | D_SELL_DECISION 卖出决策: core/position_triage.py | runtime / runtime |
| 29 | ex_core/stop_loss_take_profit_executor.py | → | D_SELL_DECISION 卖出决策: core/position_triage.py | runtime / runtime |
| 30 | ex_core/stop_loss_take_profit_executor.py | → | D_SELL_DECISION 卖出决策: core/position_triage.py | runtime / runtime |
| 31 | MiniQMT 实盘券商适配器（对接 xttrader，A股实盘交易） (ada... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 32 | D_EXECUTION_CORE — Order Manager (ex_core/order_manager.py) | → | D_SHARED 共享服务: OrderSide/OrderStatus/OrderType — 交易枚举真源 (5.152 #1... | 导入依赖 / import_depends |
| 33 | D_EXECUTION_CORE — TradingSession 盘中实时调仓编排器 (ex... | → | D_SHARED 共享服务: OrderSide/OrderStatus/OrderType — 交易枚举真源 (5.152 #1... | 导入依赖 / import_depends |
| 34 | D_EX_CORE adapters — 券商/风控适配器 re-export wrapper (... | → | D_TRADING 交易运营: D_EXECUTION_CORE — BrokerInterface (trading_contracts/br... | 导入依赖 / import_depends |
| 35 | MiniQMT 实盘券商适配器（对接 xttrader，A股实盘交易） (ada... | → | D_TRADING 交易运营: D_EXECUTION_CORE — BrokerInterface (trading_contracts/br... | 导入依赖 / import_depends |
| 36 | MiniQMT 实盘券商适配器（对接 xttrader，A股实盘交易） (ada... | → | D_TRADING 交易运营: Re-export wrapper: Fill 真源在 zephyr.shared.contracts.fi... | 导入依赖 / import_depends |
| 37 | MiniQMT 实盘券商适配器（对接 xttrader，A股实盘交易） (ada... | → | D_TRADING 交易运营: Re-export wrapper: Order 真源在 zephyr.shared.contracts.o... | 导入依赖 / import_depends |
| 38 | MiniQMT 实盘券商适配器（对接 xttrader，A股实盘交易） (ada... | → | D_TRADING 交易运营: Re-export wrapper: PositionSnapshot 真源在 zephyr.shared.... | 导入依赖 / import_depends |
| 39 | D_EXECUTION_CORE — Order Manager (ex_core/order_manager.py) | → | D_TRADING 交易运营: D_EXECUTION_CORE — BrokerInterface (trading_contracts/br... | 导入依赖 / import_depends |
| 40 | services/live_portfolio.py | → | D_TRADING 交易运营: Re-export wrapper: PositionSnapshot 真源在 zephyr.shared.... | 导入依赖 / import_depends |
| 41 | services/live_portfolio.py | → | D_TRADING 交易运营: risk/risk_limits.py | 导入依赖 / import_depends |
| 42 | D_EXECUTION_CORE — TradingSession 盘中实时调仓编排器 (ex... | → | D_TRADING 交易运营: D_EXECUTION_CORE — BrokerInterface (trading_contracts/br... | 导入依赖 / import_depends |
| 43 | D_EXECUTION_CORE — TradingSession 盘中实时调仓编排器 (ex... | → | D_TRADING 交易运营: D_EXECUTION_CORE — BrokerInterface (trading_contracts/br... | contract / contract |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_BACKTEST 回测: 事件驱动回测引擎（v1.1.0 新增，Tick 级回测核心） (impleme... | → | MiniQMT 实盘券商适配器（对接 xttrader，A股实盘交易） (ada... | 导入依赖 / import_depends |
| 2 | D_BACKTEST 回测: 事件驱动回测引擎（v1.1.0 新增，Tick 级回测核心） (impleme... | → | Re-export wrapper: simulation_broker 真源在 zephyr.govern... | 导入依赖 / import_depends |
| 3 | D_EX_SOR 执行路由: Broker Adapter Manager — 多券商统一适配器 (MOD-XS-002) (... | → | D_EXECUTION_CORE — Execution Engine (ex_core/execution_e... | 导入依赖 / import_depends |
| 4 | D_EX_SOR 执行路由: Execution Quality Scorer — 执行质量评分器 (MOD-XS-EXT-00... | → | ex_core/execution_report.py | data / data |
| 5 | D_EX_SOR 执行路由: Slippage Analyzer — 滑点分析器 (MOD-XS-EXT-001) (service... | → | ex_core/execution_report.py | data / data |
| 6 | D_EX_SOR 执行路由: Transaction Cost Optimizer — 交易成本优化器 (MOD-XS-EXT-... | → | ex_core/execution_report.py | data / data |
| 7 | D_TRADING 交易运营: pnl_calculator/ | → | ex_core/fill_handler.py | import / import |
| 8 | D_TRADING 交易运营: trading/settlement_reconciliation.py | → | D_EXECUTION_CORE — Order Manager (ex_core/order_manager.py) | runtime / runtime |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 11 个外部域直接连接（出边 43 条 + 入边 8 条 = 51 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_EX_CORE["D_EX_CORE<br/>执行核心"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE<br/>跨层契约基础设施"]
    D_SELL_DECISION["D_SELL_DECISION<br/>卖出决策"]
    D_BACKTEST["D_BACKTEST<br/>回测"]
    D_FACTOR["D_FACTOR<br/>因子"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_REPORTING["D_REPORTING<br/>报告"]
    D_PF_CORE["D_PF_CORE<br/>组合核心"]
    D_RISK["D_RISK<br/>风控"]
    D_EX_SOR["D_EX_SOR<br/>执行路由"]
    D_EX_CORE -->|10条 contract / contract, 导入依赖 / import_depends| D_TRADING
    D_EX_CORE -->|9条 contract / contract, 导入依赖 / import_depends| D_GOVERNANCE
    D_EX_CORE -->|8条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_EX_CORE -->|4条 runtime / runtime| D_SELL_DECISION
    D_EX_CORE -->|3条 导入依赖 / import_depends| D_BACKTEST
    D_EX_CORE -->|3条 导入依赖 / import_depends| D_FACTOR
    D_EX_CORE -->|3条 导入依赖 / import_depends| D_SHARED
    D_EX_CORE -->|1条 data / data| D_REPORTING
    D_EX_CORE -->|1条 导入依赖 / import_depends| D_PF_CORE
    D_EX_CORE -->|1条 runtime / runtime| D_RISK
    D_EX_SOR -->|4条 data / data, 导入依赖 / import_depends| D_EX_CORE
    D_BACKTEST -->|2条 导入依赖 / import_depends| D_EX_CORE
    D_TRADING -->|2条 import / import, runtime / runtime| D_EX_CORE
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
