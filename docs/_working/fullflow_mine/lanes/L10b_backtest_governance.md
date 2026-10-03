---
ttl: task_bound
title: "回测治理库与data目录挖矿作业簿"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-01
topic: fullflow_mine
---

# L10b 回测库（c1_backtest 16 表）+ 治理库（governance.db 45 表）+ data/ 目录挖矿作业簿

## ① c1_backtest 16 表读数与逐表用途判定（CH 只读，zephyr_reader SELECT-only，读数时点 2026-10-01）

**断供定案：alloc_budget_daily 停 09-28 一案=已修复。** 实测 09-29/09-30 各 2 行在库，09-15 起每日连续（30 行/11 交易日，无跳日）；修复载体=commit `8c5117b600`[st-circ-a7-20260930][全流通·P0断链三连治·F82/F27+F48/F92]（2026-09-30 落地）。骨架车道 F27+F48 断链记录就此治愈，账面闭环。另一疑点 `decision_daily.max(trade_date)=2026-10-08` **非异常**：3 行均 ingest 于 09-30，trade_date=国庆假期后下一交易日（101-08），no_trade=1/budget_run_missing 为决策时点（08:45/14:12/16:21）先于当日 alloc run 写库的正常时序语义。

| 表 | 行数 | max(日期列) | 代码命中（生产/消费） | 判定 |
|---|---|---|---|---|
| regime_snapshot_history | 3,632 | 09-30 | 24 文件：pf_alloc/allocation_inputs+orchestrator+crisis_gate、plan_engine/daily_plan | 活（分配链核心供件） |
| regime_state_anchored | 2,242 | 09-30 | 16 文件：regime/anchored_state_machine、sector_state_pipeline、pf_alloc | 活 |
| strategy_screen | 1,389 | ingest 09-30 17:11 | 24 文件：strategy_screener_3d、n_trial_ledger、dashboard、decay_certifier | 活 |
| sim_pocket_daily | 331 | 10-01 | 18 文件：rebalance_check_runner、scheduler、redline/dashboard_pipeline | 活 |
| sim_daily_report | 256 | report_date 09-30 | 3 文件：paper_outpost、sim_daily_runner | 活（消费面窄，单链） |
| sim_trade_log | 85 | 10-01 | 13 文件：shadow_portfolio、daily_decision_orchestrator、redline | 活 |
| sim_attribution_daily | 122 | 09-28 | 4 文件：pipeline_events、feedback_prior、sim_attribution_report | **挂账**：3 日未更，与 sim 链 10-01 在跑不同步，疑似归因步掉队（工单 W-3） |
| sim_platform_journal | 21 | 10-01 | 5 文件：sim_platform_journal、run_post_settlement | 活（审计台账性质，行少正常） |
| decision_daily | 127 | 10-08（节后惯例） | 6 文件：daily_decision_orchestrator、warroom、daily_loop_master_switch | 活 |
| cohort_daily_ledger | 221 | 09-30 | 6 文件：alt_data/cohort_daily_writer、emotion_index_builder | 活 |
| crisis_gate_log | 83 | 09-03 | 3 文件：pf_alloc/crisis_gate、sim_paper_ledger | 活（事件驱动型：无危机=无行，非停更） |
| hypothesis_precheck | 309 | ingest 09-30 19:35 | 7 文件：factory_intake_pipeline、feedback_prior、intake_ledger_recon | 活 |
| node_verdict | 58 | ingest 09-17 | 7 文件：trading/validation(decay_watch/runner)、dashboard | **挂账**：ingest 14 天未更，验证链 runner 调度需实证（工单 W-2） |
| alloc_budget_daily | 30 | 09-30 | 12 文件：allocation_persistence、allocation_orchestrator、l9_readiness_aggregator、scheduler | 活（断供已修，见上定案） |
| alloc_budget_change_log | 28 | 09-30 | 3 文件：allocation_persistence/orchestrator | 活 |
| alloc_shrinkage_daily | 15 | 09-30 | 4 文件：allocation_inputs/persistence/orchestrator | 活 |

小结：16 表=活 13 + 挂账 2（sim_attribution_daily、node_verdict）+ 事件型正常空转 1（crisis_gate_log 归活）。全部 16 表代码生产/消费双命中，零"表在码亡"。

## ② 治理库 governance.db 45 表三态（SQLite mode=ro）

活表 32 张（读数摘录）：reconcile_execution_log 95,919／fle_metrics 70,901／drift_audit_findings 27,570／audit_entries 23,722／drift_events 12,813／task_reviews 6,149／gate_runs 6,899／gates 1,791／drift_scan_results 2,212／tasks 2,597／events 3,111／fix_budget_consumption 807／llm_call_log 850／audit_summary 290／其余 19 张 1-52 行（gate_decisions 35、prediction_log 40、rule_enforcement_log 36、slow_queries 36、usage_records 36、integrity_records 52、judgment_records 36、fle_alerts 38、fle_dispatch_log 38、fix_records 36、f5_state 5、domains 2、fix_compliance 2、fix_idempotency 1、fix_patterns 1、scan_results 1、llm_daily_analysis 9、_schema_version 33）——全部有在岗读写链，不逐表展开。

