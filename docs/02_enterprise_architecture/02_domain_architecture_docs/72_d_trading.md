---
doc_type: architecture_view
title: D_TRADING 交易运营架构文档
version: "1.0"
status: active
date: 2026-08-01
owner: auto-generator
ttl: permanent
---

# 72_d_trading / 交易运营域 / Trading Operations

> **功能简介 / Overview**: 交易运营，负责交易生命周期管理、订单状态和成交处理

> **文档作用 / Purpose**: 展示 交易运营（D_TRADING）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/72_d_trading.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 72 | Number | 72 |
| 域ID | D_TRADING | Domain ID | D_TRADING |
| 域名称 | 交易运营 | Domain Name | Trading Operations |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 37 | Module Count | 37 |
| 域内依赖 | 12 | Internal Dependencies | 12 |
| 跨域入边 | 28 | Cross-domain Incoming | 28 |
| 跨域出边 | 59 | Cross-domain Outgoing | 59 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 37 | Production Modules | 37 |
| 容量 | 37/150 (正常) | Capacity | 37/150 (正常) |
| 描述 | 交易运营，负责交易生命周期管理、订单状态和成交处理 | Description | 交易运营，负责交易生命周期管理、订单状态和成交处理 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。全景图用颜色区分运营态/设计态，不再分页/拆子图。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景依赖图（全部模块，颜色区分运营态/设计态）

