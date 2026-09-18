---
ttl: task_bound
completes_when: 全流通战役收口报告归档
---

# 供数新鲜度致盲治理 · T1 前提复测 + 治本前后对比（车道 st-ff-sentinel-20260918）

> 数据库全程只读（`check_tables()` / `ch_reader.query`，未发告警、未写 `data/`）。
> R-019 纪律：三条前提逐条自己重跑，不复用车道报的数。

## 1. T1 三条前提复测结论

| 编号 | 车道/普查原述 | 本车道亲验数字 | 结论 |
|---|---|---|---|
| **BRK-038**（议息日历） | "死源但哨兵仍设 max_lag_days: 2 → 必然天天告警（噪音）" | 改前实跑 `check_tables()`：**checked=36 / breached=1**；`rate_decision_calendar` 的 ingest_ts 腿 `max_date=2026-09-18 lag=0 breached=false`；`max(decision_date)=2025-10-30`（滞后 **323** 天）；`bank_code='pboc'` 维度 `max(decision_date)=2019-11-20`（滞后 **2494** 天，218 行） | **不成立，因果方向确实被说反**（一次都没为此告过警）。但**口径要改两处**：①"checked 35 / breached 0" 是 z-datagap 时的数，现值 36/1（z-dag 同批新登记的 `execution_report` 腿已先点了一盏）；②任务书里"pboc 业务日期停在 2019-11-20（滞后 323 天）"把**两个口径混成了一个**：323 天是**表级** max(decision_date)=2025-10-30，2019-11-20 是 **pboc 维度**，其滞后是 2494 天。两口径现各钉一条腿。 |
| **BRK-040**（半死管线） | "调度成功、日志无错、数据不更新；09-15 一次灌 6666 万行仍只到 07-31；这张表没有哨兵阈值行" | `c1_market.alt_sz_reservoir_level`：**max(tdate)=2026-07-31 / max(ingest_ts)=2026-09-18 11:02:11** → 业务滞后 **49** 天、采集滞后 **0** 天；`count() FINAL`=**75,159,520** 行；改前确无阈值行 | **成立**（数字逐项对上）。**但片段对节奏的判断要改**：z-datagap 猜"源为月末快照"并提 `max_lag_days: 40`，实测 202509~202607 **每个自然月 distinct(tdate)=28~31 天**（202602=28）= 日频表。按 40 天档会把本次断供的前 40 天洗成"正常"，属把尺子掰弯，故本车道定 **5 天（日频档）**。 |
| **N-1**（错数进闭环） | "daily_valuation FINAL 259238 行中 close/amount/turnover 非零命中 0 行" | `count() FINAL`=**259238**；`countIf(close<>0)=0`、`countIf(amount<>0)=0`、`countIf(turnover<>0)=0`、`countIf(isNull(close))=0`（列非 Nullable）；近月窗口（>=2026-09-01）87377 行同样三列全 0，同窗 `pe_ttm` 非零 **87111/87377=99.7%**；`data_source=local_valuation`、`max(trade_date)=2026-09-17` | **成立，未被推翻**，且加了一条铁证：同日同标的与 `kline_daily.close` 逐行对照抽 20 条，**20/20 不一致**（daily_valuation.close=0 vs kline_daily.close=6.41/8.08/4.94…）→ 0 不是"无值"而是**错值**，闭环下游拿到的价格是 0。 |

**附加复测发现（原任务书未列，同型致盲）**

| 发现 | 实测 | 处置 |
|---|---|---|
| `execution_report` 阈值行引用了**不存在的列** | z-dag 同批登记 `date_col: trade_date`，但 `system.columns` 实测本表列集=order_id/symbol/…/execution_start/execution_end/ingest_ts/… **无 trade_date**；旧代码把"CH 查询失败(raw='')"和"表真空了"都写成 `empty table`，于是假在岗与真断供共用一条文案，谁也没发现这条腿从来就没生效过 | 改 `date_col: execution_start`（实测 max=2026-09-18 10:26:15Z）；旧代码的混淆已在 `supply_sentinel._scalar` 处拆开：空返回按 `query error` 上报，与 `empty table` 可区分 |
| `config/quality_sentinel_tables.yaml` 里 `kline_5min` 同样引用不存在的 `trade_date` 列 | 实跑本表三项检查（epoch/tz/空段）**全部 degraded**，而 degraded 不进 findings 计数 → CLI exit 0 看起来干净。这张表正是"1970 错位事故"同族 | 改 `date_col: trade_time`（本表只有 `trade_time`）；`check_epoch` 加同列去重，避免 date_col==ts_col 时把亿行表全史扫两遍。改后实跑 degraded 行归零 |
| `rate_decision_calendar.decision_date` 有 **435 行**纪元残留（min=1970-01-01） | 由 quality_sentinel 的 epoch 检测在真配置实跑中首次检出（此前该表不在质量哨兵册内） | 已把该表补进 `config/quality_sentinel_tables.yaml`；污染行清理归 z-drift（本车道禁 DELETE） |

## 2. 治本前后哨兵实跑对比（同一台机、同一库、只读）

