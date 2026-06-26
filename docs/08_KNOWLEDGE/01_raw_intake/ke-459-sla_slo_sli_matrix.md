---
module_id: KE-459
status: active
title: 5.2 SLA / SLO / SLI matrix / 服务等级矩阵
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 5.2 SLA / SLO / SLI matrix / 服务等级矩阵

5.2 SLA / SLO / SLI matrix / 服务等级矩阵

> **术语铁律**：**SLA**（Service Level Agreement）= 对外承诺（当前单人，无外部合同 → 大部分 SLA 列标 "internal commitment"，仅 Vendor 契约列真实 SLA）。**SLO**（Service Level Objective）= 内部目标（可量化）。**SLI**（Service Level Indicator）= 实际测量指标（可落到 metric）。
>
> **测量 / 上报位置**：所有 SLI 均接入 `technology_architecture.md §10 Observability Architecture`（当前为占位，由批次 C 任务 5.3 H14 填充，用 OpenTelemetry Metrics/Logs/Traces 三支柱）。完成前以 **"📌 → 04-TA §10 (TODO)"** 标注引用锚。

| # | SLO 名称 | 定义与场景 | Target (quant)<br/>目标值 | SLI 测量方法 | 上报位置 | 违约后果 |
|---|---------|-----------|-----------------------|-----------|---------|---------|
| **SLO-1** | **Data Freshness**<br/>数据新鲜度 | 市场时段行情从 vendor 发布到数据湖可查询的端到端延迟 | 分钟级 bar：p50 ≤ 15 s / p95 ≤ 60 s / p99 ≤ 180 s<br/>日度结算：T+1 **11:00 UTC+8** 前 100% 到齐（p99）<br/>Reference 数据（证券主数据 / 交易日历）：T 日 **18:00 UTC+8** 前到齐 | `ts_ingest − vendor_release_ts` 差值（见 `05-DA §4` PIT 三字段）；histogram export to Prometheus | 📌 → 04-TA §10 (TODO)<br/>Prom metric：`data_freshness_seconds{dataset,vendor}` | 触发 B1 降级 + 阻塞因子刷新（SLO-5）|
| **SLO-2** | **Signal Generation Latency**<br/>信号生成端到端延迟 | 市场数据进入 → 信号 payload 发布的端到端 p99（intraday batch 场景）| p50 ≤ 30 s / p95 ≤ 60 s / p99 ≤ **90 s**<br/>EOD 策略：p95 ≤ **10 min** | OTel 分布式 trace：`span=signal_generation`，端点 = data ingress timestamp → signal publish timestamp | 📌 → 04-TA §10 (TODO)<br/>OTel trace + `signal_latency_seconds` histogram | 超限则信号标记 `stale=true`，下游 portfolio 降级处理 |
| **SLO-3** | **Order Submission Latency**<br/>下单提交延迟 | 从信号发布（含通过 pre-trade risk gate）到券商 broker ACK 的 p99 | p50 ≤ 5 s / p95 ≤ 15 s / p99 ≤ **30 s**<br/>（含 A09 pre-trade risk p99 ≤ 1 s + 券商网络）| OTel span：`span=order_submit`，起点 `signal.published_at`，终点 `broker_ack_at`；Idempotency Key 命中率一并记录 | 📌 → 04-TA §10 (TODO)<br/>`order_submit_latency_seconds` + `idempotency_hit_total` | 超限则 kill-switch 触发（A13），已下订单走 H10 幂等回执 |
| **SLO-4** | **Backtest Turnaround**<br/>回测周转 TAT | 常规回测（单策略 × 5 年日频全市场）提交到结果可用的 end-to-end | 常规：p50 ≤ 10 min / p95 ≤ **30 min** / p99 ≤ 60 min<br/>重度（因子扫描 / 参数网格）：p95 ≤ **4 h** | Job 执行时长 metric：`backtest_duration_seconds{type}`；队列等待单独记 `backtest_queue_wait_seconds` | 📌 → 04-TA §10 (TODO) | 触发 B2 降级，考虑并行调度器（Airflow/Prefect）|
| **SLO-5** | **Factor Refresh Window**<br/>因子刷新窗口 | 日度因子与分钟因子的刷新时效 | 日度因子：EOD T 日 18:00 + **90 min** 内 100% 刷新完成（p99）<br/>分钟因子（滚动）：每 **5 min** 刷新一次，p99 完成时间 ≤ **5 min** | `factor_refresh_duration_seconds{cadence,factor_id}` + 完成率 `factor_refresh_success_ratio` | 📌 → 04-TA §10 (TODO) | 下游信号标记 `factor_stale=true`；连续 2 个窗口失败告警 |
| **SLO-6** | **System Availability**<br/>系统可用性 | 核心链路（data ingest + signal gen + order submit）在市场时段的月可用性 | 市场时段：**99.9% / month**（单月允许停机 ≤ **43.2 min**）<br/>非市场时段：best-effort（无承诺）| Blackbox probe 每 30 s ping 核心端点；SLI = `1 − downtime_min / market_hours_min` | 📌 → 04-TA §10 (TODO)<br/>`availability_ratio{component}` | 超限触发事后 incident review + ADR（可审计链）|
| **SLO-7** | **Data Quality**<br/>数据质量 | PIT / survivorship / lineage 三断言 + 完整度 / 一致性 / 及时性三维度 | 完整度（Completeness）：≥ **99.5%**（缺失率 ≤ 0.5%）<br/>一
