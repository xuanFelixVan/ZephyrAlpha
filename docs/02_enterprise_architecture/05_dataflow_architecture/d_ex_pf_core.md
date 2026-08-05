---
doc_type: architecture_view
title: 执行核心+组合核心域
version: "1.0"
status: active
date: 2026-08-05
owner: auto-generator
ttl: permanent
---

# 执行核心+组合核心域

> 生成时间: 2026-08-05T20:31:31
> 真源: `dataflow_graph_registry.yaml` → PostgreSQL `dataflow_*` 表
> 生成器: `generate_dataflow_diagram.py`（全文自动生成，禁止手工编辑）

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/05_dataflow_architecture/_zoomable_html/d_ex_pf_core.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

> **域职责 / Responsibility**: 执行核心+组合核心——审计日志/成交处理/持仓跟踪/实盘组合 + 组合优化/汇总/策略运行/TopN动量策略

## 域基本信息 / Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| Dataset 数 | 11 | Datasets | 11 |
| Job 数 | 10 | Jobs | 10 |
| 运营态 Dataset | 3 | Production Datasets | 3 |
| 设计态 Dataset | 8 | Design Datasets | 8 |
| 运营态 Job | 2 | Production Jobs | 2 |
| 设计态 Job | 8 | Design Jobs | 8 |
| 跨域外部 Dataset | 2 | Cross-domain Datasets | 2 |

## 数据流图

