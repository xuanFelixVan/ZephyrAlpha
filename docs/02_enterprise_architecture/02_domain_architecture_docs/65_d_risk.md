---
doc_type: architecture_view
title: D_RISK 风控架构文档
version: "1.0"
status: active
date: 2026-08-02
owner: auto-generator
ttl: permanent
---

# 65_d_risk / 风控域 / Risk Control

> **功能简介 / Overview**: 风控，负责风险指标计算、风险限额管理和风险预警

> **文档作用 / Purpose**: 展示 风控（D_RISK）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/65_d_risk.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 65 | Number | 65 |
| 域ID | D_RISK | Domain ID | D_RISK |
| 域名称 | 风控 | Domain Name | Risk Control |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 19 | Module Count | 19 |
| 域内依赖 | 19 | Internal Dependencies | 19 |
| 跨域入边 | 5 | Cross-domain Incoming | 5 |
| 跨域出边 | 7 | Cross-domain Outgoing | 7 |
| 设计态模块 | 4 | Design Modules | 4 |
| 生产态模块 | 15 | Production Modules | 15 |
| 容量 | 12/150 (正常) | Capacity | 12/150 (正常) |
| 描述 | 风控，负责风险指标计算、风险限额管理和风险预警 | Description | 风控，负责风险指标计算、风险限额管理和风险预警 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 19 个模块（生产态 15 + 设计态 4），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_risk_ashare_stop_loss_rule_engine_py["A股停止亏损规则引擎<br/>A股停止亏损规则引擎，风控的引擎，执行核心逻辑的<br/>处理引擎。<br/>⛔ 风控域，设计已就绪，等待开发排期<br/>ashare_stop_loss_rule_engine<br/>文件: risk/ashare_stop_loss_rule_engine.py<br/>(设计态 / design)"]
    src_zephyr_risk_ashare_systemic_risk_detector_py["A股系统性风险检测器<br/>A股systemic风险检测器，风控的检测器，检测特定模<br/>式或异常情况。<br/>⛔ 风控域，设计已就绪，等待开发排期<br/>ashare_systemic_risk_detector<br/>文件: risk/ashare_systemic_risk_detector.py<br/>(设计态 / design)"]
    src_zephyr_risk_core_concentration_monitor_py["core/concentration_monitor<br/>Concentration Risk Monitor — 集中度风险监控器<br/>(MOD-RK-07)<br/>文件: core/concentration_monitor.py<br/>(生产态 / production)"]
    src_zephyr_risk_core_drawdown_tracker_py["core/drawdown_tracker<br/>Drawdown Real-Time Tracker — 回撤实时追踪器<br/>(MOD-RK-011)<br/>文件: core/drawdown_tracker.py<br/>(设计态 / design)"]
    src_zephyr_risk_core_risk_budget_allocator_py["core/risk_budget_allocator<br/>Risk Budget Allocator — 风险预算分配器<br/>(MOD-RK-08)<br/>文件: core/risk_budget_allocator.py<br/>(生产态 / production)"]
    src_zephyr_risk_cross_asset_cross_market_data_adapter_ml_experiment_pipeline_py["机器学习实验管线<br/>机器学习实验管线，依赖机器学习实验管线工作<br/>ml_experiment_pipeline<br/>文件: cross_market_data_adapter/ml_experiment_<br/>pipeline.py<br/>(生产态 / production)"]
    src_zephyr_risk_drawdown_realtime_tracker_py["回撤实时追踪器<br/>回撤实时追踪器，风控的追踪器，持续跟踪某项指标或<br/>状态的变化。<br/>⛔ 风控域，设计已就绪，等待开发排期<br/>drawdown_realtime_tracker<br/>文件: risk/drawdown_realtime_tracker.py<br/>(设计态 / design)"]
    src_zephyr_risk_implementations_default_risk_manager_orchestrator_py["默认风险管理器编排器<br/>默认风险管理器编排器。D_RISK — Default Risk<br/>Manager Orchestrator<br/>文件: implementations/default_risk_manager_<br/>orchestrator.py<br/>(生产态 / production)"]
    src_zephyr_risk_ashare_stop_loss_rule_engine_py ~~~ src_zephyr_risk_ashare_systemic_risk_detector_py
    src_zephyr_risk_ashare_systemic_risk_detector_py ~~~ src_zephyr_risk_core_concentration_monitor_py
    src_zephyr_risk_core_concentration_monitor_py ~~~ src_zephyr_risk_core_drawdown_tracker_py
    src_zephyr_risk_core_drawdown_tracker_py ~~~ src_zephyr_risk_core_risk_budget_allocator_py
    src_zephyr_risk_core_risk_budget_allocator_py ~~~ src_zephyr_risk_cross_asset_cross_market_data_adapter_ml_experiment_pipeline_py
    src_zephyr_risk_cross_asset_cross_market_data_adapter_ml_experiment_pipeline_py ~~~ src_zephyr_risk_drawdown_realtime_tracker_py
    src_zephyr_risk_drawdown_realtime_tracker_py ~~~ src_zephyr_risk_implementations_default_risk_manager_orchestrator_py
    src_zephyr_risk_core_risk_decomposition_py["core/risk_decomposition<br/>Risk Decomposition Engine — 风险分解引擎<br/>(MOD-RK-16)<br/>文件: core/risk_decomposition.py<br/>(生产态 / production)"]
    src_zephyr_risk_implementations_default_position_limit_checker_py["默认持仓限制检查器<br/>默认持仓限制检查器。D_RISK — Default Position<br/>Limit Checker<br/>文件: implementations/default_position_limit_<br/>checker.py<br/>(生产态 / production)"]
    src_zephyr_risk_implementations_default_risk_limits_calculator_py["默认风险limits计算器<br/>默认风险limits计算器。D_RISK — Default Risk<br/>Limits Calculator<br/>文件: implementations/default_risk_limits_<br/>calculator.py<br/>(生产态 / production)"]
    src_zephyr_risk_implementations_default_risk_validator_py["默认风险校验器<br/>默认风险校验器。D_RISK — Default Risk Validator<br/>文件: implementations/default_risk_validator.py<br/>(生产态 / production)"]
    src_zephyr_risk_stop_loss_py["停止亏损<br/>D_RISK — Stop-Loss & Kill Switch 兼容层<br/>stop_loss<br/>文件: risk/stop_loss.py<br/>(生产态 / production)"]
    src_zephyr_risk_core_risk_decomposition_py ~~~ src_zephyr_risk_implementations_default_position_limit_checker_py
    src_zephyr_risk_implementations_default_position_limit_checker_py ~~~ src_zephyr_risk_implementations_default_risk_limits_calculator_py
    src_zephyr_risk_implementations_default_risk_limits_calculator_py ~~~ src_zephyr_risk_implementations_default_risk_validator_py
    src_zephyr_risk_implementations_default_risk_validator_py ~~~ src_zephyr_risk_stop_loss_py
    src_zephyr_risk_core_var_calculator_py["core/var_calculator<br/>VaR Calculator — 风险价值计算器 (MOD-RK-05,<br/>Phase 1)<br/>文件: core/var_calculator.py<br/>(生产态 / production)"]
    src_zephyr_risk_implementations_default_stop_loss_engine_py["默认停止亏损引擎<br/>默认停止亏损引擎。D_RISK — Default Stop-Loss<br/>Engine<br/>文件: implementations/default_stop_loss_<br/>engine.py<br/>(生产态 / production)"]
    src_zephyr_risk_risk_limits_py["风险limits<br/>风险limits。D_RISK — Risk Limits Calculator<br/>文件: risk/risk_limits.py<br/>(生产态 / production)"]
    src_zephyr_risk_risk_manager_py["风控管理器<br/>ZephyrAlpha — D_RISK Risk Management Layer —<br/>风控管理器接口<br/>risk_manager<br/>文件: risk/risk_manager.py<br/>(生产态 / production)"]
    src_zephyr_risk_risk_validator_py["风险校验器<br/>风险校验器。D_RISK — Risk Validator<br/>文件: risk/risk_validator.py<br/>(生产态 / production)"]
    src_zephyr_risk_core_var_calculator_py ~~~ src_zephyr_risk_implementations_default_stop_loss_engine_py
    src_zephyr_risk_implementations_default_stop_loss_engine_py ~~~ src_zephyr_risk_risk_limits_py
    src_zephyr_risk_risk_limits_py ~~~ src_zephyr_risk_risk_manager_py
    src_zephyr_risk_risk_manager_py ~~~ src_zephyr_risk_risk_validator_py
    src_zephyr_risk_risk_manager_base_py["风险管理器基类<br/>风险管理器基类。D_RISK — Risk Management Layer<br/>Skeleton<br/>文件: risk/risk_manager_base.py<br/>(生产态 / production)"]
    src_zephyr_risk_ashare_stop_loss_rule_engine_py -.->|导入依赖 / import_depends| src_zephyr_risk_stop_loss_py
    src_zephyr_risk_ashare_systemic_risk_detector_py -.->|导入依赖 / import_depends| src_zephyr_risk_risk_validator_py
    src_zephyr_risk_drawdown_realtime_tracker_py -.->|导入依赖 / import_depends| src_zephyr_risk_risk_validator_py
    src_zephyr_risk_core_risk_budget_allocator_py -->|import / import| src_zephyr_risk_core_risk_decomposition_py
    src_zephyr_risk_core_risk_decomposition_py -->|import / import| src_zephyr_risk_core_var_calculator_py
    src_zephyr_risk_stop_loss_py -->|导入依赖 / import_depends| src_zephyr_risk_implementations_default_stop_loss_engine_py
    src_zephyr_risk_implementations_default_position_limit_checker_py -->|导入依赖 / import_depends| src_zephyr_risk_risk_manager_base_py
    src_zephyr_risk_implementations_default_position_limit_checker_py -->|导入依赖 / import_depends| src_zephyr_risk_risk_manager_py
    src_zephyr_risk_implementations_default_risk_limits_calculator_py -->|导入依赖 / import_depends| src_zephyr_risk_risk_limits_py
    src_zephyr_risk_implementations_default_risk_limits_calculator_py -->|导入依赖 / import_depends| src_zephyr_risk_risk_manager_py
    src_zephyr_risk_implementations_default_risk_manager_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_risk_risk_manager_base_py
    src_zephyr_risk_implementations_default_risk_manager_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_risk_risk_manager_py
    src_zephyr_risk_implementations_default_risk_manager_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_risk_implementations_default_position_limit_checker_py
    src_zephyr_risk_implementations_default_risk_manager_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_risk_implementations_default_risk_limits_calculator_py
    src_zephyr_risk_implementations_default_risk_manager_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_risk_implementations_default_stop_loss_engine_py
    src_zephyr_risk_implementations_default_risk_manager_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_risk_implementations_default_risk_validator_py
    src_zephyr_risk_implementations_default_stop_loss_engine_py -->|导入依赖 / import_depends| src_zephyr_risk_risk_manager_base_py
    src_zephyr_risk_implementations_default_risk_validator_py -->|导入依赖 / import_depends| src_zephyr_risk_risk_manager_py
    src_zephyr_risk_implementations_default_risk_validator_py -->|导入依赖 / import_depends| src_zephyr_risk_risk_validator_py
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_risk_core_var_calculator_py -->|导入依赖 / import_depends| D_SHARED
    D_TRADING["交易运营<br/>交易运营，负责交易生命周期管理、订单状态和成交处<br/>理<br/>Trading Operations<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_risk_risk_manager_py -->|导入依赖 / import_depends| D_TRADING
    src_zephyr_risk_risk_manager_py -->|导入依赖 / import_depends| D_TRADING
    D_INFRASTRUCTURE["跨层契约基础设施<br/>跨层契约基础设施，负责跨层契约定义、共享契约管理<br/>和契约校验<br/>Cross-Layer Contract Infrastructure<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_risk_risk_limits_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_risk_cross_asset_cross_market_data_adapter_ml_experiment_pipeline_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_risk_risk_manager_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_risk_risk_manager_py -->|导入依赖 / import_depends| D_TRADING
    D_POSITION["仓位管理<br/>仓位管理，负责持仓跟踪、仓位计算和盈亏分析<br/>Position Management<br/>跨域节点 / cross-domain<br/>(设计态 / design)"]
    D_POSITION -.->|runtime / runtime| src_zephyr_risk_risk_limits_py
    D_PF_CORE["组合核心<br/>组合核心，负责投资组合构建、持仓管理和组合优化<br/>Portfolio Core<br/>跨域节点 / cross-domain<br/>(设计态 / design)"]
    D_PF_CORE -.->|导入依赖 / import_depends| src_zephyr_risk_risk_limits_py
    D_EX_CORE["执行核心<br/>执行核心，负责订单执行引擎、执行策略和执行管理<br/>Execution Core<br/>跨域节点 / cross-domain<br/>(设计态 / design)"]
    D_EX_CORE -.->|runtime / runtime| src_zephyr_risk_risk_validator_py
    D_GOVERNANCE["生命周期管理<br/>生命周期管理，负责蓝图/模块<br/>/任务的声明周期管理和元数据治理<br/>Lifecycle Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_risk_stop_loss_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_risk_risk_manager_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_risk_core_concentration_monitor_py,src_zephyr_risk_core_risk_budget_allocator_py,src_zephyr_risk_core_risk_decomposition_py,src_zephyr_risk_core_var_calculator_py,src_zephyr_risk_cross_asset_cross_market_data_adapter_ml_experiment_pipeline_py,src_zephyr_risk_implementations_default_position_limit_checker_py,src_zephyr_risk_implementations_default_risk_limits_calculator_py,src_zephyr_risk_implementations_default_risk_manager_orchestrator_py,src_zephyr_risk_implementations_default_risk_validator_py,src_zephyr_risk_implementations_default_stop_loss_engine_py,src_zephyr_risk_risk_limits_py,src_zephyr_risk_risk_manager_py,src_zephyr_risk_risk_manager_base_py,src_zephyr_risk_risk_validator_py,src_zephyr_risk_stop_loss_py production
    class src_zephyr_risk_ashare_stop_loss_rule_engine_py,src_zephyr_risk_ashare_systemic_risk_detector_py,src_zephyr_risk_core_drawdown_tracker_py,src_zephyr_risk_drawdown_realtime_tracker_py design
    class D_SHARED,D_TRADING,D_INFRASTRUCTURE,D_GOVERNANCE external_prod
    class D_POSITION,D_PF_CORE,D_EX_CORE external_design
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 15 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_risk_core_concentration_monitor_py["core/concentration_monitor<br/>Concentration Risk Monitor — 集中度风险监控器<br/>(MOD-RK-07)<br/>文件: core/concentration_monitor.py<br/>(生产态 / production)"]
    src_zephyr_risk_core_risk_budget_allocator_py["core/risk_budget_allocator<br/>Risk Budget Allocator — 风险预算分配器<br/>(MOD-RK-08)<br/>文件: core/risk_budget_allocator.py<br/>(生产态 / production)"]
    src_zephyr_risk_cross_asset_cross_market_data_adapter_ml_experiment_pipeline_py["机器学习实验管线<br/>机器学习实验管线，依赖机器学习实验管线工作<br/>ml_experiment_pipeline<br/>文件: cross_market_data_adapter/ml_experiment_<br/>pipeline.py<br/>(生产态 / production)"]
    src_zephyr_risk_implementations_default_risk_manager_orchestrator_py["默认风险管理器编排器<br/>默认风险管理器编排器。D_RISK — Default Risk<br/>Manager Orchestrator<br/>文件: implementations/default_risk_manager_<br/>orchestrator.py<br/>(生产态 / production)"]
    src_zephyr_risk_stop_loss_py["停止亏损<br/>D_RISK — Stop-Loss & Kill Switch 兼容层<br/>stop_loss<br/>文件: risk/stop_loss.py<br/>(生产态 / production)"]
    src_zephyr_risk_core_concentration_monitor_py ~~~ src_zephyr_risk_core_risk_budget_allocator_py
    src_zephyr_risk_core_risk_budget_allocator_py ~~~ src_zephyr_risk_cross_asset_cross_market_data_adapter_ml_experiment_pipeline_py
    src_zephyr_risk_cross_asset_cross_market_data_adapter_ml_experiment_pipeline_py ~~~ src_zephyr_risk_implementations_default_risk_manager_orchestrator_py
    src_zephyr_risk_implementations_default_risk_manager_orchestrator_py ~~~ src_zephyr_risk_stop_loss_py
    src_zephyr_risk_core_risk_decomposition_py["core/risk_decomposition<br/>Risk Decomposition Engine — 风险分解引擎<br/>(MOD-RK-16)<br/>文件: core/risk_decomposition.py<br/>(生产态 / production)"]
    src_zephyr_risk_implementations_default_position_limit_checker_py["默认持仓限制检查器<br/>默认持仓限制检查器。D_RISK — Default Position<br/>Limit Checker<br/>文件: implementations/default_position_limit_<br/>checker.py<br/>(生产态 / production)"]
    src_zephyr_risk_implementations_default_risk_limits_calculator_py["默认风险limits计算器<br/>默认风险limits计算器。D_RISK — Default Risk<br/>Limits Calculator<br/>文件: implementations/default_risk_limits_<br/>calculator.py<br/>(生产态 / production)"]
    src_zephyr_risk_implementations_default_risk_validator_py["默认风险校验器<br/>默认风险校验器。D_RISK — Default Risk Validator<br/>文件: implementations/default_risk_validator.py<br/>(生产态 / production)"]
    src_zephyr_risk_implementations_default_stop_loss_engine_py["默认停止亏损引擎<br/>默认停止亏损引擎。D_RISK — Default Stop-Loss<br/>Engine<br/>文件: implementations/default_stop_loss_<br/>engine.py<br/>(生产态 / production)"]
    src_zephyr_risk_core_risk_decomposition_py ~~~ src_zephyr_risk_implementations_default_position_limit_checker_py
    src_zephyr_risk_implementations_default_position_limit_checker_py ~~~ src_zephyr_risk_implementations_default_risk_limits_calculator_py
    src_zephyr_risk_implementations_default_risk_limits_calculator_py ~~~ src_zephyr_risk_implementations_default_risk_validator_py
    src_zephyr_risk_implementations_default_risk_validator_py ~~~ src_zephyr_risk_implementations_default_stop_loss_engine_py
    src_zephyr_risk_core_var_calculator_py["core/var_calculator<br/>VaR Calculator — 风险价值计算器 (MOD-RK-05,<br/>Phase 1)<br/>文件: core/var_calculator.py<br/>(生产态 / production)"]
    src_zephyr_risk_risk_limits_py["风险limits<br/>风险limits。D_RISK — Risk Limits Calculator<br/>文件: risk/risk_limits.py<br/>(生产态 / production)"]
    src_zephyr_risk_risk_manager_py["风控管理器<br/>ZephyrAlpha — D_RISK Risk Management Layer —<br/>风控管理器接口<br/>risk_manager<br/>文件: risk/risk_manager.py<br/>(生产态 / production)"]
    src_zephyr_risk_risk_manager_base_py["风险管理器基类<br/>风险管理器基类。D_RISK — Risk Management Layer<br/>Skeleton<br/>文件: risk/risk_manager_base.py<br/>(生产态 / production)"]
    src_zephyr_risk_risk_validator_py["风险校验器<br/>风险校验器。D_RISK — Risk Validator<br/>文件: risk/risk_validator.py<br/>(生产态 / production)"]
    src_zephyr_risk_core_var_calculator_py ~~~ src_zephyr_risk_risk_limits_py
    src_zephyr_risk_risk_limits_py ~~~ src_zephyr_risk_risk_manager_py
    src_zephyr_risk_risk_manager_py ~~~ src_zephyr_risk_risk_manager_base_py
    src_zephyr_risk_risk_manager_base_py ~~~ src_zephyr_risk_risk_validator_py
    src_zephyr_risk_core_risk_budget_allocator_py -->|import / import| src_zephyr_risk_core_risk_decomposition_py
    src_zephyr_risk_core_risk_decomposition_py -->|import / import| src_zephyr_risk_core_var_calculator_py
    src_zephyr_risk_stop_loss_py -->|导入依赖 / import_depends| src_zephyr_risk_implementations_default_stop_loss_engine_py
    src_zephyr_risk_implementations_default_position_limit_checker_py -->|导入依赖 / import_depends| src_zephyr_risk_risk_manager_base_py
    src_zephyr_risk_implementations_default_position_limit_checker_py -->|导入依赖 / import_depends| src_zephyr_risk_risk_manager_py
    src_zephyr_risk_implementations_default_risk_limits_calculator_py -->|导入依赖 / import_depends| src_zephyr_risk_risk_limits_py
    src_zephyr_risk_implementations_default_risk_limits_calculator_py -->|导入依赖 / import_depends| src_zephyr_risk_risk_manager_py
    src_zephyr_risk_implementations_default_risk_manager_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_risk_risk_manager_base_py
    src_zephyr_risk_implementations_default_risk_manager_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_risk_risk_manager_py
    src_zephyr_risk_implementations_default_risk_manager_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_risk_implementations_default_position_limit_checker_py
    src_zephyr_risk_implementations_default_risk_manager_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_risk_implementations_default_risk_limits_calculator_py
    src_zephyr_risk_implementations_default_risk_manager_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_risk_implementations_default_stop_loss_engine_py
    src_zephyr_risk_implementations_default_risk_manager_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_risk_implementations_default_risk_validator_py
    src_zephyr_risk_implementations_default_stop_loss_engine_py -->|导入依赖 / import_depends| src_zephyr_risk_risk_manager_base_py
    src_zephyr_risk_implementations_default_risk_validator_py -->|导入依赖 / import_depends| src_zephyr_risk_risk_manager_py
    src_zephyr_risk_implementations_default_risk_validator_py -->|导入依赖 / import_depends| src_zephyr_risk_risk_validator_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_risk_core_concentration_monitor_py,src_zephyr_risk_core_risk_budget_allocator_py,src_zephyr_risk_core_risk_decomposition_py,src_zephyr_risk_core_var_calculator_py,src_zephyr_risk_cross_asset_cross_market_data_adapter_ml_experiment_pipeline_py,src_zephyr_risk_implementations_default_position_limit_checker_py,src_zephyr_risk_implementations_default_risk_limits_calculator_py,src_zephyr_risk_implementations_default_risk_manager_orchestrator_py,src_zephyr_risk_implementations_default_risk_validator_py,src_zephyr_risk_implementations_default_stop_loss_engine_py,src_zephyr_risk_risk_limits_py,src_zephyr_risk_risk_manager_py,src_zephyr_risk_risk_manager_base_py,src_zephyr_risk_risk_validator_py,src_zephyr_risk_stop_loss_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 4 个），不含跨域外部节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_risk_ashare_stop_loss_rule_engine_py["A股停止亏损规则引擎<br/>A股停止亏损规则引擎，风控的引擎，执行核心逻辑的<br/>处理引擎。<br/>⛔ 风控域，设计已就绪，等待开发排期<br/>ashare_stop_loss_rule_engine<br/>文件: risk/ashare_stop_loss_rule_engine.py<br/>(设计态 / design)"]
    src_zephyr_risk_ashare_systemic_risk_detector_py["A股系统性风险检测器<br/>A股systemic风险检测器，风控的检测器，检测特定模<br/>式或异常情况。<br/>⛔ 风控域，设计已就绪，等待开发排期<br/>ashare_systemic_risk_detector<br/>文件: risk/ashare_systemic_risk_detector.py<br/>(设计态 / design)"]
    src_zephyr_risk_core_drawdown_tracker_py["core/drawdown_tracker<br/>Drawdown Real-Time Tracker — 回撤实时追踪器<br/>(MOD-RK-011)<br/>文件: core/drawdown_tracker.py<br/>(设计态 / design)"]
    src_zephyr_risk_drawdown_realtime_tracker_py["回撤实时追踪器<br/>回撤实时追踪器，风控的追踪器，持续跟踪某项指标或<br/>状态的变化。<br/>⛔ 风控域，设计已就绪，等待开发排期<br/>drawdown_realtime_tracker<br/>文件: risk/drawdown_realtime_tracker.py<br/>(设计态 / design)"]
    src_zephyr_risk_ashare_stop_loss_rule_engine_py ~~~ src_zephyr_risk_ashare_systemic_risk_detector_py
    src_zephyr_risk_ashare_systemic_risk_detector_py ~~~ src_zephyr_risk_core_drawdown_tracker_py
    src_zephyr_risk_core_drawdown_tracker_py ~~~ src_zephyr_risk_drawdown_realtime_tracker_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_risk_ashare_stop_loss_rule_engine_py,src_zephyr_risk_ashare_systemic_risk_detector_py,src_zephyr_risk_core_drawdown_tracker_py,src_zephyr_risk_drawdown_realtime_tracker_py design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 风险limits / D_RISK — Risk Limits Calculator (risk/risk_... | → | D_INFRASTRUCTURE 跨层契约基础设施: 风险limits / risk_limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 2 | 风控管理器 / risk_manager (risk/risk_manager.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: 风险limits / risk_limits (contracts/risk_limits.py) | 导入依赖 / import_depends |
| 3 | VaR Calculator — 风险价值计算器 (MOD-RK-05, Phase 1) (co... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 4 | 机器学习实验管线 / ml_experiment_pipeline (cross_market_d... | → | D_SHARED 共享服务: 机器学习实验管线 / ml_experiment_pipeline (_cross_layer/m... | 导入依赖 / import_depends |
| 5 | 风控管理器 / risk_manager (risk/risk_manager.py) | → | D_TRADING 交易运营: 风险仪表盘快照 / risk_dashboard_snapshot (risk/risk_dashb... | 导入依赖 / import_depends |
| 6 | 风控管理器 / risk_manager (risk/risk_manager.py) | → | D_TRADING 交易运营: 风险限制违规错误 / risk_limit_violation_error (risk/risk_... | 导入依赖 / import_depends |
| 7 | 风控管理器 / risk_manager (risk/risk_manager.py) | → | D_TRADING 交易运营: 风险指标 / risk_metrics (risk/risk_metrics.py) | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_EX_CORE 执行核心: 实盘仿真切换器 / live_simulation_switcher (ex_core/live_s... | → | 风险校验器 / D_RISK — Risk Validator (risk/risk_validato... | runtime / runtime |
| 2 | D_GOVERNANCE 生命周期管理: demoe2e管线 / demo_e2e_pipeline (construction/demo_e2e_pi... | → | 风控管理器 / risk_manager (risk/risk_manager.py) | 导入依赖 / import_depends |
| 3 | D_GOVERNANCE 生命周期管理: demoe2e管线 / demo_e2e_pipeline (construction/demo_e2e_pi... | → | 停止亏损 / stop_loss (risk/stop_loss.py) | 导入依赖 / import_depends |
| 4 | D_PF_CORE 组合核心: 优化器 (optimizer/) | → | 风险limits / D_RISK — Risk Limits Calculator (risk/risk_... | 导入依赖 / import_depends |
| 5 | D_POSITION 仓位管理: 持仓sizing引擎 / position_sizing_engine (core/position_si... | → | 风险limits / D_RISK — Risk Limits Calculator (risk/risk_... | runtime / runtime |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 7 个外部域直接连接（出边 7 条 + 入边 5 条 = 12 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_RISK["D_RISK<br/>风控"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE<br/>跨层契约基础设施"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_EX_CORE["D_EX_CORE<br/>执行核心"]
    D_PF_CORE["D_PF_CORE<br/>组合核心"]
    D_POSITION["D_POSITION<br/>仓位管理"]
    D_RISK -->|3条 导入依赖 / import_depends| D_TRADING
    D_RISK -->|2条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_RISK -->|2条 导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE -->|2条 导入依赖 / import_depends| D_RISK
    D_EX_CORE -->|1条 runtime / runtime| D_RISK
    D_PF_CORE -->|1条 导入依赖 / import_depends| D_RISK
    D_POSITION -->|1条 runtime / runtime| D_RISK
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
