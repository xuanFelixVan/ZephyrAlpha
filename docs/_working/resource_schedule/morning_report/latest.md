---
ttl: task_bound
status: active
generated_at: '2026-09-21T22:31:02+00:00'
---

# 资源晨报（L-9） — 2026-09-22（Asia/Shanghai）

> 生成：2026-09-21T22:31:02+00:00 · scripts/governance/generators/generate_resource_morning_report.py
> 数据源：注册表、孵化台账、样本流、通知板、闸同池并发账（只读）（零新数据源，判据全在真源侧）

## 1. 今日排班时间线（按窗起点排序，33 个实体开工 / 346 个开工窗）

| 首窗 | 末窗止 | 次数 | task_id | 池 | 申报时长(min) | 实测P90(min) | 申报内存(GB) | 状态 |
|---|---|---|---|---|---|---|---|---|
| 00:03 | 03:15 | 64 | data_slot_event_driven | default | 3 | - | 1.0 | active |
| 00:17 | 02:47 | 48 | data_slot_news_slow | default | 180 | - | 2.0 | active |
| 03:30 | 04:00 | 1 | sch_gate_full_tree_audit | default | 30 | 5 | 0.5 | active |
| 05:30 | 06:00 | 1 | data_slot_catchup_guard | default | 30 | - | 1.0 | active |
| 05:40 | 05:55 | 1 | sch_resource_sampler_writeback | default | 15 | - | 0.5 | active |
| 05:50 | 06:05 | 1 | sch_resource_view_publish | default | 15 | - | 1.0 | active |
| 06:31 | 06:36 | 1 | sch_resource_morning_report | default | 5 | 0 | 0.5 | active |
| 06:50 | 07:20 | 1 | data_slot_data_supply_sentinel | default | 30 | - | 2.0 | active |
| 07:10 | 07:40 | 1 | data_slot_calendar_coverage_check | default | 30 | - | 2.0 | active |
| 08:05 | 08:15 | 1 | sch_config_check | default | 10 | - | 0.5 | active |
| 08:20 | 08:40 | 1 | data_slot_nightly_sentiment | default | 20 | - | 1.0 | active |
| 08:34 | 08:49 | 1 | data_slot_pre_market | default | 15 | - | 1.5 | active |
| 08:41 | 08:51 | 1 | data_slot_daily_crypto | default | 10 | - | 1.0 | active |
| 09:00 | 14:17 | 64 | data_slot_intraday_minute | realtime | 2 | - | 1.0 | active |
| 09:00 | 14:17 | 64 | data_slot_intraday_realtime | realtime | 2 | - | 1.0 | active |
| 09:00 | 14:17 | 64 | data_slot_intraday_sector | realtime | 2 | - | 1.0 | active |
| 09:01 | 09:06 | 1 | sch_pattern_mining | default | 5 | - | 1.0 | active |
| 09:15 | 09:35 | 11 | data_slot_auction_highfreq | realtime | 10 | - | 1.0 | active |
| 09:25 | 09:55 | 1 | sch_paper_session | realtime | 30 | 9 | 1.0 | active |
| 10:05 | 15:15 | 5 | sch_intraday_fund_flow | realtime | 10 | - | 0.5 | active |
| 15:10 | 15:20 | 1 | sch_index_minute_eod | default | 10 | - | 0.5 | active |
| 15:30 | 16:00 | 1 | sch_post_settlement | default | 30 | 0 | 0.5 | active |
| 15:40 | 16:10 | 1 | data_slot_eod_reconciliation | default | 30 | - | 2.0 | active |
| 16:30 | 18:00 | 1 | data_slot_daily_kline | heavy | 90 | - | 3.0 | active |
| 16:45 | 17:15 | 1 | data_slot_dloop_post | default | 30 | - | 2.0 | active |
| 17:00 | 19:00 | 1 | data_slot_daily_backfill | heavy | 120 | - | 2.5 | active |
| 18:00 | 18:45 | 1 | data_slot_daily_capital | default | 45 | - | 2.0 | active |
| 19:00 | 19:45 | 1 | data_slot_daily_event | default | 45 | - | 2.0 | active |
| 20:30 | 22:30 | 1 | data_slot_research_nightly | default | 120 | - | 2.5 | active |
| 22:00 | 00:00 | 1 | data_slot_nightly_financial | heavy | 120 | - | 3.0 | active |
| 23:00 | 23:15 | 1 | data_slot_integrity_check | default | 15 | - | 1.0 | active |
| 23:30 | 00:30 | 1 | data_slot_consensus_crosscheck | default | 60 | - | 2.5 | active |
| 23:35 | 00:05 | 1 | data_slot_daily_alt_fx | default | 30 | - | 2.0 | active |

