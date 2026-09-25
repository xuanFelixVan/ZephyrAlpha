---
ttl: task_bound
title: ADJ 案卷·L09-C01 编排器收拢（蓝图版 vs 双轨转正）代码级现状
---

# ADJ · L09-C01 编排器收拢

## ① 一句话问的是什么

日循环有两个触发面（事件链 + 16:45 cron 总扳手）共用同一个编排器——问的是：**宣布哪一条是编排器本体，另一条降格为壳或删除，以免长出第三套平行实现**。

## ② 现状实测（本项为"全链路是否通电"枢纽，给到代码行号）

### 2.1 关键发现：题面是伪二选一——"蓝图版"已经建成并被两条轨共同调用

- 蓝图真源：`docs/_working/trading_vision/2026-09-16-daily-orchestrator-blueprint.md`（盘上 30,560B，与 HEAD 同字节，实测 `git cat-file -s HEAD:…`=30560）。§二定义 S1-S7，§七定义"刀0 蓝图→刀1 一库→刀2 一闸→刀3 一器→刀4 一图"，§八列 8 条待 Owner 批准点，§九.7 自裁"首版 T3/T4 只留接口签名"。
- 实现体：`src/zephyr/strategy_pipeline/daily_decision_orchestrator.py`（894 行，实测 `wc -l`）。**S1-S7 逐段在码**：`:213` S1 日历、`:344` S4 包选择、`:409` S5 仓位上限合成、`:431` S6 写侧、`:472` S7 分发，模块 docstring `:43-:50` 逐条对位蓝图 §二。→ **刀3（一器）已完**。
- 刀1（一库）：`schemas/categories/decision_daily.py` 存在且被消费（`daily_decision_orchestrator.py:818-821` 导入 `INSERT_COLUMNS/SQL_LATEST_BY_TARGET_DATE/TABLE_NAME`，实测）。
- 刀2（一闸）：实测线上行 `gate_snapshot_json` 内含 `l1/l2/l3` 分层快照（l2 当前 `"status":"absent","error":"no_persisted_gate_state_v1"`）。→ 刀2 已完，L2 门态持久化是其自身欠账（另案）。
- 刀4（一图）：`src/zephyr/frontend/dashboard/components/warroom.py:216/623/634-646` 明写"BT-P1-031 刀 4：c1_backtest.decision_daily 当日最新 run 行"，SQL 走 `SQL_LATEST_BY_TARGET_DATE` 真源。→ **刀4 也已完**。
- §九.7 自裁已被后续实现推翻：T4 `postmarket_reconcile` 在 `daily_decision_orchestrator.py:806-807` **已实体化**（docstring 自述"TRD-A17 最小实体化，L09-C02"），**不再是签名占位**。→ L09 SKEL 记的"把 `daily_decision_orchestrator.py:764-767` 签名占位做成实装"这一条，**行号与状态双双过时**（实测 764-767 是 S7 播报 return 块，不是占位）。

### 2.2 "双轨"到底是什么（实测两触发面）

| 轨 | 载体 | 触发 | 实测证据 |
|---|---|---|---|
| 轨 A 事件链 | `src/zephyr/strategy_pipeline/pipeline_events.py:1026 wire_data_scheduler()` | `daily_kline` 等数据任务 SUCCESS 订阅回调（宪法 §9.3 事件触发，禁 cron） | 实测唤醒的 `maybe_*` 产出者 **13 个**（含 `maybe_run_daily_decision`，调用点 `pipeline_events.py:1090` 附近），SKEL 所称"9 棒"计数过时 |
| 轨 B 总扳手 | `src/zephyr/plan_engine/daily_loop_master_switch.py:337 PHASE_STAGES` | `config`→`src/zephyr/data/config/schedule.yaml:249 dloop_post: cron "45 16 * * 0-4"`；特殊槽处理在 `src/zephyr/data/scheduler.py:366-433` | 实测 `PHASE_STAGES`：premarket 5 / intraday 4 / postmarket 8 / **full 16**，全链去重后 **16 段**（SKEL"16 段"与实测一致） |

- 轨 B **不另建编排器**：`daily_loop_master_switch.py:4 [DEPENDENCIES]` 明文含 `zephyr.strategy_pipeline.daily_decision_orchestrator(run_daily_decision)`，postmarket 段列表含 `"decision"`（实测）。→ **两轨共用同一个 S1-S7 实现**，不存在"第三套"。
- 总闸状态实测：`data/runtime/daily_loop_master.disabled` **不存在** → 16:45 自动圈处于启用态（`scheduler.py:367-370` 每次触发实查该文件）。

### 2.3 双触发面会不会重拍：幂等机制与在产证据