> **图例说明 / Legend**：
>
> - 🟦 **蓝色 = 运营态节点**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态节点**（design，蓝图阶段，代码未写）
> - 🟦更浅蓝 = 跨域外部 Dataset（external_prod/external_design）
> - **实线箭头 ``-->`` = 运营态数据流**（两端均 production）
> - **虚线箭头 ``-.->`` = 非运营态数据流**（含 design、混合）
> - 矩形 = Dataset（数据集）/ 圆角矩形 = Job（作业）
> - ``JOB -->|produces / 产出| DS`` = Job 产出 Dataset
> - ``DS -->|consumed by / 被消费于| JOB`` = Job 消费 Dataset

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 21 个节点（Dataset 11 + Job 10），含 12 条边，含 2 个跨域外部 Dataset。颜色区分运营态（蓝）/设计态（橙虚线）。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    DS11263["(设计态 / design) execution.audit_journal /<br/>审计日志记录<br/>（交易/系统操作审计流水）<br/>契约: - · 域: 执行核心"]
    DS11264["(设计态 / design) execution.fill_handler /<br/>成交处理记录<br/>（成交回报处理/状态更新）<br/>契约: - · 域: 执行核心"]
    DS11266["(设计态 / design) execution.live_portfolio /<br/>实盘组合状态<br/>（实时组合/资金/持仓汇总）<br/>契约: - · 域: 执行核心"]
    DS11265["(设计态 / design) execution.position_tracker /<br/>持仓跟踪记录<br/>（实时持仓/成本/盈亏跟踪）<br/>契约: - · 域: 执行核心"]
    DS32562["(生产态 / production) fill.executed /<br/>成交.已成交<br/>成交回报（symbol/quantity/price/commission<br/>/timestamp），CTR-005 Fill<br/>契约: CTR-005 · 域: 执行核心"]
    DS32561["(生产态 / production) order.target /<br/>订单.目标订单<br/>目标订单（symbol/side/quantity/price/order_<br/>type），CTR-004 Order<br/>契约: CTR-004 · 域: 组合核心"]
    DS11267["(设计态 / design) portfolio.optimizer /<br/>优化后目标权重<br/>（均值方差/风险平价/Black-Litterman）<br/>契约: - · 域: 组合核心"]
    DS11268["(设计态 / design) portfolio.portfolio_aggregate<br/>/ 组合汇总状态<br/>（多策略组合/资金分配/持仓汇总）<br/>契约: - · 域: 组合核心"]
    DS11269["(设计态 / design) portfolio.strategy_runner /<br/>策略目标权重<br/>（策略信号→目标权重转换）<br/>契约: - · 域: 组合核心"]
    DS11270["(设计态 / design) portfolio.topn_momentum_<br/>strategy / TopN动量信号<br/>（TopN选股/动量排名信号）<br/>契约: - · 域: 组合核心"]
    DS32563["(生产态 / production) position.snapshot /<br/>持仓.快照<br/>持仓快照（symbol/quantity/avg_cost/market_value<br/>/timestamp），CTR-006 PositionSnapshot<br/>契约: CTR-006 · 域: 执行核心"]
    JOB757627("(设计态 / design) ex_core.audit_journal /<br/>审计日志<br/>（消费成交/持仓数据，产出执行核心记录）<br/>文件: audit_journal/")
    JOB757628("(设计态 / design) ex_core.fill_handler /<br/>成交处理<br/>（消费成交/持仓数据，产出执行核心记录）<br/>文件: ex_core/fill_handler.py")
    JOB757630("(设计态 / design) ex_core.live_portfolio /<br/>实盘组合<br/>（消费成交/持仓数据，产出执行核心记录）<br/>文件: services/live_portfolio.py")
    JOB757629("(设计态 / design) ex_core.position_tracker /<br/>持仓跟踪<br/>（消费成交/持仓数据，产出执行核心记录）<br/>文件: position_tracker/")
    JOB1192360("(生产态 / production) execute.order / 执行.订单<br/>执行订单（实盘/模拟），产出DS-008 fill.executed<br/>+ DS-009 position.snapshot<br/>文件: ex_core/executor.py")
    JOB1192359("(生产态 / production) generate.order / 生成.订单<br/>根据信号+风险限额生成目标订单，产出DS-007<br/>order.target<br/>文件: pf_core/order_generator.py")
    JOB757631("(设计态 / design) pf_core.optimizer / 组合优化<br/>（消费信号，产出组合/权重）<br/>文件: optimizer/")
    JOB757632("(设计态 / design) pf_core.portfolio_aggregate /<br/>组合汇总<br/>（消费信号，产出组合/权重）<br/>文件: portfolio_aggregate/")
    JOB757633("(设计态 / design) pf_core.strategy_runner /<br/>策略运行<br/>（消费信号，产出组合/权重）<br/>文件: strategy_engine/strategy_runner.py")
    JOB757634("(设计态 / design) pf_core.topn_momentum_<br/>strategy / TopN动量策略<br/>（消费信号，产出组合/权重）<br/>文件: pf_core/topn_momentum_strategy.py")
    DS32559["(生产态 / production) signal.composite /<br/>信号.合成信号<br/>合成交易信号（多因子加权/截面排名<br/>/置信度），CTR-P1-015 SynthesizedSignal<br/>契约: CTR-P1-015 · 域: 信号遗留设计态<br/>跨域节点 / cross-domain"]
    DS32560["(生产态 / production) risk.limits / 风险.限额<br/>风险限额（max_position/max_drawdown/exposure_<br/>limits），CTR-003 RiskLimits<br/>契约: CTR-003 · 域: 风控<br/>跨域节点 / cross-domain"]
    JOB1192359 -->|produces / 产出| DS32561
    JOB1192360 -->|produces / 产出| DS32562
    JOB1192360 -->|produces / 产出| DS32563
    JOB757627 -.->|produces / 产出| DS11263
    JOB757628 -.->|produces / 产出| DS11264
    JOB757629 -.->|produces / 产出| DS11265
    JOB757630 -.->|produces / 产出| DS11266
    JOB757631 -.->|produces / 产出| DS11267
    JOB757632 -.->|produces / 产出| DS11268
    JOB757633 -.->|produces / 产出| DS11269
    JOB757634 -.->|produces / 产出| DS11270
    DS32559 -.->|consumed by / 被消费于| JOB1192359
    DS32560 -.->|consumed by / 被消费于| JOB1192359
    DS32561 -->|consumed by / 被消费于| JOB1192360
    JOB757632 ~~~ JOB757631
    JOB757631 ~~~ JOB757627
    JOB757627 ~~~ JOB757629
    JOB757629 ~~~ JOB757634
    JOB757634 ~~~ JOB757633
    JOB757633 ~~~ JOB757628
    JOB757628 ~~~ JOB757630
    JOB757630 ~~~ JOB1192359
    DS11268 ~~~ DS11267
    DS11267 ~~~ DS11263
    DS11263 ~~~ DS11265
    DS11265 ~~~ DS11270
    DS11270 ~~~ DS11269
    DS11269 ~~~ DS11264
    DS11264 ~~~ DS11266
    DS11266 ~~~ DS32561
    DS32562 ~~~ DS32563
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class DS32562,DS32561,DS32563,JOB1192360,JOB1192359 production
    class DS11263,DS11264,DS11266,DS11265,DS11267,DS11268,DS11269,DS11270,JOB757627,JOB757628,JOB757630,JOB757629,JOB757631,JOB757632,JOB757633,JOB757634 design
    class DS32559,DS32560 external_prod
