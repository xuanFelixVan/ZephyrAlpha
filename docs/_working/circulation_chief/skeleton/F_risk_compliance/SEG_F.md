---
ttl: task_bound
title: S3 挖矿档·F 段风控合规链（F59-F63）——W3-2
session: st-ffchief-20261001
date: 2026-10-01
status: mined
---

# F 段·风控合规链（F59-F63）六向台账（W3-2 代码级核验）

> 段结论：F59/F60/F61/F63 挖干（F61 持久化已实证在跑）；F62"零注入"说法过期——纸面链五闸已注入，
> 残余 LIVE 侧两闸+broker_ack 人工面，**施工中 by lane-f62**（本车道只核验不施工，详见 F62.md）。
> 段健康：红→黄（F62 断链级 P0 大幅收窄为 LIVE 残余）。

## F-01(F59) 风控限额与止损引擎

| 维度 | 台账 |
|------|------|
| 上游 | REG-RLM-001（限额册）；F63 NAV/持仓 |
| 下游 | F47（应急保命）/F41（执行约束） |
| 生产者 | `src/zephyr/risk/risk_manager.py:53`（RiskManagerBase ABC）；`src/zephyr/risk/atr_stop_engine.py:122`（AtrStopPlan；:72 StopRegime）；`src/zephyr/risk/core/ashare_stop_loss_engine.py` |
| 消费者 | risk/core/{ai_agent_monitor, alert_generator, model_risk_audit, operational_risk_monitor, crowding_monitor}.py、risk/implementations/{default_risk_validator, default_stop_loss_engine}.py、position/core/position_checkup_orchestrator.py（grep -rln 8 处命中） |
| 自动化态 | 事件（持仓+行情→限额/止损判定）；paper 会话"风控层必装配"（start_paper_session.py:8：DrawdownTracker 基线只取券商实时净值，读不到=拒绝装配 exit 1） |
| 运行态 | 真源册实测 `docs/01_policies_and_standards/_registry/catalogs/risk_limit_registry.yaml`：REG-RLM-001（:18），risk_limit_id 计 **118 条**（骨架写 117——计数漂移+1，4421 行） |
| 三态复核 | **挖干** ✅（计数漂移注记） |

## F-02(F60) 回撤状态机与熔断

| 维度 | 台账 |
|------|------|
| 上游 | F63 NAV 流水 |
| 下游 | F47（熔断触发全流横切） |
| 生产者 | `src/zephyr/risk/core/drawdown_state_machine.py:94`（DrawdownState Enum）；`src/zephyr/risk/core/drawdown_liquidation_guard.py:73`（CancelRatePrecheck；:92 LiquidationTimeoutAlert）；`src/zephyr/risk/core/drawdown_broker_side_stop.py`（:71/:87/:104 Config/Intent/Report 三件） |
| 消费者 | risk/core/drawdown_session_persistence.py（会话持久化）、risk/core/var_breach_state_machine.py、scripts/backtest/sim_daily_runner.py、position/core/drawdown_controller.py（start_paper_session 装配链） |
| 自动化态 | 事件（NAV 驱动分级）；paper 会话必装配（双保险=清算 guard+券商侧保护性停止 intent） |
| 运行态 | 装配证据：start_paper_session.py:8 INVARIANTS"DrawdownTracker 基线只取券商实时净值（读不到/非正=拒绝装配会话 exit 1，禁兜底常量猜基线）" |
| 三态复核 | **挖干** ✅ |

## F-03(F61) KillSwitch 三实例族

