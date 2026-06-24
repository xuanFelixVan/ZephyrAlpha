---
doc_type: domain_architecture_doc
title: D-PF_ALLOC 组合分配架构文档
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 33_d_pf_alloc / 组合分配

> **文档作用 / Purpose**: 展示 组合分配（D-PF_ALLOC）功能域的模块清单、域内依赖关系和跨域依赖关系，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-24 23:01:54
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 33 | Number | 33 |
| 域ID | D-PF_ALLOC | Domain ID | D-PF_ALLOC |
| 域名称 | 组合分配 | Domain Name | 组合分配 |
| 层级 | L2_domain | Layer | L2_domain |
| 模块数 | 114 | Module Count | 114 |
| 域内依赖 | 100 | Internal Dependencies | 100 |
| 跨域入边 | 47 | Cross-domain Incoming | 47 |
| 跨域出边 | 156 | Cross-domain Outgoing | 156 |
| 设计态模块 | 104 | Design Modules | 104 |
| 原型态模块 | 4 | Prototype Modules | 4 |
| 生产态模块 | 0 | Production Modules | 0 |
| 容量 | 114/150 (正常) | Capacity | 114/150 (正常) |
| 描述 | 资产组合分配优化 | Description | 资产组合分配优化 |

## 模块清单 / Module List

共 114 个模块（按路径排序，全部显示）

