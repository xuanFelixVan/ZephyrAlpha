---
doc_type: architecture_view
title: D_GOV_AUDIT 审计追踪架构文档
version: "1.0"
status: active
date: 2026-07-12
owner: auto-generator
ttl: permanent
---

# 32_d_gov_audit / audit_orchestration / 审计追踪 / Audit Trail

> **功能简介 / Overview**: 审计追踪，负责变更审计追踪和操作日志管理

> **文档作用 / Purpose**: 展示 审计追踪（D_GOV_AUDIT）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-12 02:28:48
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 32 | Number | 32 |
| 域ID | D_GOV_AUDIT | Domain ID | D_GOV_AUDIT |
| 域名称 | 审计追踪 | Domain Name | Audit Trail |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 2 | Module Count | 2 |
| 域内依赖 | 0 | Internal Dependencies | 0 |
| 跨域入边 | 7 | Cross-domain Incoming | 7 |
| 跨域出边 | 5 | Cross-domain Outgoing | 5 |
| 设计态模块 | 2 | Design Modules | 2 |
| 原型态模块 | 0 | Prototype Modules | 0 |
| 生产态模块 | 0 | Production Modules | 0 |
| 容量 | 0/150 (正常) | Capacity | 0/150 (正常) |
| 描述 | 审计管线编排 | Description | 审计管线编排 |

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 2 个模块 / 2 modules）。

### L1 基础层 / Foundation Layer (2 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md | docs__03_modules___cross_layer__audit_orchestrator__blueprint_md | 设计态 / design | [MOD-INF-027](../../03_modules/_cross_layer/audit_orchestrator/blueprint.md) |
| 2 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | docs__03_modules___domain_governance__audit_trail__blueprint_md | 设计态 / design | [MOD-INF-020](../../03_modules/_domain_governance/audit_trail/blueprint.md) |

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

> 展示全部 2 个模块（生产态 0 + 设计态 2 + 原型态 0），标签标注成熟度。

```mermaid
graph TD
    subgraph D_GOV_AUDIT["D_GOV_AUDIT 审计追踪"]
        docs_03_modules_cross_layer_audit_orchestrator_blueprint_md["(设计态 / design) docs__03_modules___cross_layer__audit_orchestrator__blueprint_md"]
        docs_03_modules_domain_governance_audit_trail_blueprint_md["(设计态 / design) docs__03_modules___domain_governance__audit_trail__blueprint_md"]
    end
    D_GOVERNANCE["(设计态 / design) D_GOVERNANCE"]
    docs_03_modules_cross_layer_audit_orchestrator_blueprint_md -.->|runtime / runtime| D_GOVERNANCE
    docs_03_modules_domain_governance_audit_trail_blueprint_md -.->|runtime / runtime| D_GOVERNANCE
    docs_03_modules_domain_governance_audit_trail_blueprint_md -.->|runtime / runtime| D_GOVERNANCE
    docs_03_modules_domain_governance_audit_trail_blueprint_md -.->|contract / contract| D_GOVERNANCE
    D_GOV_DRIFT["(设计态 / design) D_GOV_DRIFT"]
    docs_03_modules_domain_governance_audit_trail_blueprint_md -.->|runtime / runtime| D_GOV_DRIFT
    D_GOVERNANCE -.->|contract / contract| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_GOV_DRIFT -.->|runtime / runtime| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_GOVERNANCE -.->|contract / contract| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_GOVERNANCE -.->|contract / contract| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_GOVERNANCE -.->|runtime / runtime| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_AUTONOMY_CORE["(生产态 / production) D_AUTONOMY_CORE"]
    D_AUTONOMY_CORE -.->|runtime / runtime| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_INFRA_TELEMETRY["(生产态 / production) D_INFRA_TELEMETRY"]
    D_INFRA_TELEMETRY -.->|runtime / runtime| docs_03_modules_domain_governance_audit_trail_blueprint_md
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_03_modules_cross_layer_audit_orchestrator_blueprint_md,docs_03_modules_domain_governance_audit_trail_blueprint_md design
    class D_AUTONOMY_CORE,D_INFRA_TELEMETRY external_prod
    class D_GOVERNANCE,D_GOV_DRIFT external_design
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 仅展示已上线运行的模块（共 0 个，0 条域内依赖）。

> （无运营态模块 / No production modules）

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 2 个，0 条域内依赖）。

```mermaid
graph TD
    subgraph D_GOV_AUDIT["D_GOV_AUDIT 审计追踪"]
        docs_03_modules_cross_layer_audit_orchestrator_blueprint_md["(设计态 / design) docs__03_modules___cross_layer__audit_orchestrator__blueprint_md"]
        docs_03_modules_domain_governance_audit_trail_blueprint_md["(设计态 / design) docs__03_modules___domain_governance__audit_trail__blueprint_md"]
    end
    D_GOVERNANCE["(设计态 / design) D_GOVERNANCE"]
    docs_03_modules_cross_layer_audit_orchestrator_blueprint_md -.->|runtime / runtime| D_GOVERNANCE
    docs_03_modules_domain_governance_audit_trail_blueprint_md -.->|runtime / runtime| D_GOVERNANCE
    docs_03_modules_domain_governance_audit_trail_blueprint_md -.->|runtime / runtime| D_GOVERNANCE
    docs_03_modules_domain_governance_audit_trail_blueprint_md -.->|contract / contract| D_GOVERNANCE
    D_GOV_DRIFT["(设计态 / design) D_GOV_DRIFT"]
    docs_03_modules_domain_governance_audit_trail_blueprint_md -.->|runtime / runtime| D_GOV_DRIFT
    D_GOVERNANCE -.->|contract / contract| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_GOV_DRIFT -.->|runtime / runtime| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_GOVERNANCE -.->|contract / contract| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_GOVERNANCE -.->|contract / contract| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_GOVERNANCE -.->|runtime / runtime| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_AUTONOMY_CORE["(生产态 / production) D_AUTONOMY_CORE"]
    D_AUTONOMY_CORE -.->|runtime / runtime| docs_03_modules_domain_governance_audit_trail_blueprint_md
    D_INFRA_TELEMETRY["(生产态 / production) D_INFRA_TELEMETRY"]
    D_INFRA_TELEMETRY -.->|runtime / runtime| docs_03_modules_domain_governance_audit_trail_blueprint_md
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_03_modules_cross_layer_audit_orchestrator_blueprint_md,docs_03_modules_domain_governance_audit_trail_blueprint_md design
    class D_AUTONOMY_CORE,D_INFRA_TELEMETRY external_prod
    class D_GOVERNANCE,D_GOV_DRIFT external_design
