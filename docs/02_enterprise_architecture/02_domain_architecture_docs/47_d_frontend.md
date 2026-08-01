---
doc_type: architecture_view
title: D_FRONTEND 前端架构文档
version: "1.0"
status: active
date: 2026-08-02
owner: auto-generator
ttl: permanent
---

# 47_d_frontend / 前端域 / Frontend

> **功能简介 / Overview**: 前端，负责用户界面展示、交互可视化和前端状态管理

> **文档作用 / Purpose**: 展示 前端（D_FRONTEND）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/47_d_frontend.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 47 | Number | 47 |
| 域ID | D_FRONTEND | Domain ID | D_FRONTEND |
| 域名称 | 前端 | Domain Name | Frontend |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 14 | Module Count | 14 |
| 域内依赖 | 20 | Internal Dependencies | 20 |
| 跨域入边 | 0 | Cross-domain Incoming | 0 |
| 跨域出边 | 6 | Cross-domain Outgoing | 6 |
| 设计态模块 | 2 | Design Modules | 2 |
| 生产态模块 | 12 | Production Modules | 12 |
| 容量 | 12/150 (正常) | Capacity | 12/150 (正常) |
| 描述 | 前端，负责用户界面展示、交互可视化和前端状态管理 | Description | 前端，负责用户界面展示、交互可视化和前端状态管理 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 14 个模块（生产态 12 + 设计态 2），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    scripts_tests_test_frontend_components_py["测试前端components<br/>5个前端组件综合验证脚本（TTL=task_<br/>bound，施工完成后退役）<br/>test_frontend_components<br/>文件: tests/test_frontend_components.py<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_app_py["应用<br/>ZephyrAlpha Dashboard · Streamlit 仪表盘<br/>（已弃用 v3.1.0）<br/>app<br/>文件: dashboard/app.py<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_app_panel_py["应用面板<br/>app_panel · Panel 仪表盘主应用入口（v3.1.0,<br/>#ARCH-047）<br/>文件: dashboard/app_panel.py<br/>(生产态 / production)"]
    src_zephyr_frontend_implementations_default_approval_gateway_py["默认审批网关<br/>默认approval网关，前端的门禁，在关键节点检查是否<br/>放行<br/>⛔ 该域，设计已就绪，等待开发排期<br/>default_approval_gateway<br/>文件: implementations/default_approval_<br/>gateway.py<br/>(设计态 / design)"]
    src_zephyr_frontend_implementations_default_notification_manager_py["默认通知管理器<br/>默认通知管理器，前端的通知器，把消息推送给接收方<br/>⛔ 该域，设计已就绪，等待开发排期<br/>default_notification_manager<br/>文件: implementations/default_notification_<br/>manager.py<br/>(设计态 / design)"]
    scripts_tests_test_frontend_components_py ~~~ src_zephyr_frontend_dashboard_app_py
    src_zephyr_frontend_dashboard_app_py ~~~ src_zephyr_frontend_dashboard_app_panel_py
    src_zephyr_frontend_dashboard_app_panel_py ~~~ src_zephyr_frontend_implementations_default_approval_gateway_py
    src_zephyr_frontend_implementations_default_approval_gateway_py ~~~ src_zephyr_frontend_implementations_default_notification_manager_py
    src_zephyr_frontend_dashboard_components_backtest_performance_py["回测绩效<br/>backtest_performance ·<br/>掘金量化风格绩效分析可视化（v1.0.0, #ARCH-047）<br/>文件: components/backtest_performance.py<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_components_backtest_results_py["回测results<br/>backtest_results · 回测结果可视化组件（v3.0.0<br/>Panel+HoloViz 重构, #ARCH-047）<br/>文件: components/backtest_results.py<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_components_fitness_functions_py["适应度functions<br/>fitness_functions · Fitness Functions<br/>仪表盘组件（v3.1.0 Panel 迁移, #ARCH-047）<br/>文件: components/fitness_functions.py<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_components_order_book_py["订单book<br/>order_book · 5档盘口实时展示组件（v3.0.0<br/>Panel+HoloViz 重构, #ARCH-047）<br/>文件: components/order_book.py<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_components_position_monitor_py["持仓监控<br/>position_monitor · 实盘持仓监控组件（v3.0.0<br/>Panel+HoloViz 重构, #ARCH-047）<br/>文件: components/position_monitor.py<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_components_tick_replay_py["逐笔replay<br/>tick_replay · Tick 回放可视化组件（v3.0.0<br/>Panel+HoloViz 重构, #ARCH-047）<br/>文件: components/tick_replay.py<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_components_trade_panel_py["交易面板<br/>trade_panel · 实盘交易面板组件（v3.0.0<br/>Panel+HoloViz 重构, #ARCH-047, human_gated）<br/>文件: components/trade_panel.py<br/>(生产态 / production)"]
    src_zephyr_frontend_interface_base_py["接口基类<br/>接口基类。D_FRONTEND — Human-AI Interface Layer<br/>Skeleton<br/>文件: frontend/interface_base.py<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_components_backtest_performance_py ~~~ src_zephyr_frontend_dashboard_components_backtest_results_py
    src_zephyr_frontend_dashboard_components_backtest_results_py ~~~ src_zephyr_frontend_dashboard_components_fitness_functions_py
    src_zephyr_frontend_dashboard_components_fitness_functions_py ~~~ src_zephyr_frontend_dashboard_components_order_book_py
    src_zephyr_frontend_dashboard_components_order_book_py ~~~ src_zephyr_frontend_dashboard_components_position_monitor_py
    src_zephyr_frontend_dashboard_components_position_monitor_py ~~~ src_zephyr_frontend_dashboard_components_tick_replay_py
    src_zephyr_frontend_dashboard_components_tick_replay_py ~~~ src_zephyr_frontend_dashboard_components_trade_panel_py
    src_zephyr_frontend_dashboard_components_trade_panel_py ~~~ src_zephyr_frontend_interface_base_py
    src_zephyr_frontend_dashboard_components_chart_factory_py["chart工厂<br/>chart_factory · 图表统一工厂（v3.0.0新增,<br/>#ARCH-047）<br/>文件: components/chart_factory.py<br/>(生产态 / production)"]
    src_zephyr_frontend_implementations_default_notification_manager_py -.->|导入依赖 / import_depends| src_zephyr_frontend_interface_base_py
    src_zephyr_frontend_implementations_default_approval_gateway_py -.->|导入依赖 / import_depends| src_zephyr_frontend_interface_base_py
    src_zephyr_frontend_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_fitness_functions_py
    src_zephyr_frontend_dashboard_app_panel_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_backtest_performance_py
    src_zephyr_frontend_dashboard_app_panel_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_backtest_results_py
    src_zephyr_frontend_dashboard_app_panel_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_fitness_functions_py
    src_zephyr_frontend_dashboard_app_panel_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_order_book_py
    src_zephyr_frontend_dashboard_app_panel_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_tick_replay_py
    src_zephyr_frontend_dashboard_app_panel_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_trade_panel_py
    src_zephyr_frontend_dashboard_app_panel_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_position_monitor_py
    src_zephyr_frontend_dashboard_components_backtest_results_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_chart_factory_py
    src_zephyr_frontend_dashboard_components_order_book_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_chart_factory_py
    src_zephyr_frontend_dashboard_components_tick_replay_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_chart_factory_py
    src_zephyr_frontend_dashboard_components_trade_panel_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_chart_factory_py
    src_zephyr_frontend_dashboard_components_position_monitor_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_chart_factory_py
    scripts_tests_test_frontend_components_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_backtest_results_py
    scripts_tests_test_frontend_components_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_order_book_py
    scripts_tests_test_frontend_components_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_tick_replay_py
    scripts_tests_test_frontend_components_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_trade_panel_py
    scripts_tests_test_frontend_components_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_position_monitor_py
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_components_trade_panel_py -->|导入依赖 / import_depends| D_SHARED
    D_FEEDBACK_LOOP["反馈循环引擎<br/>反馈循环引擎，负责系统自我改进闭环：异常检测、根<br/>因诊断、自动修复和自我进化<br/>Feedback Loop Engine<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_components_fitness_functions_py -->|导入依赖 / import_depends| D_FEEDBACK_LOOP
    D_GOVERNANCE["生命周期管理<br/>生命周期管理，负责蓝图/模块<br/>/任务的声明周期管理和元数据治理<br/>Lifecycle Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_app_panel_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_frontend_dashboard_app_panel_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_frontend_dashboard_components_chart_factory_py -->|导入依赖 / import_depends| D_SHARED
    D_TRADING["交易运营<br/>交易运营，负责交易生命周期管理、订单状态和成交处<br/>理<br/>Trading Operations<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_components_trade_panel_py -->|导入依赖 / import_depends| D_TRADING
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class scripts_tests_test_frontend_components_py,src_zephyr_frontend_dashboard_app_py,src_zephyr_frontend_dashboard_app_panel_py,src_zephyr_frontend_dashboard_components_backtest_performance_py,src_zephyr_frontend_dashboard_components_backtest_results_py,src_zephyr_frontend_dashboard_components_chart_factory_py,src_zephyr_frontend_dashboard_components_fitness_functions_py,src_zephyr_frontend_dashboard_components_order_book_py,src_zephyr_frontend_dashboard_components_position_monitor_py,src_zephyr_frontend_dashboard_components_tick_replay_py,src_zephyr_frontend_dashboard_components_trade_panel_py,src_zephyr_frontend_interface_base_py production
    class src_zephyr_frontend_implementations_default_approval_gateway_py,src_zephyr_frontend_implementations_default_notification_manager_py design
    class D_SHARED,D_FEEDBACK_LOOP,D_GOVERNANCE,D_TRADING external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 12 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    scripts_tests_test_frontend_components_py["测试前端components<br/>5个前端组件综合验证脚本（TTL=task_<br/>bound，施工完成后退役）<br/>test_frontend_components<br/>文件: tests/test_frontend_components.py<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_app_py["应用<br/>ZephyrAlpha Dashboard · Streamlit 仪表盘<br/>（已弃用 v3.1.0）<br/>app<br/>文件: dashboard/app.py<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_app_panel_py["应用面板<br/>app_panel · Panel 仪表盘主应用入口（v3.1.0,<br/>#ARCH-047）<br/>文件: dashboard/app_panel.py<br/>(生产态 / production)"]
    src_zephyr_frontend_interface_base_py["接口基类<br/>接口基类。D_FRONTEND — Human-AI Interface Layer<br/>Skeleton<br/>文件: frontend/interface_base.py<br/>(生产态 / production)"]
    scripts_tests_test_frontend_components_py ~~~ src_zephyr_frontend_dashboard_app_py
    src_zephyr_frontend_dashboard_app_py ~~~ src_zephyr_frontend_dashboard_app_panel_py
    src_zephyr_frontend_dashboard_app_panel_py ~~~ src_zephyr_frontend_interface_base_py
    src_zephyr_frontend_dashboard_components_backtest_performance_py["回测绩效<br/>backtest_performance ·<br/>掘金量化风格绩效分析可视化（v1.0.0, #ARCH-047）<br/>文件: components/backtest_performance.py<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_components_backtest_results_py["回测results<br/>backtest_results · 回测结果可视化组件（v3.0.0<br/>Panel+HoloViz 重构, #ARCH-047）<br/>文件: components/backtest_results.py<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_components_fitness_functions_py["适应度functions<br/>fitness_functions · Fitness Functions<br/>仪表盘组件（v3.1.0 Panel 迁移, #ARCH-047）<br/>文件: components/fitness_functions.py<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_components_order_book_py["订单book<br/>order_book · 5档盘口实时展示组件（v3.0.0<br/>Panel+HoloViz 重构, #ARCH-047）<br/>文件: components/order_book.py<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_components_position_monitor_py["持仓监控<br/>position_monitor · 实盘持仓监控组件（v3.0.0<br/>Panel+HoloViz 重构, #ARCH-047）<br/>文件: components/position_monitor.py<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_components_tick_replay_py["逐笔replay<br/>tick_replay · Tick 回放可视化组件（v3.0.0<br/>Panel+HoloViz 重构, #ARCH-047）<br/>文件: components/tick_replay.py<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_components_trade_panel_py["交易面板<br/>trade_panel · 实盘交易面板组件（v3.0.0<br/>Panel+HoloViz 重构, #ARCH-047, human_gated）<br/>文件: components/trade_panel.py<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_components_backtest_performance_py ~~~ src_zephyr_frontend_dashboard_components_backtest_results_py
    src_zephyr_frontend_dashboard_components_backtest_results_py ~~~ src_zephyr_frontend_dashboard_components_fitness_functions_py
    src_zephyr_frontend_dashboard_components_fitness_functions_py ~~~ src_zephyr_frontend_dashboard_components_order_book_py
    src_zephyr_frontend_dashboard_components_order_book_py ~~~ src_zephyr_frontend_dashboard_components_position_monitor_py
    src_zephyr_frontend_dashboard_components_position_monitor_py ~~~ src_zephyr_frontend_dashboard_components_tick_replay_py
    src_zephyr_frontend_dashboard_components_tick_replay_py ~~~ src_zephyr_frontend_dashboard_components_trade_panel_py
    src_zephyr_frontend_dashboard_components_chart_factory_py["chart工厂<br/>chart_factory · 图表统一工厂（v3.0.0新增,<br/>#ARCH-047）<br/>文件: components/chart_factory.py<br/>(生产态 / production)"]
    src_zephyr_frontend_dashboard_app_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_fitness_functions_py
    src_zephyr_frontend_dashboard_app_panel_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_backtest_performance_py
    src_zephyr_frontend_dashboard_app_panel_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_backtest_results_py
    src_zephyr_frontend_dashboard_app_panel_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_fitness_functions_py
    src_zephyr_frontend_dashboard_app_panel_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_order_book_py
    src_zephyr_frontend_dashboard_app_panel_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_tick_replay_py
    src_zephyr_frontend_dashboard_app_panel_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_trade_panel_py
    src_zephyr_frontend_dashboard_app_panel_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_position_monitor_py
    src_zephyr_frontend_dashboard_components_backtest_results_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_chart_factory_py
    src_zephyr_frontend_dashboard_components_order_book_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_chart_factory_py
    src_zephyr_frontend_dashboard_components_tick_replay_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_chart_factory_py
    src_zephyr_frontend_dashboard_components_trade_panel_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_chart_factory_py
    src_zephyr_frontend_dashboard_components_position_monitor_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_chart_factory_py
    scripts_tests_test_frontend_components_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_backtest_results_py
    scripts_tests_test_frontend_components_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_order_book_py
    scripts_tests_test_frontend_components_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_tick_replay_py
    scripts_tests_test_frontend_components_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_trade_panel_py
    scripts_tests_test_frontend_components_py -->|导入依赖 / import_depends| src_zephyr_frontend_dashboard_components_position_monitor_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class scripts_tests_test_frontend_components_py,src_zephyr_frontend_dashboard_app_py,src_zephyr_frontend_dashboard_app_panel_py,src_zephyr_frontend_dashboard_components_backtest_performance_py,src_zephyr_frontend_dashboard_components_backtest_results_py,src_zephyr_frontend_dashboard_components_chart_factory_py,src_zephyr_frontend_dashboard_components_fitness_functions_py,src_zephyr_frontend_dashboard_components_order_book_py,src_zephyr_frontend_dashboard_components_position_monitor_py,src_zephyr_frontend_dashboard_components_tick_replay_py,src_zephyr_frontend_dashboard_components_trade_panel_py,src_zephyr_frontend_interface_base_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 2 个），不含跨域外部节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_frontend_implementations_default_approval_gateway_py["默认审批网关<br/>默认approval网关，前端的门禁，在关键节点检查是否<br/>放行<br/>⛔ 该域，设计已就绪，等待开发排期<br/>default_approval_gateway<br/>文件: implementations/default_approval_<br/>gateway.py<br/>(设计态 / design)"]
    src_zephyr_frontend_implementations_default_notification_manager_py["默认通知管理器<br/>默认通知管理器，前端的通知器，把消息推送给接收方<br/>⛔ 该域，设计已就绪，等待开发排期<br/>default_notification_manager<br/>文件: implementations/default_notification_<br/>manager.py<br/>(设计态 / design)"]
    src_zephyr_frontend_implementations_default_approval_gateway_py ~~~ src_zephyr_frontend_implementations_default_notification_manager_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_frontend_implementations_default_approval_gateway_py,src_zephyr_frontend_implementations_default_notification_manager_py design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 适应度functions / fitness_functions (components/fitness_f... | → | D_FEEDBACK_LOOP 反馈循环引擎: 适应度functions / fitness_functions (feedback_loop/fitnes... | 导入依赖 / import_depends |
| 2 | 应用面板 / app_panel (dashboard/app_panel.py) | → | D_GOVERNANCE 生命周期管理: sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 3 | 应用面板 / app_panel (dashboard/app_panel.py) | → | D_GOVERNANCE 生命周期管理: 任务repo / task_repo (persistence/task_repo.py) | 导入依赖 / import_depends |
| 4 | chart工厂 / chart_factory (components/chart_factory.py) | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 5 | 交易面板 / trade_panel (components/trade_panel.py) | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 6 | 交易面板 / trade_panel (components/trade_panel.py) | → | D_TRADING 交易运营: 订单 / order (execution/order.py) | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

无跨域入边依赖 / No cross-domain incoming dependencies

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 4 个外部域直接连接（出边 6 条 + 入边 0 条 = 6 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_FRONTEND["D_FRONTEND<br/>前端"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_FEEDBACK_LOOP["D_FEEDBACK_LOOP<br/>反馈循环引擎"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_FRONTEND -->|2条 导入依赖 / import_depends| D_GOVERNANCE
    D_FRONTEND -->|2条 导入依赖 / import_depends| D_SHARED
    D_FRONTEND -->|1条 导入依赖 / import_depends| D_FEEDBACK_LOOP
    D_FRONTEND -->|1条 导入依赖 / import_depends| D_TRADING
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
