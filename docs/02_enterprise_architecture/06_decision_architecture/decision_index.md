# 决策流图（decisiongraph）索引

> 生成时间: 2026-07-06T18:27:25
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)

## 概述

决策流图（decisiongraph）是与依赖图（depgraph）、数据流图（dataflowgraph）正交的第三维度全景图。
- depgraph 表达"谁依赖谁"（模块依赖，静态）
- dataflowgraph 表达"数据从哪流到哪"（数据流向，动态）
- decisiongraph 表达"决策如何产生"（决策流，动态）
- 三图通过 `module_id` 关联：决策节点 → 实现模块（depgraph）→ 数据流作业（dataflowgraph）

## 统计

| 类型 | 数量 |
|------|------|
| Track（轨） | 4 |
| Layer（层） | 10 |
| Node（节点） | 214 |
| Edge（边） | 0 |
| 运营态 Layer（design_maturity=production） | 3 |
| 设计态 Layer（design_maturity=design） | 7 |
| 原型态 Layer（design_maturity=prototype） | 0 |
| 运营态 Node（design_maturity=production） | 0 |
| 设计态 Node（design_maturity=design） | 214 |

> **设计态 vs 运营态**：`design_maturity` 字段区分——`design`=蓝图规划（代码未写），`production`=实际代码已实现稳定运行，`prototype`=原型验证中。对标 depgraph 的设计态/运营态机制。

## Mermaid 图表

> 以下图表通过 Mermaid 代码块内嵌，可直接在 Markdown 查看器中渲染。

### 全景图（设计态 + 运营态合并，标签标注 [design]/[production]）

