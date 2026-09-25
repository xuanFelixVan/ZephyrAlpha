---
ttl: task_bound
creation_token: m5-sched-cron-automations-20260925
---

# M5 分册 03：仓内 cron 槽位与 ZCode 侧自动化

## 一、排班真源
- **`src/zephyr/data/config/schedule.yaml`**（267 行，25 槽）= 槽位排班唯一真源；宿主=DataScheduler 单进程（无槽位级 pid）。
- cron 口径：标准 crontab（0=周日，croniter）；APScheduler dow(0=周一) 由生成器归一——**两次周日/周一差一天事故**（weekend_calibration 09-20 未 firing 根因）都出在这，改槽必须过对账。
- 槽位与 resource_profile_registry.yaml 的 `schedule_truth_source` 字段交叉挂接（生成器产出，禁手改计数）。

## 二、25 槽全景（ cron / executor / 一句话 ）
| 层 | 槽 | cron | executor | 说明 |
|---|---|---|---|---|
| L0.5 | pre_market | 34 8 * * 0-4 | default | 盘前元数据（JOB-077） |
| L0 | **auction_highfreq** | 6段 */10 15-25 9 * * 0-4 | realtime | 竞价 9:15-9:25 每 10s 五档（max_instances=1+coalesce，10s 由 3s collapse 事故改） |
| — | post_auction | 30 9 * * 0-4 | default | 09:25 竞价收官聚合 |
| L1 | intraday_realtime | */5 9-15 * * 0-4 | realtime | Tick/L2/Greeks/港股K线 |
| L2 | intraday_minute | */5 9-15 * * 0-4 | intraday_minute | A股/ETF/LOF 分钟K |
| L2.5 | intraday_sector | */5 9-15 * * 0-4 | intraday_sector | 880xxx mootdx TCP 直连 |
| L3 | event_driven | ***/3 * * * * | default | 快新闻/EDB 7×24 |
| L3.5 | **news_slow** | **17,47 * * * *** | default | 个股新闻/研报——**全仓唯一 30 分钟节拍**（"每 30 分监控件"=此槽，max_instances=1 实际 90-180min/轮） |
| — | daily_crypto | 41 8 * * * | default | 币圈 UTC 日线（原 light executor 不存在=每日 lookup failed 移除 job，**从未自动跑成**的治本案例） |
| L4 | daily_kline | 30 16 * * 0-4 | heavy | 日/周/月K+复权+估值 |
| L5 | daily_capital | 00 18 * * 0-4 | default | 资金面/龙虎榜 |
| L6 | daily_event | 00 19 * * 0-4 | default | 预期/财报/分红 |
| L6.5 | research_nightly | 30 20 * * 0-4 | default(max1) | 研报明细增量 |
| L6.9 | consensus_crosscheck | 30 23 * * 0-4 | default(max1) | 一致预期双向验证 |
| L7 | nightly_financial | 00 22 * * 0-4 | heavy | 财报/两融/股东 |
| L8 | weekend_calibration | 00 3 * * **1** | heavy | 周一 03:00（周日→周一差一天治本 09-23） |
| L9 | monthly_static | 16 9 1 * * | default | 月初静态 |
| L10 | weekend_backfill | 00 2 * * 0 | heavy | 周缺补下（APScheduler 0=周一） |
| L10.5 | daily_backfill | 00 17 * * 0-4 | heavy | 当日缺口当天补 |
| L10.7 | catchup_guard | 30 5 * * * | default | 档期对账补跑（含周末） |
| L11 | integrity_check | 00 23 * * 0-4 | default | 完整性巡检只告警 |
| L12 | daily_alt_fx | 35 23 * * 0-4 | default(max1) | ECB 汇率 |
| L13 | **data_supply_sentinel** | 50 6 * * * | default | 断供哨兵+托管 quality_sentinel（停摆闸 data/runtime/quality_sentinel.disabled） |
| L13.5a | calendar_coverage_check | 10 7 * * * | default | 交易日历逐日 diff |
| L13.5b | eod_reconciliation | 40 15 * * 0-4 | default(max1) | 日终三账核对（recon_runner） |
| L14 | **dloop_post** | 45 16 * * 0-4 | default(max1) | 日循环总扳手自动圈（闸 daily_loop_master.disabled；零下单 #305 安全态） |
| secbuild | **sector_close_final** | 10 15 * * 0-4 | default(max1) | 板块状态盘后定格（闸 sector_state_pipeline.disabled） |
| secbuild | **sector_pre_open** | 15 9 * * 0-4 | default(max1) | T 日定格复制+偏好重映射 |