| 模块路径 / Module Path | 模块名称 / Module Name | 设计成熟度 / Maturity | 构建状态 / Build Status |
|---------|---------|-----------|---------|
| D-PF-ALLOC/4级决策 APPROVE/REDUCE/REJECT/FLATTEN | 4级决策 APPROVE/REDUCE/REJECT/FLATTEN | design | design_only |
| D-PF-ALLOC/7状态生命周期 7-State Lifecycle | 7状态生命周期 7-State Lifecycle | design | design_only |
| D-PF-ALLOC/A-Share Dynamic Position Coefficient Calculator A股动态仓位系数 | A-Share Dynamic Position Coefficient ... | design | design_only |
| D-PF-ALLOC/A-Share Kelly Position Dynamic Calculator A股凯利仓位动态计算 | A-Share Kelly Position Dynamic Calcul... | design | design_only |
| D-PF-ALLOC/A-Share Position Formula Calculator A股仓位公式计算器 | A-Share Position Formula Calculator A... | design | design_only |
| D-PF-ALLOC/CapitalAllocationResult Contract CapitalAllocationResult 策略分配契约 | CapitalAllocationResult Contract Capi... | design | design_only |
| D-PF-ALLOC/Copula-GARCH Copula-GARCH模型 | Copula-GARCH Copula-GARCH模型 | design | design_only |
| D-PF-ALLOC/D-EXECUTION 执行 | D-EXECUTION 执行 | design | design_only |
| D-PF-ALLOC/D-L0→D-L1 降级路径 | D-L0→D-L1 降级路径 | design | design_only |
| D-PF-ALLOC/D-L1→D-L2 降级路径 | D-L1→D-L2 降级路径 | design | design_only |
| D-PF-ALLOC/D-L2→D-L3 降级路径 | D-L2→D-L3 降级路径 | design | design_only |
| D-PF-ALLOC/D-PF-ALLOC 组合分配域 Portfolio Allocation Domain | D-PF-ALLOC 组合分配域 Portfolio Allocation... | design | design_only |
| D-PF-ALLOC/Dynamic Capital Allocator 动态资金分配器 | Dynamic Capital Allocator 动态资金分配器 | design | design_only |
| D-PF-ALLOC/E-0073 D-RISK→D-PF-ALLOC边 | E-0073 D-RISK→D-PF-ALLOC边 | design | design_only |
| D-PF-ALLOC/ESRB系统性风险向量 ESRB Systemic Risk Vector | ESRB系统性风险向量 ESRB Systemic Risk Vector | design | design_only |
| D-PF-ALLOC/Execution Feedback Bridge执行反馈桥 | Execution Feedback Bridge执行反馈桥 | design | design_only |
| D-PF-ALLOC/IC加权 IC Weighting | IC加权 IC Weighting | design | design_only |
| D-PF-ALLOC/Kelly公式 Kelly Formula | Kelly公式 Kelly Formula | design | design_only |
| D-PF-ALLOC/Leverage Manager 杠杆管理器 | Leverage Manager 杠杆管理器 | design | design_only |
| D-PF-ALLOC/MOD-L05-001 蓝图 | MOD-L05-001 蓝图 | design | design_only |
| D-PF-ALLOC/MaxDDLimit Allocation Strategist最大回撤限制分配器 | MaxDDLimit Allocation Strategist最大回撤限... | design | design_only |
| D-PF-ALLOC/Meta-Strategy Router元策略路由 | Meta-Strategy Router元策略路由 | design | design_only |
| D-PF-ALLOC/Module Registry 4状态映射 | Module Registry 4状态映射 | design | design_only |
| D-PF-ALLOC/Multi-Strategy Capital Allocator多策略资金分配 | Multi-Strategy Capital Allocator多策略资金分配 | design | design_only |
| D-PF-ALLOC/P2 signal_engine 策略路由进程 | P2 signal_engine 策略路由进程 | design | design_only |
| D-PF-ALLOC/PA-02 Strategy Screening 3D 策略 | PA-02 Strategy Screening 3D 策略 | design | design_only |
| D-PF-ALLOC/PA-03 Rolling Window Correlation PA-03滚动窗口相关性 | PA-03 Rolling Window Correlation PA-0... | design | design_only |
| D-PF-ALLOC/PA-04增量 标的级/板块级集中度监控 | PA-04增量 标的级/板块级集中度监控 | design | design_only |
| D-PF-ALLOC/PA-04增量 隐性串谋检测扩展 | PA-04增量 隐性串谋检测扩展 | design | design_only |
| D-PF-ALLOC/PA-05增量 传染路径检测与隔离 | PA-05增量 传染路径检测与隔离 | design | design_only |
| D-PF-ALLOC/PA-06/07/08 A-Share Position 仓位 | PA-06/07/08 A-Share Position 仓位 | design | design_only |
| D-PF-ALLOC/PA-09 Stackelberg Game PA-09斯塔克尔伯格博弈 | PA-09 Stackelberg Game PA-09斯塔克尔伯格博弈 | design | design_only |
| D-PF-ALLOC/PA-11/12 Strategy Retirement 策略 | PA-11/12 Strategy Retirement 策略 | design | design_only |
| D-PF-ALLOC/PA-14 Position Limit Gate 仓位 | PA-14 Position Limit Gate 仓位 | design | design_only |
| D-PF-ALLOC/PA-15 Execution Feedback Bridge 执行 | PA-15 Execution Feedback Bridge 执行 | design | design_only |
| D-PF-ALLOC/PA-CapitalAllocated 事件 | PA-CapitalAllocated 事件 | design | design_only |
| D-PF-ALLOC/PA-CorrelationGateTriggered 事件 | PA-CorrelationGateTriggered 事件 | design | design_only |
| D-PF-ALLOC/PA-E01 CapitalAllocated 资本分配完成事件 | PA-E01 CapitalAllocated 资本分配完成事件 | design | design_only |
| D-PF-ALLOC/PA-E02 StrategyRetired 策略退役事件 | PA-E02 StrategyRetired 策略退役事件 | design | design_only |
| D-PF-ALLOC/PA-E03 CorrelationGateTriggered 相关性门禁触发事件 | PA-E03 CorrelationGateTriggered 相关性门禁... | design | design_only |
| D-PF-ALLOC/PA-E04 StrategyScreened 策略筛选完成事件 | PA-E04 StrategyScreened 策略筛选完成事件 | design | design_only |
| D-PF-ALLOC/PA-StrategyRetired 事件 | PA-StrategyRetired 事件 | design | design_only |
| D-PF-ALLOC/PA-StrategyRetired 策略退役事件 | PA-StrategyRetired 策略退役事件 | design | design_only |
| D-PF-ALLOC/Position Limit Gate Checker仓位限制门禁检查器 | Position Limit Gate Checker仓位限制门禁检查器 | design | design_only |
| D-PF-ALLOC/Position Sizer 仓位计算器 | Position Sizer 仓位计算器 | design | design_only |
| D-PF-ALLOC/RebalanceDecided 再平衡决策事件 | RebalanceDecided 再平衡决策事件 | design | design_only |
| D-PF-ALLOC/RebalanceDecided事件 | RebalanceDecided事件 | design | design_only |
| D-PF-ALLOC/Rolling Window Dynamic Correlation Analyzer滚动窗口动态相关性 | Rolling Window Dynamic Correlation An... | design | design_only |
| D-PF-ALLOC/ST-006 量化踩踏 | ST-006 量化踩踏 | design | design_only |
| D-PF-ALLOC/Signal Synthesis Combiner信号合成器 | Signal Synthesis Combiner信号合成器 | design | design_only |
| D-PF-ALLOC/Stackelberg Game-Theoretic Follower Stackelberg博弈跟随策略 | Stackelberg Game-Theoretic Follower S... | design | design_only |
| D-PF-ALLOC/Strategy Correlation Gate G12 Executor策略相关性门禁 | Strategy Correlation Gate G12 Executo... | design | design_only |
| D-PF-ALLOC/Strategy Retirement Capital Recycler策略退役资金回收器 | Strategy Retirement Capital Recycler策... | design | design_only |
| D-PF-ALLOC/Strategy Retirement Trigger策略退役触发器 | Strategy Retirement Trigger策略退役触发器 | design | design_only |
| D-PF-ALLOC/Strategy Screening 3D Evaluator策略筛选三维评估器 | Strategy Screening 3D Evaluator策略筛选三维评估器 | design | design_only |
| D-PF-ALLOC/_PARALLEL_DISCUSSIONS.md 并行 | _PARALLEL_DISCUSSIONS.md 并行 | design | design_only |
| D-PF-ALLOC/§30.1.4 D-PF-ALLOC 组合分配域（15个模块） | §30.1.4 D-PF-ALLOC 组合分配域（15个模块） | design | design_only |
| D-PF-ALLOC/仲裁规则 Arbitration Rules | 仲裁规则 Arbitration Rules | design | design_only |
| D-PF-ALLOC/体制自适应权重 Regime Adaptive Weight | 体制自适应权重 Regime Adaptive Weight | design | design_only |
| D-PF-ALLOC/信号传染 Signal Contagion | 信号传染 Signal Contagion | design | design_only |
| D-PF-ALLOC/信号冲突检测 Signal Conflict Detection | 信号冲突检测 Signal Conflict Detection | design | design_only |
| D-PF-ALLOC/共振融合 Resonance Fusion | 共振融合 Resonance Fusion | design | design_only |
| D-PF-ALLOC/决策去重 Decision Deduplication | 决策去重 Decision Deduplication | design | design_only |
| D-PF-ALLOC/冷启动协议 Cold Start Protocol | 冷启动协议 Cold Start Protocol | design | design_only |
| D-PF-ALLOC/准入门控 Admission Gate | 准入门控 Admission Gate | design | design_only |
| D-PF-ALLOC/分批建仓 Batch Position Building | 分批建仓 Batch Position Building | design | design_only |
| D-PF-ALLOC/半Kelly硬上限 Half Kelly Hard Cap | 半Kelly硬上限 Half Kelly Hard Cap | design | design_only |
| D-PF-ALLOC/因子模型 Factor Model | 因子模型 Factor Model | design | design_only |
| D-PF-ALLOC/因子正交性 Factor Orthogonality | 因子正交性 Factor Orthogonality | design | design_only |
| D-PF-ALLOC/因子重叠 Factor Overlap | 因子重叠 Factor Overlap | design | design_only |
| D-PF-ALLOC/域内依赖图 Intra-domain Dependency Graph | 域内依赖图 Intra-domain Dependency Graph | design | design_only |
| D-PF-ALLOC/多策略投票 Multi-Strategy Voting | 多策略投票 Multi-Strategy Voting | design | design_only |
| D-PF-ALLOC/安全隔离 Safety Isolation | 安全隔离 Safety Isolation | design | design_only |
| D-PF-ALLOC/尾部相关性飙升 Tail Correlation Surge | 尾部相关性飙升 Tail Correlation Surge | design | design_only |
| D-PF-ALLOC/情绪传染 Sentiment Contagion | 情绪传染 Sentiment Contagion | design | design_only |
| D-PF-ALLOC/收缩估计 Shrinkage Estimation | 收缩估计 Shrinkage Estimation | design | design_only |
| D-PF-ALLOC/数据流优化 Data Flow Optimization | 数据流优化 Data Flow Optimization | design | design_only |
| D-PF-ALLOC/板块级拥挤 Sector-level Crowding | 板块级拥挤 Sector-level Crowding | design | design_only |
| D-PF-ALLOC/标的级拥挤 Target-level Crowding | 标的级拥挤 Target-level Crowding | design | design_only |
| D-PF-ALLOC/模块组合发现 Module Combination Discovery | 模块组合发现 Module Combination Discovery | design | design_only |
| D-PF-ALLOC/模型共振反应 Model Resonance Response | 模型共振反应 Model Resonance Response | design | design_only |
| D-PF-ALLOC/模型叠加尾部放大 Model Stacking Tail Amplification | 模型叠加尾部放大 Model Stacking Tail Amplific... | design | design_only |
| D-PF-ALLOC/模型间假设不一致 Inter-model Assumption Inconsistency | 模型间假设不一致 Inter-model Assumption Incon... | design | design_only |
| D-PF-ALLOC/盘中执行必做项 Intraday Execution Must-do | 盘中执行必做项 Intraday Execution Must-do | design | design_only |
| D-PF-ALLOC/目标权重向量输出 Target Weight Vector Output | 目标权重向量输出 Target Weight Vector Output | design | design_only |
| D-PF-ALLOC/相关性体制监控 Correlation Regime Monitoring | 相关性体制监控 Correlation Regime Monitoring | design | design_only |
| D-PF-ALLOC/策略冲突检测 Strategy Conflict Detection | 策略冲突检测 Strategy Conflict Detection | design | design_only |
| D-PF-ALLOC/策略同质化检测 Strategy Homogeneity Detection | 策略同质化检测 Strategy Homogeneity Detection | design | design_only |
| D-PF-ALLOC/策略容量超限 Strategy Capacity Exceeded | 策略容量超限 Strategy Capacity Exceeded | design | design_only |
| D-PF-ALLOC/策略指纹相似度 Strategy Fingerprint Similarity | 策略指纹相似度 Strategy Fingerprint Similarity | design | design_only |
| D-PF-ALLOC/策略权重进化 Strategy Weight Evolution | 策略权重进化 Strategy Weight Evolution | design | design_only |
| D-PF-ALLOC/策略衰减检测 Strategy Decay Detection | 策略衰减检测 Strategy Decay Detection | design | design_only |
| D-PF-ALLOC/组合级硬约束 Portfolio Hard Constraints | 组合级硬约束 Portfolio Hard Constraints | design | design_only |
| D-PF-ALLOC/股票池重叠 Stock Pool Overlap | 股票池重叠 Stock Pool Overlap | design | design_only |
| D-PF-ALLOC/解耦保证 Decoupling Guarantee | 解耦保证 Decoupling Guarantee | design | design_only |
| D-PF-ALLOC/资本传染 Capital Contagion | 资本传染 Capital Contagion | design | design_only |
| D-PF-ALLOC/跨策略仓位合并 Cross-Strategy Position Merging | 跨策略仓位合并 Cross-Strategy Position Merging | design | design_only |
| D-PF-ALLOC/隐性串谋检测 Implicit Collusion Detection | 隐性串谋检测 Implicit Collusion Detection | design | design_only |
| D-PF-ALLOC/风险预算范式 Risk Budgeting Paradigm | 风险预算范式 Risk Budgeting Paradigm | design | design_only |
| src/zephyr/pf_alloc/ | 组合分配域 | design | design_only |
| src/zephyr/pf_alloc/__init__.py |  | prototype | draft |
| src/zephyr/pf_alloc/_extensions/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/pf_alloc/api/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/pf_alloc/constraint/ | 约束求解 | design | design_only |
| src/zephyr/pf_alloc/core/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/pf_alloc/infrastructure/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/pf_alloc/models/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/pf_alloc/optimizer/ | 分配优化器 | design | design_only |
| src/zephyr/pf_alloc/rebalance/ | 再平衡引擎 | design | design_only |
| src/zephyr/pf_alloc/risk_budget/ | 风险预算 | design | design_only |
| src/zephyr/pf_alloc/services/__init__.py |  | scaffold_placeholder | orphan |
| src/zephyr/pf_alloc/strategy_lifecycle_event.py |  | prototype | draft |
| src/zephyr/pf_core/default_equity_strategy.py |  | prototype | draft |
| src/zephyr/pf_core/strategy_portfolio.py |  | prototype | draft |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。每30个节点一组分页显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

