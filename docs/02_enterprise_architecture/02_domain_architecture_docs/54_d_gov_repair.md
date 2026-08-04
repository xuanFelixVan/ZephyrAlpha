---
doc_type: architecture_view
title: D_GOV_REPAIR 治理修复架构文档
version: "1.0"
status: active
date: 2026-08-04
owner: auto-generator
ttl: permanent
---

# 54_d_gov_repair / 治理修复域 / Governance Repair

> **功能简介 / Overview**: 治理修复，负责治理问题自动修复和修复策略管理

> **文档作用 / Purpose**: 展示 治理修复（D_GOV_REPAIR）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/54_d_gov_repair.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 54 | Number | 54 |
| 域ID | D_GOV_REPAIR | Domain ID | D_GOV_REPAIR |
| 域名称 | 治理修复 | Domain Name | Governance Repair |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 1 | Module Count | 1 |
| 域内依赖 | 0 | Internal Dependencies | 0 |
| 跨域入边 | 4 | Cross-domain Incoming | 4 |
| 跨域出边 | 8 | Cross-domain Outgoing | 8 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 1 | Production Modules | 1 |
| 容量 | 1/150 (正常) | Capacity | 1/150 (正常) |
| 描述 | 双轨Checkpoint(git commit + SQLite JSONL dump) | Description | 双轨Checkpoint(git commit + SQLite JSONL dump) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 1 个模块（生产态 1 + 设计态 0），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_governance_financial_governance_budget_enforcement_py["延迟导入 BudgetEngine 避免循环依赖.'''<br/>治理/financial<br/>governance包的budget_enforcement模块<br/>Budget Enforcement<br/>文件: financial_governance/budget_enforcement.py<br/>(生产态 / production)"]
    D_GOV_OPS_RESILIENCE["运维弹性治理<br/>运维弹性治理，负责运维治理、安全治理、弹性治理和<br/>升级协议<br/>Ops Resilience Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_OPS["反馈循环<br/>反馈循环，负责系统运行反馈、性能监控和自动调优闭<br/>环<br/>Feedback Loop<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_OPS
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_OPS
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_OPS
    D_AUTONOMY_CORE["自治核心<br/>自治核心，负责 AI 自治决策、目标分解和执行编排<br/>Autonomy Core<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_AUTONOMY_CORE
    D_GOVERNANCE["生命周期管理<br/>生命周期管理，负责蓝图/模块<br/>/任务的声明周期管理和元数据治理<br/>Lifecycle Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_governance_financial_governance_budget_enforcement_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_GOV_OPS_RESILIENCE -->|测试依赖 / test_depends| src_zephyr_governance_financial_governance_budget_enforcement_py
    D_GOV_OPS_RESILIENCE -->|测试依赖 / test_depends| src_zephyr_governance_financial_governance_budget_enforcement_py
    D_GOV_SCRIPTS["脚本治理<br/>脚本治理，负责脚本生命周期管理和脚本质量门禁<br/>Script Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_governance_financial_governance_budget_enforcement_py
    D_INFRA_RUNTIME["运行时集成<br/>运行时集成，负责组件生命周期编排、启动钩子和运行<br/>时上下文管理<br/>Runtime Integration<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_governance_financial_governance_budget_enforcement_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_governance_financial_governance_budget_enforcement_py production
    class D_GOV_OPS_RESILIENCE,D_OPS,D_AUTONOMY_CORE,D_GOVERNANCE,D_GOV_SCRIPTS,D_INFRA_RUNTIME external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 1 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_governance_financial_governance_budget_enforcement_py["延迟导入 BudgetEngine 避免循环依赖.'''<br/>治理/financial<br/>governance包的budget_enforcement模块<br/>Budget Enforcement<br/>文件: financial_governance/budget_enforcement.py<br/>(生产态 / production)"]
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_governance_financial_governance_budget_enforcement_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个），不含跨域外部节点。

> （无模块 / No modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 延迟导入 BudgetEngine 避免循环依赖. / Budget Enforcement ... | → | D_AUTONOMY_CORE 自治核心: 技能执行器 / skill_executor (skills/skill_executor.py) | 导入依赖 / import_depends |
| 2 | 延迟导入 BudgetEngine 避免循环依赖. / Budget Enforcement ... | → | D_GOVERNANCE 生命周期管理: 模型路由器 / model_router (intelligence_governance/model_... | 导入依赖 / import_depends |
| 3 | 延迟导入 BudgetEngine 避免循环依赖. / Budget Enforcement ... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 公共接口：wasserstein_1d / Burn Rate Monitor (ops_governa... | 导入依赖 / import_depends |
| 4 | 延迟导入 BudgetEngine 避免循环依赖. / Budget Enforcement ... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: Degradation管理器 / Degradation Manager (ops_governance/d... | 导入依赖 / import_depends |
| 5 | 延迟导入 BudgetEngine 避免循环依赖. / Budget Enforcement ... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 只读：timeouts / Timeout Guard (ops_governance/timeout_gu... | 导入依赖 / import_depends |
| 6 | 延迟导入 BudgetEngine 避免循环依赖. / Budget Enforcement ... | → | D_OPS 反馈循环: —5.133.2 DI 注入契约 / Budget Engine (ops_governance/bud... | 导入依赖 / import_depends |
| 7 | 延迟导入 BudgetEngine 避免循环依赖. / Budget Enforcement ... | → | D_OPS 反馈循环: 预算模型 / Budget Models (ops_governance/budget_models.py) | 导入依赖 / import_depends |
| 8 | 延迟导入 BudgetEngine 避免循环依赖. / Budget Enforcement ... | → | D_OPS 反馈循环: 预算跟踪器 / Budget Tracker (ops_governance/budget_tracke... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_GOV_OPS_RESILIENCE 运维弹性治理: 预算EnforcerSmoke测试 / Test Budget Enforcer Smoke (budge... | → | 延迟导入 BudgetEngine 避免循环依赖. / Budget Enforcement ... | 测试依赖 / test_depends |
| 2 | D_GOV_OPS_RESILIENCE 运维弹性治理: GCT-024 硬检查：验证 BudgetEngine 实例化、三维覆盖、策略... | → | 延迟导入 BudgetEngine 避免循环依赖. / Budget Enforcement ... | 测试依赖 / test_depends |
| 3 | D_GOV_SCRIPTS 脚本治理: 检查预算Health / Check Budget Health (d5_architecture/che... | → | 延迟导入 BudgetEngine 避免循环依赖. / Budget Enforcement ... | 导入依赖 / import_depends |
| 4 | D_INFRA_RUNTIME 运行时集成: budget_enforcement 包聚合层 / Init (budget_enforcement/__... | → | 延迟导入 BudgetEngine 避免循环依赖. / Budget Enforcement ... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 6 个外部域直接连接（出边 8 条 + 入边 4 条 = 12 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_GOV_REPAIR["D_GOV_REPAIR<br/>治理修复"]
    D_GOV_OPS_RESILIENCE["D_GOV_OPS_RESILIENCE<br/>运维弹性治理"]
    D_OPS["D_OPS<br/>反馈循环"]
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_GOV_REPAIR -->|3条 导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_GOV_REPAIR -->|3条 导入依赖 / import_depends| D_OPS
    D_GOV_REPAIR -->|1条 导入依赖 / import_depends| D_AUTONOMY_CORE
    D_GOV_REPAIR -->|1条 导入依赖 / import_depends| D_GOVERNANCE
    D_GOV_OPS_RESILIENCE -->|2条 测试依赖 / test_depends| D_GOV_REPAIR
    D_GOV_SCRIPTS -->|1条 导入依赖 / import_depends| D_GOV_REPAIR
    D_INFRA_RUNTIME -->|1条 导入依赖 / import_depends| D_GOV_REPAIR
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
