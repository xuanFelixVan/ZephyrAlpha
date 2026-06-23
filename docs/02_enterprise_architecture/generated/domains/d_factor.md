---
doc_type: domain_architecture_doc
title: D-FACTOR 因子架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-FACTOR 因子架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 13:28:28
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-FACTOR |
| 域名称 | 因子 |
| 架构层 | L2_domain |
| 模块总数 | 320 |
| 设计态模块 | 302 |
| 原型态模块 | 10 |
| 生产态模块 | 2 |
| 容量 | 2/150 (正常) |
| 描述 | 因子计算、因子库、因子评价、因子正交化。Alpha挖掘引擎。 |

## 模块清单

共 320 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-FACTOR/10风格+28行业因子完整实现+验证 Factor |  | design_only | design | 0 | 0 |
| D-FACTOR/3-Level Judgment 三级判断 |  | design_only | design | 0 | 0 |
| D-FACTOR/39类漂移检测器实现复杂度 Detector |  | design_only | design | 0 | 0 |
| D-FACTOR/6-Step Flow 6步流程 |  | design_only | design | 0 | 0 |
| D-FACTOR/87-Alpha 87-Alpha因子 |  | design_only | design | 0 | 0 |
| D-FACTOR/87-Alpha 87Alpha因子 |  | design_only | design | 0 | 0 |
| D-FACTOR/A-Share Capital Flow Factor 因子 |  | design_only | design | 0 | 0 |
| D-FACTOR/A-Share Microstructure Factor 因子 |  | design_only | design | 0 | 0 |
| D-FACTOR/ABS-001 Gate ABS-001门禁 |  | design_only | design | 0 | 0 |
| D-FACTOR/Alpha Factor Alpha因子 |  | design_only | design | 0 | 0 |
| D-FACTOR/Alpha Factor Calculation Engine 引擎因子 |  | design_only | design | 0 | 0 |
| D-FACTOR/Alpha因子 Alpha Factor |  | design_only | design | 0 | 0 |
| D-FACTOR/BVC方法 Bulk Volume Classification |  | design_only | design | 0 | 0 |
| D-FACTOR/Backpressure 背压 |  | design_only | design | 0 | 0 |
| D-FACTOR/Backpressure 背压控制 |  | design_only | design | 0 | 0 |
| D-FACTOR/Barra Risk Model 模型风险 |  | design_only | design | 0 | 0 |
| D-FACTOR/Barra因子权重方法论需MSCI参考实现 |  | design_only | design | 0 | 0 |
| D-FACTOR/Barra风险模型归D-FACTOR-06 |  | design_only | design | 0 | 0 |
| D-FACTOR/Batch Output 批量输出 |  | design_only | design | 0 | 0 |
| D-FACTOR/CTR-001 Consumer CTR-001消费者 |  | design_only | design | 0 | 0 |
| D-FACTOR/CTR-001 Consumer 契约消费者 |  | design_only | design | 0 | 0 |
| D-FACTOR/CTR-002/003 Producer CTR-002/003生产者 |  | design_only | design | 0 | 0 |
| D-FACTOR/CTR-002/003 Producer 契约生产者 |  | design_only | design | 0 | 0 |
| D-FACTOR/CTR-P1-001 FactorMonitorReport CTR-P1-001 FactorMonitorReport契约 |  | design_only | design | 0 | 0 |
| D-FACTOR/CVD 累积买卖压力 Cumulative Volume Delta |  | design_only | design | 0 | 0 |
| D-FACTOR/CVD买卖压力追踪 Cumulative Volume Delta |  | design_only | design | 0 | 0 |
| D-FACTOR/CVD价格背离 CVD Price Divergence |  | design_only | design | 0 | 0 |
| D-FACTOR/Capital Flow 资金流 |  | design_only | design | 0 | 0 |
| D-FACTOR/Causal Factor Validation Layer 因果因子验证层 |  | design_only | design | 0 | 0 |
| D-FACTOR/Causal Validator 因果验证器 |  | design_only | design | 0 | 0 |
| D-FACTOR/Correlation Redundancy Remover 相关性去冗余 |  | design_only | design | 0 | 0 |
| D-FACTOR/Cross-Market Factor 跨市场因子 |  | design_only | design | 0 | 0 |
| D-FACTOR/Crowding Detection 拥挤度检测 |  | design_only | design | 0 | 0 |
| D-FACTOR/D-AUTONOMY域就绪审计链门禁引擎 |  | design_only | design | 0 | 0 |
| D-FACTOR/D-FACTOR Engine 因子引擎 |  | design_only | design | 0 | 0 |
| D-FACTOR/D-FACTOR Engine 因子计算引擎 |  | design_only | design | 0 | 0 |
| D-FACTOR/D-FACTOR 因子 |  | design_only | design | 0 | 0 |
| D-FACTOR/D-FACTOR-01到04稳定运行产出IC历史数据大于20日 |  | design_only | design | 0 | 0 |
| D-FACTOR/D-FACTOR-04 Pipeline D-FACTOR-04管道 |  | design_only | design | 0 | 0 |
| D-FACTOR/DAG调度因子计算 |  | design_only | design | 0 | 0 |
| D-FACTOR/DecayMonitor 因子衰减监控 |  | design_only | design | 0 | 0 |
| D-FACTOR/Distribution Feature Engineering 分布特征工程 |  | design_only | design | 0 | 0 |
| D-FACTOR/Distribution Feature Engineering产出不入因子池 |  | design_only | design | 0 | 0 |
| D-FACTOR/E-SIM-05 OverfittingDetected 过拟合检测触发 |  | design_only | design | 0 | 0 |
| D-FACTOR/ESG ESG因子 |  | design_only | design | 0 | 0 |
| D-FACTOR/Engine 引擎 |  | design_only | design | 0 | 0 |
| D-FACTOR/Evaluation 评估器 |  | design_only | design | 0 | 0 |
| D-FACTOR/Event Impact Assessment 事件影响评估 |  | design_only | design | 0 | 0 |
| D-FACTOR/Factor Attribution 因子归因 |  | design_only | design | 0 | 0 |
| D-FACTOR/Factor Correlation Analyzer 因子相关性分析器 |  | design_only | design | 0 | 0 |
| D-FACTOR/Factor Definition Interface 因子定义接口 |  | design_only | design | 0 | 0 |
| D-FACTOR/Factor Dependency DAG Manager 因子依赖DAG管理器 |  | design_only | design | 0 | 0 |
| D-FACTOR/Factor Dependency Graph DAG 因子依赖图DAG |  | design_only | design | 0 | 0 |
| D-FACTOR/Factor Exposure Calculator 因子暴露计算器 |  | design_only | design | 0 | 0 |
| D-FACTOR/Factor Factory 因子工厂 |  | design_only | design | 0 | 0 |
| D-FACTOR/Factor Orthogonalizer 因子正交化器 |  | design_only | design | 0 | 0 |
| D-FACTOR/Factor Portfolio Optimizer 因子组合优化器 |  | design_only | design | 0 | 0 |
| D-FACTOR/Factor Risk Budget Allocator 因子风险预算分配器 |  | design_only | design | 0 | 0 |
| D-FACTOR/Factor Turnover Analyzer 因子换手率分析器 |  | design_only | design | 0 | 0 |
| D-FACTOR/Factor Value Feed 因子值供给 |  | design_only | design | 0 | 0 |
| D-FACTOR/FactorBase Interface Contract FactorBase接口契约 |  | design_only | design | 0 | 0 |
| D-FACTOR/FactorComputationError 因子计算错误 |  | design_only | design | 0 | 0 |
| D-FACTOR/FactorMonitorReport 因子监控报告 |  | design_only | design | 0 | 0 |
| D-FACTOR/FactorResearched 因子已研究 |  | design_only | design | 0 | 0 |
| D-FACTOR/FactorResearched 因子研究完成 |  | design_only | design | 0 | 0 |
| D-FACTOR/FactorSignal 因子信号 |  | design_only | design | 0 | 0 |
| D-FACTOR/FactorSignal 因子信号契约 |  | design_only | design | 0 | 0 |
| D-FACTOR/Feature Lifecycle Events 特征生命周期事件 |  | design_only | design | 0 | 0 |
| D-FACTOR/Feature Serving API 特征服务API |  | design_only | design | 0 | 0 |
| D-FACTOR/Feature Store 2.0声明式定义语言 Declarative Feature Definition |  | design_only | design | 0 | 0 |
| D-FACTOR/Feature Store归D-DATA-03 |  | design_only | design | 0 | 0 |
| D-FACTOR/FeatureCreated 因子创建事件 |  | design_only | design | 0 | 0 |
| D-FACTOR/FeatureDecaying 因子衰减事件 |  | design_only | design | 0 | 0 |
| D-FACTOR/FeatureDeprecated 因子废弃事件 |  | design_only | design | 0 | 0 |
| D-FACTOR/FeatureDormant 因子休眠事件 |  | design_only | design | 0 | 0 |
| D-FACTOR/FeatureOnline 因子上线事件 |  | design_only | design | 0 | 0 |
| D-FACTOR/FeatureReactivated 因子重新激活事件 |  | design_only | design | 0 | 0 |
| D-FACTOR/FeatureRegistered 因子注册事件 |  | design_only | design | 0 | 0 |
| D-FACTOR/FeatureRetired 因子退役事件 |  | design_only | design | 0 | 0 |
| D-FACTOR/FeatureValidated 因子验证事件 |  | design_only | design | 0 | 0 |
| D-FACTOR/Fundamental 基本面 |  | design_only | design | 0 | 0 |
| D-FACTOR/Fundamental 基本面因子 |  | design_only | design | 0 | 0 |
| D-FACTOR/Global Market Contagion Quantification 全球市场传导量化 |  | design_only | design | 0 | 0 |
| D-FACTOR/Governance 因子治理 |  | design_only | design | 0 | 0 |
| D-FACTOR/Grayscale Rollout 灰度发布 |  | design_only | design | 0 | 0 |
| D-FACTOR/HVN/LVN节点 High/Low Volume Node |  | design_only | design | 0 | 0 |
| D-FACTOR/HVN/LVN节点 Volume Profile HVN LVN |  | design_only | design | 0 | 0 |
| D-FACTOR/IC Decay Analyzer IC衰减分析器 |  | design_only | design | 0 | 0 |
| D-FACTOR/IC Decay Detection IC衰减检测 |  | design_only | design | 0 | 0 |
| D-FACTOR/IC/IR Evaluator IC/IR评估器 |  | design_only | design | 0 | 0 |
| D-FACTOR/IC_IR Calculator IC_IR计算器 |  | design_only | design | 0 | 0 |
| D-FACTOR/IC_IR计算 IC_IR Calculator |  | design_only | design | 0 | 0 |
| D-FACTOR/IC因子替换 IC-Based Factor Replacement |  | design_only | design | 0 | 0 |
| D-FACTOR/IC衰减三级自动处置需D-AUTONOMY自愈引擎联动 |  | design_only | design | 0 | 0 |
| D-FACTOR/IC衰减分析器 IC Decay Analyzer |  | design_only | design | 0 | 0 |
| D-FACTOR/IRCF因子 Institutional Retail Contrarian Flow |  | design_only | design | 0 | 0 |
| D-FACTOR/IRL IRL因子 |  | design_only | design | 0 | 0 |
| D-FACTOR/IRL 机构行为识别 |  | design_only | design | 0 | 0 |
| D-FACTOR/Institutional Behavior Factor 机构行为因子 |  | design_only | design | 0 | 0 |
| D-FACTOR/Intraday 日内 |  | design_only | design | 0 | 0 |
| D-FACTOR/Intraday 日内因子 |  | design_only | design | 0 | 0 |
| D-FACTOR/KAN Explainable Function Approximator KAN可解释函数逼近 |  | design_only | design | 0 | 0 |
| D-FACTOR/L1 to L2-A Factor Calculation L1→L2-A因子计算 |  | design_only | design | 0 | 0 |
| D-FACTOR/L1 因子计算层 Factor Compute Layer |  | design_only | design | 0 | 0 |
| D-FACTOR/LLM本地部署需GPU大于16GB显存 |  | design_only | design | 0 | 0 |
| D-FACTOR/Layered Backtest 分层回测 |  | design_only | design | 0 | 0 |
| D-FACTOR/Lee-Ready算法 Lee-Ready Algorithm |  | design_only | design | 0 | 0 |
| D-FACTOR/Lifecycle State Machine 生命周期状态机 |  | design_only | design | 0 | 0 |
| D-FACTOR/MacroFactorSignal 宏观因子信号 |  | design_only | design | 0 | 0 |
| D-FACTOR/Market Structure Factor 市场结构因子 |  | design_only | design | 0 | 0 |
| D-FACTOR/Microstructure 微观结构 |  | design_only | design | 0 | 0 |
| D-FACTOR/Multi-Factor Synthesis Validator 多因子合成验证器 |  | design_only | design | 0 | 0 |
| D-FACTOR/Northbound Capital Flow Model 北向资金流向模型 |  | design_only | design | 0 | 0 |
| D-FACTOR/Northbound Capital Signal 北向资金信号 |  | design_only | design | 0 | 0 |
| D-FACTOR/OCP-001 FactorBase扩展点 |  | design_only | design | 0 | 0 |
| D-FACTOR/OFI检测框架 Order Flow Imbalance |  | design_only | design | 0 | 0 |
| D-FACTOR/Overnight Global Market Contagion Model 隔夜全球市场传导模型 |  | design_only | design | 0 | 0 |
| D-FACTOR/PIT一致性保证 PIT Consistency Guarantee |  | design_only | design | 0 | 0 |
| D-FACTOR/POC Point of Control 控制点 |  | design_only | design | 0 | 0 |
| D-FACTOR/POC 公允价值核心 Point of Control |  | design_only | design | 0 | 0 |
| D-FACTOR/Parameter Config Manager 参数配置管理器 |  | design_only | design | 0 | 0 |
| D-FACTOR/Pastor-Stambaugh Liquidity Factor PS流动性因子 |  | design_only | design | 0 | 0 |
| D-FACTOR/Pastor-Stambaugh Liquidity Factor Pastor-Stambaugh流动性因子 |  | design_only | design | 0 | 0 |
| D-FACTOR/Pattern to Signal Converter 形态信号转化器 |  | design_only | design | 0 | 0 |
| D-FACTOR/Pipeline 因子与信号生产管线 |  | design_only | design | 0 | 0 |
| D-FACTOR/Pipeline 管线 |  | design_only | design | 0 | 0 |
| D-FACTOR/RankNormalized 排名标准化契约 |  | design_only | design | 0 | 0 |
| D-FACTOR/Registry 注册表 |  | design_only | design | 0 | 0 |
| D-FACTOR/SMC SMC因子 |  | design_only | design | 0 | 0 |
| D-FACTOR/SMC Smart Money Concept SMC聪明钱概念 |  | design_only | design | 0 | 0 |
| D-FACTOR/Sector Factor 板块因子 |  | design_only | design | 0 | 0 |
| D-FACTOR/Smart Money Concept算法实现 |  | design_only | design | 0 | 0 |
| D-FACTOR/Technical Indicator Factor 技术指标因子 |  | design_only | design | 0 | 0 |
| D-FACTOR/Tecton被Databricks收购影响 Tecton Acquisition Impact |  | design_only | design | 0 | 0 |
| D-FACTOR/Timing Engine 择时引擎 |  | design_only | design | 0 | 0 |
| D-FACTOR/Timing Engine 时机引擎 |  | design_only | design | 0 | 0 |
| D-FACTOR/UFL Deterministic Fact Layer UFL确定性事实层 |  | design_only | design | 0 | 0 |
| D-FACTOR/VPIN 知情交易概率 VPIN |  | design_only | design | 0 | 0 |
| D-FACTOR/Value Area 价值区域 |  | design_only | design | 0 | 0 |
| D-FACTOR/Volume Profile量能分布 Volume Profile |  | design_only | design | 0 | 0 |
| D-FACTOR/compute返回类型统一为list FactorSignal |  | design_only | design | 0 | 0 |
| D-FACTOR/consistency_check 一致性引擎 |  | design_only | design | 0 | 0 |
| D-FACTOR/factor_base.py为唯一SSoT删除base.py |  | design_only | design | 0 | 0 |
| D-FACTOR/incremental_compute 增量因子计算 |  | design_only | design | 0 | 0 |
| D-FACTOR/qwen3:8b模型权重需下载部署 |  | design_only | design | 0 | 0 |
| D-FACTOR/一致性引擎 Consistency Engine |  | design_only | design | 0 | 0 |
| D-FACTOR/一高七矮 Volume Profile HVN LVN |  | design_only | design | 0 | 0 |
| D-FACTOR/下跌强度分级 Down Strength Classification |  | design_only | design | 0 | 0 |
| D-FACTOR/主力净流入 Institutional Net Inflow Factor |  | design_only | design | 0 | 0 |
| D-FACTOR/主力吸筹 Accumulation Factor |  | design_only | design | 0 | 0 |
| D-FACTOR/主力洗盘 Shakeout Factor |  | design_only | design | 0 | 0 |
| D-FACTOR/主力派发 Distribution Factor |  | design_only | design | 0 | 0 |
| D-FACTOR/主力行为因子 Institutional Behavior Factor |  | design_only | design | 0 | 0 |
| D-FACTOR/买卖价差估算需Level-2数据 |  | design_only | design | 0 | 0 |
| D-FACTOR/五层筛选漏斗因子支撑 Factor |  | design_only | design | 0 | 0 |
| D-FACTOR/交互项构造 Interaction Feature Construction |  | design_only | design | 0 | 0 |
| D-FACTOR/价格偏离度 Price Deviation |  | design_only | design | 0 | 0 |
| D-FACTOR/传导系数 Cross-Market Transmission Coefficient |  | design_only | design | 0 | 0 |
| D-FACTOR/体制条件因子有效性 Regime-Conditional Factor Effectiveness |  | design_only | design | 0 | 0 |
| D-FACTOR/体制条件因子衰减 Regime-Conditional Factor Decay |  | design_only | design | 0 | 0 |
| D-FACTOR/信号Agent Signal Gen Agent |  | design_only | design | 0 | 0 |
| D-FACTOR/入池观察池 Probation Pool |  | design_only | design | 0 | 0 |
| D-FACTOR/冰山单占比 Iceberg Order Ratio |  | design_only | design | 0 | 0 |
| D-FACTOR/冰山单检测 Hidden Order Detection Factor |  | design_only | design | 0 | 0 |
| D-FACTOR/出货信号因子 Distribution Signal Factor |  | design_only | design | 0 | 0 |
| D-FACTOR/分布形态统计量 Distribution Shape Statistics |  | design_only | design | 0 | 0 |
| D-FACTOR/前视偏差检测归D-FACTOR-03 |  | design_only | design | 0 | 0 |
| D-FACTOR/北向持仓变化 Northbound Holding Change Factor |  | design_only | design | 0 | 0 |
| D-FACTOR/十阶段生命周期状态机 Ten-stage Lifecycle |  | design_only | design | 0 | 0 |
| D-FACTOR/单一定义原则消除偏差 Single Definition Principle |  | design_only | design | 0 | 0 |
| D-FACTOR/参数配置管理器 Parameter Config Manager |  | design_only | design | 0 | 0 |
| D-FACTOR/双存储架构 Dual Storage Architecture |  | design_only | design | 0 | 0 |
| D-FACTOR/双模运行 Dual-Mode Operation |  | design_only | design | 0 | 0 |
| D-FACTOR/另类因子 Alternative Factor |  | design_only | design | 0 | 0 |
| D-FACTOR/吸筹出货期检测 Accumulation Distribution Phase Detection |  | design_only | design | 0 | 0 |
| D-FACTOR/因子-模型联合优化R&D-Agent-Quant |  | design_only | design | 0 | 0 |
| D-FACTOR/因子IC入池阈值分级 IC Threshold Tiered |  | design_only | design | 0 | 0 |
| D-FACTOR/因子IC大于0.03是有效性最低门槛 |  | design_only | design | 0 | 0 |
| D-FACTOR/因子依赖DAG管理器 Factor Dependency DAG Manager |  | design_only | design | 0 | 0 |
| D-FACTOR/因子依赖图DAG Factor Dependency DAG |  | design_only | design | 0 | 0 |
| D-FACTOR/因子分类八大类 Factor |  | design_only | design | 0 | 0 |
| D-FACTOR/因子性能审计 Factor Performance Audit |  | design_only | design | 0 | 0 |
| D-FACTOR/因子批量计算→Feature Store检查点 |  | design_only | design | 0 | 0 |
| D-FACTOR/因子数据血缘追踪 Factor Data Lineage Tracking |  | design_only | design | 0 | 0 |
| D-FACTOR/因子暴露合规 Factor Exposure Compliance |  | design_only | design | 0 | 0 |
| D-FACTOR/因子暴露审计 Factor Exposure Audit |  | design_only | design | 0 | 0 |
| D-FACTOR/因子权重变更审批分级 Factor Weight Change Approval Tier |  | design_only | design | 0 | 0 |
| D-FACTOR/因子池容量管理 Factor Management |  | design_only | design | 0 | 0 |
| D-FACTOR/因子注册表合规 Factor Registry Compliance |  | design_only | design | 0 | 0 |
| D-FACTOR/因子版本管理 Factor Version Management |  | design_only | design | 0 | 0 |
| D-FACTOR/因子组合优化 Factor Portfolio Optimizer |  | design_only | design | 0 | 0 |
| D-FACTOR/因子血缘合规 Factor Lineage Compliance |  | design_only | design | 0 | 0 |
| D-FACTOR/因子衰减三级自动处置 Factor |  | design_only | design | 0 | 0 |
| D-FACTOR/因子衰减三级自动处置MILD MODERATE SEVERE |  | design_only | design | 0 | 0 |
| D-FACTOR/因子计算 增量因子计算 Factor Incremental |  | design_only | design | 0 | 0 |
| D-FACTOR/因子计算审计日志 Factor Compute Audit Log |  | design_only | design | 0 | 0 |
| D-FACTOR/因子退役审计 Factor Retirement Audit |  | design_only | design | 0 | 0 |
| D-FACTOR/因子预处理管线归D-DATA-02 |  | design_only | design | 0 | 0 |
| D-FACTOR/因果推断库dowhy causalml |  | design_only | design | 0 | 0 |
| D-FACTOR/图形模式库 Pattern Library |  | design_only | design | 0 | 0 |

