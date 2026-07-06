---
doc_type: architecture_view
title: 数据流图（dataflowgraph）索引
version: "1.0"
status: active
date: 2026-07-06
owner: auto-generator
ttl: permanent
---

# 数据流图（dataflowgraph）索引

> 生成时间: 2026-07-06T12:56:25
> 真源: `dataflow_graph_registry.yaml` → PostgreSQL `dataflow_*` 表（ARCH-051）
> 数据库: depgraph (PostgreSQL)

## 概述

数据流图（dataflowgraph）是与依赖图（depgraph）正交的第三维度全景图。
- depgraph 表达"谁依赖谁"（模块依赖）
- dataflowgraph 表达"数据从哪流到哪"（数据流向）
- 通过 `Job.source_code_ref` 引用 depgraph 模块 path，建立跨图关联

## 统计

| 类型 | 生产 (production) | 回测内部 (backtest_internal) | 合计 |
|------|-------------------|------------------------------|------|
| Dataset | 10 | 4 | 14 |
| Job | 8 | 5 | 13 |
| Edge | - | - | 28 |

## Mermaid 图表

> 图表内嵌在本文档中，IDE 可直接渲染显示。
>
> **图例说明 / Legend**：
> - **蓝色矩形** = 生产 Dataset（dsProd）
> - **橙色矩形** = 回测 Dataset（dsBacktest）
> - **绿色圆角矩形** = 生产 Job（jobProd）
> - **粉色圆角矩形** = 回测 Job（jobBacktest）
> - `JOB -->|produces / 产出| DS` = Job 产出 Dataset
> - `DS -->|consumed by / 被消费于| JOB` = Job 消费 Dataset

### 全景图

> 节点数: 14 datasets / 数据集, 13 jobs / 作业, 28 edges / 边

```mermaid
flowchart LR
    DS209["backtest.fills<br/>回测.模拟成交<br/>[D_BACKTEST / 回测]"]:::dsBacktest
    DS210["backtest.nav_series<br/>回测.净值序列<br/>[D_BACKTEST / 回测]"]:::dsBacktest
    DS208["backtest.target_weights<br/>回测.目标权重<br/>[D_BACKTEST / 回测]"]:::dsBacktest
    DS207["backtest.tick_event<br/>回测.Tick事件<br/>[D_BACKTEST / 回测]"]:::dsBacktest
    DS206["backtest.result<br/>回测.结果<br/>CTR: CTR-P1-016<br/>[D_BACKTEST / 回测]"]:::dsProd
    DS200["factor.momentum_20d<br/>因子.20日动量<br/>CTR: CTR-002<br/>[D_FACTOR / 因子]"]:::dsProd
    DS199["factor.value_factor<br/>因子.价值因子<br/>CTR: CTR-002<br/>[D_FACTOR / 因子]"]:::dsProd
    DS204["fill.executed<br/>成交.已成交<br/>CTR: CTR-005<br/>[D_EX_CORE / 执行核心]"]:::dsProd
    DS198["market_data.ohlc_bar<br/>市场数据.OHLC K线<br/>CTR: CTR-001<br/>[D_MKT_DATA / 市场数据]"]:::dsProd
    DS197["market_data.tick<br/>市场数据.Tick行情<br/>CTR: CTR-001<br/>[D_MKT_DATA / 市场数据]"]:::dsProd
    DS203["order.target<br/>订单.目标订单<br/>CTR: CTR-004<br/>[D_PF_CORE / 持仓核心]"]:::dsProd
    DS205["position.snapshot<br/>持仓.快照<br/>CTR: CTR-006<br/>[D_EX_CORE / 执行核心]"]:::dsProd
    DS202["risk.limits<br/>风险.限额<br/>CTR: CTR-003<br/>[D_RISK / 风险]"]:::dsProd
    DS201["signal.composite<br/>信号.合成信号<br/>CTR: CTR-P1-015<br/>[D_SIGLEGACY / 信号(legacy)]"]:::dsProd
    JOB197("backtest.calc_metrics<br/>回测.计算指标<br/>trigger: manual / 手动"):::jobBacktest
    JOB195("backtest.match_fills<br/>回测.撮合成交<br/>trigger: event_driven / 事件驱动"):::jobBacktest
    JOB193("backtest.replay_ticks<br/>回测.Tick重放<br/>trigger: manual / 手动"):::jobBacktest
    JOB194("backtest.run_event_driven<br/>回测.事件驱动运行<br/>trigger: event_driven / 事件驱动"):::jobBacktest
    JOB196("backtest.update_portfolio<br/>回测.更新组合<br/>trigger: event_driven / 事件驱动"):::jobBacktest
    JOB186("aggregate.ohlc_bar<br/>聚合.OHLC K线<br/>trigger: event_driven / 事件驱动"):::jobProd
    JOB190("check.risk_limits<br/>检查.风险限额<br/>trigger: event_driven / 事件驱动"):::jobProd
    JOB188("compute.momentum_20d<br/>计算.20日动量<br/>trigger: event_driven / 事件驱动"):::jobProd
    JOB187("compute.value_factor<br/>计算.价值因子<br/>trigger: event_driven / 事件驱动"):::jobProd
    JOB192("execute.order<br/>执行.订单<br/>trigger: event_driven / 事件驱动"):::jobProd
    JOB191("generate.order<br/>生成.订单<br/>trigger: event_driven / 事件驱动"):::jobProd
    JOB185("ingest.ifind_kline<br/>采集.iFind行情<br/>trigger: scheduled / 定时"):::jobProd
    JOB189("synthesize.signal<br/>合成.信号<br/>trigger: event_driven / 事件驱动"):::jobProd
    JOB185 -->|produces / 产出| DS197
    JOB186 -->|produces / 产出| DS198
    JOB187 -->|produces / 产出| DS199
    JOB188 -->|produces / 产出| DS200
    JOB189 -->|produces / 产出| DS201
    JOB190 -->|produces / 产出| DS202
    JOB191 -->|produces / 产出| DS203
    JOB192 -->|produces / 产出| DS204
    JOB192 -->|produces / 产出| DS205
    JOB197 -->|produces / 产出| DS206
    JOB193 -->|produces / 产出| DS207
    JOB194 -->|produces / 产出| DS208
    JOB195 -->|produces / 产出| DS209
    JOB196 -->|produces / 产出| DS210
    DS197 -->|consumed by / 被消费于| JOB186
    DS197 -->|consumed by / 被消费于| JOB193
    DS198 -->|consumed by / 被消费于| JOB187
    DS198 -->|consumed by / 被消费于| JOB188
    DS199 -->|consumed by / 被消费于| JOB189
    DS200 -->|consumed by / 被消费于| JOB189
    DS201 -->|consumed by / 被消费于| JOB190
    DS201 -->|consumed by / 被消费于| JOB191
    DS202 -->|consumed by / 被消费于| JOB191
    DS203 -->|consumed by / 被消费于| JOB192
    DS207 -->|consumed by / 被消费于| JOB194
    DS208 -->|consumed by / 被消费于| JOB195
    DS209 -->|consumed by / 被消费于| JOB196
    DS210 -->|consumed by / 被消费于| JOB197

    classDef dsProd fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef dsBacktest fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef jobProd fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    classDef jobBacktest fill:#fce4ec,stroke:#880e4f,stroke-width:2px
```

