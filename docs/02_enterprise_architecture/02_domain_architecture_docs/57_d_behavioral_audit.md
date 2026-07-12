---
doc_type: architecture_view
title: D_BEHAVIORAL_AUDIT 行为审计架构文档
version: "1.0"
status: active
date: 2026-07-13
owner: auto-generator
ttl: permanent
---

# 57_d_behavioral_audit / drift_detector_core / 行为审计 / Behavioral Audit

> **功能简介 / Overview**: 行为审计，负责 AI 决策行为的可追溯审计和合规检查

> **文档作用 / Purpose**: 展示 行为审计（D_BEHAVIORAL_AUDIT）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-13 05:42:32
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 57 | Number | 57 |
| 域ID | D_BEHAVIORAL_AUDIT | Domain ID | D_BEHAVIORAL_AUDIT |
| 域名称 | 行为审计 | Domain Name | Behavioral Audit |
| 层级 |  | Layer |  |
| 模块数 | 1 | Module Count | 1 |
| 域内依赖 | 0 | Internal Dependencies | 0 |
| 跨域入边 | 0 | Cross-domain Incoming | 0 |
| 跨域出边 | 5 | Cross-domain Outgoing | 5 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 1 | Prototype Modules | 1 |
| 生产态模块 | 0 | Production Modules | 0 |
| 容量 | 0/150 (正常) | Capacity | 0/150 (正常) |
| 描述 | AI决策行为可追溯审计 | Description | AI决策行为可追溯审计 |

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 1 个模块 / 1 modules）。

### L2 领域层 / Domain Layer (1 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/governance/drift_detector_core/bridges/__init_... | __init__.py | 原型态 / prototype | [MOD-INF-023](../../03_modules/_domain_governance/drift_detector/blueprint.md) |

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

> 展示全部 1 个模块（生产态 0 + 设计态 0 + 原型态 1），标签标注成熟度。

```mermaid
graph TD
    subgraph D_BEHAVIORAL_AUDIT["D_BEHAVIORAL_AUDIT 行为审计"]
        src_zephyr_governance_drift_detector_core_bridges_init_py["(原型态 / prototype) __init__.py"]
    end
    D_GOV_DRIFT["(生产态 / production) D_GOV_DRIFT"]
    src_zephyr_governance_drift_detector_core_bridges_init_py -.->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_governance_drift_detector_core_bridges_init_py -.->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_governance_drift_detector_core_bridges_init_py -.->|导入依赖 / import_depends| D_GOV_DRIFT
    D_SECURITY["(原型态 / prototype) D_SECURITY"]
    src_zephyr_governance_drift_detector_core_bridges_init_py -.->|导入依赖 / import_depends| D_SECURITY
    src_zephyr_governance_drift_detector_core_bridges_init_py -.->|导入依赖 / import_depends| D_SECURITY
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_governance_drift_detector_core_bridges_init_py design
    class D_GOV_DRIFT external_prod
    class D_SECURITY external_design
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 仅展示已上线运行的模块（共 0 个，0 条域内依赖）。

> （无运营态模块 / No production modules）

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个，0 条域内依赖）。

> （无设计态模块 / No design modules）

### 原型态子图（仅 design_maturity=prototype 的模块和依赖）

> 仅展示代码已写、验证中未稳定上线的原型态模块（共 1 个，0 条域内依赖）。

```mermaid
graph TD
    subgraph D_BEHAVIORAL_AUDIT["D_BEHAVIORAL_AUDIT 行为审计"]
        src_zephyr_governance_drift_detector_core_bridges_init_py["(原型态 / prototype) __init__.py"]
    end
    D_GOV_DRIFT["(生产态 / production) D_GOV_DRIFT"]
    src_zephyr_governance_drift_detector_core_bridges_init_py -.->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_governance_drift_detector_core_bridges_init_py -.->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_governance_drift_detector_core_bridges_init_py -.->|导入依赖 / import_depends| D_GOV_DRIFT
    D_SECURITY["(原型态 / prototype) D_SECURITY"]
    src_zephyr_governance_drift_detector_core_bridges_init_py -.->|导入依赖 / import_depends| D_SECURITY
    src_zephyr_governance_drift_detector_core_bridges_init_py -.->|导入依赖 / import_depends| D_SECURITY
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_governance_drift_detector_core_bridges_init_py design
    class D_GOV_DRIFT external_prod
    class D_SECURITY external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | __init__.py | → | D_GOV_DRIFT 漂移检测: Drift Detector AI 施工检测器 — ai_construction... | 导入依赖 / import_depends |
| 2 | __init__.py | → | D_GOV_DRIFT 漂移检测: Drift Engine — 编排器核心 (SRC-0030 精简后) (d... | 导入依赖 / import_depends |
| 3 | __init__.py | → | D_GOV_DRIFT 漂移检测: Drift Detector 数据模型 — drift_models.py (dri... | 导入依赖 / import_depends |
| 4 | __init__.py | → | D_SECURITY 对抗验证: Auto Reconciler — reconciler.py (reconciler.py) | 导入依赖 / import_depends |
| 5 | __init__.py | → | D_SECURITY 对抗验证: Drift State Machine — state_machine.py (state_... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

无跨域入边依赖 / No cross-domain incoming dependencies

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 2 个外部域直接连接（出边 5 条 + 入边 0 条 = 5 条）。只显示直接连接的域，不展开具体节点。

```mermaid
graph LR
    D_BEHAVIORAL_AUDIT["D_BEHAVIORAL_AUDIT<br/>行为审计"]
    D_GOV_DRIFT["D_GOV_DRIFT<br/>漂移检测"]
    D_SECURITY["D_SECURITY<br/>对抗验证"]
    D_BEHAVIORAL_AUDIT -->|3条 导入依赖 / import_depends| D_GOV_DRIFT
    D_BEHAVIORAL_AUDIT -->|2条 导入依赖 / import_depends| D_SECURITY
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