> (仅显示前 200 个模块，共 320 个)

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-MKT_DATA | 23 | domain_dependency,config_depends,contract,data,event |
| D-INFRA_RUNTIME | 19 | event,data,contract,config_depends |
| D-DATA_ENG | 14 | contract,domain_dependency,data,event,config_depends |
| D-EX_SOR | 7 | config_depends,contract,event |
| D-TRADING | 5 | contract,data,event |
| D-GOVERNANCE | 5 | import_depends,config_depends |
| D-SIGNAL | 2 | import_depends,contract |
| D-SHARED | 1 | import_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-COMPLIANCE | 65 | config_depends,event,data,contract |
| D-RISK | 54 | event,contract,data,config_depends |
| D-SECURITY | 46 | config_depends,data,contract,event |
| D-GOVERNANCE | 46 | test_depends,config_depends,contract,data,event |
| D-SIGNAL | 40 | event,domain_dependency,data,config_depends,contract |
| D-AUTONOMY_CORE | 34 | contract,event,config_depends,data |
| D-INFRA_OPS | 27 | data,event,config_depends,contract |
| D-OPS | 25 | contract,data,event,config_depends,runtime |
| D-INTEGRATION | 24 | contract,data,event,config_depends |
| D-INTELLIGENCE | 22 | data,contract,config_depends,event |
| D-FRONTEND | 22 | event,config_depends,contract,data |
| D-ML_TRAIN | 15 | domain_dependency,contract,event,data,config_depends |
| D-EX_CORE | 15 | event,config_depends,contract,data |
| D-SIMULATION | 14 | data,contract,event |
| D-KNOWLEDGE | 11 | contract,data,event,config_depends |
| D-AUTONOMY_PERM | 10 | contract,data,event,config_depends |
| D-POSITION | 8 | event,config_depends,contract,data |
| D-PF_CORE | 8 | contract,data,event |
| D-PF_ALLOC | 7 | contract,config_depends,event |
| D-REPORTING | 5 | data,contract,event |
| D-ML_SERVE | 5 | contract,data,config_depends,event |
| D-DATA_GOV | 4 | contract,config_depends,event |
| D-CROSS_ASSET | 4 | event,contract,config_depends |
| D-ALT_DATA | 4 | data,contract,event |
| D-SELL_DECISION | 2 | event,contract |
| D-DATA_SEC | 1 | data |
| D-BACKTEST | 1 | contract |

## 域内依赖图

详见 [d_factor_dependency.mmd](d_factor_dependency.mmd)
