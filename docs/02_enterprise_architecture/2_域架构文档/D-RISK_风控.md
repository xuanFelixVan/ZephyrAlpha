---
doc_type: domain_architecture_doc
title: D-RISK 风控架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-RISK 风控架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-RISK |
| 域名称 | 风控 |
| 架构层 | L2_domain |
| 模块总数 | 775 |
| 设计态模块 | 749 |
| 原型态模块 | 11 |
| 生产态模块 | 9 |
| 容量 | 9/150 (正常) |
| 描述 | 风险度量、风险限额、压力测试、实时风控。交易安全阀。 |

## 模块清单

共 775 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-RISK/4级风控决策 APPROVE/REDUCE/REJECT/FLATTEN |  | design_only | design | 0 | 0 |
| D-RISK/A Share Compliance Rule A股合规规则代管 |  | design_only | design | 0 | 0 |
| D-RISK/A-Share 5-Signal Systemic Risk Scanner A股5信号系统性风险扫描器 |  | design_only | design | 0 | 0 |
| D-RISK/A-Share Cascading Circuit Breaker A股级联熔断器 |  | design_only | design | 0 | 0 |
| D-RISK/A-Share Compliance Custody A股合规代管 |  | design_only | design | 0 | 0 |
| D-RISK/A-Share Contrarian Dedicated Stop-Loss A股逆向专用止损 |  | design_only | design | 0 | 0 |
| D-RISK/A-Share Contrarian Time-Based Stop-Loss A股逆向时间止损 |  | design_only | design | 0 | 0 |
| D-RISK/A-Share First-Minute Stop-Loss Executor A股首分钟止损执行器 |  | design_only | design | 0 | 0 |
| D-RISK/A-Share Loss Limit Enforcer A股亏损限额强制执行 |  | design_only | design | 0 | 0 |
| D-RISK/A-Share Multi-Level Loss Circuit Breaker A股多级亏损熔断器 |  | design_only | design | 0 | 0 |
| D-RISK/A-Share PDF Tail Risk Auto-Hedger A股PDF尾部风险自动对冲器 |  | design_only | design | 0 | 0 |
| D-RISK/A-Share Stock Blacklist Manager A股股票黑名单管理器 |  | design_only | design | 0 | 0 |
| D-RISK/A-Share Stop Loss 6 Patterns A股特色止损6种模式 |  | design_only | design | 0 | 0 |
| D-RISK/A-Share Stop Loss A股止损 |  | design_only | design | 0 | 0 |
| D-RISK/A-Share Stop-Loss Rule Engine A股止损规则引擎 |  | design_only | design | 0 | 0 |
| D-RISK/A-Share Stop-Loss Rule Engine A股特色止损 |  | design_only | design | 0 | 0 |
| D-RISK/A-Share Stop-Loss/Circuit Breaker Series A股特色止损/熔断系列 |  | design_only | design | 0 | 0 |
| D-RISK/A-Share Systemic Risk 3-Level Alerter A股系统性风险三级告警器 |  | design_only | design | 0 | 0 |
| D-RISK/A-Share Systemic Risk 5 Signals A股系统性风险5信号 |  | design_only | design | 0 | 0 |
| D-RISK/A-Share Systemic Risk Detector A股系统性风险检测 |  | design_only | design | 0 | 0 |
| D-RISK/A-Share Systemic Risk Detector A股系统性风险检测器 |  | design_only | design | 0 | 0 |
| D-RISK/A6合规架构何时激活 A6 Compliance Activation |  | design_only | design | 0 | 0 |
| D-RISK/AI Agent Risk AI/Agent风险 |  | design_only | design | 0 | 0 |
| D-RISK/AI Agent Risk Governance AI/Agent风险治理 |  | design_only | design | 0 | 0 |
| D-RISK/AI Agent Risk Governance Bounded Autonomy AI/Agent风险治理有界自治 |  | design_only | design | 0 | 0 |
| D-RISK/AI Agent Specific Risk AI/Agent特有风险 |  | design_only | design | 0 | 0 |
| D-RISK/AI Cannot Directly Modify Risk Parameters AI不可直接修改风控参数 |  | design_only | design | 0 | 0 |
| D-RISK/AI Risk Engine Implementer AI风控引擎实现器 |  | design_only | design | 0 | 0 |
| D-RISK/AI-Enhanced Risk Engine AI增强风控引擎 |  | design_only | design | 0 | 0 |
| D-RISK/AI/Agent Risk AI/Agent风险 |  | design_only | design | 0 | 0 |
| D-RISK/AI/Agent特有风险 AI/Agent Specific Risk |  | design_only | design | 0 | 0 |
| D-RISK/AISG Regulatory Compliance Checker AISG监管合规检查器 |  | design_only | design | 0 | 0 |
| D-RISK/AI自动触发 AI Auto Trigger |  | design_only | design | 0 | 0 |
| D-RISK/APPROVE Risk Decision 风险 |  | design_only | design | 0 | 0 |
| D-RISK/ARA五项原则 ARA Five Principles |  | design_only | design | 0 | 0 |
| D-RISK/ARA治理方程 ARA Governance Equation |  | design_only | design | 0 | 0 |
| D-RISK/ARS双轨结算模型 ARS Dual-Track Settlement |  | design_only | design | 0 | 0 |
| D-RISK/ARS状态机语义 ARS State Machine Semantics |  | design_only | design | 0 | 0 |
| D-RISK/ATR Dynamic Stop Loss Calculator ATR动态止损计算器 |  | design_only | design | 0 | 0 |
| D-RISK/ATR动态止损与Bayesian参数优化模型 ATR Dynamic Stop-Loss Model |  | design_only | design | 0 | 0 |
| D-RISK/ATR动态止盈 ATR Dynamic Take Profit |  | design_only | design | 0 | 0 |
| D-RISK/Abnormal Trade Detection Interceptor 异常交易检测拦截器 |  | design_only | design | 0 | 0 |
| D-RISK/Agent Boundary Violation Agent越界行为 |  | design_only | design | 0 | 0 |
| D-RISK/Agent Strategy Drift Must Be Detected Agent策略漂移必须被检测 |  | design_only | design | 0 | 0 |
| D-RISK/Agent失控 Agent Out-of-Control |  | design_only | design | 0 | 0 |
| D-RISK/Agent红队测试 Agent Red Team Testing |  | design_only | design | 0 | 0 |
| D-RISK/Agent行为日志 Agent Behavior Log |  | design_only | design | 0 | 0 |
| D-RISK/Agent行为监控 Agent Behavior Monitor |  | design_only | design | 0 | 0 |
| D-RISK/Agent行为监控 Agent Behavior Monitoring |  | design_only | design | 0 | 0 |
| D-RISK/Almgren-Chriss Impact Model Almgren-Chriss冲击模型 |  | design_only | design | 0 | 0 |
| D-RISK/Almgren-Chriss Optimal Execution Framework Almgren-Chriss最优执行框架 |  | design_only | design | 0 | 0 |
| D-RISK/Almgren-Chriss最优执行框架 Almgren-Chriss Optimal Execution Framework |  | design_only | design | 0 | 0 |
| D-RISK/Amihud ILLIQ Amihud非流动性指标 |  | design_only | design | 0 | 0 |
| D-RISK/Amihud ILLIQ 非流动性指标 |  | design_only | design | 0 | 0 |
| D-RISK/Amihud Illiquidity Amihud非流动性指标 |  | design_only | design | 0 | 0 |
| D-RISK/Autoencoder重构异常检测 Autoencoder Anomaly Detection |  | design_only | design | 0 | 0 |
| D-RISK/A股风险日历 A-Share Risk Calendar |  | design_only | design | 0 | 0 |
| D-RISK/BFSI领域自适应红队 FinRedTeamBench |  | design_only | design | 0 | 0 |
| D-RISK/Basel III Multiplier Factor Manager Basel III乘数因子管理器 |  | design_only | design | 0 | 0 |
| D-RISK/Bayesian优化 Bayesian Optimization |  | design_only | design | 0 | 0 |
| D-RISK/Black Swan Pattern Library 黑天鹅模式库 |  | design_only | design | 0 | 0 |
| D-RISK/Black Swan Pattern Library 黑天鹅模式库7种模式 |  | design_only | design | 0 | 0 |
| D-RISK/Brinson模型 Brinson Model |  | design_only | design | 0 | 0 |
| D-RISK/C-004 风控 Risk Control |  | design_only | design | 0 | 0 |
| D-RISK/C-038 黑天鹅检测 Black Swan Detection |  | design_only | design | 0 | 0 |
| D-RISK/C/S Pattern C/S关系模式 |  | design_only | design | 0 | 0 |
| D-RISK/CER Cancellation-to-Execution Ratio 撤单成交比 |  | design_only | design | 0 | 0 |
| D-RISK/CTR-003 RiskLimits Producer CTR-003风险限额生产者 |  | design_only | design | 0 | 0 |
| D-RISK/CTR-004 Order Consumer CTR-004订单消费者 |  | design_only | design | 0 | 0 |
| D-RISK/CTR-006 PositionSnapshot Provider CTR-006仓位快照提供者 |  | design_only | design | 0 | 0 |
| D-RISK/CTR-P1-008 Risk Dashboard Snapshot CTR-P1-008风控仪表盘快照(代码实现) |  | design_only | design | 0 | 0 |
| D-RISK/CTR-P1-008 RiskDashboardSnapshot CTR-P1-008 RiskDashboardSnapshot契约 |  | design_only | design | 0 | 0 |
| D-RISK/CTR-P1-011 RiskMetricsReport CTR-P1-011 RiskMetricsReport契约 |  | design_only | design | 0 | 0 |
| D-RISK/CUSUM控制图 CUSUM Control Chart |  | design_only | design | 0 | 0 |
| D-RISK/CVaR/ES条件风险价值 Conditional Value at Risk |  | design_only | design | 0 | 0 |
| D-RISK/Carry持有成本 Carry |  | design_only | design | 0 | 0 |
| D-RISK/CheckResult CheckResult结构 |  | design_only | design | 0 | 0 |
| D-RISK/CheckResult 检查结果 |  | design_only | design | 0 | 0 |
| D-RISK/Circuit Breaker Trigger 熔断触发 |  | design_only | design | 0 | 0 |
| D-RISK/CircuitBreaker 熔断事件 |  | design_only | design | 0 | 0 |
| D-RISK/Climate Risk Engine 气候风险引擎 |  | design_only | design | 0 | 0 |
| D-RISK/CoVaR Cross-Market Contagion CoVaR跨市场传染 |  | design_only | design | 0 | 0 |
| D-RISK/CoVaR跨市场传染 |  | design_only | design | 0 | 0 |
| D-RISK/CoVaR跨市场传染 CoVaR Cross-Market Contagion |  | design_only | design | 0 | 0 |
| D-RISK/Collaborative Trading Behavior Detector 协同交易行为检测器 |  | design_only | design | 0 | 0 |
| D-RISK/Compliance Rule 合规规则(代码实现) |  | design_only | design | 0 | 0 |
| D-RISK/Concentration Exceeds Limit 集中度超限 |  | design_only | design | 0 | 0 |
| D-RISK/Concentration Limit Non-Breakable 集中度上限不可突破 |  | design_only | design | 0 | 0 |
| D-RISK/Concentration Risk Monitor 集中度风险监控器 |  | design_only | design | 0 | 0 |
| D-RISK/Concentration Risk Monitor集中度风险监控 |  | design_only | design | 0 | 0 |
| D-RISK/Configurable Rule Engine 可配置规则引擎 |  | design_only | design | 0 | 0 |
| D-RISK/Convexity凸性收益 Convexity |  | design_only | design | 0 | 0 |
| D-RISK/Correlation Collapse 相关性崩塌 |  | design_only | design | 0 | 0 |
| D-RISK/Counterfactual Analyzer 反事实分析器 |  | design_only | design | 0 | 0 |
| D-RISK/Counterparty Risk Manager 交易对手风险管理器 |  | design_only | design | 0 | 0 |
| D-RISK/Counterparty Risk 交易对手风险 |  | design_only | design | 0 | 0 |
| D-RISK/Covariance Matrix Decomposer 协方差矩阵分解器 |  | design_only | design | 0 | 0 |
| D-RISK/Credit Risk Engine信用风险引擎 |  | design_only | design | 0 | 0 |
| D-RISK/Credit Risk 信用风险 |  | design_only | design | 0 | 0 |
| D-RISK/Cross-Market Contagion 跨市场传导 |  | design_only | design | 0 | 0 |
| D-RISK/Crowding Risk Monitor 拥挤风险监控器 |  | design_only | design | 0 | 0 |
| D-RISK/Cumulative Drawdown Exceeds Limit 累计回撤超限 |  | design_only | design | 0 | 0 |
| D-RISK/Custom Risk Report Generator 风险报告自定义生成器 |  | design_only | design | 0 | 0 |
| D-RISK/D-AUTONOMY Readiness D-AUTONOMY就绪前提 |  | design_only | design | 0 | 0 |
| D-RISK/D-DATA Readiness D-DATA就绪前提 |  | design_only | design | 0 | 0 |
| D-RISK/D-FACTOR Readiness D-FACTOR就绪前提 |  | design_only | design | 0 | 0 |
| D-RISK/D-RISK 风险 |  | design_only | design | 0 | 0 |
| D-RISK/DPG七场景 DPG Seven Scenarios |  | design_only | design | 0 | 0 |
| D-RISK/Daily Loss Exceeds Limit 单日亏损超限 |  | design_only | design | 0 | 0 |
| D-RISK/Daily Loss Limit Invariant 日损失限额不变量 |  | design_only | design | 0 | 0 |
| D-RISK/Daily Risk Report Generator 每日风险报告生成器 |  | design_only | design | 0 | 0 |
| D-RISK/Default Position Limit Checker 默认持仓限额检查器(代码实现) |  | design_only | design | 0 | 0 |
| D-RISK/Default Risk Limits Calculator 默认风险限额计算器(代码实现) |  | design_only | design | 0 | 0 |
| D-RISK/Default Risk Manager Orchestrator 默认风控管理器编排器(代码实现) |  | design_only | design | 0 | 0 |
| D-RISK/Default Risk Validator 默认风控校验器(代码实现) |  | design_only | design | 0 | 0 |
| D-RISK/Default Stop Loss Engine 默认止损引擎(代码实现) |  | design_only | design | 0 | 0 |
| ...alidator to Configurable Rule Engine Migrator DefaultRiskValidator→可配置规则引擎迁移器 |  | design_only | design | 0 | 0 |
| D-RISK/Degraded Liquidity Mode 降级流动性模式 |  | design_only | design | 0 | 0 |
| D-RISK/Degraded 风控降级事件 |  | design_only | design | 0 | 0 |
| D-RISK/Distribution Fitting Engine 分布拟合引擎 |  | design_only | design | 0 | 0 |
| D-RISK/Dragon-Tiger List Verification 龙虎榜验证 |  | design_only | design | 0 | 0 |
| D-RISK/Drawdown Real-Time Tracker 回撤实时跟踪器 |  | design_only | design | 0 | 0 |
| D-RISK/DrawdownAlerted 回撤已告警 |  | design_only | design | 0 | 0 |
| D-RISK/Drift Detection Risk Closed Loop 漂移检测与风险闭环 |  | design_only | design | 0 | 0 |
| D-RISK/Drift Exceeded Model Must Degrade 漂移超限模型必须降级 |  | design_only | design | 0 | 0 |
| D-RISK/Drift Exceeds Limit 漂移超限 |  | design_only | design | 0 | 0 |
| D-RISK/Dual-Engine Routing 双引擎路由 |  | design_only | design | 0 | 0 |
| D-RISK/Dynamic Position Adjuster 动态仓位调整器 |  | design_only | design | 0 | 0 |
| D-RISK/E-RK-01 D-RISK→间接经PC-04事件 |  | design_only | design | 0 | 0 |
| D-RISK/E-RK-03 DrawdownAlerted E-RK-03 DrawdownAlerted事件 |  | design_only | design | 0 | 0 |
| D-RISK/E-SIM-03 StressTestResult 压力测试结果 |  | design_only | design | 0 | 0 |
| D-RISK/ESG Risk ESG风险 |  | design_only | design | 0 | 0 |
| D-RISK/ESRB 14个AI风险放大向量 ESRB 14 AI Risk Amplification Vectors |  | design_only | design | 0 | 0 |
| D-RISK/ESRB 2025系统性风险报告 |  | design_only | design | 0 | 0 |
| D-RISK/ESRB Concentration Risk Vector ESRB集中度风险向量 |  | design_only | design | 0 | 0 |
| D-RISK/ESRB Data Dependency Vector ESRB数据依赖向量 |  | design_only | design | 0 | 0 |
| D-RISK/ESRB Feedback Loop Vector ESRB反馈循环向量 |  | design_only | design | 0 | 0 |
| D-RISK/ESRB Interconnection Vector ESRB互联性向量 |  | design_only | design | 0 | 0 |
| D-RISK/ESRB Model Homogenization Vector ESRB模型同质化向量 |  | design_only | design | 0 | 0 |
| D-RISK/ESRB Network Vulnerability Vector ESRB网络漏洞向量 |  | design_only | design | 0 | 0 |
| D-RISK/ESRB Opacity Vector ESRB不透明性向量 |  | design_only | design | 0 | 0 |
| D-RISK/ESRB Operational Risk Vector ESRB操作风险向量 |  | design_only | design | 0 | 0 |
| D-RISK/ESRB Procyclicality Vector ESRB顺周期性向量 |  | design_only | design | 0 | 0 |
| D-RISK/ESRB Regulatory Arbitrage Vector ESRB监管套利向量 |  | design_only | design | 0 | 0 |
| D-RISK/ESRB Speed Vector ESRB速度向量 |  | design_only | design | 0 | 0 |
| D-RISK/ESRB不透明性风险向量 ESRB Opacity |  | design_only | design | 0 | 0 |
| D-RISK/ESRB互联性风险向量 ESRB Interconnectedness |  | design_only | design | 0 | 0 |
| D-RISK/ESRB历史约束风险向量 ESRB History-Constrained |  | design_only | design | 0 | 0 |
| D-RISK/ESRB市场操纵风险向量 ESRB Market Manipulation |  | design_only | design | 0 | 0 |
| D-RISK/ESRB数据依赖风险向量 ESRB Data Dependency |  | design_only | design | 0 | 0 |
| D-RISK/ESRB模型同质性风险向量 ESRB Model Homogeneity |  | design_only | design | 0 | 0 |
| D-RISK/ESRB法律地位未定风险向量 ESRB Untested Legal Status |  | design_only | design | 0 | 0 |
| D-RISK/ESRB监管套利风险向量 ESRB Regulatory Arbitrage |  | design_only | design | 0 | 0 |
| D-RISK/ESRB网络脆弱性风险向量 ESRB Cyber Vulnerability |  | design_only | design | 0 | 0 |
| D-RISK/ESRB过度信任风险向量 ESRB Overreliance |  | design_only | design | 0 | 0 |
| D-RISK/ESRB运营风险向量 ESRB Operational Risk |  | design_only | design | 0 | 0 |
| D-RISK/ESRB速度风险向量 ESRB Speed |  | design_only | design | 0 | 0 |
| D-RISK/ESRB集中风险向量 ESRB Concentration Risk |  | design_only | design | 0 | 0 |
| D-RISK/ESRB顺周期性风险向量 ESRB Procyclicality |  | design_only | design | 0 | 0 |
| D-RISK/EVT极值理论 |  | design_only | design | 0 | 0 |
| D-RISK/Emergent Manipulation 涌现操纵模式 |  | design_only | design | 0 | 0 |
| D-RISK/Enforcement 3-Level Executor 执行3级执行器 |  | design_only | design | 0 | 0 |
| D-RISK/Enforcement Type 执行类型枚举 |  | design_only | design | 0 | 0 |
| D-RISK/Execution Result Feedback Consumption Bridger 执行结果反馈消费桥接器 |  | design_only | design | 0 | 0 |
| D-RISK/Exit Time Risk 退出时间风险 |  | design_only | design | 0 | 0 |
| D-RISK/Extreme Event Black Swan 极端事件与黑天鹅 |  | design_only | design | 0 | 0 |
| D-RISK/Extreme Liquidity Mode 极端流动性模式 |  | design_only | design | 0 | 0 |
| D-RISK/FLATTEN Risk Decision 风险 |  | design_only | design | 0 | 0 |
| D-RISK/Fail-Closed Degradation Handler Fail-Closed降级处理器 |  | design_only | design | 0 | 0 |
| D-RISK/Fail-Closed 引擎故障处置 |  | design_only | design | 0 | 0 |
| D-RISK/Fake Move Identification Signal Engine 假动作识别信号引擎 |  | design_only | design | 0 | 0 |
| D-RISK/Fake Rally Real Distribution 假拉升真出货 |  | design_only | design | 0 | 0 |
| D-RISK/Fake Rebound Real Distribution 假反弹真派发 |  | design_only | design | 0 | 0 |
| D-RISK/Fake Support Real Lure 假护盘真诱多 |  | design_only | design | 0 | 0 |
| D-RISK/Fee Track费用轨道 Fee Track |  | design_only | design | 0 | 0 |
| D-RISK/Frequent Instant Cancellation 频繁瞬时撤单 |  | design_only | design | 0 | 0 |
| D-RISK/Frequent Push-Pull 频繁拉抬打压 |  | design_only | design | 0 | 0 |
| D-RISK/GAN对抗检测 GAN Adversarial Detection |  | design_only | design | 0 | 0 |
| D-RISK/GATE-FPGA-01 AUM高频 |  | design_only | design | 0 | 0 |
| D-RISK/GATE-FPGA-02 共享内存延迟 |  | design_only | design | 0 | 0 |
| D-RISK/GATE-FUT-03 期货风控参数 |  | design_only | design | 0 | 0 |
| D-RISK/Gate/Dashboard/Profile/DSL/Warehouse Series 门禁/仪表盘/画像/DSL/仓储系列 |  | design_only | design | 0 | 0 |
| D-RISK/Grid Search 网格搜索 |  | design_only | design | 0 | 0 |
| D-RISK/Grinold & Kahn容量公式 |  | design_only | design | 0 | 0 |
| D-RISK/Hedge Execution 独立对冲执行 |  | design_only | design | 0 | 0 |
| D-RISK/Hot Path No Python Invariant 热路径禁Python不变量 |  | design_only | design | 0 | 0 |
| D-RISK/IC衰减检测 IC Decay Detection |  | design_only | design | 0 | 0 |
| D-RISK/INV-001 Kill Switch Response Time Kill Switch响应时间不变量 |  | design_only | design | 0 | 0 |
| D-RISK/IV Parametric VaR to Historical Simulation Migrator 参数法VaR→历史模拟法迁移器 |  | design_only | design | 0 | 0 |
| D-RISK/Impact Cost Risk 冲击成本风险 |  | design_only | design | 0 | 0 |
| D-RISK/Industry Concentration Compliance Detector 行业集中度合规检测器 |  | design_only | design | 0 | 0 |
| D-RISK/Industry Deviation Exceeds Limit 行业偏离超限 |  | design_only | design | 0 | 0 |
| D-RISK/Information Asymmetry Period Manipulation Detector 信息不对称期操纵检测器 |  | design_only | design | 0 | 0 |
| D-RISK/Information Asymmetry Window 信息不对称空窗期 |  | design_only | design | 0 | 0 |
| D-RISK/Instant Order Rate Anomaly 瞬时申报速率异常 |  | design_only | design | 0 | 0 |
| D-RISK/Insufficient Liquidity 流动性不足 |  | design_only | design | 0 | 0 |
| D-RISK/Intraday Time-Varying Participation Rate 日内时变参与率 |  | design_only | design | 0 | 0 |
| D-RISK/KS-L1 软暂停 Kill Switch |  | design_only | design | 0 | 0 |
| D-RISK/KS-L2 会话熔断 Kill Switch |  | design_only | design | 0 | 0 |
| D-RISK/KS-L3 通道断开 Kill Switch |  | design_only | design | 0 | 0 |