```mermaid
flowchart TD
    subgraph track_model_driven["模型驱动轨（Model-Driven Track）"]
        LL0["[production]L0: 数据接入与预处理层<br/>功能: miniQMT + iFind + t…<br/>freq: tick<br/>build: stable"]:::bsStable
        LL1["[production]L1: 因子计算层<br/>功能: 因子工厂全生命周期管理 → 盘前全量/…<br/>freq: daily<br/>build: stable"]:::bsStable
        LL2A["[design]L2A: 信号层<br/>功能: 信号工厂 → 多策略投票 → 收益率条…<br/>freq: daily<br/>build: planned"]:::bsPlanned
        N1("[design]sell_decision: 卖出决策域入口 Sell Decision Entry<br/>path: decision/sell/sell_00"):::bsPlanned
        LL2A --- N1
        N2("[design]sell_decision: 止盈信号 Take-Profit Signal<br/>path: decision/sell/sell_01"):::bsPlanned
        LL2A --- N2
        N3("[design]sell_decision: 止损信号 Stop-Loss Signal<br/>path: decision/sell/sell_02"):::bsPlanned
        LL2A --- N3
        N4("[design]sell_decision: 移动止损 Trailing Stop<br/>path: decision/sell/sell_03"):::bsPlanned
        LL2A --- N4
        N5("[design]sell_decision: 主力出货信号 Main Force Distribution Signal<br/>path: decision/sell/sell_04"):::bsPlanned
        LL2A --- N5
        N6("[design]sell_decision: 量价背离卖出 Volume-Price Divergence Sell<br/>path: decision/sell/sell_05"):::bsPlanned
        LL2A --- N6
        N7("[design]sell_decision: 突破关键位卖出 Key-Level Breakdown Sell<br/>path: decision/sell/sell_06"):::bsPlanned
        LL2A --- N7
        N8("[design]sell_decision: Watch List 实时卖出 Watch List Realtime Sell<br/>path: decision/sell/sell_07"):::bsPlanned
        LL2A --- N8
        N9("[design]sell_decision: Monitor List 定期扫描 Monitor List Periodic Scan<br/>path: decision/sell/sell_08"):::bsPlanned
        LL2A --- N9
        N10("[design]sell_decision: 卖出信号融合仲裁 Sell Signal Fusion Arbiter<br/>path: decision/sell/sell_09"):::bsPlanned
        LL2A --- N10
        N11("[design]sell_decision: 买卖冲突仲裁 Buy-Sell Conflict Arbiter<br/>path: decision/sell/sell_10"):::bsPlanned
        LL2A --- N11
        N12("[design]sell_decision: 部分卖出vs全部清仓决策 Partial vs Full Sell Decision<br/>path: decision/sell/sell_11"):::bsPlanned
        LL2A --- N12
        N13("[design]sell_decision: D-S证据理论融合 D-S Evidence Theory Fusion<br/>path: decision/sell/sell_12"):::bsPlanned
        LL2A --- N13
        N14("[design]sell_decision: 做T决策协调 T-Trade Coordinator<br/>path: decision/sell/sell_13"):::bsPlanned
        LL2A --- N14
        N15("[design]sell_decision: 黑天鹅强制卖出 Black Swan Forced Sell<br/>path: decision/sell/sell_14"):::bsPlanned
        LL2A --- N15
        N16("[design]sell_decision: Gap开盘决策框架 Gap Opening Decision Framework<br/>path: decision/sell/sell_15"):::bsPlanned
        LL2A --- N16
        N17("[design]sell_decision: 强制清仓信号 Forced Liquidation Signal<br/>path: decision/sell/sell_16"):::bsPlanned
        LL2A --- N17
        N18("[design]sell_decision: 卖出降级模式 Sell Degradation Mode<br/>path: decision/sell/sell_17"):::bsPlanned
        LL2A --- N18
        N19("[design]sell_decision: 卖出决策闭环优化 Sell Decision Closed-Loop<br/>path: decision/sell/sell_18"):::bsPlanned
        LL2A --- N19
        N141("[design]signal: 市场仿真器 Market Simulator<br/>path: decision/simulation/sim_01"):::bsPlanned
        LL2A --- N141
        N142("[design]signal: 策略仿真器 Strategy Simulator<br/>path: decision/simulation/sim_02"):::bsPlanned
        LL2A --- N142
        N143("[design]signal: 风控仿真器 Risk Simulator<br/>path: decision/simulation/sim_03"):::bsPlanned
        LL2A --- N143
        N144("[design]signal: 压力测试引擎 Stress Test Engine<br/>path: decision/simulation/sim_04"):::bsPlanned
        LL2A --- N144
        N145("[design]signal: 场景生成器 Scenario Generator<br/>path: decision/simulation/sim_05"):::bsPlanned
        LL2A --- N145
        N146("[design]signal: 历史重放引擎 History Replay Engine<br/>path: decision/simulation/sim_07"):::bsPlanned
        LL2A --- N146
        N147("[design]signal: 极端事件仿真 Extreme Event Simulator<br/>path: decision/simulation/sim_10"):::bsPlanned
        LL2A --- N147
        N148("[design]signal: 依赖图数字孪生 Dependency Graph Digital Twin<br/>path: decision/simulation/sim_13"):::bsPlanned
        LL2A --- N148
        N149("[design]signal: 混沌实验自动生成 Chaos Experiment Auto-Generator<br/>path: decision/simulation/sim_15"):::bsPlanned
        LL2A --- N149
        N150("[design]signal: 回测过拟合检测器 Backtest Overfitting Detector<br/>path: decision/simulation/sim_18"):::bsPlanned
        LL2A --- N150
        N151("[design]signal: Walk-Forward分析器 Walk-Forward Analyzer<br/>path: decision/simulation/sim_19"):::bsPlanned
        LL2A --- N151
        N152("[design]signal: 参数鲁棒性测试器 Parameter Robustness Tester<br/>path: decision/simulation/sim_21"):::bsPlanned
        LL2A --- N152
        N153("[design]signal: 验证自动化流水线 Validation Automation Pipeline<br/>path: decision/simulation/sim_33"):::bsPlanned
        LL2A --- N153
        N154("[design]signal: 自动化过拟合门禁 Automated Overfitting Detector Gate<br/>path: decision/simulation/sim_56"):::bsPlanned
        LL2A --- N154
        N155("[design]signal: 3阶段决策门控 IS→WFA→OOS 3-Stage Decision Gate<br/>path: decision/simulation/sim_g1"):::bsPlanned
        LL2A --- N155
        N177("[design]signal: Synthesizer 信号合成+权重分配<br/>path: decision/signal/sg_01"):::bsPlanned
        LL2A --- N177
        N178("[design]signal: Signal Priority Router 信号优先级路由<br/>path: decision/signal/sg_02"):::bsPlanned
        LL2A --- N178
        N179("[design]signal: LLM Strategy Agent LLM策略Agent<br/>path: decision/signal/sg_03"):::bsPlanned
        LL2A --- N179
        N180("[design]signal: Signal Tail Risk Protector 信号尾部风险保护<br/>path: decision/signal/sg_04"):::bsPlanned
        LL2A --- N180
        N181("[design]signal: A-Share Plan Conformity Evaluator A股计划吻合度评估<br/>path: decision/signal/sg_05"):::bsPlanned
        LL2A --- N181
        N182("[design]signal: A-Share Emergency Opportunity Evaluator A股应急机会评估<br/>path: decision/signal/sg_06"):::bsPlanned
        LL2A --- N182
        N183("[design]signal: A-Share Capital-Force Conflict Arbiter 主力游资冲突仲裁<br/>path: decision/signal/sg_07"):::bsPlanned
        LL2A --- N183
        N184("[design]signal: Regime Special Override Priority Manager Regime特殊覆盖优先级<br/>path: decision/signal/sg_08"):::bsPlanned
        LL2A --- N184
        N185("[design]signal: Risk-Signal Interaction Sequencer 风控-信号交互时序<br/>path: decision/signal/sg_09"):::bsPlanned
        LL2A --- N185
        N186("[design]signal: 36环节决策框架实现器 36-Step Decision Framework<br/>path: decision/signal/sg_10"):::bsPlanned
        LL2A --- N186
        N187("[design]signal: 策略替换与淘汰决策器 Strategy Replacement Decision<br/>path: decision/signal/sg_11"):::bsPlanned
        LL2A --- N187
        N188("[design]signal: 信号冲突解决 Signal Conflict Resolution<br/>path: decision/signal/sg_12"):::bsPlanned
        LL2A --- N188
        N189("[design]signal: 信号融合模块 Signal Fusion Module<br/>path: decision/signal/sg_13"):::bsPlanned
        LL2A --- N189
        N190("[design]signal: 末位淘汰 IC-Based Factor Replacement<br/>path: decision/factor/fc_01"):::bsPlanned
        LL2A --- N190
        N191("[design]signal: 批量裁剪 Batch Factor Pruning<br/>path: decision/factor/fc_02"):::bsPlanned
        LL2A --- N191
        N192("[design]signal: Multi-Source Priority Router 多源优先级路由<br/>path: decision/data/dt_01"):::bsPlanned
        LL2A --- N192
        N193("[design]signal: Cross-Source Reconciler 多源对账<br/>path: decision/data/dt_02"):::bsPlanned
        LL2A --- N193
        N194("[design]signal: Multi-Timeframe Fusion 跨频率融合<br/>path: decision/data/dt_03"):::bsPlanned
        LL2A --- N194
        N200("[design]signal: Approval Workflow UI 审批流程界面<br/>path: decision/frontend/fe_12"):::bsPlanned
        LL2A --- N200
        N201("[design]signal: Notification Router 通知路由<br/>path: decision/frontend/fe_13"):::bsPlanned
        LL2A --- N201
        N202("[design]signal: Real-time Dashboard 实时仪表盘<br/>path: decision/frontend/fe_09"):::bsPlanned
        LL2A --- N202
        N203("[design]signal: 决策树可视化器 ADR Decision Tree Visualizer<br/>path: decision/frontend/fe_m76"):::bsPlanned
        LL2A --- N203
        N204("[design]signal: 4级风控决策 APPROVE/REDUCE/REJECT/FLATTEN<br/>path: decision/research/rs_01"):::bsPlanned
        LL2A --- N204
        N205("[design]signal: 3阶段决策门控 IS→WFA→OOS 3-Stage Decision Gate<br/>path: decision/research/rs_02"):::bsPlanned
        LL2A --- N205
        N206("[design]signal: Decision Audit Trail R-102 Decision Audit Trail<br/>path: decision/research/rs_03"):::bsPlanned
        LL2A --- N206
        N209("[design]signal: 服务降级管理 Service Degradation Manager<br/>path: decision/frontend/fe_14"):::bsPlanned
        LL2A --- N209
        N210("[design]signal: 跨域运维事件链追踪 Cross-Domain Event Chain<br/>path: decision/frontend/fe_15"):::bsPlanned
        LL2A --- N210
        N211("[design]signal: 策略可解释性报告器 Strategy Explainability Reporter<br/>path: decision/research/rs_04"):::bsPlanned
        LL2A --- N211
        N212("[design]signal: A股绩效审计与优化触发器 A-Share Performance Audit<br/>path: decision/research/rs_05"):::bsPlanned
        LL2A --- N212
        N213("[design]signal: 异常决策自检 Anomaly Decision Self-Check<br/>path: decision/research/rs_06"):::bsPlanned
        LL2A --- N213
        N214("[design]signal: Knowledge Feedback Loop 知识反馈循环<br/>path: decision/research/rs_07"):::bsPlanned
        LL2A --- N214
        LL2B["[design]L2B: 主力行为层<br/>功能: 六阶段识别 + 自迭代推演 + 庄家专…<br/>freq: daily<br/>build: planned"]:::bsPlanned
        LL2C["[design]L2C: 市场状态与大盘预测层<br/>功能: 3×3矩阵 + 2叠加态 + 三层大盘…<br/>freq: daily<br/>build: planned"]:::bsPlanned
        LL2D["[design]L2D: 知识图谱与因果推演层<br/>功能: 六类知识图谱 → 事件影响链分析 → …<br/>freq: daily<br/>build: planned"]:::bsPlanned
        LL3["[design]L3: 策略组合层<br/>功能: 多策略信号合成 → 资本分配 → 元策…<br/>freq: daily<br/>build: planned"]:::bsPlanned
        N20("[design]portfolio_target: 组合核心引擎 Portfolio Core Engine<br/>path: decision/pf_core/pc_01"):::bsPlanned
        LL3 --- N20
        N21("[design]portfolio_target: 半Kelly硬上限 Half-Kelly Hard Cap<br/>path: decision/pf_core/pc_02"):::bsPlanned
        LL3 --- N21
        N22("[design]portfolio_target: 风险预算 Risk Budget<br/>path: decision/pf_core/pc_03"):::bsPlanned
        LL3 --- N22
        N23("[design]portfolio_target: 再平衡决策 Rebalance Decision<br/>path: decision/pf_core/pc_04"):::bsPlanned
        LL3 --- N23
        N24("[design]portfolio_target: 仲裁优先级体系 Arbitration Priority<br/>path: decision/pf_core/pc_05"):::bsPlanned
        LL3 --- N24
        N25("[design]portfolio_target: 多策略共振融合 Strategy Convergence Fusion<br/>path: decision/pf_core/pc_06"):::bsPlanned
        LL3 --- N25
        N26("[design]portfolio_target: 因子直通裁决 Factor Bypass Arbitration<br/>path: decision/pf_core/pc_07"):::bsPlanned
        LL3 --- N26
        N27("[design]portfolio_target: 元策略路由 Meta-Strategy Router<br/>path: decision/pf_core/pc_08"):::bsPlanned
        LL3 --- N27
        N28("[design]portfolio_target: 组合优化 Portfolio Optimization<br/>path: decision/pf_core/pc_09"):::bsPlanned
        LL3 --- N28
        N29("[design]portfolio_target: 资本分配 Capital Allocation<br/>path: decision/pf_core/pc_10"):::bsPlanned
        LL3 --- N29
        N30("[design]portfolio_target: 决策编排器 Decision Orchestrator<br/>path: decision/pf_core/pc_11"):::bsPlanned
        LL3 --- N30
        N31("[design]portfolio_target: 四轨融合器 Multi-Track Fusion<br/>path: decision/pf_core/pc_12"):::bsPlanned
        LL3 --- N31
        N32("[design]portfolio_target: 策略分配 Strategy Allocation<br/>path: decision/pf_alloc/pa_01"):::bsPlanned
        LL3 --- N32
        N33("[design]portfolio_target: 风险平价 Risk Parity<br/>path: decision/pf_alloc/pa_02"):::bsPlanned
        LL3 --- N33
        N34("[design]portfolio_target: 动态权重 Dynamic Weighting<br/>path: decision/pf_alloc/pa_03"):::bsPlanned
        LL3 --- N34
        N35("[design]portfolio_target: 策略权重再平衡 Strategy Weight Rebalance<br/>path: decision/pf_alloc/pa_04"):::bsPlanned
        LL3 --- N35
        N36("[design]portfolio_target: 多策略共识 Multi-Strategy Consensus<br/>path: decision/pf_alloc/pa_05"):::bsPlanned
        LL3 --- N36
        N37("[design]portfolio_target: 元策略选择 Meta-Strategy Selection<br/>path: decision/pf_alloc/pa_06"):::bsPlanned
        LL3 --- N37
        N38("[design]portfolio_target: 仓位唯一裁决中心 C-047 Position Sole Arbiter<br/>path: decision/position/pos_01"):::bsPlanned
        LL3 --- N38
        N39("[design]portfolio_target: 持仓状态机 Position State Machine<br/>path: decision/position/pos_02"):::bsPlanned
        LL3 --- N39
        N40("[design]portfolio_target: 仓位漂移监控 Position Drift Monitor<br/>path: decision/position/pos_03"):::bsPlanned
        LL3 --- N40
        N41("[design]portfolio_target: Kelly仓位决策 Kelly Position Decision<br/>path: decision/position/pos_04"):::bsPlanned
        LL3 --- N41
        N42("[design]portfolio_target: 风险配额 Risk Quota<br/>path: decision/position/pos_05"):::bsPlanned
        LL3 --- N42
        N43("[design]portfolio_target: 11种市场状态→仓位上限 Market State Position Cap<br/>path: decision/position/pos_06"):::bsPlanned
        LL3 --- N43
        N44("[design]portfolio_target: 组合层决策 Portfolio Layer Decision<br/>path: decision/position/pos_07"):::bsPlanned
        LL3 --- N44
        N45("[design]portfolio_target: 策略层决策 Strategy Layer Decision<br/>path: decision/position/pos_08"):::bsPlanned
        LL3 --- N45
        N46("[design]portfolio_target: 标层决策 Instrument Layer Decision<br/>path: decision/position/pos_09"):::bsPlanned
        LL3 --- N46
        N47("[design]portfolio_target: 动态层决策 Dynamic Layer Decision<br/>path: decision/position/pos_10"):::bsPlanned
        LL3 --- N47
        N48("[design]portfolio_target: 再平衡触发 Rebalance Trigger<br/>path: decision/position/pos_11"):::bsPlanned
        LL3 --- N48
        N49("[design]portfolio_target: 仓位上限硬约束 Position Cap Hard Constraint<br/>path: decision/position/pos_12"):::bsPlanned
        LL3 --- N49
        N50("[design]portfolio_target: REDUCING→EXITING状态转换 REDUCING to EXITING<br/>path: decision/position/pos_13"):::bsPlanned
        LL3 --- N50
        N51("[design]portfolio_target: 风险预算→Kelly决策 Risk Budget to Kelly<br/>path: decision/position/pos_14"):::bsPlanned
        LL3 --- N51
        N52("[design]portfolio_target: 半Kelly硬上限 Half-Kelly Hard Cap<br/>path: decision/position/pos_15"):::bsPlanned
        LL3 --- N52
        N53("[design]portfolio_target: 仓位降级 Position Degradation<br/>path: decision/position/pos_16"):::bsPlanned
        LL3 --- N53
        N54("[design]portfolio_target: 持仓状态→卖出阈值 Position State to Sell Threshold<br/>path: decision/position/pos_17"):::bsPlanned
        LL3 --- N54
        N55("[design]portfolio_target: 仓位四轨决策 Position Four-Track Decision<br/>path: decision/position/pos_18"):::bsPlanned
        LL3 --- N55
        N56("[design]portfolio_target: 仓位裁决→执行 Position Arbitration to Execution<br/>path: decision/position/pos_19"):::bsPlanned
        LL3 --- N56
        N59("[design]order: 50ms SLA Fail-Closed 50ms SLA Fail-Closed<br/>path: decision/ex_core/ex_03"):::bsPlanned
        LL3 --- N59
        N60("[design]order: Saga编排式事务 Saga Orchestrated Transaction<br/>path: decision/ex_core/ex_04"):::bsPlanned
        LL3 --- N60
        N61("[design]order: 风控检查 Risk Check<br/>path: decision/ex_core/ex_05"):::bsPlanned
        LL3 --- N61
        N62("[design]order: 信号确认 Signal Confirmation<br/>path: decision/ex_core/ex_06"):::bsPlanned
        LL3 --- N62
        N63("[design]order: 下单提交 Order Submit<br/>path: decision/ex_core/ex_07"):::bsPlanned
        LL3 --- N63
        N64("[design]order: 成交确认 Fill Confirmation<br/>path: decision/ex_core/ex_08"):::bsPlanned
        LL3 --- N64
        N65("[design]order: 持仓更新 Position Update<br/>path: decision/ex_core/ex_09"):::bsPlanned
        LL3 --- N65
        N66("[design]order: 报告生成 Report Generation<br/>path: decision/ex_core/ex_10"):::bsPlanned
        LL3 --- N66
        N71("[design]order: 流动性螺旋3阶段 Liquidity Spiral 3-Phase<br/>path: decision/ex_core/ex_15"):::bsPlanned
        LL3 --- N71
        N72("[design]order: 订单路由决策 Order Routing Decision<br/>path: decision/ex_sor/ex_16"):::bsPlanned
        LL3 --- N72
        N73("[design]order: SOR路由决策延迟 SOR Routing Latency<br/>path: decision/ex_sor/ex_17"):::bsPlanned
        LL3 --- N73
        N75("[design]order: 交易通道熔断人工恢复 Trading Channel Manual Recovery<br/>path: decision/ex_sor/ex_19"):::bsPlanned
        LL3 --- N75
        N77("[design]order: Kill-Switch四级阶梯 Kill-Switch 4-Level Cascade<br/>path: decision/ex_sor/ex_21"):::bsPlanned
        LL3 --- N77
        N78("[design]order: 熔断器矩阵 Circuit Breaker Matrix<br/>path: decision/ex_sor/ex_22"):::bsPlanned
        LL3 --- N78
        N102("[design]order: 外部订单观察者 External Order Watcher<br/>path: decision/trading/trd_01"):::bsPlanned
        LL3 --- N102
        N103("[design]order: 结算引擎 Settlement Engine<br/>path: decision/trading/trd_02"):::bsPlanned
        LL3 --- N103
        N104("[design]order: 公司行动 Corporate Action<br/>path: decision/trading/trd_03"):::bsPlanned
        LL3 --- N104
        N105("[design]order: 保证金管理 Margin Manager<br/>path: decision/trading/trd_04"):::bsPlanned
        LL3 --- N105
        N106("[design]order: 多账户 Multi-Account<br/>path: decision/trading/trd_05"):::bsPlanned
        LL3 --- N106
        N107("[design]order: 微信枢纽 WeChat Hub<br/>path: decision/trading/trd_06"):::bsPlanned
        LL3 --- N107
        N108("[design]order: C-013 4级优先级 C-013 4-Level Priority<br/>path: decision/trading/trd_07"):::bsPlanned
        LL3 --- N108
        N109("[design]order: A股交易纪律四项必做 A-Share Trading 4-Do<br/>path: decision/trading/trd_08"):::bsPlanned
        LL3 --- N109
        N110("[design]order: A股交易纪律四项严禁 A-Share Trading 4-Forbidden<br/>path: decision/trading/trd_09"):::bsPlanned
        LL3 --- N110
        N111("[design]order: 监管报送 Regulatory Reporting<br/>path: decision/trading/trd_10"):::bsPlanned
        LL3 --- N111
        N112("[design]order: 盘中即时反应决策引擎 Intraday Instant Reaction Decision Engine<br/>path: decision/trading/trd_11"):::bsPlanned
        LL3 --- N112
        N113("[design]portfolio_target: Permission Guard 七层纵深防御<br/>path: decision/aut_core/ac_01"):::bsPlanned
        LL3 --- N113
        N115("[design]portfolio_target: Self-Healing Git-native自愈<br/>path: decision/aut_core/ac_03"):::bsPlanned
        LL3 --- N115
        N116("[design]portfolio_target: Budget Enforcer 七级预算<br/>path: decision/aut_core/ac_04"):::bsPlanned
        LL3 --- N116
        N117("[design]portfolio_target: Health Monitor 9子系统监控<br/>path: decision/aut_core/ac_05"):::bsPlanned
        LL3 --- N117
        N118("[design]portfolio_target: Escalation Engine 升级引擎<br/>path: decision/aut_core/ac_06"):::bsPlanned
        LL3 --- N118
        N119("[design]portfolio_target: Rollback Engine Git-native回滚<br/>path: decision/aut_core/ac_07"):::bsPlanned
        LL3 --- N119
        N120("[design]portfolio_target: Drift Detector 39检测器<br/>path: decision/aut_core/ac_08"):::bsPlanned
        LL3 --- N120
        N121("[design]portfolio_target: Auto-Fix Engine 16修复器<br/>path: decision/aut_core/ac_09"):::bsPlanned
        LL3 --- N121
        N133("[design]portfolio_target: 编排Agent Orchestrator<br/>path: decision/aut_core/ac_21"):::bsPlanned
        LL3 --- N133
        N135("[design]portfolio_target: 做TAgent T0Trader<br/>path: decision/aut_core/ac_23"):::bsPlanned
        LL3 --- N135
        N136("[design]portfolio_target: 路由Agent Router<br/>path: decision/aut_core/ac_24"):::bsPlanned
        LL3 --- N136
        LL4["[production]L4: 风控层<br/>功能: Pre/Post-Trade 风控校验…<br/>freq: realtime<br/>build: stable"]:::bsStable
        N57("[design]compliance_check: Pre-Trade主链6项检查 Pre-Trade Main Chain 6 Checks<br/>path: decision/ex_core/ex_01"):::bsPlanned
        LL4 --- N57
        N58("[design]risk_check: Kill Switch 5层防御 Kill Switch 5-Layer Defense<br/>path: decision/ex_core/ex_02"):::bsPlanned
        LL4 --- N58
        N67("[design]risk_check: Kill Switch AI自动激活 Kill Switch AI Auto Trigger<br/>path: decision/ex_core/ex_11"):::bsPlanned
        LL4 --- N67
        N68("[design]risk_check: Kill Switch人工激活 Kill Switch Manual Trigger<br/>path: decision/ex_core/ex_12"):::bsPlanned
        LL4 --- N68
        N69("[design]risk_check: Kill Switch定时激活 Kill Switch Timer Trigger<br/>path: decision/ex_core/ex_13"):::bsPlanned
        LL4 --- N69
        N70("[design]risk_check: Kill Switch外部信号激活 Kill Switch External Signal<br/>path: decision/ex_core/ex_14"):::bsPlanned
        LL4 --- N70
        N74("[design]risk_check: 券商连接熔断+故障转移 Broker Circuit Breaker<br/>path: decision/ex_sor/ex_18"):::bsPlanned
        LL4 --- N74
        N76("[design]compliance_check: Pre-Trade合规检查流水线 Pre-Trade Compliance Pipeline<br/>path: decision/ex_sor/ex_20"):::bsPlanned
        LL4 --- N76
        N79("[design]compliance_check: 行为准入门禁 Behavioral Admission Gateway<br/>path: decision/ex_sor/ex_23"):::bsPlanned
        LL4 --- N79
        N80("[design]risk_check: 风控熔断事件 Risk Circuit Breaker Event<br/>path: decision/risk/rk_01"):::bsPlanned
        LL4 --- N80
        N81("[design]risk_check: 三层防线 Three Defense Lines<br/>path: decision/risk/rk_02"):::bsPlanned
        LL4 --- N81
        N82("[design]risk_check: 双引擎风控 Dual Engine Risk<br/>path: decision/risk/rk_03"):::bsPlanned
        LL4 --- N82
        N83("[design]risk_check: 4级风控决策门控 4-Level Risk Decision Gate<br/>path: decision/risk/rk_04"):::bsPlanned
        LL4 --- N83
        N84("[design]risk_check: 压力测试引擎 Stress Test Engine<br/>path: decision/risk/rk_05"):::bsPlanned
        LL4 --- N84
        N85("[design]risk_check: 黑天鹅模式库 Black Swan Pattern Library<br/>path: decision/risk/rk_06"):::bsPlanned
        LL4 --- N85
        N86("[design]risk_check: 流动性危机模拟 Liquidity Crisis Simulation<br/>path: decision/risk/rk_07"):::bsPlanned
        LL4 --- N86
        N87("[design]risk_check: 反向压力测试4步法 Reverse Stress Test 4-Step<br/>path: decision/risk/rk_08"):::bsPlanned
        LL4 --- N87
        N88("[design]risk_check: 二阶效应与传染模型 Second-Order Effect Model<br/>path: decision/risk/rk_09"):::bsPlanned
        LL4 --- N88
        N89("[design]risk_check: 风控否决权 Risk Veto<br/>path: decision/risk/rk_10"):::bsPlanned
        LL4 --- N89
        N90("[design]risk_check: 风控状态 Risk State<br/>path: decision/risk/rk_11"):::bsPlanned
        LL4 --- N90
        N91("[design]risk_check: 风控参数变更审批 Risk Parameter Approval<br/>path: decision/risk/rk_12"):::bsPlanned
        LL4 --- N91
        N92("[design]risk_check: 熔断恢复确认 Circuit Breaker Recovery Confirm<br/>path: decision/risk/rk_13"):::bsPlanned
        LL4 --- N92
        N93("[design]risk_check: OBSERVING软止损观察期 OBSERVING Soft Stop<br/>path: decision/risk/rk_14"):::bsPlanned
        LL4 --- N93
        N94("[design]risk_check: 风险预算 Risk Budget<br/>path: decision/risk/rk_15"):::bsPlanned
        LL4 --- N94
        N95("[design]risk_check: VaR计算 VaR Calculation<br/>path: decision/risk/rk_16"):::bsPlanned
        LL4 --- N95
        N96("[design]risk_check: 回撤监控 Drawdown Monitor<br/>path: decision/risk/rk_17"):::bsPlanned
        LL4 --- N96
        N97("[design]risk_check: 风控信号交互时序 Risk-Signal Timing<br/>path: decision/risk/rk_18"):::bsPlanned
        LL4 --- N97
        N98("[design]risk_check: 风控事件 Risk Event<br/>path: decision/risk/rk_19"):::bsPlanned
        LL4 --- N98
        N99("[design]risk_check: FLATTEN硬编码触发 FLATTEN Hardcoded Trigger<br/>path: decision/risk/rk_20"):::bsPlanned
        LL4 --- N99
        N100("[design]risk_check: 5级风险否决引擎 5-Level Risk Veto Engine<br/>path: decision/risk/rk_21"):::bsPlanned
        LL4 --- N100
        N101("[design]risk_check: Pod级止损 Pod-Level Stop Loss<br/>path: decision/risk/rk_22"):::bsPlanned
        LL4 --- N101
        N114("[design]compliance_check: Audit Trail Merkle哈希链<br/>path: decision/aut_core/ac_02"):::bsPlanned
        LL4 --- N114
        N122("[design]compliance_check: Decision Audit Trail 决策审计<br/>path: decision/aut_core/ac_10"):::bsPlanned
        LL4 --- N122
        N123("[design]compliance_check: Kill Switch直通路径 Kill Switch Direct Path<br/>path: decision/aut_perm/ap_11"):::bsPlanned
        LL4 --- N123
        N124("[design]compliance_check: 4级自治模型 Level 0-3 Autonomy Model<br/>path: decision/aut_perm/ap_12"):::bsPlanned
        LL4 --- N124
        N125("[design]compliance_check: AI自治边界三级分类<br/>path: decision/aut_perm/ap_13"):::bsPlanned
        LL4 --- N125
        N126("[design]compliance_check: Agentic Drift 5类攻击模式<br/>path: decision/aut_perm/ap_14"):::bsPlanned
        LL4 --- N126
        N127("[design]compliance_check: 行为审计7信号 S-01~S-07<br/>path: decision/aut_perm/ap_15"):::bsPlanned
        LL4 --- N127
        N128("[design]compliance_check: ARS双轨结算模型 ARS Dual-Track Settlement<br/>path: decision/aut_perm/ap_16"):::bsPlanned
        LL4 --- N128
        N129("[design]risk_check: AI自治熔断5条件 VR-009 5 Conditions<br/>path: decision/aut_perm/ap_17"):::bsPlanned
        LL4 --- N129
        N130("[design]risk_check: L0完全人工→L4降级模式 L0 to L4 Degradation<br/>path: decision/aut_perm/ap_18"):::bsPlanned
        LL4 --- N130
        N131("[design]risk_check: 4级风控决策 APPROVE/REDUCE/REJECT/FLATTEN<br/>path: decision/aut_perm/ap_19"):::bsPlanned
        LL4 --- N131
        N132("[design]compliance_check: 人类监督四层级 L0~L3 Human Oversight<br/>path: decision/aut_perm/ap_20"):::bsPlanned
        LL4 --- N132
        N134("[design]risk_check: 风控Agent RiskManager<br/>path: decision/aut_core/ac_22"):::bsPlanned
        LL4 --- N134
        N137("[design]compliance_check: A2A检查网关策略引擎 A2A Check Gateway<br/>path: decision/aut_perm/ap_21"):::bsPlanned
        LL4 --- N137
        N138("[design]compliance_check: LLM Agent路由 级联控制器 Cascade Controller<br/>path: decision/aut_perm/ap_22"):::bsPlanned
        LL4 --- N138
        N139("[design]risk_check: 应急保命轨 Emergency Track<br/>path: decision/aut_perm/ap_23"):::bsPlanned
        LL4 --- N139
        N140("[design]compliance_check: 置信度分层决策 C-031 Confidence-Layered Decision<br/>path: decision/aut_perm/ap_24"):::bsPlanned
        LL4 --- N140
        N156("[design]compliance_check: AuditLedger 审计账本<br/>path: decision/governance/gov_001"):::bsPlanned
        LL4 --- N156
        N157("[design]compliance_check: DDDRuleEnforcer DDD铁律执行器<br/>path: decision/governance/gov_002"):::bsPlanned
        LL4 --- N157
        N158("[design]compliance_check: DecisionProvenance 决策溯源链<br/>path: decision/governance/gov_003"):::bsPlanned
        LL4 --- N158
        N159("[design]compliance_check: PhaseGateManager 阶段门禁管理<br/>path: decision/governance/gov_004"):::bsPlanned
        LL4 --- N159
        N160("[design]compliance_check: ConstitutionalGuard 宪法守卫<br/>path: decision/governance/gov_005"):::bsPlanned
        LL4 --- N160
        N161("[design]compliance_check: ComplianceAuditor 合规审计器<br/>path: decision/governance/gov_006"):::bsPlanned
        LL4 --- N161
        N162("[design]compliance_check: IncidentResponse 事件响应与升级<br/>path: decision/governance/gov_007"):::bsPlanned
        LL4 --- N162
        N163("[design]compliance_check: SystemTopologyAuditor 系统拓扑审计<br/>path: decision/governance/gov_008"):::bsPlanned
        LL4 --- N163
        N164("[design]compliance_check: 决策疲劳检测 Decision Fatigue Detection<br/>path: decision/governance/gov_009"):::bsPlanned
        LL4 --- N164
        N165("[design]compliance_check: Agent辩论机制 Agent Debate<br/>path: decision/governance/gov_010"):::bsPlanned
        LL4 --- N165
        N166("[design]compliance_check: AI Compliance Validator AI合规验证<br/>path: decision/compliance/cmp_01"):::bsPlanned
        LL4 --- N166
        N167("[design]compliance_check: 决策溯源链 Decision Provenance Chain<br/>path: decision/compliance/cmp_02"):::bsPlanned
        LL4 --- N167
        N168("[design]compliance_check: TraceCompleteness TC≥0.997<br/>path: decision/compliance/cmp_03"):::bsPlanned
        LL4 --- N168
        N169("[design]compliance_check: AI合规边界 Tier 1/2/3风险分级<br/>path: decision/compliance/cmp_04"):::bsPlanned
        LL4 --- N169
        N170("[design]compliance_check: Pre-Trade合规检查三模式 Pre-Trade 3-Mode Check<br/>path: decision/compliance/cmp_05"):::bsPlanned
        LL4 --- N170
        N171("[design]compliance_check: Kill Switch <1秒响应 Kill Switch <1s Response<br/>path: decision/compliance/cmp_06"):::bsPlanned
        LL4 --- N171
        N172("[design]compliance_check: 人类监督四层级 L0~L3 Human Oversight 4-Level<br/>path: decision/compliance/cmp_07"):::bsPlanned
        LL4 --- N172
        N173("[design]compliance_check: AI决策可追溯性 AI Decision Traceability<br/>path: decision/compliance/cmp_08"):::bsPlanned
        LL4 --- N173
        N174("[design]compliance_check: AI决策可解释性门控 AI Decision Explainability Gate<br/>path: decision/compliance/cmp_09"):::bsPlanned
        LL4 --- N174
        N175("[design]compliance_check: 监管报告 Regulatory Report<br/>path: decision/compliance/cmp_10"):::bsPlanned
        LL4 --- N175
        N176("[design]compliance_check: 法域冲突解决 CrossBorderReg Navigator<br/>path: decision/compliance/cmp_11"):::bsPlanned
        LL4 --- N176
        N195("[design]compliance_check: AISGGate 九层防御 L0-L8<br/>path: decision/security/sec_001"):::bsPlanned
        LL4 --- N195
        N196("[design]compliance_check: ACLGuard Kill Switch执行<br/>path: decision/security/sec_009a"):::bsPlanned
        LL4 --- N196
        N197("[design]compliance_check: Kill Switch紧急熔断 Kill Switch Emergency<br/>path: decision/security/sec_009b"):::bsPlanned
        LL4 --- N197
        N198("[design]compliance_check: Secret Manager 密钥管理<br/>path: decision/security/sec_007"):::bsPlanned
        LL4 --- N198
        N199("[design]compliance_check: Self-Protect 自保护<br/>path: decision/security/sec_008"):::bsPlanned
        LL4 --- N199
        N207("[design]compliance_check: LLM Gateway 推理网关 LLM Gateway<br/>path: decision/security/sec_010"):::bsPlanned
        LL4 --- N207
        N208("[design]compliance_check: 推理熔断器 Inference Circuit Breaker<br/>path: decision/security/sec_011"):::bsPlanned
        LL4 --- N208
        LL5["[design]L5: 学习层<br/>功能: 7阶段学习流水线 → 模块工厂 → 知…<br/>freq: weekly<br/>build: planned"]:::bsPlanned
        LL6["[design]L6: 自评估层<br/>功能: LLM 自评估(Judge+交叉验证)…<br/>freq: weekly<br/>build: planned"]:::bsPlanned
    end
    subgraph track_data_driven["数据驱动轨（Data-Driven Track）"]
    end
    subgraph track_human_override["人工指令轨（Human Override Track）"]
    end
    subgraph track_emergency["应急保命轨（Emergency Track）"]
    end
    LL0 -.->|triggering| LL1
    LL1 -.->|triggering| LL2A
    LL2A -.->|triggering| LL2B
    LL2B -.->|triggering| LL2C
    LL2C -.->|triggering| LL2D
    LL2D -.->|triggering| LL3
    LL3 -.->|triggering| LL4
    LL4 -.->|triggering| LL5
    LL5 -.->|triggering| LL6

    classDef bsStable fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef bsGenerated fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#000
    classDef bsTesting fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px,color:#000
    classDef bsPlanned fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef bsDeprecated fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#000,stroke-dasharray: 5 5
```

