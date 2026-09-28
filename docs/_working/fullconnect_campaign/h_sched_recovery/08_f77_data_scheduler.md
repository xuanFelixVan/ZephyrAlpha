---
ttl: task_bound
title: F77 数据调度常驻（DataScheduler 25 槽/tasks.yaml 271 任务）——L08 复飞矿道案卷·STALE 13/假绿 5 归属卷
session: zc-l08-20260927
---

# F77 · 数据调度常驻

> 总册行：I 段 F77，状态 built，P1，`src/zephyr/data/scheduler.py`。M0=S2。
> 本卷=09-27 复飞复测。基册=m5_scheduling/02 册 §五+03 册（25 槽全景）。本卷主责=**STALE 13 腿/假绿 5 腿归属标注（今日清单 §2.2）+tasks.yaml 分母勘误**。

## 一、六向台账（实证锚点，09-27 活探）

| 向 | 内容 |
|----|------|
| 上游输入 | src/zephyr/data/config/tasks.yaml（**09-27 实测 task_id 计 271，其中 option_daily_stats 一条 disabled: true=#ARCH-CH-022 capability 契约拦截在案**——270 活+1 禁=骨架 271 分母差的解，见勘误）；schedule.yaml（排班真源 25 槽） |
| 下游消费 | CH/PG 数据表全消费端；data_supply_sentinel 断供哨兵；Alerter/前端 OpsAlertFeed |
| 自动化触发 | 09-27 实测：`ZephyrAlpha_DataScheduler` Running（guard 三链 wscript→start_scheduler.ps1→python -m zephyr.data.scheduler）；`tmp/scheduler.heartbeat`=2026-09-27T06:54:16（guard 21540/child 29748，新鲜）；scheduler_run.log 滚动至 06:54（akshare/FRED/RSS 实跑行） |
| 真源与注册表 | schedule.yaml（25 槽，crontab 口径 0=周日，两次周日/周一事故在案）；resource_profile_registry.yaml（schedule_truth_source 逐实体挂接）；tasks.yaml（采集任务真源） |
| 门禁与质量尺 | 槽位改动过 `_run_special_schedule` 白名单（新开有名无实槽=静默假绿 R-021）；新槽必查 executor 白名单（S16 daily_crypto 教训）；生成器禁 datetime.now() |
| 当前运行状态 | **绿（宿主活，三心跳新鲜，日志滚动）**；黄红点=STALE 13/假绿 5/FAILED 8/NEVER_RUN 10 腿（§四归属标注） |

## 二、子模块三级枚举（调度面）

1. **OS 层**：ZephyrAlpha_DataScheduler（LogOn+PT5M，Running）+TickSubscriber（PT5M，Running，tick 订阅常驻）+CHHealthProbe（PT5M，Running）——guard 三卫士（锁+15s 心跳+僵尸接管）。
2. **槽位层（25 槽，03 册全景维持）**：L0.5 pre_market→L0 auction_highfreq（10s 五档）→盘中 L1/L2/L2.5 三实时层+L3 event_driven 7×24+L3.5 news_slow（全仓唯一 30 分节拍）→盘后 L4 daily_kline/L5 capital/L6 event→夜间 L7 nightly_financial/consensus_crosscheck→周期 weekend_calibration（周一 03:00 治本后）/monthly_static/weekend_backfill/daily_backfill→自愈 catchup_guard 05:30/data_supply_sentinel 06:50/calendar_coverage_check 07:10/integrity_check 23:00/eod_reconciliation 15:40→特殊 dloop_post 16:45（总闸 daily_loop_master.disabled 不存在=启用）/sector_close_final+sector_pre_open（闸 sector_state_pipeline.disabled 不存在=启用）。
3. **任务层（tasks.yaml 271 task_id）**：采集任务族（kline_daily/basic/valuation/index/margin…）；DAG 依赖=dependencies 字段（§6.3 蓝图）；fallback_sources；trading_day_only；disabled 位（option_daily_stats 1 条）。

## 三、接线四态独立复核

