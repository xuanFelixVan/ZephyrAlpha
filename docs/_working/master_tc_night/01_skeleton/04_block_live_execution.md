---
created: "2026-10-07"
ttl: task_bound
title: "总包夜战 W1·业务块子册：实盘执行（27 环节×子模块×上下游×本夜卡）"
session: st-mastertc-mine
---

# 0x_block：实盘执行（D 段交易决策消费(F37-F52)+E 段执行基建(F53-F58)+F 段风控合规(F59-F63)）

> 环节行/职责/上下游/模块锚点全部复用 `docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md`（F01-F122）与 `docs/_working/fullconnect_campaign/00_skeleton/00_skeleton_verified.md`（F123-F132 定版新增）；状态轴复用 `docs/_working/night_sweep_20260929/00_skeleton_nightsweep.md`。本册只做块视图组装+本夜卡挂接，不重挖、不改真源。

## 一、环节清单（27 环节）

| 环节 | 名称 | 段 | 状态轴 | 基态 | 上游（谁供料）| 下游（谁消费）| 核心模块锚点 | 本夜卡 |
|---|---|---|---|---|---|---|---|---|
| F037 | L0 盘前作战计划 | B | 已通 | built | F33/F50 | F38-F41 | TDM-E-L0-01..04；src/zephyr/plan_engine/daily_warroom_pipeline.py 等 4 件 | — |
| F038 | L1 大盘总闸+六传感器 | B | 已通 | built | A 段行情 | F39-F41 | TDM-E-L1-S0..S5+AGG；src/zephyr/regime/core/regime_detector.py、anchored_state_mac | C445(L10) |
| F039 | L2 板块选择 | B | 已通 | built | F38 | F40/F41 | TDM-E-L2-*；src/zephyr/signal_ashare/sector/ 全族 | — |
| F040 | L3 个股选择 | B | 已通 | built | F39 | F41 | TDM-E-L3-*；signal_fundamental/selection_funnel.py、negative_veto.py 等 | — |
| F041 | L4 买卖点与执行 | B | 开口 | built | F40 | F53-F58 | TDM-E-L4-*；src/zephyr/ex_core/、ex_sor/ | — |
| F042 | P1 持仓体检 | B | 开口 | built | F57 对账 | F43/F45 | TDM-P-P1-*；src/zephyr/position/core/ 全族 | — |
| F043 | P2 做T与加减仓 | B | 开口 | built | F42 | F44/F46 | TDM-P-P2-*；sell_decision/core/t_trade_coordinator.py、position/core/rebalance_eng | C205(L7) |
| F044 | P3 加仓决策 | B | 已通 | built | F42 | F41 | TDM-P-P3-*；position/core/pyramiding_rules.py、position_sizing_engine.py | — |
| F045 | S1 卖出信号收集评分 | B | 开口 | built | F42/F38 | F46 | TDM-X-S1-*；src/zephyr/sell_decision/core/sell_signal_* | — |
| F046 | S2 离场执行 | B | 开口 | built | F45 | F53-F57 | TDM-X-S2-*；sell_decision/core/sell_execution_planner.py、ex_sor/core/sell_session | — |
| F047 | R1 应急保命 | B | 开口 | built | F59 回撤 | 全流 | TDM-X-R1-*；security/access_control/kill_switch.py、risk/core/drawdown_state_machi | — |
| F048 | C1 预算切分 | B | 已通 | built | F27/F71 | F49 | TDM-F-C1；src/zephyr/pf_alloc/core/multi_strategy_capital_allocator.py | — |
| F049 | C2 组合聚合 | B | 已通 | built | F48 | F50 | TDM-F-C2-*；position/core/firm_risk_aggregator.py、correlation_regime_monitor.py | — |
| F050 | C3 绩效归因反馈 | B | 已通 | built | F49/F28 | F37/F21 回灌 | TDM-F-C3-*；pf_core/core/performance_attribution_engine.py、factor/governance/life | — |
| F051 | 币圈决策骨架 | B | 开口 | missing | — | — | TDM-C-L1..L4（module_ref 全空） | C267(L8) |
| F052 | 验证方法学与决策算法库 | B | 已通 | built | — | F23/F35/F66 | REG-VALM-001（validation_method_registry.yaml）；REG-DAL-001（decision_algo_registry | C247(L4)、C251(L7) |
| F053 | 订单生命周期与预检 | E | 开口 | built | F41/F46 | F56/F57 | src/zephyr/ex_core/order_manager.py、pre_execution_checker.py、fill_handler.py、pri | C46(L6)、C103(L10) |
| F054 | 打板执行族 | E | 已通 | built | F41 | F53 | src/zephyr/ex_core/daban_*.py | — |
| F055 | 执行算法路由 SOR | E | 已通 | built | F41/F46 | F53 | src/zephyr/ex_sor/core/algo_execution_selector.py、broker_adapter_manager.py | C202(L2)、C81(L10) |
| F056 | QMT/miniQMT 桥 | E | 等Owner | built | F53 | 券商→F57 | src/zephyr/ex_core/adapters/miniqmt_broker.py、qmt_trading_session.py、broker_link | C63(L10) |
| F057 | 结算对账与三方核对 | E | 开口 | built | F56 | F42/F63 | src/zephyr/trading/settlement_reconciliation.py、three_way_reconciliation.py；ex_c | C299(L5)、C107(L7) |
| F058 | 执行成本反馈 | E | 开口 | partial | F57 | F55/F28 | src/zephyr/ex_sor/services/execution_quality_scorer.py（TDM-E-L4-14） | — |
| F059 | 风控限额与止损引擎 | F | 已通 | built | REG-RLM-001 | F47/F41 | src/zephyr/risk/（risk_manager.py、atr_stop_engine.py、ashare_stop_loss_engine.py） | C189(L9) |
| F060 | 回撤状态机与熔断 | F | 已通 | built | F63 NAV | F47 | src/zephyr/risk/core/drawdown_state_machine.py、drawdown_liquidation_guard.py、dra | C82(L10) |
| F061 | KillSwitch 三实例族 | F | 已通 | built | F47/F59 | 全交易面 | trading/trading_contracts/risk/trading_kill_switch.py；infrastructure/capacity_as | — |
| F062 | 合规门与程序化交易报告 | F | 等Owner | built | REG-CMP-REPORT-001 | F53 拒单 | src/zephyr/compliance/；compliance_report_registry.yaml（broker_ack 人工回填） | C287(L10) |
| F063 | 仓位管理与对账 | F | 已通 | built | F57 | F42/F60 | src/zephyr/position/core/position_state_machine.py、position_reconciler.py、live_n | — |