### 运营态全景图（仅 design_maturity=production 的 layer/node）

> 仅展示已实现稳定运行的决策层/节点（共 3 层，0 边）。

```mermaid
flowchart TD
    subgraph track_model_driven["模型驱动轨（Model-Driven Track）"]
        LL0["[production]L0: 数据接入与预处理层<br/>功能: miniQMT + iFind + t…<br/>freq: tick<br/>build: stable"]:::bsStable
        LL1["[production]L1: 因子计算层<br/>功能: 因子工厂全生命周期管理 → 盘前全量/…<br/>freq: daily<br/>build: stable"]:::bsStable
        LL4["[production]L4: 风控层<br/>功能: Pre/Post-Trade 风控校验…<br/>freq: realtime<br/>build: stable"]:::bsStable
    end
    subgraph track_data_driven["数据驱动轨（Data-Driven Track）"]
    end
    subgraph track_human_override["人工指令轨（Human Override Track）"]
    end
    subgraph track_emergency["应急保命轨（Emergency Track）"]
    end
    LL0 -.->|triggering| LL1
    LL1 -.->|triggering| LL4

    classDef bsStable fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef bsGenerated fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#000
    classDef bsTesting fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px,color:#000
    classDef bsPlanned fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef bsDeprecated fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#000,stroke-dasharray: 5 5
```

