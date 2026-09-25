---
ttl: task_bound
title: L01-S9 子模块挖矿簿 · alt_regime_signal 另类传导通道
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成（含一项对 SKEL 的改判）
---

# L01 · S9 alt_regime_signal 另类传导

**① 职责一句话**：把仓内另类数据（BDI/BTC/恐贪/连板情绪/台风）折算成日频状态信号表，为状态层提供"盘面之外"的传导腿。

**② 现状实测**

| 项 | 实测 |
|---|---|
| 生产件 | `src/zephyr/alt_data/alt_regime_signals.py` 541+ 行（MOD-L00-004，production）；五信号位 F4_BDI_MOMENTUM_Z20 / F14_BTC_MOMENTUM_30D / F15_FNG_INDEX / F23_LIMITUP_EMOTION / F7_TYPHOON_EVENT |
| 任务 | `tasks.yaml:2783 alt_regime_signal_refresh`（scheduler.py 源路由 AltRegimeSignalProvider） |
| 表 | `c1_market.alt_regime_signal`（signal_date/signal_id/signal_value/state/detail/source） |
| 消费面 | ①`regime_data_loader.load_alt_regime_signals`（:261）**全仓零调用者**（本册 grep 复核：唯一命中=定义处）②**改判**：`src/zephyr/backtest/regime_validation/condition_package.py:8,51,53` 已把该表作 GPU 条件包"状态轴真身"直读（`_STATE_FAMILY="F4_BDI_MOMENTUM_Z20"`）——SKEL 记"产槽在产、消费端零调用"，实测**消费端已有一条（回测侧）真读**，缺的是 regime 生产链侧（loader 腿） |
| 触及文件 | alt_regime_signals.py / alt_source_bootstrap.py / condition_package.py / scheduler.py / regime_data_loader.py / scripts/ch/apply_market_tables_ddl.py（本册 grep 全清单） |
| INVARIANT | F23 阈值 v1=provisional，毕业前禁进决策硬链（头注 :44-48）；F7 定位=风险日历非收益因子（P0 事件研究 217 场） |

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：alt_shipping_index/crypto_kline_daily/sentiment_panel/limit_up_down×stk_limit/landfall_history。外部：已查无（BDI→A 股传导的外部一线件本轮未做定向检索，**列长尾**，查法登记：以"shipping index freight rate equity returns China"定向搜） |
| ②下游 | 内部：GPU 条件包（实证）+ regime 面板（未接）。外部：已查无（同上） |
| ③算法 | 内部：z-score/动量/事件标记三种折法。外部：已查无 |
| ④后端 | 内部：loader 腿零调用=L01-C06 施工项仍在。外部：已查无 |
| ⑤前端 | 内部：无呈现面（信号表可经面板扩列）。外部：已查无 |
| ⑥数据字段 | 内部：五信号位字段齐；质量画像=F15 依赖 sentiment_panel（币圈面板，known_issues 自注），F23 依赖 daban（**本册实测 daban_board_event 仅 16 个唯一日、max 2026-09-22**）→ 短史硬约束 |

**④ 缺口清单**：L01-C06（在册，loader 接线）；LK-L01-…（无新增）；**L01-S9-G1** 五信号位与七态概率的融合算法未定义（现在只做条件包轴、不做概率融合）；**L01-S9-G2** F23 provisional 无毕业考试排期。

**⑤ 三态裁定**：L01-C06=施工（P1，在册）；G1=挂起排期（解锁=F4 在 GPU 成绩单一轮的增量证据，先证增量再谈融合，净零）；G2=挂起排期（解锁=下一预注册窗口，禁无卡转正）。

**⑥ 挖矿日志**：R1 内部消费面 grep→signal（改判：回测侧已有真读）；R2 内部 daban 短史探针→signal；R3 外部 BDI 传导→noise，归因=**未做定向检索即下结论的成本更高，故本轮如实记"已查无+列长尾"**，不虚构引文。

**封矿判据**：六向封口（含 4 处如实已查无+1 条登记长尾）→ **子模块封矿**。