> 注：标 64 次的行被闸 `expand_windows` 单表达式 64 步上限截断，末窗非本日真末窗（逐窗明细真源=周历视图，晨报名下不抄第二份）。

未排产/常驻实体 54 个（不计入今日冲突账，planned 走 R-D 裁定）：

> data_slot_monthly_static、data_slot_weekend_backfill、data_slot_weekend_calibration、drill_emergency_bypass、drill_recovery、drill_script_failure、dynamic_local_replay、event_dashboard_backtest_run、event_dashboard_services_control、event_model_exam_trigger、manual_bdpan_tick_backfill、manual_bse_minute_backfill…余 42 个见注册表

## 2. 当前同刻冲突（第四查 sched_pool_concurrency，地平线 1 天）

- 待清零（block）：**0**
- 留痕（warn）：1
- co_start_intent 豁免对（裁定 R-F，不计冲突）：13

- `[warn] sched_pool_concurrency` **data_slot_auction_highfreq+data_slot_intraday_minute+data_slot_intraday_realtime+data_slot_intraday_sector+sch_intraday_fund_flow+sch_paper_session** — 池 realtime 同刻共开工意图声明豁免 13 对（双方均声明 co_start_intent，判据①不记账；判据②内存预算与互斥组交叠照判）

## 3. 校准 flag 摘要（申报 vs 实测偏差 >阈值）

- 报告生成：2026-09-18T22:17:03+00:00 · 阈值 30.0%
- flag 字段数：11（实体 7）｜低估 2｜高估 9｜样本不足 76

| task_id | 字段 | 申报 | 实测 | 偏差 | 方向 | 建议 |
|---|---|---|---|---|---|---|
| manual_kronos_adapter | est_duration_min | 5.0 | 3.1 | -38.0% | 高估 | 建议下调申报值（实测更短/更小，白占并发预算） |
| manual_kronos_adapter | peak_mem_gb | 0.5 | 0.1616 | -67.7% | 高估 | 建议下调申报值（实测更短/更小，白占并发预算） |
| sch_c4_exam | est_duration_min | 480.0 | 2.6 | -99.5% | 高估 | 建议下调申报值（实测更短/更小，白占并发预算） |
| sch_c4_exam | peak_mem_gb | 2.0 | 0.0817 | -95.9% | 高估 | 建议下调申报值（实测更短/更小，白占并发预算） |
| sch_factory_lane_c | peak_mem_gb | 2.0 | 0.0819 | -95.9% | 高估 | 建议下调申报值（实测更短/更小，白占并发预算） |
| sch_ollama_serve | peak_mem_gb | 8.0 | 0.3774 | -95.3% | 高估 | 建议下调申报值（实测更短/更小，白占并发预算） |
| sch_post_settlement | est_duration_min | 30.0 | 0.5 | -98.3% | 高估 | 建议下调申报值（实测更短/更小，白占并发预算） |
| sch_process_reaper | est_duration_min | 6.0 | 2.2 | -63.3% | 高估 | 建议下调申报值（实测更短/更小，白占并发预算） |
| sch_process_reaper | peak_mem_gb | 0.5 | 0.2808 | -43.8% | 高估 | 建议下调申报值（实测更短/更小，白占并发预算） |
| sch_worktree_drift_watchdog | est_duration_min | 1.0 | 464.9 | 46390.0% | 低估 | 建议上调申报值（实测更长/更大，班次会压到下一班） |
| sch_worktree_drift_watchdog | peak_mem_gb | 0.5 | 3.4117 | 582.3% | 低估 | 建议上调申报值（实测更长/更大，班次会压到下一班） |

