---
ttl: permanent
doc_type: architecture_view
generator: generate_trading_flow_diagram.py
---

# 交易决策总指挥图（全流程全景）

> 本图包含全部 141 个决策节点（按6阶段 subgraph 分层）+ 136 条决策边（含跨阶段）。
> 一张图看懂「钱怎么赚」的完整交易决策流程。

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/07_trading_decision_architecture/_zoomable_html/00_panorama.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 怎么看这张图

1. **6 个 subgraph** = 6 个业务阶段（选股→买入→卖出→仓位→执行→对账），从上到下是钱的流向
2. **节点颜色**：🟦 蓝色=运营态(production, 已上线) ｜ 🟧 橙色虚线=设计态(design, 待施工)
3. **边样式**：实线=运营态依赖 ｜ 虚线=非运营态依赖（含设计态/混合）
4. **跨阶段边**：连接不同 subgraph 的边，体现阶段间数据/触发流转
5. 网页版可 Ctrl+滚轮无限缩放，拖动平移查看每个节点细节

## 各阶段分图

- [选股决策流](01_stock_selection.md)（5 节点）
- [买入决策流](02_buy_flow.md)（13 节点）
- [卖出决策流](03_sell_flow.md)（19 节点）
- [仓位裁决](04_position_flow.md)（37 节点）
- [执行](05_execution_flow.md)（56 节点）
- [对账](06_reconciliation.md)（11 节点）

## 总指挥图（Mermaid）

