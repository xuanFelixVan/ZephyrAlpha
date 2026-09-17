---
ttl: task_bound
completes_when: 数据线完成①采集链重启+09-16/09-17 补跑 ②ETF 族 60min 结构缺口经通道 C/D 回补 ③覆盖矩阵复跑缺格清零 ④known_data_gaps.yaml kline_etf_60min_depth_windows 条目回写 resolution_actual
---

# ETF 60min 深度补深工单（数据线移交件）

> 移交方：st-datavein-20260917（数据矿脉评估与补深代理，Owner 令"继续开工"）
> 接收方：数据采集线
> 性质：盘点+定损已完成；执行需数据线的通道/代码权限，本会话按分工边界不抢车道、不硬补。

## 一、结论速览

1. c1_market.kline_etf_60min 深史总体健康（510050 至 2005-02-23，4 bar/日恒定），真实缺口=「1 个全族零行日（2023-06-05）+ 7 月断档窗 07-01~07-17（只剩 31 只考试子集）+ 07-28 半日（545/1,607）+ 159915 孤立散格 2021-02-08 + 09-16 EOD 写入中断半根」，合计约 9.0 万 bar 可回补，其中 ~95% 可由 CH 内 etf_1min 合成救回。
2. 本会话实证：既有通道当前全部不可直达 kline_etf_60min（§三），按诚实条款工单移交，不做裸写硬补。
3. 紧急：今日 09-17 采集链全停——tick_data/tick_depth_5/kline_etf_* 全家 0 行（截至 13:40），而桥沙箱文件在实时产出（E:\qmt_bridge_sim\ticks3.csv 秒级刷新）——消费进程今天没跑。今晚恰是 9/17 收盘后 miniqmt→qmt_bridge 切源窗口，建议一并处置。
4. T3：tick_depth_5 距做T 精确回测可用还差约 17 个全市场交易日（§四）；服务器 ~1 个月保留窗内的近期五档回补机会随时间流逝每日报废。
5. T4：circ_mv 断供已被裁定#288 治本+重采，本会话复验 100% 非空，无残余动作（§五）。

## 二、T1 覆盖矩阵

全表：5,962,194 行｜末日 2026-09-16｜ReplacingMergeTree (symbol, trade_time)｜bar 时刻 10:30/11:30/14:00/15:00（4 根/日恒定）。
基准口径：kline_etf_daily 自身仅 2026-07-01 起（55 日，此前每日仅 1 只），比 60min 浅——"以 daily 为应有日基准"不可行，本矩阵以 trade_calendar(is_open=1) 为基准。

五只重点（S-OWNER-001/002 考试标的）：

| symbol | 首日 | 应有日 | 实有日 | 缺日 | 缺口明细 |
|---|---|---|---|---|---|
| 510300 | 2012-05-28 | 3,479 | 3,465 | 14 | 2023-06-05；07-01~07-17（13 交易日）；09-16 半根 3/4 |
| 510050 | 2005-02-23 | 5,244 | 5,230 | 14 | 同上；09-16 半根 3/4 |
| 159915 | 2011-12-09 | 3,588 | 3,572 | 16 | 上行 + 2021-02-08（孤立）+ 07-28；09-16 半根 2/4 |
| 510500 | 2013-03-15 | 3,284 | 3,269 | 15 | 上行 + 07-28；09-16 半根 2/4 |
| 512100 | 2016-11-04 | 2,399 | 2,385 | 14 | 上行；09-16 半根 3/4 |

全表结构缺口（对照当日家族规模 ~1,660 只）：

| 窗口 | 形态 | 缺格量级 |
|---|---|---|
| 2023-06-05（1 日） | 全族 0 行（全历史唯一零行交易日） | ~758 只×4 ≈ 3.0K bar |
| 2026-07-01~07-17（13 交易日） | 仅 31 只/日（考试子集幸存） | ~13×1,545 只×4 ≈ 80K bar |
| 2026-07-28 | 半日断（545/1,607 只） | ~1,062×4 ≈ 4.2K bar |
| 2026-09-16 | EOD 任务 FAILED，1,663 只仅早市 bar | ~2.7K bar（下午两根） |

旁证（同族受害，同一笔回补可顺带治愈）：07 月窗内 kline_etf_5min 仅 438-447 只/日、15/30min 463-472 只/日；1min 反而全程满覆盖（1,575-1,601 只/日）。

## 三、通道评估（本会话实证，2026-09-17 13:10-13:40）