| 指标 | 改前 | 改后 | 解读 |
|---|---|---|---|
| `checked` | 36 | **51** | +15 条腿（11 张无哨兵表补册 + 4 条维度/业务/填充率新腿） |
| `breached` | 1 | **8** | 上升是**正确的**：点亮的都是实测存在的断供/错数，无一为凑数 |
| `blind_spots`（仅心跳腿覆盖的表） | 无此概念（不可见） | **0** | 2 张心跳表（rate_decision_calendar / hl_liquidation_raw）各补业务腿后归零；今后再有"只配 ingest_ts"的表会被 WARN 出声而非静默算已覆盖 |
| `ok` | False | False | 8 条红各自真伪见下表 |

### 新点亮 7 条 breach 的逐条真伪判读

| breach | 实测依据 | 判读 |
|---|---|---|
| alt_sz_reservoir_level tdate lag=49>5 | max(tdate)=2026-07-31，采集仍写 | **真断供**（源端停更，任务 enabled 空转） |
| rate_decision_calendar decision_date lag=323>75 | 表级 max=2025-10-30 | **真断供**（金十 dc_*_calendar 族退役） |
| rate_decision_calendar pboc 维度 lag=2494>90 | bank_code='pboc' max=2019-11-20 | **真断供**，且是国内最吃的一条腿 |
| futures_warehouse_receipt SHFE lag=305>10 | CZCE 到 2026-09-18 正常、SHFE 止于 2025-11-17 | **真断供**（表级被掩护，维度腿才看得见） |
| daily_valuation 低填充 {close:0, amount:0, turnover:0} | 87377 行三列非零 0；与 kline_daily 20/20 不一致 | **真错数**（不是阈值不合理） |
| index_valuation_daily 低填充 {cape_5y:0, pe_pct:0, erp:0} | 8125/8125 全 NULL；同表 pe_ttm 有值 | **真缺算**（internal_compute 只挂 fallback，源一成功就永不重算）→ 已并入 `index_valuation_daily_compute_after_ingest` 任务 |
| kline_sector_intraday tdx 腿 lag=8>5 且 rows=0<100000 | 近 5 日 data_source='tdx' 行数 0；09-11 起近端只有 synth_sh/synth_eq | **真冒充**（表级"有行"是合成行填的） |
| c3_fundamental.dividend lag=79>30 | max(announce_date)=2026-07-01；202608/202609 两个整月 0 行（对照 202508=5366 行）；旧任务 `dividend_incremental` 于 2026-09-09 方案D 停用 | **真断供**，根因已归因；已并入 akshare 承接任务 |

**没有一条被"调回宽松"**：唯一被改小的阈值是 alt_sz（片段提的 40 → 实测日频定 5），方向相反。

## 3. 补册表逐张抽检（每表 20 行，只读）

| 表 | max(锚) | FINAL 行数 | 样本 | 主键非空 | 值列非零 | 样本源 | 在册任务（改后） |
|---|---|---|---|---|---|---|---|
| index_valuation_daily | 2026-09-17 | 8,125 | 20 | 20/20 | pe_ttm 20/20 | akshare_csindex | incremental(daily_kline)+backfill+**compute_after_ingest(新)** |
| daily_valuation | 2026-09-17 | 259,238 | 20 | 20/20 | **close 0/20** | local_valuation | incremental+full_refresh |
| northbound_hold_snapshot | 2026-06-30 | 30,574 | 20 | 20/20 | hold_share 20/20 | tushare | refresh(nightly_financial) |
| alt_sz_reservoir_level | 2026-07-31 | 75,159,520 | 20（末 20 个业务日止 07-31） | 20/20 | n/a（列集 id/stcd/tm/tdate/rz） | 同左 | incremental(daily_event) enabled |
| kline_sector_intraday | 2026-09-15 | 9,737,456 | 20 | 20/20 | close 20/20 | **synth_sh**（真值 tdx 已 0 行） | 5 个 intraday_sector 任务 enabled |
| auction_snapshot | 2026-09-16 | 251,598 | 20 | 20/20 | n/a | miniqmt | auction_data_snapshot |
| macro_data | 2026-09-18 | 50,168 | 20 | 20/20 | n/a | akshare/eia 混源 | 7 条在册 |
| edb_data | 1970-01-01（空表） | **0** | 0 | n/a | n/a | — | **NO_TASK**（iFind 2026-08-14 退役）→ 故意不配阈值行 |
| c3_fundamental.dividend | 2026-07-01 | 116,334 | 20（20/20 都是 07-01 当天=断崖） | 20/20 | n/a | bdpan | 旧 disabled + **akshare 承接(新)** |
| c3_fundamental.audit_opinion | 2026-05-29 | 96,010 | 20 | 20/20 | n/a | bdpan | incremental **extra.disabled=true** |
| c3_fundamental.rights_issue | 2026-06-30 | 80,803 | 20 | 20/20 | n/a | akshare | incremental **extra.disabled=true** |
| rate_decision_calendar | 2025-10-30 | 3,086 | 20 | 20/20 | rate_value 20/20 | akshare | refresh(daily_capital) enabled |
| futures_warehouse_receipt | 2026-09-18 | 2,882,081 | 20 | 20/20 | receipts 18/20 | akshare_alt | incremental + 2 backfill disabled |
| sector_fund_flow | 2026-09-18 | 1,467 | 20 | 20/20 | n/a | ths | **tasks.yaml 无条目**（由采集管线直写） |

