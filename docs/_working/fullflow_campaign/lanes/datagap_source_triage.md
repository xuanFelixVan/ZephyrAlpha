---
ttl: task_bound
completes_when: 全流通战役 FF-01 数据缺口簇收口且总包复核签字
---

# datagap 车道 · FF-01 断源群逐条分类（含普查复测更正）

> 车道 `st-ff-datagap-20260918`｜2026-09-18。每条**先复跑实测**再判三件事：
> ①能否换源救 ②只能等新数据（历史结构性不可得）③需 Owner 门位（付费/注册账号/净删）。
> "实测"列全部是本车道当日 `SELECT count()/FINAL` 或直接读配置得到的数字。

## A. 普查结论已失效（别修不存在的东西）

| 断点 | 普查记载 | 2026-09-18 实测 | 处置建议 |
|---|---|---|---|
| BRK-029 `c1_market.sector_fund_flow` | "假通道：表在册、从未有一行" | **1467 行**，sector_type=industry，90 个板块，覆盖 4 个交易日（2026-09-15 17:27:13 → 2026-09-18 15:06:22），哨兵 lag=0 breach=false | 假通道**已于 09-15 建成真通道**（采集器 `scripts/data/collect_sector_fund_flow.py` + 计划任务 ZephyrAlpha_IntradayFundFlow 五时点快照）。台账 status=mitigated 是对的，**普查陈旧**。残余=历史不可回补（THS 仅"即时"口径）→ 建议改判"历史永久不可得 + 未来逐日累积"。**另：该表哨兵行仍带 `allow_empty: true`**（它 09-15 之前正是 0 行状态），白名单曾把它洗成"永久无告警"，与 BRK-046 同型 |
| BRK-034 | 同键双行并存 | 双行 0 组，但计算列 NULL 100% | 见 `lanes/datagap_corrupt_rows.md` §1-2 |
| BRK-035 | 撞码静默污染中 | 库内 0 撞码，fetcher 判别在位 | 改判"源头拦阻已生效"，残余=判别失效无告警（同档 §3） |
| BRK-038 | "哨兵仍设 max_lag_days:2 → **必然天天告警（噪音）**" | 实跑 `zephyr.data.supply_sentinel.check_tables()`：**checked 35 / breached 0 / ok True**，本表 max_date=2026-09-18 lag_days=0 detail=ok | **普查方向相反**。`date_col: ingest_ts` 是按"管线存活"配的（配置文件 L46-49 注释自述理由），所以它**永不告警**。真缺陷=**业务日期 decision_date 停更 323 天完全不可见**（实测 max(decision_date)=2025-10-30，11 央行全停，pboc 更停在 2019-11-20）→ 属"①入口有料 + ⑥失败会响"双失守，不是噪音。换源后按 decision_date 配阈值会**立刻告警且是真阳性** |
| BRK-022 | 零调用写入器挂 monitoring | 普查自证已接 `scripts/data/run_nightly_sentiment.py:41` + schedule.yaml 已有 nightly_sentiment | 台账陈旧，建议关闭该 monitoring 条目（本车道不代改他条，仅登记） |

## B. 可换源救（本车道只调研+登记，接入另派）

| 断点 | 表 | 实测现状 | 可救路径 | Owner 门位 |
|---|---|---|---|---|
| BRK-030 | `c3_fundamental.dividend` | FINAL 116334 行，2026 年 11101 行，**max(announce_date)=2026-07-01**（8/9 月零行=半年报披露季空洞）；任务 `dividend_incremental` schedule=disabled | 参照"A4 股东户数切 akshare"同配方：miniqmt→akshare 分红预案（stock_fhps_detail_em 族），挂 daily_event 槽 + 哨兵档（任务片段与哨兵片段均已出） | 否 |
| BRK-031 | `c3_fundamental.audit_opinion` | **96010 行在库**，max(announce_date)=2026-05-29 | akshare 1.18+ 移除批量接口 → 换源候选=巨潮/交易所公告逐只查询或 tushare 审计意见接口（须先做体积与限流评估）；历史在库无损 | 否 |
| BRK-031 | `c3_fundamental.rights_issue` | **80803 行在库**，max(announce_date)=2026-06-30 | 配股无批量接口 → 逐只公告解析或东财 datacenter 配股通道 | 否 |
| BRK-038 | `c1_market.rate_decision_calendar` | FINAL 3086 行 / 11 央行，max(decision_date)=2025-10-30；管线 ingest 仍日更（2026-09-18 10:04 UTC） | 总包 R-F 前裁=**双源并接**：Fed 官网 FOMC 日历为权威主源 + 东财 datacenter 央行利率为国内备源，两源都做 G 盘原文快照（理由：议息日历权威真源只能是发行方，第三方转述已实证停更 323 天；中国央行无公开日历必须靠东财补国内腿）。本车道已出任务片段 + 哨兵口径片段；**provider 换源施工需另批**（见 §E 验收三样） | 否 |
| BRK-027 | `c1_market.edb_data` | **0 行 / 0 parts**（表在册，engine ReplacingMergeTree）；iFind 已于 2026-08-14 退役 | 台账已判"以 `c1_market.macro_data` 为主宏观源"——实测 macro_data FINAL **50168 行、max(report_date)=2026-09-18（当天）**=替代源活着且新鲜。**建议改判：edb_data 永久 0 行 + 宏观输入已由 macro_data 承接，FF-06 L2C 不存在"无输入"**；edb_data 表清撤属净删门位，只登记不执行 | 清撤需 Owner |

## C. 结构性不可回补（必须写死"历史永久不可得"，否则后人反复试）