**13 张 0 行表逐张判定**（判据：CREATE 来源+INSERT 写口+SELECT 消费，全仓 grep 排除 tests）：

| 表 | 写口 | 读口 | 三态判定 |
|---|---|---|---|
| attribution_results | reporting/attribution_result_store.py:88 | 唯一调用链 attribution_calculator **无生产调用方** | 待激活：有表有写口无触发，Brinson 归因结果链未接线（工单 W-1） |
| audit_trail | 全仓零写 | 全仓零读 | **候退役**：hash-chain 设计未启用；活跃审计由 audit_entries（23,722 行）承担，同域被替代 |
| circuit_breaker_state | gov_enforcement/rule_enforcement/circuit_breaker.py:299 | admission_controller | 待激活：写口在岗，0 行=熔断未发生（正常空，禁退役） |
| costs | 全仓零写 | 全仓零读 | **候退役**：w5_1 零触发零消费；建表 SQL 无代码来源（外部手建），挂 Owner 净删门位 |
| ke_tombstones | 全仓零写 | 全仓零读 | 待激活：knowledge 生命周期配套墓碑，随 knowledge 家族联动；单判候退会斩断 KE 退役语义 |
| knowledge | 全仓零写 | d5_architecture 两验证器 SELECT ke_id（detect_deprecated_adr_references:72、validate_cross_references:235） | 待激活：**有读无写**——消费端等米下锅，缺生产者（工单 W-1b） |
| reconciliation_differences | trading/recon_runner.py:117（append-only） | recon 链 | 活链路正常空：recon 在岗（execution_log 95,919 行）而差异 0 行=零漂移，"待触发"非死表 |
| report_archive | 全仓零写 | api_server/review_trigger 引用名 | **候退役**：实际归档走 JSONL sink（reporting/report_archive_sink.py persist→文件），DB 表口径被替代 |
| switch_registry | intelligence/switch_engine/switch_registry.py:182（f-string INSERT） | switch_engine 家族 | 待激活：champion/challenger 引擎在库，无注册事件发生（安全侧空） |
| task_events | gov_audit/event_store.py:184+schema v2 迁移 | projection_engine/snapshot_manager | **挂账**：写口齐但未跑；同域活表 events(3,111) 已承担事件流——w5_1 同域重复簇，收敛裁定另案（工单 W-4） |
| task_files | task_repo.py:231+orchestrator/file_task_mapper.py:78 | coordination_state_board/session_worktree | **挂账**：tasks 活跃（2,597 行）而映射件未接，文件-任务关联链未启用 |
| task_snapshots | governance/audit/snapshot_manager.py:134 | 断点续扫 | **挂账**：快照管理器未运行，事件溯源断点恢复面未开 |
| tx_idempotency | financial_governance/atomic_transaction_manager.py:636（PREPARED） | 同模块 | 待激活：资金原子事务从未发生=安全侧空，禁退役（资金操作前置幂等件） |

三态计数：**活（含待触发正常空）1 + 待激活 6（attribution_results/circuit_breaker_state/ke_tombstones/knowledge/switch_registry/tx_idempotency）+ 挂账 3（task_events/task_files/task_snapshots）+ 候退役 3（audit_trail/costs/report_archive）**。候退役只登记不执行（注册表净删=Owner 门位 §5）。

## ③ data/ 目录资产粗矩阵

