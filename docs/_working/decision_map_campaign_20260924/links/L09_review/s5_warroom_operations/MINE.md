---
ttl: task_bound
title: L09-S5 子模块挖矿簿 · warroom 作战室
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L09
status: MINE 完成（六向封口；scenario_plan/outcome 族行数为 governance.db 只读探针实测）
---

# L09 · S5 warroom 作战室

**① 职责一句话**：把"今天盘前我怎么设想市场、盘中走到哪一格、收盘证明我猜没猜中"积累成**可校准的情景样本**，并把三张作战室任务卡（盘中实时走势／明日概率／验证昨日计划）落到判定台账上。

**② 现状实测（2026-09-26）**

### 实码与成熟度
| 件 | module_id | 实码 | 头注 |
|---|---|---|---|
| 日循环管线 | MOD-PLAN-018 | `src/zephyr/plan_engine/daily_warroom_pipeline.py`；`run_daily_warroom_pipeline`（`:359`，`phase` premarket/postmarket/**both**，`:281` 非法 phase fail-closed）；结果 dataclass `DailyWarroomPipelineResult`（`:148-160`，逐段 status） | `[MATURITY] production`；`[CONSUMERS]` 57 号日循环 SOP 环节④ + 盘前管线 + W0/W6 样本积累 |
| 情景记录器 | （依赖件） | `plan_engine/scenario_plan_recorder.py`：`compute_and_record_scenario_plan` / `writeback_scenario_outcome` / `ScenarioRecorderConfig` / `ScenarioOutcomeVerdict` | 被 018 import（`:67-71`） |
| 仪表盘组件 | MOD-L28-WARROOM | `src/zephyr/frontend/dashboard/components/warroom.py`（`:623` 快照→dict、`:634-646` `SQL_LATEST_BY_TARGET_DATE` 取当日最新 run、`:1296` 今日决策面板、`:1320 render_warroom`） | 人机面唯一入口 |

### 触发面实测（三态判定）
| 触发面 | 实测 | 判定 |
|---|---|---|
| 事件链钩子 10 `maybe_run_warroom_pipeline`（`pipeline_events.py:923-957`） | 调 `run_daily_warroom_pipeline(day, phase="both")`；幂等键 `warroom_pipeline:<D>`，记号先落再动手 | **已接电**（SKEL"仓库内零调用方"旧结论已作废，本册实测有调用方） |
| dloop `warroom` 段（`PHASE_STAGES` premarket 与 postmarket 各一次；full 去重后单次） | 在 `dloop_post` 16:45 圈内 | **已接电** |
| 独立 schtasks 任务 | 本册 `schtasks //query` 实测 50 项 Zephyr 族中**无任何 warroom 专责任务** | **无第三通道**（=事实陈述，非缺口：两委托已覆盖） |
| 三任务之"盘中实时走势分析"（addendum 任务 1） | 事件链 60min bar 唤醒（钩子 5/8） | **部分接电**，见下 |

### 三任务产品需求 → 实现映射（本册逐条对表 `2026-09-16-blueprint-addendum-warroom-three-tasks.md`）
| 任务 | 要求 | 实码/实测 | 判定 |
|---|---|---|---|
| 1 盘中实时走势分析（原缺口） | 分钟级五态判定+概率+**证据列**（量比/涨跌家数比/进攻板块拉板数/缺口/隔夜参照）+尾盘预测 → `judgment_intraday_market_state` | 件在=`plan_engine/intraday_l1_tracker`；表实测 **20 行 / 5 个自然日（asof_ts 09-18→09-24）**，结算列 20/20 满回填；**payload JSON 键实测=`{evidence, rest_of_day, state_label, state_probs}`** | **已接电但两处偏差**：(a) 证据是 **payload 内嵌对象，不是独立列** ⇒ 任何按证据维度做的分组/回捞都需 JSON 展开，addendum 的"证据列"字面需求未满足（L09-C08 的准确表述应改为此）；(b) 需求说"分钟级"，实测节拍是 **60min bar 唤醒**（`_AUCTION_WAKE_TASKS` 仅 ETF 1min/5min 用于竞价件，L1 用 60min） |
| 2 明日走势概率 | `judgment_next_day_forecast` 三态概率+分位+隔夜指纹，接 `brier_calibration` 自动回填 | 件在=`next_day_forecaster`；表实测 **仅 4 行，asof_ts 停在 2026-09-20**，`brier_score/log_loss/calibration_bucket` 各 1/4 | **覆盖未接电（产出已停摆 5 个交易日）**——钩子在链上（钩子 9）却连续无产，详见"②·停摆实证" |
| 3 验证昨日计划 | 晨间 `daily_plan`（场景触发条件须可测量）+盘中 `scenario_hits`+EOD `actual_scenario/plan_followed/deviations` | 件在=`daily_plan`/`scenario_classifier`/`close_verifier`；实测 `judgment_daily_plan` **9 行**（eval_score 2/9）、`judgment_plan_verification` **14 行**（`plan_followed`/`deviations` 14/14 满填，`plan_quality_score` 6/14） | **已接电**（三任务里最健康的一支，但质量分缺口 8/14） |

### 样本积累实测（W0 校准的进度真相，`data/databases/governance.db` → `prediction_log`，经 `zephyr.shared.io.sqlite_factory.get_db_connection` 只读）
`prediction_log` 总 **35 行**，按类型：
| prediction_type | 行数 | 日期跨度 | 唯一日 |
|---|---|---|---|
| `plan_revision` | **17** | **全部 2026-08-21** | 1 |
| `sentiment_score` | 7 | 09-21→09-24 | 4 |
| `scenario_plan` | **6** | 09-16、09-21、09-22、09-23、09-24、**09-28** | 6 |
| `outcome` | **4** | 09-21→09-24 | 4 |
| `auction_hit` | **1** | 09-23 | 1 |

⇒ 三条硬事实：
1. **W0 需 20 交易日校准样本，现 6 条 ⇒ 30%**，且 09-17/09-18/09-25 三个交易日无 plan 行（与 S4 册 decision_daily 缺目标日同源）。
2. **plan:outcome = 6:4 ⇒ 2 条预案永无验证行**（09-16 与 09-28 两日的 plan 无对应 outcome；09-28 属未来日尚未到期，09-16 属**已到期未回写**）。
3. **`plan_revision` 17 行全挤在 2026-08-21 单日、此后 5 周零产出**——写入者=`plan_engine.boundary_revision_engine`（盘中档位修订留痕，其 `:50` 注释自约"每次实际改档写 prediction_log，prediction_type='plan_revision'"）。⇒ 这不是"缺件"，是**件曾真实产出过、然后断供**。对 L09-C01 有直接价值：**蓝图 T3（盘中修订）的落地基座已存在且有历史实证**，收拢时不该按"零起点"估工。

### ②·停摆实证（全链级证据，本册为主登记处）
`.runtime/strategy_pipeline/last_audit.json` 实测 35 个记号，按业务日的最后一批：
`regime_snapshot_daily:2026-09-24`、`judgment_ledger_settle:2026-09-24`、`warroom_pipeline:2026-09-24`、`pf_alloc_daily:2026-09-24`（落盘时刻 2026-09-25T00:42–00:43 UTC）。
**无任何 `*:2026-09-25` 记号**；同侧 `kline_index` 实测 `max(trade_date)=2026-09-24`。
⇒ 09-25（周五，交易日）数据未入库 ⇒ 事件链按 fail-closed **正确停摆**（无唤醒词即不跑，这是设计而非缺陷）。
⇒ 但后果被三件事叠加放大：(i) 事件链停摆当日 `next_day_forecast`/`warroom` 零产；(ii) dloop cron 侧 09-25 晨仍产出了一条 `trade_date=2026-09-28`（`asof_data_date=09-24`，ingest 09-25T00:43 UTC）的拍板行 ⇒ **09-25 这个交易日在决策台账上被整日跳过**；(iii) 哨兵 `max(trade_date)=09-28 > ref=09-25` ⇒ `lag=0`、告警文件 `.runtime/logs/decision_chain_alert.jsonl` **实测不存在**（自 09-25 上线以来一次未发）。
⇒ 净结论：**"链通电"与"链每天通电"是两件事；当前没有任何组件负责区分它们。**（S1 册逐跳表的 H1/H8、S4 册哨兵消音条、本册停摆实证，三处同一根因，不各自立项。）

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：`scenario_planner`（MOD-PLAN-005）预测输入件；`market_trade_calendar`（次交易日解析，`:28` 注释）；`kline`/`kline_etf_1min`（`:52` 依赖声明）。外部：已查无 |
| ②下游 | 内部：dloop `warroom` 段 + 事件链钩子 10（两委托）；仪表盘 warroom 组件（人工面）；MOD-PLAN-009 三维归因读 `scenario_plan`×outcome 族（S7 册）。**断点**：outcome 回写只有 4 条 ⇒ 归因侧分母先天不足 |
| ③算法 | 内部：`scenario_plan_recorder` 内容寻址幂等（`payload=ScenarioPlan.to_dict()` 确定性无时间戳，`:38`）；五态判定+概率；`close_verifier` 归 MOD-PLAN-008 的 9 格 outcome 判定。外部：情景化预测+结果回写=forecasting 域标准"预测账本（prediction ledger / forecasting-hub 型）"体裁，**Brier 尺已在 S3 册对表**，本块不重复引 |
| ④后端 | 内部：①**引擎双落点**——判定行在 CH（`c1_market.judgment_*`）、情景样本在 sqlite（`governance.db.prediction_log`）⇒ 跨引擎无法 JOIN，W0"计划↔结果↔判定"三方对齐只能靠应用层拼；②`prediction_log` 为 append-only 保首条不覆写（writer INVARIANTS），与 CH 侧 Mutation 回填是两套幂等哲学；③phase 语义陷阱：`both`=先回写当日再备次交易日，而钩子恒用 `both` ⇒ **事件链里跑的"盘前段"实际在 T-1 傍晚**（与 S2 册 H1 同源）；④次交易日解析失败 fail-**open**（`:13` ERROR_CONTRACT：→None，盘前段 `skipped:no_next_trading_day`）⇒ 日历缺行时静默跳过而不告警 |
| ⑤前端 | 内部：`warroom.py` 面板只读展示今日决策快照；作战室"三任务"卡片的 UI 完成度未在本册实测（面板函数 `:1296/:1320` 在，逐卡覆盖需前端专检）。外部：已查无 |
| ⑥数据字段 | 内部：**"字段在"≠"数据可得"三例**——(1) `evidence` 在 payload 里⇒ 无独立列 ⇒ 不可分组；(2) `plan_quality_score` 列在但 6/14；(3) `prediction_log` 表 35 行里 17 行是同一天的 `plan_revision` ⇒ 单看"表有行数"会严重高估活跃面。另：`prediction_log` 无 `expected_trade_date`，缺勤判定同样只能靠应用层日历 |

**④ 缺口清单**

| 编号 | 内容 | 状态 |
|---|---|---|
| TRD-A05 / L09-C08 | 三任务之盘中实时走势触发面 + addendum 对齐 | 在册，**本册改写其靶心**：不是"缺证据列"而是"证据在 payload 未升列 + 节拍是 60min 而需求写分钟级" |
| L09-S5-G1（新） | **`next_day_forecast` 产出停摆 5 个交易日**（末次 09-20，全史 4 行）而钩子 9 在链上 ⇒ 属"接电而无声失灵"，比"未接电"更难发现 | 新增·P1 |
| L09-S5-G2（新） | **plan↔outcome 配平缺口**：6 plan vs 4 outcome，09-16 已到期无回写 ⇒ `writeback_scenario_outcome` 对该日静默失败或从未触发 | 新增 |
| L09-S5-G3（新） | **跨引擎割据**：判定行 CH、情景样本 sqlite，无共同日期主轴 ⇒ W0 校准闭环无法用一条 SQL 表达 | 新增（与 S4 册时间轴冲突同源，可合并处置） |
| L09-S5-G4（新） | **次交易日 fail-open 静默**：日历缺行 ⇒ `skipped:no_next_trading_day` 不告警；与 `schedule.yaml:219-227` R-021"有名无实假通道"同型 | 新增 |
| L09-S5-G5（新） | `plan_revision` 断供 5 周（17 行全在 08-21）无人追责 ⇒ 说明"表里有历史行"会掩盖"当前零产出"，任何盘点须按 max 日期而非总行数 | 新增（口径级） |
| L09-C01 关联 | `boundary_revision_engine` 已产过真行 ⇒ T3 收拢工时应按"复活+接节拍"估，不按"新建"估 | 供裁定材料（S1 册⑤） |

**⑤ 自审闸三态裁定**

| 项 | 裁定 | 理由 / 解锁条件 |
|---|---|---|
| L09-S5-G1 停摆检测 | **施工（P1）** | 终局全貌下"哪段几天没产"必须机读。处方=与 S1 册 G1、S4 册哨兵缺陷**合并成一个组件**："逐期望交易日 × 逐段"的存在性矩阵（数据源=last_audit 记号 + 各表 max 日期 + 交易日历），一次解决 max() 盲区／哨兵永不发火／停摆无人知三题。**净零内收：不新建哨兵件，改造已落地的 `decision_chain_sentinel` 的尺子**（其头注已自约"只管滞后尺，参照 quality_sentinel 先例"，本册结论=滞后尺的算法要从 max 换成逐日 diff） |
| L09-S5-G2 配平 | 施工（P1，随 G1） | 同一矩阵加一列 plan/outcome 配平差即可 |
| L09-S5-G3 跨引擎 | 挂起排期 | 解锁=L09-C02（第四本账落库时统一日期主轴，届时一并决定 prediction_log 是否镜像入 CH；先动=无谓迁移） |
| L09-S5-G4 fail-open 出声 | 施工（P2） | 一行 WARN 告警；不许静默跳过（宪法精神=失败必须出声） |
| L09-S5-G5 盘点口径 | 施工（P3，本册即交付结论） | 静态清单禁手工维护（§9.5）⇒ 该由矩阵件产出 |
| 战斗室任务 1"证据列升列" | **挂起排期 + 解锁条件** | 解锁=L09-C06 结算聚合件同期做：那时才知道要按哪几个证据维度分组，先升列=可能选错列再改（CH 改列代价高）。不许以"面板现在也能看 payload"当已满足 |
| warroom 本体 | **不封矿** | 样本仅 6 条不构成封矿理由（方法论明令禁以规模小封矿）；且它是全链唯一产生"可证伪判定"的地方，终局全貌=日频 20 日窗滚动 + 校准曲线自动出图 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | 归因 |
|---|---|---|---|
| R1 | 018 头注/phase 语义/结果契约 + `pipeline_events.py:923-957` 钩子 | signal | "零调用方"旧结论作废；`phase="both"` 的时序陷阱现形 |
| R2 | `governance.db.prediction_log` 按类型×日密度（经仓内 `get_db_connection` SSoT，非裸连） | signal | **主力发现**：6/4/1/17 的分布 + plan_revision 断供 |
| R3 | `judgment_intraday_market_state.payload` JSON 键展开 | signal | 证据列存在但在 payload ⇒ L09-C08 靶心改写 |
| R4 | `last_audit.json` 35 记号逐键读 + `kline_index max` 对拍 | signal | 09-25 全链停摆实证（并证明其为 fail-closed 正确行为） |
| R5 | addendum 三任务原文逐条对表实码 | signal | 任务 1 部分已建（原记"本体未建"偏保守）、任务 2 停摆、任务 3 最健康 |
| R6 | schtasks warroom 专责任务 | noise（不存在） | 归因=**方向本就无矿**（两委托已覆盖），登记为"实测无"防后续车道重复找 |
| R7 | 外部对表 | 未做 | 延至统一轮；候选=forecasting ledger / prediction-and-outcome 样本积累体裁。登记为"本册未做外部对表" |

**本册封矿判据**：六向封口；三任务各给"实码/行数/触发面/偏差"四件套；全链停摆实证在本册落地（供 S1/S4/S6 册交叉引用）。⇒ **子模块封矿**。