## 三、交易日全天时序（把 25 槽+OS 任务拼成一天）
```
05:30 catchup_guard → 06:50 data_supply_sentinel → 07:10 calendar_coverage_check
08:20 nightly_sentiment → 08:30 daily_crypto → 08:34 pre_market
09:01 PatternMining(任务) → 09:05 ConfigCheck → 09:15 sector_pre_open
09:20 BoardIndexRealtime(任务复活件) → 09:25 auction 收官+PaperSession(任务)
09:35 SimBridgeExecute(任务) → 盘中 */3 新闻 + */5 三实时层 + 30 分 news_slow
12:55 QMTWatchdog(任务) → 13:05 SimBridgeExecute(任务)
15:05 IntradayFundFlow(任务,5 时点末班) → 15:10 IndexMinuteEOD(任务)+sector_close_final
15:30 PostSettlement(任务) → 15:40 eod_reconciliation → 16:30 daily_kline
16:40 SectorSnapshot(任务) → 16:45 dloop_post → 17:00 daily_backfill
18:00 daily_capital → 18:05 TTLRejudgeDaily(任务) → 19:00 daily_event
20:30 research_nightly → 22:00 nightly_financial → 23:00 integrity_check
23:30 consensus_crosscheck → 23:35 daily_alt_fx
凌晨带：02:30 tilib 夜回填(任务,exit1 带病) → 03:30 GateFullTreeAudit+LibraryLedgerBackup → 05:40/05:50/06:00/06:31 资源/备份四连
```

## 四、ZCode 侧 automations
- **结论：零可见登记**。`C:/Users/fanzi/.zcode/v2/setting.json`、`config.json` 均为 UI/provider 偏好，无 automation/cron 类条目；项目内无 `.zcode/` automations 目录；动态工作流存档（ListSavedWorkflows）与本命题无关。
- 即：**"ZCode 侧每 30 分监控件"不存在**——全仓唯一 30 分钟节拍是 DataScheduler 的 news_slow 槽（数据层非监控）；监控责任全部由 OS 计划任务（DeadmanSwitch PT5M、ResourceRegenCheck PT1H、BeltDaemon PT1M、reaper PT10M）+ 仓内哨兵槽（06:50/07:10/23:00）承担。
- 近旁体制：`docs/_working/cmd_ledger/automation_master_plan.md` 59h 窗"每 4h 心跳记账"是战役节奏不是常驻监控。

## 五、六向台账速记
- 上游：schedule.yaml+tasks.yaml（槽）｜register_*.ps1（OS 任务）｜Owner 指令（automation_master_plan）。
- 下游：CH/PG 数据表、堵点本、Alerter 告警、前端晋升页。
- 自动化触发：见本册全表。
- 真源：schedule.yaml（槽）/resource_profile_registry.yaml（资源画像）/ROOR（注册表发现）。
- 门禁：槽位改动过 scheduler.py `_run_special_schedule` 白名单（新开有名无实槽=静默假绿 R-021）；生成器禁 datetime.now()。
- 现状：**绿**（DataScheduler pid 47472 活、三心跳新鲜；yellow 点位见 04 册）。

## 六、复核命令
```
cat src/zephyr/data/config/schedule.yaml | grep -c "^  [a-z_]*:"      # 槽位数
tail -20 tmp/scheduler_run.log
python -c "import yaml,sys; d=yaml.safe_load(open('src/zephyr/data/config/schedule.yaml',encoding='utf-8')); print(list(d['schedules']))"
```