### 设计态全景图（仅 design_maturity=design 的 layer/node）

> 仅展示蓝图规划中尚未实现的决策层/节点（共 7 层，0 边）。

```mermaid
flowchart TD
    subgraph track_model_driven["模型驱动轨（Model-Driven Track）"]
        LL2A["[design]L2A: 信号层<br/>功能: 信号工厂 → 多策略投票 → 收益率条…<br/>freq: daily<br/>build: planned"]:::bsPlanned
        N1("[design]sell_decision: 卖出决策域入口 Sell Decision Entry<br/>path: decision/sell/sell_00"):::bsPlanned
        LL2A --- N1
        N2("[design]sell_decision: 止盈信号 Take-Profit Signal<br/>path: decision/sell/sell_01"):::bsPlanned
        LL2A --- N2
        N3("[design]sell_decision: 止损信号 Stop-Loss Signal<br/>path: decision/sell/sell_02"):::bsPlanned
        LL2A --- N3
        N4("[design]sell_decision: 移动止损 Trailing Stop<br/>path: decision/sell/sell_03"):::bsPlanned
        LL2A --- N4
        N5("[design]sell_decision: 主力出货信号 Main Force Distribution Signal<br/>path: decision/sell/sell_04"):::bsPlanned
        LL2A --- N5
        N6("[design]sell_decision: 量价背离卖出 Volume-Price Divergence Sell<br/>path: decision/sell/sell_05"):::bsPlanned
        LL2A --- N6
        N7("[design]sell_decision: 突破关键位卖出 Key-Level Breakdown Sell<br/>path: decision/sell/sell_06"):::bsPlanned
        LL2A --- N7
        N8("[design]sell_decision: Watch List 实时卖出 Watch List Realtime Sell<br/>path: decision/sell/sell_07"):::bsPlanned
        LL2A --- N8
        N9("[design]sell_decision: Monitor List 定期扫描 Monitor List Periodic Scan<br/>path: decision/sell/sell_08"):::bsPlanned
        LL2A --- N9
        N10("[design]sell_decision: 卖出信号融合仲裁 Sell Signal Fusion Arbiter<br/>path: decision/sell/sell_09"):::bsPlanned
        LL2A --- N10
        N11("[design]sell_decision: 买卖冲突仲裁 Buy-Sell Conflict Arbiter<br/>path: decision/sell/sell_10"):::bsPlanned
        LL2A --- N11
        N12("[design]sell_decision: 部分卖出vs全部清仓决策 Partial vs Full Sell Decision<br/>path: decision/sell/sell_11"):::bsPlanned
        LL2A --- N12
        N13("[design]sell_decision: D-S证据理论融合 D-S Evidence Theory Fusion<br/>path: decision/sell/sell_12"):::bsPlanned
        LL2A --- N13
        N14("[design]sell_decision: 做T决策协调 T-Trade Coordinator<br/>path: decision/sell/sell_13"):::bsPlanned
        LL2A --- N14
        N15("[design]sell_decision: 黑天鹅强制卖出 Black Swan Forced Sell<br/>path: decision/sell/sell_14"):::bsPlanned
        LL2A --- N15
        N16("[design]sell_decision: Gap开盘决策框架 Gap Opening Decision Framework<br/>path: decision/sell/sell_15"):::bsPlanned
        LL2A --- N16
        N17("[design]sell_decision: 强制清仓信号 Forced Liquidation Signal<br/>path: decision/sell/sell_16"):::bsPlanned
        LL2A --- N17
        N18("[design]sell_decision: 卖出降级模式 Sell Degradation Mode<br/>path: decision/sell/sell_17"):::bsPlanned
        LL2A --- N18
        N19("[design]sell_decision: 卖出决策闭环优化 Sell Decision Closed-Loop<br/>path: decision/sell/sell_18"):::bsPlanned
        LL2A --- N19
        N141("[design]signal: 市场仿真器 Market Simulator<br/>path: decision/simulation/sim_01"):::bsPlanned
        LL2A --- N141
        N142("[design]signal: 策略仿真器 Strategy Simulator<br/>path: decision/simulation/sim_02"):::bsPlanned
        LL2A --- N142
        N143("[design]signal: 风控仿真器 Risk Simulator<br/>path: decision/simulation/sim_03"):::bsPlanned
        LL2A --- N143
        N144("[design]signal: 压力测试引擎 Stress Test Engine<br/>path: decision/simulation/sim_04"):::bsPlanned
        LL2A --- N144
        N145("[design]signal: 场景生成器 Scenario Generator<br/>path: decision/simulation/sim_05"):::bsPlanned
        LL2A --- N145
        N146("[design]signal: 历史重放引擎 History Replay Engine<br/>path: decision/simulation/sim_07"):::bsPlanned
        LL2A --- N146
        N147("[design]signal: 极端事件仿真 Extreme Event Simulator<br/>path: decision/simulation/sim_10"):::bsPlanned
        LL2A --- N147
        N148("[design]signal: 依赖图数字孪生 Dependency Graph Digital Twin<br/>path: decision/simulation/sim_13"):::bsPlanned
        LL2A --- N148
        N149("[design]signal: 混沌实验自动生成 Chaos Experiment Auto-Generator<br/>path: decision/simulation/sim_15"):::bsPlanned
        LL2A --- N149
        N150("[design]signal: 回测过拟合检测器 Backtest Overfitting Detector<br/>path: decision/simulation/sim_18"):::bsPlanned
        LL2A --- N150
        N151("[design]signal: Walk-Forward分析器 Walk-Forward Analyzer<br/>path: decision/simulation/sim_19"):::bsPlanned
        LL2A --- N151
        N152("[design]signal: 参数鲁棒性测试器 Parameter Robustness Tester<br/>path: decision/simulation/sim_21"):::bsPlanned
        LL2A --- N152
        N153("[design]signal: 验证自动化流水线 Validation Automation Pipeline<br/>path: decision/simulation/sim_33"):::bsPlanned
        LL2A --- N153
        N154("[design]signal: 自动化过拟合门禁 Automated Overfitting Detector Gate<br/>path: decision/simulation/sim_56"):::bsPlanned
        LL2A --- N154
        N155("[design]signal: 3阶段决策门控 IS→WFA→OOS 3-Stage Decision Gate<br/>path: decision/simulation/sim_g1"):::bsPlanned
        LL2A --- N155
        N177("[design]signal: Synthesizer 信号合成+权重分配<br/>path: decision/signal/sg_01"):::bsPlanned
        LL2A --- N177
        N178("[design]signal: Signal Priority Router 信号优先级路由<br/>path: decision/signal/sg_02"):::bsPlanned
        LL2A --- N178
        N179("[design]signal: LLM Strategy Agent LLM策略Agent<br/>path: decision/signal/sg_03"):::bsPlanned
        LL2A --- N179
        N180("[design]signal: Signal Tail Risk Protector 信号尾部风险保护<br/>path: decision/signal/sg_04"):::bsPlanned
        LL2A --- N180
        N181("[design]signal: A-Share Plan Conformity Evaluator A股计划吻合度评估<br/>path: decision/signal/sg_05"):::bsPlanned
        LL2A --- N181
        N182("[design]signal: A-Share Emergency Opportunity Evaluator A股应急机会评估<br/>path: decision/signal/sg_06"):::bsPlanned
        LL2A --- N182
        N183("[design]signal: A-Share Capital-Force Conflict Arbiter 主力游资冲突仲裁<br/>path: decision/signal/sg_07"):::bsPlanned
        LL2A --- N183
        N184("[design]signal: Regime Special Override Priority Manager Regime特殊覆盖优先级<br/>path: decision/signal/sg_08"):::bsPlanned
        LL2A --- N184
        N185("[design]signal: Risk-Signal Interaction Sequencer 风控-信号交互时序<br/>path: decision/signal/sg_09"):::bsPlanned
        LL2A --- N185
        N186("[design]signal: 36环节决策框架实现器 36-Step Decision Framework<br/>path: decision/signal/sg_10"):::bsPlanned
        LL2A --- N186
        N187("[design]signal: 策略替换与淘汰决策器 Strategy Replacement Decision<br/>path: decision/signal/sg_11"):::bsPlanned
        LL2A --- N187
        N188("[design]signal: 信号冲突解决 Signal Conflict Resolution<br/>path: decision/signal/sg_12"):::bsPlanned
        LL2A --- N188
        N189("[design]signal: 信号融合模块 Signal Fusion Module<br/>path: decision/signal/sg_13"):::bsPlanned
        LL2A --- N189
        N190("[design]signal: 末位淘汰 IC-Based Factor Replacement<br/>path: decision/factor/fc_01"):::bsPlanned
        LL2A --- N190
        N191("[design]signal: 批量裁剪 Batch Factor Pruning<br/>path: decision/factor/fc_02"):::bsPlanned
        LL2A --- N191
        N192("[design]signal: Multi-Source Priority Router 多源优先级路由<br/>path: decision/data/dt_01"):::bsPlanned
        LL2A --- N192
        N193("[design]signal: Cross-Source Reconciler 多源对账<br/>path: decision/data/dt_02"):::bsPlanned
        LL2A --- N193
        N194("[design]signal: Multi-Timeframe Fusion 跨频率融合<br/>path: decision/data/dt_03"):::bsPlanned
        LL2A --- N194
        N200("[design]signal: Approval Workflow UI 审批流程界面<br/>path: decision/frontend/fe_12"):::bsPlanned
        LL2A --- N200
        N201("[design]signal: Notification Router 通知路由<br/>path: decision/frontend/fe_13"):::bsPlanned
        LL2A --- N201
        N202("[design]signal: Real-time Dashboard 实时仪表盘<br/>path: decision/frontend/fe_09"):::bsPlanned
        LL2A --- N202
        N203("[design]signal: 决策树可视化器 ADR Decision Tree Visualizer<br/>path: decision/frontend/fe_m76"):::bsPlanned
        LL2A --- N203
        N204("[design]signal: 4级风控决策 APPROVE/REDUCE/REJECT/FLATTEN<br/>path: decision/research/rs_01"):::bsPlanned
        LL2A --- N204
        N205("[design]signal: 3阶段决策门控 IS→WFA→OOS 3-Stage Decision Gate<br/>path: decision/research/rs_02"):::bsPlanned
        LL2A --- N205
        N206("[design]signal: Decision Audit Trail R-102 Decision Audit Trail<br/>path: decision/research/rs_03"):::bsPlanned
        LL2A --- N206
        N209("[design]signal: 服务降级管理 Service Degradation Manager<br/>path: decision/frontend/fe_14"):::bsPlanned
        LL2A --- N209
        N210("[design]signal: 跨域运维事件链追踪 Cross-Domain Event Chain<br/>path: decision/frontend/fe_15"):::bsPlanned
        LL2A --- N210
        N211("[design]signal: 策略可解释性报告器 Strategy Explainability Reporter<br/>path: decision/research/rs_04"):::bsPlanned
        LL2A --- N211
        N212("[design]signal: A股绩效审计与优化触发器 A-Share Performance Audit<br/>path: decision/research/rs_05"):::bsPlanned
        LL2A --- N212
        N213("[design]signal: 异常决策自检 Anomaly Decision Self-Check<br/>path: decision/research/rs_06"):::bsPlanned
        LL2A --- N213
        N214("[design]signal: Knowledge Feedback Loop 知识反馈循环<br/>path: decision/research/rs_07"):::bsPlanned
        LL2A --- N214
        LL2B["[design]L2B: 主力行为层<br/>功能: 六阶段识别 + 自迭代推演 + 庄家专…<br/>freq: daily<br/>build: planned"]:::bsPlanned
        LL2C["[design]L2C: 市场状态与大盘预测层<br/>功能: 3×3矩阵 + 2叠加态 + 三层大盘…<br/>freq: daily<br/>build: planned"]:::bsPlanned
        LL2D["[design]L2D: 知识图谱与因果推演层<br/>功能: 六类知识图谱 → 事件影响链分析 → …<br/>freq: daily<br/>build: planned"]:::bsPlanned
        LL3["[design]L3: 策略组合层<br/>功能: 多策略信号合成 → 资本分配 → 元策…<br/>freq: daily<br/>build: planned"]:::bsPlanned
        N20("[design]portfolio_target: 组合核心引擎 Portfolio Core Engine<br/>path: decision/pf_core/pc_01"):::bsPlanned
        LL3 --- N20
        N21("[design]portfolio_target: 半Kelly硬上限 Half-Kelly Hard Cap<br/>path: decision/pf_core/pc_02"):::bsPlanned
        LL3 --- N21
        N22("[design]portfolio_target: 风险预算 Risk Budget<br/>path: decision/pf_core/pc_03"):::bsPlanned
        LL3 --- N22
        N23("[design]portfolio_target: 再平衡决策 Rebalance Decision<br/>path: decision/pf_core/pc_04"):::bsPlanned
        LL3 --- N23
        N24("[design]portfolio_target: 仲裁优先级体系 Arbitration Priority<br/>path: decision/pf_core/pc_05"):::bsPlanned
        LL3 --- N24
        N25("[design]portfolio_target: 多策略共振融合 Strategy Convergence Fusion<br/>path: decision/pf_core/pc_06"):::bsPlanned
        LL3 --- N25
        N26("[design]portfolio_target: 因子直通裁决 Factor Bypass Arbitration<br/>path: decision/pf_core/pc_07"):::bsPlanned
        LL3 --- N26
        N27("[design]portfolio_target: 元策略路由 Meta-Strategy Router<br/>path: decision/pf_core/pc_08"):::bsPlanned
        LL3 --- N27
        N28("[design]portfolio_target: 组合优化 Portfolio Optimization<br/>path: decision/pf_core/pc_09"):::bsPlanned
        LL3 --- N28
        N29("[design]portfolio_target: 资本分配 Capital Allocation<br/>path: decision/pf_core/pc_10"):::bsPlanned
        LL3 --- N29
        N30("[design]portfolio_target: 决策编排器 Decision Orchestrator<br/>path: decision/pf_core/pc_11"):::bsPlanned
        LL3 --- N30
        N31("[design]portfolio_target: 四轨融合器 Multi-Track Fusion<br/>path: decision/pf_core/pc_12"):::bsPlanned
        LL3 --- N31
        N32("[design]portfolio_target: 策略分配 Strategy Allocation<br/>path: decision/pf_alloc/pa_01"):::bsPlanned
        LL3 --- N32
        N33("[design]portfolio_target: 风险平价 Risk Parity<br/>path: decision/pf_alloc/pa_02"):::bsPlanned
        LL3 --- N33
        N34("[design]portfolio_target: 动态权重 Dynamic Weighting<br/>path: decision/pf_alloc/pa_03"):::bsPlanned
        LL3 --- N34
        N35("[design]portfolio_target: 策略权重再平衡 Strategy Weight Rebalance<br/>path: decision/pf_alloc/pa_04"):::bsPlanned
        LL3 --- N35
        N36("[design]portfolio_target: 多策略共识 Multi-Strategy Consensus<br/>path: decision/pf_alloc/pa_05"):::bsPlanned
        LL3 --- N36
        N37("[design]portfolio_target: 元策略选择 Meta-Strategy Selection<br/>path: decision/pf_alloc/pa_06"):::bsPlanned
        LL3 --- N37
        N38("[design]portfolio_target: 仓位唯一裁决中心 C-047 Position Sole Arbiter<br/>path: decision/position/pos_01"):::bsPlanned
        LL3 --- N38
        N39("[design]portfolio_target: 持仓状态机 Position State Machine<br/>path: decision/position/pos_02"):::bsPlanned
        LL3 --- N39
        N40("[design]portfolio_target: 仓位漂移监控 Position Drift Monitor<br/>path: decision/position/pos_03"):::bsPlanned
        LL3 --- N40
        N41("[design]portfolio_target: Kelly仓位决策 Kelly Position Decision<br/>path: decision/position/pos_04"):::bsPlanned
        LL3 --- N41
        N42("[design]portfolio_target: 风险配额 Risk Quota<br/>path: decision/position/pos_05"):::bsPlanned
        LL3 --- N42
        N43("[design]portfolio_target: 11种市场状态→仓位上限 Market State Position Cap<br/>path: decision/position/pos_06"):::bsPlanned
        LL3 --- N43
        N44("[design]portfolio_target: 组合层决策 Portfolio Layer Decision<br/>path: decision/position/pos_07"):::bsPlanned
        LL3 --- N44
        N45("[design]portfolio_target: 策略层决策 Strategy Layer Decision<br/>path: decision/position/pos_08"):::bsPlanned
        LL3 --- N45
        N46("[design]portfolio_target: 标层决策 Instrument Layer Decision<br/>path: decision/position/pos_09"):::bsPlanned
        LL3 --- N46
        N47("[design]portfolio_target: 动态层决策 Dynamic Layer Decision<br/>path: decision/position/pos_10"):::bsPlanned
        LL3 --- N47
        N48("[design]portfolio_target: 再平衡触发 Rebalance Trigger<br/>path: decision/position/pos_11"):::bsPlanned
        LL3 --- N48
        N49("[design]portfolio_target: 仓位上限硬约束 Position Cap Hard Constraint<br/>path: decision/position/pos_12"):::bsPlanned
        LL3 --- N49
        N50("[design]portfolio_target: REDUCING→EXITING状态转换 REDUCING to EXITING<br/>path: decision/position/pos_13"):::bsPlanned
        LL3 --- N50
        N51("[design]portfolio_target: 风险预算→Kelly决策 Risk Budget to Kelly<br/>path: decision/position/pos_14"):::bsPlanned
        LL3 --- N51
        N52("[design]portfolio_target: 半Kelly硬上限 Half-Kelly Hard Cap<br/>path: decision/position/pos_15"):::bsPlanned
        LL3 --- N52
        N53("[design]portfolio_target: 仓位降级 Position Degradation<br/>path: decision/position/pos_16"):::bsPlanned
        LL3 --- N53
        N54("[design]portfolio_target: 持仓状态→卖出阈值 Position State to Sell Threshold<br/>path: decision/position/pos_17"):::bsPlanned
        LL3 --- N54
        N55("[design]portfolio_target: 仓位四轨决策 Position Four-Track Decision<br/>path: decision/position/pos_18"):::bsPlanned
        LL3 --- N55
        N56("[design]portfolio_target: 仓位裁决→执行 Position Arbitration to Execution<br/>path: decision/position/pos_19"):::bsPlanned
        LL3 --- N56
        N59("[design]order: 50ms SLA Fail-Closed 50ms SLA Fail-Closed<br/>path: decision/ex_core/ex_03"):::bsPlanned
        LL3 --- N59
        N60("[design]order: Saga编排式事务 Saga Orchestrated Transaction<br/>path: decision/ex_core/ex_04"):::bsPlanned
        LL3 --- N60
        N61("[design]order: 风控检查 Risk Check<br/>path: decision/ex_core/ex_05"):::bsPlanned
        LL3 --- N61
        N62("[design]order: 信号确认 Signal Confirmation<br/>path: decision/ex_core/ex_06"):::bsPlanned
        LL3 --- N62
        N63("[design]order: 下单提交 Order Submit<br/>path: decision/ex_core/ex_07"):::bsPlanned
        LL3 --- N63
        N64("[design]order: 成交确认 Fill Confirmation<br/>path: decision/ex_core/ex_08"):::bsPlanned
        LL3 --- N64
        N65("[design]order: 持仓更新 Position Update<br/>path: decision/ex_core/ex_09"):::bsPlanned
        LL3 --- N65
        N66("[design]order: 报告生成 Report Generation<br/>path: decision/ex_core/ex_10"):::bsPlanned
        LL3 --- N66
        N71("[design]order: 流动性螺旋3阶段 Liquidity Spiral 3-Phase<br/>path: decision/ex_core/ex_15"):::bsPlanned
        LL3 --- N71
        N72("[design]order: 订单路由决策 Order Routing Decision<br/>path: decision/ex_sor/ex_16"):::bsPlanned
        LL3 --- N72
        N73("[design]order: SOR路由决策延迟 SOR Routing Latency<br/>path: decision/ex_sor/ex_17"):::bsPlanned
        LL3 --- N73
        N75("[design]order: 交易通道熔断人工恢复 Trading Channel Manual Recovery<br/>path: decision/ex_sor/ex_19"):::bsPlanned
        LL3 --- N75
        N77("[design]order: Kill-Switch四级阶梯 Kill-Switch 4-Level Cascade<br/>path: decision/ex_sor/ex_21"):::bsPlanned
        LL3 --- N77
        N78("[design]order: 熔断器矩阵 Circuit Breaker Matrix<br/>path: decision/ex_sor/ex_22"):::bsPlanned
        LL3 --- N78
        N102("[design]order: 外部订单观察者 External Order Watcher<br/>path: decision/trading/trd_01"):::bsPlanned
        LL3 --- N102
        N103("[design]order: 结算引擎 Settlement Engine<br/>path: decision/trading/trd_02"):::bsPlanned
        LL3 --- N103
        N104("[design]order: 公司行动 Corporate Action<br/>path: decision/trading/trd_03"):::bsPlanned
        LL3 --- N104
        N105("[design]order: 保证金管理 Margin Manager<br/>path: decision/trading/trd_04"):::bsPlanned
        LL3 --- N105
        N106("[design]order: 多账户 Multi-Account<br/>path: decision/trading/trd_05"):::bsPlanned
        LL3 --- N106
        N107("[design]order: 微信枢纽 WeChat Hub<br/>path: decision/trading/trd_06"):::bsPlanned
        LL3 --- N107
        N108("[design]order: C-013 4级优先级 C-013 4-Level Priority<br/>path: decision/trading/trd_07"):::bsPlanned
        LL3 --- N108
        N109("[design]order: A股交易纪律四项必做 A-Share Trading 4-Do<br/>path: decision/trading/trd_08"):::bsPlanned
        LL3 --- N109
        N110("[design]order: A股交易纪律四项严禁 A-Share Trading 4-Forbidden<br/>path: decision/trading/trd_09"):::bsPlanned
        LL3 --- N110
        N111("[design]order: 监管报送 Regulatory Reporting<br/>path: decision/trading/trd_10"):::bsPlanned
        LL3 --- N111
        N112("[design]order: 盘中即时反应决策引擎 Intraday Instant Reaction Decision Engine<br/>path: decision/trading/trd_11"):::bsPlanned
        LL3 --- N112
        N113("[design]portfolio_target: Permission Guard 七层纵深防御<br/>path: decision/aut_core/ac_01"):::bsPlanned
        LL3 --- N113
        N115("[design]portfolio_target: Self-Healing Git-native自愈<br/>path: decision/aut_core/ac_03"):::bsPlanned
        LL3 --- N115
        N116("[design]portfolio_target: Budget Enforcer 七级预算<br/>path: decision/aut_core/ac_04"):::bsPlanned
        LL3 --- N116
        N117("[design]portfolio_target: Health Monitor 9子系统监控<br/>path: decision/aut_core/ac_05"):::bsPlanned
        LL3 --- N117
        N118("[design]portfolio_target: Escalation Engine 升级引擎<br/>path: decision/aut_core/ac_06"):::bsPlanned
        LL3 --- N118
        N119("[design]portfolio_target: Rollback Engine Git-native回滚<br/>path: decision/aut_core/ac_07"):::bsPlanned
        LL3 --- N119
        N120("[design]portfolio_target: Drift Detector 39检测器<br/>path: decision/aut_core/ac_08"):::bsPlanned
        LL3 --- N120
        N121("[design]portfolio_target: Auto-Fix Engine 16修复器<br/>path: decision/aut_core/ac_09"):::bsPlanned
        LL3 --- N121
        N133("[design]portfolio_target: 编排Agent Orchestrator<br/>path: decision/aut_core/ac_21"):::bsPlanned
        LL3 --- N133
        N135("[design]portfolio_target: 做TAgent T0Trader<br/>path: decision/aut_core/ac_23"):::bsPlanned
        LL3 --- N135
        N136("[design]portfolio_target: 路由Agent Router<br/>path: decision/aut_core/ac_24"):::bsPlanned
        LL3 --- N136
        LL5["[design]L5: 学习层<br/>功能: 7阶段学习流水线 → 模块工厂 → 知…<br/>freq: weekly<br/>build: planned"]:::bsPlanned
        LL6["[design]L6: 自评估层<br/>功能: LLM 自评估(Judge+交叉验证)…<br/>freq: weekly<br/>build: planned"]:::bsPlanned
    end
    subgraph track_data_driven["数据驱动轨（Data-Driven Track）"]
    end
    subgraph track_human_override["人工指令轨（Human Override Track）"]
    end
    subgraph track_emergency["应急保命轨（Emergency Track）"]
    end
    LL2A -.->|triggering| LL2B
    LL2B -.->|triggering| LL2C
    LL2C -.->|triggering| LL2D
    LL2D -.->|triggering| LL3
    LL3 -.->|triggering| LL5
    LL5 -.->|triggering| LL6

    classDef bsStable fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef bsGenerated fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#000
    classDef bsTesting fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px,color:#000
    classDef bsPlanned fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef bsDeprecated fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#000,stroke-dasharray: 5 5
```

