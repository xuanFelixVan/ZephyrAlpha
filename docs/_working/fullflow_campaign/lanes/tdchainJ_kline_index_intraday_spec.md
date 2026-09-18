---
ttl: task_bound
completes_when: residG 车道按本规格落地 kline_index_intraday DDL 与采集任务登记
title: kline_index_intraday 建表规格（tdchainJ 车道出品，转 residG 执行）
lane: st-ff-tdchainJ-20260918
date: 2026-09-18
---

# `c1_market.kline_index_intraday` 建表规格

> 出品依据：a0 总谱 §3 数据面缺口（kline_index_intraday 不存在，intraday_l1_tracker 用 510300 代理）+
> 总包预裁（立项，residG 执行）。房规对齐实测 `SHOW CREATE TABLE c1_market.kline_etf_15min`
> （2026-09-18 午后，DatabaseService 只读）。

## 1. 用途与消费方

- 消费方：`src/zephyr/plan_engine/intraday_l1_tracker.py`（摘除 `pending_minute_source(etf_510300_proxy)`
  代理，改用真实指数分钟线）；后续 L2/L3 盘中链路可复用。
- 标的范围（首批建议）：`000001`（上证综指）、`000300`（沪深300）、`399006`（创业板指）、
  `000905`（中证500）。symbol 口径=**裸码**（对齐 `market_index_kline`/`kline_index` 既有惯例：
  `000001` 非 `000001.SH`），交易所归属走 `exchange` 列。

## 2. DDL（字段/引擎/排序键/分区）

```sql
CREATE TABLE IF NOT EXISTS c1_market.kline_index_intraday
(
    trade_date   Date,
    trade_time   DateTime64(3, 'Asia/Shanghai'),   -- RULE-SCHEMA-TZ：显式时区
    symbol       String,                            -- 裸码（'000001'）
    period       LowCardinality(String),            -- '1min'/'5min'/'15min'/'30min'/'60min'
    open         Decimal(18, 4),
    close        Decimal(18, 4),
    high         Decimal(18, 4),
    low          Decimal(18, 4),
    volume       UInt64,
    amount       Decimal(18, 2),
    pct_change   Decimal(18, 4) DEFAULT 0,
    amplitude    Decimal(18, 4) DEFAULT 0,
    data_source  LowCardinality(String) DEFAULT 'xtdata',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now()
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, period, trade_time)
SETTINGS index_granularity = 8192;
```

设计要点：
- **单表多周期**（period 列入排序键）而非 kline_etf_* 的五表分拆：指数标的数少（首批 4 只），
  分表收益低；消费方按 `period='1min'` 过滤即得与分表等价性能。若 residG 评估后坚持房规分表
  （kline_index_1min/5min/...），字段与引擎口径不变，仅去 period 列——两案均可，residG 定。
- ReplacingMergeTree + 查询必带 `FINAL`（c1_market 全系房规，CONSTRUCTION_DISCIPLINE §7）。
- 时区：trade_time 显式 `Asia/Shanghai`、ingest_ts `UTC`——与 kline_etf_15min 实测 DDL 完全同构
  （本次 ETF 时区劈叉事故的教训面：写入侧禁 naive 时间戳）。
- 指数无成交额时 amount 置 0 不置 NULL（对齐既有 K 线族）。

## 3. 写入侧（采集任务）

- 落点：`src/zephyr/data/config/tasks.yaml` 新增任务（residG 独占文件）；数据源建议 xtdata
  指数分钟K（与 miniQMT 采集链同构，白班终端在线窗内回补）或 bdpan 备源。
- 幂等键：`(symbol, period, trade_time)`；禁 forming bar 中间态入库（本仓明确禁），
  只写已收盘 bar。
- 批量写入遵守 CH-BATCH-SIZE：`BufferedWriter` 循环 add + flush，禁 for 体内 write_result。

## 4. 验收判据

1. DDL 落地后 `system.tables` 可查到该表；
2. 采集任务跑通一个交易日后：`SELECT period, count() ... FINAL GROUP BY period` 各周期非空；
3. 抽查一日 000300 的 1min  bar 数 = 240（沪深交易分钟数）；
4. `intraday_l1_tracker.py` 消费切换与代理注记摘除=另批（不在本规格验收内）。

## 5. 边界声明

- 本车道（tdchainJ）只交规格：`apply_market_tables_ddl.py`、`tasks.yaml` 均归 residG 独占，未触碰。
- 表名注册：新表须挂 TABLE-NAME-REGISTRY 品类 YAML（residG 施工批同批落地，防硬编码表名门禁连坐）。
