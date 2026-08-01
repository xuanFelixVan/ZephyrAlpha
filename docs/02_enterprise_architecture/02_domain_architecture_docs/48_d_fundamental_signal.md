---
doc_type: architecture_view
title: D_FUNDAMENTAL_SIGNAL 基本面信号架构文档
version: "1.0"
status: active
date: 2026-08-02
owner: auto-generator
ttl: permanent
---

# 48_d_fundamental_signal / 基本面信号域 / Fundamental Signal

> **功能简介 / Overview**: 基本面信号，负责基于财务数据的基本面信号生成

> **文档作用 / Purpose**: 展示 基本面信号（D_FUNDAMENTAL_SIGNAL）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/48_d_fundamental_signal.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 48 | Number | 48 |
| 域ID | D_FUNDAMENTAL_SIGNAL | Domain ID | D_FUNDAMENTAL_SIGNAL |
| 域名称 | 基本面信号 | Domain Name | Fundamental Signal |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 13 | Module Count | 13 |
| 域内依赖 | 7 | Internal Dependencies | 7 |
| 跨域入边 | 2 | Cross-domain Incoming | 2 |
| 跨域出边 | 18 | Cross-domain Outgoing | 18 |
| 设计态模块 | 3 | Design Modules | 3 |
| 生产态模块 | 10 | Production Modules | 10 |
| 容量 | 10/150 (正常) | Capacity | 10/150 (正常) |
| 描述 | 财务指标信号 | Description | 财务指标信号 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 13 个模块（生产态 10 + 设计态 3），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_signal_fundamental_init_py["基本面信号域包<br/>基本面信号域的总入口文件夹。把这个域里管信号生成<br/>、资金分配、信号合成的几块代码归到一起，用到谁才<br/>加载谁，避免一上来全加载拖慢启动。<br/>Fundamental Signal Domain Package<br/>Unified package for D_FUNDAMENTAL_SIGNAL<br/>domain, aggregating signal generation,<br/>strategy, synthesis, combiner, capital<br/>allocation and pipeline; lazily re-exports<br/>submodule main classes via __getattr__<br/>文件: signal_fundamental/__init__.py<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_audit_signal_audit_logger_py["信号审计日志器<br/>给信号留操作录像的记账员。从因子变信号、信号变资<br/>金分配，每一步关键操作都记一笔，事后出问题能倒查<br/>是哪一步、哪个信号出了岔。<br/>⛔ 基本面信号域，设计已就绪，等待开发排期<br/>Signal Audit Logger<br/>(Design) Full-link audit logger for signal<br/>generation, recording key operations and<br/>intermediate results in factor->signal->capital<br/>allocation process<br/>文件: audit/signal_audit_logger.py<br/>(设计态 / design)"]
    src_zephyr_signal_fundamental_capital_capital_allocation_result_py["资本分配结果（兼容导出）<br/>资本分配结果的兼容导出垫片。老代码从这导入不会断<br/>，真源在别处，这层只是转发，避免改一处坏一片。<br/>Compat re-export shim for<br/>CapitalAllocationResult, keeping old import<br/>paths working<br/>文件: capital/capital_allocation_result.py<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_capital_capital_allocator_py["资本分配器（兼容导出）<br/>资本分配器的兼容入口。老代码从这导入不会断，真源<br/>在 strategy<br/>目录里。这层只转发不定义，防止多真源同步漂移。<br/>Capital Allocator (compat re-export)<br/>Backward-compat entry, real source in<br/>strategy.capital_allocator; do not redefine<br/>contract types or ABCs here<br/>文件: capital/capital_allocator.py<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_capital_default_capital_allocator_py["默认资本分配器（兼容导出）<br/>默认资本分配器的兼容导出垫片，真源在 strategy<br/>目录，这层只转发保持老路径不断。<br/>Compat re-export shim for default capital<br/>allocator, real source in strategy dir<br/>文件: capital/default_capital_allocator.py<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py["默认信号聚合器<br/>信号聚合器的默认实现。基类定了怎么聚合，这层填具<br/>体怎么把多个因子信号合并成一个合成信号。<br/>Default Signal Aggregator<br/>Default implementation of signal aggregator,<br/>concrete multi-factor signal merging logic<br/>文件: implementations/default_signal_<br/>aggregator.py<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_pipeline_py["管线<br/>从因子域到信号域的跨层集成管道。把因子信号一路加<br/>工成可交易信号，是整个信号生成流程的总调度。<br/>Alpha Signal Pipeline<br/>AlphaSignalPipeline, D_FACTOR->D_SIGNAL<br/>cross-layer integration pipeline, processes<br/>factor signals into tradeable signals<br/>文件: signal_fundamental/pipeline.py<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_router_signal_priority_router_py["信号优先级路由器<br/>给信号排优先级的路由器。多个信号同时来时，按优先<br/>级决定先处理谁后处理谁，避免重要信号被淹没。<br/>⛔ 基本面信号域，设计已就绪，等待开发排期<br/>Signal Priority Router<br/>(Design) Signal priority router, decides<br/>processing order when multiple signals arrive<br/>simultaneously by priority<br/>文件: router/signal_priority_router.py<br/>(设计态 / design)"]
    src_zephyr_signal_fundamental_init_py ~~~ src_zephyr_signal_fundamental_audit_signal_audit_logger_py
    src_zephyr_signal_fundamental_audit_signal_audit_logger_py ~~~ src_zephyr_signal_fundamental_capital_capital_allocation_result_py
    src_zephyr_signal_fundamental_capital_capital_allocation_result_py ~~~ src_zephyr_signal_fundamental_capital_capital_allocator_py
    src_zephyr_signal_fundamental_capital_capital_allocator_py ~~~ src_zephyr_signal_fundamental_capital_default_capital_allocator_py
    src_zephyr_signal_fundamental_capital_default_capital_allocator_py ~~~ src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py
    src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py ~~~ src_zephyr_signal_fundamental_pipeline_py
    src_zephyr_signal_fundamental_pipeline_py ~~~ src_zephyr_signal_fundamental_router_signal_priority_router_py
    src_zephyr_signal_fundamental_router_signal_conflict_resolver_py["信号冲突解决器<br/>解决信号冲突的裁判。多个信号互相矛盾<br/>（一个说买一个说卖）时，裁定听谁的，避免信号打架<br/>系统无所适从。<br/>⛔ 基本面信号域，设计已就绪，等待开发排期<br/>Signal Conflict Resolver<br/>(Design) Signal conflict resolver, adjudicates<br/>which signal to adopt when multiple signals<br/>contradict each other<br/>文件: router/signal_conflict_resolver.py<br/>(设计态 / design)"]
    src_zephyr_signal_fundamental_strategy_capital_allocator_py["策略资本分配器<br/>资本分配器的真源实现。决定每个信号分到多少资金，<br/>是资金怎么分的核心逻辑所在。<br/>Strategy Capital Allocator<br/>Real source implementation of capital<br/>allocator, decides how much capital each signal<br/>gets<br/>文件: strategy/capital_allocator.py<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py["策略默认资本分配器<br/>资本分配器的默认实现。基类定了分配框架，这层填具<br/>体的资金分配算法。<br/>Strategy Default Capital Allocator<br/>Default implementation of capital allocator,<br/>concrete capital allocation algorithm<br/>文件: implementations/default_capital_<br/>allocator.py<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_synth_signal_synthesizer_py["信号合成器<br/>信号合成引擎。把多个因子信号加权聚合成一个统一的<br/>合成交易信号，顺带归一化去噪、识别市场状态、检测<br/>信号退化，是信号合二为一的核心。<br/>Signal Synthesizer<br/>Signal synthesis engine, weighted-aggregates<br/>multi-factor signals into unified tradeable<br/>signal; normalization, regime detection,<br/>degradation warning<br/>文件: synth/signal_synthesizer.py<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_router_signal_conflict_resolver_py ~~~ src_zephyr_signal_fundamental_strategy_capital_allocator_py
    src_zephyr_signal_fundamental_strategy_capital_allocator_py ~~~ src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py
    src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py ~~~ src_zephyr_signal_fundamental_synth_signal_synthesizer_py
    src_zephyr_signal_fundamental_gen_aggregator_base_py["信号生成聚合基类<br/>信号生成层的基类。把多因子信号聚合成可交易的合成<br/>信号，再分配资金，顺带检测信号质量有没有退化。是<br/>这块的抽象地基，具体做法由子类填。<br/>Signal Generation Aggregator Base<br/>Signal generation layer base class, synthesizes<br/>factor signals into tradeable signals;<br/>multi-factor aggregation, synthesis, capital<br/>allocation, degradation detection<br/>文件: gen/aggregator_base.py<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_router_signal_priority_router_py -.->|runtime / runtime| src_zephyr_signal_fundamental_router_signal_conflict_resolver_py
    src_zephyr_signal_fundamental_capital_capital_allocator_py -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_strategy_capital_allocator_py
    src_zephyr_signal_fundamental_pipeline_py -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_synth_signal_synthesizer_py
    src_zephyr_signal_fundamental_capital_default_capital_allocator_py -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py
    src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_gen_aggregator_base_py
    src_zephyr_signal_fundamental_strategy_capital_allocator_py -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_gen_aggregator_base_py
    src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_gen_aggregator_base_py
    D_ASHARE_SIGNAL["A股特色信号<br/>A 股特色信号，负责 A<br/>股市场特色交易信号的生成和管理<br/>A-Share Signal<br/>跨域节点 / cross-domain<br/>(设计态 / design)"]
    src_zephyr_signal_fundamental_router_signal_conflict_resolver_py -.->|event / event| D_ASHARE_SIGNAL
    D_INFRASTRUCTURE["跨层契约基础设施<br/>跨层契约基础设施，负责跨层契约定义、共享契约管理<br/>和契约校验<br/>Cross-Layer Contract Infrastructure<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_synth_signal_synthesizer_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_signal_fundamental_pipeline_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    D_TRADING["交易运营<br/>交易运营，负责交易生命周期管理、订单状态和成交处<br/>理<br/>Trading Operations<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_capital_capital_allocation_result_py -->|导入依赖 / import_depends| D_TRADING
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_pipeline_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py -->|导入依赖 / import_depends| D_TRADING
    src_zephyr_signal_fundamental_gen_aggregator_base_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_signal_fundamental_gen_aggregator_base_py -->|导入依赖 / import_depends| D_TRADING
    src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_signal_fundamental_synth_signal_synthesizer_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_signal_fundamental_gen_aggregator_base_py -->|导入依赖 / import_depends| D_TRADING
    src_zephyr_signal_fundamental_pipeline_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    src_zephyr_signal_fundamental_strategy_capital_allocator_py -->|导入依赖 / import_depends| D_TRADING
    D_FACTOR["因子<br/>因子，负责因子计算、因子库管理和因子评价<br/>Factor<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_FACTOR -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_pipeline_py
    D_GOVERNANCE["生命周期管理<br/>生命周期管理，负责蓝图/模块<br/>/任务的声明周期管理和元数据治理<br/>Lifecycle Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_init_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_signal_fundamental_init_py,src_zephyr_signal_fundamental_capital_capital_allocation_result_py,src_zephyr_signal_fundamental_capital_capital_allocator_py,src_zephyr_signal_fundamental_capital_default_capital_allocator_py,src_zephyr_signal_fundamental_gen_aggregator_base_py,src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py,src_zephyr_signal_fundamental_pipeline_py,src_zephyr_signal_fundamental_strategy_capital_allocator_py,src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py,src_zephyr_signal_fundamental_synth_signal_synthesizer_py production
    class src_zephyr_signal_fundamental_audit_signal_audit_logger_py,src_zephyr_signal_fundamental_router_signal_conflict_resolver_py,src_zephyr_signal_fundamental_router_signal_priority_router_py design
    class D_INFRASTRUCTURE,D_TRADING,D_SHARED,D_FACTOR,D_GOVERNANCE external_prod
    class D_ASHARE_SIGNAL external_design
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 10 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_signal_fundamental_init_py["基本面信号域包<br/>基本面信号域的总入口文件夹。把这个域里管信号生成<br/>、资金分配、信号合成的几块代码归到一起，用到谁才<br/>加载谁，避免一上来全加载拖慢启动。<br/>Fundamental Signal Domain Package<br/>Unified package for D_FUNDAMENTAL_SIGNAL<br/>domain, aggregating signal generation,<br/>strategy, synthesis, combiner, capital<br/>allocation and pipeline; lazily re-exports<br/>submodule main classes via __getattr__<br/>文件: signal_fundamental/__init__.py<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_capital_capital_allocation_result_py["资本分配结果（兼容导出）<br/>资本分配结果的兼容导出垫片。老代码从这导入不会断<br/>，真源在别处，这层只是转发，避免改一处坏一片。<br/>Compat re-export shim for<br/>CapitalAllocationResult, keeping old import<br/>paths working<br/>文件: capital/capital_allocation_result.py<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_capital_capital_allocator_py["资本分配器（兼容导出）<br/>资本分配器的兼容入口。老代码从这导入不会断，真源<br/>在 strategy<br/>目录里。这层只转发不定义，防止多真源同步漂移。<br/>Capital Allocator (compat re-export)<br/>Backward-compat entry, real source in<br/>strategy.capital_allocator; do not redefine<br/>contract types or ABCs here<br/>文件: capital/capital_allocator.py<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_capital_default_capital_allocator_py["默认资本分配器（兼容导出）<br/>默认资本分配器的兼容导出垫片，真源在 strategy<br/>目录，这层只转发保持老路径不断。<br/>Compat re-export shim for default capital<br/>allocator, real source in strategy dir<br/>文件: capital/default_capital_allocator.py<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py["默认信号聚合器<br/>信号聚合器的默认实现。基类定了怎么聚合，这层填具<br/>体怎么把多个因子信号合并成一个合成信号。<br/>Default Signal Aggregator<br/>Default implementation of signal aggregator,<br/>concrete multi-factor signal merging logic<br/>文件: implementations/default_signal_<br/>aggregator.py<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_pipeline_py["管线<br/>从因子域到信号域的跨层集成管道。把因子信号一路加<br/>工成可交易信号，是整个信号生成流程的总调度。<br/>Alpha Signal Pipeline<br/>AlphaSignalPipeline, D_FACTOR->D_SIGNAL<br/>cross-layer integration pipeline, processes<br/>factor signals into tradeable signals<br/>文件: signal_fundamental/pipeline.py<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_init_py ~~~ src_zephyr_signal_fundamental_capital_capital_allocation_result_py
    src_zephyr_signal_fundamental_capital_capital_allocation_result_py ~~~ src_zephyr_signal_fundamental_capital_capital_allocator_py
    src_zephyr_signal_fundamental_capital_capital_allocator_py ~~~ src_zephyr_signal_fundamental_capital_default_capital_allocator_py
    src_zephyr_signal_fundamental_capital_default_capital_allocator_py ~~~ src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py
    src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py ~~~ src_zephyr_signal_fundamental_pipeline_py
    src_zephyr_signal_fundamental_strategy_capital_allocator_py["策略资本分配器<br/>资本分配器的真源实现。决定每个信号分到多少资金，<br/>是资金怎么分的核心逻辑所在。<br/>Strategy Capital Allocator<br/>Real source implementation of capital<br/>allocator, decides how much capital each signal<br/>gets<br/>文件: strategy/capital_allocator.py<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py["策略默认资本分配器<br/>资本分配器的默认实现。基类定了分配框架，这层填具<br/>体的资金分配算法。<br/>Strategy Default Capital Allocator<br/>Default implementation of capital allocator,<br/>concrete capital allocation algorithm<br/>文件: implementations/default_capital_<br/>allocator.py<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_synth_signal_synthesizer_py["信号合成器<br/>信号合成引擎。把多个因子信号加权聚合成一个统一的<br/>合成交易信号，顺带归一化去噪、识别市场状态、检测<br/>信号退化，是信号合二为一的核心。<br/>Signal Synthesizer<br/>Signal synthesis engine, weighted-aggregates<br/>multi-factor signals into unified tradeable<br/>signal; normalization, regime detection,<br/>degradation warning<br/>文件: synth/signal_synthesizer.py<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_strategy_capital_allocator_py ~~~ src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py
    src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py ~~~ src_zephyr_signal_fundamental_synth_signal_synthesizer_py
    src_zephyr_signal_fundamental_gen_aggregator_base_py["信号生成聚合基类<br/>信号生成层的基类。把多因子信号聚合成可交易的合成<br/>信号，再分配资金，顺带检测信号质量有没有退化。是<br/>这块的抽象地基，具体做法由子类填。<br/>Signal Generation Aggregator Base<br/>Signal generation layer base class, synthesizes<br/>factor signals into tradeable signals;<br/>multi-factor aggregation, synthesis, capital<br/>allocation, degradation detection<br/>文件: gen/aggregator_base.py<br/>(生产态 / production)"]
    src_zephyr_signal_fundamental_capital_capital_allocator_py -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_strategy_capital_allocator_py
    src_zephyr_signal_fundamental_pipeline_py -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_synth_signal_synthesizer_py
    src_zephyr_signal_fundamental_capital_default_capital_allocator_py -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py
    src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_gen_aggregator_base_py
    src_zephyr_signal_fundamental_strategy_capital_allocator_py -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_gen_aggregator_base_py
    src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py -->|导入依赖 / import_depends| src_zephyr_signal_fundamental_gen_aggregator_base_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_signal_fundamental_init_py,src_zephyr_signal_fundamental_capital_capital_allocation_result_py,src_zephyr_signal_fundamental_capital_capital_allocator_py,src_zephyr_signal_fundamental_capital_default_capital_allocator_py,src_zephyr_signal_fundamental_gen_aggregator_base_py,src_zephyr_signal_fundamental_gen_implementations_default_signal_aggregator_py,src_zephyr_signal_fundamental_pipeline_py,src_zephyr_signal_fundamental_strategy_capital_allocator_py,src_zephyr_signal_fundamental_strategy_implementations_default_capital_allocator_py,src_zephyr_signal_fundamental_synth_signal_synthesizer_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 3 个），不含跨域外部节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_signal_fundamental_audit_signal_audit_logger_py["信号审计日志器<br/>给信号留操作录像的记账员。从因子变信号、信号变资<br/>金分配，每一步关键操作都记一笔，事后出问题能倒查<br/>是哪一步、哪个信号出了岔。<br/>⛔ 基本面信号域，设计已就绪，等待开发排期<br/>Signal Audit Logger<br/>(Design) Full-link audit logger for signal<br/>generation, recording key operations and<br/>intermediate results in factor->signal->capital<br/>allocation process<br/>文件: audit/signal_audit_logger.py<br/>(设计态 / design)"]
    src_zephyr_signal_fundamental_router_signal_priority_router_py["信号优先级路由器<br/>给信号排优先级的路由器。多个信号同时来时，按优先<br/>级决定先处理谁后处理谁，避免重要信号被淹没。<br/>⛔ 基本面信号域，设计已就绪，等待开发排期<br/>Signal Priority Router<br/>(Design) Signal priority router, decides<br/>processing order when multiple signals arrive<br/>simultaneously by priority<br/>文件: router/signal_priority_router.py<br/>(设计态 / design)"]
    src_zephyr_signal_fundamental_audit_signal_audit_logger_py ~~~ src_zephyr_signal_fundamental_router_signal_priority_router_py
    src_zephyr_signal_fundamental_router_signal_conflict_resolver_py["信号冲突解决器<br/>解决信号冲突的裁判。多个信号互相矛盾<br/>（一个说买一个说卖）时，裁定听谁的，避免信号打架<br/>系统无所适从。<br/>⛔ 基本面信号域，设计已就绪，等待开发排期<br/>Signal Conflict Resolver<br/>(Design) Signal conflict resolver, adjudicates<br/>which signal to adopt when multiple signals<br/>contradict each other<br/>文件: router/signal_conflict_resolver.py<br/>(设计态 / design)"]
    src_zephyr_signal_fundamental_router_signal_priority_router_py -.->|runtime / runtime| src_zephyr_signal_fundamental_router_signal_conflict_resolver_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_signal_fundamental_audit_signal_audit_logger_py,src_zephyr_signal_fundamental_router_signal_conflict_resolver_py,src_zephyr_signal_fundamental_router_signal_priority_router_py design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 信号冲突解决器 / Signal Conflict Resolver (router/signal_... | → | D_ASHARE_SIGNAL A股特色信号: 机构行为分析器 / institutional_behavior_analyzer (signal_... | event / event |
| 2 | 管线 / Alpha Signal Pipeline (signal_fundamental/pipeline... | → | D_FACTOR 因子: 因子基类 / ZephyrAlpha — D_FACTOR Alpha Factor Layer (fa... | 导入依赖 / import_depends |
| 3 | 信号生成聚合基类 / Signal Generation Aggregator Base (gen... | → | D_INFRASTRUCTURE 跨层契约基础设施: 因子信号 / factor_signal (contracts/factor_signal.py) | 导入依赖 / import_depends |
| 4 | 信号生成聚合基类 / Signal Generation Aggregator Base (gen... | → | D_INFRASTRUCTURE 跨层契约基础设施: synthesized信号 / synthesized_signal (contracts/synthesiz... | 导入依赖 / import_depends |
| 5 | 默认信号聚合器 / Default Signal Aggregator (implementatio... | → | D_INFRASTRUCTURE 跨层契约基础设施: 因子信号 / factor_signal (contracts/factor_signal.py) | 导入依赖 / import_depends |
| 6 | 默认信号聚合器 / Default Signal Aggregator (implementatio... | → | D_INFRASTRUCTURE 跨层契约基础设施: synthesized信号 / synthesized_signal (contracts/synthesiz... | 导入依赖 / import_depends |
| 7 | 管线 / Alpha Signal Pipeline (signal_fundamental/pipeline... | → | D_INFRASTRUCTURE 跨层契约基础设施: 因子信号 / factor_signal (contracts/factor_signal.py) | 导入依赖 / import_depends |
| 8 | 管线 / Alpha Signal Pipeline (signal_fundamental/pipeline... | → | D_INFRASTRUCTURE 跨层契约基础设施: synthesized信号 / synthesized_signal (contracts/synthesiz... | 导入依赖 / import_depends |
| 9 | 策略默认资本分配器 / Strategy Default Capital Allocator (... | → | D_INFRASTRUCTURE 跨层契约基础设施: synthesized信号 / synthesized_signal (contracts/synthesiz... | 导入依赖 / import_depends |
| 10 | 信号合成器 / Signal Synthesizer (synth/signal_synthesizer... | → | D_INFRASTRUCTURE 跨层契约基础设施: 因子信号 / factor_signal (contracts/factor_signal.py) | 导入依赖 / import_depends |
| 11 | 信号合成器 / Signal Synthesizer (synth/signal_synthesizer... | → | D_INFRASTRUCTURE 跨层契约基础设施: synthesized信号 / synthesized_signal (contracts/synthesiz... | 导入依赖 / import_depends |
| 12 | 管线 / Alpha Signal Pipeline (signal_fundamental/pipeline... | → | D_SHARED 共享服务: 错误 / errors (foundation/errors.py) | 导入依赖 / import_depends |
| 13 | 管线 / Alpha Signal Pipeline (signal_fundamental/pipeline... | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 14 | 资本分配结果（兼容导出） / Capital Allocation Result (com... | → | D_TRADING 交易运营: 资本分配结果 / capital_allocation_result (execution/capit... | 导入依赖 / import_depends |
| 15 | 信号生成聚合基类 / Signal Generation Aggregator Base (gen... | → | D_TRADING 交易运营: 资本分配结果 / capital_allocation_result (execution/capit... | 导入依赖 / import_depends |
| 16 | 信号生成聚合基类 / Signal Generation Aggregator Base (gen... | → | D_TRADING 交易运营: 信号退化警告 / signal_degradation_warning (market/signal_... | 导入依赖 / import_depends |
| 17 | 策略资本分配器 / Strategy Capital Allocator (strategy/cap... | → | D_TRADING 交易运营: 资本分配结果 / capital_allocation_result (execution/capit... | 导入依赖 / import_depends |
| 18 | 策略默认资本分配器 / Strategy Default Capital Allocator (... | → | D_TRADING 交易运营: 资本分配结果 / capital_allocation_result (execution/capit... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_FACTOR 因子: 阿尔法信号管线 / alpha_signal_pipeline (factor/alpha_sign... | → | 管线 / Alpha Signal Pipeline (signal_fundamental/pipeline... | 导入依赖 / import_depends |
| 2 | D_GOVERNANCE 生命周期管理: demoe2e管线 / demo_e2e_pipeline (construction/demo_e2e_pi... | → | 基本面信号域包 / Fundamental Signal Domain Package (signa... | 导入依赖 / import_depends |

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
