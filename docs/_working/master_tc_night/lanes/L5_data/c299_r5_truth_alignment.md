---
ttl: task_bound
completes_when: 总包夜战战役(master_tc_night)归档收尾
---

# C299 — R5 三处真源收敛对齐方案（st-mastertc-l5，2026-10-07）

> 范围：reconciliation_differences / consensus / score 三处双源对账的真源收敛（R5 尺）
> 已知分歧（卡面挂号）：consensus 侧 dow=2-6 vs schedule 1-5。
> 本档=对齐方案+裁定理由；**生产配置本夜零改动**（改配置属调度域，§4 登记移交）。

## 1. 三处现状（dual_source_guard 统一判据面）

三处共用 `src/zephyr/data/dual_source_guard.py` 判据收敛件（在册病根 W-36/X-40：两库皆空被读成"干净"）：

| 处 | 双源面 | 病灶 | 现状 |
|---|---|---|---|
| reconciliation_differences | DuckDB governance.db ↔ c1_market.reconciliation_differences | 两库皆空=零落地面，eod_reconciliation 槽（cron `40 15 * * 0-4`）产出无处写 | known_data_gaps `reconciliation_differences_dual_empty_disease` 在册（open） |
| consensus | consensus 双源对账（consensus_crosscheck 槽 cron `30 0 * * 1-5`） | **消费侧日历窗 dow=2-6 与排班面 1-5 不一致**——跑班日历与读数窗错位 | 本档收敛对象 |
| score 族 | score 双源（news_sentiment_score 等） | 同律：写班/读窗日历各异 | nightly_news_score 槽已接线（EXEC-2b 治本），读窗待同口径复核 |

分歧根因：排班（schedule.yaml cron dow）与数据消费窗（表内按 dow 过滤/取数）各自为政，且 cron dow 语义（0=周日 vs 0=周一）在两代槽位间不一致（daily_kline/eod_reconciliation 用 `0-4`，consensus_crosscheck 用 `1-5`——两种写法至少一种在当前调度器语义下错位）。

## 2. 真源裁定（本车道裁定理由，落 workbook）

**真源=trades 日历（trade_calendar）为主，schedule.yaml 为班面唯一表达。** 理由：

1. 一切三处对账的对象是**交易日事实**（收盘后对账/打分/共识重建），自然真源=交易日历；
   cron dow 只是"何时跑"的班面投影，用它反推"哪些日该有数"是把投影当本体（SSOT 倒挂）。
2. 宪法 RULE-SSOT：机械判定禁止凭记忆——dow 数字推日历正是"凭记忆"，trade_calendar 是库内可查真源。
3. scheduler.py:196 已有 `now.weekday() >= 5` 跳周末语义（Python weekday Mon=0）——班面与日历桥
   已在场，收敛方向是**让消费窗走同一桥**，而不是三处各写一套 dow 补丁。

## 3. 对齐方案（分三步，另批执行）

1. **判据统一**：三处消费/对账窗改走 `trade_calendar.is_trading_day(date)`（或既有日历 helper），
   禁裸 dow 过滤；dual_source_guard 宿主侧（recon_runner/consensus_crosscheck/score 宿主）取数窗
   由"dow∈窗口"改"日历交易日 ∧ 槽位已跑"双条件。
2. **班面校准**：schedule.yaml 三槽 cron dow 语义统一（0-4 与 1-5 二选一，按调度器实测语义），
   附注释钉死 0=周日 or 0=周一（cron 标准语义=0/7=周日）；**调度域移交项**（本夜不动）。
3. **验收尺**：三处 both_empty/one_sided 状态在"交易日∧槽位已跑"条件下连续 5 个交易日无假绿
   （dual_source_guard SOURCE_PAIR_RED 语义复用），即视为收敛完成。

## 4. 移交登记（本夜不动生产配置）

- schedule.yaml cron 语义统一 → 调度域（scheduler.py/_run_special_schedule 白名单面同 owner）。
- consensus 消费窗 dow=2-6 具体代码位置 → 随第 1 步施工批落位（grep 面已在档：src/zephyr/data/consensus_crosscheck.py 消费侧）。
- 本档真源裁定理由已同步进 L5 workbook §C299；known_data_gaps 的 reconciliation_differences 挂账行已更新（对齐方案入口+last_updated=2026-10-07）。