| 维度 | 台账 |
|------|------|
| 上游 | F47 熔断信号/F59 限额违约 |
| 下游 | 全交易面闸（执行/会话/API 面） |
| 生产者 | ①`src/zephyr/trading/trading_contracts/risk/trading_kill_switch.py:61`（KillSwitch BaseModel；:52 KillSwitchLevel）+ **持久化件** `kill_switch_state_store.py`（:50 DEFAULT_STATE_RELATIVE=`data/runtime/trading_kill_switch_state.json`；:60 save_state；:93 rebuild_from_disk）；②`src/zephyr/infrastructure/capacity_assurance/kill_switch.py:50`（:43 FuseState）；③`src/zephyr/security/access_control/kill_switch.py:75`（KillSwitchStatus；:66 State） |
| 消费者 | ex_core/trading_session.py、frontend/dashboard/api_server.py（三实例族消费）；autonomy_core/kill_switch_orchestrator.py、ai_layer/redline/{negative_list, session_env_guard}.py、ai_layer/intake/intake_events.py、data/alert_webhook_dispatch.py（access_control 实例消费面） |
| 自动化态 | 事件（熔断信号→闸位翻转）；重启存活（状态外部化） |
| 运行态 | **持久化实跑在案**：`data/runtime/trading_kill_switch_state.json` saved_at=2026-09-30T10:15:46Z，POSITION_LIMIT active=true、DAILY_LOSS/CIRCUIT_BREAKER/SECOND_LEVEL/API_TIMEOUT 各闸位在册；装配注记 start_paper_session.py:8"Kill Switch 状态经 JsonStateStore 外部化（重启存活熔断，#ARCH-QUANT-002 生产零注入治本）" |
| 三态复核 | **挖干** ✅；骨架"持久化待裁"→**实证已落地**（state store+影子件+rebuild 链），建议 Owner 追认注记（见三态变迁清单 #3） |

## F-04(F62) 合规门与程序化交易报告

| 维度 | 台账 |
|------|------|
| 上游 | REG-CMP-REPORT-001（报备登记） |
| 下游 | F53 拒单（ComplianceGateBlockError） |
| 生产者 | `src/zephyr/compliance/compliance_report_registry.py:133`（ReportGate；:144 check()）；注入面 `src/zephyr/ex_core/order_manager.py:371`（_check_compliance_gates 五道硬闸）；装配面 sim_saga_assembly.py:163-177（五闸全注入）、qmt_trading_session.py:121-129（三闸） |
| 消费者 | F53 submit_order（:348 挂点，:394-396 先报告后交易拒单）；manipulation_realtime_monitor（订单事件流消费委托流） |
| 自动化态 | 事件（发单前同步硬闸，Fail-Closed）；broker_ack 报送动作为人工（设计内，INVARIANTS :8） |
| 运行态 | 提交 fa9ae365331 [st-zcloseout-20260928]"F62 P0-10 模拟侧执法接线重投……G07 程序化报备闸+G09 信息空窗回避闸接入 OrderManager C-002 链……8 项红绿合成测试全绿。实盘路径文件零改动" |
| 三态复核 | **存疑(P0 断链级)→纸面链 built**：M7"码成闸空零注入"过期（三闸 08-15 AI-ASM-001+两闸 09-28 st-zcloseout）；残余=LIVE QMT 路径仅 3/5 闸+broker_ack 人工回填面。**施工中 by lane-f62**（.runtime/sessions/st-c8-f62 等会话在案；本车道只核验不施工）。详见 F62.md |

## F-05(F63) 仓位管理与对账

| 维度 | 台账 |
|------|------|
| 上游 | F57 对账/成交流 |
| 下游 | F42（体检）/F60（NAV 喂回撤机） |
| 生产者 | `src/zephyr/position/core/position_state_machine.py:91`（PositionState；:103 ObservingReason）；`src/zephyr/position/live_nav_recorder.py`（:63 AssetSnapshot/:72 NavPoint/:85 NavCurve/:102 SimulatedQmtAssetSource）；position_reconciler（ex_core 与 position 双目录各一件，见漂移注记） |
| 消费者 | position/core/position_checkup_orchestrator.py、position/services/position_audit_logger.py、frontend/services/dashboard_feeds.py、scripts/run_post_settlement.py |
| 自动化态 | 定时（盘后对账）+事件（成交驱动状态机流转） |
| 运行态 | sch_post_settlement 采样至 09-30 00:18（与 F57 共链）；NAV 链经 live_nav_recorder 供 F60 基线 |
| 三态复核 | **挖干** ✅；漂移注记：`src/zephyr/ex_core/position_reconciler.py`（218 行）与 `src/zephyr/position/position_reconciler.py`（207 行）同名 PositionReconciler 双件并存——克隆嫌疑登记（clone_guard 面，非断链，不属本车道处置） |