> 展示全部 37 个模块（生产态 37 + 设计态 0），节点含成熟度+中英文名+大白话+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_trading_action_dispatcher_init_py["(生产态 / production) 交易运营Action Dispatcher包 / Trading Action Dispatcher Package<br/>交易运营域下 action_dispatcher 子包，归集该方向的模块。本身不含业务逻辑，只是组织归属。<br/>文件: action_dispatcher/__init__.py"]
    src_zephyr_trading_admission_controller_py["(生产态 / production) 5.171 修复：admit(event: Any) Any 滥用——定义 VerdictEvent Protocol<br/>5.171 修复：admit(event: Any) Any 滥用——定义 VerdictEvent Protocol<br/>文件: trading/admission_controller.py"]
    src_zephyr_trading_auto_dispatcher_py["(生产态 / production) AutoDispatcher — 守护进程内的轻量 PipelineDispatcher<br/>AutoDispatcher — 守护进程内的轻量 PipelineDispatcher<br/>文件: trading/auto_dispatcher.py"]
    src_zephyr_trading_conductor_py["(生产态 / production) Conductor — AI session 全自动指挥官。<br/>Conductor — AI session 全自动指挥官。<br/>文件: trading/conductor.py"]
    src_zephyr_trading_gpu_consensus_scheduler_py["(生产态 / production) noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复...<br/>noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复...<br/>文件: trading/gpu_consensus_scheduler.py"]
    src_zephyr_trading_gpu_monitor_py["(生产态 / production) gpu_monitor.py — NVIDIA GPU 状态采集器<br/>gpu_monitor.py — NVIDIA GPU 状态采集器<br/>文件: trading/gpu_monitor.py"]
    src_zephyr_trading_ide_health_daemon_py["(生产态 / production) ide_health_daemon.py — TRAE IDE 幽灵窗口守护线程<br/>ide_health_daemon.py — TRAE IDE 幽灵窗口守护线程<br/>文件: trading/ide_health_daemon.py"]
    src_zephyr_trading_runtime_async_runtime_py["(生产态 / production) 事件循环引导 + run_in_executor 桥接。<br/>事件循环引导 + run_in_executor 桥接。<br/>文件: runtime/async_runtime.py"]
    src_zephyr_trading_speed_baseline_checker_py["(生产态 / production) Return True if the process belongs to this project, is a Python process,<br/>Return True if the process belongs to this project, is a Python process,<br/>文件: trading/speed_baseline_checker.py"]
    src_zephyr_trading_trading_contracts_broker_interface_py["(生产态 / production) D_EXECUTION_CORE — BrokerInterface<br/>D_EXECUTION_CORE — BrokerInterface<br/>文件: trading_contracts/broker_interface.py"]
    src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py["(生产态 / production) ==== BEGIN CODGEN:CTR-P1-003 ====<br/>==== BEGIN CODGEN:CTR-P1-003 ====<br/>文件: execution/capital_allocation_result.py"]
    src_zephyr_trading_trading_contracts_execution_execution_rejection_error_py["(生产态 / production) ==== BEGIN CODGEN:CTR-ERR-005 ====<br/>==== BEGIN CODGEN:CTR-ERR-005 ====<br/>文件: execution/execution_rejection_error.py"]
    src_zephyr_trading_trading_contracts_execution_execution_report_py["(生产态 / production) Re-export wrapper: ExecutionReport 真源在 zephyr.shared.contracts.execution_r...<br/>Re-export wrapper: ExecutionReport 真源在 zephyr.shared.contracts.execution_r...<br/>文件: execution/execution_report.py"]
    src_zephyr_trading_trading_contracts_execution_fill_py["(生产态 / production) Re-export wrapper: Fill 真源在 zephyr.shared.contracts.fill（CTR-005 codegen）<br/>Re-export wrapper: Fill 真源在 zephyr.shared.contracts.fill（CTR-005 codegen）<br/>文件: execution/fill.py"]
    src_zephyr_trading_trading_contracts_execution_model_serving_request_py["(生产态 / production) ==== BEGIN CODGEN:CTR-P1-004 ====<br/>==== BEGIN CODGEN:CTR-P1-004 ====<br/>文件: execution/model_serving_request.py"]
    src_zephyr_trading_trading_contracts_execution_position_py["(生产态 / production) Re-export wrapper: PositionSnapshot 真源在 zephyr.shared.contracts.position（...<br/>Re-export wrapper: PositionSnapshot 真源在 zephyr.shared.contracts.position（...<br/>文件: execution/position.py"]
    src_zephyr_trading_trading_contracts_factories_py["(生产态 / production) trading-contracts/factories.py — 交易域数据契约工厂方法<br/>trading-contracts/factories.py — 交易域数据契约工厂方法<br/>文件: trading_contracts/factories.py"]
    src_zephyr_trading_trading_contracts_market_instrument_py["(生产态 / production)<br/>文件: market/instrument.py"]
    src_zephyr_trading_trading_contracts_market_signal_degradation_warning_py["(生产态 / production) ==== BEGIN CODGEN:CTR-ERR-003 ====<br/>==== BEGIN CODGEN:CTR-ERR-003 ====<br/>文件: market/signal_degradation_warning.py"]
    src_zephyr_trading_trading_contracts_portfolio_contracts_money_py["(生产态 / production) 过渡兼容层（DEPRECATED）—— Money 契约 canonical 真源已收敛至 shared 侧。<br/>过渡兼容层（DEPRECATED）—— Money 契约 canonical 真源已收敛至 shared 侧。<br/>文件: contracts/money.py"]
    src_zephyr_trading_trading_contracts_portfolio_contracts_performance_attribution_report_py["(生产态 / production) Re-export shim — 真源已收敛至 zephyr.shared.contracts.performance_attributio...<br/>Re-export shim — 真源已收敛至 zephyr.shared.contracts.performance_attributio...<br/>文件: contracts/performance_attribution_report.py"]
    src_zephyr_trading_trading_contracts_portfolio_contracts_strategy_lifecycle_event_py["(生产态 / production) Re-export from shared SSoT — zephyr.shared.contracts.strategy_lifecycle_event<br/>Re-export from shared SSoT — zephyr.shared.contracts.strategy_lifecycle_event<br/>文件: contracts/strategy_lifecycle_event.py"]
    src_zephyr_trading_trading_contracts_risk_compliance_rule_py["(生产态 / production) ==== BEGIN CODGEN:CTR-P1-012 ====<br/>==== BEGIN CODGEN:CTR-P1-012 ====<br/>文件: risk/compliance_rule.py"]
    src_zephyr_trading_trading_contracts_risk_risk_limit_violation_error_py["(生产态 / production)<br/>文件: risk/risk_limit_violation_error.py"]
    src_zephyr_trading_trading_contracts_risk_risk_validator_protocol_py["(生产态 / production)<br/>文件: risk/risk_validator_protocol.py"]
    src_zephyr_trading_trading_contracts_risk_trading_kill_switch_py["(生产态 / production) SRC-0041: Copy file -- keep independent implementation, pending future review<br/>SRC-0041: Copy file -- keep independent implementation, pending future review<br/>文件: risk/trading_kill_switch.py"]
    src_zephyr_trading_action_dispatcher_init_py ~~~ src_zephyr_trading_admission_controller_py
    src_zephyr_trading_admission_controller_py ~~~ src_zephyr_trading_auto_dispatcher_py
    src_zephyr_trading_auto_dispatcher_py ~~~ src_zephyr_trading_conductor_py
    src_zephyr_trading_conductor_py ~~~ src_zephyr_trading_gpu_consensus_scheduler_py
    src_zephyr_trading_gpu_consensus_scheduler_py ~~~ src_zephyr_trading_gpu_monitor_py
    src_zephyr_trading_gpu_monitor_py ~~~ src_zephyr_trading_ide_health_daemon_py
    src_zephyr_trading_ide_health_daemon_py ~~~ src_zephyr_trading_runtime_async_runtime_py
    src_zephyr_trading_runtime_async_runtime_py ~~~ src_zephyr_trading_speed_baseline_checker_py
    src_zephyr_trading_speed_baseline_checker_py ~~~ src_zephyr_trading_trading_contracts_broker_interface_py
    src_zephyr_trading_trading_contracts_broker_interface_py ~~~ src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py
    src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py ~~~ src_zephyr_trading_trading_contracts_execution_execution_rejection_error_py
    src_zephyr_trading_trading_contracts_execution_execution_rejection_error_py ~~~ src_zephyr_trading_trading_contracts_execution_execution_report_py
    src_zephyr_trading_trading_contracts_execution_execution_report_py ~~~ src_zephyr_trading_trading_contracts_execution_fill_py
    src_zephyr_trading_trading_contracts_execution_fill_py ~~~ src_zephyr_trading_trading_contracts_execution_model_serving_request_py
    src_zephyr_trading_trading_contracts_execution_model_serving_request_py ~~~ src_zephyr_trading_trading_contracts_execution_position_py
    src_zephyr_trading_trading_contracts_execution_position_py ~~~ src_zephyr_trading_trading_contracts_factories_py
    src_zephyr_trading_trading_contracts_factories_py ~~~ src_zephyr_trading_trading_contracts_market_instrument_py
    src_zephyr_trading_trading_contracts_market_instrument_py ~~~ src_zephyr_trading_trading_contracts_market_signal_degradation_warning_py
    src_zephyr_trading_trading_contracts_market_signal_degradation_warning_py ~~~ src_zephyr_trading_trading_contracts_portfolio_contracts_money_py
    src_zephyr_trading_trading_contracts_portfolio_contracts_money_py ~~~ src_zephyr_trading_trading_contracts_portfolio_contracts_performance_attribution_report_py
    src_zephyr_trading_trading_contracts_portfolio_contracts_performance_attribution_report_py ~~~ src_zephyr_trading_trading_contracts_portfolio_contracts_strategy_lifecycle_event_py
    src_zephyr_trading_trading_contracts_portfolio_contracts_strategy_lifecycle_event_py ~~~ src_zephyr_trading_trading_contracts_risk_compliance_rule_py
    src_zephyr_trading_trading_contracts_risk_compliance_rule_py ~~~ src_zephyr_trading_trading_contracts_risk_risk_limit_violation_error_py
    src_zephyr_trading_trading_contracts_risk_risk_limit_violation_error_py ~~~ src_zephyr_trading_trading_contracts_risk_risk_validator_protocol_py
    src_zephyr_trading_trading_contracts_risk_risk_validator_protocol_py ~~~ src_zephyr_trading_trading_contracts_risk_trading_kill_switch_py
    src_zephyr_trading_action_dispatcher_annotation_writer_py["(生产态 / production) 注释注解写入器（从 ActionDispatcher._annotate_py_file/_tag_module/_annotate_b...<br/>注释注解写入器（从 ActionDispatcher._annotate_py_file/_tag_module/_annotate_b...<br/>文件: action_dispatcher/_annotation_writer.py"]
    src_zephyr_trading_action_dispatcher_audit_log_writer_py["(生产态 / production) 审计日志写入器（从 ActionDispatcher._write_triage_log 提取）。<br/>审计日志写入器（从 ActionDispatcher._write_triage_log 提取）。<br/>文件: action_dispatcher/_audit_log_writer.py"]
    src_zephyr_trading_action_dispatcher_file_lifecycle_manager_py["(生产态 / production) 文件生命周期管理器（从 ActionDispatcher._create_file / _delete_file / _versio...<br/>文件生命周期管理器（从 ActionDispatcher._create_file / _delete_file / _versio...<br/>文件: action_dispatcher/_file_lifecycle_manager.py"]
    src_zephyr_trading_action_dispatcher_search_replace_engine_py["(生产态 / production) 搜索替换引擎（从 ActionDispatcher._search_replace_file 及两个底层方法提取）。<br/>搜索替换引擎（从 ActionDispatcher._search_replace_file 及两个底层方法提取）。<br/>文件: action_dispatcher/_search_replace_engine.py"]
    src_zephyr_trading_autopilot_py["(生产态 / production) AutoPilot — AI session 自动找活干、认领任务。<br/>AutoPilot — AI session 自动找活干、认领任务。<br/>文件: trading/autopilot.py"]
    src_zephyr_trading_trading_contracts_execution_order_py["(生产态 / production) Re-export wrapper: Order 真源在 zephyr.shared.contracts.order（CTR-004 codegen）<br/>Re-export wrapper: Order 真源在 zephyr.shared.contracts.order（CTR-004 codegen）<br/>文件: execution/order.py"]
    src_zephyr_trading_trading_contracts_risk_risk_dashboard_snapshot_py["(生产态 / production) ==== BEGIN CODGEN:CTR-P1-008 ====<br/>==== BEGIN CODGEN:CTR-P1-008 ====<br/>文件: risk/risk_dashboard_snapshot.py"]
    src_zephyr_trading_trading_contracts_risk_risk_limits_py["(生产态 / production) ==== BEGIN CODGEN:CTR-003 ====<br/>==== BEGIN CODGEN:CTR-003 ====<br/>文件: risk/risk_limits.py"]
    src_zephyr_trading_trading_contracts_risk_risk_metrics_py["(生产态 / production) ==== BEGIN CODGEN:CTR-P1-011 ====<br/>==== BEGIN CODGEN:CTR-P1-011 ====<br/>文件: risk/risk_metrics.py"]
    src_zephyr_trading_verdict_engine_py["(生产态 / production) noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复...<br/>noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复...<br/>文件: trading/verdict_engine.py"]
    src_zephyr_trading_action_dispatcher_annotation_writer_py ~~~ src_zephyr_trading_action_dispatcher_audit_log_writer_py
    src_zephyr_trading_action_dispatcher_audit_log_writer_py ~~~ src_zephyr_trading_action_dispatcher_file_lifecycle_manager_py
    src_zephyr_trading_action_dispatcher_file_lifecycle_manager_py ~~~ src_zephyr_trading_action_dispatcher_search_replace_engine_py
    src_zephyr_trading_action_dispatcher_search_replace_engine_py ~~~ src_zephyr_trading_autopilot_py
    src_zephyr_trading_autopilot_py ~~~ src_zephyr_trading_trading_contracts_execution_order_py
    src_zephyr_trading_trading_contracts_execution_order_py ~~~ src_zephyr_trading_trading_contracts_risk_risk_dashboard_snapshot_py
    src_zephyr_trading_trading_contracts_risk_risk_dashboard_snapshot_py ~~~ src_zephyr_trading_trading_contracts_risk_risk_limits_py
    src_zephyr_trading_trading_contracts_risk_risk_limits_py ~~~ src_zephyr_trading_trading_contracts_risk_risk_metrics_py
    src_zephyr_trading_trading_contracts_risk_risk_metrics_py ~~~ src_zephyr_trading_verdict_engine_py
    src_zephyr_trading_protection_index_py["(生产态 / production)<br/>文件: trading/protection_index.py"]
    src_zephyr_trading_conductor_py -->|导入依赖 / import_depends| src_zephyr_trading_autopilot_py
    src_zephyr_trading_gpu_consensus_scheduler_py -->|导入依赖 / import_depends| src_zephyr_trading_verdict_engine_py
    src_zephyr_trading_protection_index_py -->|导入依赖 / import_depends| src_zephyr_trading_verdict_engine_py
    src_zephyr_trading_verdict_engine_py -->|导入依赖 / import_depends| src_zephyr_trading_protection_index_py
    src_zephyr_trading_action_dispatcher_init_py -->|导入依赖 / import_depends| src_zephyr_trading_action_dispatcher_annotation_writer_py
    src_zephyr_trading_action_dispatcher_init_py -->|导入依赖 / import_depends| src_zephyr_trading_action_dispatcher_audit_log_writer_py
    src_zephyr_trading_action_dispatcher_init_py -->|导入依赖 / import_depends| src_zephyr_trading_action_dispatcher_search_replace_engine_py
    src_zephyr_trading_action_dispatcher_init_py -->|导入依赖 / import_depends| src_zephyr_trading_action_dispatcher_file_lifecycle_manager_py
    src_zephyr_trading_trading_contracts_factories_py -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_order_py
    src_zephyr_trading_trading_contracts_factories_py -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_dashboard_snapshot_py
    src_zephyr_trading_trading_contracts_factories_py -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_limits_py
    src_zephyr_trading_trading_contracts_factories_py -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_metrics_py
    D_GOVERNANCE["(生产态 / production) 生命周期管理 / Lifecycle Management<br/>生命周期管理，负责蓝图/模块/任务的声明周期管理和元数据治理<br/>跨域节点 / cross-domain"]
    src_zephyr_trading_autopilot_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_ORCHESTRATOR["(生产态 / production) 代理编排器 / Agent Orchestrator<br/>代理编排器，负责 Agent 任务全生命周期：任务入队、调度、沙箱执行、幻觉检测和收尾归档<br/>跨域节点 / cross-domain"]
    src_zephyr_trading_auto_dispatcher_py -->|导入依赖 / import_depends| D_ORCHESTRATOR
    D_GOV_AUDIT["(生产态 / production) 审计追踪 / Audit Trail<br/>审计追踪，负责变更审计追踪和操作日志管理<br/>跨域节点 / cross-domain"]
    src_zephyr_trading_verdict_engine_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    D_INFRASTRUCTURE["(生产态 / production) 跨层契约基础设施 / Cross-Layer Contract Infrastructure<br/>跨层契约基础设施，负责跨层契约定义、共享契约管理和契约校验<br/>跨域节点 / cross-domain"]
    src_zephyr_trading_trading_contracts_broker_interface_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    D_SHARED["(生产态 / production) 共享服务 / Shared Services<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>跨域节点 / cross-domain"]
    src_zephyr_trading_ide_health_daemon_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_gpu_monitor_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_ide_health_daemon_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_speed_baseline_checker_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_action_dispatcher_init_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_trading_contracts_execution_execution_report_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_trading_action_dispatcher_init_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_trading_contracts_risk_risk_limits_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_trading_auto_dispatcher_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_autopilot_py -->|导入依赖 / import_depends| D_SHARED
    D_INFRA_RUNTIME["(生产态 / production) 运行时集成 / Runtime Integration<br/>运行时集成，负责组件生命周期编排、启动钩子和运行时上下文管理<br/>跨域节点 / cross-domain"]
    src_zephyr_trading_action_dispatcher_annotation_writer_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    D_EX_CORE["(设计态 / design) 执行核心 / Execution Core<br/>执行核心，负责订单执行引擎、执行策略和执行管理<br/>跨域节点 / cross-domain"]
    D_EX_CORE -.->|contract / contract| src_zephyr_trading_trading_contracts_broker_interface_py
    D_RISK["(生产态 / production) 风控 / Risk Control<br/>风控，负责风险指标计算、风险限额管理和风险预警<br/>跨域节点 / cross-domain"]
    D_RISK -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_limit_violation_error_py
    D_FUNDAMENTAL_SIGNAL["(生产态 / production) 基本面信号 / Fundamental Signal<br/>基本面信号，负责基于财务数据的基本面信号生成<br/>跨域节点 / cross-domain"]
    D_FUNDAMENTAL_SIGNAL -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py
    D_RISK -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_dashboard_snapshot_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_trading_ide_health_daemon_py
    D_EX_CORE -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_broker_interface_py
    D_ML_TRAIN["(生产态 / production) 训练 / Training<br/>训练，负责模型训练、特征工程和模型评估<br/>跨域节点 / cross-domain"]
    D_ML_TRAIN -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_model_serving_request_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_broker_interface_py
    D_FUNDAMENTAL_SIGNAL -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py
    D_ML_TRAIN -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_model_serving_request_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_trading_gpu_monitor_py
    D_FUNDAMENTAL_SIGNAL -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py
    D_EX_CORE -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_position_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_action_dispatcher_init_py,src_zephyr_trading_action_dispatcher_annotation_writer_py,src_zephyr_trading_action_dispatcher_audit_log_writer_py,src_zephyr_trading_action_dispatcher_file_lifecycle_manager_py,src_zephyr_trading_action_dispatcher_search_replace_engine_py,src_zephyr_trading_admission_controller_py,src_zephyr_trading_auto_dispatcher_py,src_zephyr_trading_autopilot_py,src_zephyr_trading_conductor_py,src_zephyr_trading_gpu_consensus_scheduler_py,src_zephyr_trading_gpu_monitor_py,src_zephyr_trading_ide_health_daemon_py,src_zephyr_trading_protection_index_py,src_zephyr_trading_runtime_async_runtime_py,src_zephyr_trading_speed_baseline_checker_py,src_zephyr_trading_trading_contracts_broker_interface_py,src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py,src_zephyr_trading_trading_contracts_execution_execution_rejection_error_py,src_zephyr_trading_trading_contracts_execution_execution_report_py,src_zephyr_trading_trading_contracts_execution_fill_py,src_zephyr_trading_trading_contracts_execution_model_serving_request_py,src_zephyr_trading_trading_contracts_execution_order_py,src_zephyr_trading_trading_contracts_execution_position_py,src_zephyr_trading_trading_contracts_factories_py,src_zephyr_trading_trading_contracts_market_instrument_py,src_zephyr_trading_trading_contracts_market_signal_degradation_warning_py,src_zephyr_trading_trading_contracts_portfolio_contracts_money_py,src_zephyr_trading_trading_contracts_portfolio_contracts_performance_attribution_report_py,src_zephyr_trading_trading_contracts_portfolio_contracts_strategy_lifecycle_event_py,src_zephyr_trading_trading_contracts_risk_compliance_rule_py,src_zephyr_trading_trading_contracts_risk_risk_dashboard_snapshot_py,src_zephyr_trading_trading_contracts_risk_risk_limit_violation_error_py,src_zephyr_trading_trading_contracts_risk_risk_limits_py,src_zephyr_trading_trading_contracts_risk_risk_metrics_py,src_zephyr_trading_trading_contracts_risk_risk_validator_protocol_py,src_zephyr_trading_trading_contracts_risk_trading_kill_switch_py,src_zephyr_trading_verdict_engine_py production
    class D_GOVERNANCE,D_ORCHESTRATOR,D_GOV_AUDIT,D_INFRASTRUCTURE,D_SHARED,D_INFRA_RUNTIME,D_RISK,D_FUNDAMENTAL_SIGNAL,D_ML_TRAIN external_prod
    class D_EX_CORE external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | AutoDispatcher — 守护进程内的轻量 PipelineDispatcher (tr... | → | D_GOVERNANCE 生命周期管理: TaskRepository — 任务登记表 CRUD + 状态机（T-1-04） (per... | 导入依赖 / import_depends |
| 2 | AutoPilot — AI session 自动找活干、认领任务。 (trading/a... | → | D_GOVERNANCE 生命周期管理: TaskRepository — 任务登记表 CRUD + 状态机（T-1-04） (per... | 导入依赖 / import_depends |
| 3 | Conductor — AI session 全自动指挥官。 (trading/conductor.py) | → | D_GOVERNANCE 生命周期管理: TaskRepository — 任务登记表 CRUD + 状态机（T-1-04） (per... | 导入依赖 / import_depends |
| 4 | ide_health_daemon.py — TRAE IDE 幽灵窗口守护线程 (tradin... | → | D_GOVERNANCE 生命周期管理: TaskRepository — 任务登记表 CRUD + 状态机（T-1-04） (per... | 导入依赖 / import_depends |
| 5 | noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问... | → | D_GOV_AUDIT 审计追踪: 治本（裁定#18 G2）：本文件原为桩实现——AuditEventType/Fi... | 导入依赖 / import_depends |
| 6 | D_EXECUTION_CORE — BrokerInterface (trading_contracts/br... | → | D_INFRASTRUCTURE 跨层契约基础设施: ==== BEGIN CODGEN:CTR-005 ==== (contracts/fill.py) | 导入依赖 / import_depends |
| 7 | D_EXECUTION_CORE — BrokerInterface (trading_contracts/br... | → | D_INFRASTRUCTURE 跨层契约基础设施: ==== BEGIN CODGEN:CTR-004 ==== (contracts/order.py) | 导入依赖 / import_depends |
| 8 | D_EXECUTION_CORE — BrokerInterface (trading_contracts/br... | → | D_INFRASTRUCTURE 跨层契约基础设施: ==== BEGIN CODGEN:CTR-006 ==== (contracts/position.py) | 导入依赖 / import_depends |
| 9 | ==== BEGIN CODGEN:CTR-ERR-005 ==== (execution/execution_r... | → | D_INFRASTRUCTURE 跨层契约基础设施: ==== BEGIN CODGEN:CTR-TRACE-001 ==== (contracts/trace_con... | 导入依赖 / import_depends |
| 10 | Re-export wrapper: ExecutionReport 真源在 zephyr.shared.c... | → | D_INFRASTRUCTURE 跨层契约基础设施: ==== BEGIN CODGEN:CTR-P1-007 ==== (contracts/execution_re... | 导入依赖 / import_depends |
| 11 | Re-export wrapper: Fill 真源在 zephyr.shared.contracts.fi... | → | D_INFRASTRUCTURE 跨层契约基础设施: ==== BEGIN CODGEN:CTR-005 ==== (contracts/fill.py) | 导入依赖 / import_depends |
| 12 | Re-export wrapper: Order 真源在 zephyr.shared.contracts.o... | → | D_INFRASTRUCTURE 跨层契约基础设施: ==== BEGIN CODGEN:CTR-004 ==== (contracts/order.py) | 导入依赖 / import_depends |
| 13 | Re-export wrapper: PositionSnapshot 真源在 zephyr.shared.... | → | D_INFRASTRUCTURE 跨层契约基础设施: ==== BEGIN CODGEN:CTR-006 ==== (contracts/position.py) | 导入依赖 / import_depends |
| 14 | trading-contracts/factories.py — 交易域数据契约工厂方法 ... | → | D_INFRASTRUCTURE 跨层契约基础设施: ==== BEGIN CODGEN:CTR-002 ==== (contracts/factor_signal.py) | 导入依赖 / import_depends |
| 15 | trading-contracts/factories.py — 交易域数据契约工厂方法 ... | → | D_INFRASTRUCTURE 跨层契约基础设施: ==== BEGIN CODGEN:CTR-P1-015 ==== (contracts/synthesized_... | 导入依赖 / import_depends |
| 16 | ==== BEGIN CODGEN:CTR-ERR-003 ==== (market/signal_degrada... | → | D_INFRASTRUCTURE 跨层契约基础设施: ==== BEGIN CODGEN:CTR-TRACE-001 ==== (contracts/trace_con... | 导入依赖 / import_depends |
| 17 | Re-export shim — 真源已收敛至 zephyr.shared.contracts.pe... | → | D_INFRASTRUCTURE 跨层契约基础设施: ==== BEGIN CODGEN:CTR-P1-009 ==== (contracts/performance_... | 导入依赖 / import_depends |
| 18 | Re-export from shared SSoT — zephyr.shared.contracts.str... | → | D_INFRASTRUCTURE 跨层契约基础设施: ==== BEGIN CODGEN:CTR-P1-006 ==== (contracts/strategy_lif... | 导入依赖 / import_depends |
| 19 | risk/risk_limit_violation_error.py | → | D_INFRASTRUCTURE 跨层契约基础设施: ==== BEGIN CODGEN:CTR-TRACE-001 ==== (contracts/trace_con... | 导入依赖 / import_depends |
| 20 | ==== BEGIN CODGEN:CTR-003 ==== (risk/risk_limits.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: ==== BEGIN CODGEN:CTR-TRACE-001 ==== (contracts/trace_con... | 导入依赖 / import_depends |
| 21 | risk/risk_validator_protocol.py | → | D_INFRASTRUCTURE 跨层契约基础设施: ==== BEGIN CODGEN:CTR-003 ==== (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 22 | 交易运营Action Dispatcher包 / Trading Action Dispatcher P... | → | D_INFRA_RUNTIME 运行时集成: Task Scheduler — 任务调度器。 (queue/task_scheduler.py) | 导入依赖 / import_depends |
| 23 | 注释注解写入器（从 ActionDispatcher._annotate_py_file/_ta... | → | D_INFRA_RUNTIME 运行时集成: ActionDispatcher --- 大脑的"手" v2.0 (Phase 2) (trading/a... | 导入依赖 / import_depends |
| 24 | 审计日志写入器（从 ActionDispatcher._write_triage_log 提... | → | D_INFRA_RUNTIME 运行时集成: ActionDispatcher --- 大脑的"手" v2.0 (Phase 2) (trading/a... | 导入依赖 / import_depends |
| 25 | 文件生命周期管理器（从 ActionDispatcher._create_file / _d... | → | D_INFRA_RUNTIME 运行时集成: ActionDispatcher --- 大脑的"手" v2.0 (Phase 2) (trading/a... | 导入依赖 / import_depends |
| 26 | 搜索替换引擎（从 ActionDispatcher._search_replace_file 及... | → | D_INFRA_RUNTIME 运行时集成: ActionDispatcher --- 大脑的"手" v2.0 (Phase 2) (trading/a... | 导入依赖 / import_depends |
| 27 | ide_health_daemon.py — TRAE IDE 幽灵窗口守护线程 (tradin... | → | D_INFRA_RUNTIME 运行时集成: daemon_registry.py - unified daemon thread registry + res... | 导入依赖 / import_depends |
| 28 | noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问... | → | D_INTEGRATION 管线路由: LocalModelScheduler — L2 本地模型 24/7 调度循环 (local_m... | 导入依赖 / import_depends |
| 29 | AutoDispatcher — 守护进程内的轻量 PipelineDispatcher (tr... | → | D_ORCHESTRATOR 代理编排器: ActiveTaskQueue — 后台任务轮询与自动分发 (core/task_queu... | 导入依赖 / import_depends |
| 30 | AutoDispatcher — 守护进程内的轻量 PipelineDispatcher (tr... | → | D_ORCHESTRATOR 代理编排器: Orc->CE 上下文桥接 — request_context() 生产者 (execution... | 导入依赖 / import_depends |
| 31 | AutoDispatcher — 守护进程内的轻量 PipelineDispatcher (tr... | → | D_ORCHESTRATOR 代理编排器: Orc->Script 脚本执行器 — run_audit() 生产者 (execution/s... | 导入依赖 / import_depends |
| 32 | 交易运营Action Dispatcher包 / Trading Action Dispatcher P... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 33 | 交易运营Action Dispatcher包 / Trading Action Dispatcher P... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 34 | 交易运营Action Dispatcher包 / Trading Action Dispatcher P... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 35 | 交易运营Action Dispatcher包 / Trading Action Dispatcher P... | → | D_SHARED 共享服务: task_types — 任务系统核心类型 re-export 层 (schema/task_... | 导入依赖 / import_depends |
| 36 | AutoDispatcher — 守护进程内的轻量 PipelineDispatcher (tr... | → | D_SHARED 共享服务: TaskRepositoryProtocol — TaskRepository 的 Protocol 接口... | 导入依赖 / import_depends |
| 37 | AutoDispatcher — 守护进程内的轻量 PipelineDispatcher (tr... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export（Single S... | 导入依赖 / import_depends |
| 38 | AutoPilot — AI session 自动找活干、认领任务。 (trading/a... | → | D_SHARED 共享服务: TaskRepositoryProtocol — TaskRepository 的 Protocol 接口... | 导入依赖 / import_depends |
| 39 | AutoPilot — AI session 自动找活干、认领任务。 (trading/a... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (shared/event_bu... | 导入依赖 / import_depends |
| 40 | AutoPilot — AI session 自动找活干、认领任务。 (trading/a... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export（Single S... | 导入依赖 / import_depends |
| 41 | AutoPilot — AI session 自动找活干、认领任务。 (trading/a... | → | D_SHARED 共享服务: ZephyrAlpha 任务系统核心数据模型 (foundation/models.py) | 导入依赖 / import_depends |
| 42 | Conductor — AI session 全自动指挥官。 (trading/conductor.py) | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export（Single S... | 导入依赖 / import_depends |
| 43 | Conductor — AI session 全自动指挥官。 (trading/conductor.py) | → | D_SHARED 共享服务: ZephyrAlpha 任务系统核心数据模型 (foundation/models.py) | 导入依赖 / import_depends |
| 44 | noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export（Single S... | 导入依赖 / import_depends |
| 45 | gpu_monitor.py — NVIDIA GPU 状态采集器 (trading/gpu_moni... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 46 | ide_health_daemon.py — TRAE IDE 幽灵窗口守护线程 (tradin... | → | D_SHARED 共享服务: TaskRepositoryProtocol — TaskRepository 的 Protocol 接口... | 导入依赖 / import_depends |
| 47 | ide_health_daemon.py — TRAE IDE 幽灵窗口守护线程 (tradin... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (shared/event_bu... | 导入依赖 / import_depends |
| 48 | ide_health_daemon.py — TRAE IDE 幽灵窗口守护线程 (tradin... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export（Single S... | 导入依赖 / import_depends |
| 49 | ide_health_daemon.py — TRAE IDE 幽灵窗口守护线程 (tradin... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 50 | ide_health_daemon.py — TRAE IDE 幽灵窗口守护线程 (tradin... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |
| 51 | 事件循环引导 + run_in_executor 桥接。 (runtime/async_runt... | → | D_SHARED 共享服务: async_utils.py — async/sync 边界桥接（5.12.8 修复） (uti... | 导入依赖 / import_depends |
| 52 | Return True if the process belongs to this project, is a ... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 53 | Re-export wrapper: Order 真源在 zephyr.shared.contracts.o... | → | D_SHARED 共享服务: OrderSide/OrderStatus/OrderType — 交易枚举真源 (5.152 #1... | 导入依赖 / import_depends |
| 54 | 过渡兼容层（DEPRECATED）—— Money 契约 canonical 真源已... | → | D_SHARED 共享服务: 查询货币精度（小数位数）。 (portfolio/money.py) | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_EX_CORE 执行核心: 执行核心适配器包 / Ex Core Adapters Package (adapters/__i... | → | D_EXECUTION_CORE — BrokerInterface (trading_contracts/br... | 导入依赖 / import_depends |
| 2 | D_EX_CORE 执行核心: MiniQMT 实盘券商适配器（对接 xttrader，A股实盘交易） (ada... | → | D_EXECUTION_CORE — BrokerInterface (trading_contracts/br... | 导入依赖 / import_depends |
| 3 | D_EX_CORE 执行核心: MiniQMT 实盘券商适配器（对接 xttrader，A股实盘交易） (ada... | → | Re-export wrapper: Fill 真源在 zephyr.shared.contracts.fi... | 导入依赖 / import_depends |
| 4 | D_EX_CORE 执行核心: MiniQMT 实盘券商适配器（对接 xttrader，A股实盘交易） (ada... | → | Re-export wrapper: Order 真源在 zephyr.shared.contracts.o... | 导入依赖 / import_depends |
| 5 | D_EX_CORE 执行核心: MiniQMT 实盘券商适配器（对接 xttrader，A股实盘交易） (ada... | → | Re-export wrapper: PositionSnapshot 真源在 zephyr.shared.... | 导入依赖 / import_depends |
| 6 | D_EX_CORE 执行核心: D_EXECUTION_CORE — Order Manager (ex_core/order_manager.py) | → | D_EXECUTION_CORE — BrokerInterface (trading_contracts/br... | 导入依赖 / import_depends |
| 7 | D_EX_CORE 执行核心: D_EXECUTION_CORE — TradingSession 盘中实时调仓编排器 (ex... | → | D_EXECUTION_CORE — BrokerInterface (trading_contracts/br... | contract / contract |
| 8 | D_FRONTEND 前端: trade_panel · 实盘交易面板组件（v3.0.0 Panel+HoloViz 重... | → | Re-export wrapper: Order 真源在 zephyr.shared.contracts.o... | 导入依赖 / import_depends |
| 9 | D_FUNDAMENTAL_SIGNAL 基本面信号: D_FUNDAMENTAL_SIGNAL — CapitalAllocationResult re-export... | → | ==== BEGIN CODGEN:CTR-P1-003 ==== (execution/capital_allo... | 导入依赖 / import_depends |
| 10 | D_FUNDAMENTAL_SIGNAL 基本面信号: D_SIGNAL — Signal Generation Layer (gen/aggregator_base.py) | → | ==== BEGIN CODGEN:CTR-P1-003 ==== (execution/capital_allo... | 导入依赖 / import_depends |
| 11 | D_FUNDAMENTAL_SIGNAL 基本面信号: D_SIGNAL — Signal Generation Layer (gen/aggregator_base.py) | → | ==== BEGIN CODGEN:CTR-ERR-003 ==== (market/signal_degrada... | 导入依赖 / import_depends |
| 12 | D_FUNDAMENTAL_SIGNAL 基本面信号: D_FUNDAMENTAL_SIGNAL — Capital Allocator（兼容导出） (st... | → | ==== BEGIN CODGEN:CTR-P1-003 ==== (execution/capital_allo... | 导入依赖 / import_depends |
| 13 | D_FUNDAMENTAL_SIGNAL 基本面信号: D_SIGNAL — Default Capital Allocator (implementations/de... | → | ==== BEGIN CODGEN:CTR-P1-003 ==== (execution/capital_allo... | 导入依赖 / import_depends |
| 14 | D_GOVERNANCE 生命周期管理: D_EXECUTION_CORE — Simulation Broker Adapter (adapters/s... | → | D_EXECUTION_CORE — BrokerInterface (trading_contracts/br... | 导入依赖 / import_depends |
| 15 | D_INFRA_RUNTIME 运行时集成: 从 TaskRepository 查询 task 的 source_blueprint，失败返回... | → | ide_health_daemon.py — TRAE IDE 幽灵窗口守护线程 (tradin... | 导入依赖 / import_depends |
| 16 | D_INFRA_RUNTIME 运行时集成: resource_optimization.py - MAPE-K autonomic resource opti... | → | gpu_monitor.py — NVIDIA GPU 状态采集器 (trading/gpu_moni... | 导入依赖 / import_depends |
| 17 | D_INFRA_RUNTIME 运行时集成: resource_optimization.py - MAPE-K autonomic resource opti... | → | ide_health_daemon.py — TRAE IDE 幽灵窗口守护线程 (tradin... | 导入依赖 / import_depends |
| 18 | D_INTEGRATION 管线路由: behavioral_admission/admission_response.py | → | 5.171 修复：admit(event: Any) Any 滥用——定义 VerdictEve... | 导入依赖 / import_depends |
| 19 | D_INTELLIGENCE 上下文管理: D_ML_TRAIN — Default Inference Engine (implementations/d... | → | ==== BEGIN CODGEN:CTR-P1-004 ==== (execution/model_servin... | 导入依赖 / import_depends |
| 20 | D_ML_TRAIN 训练: D_ML_TRAIN — Default Inference Engine (implementations/d... | → | ==== BEGIN CODGEN:CTR-P1-004 ==== (execution/model_servin... | 导入依赖 / import_depends |
| 21 | D_ML_TRAIN 训练: D_ML_TRAIN — ML Inference Base (ml_train/inference_base.py) | → | ==== BEGIN CODGEN:CTR-P1-004 ==== (execution/model_servin... | 导入依赖 / import_depends |
| 22 | D_RISK 风控: ZephyrAlpha — D_RISK Risk Management Layer — 风控管理器... | → | ==== BEGIN CODGEN:CTR-P1-008 ==== (risk/risk_dashboard_sn... | 导入依赖 / import_depends |
| 23 | D_RISK 风控: ZephyrAlpha — D_RISK Risk Management Layer — 风控管理器... | → | risk/risk_limit_violation_error.py | 导入依赖 / import_depends |
| 24 | D_RISK 风控: ZephyrAlpha — D_RISK Risk Management Layer — 风控管理器... | → | ==== BEGIN CODGEN:CTR-P1-011 ==== (risk/risk_metrics.py) | 导入依赖 / import_depends |
| 25 | D_SIGQC 信号质量控制: D_SIGQC — Signal Quality Degradation Monitor Base (signa... | → | ==== BEGIN CODGEN:CTR-ERR-003 ==== (market/signal_degrada... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 16 个外部域直接连接（出边 59 条 + 入边 28 条 = 87 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_TRADING["D_TRADING<br/>交易运营"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE<br/>跨层契约基础设施"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_ORCHESTRATOR["D_ORCHESTRATOR<br/>代理编排器"]
    D_DATA["D_DATA<br/>数据接入层"]
    D_EX_CORE["D_EX_CORE<br/>执行核心"]
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_POSITION["D_POSITION<br/>仓位管理"]
    D_FUNDAMENTAL_SIGNAL["D_FUNDAMENTAL_SIGNAL<br/>基本面信号"]
    D_RISK["D_RISK<br/>风控"]
    D_ML_TRAIN["D_ML_TRAIN<br/>训练"]
    D_SIGQC["D_SIGQC<br/>信号质量控制"]
    D_FRONTEND["D_FRONTEND<br/>前端"]
    D_INTELLIGENCE["D_INTELLIGENCE<br/>上下文管理"]
    D_TRADING -->|23条 导入依赖 / import_depends| D_SHARED
    D_TRADING -->|16条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_TRADING -->|6条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_TRADING -->|4条 导入依赖 / import_depends| D_GOVERNANCE
    D_TRADING -->|3条 导入依赖 / import_depends| D_ORCHESTRATOR
    D_TRADING -->|2条 runtime / runtime| D_DATA
    D_TRADING -->|2条 import / import, runtime / runtime| D_EX_CORE
    D_TRADING -->|1条 导入依赖 / import_depends| D_INTEGRATION
    D_TRADING -->|1条 导入依赖 / import_depends| D_GOV_AUDIT
    D_TRADING -->|1条 导入依赖 / import_depends| D_POSITION
    D_EX_CORE -->|9条 contract / contract, 导入依赖 / import_depends| D_TRADING
    D_FUNDAMENTAL_SIGNAL -->|5条 导入依赖 / import_depends| D_TRADING
    D_RISK -->|4条 import / import, 导入依赖 / import_depends| D_TRADING
    D_INFRA_RUNTIME -->|3条 导入依赖 / import_depends| D_TRADING
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
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