### 生产数据流图（scope=production）

> 节点数: 10 datasets / 数据集, 8 jobs / 作业, 18 edges / 边

```mermaid
flowchart LR
    DS206["backtest.result<br/>回测.结果<br/>CTR: CTR-P1-016<br/>[D_BACKTEST / 回测]"]:::dsProd
    DS200["factor.momentum_20d<br/>因子.20日动量<br/>CTR: CTR-002<br/>[D_FACTOR / 因子]"]:::dsProd
    DS199["factor.value_factor<br/>因子.价值因子<br/>CTR: CTR-002<br/>[D_FACTOR / 因子]"]:::dsProd
    DS204["fill.executed<br/>成交.已成交<br/>CTR: CTR-005<br/>[D_EX_CORE / 执行核心]"]:::dsProd
    DS198["market_data.ohlc_bar<br/>市场数据.OHLC K线<br/>CTR: CTR-001<br/>[D_MKT_DATA / 市场数据]"]:::dsProd
    DS197["market_data.tick<br/>市场数据.Tick行情<br/>CTR: CTR-001<br/>[D_MKT_DATA / 市场数据]"]:::dsProd
    DS203["order.target<br/>订单.目标订单<br/>CTR: CTR-004<br/>[D_PF_CORE / 持仓核心]"]:::dsProd
    DS205["position.snapshot<br/>持仓.快照<br/>CTR: CTR-006<br/>[D_EX_CORE / 执行核心]"]:::dsProd
    DS202["risk.limits<br/>风险.限额<br/>CTR: CTR-003<br/>[D_RISK / 风险]"]:::dsProd
    DS201["signal.composite<br/>信号.合成信号<br/>CTR: CTR-P1-015<br/>[D_SIGLEGACY / 信号(legacy)]"]:::dsProd
    JOB186("aggregate.ohlc_bar<br/>聚合.OHLC K线<br/>trigger: event_driven / 事件驱动"):::jobProd
    JOB190("check.risk_limits<br/>检查.风险限额<br/>trigger: event_driven / 事件驱动"):::jobProd
    JOB188("compute.momentum_20d<br/>计算.20日动量<br/>trigger: event_driven / 事件驱动"):::jobProd
    JOB187("compute.value_factor<br/>计算.价值因子<br/>trigger: event_driven / 事件驱动"):::jobProd
    JOB192("execute.order<br/>执行.订单<br/>trigger: event_driven / 事件驱动"):::jobProd
    JOB191("generate.order<br/>生成.订单<br/>trigger: event_driven / 事件驱动"):::jobProd
    JOB185("ingest.ifind_kline<br/>采集.iFind行情<br/>trigger: scheduled / 定时"):::jobProd
    JOB189("synthesize.signal<br/>合成.信号<br/>trigger: event_driven / 事件驱动"):::jobProd
    JOB185 -->|produces / 产出| DS197
    JOB186 -->|produces / 产出| DS198
    JOB187 -->|produces / 产出| DS199
    JOB188 -->|produces / 产出| DS200
    JOB189 -->|produces / 产出| DS201
    JOB190 -->|produces / 产出| DS202
    JOB191 -->|produces / 产出| DS203
    JOB192 -->|produces / 产出| DS204
    JOB192 -->|produces / 产出| DS205
    DS197 -->|consumed by / 被消费于| JOB186
    DS198 -->|consumed by / 被消费于| JOB187
    DS198 -->|consumed by / 被消费于| JOB188
    DS199 -->|consumed by / 被消费于| JOB189
    DS200 -->|consumed by / 被消费于| JOB189
    DS201 -->|consumed by / 被消费于| JOB190
    DS201 -->|consumed by / 被消费于| JOB191
    DS202 -->|consumed by / 被消费于| JOB191
    DS203 -->|consumed by / 被消费于| JOB192

    classDef dsProd fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef dsBacktest fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef jobProd fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    classDef jobBacktest fill:#fce4ec,stroke:#880e4f,stroke-width:2px
```

