# 数据流图（dataflowgraph）索引

> 生成时间: 2026-07-06T05:09:04
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

### 全景图
- [dataflow_overview.mmd](dataflow_overview.mmd)

### 生产数据流图（scope=production）
- [dataflow_production.mmd](dataflow_production.mmd)

### 回测内部数据流图（scope=backtest_internal）
- [dataflow_backtest.mmd](dataflow_backtest.mmd)

## Dataset 清单

| ID | entity_name | scope | contract_ref | domain | pit_policy | build_status |
|----|-------------|-------|--------------|--------|------------|--------------|
| DS-083 | backtest.fills | backtest_internal | - | D_BACKTEST | strict | generated |
| DS-084 | backtest.nav_series | backtest_internal | - | D_BACKTEST | strict | generated |
| DS-082 | backtest.target_weights | backtest_internal | - | D_BACKTEST | strict | generated |
| DS-081 | backtest.tick_event | backtest_internal | - | D_BACKTEST | strict | generated |
| DS-080 | backtest.result | production | CTR-P1-016 | D_BACKTEST | strict | generated |
| DS-074 | factor.momentum_20d | production | CTR-002 | D_FACTOR | strict | generated |
| DS-073 | factor.value_factor | production | CTR-002 | D_FACTOR | strict | generated |
| DS-078 | fill.executed | production | CTR-005 | D_EX_CORE | strict | generated |
| DS-072 | market_data.ohlc_bar | production | CTR-001 | D_MKT_DATA | strict | generated |
| DS-071 | market_data.tick | production | CTR-001 | D_MKT_DATA | strict | generated |
| DS-077 | order.target | production | CTR-004 | D_PF_CORE | strict | generated |
| DS-079 | position.snapshot | production | CTR-006 | D_EX_CORE | strict | generated |
| DS-076 | risk.limits | production | CTR-003 | D_RISK | strict | generated |
| DS-075 | signal.composite | production | CTR-P1-015 | D_SIGLEGACY | strict | generated |

## Job 清单

| ID | job_name | scope | source_code_ref | trigger_type | run_context | build_status |
|----|----------|-------|-----------------|--------------|-------------|--------------|
| JOB-080 | backtest.calc_metrics | backtest_internal | src/zephyr/backtest/metrics.py | manual | backtest_tick | generated |
| JOB-078 | backtest.match_fills | backtest_internal | src/zephyr/backtest/matching_logic.py | event_driven | backtest_tick | generated |
| JOB-076 | backtest.replay_ticks | backtest_internal | src/zephyr/backtest/tick_replay.py | manual | backtest_tick | generated |
| JOB-077 | backtest.run_event_driven | backtest_internal | src/zephyr/backtest/event_engine.py | event_driven | backtest_tick | generated |
| JOB-079 | backtest.update_portfolio | backtest_internal | src/zephyr/backtest/portfolio.py | event_driven | backtest_tick | generated |
| JOB-069 | aggregate.ohlc_bar | production | src/zephyr/data/aggregator.py | event_driven | production | generated |
| JOB-073 | check.risk_limits | production | src/zephyr/risk/risk_checker.py | event_driven | production | generated |
| JOB-071 | compute.momentum_20d | production | src/zephyr/factor/momentum.py | event_driven | production | generated |
| JOB-070 | compute.value_factor | production | src/zephyr/factor/value_factor.py | event_driven | production | generated |
| JOB-075 | execute.order | production | src/zephyr/ex_core/executor.py | event_driven | production | generated |
| JOB-074 | generate.order | production | src/zephyr/pf_core/order_generator.py | event_driven | production | generated |
| JOB-068 | ingest.ifind_kline | production | src/zephyr/data/ingest_ifind.py | scheduled | production | generated |
| JOB-072 | synthesize.signal | production | src/zephyr/signal_ashare/synthesizer.py | event_driven | production | generated |