> 校正批须经人在环改申报值：measured.* 写权归采样器 writeback，校准器只出报告。

## 4. 告警板未决条目（共 105：critical 21 / warning 84；近期已解除灰显 23）

- **[critical]** 告警外发通道不可用（fail-closed）（`alert-webhook/channel-unavailable`，×1，首发 2026-09-21T20:02:42+00:00）enabled=false（缺省 fail-closed：无端点配置即不外发）；本轮 1 条告警无机器侧出口
- **[critical]** 告警外发通道不可用（fail-closed）（`alert-webhook/channel-unavailable`，×1，首发 2026-09-21T19:02:18+00:00）enabled=false（缺省 fail-closed：无端点配置即不外发）；本轮 1 条告警无机器侧出口
- **[critical]** 告警外发通道不可用（fail-closed）（`alert-webhook/channel-unavailable`，×1，首发 2026-09-21T16:26:08+00:00）enabled=false（缺省 fail-closed：无端点配置即不外发）；本轮 1 条告警无机器侧出口
- **[critical]** 告警外发通道不可用（fail-closed）（`alert-webhook/channel-unavailable`，×1，首发 2026-09-21T13:19:55+00:00）enabled=false（缺省 fail-closed：无端点配置即不外发）；本轮 1 条告警无机器侧出口
- **[critical]** 告警外发通道不可用（fail-closed）（`alert-webhook/channel-unavailable`，×1，首发 2026-09-21T09:19:19+00:00）enabled=false（缺省 fail-closed：无端点配置即不外发）；本轮 1 条告警无机器侧出口
- **[critical]** 告警外发通道不可用（fail-closed）（`alert-webhook/channel-unavailable`，×1，首发 2026-09-21T06:20:34+00:00）enabled=false（缺省 fail-closed：无端点配置即不外发）；本轮 1 条告警无机器侧出口
- **[critical]** 告警外发通道不可用（fail-closed）（`alert-webhook/channel-unavailable`，×1，首发 2026-09-21T05:59:43+00:00）enabled=false（缺省 fail-closed：无端点配置即不外发）；本轮 1 条告警无机器侧出口
- **[critical]** 告警外发通道不可用（fail-closed）（`alert-webhook/channel-unavailable`，×1，首发 2026-09-21T05:32:37+00:00）enabled=false（缺省 fail-closed：无端点配置即不外发）；本轮 1 条告警无机器侧出口
- **[critical]** 告警外发通道不可用（fail-closed）（`alert-webhook/channel-unavailable`，×1，首发 2026-09-21T04:18:55+00:00）enabled=false（缺省 fail-closed：无端点配置即不外发）；本轮 1 条告警无机器侧出口
- **[critical]** 告警外发通道不可用（fail-closed）（`alert-webhook/channel-unavailable`，×1，首发 2026-09-21T03:10:40+00:00）enabled=false（缺省 fail-closed：无端点配置即不外发）；本轮 1 条告警无机器侧出口
- **[critical]** 告警外发通道不可用（fail-closed）（`alert-webhook/channel-unavailable`，×1，首发 2026-09-21T02:46:13+00:00）enabled=false（缺省 fail-closed：无端点配置即不外发）；本轮 1 条告警无机器侧出口
- **[critical]** 告警外发通道不可用（fail-closed）（`alert-webhook/channel-unavailable`，×1，首发 2026-09-21T01:18:41+00:00）enabled=false（缺省 fail-closed：无端点配置即不外发）；本轮 1 条告警无机器侧出口
- …余 93 条见 `GET /api/ops-notifications`

## 5. 再生新鲜度

- 注册表再生时刻：2026-09-21T16:21:23Z（距今 6.2 小时）
- total_entities 声明 88 vs 实盘 88：一致
- 样本流最近落盘：2026-09-21T22:30:44+00:00（距今 0.0 小时）
- 孵化台账：995 条（存活 995，坏行 0）