### 第 1 页 / 共 4 页 / Page 1 of 4

```mermaid
graph TD
    subgraph D_PF_ALLOC["D-PF_ALLOC 组合分配"]
        D_PF_ALLOC_4_APPROVE_REDUCE_REJECT_FLATTEN["4级决策 APPROVE/REDUCE/REJECT/FLATTEN design"]
        D_PF_ALLOC_7_7_State_Lifecycle["7状态生命周期 7-State Lifecycle design"]
        D_PF_ALLOC_A_Share_Dynamic_Position_Coefficient_Calculator_A["A-Share Dynamic Position Coefficient Calculator... design"]
        D_PF_ALLOC_A_Share_Kelly_Position_Dynamic_Calculator_A["A-Share Kelly Position Dynamic Calculator A股凯利仓... design"]
        D_PF_ALLOC_A_Share_Position_Formula_Calculator_A["A-Share Position Formula Calculator A股仓位公式计算器 design"]
        D_PF_ALLOC_CapitalAllocationResult_Contract_CapitalAllocationResult["CapitalAllocationResult Contract CapitalAllocat... design"]
        D_PF_ALLOC_Copula_GARCH_Copula_GARCH["Copula-GARCH Copula-GARCH模型 design"]
        D_PF_ALLOC_D_EXECUTION["D-EXECUTION 执行 design"]
        D_PF_ALLOC_D_L0_D_L1["D-L0→D-L1 降级路径 design"]
        D_PF_ALLOC_D_L1_D_L2["D-L1→D-L2 降级路径 design"]
        D_PF_ALLOC_D_L2_D_L3["D-L2→D-L3 降级路径 design"]
        D_PF_ALLOC_D_PF_ALLOC_Portfolio_Allocation_Domain["D-PF-ALLOC 组合分配域 Portfolio Allocation Domain design"]
        D_PF_ALLOC_Dynamic_Capital_Allocator["Dynamic Capital Allocator 动态资金分配器 design"]
        D_PF_ALLOC_E_0073_D_RISK_D_PF_ALLOC["E-0073 D-RISK→D-PF-ALLOC边 design"]
        D_PF_ALLOC_ESRB_ESRB_Systemic_Risk_Vector["ESRB系统性风险向量 ESRB Systemic Risk Vector design"]
        D_PF_ALLOC_Execution_Feedback_Bridge["Execution Feedback Bridge执行反馈桥 design"]
        D_PF_ALLOC_IC_IC_Weighting["IC加权 IC Weighting design"]
        D_PF_ALLOC_Kelly_Kelly_Formula["Kelly公式 Kelly Formula design"]
        D_PF_ALLOC_Leverage_Manager["Leverage Manager 杠杆管理器 design"]
        D_PF_ALLOC_MOD_L05_001["MOD-L05-001 蓝图 design"]
        D_PF_ALLOC_MaxDDLimit_Allocation_Strategist["MaxDDLimit Allocation Strategist最大回撤限制分配器 design"]
        D_PF_ALLOC_Meta_Strategy_Router["Meta-Strategy Router元策略路由 design"]
        D_PF_ALLOC_Module_Registry_4["Module Registry 4状态映射 design"]
        D_PF_ALLOC_Multi_Strategy_Capital_Allocator["Multi-Strategy Capital Allocator多策略资金分配 design"]
        D_PF_ALLOC_P2_signal_engine["P2 signal_engine 策略路由进程 design"]
        D_PF_ALLOC_PA_02_Strategy_Screening_3D["PA-02 Strategy Screening 3D 策略 design"]
        D_PF_ALLOC_PA_03_Rolling_Window_Correlation_PA_03["PA-03 Rolling Window Correlation PA-03滚动窗口相关性 design"]
        D_PF_ALLOC_PA_04["PA-04增量 标的级/板块级集中度监控 design"]
        D_PF_ALLOC_PA_04_1["PA-04增量 隐性串谋检测扩展 design"]
        D_PF_ALLOC_PA_05["PA-05增量 传染路径检测与隔离 design"]
    end
    D_PF_ALLOC_A_Share_Dynamic_Position_Coefficient_Calculator_A -.->|import_depends| D_PF_ALLOC_Meta_Strategy_Router
    D_PF_ALLOC_A_Share_Dynamic_Position_Coefficient_Calculator_A -.->|import_depends| D_PF_ALLOC_D_EXECUTION
    D_PF_ALLOC_A_Share_Position_Formula_Calculator_A -.->|import_depends| D_PF_ALLOC_A_Share_Kelly_Position_Dynamic_Calculator_A
    D_PF_ALLOC_Leverage_Manager -.->|import_depends| D_PF_ALLOC_PA_02_Strategy_Screening_3D
    D_PF_ALLOC_PA_02_Strategy_Screening_3D -.->|import_depends| D_PF_ALLOC_PA_03_Rolling_Window_Correlation_PA_03
    D_PF_ALLOC_Module_Registry_4 -.->|import_depends| D_PF_ALLOC_D_L0_D_L1
    D_PF_ALLOC_D_L0_D_L1 -.->|import_depends| D_PF_ALLOC_D_L1_D_L2
    D_PF_ALLOC_D_L1_D_L2 -.->|import_depends| D_PF_ALLOC_D_L2_D_L3
    D_PF_ALLOC_D_L2_D_L3 -.->|import_depends| D_PF_ALLOC_P2_signal_engine
    D_PF_ALLOC_D_L2_D_L3 -.->|event| D_PF_ALLOC_E_0073_D_RISK_D_PF_ALLOC
    D_PF_ALLOC_MOD_L05_001 -.->|import_depends| D_PF_ALLOC_IC_IC_Weighting
    D_PF_ALLOC_IC_IC_Weighting -.->|import_depends| D_PF_ALLOC_PA_04_1
    D_PF_ALLOC_PA_04_1 -.->|import_depends| D_PF_ALLOC_PA_04
    D_PF_ALLOC_PA_04 -.->|import_depends| D_PF_ALLOC_PA_05
    D_INTEGRATION["D-INTEGRATION design"]
    D_PF_ALLOC_Meta_Strategy_Router -.->|event| D_INTEGRATION
    D_MKT_DATA["D-MKT_DATA design"]
    D_PF_ALLOC_Multi_Strategy_Capital_Allocator -.->|event| D_MKT_DATA
    D_PF_ALLOC_A_Share_Position_Formula_Calculator_A -.->|contract| D_MKT_DATA
    D_PF_CORE["D-PF_CORE design"]
    D_PF_ALLOC_A_Share_Position_Formula_Calculator_A -.->|event| D_PF_CORE
    D_PF_ALLOC_A_Share_Kelly_Position_Dynamic_Calculator_A -.->|contract| D_PF_CORE
    D_RISK["D-RISK design"]
    D_PF_ALLOC_A_Share_Kelly_Position_Dynamic_Calculator_A -.->|data| D_RISK
    D_SIGNAL["D-SIGNAL design"]
    D_PF_ALLOC_A_Share_Kelly_Position_Dynamic_Calculator_A -.->|contract| D_SIGNAL
    D_AUTONOMY_PERM["D-AUTONOMY_PERM design"]
    D_PF_ALLOC_MaxDDLimit_Allocation_Strategist -.->|event| D_AUTONOMY_PERM
    D_PF_ALLOC_MaxDDLimit_Allocation_Strategist -.->|contract| D_RISK
    D_ML_TRAIN["D-ML_TRAIN design"]
    D_PF_ALLOC_D_EXECUTION -.->|event| D_ML_TRAIN
    D_GOVERNANCE["D-GOVERNANCE design"]
    D_PF_ALLOC_D_EXECUTION -.->|contract| D_GOVERNANCE
    D_SIMULATION["D-SIMULATION design"]
    D_PF_ALLOC_D_EXECUTION -.->|event| D_SIMULATION
    D_INTELLIGENCE["D-INTELLIGENCE design"]
    D_PF_ALLOC_D_EXECUTION -.->|event| D_INTELLIGENCE
    D_SECURITY["D-SECURITY design"]
    D_PF_ALLOC_Execution_Feedback_Bridge -.->|contract| D_SECURITY
    D_PF_ALLOC_Execution_Feedback_Bridge -.->|event| D_RISK
    D_COMPLIANCE["D-COMPLIANCE design"]
    D_COMPLIANCE -.->|data| D_PF_ALLOC_A_Share_Kelly_Position_Dynamic_Calculator_A
    D_FRONTEND["D-FRONTEND design"]
    D_FRONTEND -.->|contract| D_PF_ALLOC_A_Share_Kelly_Position_Dynamic_Calculator_A
    D_OPS["D-OPS design"]
    D_OPS -.->|data| D_PF_ALLOC_A_Share_Kelly_Position_Dynamic_Calculator_A
    D_OPS -.->|contract| D_PF_ALLOC_Execution_Feedback_Bridge
    D_INFRA_OPS["D-INFRA_OPS design"]
    D_INFRA_OPS -.->|event| D_PF_ALLOC_Dynamic_Capital_Allocator
    D_CROSS_ASSET["D-CROSS_ASSET design"]
    D_CROSS_ASSET -.->|event| D_PF_ALLOC_Leverage_Manager
    D_CROSS_ASSET -.->|data| D_PF_ALLOC_CapitalAllocationResult_Contract_CapitalAllocationResult
    D_COMPLIANCE -.->|data| D_PF_ALLOC_PA_02_Strategy_Screening_3D
    D_INFRA_OPS -.->|event| D_PF_ALLOC_Copula_GARCH_Copula_GARCH
    D_COMPLIANCE -.->|event| D_PF_ALLOC_Copula_GARCH_Copula_GARCH
    D_OPS -.->|data| D_PF_ALLOC_4_APPROVE_REDUCE_REJECT_FLATTEN
    D_COMPLIANCE -.->|config_depends| D_PF_ALLOC_D_L0_D_L1
    D_INFRA_OPS -.->|event| D_PF_ALLOC_PA_05
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class D_PF_ALLOC_4_APPROVE_REDUCE_REJECT_FLATTEN,D_PF_ALLOC_7_7_State_Lifecycle,D_PF_ALLOC_A_Share_Dynamic_Position_Coefficient_Calculator_A,D_PF_ALLOC_A_Share_Kelly_Position_Dynamic_Calculator_A,D_PF_ALLOC_A_Share_Position_Formula_Calculator_A,D_PF_ALLOC_CapitalAllocationResult_Contract_CapitalAllocationResult,D_PF_ALLOC_Copula_GARCH_Copula_GARCH,D_PF_ALLOC_D_EXECUTION,D_PF_ALLOC_D_L0_D_L1,D_PF_ALLOC_D_L1_D_L2,D_PF_ALLOC_D_L2_D_L3,D_PF_ALLOC_D_PF_ALLOC_Portfolio_Allocation_Domain,D_PF_ALLOC_Dynamic_Capital_Allocator,D_PF_ALLOC_E_0073_D_RISK_D_PF_ALLOC,D_PF_ALLOC_ESRB_ESRB_Systemic_Risk_Vector,D_PF_ALLOC_Execution_Feedback_Bridge,D_PF_ALLOC_IC_IC_Weighting,D_PF_ALLOC_Kelly_Kelly_Formula,D_PF_ALLOC_Leverage_Manager,D_PF_ALLOC_MOD_L05_001,D_PF_ALLOC_MaxDDLimit_Allocation_Strategist,D_PF_ALLOC_Meta_Strategy_Router,D_PF_ALLOC_Module_Registry_4,D_PF_ALLOC_Multi_Strategy_Capital_Allocator,D_PF_ALLOC_P2_signal_engine,D_PF_ALLOC_PA_02_Strategy_Screening_3D,D_PF_ALLOC_PA_03_Rolling_Window_Correlation_PA_03,D_PF_ALLOC_PA_04,D_PF_ALLOC_PA_04_1,D_PF_ALLOC_PA_05 design
    class D_INTEGRATION,D_MKT_DATA,D_PF_CORE,D_RISK,D_SIGNAL,D_AUTONOMY_PERM,D_ML_TRAIN,D_GOVERNANCE,D_SIMULATION,D_INTELLIGENCE,D_SECURITY,D_COMPLIANCE,D_FRONTEND,D_OPS,D_INFRA_OPS,D_CROSS_ASSET external_design
```