## 二、块内数据流与上下游（谁喂谁、谁消费谁——真源 DAG 摘录）

### B 段·策略供给链＝策略工厂（F037-F052）

- **F037 L0 盘前作战计划**：计划生成/偏离监控/收盘复盘明日边界/盘中滚动预测。上游=F33/F50；下游=F38-F41。本夜无卡
- **F038 L1 大盘总闸+六传感器**：指数/内部结构/赚钱效应/波动率/宏观/日级六路→7 态状态机判定。上游=A 段行情；下游=F39-F41。本夜卡：C445
- **F039 L2 板块选择**：强度综合/轮动 RRG/调整周期/水温响应/传导/回踩/催化/比价 10 组 30 节点。上游=F38；下游=F40/F41。本夜无卡
- **F040 L3 个股选择**：Universe→九阶段选票→双池评分→负面否决→顺位→环境开关→候选池→可交易预检。上游=F39；下游=F41。本夜无卡
- **F041 L4 买卖点与执行**：分批/时序/价格锚/资金分配/打板/SOR/条件单/订单生命周期/容灾对账 15 节点。上游=F40；下游=F53-F58。本夜无卡（开口，见总表 §五建议）
- **F042 P1 持仓体检**：对账快照/分级监控/买入逻辑存活/风险否决/漂移/动作清单 6 节点。上游=F57 对账；下游=F43/F45。本夜无卡（开口，见总表 §五建议）
- **F043 P2 做T与加减仓**：做T 资格/调度/闭环+减仓再平衡 4 节点。上游=F42；下游=F44/F46。本夜卡：C205
- **F044 P3 加仓决策**：资格门/金字塔规则/量级风险核算/时点执行 4 节点。上游=F42；下游=F41。本夜无卡
- **F045 S1 卖出信号收集评分**：六桶分类/止损族/止盈族/破位退潮/融合紧迫度/强制清仓绕过 6 节点。上游=F42/F38；下游=F46。本夜无卡（开口，见总表 §五建议）
- **F046 S2 离场执行**：方式路由/T+1 涨跌停约束/时段路由/条件单/分批止盈/闭环效率 6 节点。上游=F45；下游=F53-F57。本夜无卡（开口，见总表 §五建议）
- **F047 R1 应急保命**：熔断分级/熔断期减仓处置/护盘白名单（横切全流）。上游=F59 回撤；下游=全流。本夜无卡（开口，见总表 §五建议）
- **F048 C1 预算切分**：多策略资金预算切分。上游=F27/F71；下游=F49。本夜无卡
- **F049 C2 组合聚合**：目标聚合净额轧平/约束栈/相关性聚类/budget 三级升级 4 节点。上游=F48；下游=F50。本夜无卡
- **F050 C3 绩效归因反馈**：多维归因/升降级退役评审/sleeve 调权/参数校准/信号健康 5 节点。上游=F49/F28；下游=F37/F21 回灌。本夜无卡
- **F051 币圈决策骨架**：TDM-C-L1..L4 四节点（同 schema 第二实例）。上游=—；下游=—。本夜卡：C267
- **F052 验证方法学与决策算法库**：节点级"怎么算对错"五类验证方法+27 条 DAL 决策算法。上游=—；下游=F23/F35/F66。本夜卡：C247、C251

### E 段·执行基建链（F053-F058）