### 回测内部数据流图（scope=backtest_internal）

> 节点数: 4 datasets / 数据集, 5 jobs / 作业, 8 edges / 边

```mermaid
flowchart LR
    DS209["backtest.fills<br/>回测.模拟成交<br/>[D_BACKTEST / 回测]"]:::dsBacktest
    DS210["backtest.nav_series<br/>回测.净值序列<br/>[D_BACKTEST / 回测]"]:::dsBacktest
    DS208["backtest.target_weights<br/>回测.目标权重<br/>[D_BACKTEST / 回测]"]:::dsBacktest
    DS207["backtest.tick_event<br/>回测.Tick事件<br/>[D_BACKTEST / 回测]"]:::dsBacktest
    JOB197("backtest.calc_metrics<br/>回测.计算指标<br/>trigger: manual / 手动"):::jobBacktest
    JOB195("backtest.match_fills<br/>回测.撮合成交<br/>trigger: event_driven / 事件驱动"):::jobBacktest
    JOB193("backtest.replay_ticks<br/>回测.Tick重放<br/>trigger: manual / 手动"):::jobBacktest
    JOB194("backtest.run_event_driven<br/>回测.事件驱动运行<br/>trigger: event_driven / 事件驱动"):::jobBacktest
    JOB196("backtest.update_portfolio<br/>回测.更新组合<br/>trigger: event_driven / 事件驱动"):::jobBacktest
    JOB193 -->|produces / 产出| DS207
    JOB194 -->|produces / 产出| DS208
    JOB195 -->|produces / 产出| DS209
    JOB196 -->|produces / 产出| DS210
    DS207 -->|consumed by / 被消费于| JOB194
    DS208 -->|consumed by / 被消费于| JOB195
    DS209 -->|consumed by / 被消费于| JOB196
    DS210 -->|consumed by / 被消费于| JOB197

    classDef dsProd fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef dsBacktest fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef jobProd fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    classDef jobBacktest fill:#fce4ec,stroke:#880e4f,stroke-width:2px
```

## Dataset 清单

