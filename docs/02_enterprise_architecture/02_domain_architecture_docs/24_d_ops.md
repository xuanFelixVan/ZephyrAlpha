---
doc_type: architecture_view
title: D_OPS 反馈循环架构文档
version: "1.0"
status: active
date: 2026-08-02
owner: auto-generator
ttl: permanent
---

# 24_d_ops / 反馈循环域 / Feedback Loop

> **功能简介 / Overview**: 反馈循环，负责系统运行反馈、性能监控和自动调优闭环

> **文档作用 / Purpose**: 展示 反馈循环（D_OPS）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/24_d_ops.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 24 | Number | 24 |
| 域ID | D_OPS | Domain ID | D_OPS |
| 域名称 | 反馈循环 | Domain Name | Feedback Loop |
| 层级 | L1 基础平台层 | Layer | L1 Foundation |
| 模块数 | 11 | Module Count | 11 |
| 域内依赖 | 2 | Internal Dependencies | 2 |
| 跨域入边 | 20 | Cross-domain Incoming | 20 |
| 跨域出边 | 12 | Cross-domain Outgoing | 12 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 11 | Production Modules | 11 |
| 容量 | 11/150 (正常) | Capacity | 11/150 (正常) |
| 描述 | 自动引导(auto_bootstrap) | Description | 自动引导(auto_bootstrap) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 11 个模块（生产态 11 + 设计态 0），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    scripts_governance_observability_gate_cache_py["门禁缓存<br/>门禁结果缓存器，缓存门禁检查结果避免重复计算，提<br/>升 CI 流水线执行速度。<br/>文件: observability/gate_cache.py<br/>(生产态 / production)"]
    scripts_setup_dev_env_py["开发环境一次性初始化（裁定<br/>#ARCH-PYTHON-SITECUSTOMIZE<br/>开发环境一次性初始化。<br/>setup_dev_env<br/>文件: scripts/setup_dev_env.py<br/>(生产态 / production)"]
    src_zephyr_governance_observability_governance_observability_dashboard_py["可观测性仪表盘<br/>observability仪表盘，治理的核心类，封装Dashboard<br/>Panel相关逻辑。<br/>observability_dashboard<br/>文件: observability_governance<br/>/observability_dashboard.py<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_budget_engine_py["预算引擎<br/>运维管理<br/>文件: ops_governance/budget_engine.py<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_budget_handler_py["预算处理器<br/>G-CT-006 消费端 — Escalation.on_budget_alert()<br/>预算告急升级处理.<br/>budget_handler<br/>文件: ops_governance/budget_handler.py<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_budget_profile_manager_py["预算档案管理器<br/>治理管控（budget profile）<br/>budget_profile_manager<br/>文件: ops_governance/budget_profile_manager.py<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_budget_tracker_py["预算追踪器<br/>治理的追踪器，持续跟踪某项指标或状态的变化<br/>budget_tracker<br/>文件: ops_governance/budget_tracker.py<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_cost_budget_py["成本预算<br/>— AI 成本预算与强制熔断（Phase 11 / 盲点 B26）<br/>cost_budget<br/>文件: ops_governance/cost_budget.py<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_meta_observability_py["元可观测性<br/>Meta Observability — v0.10.0 协议自身可观测性:<br/>self loop latency+p99+edge case rate。<br/>meta_observability<br/>文件: ops_governance/meta_observability.py<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_token_budget_py["令牌预算<br/>Token/Cost/Time三维预算;超预算拒绝<br/>token_budget<br/>文件: ops_governance/token_budget.py<br/>(生产态 / production)"]
    scripts_governance_observability_gate_cache_py ~~~ scripts_setup_dev_env_py
    scripts_setup_dev_env_py ~~~ src_zephyr_governance_observability_governance_observability_dashboard_py
    src_zephyr_governance_observability_governance_observability_dashboard_py ~~~ src_zephyr_governance_ops_governance_budget_engine_py
    src_zephyr_governance_ops_governance_budget_engine_py ~~~ src_zephyr_governance_ops_governance_budget_handler_py
    src_zephyr_governance_ops_governance_budget_handler_py ~~~ src_zephyr_governance_ops_governance_budget_profile_manager_py
    src_zephyr_governance_ops_governance_budget_profile_manager_py ~~~ src_zephyr_governance_ops_governance_budget_tracker_py
    src_zephyr_governance_ops_governance_budget_tracker_py ~~~ src_zephyr_governance_ops_governance_cost_budget_py
    src_zephyr_governance_ops_governance_cost_budget_py ~~~ src_zephyr_governance_ops_governance_meta_observability_py
    src_zephyr_governance_ops_governance_meta_observability_py ~~~ src_zephyr_governance_ops_governance_token_budget_py
    src_zephyr_governance_ops_governance_budget_models_py["预算模型<br/>预算执行器数据模型，定义预算限额、消耗记录与决策<br/>的 Pydantic 模型。<br/>文件: ops_governance/budget_models.py<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_budget_engine_py -->|导入依赖 / import_depends| src_zephyr_governance_ops_governance_budget_models_py
    src_zephyr_governance_ops_governance_budget_tracker_py -->|导入依赖 / import_depends| src_zephyr_governance_ops_governance_budget_models_py
    D_GOV_SCRIPTS["脚本治理<br/>脚本治理，负责脚本生命周期管理和脚本质量门禁<br/>Script Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    scripts_governance_observability_gate_cache_py -->|导入依赖 / import_depends| D_GOV_SCRIPTS
    scripts_governance_observability_gate_cache_py -->|导入依赖 / import_depends| D_GOV_SCRIPTS
    D_GOV_OPS_RESILIENCE["运维弹性治理<br/>运维弹性治理，负责运维治理、安全治理、弹性治理和<br/>升级协议<br/>Ops Resilience Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_budget_handler_py -->|导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_INFRA_RECOVERY["回滚恢复<br/>回滚恢复，负责系统故障时的状态回滚、事务补偿和恢<br/>复编排<br/>Rollback Recovery<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_budget_tracker_py -->|导入依赖 / import_depends| D_INFRA_RECOVERY
    D_GOV_DRIFT["漂移检测<br/>漂移检测，负责架构漂移检测和漂移告警<br/>Drift Detection<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_budget_engine_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_governance_ops_governance_budget_engine_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_budget_engine_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["生命周期管理<br/>生命周期管理，负责蓝图/模块<br/>/任务的声明周期管理和元数据治理<br/>Lifecycle Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_budget_handler_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_governance_ops_governance_budget_engine_py -->|导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    src_zephyr_governance_ops_governance_cost_budget_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_governance_ops_governance_budget_handler_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_governance_ops_governance_cost_budget_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_REPAIR["治理修复<br/>治理修复，负责治理问题自动修复和修复策略管理<br/>Governance Repair<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOV_REPAIR -->|导入依赖 / import_depends| src_zephyr_governance_ops_governance_budget_engine_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_governance_ops_governance_budget_engine_py
    D_GOV_ENFORCEMENT["规则执行<br/>规则执行，负责治理规则执行和门禁拦截<br/>Rule Enforcement<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_governance_ops_governance_budget_models_py
    D_INTEGRATION["管线路由<br/>管线路由，负责跨域数据流路由、管道编排和集成适配<br/>Pipeline Routing<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_governance_ops_governance_budget_engine_py
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_governance_ops_governance_budget_models_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_governance_ops_governance_budget_models_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_governance_ops_governance_budget_models_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_governance_ops_governance_budget_models_py
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_governance_ops_governance_budget_engine_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_governance_ops_governance_budget_engine_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_governance_ops_governance_budget_engine_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_governance_ops_governance_budget_models_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_governance_ops_governance_budget_models_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_governance_ops_governance_budget_models_py
    D_GOV_OPS_RESILIENCE -->|导入依赖 / import_depends| src_zephyr_governance_ops_governance_budget_models_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class scripts_governance_observability_gate_cache_py,scripts_setup_dev_env_py,src_zephyr_governance_observability_governance_observability_dashboard_py,src_zephyr_governance_ops_governance_budget_engine_py,src_zephyr_governance_ops_governance_budget_handler_py,src_zephyr_governance_ops_governance_budget_models_py,src_zephyr_governance_ops_governance_budget_profile_manager_py,src_zephyr_governance_ops_governance_budget_tracker_py,src_zephyr_governance_ops_governance_cost_budget_py,src_zephyr_governance_ops_governance_meta_observability_py,src_zephyr_governance_ops_governance_token_budget_py production
    class D_GOV_SCRIPTS,D_GOV_OPS_RESILIENCE,D_INFRA_RECOVERY,D_GOV_DRIFT,D_SHARED,D_GOVERNANCE,D_GOV_REPAIR,D_GOV_ENFORCEMENT,D_INTEGRATION external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 11 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    scripts_governance_observability_gate_cache_py["门禁缓存<br/>门禁结果缓存器，缓存门禁检查结果避免重复计算，提<br/>升 CI 流水线执行速度。<br/>文件: observability/gate_cache.py<br/>(生产态 / production)"]
    scripts_setup_dev_env_py["开发环境一次性初始化（裁定<br/>#ARCH-PYTHON-SITECUSTOMIZE<br/>开发环境一次性初始化。<br/>setup_dev_env<br/>文件: scripts/setup_dev_env.py<br/>(生产态 / production)"]
    src_zephyr_governance_observability_governance_observability_dashboard_py["可观测性仪表盘<br/>observability仪表盘，治理的核心类，封装Dashboard<br/>Panel相关逻辑。<br/>observability_dashboard<br/>文件: observability_governance<br/>/observability_dashboard.py<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_budget_engine_py["预算引擎<br/>运维管理<br/>文件: ops_governance/budget_engine.py<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_budget_handler_py["预算处理器<br/>G-CT-006 消费端 — Escalation.on_budget_alert()<br/>预算告急升级处理.<br/>budget_handler<br/>文件: ops_governance/budget_handler.py<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_budget_profile_manager_py["预算档案管理器<br/>治理管控（budget profile）<br/>budget_profile_manager<br/>文件: ops_governance/budget_profile_manager.py<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_budget_tracker_py["预算追踪器<br/>治理的追踪器，持续跟踪某项指标或状态的变化<br/>budget_tracker<br/>文件: ops_governance/budget_tracker.py<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_cost_budget_py["成本预算<br/>— AI 成本预算与强制熔断（Phase 11 / 盲点 B26）<br/>cost_budget<br/>文件: ops_governance/cost_budget.py<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_meta_observability_py["元可观测性<br/>Meta Observability — v0.10.0 协议自身可观测性:<br/>self loop latency+p99+edge case rate。<br/>meta_observability<br/>文件: ops_governance/meta_observability.py<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_token_budget_py["令牌预算<br/>Token/Cost/Time三维预算;超预算拒绝<br/>token_budget<br/>文件: ops_governance/token_budget.py<br/>(生产态 / production)"]
    scripts_governance_observability_gate_cache_py ~~~ scripts_setup_dev_env_py
    scripts_setup_dev_env_py ~~~ src_zephyr_governance_observability_governance_observability_dashboard_py
    src_zephyr_governance_observability_governance_observability_dashboard_py ~~~ src_zephyr_governance_ops_governance_budget_engine_py
    src_zephyr_governance_ops_governance_budget_engine_py ~~~ src_zephyr_governance_ops_governance_budget_handler_py
    src_zephyr_governance_ops_governance_budget_handler_py ~~~ src_zephyr_governance_ops_governance_budget_profile_manager_py
    src_zephyr_governance_ops_governance_budget_profile_manager_py ~~~ src_zephyr_governance_ops_governance_budget_tracker_py
    src_zephyr_governance_ops_governance_budget_tracker_py ~~~ src_zephyr_governance_ops_governance_cost_budget_py
    src_zephyr_governance_ops_governance_cost_budget_py ~~~ src_zephyr_governance_ops_governance_meta_observability_py
    src_zephyr_governance_ops_governance_meta_observability_py ~~~ src_zephyr_governance_ops_governance_token_budget_py
    src_zephyr_governance_ops_governance_budget_models_py["预算模型<br/>预算执行器数据模型，定义预算限额、消耗记录与决策<br/>的 Pydantic 模型。<br/>文件: ops_governance/budget_models.py<br/>(生产态 / production)"]
    src_zephyr_governance_ops_governance_budget_engine_py -->|导入依赖 / import_depends| src_zephyr_governance_ops_governance_budget_models_py
    src_zephyr_governance_ops_governance_budget_tracker_py -->|导入依赖 / import_depends| src_zephyr_governance_ops_governance_budget_models_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class scripts_governance_observability_gate_cache_py,scripts_setup_dev_env_py,src_zephyr_governance_observability_governance_observability_dashboard_py,src_zephyr_governance_ops_governance_budget_engine_py,src_zephyr_governance_ops_governance_budget_handler_py,src_zephyr_governance_ops_governance_budget_models_py,src_zephyr_governance_ops_governance_budget_profile_manager_py,src_zephyr_governance_ops_governance_budget_tracker_py,src_zephyr_governance_ops_governance_cost_budget_py,src_zephyr_governance_ops_governance_meta_observability_py,src_zephyr_governance_ops_governance_token_budget_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个），不含跨域外部节点。

> （无模块 / No modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 预算处理器 / budget_handler (ops_governance/budget_handle... | → | D_GOVERNANCE 生命周期管理: 适配器 / adapter (services/adapter.py) | 导入依赖 / import_depends |
| 2 | 预算引擎 / Budget Enforcer core engine — MOD-INF-024 (op... | → | D_GOV_DRIFT 漂移检测: 漂移基础设施 / drift_infrastructure (gov_drift/drift_infr... | 导入依赖 / import_depends |
| 3 | 预算引擎 / Budget Enforcer core engine — MOD-INF-024 (op... | → | D_GOV_DRIFT 漂移检测: 螺旋预警系统 / spiral_ews (gov_drift/spiral_ews.py) | 导入依赖 / import_depends |
| 4 | 预算引擎 / Budget Enforcer core engine — MOD-INF-024 (op... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: ipi防御 / ipi_defense (security_governance/ipi_defense.py) | 导入依赖 / import_depends |
| 5 | 预算处理器 / budget_handler (ops_governance/budget_handle... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 契约 / contracts (escalation/contracts.py) | 导入依赖 / import_depends |
| 6 | 门禁缓存 / Module docstring — see module-level docstring... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 7 | 门禁缓存 / Module docstring — see module-level docstring... | → | D_GOV_SCRIPTS 脚本治理: 文件工具 / file_utils (_shared/file_utils.py) | 导入依赖 / import_depends |
| 8 | 预算追踪器 / budget_tracker (ops_governance/budget_tracke... | → | D_INFRA_RECOVERY 回滚恢复: 预算追踪器 / budget_tracker (rollback/budget_tracker.py) | 导入依赖 / import_depends |
| 9 | 预算引擎 / Budget Enforcer core engine — MOD-INF-024 (op... | → | D_SHARED 共享服务: 事件总线 / event_bus (shared/event_bus.py) | 导入依赖 / import_depends |
| 10 | 预算处理器 / budget_handler (ops_governance/budget_handle... | → | D_SHARED 共享服务: 预算告警 / budget_alert (escalation/budget_alert.py) | 导入依赖 / import_depends |
| 11 | 成本预算 / cost_budget (ops_governance/cost_budget.py) | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 12 | 成本预算 / cost_budget (ops_governance/cost_budget.py) | → | D_SHARED 共享服务: 指标 / metrics (observability/metrics.py) | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_GOVERNANCE 生命周期管理: 模型提供器数据 / model_provider_data (intelligence_govern... | → | 预算模型 / Budget Enforcer data models — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 2 | D_GOVERNANCE 生命周期管理: 模型路由器 / model_router (intelligence_governance/model_... | → | 预算模型 / Budget Enforcer data models — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 3 | D_GOVERNANCE 生命周期管理: 治理服务端 / governance_server (mcp/governance_server.py) | → | 预算引擎 / Budget Enforcer core engine — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 4 | D_GOVERNANCE 生命周期管理: 治理服务端 / governance_server (mcp/governance_server.py) | → | 预算模型 / Budget Enforcer data models — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 5 | D_GOV_ENFORCEMENT 规则执行: preflight门禁 / pre_flight_gate (rule_enforcement/pre_fli... | → | 预算引擎 / Budget Enforcer core engine — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 6 | D_GOV_ENFORCEMENT 规则执行: preflight门禁 / pre_flight_gate (rule_enforcement/pre_fli... | → | 预算模型 / Budget Enforcer data models — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 7 | D_GOV_OPS_RESILIENCE 运维弹性治理: burn速率监控器 / Burn Rate Monitor — MOD-INF-024 (ops_go... | → | 预算模型 / Budget Enforcer data models — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 8 | D_GOV_OPS_RESILIENCE 运维弹性治理: 成本attributor / cost_attributor (ops_governance/cost_att... | → | 预算模型 / Budget Enforcer data models — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 9 | D_GOV_OPS_RESILIENCE 运维弹性治理: 退化管理器 / degradation_manager (ops_governance/degradat... | → | 预算模型 / Budget Enforcer data models — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 10 | D_GOV_OPS_RESILIENCE 运维弹性治理: 阶段检查注册表 / phase_check_registry (ops_governance/pha... | → | 预算引擎 / Budget Enforcer core engine — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 11 | D_GOV_OPS_RESILIENCE 运维弹性治理: 阶段检查注册表 / phase_check_registry (ops_governance/pha... | → | 预算模型 / Budget Enforcer data models — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 12 | D_GOV_OPS_RESILIENCE 运维弹性治理: 对抗测试器 / adversarial_tester (security_governance/adve... | → | 预算引擎 / Budget Enforcer core engine — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 13 | D_GOV_OPS_RESILIENCE 运维弹性治理: 对抗测试器 / adversarial_tester (security_governance/adve... | → | 预算模型 / Budget Enforcer data models — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 14 | D_GOV_REPAIR 治理修复: 预算执行 / budget_enforcement (financial_governance/budge... | → | 预算引擎 / Budget Enforcer core engine — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 15 | D_GOV_REPAIR 治理修复: 预算执行 / budget_enforcement (financial_governance/budge... | → | 预算模型 / Budget Enforcer data models — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 16 | D_GOV_REPAIR 治理修复: 预算执行 / budget_enforcement (financial_governance/budge... | → | 预算追踪器 / budget_tracker (ops_governance/budget_tracke... | 导入依赖 / import_depends |
| 17 | D_INFRA_RUNTIME 运行时集成: 启动钩子 / boot_hooks (trading/boot_hooks.py) | → | 预算引擎 / Budget Enforcer core engine — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 18 | D_INTEGRATION 管线路由: OllamaChat — 通过 Ollama HTTP API 进行本地 LLM / ollama_... | → | 预算引擎 / Budget Enforcer core engine — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 19 | D_INTEGRATION 管线路由: 管线编排器 / pipeline_orchestrator (integration/pipeline_... | → | 预算引擎 / Budget Enforcer core engine — MOD-INF-024 (op... | 导入依赖 / import_depends |
| 20 | D_INTEGRATION 管线路由: 管线编排器 / pipeline_orchestrator (integration/pipeline_... | → | 预算模型 / Budget Enforcer data models — MOD-INF-024 (op... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 10 个外部域直接连接（出边 12 条 + 入边 20 条 = 32 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_OPS["D_OPS<br/>反馈循环"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_GOV_DRIFT["D_GOV_DRIFT<br/>漂移检测"]
    D_GOV_OPS_RESILIENCE["D_GOV_OPS_RESILIENCE<br/>运维弹性治理"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_INFRA_RECOVERY["D_INFRA_RECOVERY<br/>回滚恢复"]
    D_GOV_REPAIR["D_GOV_REPAIR<br/>治理修复"]
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_OPS -->|4条 导入依赖 / import_depends| D_SHARED
    D_OPS -->|2条 导入依赖 / import_depends| D_GOV_DRIFT
    D_OPS -->|2条 导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_OPS -->|2条 导入依赖 / import_depends| D_GOV_SCRIPTS
    D_OPS -->|1条 导入依赖 / import_depends| D_GOVERNANCE
    D_OPS -->|1条 导入依赖 / import_depends| D_INFRA_RECOVERY
    D_GOV_OPS_RESILIENCE -->|7条 导入依赖 / import_depends| D_OPS
    D_GOVERNANCE -->|4条 导入依赖 / import_depends| D_OPS
    D_GOV_REPAIR -->|3条 导入依赖 / import_depends| D_OPS
    D_INTEGRATION -->|3条 导入依赖 / import_depends| D_OPS
    D_GOV_ENFORCEMENT -->|2条 导入依赖 / import_depends| D_OPS
    D_INFRA_RUNTIME -->|1条 导入依赖 / import_depends| D_OPS
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