### 层级详情图（10 层卡片 + 频率/状态，标签标注 [design]/[production]）

```mermaid
flowchart LR
    LL0["[production] L0 数据接入与预处理层<br/>Data Ingestion & Preprocessing<br/>功能: miniQMT + iFind + t…<br/>频率: tick<br/>成熟度: production<br/>build: stable"]:::bsStable
    LL1["[production] L1 因子计算层<br/>Factor Calculation<br/>功能: 因子工厂全生命周期管理 → 盘前全量/…<br/>频率: daily<br/>成熟度: production<br/>build: stable"]:::bsStable
    LL2A["[design] L2A 信号层<br/>Signal Generation<br/>功能: 信号工厂 → 多策略投票 → 收益率条…<br/>频率: daily<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LL2B["[design] L2B 主力行为层<br/>Main Force Behavior Analysis<br/>功能: 六阶段识别 + 自迭代推演 + 庄家专…<br/>频率: daily<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LL2C["[design] L2C 市场状态与大盘预测层<br/>Market State & Index Prediction<br/>功能: 3×3矩阵 + 2叠加态 + 三层大盘…<br/>频率: daily<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LL2D["[design] L2D 知识图谱与因果推演层<br/>Knowledge Graph & Causal Inference<br/>功能: 六类知识图谱 → 事件影响链分析 → …<br/>频率: daily<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LL3["[design] L3 策略组合层<br/>Strategy & Portfolio Combination<br/>功能: 多策略信号合成 → 资本分配 → 元策…<br/>频率: daily<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LL4["[production] L4 风控层<br/>Risk Control<br/>功能: Pre/Post-Trade 风控校验…<br/>频率: realtime<br/>成熟度: production<br/>build: stable"]:::bsStable
    LL5["[design] L5 学习层<br/>Learning & Optimization<br/>功能: 7阶段学习流水线 → 模块工厂 → 知…<br/>频率: weekly<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LL6["[design] L6 自评估层<br/>Self Evaluation<br/>功能: LLM 自评估(Judge+交叉验证)…<br/>频率: weekly<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LL0 -->|triggering| LL1
    LL1 -->|triggering| LL2A
    LL2A -->|triggering| LL2B
    LL2B -->|triggering| LL2C
    LL2C -->|triggering| LL2D
    LL2D -->|triggering| LL3
    LL3 -->|triggering| LL4
    LL4 -->|triggering| LL5
    LL5 -->|triggering| LL6
    L6 -.->|feedback| L1
    L6 -.->|feedback| L5

    classDef bsStable fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef bsGenerated fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#000
    classDef bsTesting fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px,color:#000
    classDef bsPlanned fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef bsDeprecated fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#000,stroke-dasharray: 5 5
```

