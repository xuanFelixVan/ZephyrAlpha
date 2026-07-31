---
doc_type: architecture_view
title: D_FUNDAMENTAL_SIGNAL 基本面信号架构文档
version: "1.0"
status: active
date: 2026-08-01
owner: auto-generator
ttl: permanent
---

# 48_d_fundamental_signal / 基本面信号域 / Fundamental Signal

> **功能简介 / Overview**: 基本面信号，负责基于财务数据的基本面信号生成

> **文档作用 / Purpose**: 展示 基本面信号（D_FUNDAMENTAL_SIGNAL）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/48_d_fundamental_signal.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 48 | Number | 48 |
| 域ID | D_FUNDAMENTAL_SIGNAL | Domain ID | D_FUNDAMENTAL_SIGNAL |
| 域名称 | 基本面信号 | Domain Name | Fundamental Signal |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 10 | Module Count | 10 |
| 域内依赖 | 6 | Internal Dependencies | 6 |
| 跨域入边 | 2 | Cross-domain Incoming | 2 |
| 跨域出边 | 18 | Cross-domain Outgoing | 18 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 10 | Production Modules | 10 |
| 容量 | 10/150 (正常) | Capacity | 10/150 (正常) |
| 描述 | 财务指标信号 | Description | 财务指标信号 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。含三个视图：全景图（颜色区分运营态/设计态）+ 运营态子图 + 设计态子图；全景图不分页。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景依赖图（全部模块，颜色区分运营态/设计态）