- 幂等位点：`daily_decision_orchestrator.py:182-211` `_marker_path/_marker_seen/_touch_marker`，业务日级 key `daily_decision:<data_date>`，写入用 `safe_write_text`（CAS）；语义=先拍板先占，失败不回滚（防唤醒点重拍风暴）。逃生=`force_decision`（`daily_loop_master_switch.py:42` 用法示例）。
- 盘上实据：`.runtime/strategy_pipeline/daily_decision_marker.json`（mtime 2026-09-25 08:43）实测仅 5 个 key：`2026-09-18/21/22/23/24`。
- 库侧实据（只读经 `zephyr.data.ch_reader`，并按纪律换 reader 复核）：`c1_backtest.decision_daily` **72 行**，按 `trade_date` 分组实测最近为 2026-09-28(1)/09-24(1)/09-23(1)/09-22(1)/09-21(2)/09-16(66)；最新行 `ingest_ts=2026-09-25 00:43:10Z`、`run_id=decision-2026-09-24-685521`、`asof_data_date=2026-09-24`。→ **标记与库行逐日对应，双触发面未产生重拍行**。
- 失败面实据：`data/failures/` 全目录内 dloop_post 相关记录**仅 1 条**——`20260924_dloop_post_084500.json`（实测原文）：`cannot import name 'SQL_LATEST_ANCHORED_STATE' from 'schemas.categories.backtest.backtest_regime_state_anchored'`。该缺陷已随 L01-C01 以"本地定义"修法闭环（`src/zephyr/pf_alloc/allocation_inputs.py:622-633` 注释自述+实测 `from zephyr.pf_alloc.allocation_inputs import SQL_LATEST_ANCHORED_STATE` IMPORT OK）。
- 调度器活着：`.runtime/strategy_pipeline/last_receipt.json` mtime 2026-09-25 21:42（实测）。

### 2.4 "通电"的真正断点不在编排器（实测）

最新 20 行 `decision_daily` 的 `package_set_json` 实测：**20/20 全部 `enabled_packages: []` 且 `incomplete: true`**，`mounted` 恒 `['STR-MOMTREND-033']`，`source_confidence` 为 `proposed`。根因不在编排而在两处上游：
1. `daily_decision_orchestrator.py:121` `GRADUATED_PACKAGES: Final[frozenset[str]] = frozenset()`（实测）→ `:400` `enabled = sorted(set(mounted) & set(GRADUATED_PACKAGES))` 恒空。这是裁定#305 第 2 点的**有意安全态**，注释自述（`:385`）。
2. `state_matrix` 的 `TDM-E-L1|<state>` 格 `confidence=proposed`、部分格缺 → `incomplete` 的另一半由 L06-C01 上岗规则 v1（Owner 追认+填格）决定。

→ **编排器在跑、在写、在播报，但拍出来是"空包=不下单"**。收拢令无论选哪条，都不解锁这一段；解锁它的是 L06-C01，不是 L09-C01。

### 2.5 计数漂移登记（实测 vs 文档）

| 文档口径 | 文档出处 | 实测 |
|---|---|---|
| 事件链"9 棒" | L09 SKEL §施工表 | 13 个 `maybe_*` 唤醒产出者 |
| `postmarket_reconcile` 为"764-767 签名占位" | L09 SKEL L09-C02 | 已实体化于 `:806`；764-767 是 S7 播报块 |
| "T3/T4 首版只留签名" | 蓝图 §九.7 | T4 已实装（T3 盘中修订未见实装，实测未grep到 `intraday_revise`） |
| 蓝图版=待施工的"完全体" | 19 号文 C 栏/D9 行 | 刀1/刀2/刀3/刀4 均已在码/在库/在面板 |

（"16 段"与"29 槽"两项本次未复测，标注引自 SKEL/schedule 注释。）

## ③ 可选路径

**路径 A：双轨转正——宣布事件链为唯一本体，16:45 dloop_post 降为"补漏看门狗"**
- 工作项：①`dloop_post` 段表裁剪为"仅事件链未覆盖的段"（避免 16 段与 13 产出者的重叠维护）；②在两处模块头互写"唯一本体=事件链，本槽=补偿"声明（现 `daily_loop_master_switch.py:8` 已声明幂等委托，缺"本体归属"）；③MOD-PLAN-021 复用/退役随批（L09-C09）。
- 代价：低（零新代码，删/降段数即可）；不可逆点：段表一旦裁剪，被删段的"每日兜底重算"能力消失（事件漏醒=当日永久缺行）。

**路径 B：蓝图版完全体施工——把 16:45 升为唯一节拍，事件链产出者逐个退役入器**
- 工作项：①13 个 `maybe_*` 逐个迁入编排器段表并保留各自幂等键；②补 T3 盘中修订段；③蓝图 §八 8 批准点逐条裁完（含"首版接入包集合""仓位参数 proposed→confirmed"）；④宪法 §9.3"编排器须事件触发"与 cron 圈的合规性需一条新裁定明确豁免（现豁免只覆盖 dloop_post 单槽）。
- 代价：M-L 工程量，且**与宪法 §9.3 有正面摩擦**（cron 作主编排触发面）。
- 不可逆点：`maybe_*` 钩子一旦摘除，除 dloop 之外的下游（判定台账/结算/分配链）失去唤醒点，回退需重建订阅链。