- **F053 订单生命周期与预检**：订单状态机/订单级预检/部分成交撤改/价格笼子硬约束。上游=F41/F46；下游=F56/F57。本夜卡：C46、C103
- **F054 打板执行族**：daban 六件套（执行/退出/瞬时熔断/载荷/监控/信号决策）。上游=F41；下游=F53。本夜无卡
- **F055 执行算法路由 SOR**：智能拆单/算法选择/场所选择/卖出时段路由。上游=F41/F46；下游=F53。本夜卡：C202、C81
- **F056 QMT/miniQMT 桥**：券商通道文件桥 broker/行情/交易会话/链路探针。上游=F53；下游=券商→F57。本夜卡：C63
- **F057 结算对账与三方核对**：结算对账/三方核对/盘后管线/EOD 四步对账。上游=F56；下游=F42/F63。本夜卡：C299、C107
- **F058 执行成本反馈**：执行质量评分→选型回写（G4 增长批闭环）。上游=F57；下游=F55/F28。本夜无卡（开口，见总表 §五建议）

### F 段·风控合规链（F059-F063）

- **F059 风控限额与止损引擎**：risk_limit 117 条九类+ATR 止损/持仓风控。上游=REG-RLM-001；下游=F47/F41。本夜卡：C189
- **F060 回撤状态机与熔断**：回撤分级状态机+清算守卫+券商端止损双保险。上游=F63 NAV；下游=F47。本夜卡：C82
- **F061 KillSwitch 三实例族**：交易级/容量级/回滚级 kill switch+状态存储。上游=F47/F59；下游=全交易面。本夜无卡
- **F062 合规门与程序化交易报告**：先报告后交易铁律 ReportGate C-002 拒单+硬边界 FeatureGate。上游=REG-CMP-REPORT-001；下游=F53 拒单。本夜卡：C287
- **F063 仓位管理与对账**：持仓状态机/对账/NAV 记录/仓位漂移。上游=F57；下游=F42/F60。本夜无卡

## 三、本夜涉及卡（15 张，去重按主挂接）

| 卡号 | 车道 | 自审闸预判 | 卡面摘要（canonical）| night_sweep 机判交叉 |
|---|---|---|---|---|
| C445 | L10 | **GREEN** | 补-1 判不出市场相位时限价单拒不拒（C5，前置相位判别器） | — |
| C205 | L7 | **GREEN** | 做T全量算 271 批（自称 3/271≈66h） | — |
| C267 | L8 | **WAIT** | 退役批（空壳表8张/F51币圈/F130 ml_serve/六个0字节死库归档后删） | 123、130、132、51 |
| C247 | L4 | **GREEN** | W-176业界对表四家注记并入W-102 | — |
| C251 | L7 | **GREEN** | dossier_academic建议采纳汇总（D1统计纪律/Lin2021/Marshall2006） | 20、22 |
| C46 | L6 | **GREEN** | 二期战役序列整体未开工（F53 Saga/F04 清洗四引擎/F73/F75/F92/F30/F05-F06+00_workorders §四 F42 体检编排/F43 做T/F45 S1 扫描/F4 | 30、4、42、43、45、46、47、5、53、56、6、73、74、75、92 |
| C103 | L10 | **GREEN** | OrderFileStore 归档语义未裁 | — |
| C202 | L2 | **GREEN** | 文件群10 双接线 5 件（src/zephyr/ex_sor 等） | 41 |
| C81 | L10 | **GREEN** | L07-C03 执行算法层收口裁定（XS-011 vs EX-062） | — |
| C63 | L10 | **WAIT** | TRD-A10 两步走（模拟换版即做=工程面就绪；实盘拒单启用=Owner 亲手+30 交易日窗；99 #29） | 56 |
| C299 | L5 | **WAIT** | R5 三处真源收敛（reconciliation_differences/consensus/score） | — |
| C107 | L7 | **GREEN** | M7 实盘执行链 F57 恒空总根=Fill 事实无生产写者→单一写者接通（半场） | 57 |
| C189 | L9 | **GREEN** | P1-2 L08 外部对表 5 项（熔断双签/Grossman-Zhou/Amihud+VPIN/Riskfolio-Lib/Agent行为熔断） | — |
| C82 | L10 | **GREEN** | L08-C03 MOD-RK-049 状态机三选一（接线/收编/退役） | — |
| C287 | L10 | **WAIT** | 实盘准入live O-2~O-9（等模拟盘绿天数积累） | 62 |

## 四、处方指针（复用既有工单，不新开处方）

- 挖矿处方卷=docs/_working/fullconnect_campaign/ 各域 per-F 卷（总表夜战骨架处方指针列）；施工序列=docs/_working/fullconnect_campaign/00_workorders.md（S1-S5+§四下一战役）；分诊六态=docs/_working/final_delivery_campaign/workorders_{governance,commit_clean,data_exam_factory,docs_misc}.md。
- 本块开口环节中已有工单无卡者（如 F115'R1-R3 最薄一刀'）按总表 §五建议补卡挂接，工单不重写。
- Owner 门位卡（等Owner 状态轴/§五 保留）本夜只登记不施工；清单见总表 §四 WAIT 行。

## 五、复核命令

```bash
# 本块环节数与总表 §三 行一致；卡数与总表 §四 该块行数一致（主挂接口径）
grep -c '^| F' docs/_working/master_tc_night/01_skeleton/04_block_live_execution.md
```
