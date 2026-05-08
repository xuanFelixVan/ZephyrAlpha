---
module_id: KE-documentat-10_1_metrics-000
title: 10.1 Metrics / 指标
category: documentation
---

# 10.1 Metrics / 指标

10.1 Metrics / 指标

**业务指标**：

| Metric Name | 说明 | SLO 关联 |
|-------------|------|---------|
| `zephyr_orders_total` | 订单提交总数 | SLO-3 |
| `zephyr_order_fill_rate` | 成交率 | SLO-3 |
| `zephyr_pnl_daily` | 日 PnL | — |
| `zephyr_backtest_duration_seconds` | 回测耗时 | SLO-4 |
| `zephyr_factor_refresh_lag_seconds` | 因子刷新滞后 | SLO-5 |

**技术指标**：

| Metric Name | 说明 | 告警阈值 |
|-------------|------|---------|
| `zephyr_request_duration_seconds` | API 调用延迟 | p99 > 5s |
| `zephyr_error_rate` | 错误率（分 layer） | > 1% |
| `zephyr_llm_tokens_total` | LLM Token 消耗 | 月超阈值 |
| `zephyr_data_freshness_lag_seconds` | 数据新鲜度 | SLO-1 p99 ≤180s |

**基础设施指标**：`process_cpu_seconds_total`（>80% 5min 告警）、`process_resident_memory_bytes`（>8GB）、`disk_io_time_seconds_total`（写延迟 >100ms）