### 第 2 页 / 共 4 页 / Page 2 of 4

```mermaid
graph TD
    subgraph D_PF_ALLOC["D-PF_ALLOC 组合分配"]
        D_PF_ALLOC_PA_06_07_08_A_Share_Position["PA-06/07/08 A-Share Position 仓位 design"]
        D_PF_ALLOC_PA_09_Stackelberg_Game_PA_09["PA-09 Stackelberg Game PA-09斯塔克尔伯格博弈 design"]
        D_PF_ALLOC_PA_11_12_Strategy_Retirement["PA-11/12 Strategy Retirement 策略 design"]
        D_PF_ALLOC_PA_14_Position_Limit_Gate["PA-14 Position Limit Gate 仓位 design"]
        D_PF_ALLOC_PA_15_Execution_Feedback_Bridge["PA-15 Execution Feedback Bridge 执行 design"]
        D_PF_ALLOC_PA_CapitalAllocated["PA-CapitalAllocated 事件 design"]
        D_PF_ALLOC_PA_CorrelationGateTriggered["PA-CorrelationGateTriggered 事件 design"]
        D_PF_ALLOC_PA_E01_CapitalAllocated["PA-E01 CapitalAllocated 资本分配完成事件 design"]
        D_PF_ALLOC_PA_E02_StrategyRetired["PA-E02 StrategyRetired 策略退役事件 design"]
        D_PF_ALLOC_PA_E03_CorrelationGateTriggered["PA-E03 CorrelationGateTriggered 相关性门禁触发事件 design"]
        D_PF_ALLOC_PA_E04_StrategyScreened["PA-E04 StrategyScreened 策略筛选完成事件 design"]
        D_PF_ALLOC_PA_StrategyRetired["PA-StrategyRetired 事件 design"]
        D_PF_ALLOC_PA_StrategyRetired_1["PA-StrategyRetired 策略退役事件 design"]
        D_PF_ALLOC_Position_Limit_Gate_Checker["Position Limit Gate Checker仓位限制门禁检查器 design"]
        D_PF_ALLOC_Position_Sizer["Position Sizer 仓位计算器 design"]
        D_PF_ALLOC_RebalanceDecided["RebalanceDecided 再平衡决策事件 design"]
        D_PF_ALLOC_RebalanceDecided_1["RebalanceDecided事件 design"]
        D_PF_ALLOC_Rolling_Window_Dynamic_Correlation_Analyzer["Rolling Window Dynamic Correlation Analyzer滚动窗口... design"]
        D_PF_ALLOC_ST_006["ST-006 量化踩踏 design"]
        D_PF_ALLOC_Signal_Synthesis_Combiner["Signal Synthesis Combiner信号合成器 design"]
        D_PF_ALLOC_Stackelberg_Game_Theoretic_Follower_Stackelberg["Stackelberg Game-Theoretic Follower Stackelberg... design"]
        D_PF_ALLOC_Strategy_Correlation_Gate_G12_Executor["Strategy Correlation Gate G12 Executor策略相关性门禁 design"]
        D_PF_ALLOC_Strategy_Retirement_Capital_Recycler["Strategy Retirement Capital Recycler策略退役资金回收器 design"]
        D_PF_ALLOC_Strategy_Retirement_Trigger["Strategy Retirement Trigger策略退役触发器 design"]
        D_PF_ALLOC_Strategy_Screening_3D_Evaluator["Strategy Screening 3D Evaluator策略筛选三维评估器 design"]
        D_PF_ALLOC_PARALLEL_DISCUSSIONS_md["_PARALLEL_DISCUSSIONS.md 并行 design"]
        D_PF_ALLOC_30_1_4_D_PF_ALLOC_15["§30.1.4 D-PF-ALLOC 组合分配域（15个模块） design"]
        D_PF_ALLOC_Arbitration_Rules["仲裁规则 Arbitration Rules design"]
        D_PF_ALLOC_Regime_Adaptive_Weight["体制自适应权重 Regime Adaptive Weight design"]
        D_PF_ALLOC_Signal_Contagion["信号传染 Signal Contagion design"]
    end
    D_PF_ALLOC_Strategy_Screening_3D_Evaluator -.->|import_depends| D_PF_ALLOC_Rolling_Window_Dynamic_Correlation_Analyzer
    D_PF_ALLOC_Stackelberg_Game_Theoretic_Follower_Stackelberg -.->|import_depends| D_PF_ALLOC_Signal_Synthesis_Combiner
    D_PF_ALLOC_Signal_Synthesis_Combiner -.->|import_depends| D_PF_ALLOC_Strategy_Retirement_Trigger
    D_PF_ALLOC_Strategy_Retirement_Trigger -.->|import_depends| D_PF_ALLOC_Strategy_Retirement_Capital_Recycler
    D_PF_ALLOC_PA_06_07_08_A_Share_Position -.->|import_depends| D_PF_ALLOC_PA_09_Stackelberg_Game_PA_09
    D_PF_ALLOC_PA_09_Stackelberg_Game_PA_09 -.->|import_depends| D_PF_ALLOC_PA_11_12_Strategy_Retirement
    D_PF_ALLOC_PA_09_Stackelberg_Game_PA_09 -.->|event| D_PF_ALLOC_PA_E04_StrategyScreened
    D_PF_ALLOC_PA_11_12_Strategy_Retirement -.->|import_depends| D_PF_ALLOC_PA_15_Execution_Feedback_Bridge
    D_PF_ALLOC_PA_15_Execution_Feedback_Bridge -.->|import_depends| D_PF_ALLOC_Regime_Adaptive_Weight
    D_RISK["D-RISK design"]
    D_PF_ALLOC_Strategy_Screening_3D_Evaluator -.->|data| D_RISK
    D_INTEGRATION["D-INTEGRATION design"]
    D_PF_ALLOC_Strategy_Screening_3D_Evaluator -.->|contract| D_INTEGRATION
    D_INTELLIGENCE["D-INTELLIGENCE design"]
    D_PF_ALLOC_Rolling_Window_Dynamic_Correlation_Analyzer -.->|data| D_INTELLIGENCE
    D_SIMULATION["D-SIMULATION design"]
    D_PF_ALLOC_Rolling_Window_Dynamic_Correlation_Analyzer -.->|event| D_SIMULATION
    D_KNOWLEDGE["D-KNOWLEDGE design"]
    D_PF_ALLOC_Rolling_Window_Dynamic_Correlation_Analyzer -.->|config_depends| D_KNOWLEDGE
    D_FACTOR["D-FACTOR design"]
    D_PF_ALLOC_Rolling_Window_Dynamic_Correlation_Analyzer -.->|config_depends| D_FACTOR
    D_AUTONOMY_PERM["D-AUTONOMY_PERM design"]
    D_PF_ALLOC_Strategy_Correlation_Gate_G12_Executor -.->|contract| D_AUTONOMY_PERM
    D_PF_CORE["D-PF_CORE design"]
    D_PF_ALLOC_Stackelberg_Game_Theoretic_Follower_Stackelberg -.->|contract| D_PF_CORE
    D_SIGNAL["D-SIGNAL design"]
    D_PF_ALLOC_Signal_Synthesis_Combiner -.->|event| D_SIGNAL
    D_PF_ALLOC_Strategy_Retirement_Capital_Recycler -.->|data| D_RISK
    D_PF_ALLOC_Strategy_Retirement_Capital_Recycler -.->|data| D_SIGNAL
    D_SECURITY["D-SECURITY design"]
    D_PF_ALLOC_Strategy_Retirement_Capital_Recycler -.->|config_depends| D_SECURITY
    D_PF_ALLOC_Strategy_Retirement_Capital_Recycler -.->|event| D_INTEGRATION
    D_PF_ALLOC_RebalanceDecided -.->|data| D_RISK
    D_PF_ALLOC_RebalanceDecided -.->|data| D_SECURITY
    D_FRONTEND["D-FRONTEND design"]
    D_FRONTEND -.->|data| D_PF_ALLOC_Strategy_Screening_3D_Evaluator
    D_FRONTEND -.->|contract| D_PF_ALLOC_Strategy_Correlation_Gate_G12_Executor
    D_COMPLIANCE["D-COMPLIANCE design"]
    D_COMPLIANCE -.->|event| D_PF_ALLOC_30_1_4_D_PF_ALLOC_15
    D_INFRA_OPS["D-INFRA_OPS design"]
    D_INFRA_OPS -.->|config_depends| D_PF_ALLOC_PA_CorrelationGateTriggered
    D_OPS["D-OPS design"]
    D_OPS -.->|config_depends| D_PF_ALLOC_PA_06_07_08_A_Share_Position
    D_COMPLIANCE -.->|contract| D_PF_ALLOC_PA_09_Stackelberg_Game_PA_09
    D_INFRA_OPS -.->|event| D_PF_ALLOC_PA_09_Stackelberg_Game_PA_09
    D_COMPLIANCE -.->|config_depends| D_PF_ALLOC_PA_09_Stackelberg_Game_PA_09
    D_INFRA_OPS -.->|contract| D_PF_ALLOC_PA_14_Position_Limit_Gate
    D_FRONTEND -.->|config_depends| D_PF_ALLOC_PA_14_Position_Limit_Gate
    D_INFRA_OPS -.->|contract| D_PF_ALLOC_PA_E01_CapitalAllocated
    D_COMPLIANCE -.->|data| D_PF_ALLOC_PA_E01_CapitalAllocated
    D_COMPLIANCE -.->|config_depends| D_PF_ALLOC_PA_E03_CorrelationGateTriggered
    D_INFRA_OPS -.->|contract| D_PF_ALLOC_ST_006
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class D_PF_ALLOC_PA_06_07_08_A_Share_Position,D_PF_ALLOC_PA_09_Stackelberg_Game_PA_09,D_PF_ALLOC_PA_11_12_Strategy_Retirement,D_PF_ALLOC_PA_14_Position_Limit_Gate,D_PF_ALLOC_PA_15_Execution_Feedback_Bridge,D_PF_ALLOC_PA_CapitalAllocated,D_PF_ALLOC_PA_CorrelationGateTriggered,D_PF_ALLOC_PA_E01_CapitalAllocated,D_PF_ALLOC_PA_E02_StrategyRetired,D_PF_ALLOC_PA_E03_CorrelationGateTriggered,D_PF_ALLOC_PA_E04_StrategyScreened,D_PF_ALLOC_PA_StrategyRetired,D_PF_ALLOC_PA_StrategyRetired_1,D_PF_ALLOC_Position_Limit_Gate_Checker,D_PF_ALLOC_Position_Sizer,D_PF_ALLOC_RebalanceDecided,D_PF_ALLOC_RebalanceDecided_1,D_PF_ALLOC_Rolling_Window_Dynamic_Correlation_Analyzer,D_PF_ALLOC_ST_006,D_PF_ALLOC_Signal_Synthesis_Combiner,D_PF_ALLOC_Stackelberg_Game_Theoretic_Follower_Stackelberg,D_PF_ALLOC_Strategy_Correlation_Gate_G12_Executor,D_PF_ALLOC_Strategy_Retirement_Capital_Recycler,D_PF_ALLOC_Strategy_Retirement_Trigger,D_PF_ALLOC_Strategy_Screening_3D_Evaluator,D_PF_ALLOC_PARALLEL_DISCUSSIONS_md,D_PF_ALLOC_30_1_4_D_PF_ALLOC_15,D_PF_ALLOC_Arbitration_Rules,D_PF_ALLOC_Regime_Adaptive_Weight,D_PF_ALLOC_Signal_Contagion design
    class D_RISK,D_INTEGRATION,D_INTELLIGENCE,D_SIMULATION,D_KNOWLEDGE,D_FACTOR,D_AUTONOMY_PERM,D_PF_CORE,D_SIGNAL,D_SECURITY,D_FRONTEND,D_COMPLIANCE,D_INFRA_OPS,D_OPS external_design
```

