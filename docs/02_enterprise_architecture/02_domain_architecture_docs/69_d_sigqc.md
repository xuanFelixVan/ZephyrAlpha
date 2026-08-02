---
doc_type: architecture_view
title: D_SIGQC 信号质量控制架构文档
version: "1.0"
status: active
date: 2026-08-02
owner: auto-generator
ttl: permanent
---

# 69_d_sigqc / 信号质量控制域 / Signal Quality Control

> **功能简介 / Overview**: 信号质量控制，负责信号质量评估、异常检测和质量门禁

> **文档作用 / Purpose**: 展示 信号质量控制（D_SIGQC）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/69_d_sigqc.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

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

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 2 个模块（生产态 2 + 设计态 0），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_signal_quality_init_py["zephyr/signal_quality 包入口<br/>信号质量域。负责信号质量评估/信号过滤/信号降级<br/>/信号冲突检测。<br/>D_SIGQC — Signal Quality Domain<br/>文件: signal_quality/__init__.py<br/>(生产态 / production)"]
    src_zephyr_signal_quality_degradation_monitor_base_py["退化监控基类<br/>信号质量降级监视器抽象基类（OCP 扩展点<br/>D_SIGQC-DEG）。<br/>文件: signal_quality/degradation_monitor_base.py<br/>(生产态 / production)"]
    src_zephyr_signal_quality_init_py -->|导入依赖 / import_depends| src_zephyr_signal_quality_degradation_monitor_base_py
    D_INFRASTRUCTURE["跨层契约基础设施<br/>跨层契约基础设施，负责跨层契约定义、共享契约管理<br/>和契约校验<br/>Cross-Layer Contract Infrastructure<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_signal_quality_degradation_monitor_base_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    D_TRADING["交易运营<br/>交易运营，负责交易生命周期管理、订单状态和成交处<br/>理<br/>Trading Operations<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_signal_quality_degradation_monitor_base_py -->|导入依赖 / import_depends| D_TRADING
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_signal_quality_init_py,src_zephyr_signal_quality_degradation_monitor_base_py production
    class D_INFRASTRUCTURE,D_TRADING external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 2 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_signal_quality_init_py["zephyr/signal_quality 包入口<br/>信号质量域。负责信号质量评估/信号过滤/信号降级<br/>/信号冲突检测。<br/>D_SIGQC — Signal Quality Domain<br/>文件: signal_quality/__init__.py<br/>(生产态 / production)"]
    src_zephyr_signal_quality_degradation_monitor_base_py["退化监控基类<br/>信号质量降级监视器抽象基类（OCP 扩展点<br/>D_SIGQC-DEG）。<br/>文件: signal_quality/degradation_monitor_base.py<br/>(生产态 / production)"]
    src_zephyr_signal_quality_init_py -->|导入依赖 / import_depends| src_zephyr_signal_quality_degradation_monitor_base_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_signal_quality_init_py,src_zephyr_signal_quality_degradation_monitor_base_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个），不含跨域外部节点。

> （无模块 / No modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 退化监控基类 / D_SIGQC — Signal Quality Degradation Moni... | → | D_INFRASTRUCTURE 跨层契约基础设施: synthesized信号 / synthesized_signal (contracts/synthesiz... | 导入依赖 / import_depends |
| 2 | 退化监控基类 / D_SIGQC — Signal Quality Degradation Moni... | → | D_TRADING 交易运营: 信号退化警告 / signal_degradation_warning (market/signal_... | 导入依赖 / import_depends |

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
