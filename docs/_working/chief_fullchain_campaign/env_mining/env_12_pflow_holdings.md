---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_12_pflow_holdings.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-12 持仓管理 挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案

- **真源锚**：config/trading_decision_map.yaml nodes[flow=position_flow]（PFLOW+P1×7+P2×5+P3×5=18）；骨架=01_skeleton_environments.md §2-丙
- **职责一句话**：买入后的仓位照看三段——P1 持仓体检（对账/分级/逻辑存活/风险否决）、P2 做T与加减仓（T+1 资格→调度→闭环→再平衡）、P3 金字塔加仓（资格门→规则→量级→时点）
- **节点清单（18）**：P-FLOW 手上仓位今天怎么照顾(terminal)｜P1 持仓体检｜P1-01 对账与台账快照(position_state_machine)｜P1-02 分级监控频率(position_triage)｜P1-03 买入逻辑存活(thesis_survival)｜P1-04 风险否决体检(ashare_stop_loss_engine)｜P1-05 组合级体检(position_drift_monitor)｜P1-06 结论与动作清单(position_adjudication_center)｜P2 做T与加减仓｜P2-01 做T资格与成本前置(critical,t1_sellable)｜P2-02 做T调度(t_trade_coordinator)｜P2-03 做T闭环与成功判定(critical,t0_trading_pipeline)｜P2-04 减仓与再平衡(rebalance_engine)｜P3 加仓决策｜P3-01 资格门(pyramiding_rules)｜P3-02 金字塔规则(同文件)｜P3-03 量级与风险核算(position_sizing_engine)｜P3-04 时点与执行(position_limit_enforcer)
- **图面状态**：confidence proposed=14 / untested=4；activation premarket7/intraday6/continuous3/on_demand2；critical=P2-01+P2-03；red_reason：FLOW/P1/P2/P3=structural/terminal

## §1 六向台账

| 向 | 内部反查发现（带路径证据） | 外部 | 判定 |
|---|---|---|---|
| ①上游 | 图内 IN 7 边：L1-AGG 三喂（P1/P3-01/P2-01——市场状态直改做T与加仓资格）、L4-10 订单状态机→P1-01（成交落地进台账）、X-R1/X-R1-02 应急→P2-01/P2-04（保命压倒做T）、L0-04→P2 | T+1 可卖数量核算为 A 股制度件；做T 闭环成功判定口径为仓内定义 | signal |
| ②下游 | 图内 OUT 8 边：P1-04/P1-06/P2→X-S1 卖出信号、P2-04/P2-03→X-S2-01 卖出执行、P3-04→L4 买入执行、P2-03→F-C3-01 归因。grep 消费方：src/zephyr/autonomy_core/agents/t0_trader_agent.py、frontend/services/dashboard_feeds.py、plan_engine/daily_loop_master_switch.py、pf_alloc/allocation_orchestrator.py、position/core/core_satellite_allocator.py+intraday_position_constraint.py；日循环挂点：position_checkup_orchestrator.py:5（trading_day_cycle_map.yaml:2488）+ pf_alloc_rebalance_check 槽（:4331/:4465） | — | signal |
| ③算法机制 | 持仓状态机台账（position/core/position_state_machine.py）；体检编排（position_checkup_orchestrator.py→adjudication_center.py 动作清单）；T+1 可卖（t1_sellable.py，critical）；做T管线（signal_ashare/intraday_t0/t0_trading_pipeline.py，critical；t_trade_coordinator 调度）；金字塔（pyramiding_rules.py）；量级（position_sizing_engine.py）；限额（position_limit_enforcer.py） | — | signal |
| ④后端代码 | 14/18 有码全在盘（无码=P1/P2/P3/FLOW 四个族父节点）。tests/：tests/position/{test_t1_sellable,test_position_sizing_engine,test_position_checkup_orchestrator,test_pyramiding_rules,test_budget_change_handler,test_sell_position_link,test_position_audit_logger}.py、tests/trade/position/ 同名镜像、tests/gov/audit/test_t0_{ceiling_capacity_exam,conditional_e4_v3_exam,gpu_condition_pack,six_phase_materialize}.py（做T考试族 4 件）、tests/ai/autonomy/{test_t0_trader_agent,test_position_optimizer}.py、tests/trade/sell_decision/test_t_trade_coordinator.py | — | signal |
| ⑤前端呈现（只登记） | dashboard/components/position_monitor.py、app_panel.py、services/dashboard_feeds.py、api_server.py 持仓读出面 | — | signal（登记） |
| ⑥数据字段 | data_refs=DS-009（持仓/成交表族）/DS-150/DS-067/DS-082/DS-107；台账快照产物喂 ENV-15 账务对账（其 unwired 缺口另簿在册） | — | signal |

## §2 挖干自评

- **三扫收敛?** 收敛。测试轮发现 t0 考试族 4 件在 gov/audit（超出预期密度），消费方轮 t0_trader_agent/dashboard_feeds 后归零。
- **未挖长尾**：(a) t1_sellable 与 X-S2-02 同文件双节点的职责切分核对（一码两图节点，边界待图侧澄清）；(b) position_drift_monitor 与 firm_risk_aggregator 的体检/约束重叠度；(c) rebalance_engine 触发源清单。
- **🌑不可得**：①做T闭环的历史成功率台账（t0 考试在册但通过率读数待施工批）；②P1-03 thesis_survival 的"买入逻辑"结构化存储面（假设文本从哪来无证据）。

## §3 挖后自审闸三态裁定

**挂起排期（主体）——图语义→代码施工令缺口（激活依赖上游）**

- 理由：14/18 有码+测试密度可观（position 双目录+t0 考试族 4 件），实现面不缺；缺的是激活链——P1/P2/P3 全部以 L1-AGG 状态与 L4 成交回执为触发源，两源均在挂起链（ENV-08/ENV-11），本流单独施工=无米之炊；且 14 节点全 proposed 无 verified。按纪律挂起排期。
- 施工令候选（解锁后顺位）：P1 体检编排日循环化（position_checkup_orchestrator 已有挂点:2488，补全天候触发面）> P2-01/P2-03 两个 critical 的 sim 腿考试转正 > P3 金字塔规则参数考试。
- 解锁条件：ENV-08 state_matrix 激活 + ENV-11 执行层 sim 腿跑通 + Owner production 门位。
- 保命交叉（X-R1→P2-01 压倒关系）维持只读，不因本流挂起而弱化。

## §4 挖矿日志

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| 1 | 图字段轮：18 节点三段分族+critical 双点（P2-01/P2-03）确认 | signal | structural/terminal 分型；t1_sellable 一码双节点发现 |
| 2 | 代码轮：14 module_ref 存在性+position/t0 测试族盘点 | signal | 零失踪；t0 考试族 4 件+position 双目录=测试密度全场前列 |
| 3 | 消费方轮：position_checkup/t0_trading_pipeline/day-cycle 反查 | signal | 日循环两挂点（checkup:2488、rebalance_check 槽）；t0_trader_agent 自治消费锚 |
