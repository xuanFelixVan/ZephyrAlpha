---
doc_type: architecture_view
title: D_INFRASTRUCTURE 跨层契约基础设施架构文档
version: "1.0"
status: active
date: 2026-08-03
owner: auto-generator
ttl: permanent
---

# 02_d_infrastructure / 跨层契约基础设施域 / Cross-Layer Contract Infrastructure

> **功能简介 / Overview**: 跨层契约基础设施，负责跨层契约定义、共享契约管理和契约校验

> **文档作用 / Purpose**: 展示 跨层契约基础设施（D_INFRASTRUCTURE）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/02_d_infrastructure.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 02 | Number | 02 |
| 域ID | D_INFRASTRUCTURE | Domain ID | D_INFRASTRUCTURE |
| 域名称 | 跨层契约基础设施 | Domain Name | Cross-Layer Contract Infrastructure |
| 层级 | L0 基础设施层 | Layer | L0 Infrastructure |
| 模块数 | 26 | Module Count | 26 |
| 域内依赖 | 2 | Internal Dependencies | 2 |
| 跨域入边 | 102 | Cross-domain Incoming | 102 |
| 跨域出边 | 11 | Cross-domain Outgoing | 11 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 26 | Production Modules | 26 |
| 容量 | 26/150 (正常) | Capacity | 26/150 (正常) |
| 描述 | 跨层契约数据类(CTR-001 NormalizedMarketData 等) | Description | 跨层契约数据类(CTR-001 NormalizedMarketData 等) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 26 个模块（生产态 26 + 设计态 0），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    scripts_backup_backup_reconciler_py["备份协调器<br/>灾备备份系统事件触发器（post-commit reconciler）<br/>backup_reconciler<br/>文件: backup/backup_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_config_init_py["infrastructure/config 包入口<br/>配置加载与环境管理；跨平面共享配置<br/>（risk_params.yaml 等），自身属 Warm<br/>文件: config/__init__.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_capital_allocation_result_py["资本分配结果<br/>资本allocation结果，contracts的结果，封装操作结<br/>果的数据结构。<br/>capital_allocation_result<br/>文件: contracts/capital_allocation_result.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_compliance_rule_py["合规规则<br/>contracts的核心类，封装ComplianceRule相关逻辑<br/>compliance_rule<br/>文件: contracts/compliance_rule.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_execution_report_py["执行报告<br/>contracts的报告器，汇总数据生成报告（execution<br/>report）<br/>execution_report<br/>文件: contracts/execution_report.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_experiment_result_py["实验结果<br/>contracts的结果，封装操作结果的数据结构<br/>experiment_result<br/>文件: contracts/experiment_result.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_factor_monitor_report_py["因子监控报告<br/>contracts的监控器，持续监视某项指标，异常时上报<br/>factor_monitor_report<br/>文件: contracts/factor_monitor_report.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_factor_signal_py["因子信号<br/>contracts的核心类，封装FactorSignal相关逻辑<br/>factor_signal<br/>文件: contracts/factor_signal.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_fill_py["成交<br/>contracts的核心类，封装成交相关逻辑<br/>fill<br/>文件: contracts/fill.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_macro_factor_signal_py["macro因子信号<br/>contracts的核心类，封装MacroFactorSignal相关逻辑<br/>macro_factor_signal<br/>文件: contracts/macro_factor_signal.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_market_data_py["市场数据<br/>contracts的核心类，封装NormalizedMarketData相关<br/>逻辑<br/>market_data<br/>文件: contracts/market_data.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_model_serving_request_py["模型服务请求<br/>contracts的模型，定义数据结构和字段（model<br/>serving request）<br/>model_serving_request<br/>文件: contracts/model_serving_request.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_model_serving_response_py["模型服务响应<br/>contracts的模型，定义数据结构和字段（model<br/>serving response）<br/>model_serving_response<br/>文件: contracts/model_serving_response.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_order_py["订单<br/>contracts的核心类，封装订单相关逻辑<br/>order<br/>文件: contracts/order.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_performance_attribution_report_py["绩效attribution报告<br/>contracts的报告器，汇总数据生成报告<br/>（performance attribution report）<br/>performance_attribution_report<br/>文件: contracts<br/>/performance_attribution_report.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_position_py["持仓<br/>contracts的核心类，封装PositionSnapshot相关逻辑<br/>文件: contracts/position.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_risk_dashboard_snapshot_py["风险仪表盘快照<br/>contracts的核心类，封装RiskDashboardSnapshot相关<br/>逻辑<br/>risk_dashboard_snapshot<br/>文件: contracts/risk_dashboard_snapshot.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_risk_metrics_py["风险指标<br/>contracts的报告器，汇总数据生成报告（risk<br/>metrics）<br/>risk_metrics<br/>文件: contracts/risk_metrics.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_strategy_lifecycle_event_py["策略生命周期事件<br/>contracts的事件，定义和分发事件<br/>strategy_lifecycle_event<br/>文件: contracts/strategy_lifecycle_event.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_synthesized_signal_py["synthesized信号<br/>contracts的核心类，封装SynthesizedSignal相关逻辑<br/>synthesized_signal<br/>文件: contracts/synthesized_signal.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_system_configuration_py["系统配置<br/>contracts的配置，管理配置项的读取和校验（system<br/>configuration）<br/>system_configuration<br/>文件: contracts/system_configuration.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_target_portfolio_py["目标组合契约<br/>组合优化器输出的不可变快照，代表再平衡决策产生的<br/>目标权重及漂移信息，供执行、持仓、报告域消费<br/>TargetPortfolio<br/>文件: contracts/target_portfolio.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_telemetry_emitter_py["遥测发射器<br/>遥测emitter，contracts的核心类，封装TelemetryEmi<br/>tter相关逻辑。<br/>telemetry_emitter<br/>文件: contracts/telemetry_emitter.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_trace_context_py["追踪上下文<br/>contracts的核心类，封装TraceContext相关逻辑<br/>trace_context<br/>文件: contracts/trace_context.py<br/>(生产态 / production)"]
    scripts_backup_backup_reconciler_py ~~~ src_zephyr_infrastructure_config_init_py
    src_zephyr_infrastructure_config_init_py ~~~ src_zephyr_shared_contracts_capital_allocation_result_py
    src_zephyr_shared_contracts_capital_allocation_result_py ~~~ src_zephyr_shared_contracts_compliance_rule_py
    src_zephyr_shared_contracts_compliance_rule_py ~~~ src_zephyr_shared_contracts_execution_report_py
    src_zephyr_shared_contracts_execution_report_py ~~~ src_zephyr_shared_contracts_experiment_result_py
    src_zephyr_shared_contracts_experiment_result_py ~~~ src_zephyr_shared_contracts_factor_monitor_report_py
    src_zephyr_shared_contracts_factor_monitor_report_py ~~~ src_zephyr_shared_contracts_factor_signal_py
    src_zephyr_shared_contracts_factor_signal_py ~~~ src_zephyr_shared_contracts_fill_py
    src_zephyr_shared_contracts_fill_py ~~~ src_zephyr_shared_contracts_macro_factor_signal_py
    src_zephyr_shared_contracts_macro_factor_signal_py ~~~ src_zephyr_shared_contracts_market_data_py
    src_zephyr_shared_contracts_market_data_py ~~~ src_zephyr_shared_contracts_model_serving_request_py
    src_zephyr_shared_contracts_model_serving_request_py ~~~ src_zephyr_shared_contracts_model_serving_response_py
    src_zephyr_shared_contracts_model_serving_response_py ~~~ src_zephyr_shared_contracts_order_py
    src_zephyr_shared_contracts_order_py ~~~ src_zephyr_shared_contracts_performance_attribution_report_py
    src_zephyr_shared_contracts_performance_attribution_report_py ~~~ src_zephyr_shared_contracts_position_py
    src_zephyr_shared_contracts_position_py ~~~ src_zephyr_shared_contracts_risk_dashboard_snapshot_py
    src_zephyr_shared_contracts_risk_dashboard_snapshot_py ~~~ src_zephyr_shared_contracts_risk_metrics_py
    src_zephyr_shared_contracts_risk_metrics_py ~~~ src_zephyr_shared_contracts_strategy_lifecycle_event_py
    src_zephyr_shared_contracts_strategy_lifecycle_event_py ~~~ src_zephyr_shared_contracts_synthesized_signal_py
    src_zephyr_shared_contracts_synthesized_signal_py ~~~ src_zephyr_shared_contracts_system_configuration_py
    src_zephyr_shared_contracts_system_configuration_py ~~~ src_zephyr_shared_contracts_target_portfolio_py
    src_zephyr_shared_contracts_target_portfolio_py ~~~ src_zephyr_shared_contracts_telemetry_emitter_py
    src_zephyr_shared_contracts_telemetry_emitter_py ~~~ src_zephyr_shared_contracts_trace_context_py
    src_zephyr_infrastructure_config_app_config_py["应用配置<br/>数据类与加载/热重载逻辑<br/>app_config<br/>文件: config/app_config.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_risk_limits_py["风险limits<br/>contracts的核心类，封装RiskLimits相关逻辑<br/>risk_limits<br/>文件: contracts/risk_limits.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_config_app_config_py ~~~ src_zephyr_shared_contracts_risk_limits_py
    src_zephyr_infrastructure_config_init_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_config_app_config_py
    src_zephyr_shared_contracts_target_portfolio_py -->|导入依赖 / import_depends| src_zephyr_shared_contracts_risk_limits_py
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_target_portfolio_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_shared_contracts_synthesized_signal_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_shared_contracts_market_data_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_AUDIT["审计追踪<br/>审计追踪，负责变更审计追踪和操作日志管理<br/>Audit Trail<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    scripts_backup_backup_reconciler_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    src_zephyr_shared_contracts_risk_limits_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_shared_contracts_experiment_result_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_shared_contracts_position_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_shared_contracts_factor_signal_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_shared_contracts_fill_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_shared_contracts_order_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_shared_contracts_order_py -->|导入依赖 / import_depends| D_SHARED
    D_PF_CORE["组合核心<br/>组合核心，负责投资组合构建、持仓管理和组合优化<br/>Portfolio Core<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_PF_CORE -->|contract / contract| src_zephyr_shared_contracts_strategy_lifecycle_event_py
    D_PF_CORE -->|contract / contract| src_zephyr_shared_contracts_target_portfolio_py
    D_EX_CORE["执行核心<br/>执行核心，负责订单执行引擎、执行策略和执行管理<br/>Execution Core<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_EX_CORE -->|导入依赖 / import_depends| src_zephyr_shared_contracts_position_py
    D_EX_CORE -->|导入依赖 / import_depends| src_zephyr_shared_contracts_order_py
    D_TRADING["交易运营<br/>交易运营，负责交易生命周期管理、订单状态和成交处<br/>理<br/>Trading Operations<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_TRADING -->|测试依赖 / test_depends| src_zephyr_shared_contracts_fill_py
    D_EX_CORE -->|导入依赖 / import_depends| src_zephyr_shared_contracts_position_py
    D_MKT_DATA["行情数据<br/>行情数据，负责市场行情数据的采集、分发和订阅管理<br/>Market Data<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_MKT_DATA -->|测试依赖 / test_depends| src_zephyr_shared_contracts_market_data_py
    D_PF_CORE -->|导入依赖 / import_depends| src_zephyr_shared_contracts_risk_limits_py
    D_EX_CORE -->|导入依赖 / import_depends| src_zephyr_shared_contracts_order_py
    D_EX_CORE -->|导入依赖 / import_depends| src_zephyr_shared_contracts_fill_py
    D_PF_CORE -->|导入依赖 / import_depends| src_zephyr_shared_contracts_target_portfolio_py
    D_PF_CORE -->|导入依赖 / import_depends| src_zephyr_shared_contracts_strategy_lifecycle_event_py
    D_PF_CORE -->|导入依赖 / import_depends| src_zephyr_shared_contracts_performance_attribution_report_py
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_shared_contracts_fill_py
    D_MKT_DATA -->|导入依赖 / import_depends| src_zephyr_shared_contracts_market_data_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class scripts_backup_backup_reconciler_py,src_zephyr_infrastructure_config_init_py,src_zephyr_infrastructure_config_app_config_py,src_zephyr_shared_contracts_capital_allocation_result_py,src_zephyr_shared_contracts_compliance_rule_py,src_zephyr_shared_contracts_execution_report_py,src_zephyr_shared_contracts_experiment_result_py,src_zephyr_shared_contracts_factor_monitor_report_py,src_zephyr_shared_contracts_factor_signal_py,src_zephyr_shared_contracts_fill_py,src_zephyr_shared_contracts_macro_factor_signal_py,src_zephyr_shared_contracts_market_data_py,src_zephyr_shared_contracts_model_serving_request_py,src_zephyr_shared_contracts_model_serving_response_py,src_zephyr_shared_contracts_order_py,src_zephyr_shared_contracts_performance_attribution_report_py,src_zephyr_shared_contracts_position_py,src_zephyr_shared_contracts_risk_dashboard_snapshot_py,src_zephyr_shared_contracts_risk_limits_py,src_zephyr_shared_contracts_risk_metrics_py,src_zephyr_shared_contracts_strategy_lifecycle_event_py,src_zephyr_shared_contracts_synthesized_signal_py,src_zephyr_shared_contracts_system_configuration_py,src_zephyr_shared_contracts_target_portfolio_py,src_zephyr_shared_contracts_telemetry_emitter_py,src_zephyr_shared_contracts_trace_context_py production
    class D_SHARED,D_GOV_AUDIT,D_PF_CORE,D_EX_CORE,D_TRADING,D_MKT_DATA external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 26 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    scripts_backup_backup_reconciler_py["备份协调器<br/>灾备备份系统事件触发器（post-commit reconciler）<br/>backup_reconciler<br/>文件: backup/backup_reconciler.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_config_init_py["infrastructure/config 包入口<br/>配置加载与环境管理；跨平面共享配置<br/>（risk_params.yaml 等），自身属 Warm<br/>文件: config/__init__.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_capital_allocation_result_py["资本分配结果<br/>资本allocation结果，contracts的结果，封装操作结<br/>果的数据结构。<br/>capital_allocation_result<br/>文件: contracts/capital_allocation_result.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_compliance_rule_py["合规规则<br/>contracts的核心类，封装ComplianceRule相关逻辑<br/>compliance_rule<br/>文件: contracts/compliance_rule.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_execution_report_py["执行报告<br/>contracts的报告器，汇总数据生成报告（execution<br/>report）<br/>execution_report<br/>文件: contracts/execution_report.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_experiment_result_py["实验结果<br/>contracts的结果，封装操作结果的数据结构<br/>experiment_result<br/>文件: contracts/experiment_result.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_factor_monitor_report_py["因子监控报告<br/>contracts的监控器，持续监视某项指标，异常时上报<br/>factor_monitor_report<br/>文件: contracts/factor_monitor_report.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_factor_signal_py["因子信号<br/>contracts的核心类，封装FactorSignal相关逻辑<br/>factor_signal<br/>文件: contracts/factor_signal.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_fill_py["成交<br/>contracts的核心类，封装成交相关逻辑<br/>fill<br/>文件: contracts/fill.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_macro_factor_signal_py["macro因子信号<br/>contracts的核心类，封装MacroFactorSignal相关逻辑<br/>macro_factor_signal<br/>文件: contracts/macro_factor_signal.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_market_data_py["市场数据<br/>contracts的核心类，封装NormalizedMarketData相关<br/>逻辑<br/>market_data<br/>文件: contracts/market_data.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_model_serving_request_py["模型服务请求<br/>contracts的模型，定义数据结构和字段（model<br/>serving request）<br/>model_serving_request<br/>文件: contracts/model_serving_request.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_model_serving_response_py["模型服务响应<br/>contracts的模型，定义数据结构和字段（model<br/>serving response）<br/>model_serving_response<br/>文件: contracts/model_serving_response.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_order_py["订单<br/>contracts的核心类，封装订单相关逻辑<br/>order<br/>文件: contracts/order.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_performance_attribution_report_py["绩效attribution报告<br/>contracts的报告器，汇总数据生成报告<br/>（performance attribution report）<br/>performance_attribution_report<br/>文件: contracts<br/>/performance_attribution_report.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_position_py["持仓<br/>contracts的核心类，封装PositionSnapshot相关逻辑<br/>文件: contracts/position.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_risk_dashboard_snapshot_py["风险仪表盘快照<br/>contracts的核心类，封装RiskDashboardSnapshot相关<br/>逻辑<br/>risk_dashboard_snapshot<br/>文件: contracts/risk_dashboard_snapshot.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_risk_metrics_py["风险指标<br/>contracts的报告器，汇总数据生成报告（risk<br/>metrics）<br/>risk_metrics<br/>文件: contracts/risk_metrics.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_strategy_lifecycle_event_py["策略生命周期事件<br/>contracts的事件，定义和分发事件<br/>strategy_lifecycle_event<br/>文件: contracts/strategy_lifecycle_event.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_synthesized_signal_py["synthesized信号<br/>contracts的核心类，封装SynthesizedSignal相关逻辑<br/>synthesized_signal<br/>文件: contracts/synthesized_signal.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_system_configuration_py["系统配置<br/>contracts的配置，管理配置项的读取和校验（system<br/>configuration）<br/>system_configuration<br/>文件: contracts/system_configuration.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_target_portfolio_py["目标组合契约<br/>组合优化器输出的不可变快照，代表再平衡决策产生的<br/>目标权重及漂移信息，供执行、持仓、报告域消费<br/>TargetPortfolio<br/>文件: contracts/target_portfolio.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_telemetry_emitter_py["遥测发射器<br/>遥测emitter，contracts的核心类，封装TelemetryEmi<br/>tter相关逻辑。<br/>telemetry_emitter<br/>文件: contracts/telemetry_emitter.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_trace_context_py["追踪上下文<br/>contracts的核心类，封装TraceContext相关逻辑<br/>trace_context<br/>文件: contracts/trace_context.py<br/>(生产态 / production)"]
    scripts_backup_backup_reconciler_py ~~~ src_zephyr_infrastructure_config_init_py
    src_zephyr_infrastructure_config_init_py ~~~ src_zephyr_shared_contracts_capital_allocation_result_py
    src_zephyr_shared_contracts_capital_allocation_result_py ~~~ src_zephyr_shared_contracts_compliance_rule_py
    src_zephyr_shared_contracts_compliance_rule_py ~~~ src_zephyr_shared_contracts_execution_report_py
    src_zephyr_shared_contracts_execution_report_py ~~~ src_zephyr_shared_contracts_experiment_result_py
    src_zephyr_shared_contracts_experiment_result_py ~~~ src_zephyr_shared_contracts_factor_monitor_report_py
    src_zephyr_shared_contracts_factor_monitor_report_py ~~~ src_zephyr_shared_contracts_factor_signal_py
    src_zephyr_shared_contracts_factor_signal_py ~~~ src_zephyr_shared_contracts_fill_py
    src_zephyr_shared_contracts_fill_py ~~~ src_zephyr_shared_contracts_macro_factor_signal_py
    src_zephyr_shared_contracts_macro_factor_signal_py ~~~ src_zephyr_shared_contracts_market_data_py
    src_zephyr_shared_contracts_market_data_py ~~~ src_zephyr_shared_contracts_model_serving_request_py
    src_zephyr_shared_contracts_model_serving_request_py ~~~ src_zephyr_shared_contracts_model_serving_response_py
    src_zephyr_shared_contracts_model_serving_response_py ~~~ src_zephyr_shared_contracts_order_py
    src_zephyr_shared_contracts_order_py ~~~ src_zephyr_shared_contracts_performance_attribution_report_py
    src_zephyr_shared_contracts_performance_attribution_report_py ~~~ src_zephyr_shared_contracts_position_py
    src_zephyr_shared_contracts_position_py ~~~ src_zephyr_shared_contracts_risk_dashboard_snapshot_py
    src_zephyr_shared_contracts_risk_dashboard_snapshot_py ~~~ src_zephyr_shared_contracts_risk_metrics_py
    src_zephyr_shared_contracts_risk_metrics_py ~~~ src_zephyr_shared_contracts_strategy_lifecycle_event_py
    src_zephyr_shared_contracts_strategy_lifecycle_event_py ~~~ src_zephyr_shared_contracts_synthesized_signal_py
    src_zephyr_shared_contracts_synthesized_signal_py ~~~ src_zephyr_shared_contracts_system_configuration_py
    src_zephyr_shared_contracts_system_configuration_py ~~~ src_zephyr_shared_contracts_target_portfolio_py
    src_zephyr_shared_contracts_target_portfolio_py ~~~ src_zephyr_shared_contracts_telemetry_emitter_py
    src_zephyr_shared_contracts_telemetry_emitter_py ~~~ src_zephyr_shared_contracts_trace_context_py
    src_zephyr_infrastructure_config_app_config_py["应用配置<br/>数据类与加载/热重载逻辑<br/>app_config<br/>文件: config/app_config.py<br/>(生产态 / production)"]
    src_zephyr_shared_contracts_risk_limits_py["风险limits<br/>contracts的核心类，封装RiskLimits相关逻辑<br/>risk_limits<br/>文件: contracts/risk_limits.py<br/>(生产态 / production)"]
    src_zephyr_infrastructure_config_app_config_py ~~~ src_zephyr_shared_contracts_risk_limits_py
    src_zephyr_infrastructure_config_init_py -->|导入依赖 / import_depends| src_zephyr_infrastructure_config_app_config_py
    src_zephyr_shared_contracts_target_portfolio_py -->|导入依赖 / import_depends| src_zephyr_shared_contracts_risk_limits_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class scripts_backup_backup_reconciler_py,src_zephyr_infrastructure_config_init_py,src_zephyr_infrastructure_config_app_config_py,src_zephyr_shared_contracts_capital_allocation_result_py,src_zephyr_shared_contracts_compliance_rule_py,src_zephyr_shared_contracts_execution_report_py,src_zephyr_shared_contracts_experiment_result_py,src_zephyr_shared_contracts_factor_monitor_report_py,src_zephyr_shared_contracts_factor_signal_py,src_zephyr_shared_contracts_fill_py,src_zephyr_shared_contracts_macro_factor_signal_py,src_zephyr_shared_contracts_market_data_py,src_zephyr_shared_contracts_model_serving_request_py,src_zephyr_shared_contracts_model_serving_response_py,src_zephyr_shared_contracts_order_py,src_zephyr_shared_contracts_performance_attribution_report_py,src_zephyr_shared_contracts_position_py,src_zephyr_shared_contracts_risk_dashboard_snapshot_py,src_zephyr_shared_contracts_risk_limits_py,src_zephyr_shared_contracts_risk_metrics_py,src_zephyr_shared_contracts_strategy_lifecycle_event_py,src_zephyr_shared_contracts_synthesized_signal_py,src_zephyr_shared_contracts_system_configuration_py,src_zephyr_shared_contracts_target_portfolio_py,src_zephyr_shared_contracts_telemetry_emitter_py,src_zephyr_shared_contracts_trace_context_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个），不含跨域外部节点。

> （无模块 / No modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 备份协调器 / backup_reconciler (backup/backup_reconciler.py) | → | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 2 | 实验结果 / experiment_result (contracts/experiment_result... | → | D_SHARED 共享服务: 追踪上下文 / trace_context (core/trace_context.py) | 导入依赖 / import_depends |
| 3 | 因子信号 / factor_signal (contracts/factor_signal.py) | → | D_SHARED 共享服务: 追踪上下文 / trace_context (core/trace_context.py) | 导入依赖 / import_depends |
| 4 | 成交 / fill (contracts/fill.py) | → | D_SHARED 共享服务: 追踪上下文 / trace_context (core/trace_context.py) | 导入依赖 / import_depends |
| 5 | 市场数据 / market_data (contracts/market_data.py) | → | D_SHARED 共享服务: 追踪上下文 / trace_context (core/trace_context.py) | 导入依赖 / import_depends |
| 6 | 订单 / order (contracts/order.py) | → | D_SHARED 共享服务: 追踪上下文 / trace_context (core/trace_context.py) | 导入依赖 / import_depends |
| 7 | 订单 / order (contracts/order.py) | → | D_SHARED 共享服务: 订单枚举 / order_enums (enums/order_enums.py) | 导入依赖 / import_depends |
| 8 | 持仓 / position (contracts/position.py) | → | D_SHARED 共享服务: 追踪上下文 / trace_context (core/trace_context.py) | 导入依赖 / import_depends |
| 9 | 风险limits / risk_limits (contracts/risk_limits.py) | → | D_SHARED 共享服务: 追踪上下文 / trace_context (core/trace_context.py) | 导入依赖 / import_depends |
| 10 | synthesized信号 / synthesized_signal (contracts/synthesiz... | → | D_SHARED 共享服务: 追踪上下文 / trace_context (core/trace_context.py) | 导入依赖 / import_depends |
| 11 | 目标组合契约 / TargetPortfolio (contracts/target_portfoli... | → | D_SHARED 共享服务: 追踪上下文 / trace_context (core/trace_context.py) | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_EX_CORE 执行核心: D_EX_CORE — Aggregate Root Manager (执行域聚合根管理器) ... | → | 成交 / fill (contracts/fill.py) | 导入依赖 / import_depends |
| 2 | D_EX_CORE 执行核心: D_EX_CORE — Aggregate Root Manager (执行域聚合根管理器) ... | → | 订单 / order (contracts/order.py) | 导入依赖 / import_depends |
| 3 | D_EX_CORE 执行核心: D_EX_CORE — Aggregate Root Manager (执行域聚合根管理器) ... | → | 持仓 / position (contracts/position.py) | 导入依赖 / import_depends |
| 4 | D_EX_CORE 执行核心: 执行引擎 / D_EXECUTION_CORE — Execution Engine (ex_core/... | → | 订单 / order (contracts/order.py) | 导入依赖 / import_depends |
| 5 | D_EX_CORE 执行核心: 执行引擎 / D_EXECUTION_CORE — Execution Engine (ex_core/... | → | 风险limits / risk_limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 6 | D_EX_CORE 执行核心: 部分成交处理器 (ex_core/fill_handler.py) | → | 成交 / fill (contracts/fill.py) | 导入依赖 / import_depends |
| 7 | D_EX_CORE 执行核心: 部分成交处理器 (ex_core/fill_handler.py) | → | 订单 / order (contracts/order.py) | 导入依赖 / import_depends |
| 8 | D_EX_CORE 执行核心: 下单执行 Saga 编排器 / Order Execution Saga (ex_core/orde... | → | 成交 / fill (contracts/fill.py) | 导入依赖 / import_depends |
| 9 | D_EX_CORE 执行核心: 下单执行 Saga 编排器 / Order Execution Saga (ex_core/orde... | → | 订单 / order (contracts/order.py) | 导入依赖 / import_depends |
| 10 | D_EX_CORE 执行核心: 下单执行 Saga 编排器 / Order Execution Saga (ex_core/orde... | → | 风险limits / risk_limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 11 | D_EX_CORE 执行核心: 订单管理器 / D_EXECUTION_CORE — Order Manager (ex_core/o... | → | 成交 / fill (contracts/fill.py) | 导入依赖 / import_depends |
| 12 | D_EX_CORE 执行核心: 订单管理器 / D_EXECUTION_CORE — Order Manager (ex_core/o... | → | 订单 / order (contracts/order.py) | 导入依赖 / import_depends |
| 13 | D_EX_CORE 执行核心: 盘中持仓对账器 / D_EXECUTION_CORE (ex_core/position_recon... | → | 持仓 / position (contracts/position.py) | 导入依赖 / import_depends |
| 14 | D_EX_CORE 执行核心: Position Tracker / D_EXECUTION_CORE (position_tracker/tra... | → | 成交 / fill (contracts/fill.py) | 导入依赖 / import_depends |
| 15 | D_EX_CORE 执行核心: Position Tracker / D_EXECUTION_CORE (position_tracker/tra... | → | 持仓 / position (contracts/position.py) | 导入依赖 / import_depends |
| 16 | D_EX_CORE 执行核心: 执行域仓储接口 (ex_core/repository_interface.py) | → | 订单 / order (contracts/order.py) | 导入依赖 / import_depends |
| 17 | D_EX_CORE 执行核心: 执行域仓储接口 (ex_core/repository_interface.py) | → | 持仓 / position (contracts/position.py) | 导入依赖 / import_depends |
| 18 | D_EX_CORE 执行核心: 交易会话 / trading_session (ex_core/trading_session.py) | → | 成交 / fill (contracts/fill.py) | 导入依赖 / import_depends |
| 19 | D_EX_CORE 执行核心: 交易会话 / trading_session (ex_core/trading_session.py) | → | 订单 / order (contracts/order.py) | 导入依赖 / import_depends |
| 20 | D_EX_CORE 执行核心: 交易会话 / trading_session (ex_core/trading_session.py) | → | 持仓 / position (contracts/position.py) | 导入依赖 / import_depends |
| 21 | D_EX_CORE 执行核心: 交易会话 / trading_session (ex_core/trading_session.py) | → | 风险limits / risk_limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 22 | D_EX_CORE 执行核心: PositionReconciler 单元测试 — D-EX-CORE-56 盘中持仓对账... | → | 成交 / fill (contracts/fill.py) | 测试依赖 / test_depends |
| 23 | D_EX_CORE 执行核心: PositionReconciler 单元测试 — D-EX-CORE-56 盘中持仓对账... | → | 持仓 / position (contracts/position.py) | 测试依赖 / test_depends |
| 24 | D_EX_SOR 执行路由: 券商 API 连接器 / Broker API Connector (api/broker_api_co... | → | 成交 / fill (contracts/fill.py) | 导入依赖 / import_depends |
| 25 | D_EX_SOR 执行路由: 券商 API 连接器 / Broker API Connector (api/broker_api_co... | → | 订单 / order (contracts/order.py) | 导入依赖 / import_depends |
| 26 | D_EX_SOR 执行路由: 算法执行选择器 / algo_execution_selector (core/algo_execu... | → | 订单 / order (contracts/order.py) | 导入依赖 / import_depends |
| 27 | D_EX_SOR 执行路由: 算法交易引擎 / algo_trading_engine (core/algo_trading_eng... | → | 订单 / order (contracts/order.py) | 导入依赖 / import_depends |
| 28 | D_EX_SOR 执行路由: 经纪人适配器管理器 / broker_adapter_manager (core/broker_... | → | 成交 / fill (contracts/fill.py) | 导入依赖 / import_depends |
| 29 | D_EX_SOR 执行路由: 经纪人适配器管理器 / broker_adapter_manager (core/broker_... | → | 订单 / order (contracts/order.py) | 导入依赖 / import_depends |
| 30 | D_EX_SOR 执行路由: optimal订单路由器 / optimal_order_router (core/optimal_or... | → | 订单 / order (contracts/order.py) | 导入依赖 / import_depends |
| 31 | D_FACTOR 因子: 转换器 / converter (ctr001_consumer/converter.py) | → | 市场数据 / market_data (contracts/market_data.py) | 导入依赖 / import_depends |
| 32 | D_FACTOR 因子: 转换器 / converter (ctr002_producer/converter.py) | → | 因子信号 / factor_signal (contracts/factor_signal.py) | 导入依赖 / import_depends |
| 33 | D_FUNDAMENTAL_SIGNAL 基本面信号: 信号生成聚合基类 / Signal Generation Aggregator Base (gen... | → | 因子信号 / factor_signal (contracts/factor_signal.py) | 导入依赖 / import_depends |
| 34 | D_FUNDAMENTAL_SIGNAL 基本面信号: 信号生成聚合基类 / Signal Generation Aggregator Base (gen... | → | synthesized信号 / synthesized_signal (contracts/synthesiz... | 导入依赖 / import_depends |
| 35 | D_FUNDAMENTAL_SIGNAL 基本面信号: 默认信号聚合器 / Default Signal Aggregator (implementatio... | → | 因子信号 / factor_signal (contracts/factor_signal.py) | 导入依赖 / import_depends |
| 36 | D_FUNDAMENTAL_SIGNAL 基本面信号: 默认信号聚合器 / Default Signal Aggregator (implementatio... | → | synthesized信号 / synthesized_signal (contracts/synthesiz... | 导入依赖 / import_depends |
| 37 | D_FUNDAMENTAL_SIGNAL 基本面信号: 管线 / Alpha Signal Pipeline (signal_fundamental/pipeline... | → | 因子信号 / factor_signal (contracts/factor_signal.py) | 导入依赖 / import_depends |
| 38 | D_FUNDAMENTAL_SIGNAL 基本面信号: 管线 / Alpha Signal Pipeline (signal_fundamental/pipeline... | → | synthesized信号 / synthesized_signal (contracts/synthesiz... | 导入依赖 / import_depends |
| 39 | D_FUNDAMENTAL_SIGNAL 基本面信号: 策略默认资本分配器 / Strategy Default Capital Allocator (... | → | synthesized信号 / synthesized_signal (contracts/synthesiz... | 导入依赖 / import_depends |
| 40 | D_FUNDAMENTAL_SIGNAL 基本面信号: 信号合成器 / Signal Synthesizer (synth/signal_synthesizer... | → | 因子信号 / factor_signal (contracts/factor_signal.py) | 导入依赖 / import_depends |
| 41 | D_FUNDAMENTAL_SIGNAL 基本面信号: 信号合成器 / Signal Synthesizer (synth/signal_synthesizer... | → | synthesized信号 / synthesized_signal (contracts/synthesiz... | 导入依赖 / import_depends |
| 42 | D_GOVERNANCE 生命周期管理: A2Afull验证 / a2a_full_verification (scripts/a2a_full_ver... | → | 包入口 / __init__ (config/__init__.py) | 导入依赖 / import_depends |
| 43 | D_GOVERNANCE 生命周期管理: 本地层daemon / local_layer_daemon (construction/local_lay... | → | 包入口 / __init__ (config/__init__.py) | 导入依赖 / import_depends |
| 44 | D_GOVERNANCE 生命周期管理: 风险验证桥接 / D_EXECUTION_CORE — Risk Validation Bridge... | → | 风险limits / risk_limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 45 | D_GOVERNANCE 生命周期管理: 仿真经纪人 / D_EXECUTION_CORE — Simulation Broker Adapte... | → | 成交 / fill (contracts/fill.py) | 导入依赖 / import_depends |
| 46 | D_GOVERNANCE 生命周期管理: 仿真经纪人 / D_EXECUTION_CORE — Simulation Broker Adapte... | → | 订单 / order (contracts/order.py) | 导入依赖 / import_depends |
| 47 | D_GOVERNANCE 生命周期管理: 仿真经纪人 / D_EXECUTION_CORE — Simulation Broker Adapte... | → | 持仓 / position (contracts/position.py) | 导入依赖 / import_depends |
| 48 | D_GOV_CODE_QUALITY 代码质量治理: 配置 / config (code_dedup/config.py) | → | 应用配置 / app_config (config/app_config.py) | 导入依赖 / import_depends |
| 49 | D_GOV_ENFORCEMENT 规则执行: 合规规则 / compliance_rule (rule_enforcement/compliance_r... | → | 合规规则 / compliance_rule (contracts/compliance_rule.py) | 导入依赖 / import_depends |
| 50 | D_INFRA_RUNTIME 运行时集成: 健康监控 / health_monitor (trading/health_monitor.py) | → | 遥测发射器 / telemetry_emitter (contracts/telemetry_emitt... | 导入依赖 / import_depends |
| 51 | D_MKT_DATA 行情数据: 包入口 / __init__ (market_data/__init__.py) | → | 市场数据 / market_data (contracts/market_data.py) | 导入依赖 / import_depends |
| 52 | D_MKT_DATA 行情数据: D_MKT_DATA — Connector Base (行情数据连接器基类) (connec... | → | 市场数据 / market_data (contracts/market_data.py) | 导入依赖 / import_depends |
| 53 | D_MKT_DATA 行情数据: 生产者 / producer (normalized_market_data_producer/produc... | → | 市场数据 / market_data (contracts/market_data.py) | 导入依赖 / import_depends |
| 54 | D_MKT_DATA 行情数据: vendor基类 / vendor_base (market_data/vendor_base.py) | → | 市场数据 / market_data (contracts/market_data.py) | 导入依赖 / import_depends |
| 55 | D_MKT_DATA 行情数据: MOD-MKT-002 Vendor Base 单元测试. (market_data/test_vendo... | → | 市场数据 / market_data (contracts/market_data.py) | 测试依赖 / test_depends |
| 56 | D_PF_ALLOC 组合分配: 策略生命周期事件 / strategy_lifecycle_event (pf_alloc/str... | → | 策略生命周期事件 / strategy_lifecycle_event (contracts/st... | 导入依赖 / import_depends |
| 57 | D_PF_ALLOC 组合分配: 默认权益策略 / D_PORTFOLIO_CORE — Default Equity Long-On... | → | 订单 / order (contracts/order.py) | 导入依赖 / import_depends |
| 58 | D_PF_CORE 组合核心: 约束求解器 (core/constraint_solver.py) | → | 风险limits / risk_limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 59 | D_PF_CORE 组合核心: 绩效归因引擎 (core/performance_attribution_engine.py) | → | 绩效attribution报告 / performance_attribution_report (con... | 导入依赖 / import_depends |
| 60 | D_PF_CORE 组合核心: 组合优化器 (core/portfolio_optimizer.py) | → | 风险limits / risk_limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 61 | D_PF_CORE 组合核心: 组合优化器 (core/portfolio_optimizer.py) | → | 目标组合契约 / TargetPortfolio (contracts/target_portfoli... | contract / contract |
| 62 | D_PF_CORE 组合核心: 组合优化器 (core/portfolio_optimizer.py) | → | 目标组合契约 / TargetPortfolio (contracts/target_portfoli... | 导入依赖 / import_depends |
| 63 | D_PF_CORE 组合核心: 再平衡调度器 (core/rebalance_scheduler.py) | → | 风险limits / risk_limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 64 | D_PF_CORE 组合核心: 再平衡调度器 (core/rebalance_scheduler.py) | → | 目标组合契约 / TargetPortfolio (contracts/target_portfoli... | 导入依赖 / import_depends |
| 65 | D_PF_CORE 组合核心: 策略引擎 (core/strategy_engine.py) | → | 策略生命周期事件 / strategy_lifecycle_event (contracts/st... | contract / contract |
| 66 | D_PF_CORE 组合核心: 策略引擎 (core/strategy_engine.py) | → | 策略生命周期事件 / strategy_lifecycle_event (contracts/st... | 导入依赖 / import_depends |
| 67 | D_POSITION 仓位管理: 持仓sizing引擎 / position_sizing_engine (core/position_si... | → | 风险limits / risk_limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 68 | D_POSITION 仓位管理: Position Sizing Engine 测试 (MOD-POS-001 阶段1)。 (positi... | → | 风险limits / risk_limits (contracts/risk_limits.py) | 测试依赖 / test_depends |
| 69 | D_REPORTING 报告: analytics基类 / D_REPORTING — Post-Trade Analytics Layer... | → | 执行报告 / execution_report (contracts/execution_report.py) | 导入依赖 / import_depends |
| 70 | D_REPORTING 报告: analytics基类 / D_REPORTING — Post-Trade Analytics Layer... | → | 成交 / fill (contracts/fill.py) | 导入依赖 / import_depends |
| 71 | D_REPORTING 报告: analytics基类 / D_REPORTING — Post-Trade Analytics Layer... | → | 订单 / order (contracts/order.py) | 导入依赖 / import_depends |
| 72 | D_REPORTING 报告: analytics基类 / D_REPORTING — Post-Trade Analytics Layer... | → | 绩效attribution报告 / performance_attribution_report (con... | 导入依赖 / import_depends |
| 73 | D_REPORTING 报告: 默认attribution引擎 / D_REPORTING — Default Attribution ... | → | 绩效attribution报告 / performance_attribution_report (con... | 导入依赖 / import_depends |
| 74 | D_REPORTING 报告: 默认tca引擎 / D_REPORTING — Default TCA Engine (reportin... | → | 执行报告 / execution_report (contracts/execution_report.py) | 导入依赖 / import_depends |
| 75 | D_REPORTING 报告: 默认tca引擎 / D_REPORTING — Default TCA Engine (reportin... | → | 成交 / fill (contracts/fill.py) | 导入依赖 / import_depends |
| 76 | D_REPORTING 报告: 默认tca引擎 / D_REPORTING — Default TCA Engine (reportin... | → | 订单 / order (contracts/order.py) | 导入依赖 / import_depends |
| 77 | D_REPORTING 报告: 实时盈亏仪表盘 / realtime_pnl_dashboard (reporting/realti... | → | 成交 / fill (contracts/fill.py) | 导入依赖 / import_depends |
| 78 | D_REPORTING 报告: MOD-RPT-004 Real-time P&L Dashboard 单元测试. (reporting/... | → | 成交 / fill (contracts/fill.py) | 测试依赖 / test_depends |
| 79 | D_RISK 风控: 风险limits / D_RISK — Risk Limits Calculator (risk/risk_... | → | 风险limits / risk_limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 80 | D_RISK 风控: 风控管理器 / risk_manager (risk/risk_manager.py) | → | 风险limits / risk_limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 81 | D_SHARED 共享服务: 绩效attribution报告 / performance_attribution_report (por... | → | 绩效attribution报告 / performance_attribution_report (con... | 导入依赖 / import_depends |
| 82 | D_SIGQC 信号质量控制: 退化监控基类 / D_SIGQC — Signal Quality Degradation Moni... | → | synthesized信号 / synthesized_signal (contracts/synthesiz... | 导入依赖 / import_depends |
| 83 | D_SIMULATION 仿真: 管线基类 / pipeline_base (simulation/pipeline_base.py) | → | 实验结果 / experiment_result (contracts/experiment_result... | 导入依赖 / import_depends |
| 84 | D_TRADING 交易运营: PnL Calculator / D_TRADING (trading/pnl_calculator.py) | → | 成交 / fill (contracts/fill.py) | 导入依赖 / import_depends |
| 85 | D_TRADING 交易运营: 结算对账 / settlement_reconciliation (trading/settlement_... | → | 成交 / fill (contracts/fill.py) | 导入依赖 / import_depends |
| 86 | D_TRADING 交易运营: 经纪人接口 / D_EXECUTION_CORE — BrokerInterface (trading... | → | 成交 / fill (contracts/fill.py) | 导入依赖 / import_depends |
| 87 | D_TRADING 交易运营: 经纪人接口 / D_EXECUTION_CORE — BrokerInterface (trading... | → | 订单 / order (contracts/order.py) | 导入依赖 / import_depends |
| 88 | D_TRADING 交易运营: 经纪人接口 / D_EXECUTION_CORE — BrokerInterface (trading... | → | 持仓 / position (contracts/position.py) | 导入依赖 / import_depends |
| 89 | D_TRADING 交易运营: 执行拒绝错误 / execution_rejection_error (execution/execu... | → | 追踪上下文 / trace_context (contracts/trace_context.py) | 导入依赖 / import_depends |
| 90 | D_TRADING 交易运营: 执行报告 / execution_report (execution/execution_report.py) | → | 执行报告 / execution_report (contracts/execution_report.py) | 导入依赖 / import_depends |
| 91 | D_TRADING 交易运营: 成交 / fill (execution/fill.py) | → | 成交 / fill (contracts/fill.py) | 导入依赖 / import_depends |
| 92 | D_TRADING 交易运营: 订单 / order (execution/order.py) | → | 订单 / order (contracts/order.py) | 导入依赖 / import_depends |
| 93 | D_TRADING 交易运营: 持仓 / position (execution/position.py) | → | 持仓 / position (contracts/position.py) | 导入依赖 / import_depends |
| 94 | D_TRADING 交易运营: 工厂 / factories (trading_contracts/factories.py) | → | 因子信号 / factor_signal (contracts/factor_signal.py) | 导入依赖 / import_depends |
| 95 | D_TRADING 交易运营: 工厂 / factories (trading_contracts/factories.py) | → | synthesized信号 / synthesized_signal (contracts/synthesiz... | 导入依赖 / import_depends |
| 96 | D_TRADING 交易运营: 绩效attribution报告 / performance_attribution_report (con... | → | 绩效attribution报告 / performance_attribution_report (con... | 导入依赖 / import_depends |
| 97 | D_TRADING 交易运营: 策略生命周期事件 / strategy_lifecycle_event (contracts/st... | → | 策略生命周期事件 / strategy_lifecycle_event (contracts/st... | 导入依赖 / import_depends |
| 98 | D_TRADING 交易运营: 风险限制违规错误 / risk_limit_violation_error (risk/risk_... | → | 追踪上下文 / trace_context (contracts/trace_context.py) | 导入依赖 / import_depends |
| 99 | D_TRADING 交易运营: 风险limits / risk_limits (risk/risk_limits.py) | → | 追踪上下文 / trace_context (contracts/trace_context.py) | 导入依赖 / import_depends |
| 100 | D_TRADING 交易运营: 风险校验器协议 / risk_validator_protocol (risk/risk_valid... | → | 风险limits / risk_limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 101 | D_TRADING 交易运营: MOD-TRADING-002 PnL Calculator 单元测试. (trading/test_pn... | → | 成交 / fill (contracts/fill.py) | 测试依赖 / test_depends |
| 102 | D_TRADING 交易运营: MOD-TRADING-003 Settlement & Reconciliation Engine 单元测... | → | 成交 / fill (contracts/fill.py) | 测试依赖 / test_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 19 个外部域直接连接（出边 11 条 + 入边 102 条 = 113 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_INFRASTRUCTURE["D_INFRASTRUCTURE<br/>跨层契约基础设施"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_EX_CORE["D_EX_CORE<br/>执行核心"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_REPORTING["D_REPORTING<br/>报告"]
    D_PF_CORE["D_PF_CORE<br/>组合核心"]
    D_FUNDAMENTAL_SIGNAL["D_FUNDAMENTAL_SIGNAL<br/>基本面信号"]
    D_EX_SOR["D_EX_SOR<br/>执行路由"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_MKT_DATA["D_MKT_DATA<br/>行情数据"]
    D_FACTOR["D_FACTOR<br/>因子"]
    D_PF_ALLOC["D_PF_ALLOC<br/>组合分配"]
    D_POSITION["D_POSITION<br/>仓位管理"]
    D_RISK["D_RISK<br/>风控"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_SIGQC["D_SIGQC<br/>信号质量控制"]
    D_GOV_CODE_QUALITY["D_GOV_CODE_QUALITY<br/>代码质量治理"]
    D_SIMULATION["D_SIMULATION<br/>仿真"]
    D_INFRASTRUCTURE -->|10条 导入依赖 / import_depends| D_SHARED
    D_INFRASTRUCTURE -->|1条 导入依赖 / import_depends| D_GOV_AUDIT
    D_EX_CORE -->|23条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INFRASTRUCTURE
    D_TRADING -->|19条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INFRASTRUCTURE
    D_REPORTING -->|10条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INFRASTRUCTURE
    D_PF_CORE -->|9条 contract / contract, 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_FUNDAMENTAL_SIGNAL -->|9条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_EX_SOR -->|7条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_GOVERNANCE -->|6条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_MKT_DATA -->|5条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INFRASTRUCTURE
    D_FACTOR -->|2条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_PF_ALLOC -->|2条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_POSITION -->|2条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INFRASTRUCTURE
    D_RISK -->|2条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_INFRA_RUNTIME -->|1条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_GOV_ENFORCEMENT -->|1条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_SHARED -->|1条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_SIGQC -->|1条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_GOV_CODE_QUALITY -->|1条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_SIMULATION -->|1条 导入依赖 / import_depends| D_INFRASTRUCTURE
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