```

### 运营态的图（仅 design_maturity=production）

> 仅展示已实现稳定运行的节点（运营态：3 datasets / 数据集, 2 jobs / 作业, 4 edges / 边）。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    DS32562["(生产态 / production) fill.executed /<br/>成交.已成交<br/>成交回报（symbol/quantity/price/commission<br/>/timestamp），CTR-005 Fill<br/>契约: CTR-005 · 域: 执行核心"]
    DS32561["(生产态 / production) order.target /<br/>订单.目标订单<br/>目标订单（symbol/side/quantity/price/order_<br/>type），CTR-004 Order<br/>契约: CTR-004 · 域: 组合核心"]
    DS32563["(生产态 / production) position.snapshot /<br/>持仓.快照<br/>持仓快照（symbol/quantity/avg_cost/market_value<br/>/timestamp），CTR-006 PositionSnapshot<br/>契约: CTR-006 · 域: 执行核心"]
    JOB1192360("(生产态 / production) execute.order / 执行.订单<br/>执行订单（实盘/模拟），产出DS-008 fill.executed<br/>+ DS-009 position.snapshot<br/>文件: ex_core/executor.py")
    JOB1192359("(生产态 / production) generate.order / 生成.订单<br/>根据信号+风险限额生成目标订单，产出DS-007<br/>order.target<br/>文件: pf_core/order_generator.py")
    JOB1192359 -->|produces / 产出| DS32561
    JOB1192360 -->|produces / 产出| DS32562
    JOB1192360 -->|produces / 产出| DS32563
    DS32561 -->|consumed by / 被消费于| JOB1192360
    DS32562 ~~~ DS32563
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class DS32562,DS32561,DS32563,JOB1192360,JOB1192359 production
```

### 设计态的图（仅 design_maturity=design）

