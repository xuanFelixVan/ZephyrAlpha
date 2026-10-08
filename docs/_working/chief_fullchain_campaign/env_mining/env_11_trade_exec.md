---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_11_trade_exec.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-11 买卖点与执行 挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案

- **真源锚**：config/trading_decision_map.yaml nodes[layer=L4]（16）；骨架=01_skeleton_environments.md §2-丙
- **职责一句话**：候选→成交的执行总枢纽：分批/时序/锚价/资金分配/打板专项/执行算法/条件队列/突破降级/硬约束/订单九态/部分成交/预检/容灾对账 13 子环节
- **节点清单（16）**：L4 买卖点与执行(structural)｜L4-01 分批建仓(order_splitter)｜L4-02 买入时序(closing_session_decision)｜L4-03 价格锚定(pricing_policy)｜L4-04 资金分配多标的(capital_allocator)｜L4-05 打板执行专项(daban_execution)｜L4-06 执行算法(algo_execution_selector)｜L4-07 条件触发队列(local_order_queue)｜L4-08 突破失败降级(breakout_failure_detector)｜L4-09 执行硬约束(critical,price_cage)｜L4-10 订单生命周期状态机(order_manager)｜L4-11 部分成交与撤改(fill_handler)｜L4-12 订单级预检(pre_execution_checker)｜L4-13 执行容灾对账(three_way_reconciliation)｜L4-14 执行成本反馈与选型回写(execution_quality_scorer)｜TDM-C-L4 币圈买卖点(not_built)
- **图面状态**：confidence proposed=14 / untested=2；activation intraday10/continuous5/postmarket1；materiality critical=L4-09（骨架"critical 11 集中带"实核=全图 critical 共 11：L9×5+L1×2+L4-09+P2-01/P2-03+X-S2-01，执行邻接带占 4）

## §1 六向台账

| 向 | 内部反查发现（带路径证据） | 外部 | 判定 |
|---|---|---|---|
| ①上游 | 图内 IN 10 边：L3/L3-10 预检喂入、L2-03-1/L2-07-1 直喂 L4、P-P3-04 加仓时点回喂、F-C2-01 组合净指令喂入、X-S2-06 卖出闭环→L4-12 预检、X-R1-03 白名单→L4、L9-A02 Tick→L4-14 成本反馈 | 分批+锚价+SOR 选型+预检为业界执行标配（ execution algo stack） | signal |
| ②下游 | 图内 OUT 4 边：L4→E-FLOW 输出建仓信号、L4-08→X-S1 卖出信号、L4-10→P-P1-01 持仓对账、L4-13→F-C3-01 归因。grep 消费方：src/zephyr/ex_core/execution_engine.py、aggregate_root_manager.py、eod_reconciliation.py、execution_report_producer.py、risk_layer_orchestrator.py、compliance/manipulation_realtime_monitor.py；日循环实接：ex_core/live_strategy_adapter.py（trading_day_cycle_map.yaml:812/1843/1890，CONSUMERS 接线自证） | — | signal |
| ③算法机制 | L4-09 五道硬约束（T+1/涨跌停价格笼±2%/成本吃收益 1/3 否决/资金可用/持仓限额——algo_note 在图，码=ex_core/price_cage.py）；订单九态状态机（order_manager.py）；打板全家桶（ex_core/daban_execution.py+daban_instant_circuit_breaker.py+daban_pit_safety.py+daban_monitors.py）；SOR 选型（ex_sor/core/algo_execution_selector.py）；成本回写（ex_sor/services/execution_quality_scorer.py） | 价格笼子/	T+1 为 A 股制度约束，非可选项 | signal |
| ④后端代码 | 14/16 有码全在盘（无码=L4 父节点+币圈）。ex_core 40+ 件在盘（execution_engine/ghost_order_sentinel/cancel_rate_guard/board_lot 等）。tests/：tests/trade/ex_core/{test_daban_execution,test_order_splitter,test_price_cage,test_price_cage_bf6_wiring,test_aggregate_root_manager}.py、adapters/test_qmt_file_bridge_broker.py+test_qmt_file_bridge_quote.py+test_pretrade_risk_gate_sim.py、tests/trade/ex_sor/test_algo_execution_selector.py；**three_way_reconciliation 专测已查无**（tests grep 只中 gov 对账无关件） | — | 半实现 |
| ⑤前端呈现（只登记） | dashboard/components/trade_panel.py、app_panel.py、api_server.py 委托/成交读出面 | — | signal（登记） |
| ⑥数据字段 | data_refs=DS-150/DS-082/DS-008（Tick/快照）；执行侧产物=execution_report（execution_report_producer.py）→ 喂 ENV-15 三账（其 unwired 缺口见 env_15 簿） | — | signal |

## §2 挖干自评

- **三扫收敛?** 收敛。代码轮证实 ex_core 实现密度全场最高（40+ 件+QMT 双桥测试），消费方轮新增 compliance/risk_layer 两处后归零。
- **未挖长尾**：(a) daban_* 八件族逐件的触发条件矩阵；(b) order_manager 九态迁移完整性对图注的逐态核对；(c) execution_quality_scorer 回写 L4-06 选型的闭环证据链。
- **🌑不可得**：①L4-13 三账对账的运行痕迹（下游 ENV-15 全链 unwired，本层产物落没落表无证据）；②真实柜台（QMT 文件桥之外）的实盘打卡（sim 之外不可得）。

## §3 挖后自审闸三态裁定

**挂起排期（主体）+ 2 条施工令候选登记**

- 理由：实现与测试密度虽高，但 14/16 全 proposed、无一 verified，且执行层激活依赖上游 L3 候选与 F-C2-01 净指令两源（均在挂起链上）；单独激活执行层=空转风险。真正可先行的是两个不依赖上游的收尾切口，登记为施工令候选：①L4-13 three_way_reconciliation 专测补齐+与 ENV-15 三账链合流施工（对账是独立收口）；②execution_report→对账表落地接线（ENV-15 全链最薄缺口的输入端）。
- 解锁条件：ENV-14 组合净指令源激活（sim 腿）+ Owner production 门位 + QMT 桥实盘演练窗（💰/🧪 门位归 Owner）。
- C-L4 币圈=not_built 外域封存。

## §4 挖矿日志

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| 1 | 图字段轮：16 节点切片+全图 critical=11 复核（骨架"集中带"口径勘误） | signal | critical 名单：L9×5/L1×2/L4-09/P2-01/P2-03/X-S2-01 |
| 2 | 代码轮：ex_core/ex_sor 家族盘点+trade 测试目录核验 | signal | 14/16 有码零失踪；three_way 专测已查无=缺口 |
| 3 | 消费方轮：order_manager/live_strategy_adapter/day-cycle 反查 | signal | 日循环 live_strategy_adapter 接线三处；compliance/risk_layer 消费锚 |
