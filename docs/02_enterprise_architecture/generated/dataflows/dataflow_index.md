# 数据流图（dataflowgraph）索引

> 生成时间: 2026-07-06T05:32:58
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
| DS-139 | backtest.fills | backtest_internal | - | D_BACKTEST | strict | generated |
| DS-140 | backtest.nav_series | backtest_internal | - | D_BACKTEST | strict | generated |
| DS-138 | backtest.target_weights | backtest_internal | - | D_BACKTEST | strict | generated |
| DS-137 | backtest.tick_event | backtest_internal | - | D_BACKTEST | strict | generated |
| DS-136 | backtest.result | production | CTR-P1-016 | D_BACKTEST | strict | generated |
| DS-130 | factor.momentum_20d | production | CTR-002 | D_FACTOR | strict | generated |
| DS-129 | factor.value_factor | production | CTR-002 | D_FACTOR | strict | generated |
| DS-134 | fill.executed | production | CTR-005 | D_EX_CORE | strict | generated |
| DS-128 | market_data.ohlc_bar | production | CTR-001 | D_MKT_DATA | strict | generated |
| DS-127 | market_data.tick | production | CTR-001 | D_MKT_DATA | strict | generated |
| DS-133 | order.target | production | CTR-004 | D_PF_CORE | strict | generated |
| DS-135 | position.snapshot | production | CTR-006 | D_EX_CORE | strict | generated |
| DS-132 | risk.limits | production | CTR-003 | D_RISK | strict | generated |
| DS-131 | signal.composite | production | CTR-P1-015 | D_SIGLEGACY | strict | generated |

## Job 清单

| ID | job_name | scope | source_code_ref | trigger_type | run_context | build_status |
|----|----------|-------|-----------------|--------------|-------------|--------------|
| JOB-132 | backtest.calc_metrics | backtest_internal | src/zephyr/backtest/metrics.py | manual | backtest_tick | generated |
| JOB-130 | backtest.match_fills | backtest_internal | src/zephyr/backtest/matching_logic.py | event_driven | backtest_tick | generated |
| JOB-128 | backtest.replay_ticks | backtest_internal | src/zephyr/backtest/tick_replay.py | manual | backtest_tick | generated |
| JOB-129 | backtest.run_event_driven | backtest_internal | src/zephyr/backtest/event_engine.py | event_driven | backtest_tick | generated |
| JOB-131 | backtest.update_portfolio | backtest_internal | src/zephyr/backtest/portfolio.py | event_driven | backtest_tick | generated |
| JOB-121 | aggregate.ohlc_bar | production | src/zephyr/data/aggregator.py | event_driven | production | generated |
| JOB-125 | check.risk_limits | production | src/zephyr/risk/risk_checker.py | event_driven | production | generated |
| JOB-123 | compute.momentum_20d | production | src/zephyr/factor/momentum.py | event_driven | production | generated |
| JOB-122 | compute.value_factor | production | src/zephyr/factor/value_factor.py | event_driven | production | generated |
| JOB-127 | execute.order | production | src/zephyr/ex_core/executor.py | event_driven | production | generated |
| JOB-126 | generate.order | production | src/zephyr/pf_core/order_generator.py | event_driven | production | generated |
| JOB-120 | ingest.ifind_kline | production | src/zephyr/data/ingest_ifind.py | scheduled | production | generated |
| JOB-124 | synthesize.signal | production | src/zephyr/signal_ashare/synthesizer.py | event_driven | production | generated |