### 第 3 页 / 共 4 页 / Page 3 of 4

```mermaid
graph TD
    subgraph D_PF_ALLOC["D-PF_ALLOC 组合分配"]
        D_PF_ALLOC_Signal_Conflict_Detection["信号冲突检测 Signal Conflict Detection design"]
        D_PF_ALLOC_Resonance_Fusion["共振融合 Resonance Fusion design"]
        D_PF_ALLOC_Decision_Deduplication["决策去重 Decision Deduplication design"]
        D_PF_ALLOC_Cold_Start_Protocol["冷启动协议 Cold Start Protocol design"]
        D_PF_ALLOC_Admission_Gate["准入门控 Admission Gate design"]
        D_PF_ALLOC_Batch_Position_Building["分批建仓 Batch Position Building design"]
        D_PF_ALLOC_Kelly_Half_Kelly_Hard_Cap["半Kelly硬上限 Half Kelly Hard Cap design"]
        D_PF_ALLOC_Factor_Model["因子模型 Factor Model design"]
        D_PF_ALLOC_Factor_Orthogonality["因子正交性 Factor Orthogonality design"]
        D_PF_ALLOC_Factor_Overlap["因子重叠 Factor Overlap design"]
        D_PF_ALLOC_Intra_domain_Dependency_Graph["域内依赖图 Intra-domain Dependency Graph design"]
        D_PF_ALLOC_Multi_Strategy_Voting["多策略投票 Multi-Strategy Voting design"]
        D_PF_ALLOC_Safety_Isolation["安全隔离 Safety Isolation design"]
        D_PF_ALLOC_Tail_Correlation_Surge["尾部相关性飙升 Tail Correlation Surge design"]
        D_PF_ALLOC_Sentiment_Contagion["情绪传染 Sentiment Contagion design"]
        D_PF_ALLOC_Shrinkage_Estimation["收缩估计 Shrinkage Estimation design"]
        D_PF_ALLOC_Data_Flow_Optimization["数据流优化 Data Flow Optimization design"]
        D_PF_ALLOC_Sector_level_Crowding["板块级拥挤 Sector-level Crowding design"]
        D_PF_ALLOC_Target_level_Crowding["标的级拥挤 Target-level Crowding design"]
        D_PF_ALLOC_Module_Combination_Discovery["模块组合发现 Module Combination Discovery design"]
        D_PF_ALLOC_Model_Resonance_Response["模型共振反应 Model Resonance Response design"]
        D_PF_ALLOC_Model_Stacking_Tail_Amplification["模型叠加尾部放大 Model Stacking Tail Amplification design"]
        D_PF_ALLOC_Inter_model_Assumption_Inconsistency["模型间假设不一致 Inter-model Assumption Inconsistency design"]
        D_PF_ALLOC_Intraday_Execution_Must_do["盘中执行必做项 Intraday Execution Must-do design"]
        D_PF_ALLOC_Target_Weight_Vector_Output["目标权重向量输出 Target Weight Vector Output design"]
        D_PF_ALLOC_Correlation_Regime_Monitoring["相关性体制监控 Correlation Regime Monitoring design"]
        D_PF_ALLOC_Strategy_Conflict_Detection["策略冲突检测 Strategy Conflict Detection design"]
        D_PF_ALLOC_Strategy_Homogeneity_Detection["策略同质化检测 Strategy Homogeneity Detection design"]
        D_PF_ALLOC_Strategy_Capacity_Exceeded["策略容量超限 Strategy Capacity Exceeded design"]
        D_PF_ALLOC_Strategy_Fingerprint_Similarity["策略指纹相似度 Strategy Fingerprint Similarity design"]
    end
    D_PF_ALLOC_Strategy_Fingerprint_Similarity -.->|import_depends| D_PF_ALLOC_Factor_Orthogonality
    D_PF_ALLOC_Factor_Orthogonality -.->|import_depends| D_PF_ALLOC_Multi_Strategy_Voting
    D_PF_ALLOC_Multi_Strategy_Voting -.->|import_depends| D_PF_ALLOC_Resonance_Fusion
    D_PF_ALLOC_Resonance_Fusion -.->|import_depends| D_PF_ALLOC_Decision_Deduplication
    D_PF_ALLOC_Shrinkage_Estimation -.->|import_depends| D_PF_ALLOC_Factor_Model
    D_PF_ALLOC_Admission_Gate -.->|config_depends| D_PF_ALLOC_Strategy_Homogeneity_Detection
    D_PF_ALLOC_Batch_Position_Building -.->|import_depends| D_PF_ALLOC_Strategy_Homogeneity_Detection
    D_PF_ALLOC_Tail_Correlation_Surge -.->|import_depends| D_PF_ALLOC_Factor_Overlap
    D_PF_ALLOC_Target_level_Crowding -.->|import_depends| D_PF_ALLOC_Sector_level_Crowding
    D_PF_ALLOC_Sentiment_Contagion -.->|import_depends| D_PF_ALLOC_Inter_model_Assumption_Inconsistency
    D_PF_ALLOC_Inter_model_Assumption_Inconsistency -.->|import_depends| D_PF_ALLOC_Model_Resonance_Response
    D_PF_ALLOC_Model_Resonance_Response -.->|import_depends| D_PF_ALLOC_Model_Stacking_Tail_Amplification
    D_PF_ALLOC_Model_Stacking_Tail_Amplification -.->|import_depends| D_PF_ALLOC_Strategy_Capacity_Exceeded
    D_PF_ALLOC_Module_Combination_Discovery -.->|import_depends| D_PF_ALLOC_Data_Flow_Optimization
    D_PF_ALLOC_Strategy_Conflict_Detection -.->|import_depends| D_PF_ALLOC_Intraday_Execution_Must_do
    D_SELL_DECISION["D-SELL_DECISION design"]
    D_PF_ALLOC_Strategy_Fingerprint_Similarity -.->|event| D_SELL_DECISION
    D_RISK["D-RISK design"]
    D_PF_ALLOC_Resonance_Fusion -.->|contract| D_RISK
    D_INTELLIGENCE["D-INTELLIGENCE design"]
    D_PF_ALLOC_Resonance_Fusion -.->|contract| D_INTELLIGENCE
    D_REPORTING["D-REPORTING design"]
    D_PF_ALLOC_Decision_Deduplication -.->|contract| D_REPORTING
    D_MKT_DATA["D-MKT_DATA design"]
    D_PF_ALLOC_Signal_Conflict_Detection -.->|data| D_MKT_DATA
    D_GOVERNANCE["D-GOVERNANCE design"]
    D_PF_ALLOC_Shrinkage_Estimation -.->|config_depends| D_GOVERNANCE
    D_PF_ALLOC_Shrinkage_Estimation -.->|contract| D_RISK
    D_PF_ALLOC_Factor_Model -.->|contract| D_RISK
    D_EX_SOR["D-EX_SOR design"]
    D_PF_ALLOC_Factor_Model -.->|config_depends| D_EX_SOR
    D_SIGNAL["D-SIGNAL design"]
    D_PF_ALLOC_Correlation_Regime_Monitoring -.->|data| D_SIGNAL
    D_SECURITY["D-SECURITY design"]
    D_PF_ALLOC_Admission_Gate -.->|data| D_SECURITY
    D_PF_ALLOC_Admission_Gate -.->|event| D_RISK
    D_FACTOR["D-FACTOR design"]
    D_PF_ALLOC_Cold_Start_Protocol -.->|contract| D_FACTOR
    D_PF_ALLOC_Batch_Position_Building -.->|contract| D_SECURITY
    D_PF_ALLOC_Batch_Position_Building -.->|data| D_SECURITY
    D_OPS["D-OPS design"]
    D_OPS -.->|event| D_PF_ALLOC_Factor_Orthogonality
    D_COMPLIANCE["D-COMPLIANCE design"]
    D_COMPLIANCE -.->|data| D_PF_ALLOC_Factor_Orthogonality
    D_COMPLIANCE -.->|event| D_PF_ALLOC_Multi_Strategy_Voting
    D_COMPLIANCE -.->|event| D_PF_ALLOC_Decision_Deduplication
    D_COMPLIANCE -.->|data| D_PF_ALLOC_Factor_Model
    D_OPS -.->|contract| D_PF_ALLOC_Correlation_Regime_Monitoring
    D_FRONTEND["D-FRONTEND design"]
    D_FRONTEND -.->|contract| D_PF_ALLOC_Strategy_Homogeneity_Detection
    D_COMPLIANCE -.->|contract| D_PF_ALLOC_Factor_Overlap
    D_COMPLIANCE -.->|data| D_PF_ALLOC_Sector_level_Crowding
    D_INFRA_OPS["D-INFRA_OPS design"]
    D_INFRA_OPS -.->|contract| D_PF_ALLOC_Intraday_Execution_Must_do
    D_INFRA_OPS -.->|event| D_PF_ALLOC_Intraday_Execution_Must_do
    D_COMPLIANCE -.->|config_depends| D_PF_ALLOC_Safety_Isolation
    D_OPS -.->|contract| D_PF_ALLOC_Intra_domain_Dependency_Graph
    D_COMPLIANCE -.->|config_depends| D_PF_ALLOC_Intra_domain_Dependency_Graph
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class D_PF_ALLOC_Signal_Conflict_Detection,D_PF_ALLOC_Resonance_Fusion,D_PF_ALLOC_Decision_Deduplication,D_PF_ALLOC_Cold_Start_Protocol,D_PF_ALLOC_Admission_Gate,D_PF_ALLOC_Batch_Position_Building,D_PF_ALLOC_Kelly_Half_Kelly_Hard_Cap,D_PF_ALLOC_Factor_Model,D_PF_ALLOC_Factor_Orthogonality,D_PF_ALLOC_Factor_Overlap,D_PF_ALLOC_Intra_domain_Dependency_Graph,D_PF_ALLOC_Multi_Strategy_Voting,D_PF_ALLOC_Safety_Isolation,D_PF_ALLOC_Tail_Correlation_Surge,D_PF_ALLOC_Sentiment_Contagion,D_PF_ALLOC_Shrinkage_Estimation,D_PF_ALLOC_Data_Flow_Optimization,D_PF_ALLOC_Sector_level_Crowding,D_PF_ALLOC_Target_level_Crowding,D_PF_ALLOC_Module_Combination_Discovery,D_PF_ALLOC_Model_Resonance_Response,D_PF_ALLOC_Model_Stacking_Tail_Amplification,D_PF_ALLOC_Inter_model_Assumption_Inconsistency,D_PF_ALLOC_Intraday_Execution_Must_do,D_PF_ALLOC_Target_Weight_Vector_Output,D_PF_ALLOC_Correlation_Regime_Monitoring,D_PF_ALLOC_Strategy_Conflict_Detection,D_PF_ALLOC_Strategy_Homogeneity_Detection,D_PF_ALLOC_Strategy_Capacity_Exceeded,D_PF_ALLOC_Strategy_Fingerprint_Similarity design
    class D_SELL_DECISION,D_RISK,D_INTELLIGENCE,D_REPORTING,D_MKT_DATA,D_GOVERNANCE,D_EX_SOR,D_SIGNAL,D_SECURITY,D_FACTOR,D_OPS,D_COMPLIANCE,D_FRONTEND,D_INFRA_OPS external_design
```