- 总册 built → **维持 built**（宿主/心跳/日志/哨兵四证当日齐）。
- **骨架勘误（今日清单 L-1 分母差的解）**：§2.2 "tasks.yaml 270 vs 骨架 271 差 1"——09-27 实测 `grep -c "task_id:"`=**271**，其中 option_daily_stats 带 `disabled: true`（尾段注释：#ARCH-CH-022 capability 契约校验正确拦截，akshare 无该能力实现，定时管道从未跑通；恢复=provider 补实现后摘除）。**270=271−1 disabled，差 1 非漂移而是禁用腿**；骨架侧若按"在册数"计 271 则自洽，两口径应注明。

## 四、缺口清单（STALE 13/假绿 5 归属标注=本卷主责）

**归属判定：今日清单 §2.2 全部管线腿（STALE 13/假绿 5/FAILED 8/NEVER_RUN 10/NO_TARGET_TABLE 4）均在 tasks.yaml 采集任务族=本环节（F77）带内**；09-27 逐腿 grep 实测在册（realtime_snapshot_incremental/etf_benchmark_refresh/suspend_status_premarket+postclose/derive_weekend/kline_sector_5min/stock_basic_premarket/technical_indicator_full_refresh 等全部命中 task_id）。

| # | 腿族 | 处置（今日清单 §2.2 维持） | 优先 |
|---|------|------|------|
| 1 | **STALE 13 腿**（daily_valuation、index_member_postclose、kline_sector_15min/1min/30min/5min/60min、restricted_shares、share_change、stock_basic_postclose/premarket、technical_indicator_full_refresh、top10_circulating_shareholders）——**归属 F77**；reaper keep 白名单 208 行含相关 6 行命中=防误杀循环逐腿核对义务在本带 | 逐腿核对白名单与产出新鲜度；防误杀/防假活双向 | **P1**（L08 带内归属） |
| 2 | **假绿 FALSE_GREEN 5 腿**（realtime_snapshot_incremental、etf_benchmark_refresh、suspend_status_premarket/postclose/derive_weekend）——SUCCESS 但目标表 0 行——**归属 F77** | C4 假绿灯交叉尺（task_runs 回执×目标表真行数互证+rows_written 记回执+空态分离） | **P1**（L08 带内归属） |
| 3 | FAILED 8 腿（2 腿 str/date 共因→C1 _norm_date 一处覆盖三实例；6 腿待裁修接口/换源/退役） | 共因修复+逐腿裁（pattern_win_rate 不同根勿打包护栏维持） | P1 |
| 4 | NEVER_RUN 10 腿 | 逐腿核"冗余注册 vs 应跑未跑" | P2 |
| 5 | NO_TARGET_TABLE 4 腿（QMT 占位死腿×3+trading_lifecycle_weekly） | 注销 vs 补登记待裁 | P2 |
| 6 | recon_runner 是否被真触发未证（L-3） | eod_reconciliation 槽 15:40 触发链取证 | P2 |
| 7 | 值级假绿（news_sentiment_score 冻结 2025-09-09 Owner 门；restricted_shares 前瞻值 2035 污染新鲜度尺） | Owner 门/施工各归 | P1 |

## 五、自审闸三态

**挖干（调度面复核）**：宿主/心跳/日志/槽位白名单/任务分母五证当日活探；管线腿病状归属逐腿 grep 实测（非转抄）。开口=腿级修复本身归 M3 施工批（本卷只定归属与复验口径）。三态=**维持 built，带内病腿 26 条归属落定**。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
grep -c "task_id:" src/zephyr/data/config/tasks.yaml                        # 271
grep -n "disabled: true" src/zephyr/data/config/tasks.yaml                  # option_daily_stats 腿
cat tmp/scheduler.heartbeat; tail -3 tmp/scheduler_run.log                  # 心跳+滚动
for t in realtime_snapshot_incremental etf_benchmark_refresh suspend_status_premarket kline_sector_5min stock_basic_premarket technical_indicator_full_refresh daily_valuation; do grep -c "task_id: $t" src/zephyr/data/config/tasks.yaml; done   # 全≥1=在册
ls data/runtime/daily_loop_master.disabled data/runtime/sector_state_pipeline.disabled 2>&1   # 双不存在=启用态
```