| 断点 | 表 | 实测 | 写死结论 |
|---|---|---|---|
| BRK-039 | `c1_market.futures_warehouse_receipt` | FINAL：CZCE 1,980,170 行至 **2026-09-18（当天）**；SHFE 901,911 行至 **2025-11-17** 后无 | **SHFE 维度 2025-11-18 起历史永久不可回补**（官网归档接口自 2025-12 起 404，provider 归档硬界 `_SHFE_ARCHIVE_END=2025-11-30`）。表级哨兵 max(trade_date) 被 CZCE 满足 → **单维度停更被表级新鲜度掩盖**（实跑本表 breach=false、lag_days=0）。新增第 4 类盲区命名：**维度盲区**——哨兵只有表粒度，无 (表, 交易所/维度) 粒度 |
| BRK-041 | `c1_market.auction_snapshot` | FINAL 251598 行 / **47 个密集日**（2026-06-01~2026-09-16；普查记 40 日，已增至 47） | 竞价"过程"数据（9:15-9:25 挂撤单序列）**任何渠道都不存在、历史不可回补**，只能自 2026-09-18 桥流（tick_depth_5）起逐日累积。**最少交易日说明**：按台账 `auction_window_pre_202606_gap` 口径，40 个真值日曾用于标定"1min 首 bar 量=混合口径"；若 FF-06 竞价信号按 `REG-VALM-001` 同线判据（桶内 n≥30 且滑点均值 ≤20bp→valid / ≤40bp→pending / >40bp→noise），则**每个因子桶至少 30 个独立观测**——按"每交易日 1 观测/因子"口径需 **≥30 个交易日**（当前 47 日已达门槛，缺的是 2026-06 前的历史深度，且不可补）；按"标的×日"口径样本充足。结论登记为"历史不可回补 + 未来逐日累积" |
| BRK-040 | `c1_market.alt_sz_reservoir_level` | FINAL 75,159,520 行；**max(tdate)=2026-07-31**（业务日），**max(ingest_ts)=2026-09-18 11:02 UTC** → 业务滞后 **49 天**而采集滞后 **0 天**；近三次灌入：09-18 99,520 行（max tdate 仍 07-31）、09-15 66,660,000 行、09-14 8,400,000 行 | 任务活、源停（疑省水文平台停更/换版）。判定=**半死管线，存量无损，缺的是新数**。09-15 一次灌 6666 万行说明链路在做全史重拉，重拉回来的仍是 ≤07-31 的数 → **源端确实没有 8 月后数据**（解析失败不会落成 99,520 行）。处置：①换源（`data_source_onboarding_sop`）②或按 F4 先例"平台停更留痕"降级留史；③**该表在哨兵配置里根本没有阈值行**（⑤哨兵在岗=0），业务日期判据片段已出。同族 `alt_sz_reservoir_rain_day/month` 与 station 表待一并核查 |
| BRK-037 | `c1_market.kline_sector_intraday` | 2026-09-10 之后 **data_source='tdx' 零行**；09-11/09-15 全部是 `synth_sh`（279,560 行）、09-14 是 `synth_eq`（139,780 行），每时点 580 code | mootdx/tdx 真值通道死亡**仍成立**（真值止于 09-10，且 09-10 为半日残缺 563 code / 37,857 行）。**新增事实：库里有合成行冒充真值外观**——消费方不按 data_source 过滤就会把 synth 当实测真值（方案 J 已如实标记，风险在下游不自知）。`intraday_sector` 档期（5 任务，cron "*/5 9-15 * * 0-4"）空转，停用建议已出任务片段 |
| BRK-042 | `c1_market.alt_movie_boxoffice` | `SELECT count() FROM system.tables WHERE database='c1_market' AND name='alt_movie_boxoffice'` → **0（表不存在）** | 艺恩 ys.endata.cn 改登录制，akshare 1.18.75 与 1.18.94 的 movie_yien.py 均无 token 机制（台账实证）→ **无免费源、表未建**。status=open 的正确改法=转"无源留痕"，**不建表不建任务**；若要做须走第 3 批爬虫试点 + compliance_reviewer 评估。付费层属 Owner 门位 |

## D. 需 Owner 门位（只登记，禁自行执行）

| 断点 | 事项 | 现状 |
|---|---|---|
| BRK-028 | 北向资金日频流 `c1_market.hk_connect_flow`（港交所 2024-08-19 起停止公布） | 需 Owner 注册替代外部源；2014-11-17~2024-08-16 共 4052 行历史完整 |
| BRK-032 | Level-2 逐笔 `c1_market.l2_tick` 需付费行情权限 | 任务已 disabled，降级 get_full_tick 五档快照；TDM L2B 主力行为层精度受损。**禁自行开通** |
| BRK-036 | ETF 分钟族时区劈叉 ~4.12 亿行 | 修复件 `scripts/ch/repair_etf_minute_tz_split.py` 就绪（影子表重建+换名，可逆），`--execute` 需低峰窗 + Owner 批（资金破坏性） |
| N-3（新增） | 议息日历 / 水文 / 分红 三处换源的 provider 接入 | 本车道出片段与需求，接入需排批（provider 面本车道独占，可直接施工，但受轮数预算与"每源三件套齐"约束） |
| N-4（新增） | `daily_valuation` 9 个行情腿列的 schema 裁定（A/B/C 三选一） | 见 `datagap_corrupt_rows.md` §4 |

## E. 新源接入验收三样（本车道未接入新源，故本轮不适用）

本车道交付=**止血**（provider 写前携带 + 宽窗重采续跑）、**点亮**（哨兵业务日期片段）、
**登记**（换源需求与施工输入）。因未新增数据源，
"①有增量任务 ②有哨兵阈值 ③抽检 20 条与源对得上"三样**未触发**；
后续 BRK-038/030/031 换源批必须三样齐（片段已备好可直取），缺一不收工。