| 通道 | 状态 | 实证 |
|---|---|---|
| A. miniqmt 增量任务正道（tasks.yaml `kline_etf_60min_incremental`：period=1h + sector 沪深ETF，download_history_data + get_market_data_ex） | 源断 | xtdata 探活失败："无法连接xtquant服务"；XtMiniQmt.exe 进程不在，D:\国金QMT交易端 仅剩 userdata_mini（主程序已清退；模拟版幸存 E:\国金QMT交易端模拟\bin.x64\XtMiniQmt.exe）；userdata_mini/down_queue 自 07-24 未动 |
| B. qmt_bridge kline_60min（9/17 收盘后切源目标通道） | 表错 | qmt_bridge_provider._KLINE_PERIOD_MAP 与 ch_tick_kline.synth_kline_from_1min 的源/目标均硬编码 A 股表（c1_market.kline_1min→kline_60min），ETF 族不在路由内 |
| C. CH 内 etf_1min→etf_60min 合成 | 数据在、通道缺 | kline_etf_1min（3.26 亿行）在缺口窗覆盖充分（07 月窗 1,575-1,601 只/日；2023-06-05 有 759 只 vs 当时家族 758 只）。本会话红线禁裸 SQL 写；既有合成模块不支持 ETF 表——扩展属数据线代码权限 |
| D. 大QMT 沙箱 ContextInfo download_history_data（known_data_gaps.yaml 头注"通道 A"，今日并行会话刚实证补 tick_data 2026-08 缺 7 天） | 可用（沙箱侧） | XtItClient.exe 在跑（PID 21836）；9/18 miniQMT 清退后仍可用（迁移台账 §11.5a 实证）；适合 2021-02-08 散格、09-16 下午段等合成源覆盖不到的格子 |

移交建议（数据线组合执行）：

- **首选=通道 C**（一次代码投入，永久受益）：仿 scripts/data/backfill_lof_minute_history.py / backfill_bse_minute_history.py 先例，把 ch_tick_kline 合成路径参数化（或写 ETF 变体 CLI）：只补缺格（零覆盖白名单过滤）、dry-run 默认、BufferedWriter 正道写入、--execute 后复验缺格清零。预计覆盖 ~95% 缺格。
- **兜底=通道 D**：对合成源不覆盖的格子（2021-02-08、各窗口下午段如有缺失）逐日下载。
- **运维急件（先于一切）**：09-16 半根 = EOD 任务 FAILED（integrator_progress.db：1/5/15/30/60min 五任务 15:36-16:15 全 FAILED，"ClickHouse 写入失败"）；今日 09-17 全链 0 行。重启采集链 + 重跑即愈，恰逢今晚切源窗口。

## 四、T3 tick_depth_5（做T 精确回测地基）

- 现状：18,832,803 行，2026-07-24 ~ 2026-09-16；全市场 3 秒五档快照自 09-11 起步：09-11=8,392 → 09-14=842,243 → 09-15=5,744,250 → 09-16=12,205,202 行（7,973 只）。
- 单标的深史：510300 09-03/04/07/08 四日 20,581 行（09-09 回填，五档完整率/quality_flag=1 均 100%，迁移台账任务一）。
- 立项口径（迁移台账裁定⑤，2026-09-09）：更早的深史五档任何渠道都不存在，自切换日起逐日累积=设计边界，未登记固定行数目标。
- **距可用判断**：做T 精确回测（五档精细撮合）常规 walkforward 需 ≥20 个全市场交易日；现仅 3 日（09-14/15/16）→ **还差 ~17 个交易日（约 3.5 周，前提=采集链每日在跑）**。近期增量回补机会：大QMT 沙箱 ContextInfo 服务器保留约 1 个月，08-18~09-10 约 19 个交易日的五档（19 列含 bid1-5/ask1-5）可尝试经通道 D 回补——每晚一天窗口少一天。

## 五、T4 circ_mv（复验闭环，无移交项）

- 09-14/15/16 实测：5,562/5,562/5,564 行 circ_mv 100% 非空，单源 akshare；裁定#288 修复在码（akshare_provider._yuan_to_wan 元→万元映射 + 写前主键幂等去重）。
- 07-01~09-13 合成行（data_source='synth_shares_close'，99%+ 覆盖）按 known_data_gaps 登记待 weekend_calibration 自然替换，非本单范围。
- daban 09-15 default 负载行已由 st-dabanre 车道裁定#302 同键重放复真。
- 提示：stock_indicator 最新=09-16，今日亦停采（同 §三运维急件）。

## 六、建议执行序（数据线，今晚 9/17 切源窗口）

1. （收盘后）重启采集链；重跑 kline_etf_{1,5,15,30,60}min_incremental 五任务（last_key=20260916、状态 FAILED）补齐 09-16/09-17；确认 tick_subscriber 桥模式恢复落盘。
2. 通道 C 代码件：synth ETF 参数化 + 回补 CLI（先例=LOF/BSE 两 CLI），dry-run 定损→execute→复验。
3. 残余格子（2021-02-08 等）走通道 D 沙箱下载。
4. known_data_gaps.yaml `kline_etf_60min_depth_windows` 条目回写 resolution_actual。

## 凭据

- 探针脚本输出留痕：.runtime/sessions/st-datavein-20260917/staging/probe_etf60min_20260917.txt
- 登记条目：src/zephyr/data/config/known_data_gaps.yaml（本单同 commit）
