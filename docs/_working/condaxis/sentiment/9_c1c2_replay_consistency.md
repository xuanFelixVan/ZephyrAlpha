---
ttl: task_bound
title: C1/C2 一致性对拍——派生重放 vs 在产 builder（examchief_campaign/10_ §5 转达件的执行与结论）
created: '2026-10-14'
session: st-condaxis-20261013
status: consistency_check_done
family_id: CONDAXIS-CAMPAIGN
completes_when: daban 深史重放（Owner 夜间窗）执行后回填观测数并随战役归档
---

# C1/C2 一致性对拍（st-condaxis 情绪线，2026-10-14）

## §1 对拍设计（应 examchief_campaign/10_ §5 处方）

- **两径张力原文**：调研行（00_inputs 情绪档:180）写"候选源=akshare 涨停池族，源侧仅存近约 30 日⇒外部回补"；终报写"daban=kline 派生可全史重放"。两路径不同型，须先钉"派生重放式 vs 在产"的一致性，否则 A 卡重考把史浅修复冒充信号变化。
- **事实澄清（对拍前提）**：`daban_board_event` 的在产推导链＝`daban_board_event_deriver.collect_derived_events`（CH 只读；kline_daily＋涨停价三级链[库内 stk_limit→tushare→规则推导]＋可选 tick/分钟富化）——**本来就不吃 limit_up_pool**；"akshare 30 日窗"约束的是 limit_up_pool（C1/C2 零消费，7_deep_history_assessment.md 翻案在案）。故本对拍＝**同 deriver 的重放幂等性审计**＋"关富化腿纯 kline 面"与"在产面（含富化）"的 C1/C2 子件等值性。
- **Side A（在产）**：c1_market.daban_board_event FINAL，窗 2026-09-01..10-12（24 交易日）。
- **Side B（重放）**：同 `collect_derived_events(start, end, ch_client, intraday=False, seal_ticks=False)` 现场重跑（零生产写；C1/C2 四子件 touched/sealed/max_consec/promotion 均不消费盘中/封单富化面，关腿不损失对拍面）。
- **同式**：C1 三子件日值照 builder `_SQL_LIMITUP_DAILY` 聚合口径；C2 照 `_SQL_PROMOTION` 的日历日 +1 自连接语义**原样复刻**（含跨周末漏计的产线特性——两把尺同病才算同尺）。

## §2 对拍结果（24 个交易日逐格）

| 子件 | 全等日 | 最大差 | 差异日 |
|---|---|---|---|
| touched 触板家数 | 23/24 | 1 家 | 09-24 |
| sealed 封住家数 | 23/24 | 1 家 | 09-24 |
| max_consec 最高连板 | **24/24** | 0 | — |
| seal_rate 封住率 | 23/24 | 0.0032 | 09-24 |
| promotion 晋级率 | 23/24 | 0.0047 | 09-24 |

## §3 差异归因（唯一差异日 2026-09-24，标的 002264）

- kline 09-24：high=close=8.13＝涨停价（stk_limit 09-24 limit_up=8.13，limit_src=ch_stk_limit）——**该票当日真实触板且封住**。
- 在产表：002264 在 09-24 **无行**（末行 09-22 touched=1/sealed=0）；重放：有行（touched=1/sealed=1/consec=1）。
- 根因＝**产线时序竞速漏行**：当日批跑时该 symbol-day 的涨停价/日 K 未落库，deriver 按 fail-closed 纪律跳过（"涨停价缺失跳过不出伪事件"），后续增量以"缺日"为触发不重扫已有日 ⇒ 行缺失固化。**非公式差异**——现时点数据齐备后重放即复现该事件。

## §4 结论（一句话）

**两径同尺**：公式与聚合口径零差异（23/24 全等＋唯一差异可归因为产线数据到达竞速的漏行，重放反而更全更真）；"派生重放"路径可用作深史回补的正式通道。

## §5 对考试线的回执（对应 10_ §3 三数中的第 3 数；前两数待重放）

1/2（覆盖窗与 obs/status）＝待 daban 深史重放执行（**须 Owner 夜间窗**，月块分片，7_deep_history_assessment.md 分支 A 排期项）后回填；3（一致性对拍）＝**本册 §2/§3/§4**：同尺成立，唯一差异 1 票归因产线漏行。

**操作建议（给 A 卡重考的防两把尺条款）**：重考所用的 daban 段应**整体走重放统一面**（含现产 24 日的重放重生成，即"同尺重建"），禁止"现产段＋回补段"直接拼接——否则 002264 类产线漏行会被当成信号变化。重放统一面落表建议带 `batch_tag='replay_unified'` 与现产行物理分区，PIT 与幂等口径沿 deriver 既有纪律。

## §6 留痕

- 运行器与全量对拍表：集成车道 `.runtime/tmp/duipai.py` / `duipai_full.csv`（临时面，收班即清；结果已全部誊入本册）。
- 连接件：docs/_working/examchief_campaign/10_crossline_daban_backfill_to_condaxis.yaml（§5 转达面）。