**路径 C（本卷实测支持的最小选项）：不做二选一，只下"防第三套"收拢令 + 补双轨对账声明**
- 工作项：①裁定写明"编排器本体唯一 = `daily_decision_orchestrator` S1-S7，两轨皆触发面，禁新建第三实现"；②把 2.3 的幂等冲实写成可机判的守卫（同日两触发面至多一行 `run_id` 或"新 run_id 追加"，按现有 marker 语义即可断言）；③`dloop_post` 与事件链的段重叠列一张表（实测 16 vs 13，交集需点名）；④L09-C02 改判为"已交付待验收"、L09 SKEL 行号更正。
- 代价：不解决"谁该是主时钟"的运维心智问题；不可逆点：无。

## ④ 专业对照（外部论据，URL+发布方+年份）

1. **同一 Durable 任务被多触发面唤醒时，业界要求以"幂等 + 唯一写者"取代"删触发面"**：Apache Airflow 官方"Idempotency"核心概念页明确 task 必须可安全重跑、并以 idempotency key 保证重复调度的正确性；其 Datasets 文档另述"数据到达驱动的 DAG（event-driven）与时间驱动（time-based）可并存，由数据新鲜度而非墙钟决定重跑"。
   - https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/idempotency.html （Apache Software Foundation，2024）
   - https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html#dataset-triggering （Apache Software Foundation，2024）
2. **Orchestration vs Choreography 是显式的架构二选一，且业界共识是"混合时须指定中心"**：Camunda 官方概念文档把"中心编排器（orchestration）"与"去中心协同（choreography）"对立定义，并指出大型系统通常混用，但**必须有一处权威流程定义**，否则流程可见性丢失。
   - https://docs.camunda.io/docs/components/concepts/orchestration-vs-choreography/ （Camunda，2024）
3. **分布式幂等写模式（先占记号 + 重跑无害）的开源正典**：Fowler《Patterns of Distributed Systems》"Idempotent" 章（Addison-Wesley，2021）描述 request-ID / dedupe-key 先占后写的做法，与本仓 `_touch_marker` 先拍板先占、失败不回滚同构。
   - https://martinfowler.com/articles/patterns-of-distributed-systems/idempotent.html （Pearson/Fowler，Addison-Wesley，2021）

三源独立（Apache 基金会 / 商业 BPM 厂商文档 / 学术-工业合著专著），检索日期 2026-09-25。共同指向：**两触发面并存不构成需要"砍掉一条"的缺陷，需要的是"单一权威实现 + 可机判幂等声明"——即路径 C 的形态。**

## ⑤ 风险（做错的最坏情形）

- **资金安全：当前零暴露**（GRADUATED_PACKAGES 恒空 + 观察记录模式，实测 2.4）。**但这是"今天"的安全**：一旦包集非空（L06-C01 落地/毕业策略出现），双触发面的日序差异会立刻变成"同一天两条不同仓位上限"的生产事故，而现在的幂等是"先占者胜"（后到的合法修订会被吞）→ **路径 C 若不加 T3 修订权设计，等于把未来某天的仓位下调指令静默丢弃**。这是本项唯一的资金尾部。
- 选 B 的运维代价：13 个钩子迁移期任一漏迁 = 该产出永久停摆且无告警（哨兵 L09-C04 未施工）；且违反 §9.3 需新裁定，属 high 域门位。
- 选 A 的运维代价：段表裁剪掉的事件漏醒兜底能力消失，历史上 2026-09-15~09-18 断供事故的形态会重演（`daily_loop_master_switch.py:8` 自述该根因，引自注释未复测）。
- 不裁（维持现状）的代价：**L09 SKEL 的"增量工作冻结在双轨上"无机制执行**，下一批人可能在总扳手里再写一遍 decision 段 → 那才是真第三套。

## ⑥ 解锁依赖（还缺什么）

1. **段重叠点名表**：`PHASE_STAGES.full` 16 段 × `wire_data_scheduler` 13 产出者的交集，逐段注明"事件链已覆盖/仅 cron 覆盖/两者重叠"——本班未盘（缺一次成表工作）。
2. L09-C04 决策链哨兵未施工 → 目前"漏跑"与"跑了但空包"**在观感上无法区分**（实测无任何 decision 缺勤告警件）。
3. 蓝图 §八 8 批准点逐条裁定结果（本项无论哪条路径都依赖其中第 2/3/7 点）。
4. L06-C01 上岗规则 v1 的 state_matrix 填格与 Owner 追认（否则"通电"永远停在空包）。
5. L09 SKEL 三处计数/行号更正（9→13、764-767→806、T3/T4 自裁状态）。

## ⑦ 一句话推荐（推荐待总筹拍）

推荐 **C（只下"编排器本体唯一=orchestrator、两轨皆触发面、禁第三套"的收拢令，并把"二选一"降级为未来的可选优化）**，同时把 **A 的两个子件（双轨对账机判守卫 + 段重叠点名表）** 挂为 C 的随批工作项，理由：实测蓝图版 S1-S7+刀1-刀4 已在产，"二选一"的前提（有两条实现可选）不成立，强行裁 B 会付 13 钩子迁移费却买不到任何新能力。
