---
ttl: task_bound
title: S3 挖矿档·H 段模拟盘→转正链（F72-F75）——W3-2
session: st-ffchief-20261001
date: 2026-10-01
status: mined
---

# H 段·模拟盘→转正链（F72-F75）六向台账（W3-2 代码级核验）

> 段结论：两大 P0 断链改判——F72 SimBridge 断腿已重建在跑（断点移位至 orders 供单缺位）、
> F73 晋升判据执行器已建成在跑（league_judge.py，月度判定书两档均诚实空场）。
> F74 挖干维持；F75 维持存疑（件全等流量）。段健康：红→黄。
> 详见同目录 F72.md / F73.md / F75.md。

## H-01(F72) 模拟盘日跑四件

| 维度 | 台账 |
|------|------|
| 上游 | F25（registry 幸存者）/F70（偏差检测准入门） |
| 下游 | F73（联赛赛绩）/F74（转正建议素材） |
| 生产者 | `src/zephyr/ex_core/live_strategy_adapter.py`（:131 StrategySlot、:106 SlotState、:433 行）；`scripts/start_paper_session.py`（--service=LiveStrategyAdapter 常驻监督模式）；`scripts/backtest/sim_daily_runner.py`（六腿日跑：plan-bridge/plan-execute/e4-replay/report/settle/bridge-execute，:1587；:944 "bridge-execute（F56 断腿重建：SimBridgeExecute 执行腿，处方=delivery_report_20260923 §3）"）；strategy_pipeline/paper_outpost.py |
| 消费者 | F73 league_judge（纸面净值日收益差=赛绩源）；F74 promotion_advisory（四件产出消费） |
| 自动化态 | 定时日跑双任务：sch_paper_session（resource_profile_registry.yaml:1893，采样在档）+ sch_sim_bridge_execute（:2101，09:35/13:05 双时点，run_sim_bridge_execute_daily.ps1:76） |
| 运行态 | sch_paper_session 采样至 10-01 02:56（pid 28496 elapsed 289.7s）；paper_outpost 产物 runs/SCR-OUTPOST-20260930-204826；sim_bridge_execute.log 09-30 双跑 exit 0（"0=ok or honest no-order row"）、10-01 假日 SKIP；heartbeat tmp/live_strategy_biz.heartbeat 09-30 09:35 |
| 三态复核 | **存疑(P0)→改判**：M5"09-24 静默断链"已由 F56 断腿重建批清偿（执行腿 built 在跑+幂等+窗口闸）；残余断点移位=orders 委托批次文件生产者缺位（bridge-execute 诚实 SKIP），详见 F72.md |

## H-02(F73) A/B 联赛与分仓

| 维度 | 台账 |
|------|------|
| 上游 | F72（模拟盘赛绩） |
| 下游 | F74（challenger 上位建议消费位） |
| 生产者 | `scripts/backtest/league_judge.py`（MOD-AUTO-L11-JUDGE，头注"A/B 联赛成对晋升判据执行器（处方 02_ab_league.md 堵点 2/3，F73）"；:433 run_league_judge_due）+ league_registry/league_archive/league_monthly_snapshot/league_restore 五件套 |
| 消费者 | Owner 终审门（判定书建议≠决定）；F74 promotion_advisory（[CONSUMERS] 头注 :9-10） |
| 自动化态 | **事件接线**（非 cron）：strategy_pipeline/pipeline_events.py:214 `"league_judge_due": ("scripts.backtest.league_judge", "run_league_judge_due")`；:798 注册（st-c9-f73 处方堵点 2/6）；月度档 |
| 运行态 | `data/backtest_artifacts/league/judgments/judgment-2026-09.json` + `judgment-2026-10.json`（后者 generated_at=2026-10-01 05:51 UTC，今晨实跑）；两档均 empty_field=true **诚实空场**（零成员/零对局）；判尺 STD-SIM-ACCESS-002=frozen（09-18）/STD-SWITCH-001=draft；msprt 成对判定+BHY q=0.10+相关性闸 ρ=0.7 口径全配 |
| 三态复核 | **存疑(P0 design 未施工)→挖干（翻绿）**：骨架"晋升判据执行器未写"过期（执行器建成+事件接线+两档月度产出）；残余=零参赛者空转（详见 F73.md） |

## H-03(F74) 转正建议书汇总器

| 维度 | 台账 |
|------|------|
| 上游 | F72 四件产出/F73 判定书 |
| 下游 | **Owner 门位→实盘**（全链唯一人工门） |
| 生产者 | `src/zephyr/strategy_pipeline/promotion_advisory.py`（895 行；:101 OWNER_TOKEN_KEY=ZEPHYR_OWNER_APPROVAL_TOKEN；:659"未配置密钥 → fail-closed"；:641/:645 safe_write CAS+写后复核 fail-closed；:674 总闸探针非 normal=拒）；素材读取 :128 governance/:141 deviation_months/:164 fw_evidence/:197 registry_entries/:216 bothwin_items |
| 消费者 | Owner（api_server.py:5014 POST /api/promotion-decide，第四获准写端点，token 常量时间比对）；实盘装配链 |
| 自动化态 | 事件（pipeline_events.py:202 `"promotion_advisory_due": (…promotion_advisory, "run_promotion_advisory_due")`）+人工拍板 decide |
| 运行态 | 门在、advisory 事件链在、token fail-closed 在码；**Owner decide 流量本轮未见实拍**（data/docs 无近期 promotion 决策产物）——"有门无拍板流量"态维持 |
| 三态复核 | **挖干(翻绿) 维持** ✅（骨架翻绿判定复核成立：895 行+事件映射+API 端点三证齐） |

## H-04(F75) 策略生命周期状态机

| 维度 | 台账 |
|------|------|
| 上游 | F23-F27（考试/模拟结果） |
| 下游 | REG-STR-001（strategy_registry.yaml=`docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml` 在册） |
| 生产者 | `src/zephyr/strategy_pipeline/lifecycle_fsm.py`（:125 build_strategy_fsm、:87 SimPromotionGuard、:99 OwnerTokenGuard）；intake.py / registry_writer.py / screen_source.py 同域四件 |
| 消费者 | strategy_pipeline/{paper_outpost, promotion_advisory, intake, pipeline_events}.py（grep -rln 命中） |
| 自动化态 | 事件（考试/模拟结果驱动 FSM 流转；SimPromotionGuard+OwnerTokenGuard 双 guard 把门） |
| 运行态 | 件全+guard 双保险在码；流转流量依 H-01 供单与 H-03 advisory 链（上游空转则 FSM 低速），未发现断链 |
| 三态复核 | **存疑 维持**（偏 built 等流量：代码面无缺口，判定依据=流转实拍不足；维持骨架存疑口径不翻绿）。详见 F75.md |
