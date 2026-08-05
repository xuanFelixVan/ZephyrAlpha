---
doc_type: architecture_view
title: D_COMPLIANCE 合规架构文档
version: "1.0"
status: active
date: 2026-08-05
owner: auto-generator
ttl: permanent
---

# 38_d_compliance / 合规域 / Compliance

> **功能简介 / Overview**: 合规，负责交易合规检查、规则引擎和合规报告

> **文档作用 / Purpose**: 展示 合规（D_COMPLIANCE）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/38_d_compliance.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 38 | Number | 38 |
| 域ID | D_COMPLIANCE | Domain ID | D_COMPLIANCE |
| 域名称 | 合规 | Domain Name | Compliance |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 10 | Module Count | 10 |
| 域内依赖 | 0 | Internal Dependencies | 0 |
| 跨域入边 | 0 | Cross-domain Incoming | 0 |
| 跨域出边 | 50 | Cross-domain Outgoing | 50 |
| 设计态模块 | 8 | Design Modules | 8 |
| 生产态模块 | 2 | Production Modules | 2 |
| 容量 | 2/150 (正常) | Capacity | 2/150 (正常) |
| 描述 | 合规校验引擎 | Description | 合规校验引擎 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 10 个模块（生产态 2 + 设计态 8），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_compliance_async_intercept_queue_py["异步intercept队列<br/>合规的同步器，保持数据同步一致<br/>⛔ 合规域，设计已就绪，等待开发排期<br/>async_intercept_queue<br/>文件: compliance/async_intercept_queue.py<br/>(设计态 / design)"]
    src_zephyr_compliance_behavioral_auditor_init_py["compliance/behavioral_auditor 包入口<br/>审计的包入口，把这一层的子模块归到一起统一管理，<br/>用到谁才加载谁，避免一次性全加载拖慢启动。<br/>文件: behavioral_auditor/__init__.py<br/>(生产态 / production)"]
    src_zephyr_compliance_compliance_continuous_ops_py["compliance/compliance_continuous_ops<br/>compliance包的compliance_continuous_ops模块<br/>文件: compliance/compliance_continuous_ops.py<br/>(设计态 / design)"]
    src_zephyr_compliance_compliance_tech_enabler_py["compliance/compliance_tech_enabler<br/>compliance包的compliance_tech_enabler模块<br/>文件: compliance/compliance_tech_enabler.py<br/>(设计态 / design)"]
    src_zephyr_compliance_discipline_must_do_checker_py["compliance/discipline_must_do_checker<br/>compliance包的discipline_must_do_checker模块<br/>文件: compliance/discipline_must_do_checker.py<br/>(设计态 / design)"]
    src_zephyr_compliance_discipline_prohibition_checker_py["compliance/discipline_prohibition_checker<br/>compliance包的discipline_prohibition_checker模块<br/>文件: compliance<br/>/discipline_prohibition_checker.py<br/>(设计态 / design)"]
    src_zephyr_compliance_eu_ai_act_ruling_py["compliance/eu_ai_act_ruling<br/>compliance包的eu_ai_act_ruling模块<br/>文件: compliance/eu_ai_act_ruling.py<br/>(设计态 / design)"]
    src_zephyr_compliance_hard_boundary_adjudicator_py["compliance/hard_boundary_adjudicator<br/>compliance包的hard_boundary_adjudicator模块<br/>文件: compliance/hard_boundary_adjudicator.py<br/>(设计态 / design)"]
    src_zephyr_compliance_trading_compliance_detector_py["compliance/trading_compliance_detector<br/>compliance包的trading_compliance_detector模块<br/>文件: compliance/trading_compliance_detector.py<br/>(设计态 / design)"]
    src_zephyr_compliance_zero_knowledge_audit_stub_init_py["compliance/zero_knowledge_audit_stub 包入口<br/>域量化架构 · D_COMPLIANCE 合规层<br/>D_COMPLIANCE Compliance<br/>文件: zero_knowledge_audit_stub/__init__.py<br/>(生产态 / production)"]
    src_zephyr_compliance_async_intercept_queue_py ~~~ src_zephyr_compliance_behavioral_auditor_init_py
    src_zephyr_compliance_behavioral_auditor_init_py ~~~ src_zephyr_compliance_compliance_continuous_ops_py
    src_zephyr_compliance_compliance_continuous_ops_py ~~~ src_zephyr_compliance_compliance_tech_enabler_py
    src_zephyr_compliance_compliance_tech_enabler_py ~~~ src_zephyr_compliance_discipline_must_do_checker_py
    src_zephyr_compliance_discipline_must_do_checker_py ~~~ src_zephyr_compliance_discipline_prohibition_checker_py
    src_zephyr_compliance_discipline_prohibition_checker_py ~~~ src_zephyr_compliance_eu_ai_act_ruling_py
    src_zephyr_compliance_eu_ai_act_ruling_py ~~~ src_zephyr_compliance_hard_boundary_adjudicator_py
    src_zephyr_compliance_hard_boundary_adjudicator_py ~~~ src_zephyr_compliance_trading_compliance_detector_py
    src_zephyr_compliance_trading_compliance_detector_py ~~~ src_zephyr_compliance_zero_knowledge_audit_stub_init_py
    D_GOV_OPS_RESILIENCE["运维弹性治理<br/>运维弹性治理，负责运维治理、安全治理、弹性治理和<br/>升级协议<br/>Ops Resilience Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_compliance_async_intercept_queue_py -.->|runtime / runtime| D_GOV_OPS_RESILIENCE
    D_GOV_DRIFT["漂移检测<br/>漂移检测，负责架构漂移检测和漂移告警<br/>Drift Detection<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_compliance_behavioral_auditor_init_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_compliance_behavioral_auditor_init_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_compliance_behavioral_auditor_init_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_compliance_behavioral_auditor_init_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_compliance_behavioral_auditor_init_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_compliance_behavioral_auditor_init_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_compliance_behavioral_auditor_init_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_compliance_behavioral_auditor_init_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_compliance_behavioral_auditor_init_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_compliance_behavioral_auditor_init_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    D_SECURITY["对抗验证<br/>对抗验证，负责系统安全对抗测试、漏洞扫描和攻防验<br/>证<br/>Adversarial Validation<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_compliance_behavioral_auditor_init_py -->|导入依赖 / import_depends| D_SECURITY
    src_zephyr_compliance_behavioral_auditor_init_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_compliance_behavioral_auditor_init_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_compliance_behavioral_auditor_init_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_compliance_behavioral_auditor_init_py,src_zephyr_compliance_zero_knowledge_audit_stub_init_py production
    class src_zephyr_compliance_async_intercept_queue_py,src_zephyr_compliance_compliance_continuous_ops_py,src_zephyr_compliance_compliance_tech_enabler_py,src_zephyr_compliance_discipline_must_do_checker_py,src_zephyr_compliance_discipline_prohibition_checker_py,src_zephyr_compliance_eu_ai_act_ruling_py,src_zephyr_compliance_hard_boundary_adjudicator_py,src_zephyr_compliance_trading_compliance_detector_py design
    class D_GOV_OPS_RESILIENCE,D_GOV_DRIFT,D_SECURITY external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 2 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_compliance_behavioral_auditor_init_py["compliance/behavioral_auditor 包入口<br/>审计的包入口，把这一层的子模块归到一起统一管理，<br/>用到谁才加载谁，避免一次性全加载拖慢启动。<br/>文件: behavioral_auditor/__init__.py<br/>(生产态 / production)"]
    src_zephyr_compliance_zero_knowledge_audit_stub_init_py["compliance/zero_knowledge_audit_stub 包入口<br/>域量化架构 · D_COMPLIANCE 合规层<br/>D_COMPLIANCE Compliance<br/>文件: zero_knowledge_audit_stub/__init__.py<br/>(生产态 / production)"]
    src_zephyr_compliance_behavioral_auditor_init_py ~~~ src_zephyr_compliance_zero_knowledge_audit_stub_init_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_compliance_behavioral_auditor_init_py,src_zephyr_compliance_zero_knowledge_audit_stub_init_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 8 个），不含跨域外部节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_compliance_async_intercept_queue_py["异步intercept队列<br/>合规的同步器，保持数据同步一致<br/>⛔ 合规域，设计已就绪，等待开发排期<br/>async_intercept_queue<br/>文件: compliance/async_intercept_queue.py<br/>(设计态 / design)"]
    src_zephyr_compliance_compliance_continuous_ops_py["compliance/compliance_continuous_ops<br/>compliance包的compliance_continuous_ops模块<br/>文件: compliance/compliance_continuous_ops.py<br/>(设计态 / design)"]
    src_zephyr_compliance_compliance_tech_enabler_py["compliance/compliance_tech_enabler<br/>compliance包的compliance_tech_enabler模块<br/>文件: compliance/compliance_tech_enabler.py<br/>(设计态 / design)"]
    src_zephyr_compliance_discipline_must_do_checker_py["compliance/discipline_must_do_checker<br/>compliance包的discipline_must_do_checker模块<br/>文件: compliance/discipline_must_do_checker.py<br/>(设计态 / design)"]
    src_zephyr_compliance_discipline_prohibition_checker_py["compliance/discipline_prohibition_checker<br/>compliance包的discipline_prohibition_checker模块<br/>文件: compliance<br/>/discipline_prohibition_checker.py<br/>(设计态 / design)"]
    src_zephyr_compliance_eu_ai_act_ruling_py["compliance/eu_ai_act_ruling<br/>compliance包的eu_ai_act_ruling模块<br/>文件: compliance/eu_ai_act_ruling.py<br/>(设计态 / design)"]
    src_zephyr_compliance_hard_boundary_adjudicator_py["compliance/hard_boundary_adjudicator<br/>compliance包的hard_boundary_adjudicator模块<br/>文件: compliance/hard_boundary_adjudicator.py<br/>(设计态 / design)"]
    src_zephyr_compliance_trading_compliance_detector_py["compliance/trading_compliance_detector<br/>compliance包的trading_compliance_detector模块<br/>文件: compliance/trading_compliance_detector.py<br/>(设计态 / design)"]
    src_zephyr_compliance_async_intercept_queue_py ~~~ src_zephyr_compliance_compliance_continuous_ops_py
    src_zephyr_compliance_compliance_continuous_ops_py ~~~ src_zephyr_compliance_compliance_tech_enabler_py
    src_zephyr_compliance_compliance_tech_enabler_py ~~~ src_zephyr_compliance_discipline_must_do_checker_py
    src_zephyr_compliance_discipline_must_do_checker_py ~~~ src_zephyr_compliance_discipline_prohibition_checker_py
    src_zephyr_compliance_discipline_prohibition_checker_py ~~~ src_zephyr_compliance_eu_ai_act_ruling_py
    src_zephyr_compliance_eu_ai_act_ruling_py ~~~ src_zephyr_compliance_hard_boundary_adjudicator_py
    src_zephyr_compliance_hard_boundary_adjudicator_py ~~~ src_zephyr_compliance_trading_compliance_detector_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_compliance_async_intercept_queue_py,src_zephyr_compliance_compliance_continuous_ops_py,src_zephyr_compliance_compliance_tech_enabler_py,src_zephyr_compliance_discipline_must_do_checker_py,src_zephyr_compliance_discipline_prohibition_checker_py,src_zephyr_compliance_eu_ai_act_ruling_py,src_zephyr_compliance_hard_boundary_adjudicator_py,src_zephyr_compliance_trading_compliance_detector_py design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: Absence管理器 / Absence Manager (gov_drift/absence_manage... | 导入依赖 / import_depends |
| 2 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: AiConstruction检测器 / Ai Construction Detectors (gov_dri... | 导入依赖 / import_depends |
| 3 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: Ai上下文注入器 / Ai Context Injector (gov_drift/ai_contex... | 导入依赖 / import_depends |
| 4 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: Backcompat检查器 / Backcompat Checker (gov_drift/backcomp... | 导入依赖 / import_depends |
| 5 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 只读：baselines_root / Baseline Manager (gov_drift/baseli... | 导入依赖 / import_depends |
| 6 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 基线Poisoning守卫 / Baseline Poisoning Guard (gov_drift/b... | 导入依赖 / import_depends |
| 7 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: Canary控制器 / Canary Controller (gov_drift/canary_contro... | 导入依赖 / import_depends |
| 8 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 级联检测器 / Cascade Detector (gov_drift/cascade_detector... | 导入依赖 / import_depends |
| 9 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 混沌注入器 / Chaos Injector (gov_drift/chaos_injector.py) | 导入依赖 / import_depends |
| 10 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 配置一致性 / Config Consistency (gov_drift/config_consist... | 导入依赖 / import_depends |
| 11 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 契约漂移检测器 / Contract Drift Detector (gov_drift/contr... | 导入依赖 / import_depends |
| 12 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 只读：db_path / Correlation Engine (gov_drift/correlation... | 导入依赖 / import_depends |
| 13 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: Credibility引擎 / Credibility Engine (gov_drift/credibili... | 导入依赖 / import_depends |
| 14 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 只读：history / Cross Module Score (gov_drift/cross_modul... | 导入依赖 / import_depends |
| 15 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 仪表盘 / Dashboard (gov_drift/dashboard.py) | 导入依赖 / import_depends |
| 16 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 只读：max_parallel / Detector Dispatcher (gov_drift/detec... | 导入依赖 / import_depends |
| 17 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 漂移引擎 / Drift Engine (gov_drift/drift_engine.py) | 导入依赖 / import_depends |
| 18 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 只读：audit_dir / Drift Hotfix Bypass (gov_drift/drift_ho... | 导入依赖 / import_depends |
| 19 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 漂移基础设施 / Drift Infrastructure (gov_drift/drift_infr... | 导入依赖 / import_depends |
| 20 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 漂移模型 / Drift Models (gov_drift/drift_models.py) | 导入依赖 / import_depends |
| 21 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 语义漂移检测结果 / Drift Result Types (gov_drift/drift_re... | 导入依赖 / import_depends |
| 22 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 从重复漂移事件中提取的可训练模式 / Drift Training (gov_dr... | 导入依赖 / import_depends |
| 23 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 文件Attr检查器 / File Attr Checker (gov_drift/file_attr_c... | 导入依赖 / import_depends |
| 24 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 重放baseline历史，重构时间线 / Forensics Engine (gov_drif... | 导入依赖 / import_depends |
| 25 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 只读：project_root / Gate Persistence (gov_drift/gate_per... | 导入依赖 / import_depends |
| 26 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 只读：cache / Git Bisector (gov_drift/git_bisector.py) | 导入依赖 / import_depends |
| 27 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: Gitignore审计器 / Gitignore Auditor (gov_drift/gitignore_... | 导入依赖 / import_depends |
| 28 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 构建跨Session交接包 / Handoff Manager (gov_drift/handoff_... | 导入依赖 / import_depends |
| 29 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: Headless扫描器 / Headless Scanner (gov_drift/headless_sca... | 导入依赖 / import_depends |
| 30 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 只读：project_root / Incremental Scanner (gov_drift/incre... | 导入依赖 / import_depends |
| 31 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: NamingMagic检查器 / Naming Magic Checker (gov_drift/namin... | 导入依赖 / import_depends |
| 32 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 孤儿扫描器 / Orphan Scanner (gov_drift/orphan_scanner.py) | 导入依赖 / import_depends |
| 33 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: Python Compat (gov_drift/python_compat.py) | 导入依赖 / import_depends |
| 34 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 资源守卫 / Resource Guard (gov_drift/resource_guard.py) | 导入依赖 / import_depends |
| 35 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 只读：effort_feedback / Roi Engine (gov_drift/roi_engine.py) | 导入依赖 / import_depends |
| 36 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 行为漂移->回滚触发. / Rollback Bridge (gov_drift/rollback... | 导入依赖 / import_depends |
| 37 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 只读：lock_dir / Scan Mutex (gov_drift/scan_mutex.py) | 导入依赖 / import_depends |
| 38 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: Self检查 / Self Check (gov_drift/self_check.py) | 导入依赖 / import_depends |
| 39 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 只读：patterns / Suppression Learner (gov_drift/suppressi... | 导入依赖 / import_depends |
| 40 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: Symlink检查器 / Symlink Checker (gov_drift/symlink_checke... | 导入依赖 / import_depends |
| 41 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: TamperProof审计 / Tamper Proof Audit (gov_drift/tamper_pr... | 导入依赖 / import_depends |
| 42 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 检查测试夹具中硬编码数据结构是否与 ORM/pydantic schema 一... | 导入依赖 / import_depends |
| 43 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_GOV_DRIFT 漂移检测: 只读：archive_dir / Trend Analyzer (gov_drift/trend_analy... | 导入依赖 / import_depends |
| 44 | 异步intercept队列 / async_intercept_queue (compliance/asy... | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 审计动作类型 / Security Gateway Base (security_governance... | runtime / runtime |
| 45 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_INFRA_RUNTIME 运行时集成: 状态Machine / State Machine (auto_fix_engine/state_machin... | 导入依赖 / import_depends |
| 46 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_SECURITY 对抗验证: Alert路由器 / Alert Router (gov_drift/alert_router.py) | 导入依赖 / import_depends |
| 47 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_SECURITY 对抗验证: 冷启动 / Cold Start (gov_drift/cold_start.py) | 导入依赖 / import_depends |
| 48 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_SECURITY 对抗验证: ManagedDriftEvent Pydantic V2 BaseModel 漂移事件定义. / E... | 导入依赖 / import_depends |
| 49 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_SECURITY 对抗验证: 对账器 / Reconciler (gov_drift/reconciler.py) | 导入依赖 / import_depends |
| 50 | 包入口 / __init__ (behavioral_auditor/__init__.py) | → | D_SECURITY 对抗验证: 构造 YAML frontmatter / Runbook Generator (gov_drift/runb... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

无跨域入边依赖 / No cross-domain incoming dependencies

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 4 个外部域直接连接（出边 50 条 + 入边 0 条 = 50 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_COMPLIANCE["D_COMPLIANCE<br/>合规"]
    D_GOV_DRIFT["D_GOV_DRIFT<br/>漂移检测"]
    D_SECURITY["D_SECURITY<br/>对抗验证"]
    D_GOV_OPS_RESILIENCE["D_GOV_OPS_RESILIENCE<br/>运维弹性治理"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_COMPLIANCE -->|43条 导入依赖 / import_depends| D_GOV_DRIFT
    D_COMPLIANCE -->|5条 导入依赖 / import_depends| D_SECURITY
    D_COMPLIANCE -->|1条 runtime / runtime| D_GOV_OPS_RESILIENCE
    D_COMPLIANCE -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
