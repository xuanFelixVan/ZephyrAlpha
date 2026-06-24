---
doc_type: domain_architecture_diagram
title: D-PF_ALLOC 组合分配架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 33_d_pf_alloc / 组合分配 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示组合分配（D-PF_ALLOC）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 21:40:10
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 组合分配（D-PF_ALLOC）的模块分布。共 114 个模块 / 114 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│             L1 基础层 / Foundation Layer (2 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/pf_core/default_equity_strategy.py  [prototype]     │
│   src/zephyr/pf_core/strategy_portfolio.py  [prototype]          │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (13 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   组合分配域  [design]                                           │
│   src/zephyr/pf_alloc/__init__.py  [prototype]                   │
│   src/zephyr/pf_alloc/_extensions/__init__.py  [scaffold_plac... │
│   src/zephyr/pf_alloc/api/__init__.py  [scaffold_placeholder]    │
│   约束求解  [design]                                             │
│   src/zephyr/pf_alloc/core/__init__.py  [scaffold_placeholder]   │
│   src/zephyr/pf_alloc/infrastructure/__init__.py  [scaffold_p... │
│   src/zephyr/pf_alloc/models/__init__.py  [scaffold_placeholder] │
│   分配优化器  [design]                                           │
│   再平衡引擎  [design]                                           │
│   风险预算  [design]                                             │
│   src/zephyr/pf_alloc/services/__init__.py  [scaffold_placeho... │
│   src/zephyr/pf_alloc/strategy_lifecycle_event.py  [prototype]   │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (99 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   4级决策 APPROVE/REDUCE/REJECT/FLATTEN  [design]                │
│   7状态生命周期 7-State Lifecycle  [design]                      │
│   A-Share Dynamic Position Coefficient Calculator A股动态仓位... │
│   A-Share Kelly Position Dynamic Calculator A股凯利仓位动态计... │
│   A-Share Position Formula Calculator A股仓位公式计算器  [des... │
│   CapitalAllocationResult Contract CapitalAllocationResult 策... │
│   Copula-GARCH Copula-GARCH模型  [design]                        │
│   D-EXECUTION 执行  [design]                                     │
│   D-L0→D-L1 降级路径  [design]                                   │
│   D-L1→D-L2 降级路径  [design]                                   │
│   D-L2→D-L3 降级路径  [design]                                   │
│   D-PF-ALLOC 组合分配域 Portfolio Allocation Domain  [design]    │
│   Dynamic Capital Allocator 动态资金分配器  [design]             │
│   E-0073 D-RISK→D-PF-ALLOC边  [design]                           │
│   ESRB系统性风险向量 ESRB Systemic Risk Vector  [design]         │
│   Execution Feedback Bridge执行反馈桥  [design]                  │
│   IC加权 IC Weighting  [design]                                  │
│   Kelly公式 Kelly Formula  [design]                              │
│   ...还有 81 个模块 / 81 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 114 个模块 / 114 modules）。

### L1 基础层 / Foundation Layer (2 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/pf_core/default_equity_strategy.py | src/zephyr/pf_core/default_equity_str... | prototype | draft |
| 2 | src/zephyr/pf_core/strategy_portfolio.py | src/zephyr/pf_core/strategy_portfolio.py | prototype | draft |

### L2 领域层 / Domain Layer (13 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/pf_alloc/ | 组合分配域 | design | design_only |
| 2 | src/zephyr/pf_alloc/__init__.py | src/zephyr/pf_alloc/__init__.py | prototype | draft |
| 3 | src/zephyr/pf_alloc/_extensions/__init__.py | src/zephyr/pf_alloc/_extensions/__ini... | scaffold_placeholder | orphan |
| 4 | src/zephyr/pf_alloc/api/__init__.py | src/zephyr/pf_alloc/api/__init__.py | scaffold_placeholder | orphan |
| 5 | src/zephyr/pf_alloc/constraint/ | 约束求解 | design | design_only |
| 6 | src/zephyr/pf_alloc/core/__init__.py | src/zephyr/pf_alloc/core/__init__.py | scaffold_placeholder | orphan |
| 7 | src/zephyr/pf_alloc/infrastructure/__init__.py | src/zephyr/pf_alloc/infrastructure/__... | scaffold_placeholder | orphan |
| 8 | src/zephyr/pf_alloc/models/__init__.py | src/zephyr/pf_alloc/models/__init__.py | scaffold_placeholder | orphan |
| 9 | src/zephyr/pf_alloc/optimizer/ | 分配优化器 | design | design_only |
| 10 | src/zephyr/pf_alloc/rebalance/ | 再平衡引擎 | design | design_only |
| 11 | src/zephyr/pf_alloc/risk_budget/ | 风险预算 | design | design_only |
| 12 | src/zephyr/pf_alloc/services/__init__.py | src/zephyr/pf_alloc/services/__init__.py | scaffold_placeholder | orphan |
| 13 | src/zephyr/pf_alloc/strategy_lifecycle_event.py | src/zephyr/pf_alloc/strategy_lifecycl... | prototype | draft |

### 未分类 / Unclassified (99 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-PF-ALLOC/4级决策 APPROVE/REDUCE/REJECT/FLATTEN | 4级决策 APPROVE/REDUCE/REJECT/FLATTEN | design | design_only |
| 2 | D-PF-ALLOC/7状态生命周期 7-State Lifecycle | 7状态生命周期 7-State Lifecycle | design | design_only |
| 3 | D-PF-ALLOC/A-Share Dynamic Position Coefficient Calculato... | A-Share Dynamic Position Coefficient ... | design | design_only |
| 4 | D-PF-ALLOC/A-Share Kelly Position Dynamic Calculator A股... | A-Share Kelly Position Dynamic Calcul... | design | design_only |
| 5 | D-PF-ALLOC/A-Share Position Formula Calculator A股仓位公... | A-Share Position Formula Calculator A... | design | design_only |
| 6 | D-PF-ALLOC/CapitalAllocationResult Contract CapitalAlloca... | CapitalAllocationResult Contract Capi... | design | design_only |
| 7 | D-PF-ALLOC/Copula-GARCH Copula-GARCH模型 | Copula-GARCH Copula-GARCH模型 | design | design_only |
| 8 | D-PF-ALLOC/D-EXECUTION 执行 | D-EXECUTION 执行 | design | design_only |
| 9 | D-PF-ALLOC/D-L0→D-L1 降级路径 | D-L0→D-L1 降级路径 | design | design_only |
| 10 | D-PF-ALLOC/D-L1→D-L2 降级路径 | D-L1→D-L2 降级路径 | design | design_only |
| 11 | D-PF-ALLOC/D-L2→D-L3 降级路径 | D-L2→D-L3 降级路径 | design | design_only |
| 12 | D-PF-ALLOC/D-PF-ALLOC 组合分配域 Portfolio Allocation Domain | D-PF-ALLOC 组合分配域 Portfolio Alloc... | design | design_only |
| 13 | D-PF-ALLOC/Dynamic Capital Allocator 动态资金分配器 | Dynamic Capital Allocator 动态资金分配器 | design | design_only |
| 14 | D-PF-ALLOC/E-0073 D-RISK→D-PF-ALLOC边 | E-0073 D-RISK→D-PF-ALLOC边 | design | design_only |
| 15 | D-PF-ALLOC/ESRB系统性风险向量 ESRB Systemic Risk Vector | ESRB系统性风险向量 ESRB Systemic Risk... | design | design_only |
| 16 | D-PF-ALLOC/Execution Feedback Bridge执行反馈桥 | Execution Feedback Bridge执行反馈桥 | design | design_only |
| 17 | D-PF-ALLOC/IC加权 IC Weighting | IC加权 IC Weighting | design | design_only |
| 18 | D-PF-ALLOC/Kelly公式 Kelly Formula | Kelly公式 Kelly Formula | design | design_only |
| 19 | D-PF-ALLOC/Leverage Manager 杠杆管理器 | Leverage Manager 杠杆管理器 | design | design_only |
| 20 | D-PF-ALLOC/MOD-L05-001 蓝图 | MOD-L05-001 蓝图 | design | design_only |
| 21 | D-PF-ALLOC/MaxDDLimit Allocation Strategist最大回撤限制分... | MaxDDLimit Allocation Strategist最大... | design | design_only |
| 22 | D-PF-ALLOC/Meta-Strategy Router元策略路由 | Meta-Strategy Router元策略路由 | design | design_only |
| 23 | D-PF-ALLOC/Module Registry 4状态映射 | Module Registry 4状态映射 | design | design_only |
| 24 | D-PF-ALLOC/Multi-Strategy Capital Allocator多策略资金分配 | Multi-Strategy Capital Allocator多策... | design | design_only |
| 25 | D-PF-ALLOC/P2 signal_engine 策略路由进程 | P2 signal_engine 策略路由进程 | design | design_only |
| 26 | D-PF-ALLOC/PA-02 Strategy Screening 3D 策略 | PA-02 Strategy Screening 3D 策略 | design | design_only |
| 27 | D-PF-ALLOC/PA-03 Rolling Window Correlation PA-03滚动窗口... | PA-03 Rolling Window Correlation PA-0... | design | design_only |
| 28 | D-PF-ALLOC/PA-04增量 标的级/板块级集中度监控 | PA-04增量 标的级/板块级集中度监控 | design | design_only |
| 29 | D-PF-ALLOC/PA-04增量 隐性串谋检测扩展 | PA-04增量 隐性串谋检测扩展 | design | design_only |
| 30 | D-PF-ALLOC/PA-05增量 传染路径检测与隔离 | PA-05增量 传染路径检测与隔离 | design | design_only |
| 31 | D-PF-ALLOC/PA-06/07/08 A-Share Position 仓位 | PA-06/07/08 A-Share Position 仓位 | design | design_only |
| 32 | D-PF-ALLOC/PA-09 Stackelberg Game PA-09斯塔克尔伯格博弈 | PA-09 Stackelberg Game PA-09斯塔克尔... | design | design_only |
| 33 | D-PF-ALLOC/PA-11/12 Strategy Retirement 策略 | PA-11/12 Strategy Retirement 策略 | design | design_only |
| 34 | D-PF-ALLOC/PA-14 Position Limit Gate 仓位 | PA-14 Position Limit Gate 仓位 | design | design_only |
| 35 | D-PF-ALLOC/PA-15 Execution Feedback Bridge 执行 | PA-15 Execution Feedback Bridge 执行 | design | design_only |
| 36 | D-PF-ALLOC/PA-CapitalAllocated 事件 | PA-CapitalAllocated 事件 | design | design_only |
| 37 | D-PF-ALLOC/PA-CorrelationGateTriggered 事件 | PA-CorrelationGateTriggered 事件 | design | design_only |
| 38 | D-PF-ALLOC/PA-E01 CapitalAllocated 资本分配完成事件 | PA-E01 CapitalAllocated 资本分配完成事件 | design | design_only |
| 39 | D-PF-ALLOC/PA-E02 StrategyRetired 策略退役事件 | PA-E02 StrategyRetired 策略退役事件 | design | design_only |
| 40 | D-PF-ALLOC/PA-E03 CorrelationGateTriggered 相关性门禁触发... | PA-E03 CorrelationGateTriggered 相关... | design | design_only |
| 41 | D-PF-ALLOC/PA-E04 StrategyScreened 策略筛选完成事件 | PA-E04 StrategyScreened 策略筛选完成事件 | design | design_only |
| 42 | D-PF-ALLOC/PA-StrategyRetired 事件 | PA-StrategyRetired 事件 | design | design_only |
| 43 | D-PF-ALLOC/PA-StrategyRetired 策略退役事件 | PA-StrategyRetired 策略退役事件 | design | design_only |
| 44 | D-PF-ALLOC/Position Limit Gate Checker仓位限制门禁检查器 | Position Limit Gate Checker仓位限制门... | design | design_only |
| 45 | D-PF-ALLOC/Position Sizer 仓位计算器 | Position Sizer 仓位计算器 | design | design_only |
| 46 | D-PF-ALLOC/RebalanceDecided 再平衡决策事件 | RebalanceDecided 再平衡决策事件 | design | design_only |
| 47 | D-PF-ALLOC/RebalanceDecided事件 | RebalanceDecided事件 | design | design_only |
| 48 | D-PF-ALLOC/Rolling Window Dynamic Correlation Analyzer滚... | Rolling Window Dynamic Correlation An... | design | design_only |
| 49 | D-PF-ALLOC/ST-006 量化踩踏 | ST-006 量化踩踏 | design | design_only |
| 50 | D-PF-ALLOC/Signal Synthesis Combiner信号合成器 | Signal Synthesis Combiner信号合成器 | design | design_only |
| 51 | D-PF-ALLOC/Stackelberg Game-Theoretic Follower Stackelber... | Stackelberg Game-Theoretic Follower S... | design | design_only |
| 52 | D-PF-ALLOC/Strategy Correlation Gate G12 Executor策略相关... | Strategy Correlation Gate G12 Executo... | design | design_only |
| 53 | D-PF-ALLOC/Strategy Retirement Capital Recycler策略退役资... | Strategy Retirement Capital Recycler... | design | design_only |
| 54 | D-PF-ALLOC/Strategy Retirement Trigger策略退役触发器 | Strategy Retirement Trigger策略退役触... | design | design_only |
| 55 | D-PF-ALLOC/Strategy Screening 3D Evaluator策略筛选三维评估器 | Strategy Screening 3D Evaluator策略筛... | design | design_only |
| 56 | D-PF-ALLOC/_PARALLEL_DISCUSSIONS.md 并行 | _PARALLEL_DISCUSSIONS.md 并行 | design | design_only |
| 57 | D-PF-ALLOC/§30.1.4 D-PF-ALLOC 组合分配域（15个模块） | §30.1.4 D-PF-ALLOC 组合分配域（15个... | design | design_only |
| 58 | D-PF-ALLOC/仲裁规则 Arbitration Rules | 仲裁规则 Arbitration Rules | design | design_only |
| 59 | D-PF-ALLOC/体制自适应权重 Regime Adaptive Weight | 体制自适应权重 Regime Adaptive Weight | design | design_only |
| 60 | D-PF-ALLOC/信号传染 Signal Contagion | 信号传染 Signal Contagion | design | design_only |
| 61 | D-PF-ALLOC/信号冲突检测 Signal Conflict Detection | 信号冲突检测 Signal Conflict Detection | design | design_only |
| 62 | D-PF-ALLOC/共振融合 Resonance Fusion | 共振融合 Resonance Fusion | design | design_only |
| 63 | D-PF-ALLOC/决策去重 Decision Deduplication | 决策去重 Decision Deduplication | design | design_only |
| 64 | D-PF-ALLOC/冷启动协议 Cold Start Protocol | 冷启动协议 Cold Start Protocol | design | design_only |
| 65 | D-PF-ALLOC/准入门控 Admission Gate | 准入门控 Admission Gate | design | design_only |
| 66 | D-PF-ALLOC/分批建仓 Batch Position Building | 分批建仓 Batch Position Building | design | design_only |
| 67 | D-PF-ALLOC/半Kelly硬上限 Half Kelly Hard Cap | 半Kelly硬上限 Half Kelly Hard Cap | design | design_only |
| 68 | D-PF-ALLOC/因子模型 Factor Model | 因子模型 Factor Model | design | design_only |
| 69 | D-PF-ALLOC/因子正交性 Factor Orthogonality | 因子正交性 Factor Orthogonality | design | design_only |
| 70 | D-PF-ALLOC/因子重叠 Factor Overlap | 因子重叠 Factor Overlap | design | design_only |
| 71 | D-PF-ALLOC/域内依赖图 Intra-domain Dependency Graph | 域内依赖图 Intra-domain Dependency Graph | design | design_only |
| 72 | D-PF-ALLOC/多策略投票 Multi-Strategy Voting | 多策略投票 Multi-Strategy Voting | design | design_only |
| 73 | D-PF-ALLOC/安全隔离 Safety Isolation | 安全隔离 Safety Isolation | design | design_only |
| 74 | D-PF-ALLOC/尾部相关性飙升 Tail Correlation Surge | 尾部相关性飙升 Tail Correlation Surge | design | design_only |
| 75 | D-PF-ALLOC/情绪传染 Sentiment Contagion | 情绪传染 Sentiment Contagion | design | design_only |
| 76 | D-PF-ALLOC/收缩估计 Shrinkage Estimation | 收缩估计 Shrinkage Estimation | design | design_only |
| 77 | D-PF-ALLOC/数据流优化 Data Flow Optimization | 数据流优化 Data Flow Optimization | design | design_only |
| 78 | D-PF-ALLOC/板块级拥挤 Sector-level Crowding | 板块级拥挤 Sector-level Crowding | design | design_only |
| 79 | D-PF-ALLOC/标的级拥挤 Target-level Crowding | 标的级拥挤 Target-level Crowding | design | design_only |
| 80 | D-PF-ALLOC/模块组合发现 Module Combination Discovery | 模块组合发现 Module Combination Disco... | design | design_only |
| 81 | D-PF-ALLOC/模型共振反应 Model Resonance Response | 模型共振反应 Model Resonance Response | design | design_only |
| 82 | D-PF-ALLOC/模型叠加尾部放大 Model Stacking Tail Amplifica... | 模型叠加尾部放大 Model Stacking Tail ... | design | design_only |
| 83 | D-PF-ALLOC/模型间假设不一致 Inter-model Assumption Incons... | 模型间假设不一致 Inter-model Assumpti... | design | design_only |
| 84 | D-PF-ALLOC/盘中执行必做项 Intraday Execution Must-do | 盘中执行必做项 Intraday Execution Mus... | design | design_only |
| 85 | D-PF-ALLOC/目标权重向量输出 Target Weight Vector Output | 目标权重向量输出 Target Weight Vector... | design | design_only |
| 86 | D-PF-ALLOC/相关性体制监控 Correlation Regime Monitoring | 相关性体制监控 Correlation Regime Mon... | design | design_only |
| 87 | D-PF-ALLOC/策略冲突检测 Strategy Conflict Detection | 策略冲突检测 Strategy Conflict Detection | design | design_only |
| 88 | D-PF-ALLOC/策略同质化检测 Strategy Homogeneity Detection | 策略同质化检测 Strategy Homogeneity D... | design | design_only |
| 89 | D-PF-ALLOC/策略容量超限 Strategy Capacity Exceeded | 策略容量超限 Strategy Capacity Exceeded | design | design_only |
| 90 | D-PF-ALLOC/策略指纹相似度 Strategy Fingerprint Similarity | 策略指纹相似度 Strategy Fingerprint S... | design | design_only |
| 91 | D-PF-ALLOC/策略权重进化 Strategy Weight Evolution | 策略权重进化 Strategy Weight Evolution | design | design_only |
| 92 | D-PF-ALLOC/策略衰减检测 Strategy Decay Detection | 策略衰减检测 Strategy Decay Detection | design | design_only |
| 93 | D-PF-ALLOC/组合级硬约束 Portfolio Hard Constraints | 组合级硬约束 Portfolio Hard Constraints | design | design_only |
| 94 | D-PF-ALLOC/股票池重叠 Stock Pool Overlap | 股票池重叠 Stock Pool Overlap | design | design_only |
| 95 | D-PF-ALLOC/解耦保证 Decoupling Guarantee | 解耦保证 Decoupling Guarantee | design | design_only |
| 96 | D-PF-ALLOC/资本传染 Capital Contagion | 资本传染 Capital Contagion | design | design_only |
| 97 | D-PF-ALLOC/跨策略仓位合并 Cross-Strategy Position Merging | 跨策略仓位合并 Cross-Strategy Positio... | design | design_only |
| 98 | D-PF-ALLOC/隐性串谋检测 Implicit Collusion Detection | 隐性串谋检测 Implicit Collusion Detec... | design | design_only |
| 99 | D-PF-ALLOC/风险预算范式 Risk Budgeting Paradigm | 风险预算范式 Risk Budgeting Paradigm | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 100 条 / 100 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 100 条 / 100 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 5                               │
│   [import_depends]: 83 条 / edges                                │
│   [event]: 12 条 / edges                                         │
│   [contract]: 2 条 / edges                                       │
│   [config_depends]: 2 条 / edges                                 │
│   [data]: 1 条 / edges                                           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (83 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   A-Share Dynamic Position ... → Meta-Strategy Router元策...     │
│   A-Share Dynamic Position ... → D-EXECUTION 执行                │
│   Meta-Strategy Router元策... → Strategy Screening 3D Eva...     │
│   Strategy Screening 3D Eva... → Rolling Window Dynamic Co...    │
│   Rolling Window Dynamic Co... → Multi-Strategy Capital Al...    │
│   Multi-Strategy Capital Al... → Strategy Correlation Gate...    │
│   Strategy Correlation Gate... → A-Share Position Formula ...    │
│   A-Share Position Formula ... → A-Share Kelly Position Dy...    │
│   A-Share Kelly Position Dy... → Stackelberg Game-Theoreti...    │
│   Stackelberg Game-Theoreti... → Signal Synthesis Combiner...    │
│   Signal Synthesis Combiner... → Strategy Retirement Trigg...    │
│   Strategy Retirement Trigg... → Strategy Retirement Capit...    │
│   Strategy Retirement Capit... → MaxDDLimit Allocation Str...    │
│   MaxDDLimit Allocation Str... → Position Limit Gate Check...    │
│   Position Limit Gate Check... → Execution Feedback Bridge...    │
│   Execution Feedback Bridge... → §30.1.4 D-PF-ALLOC 组合...      │
│   §30.1.4 D-PF-ALLOC 组合... → Dynamic Capital Allocator...      │
│   Dynamic Capital Allocator... → Position Sizer 仓位计算器       │
│   Position Sizer 仓位计算器 → Leverage Manager 杠杆管理器        │
│   Leverage Manager 杠杆管理器 → PA-02 Strategy Screening ...     │
│   PA-02 Strategy Screening ... → PA-03 Rolling Window Corr...    │
│   PA-03 Rolling Window Corr... → PA-06/07/08 A-Share Posit...    │
│   PA-06/07/08 A-Share Posit... → PA-09 Stackelberg Game PA...    │
│   PA-09 Stackelberg Game PA... → PA-11/12 Strategy Retirem...    │
│   PA-11/12 Strategy Retirem... → PA-15 Execution Feedback ...    │
│   PA-15 Execution Feedback ... → 体制自适应权重 Regime Ada...    │
│   PA-15 Execution Feedback ... → 域内依赖图 Intra-domain D...    │
│   体制自适应权重 Regime Ada... → 策略指纹相似度 Strategy F...    │
│   策略指纹相似度 Strategy F... → 因子正交性 Factor Orthogo...    │
│   因子正交性 Factor Orthogo... → 多策略投票 Multi-Strategy...    │
│   多策略投票 Multi-Strategy... → 共振融合 Resonance Fusion       │
│   共振融合 Resonance Fusion → 决策去重 Decision Dedupli...       │
│   决策去重 Decision Dedupli... → 跨策略仓位合并 Cross-Stra...    │
│   跨策略仓位合并 Cross-Stra... → 信号冲突检测 Signal Confl...    │
│   信号冲突检测 Signal Confl... → 风险预算范式 Risk Budgeti...    │
│   风险预算范式 Risk Budgeti... → 收缩估计 Shrinkage Estima...    │
│   收缩估计 Shrinkage Estima... → 因子模型 Factor Model           │
│   因子模型 Factor Model → Copula-GARCH Copula-GARCH...           │
│   Copula-GARCH Copula-GARCH... → 相关性体制监控 Correlatio...    │
│   相关性体制监控 Correlatio... → 7状态生命周期 7-State Lif...    │
│   7状态生命周期 7-State Lif... → 冷启动协议 Cold Start Pro...    │
│   冷启动协议 Cold Start Pro... → 策略衰减检测 Strategy Dec...    │
│   策略衰减检测 Strategy Dec... → Kelly公式 Kelly Formula         │
│   Kelly公式 Kelly Formula → 半Kelly硬上限 Half Kelly ...         │
│   半Kelly硬上限 Half Kelly ... → 组合级硬约束 Portfolio Ha...    │
│   组合级硬约束 Portfolio Ha... → 分批建仓 Batch Position B...    │
│   分批建仓 Batch Position B... → 策略同质化检测 Strategy H...    │
│   策略同质化检测 Strategy H... → 隐性串谋检测 Implicit Col...    │
│   隐性串谋检测 Implicit Col... → 尾部相关性飙升 Tail Corre...    │
│   ...还有 34 条 / 34 more edges                                  │
└──────────────────────────────────────────────────────────────────┘

**[event]** (12 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (2 条 / edges) — 已达显示上限，省略 / limit reached

**[config_depends]** (2 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (1 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 100 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `33_d_pf_alloc_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