> (仅显示前 200 个模块，共 775 个)

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-SECURITY | 98 | contract,data,config_depends,event |
| D-SIGNAL | 71 | config_depends,event,data,contract |
| D-INFRA_RUNTIME | 63 | data,contract,event,config_depends |
| D-FACTOR | 54 | config_depends,event,contract,data |
| D-MKT_DATA | 53 | domain_dependency,config_depends,event,contract,data |
| D-TRADING | 30 | contract,import_depends,event,data,config_depends |
| D-DATA_ENG | 26 | data,contract,event,config_depends |
| D-ML_TRAIN | 23 | contract,config_depends,event,data |
| D-EX_CORE | 20 | contract,event,data,config_depends |
| D-EX_SOR | 19 | event,config_depends,contract,data |
| D-POSITION | 18 | contract,domain_dependency,data,config_depends,event |
| D-SHARED | 1 | import_depends |
| D-GOVERNANCE | 1 | config_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-COMPLIANCE | 166 | domain_dependency,event,contract,config_depends,data |
| D-GOVERNANCE | 130 | import_depends,test_depends,data,contract,config_depends,event |
| D-AUTONOMY_CORE | 87 | contract,event,data,config_depends |
| D-INTEGRATION | 69 | event,config_depends,contract,data |
| D-INFRA_OPS | 68 | event,data,contract,config_depends |
| D-OPS | 50 | event,contract,config_depends,data |
| D-AUTONOMY_PERM | 48 | contract,event,data,config_depends |
| D-FRONTEND | 47 | config_depends,event,contract,data |
| D-INTELLIGENCE | 35 | data,event,contract,config_depends |
| D-KNOWLEDGE | 29 | event,contract,data,config_depends |
| D-PF_CORE | 27 | event,data,contract,config_depends |
| D-PF_ALLOC | 26 | domain_dependency,data,contract,event,config_depends |
| D-REPORTING | 22 | contract,data,event,config_depends |
| D-SIMULATION | 19 | event,config_depends,contract,data |
| D-SELL_DECISION | 14 | domain_dependency,config_depends,event,data,contract |
| D-CROSS_ASSET | 13 | event,config_depends,contract,data |
| D-ALT_DATA | 10 | contract,event,data |
| D-DATA_GOV | 6 | data,event,contract |
| D-ML_SERVE | 4 | contract,event |
| D-BACKTEST | 3 | event,contract,data |
| D-DATA_SEC | 1 | event |

## 域内依赖图

详见 [d_risk_dependency.mmd](d_risk_dependency.mmd)