> 展示全部 10 个模块（生产态 10 + 设计态 0），节点含成熟度+中英文名+大白话+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_signal_fundamental_init_py["(生产态 / production) D_SIGNAL Signal Domain<br/>D_SIGNAL Signal Domain<br/>文件: signal_fundamental/__init__.py"]
    src_zephyr_signal_fundamental_capital_capital_allocation_result_py["(生产态 / production) D_FUNDAMENTAL_SIGNAL — CapitalAllocationResult re-export shim<br/>D_FUNDAMENTAL_SIGNAL — CapitalAllocationResult re-export shim<br/>文件: capital/capital_allocation_result.py"]
    src_zephyr_signal_fundamental_capital_capital_allocator_py["(生产态 / production) D_SIGNAL — Capital Allocator（兼容 re-export shim）<br/>D_SIGNAL — Capital Allocator（兼容 re-export shim）<br/>文件: capital/capital_allocator.py"]
    src_zephyr_signal_fundamental_capital_default_capital_allocator_py["(生产态 / production) D_SIGNAL — Default Capital Allocator（兼容 re-export shim）<br/>D_SIGNAL — Default Capital Allocator（兼容 re-export shim）<br/>文件: capital/default_capital_allocator.py"]
    src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py["(生产态 / production) D_SIGNAL — Default Signal Aggregator<br/>D_SIGNAL — Default Signal Aggregator<br/>文件: implementations/default_signal_aggregator.py"]
    src_zephyr_signal_fundamental_pipeline_py["(生产态 / production) AlphaSignalPipeline D_FACTOR->D_SIGNAL跨层集成管道<br/>AlphaSignalPipeline D_FACTOR->D_SIGNAL跨层集成管道<br/>文件: signal_fundamental/pipeline.py"]
    src_zephyr_signal_fundamental_init_py ~~~ src_zephyr_signal_fundamental_capital_capital_allocation_result_py
    src_zephyr_signal_fundamental_capital_capital_allocation_result_py ~~~ src_zephyr_signal_fundamental_capital_capital_allocator_py
    src_zephyr_signal_fundamental_capital_capital_allocator_py ~~~ src_zephyr_signal_fundamental_capital_default_capital_allocator_py
    src_zephyr_signal_fundamental_capital_default_capital_allocator_py ~~~ src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py
    src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py ~~~ src_zephyr_signal_fundamental_pipeline_py
    src_zephyr_signal_fundamental_strategy_capital_allocator_py["(生产态 / production) D_FUNDAMENTAL_SIGNAL — Capital Allocator（兼容导出）<br/>D_FUNDAMENTAL_SIGNAL — Capital Allocator（兼容导出）<br/>文件: strategy/capital_allocator.py"]
    src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py["(生产态 / production) D_SIGNAL — Default Capital Allocator<br/>D_SIGNAL — Default Capital Allocator<br/>文件: implementations/default_capital_allocator.py"]
    src_zephyr_signal_fundamental_synth_signal_synthesizer_py["(生产态 / production) D_SIGNAL — Signal Synthesizer<br/>D_SIGNAL — Signal Synthesizer<br/>文件: synth/signal_synthesizer.py"]
    src_zephyr_signal_fundamental_strategy_capital_allocator_py ~~~ src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py
    src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py ~~~ src_zephyr_signal_fundamental_synth_signal_synthesizer_py
    src_zephyr_signal_fundamental_gen_aggregator_base_py["(生产态 / production) D_SIGNAL — Signal Generation Layer<br/>D_SIGNAL — Signal Generation Layer<br/>文件: gen/aggregator_base.py"]
    src_zephyr_signal_fundamental_pipeline_py -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_synth_signal_synthesizer_py
    src_zephyr_signal_fundamental_capital_default_capital_allocator_py -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py
    src_zephyr_signal_fundamental_capital_capital_allocator_py -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_strategy_capital_allocator_py
    src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_gen_aggregator_base_py
    src_zephyr_signal_fundamental_strategy_capital_allocator_py -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_gen_aggregator_base_py
    src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_gen_aggregator_base_py
    D_INFRASTRUCTURE["(生产态 / production) 跨层契约基础设施 / Cross-Layer Contract Infrastructure<br/>跨层契约基础设施，负责跨层契约定义、共享契约管理和契约校验<br/>跨域节点 / cross-domain"]
    src_zephyr_signal_fundamental_gen_aggregator_base_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_signal_fundamental_synth_signal_synthesizer_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    D_TRADING["(生产态 / production) 交易运营 / Trading Operations<br/>交易运营，负责交易生命周期管理、订单状态和成交处理<br/>跨域节点 / cross-domain"]
    src_zephyr_signal_fundamental_capital_capital_allocation_result_py -->|导入依赖 / import_depends| D_TRADING
    src_zephyr_signal_fundamental_strategy_capital_allocator_py -->|导入依赖 / import_depends| D_TRADING
    D_FACTOR["(生产态 / production) 因子 / Factor<br/>因子，负责因子计算、因子库管理和因子评价<br/>跨域节点 / cross-domain"]
    src_zephyr_signal_fundamental_pipeline_py -->|导入依赖 / import_depends| D_FACTOR
    D_SHARED["(生产态 / production) 共享服务 / Shared Services<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>跨域节点 / cross-domain"]
    src_zephyr_signal_fundamental_pipeline_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py -->|导入依赖 / import_depends| D_TRADING
    src_zephyr_signal_fundamental_gen_aggregator_base_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_signal_fundamental_pipeline_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_signal_fundamental_synth_signal_synthesizer_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_signal_fundamental_gen_aggregator_base_py -->|导入依赖 / import_depends| D_TRADING
    src_zephyr_signal_fundamental_gen_aggregator_base_py -->|导入依赖 / import_depends| D_TRADING
    src_zephyr_signal_fundamental_pipeline_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["(生产态 / production) 生命周期管理 / Lifecycle Management<br/>生命周期管理，负责蓝图/模块/任务的声明周期管理和元数据治理<br/>跨域节点 / cross-domain"]
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_init_py
    D_FACTOR -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_pipeline_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_signal_fundamental_init_py,src_zephyr_signal_fundamental_capital_capital_allocation_result_py,src_zephyr_signal_fundamental_capital_capital_allocator_py,src_zephyr_signal_fundamental_capital_default_capital_allocator_py,src_zephyr_signal_fundamental_gen_aggregator_base_py,src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py,src_zephyr_signal_fundamental_pipeline_py,src_zephyr_signal_fundamental_strategy_capital_allocator_py,src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py,src_zephyr_signal_fundamental_synth_signal_synthesizer_py production
    class D_INFRASTRUCTURE,D_TRADING,D_FACTOR,D_SHARED,D_GOVERNANCE external_prod
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 本域 10 个模块全部为运营态（production），上方全景图即运营态全貌，不再重复绘制。

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> （无设计态模块 / No design modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | AlphaSignalPipeline D_FACTOR->D_SIGNAL跨层集成管道 (signa... | → | D_FACTOR 因子: ZephyrAlpha — D_FACTOR Alpha Factor Layer (factor/factor... | 导入依赖 / import_depends |
| 2 | D_SIGNAL — Signal Generation Layer (gen/aggregator_base.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/factor_signal.py | 导入依赖 / import_depends |
| 3 | D_SIGNAL — Signal Generation Layer (gen/aggregator_base.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/synthesized_signal.py | 导入依赖 / import_depends |
| 4 | D_SIGNAL — Default Signal Aggregator (implementations/de... | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/factor_signal.py | 导入依赖 / import_depends |
| 5 | D_SIGNAL — Default Signal Aggregator (implementations/de... | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/synthesized_signal.py | 导入依赖 / import_depends |
| 6 | AlphaSignalPipeline D_FACTOR->D_SIGNAL跨层集成管道 (signa... | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/factor_signal.py | 导入依赖 / import_depends |
| 7 | AlphaSignalPipeline D_FACTOR->D_SIGNAL跨层集成管道 (signa... | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/synthesized_signal.py | 导入依赖 / import_depends |
| 8 | D_SIGNAL — Default Capital Allocator (implementations/de... | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/synthesized_signal.py | 导入依赖 / import_depends |
| 9 | D_SIGNAL — Signal Synthesizer (synth/signal_synthesizer.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/factor_signal.py | 导入依赖 / import_depends |
| 10 | D_SIGNAL — Signal Synthesizer (synth/signal_synthesizer.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: contracts/synthesized_signal.py | 导入依赖 / import_depends |
| 11 | AlphaSignalPipeline D_FACTOR->D_SIGNAL跨层集成管道 (signa... | → | D_SHARED 共享服务: errors.py —— ZephyrAlpha 统一错误层次（Traditional Exce... | 导入依赖 / import_depends |
| 12 | AlphaSignalPipeline D_FACTOR->D_SIGNAL跨层集成管道 (signa... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 \| 盲点 B19... | 导入依赖 / import_depends |
| 13 | D_FUNDAMENTAL_SIGNAL — CapitalAllocationResult re-export... | → | D_TRADING 交易运营: execution/capital_allocation_result.py | 导入依赖 / import_depends |
| 14 | D_SIGNAL — Signal Generation Layer (gen/aggregator_base.py) | → | D_TRADING 交易运营: execution/capital_allocation_result.py | 导入依赖 / import_depends |
| 15 | D_SIGNAL — Signal Generation Layer (gen/aggregator_base.py) | → | D_TRADING 交易运营: market/signal_degradation_warning.py | 导入依赖 / import_depends |
| 16 | D_FUNDAMENTAL_SIGNAL — Capital Allocator（兼容导出） (st... | → | D_TRADING 交易运营: execution/capital_allocation_result.py | 导入依赖 / import_depends |
| 17 | D_SIGNAL — Default Capital Allocator (implementations/de... | → | D_TRADING 交易运营: execution/capital_allocation_result.py | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_FACTOR 因子: factor/alpha_signal_pipeline.py | → | AlphaSignalPipeline D_FACTOR->D_SIGNAL跨层集成管道 (signa... | 导入依赖 / import_depends |
| 2 | D_GOVERNANCE 生命周期管理: C-track 端到端演示 —— 全流水线一次性运行 (construction/... | → | D_SIGNAL Signal Domain (signal_fundamental/__init__.py) | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 6 个外部域直接连接（出边 18 条 + 入边 2 条 = 20 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_FUNDAMENTAL_SIGNAL["D_FUNDAMENTAL_SIGNAL<br/>基本面信号"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE<br/>跨层契约基础设施"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_ASHARE_SIGNAL["D_ASHARE_SIGNAL<br/>A股特色信号"]
    D_FACTOR["D_FACTOR<br/>因子"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_FUNDAMENTAL_SIGNAL -->|9条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_FUNDAMENTAL_SIGNAL -->|5条 导入依赖 / import_depends| D_TRADING
    D_FUNDAMENTAL_SIGNAL -->|2条 导入依赖 / import_depends| D_SHARED
    D_FUNDAMENTAL_SIGNAL -->|1条 event / event| D_ASHARE_SIGNAL
    D_FUNDAMENTAL_SIGNAL -->|1条 导入依赖 / import_depends| D_FACTOR
    D_FACTOR -->|1条 导入依赖 / import_depends| D_FUNDAMENTAL_SIGNAL
    D_GOVERNANCE -->|1条 导入依赖 / import_depends| D_FUNDAMENTAL_SIGNAL
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
