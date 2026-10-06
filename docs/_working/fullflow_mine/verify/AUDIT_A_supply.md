---
ttl: task_bound
title: "断供修复类22项两日后复审"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-04
---

# AUDIT-A：断供止血+修复 22 项两日后复审（2026-10-04）

> 复审口径：CH c1_market/c3_fundamental/c1_backtest 只读实勘（ch_config reader）；交易日锚=kline_daily max=2026-09-30（国庆休市 10-01~10-07，节后首交易日 10-08）——**市日频表 max=09-30 即"节前鲜"，早于 09-30 即仍未修**；7x24 表（新闻/情绪/全球期货）以 10-03 为鲜。工单真源=lanes/L01b、L04、L05b、L06、L07、L08、L10b 各 §工单；旧值=各簿 2026-10-01 读数。git log --since=2026-10-01 共 196 commit 全量扫过，仅 1 项命中本清单。

## 逐项判定表

| 项 | 工单对象 | 旧状态(10-01) | 现状态(10-04 实勘) | 判定 |
|---|---|---|---|---|
| ① | option_greeks/iv_surface 停 09-23 | 停 09-23 伤害现役消费者 | greeks max=09-23、iv_surface max=09-23 均零推进；同通道 option_kline 已鲜至 09-30（通道活、产出步断） | 仍需修（W1 未动，P0 最急不变） |
| ② | news_sentiment_score 断 13 月 | max publish 2025-09-09 | max publish 2025-09-09、7,733,898 行零增 | 仍需修（L04 W1 未动） |
| ③ | nightly_sentiment 双断供 | market 窗缺 09-29/30；symbol 窗止 08-20 | market 窗 194 行 max window_end=**2026-10-03 08:00**（节假日在持续产出）；symbol 窗 19,635 行止 08-21 仍死 | 半修✅（market 腿调度链已自愈复跑；symbol 腿仍需修=W-02 剩半） |
| ④ | typhoon_landfall 断 8 年 | 845 行 max year=2018 | 845 行 max year=2018 零增 | 仍需修（L07 W1 未动） |
| ⑤ | reservoir_level 半死 | 业务停 2026-07-31、75,463,972 行 | max(tdate)=2026-07-31 不变；行数 75,264,932（-19.9 万，疑 ReplacingMergeTree 去重合并，业务面零推进） | 仍需修（核源→降采样+封档方案不变；行数收缩记观察） |
| ⑥ | board_index_tick 断档 | 仅 09-15/24/28/30 四日+09-30 半日截断 | ingest 日直方图仍仅此四日，09-29 仍缺、09-30 仍 09:35 截断；行数微降（疑去重） | 仍需修（L05b W2 供给修复+supply 接线均未动） |
| ⑦ | node_verdict/sim_attribution_daily 停更 | node ingest 09-17；attr max 09-28 | node_verdict 58 行 ingest 09-17 不变、tasks.yaml 零挂钩；sim_attribution_daily max=**09-30**（09-29/30 新行在库，行数 122→88 疑合并压实） | 半修✅（attr 已追平节前最后交易日，未检出专项修复 commit，疑 sim 链自愈，owner 抽查 pipeline_events 写入路径即可销账）；node_verdict 仍需修（W-2 调度实证未做） |
| ⑧ | equity_pledge 双表 | summary 月行数 08=4/09=4；detail 止 07-03 | summary max end_date 09-24、月行数 08=4/09=4 不变；detail 122,922 行 max announce 07-03 不变 | 仍需修（L04 W2 未动） |
| ⑨ | top10_circulating 中报批缺 | max announce 05-15 | 2,138,764 行零增、max 05-15 不变 | 仍需修（L04 W3 未动） |
| ⑩ | port/stat monthly+阈值行 | port 止 2025-07；stat 止 2025-06；sentinel 无阈值行 | port max month 2025-07、stat max report_ym 202506 均不变；data_supply_sentinel.yaml 仍仅 reservoir 有阈值行 | 仍需修（L07 W6 两半均未动） |
| ⑪ | rate_decision_calendar 停 11 月 | max 2025-10-30（任务在管线死） | max(decision_date)=2025-10-30 不变；task rate_decision_calendar_refresh 仍在岗空转 | 仍需修（L08 WO-5 未动） |
| ⑫ | cftc 刷新任务 | max 2026-09-08、tasks.yaml 无任务 | max(report_date)=2026-09-08 不变；tasks.yaml 仍零 cftc 条目 | 仍需修（L08 WO-6 未动） |
| ⑬ | road_freight/futures_position/hog_spot 三探活 | 停 08-21/停 09-23/滞后 2 天 | 三表 max（08-21、09-23、09-28）全不变；futures_position 09-16~19、09-24~30 缺口延续 | 仍需修（L08 WO-11 三查全未动） |
| ⑭ | gold_etf_holdings 停 09-17 无任务 | 停 09-17、零调度 | max 09-17、2,871 行不变；tasks.yaml 仍零条目 | 仍需修 |
| ⑮ | market_etf_share_snapshot 单日 | 仅 09-18 单日 | 仍仅 09-18 单日 1,621 行（etf_share_snapshot_refresh 任务在管线死） | 仍需修（L01b W2 未动） |
| ⑯ | market_signal_history 断供 | 329 行 max 09-04、写侧零挂钩 | 329 行 max 09-04 不变；tasks.yaml 零挂钩，W-01 二选一未裁决 | 仍需修 |
| ⑰ | news_sentiment_window | 同③ | 同③（symbol 窗止 08-21） | 同③（半修；审计归并：与③同表同工单 W-02） |
| ⑱ | emotion_index auction 段 | 17 行止 09-23 无任务 | 17 行止 09-23 不变；schedule.yaml post_auction 槽在（09-23 新增）但 tasks.yaml 零任务引用该槽 | 仍需修（W-06 补任务或退役未裁；补任务现成槽位=post_auction） |
| ⑲ | kline_global HSI/N225/KOSPI | 三标的停 08 月下旬、任务 disabled | HSI 08-28/N225 08-28/KOSPI 08-27 不变，三任务仍 disabled（capability 待 provider 窗口） | 仍需修+方案修正（见下） |
| ⑳ | a50 隔夜修正通道 | enable_a50_channel=False | overnight_boundary_reviser.py:211 仍 False（数据面 a50_futures_daily 2,619 行鲜至 10-02） | 仍需修（L08 WO-7 一行翻转未做，成本最低的一张） |
| ㉑ | weekly/monthly 非复权 停 09-15 | 停 09-15（hfq 版 09-30 活） | kline_weekly max 09-15/kline_monthly 09-15 不变；hfq 版鲜至 09-30；tasks.yaml miniqmt 任务 disabled 留痕自述"100% 由 local_qfq 通道喂数" | 仍需修（根因坐实=local_qfq 通道断+唯一喂口停用；W8 二选一天平略向退役倾斜，hfq 已接管） |
| ㉒ | pdf_forecast/main_business | pdf 止 2021-12-31；main_business 止 2026-03-31 | 两表零推进（pdf max publish 2021-12-31；report_period 2026-03-31） | 仍需修（L04 W6 定性+W9 补期均未裁未动） |
| ㉓ | option_daily_stats | 三零（停 09-22+disabled+零消费） | max 09-22、11,544 行不变，三零维持 | 方案修正（非修复项：维持 L01b §⑥ 退役评审 C 出口，PCR 因子立项时才复活） |