### 第 4 页 / 共 4 页 / Page 4 of 4

```mermaid
graph TD
    subgraph D_PF_ALLOC["D-PF_ALLOC 组合分配"]
        D_PF_ALLOC_Strategy_Weight_Evolution["策略权重进化 Strategy Weight Evolution design"]
        D_PF_ALLOC_Strategy_Decay_Detection["策略衰减检测 Strategy Decay Detection design"]
        D_PF_ALLOC_Portfolio_Hard_Constraints["组合级硬约束 Portfolio Hard Constraints design"]
        D_PF_ALLOC_Stock_Pool_Overlap["股票池重叠 Stock Pool Overlap design"]
        D_PF_ALLOC_Decoupling_Guarantee["解耦保证 Decoupling Guarantee design"]
        D_PF_ALLOC_Capital_Contagion["资本传染 Capital Contagion design"]
        D_PF_ALLOC_Cross_Strategy_Position_Merging["跨策略仓位合并 Cross-Strategy Position Merging design"]
        D_PF_ALLOC_Implicit_Collusion_Detection["隐性串谋检测 Implicit Collusion Detection design"]
        D_PF_ALLOC_Risk_Budgeting_Paradigm["风险预算范式 Risk Budgeting Paradigm design"]
        src_zephyr_pf_alloc["组合分配域 design"]
        src_zephyr_pf_alloc_init_py["src/zephyr/pf_alloc/__init__.py prototype"]
        src_zephyr_pf_alloc_extensions_init_py["src/zephyr/pf_alloc/_extensions/__init__.py scaffold_placeholder"]
        src_zephyr_pf_alloc_api_init_py["src/zephyr/pf_alloc/api/__init__.py scaffold_placeholder"]
        src_zephyr_pf_alloc_constraint["约束求解 design"]
        src_zephyr_pf_alloc_core_init_py["src/zephyr/pf_alloc/core/__init__.py scaffold_placeholder"]
        src_zephyr_pf_alloc_infrastructure_init_py["src/zephyr/pf_alloc/infrastructure/__init__.py scaffold_placeholder"]
        src_zephyr_pf_alloc_models_init_py["src/zephyr/pf_alloc/models/__init__.py scaffold_placeholder"]
        src_zephyr_pf_alloc_optimizer["分配优化器 design"]
        src_zephyr_pf_alloc_rebalance["再平衡引擎 design"]
        src_zephyr_pf_alloc_risk_budget["风险预算 design"]
        src_zephyr_pf_alloc_services_init_py["src/zephyr/pf_alloc/services/__init__.py scaffold_placeholder"]
        src_zephyr_pf_alloc_strategy_lifecycle_event_py["src/zephyr/pf_alloc/strategy_lifecycle_event.py prototype"]
        src_zephyr_pf_core_default_equity_strategy_py["src/zephyr/pf_core/default_equity_strategy.py prototype"]
        src_zephyr_pf_core_strategy_portfolio_py["src/zephyr/pf_core/strategy_portfolio.py prototype"]
    end
    D_SHARED["D-SHARED prototype"]
    src_zephyr_pf_alloc -.->|contract| D_SHARED
    D_GOVERNANCE["D-GOVERNANCE prototype"]
    src_zephyr_pf_core_default_equity_strategy_py -.->|import_depends| D_GOVERNANCE
    D_TRADING["D-TRADING production"]
    src_zephyr_pf_core_default_equity_strategy_py -.->|import_depends| D_TRADING
    src_zephyr_pf_core_strategy_portfolio_py -.->|config_depends| D_GOVERNANCE
    src_zephyr_pf_alloc_strategy_lifecycle_event_py -.->|import_depends| D_SHARED
    D_KNOWLEDGE["D-KNOWLEDGE design"]
    D_PF_ALLOC_Cross_Strategy_Position_Merging -.->|event| D_KNOWLEDGE
    D_INFRA_RUNTIME["D-INFRA_RUNTIME design"]
    D_PF_ALLOC_Cross_Strategy_Position_Merging -.->|data| D_INFRA_RUNTIME
    D_PF_ALLOC_Risk_Budgeting_Paradigm -.->|contract| D_GOVERNANCE
    D_AUTONOMY_CORE["D-AUTONOMY_CORE design"]
    D_PF_ALLOC_Risk_Budgeting_Paradigm -.->|data| D_AUTONOMY_CORE
    D_SECURITY["D-SECURITY design"]
    D_PF_ALLOC_Risk_Budgeting_Paradigm -.->|event| D_SECURITY
    D_PF_ALLOC_Risk_Budgeting_Paradigm -.->|event| D_SECURITY
    D_INTEGRATION["D-INTEGRATION design"]
    D_PF_ALLOC_Portfolio_Hard_Constraints -.->|data| D_INTEGRATION
    D_RISK["D-RISK design"]
    D_PF_ALLOC_Portfolio_Hard_Constraints -.->|contract| D_RISK
    D_POSITION["D-POSITION design"]
    D_PF_ALLOC_Portfolio_Hard_Constraints -.->|config_depends| D_POSITION
    D_PF_ALLOC_Portfolio_Hard_Constraints -.->|data| D_TRADING
    D_GOVERNANCE -.->|import_depends| src_zephyr_pf_core_default_equity_strategy_py
    D_COMPLIANCE["D-COMPLIANCE design"]
    D_COMPLIANCE -.->|data| D_PF_ALLOC_Risk_Budgeting_Paradigm
    D_COMPLIANCE -.->|event| D_PF_ALLOC_Portfolio_Hard_Constraints
    D_COMPLIANCE -.->|event| D_PF_ALLOC_Stock_Pool_Overlap
    D_OPS["D-OPS design"]
    D_OPS -.->|event| D_PF_ALLOC_Stock_Pool_Overlap
    D_INFRA_OPS["D-INFRA_OPS design"]
    D_INFRA_OPS -.->|config_depends| D_PF_ALLOC_Strategy_Weight_Evolution
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class D_PF_ALLOC_Strategy_Weight_Evolution,D_PF_ALLOC_Strategy_Decay_Detection,D_PF_ALLOC_Portfolio_Hard_Constraints,D_PF_ALLOC_Stock_Pool_Overlap,D_PF_ALLOC_Decoupling_Guarantee,D_PF_ALLOC_Capital_Contagion,D_PF_ALLOC_Cross_Strategy_Position_Merging,D_PF_ALLOC_Implicit_Collusion_Detection,D_PF_ALLOC_Risk_Budgeting_Paradigm,src_zephyr_pf_alloc,src_zephyr_pf_alloc_init_py,src_zephyr_pf_alloc_extensions_init_py,src_zephyr_pf_alloc_api_init_py,src_zephyr_pf_alloc_constraint,src_zephyr_pf_alloc_core_init_py,src_zephyr_pf_alloc_infrastructure_init_py,src_zephyr_pf_alloc_models_init_py,src_zephyr_pf_alloc_optimizer,src_zephyr_pf_alloc_rebalance,src_zephyr_pf_alloc_risk_budget,src_zephyr_pf_alloc_services_init_py,src_zephyr_pf_alloc_strategy_lifecycle_event_py,src_zephyr_pf_core_default_equity_strategy_py,src_zephyr_pf_core_strategy_portfolio_py design
    class D_TRADING external_prod
    class D_SHARED,D_GOVERNANCE,D_KNOWLEDGE,D_INFRA_RUNTIME,D_AUTONOMY_CORE,D_SECURITY,D_INTEGRATION,D_RISK,D_POSITION,D_COMPLIANCE,D_OPS,D_INFRA_OPS external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 / Target Domain | 依赖数 / Count | 依赖类型 / Type |
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

### 依赖本域的其他域（入边）/ Depended By

| 源域 / Source Domain | 依赖数 / Count | 依赖类型 / Type |
|------|:---:|---------|
| D-COMPLIANCE | 20 | data,event,contract,config_depends |
| D-INFRA_OPS | 11 | event,config_depends,contract |
| D-OPS | 8 | data,contract,config_depends,event |
| D-FRONTEND | 5 | data,contract,config_depends |
| D-CROSS_ASSET | 2 | event,data |
| D-GOVERNANCE | 1 | import_depends |

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