### 不变量图（6 节点类型 + 5 承重墙不变量）

```mermaid
flowchart TD
    NT_signal["信号节点<br/>Signal"]:::nodeType
    NT_portfolio_target["仓位目标节点<br/>Portfolio Target"]:::nodeType
    NT_risk_check["风控节点<br/>Risk Check"]:::nodeType
    NT_order["订单节点<br/>Order"]:::nodeType
    NT_execution["执行节点<br/>Execution"]:::nodeType
    NT_feedback["反馈节点<br/>Feedback"]:::nodeType
    NT_signal -->|portfolio_target| NT_portfolio_target
    NT_portfolio_target -->|risk_check| NT_risk_check
    NT_risk_check -->|approving| NT_order
    NT_order -->|triggering| NT_execution
    NT_execution -.->|feedback| NT_feedback
    NT_feedback -.->|informing| NT_signal
    NT_signal -.->|禁止| NT_order
    linkStyle 6 stroke:#c62828,stroke-width:2px,stroke-dasharray: 5 5
    INV_DEC_INV_001(["DEC-INV-001<br/>风控一票否决<br/>Risk Veto Mandatory"]):::invariant
    INV_DEC_INV_002(["DEC-INV-002<br/>信号仓位分离<br/>Signal-Order Separation"]):::invariant
    INV_DEC_INV_003(["DEC-INV-003<br/>DAG 无环<br/>DAG No-Cycle"]):::invariant
    INV_DEC_INV_004(["DEC-INV-004<br/>时间单调性<br/>Time Monotonicity"]):::invariant
    INV_DEC_INV_005(["DEC-INV-005<br/>证据哈希必填<br/>Evidence Hash Required"]):::invariant
    INV_DEC_INV_001 -.- NT_order
    INV_DEC_INV_002 -.- NT_signal
    INV_DEC_INV_003 -.- NT_feedback
    INV_DEC_INV_005 -.- NT_signal

    classDef nodeType fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
    classDef invariant fill:#fff8e1,stroke:#ff8f00,stroke-width:2px,color:#000
```

## Track 清单（四轨）

| track_id | 名称 | 英文名 | 优先级 | 激活条件 |
|----------|------|--------|--------|----------|
| model_driven | 模型驱动轨 | Model-Driven Track | 1 | 正常运行时 |
| data_driven | 数据驱动轨 | Data-Driven Track | 2 | 模型驱动轨信号不足时补充 |
| human_override | 人工指令轨 | Human Override Track | 3 | 人工干预时 |
| emergency | 应急保命轨 | Emergency Track | 4 | 所有模型/策略/信号失效时 |

## Layer 清单（L0-L6）

| layer_id | 名称 | 英文名 | 所属轨 | 蓝图(module_id) | 蓝图名(派生) | 代码引用 | 功能简述 | 决策频率 | 成熟度 | build_status |
|----------|------|--------|--------|-----------------|--------------|----------|----------|----------|--------|--------------|
| L0 | 数据接入与预处理层 | Data Ingestion & Preprocessing | model_driven | - | - | - | miniQMT + iFind + tushare + 另类数据源 → 事件总线 → 分层时序存储 产出：tick_data / ohlc_bar / factor_input_data | tick | production | stable |
| L1 | 因子计算层 | Factor Calculation | model_driven | - | - | - | 因子工厂全生命周期管理 → 盘前全量/盘中增量双模计算 → 因子池 产出：factor_value（带 PIT 合规标记） | daily | production | stable |
| L2A | 信号层 | Signal Generation | model_driven | - | - | - | 信号工厂 → 多策略投票 → 收益率条件密度预测 → Transformer/Mamba时序增强 → 共形预测 产出：signal（Insight: direction/confidence/horizon） | daily | design | planned |
| L2B | 主力行为层 | Main Force Behavior Analysis | model_driven | - | - | - | 六阶段识别 + 自迭代推演 + 庄家专项 + 群体博弈模拟 产出：main_force_signal（主力行为画像） | daily | design | planned |
| L2C | 市场状态与大盘预测层 | Market State & Index Prediction | model_driven | - | - | - | 3×3矩阵 + 2叠加态 + 三层大盘预测 + T+1次日8态走势预测 + 体制转换检测(HMM/变点) 产出：market_state_prediction（大盘方向/波动率/体制判断） | daily | design | planned |
| L2D | 知识图谱与因果推演层 | Knowledge Graph & Causal Inference | model_driven | - | - | - | 六类知识图谱 → 事件影响链分析 → 因果传导推演 → GNN股票关系建模 → Causal ML 产出：causal_inference_result（因果推断结果） | daily | design | planned |
| L3 | 策略组合层 | Strategy & Portfolio Combination | model_driven | - | - | - | 多策略信号合成 → 资本分配 → 元策略路由 → 组合构建 产出：portfolio_target（PortfolioTarget: 目标仓位） | daily | design | planned |
| L4 | 风控层 | Risk Control | model_driven | - | - | - | Pre/Post-Trade 风控校验 + Kill Switch 熔断 + 止损评估 产出：risk_check（RiskDecision: approve/veto/adjust） | realtime | production | stable |
| L5 | 学习层 | Learning & Optimization | model_driven | - | - | - | 7阶段学习流水线 → 模块工厂 → 知识采集 → 反馈闭环 产出：learning_feedback（策略优化建议） | weekly | design | planned |
| L6 | 自评估层 | Self Evaluation | model_driven | - | - | - | LLM 自评估(Judge+交叉验证) + 多模态金融推理 + VeNRA零幻觉锚定 产出：self_evaluation（决策质量评估） | weekly | design | planned |

## Node 清单（运行时决策节点）

