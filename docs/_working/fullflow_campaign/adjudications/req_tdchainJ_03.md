---
ttl: task_bound
completes_when: 总包将 kline_index_intraday 建表规格转交 residG 车道执行（DDL 落地+tasks.yaml 登记）
title: 裁定申请书 req_tdchainJ_03——kline_index_intraday 新表立项（转 residG）
lane: st-ff-tdchainJ-20260918
date: 2026-09-18
---

# req_tdchainJ_03 · `kline_index_intraday` 新表立项（总包预裁=立项，residG 执行）

## 背景

- 缺表实测（2026-09-18 午后，DatabaseService 只读）：`system.tables` 中
  `c1_market.kline_index_intraday` = 0 件；库内既有 index 族 = `kline_index`（日频）/`kline_index_calc`/
  `index_quote`/`market_index_meta` 等，无指数分钟表。
- 现行降级：`src/zephyr/plan_engine/intraday_l1_tracker.py:405-409`
  `proxy_notes.index_intraday = "pending_minute_source(etf_510300_proxy)"`——用 510300 ETF 分钟线
  代理指数分钟线，L1 跟踪器精度受代理基差污染。
- 归属：建表须改 `scripts/ch/apply_market_tables_ddl.py`（residG 独占，COORDINATION_LEDGER §2）；
  写入侧任务登记须碰 `src/zephyr/data/config/tasks.yaml`（同 residG 独占）——故本车道只交规格不施工。

## DDL 规格

全文见：`docs/_working/fullflow_campaign/lanes/tdchainJ_kline_index_intraday_spec.md`
（字段/引擎/排序键/分区/时区口径，对齐 `kline_etf_15min` 实测房规，RULE-SCHEMA-TZ 合规）。

## 请求总包动作

1. 确认立项（预裁已给：立项，由 residG 车道执行）；
2. 转交 residG：DDL 入 `apply_market_tables_ddl.py` + 采集任务入 `tasks.yaml`（数据源=指数分钟线，
   建议 xtdata 指数分钟K 或 bdpan 同源，与 kline_etf_* 采集链同构）；
3. 落地后由消费侧（plan_engine）摘除 510300 代理注记（另批，不属本申请）。

## 影响面

纯新增表+新增采集任务，零既有表变更；消费侧切换另批走独立门。
