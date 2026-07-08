---
doc_type: architecture_view
title: D_OPS 反馈循环架构文档
version: "1.0"
status: active
date: 2026-07-09
owner: auto-generator
ttl: permanent
---

# 15_d_ops / telemetry / 反馈循环 / Feedback Loop

> **功能简介 / Overview**: 反馈循环，负责系统运行反馈、性能监控和自动调优闭环

> **文档作用 / Purpose**: 展示 反馈循环（D_OPS）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-09 04:34:12
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 15 | Number | 15 |
| 域ID | D_OPS | Domain ID | D_OPS |
| 域名称 | 反馈循环 | Domain Name | Feedback Loop |
| 层级 | L1 基础平台层 | Layer | L1 Foundation |
| 模块数 | 3 | Module Count | 3 |
| 域内依赖 | 0 | Internal Dependencies | 0 |
| 跨域入边 | 8 | Cross-domain Incoming | 8 |
| 跨域出边 | 2 | Cross-domain Outgoing | 2 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 0 | Prototype Modules | 0 |
| 生产态模块 | 3 | Production Modules | 3 |
| 容量 | 3/150 (正常) | Capacity | 3/150 (正常) |
| 描述 | 自动引导(auto_bootstrap) | Description | 自动引导(auto_bootstrap) |

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 3 个模块 / 3 modules）。

### L1 基础层 / Foundation Layer (3 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/shared/observability/metrics.py | metrics.py —— 轻量级 Metrics 收集基础设施（Ph... | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |
| 2 | src/zephyr/shared/observability/reasoning_spans.py | reasoning_spans.py | 生产态 / production |  |
| 3 | src/zephyr/shared/observability/tracing.py | tracing.py —— OpenTelemetry 分布式追踪（Phase... | 生产态 / production | [MOD-INF-016](../../03_modules/_cross_layer/shared_core/blueprint.md) |

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

> 展示全部 3 个模块（生产态 3 + 设计态 0 + 原型态 0），标签标注成熟度。

```mermaid
graph TD
    subgraph D_OPS["D_OPS 反馈循环"]
        src_zephyr_shared_observability_metrics_py["(生产态 / production) metrics.py —— 轻量级 Metrics 收集基础设施（Ph...<br/>文件: metrics.py"]
        src_zephyr_shared_observability_reasoning_spans_py["(生产态 / production) reasoning_spans.py"]
        src_zephyr_shared_observability_tracing_py["(生产态 / production) tracing.py —— OpenTelemetry 分布式追踪（Phase...<br/>文件: tracing.py"]
    end
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_shared_observability_metrics_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_shared_observability_tracing_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_shared_observability_metrics_py
    D_TRADING["(生产态 / production) D_TRADING"]
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_shared_observability_metrics_py
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_shared_observability_metrics_py
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_shared_observability_metrics_py
    D_AUDITTEST["(原型态 / prototype) D_AUDITTEST"]
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_shared_observability_metrics_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_shared_observability_metrics_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_shared_observability_metrics_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_shared_observability_tracing_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_shared_observability_metrics_py,src_zephyr_shared_observability_reasoning_spans_py,src_zephyr_shared_observability_tracing_py production
    class D_SHARED,D_GOVERNANCE,D_TRADING external_prod
    class D_AUDITTEST external_design
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 仅展示已上线运行的模块（共 3 个，0 条域内依赖）。

```mermaid
graph TD
    subgraph D_OPS["D_OPS 反馈循环"]
        src_zephyr_shared_observability_metrics_py["(生产态 / production) metrics.py —— 轻量级 Metrics 收集基础设施（Ph...<br/>文件: metrics.py"]
        src_zephyr_shared_observability_reasoning_spans_py["(生产态 / production) reasoning_spans.py"]
        src_zephyr_shared_observability_tracing_py["(生产态 / production) tracing.py —— OpenTelemetry 分布式追踪（Phase...<br/>文件: tracing.py"]
    end
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_shared_observability_metrics_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_shared_observability_tracing_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_shared_observability_metrics_py
    D_TRADING["(生产态 / production) D_TRADING"]
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_shared_observability_metrics_py
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_shared_observability_metrics_py
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_shared_observability_metrics_py
    D_AUDITTEST["(原型态 / prototype) D_AUDITTEST"]
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_shared_observability_metrics_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_shared_observability_metrics_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_shared_observability_metrics_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_shared_observability_tracing_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_shared_observability_metrics_py,src_zephyr_shared_observability_reasoning_spans_py,src_zephyr_shared_observability_tracing_py production
    class D_SHARED,D_GOVERNANCE,D_TRADING external_prod
    class D_AUDITTEST external_design
```

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个，0 条域内依赖）。

> （无设计态模块 / No design modules）

### 原型态子图（仅 design_maturity=prototype 的模块和依赖）

> 仅展示代码已写、验证中未稳定上线的原型态模块（共 0 个，0 条域内依赖）。

> （无原型态模块 / No prototype modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | metrics.py —— 轻量级 Metrics 收集基础设施（Ph... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (event... | 导入依赖 / import_depends |
| 2 | tracing.py —— OpenTelemetry 分布式追踪（Phase... | → | D_SHARED 共享服务: logging.py —— ZephyrAlpha 结构化日志系统（Str... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_AUDITTEST 审计测试套件: F21 自动启动测试 — DM-201250 (test_f21_auto_st... | → | metrics.py —— 轻量级 Metrics 收集基础设施（Ph... | 测试依赖 / test_depends |
| 2 | D_AUDITTEST 审计测试套件: F21 事件启动测试 — DM-201250 (test_f21_event_d... | → | metrics.py —— 轻量级 Metrics 收集基础设施（Ph... | 测试依赖 / test_depends |
| 3 | D_AUDITTEST 审计测试套件: test_observability_metrics.py | → | metrics.py —— 轻量级 Metrics 收集基础设施（Ph... | 测试依赖 / test_depends |
| 4 | D_AUDITTEST 审计测试套件: test_observability_tracing.py | → | tracing.py —— OpenTelemetry 分布式追踪（Phase... | 测试依赖 / test_depends |
| 5 | D_GOVERNANCE 生命周期管理: cost_budget.py —— AI 成本预算与强制熔断（Phas... | → | metrics.py —— 轻量级 Metrics 收集基础设施（Ph... | 导入依赖 / import_depends |
| 6 | D_TRADING 交易运营: boot_hooks.py | → | metrics.py —— 轻量级 Metrics 收集基础设施（Ph... | 导入依赖 / import_depends |
| 7 | D_TRADING 交易运营: Finalizer — 优雅清理器 (finalizer.py) | → | metrics.py —— 轻量级 Metrics 收集基础设施（Ph... | 导入依赖 / import_depends |
| 8 | D_TRADING 交易运营: HealthMonitor — 健康监控 + 自愈 (health_monito... | → | metrics.py —— 轻量级 Metrics 收集基础设施（Ph... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 4 个外部域直接连接（出边 2 条 + 入边 8 条 = 10 条）。只显示直接连接的域，不展开具体节点。

```mermaid
graph LR
    D_OPS["D_OPS<br/>反馈循环"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_AUDITTEST["D_AUDITTEST<br/>审计测试套件"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_OPS -->|2条 导入依赖 / import_depends| D_SHARED
    D_AUDITTEST -->|4条 测试依赖 / test_depends| D_OPS
    D_TRADING -->|3条 导入依赖 / import_depends| D_OPS
    D_GOVERNANCE -->|1条 导入依赖 / import_depends| D_OPS
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