| node_id | layer | type | name | path | module_id | 代码引用 | 成熟度 | build_status |
|---------|-------|------|------|------|-----------|----------|--------|--------------|
| 1 | L2A | sell_decision | 卖出决策域入口 Sell Decision Entry | decision/sell/sell_00 | - | - | design | planned |
| 2 | L2A | sell_decision | 止盈信号 Take-Profit Signal | decision/sell/sell_01 | - | - | design | planned |
| 3 | L2A | sell_decision | 止损信号 Stop-Loss Signal | decision/sell/sell_02 | - | - | design | planned |
| 4 | L2A | sell_decision | 移动止损 Trailing Stop | decision/sell/sell_03 | - | - | design | planned |
| 5 | L2A | sell_decision | 主力出货信号 Main Force Distribution Signal | decision/sell/sell_04 | - | - | design | planned |
| 6 | L2A | sell_decision | 量价背离卖出 Volume-Price Divergence Sell | decision/sell/sell_05 | - | - | design | planned |
| 7 | L2A | sell_decision | 突破关键位卖出 Key-Level Breakdown Sell | decision/sell/sell_06 | - | - | design | planned |
| 8 | L2A | sell_decision | Watch List 实时卖出 Watch List Realtime Sell | decision/sell/sell_07 | - | - | design | planned |
| 9 | L2A | sell_decision | Monitor List 定期扫描 Monitor List Periodic Scan | decision/sell/sell_08 | - | - | design | planned |
| 10 | L2A | sell_decision | 卖出信号融合仲裁 Sell Signal Fusion Arbiter | decision/sell/sell_09 | - | - | design | planned |
| 11 | L2A | sell_decision | 买卖冲突仲裁 Buy-Sell Conflict Arbiter | decision/sell/sell_10 | - | - | design | planned |
| 12 | L2A | sell_decision | 部分卖出vs全部清仓决策 Partial vs Full Sell Decision | decision/sell/sell_11 | - | - | design | planned |
| 13 | L2A | sell_decision | D-S证据理论融合 D-S Evidence Theory Fusion | decision/sell/sell_12 | - | - | design | planned |
| 14 | L2A | sell_decision | 做T决策协调 T-Trade Coordinator | decision/sell/sell_13 | - | - | design | planned |
| 15 | L2A | sell_decision | 黑天鹅强制卖出 Black Swan Forced Sell | decision/sell/sell_14 | - | - | design | planned |
| 16 | L2A | sell_decision | Gap开盘决策框架 Gap Opening Decision Framework | decision/sell/sell_15 | - | - | design | planned |
| 17 | L2A | sell_decision | 强制清仓信号 Forced Liquidation Signal | decision/sell/sell_16 | - | - | design | planned |
| 18 | L2A | sell_decision | 卖出降级模式 Sell Degradation Mode | decision/sell/sell_17 | - | - | design | planned |
| 19 | L2A | sell_decision | 卖出决策闭环优化 Sell Decision Closed-Loop | decision/sell/sell_18 | - | - | design | planned |
| 141 | L2A | signal | 市场仿真器 Market Simulator | decision/simulation/sim_01 | - | - | design | planned |
| 142 | L2A | signal | 策略仿真器 Strategy Simulator | decision/simulation/sim_02 | - | - | design | planned |
| 143 | L2A | signal | 风控仿真器 Risk Simulator | decision/simulation/sim_03 | - | - | design | planned |
| 144 | L2A | signal | 压力测试引擎 Stress Test Engine | decision/simulation/sim_04 | - | - | design | planned |
| 145 | L2A | signal | 场景生成器 Scenario Generator | decision/simulation/sim_05 | - | - | design | planned |
| 146 | L2A | signal | 历史重放引擎 History Replay Engine | decision/simulation/sim_07 | - | - | design | planned |
| 147 | L2A | signal | 极端事件仿真 Extreme Event Simulator | decision/simulation/sim_10 | - | - | design | planned |
| 148 | L2A | signal | 依赖图数字孪生 Dependency Graph Digital Twin | decision/simulation/sim_13 | - | - | design | planned |
| 149 | L2A | signal | 混沌实验自动生成 Chaos Experiment Auto-Generator | decision/simulation/sim_15 | - | - | design | planned |
| 150 | L2A | signal | 回测过拟合检测器 Backtest Overfitting Detector | decision/simulation/sim_18 | - | - | design | planned |
| 151 | L2A | signal | Walk-Forward分析器 Walk-Forward Analyzer | decision/simulation/sim_19 | - | - | design | planned |
| 152 | L2A | signal | 参数鲁棒性测试器 Parameter Robustness Tester | decision/simulation/sim_21 | - | - | design | planned |
| 153 | L2A | signal | 验证自动化流水线 Validation Automation Pipeline | decision/simulation/sim_33 | - | - | design | planned |
| 154 | L2A | signal | 自动化过拟合门禁 Automated Overfitting Detector Gate | decision/simulation/sim_56 | - | - | design | planned |
| 155 | L2A | signal | 3阶段决策门控 IS→WFA→OOS 3-Stage Decision Gate | decision/simulation/sim_g1 | - | - | design | planned |
| 177 | L2A | signal | Synthesizer 信号合成+权重分配 | decision/signal/sg_01 | - | - | design | planned |
| 178 | L2A | signal | Signal Priority Router 信号优先级路由 | decision/signal/sg_02 | - | - | design | planned |
| 179 | L2A | signal | LLM Strategy Agent LLM策略Agent | decision/signal/sg_03 | - | - | design | planned |
| 180 | L2A | signal | Signal Tail Risk Protector 信号尾部风险保护 | decision/signal/sg_04 | - | - | design | planned |
| 181 | L2A | signal | A-Share Plan Conformity Evaluator A股计划吻合度评估 | decision/signal/sg_05 | - | - | design | planned |
| 182 | L2A | signal | A-Share Emergency Opportunity Evaluator A股应急机会评估 | decision/signal/sg_06 | - | - | design | planned |
| 183 | L2A | signal | A-Share Capital-Force Conflict Arbiter 主力游资冲突仲裁 | decision/signal/sg_07 | - | - | design | planned |
| 184 | L2A | signal | Regime Special Override Priority Manager Regime特殊覆盖优先级 | decision/signal/sg_08 | - | - | design | planned |
| 185 | L2A | signal | Risk-Signal Interaction Sequencer 风控-信号交互时序 | decision/signal/sg_09 | - | - | design | planned |
| 186 | L2A | signal | 36环节决策框架实现器 36-Step Decision Framework | decision/signal/sg_10 | - | - | design | planned |
| 187 | L2A | signal | 策略替换与淘汰决策器 Strategy Replacement Decision | decision/signal/sg_11 | - | - | design | planned |
| 188 | L2A | signal | 信号冲突解决 Signal Conflict Resolution | decision/signal/sg_12 | - | - | design | planned |
| 189 | L2A | signal | 信号融合模块 Signal Fusion Module | decision/signal/sg_13 | - | - | design | planned |
| 190 | L2A | signal | 末位淘汰 IC-Based Factor Replacement | decision/factor/fc_01 | - | - | design | planned |
| 191 | L2A | signal | 批量裁剪 Batch Factor Pruning | decision/factor/fc_02 | - | - | design | planned |
| 192 | L2A | signal | Multi-Source Priority Router 多源优先级路由 | decision/data/dt_01 | - | - | design | planned |
| 193 | L2A | signal | Cross-Source Reconciler 多源对账 | decision/data/dt_02 | - | - | design | planned |
| 194 | L2A | signal | Multi-Timeframe Fusion 跨频率融合 | decision/data/dt_03 | - | - | design | planned |
| 200 | L2A | signal | Approval Workflow UI 审批流程界面 | decision/frontend/fe_12 | - | - | design | planned |
| 201 | L2A | signal | Notification Router 通知路由 | decision/frontend/fe_13 | - | - | design | planned |
| 202 | L2A | signal | Real-time Dashboard 实时仪表盘 | decision/frontend/fe_09 | - | - | design | planned |
| 203 | L2A | signal | 决策树可视化器 ADR Decision Tree Visualizer | decision/frontend/fe_m76 | - | - | design | planned |
| 204 | L2A | signal | 4级风控决策 APPROVE/REDUCE/REJECT/FLATTEN | decision/research/rs_01 | - | - | design | planned |
| 205 | L2A | signal | 3阶段决策门控 IS→WFA→OOS 3-Stage Decision Gate | decision/research/rs_02 | - | - | design | planned |
| 206 | L2A | signal | Decision Audit Trail R-102 Decision Audit Trail | decision/research/rs_03 | - | - | design | planned |
| 209 | L2A | signal | 服务降级管理 Service Degradation Manager | decision/frontend/fe_14 | - | - | design | planned |
| 210 | L2A | signal | 跨域运维事件链追踪 Cross-Domain Event Chain | decision/frontend/fe_15 | - | - | design | planned |
| 211 | L2A | signal | 策略可解释性报告器 Strategy Explainability Reporter | decision/research/rs_04 | - | - | design | planned |
| 212 | L2A | signal | A股绩效审计与优化触发器 A-Share Performance Audit | decision/research/rs_05 | - | - | design | planned |
| 213 | L2A | signal | 异常决策自检 Anomaly Decision Self-Check | decision/research/rs_06 | - | - | design | planned |
| 214 | L2A | signal | Knowledge Feedback Loop 知识反馈循环 | decision/research/rs_07 | - | - | design | planned |
| 20 | L3 | portfolio_target | 组合核心引擎 Portfolio Core Engine | decision/pf_core/pc_01 | - | - | design | planned |
| 21 | L3 | portfolio_target | 半Kelly硬上限 Half-Kelly Hard Cap | decision/pf_core/pc_02 | - | - | design | planned |
| 22 | L3 | portfolio_target | 风险预算 Risk Budget | decision/pf_core/pc_03 | - | - | design | planned |
| 23 | L3 | portfolio_target | 再平衡决策 Rebalance Decision | decision/pf_core/pc_04 | - | - | design | planned |
| 24 | L3 | portfolio_target | 仲裁优先级体系 Arbitration Priority | decision/pf_core/pc_05 | - | - | design | planned |
| 25 | L3 | portfolio_target | 多策略共振融合 Strategy Convergence Fusion | decision/pf_core/pc_06 | - | - | design | planned |
| 26 | L3 | portfolio_target | 因子直通裁决 Factor Bypass Arbitration | decision/pf_core/pc_07 | - | - | design | planned |
| 27 | L3 | portfolio_target | 元策略路由 Meta-Strategy Router | decision/pf_core/pc_08 | - | - | design | planned |
| 28 | L3 | portfolio_target | 组合优化 Portfolio Optimization | decision/pf_core/pc_09 | - | - | design | planned |
| 29 | L3 | portfolio_target | 资本分配 Capital Allocation | decision/pf_core/pc_10 | - | - | design | planned |
| 30 | L3 | portfolio_target | 决策编排器 Decision Orchestrator | decision/pf_core/pc_11 | - | - | design | planned |
| 31 | L3 | portfolio_target | 四轨融合器 Multi-Track Fusion | decision/pf_core/pc_12 | - | - | design | planned |
| 32 | L3 | portfolio_target | 策略分配 Strategy Allocation | decision/pf_alloc/pa_01 | - | - | design | planned |
| 33 | L3 | portfolio_target | 风险平价 Risk Parity | decision/pf_alloc/pa_02 | - | - | design | planned |
| 34 | L3 | portfolio_target | 动态权重 Dynamic Weighting | decision/pf_alloc/pa_03 | - | - | design | planned |
| 35 | L3 | portfolio_target | 策略权重再平衡 Strategy Weight Rebalance | decision/pf_alloc/pa_04 | - | - | design | planned |
| 36 | L3 | portfolio_target | 多策略共识 Multi-Strategy Consensus | decision/pf_alloc/pa_05 | - | - | design | planned |
| 37 | L3 | portfolio_target | 元策略选择 Meta-Strategy Selection | decision/pf_alloc/pa_06 | - | - | design | planned |
| 38 | L3 | portfolio_target | 仓位唯一裁决中心 C-047 Position Sole Arbiter | decision/position/pos_01 | - | - | design | planned |
| 39 | L3 | portfolio_target | 持仓状态机 Position State Machine | decision/position/pos_02 | - | - | design | planned |
| 40 | L3 | portfolio_target | 仓位漂移监控 Position Drift Monitor | decision/position/pos_03 | - | - | design | planned |
| 41 | L3 | portfolio_target | Kelly仓位决策 Kelly Position Decision | decision/position/pos_04 | - | - | design | planned |
| 42 | L3 | portfolio_target | 风险配额 Risk Quota | decision/position/pos_05 | - | - | design | planned |
| 43 | L3 | portfolio_target | 11种市场状态→仓位上限 Market State Position Cap | decision/position/pos_06 | - | - | design | planned |
| 44 | L3 | portfolio_target | 组合层决策 Portfolio Layer Decision | decision/position/pos_07 | - | - | design | planned |
| 45 | L3 | portfolio_target | 策略层决策 Strategy Layer Decision | decision/position/pos_08 | - | - | design | planned |
| 46 | L3 | portfolio_target | 标层决策 Instrument Layer Decision | decision/position/pos_09 | - | - | design | planned |
| 47 | L3 | portfolio_target | 动态层决策 Dynamic Layer Decision | decision/position/pos_10 | - | - | design | planned |
| 48 | L3 | portfolio_target | 再平衡触发 Rebalance Trigger | decision/position/pos_11 | - | - | design | planned |
| 49 | L3 | portfolio_target | 仓位上限硬约束 Position Cap Hard Constraint | decision/position/pos_12 | - | - | design | planned |
| 50 | L3 | portfolio_target | REDUCING→EXITING状态转换 REDUCING to EXITING | decision/position/pos_13 | - | - | design | planned |
| 51 | L3 | portfolio_target | 风险预算→Kelly决策 Risk Budget to Kelly | decision/position/pos_14 | - | - | design | planned |
| 52 | L3 | portfolio_target | 半Kelly硬上限 Half-Kelly Hard Cap | decision/position/pos_15 | - | - | design | planned |
| 53 | L3 | portfolio_target | 仓位降级 Position Degradation | decision/position/pos_16 | - | - | design | planned |
| 54 | L3 | portfolio_target | 持仓状态→卖出阈值 Position State to Sell Threshold | decision/position/pos_17 | - | - | design | planned |
| 55 | L3 | portfolio_target | 仓位四轨决策 Position Four-Track Decision | decision/position/pos_18 | - | - | design | planned |
| 56 | L3 | portfolio_target | 仓位裁决→执行 Position Arbitration to Execution | decision/position/pos_19 | - | - | design | planned |
| 59 | L3 | order | 50ms SLA Fail-Closed 50ms SLA Fail-Closed | decision/ex_core/ex_03 | - | - | design | planned |
| 60 | L3 | order | Saga编排式事务 Saga Orchestrated Transaction | decision/ex_core/ex_04 | - | - | design | planned |
| 61 | L3 | order | 风控检查 Risk Check | decision/ex_core/ex_05 | - | - | design | planned |
| 62 | L3 | order | 信号确认 Signal Confirmation | decision/ex_core/ex_06 | - | - | design | planned |
| 63 | L3 | order | 下单提交 Order Submit | decision/ex_core/ex_07 | - | - | design | planned |
| 64 | L3 | order | 成交确认 Fill Confirmation | decision/ex_core/ex_08 | - | - | design | planned |
| 65 | L3 | order | 持仓更新 Position Update | decision/ex_core/ex_09 | - | - | design | planned |
| 66 | L3 | order | 报告生成 Report Generation | decision/ex_core/ex_10 | - | - | design | planned |
| 71 | L3 | order | 流动性螺旋3阶段 Liquidity Spiral 3-Phase | decision/ex_core/ex_15 | - | - | design | planned |
| 72 | L3 | order | 订单路由决策 Order Routing Decision | decision/ex_sor/ex_16 | - | - | design | planned |
| 73 | L3 | order | SOR路由决策延迟 SOR Routing Latency | decision/ex_sor/ex_17 | - | - | design | planned |
| 75 | L3 | order | 交易通道熔断人工恢复 Trading Channel Manual Recovery | decision/ex_sor/ex_19 | - | - | design | planned |
| 77 | L3 | order | Kill-Switch四级阶梯 Kill-Switch 4-Level Cascade | decision/ex_sor/ex_21 | - | - | design | planned |
| 78 | L3 | order | 熔断器矩阵 Circuit Breaker Matrix | decision/ex_sor/ex_22 | - | - | design | planned |
| 102 | L3 | order | 外部订单观察者 External Order Watcher | decision/trading/trd_01 | - | - | design | planned |
| 103 | L3 | order | 结算引擎 Settlement Engine | decision/trading/trd_02 | - | - | design | planned |
| 104 | L3 | order | 公司行动 Corporate Action | decision/trading/trd_03 | - | - | design | planned |
| 105 | L3 | order | 保证金管理 Margin Manager | decision/trading/trd_04 | - | - | design | planned |
| 106 | L3 | order | 多账户 Multi-Account | decision/trading/trd_05 | - | - | design | planned |
| 107 | L3 | order | 微信枢纽 WeChat Hub | decision/trading/trd_06 | - | - | design | planned |
| 108 | L3 | order | C-013 4级优先级 C-013 4-Level Priority | decision/trading/trd_07 | - | - | design | planned |
| 109 | L3 | order | A股交易纪律四项必做 A-Share Trading 4-Do | decision/trading/trd_08 | - | - | design | planned |
| 110 | L3 | order | A股交易纪律四项严禁 A-Share Trading 4-Forbidden | decision/trading/trd_09 | - | - | design | planned |
| 111 | L3 | order | 监管报送 Regulatory Reporting | decision/trading/trd_10 | - | - | design | planned |
| 112 | L3 | order | 盘中即时反应决策引擎 Intraday Instant Reaction Decision Engine | decision/trading/trd_11 | - | - | design | planned |
| 113 | L3 | portfolio_target | Permission Guard 七层纵深防御 | decision/aut_core/ac_01 | - | - | design | planned |
| 115 | L3 | portfolio_target | Self-Healing Git-native自愈 | decision/aut_core/ac_03 | - | - | design | planned |
| 116 | L3 | portfolio_target | Budget Enforcer 七级预算 | decision/aut_core/ac_04 | - | - | design | planned |
| 117 | L3 | portfolio_target | Health Monitor 9子系统监控 | decision/aut_core/ac_05 | - | - | design | planned |
| 118 | L3 | portfolio_target | Escalation Engine 升级引擎 | decision/aut_core/ac_06 | - | - | design | planned |
| 119 | L3 | portfolio_target | Rollback Engine Git-native回滚 | decision/aut_core/ac_07 | - | - | design | planned |
| 120 | L3 | portfolio_target | Drift Detector 39检测器 | decision/aut_core/ac_08 | - | - | design | planned |
| 121 | L3 | portfolio_target | Auto-Fix Engine 16修复器 | decision/aut_core/ac_09 | - | - | design | planned |
| 133 | L3 | portfolio_target | 编排Agent Orchestrator | decision/aut_core/ac_21 | - | - | design | planned |
| 135 | L3 | portfolio_target | 做TAgent T0Trader | decision/aut_core/ac_23 | - | - | design | planned |
| 136 | L3 | portfolio_target | 路由Agent Router | decision/aut_core/ac_24 | - | - | design | planned |
| 57 | L4 | compliance_check | Pre-Trade主链6项检查 Pre-Trade Main Chain 6 Checks | decision/ex_core/ex_01 | - | - | design | planned |
| 58 | L4 | risk_check | Kill Switch 5层防御 Kill Switch 5-Layer Defense | decision/ex_core/ex_02 | - | - | design | planned |
| 67 | L4 | risk_check | Kill Switch AI自动激活 Kill Switch AI Auto Trigger | decision/ex_core/ex_11 | - | - | design | planned |
| 68 | L4 | risk_check | Kill Switch人工激活 Kill Switch Manual Trigger | decision/ex_core/ex_12 | - | - | design | planned |
| 69 | L4 | risk_check | Kill Switch定时激活 Kill Switch Timer Trigger | decision/ex_core/ex_13 | - | - | design | planned |
| 70 | L4 | risk_check | Kill Switch外部信号激活 Kill Switch External Signal | decision/ex_core/ex_14 | - | - | design | planned |
| 74 | L4 | risk_check | 券商连接熔断+故障转移 Broker Circuit Breaker | decision/ex_sor/ex_18 | - | - | design | planned |
| 76 | L4 | compliance_check | Pre-Trade合规检查流水线 Pre-Trade Compliance Pipeline | decision/ex_sor/ex_20 | - | - | design | planned |
| 79 | L4 | compliance_check | 行为准入门禁 Behavioral Admission Gateway | decision/ex_sor/ex_23 | - | - | design | planned |
| 80 | L4 | risk_check | 风控熔断事件 Risk Circuit Breaker Event | decision/risk/rk_01 | - | - | design | planned |
| 81 | L4 | risk_check | 三层防线 Three Defense Lines | decision/risk/rk_02 | - | - | design | planned |
| 82 | L4 | risk_check | 双引擎风控 Dual Engine Risk | decision/risk/rk_03 | - | - | design | planned |
| 83 | L4 | risk_check | 4级风控决策门控 4-Level Risk Decision Gate | decision/risk/rk_04 | - | - | design | planned |
| 84 | L4 | risk_check | 压力测试引擎 Stress Test Engine | decision/risk/rk_05 | - | - | design | planned |
| 85 | L4 | risk_check | 黑天鹅模式库 Black Swan Pattern Library | decision/risk/rk_06 | - | - | design | planned |
| 86 | L4 | risk_check | 流动性危机模拟 Liquidity Crisis Simulation | decision/risk/rk_07 | - | - | design | planned |
| 87 | L4 | risk_check | 反向压力测试4步法 Reverse Stress Test 4-Step | decision/risk/rk_08 | - | - | design | planned |
| 88 | L4 | risk_check | 二阶效应与传染模型 Second-Order Effect Model | decision/risk/rk_09 | - | - | design | planned |
| 89 | L4 | risk_check | 风控否决权 Risk Veto | decision/risk/rk_10 | - | - | design | planned |
| 90 | L4 | risk_check | 风控状态 Risk State | decision/risk/rk_11 | - | - | design | planned |
| 91 | L4 | risk_check | 风控参数变更审批 Risk Parameter Approval | decision/risk/rk_12 | - | - | design | planned |
| 92 | L4 | risk_check | 熔断恢复确认 Circuit Breaker Recovery Confirm | decision/risk/rk_13 | - | - | design | planned |
| 93 | L4 | risk_check | OBSERVING软止损观察期 OBSERVING Soft Stop | decision/risk/rk_14 | - | - | design | planned |
| 94 | L4 | risk_check | 风险预算 Risk Budget | decision/risk/rk_15 | - | - | design | planned |
| 95 | L4 | risk_check | VaR计算 VaR Calculation | decision/risk/rk_16 | - | - | design | planned |
| 96 | L4 | risk_check | 回撤监控 Drawdown Monitor | decision/risk/rk_17 | - | - | design | planned |
| 97 | L4 | risk_check | 风控信号交互时序 Risk-Signal Timing | decision/risk/rk_18 | - | - | design | planned |
| 98 | L4 | risk_check | 风控事件 Risk Event | decision/risk/rk_19 | - | - | design | planned |
| 99 | L4 | risk_check | FLATTEN硬编码触发 FLATTEN Hardcoded Trigger | decision/risk/rk_20 | - | - | design | planned |
| 100 | L4 | risk_check | 5级风险否决引擎 5-Level Risk Veto Engine | decision/risk/rk_21 | - | - | design | planned |
| 101 | L4 | risk_check | Pod级止损 Pod-Level Stop Loss | decision/risk/rk_22 | - | - | design | planned |
| 114 | L4 | compliance_check | Audit Trail Merkle哈希链 | decision/aut_core/ac_02 | - | - | design | planned |
| 122 | L4 | compliance_check | Decision Audit Trail 决策审计 | decision/aut_core/ac_10 | - | - | design | planned |
| 123 | L4 | compliance_check | Kill Switch直通路径 Kill Switch Direct Path | decision/aut_perm/ap_11 | - | - | design | planned |
| 124 | L4 | compliance_check | 4级自治模型 Level 0-3 Autonomy Model | decision/aut_perm/ap_12 | - | - | design | planned |
| 125 | L4 | compliance_check | AI自治边界三级分类 | decision/aut_perm/ap_13 | - | - | design | planned |
| 126 | L4 | compliance_check | Agentic Drift 5类攻击模式 | decision/aut_perm/ap_14 | - | - | design | planned |
| 127 | L4 | compliance_check | 行为审计7信号 S-01~S-07 | decision/aut_perm/ap_15 | - | - | design | planned |
| 128 | L4 | compliance_check | ARS双轨结算模型 ARS Dual-Track Settlement | decision/aut_perm/ap_16 | - | - | design | planned |
| 129 | L4 | risk_check | AI自治熔断5条件 VR-009 5 Conditions | decision/aut_perm/ap_17 | - | - | design | planned |
| 130 | L4 | risk_check | L0完全人工→L4降级模式 L0 to L4 Degradation | decision/aut_perm/ap_18 | - | - | design | planned |
| 131 | L4 | risk_check | 4级风控决策 APPROVE/REDUCE/REJECT/FLATTEN | decision/aut_perm/ap_19 | - | - | design | planned |
| 132 | L4 | compliance_check | 人类监督四层级 L0~L3 Human Oversight | decision/aut_perm/ap_20 | - | - | design | planned |
| 134 | L4 | risk_check | 风控Agent RiskManager | decision/aut_core/ac_22 | - | - | design | planned |
| 137 | L4 | compliance_check | A2A检查网关策略引擎 A2A Check Gateway | decision/aut_perm/ap_21 | - | - | design | planned |
| 138 | L4 | compliance_check | LLM Agent路由 级联控制器 Cascade Controller | decision/aut_perm/ap_22 | - | - | design | planned |
| 139 | L4 | risk_check | 应急保命轨 Emergency Track | decision/aut_perm/ap_23 | - | - | design | planned |
| 140 | L4 | compliance_check | 置信度分层决策 C-031 Confidence-Layered Decision | decision/aut_perm/ap_24 | - | - | design | planned |
| 156 | L4 | compliance_check | AuditLedger 审计账本 | decision/governance/gov_001 | - | - | design | planned |
| 157 | L4 | compliance_check | DDDRuleEnforcer DDD铁律执行器 | decision/governance/gov_002 | - | - | design | planned |
| 158 | L4 | compliance_check | DecisionProvenance 决策溯源链 | decision/governance/gov_003 | - | - | design | planned |
| 159 | L4 | compliance_check | PhaseGateManager 阶段门禁管理 | decision/governance/gov_004 | - | - | design | planned |
| 160 | L4 | compliance_check | ConstitutionalGuard 宪法守卫 | decision/governance/gov_005 | - | - | design | planned |
| 161 | L4 | compliance_check | ComplianceAuditor 合规审计器 | decision/governance/gov_006 | - | - | design | planned |
| 162 | L4 | compliance_check | IncidentResponse 事件响应与升级 | decision/governance/gov_007 | - | - | design | planned |
| 163 | L4 | compliance_check | SystemTopologyAuditor 系统拓扑审计 | decision/governance/gov_008 | - | - | design | planned |
| 164 | L4 | compliance_check | 决策疲劳检测 Decision Fatigue Detection | decision/governance/gov_009 | - | - | design | planned |
| 165 | L4 | compliance_check | Agent辩论机制 Agent Debate | decision/governance/gov_010 | - | - | design | planned |
| 166 | L4 | compliance_check | AI Compliance Validator AI合规验证 | decision/compliance/cmp_01 | - | - | design | planned |
| 167 | L4 | compliance_check | 决策溯源链 Decision Provenance Chain | decision/compliance/cmp_02 | - | - | design | planned |
| 168 | L4 | compliance_check | TraceCompleteness TC≥0.997 | decision/compliance/cmp_03 | - | - | design | planned |
| 169 | L4 | compliance_check | AI合规边界 Tier 1/2/3风险分级 | decision/compliance/cmp_04 | - | - | design | planned |
| 170 | L4 | compliance_check | Pre-Trade合规检查三模式 Pre-Trade 3-Mode Check | decision/compliance/cmp_05 | - | - | design | planned |
| 171 | L4 | compliance_check | Kill Switch <1秒响应 Kill Switch <1s Response | decision/compliance/cmp_06 | - | - | design | planned |
| 172 | L4 | compliance_check | 人类监督四层级 L0~L3 Human Oversight 4-Level | decision/compliance/cmp_07 | - | - | design | planned |
| 173 | L4 | compliance_check | AI决策可追溯性 AI Decision Traceability | decision/compliance/cmp_08 | - | - | design | planned |
| 174 | L4 | compliance_check | AI决策可解释性门控 AI Decision Explainability Gate | decision/compliance/cmp_09 | - | - | design | planned |
| 175 | L4 | compliance_check | 监管报告 Regulatory Report | decision/compliance/cmp_10 | - | - | design | planned |
| 176 | L4 | compliance_check | 法域冲突解决 CrossBorderReg Navigator | decision/compliance/cmp_11 | - | - | design | planned |
| 195 | L4 | compliance_check | AISGGate 九层防御 L0-L8 | decision/security/sec_001 | - | - | design | planned |
| 196 | L4 | compliance_check | ACLGuard Kill Switch执行 | decision/security/sec_009a | - | - | design | planned |
| 197 | L4 | compliance_check | Kill Switch紧急熔断 Kill Switch Emergency | decision/security/sec_009b | - | - | design | planned |
| 198 | L4 | compliance_check | Secret Manager 密钥管理 | decision/security/sec_007 | - | - | design | planned |
| 199 | L4 | compliance_check | Self-Protect 自保护 | decision/security/sec_008 | - | - | design | planned |
| 207 | L4 | compliance_check | LLM Gateway 推理网关 LLM Gateway | decision/security/sec_010 | - | - | design | planned |
| 208 | L4 | compliance_check | 推理熔断器 Inference Circuit Breaker | decision/security/sec_011 | - | - | design | planned |