> 仅展示蓝图阶段、代码未写的设计态节点（设计态：8 datasets / 数据集, 8 jobs / 作业, 8 edges / 边）。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
flowchart TD
    DS11263["(设计态 / design) execution.audit_journal /<br/>审计日志记录<br/>（交易/系统操作审计流水）<br/>契约: - · 域: 执行核心"]
    DS11264["(设计态 / design) execution.fill_handler /<br/>成交处理记录<br/>（成交回报处理/状态更新）<br/>契约: - · 域: 执行核心"]
    DS11266["(设计态 / design) execution.live_portfolio /<br/>实盘组合状态<br/>（实时组合/资金/持仓汇总）<br/>契约: - · 域: 执行核心"]
    DS11265["(设计态 / design) execution.position_tracker /<br/>持仓跟踪记录<br/>（实时持仓/成本/盈亏跟踪）<br/>契约: - · 域: 执行核心"]
    DS11267["(设计态 / design) portfolio.optimizer /<br/>优化后目标权重<br/>（均值方差/风险平价/Black-Litterman）<br/>契约: - · 域: 组合核心"]
    DS11268["(设计态 / design) portfolio.portfolio_aggregate<br/>/ 组合汇总状态<br/>（多策略组合/资金分配/持仓汇总）<br/>契约: - · 域: 组合核心"]
    DS11269["(设计态 / design) portfolio.strategy_runner /<br/>策略目标权重<br/>（策略信号→目标权重转换）<br/>契约: - · 域: 组合核心"]
    DS11270["(设计态 / design) portfolio.topn_momentum_<br/>strategy / TopN动量信号<br/>（TopN选股/动量排名信号）<br/>契约: - · 域: 组合核心"]
    JOB757627("(设计态 / design) ex_core.audit_journal /<br/>审计日志<br/>（消费成交/持仓数据，产出执行核心记录）<br/>文件: audit_journal/")
    JOB757628("(设计态 / design) ex_core.fill_handler /<br/>成交处理<br/>（消费成交/持仓数据，产出执行核心记录）<br/>文件: ex_core/fill_handler.py")
    JOB757630("(设计态 / design) ex_core.live_portfolio /<br/>实盘组合<br/>（消费成交/持仓数据，产出执行核心记录）<br/>文件: services/live_portfolio.py")
    JOB757629("(设计态 / design) ex_core.position_tracker /<br/>持仓跟踪<br/>（消费成交/持仓数据，产出执行核心记录）<br/>文件: position_tracker/")
    JOB757631("(设计态 / design) pf_core.optimizer / 组合优化<br/>（消费信号，产出组合/权重）<br/>文件: optimizer/")
    JOB757632("(设计态 / design) pf_core.portfolio_aggregate /<br/>组合汇总<br/>（消费信号，产出组合/权重）<br/>文件: portfolio_aggregate/")
    JOB757633("(设计态 / design) pf_core.strategy_runner /<br/>策略运行<br/>（消费信号，产出组合/权重）<br/>文件: strategy_engine/strategy_runner.py")
    JOB757634("(设计态 / design) pf_core.topn_momentum_<br/>strategy / TopN动量策略<br/>（消费信号，产出组合/权重）<br/>文件: pf_core/topn_momentum_strategy.py")
    JOB757627 -.->|produces / 产出| DS11263
    JOB757628 -.->|produces / 产出| DS11264
    JOB757629 -.->|produces / 产出| DS11265
    JOB757630 -.->|produces / 产出| DS11266
    JOB757631 -.->|produces / 产出| DS11267
    JOB757632 -.->|produces / 产出| DS11268
    JOB757633 -.->|produces / 产出| DS11269
    JOB757634 -.->|produces / 产出| DS11270
    JOB757634 ~~~ JOB757628
    JOB757628 ~~~ JOB757627
    JOB757627 ~~~ JOB757630
    JOB757630 ~~~ JOB757632
    JOB757632 ~~~ JOB757631
    JOB757631 ~~~ JOB757629
    JOB757629 ~~~ JOB757633
    DS11270 ~~~ DS11264
    DS11264 ~~~ DS11263
    DS11263 ~~~ DS11266
    DS11266 ~~~ DS11268
    DS11268 ~~~ DS11267
    DS11267 ~~~ DS11265
    DS11265 ~~~ DS11269
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class DS11263,DS11264,DS11266,DS11265,DS11267,DS11268,DS11269,DS11270,JOB757627,JOB757628,JOB757630,JOB757629,JOB757631,JOB757632,JOB757633,JOB757634 design
```

## Dataset 清单

| ID | entity_name / 实体名 | scope / 范围 | domain / 域 | design_maturity / 设计成熟度 | module_id / 蓝图 | 功能简述 |
|----|----------------------|--------------|------------|------------------------------|------------------|----------|
| DS-11263 | execution.audit_journal | production / 生产 | D_EX_CORE / 执行核心 | design / 设计 | MOD-EX-003 | 审计日志记录（交易/系统操作审计流水） |
| DS-11264 | execution.fill_handler | production / 生产 | D_EX_CORE / 执行核心 | design / 设计 | MOD-EX-001 | 成交处理记录（成交回报处理/状态更新） |
| DS-11266 | execution.live_portfolio | production / 生产 | D_EX_CORE / 执行核心 | design / 设计 | MOD-L06-001 | 实盘组合状态（实时组合/资金/持仓汇总） |
| DS-11265 | execution.position_tracker | production / 生产 | D_EX_CORE / 执行核心 | design / 设计 | MOD-EX-002 | 持仓跟踪记录（实时持仓/成本/盈亏跟踪） |
| DS-32562 | fill.executed / 成交.已成交 | production / 生产 | D_EX_CORE / 执行核心 | production / 生产 | MOD-L06-001 | 成交回报（symbol/quantity/price/commission/timestamp），CTR-005 Fill |
| DS-32561 | order.target / 订单.目标订单 | production / 生产 | D_PF_CORE / 组合核心 | production / 生产 | MOD-L05-001 | 目标订单（symbol/side/quantity/price/order_type），CTR-004 Order |
| DS-11267 | portfolio.optimizer | production / 生产 | D_PF_CORE / 组合核心 | design / 设计 | MOD-PF-001 | 优化后目标权重（均值方差/风险平价/Black-Litterman） |
| DS-11268 | portfolio.portfolio_aggregate | production / 生产 | D_PF_CORE / 组合核心 | design / 设计 | MOD-PF-003 | 组合汇总状态（多策略组合/资金分配/持仓汇总） |
| DS-11269 | portfolio.strategy_runner | production / 生产 | D_PF_CORE / 组合核心 | design / 设计 | MOD-L05-001 | 策略目标权重（策略信号→目标权重转换） |
| DS-11270 | portfolio.topn_momentum_strategy | production / 生产 | D_PF_CORE / 组合核心 | design / 设计 | MOD-L05-001 | TopN动量信号（TopN选股/动量排名信号） |
| DS-32563 | position.snapshot / 持仓.快照 | production / 生产 | D_EX_CORE / 执行核心 | production / 生产 | MOD-L06-001 | 持仓快照（symbol/quantity/avg_cost/market_value/timestamp），CTR-006 PositionSnapshot |

## Job 清单

| ID | job_name / 作业名 | trigger_type / 触发类型 | design_maturity / 设计成熟度 | module_id / 蓝图 | 功能简述 |
|----|-------------------|----------------------------|------------------------------|------------------|----------|
| JOB-757627 | ex_core.audit_journal | event_driven / 事件驱动 | design / 设计 | MOD-EX-003 | 审计日志（消费成交/持仓数据，产出执行核心记录） |
| JOB-757628 | ex_core.fill_handler | event_driven / 事件驱动 | design / 设计 | MOD-EX-001 | 成交处理（消费成交/持仓数据，产出执行核心记录） |
| JOB-757630 | ex_core.live_portfolio | event_driven / 事件驱动 | design / 设计 | MOD-L06-001 | 实盘组合（消费成交/持仓数据，产出执行核心记录） |
| JOB-757629 | ex_core.position_tracker | event_driven / 事件驱动 | design / 设计 | MOD-EX-002 | 持仓跟踪（消费成交/持仓数据，产出执行核心记录） |
| JOB-1192360 | execute.order / 执行.订单 | event_driven / 事件驱动 | production / 生产 | MOD-L06-001 | 执行订单（实盘/模拟），产出DS-008 fill.executed + DS-009 position.snapshot |
| JOB-1192359 | generate.order / 生成.订单 | event_driven / 事件驱动 | production / 生产 | MOD-L05-001 | 根据信号+风险限额生成目标订单，产出DS-007 order.target |
| JOB-757631 | pf_core.optimizer | event_driven / 事件驱动 | design / 设计 | MOD-PF-001 | 组合优化（消费信号，产出组合/权重） |
| JOB-757632 | pf_core.portfolio_aggregate | event_driven / 事件驱动 | design / 设计 | MOD-PF-003 | 组合汇总（消费信号，产出组合/权重） |
| JOB-757633 | pf_core.strategy_runner | event_driven / 事件驱动 | design / 设计 | MOD-L05-001 | 策略运行（消费信号，产出组合/权重） |
| JOB-757634 | pf_core.topn_momentum_strategy | event_driven / 事件驱动 | design / 设计 | MOD-L05-001 | TopN动量策略（消费信号，产出组合/权重） |

## 跨域依赖 / Cross-domain Dependencies

### 依赖本域的外部 Dataset（入边）/ Consumed From

| 外部 Dataset | 域 | 成熟度 | 被本域 Job 消费 |
|-------------|------|--------|----------------|
| signal.composite | D_SIGLEGACY / 信号遗留设计态 | production / 生产 | generate.order |
| risk.limits | D_RISK / 风控 | production / 生产 | generate.order |

[← 返回索引](dataflow_index.md)