> 全部决策节点 + 决策边。大图请在 HTML 网页版查看（Ctrl+滚轮缩放）。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': '#eaeaea', 'clusterBorder': '#888888', 'fontSize': '14px'}}}%%
flowchart TD
    subgraph S_stock_selection["选股决策流（5节点）"]
    n190["(设计态 / design) 末位淘汰 IC-Based Factor Replacement<br/>signal | L2A | decision/factor/fc_01"]
    n191["(设计态 / design) 批量裁剪 Batch Factor Pruning<br/>signal | L2A | decision/factor/fc_02"]
    n192["(设计态 / design) Multi-Source Priority Router 多源优先级路由<br/>signal | L2A | decision/data/dt_01"]
    n193["(设计态 / design) Cross-Source Reconciler 多源对账<br/>signal | L2A | decision/data/dt_02"]
    n194["(设计态 / design) Multi-Timeframe Fusion 跨频率融合<br/>signal | L2A | decision/data/dt_03"]
    end
    subgraph S_buy_flow["买入决策流（13节点）"]
    n177["(设计态 / design) Synthesizer 信号合成+权重分配<br/>signal | L2A | decision/signal/sg_01"]
    n178["(设计态 / design) Signal Priority Router 信号优先级路由<br/>signal | L2A | decision/signal/sg_02"]
    n179["(设计态 / design) LLM Strategy Agent LLM策略Agent<br/>signal | L2A | decision/signal/sg_03"]
    n180["(设计态 / design) Signal Tail Risk Protector 信号尾部风险保护<br/>signal | L2A | decision/signal/sg_04"]
    n181["(设计态 / design) A-Share Plan Conformity Evaluator A股计划吻合度评估<br/>signal | L2A | decision/signal/sg_05"]
    n182["(设计态 / design) A-Share Emergency Opportunity Evaluator A股应急机会评估<br/>signal | L2A | decision/signal/sg_06"]
    n183["(设计态 / design) A-Share Capital-Force Conflict Arbiter 主力游资冲突仲裁<br/>signal | L2A | decision/signal/sg_07"]
    n184["(设计态 / design) Regime Special Override Priority Manager Regime特殊覆盖优先级<br/>signal | L2A | decision/signal/sg_08"]
    n185["(设计态 / design) Risk-Signal Interaction Sequencer 风控-信号交互时序<br/>signal | L2A | decision/signal/sg_09"]
    n186["(设计态 / design) 36环节决策框架实现器 36-Step Decision Framework<br/>signal | L2A | decision/signal/sg_10"]
    n187["(设计态 / design) 策略替换与淘汰决策器 Strategy Replacement Decision<br/>signal | L2A | decision/signal/sg_11"]
    n188["(设计态 / design) 信号冲突解决 Signal Conflict Resolution<br/>signal | L2A | decision/signal/sg_12"]
    n189["(设计态 / design) 信号融合模块 Signal Fusion Module<br/>signal | L2A | decision/signal/sg_13"]
    end
    subgraph S_sell_flow["卖出决策流（19节点）"]
    n1["(设计态 / design) 卖出决策域入口 Sell Decision Entry<br/>sell_decision | L2A | decision/sell/sell_00"]
    n2["(设计态 / design) 止盈信号 Take-Profit Signal<br/>sell_decision | L2A | decision/sell/sell_01"]
    n3["(设计态 / design) 止损信号 Stop-Loss Signal<br/>sell_decision | L2A | decision/sell/sell_02"]
    n4["(设计态 / design) 移动止损 Trailing Stop<br/>sell_decision | L2A | decision/sell/sell_03"]
    n5["(设计态 / design) 主力出货信号 Main Force Distribution Signal<br/>sell_decision | L2A | decision/sell/sell_04"]
    n6["(设计态 / design) 量价背离卖出 Volume-Price Divergence Sell<br/>sell_decision | L2A | decision/sell/sell_05"]
    n7["(设计态 / design) 突破关键位卖出 Key-Level Breakdown Sell<br/>sell_decision | L2A | decision/sell/sell_06"]
    n8["(设计态 / design) Watch List 实时卖出 Watch List Realtime Sell<br/>sell_decision | L2A | decision/sell/sell_07"]
    n9["(设计态 / design) Monitor List 定期扫描 Monitor List Periodic Scan<br/>sell_decision | L2A | decision/sell/sell_08"]
    n10["(设计态 / design) 卖出信号融合仲裁 Sell Signal Fusion Arbiter<br/>sell_decision | L2A | decision/sell/sell_09"]
    n11["(设计态 / design) 买卖冲突仲裁 Buy-Sell Conflict Arbiter<br/>sell_decision | L2A | decision/sell/sell_10"]
    n12["(设计态 / design) 部分卖出vs全部清仓决策 Partial vs Full Sell Decision<br/>sell_decision | L2A | decision/sell/sell_11"]
    n13["(设计态 / design) D-S证据理论融合 D-S Evidence Theory Fusion<br/>sell_decision | L2A | decision/sell/sell_12"]
    n14["(设计态 / design) 做T决策协调 T-Trade Coordinator<br/>sell_decision | L2A | decision/sell/sell_13"]
    n15["(设计态 / design) 黑天鹅强制卖出 Black Swan Forced Sell<br/>sell_decision | L2A | decision/sell/sell_14"]
    n16["(设计态 / design) Gap开盘决策框架 Gap Opening Decision Framework<br/>sell_decision | L2A | decision/sell/sell_15"]
    n17["(设计态 / design) 强制清仓信号 Forced Liquidation Signal<br/>sell_decision | L2A | decision/sell/sell_16"]
    n18["(设计态 / design) 卖出降级模式 Sell Degradation Mode<br/>sell_decision | L2A | decision/sell/sell_17"]
    n19["(设计态 / design) 卖出决策闭环优化 Sell Decision Closed-Loop<br/>sell_decision | L2A | decision/sell/sell_18"]
    end
    subgraph S_position_management["仓位裁决（37节点）"]
    n20["(设计态 / design) 组合核心引擎 Portfolio Core Engine<br/>portfolio_target | L3 | decision/pf_core/pc_01"]
    n21["(设计态 / design) 半Kelly硬上限 Half-Kelly Hard Cap<br/>portfolio_target | L3 | decision/pf_core/pc_02"]
    n22["(设计态 / design) 风险预算 Risk Budget<br/>portfolio_target | L3 | decision/pf_core/pc_03"]
    n23["(设计态 / design) 再平衡决策 Rebalance Decision<br/>portfolio_target | L3 | decision/pf_core/pc_04"]
    n24["(设计态 / design) 仲裁优先级体系 Arbitration Priority<br/>portfolio_target | L3 | decision/pf_core/pc_05"]
    n25["(设计态 / design) 多策略共振融合 Strategy Convergence Fusion<br/>portfolio_target | L3 | decision/pf_core/pc_06"]
    n26["(设计态 / design) 因子直通裁决 Factor Bypass Arbitration<br/>portfolio_target | L3 | decision/pf_core/pc_07"]
    n27["(设计态 / design) 元策略路由 Meta-Strategy Router<br/>portfolio_target | L3 | decision/pf_core/pc_08"]
    n28["(设计态 / design) 组合优化 Portfolio Optimization<br/>portfolio_target | L3 | decision/pf_core/pc_09"]
    n29["(设计态 / design) 资本分配 Capital Allocation<br/>portfolio_target | L3 | decision/pf_core/pc_10"]
    n30["(设计态 / design) 决策编排器 Decision Orchestrator<br/>portfolio_target | L3 | decision/pf_core/pc_11"]
    n31["(设计态 / design) 四轨融合器 Multi-Track Fusion<br/>portfolio_target | L3 | decision/pf_core/pc_12"]
    n32["(设计态 / design) 策略分配 Strategy Allocation<br/>portfolio_target | L3 | decision/pf_alloc/pa_01"]
    n33["(设计态 / design) 风险平价 Risk Parity<br/>portfolio_target | L3 | decision/pf_alloc/pa_02"]
    n34["(设计态 / design) 动态权重 Dynamic Weighting<br/>portfolio_target | L3 | decision/pf_alloc/pa_03"]
    n35["(设计态 / design) 策略权重再平衡 Strategy Weight Rebalance<br/>portfolio_target | L3 | decision/pf_alloc/pa_04"]
    n36["(设计态 / design) 多策略共识 Multi-Strategy Consensus<br/>portfolio_target | L3 | decision/pf_alloc/pa_05"]
    n37["(设计态 / design) 元策略选择 Meta-Strategy Selection<br/>portfolio_target | L3 | decision/pf_alloc/pa_06"]
    n38["(设计态 / design) 仓位唯一裁决中心 C-047 Position Sole Arbiter<br/>portfolio_target | L3 | decision/position/pos_01"]
    n39["(设计态 / design) 持仓状态机 Position State Machine<br/>portfolio_target | L3 | decision/position/pos_02"]
    n40["(设计态 / design) 仓位漂移监控 Position Drift Monitor<br/>portfolio_target | L3 | decision/position/pos_03"]
    n41["(设计态 / design) Kelly仓位决策 Kelly Position Decision<br/>portfolio_target | L3 | decision/position/pos_04"]
    n42["(设计态 / design) 风险配额 Risk Quota<br/>portfolio_target | L3 | decision/position/pos_05"]
    n43["(设计态 / design) 11种市场状态→仓位上限 Market State Position Cap<br/>portfolio_target | L3 | decision/position/pos_06"]
    n44["(设计态 / design) 组合层决策 Portfolio Layer Decision<br/>portfolio_target | L3 | decision/position/pos_07"]
    n45["(设计态 / design) 策略层决策 Strategy Layer Decision<br/>portfolio_target | L3 | decision/position/pos_08"]
    n46["(设计态 / design) 标层决策 Instrument Layer Decision<br/>portfolio_target | L3 | decision/position/pos_09"]
    n47["(设计态 / design) 动态层决策 Dynamic Layer Decision<br/>portfolio_target | L3 | decision/position/pos_10"]
    n48["(设计态 / design) 再平衡触发 Rebalance Trigger<br/>portfolio_target | L3 | decision/position/pos_11"]
    n49["(设计态 / design) 仓位上限硬约束 Position Cap Hard Constraint<br/>portfolio_target | L3 | decision/position/pos_12"]
    n50["(设计态 / design) REDUCING→EXITING状态转换 REDUCING to EXITING<br/>portfolio_target | L3 | decision/position/pos_13"]
    n51["(设计态 / design) 风险预算→Kelly决策 Risk Budget to Kelly<br/>portfolio_target | L3 | decision/position/pos_14"]
    n52["(设计态 / design) 半Kelly硬上限 Half-Kelly Hard Cap<br/>portfolio_target | L3 | decision/position/pos_15"]
    n53["(设计态 / design) 仓位降级 Position Degradation<br/>portfolio_target | L3 | decision/position/pos_16"]
    n54["(设计态 / design) 持仓状态→卖出阈值 Position State to Sell Threshold<br/>portfolio_target | L3 | decision/position/pos_17"]
    n55["(设计态 / design) 仓位四轨决策 Position Four-Track Decision<br/>portfolio_target | L3 | decision/position/pos_18"]
    n56["(设计态 / design) 仓位裁决→执行 Position Arbitration to Execution<br/>portfolio_target | L3 | decision/position/pos_19"]
    end
    subgraph S_execution["执行（56节点）"]
    n57["(设计态 / design) Pre-Trade主链6项检查 Pre-Trade Main Chain 6 Checks<br/>compliance_check | L4 | decision/ex_core/ex_01"]
    n58["(设计态 / design) Kill Switch 5层防御 Kill Switch 5-Layer Defense<br/>risk_check | L4 | decision/ex_core/ex_02"]
    n59["(设计态 / design) 50ms SLA Fail-Closed 50ms SLA Fail-Closed<br/>order | L3 | decision/ex_core/ex_03"]
    n60["(设计态 / design) Saga编排式事务 Saga Orchestrated Transaction<br/>order | L3 | decision/ex_core/ex_04"]
    n61["(设计态 / design) 风控检查 Risk Check<br/>order | L3 | decision/ex_core/ex_05"]
    n62["(设计态 / design) 信号确认 Signal Confirmation<br/>order | L3 | decision/ex_core/ex_06"]
    n63["(设计态 / design) 下单提交 Order Submit<br/>order | L3 | decision/ex_core/ex_07"]
    n64["(设计态 / design) 成交确认 Fill Confirmation<br/>order | L3 | decision/ex_core/ex_08"]
    n65["(设计态 / design) 持仓更新 Position Update<br/>order | L3 | decision/ex_core/ex_09"]
    n66["(设计态 / design) 报告生成 Report Generation<br/>order | L3 | decision/ex_core/ex_10"]
    n67["(设计态 / design) Kill Switch AI自动激活 Kill Switch AI Auto Trigger<br/>risk_check | L4 | decision/ex_core/ex_11"]
    n68["(设计态 / design) Kill Switch人工激活 Kill Switch Manual Trigger<br/>risk_check | L4 | decision/ex_core/ex_12"]
    n69["(设计态 / design) Kill Switch定时激活 Kill Switch Timer Trigger<br/>risk_check | L4 | decision/ex_core/ex_13"]
    n70["(设计态 / design) Kill Switch外部信号激活 Kill Switch External Signal<br/>risk_check | L4 | decision/ex_core/ex_14"]
    n71["(设计态 / design) 流动性螺旋3阶段 Liquidity Spiral 3-Phase<br/>order | L3 | decision/ex_core/ex_15"]
    n72["(设计态 / design) 订单路由决策 Order Routing Decision<br/>order | L3 | decision/ex_sor/ex_16"]
    n73["(设计态 / design) SOR路由决策延迟 SOR Routing Latency<br/>order | L3 | decision/ex_sor/ex_17"]
    n74["(设计态 / design) 券商连接熔断+故障转移 Broker Circuit Breaker<br/>risk_check | L4 | decision/ex_sor/ex_18"]
    n75["(设计态 / design) 交易通道熔断人工恢复 Trading Channel Manual Recovery<br/>order | L3 | decision/ex_sor/ex_19"]
    n76["(设计态 / design) Pre-Trade合规检查流水线 Pre-Trade Compliance Pipeline<br/>compliance_check | L4 | decision/ex_sor/ex_20"]
    n77["(设计态 / design) Kill-Switch四级阶梯 Kill-Switch 4-Level Cascade<br/>order | L3 | decision/ex_sor/ex_21"]
    n78["(设计态 / design) 熔断器矩阵 Circuit Breaker Matrix<br/>order | L3 | decision/ex_sor/ex_22"]
    n79["(设计态 / design) 行为准入门禁 Behavioral Admission Gateway<br/>compliance_check | L4 | decision/ex_sor/ex_23"]
    n80["(设计态 / design) 风控熔断事件 Risk Circuit Breaker Event<br/>risk_check | L4 | decision/risk/rk_01"]
    n81["(设计态 / design) 三层防线 Three Defense Lines<br/>risk_check | L4 | decision/risk/rk_02"]
    n82["(设计态 / design) 双引擎风控 Dual Engine Risk<br/>risk_check | L4 | decision/risk/rk_03"]
    n83["(设计态 / design) 4级风控决策门控 4-Level Risk Decision Gate<br/>risk_check | L4 | decision/risk/rk_04"]
    n84["(设计态 / design) 压力测试引擎 Stress Test Engine<br/>risk_check | L4 | decision/risk/rk_05"]
    n85["(设计态 / design) 黑天鹅模式库 Black Swan Pattern Library<br/>risk_check | L4 | decision/risk/rk_06"]
    n86["(设计态 / design) 流动性危机模拟 Liquidity Crisis Simulation<br/>risk_check | L4 | decision/risk/rk_07"]
    n87["(设计态 / design) 反向压力测试4步法 Reverse Stress Test 4-Step<br/>risk_check | L4 | decision/risk/rk_08"]
    n88["(设计态 / design) 二阶效应与传染模型 Second-Order Effect Model<br/>risk_check | L4 | decision/risk/rk_09"]
    n89["(设计态 / design) 风控否决权 Risk Veto<br/>risk_check | L4 | decision/risk/rk_10"]
    n90["(设计态 / design) 风控状态 Risk State<br/>risk_check | L4 | decision/risk/rk_11"]
    n91["(设计态 / design) 风控参数变更审批 Risk Parameter Approval<br/>risk_check | L4 | decision/risk/rk_12"]
    n92["(设计态 / design) 熔断恢复确认 Circuit Breaker Recovery Confirm<br/>risk_check | L4 | decision/risk/rk_13"]
    n93["(设计态 / design) OBSERVING软止损观察期 OBSERVING Soft Stop<br/>risk_check | L4 | decision/risk/rk_14"]
    n94["(设计态 / design) 风险预算 Risk Budget<br/>risk_check | L4 | decision/risk/rk_15"]
    n95["(设计态 / design) VaR计算 VaR Calculation<br/>risk_check | L4 | decision/risk/rk_16"]
    n96["(设计态 / design) 回撤监控 Drawdown Monitor<br/>risk_check | L4 | decision/risk/rk_17"]
    n97["(设计态 / design) 风控信号交互时序 Risk-Signal Timing<br/>risk_check | L4 | decision/risk/rk_18"]
    n98["(设计态 / design) 风控事件 Risk Event<br/>risk_check | L4 | decision/risk/rk_19"]
    n99["(设计态 / design) FLATTEN硬编码触发 FLATTEN Hardcoded Trigger<br/>risk_check | L4 | decision/risk/rk_20"]
    n100["(设计态 / design) 5级风险否决引擎 5-Level Risk Veto Engine<br/>risk_check | L4 | decision/risk/rk_21"]
    n101["(设计态 / design) Pod级止损 Pod-Level Stop Loss<br/>risk_check | L4 | decision/risk/rk_22"]
    n102["(设计态 / design) 外部订单观察者 External Order Watcher<br/>order | L3 | decision/trading/trd_01"]
    n103["(设计态 / design) 结算引擎 Settlement Engine<br/>order | L3 | decision/trading/trd_02"]
    n104["(设计态 / design) 公司行动 Corporate Action<br/>order | L3 | decision/trading/trd_03"]
    n105["(设计态 / design) 保证金管理 Margin Manager<br/>order | L3 | decision/trading/trd_04"]
    n106["(设计态 / design) 多账户 Multi-Account<br/>order | L3 | decision/trading/trd_05"]
    n107["(设计态 / design) 微信枢纽 WeChat Hub<br/>order | L3 | decision/trading/trd_06"]
    n108["(设计态 / design) C-013 4级优先级 C-013 4-Level Priority<br/>order | L3 | decision/trading/trd_07"]
    n109["(设计态 / design) A股交易纪律四项必做 A-Share Trading 4-Do<br/>order | L3 | decision/trading/trd_08"]
    n110["(设计态 / design) A股交易纪律四项严禁 A-Share Trading 4-Forbidden<br/>order | L3 | decision/trading/trd_09"]
    n111["(设计态 / design) 监管报送 Regulatory Reporting<br/>order | L3 | decision/trading/trd_10"]
    n112["(设计态 / design) 盘中即时反应决策引擎 Intraday Instant Reaction Decision Engine<br/>order | L3 | decision/trading/trd_11"]
    end
    subgraph S_reconciliation["对账（11节点）"]
    n166["(设计态 / design) AI Compliance Validator AI合规验证<br/>compliance_check | L4 | decision/compliance/cmp_01"]
    n167["(设计态 / design) 决策溯源链 Decision Provenance Chain<br/>compliance_check | L4 | decision/compliance/cmp_02"]
    n168["(设计态 / design) TraceCompleteness TC≥0.997<br/>compliance_check | L4 | decision/compliance/cmp_03"]
    n169["(设计态 / design) AI合规边界 Tier 1/2/3风险分级<br/>compliance_check | L4 | decision/compliance/cmp_04"]
    n170["(设计态 / design) Pre-Trade合规检查三模式 Pre-Trade 3-Mode Check<br/>compliance_check | L4 | decision/compliance/cmp_05"]
    n171["(设计态 / design) Kill Switch <1秒响应 Kill Switch <1s Response<br/>compliance_check | L4 | decision/compliance/cmp_06"]
    n172["(设计态 / design) 人类监督四层级 L0~L3 Human Oversight 4-Level<br/>compliance_check | L4 | decision/compliance/cmp_07"]
    n173["(设计态 / design) AI决策可追溯性 AI Decision Traceability<br/>compliance_check | L4 | decision/compliance/cmp_08"]
    n174["(设计态 / design) AI决策可解释性门控 AI Decision Explainability Gate<br/>compliance_check | L4 | decision/compliance/cmp_09"]
    n175["(设计态 / design) 监管报告 Regulatory Report<br/>compliance_check | L4 | decision/compliance/cmp_10"]
    n176["(设计态 / design) 法域冲突解决 CrossBorderReg Navigator<br/>compliance_check | L4 | decision/compliance/cmp_11"]
    end
    n192 -.-> n193
    n193 -.-> n194
    n194 -.-> n190
    n190 -.-> n191
    n1 -.-> n2
    n2 -.-> n3
    n3 -.-> n4
    n4 -.-> n5
    n5 -.-> n6
    n6 -.-> n7
    n7 -.-> n8
    n8 -.-> n9
    n9 -.-> n10
    n10 -.-> n11
    n11 -.-> n12
    n12 -.-> n13
    n13 -.-> n14
    n14 -.-> n15
    n15 -.-> n16
    n16 -.-> n17
    n17 -.-> n18
    n18 -.-> n19
    n19 -.-> n177
    n177 -.-> n178
    n178 -.-> n179
    n179 -.-> n180
    n180 -.-> n181
    n181 -.-> n182
    n182 -.-> n183
    n183 -.-> n184
    n184 -.-> n185
    n185 -.-> n186
    n186 -.-> n187
    n187 -.-> n188
    n188 -.-> n189
    n59 -.-> n60
    n60 -.-> n61
    n61 -.-> n62
    n62 -.-> n63
    n63 -.-> n64
    n64 -.-> n65
    n65 -.-> n66
    n66 -.-> n71
    n71 -.-> n72
    n72 -.-> n73
    n73 -.-> n75
    n75 -.-> n77
    n77 -.-> n78
    n78 -.-> n32
    n32 -.-> n33
    n33 -.-> n34
    n34 -.-> n35
    n35 -.-> n36
    n36 -.-> n37
    n37 -.-> n20
    n20 -.-> n21
    n21 -.-> n22
    n22 -.-> n23
    n23 -.-> n24
    n24 -.-> n25
    n25 -.-> n26
    n26 -.-> n27
    n27 -.-> n28
    n28 -.-> n29
    n29 -.-> n30
    n30 -.-> n31
    n31 -.-> n38
    n38 -.-> n39
    n39 -.-> n40
    n40 -.-> n41
    n41 -.-> n42
    n42 -.-> n43
    n43 -.-> n44
    n44 -.-> n45
    n45 -.-> n46
    n46 -.-> n47
    n47 -.-> n48
    n48 -.-> n49
    n49 -.-> n50
    n50 -.-> n51
    n51 -.-> n52
    n52 -.-> n53
    n53 -.-> n54
    n54 -.-> n55
    n55 -.-> n56
    n56 -.-> n102
    n102 -.-> n103
    n103 -.-> n104
    n104 -.-> n105
    n105 -.-> n106
    n106 -.-> n107
    n107 -.-> n108
    n108 -.-> n109
    n109 -.-> n110
    n110 -.-> n111
    n111 -.-> n112
    n166 -.-> n167
    n167 -.-> n168
    n168 -.-> n169
    n169 -.-> n170
    n170 -.-> n171
    n171 -.-> n172
    n172 -.-> n173
    n173 -.-> n174
    n174 -.-> n175
    n175 -.-> n176
    n176 -.-> n57
    n57 -.-> n58
    n58 -.-> n67
    n67 -.-> n68
    n68 -.-> n69
    n69 -.-> n70
    n70 -.-> n74
    n74 -.-> n76
    n76 -.-> n79
    n80 -.-> n81
    n81 -.-> n82
    n82 -.-> n83
    n83 -.-> n84
    n84 -.-> n85
    n85 -.-> n86
    n86 -.-> n87
    n87 -.-> n88
    n88 -.-> n89
    n89 -.-> n90
    n90 -.-> n91
    n91 -.-> n92
    n92 -.-> n93
    n93 -.-> n94
    n94 -.-> n95
    n95 -.-> n96
    n96 -.-> n97
    n97 -.-> n98
    n98 -.-> n99
    n99 -.-> n100
    n100 -.-> n101
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    class n1,n2,n3,n4,n5,n6,n7,n8,n9,n10,n11,n12,n13,n14,n15,n16,n17,n18,n19,n20,n21,n22,n23,n24,n25,n26,n27,n28,n29,n30,n31,n32,n33,n34,n35,n36,n37,n38,n39,n40,n41,n42,n43,n44,n45,n46,n47,n48,n49,n50,n51,n52,n53,n54,n55,n56,n57,n58,n59,n60,n61,n62,n63,n64,n65,n66,n67,n68,n69,n70,n71,n72,n73,n74,n75,n76,n77,n78,n79,n80,n81,n82,n83,n84,n85,n86,n87,n88,n89,n90,n91,n92,n93,n94,n95,n96,n97,n98,n99,n100,n101,n102,n103,n104,n105,n106,n107,n108,n109,n110,n111,n112,n166,n167,n168,n169,n170,n171,n172,n173,n174,n175,n176,n177,n178,n179,n180,n181,n182,n183,n184,n185,n186,n187,n188,n189,n190,n191,n192,n193,n194 design
```

> 数据源：depgraph (PostgreSQL) decision_nodes + decision_edges（flow_stage 已标定节点）