## 伴生发现（非 22 项本体）

- **USDCNH 已接通**：commit `867d821d45`（2026-10-01，author=lane，[GAP-F-23]）sina fx_susdcnh 翻案接入，kline_global.USDCNH 3,102 行 2014-11-07~09-29、任务 global_usdcnh_daily_incremental 已启用——L08 WO-10"usdcnh 全源失效寻源长尾"可销账。
- 22 项之外两日窗口内 196 commits，其余均未触及本清单对象；两处行数微降（board_index_tick -584、reservoir -19.9 万）疑似 ReplacingMergeTree 去重合并，非数据丢失，仅记观察。

## 汇总

- **完整已修：0 项**；**部分恢复：2 项**（③/⑰ market 窗腿、⑦ sim_attribution_daily——均系调度链自愈复跑，未检出专项修复 commit）。
- **仍需修：19 项**（①②④⑤⑥⑦node半⑧⑨⑩⑪⑫⑬⑭⑮⑯⑱⑲⑳㉑㉒；其中 ⑦ node_verdict 与 ⑨⑩⑫⑭⑮ 属"加任务/回补"类低成本项，①②⑥ 为仍流血的 P0 三甲）。
- **方案修正：3 条**——⑲ HSI/N225/KOSPI 放弃等 provider 封装、复制 USDCNH 已验证的 sina 直连契约改任务直采；㉓ option_daily_stats 按退役评审处置不按修复处置；③⑰ 审计归并为同一工单 W-02 双腿（market 已愈、symbol 未愈）。
- 优先序建议不变：P0=①（regime/期权情绪在吃 11 天旧数）>②（13 月断粮）>⑥（做T 兜底位缺位）；低成本速赢批=⑳一行翻转+⑧⑨⑩⑫⑭⑮补任务回补。

## 自审与合规

- 只读纪律：CH 全程 zephyr reader 配方只读（SELECT/system.columns）；零裸写库——过。
- 写域纪律：本两日复审仅新增本文件一册，零既有文件改动、零 git 写、零 commit——过。
- 环境纪律：每条 python 前 PATH 修正 Python312——过。
- 待办移交：本文件 CREATE-GUARD creation_token 留待总筹落地批次登记（L10b 车道同款先例）。
