---
ttl: task_bound
doc_type: log
title: L02-G 子类目挖矿簿 · 明日情绪盘中滚动预测（TDM-E-L0-04 三零件族）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成（对 D7/L0-04"未接电"判定提出实测改判）
---

**① 一句话**：把 8 态转移先验、相似日匹配、Brier 校准三零件合成"明日情绪/走势概率"，是情绪环节唯一的概率件（SKEL 记"本环节无概率表"，本册改判为"有件、口径待收"）。

**② 实测（行数/成熟度=本册 wc + 头注）**：`plan_engine/next_day_forecaster.py` 428 行 **testing**，头注 CONSUMERS 明写 `pipeline_events 事件挂点 maybe_emit_next_day_forecast`；**本册在 `strategy_pipeline/pipeline_events.py:1078-1082` 实测到该挂点真实存在并被调用**，且 :392-395 写 `JUDGMENT_TABLES["next_day_forecast"]`、docstring 自注"次日概率的唯一自动产出者：daily_kline SUCCESS=自然唤醒（T 日数据齐）"、:334-335 "T 日日线不在库→禁猜日发射（raise）"；配套 `similar_day_evaluator.py` 345 行 testing、`brier_calibration.py` 461 行 testing（CONSUMERS=作战室 W0/W6 + GAP-F-01）、`scenario_probability_model.py` 896 行 testing、`judgment_ledger.py` 594 行 testing（结算件 `pipeline_events:875 maybe_settle_judgment_ledger` 亦在链）、`intraday_tomorrow_forecast.py` 324 行 design。**→ 与 09 号文环节 1/2/9 反复出现的"D7 三消费点未接线 / L0-04 覆盖未接电"叙述不符**：盘后链（daily_kline SUCCESS）已通，缺的是**盘中四时点（10:00/11:00/13:30/14:30）滚动腿**（intraday_tomorrow_forecast 仍 design）。本册不改判据，如实记"叙述与现状脱节"，交总筹与 L09 车道复核。

**③ 六向**：①上游 kline_index 000300 全史（:114-117）+ 情绪/状态轴。②下游 判定台账三表→作战室→Brier 回填。③算法 转移先验+相似日+校准三件；外部=概率预报校准口径与仓内 Brier 一致（17 号文 §一已立法，沿用不重复引）。④后端 盘中腿挂点缺位（见上）。⑤前端 作战室组件（人工面）。⑥字段 signal 轴齐；质量画像=真值窗短（情绪 16 日全成分史）。外部（本轮新增）：状态层"点预测天花板"铁律已在 panel INVARIANT 记 52-53%，与外部"方向预测困难"共识一致 → 单源，标待验证不入图。

**④ 缺口**：D7（在册，本册范围收窄为"盘中滚动腿"）；LK-L01-…；**L02-G-G1 09 号文环节 2"本环节无专属概率表"的结论应更正为"概率表=next_day_forecast 族（盘后已产）+ 盘中未产"**；**L02-G-G2 Brier 回填与 next_day 产出的双向链路无机读校验件**。

**⑤ 三态裁定**：G1=**施工 P0（文档面）**——本册即补，随落地车道入 09 号文勘误；G2=**施工 P2**；D7 盘中腿=挂起排期（解锁=L09 编排器盘中节拍）。

**⑥ 日志**：R1 内部：挂点与产出者实测→signal（改判）；R2 内部：六件族成熟度清单→signal；R3 外部：概率预报校准→沿用/已查无新料。

**封矿判据**：六向封口 + 一项环节级结论改判留证 → **子模块封矿**。