**诚实条款**：以上"与源对得上"= CH 侧行级自洽（主键非空、值列非零、源标签与在册任务 source 一致、样本业务日不越锚）+ 一处跨表互证（daily_valuation vs kline_daily 同日同标的 20/20 不一致）。**未做真回源 API 比对**（provider 面本车道禁写、且需外部账号/限速），此缺口如实登记，不当已达成。

## 4. 能红证据（按字节还原，6 处变异全部必红）

| 变异 | 打在哪 | 命中的测试 | 结果 |
|---|---|---|---|
| μ1 把 `decision_date` 表级腿改名 | data_supply_sentinel.yaml | test_shipped_config_has_business_leg_for_the_four_measured_blind_spots | rc=1 红，还原一致 |
| μ2 日频水位表阈值 5→40（掰弯尺子） | 同上 | test_shipped_config_daily_tables_are_not_loosened_past_ten_days | rc=1 红 |
| μ3 填充率列换成有值的 pe_ttm/pb_mrq | 同上 | test_shipped_config_covers_every_measured_table... | rc=1 红 |
| μ4 新鲜度腿永不判红（`if False and …`） | supply_sentinel.py | test_stale_business_date_alarms_even_when_ingest_leg_is_fresh | rc=1 红 |
| μ5 盲点识别永返空 | supply_sentinel.py | test_heartbeat_only_coverage_is_reported_as_blind_spot | rc=1 红 |
| μ6 忽略 row_filter（SHFE 回到被掩护） | supply_sentinel.py | test_row_filter_leg_detects_single_exchange_outage | rc=1 红 |

| μ7 把 kline_5min 的 date_col 还原成不存在的 trade_date | quality_sentinel_tables.yaml | TestHostedSweep::test_shipped_quality_tables_have_their_anchor_columns | rc=1 红，还原一致 |

**μ1/μ3 第一轮曾"变异后仍绿"**：因为第一版两条出厂配置断言只查"有没有这条腿"，维度腿能替表级腿过关、填充率列换成有值的列也能过关。**是变异台把测试自身的漏洞照出来的**，随后把断言加强到"恰一条表级腿 + 逐列名列核 + 地板腿必须切真值源"，重跑才 6/6 必红。该过程如实留档（R-026 第 8 型的自我复现：自检结论也要被证伪一次）。

还原后三套件：`test_supply_sentinel.py` 22 passed / `test_quality_sentinel.py` 49 passed / `test_failopen_brk049.py` 11 passed（他车道成品未破）。

## 5. 质量哨兵（quality_sentinel）排班四要素实跑证据

| 要素 | 落点 | 实测证据 |
|---|---|---|
| 自动触发 | L13 `data_supply_sentinel` 槽位（schedule.yaml，06:50 日批 APScheduler） | `scheduler.py:238` 分支已活（既有）；本车道把托管腿接进 `run_supply_sentinel` |
| 自动运行 | `run_hosted_sweep` → `load_specs` → `run_sentinel`（CH 只读经 DatabaseService reader 槽） | 首班实跑：`{"ok": false, "findings_count": 2, "tables_checked": 1, "report_path": ...\2026-09-18_report.json}`，告警 2 条（CRITICAL epoch / ERROR empty_segment） |
| 自动维护 | `sweep_cadence_days: 7` 节奏闸，状态真源=报告文件名（不另立 state） | 次班实跑：`{"ok": true, "skipped": "cadence_7d_last_2026-09-18"}`，零 CH 调用 |
| 自动关闭 | `data/runtime/quality_sentinel.disabled` 标记文件（每次触发实查） | 实跑：`{"ok": true, "skipped": "master_switch_off"}`，`executor.calls == []`（测试内亦钉） |

## 6. 为什么**没有**给 quality_sentinel 建 tasks.yaml 条目（与任务书字面不同，附实测理由）

实测：本仓特殊时段槽位 `integrity_check` / `catchup_guard` / `data_supply_sentinel` / `consensus_crosscheck` / `nightly_sentiment` **没有一个**在 tasks.yaml 有条目（tasks.yaml 266 条里 `schedule:` 取值只有 provider 档期）；且 `scheduler.py:204 _run_special_schedule` 是硬编码白名单、`:2110` 对"无任务时段"只 `log.warning` 后 `return {}`。
→ 若按字面新增 `quality_sentinel:` 槽位而不改 scheduler.py（禁写面），得到的是"调度器每班唤醒、打一行日志、静默返回成功"的 **R-021 型假通道**；若硬塞一条 tasks.yaml 任务，则要绑 source/capability/provider 三件，而哨兵不是数据源。
→ 故选"由 L13 托管"（真跑、真告警、真总闸），并把取舍登记为 `adjudications/req_sentinel_01.md` 待裁。