| ID | entity_name / 实体名 | scope / 范围 | contract_ref / 契约引用 | domain / 域 | pit_policy / PIT策略 | build_status / 构建状态 |
|----|----------------------|--------------|---------------------------|------------|------------------|--------------------|
| DS-209 | backtest.fills / 回测.模拟成交 | backtest_internal / 回测内部 | - | D_BACKTEST / 回测 | strict / 严格 | generated / 已生成 |
| DS-210 | backtest.nav_series / 回测.净值序列 | backtest_internal / 回测内部 | - | D_BACKTEST / 回测 | strict / 严格 | generated / 已生成 |
| DS-208 | backtest.target_weights / 回测.目标权重 | backtest_internal / 回测内部 | - | D_BACKTEST / 回测 | strict / 严格 | generated / 已生成 |
| DS-207 | backtest.tick_event / 回测.Tick事件 | backtest_internal / 回测内部 | - | D_BACKTEST / 回测 | strict / 严格 | generated / 已生成 |
| DS-206 | backtest.result / 回测.结果 | production / 生产 | CTR-P1-016 | D_BACKTEST / 回测 | strict / 严格 | generated / 已生成 |
| DS-200 | factor.momentum_20d / 因子.20日动量 | production / 生产 | CTR-002 | D_FACTOR / 因子 | strict / 严格 | generated / 已生成 |
| DS-199 | factor.value_factor / 因子.价值因子 | production / 生产 | CTR-002 | D_FACTOR / 因子 | strict / 严格 | generated / 已生成 |
| DS-204 | fill.executed / 成交.已成交 | production / 生产 | CTR-005 | D_EX_CORE / 执行核心 | strict / 严格 | generated / 已生成 |
| DS-198 | market_data.ohlc_bar / 市场数据.OHLC K线 | production / 生产 | CTR-001 | D_MKT_DATA / 市场数据 | strict / 严格 | generated / 已生成 |
| DS-197 | market_data.tick / 市场数据.Tick行情 | production / 生产 | CTR-001 | D_MKT_DATA / 市场数据 | strict / 严格 | generated / 已生成 |
| DS-203 | order.target / 订单.目标订单 | production / 生产 | CTR-004 | D_PF_CORE / 持仓核心 | strict / 严格 | generated / 已生成 |
| DS-205 | position.snapshot / 持仓.快照 | production / 生产 | CTR-006 | D_EX_CORE / 执行核心 | strict / 严格 | generated / 已生成 |
| DS-202 | risk.limits / 风险.限额 | production / 生产 | CTR-003 | D_RISK / 风险 | strict / 严格 | generated / 已生成 |
| DS-201 | signal.composite / 信号.合成信号 | production / 生产 | CTR-P1-015 | D_SIGLEGACY / 信号(legacy) | strict / 严格 | generated / 已生成 |

## Job 清单

| ID | job_name / 作业名 | scope / 范围 | source_code_ref / 源码引用 | trigger_type / 触发类型 | run_context / 运行上下文 | build_status / 构建状态 |
|----|-------------------|--------------|------------------------------|----------------------------|------------------------------|--------------------|
| JOB-197 | backtest.calc_metrics / 回测.计算指标 | backtest_internal / 回测内部 | src/zephyr/backtest/metrics.py | manual / 手动 | backtest_tick | generated / 已生成 |
| JOB-195 | backtest.match_fills / 回测.撮合成交 | backtest_internal / 回测内部 | src/zephyr/backtest/matching_logic.py | event_driven / 事件驱动 | backtest_tick | generated / 已生成 |
| JOB-193 | backtest.replay_ticks / 回测.Tick重放 | backtest_internal / 回测内部 | src/zephyr/backtest/tick_replay.py | manual / 手动 | backtest_tick | generated / 已生成 |
| JOB-194 | backtest.run_event_driven / 回测.事件驱动运行 | backtest_internal / 回测内部 | src/zephyr/backtest/event_engine.py | event_driven / 事件驱动 | backtest_tick | generated / 已生成 |
| JOB-196 | backtest.update_portfolio / 回测.更新组合 | backtest_internal / 回测内部 | src/zephyr/backtest/portfolio.py | event_driven / 事件驱动 | backtest_tick | generated / 已生成 |
| JOB-186 | aggregate.ohlc_bar / 聚合.OHLC K线 | production / 生产 | src/zephyr/data/aggregator.py | event_driven / 事件驱动 | production / 生产 | generated / 已生成 |
| JOB-190 | check.risk_limits / 检查.风险限额 | production / 生产 | src/zephyr/risk/risk_checker.py | event_driven / 事件驱动 | production / 生产 | generated / 已生成 |
| JOB-188 | compute.momentum_20d / 计算.20日动量 | production / 生产 | src/zephyr/factor/momentum.py | event_driven / 事件驱动 | production / 生产 | generated / 已生成 |
| JOB-187 | compute.value_factor / 计算.价值因子 | production / 生产 | src/zephyr/factor/value_factor.py | event_driven / 事件驱动 | production / 生产 | generated / 已生成 |
| JOB-192 | execute.order / 执行.订单 | production / 生产 | src/zephyr/ex_core/executor.py | event_driven / 事件驱动 | production / 生产 | generated / 已生成 |
| JOB-191 | generate.order / 生成.订单 | production / 生产 | src/zephyr/pf_core/order_generator.py | event_driven / 事件驱动 | production / 生产 | generated / 已生成 |
| JOB-185 | ingest.ifind_kline / 采集.iFind行情 | production / 生产 | src/zephyr/data/ingest_ifind.py | scheduled / 定时 | production / 生产 | generated / 已生成 |
| JOB-189 | synthesize.signal / 合成.信号 | production / 生产 | src/zephyr/signal_ashare/synthesizer.py | event_driven / 事件驱动 | production / 生产 | generated / 已生成 |