```

### 原型态子图（仅 design_maturity=prototype 的模块和依赖）

> 仅展示代码已写、验证中未稳定上线的原型态模块（共 0 个，0 条域内依赖）。

> （无原型态模块 / No prototype modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | blueprint.md | → | D_GOVERNANCE 生命周期管理: blueprint.md | runtime / runtime |
| 2 | blueprint.md | → | D_GOVERNANCE 生命周期管理: blueprint.md | runtime / runtime |
| 3 | blueprint.md | → | D_GOVERNANCE 生命周期管理: blueprint.md | runtime / runtime |
| 4 | blueprint.md | → | D_GOVERNANCE 生命周期管理: blueprint.md | contract / contract |
| 5 | blueprint.md | → | D_GOV_DRIFT 漂移检测: blueprint.md | runtime / runtime |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_AUTONOMY_CORE 自治核心: MOD-INF-019: Agent Spec — Agent Observability ... | → | blueprint.md | runtime / runtime |
| 2 | D_GOVERNANCE 生命周期管理: blueprint.md | → | blueprint.md | contract / contract |
| 3 | D_GOVERNANCE 生命周期管理: blueprint.md | → | blueprint.md | contract / contract |
| 4 | D_GOVERNANCE 生命周期管理: blueprint.md | → | blueprint.md | contract / contract |
| 5 | D_GOVERNANCE 生命周期管理: blueprint.md | → | blueprint.md | runtime / runtime |
| 6 | D_GOV_DRIFT 漂移检测: blueprint.md | → | blueprint.md | runtime / runtime |
| 7 | D_INFRA_TELEMETRY 可观测性: otel_instrumentation.py — 全链路 OTel (B12, DD... | → | blueprint.md | runtime / runtime |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 4 个外部域直接连接（出边 5 条 + 入边 7 条 = 12 条）。只显示直接连接的域，不展开具体节点。

```mermaid
graph LR
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_GOV_DRIFT["D_GOV_DRIFT<br/>漂移检测"]
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_INFRA_TELEMETRY["D_INFRA_TELEMETRY<br/>可观测性"]
    D_GOV_AUDIT -->|4条 contract / contract, runtime / runtime| D_GOVERNANCE
    D_GOV_AUDIT -->|1条 runtime / runtime| D_GOV_DRIFT
    D_GOVERNANCE -->|4条 contract / contract, runtime / runtime| D_GOV_AUDIT
    D_AUTONOMY_CORE -->|1条 runtime / runtime| D_GOV_AUDIT
    D_GOV_DRIFT -->|1条 runtime / runtime| D_GOV_AUDIT
    D_INFRA_TELEMETRY -->|1条 runtime / runtime| D_GOV_AUDIT
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
