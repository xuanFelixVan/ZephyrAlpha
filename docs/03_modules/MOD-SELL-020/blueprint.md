---
module_id: MOD-SELL-020
title: "离场执行编排器蓝图 — S1 扫描→S2-01 路由→计划三件闭环 + R1-02 熔断处置挂接"
doc_type: blueprint
status: Active
version: "0.1.0"
ttl: permanent
design_maturity: design
layer: L03_sell_decision
layer_name: sell_decision
functional_domain: sell_decision
responsibility_domain: 
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-09-29"
last_updated: "2026-09-29"
priority: P0
blueprint_level: module
---

# MOD-SELL-020 | Exit Execution Orchestrator 离场执行编排器

> **域**: D_SELL_DECISION | **层**: L03 卖出决策 | **优先级**: P0 | **safety**: M | **ai_autonomy**: ai_modifiable
> **状态**: design（planned→testing 随批转） | **版本**: 0.1.0 | **SSoT**: depgraph MOD-SELL-020
> **立项真源**: docs/_working/fullconnect_campaign/f_exec_risk/01_f46_s2_exit_execution.md 缺口 1（S1→S2-01 路由编排缺位，P0）+ 02_f47_r1_emergency_lifeline.md 缺口 1（R1-02 判了没人执行，P0）

## 1. 模块定位

F46/F47 两卷 P0 缺口的编排收口件（services 层，paper 车道）：①消费 S1 扫描产物（**事件文件接口**，
JSONL 契约先行——S1 编排袋 st-c9-f45 未落，本件只依赖卷内契约 `FusedSellDecision` 语义，不 import 其未落
模块，防碰）；②把执行计划三件（sell_execution_planner MOD-SELL-019 / scaling_out MOD-SELL-017 /
sell_execution_quality_tracker MOD-SELL-012，包外零消费实证见 F46 卷）接入 plan 生成→校验→执行最薄
生产调用链；③R1-02 熔断期减仓处置编排挂接（drawdown_state_machine 判定→梯度减仓/全清路由 +
drawdown_liquidation_guard MOD-RK-050 撤单率预检/全清超时守卫，破其零消费）。**零真实订单、零 DB、
纯文件平面**——产出仅为 paper 意图记录（order intents），真实执行归 40 号执行层（F53）。

## 2. 不变量 (INVARIANTS)

- **事件文件接口防碰**：S1 产物以 JSONL 行协议输入（`sell_exit_directive`），缺 `execution_signal`
  的行如实 skip 留痕不猜测（零伪造）；本件不 import st-c9-f45 未落模块。
- **R-M2-5 防御姿态**：paper 平面仅防御动作（强清市价/止损限价/收盘竞价止损/跌停排队）可机械执行
  出 intent；止盈尾盘/置换类如实记 `unexecutable(action_not_order_mapped)`（Owner 裁定 R-M2-5 选②）。
- **盘外 fail-closed**：route_sell 盘外 NO_ROUTE→blocker，不出 intent（继承 MOD-XS-016 语义）。
- **T+1/跌停硬约束透传**：BLOCKED_T1/LIMIT_DOWN_QUEUE 为合法状态输出，不改判不吞（MOD-SELL-019）。
- **R1-02 梯度非一刀切**（D113）：减仓序=重亏(浮亏升序)→高波动(ATR 降序)→压舱石保留最后；
  L4 全清走 KILL_SWITCH 强清事件进 S2-01 绕过通道（ planner INVARIANTS：KillSwitch 流动性差先卖）。
- **守卫前置**：KILL 路径必过 check_cancel_rate（撤单率 12% 预警/15% 禁续撤）+
  check_liquidation_timeout（30s 未全清告警人工介入，不自动强平）——MOD-RK-050 语义透传。
- **纯文件平面**：本件不触 DB、不触真实下单通道、不启进程；continuous 保命扫描常驻归 RC/M7+M5
  常驻族（F47 缺口 2，启动=Owner/运行班门位），本件仅提供可被其调用的编排函数。

## 3. 接口

- `load_exit_signal_events(path)` → `EventLoadResult(events, skipped)`：JSONL 事件装载。
- `build_exit_plan(event, *, now_time, today)` → `ExitExecutionPlan`：信号→S2-01 时序映射（planner）
  +S2-03 时段路由（router）+S2-05 分批提示（scaling_out 可选注入）。
- `decide_execution_posture(plan, *, plane="paper")` → `PostureDecision`：R-M2-5 姿态闸。
- `run_exit_execution_cycle(events_path, out_dir, *, fills_path, ...)` → `CycleReport`：
  计划→校验→执行（写 intent 文件）→S2-06 质量闭环（fills 注入时 evaluate_execution_quality）。
- `route_drawdown_disposal(state, positions, **guards)` → `DrawdownDisposalPlan`：R1-01 判定→
  R1-02 处置编排（L1-L4 指令分级）；`disposal_to_exit_events(plan, ...)` 桥接 L4→S2 强清事件。

## 4. 依据

- F46 卷 §三/§四（三件零消费复证、缺口 1）+ F47 卷 §一/§三/§四（R1-02 零消费、缺口 1/2）
- 42 号 memo §3.7/§3.8/§3.9；TDM-X-S2-01/03/05/06、TDM-X-R1-01/02 节点语义
- R-M2-5（模拟盘仅防御姿态可机械执行）；D95 输入仲裁序；D113 减仓顺序