| 资产 | 体量/读数 | 生产/消费链 | 判定 |
|---|---|---|---|
| models/ | 2.7G，local_model 内嵌 bge-m3、bge-small-zh-v1.5、paraphrase-multilingual-MiniLM-L12-v2 | 消费=zephyr.integration.local_model.embedding_router（CLI 懒加载）+autonomy_core drift_semantic_reviewer | 活（本地嵌入兜底，消费频次低挂观察） |
| sentiment_batch/ | 87M：daily_sentiment.jsonl、predictions.jsonl、benchmark.json | 生产=scheduler nightly_sentiment_batch→nightly_sentiment_window；读=scripts/ml/accept_nlp_pipeline 验收+sentiment_pipeline 自述 regime S2 bad_news_flat negative_count 源 | 活（夜批在调度） |
| backtest_artifacts/ | 125M：bt-*.json 60 份 run archive+t0_rule_engine 265 parquet | 消费=backtest/run_archive、closed_book_gate、io/result_repository、dashboard api_server、library lookup | 活 |
| strategy_intake/ | 95M：grid_* 28 批（最新 20260929-040141）、conditional_tables、f06_survivors.csv、c4_deferrals.csv | 消费=strategy_pipeline/intake、promotion_advisory、n_trial_ledger、t0 exams | 活（grid 链跑到 09-29） |
| audit_trail/（目录） | events.jsonl ~88MiB，mtime 09-30 18:16 | compliance/audit_trail 家族热写 | 活（近热）；与 audit-trail/（连字符，events 7 月陈迹+9-29 shadow plan）**双胞胎目录**→w5_1 收敛候选 |
| 空目录×4 | fills（mtime 08-27）/gate_cache（08-27）/scans（09-06）均 0 项 | 全仓无消费引用 | **候退役登记×3**；library_snapshots 0 项但 mtime=10-01 03:32（今日有触点，疑 TTL 轮换清扫）→留观不退 |
| local_fallback/ | 槽位 c1_backtest__sim_daily_report/pocket_daily/trade_log、c1_market__alt_* 全空；_quarantine_20261001 今日 03:52 新建 | CH 降级兜底通道 | 活（零落盘=CH 稳定无降级，隔离区在岗） |
| integrator_progress.db | 38MB，mtime 10-01 04:00 | 数据集成器进度账 | 活（每日写入） |

## ④ 工单（按优先级）

- **W-1 attribution_results 接线**：attribution_calculator 全仓无生产调用方，Brinson 归因结果链"有表有写口无触发"。接线批决策：挂到 decision_daily/sim_attribution_daily 下游，或 defer_reason 登记挂账。W-1b 同批：knowledge 表有读无写（d5 两验证器空转），补 KE 生产入口或宣判该消费面关闭。
- **W-2 node_verdict 停更实证**：ingest 停 09-17（14 天），trading/validation/runner 调度是否存在/被摘除需跑一次 `--status` 实证；与 sim_attribution_daily（停 09-28）同查——两表都属"链在表停"。
- **W-3 命名双胞胎收敛**：data/audit_trail/ vs data/audit-trail/（目录级）+ task_events vs events（治理库表级）两案并交总筹，按 w5_1 同真源可派生必并/同域重复簇收敛裁断；候选退役清单（audit_trail 表、costs 表、report_archive 表、fills/gate_cache/scans 目录）一并提请 Owner 净删门位。

## ⑤ 六向台账（§9A，本车道三资产合并作答，查无留痕）

- Q1 因子：c1_backtest 为因子下游沉淀层非原料层，不产新因子——查无（留痕）；sim_attribution_daily 修复后其 attribution 列可反哺 factor_registry 复核（弱）。
- Q2 策略：alloc_budget_daily/change_log/shrinkage=组合层策略预算真源，strategy_screen→TDM 挂载（STR-MOMTREND-033 mounted 在案）——接线在岗；策略侧缺口=无已毕业包可启（decision 日志自述，裁定#305 安全态）。
- Q3 模块：16 表生产消费双命中已列①；治理库 13 空表写读口已列②——模块级盲点=attribution_calculator 无调用方、snapshot_manager/event_store 未运行。
- Q4 环节：scheduler nightly_sentiment_batch、夜间 grid（09-29）、integrator（10-01 04:00）调度在岗；node_verdict 对应环节疑似脱调度（W-2 实证）。
- Q5 地图：S07_G_回测模拟链/S11_K_治理门禁链骨架与本车道读数吻合；decision_daily gate_snapshot L4 缺席="budget_run_missing"自陈在案，与全流通 P0 断链三连治对应，修后需复扫一次 decision 链全绿验证。
- Q6 盲点：①治理库"零行≠死表"的表意两态（circuit_breaker/tx_idempotency/reconciliation_differences 属安全侧空）census 口径未区分，建议 wiring_registry 加 state=armed 语义；②data/ 根存在 audit_trail 与 audit-trail 双写口 88MiB 级重复风险；③costs 表无代码建表来源=库内存在"野生 DDL"，schema 治理盲区。

## ⑥ 自审闸三态

- 只读纪律：CH 走 zephyr_reader（SELECT-only RBAC）+SQLite `mode=ro` URI，零写库——**过**。
- 写域纪律：本车道仅写本产出文件一个新文件，零既有文件改动、零 git 写、零 commit——**过**。
- 环境纪律：每条 python 前 PATH 修正 Python312（实测 3.12.8）；SOP §9A/§9B/§9C 已读并按三态出口作答——**过**。
- 待办移交：本文件 CREATE-GUARD creation_token 留待总筹落地批次登记（本车道禁 git 写无法自登记）；候退役 6 项（3 表+3 目录）均只登记未执行，合规 §9C 三态出口与 §5 门位。

## 修订记录

- 2026-10-01 v1.0.0 首版：16 表断供定案（alloc 已修）+13 空表三态（待激活 6/挂账 3/候退役 3）+data/ 粗矩阵+工单 3 项。
