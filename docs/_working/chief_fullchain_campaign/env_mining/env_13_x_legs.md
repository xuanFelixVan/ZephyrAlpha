---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_13_x_legs.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-13 离场与应急风控 挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案

- **真源锚**：config/trading_decision_map.yaml nodes[flow=exit_flow]（XFLOW+S1×7+S2×7+X1×4=19）；骨架=01_skeleton_environments.md §2-丙
- **职责一句话**：S1 卖出信号六桶收集评分→S2 离场执行路由（怎么卖）→X1 应急保命横切（kill switch 常驻不可移除，X1 是全系统保命红线）
- **节点清单（19）**：X-FLOW 今天卖什么(terminal)｜S1 信号收集评分｜S1-01 六桶分类(sell_signal_collector)｜S1-02 止损族(stop_loss_strategy)｜S1-03 止盈族(take_profit_strategy)｜S1-04 破位退潮(breakout_failure_detector)｜S1-05 融合紧迫度(sell_signal_fusion_engine)｜S1-06 强制清仓绕过(strategy_abnormal_exit_orchestrator)｜S2 离场执行｜S2-01 执行方式路由(critical,sell_execution_planner)｜S2-02 T+1 涨跌停约束(t1_sellable)｜S2-03 执行时段路由(sell_session_router)｜S2-04 本地条件单(local_order_queue)｜S2-05 分批止盈(scaling_out)｜S2-06 卖出闭环效率(sell_execution_quality_tracker)｜X1 应急保命(kill_switch)｜X1-01 熔断分级(drawdown_state_machine)｜X1-02 熔断期减仓(drawdown_liquidation_guard)｜X1-03 护盘白名单(defensive_asset_whitelist)
- **图面状态**：confidence proposed=16 / untested=3；activation continuous11/intraday7/postmarket1（红线常驻）；critical=X-S2-01；red_reason：FLOW/S1/S2=structural/terminal；**X1 红线语义（图 algo_note）：组合回撤 25% 或单日 -6%→无条件全清仓+冻结全部开仓通道，仅 Owner 手动解除，AI 熔断只降档不升档**

## §1 六向台账

| 向 | 内部反查发现（带路径证据） | 外部 | 判定 |
|---|---|---|---|
| ①上游 | 图内 IN 13 边（全场最多）：L4-08 突破失败降级、L1-AGG、P-P2/P1-04/P1-06、P2-04/P2-03、F-C2-01、L0→X-R1、L9-V1/V2——四流全喂离场，"卖"是全图汇聚点 | 止损/止盈/破位三族+紧迫度融合与业界 sell-side stack 同构；熔断红线为仓内 Owner 合规设定 | signal |
| ②下游 | 图内 OUT 6 边：S2-06→F-C3-01 归因+L4-12 预检回喂、X-R1→F-C2-01/P-P2-01、X-R1-02→P2-04、X-R1-03→L4。grep 消费方：src/zephyr/trading/boot_hooks.py、trading/trigger_registry.py、trading/protection_index.py、trading/trading_contracts/risk/kill_switch_state_store.py+trading_kill_switch.py、ex_core/pre_execution_checker.py+risk_layer_orchestrator.py+trading_session.py（kill switch 常驻挂 boot/trigger/precheck 三面） | — | signal |
| ③算法机制 | 六桶信号分类（sell_decision/core/sell_signal_collector.py）；融合紧迫度（sell_signal_fusion_engine.py）；回撤状态机熔断分级（risk/core/drawdown_state_machine.py）；清算卫兵（drawdown_liquidation_guard.py）；护盘白名单（position/core/defensive_asset_whitelist.py）；绕过通道（trading/strategy_abnormal_exit_orchestrator.py，S1-06 强制清仓不走常规评分）；执行方式/时段双路由（sell_execution_planner.py+ex_sor/core/sell_session_router.py） | — | signal |
| ④后端代码 | 16/19 有码全在盘（无码=X-FLOW/S1/S2 三个族头节点）。tests/：tests/trade/sell_decision/{test_sell_signal_collector,test_s1_scan_orchestrator,test_t_trade_coordinator,test_breakout_failure_detector,test_scaling_out,test_scaling_out_architect,test_sell_execution_planner,test_stop_hunting_protector,test_replacement_rebalance_seller}.py；tests/gov/risk/{test_drawdown_state_machine,test_drawdown_liquidation_guard,test_drawdown_attribution,test_drawdown_bankruptcy_floor,test_drawdown_broker_side_stop,test_drawdown_consecutive_loss,test_drawdown_forced_rest,test_drawdown_session_persistence,test_ashare_stop_loss_engine,test_risk_signal_consumer_wiring}.py；tests/position/test_defensive_asset_whitelist.py | — | signal |
| ⑤前端呈现（只登记） | dashboard/components/warroom.py（熔断/保命状态读出）、api_server.py；kill switch 状态面经 trading_contracts/risk/store | — | signal（登记） |
| ⑥数据字段 | data_refs=DS-082/DS-150；drawdown 会话持久化有专测（test_drawdown_session_persistence=熔断态跨重启证据面） | — | signal |

## §2 挖干自评

- **三扫收敛?** 收敛。消费方轮证实 kill switch 三面挂载（boot/trigger/precheck）是本轮最大增量，此后归零。
- **未挖长尾**：(a) S1-01 六桶逐桶的信号源映射表（桶清单在图、逐桶源在码，对位表未逐条核）；(b) S2-06 退出效率追踪的指标口径；(c) S1-06 绕过通道的触发白名单与审计留痕核对。
- **🌑不可得**：①25%/-6% 红线参数的 Owner 裁定底稿（裁定登记归 governance 域，本簿只录图面语义）；②真实熔断触发历史（触发即清仓，无回放台账可得）。

## §3 挖后自审闸三态裁定

**X1 保命四节点=方案封矿（常驻维持）；S1/S2 十五节点=挂起排期**

- 封矿理由（X1）：保命红线终局形态就是现在这样——kill switch 常驻任何档位不可移除、触发即全清+冻结、仅 Owner 手动解除、只降不升；三面挂载（boot_hooks/trigger_registry/pre_execution_checker）+回撤状态机 10 件测试在盘。终局里它没有"再多一步"的位置，继续施工=给保命线加复杂度=加风险。任何后续批次不得以"激活"名义改 X1。
- 挂起理由（S1/S2）：实现与测试齐备但全 proposed，激活依赖 P 流动作清单与 L1 状态（上游挂起链）；且 S2-01 critical 路由的转正须以 sim 腿考试为前提。
- S1/S2 解锁条件：ENV-08/ENV-12 激活 + sim 腿卖出考试通过 + Owner production 门位；X1 挂载面（三 consumers）列入免检保护清单。

## §4 挖矿日志

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| 1 | 图字段轮：19 节点切片+X1 红线语义全文摘录（25%/-6%/只降不升） | signal | critical=X-S2-01；IN 13 边=全场最汇聚点确认 |
| 2 | 代码轮：sell_decision/drawdown/kill_switch 三族码+测试盘点 | signal | 16/19 有码零失踪；drawdown 测试族 10 件、sell_decision 测试 9 件 |
| 3 | 消费方轮：kill_switch 全 trading/ex_core 反查 | signal | 常驻三面挂载（boot_hooks/trigger_registry/precheck）=X1 封矿核心证据 |
