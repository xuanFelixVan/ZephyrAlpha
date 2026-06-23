---
doc_type: domain_architecture_doc
title: D-PF_ALLOC 组合分配架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-PF_ALLOC 组合分配架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-PF_ALLOC |
| 域名称 | 组合分配 |
| 架构层 | L2_domain |
| 模块总数 | 114 |
| 设计态模块 | 104 |
| 原型态模块 | 4 |
| 生产态模块 | 0 |
| 容量 | 0/150 (正常) |
| 描述 | 资产组合分配优化 |

## 模块清单

共 114 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-PF-ALLOC/4级决策 APPROVE/REDUCE/REJECT/FLATTEN |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/7状态生命周期 7-State Lifecycle |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/A-Share Dynamic Position Coefficient Calculator A股动态仓位系数 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/A-Share Kelly Position Dynamic Calculator A股凯利仓位动态计算 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/A-Share Position Formula Calculator A股仓位公式计算器 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/CapitalAllocationResult Contract CapitalAllocationResult 策略分配契约 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/Copula-GARCH Copula-GARCH模型 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/D-EXECUTION 执行 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/D-L0→D-L1 降级路径 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/D-L1→D-L2 降级路径 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/D-L2→D-L3 降级路径 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/D-PF-ALLOC 组合分配域 Portfolio Allocation Domain |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/Dynamic Capital Allocator 动态资金分配器 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/E-0073 D-RISK→D-PF-ALLOC边 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/ESRB系统性风险向量 ESRB Systemic Risk Vector |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/Execution Feedback Bridge执行反馈桥 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/IC加权 IC Weighting |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/Kelly公式 Kelly Formula |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/Leverage Manager 杠杆管理器 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/MOD-L05-001 蓝图 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/MaxDDLimit Allocation Strategist最大回撤限制分配器 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/Meta-Strategy Router元策略路由 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/Module Registry 4状态映射 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/Multi-Strategy Capital Allocator多策略资金分配 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/P2 signal_engine 策略路由进程 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/PA-02 Strategy Screening 3D 策略 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/PA-03 Rolling Window Correlation PA-03滚动窗口相关性 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/PA-04增量 标的级/板块级集中度监控 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/PA-04增量 隐性串谋检测扩展 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/PA-05增量 传染路径检测与隔离 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/PA-06/07/08 A-Share Position 仓位 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/PA-09 Stackelberg Game PA-09斯塔克尔伯格博弈 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/PA-11/12 Strategy Retirement 策略 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/PA-14 Position Limit Gate 仓位 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/PA-15 Execution Feedback Bridge 执行 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/PA-CapitalAllocated 事件 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/PA-CorrelationGateTriggered 事件 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/PA-E01 CapitalAllocated 资本分配完成事件 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/PA-E02 StrategyRetired 策略退役事件 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/PA-E03 CorrelationGateTriggered 相关性门禁触发事件 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/PA-E04 StrategyScreened 策略筛选完成事件 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/PA-StrategyRetired 事件 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/PA-StrategyRetired 策略退役事件 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/Position Limit Gate Checker仓位限制门禁检查器 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/Position Sizer 仓位计算器 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/RebalanceDecided 再平衡决策事件 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/RebalanceDecided事件 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/Rolling Window Dynamic Correlation Analyzer滚动窗口动态相关性 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/ST-006 量化踩踏 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/Signal Synthesis Combiner信号合成器 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/Stackelberg Game-Theoretic Follower Stackelberg博弈跟随策略 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/Strategy Correlation Gate G12 Executor策略相关性门禁 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/Strategy Retirement Capital Recycler策略退役资金回收器 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/Strategy Retirement Trigger策略退役触发器 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/Strategy Screening 3D Evaluator策略筛选三维评估器 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/_PARALLEL_DISCUSSIONS.md 并行 |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/§30.1.4 D-PF-ALLOC 组合分配域（15个模块） |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/仲裁规则 Arbitration Rules |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/体制自适应权重 Regime Adaptive Weight |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/信号传染 Signal Contagion |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/信号冲突检测 Signal Conflict Detection |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/共振融合 Resonance Fusion |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/决策去重 Decision Deduplication |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/冷启动协议 Cold Start Protocol |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/准入门控 Admission Gate |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/分批建仓 Batch Position Building |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/半Kelly硬上限 Half Kelly Hard Cap |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/因子模型 Factor Model |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/因子正交性 Factor Orthogonality |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/因子重叠 Factor Overlap |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/域内依赖图 Intra-domain Dependency Graph |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/多策略投票 Multi-Strategy Voting |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/安全隔离 Safety Isolation |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/尾部相关性飙升 Tail Correlation Surge |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/情绪传染 Sentiment Contagion |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/收缩估计 Shrinkage Estimation |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/数据流优化 Data Flow Optimization |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/板块级拥挤 Sector-level Crowding |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/标的级拥挤 Target-level Crowding |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/模块组合发现 Module Combination Discovery |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/模型共振反应 Model Resonance Response |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/模型叠加尾部放大 Model Stacking Tail Amplification |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/模型间假设不一致 Inter-model Assumption Inconsistency |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/盘中执行必做项 Intraday Execution Must-do |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/目标权重向量输出 Target Weight Vector Output |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/相关性体制监控 Correlation Regime Monitoring |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/策略冲突检测 Strategy Conflict Detection |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/策略同质化检测 Strategy Homogeneity Detection |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/策略容量超限 Strategy Capacity Exceeded |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/策略指纹相似度 Strategy Fingerprint Similarity |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/策略权重进化 Strategy Weight Evolution |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/策略衰减检测 Strategy Decay Detection |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/组合级硬约束 Portfolio Hard Constraints |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/股票池重叠 Stock Pool Overlap |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/解耦保证 Decoupling Guarantee |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/资本传染 Capital Contagion |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/跨策略仓位合并 Cross-Strategy Position Merging |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/隐性串谋检测 Implicit Collusion Detection |  | design_only | design | 0 | 0 |
| D-PF-ALLOC/风险预算范式 Risk Budgeting Paradigm |  | design_only | design | 0 | 0 |
| src/zephyr/pf_alloc/ | MOD-PF_ALLOC | design_only | design | 0 | 11 |
| src/zephyr/pf_alloc/__init__.py | MOD-PF_ALLOC | draft | prototype | 1 | 0 |
| src/zephyr/pf_alloc/_extensions/__init__.py | MOD-PF_ALLOC | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/pf_alloc/api/__init__.py | MOD-PF_ALLOC | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/pf_alloc/constraint/ | MOD-PF_ALLOC | design_only | design | 0 | 0 |
| src/zephyr/pf_alloc/core/__init__.py | MOD-PF_ALLOC | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/pf_alloc/infrastructure/__init__.py | MOD-PF_ALLOC | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/pf_alloc/models/__init__.py | MOD-PF_ALLOC | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/pf_alloc/optimizer/ | MOD-PF_ALLOC | design_only | design | 0 | 0 |
| src/zephyr/pf_alloc/rebalance/ | MOD-PF_ALLOC | design_only | design | 0 | 0 |
| src/zephyr/pf_alloc/risk_budget/ | MOD-PF_ALLOC | design_only | design | 0 | 0 |
| src/zephyr/pf_alloc/services/__init__.py | MOD-PF_ALLOC | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/pf_alloc/strategy_lifecycle_event.py | SRC-195 | draft | prototype | 0 | 1 |
| src/zephyr/pf_core/default_equity_strategy.py | MOD-L05-001 | draft | prototype | 2 | 2 |
| src/zephyr/pf_core/strategy_portfolio.py | MOD-INF-022 | draft | prototype | 0 | 1 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-RISK | 26 | data,contract,event,domain_dependency,config_depends |
| D-SECURITY | 14 | config_depends,contract,data,event |
| D-GOVERNANCE | 14 | import_depends,config_depends,contract,event,data |
| D-SIGNAL | 13 | contract,event,data,config_depends |
| D-INFRA_RUNTIME | 10 | data,event,config_depends,contract |
| D-INTELLIGENCE | 8 | data,event,contract,config_depends |
| D-INTEGRATION | 8 | event,contract,data |
| D-MKT_DATA | 7 | event,contract,data |
| D-FACTOR | 7 | config_depends,contract,event |
| D-PF_CORE | 6 | event,contract,data |
| D-AUTONOMY_CORE | 6 | event,data,contract |
| D-AUTONOMY_PERM | 5 | contract,event,data |
| D-TRADING | 4 | import_depends,contract,data |
| D-EX_SOR | 4 | config_depends,data,contract |
| D-DATA_ENG | 4 | event,contract |
| D-SIMULATION | 3 | event,config_depends |
| D-REPORTING | 3 | data,contract |
| D-KNOWLEDGE | 3 | config_depends,event,contract |
| D-SHARED | 2 | contract,import_depends |
| D-SELL_DECISION | 2 | event,contract |
| D-POSITION | 2 | config_depends,contract |
| D-ML_TRAIN | 2 | event,data |
| D-ALT_DATA | 2 | data,event |
| D-EX_CORE | 1 | data |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-COMPLIANCE | 20 | data,event,contract,config_depends |
| D-INFRA_OPS | 11 | event,config_depends,contract |
| D-OPS | 8 | data,contract,config_depends,event |
| D-FRONTEND | 5 | data,contract,config_depends |
| D-CROSS_ASSET | 2 | event,data |
| D-GOVERNANCE | 1 | import_depends |

## 域内依赖图

详见 [d_pf_alloc_dependency.mmd](d_pf_alloc_dependency.mmd)
