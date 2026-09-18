---
ttl: task_bound
completes_when: 全流通战役收口报告归档
---

# 处方 · 议息日历换源（片段 ②③）与 intraday_sector 停档期（⑤）——待裁/待他车道

## A. 议息日历双源并接（datagap 片段 ②③，**本车道未并入 tasks.yaml**）
片段提的两条任务 `source: fed_official` 与 `source: eastmoney_datacenter` 在数据源注册表
中**不存在**（本车道禁写 provider 面）。直接登记 = 每班 fetch 必失败的空挂任务，
正是本轮要消灭的"任务在册=有数据"错觉（R-021），故只做处方：
1. 在 `data_sources_registry` 注册 Fed 官网（federalreserve.gov monetarypolicy 日历）与
   东财数据中心两条通道，落 `CapabilityContract("rate_decision_calendar")`；
2. 能力到位后再把片段两条任务落 `schedule: weekly_capital`（Fed 权威主源 + 东财补国内腿，
   `snapshot_raw: true` 留原文快照，防再次"第三方转述停更 2494 天无人知"）；
3. 现 `rate_decision_calendar_refresh`（金十 akshare macro_bank_* 族）**禁删**，
   换源确认后按 BRK-051 先例改 `schedule: disabled` + `disabled_reason` 留痕；
4. 哨兵侧已先钉三条腿：ingest 心跳腿（存活）+ `decision_date` 表级业务腿（75d）+
   `bank_code='pboc'` 维度腿（90d）。换源完成后三条腿应同时转绿；
   若 Owner 决定止噪，只可临时放宽 `max_lag_days` 并写 `reviewed_at/reviewed_by`，**禁删行**。

## B. intraday_sector 五任务停档期（片段 ⑤，登记 `req_sentinel_02` 待裁）
实测：`data_source='tdx'` 真值自 2026-09-11 起 0 行，近端只有 `synth_sh/synth_eq` 合成行；
5 个 `kline_sector_*_incremental` 任务仍每 5 分钟唤醒。片段建议停档期。
本车道**不代做该决定**（=生产切换，且合成分区正是这些任务产出的，停用会改变下游可见数据），
只把"真值源无行"点亮成常驻红：`row_filter: "data_source = 'tdx'"` +
`min_rows_in_window {window_days:5, min_rows:100000}`（实测 rows=0 < floor，红）。

## C. SHFE 仓单与 pboc 维度备源
`futures_warehouse_receipt_backfill_shfe`（disabled）与 SHFE 实时腿同族，305 天停更已点亮；
备源通道建设归数据源车道，本车道只保证"停更每天都在响"。
