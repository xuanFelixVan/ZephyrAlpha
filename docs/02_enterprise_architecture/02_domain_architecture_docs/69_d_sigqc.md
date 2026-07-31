---
doc_type: architecture_view
title: D_SIGQC 信号质量控制架构文档
version: "1.0"
status: active
date: 2026-07-31
owner: auto-generator
ttl: permanent
---

# 69_d_sigqc / 信号质量控制 / Signal Quality Control

> **功能简介 / Overview**: 信号质量控制，负责信号质量评估、异常检测和质量门禁

> **文档作用 / Purpose**: 展示 信号质量控制（D_SIGQC）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 69 | Number | 69 |
| 域ID | D_SIGQC | Domain ID | D_SIGQC |
| 域名称 | 信号质量控制 | Domain Name | Signal Quality Control |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 2 | Module Count | 2 |
| 域内依赖 | 1 | Internal Dependencies | 1 |
| 跨域入边 | 0 | Cross-domain Incoming | 0 |
| 跨域出边 | 2 | Cross-domain Outgoing | 2 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 2 | Production Modules | 2 |
| 容量 | 2/150 (正常) | Capacity | 2/150 (正常) |
| 描述 | 信号质量评估 | Description | 信号质量评估 |

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 2 个模块 / 2 modules）。

### L2 领域层 / Domain Layer (2 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/signal_quality/__init__.py | D_SIGQC — Signal Quality Domain | 生产态 / production |  |
| 2 | src/zephyr/signal_quality/degradation_monitor_base.py | D_SIGQC — Signal Quality Degradation Monitor Base | 生产态 / production |  |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。参考 decision_index.md 设计，分三个视图：合并全景图、运营态子图、设计态子图（按 design_maturity 实际值拆分）。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 合并全景图（全部模块，标签标注成熟度）

> 展示全部 2 个模块（生产态 2 + 设计态 0），标签标注成熟度。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_signal_quality_init_py["(生产态 / production) D_SIGQC — Signal Quality Domain<br/>文件: signal_quality/__init__.py"]
    src_zephyr_signal_quality_degradation_monitor_base_py["(生产态 / production) D_SIGQC — Signal Quality Degradation Monitor Base<br/>文件: signal_quality/degradation_monitor_base.py"]
    src_zephyr_signal_quality_init_py -->|导入依赖 / import_depends| src_zephyr_signal_quality_degradation_monitor_base_py
    D_INFRASTRUCTURE["(生产态 / production) D_INFRASTRUCTURE 跨层契约基础设施"]
    src_zephyr_signal_quality_degradation_monitor_base_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    D_TRADING["(生产态 / production) D_TRADING 交易运营"]
    src_zephyr_signal_quality_degradation_monitor_base_py -->|导入依赖 / import_depends| D_TRADING
    classDef production fill:#e8edf2,stroke:#0277bd,stroke-width:2px,color:#1a1a1a
    classDef design fill:#f0ebe3,stroke:#bf360c,stroke-width:2px,color:#1a1a1a,stroke-dasharray: 5 5
    classDef external_prod fill:#e8efe9,stroke:#1b5e20,stroke-width:1px,color:#1a1a1a
    classDef external_design fill:#efe5ea,stroke:#880e4f,stroke-width:1px,color:#1a1a1a,stroke-dasharray: 5 5
    class src_zephyr_signal_quality_init_py,src_zephyr_signal_quality_degradation_monitor_base_py production
    class D_INFRASTRUCTURE,D_TRADING external_prod
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 仅展示已上线运行的模块（共 2 个，1 条域内依赖）。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_signal_quality_init_py["(生产态 / production) D_SIGQC — Signal Quality Domain<br/>文件: signal_quality/__init__.py"]
    src_zephyr_signal_quality_degradation_monitor_base_py["(生产态 / production) D_SIGQC — Signal Quality Degradation Monitor Base<br/>文件: signal_quality/degradation_monitor_base.py"]
    src_zephyr_signal_quality_init_py -->|导入依赖 / import_depends| src_zephyr_signal_quality_degradation_monitor_base_py
    D_INFRASTRUCTURE["(生产态 / production) D_INFRASTRUCTURE 跨层契约基础设施"]
    src_zephyr_signal_quality_degradation_monitor_base_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    D_TRADING["(生产态 / production) D_TRADING 交易运营"]
    src_zephyr_signal_quality_degradation_monitor_base_py -->|导入依赖 / import_depends| D_TRADING
    classDef production fill:#e8edf2,stroke:#0277bd,stroke-width:2px,color:#1a1a1a
    classDef design fill:#f0ebe3,stroke:#bf360c,stroke-width:2px,color:#1a1a1a,stroke-dasharray: 5 5
    classDef external_prod fill:#e8efe9,stroke:#1b5e20,stroke-width:1px,color:#1a1a1a
    classDef external_design fill:#efe5ea,stroke:#880e4f,stroke-width:1px,color:#1a1a1a,stroke-dasharray: 5 5
    class src_zephyr_signal_quality_init_py,src_zephyr_signal_quality_degradation_monitor_base_py production
    class D_INFRASTRUCTURE,D_TRADING external_prod
```

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个，0 条域内依赖）。

> （无设计态模块 / No design modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_SIGQC — Signal Quality Degradation Monitor B... | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/synthesized_signal.py | 导入依赖 / import_depends |
| 2 | D_SIGQC — Signal Quality Degradation Monitor B... | → | D_TRADING 交易运营: market/signal_degradation_warning.py | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

无跨域入边依赖 / No cross-domain incoming dependencies

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 2 个外部域直接连接（出边 2 条 + 入边 0 条 = 2 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_SIGQC["D_SIGQC<br/>信号质量控制"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE<br/>跨层契约基础设施"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_SIGQC -->|1条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_SIGQC -->|1条 导入依赖 / import_depends| D_TRADING
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
