---
doc_type: audit_report
title: 候选模块清单 — D_PF_CORE
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_PF_CORE 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **137** 条（原有 0 + harvest 137）。
> harvest 去重四态: likely_new=70 / likely_implemented=33 / likely_planned=10 / uncertain=24

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 四问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-HARVEST-0014 | Strategy Factory 策略工厂 | C 006：策略工厂 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0015 | Multi-Scenario Response & Contingency 多情景对策与预案 | C 005：多情景对策与预案 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0018 | Strategy Capacity Modeling 策略容量建模 | C 042：策略容量建模 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0024 | Factor/Strategy Crowding Deep Detection 因子/策略拥挤度深度检测 | C 045：因子/策略拥挤度深度检测 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0030 | Explainability 决策可解释性与溯源 | C 030：决策可解释性与溯源（P0） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0047 | 多账户多策略 Strategy | C 018：多账户多策略 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0092 | Strategy Engine策略引擎 | / PC-01 / Strategy Engine策略引擎 / ✅ 能建 / 📋 项目内有蓝图编号MOD-L05-001部分建设 / 策略注册+选择+信号生成+生命周期管理 / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0093 | Portfolio Optimizer组合优化器 | / PC-02 / Portfolio Optimizer组合优化器 / ✅ 能建 / / 均值方差+风险平价+Black-Litterman+CPPI+TIPP。与§29.9 RL组合优化互补: PC-02提供传统优化基线, §29.9 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0095 | Constraint Solver约束求解器 | / PC-04 / Constraint Solver约束求解器 / ✅ 能建 / / 权重边界+行业集中度+流动性+ESG+监管约束 / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0096 | Risk Parity Engine风险平价引擎 | / PC-05 / Risk Parity Engine风险平价引擎 / ✅ 能建 / / 等风险贡献+层次风险平价+因子风险平价 / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0097 | Multi-Objective Optimizer多目标优化器 | / PC-06 / Multi-Objective Optimizer多目标优化器 / ❌ 不能建 / / 门禁: ①组合优化器PC-02稳定运行 ②开发带宽释放 / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0098 | Tax Loss Harvester税损收割器 | / PC-07 / Tax Loss Harvester税损收割器 / ❌ 不能建 / / 门禁: Long-Only T+1无做空对冲，税损收割空间有限 / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0099 | Portfolio Drift Monitor组合漂移监控器 | / PC-08 / Portfolio Drift Monitor组合漂移监控器 / ✅ 能建 / / 权重/因子暴露/风险/风格漂移检测+CUSUM / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0100 | Cash Flow Manager资金流管理器 | / PC-09 / Cash Flow Manager资金流管理器 / ✅ 能建 / / 申购赎回+分红再投资+现金拖累优化 / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0101 | Rebalance Cost Analyzer再平衡成本分析器 | / PC-10 / Rebalance Cost Analyzer再平衡成本分析器 / ✅ 能建 / / 显性(佣金/印花税)+隐性(冲击/价差)+税收+机会成本 / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0102 | Liquidity Estimator流动性估计器 | / PC-11 / Liquidity Estimator流动性估计器 / ✅ 能建 / / 市场深度+成交量预测+流动性风险评分 / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0103 | Portfolio Stress Tester组合压力测试器 | / PC-12 / Portfolio Stress Tester组合压力测试器 / ✅ 能建 / / 历史+假设+反向压力测试+敏感性分析 / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0104 | Sector Exposure Manager行业敞口管理器 | / PC-13 / Sector Exposure Manager行业敞口管理器 / ✅ 能建 / / GICS/申万分类+敞口计算+集中度监控 / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0105 | Factor Exposure Manager因子敞口管理器 | / PC-14 / Factor Exposure Manager因子敞口管理器 / ✅ 能建 / / 风格/行业/国家因子敞口+Barra风险模型 / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0106 | Portfolio Benchmark Manager组合基准管理器 | / PC-15 / Portfolio Benchmark Manager组合基准管理器 / ✅ 能建 / / 基准选择+跟踪误差+信息比率+主动份额 / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0107 | Carbon Footprint Calculator碳足迹计算器 | / PC-16 / Carbon Footprint Calculator碳足迹计算器 / ❌ 不能建 / / 门禁: ①ESG数据源接入 ②50万AUM规模无需碳报告 / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0108 | Strategy Capacity Estimator策略容量估计器 | / PC-17 / Strategy Capacity Estimator策略容量估计器 / ✅ 能建 / / AUM容量上限+利用率+流动性约束容量 / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0109 | Performance Attribution Engine绩效归因引擎 | / PC-18 / Performance Attribution Engine绩效归因引擎 / ✅ 能建 / 📋 项目有蓝图编号MOD-L07-001但是没建设 / Brinson归因+因子归因+选股/择时分解 / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0358 | §2.1 多源数据接入与分层存储架构 Data Ingestion Storage | §2.1 多源数据接入与分层存储架构 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0359 | 模块3 缺口回补概率模型（Gap Fill Probability Model） | 模块3 缺口回补概率模型（Gap Fill Probability Model） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0360 | 模块4 逼空行情检测模型（Short Squeeze Detection Model） | 模块4 逼空行情检测模型（Short Squeeze Detection Model） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0361 | 模块7 多指标背离检测模型（Multi-Indicator Divergence Detection Model） | ### 模块7 多指标背离检测模型（Multi-Indicator Divergence Detection Model） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0362 | 模块8 板块资金流再配置模型（Sector Flow Reallocation Model） | 模块8 板块资金流再配置模型（Sector Flow Reallocation Model） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0363 | 模块10 动量领导因子与涨停板生态模型（Momentum Leadership & Limit-Up Factor） | ### 模块10 动量领导因子与涨停板生态模型（Momentum Leadership & Limit-Up Factor） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0364 | 模块11 动量层级与板块持续性模型（Momentum Hierarchy & Persistence Model） | ### 模块11 动量层级与板块持续性模型（Momentum Hierarchy & Persistence Model） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0365 | 模块12 板块间资金流迁移检测模型（Inter-Sector Flow Migration Detection） | ### 模块12 板块间资金流迁移检测模型（Inter-Sector Flow Migration Detection） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0366 | 模块15 假突破与诱多检测模型（False Breakout & Bull Trap Detection Model） | ### 模块15 假突破与诱多检测模型（False Breakout & Bull Trap Detection Model） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0367 | 模块16 情绪-价格背离指数模型（Sentiment-Price Divergence Index） | 模块16 情绪 价格背离指数模型（Sentiment Price Divergence Index） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0369 | 19.2 Ensemble-HMM增强框架 | 19.2 Ensemble HMM增强框架 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0370 | 模块26 3秒级逆势资金流识别模块 Module 26 3-Second Contrarian Capital Flow Identification | 模块26 3秒级逆势资金流识别模块 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0371 | 26.5 逆势资金流与已有模块的联动 26.5 Contrarian Capital Flow Linkage with Existing Modules | 26.5 逆势资金流与已有模块的联动 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0372 | 模块31 协同交易行为检测模型（Coordinated Trading Detection Model） | ### 模块31 协同交易行为检测模型（Coordinated Trading Detection Model） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0373 | 31.3 高级协同检测（基于ESMA MABUM框架） | 31.3 高级协同检测（基于ESMA MABUM框架） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0374 | 模块34 异质参与者互动模型（Heterogeneous Agent Interaction Model） | ### 模块34 异质参与者互动模型（Heterogeneous Agent Interaction Model） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0376 | 模块51 波动率压缩与突破模型（Volatility Compression & Breakout Model） | ### 模块51 波动率压缩与突破模型（Volatility Compression & Breakout Model） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0377 | 模块52 汇总：缺失模块与建议归属层映射（更新版） Module 52 Summary: Missing Modules and Suggested Layer Mapping (Updated) | 模块52 汇总：缺失模块与建议归属层映射（更新版） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0378 | 模块58 附录：已有架构覆盖的功能（不重复列出） Module 58 Appendix: Functions Covered by Existing Architecture | 模块58 附录：已有架构覆盖的功能（不重复列出） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0379 | 模块58 附录二：已剔除模块说明（架构文档完全覆盖） Module 58 Appendix 2: Removed Modules Description | 模块58 附录二：已剔除模块说明（架构文档完全覆盖） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0380 | Signal Factory §4.1 信号工厂九大子阶段 | §4.1 信号工厂九大子阶段 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0381 | §4.4 信号聚合器架构 Signal Aggregator | §4.4 信号聚合器架构 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0382 | 模块29 次日上涨概率统一门槛模块 Module 29 Next-Day Rise Probability Unified Threshold | 模块29 次日上涨概率统一门槛模块 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0383 | 模块27 主力假动作与筹码派发识别模块 Module 27 Main Force Fake Action and Chip Distribution Identification | 模块27 主力假动作与筹码派发识别模块 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0384 | 模块23 量能体制自适应策略模型（Volume Regime Adaptive Strategy Model） | ### 模块23 量能体制自适应策略模型（Volume Regime Adaptive Strategy Model） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0385 | 模块32 市场风格体制识别模型（Market Style Regime Identification Model） | ### 模块32 市场风格体制识别模型（Market Style Regime Identification Model） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0386 | 模块28 利好落地变利空（预期透支）模块 Module 28 Good News Becomes Bad News (Expectation Overdraw) | 模块28 利好落地变利空（预期透支）模块 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0387 | 28.5 与已有模块的联动 28.5 Linkage with Existing Modules | 28.5 与已有模块的联动 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0388 | §8.1 策略工厂(C-006)与信号工厂(C-028)的协作 | ### §8.1 策略工厂(C-006)与信号工厂(C-028)的协作 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0389 | §8.5 组合优化引擎 Portfolio Engine | §8.5 组合优化引擎 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0390 | 模块24 核心-卫星仓位管理模型（Core-Satellite Position Management Model） | ### 模块24 核心-卫星仓位管理模型（Core-Satellite Position Management Model） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0391 | Decision Orchestrator 决策编排器——缺失功能模块 | 决策编排器——缺失功能模块 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0392 | 模块57 多因子叠加择时模型（Multi-Factor Overlay Timing Model） | 模块57 多因子叠加择时模型（Multi Factor Overlay Timing Model） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0393 | §12.4 C-033 过拟合系统性防护 | §12.4 C 033 过拟合系统性防护 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0394 | §20.8 方法论约束八：训练-服务一致性(Feature Store) | §20.8 方法论约束八：训练 服务一致性(Feature Store) | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0395 | 决策四：模型/策略漂移检测框架 Strategy Model | 决策四：模型/策略漂移检测框架 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0396 | C-006：策略工厂 | C 006：策略工厂 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0397 | C-047：仓位管理唯一裁决中心 | C 047：仓位管理唯一裁决中心 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0398 | C-016：知识图谱引擎 | C 016：知识图谱引擎 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0399 | C-027：因子工厂（P0） | C 027：因子工厂（P0） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0400 | C-028：信号工厂（P0） | C 028：信号工厂（P0） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0401 | C-033：过拟合系统性防护 | C 033：过拟合系统性防护 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0402 | C-040：系统性压力测试 | C 040：系统性压力测试 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0403 | §24 外部系统交互引用 External | §24 外部系统交互引用 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0404 | §24.1 外部系统交互矩阵 External | §24.1 外部系统交互矩阵 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0405 | §27 系统级成功指标引用 | §27 系统级成功指标引用 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0406 | 🟢 生存线（Survival）—— 低于此线系统进入警告状态，需风控自动收紧；持续低于此线则系统不值得长期运行 | #### 🟢 生存线（Survival）—— 低于此线系统进入警告状态，需风控自动收紧；持续低于此线则系统不值得长期运行 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0407 | 🟡 健康线（Healthy）—— 系统运行良好，可以放心 | 🟡 健康线（Healthy）—— 系统运行良好，可以放心 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0408 | §29.1 多进程隔离与运行时架构（→A9运维架构） | §29.1 多进程隔离与运行时架构（→A9运维架构） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0409 | §29.2 特征存储 (Feature Store) | §29.2 特征存储 (Feature Store) | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0410 | §29.4 时序数据库与分层存储架构（→A3数据架构） | §29.4 时序数据库与分层存储架构（→A3数据架构） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0411 | §29.10 盘中即时反应决策引擎 Engine | §29.10 盘中即时反应决策引擎 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0412 | §29.27 多智能体编排框架选型与MCP协议（→A7 Agent架构） | §29.27 多智能体编排框架选型与MCP协议（→A7 Agent架构） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0413 | §29.35 持续学习抗遗忘框架（v6.0新增） | §29.35 持续学习抗遗忘框架（v6.0新增） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0414 | 裁定15: FinRL-X模块化交易基础设施 | 裁定15: FinRL X模块化交易基础设施 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0415 | 裁定18: 中金Quant 4.0框架对齐 | 裁定18: 中金Quant 4.0框架对齐 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0416 | 裁定22: 持续学习抗遗忘框架（§29.35） Decision 22: Continuous Learning Anti-Forgetting Framework (§29.35) | 裁定22: 持续学习抗遗忘框架（§29.35） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0417 | §29.21 学习系统桥接声明 | §29.21 学习系统桥接声明 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0418 | §30 场外草稿区缺失模块补充 | §30 场外草稿区缺失模块补充 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0419 | §30.1 核心价值链域缺失模块 Core | §30.1 核心价值链域缺失模块 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0420 | §30.1.3 D-PF-CORE 组合核心域（18个模块） | §30.1.3 D PF CORE 组合核心域（18个模块） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0422 | §30.2 增强与扩展域缺失模块 | §30.2 增强与扩展域缺失模块 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0423 | §30.3 核心交易链域缺失模块 Core | §30.3 核心交易链域缺失模块 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0424 | P0 模块明细 | P0 模块明细 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0425 | P1 模块分类汇总（92个） | P1 模块分类汇总（92个） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0426 | P2 模块分类汇总（30个） | P2 模块分类汇总（30个） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0427 | P3 模块分类汇总（3个） | P3 模块分类汇总（3个） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0428 | P1 模块分类汇总（99个） | P1 模块分类汇总（99个） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0429 | P2 模块分类汇总（29个） | P2 模块分类汇总（29个） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0430 | P1 模块分类汇总（85个） | P1 模块分类汇总（85个） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0431 | P2 模块分类汇总（62个） | P2 模块分类汇总（62个） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0432 | P3 模块分类汇总（1个） | P3 模块分类汇总（1个） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0433 | P1 模块分类汇总（7个） | P1 模块分类汇总（7个） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0434 | P2 模块分类汇总（11个） | P2 模块分类汇总（11个） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0435 | P1 模块分类汇总（5个） | P1 模块分类汇总（5个） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0436 | P2 模块分类汇总（7个） | P2 模块分类汇总（7个） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0437 | XS-EXT 模块分类汇总（5个） | XS EXT 模块分类汇总（5个） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0438 | P1 模块分类汇总（14个） | P1 模块分类汇总（14个） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0439 | P2 模块分类汇总（17个） | P2 模块分类汇总（17个） | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0440 | ❌不能建模块门禁条件分布 Cannot Build Module Gate Condition Distribution | ❌不能建模块门禁条件分布 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0441 | §30.4 ML与数据工程域缺失模块 | §30.4 ML与数据工程域缺失模块 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0443 | §30.5 自治与基础设施域缺失模块 Base | §30.5 自治与基础设施域缺失模块 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0444 | Governance Domain §30.6 运维安全治理域缺失模块 | §30.6 运维安全治理域缺失模块 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0464 | L3-L6 决策/仓位/风控/执行/闭环数据 | 决策事件→仓位分配→风控审批→订单执行→成交回报→闭环优化 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0528 | Portfolio Core 组合核心 | / L2→L3 / momentum_buy_signal / risk_budget_alloc / buy_decision / D-PF-CORE / CTR-005 / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0678 | 账户状态物化视图 Account Status View | / 风控状态 / risk:status / Hash / 实时 / <5ms / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0691 | Portfolio Construction Engine 组合构建引擎 | 组合构建引擎均值方差Black-Litterman风险平价层次风险平价 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0692 | Portfolio Risk Decomposer 组合风险分解器 | 组合风险分解因子贡献残差分析边际风险Brinson归因风险预算 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0693 | Multi-Strategy Allocator 多策略分配器 | 多策略分配器策略容量评估策略相关性动态资金分配策略生命周期 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0694 | Portfolio Rebalancer 组合再平衡器 | 组合再平衡器阈值触发时间触发成本感知再平衡增量再平衡 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0695 | Strategy Signal Router 策略信号路由器 | 策略信号路由器信号策略匹配信号分发信号优先级信号冲突处理 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0913 | Automatic Strategy Discovery 自动策略发现 | GP/SR/FactorMAD/R&D-Agent-Quant自动挖掘有效策略 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0919 | LLM Evolutionary Strategy Search LLM进化式策略搜索 | LLM驱动策略空间搜索 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0926 | Multi-Track Fusion 四轨融合器 | 四轨信号融合为统一决策流(应急>人工>自动) | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0927 | Decision Orchestrator 决策编排器 | 5条决策路径统一出口+优先级仲裁+冲突消解+时序编排 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2254 | Auto Down-Weight 自动降权 | 自动降权策略退化时权重降为0 D-REPORTING-02产出策略退化检测数据 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2312 | Portfolio State 组合状态检查点 | 组合状态每日收盘后Parquet全量组合回滚粒度 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2567 | C-034 Main Force Behavior Inference 主力行为推演 | 主力行为推演已有出货派发概率输出 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2568 | C-039 Cross Market Transmission 跨市场传导 | 跨市场传导GNN关系建模 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2569 | C-045 Crowd Degree Detection 拥挤度检测 | 拥挤度检测+市场状态仓位上限 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2570 | C-006 Strategy Type Catalog 策略类型目录 | 6大类策略目录+策略去重 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2595 | Capability Positioning Book 能力定位书 | 所有架构图的元初输入不属于9+1架构图 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3273 | StrategyRegistry 策略注册表 | D-PF-CORE就绪StrategyRegistry | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4230 | Strategy Portfolio 策略组合 | / strategy_portfolio.py / governance/ / 策略组合 / ❌ 属于D-PF-CORE——策略组合是组合核心域 / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4946 | Portfolio Optimization Engine 组合优化引擎 | 权重优化+风险预算+策略冷启动+分布感知仓位+Copula-GARCH+RL增强 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4947 | Multi-Strategy Resonance Fusion 多策略共振融合层 | 投票共振全同向→强/多数→中/分歧→弱 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4948 | Factor Direct Layer 因子直通层 | 策略未覆盖/冲突时因子加权融合直接产生决策 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4949 | Sell Decision Engine 卖出决策引擎 | 卖出信号层+卖出策略工厂+卖出信号融合仲裁+卖出闭环优化 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4950 | MTF Four-Track Fusion 四轨融合器 | 轨道1+2同向→强共振/单轨→中等/冲突→L6审查 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4951 | Event Sourcing 事件溯源 | EventSourcing全事件链可回溯 | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5066 | HRP/Black-Litterman Portfolio Optimization HRP/Black-Litterman组合优化 | /  2  / 🟧重要 / HRP/Black-Litterman组合优化备选 / ⚠️简短提及 / López de Prado (2016) Building Diversified Portfolios; Black-Litterma | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5253 | Liquidity Estimator 流动性估算器 | / 合并→PC-08 / Liquidity Estimator / 流动性是容量约束的子功能 / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5254 | Benchmark Manager 基准管理器 | / 合并→PC-10 / Benchmark Manager / 基准管理是绩效归因的子功能 / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5255 | Carbon Footprint 碳足迹 | / 移除 / Carbon Footprint / P2远期ESG / | D_PF_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |

## 按四问卡点分组（为什么没开发）

> 四问过滤：q1已实现 / q2需求驱动 / q3域活着 / q4 AI替代。任一问「否」即不进 depgraph 设计态，登记在候选库。

### 待评估（137 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-HARVEST-0014 | Strategy Factory 策略工厂 | C 006：策略工厂 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0015 | Multi-Scenario Response & Contingency 多情景对策与预案 | C 005：多情景对策与预案 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0018 | Strategy Capacity Modeling 策略容量建模 | C 042：策略容量建模 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0024 | Factor/Strategy Crowding Deep Detection 因子/策略拥挤度深度检测 | C 045：因子/策略拥挤度深度检测 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0030 | Explainability 决策可解释性与溯源 | C 030：决策可解释性与溯源（P0） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0047 | 多账户多策略 Strategy | C 018：多账户多策略 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0092 | Strategy Engine策略引擎 | / PC-01 / Strategy Engine策略引擎 / ✅ 能建 / 📋 项目内有蓝图编号MOD-L05-001部分建设 / 策略注册+选择+信号生成+生命周期管理 / | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0093 | Portfolio Optimizer组合优化器 | / PC-02 / Portfolio Optimizer组合优化器 / ✅ 能建 / / 均值方差+风险平价+Black-Litterman+CPPI+TIPP。与§29.9 RL组合优化互补: PC-02提供传统优化基线, §29.9 | D_PF_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0095 | Constraint Solver约束求解器 | / PC-04 / Constraint Solver约束求解器 / ✅ 能建 / / 权重边界+行业集中度+流动性+ESG+监管约束 / | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0096 | Risk Parity Engine风险平价引擎 | / PC-05 / Risk Parity Engine风险平价引擎 / ✅ 能建 / / 等风险贡献+层次风险平价+因子风险平价 / | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0097 | Multi-Objective Optimizer多目标优化器 | / PC-06 / Multi-Objective Optimizer多目标优化器 / ❌ 不能建 / / 门禁: ①组合优化器PC-02稳定运行 ②开发带宽释放 / | D_PF_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0098 | Tax Loss Harvester税损收割器 | / PC-07 / Tax Loss Harvester税损收割器 / ❌ 不能建 / / 门禁: Long-Only T+1无做空对冲，税损收割空间有限 / | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0099 | Portfolio Drift Monitor组合漂移监控器 | / PC-08 / Portfolio Drift Monitor组合漂移监控器 / ✅ 能建 / / 权重/因子暴露/风险/风格漂移检测+CUSUM / | D_PF_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0100 | Cash Flow Manager资金流管理器 | / PC-09 / Cash Flow Manager资金流管理器 / ✅ 能建 / / 申购赎回+分红再投资+现金拖累优化 / | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0101 | Rebalance Cost Analyzer再平衡成本分析器 | / PC-10 / Rebalance Cost Analyzer再平衡成本分析器 / ✅ 能建 / / 显性(佣金/印花税)+隐性(冲击/价差)+税收+机会成本 / | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0102 | Liquidity Estimator流动性估计器 | / PC-11 / Liquidity Estimator流动性估计器 / ✅ 能建 / / 市场深度+成交量预测+流动性风险评分 / | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0103 | Portfolio Stress Tester组合压力测试器 | / PC-12 / Portfolio Stress Tester组合压力测试器 / ✅ 能建 / / 历史+假设+反向压力测试+敏感性分析 / | D_PF_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0104 | Sector Exposure Manager行业敞口管理器 | / PC-13 / Sector Exposure Manager行业敞口管理器 / ✅ 能建 / / GICS/申万分类+敞口计算+集中度监控 / | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0105 | Factor Exposure Manager因子敞口管理器 | / PC-14 / Factor Exposure Manager因子敞口管理器 / ✅ 能建 / / 风格/行业/国家因子敞口+Barra风险模型 / | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0106 | Portfolio Benchmark Manager组合基准管理器 | / PC-15 / Portfolio Benchmark Manager组合基准管理器 / ✅ 能建 / / 基准选择+跟踪误差+信息比率+主动份额 / | D_PF_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0107 | Carbon Footprint Calculator碳足迹计算器 | / PC-16 / Carbon Footprint Calculator碳足迹计算器 / ❌ 不能建 / / 门禁: ①ESG数据源接入 ②50万AUM规模无需碳报告 / | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0108 | Strategy Capacity Estimator策略容量估计器 | / PC-17 / Strategy Capacity Estimator策略容量估计器 / ✅ 能建 / / AUM容量上限+利用率+流动性约束容量 / | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0109 | Performance Attribution Engine绩效归因引擎 | / PC-18 / Performance Attribution Engine绩效归因引擎 / ✅ 能建 / 📋 项目有蓝图编号MOD-L07-001但是没建设 / Brinson归因+因子归因+选股/择时分解 / | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0358 | §2.1 多源数据接入与分层存储架构 Data Ingestion Storage | §2.1 多源数据接入与分层存储架构 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0359 | 模块3 缺口回补概率模型（Gap Fill Probability Model） | 模块3 缺口回补概率模型（Gap Fill Probability Model） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0360 | 模块4 逼空行情检测模型（Short Squeeze Detection Model） | 模块4 逼空行情检测模型（Short Squeeze Detection Model） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0361 | 模块7 多指标背离检测模型（Multi-Indicator Divergence Detection Model） | ### 模块7 多指标背离检测模型（Multi-Indicator Divergence Detection Model） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0362 | 模块8 板块资金流再配置模型（Sector Flow Reallocation Model） | 模块8 板块资金流再配置模型（Sector Flow Reallocation Model） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0363 | 模块10 动量领导因子与涨停板生态模型（Momentum Leadership & Limit-Up Factor） | ### 模块10 动量领导因子与涨停板生态模型（Momentum Leadership & Limit-Up Factor） | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0364 | 模块11 动量层级与板块持续性模型（Momentum Hierarchy & Persistence Model） | ### 模块11 动量层级与板块持续性模型（Momentum Hierarchy & Persistence Model） | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0365 | 模块12 板块间资金流迁移检测模型（Inter-Sector Flow Migration Detection） | ### 模块12 板块间资金流迁移检测模型（Inter-Sector Flow Migration Detection） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0366 | 模块15 假突破与诱多检测模型（False Breakout & Bull Trap Detection Model） | ### 模块15 假突破与诱多检测模型（False Breakout & Bull Trap Detection Model） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0367 | 模块16 情绪-价格背离指数模型（Sentiment-Price Divergence Index） | 模块16 情绪 价格背离指数模型（Sentiment Price Divergence Index） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0369 | 19.2 Ensemble-HMM增强框架 | 19.2 Ensemble HMM增强框架 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0370 | 模块26 3秒级逆势资金流识别模块 Module 26 3-Second Contrarian Capital Flow Identification | 模块26 3秒级逆势资金流识别模块 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0371 | 26.5 逆势资金流与已有模块的联动 26.5 Contrarian Capital Flow Linkage with Existing Modules | 26.5 逆势资金流与已有模块的联动 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0372 | 模块31 协同交易行为检测模型（Coordinated Trading Detection Model） | ### 模块31 协同交易行为检测模型（Coordinated Trading Detection Model） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0373 | 31.3 高级协同检测（基于ESMA MABUM框架） | 31.3 高级协同检测（基于ESMA MABUM框架） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0374 | 模块34 异质参与者互动模型（Heterogeneous Agent Interaction Model） | ### 模块34 异质参与者互动模型（Heterogeneous Agent Interaction Model） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0376 | 模块51 波动率压缩与突破模型（Volatility Compression & Breakout Model） | ### 模块51 波动率压缩与突破模型（Volatility Compression & Breakout Model） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0377 | 模块52 汇总：缺失模块与建议归属层映射（更新版） Module 52 Summary: Missing Modules and Suggested Layer Mapping (Updated) | 模块52 汇总：缺失模块与建议归属层映射（更新版） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0378 | 模块58 附录：已有架构覆盖的功能（不重复列出） Module 58 Appendix: Functions Covered by Existing Architecture | 模块58 附录：已有架构覆盖的功能（不重复列出） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0379 | 模块58 附录二：已剔除模块说明（架构文档完全覆盖） Module 58 Appendix 2: Removed Modules Description | 模块58 附录二：已剔除模块说明（架构文档完全覆盖） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0380 | Signal Factory §4.1 信号工厂九大子阶段 | §4.1 信号工厂九大子阶段 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0381 | §4.4 信号聚合器架构 Signal Aggregator | §4.4 信号聚合器架构 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0382 | 模块29 次日上涨概率统一门槛模块 Module 29 Next-Day Rise Probability Unified Threshold | 模块29 次日上涨概率统一门槛模块 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0383 | 模块27 主力假动作与筹码派发识别模块 Module 27 Main Force Fake Action and Chip Distribution Identification | 模块27 主力假动作与筹码派发识别模块 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0384 | 模块23 量能体制自适应策略模型（Volume Regime Adaptive Strategy Model） | ### 模块23 量能体制自适应策略模型（Volume Regime Adaptive Strategy Model） | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0385 | 模块32 市场风格体制识别模型（Market Style Regime Identification Model） | ### 模块32 市场风格体制识别模型（Market Style Regime Identification Model） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0386 | 模块28 利好落地变利空（预期透支）模块 Module 28 Good News Becomes Bad News (Expectation Overdraw) | 模块28 利好落地变利空（预期透支）模块 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0387 | 28.5 与已有模块的联动 28.5 Linkage with Existing Modules | 28.5 与已有模块的联动 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0388 | §8.1 策略工厂(C-006)与信号工厂(C-028)的协作 | ### §8.1 策略工厂(C-006)与信号工厂(C-028)的协作 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0389 | §8.5 组合优化引擎 Portfolio Engine | §8.5 组合优化引擎 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0390 | 模块24 核心-卫星仓位管理模型（Core-Satellite Position Management Model） | ### 模块24 核心-卫星仓位管理模型（Core-Satellite Position Management Model） | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0391 | Decision Orchestrator 决策编排器——缺失功能模块 | 决策编排器——缺失功能模块 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0392 | 模块57 多因子叠加择时模型（Multi-Factor Overlay Timing Model） | 模块57 多因子叠加择时模型（Multi Factor Overlay Timing Model） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0393 | §12.4 C-033 过拟合系统性防护 | §12.4 C 033 过拟合系统性防护 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0394 | §20.8 方法论约束八：训练-服务一致性(Feature Store) | §20.8 方法论约束八：训练 服务一致性(Feature Store) | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0395 | 决策四：模型/策略漂移检测框架 Strategy Model | 决策四：模型/策略漂移检测框架 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0396 | C-006：策略工厂 | C 006：策略工厂 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0397 | C-047：仓位管理唯一裁决中心 | C 047：仓位管理唯一裁决中心 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0398 | C-016：知识图谱引擎 | C 016：知识图谱引擎 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0399 | C-027：因子工厂（P0） | C 027：因子工厂（P0） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0400 | C-028：信号工厂（P0） | C 028：信号工厂（P0） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0401 | C-033：过拟合系统性防护 | C 033：过拟合系统性防护 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0402 | C-040：系统性压力测试 | C 040：系统性压力测试 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0403 | §24 外部系统交互引用 External | §24 外部系统交互引用 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0404 | §24.1 外部系统交互矩阵 External | §24.1 外部系统交互矩阵 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0405 | §27 系统级成功指标引用 | §27 系统级成功指标引用 | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0406 | 🟢 生存线（Survival）—— 低于此线系统进入警告状态，需风控自动收紧；持续低于此线则系统不值得长期运行 | #### 🟢 生存线（Survival）—— 低于此线系统进入警告状态，需风控自动收紧；持续低于此线则系统不值得长期运行 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0407 | 🟡 健康线（Healthy）—— 系统运行良好，可以放心 | 🟡 健康线（Healthy）—— 系统运行良好，可以放心 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0408 | §29.1 多进程隔离与运行时架构（→A9运维架构） | §29.1 多进程隔离与运行时架构（→A9运维架构） | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0409 | §29.2 特征存储 (Feature Store) | §29.2 特征存储 (Feature Store) | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0410 | §29.4 时序数据库与分层存储架构（→A3数据架构） | §29.4 时序数据库与分层存储架构（→A3数据架构） | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0411 | §29.10 盘中即时反应决策引擎 Engine | §29.10 盘中即时反应决策引擎 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0412 | §29.27 多智能体编排框架选型与MCP协议（→A7 Agent架构） | §29.27 多智能体编排框架选型与MCP协议（→A7 Agent架构） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0413 | §29.35 持续学习抗遗忘框架（v6.0新增） | §29.35 持续学习抗遗忘框架（v6.0新增） | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0414 | 裁定15: FinRL-X模块化交易基础设施 | 裁定15: FinRL X模块化交易基础设施 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0415 | 裁定18: 中金Quant 4.0框架对齐 | 裁定18: 中金Quant 4.0框架对齐 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0416 | 裁定22: 持续学习抗遗忘框架（§29.35） Decision 22: Continuous Learning Anti-Forgetting Framework (§29.35) | 裁定22: 持续学习抗遗忘框架（§29.35） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0417 | §29.21 学习系统桥接声明 | §29.21 学习系统桥接声明 | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0418 | §30 场外草稿区缺失模块补充 | §30 场外草稿区缺失模块补充 | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0419 | §30.1 核心价值链域缺失模块 Core | §30.1 核心价值链域缺失模块 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0420 | §30.1.3 D-PF-CORE 组合核心域（18个模块） | §30.1.3 D PF CORE 组合核心域（18个模块） | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0422 | §30.2 增强与扩展域缺失模块 | §30.2 增强与扩展域缺失模块 | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0423 | §30.3 核心交易链域缺失模块 Core | §30.3 核心交易链域缺失模块 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0424 | P0 模块明细 | P0 模块明细 | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0425 | P1 模块分类汇总（92个） | P1 模块分类汇总（92个） | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0426 | P2 模块分类汇总（30个） | P2 模块分类汇总（30个） | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0427 | P3 模块分类汇总（3个） | P3 模块分类汇总（3个） | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0428 | P1 模块分类汇总（99个） | P1 模块分类汇总（99个） | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0429 | P2 模块分类汇总（29个） | P2 模块分类汇总（29个） | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0430 | P1 模块分类汇总（85个） | P1 模块分类汇总（85个） | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0431 | P2 模块分类汇总（62个） | P2 模块分类汇总（62个） | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0432 | P3 模块分类汇总（1个） | P3 模块分类汇总（1个） | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0433 | P1 模块分类汇总（7个） | P1 模块分类汇总（7个） | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0434 | P2 模块分类汇总（11个） | P2 模块分类汇总（11个） | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0435 | P1 模块分类汇总（5个） | P1 模块分类汇总（5个） | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0436 | P2 模块分类汇总（7个） | P2 模块分类汇总（7个） | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0437 | XS-EXT 模块分类汇总（5个） | XS EXT 模块分类汇总（5个） | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0438 | P1 模块分类汇总（14个） | P1 模块分类汇总（14个） | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0439 | P2 模块分类汇总（17个） | P2 模块分类汇总（17个） | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0440 | ❌不能建模块门禁条件分布 Cannot Build Module Gate Condition Distribution | ❌不能建模块门禁条件分布 | D_PF_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0441 | §30.4 ML与数据工程域缺失模块 | §30.4 ML与数据工程域缺失模块 | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0443 | §30.5 自治与基础设施域缺失模块 Base | §30.5 自治与基础设施域缺失模块 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0444 | Governance Domain §30.6 运维安全治理域缺失模块 | §30.6 运维安全治理域缺失模块 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0464 | L3-L6 决策/仓位/风控/执行/闭环数据 | 决策事件→仓位分配→风控审批→订单执行→成交回报→闭环优化 | D_PF_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0528 | Portfolio Core 组合核心 | / L2→L3 / momentum_buy_signal / risk_budget_alloc / buy_decision / D-PF-CORE / CTR-005 / | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0678 | 账户状态物化视图 Account Status View | / 风控状态 / risk:status / Hash / 实时 / <5ms / | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0691 | Portfolio Construction Engine 组合构建引擎 | 组合构建引擎均值方差Black-Litterman风险平价层次风险平价 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0692 | Portfolio Risk Decomposer 组合风险分解器 | 组合风险分解因子贡献残差分析边际风险Brinson归因风险预算 | D_PF_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0693 | Multi-Strategy Allocator 多策略分配器 | 多策略分配器策略容量评估策略相关性动态资金分配策略生命周期 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0694 | Portfolio Rebalancer 组合再平衡器 | 组合再平衡器阈值触发时间触发成本感知再平衡增量再平衡 | D_PF_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0695 | Strategy Signal Router 策略信号路由器 | 策略信号路由器信号策略匹配信号分发信号优先级信号冲突处理 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0913 | Automatic Strategy Discovery 自动策略发现 | GP/SR/FactorMAD/R&D-Agent-Quant自动挖掘有效策略 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0919 | LLM Evolutionary Strategy Search LLM进化式策略搜索 | LLM驱动策略空间搜索 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0926 | Multi-Track Fusion 四轨融合器 | 四轨信号融合为统一决策流(应急>人工>自动) | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0927 | Decision Orchestrator 决策编排器 | 5条决策路径统一出口+优先级仲裁+冲突消解+时序编排 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2254 | Auto Down-Weight 自动降权 | 自动降权策略退化时权重降为0 D-REPORTING-02产出策略退化检测数据 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2312 | Portfolio State 组合状态检查点 | 组合状态每日收盘后Parquet全量组合回滚粒度 | D_PF_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-2567 | C-034 Main Force Behavior Inference 主力行为推演 | 主力行为推演已有出货派发概率输出 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2568 | C-039 Cross Market Transmission 跨市场传导 | 跨市场传导GNN关系建模 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2569 | C-045 Crowd Degree Detection 拥挤度检测 | 拥挤度检测+市场状态仓位上限 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2570 | C-006 Strategy Type Catalog 策略类型目录 | 6大类策略目录+策略去重 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2595 | Capability Positioning Book 能力定位书 | 所有架构图的元初输入不属于9+1架构图 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3273 | StrategyRegistry 策略注册表 | D-PF-CORE就绪StrategyRegistry | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4230 | Strategy Portfolio 策略组合 | / strategy_portfolio.py / governance/ / 策略组合 / ❌ 属于D-PF-CORE——策略组合是组合核心域 / | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4946 | Portfolio Optimization Engine 组合优化引擎 | 权重优化+风险预算+策略冷启动+分布感知仓位+Copula-GARCH+RL增强 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4947 | Multi-Strategy Resonance Fusion 多策略共振融合层 | 投票共振全同向→强/多数→中/分歧→弱 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4948 | Factor Direct Layer 因子直通层 | 策略未覆盖/冲突时因子加权融合直接产生决策 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-4949 | Sell Decision Engine 卖出决策引擎 | 卖出信号层+卖出策略工厂+卖出信号融合仲裁+卖出闭环优化 | D_PF_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4950 | MTF Four-Track Fusion 四轨融合器 | 轨道1+2同向→强共振/单轨→中等/冲突→L6审查 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-4951 | Event Sourcing 事件溯源 | EventSourcing全事件链可回溯 | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-5066 | HRP/Black-Litterman Portfolio Optimization HRP/Black-Litterman组合优化 | /  2  / 🟧重要 / HRP/Black-Litterman组合优化备选 / ⚠️简短提及 / López de Prado (2016) Building Diversified Portfolios; Black-Litterma | D_PF_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-5253 | Liquidity Estimator 流动性估算器 | / 合并→PC-08 / Liquidity Estimator / 流动性是容量约束的子功能 / | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-5254 | Benchmark Manager 基准管理器 | / 合并→PC-10 / Benchmark Manager / 基准管理是绩效归因的子功能 / | D_PF_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-5255 | Carbon Footprint 碳足迹 | / 移除 / Carbon Footprint / P2远期ESG / | D_PF_CORE | harvest待评估（likely_new） |  |

## 复查时间表

> 按 next_review_date 升序。复查时重新过四问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-11-30 | quarterly | CAND-HARVEST-0014 | Strategy Factory 策略工厂 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0015 | Multi-Scenario Response & Contingency 多情景对策与预案 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0018 | Strategy Capacity Modeling 策略容量建模 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0024 | Factor/Strategy Crowding Deep Detection 因子/策略拥挤度深度检测 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0030 | Explainability 决策可解释性与溯源 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0047 | 多账户多策略 Strategy | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0092 | Strategy Engine策略引擎 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0093 | Portfolio Optimizer组合优化器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0095 | Constraint Solver约束求解器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0096 | Risk Parity Engine风险平价引擎 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0097 | Multi-Objective Optimizer多目标优化器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0098 | Tax Loss Harvester税损收割器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0099 | Portfolio Drift Monitor组合漂移监控器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0100 | Cash Flow Manager资金流管理器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0101 | Rebalance Cost Analyzer再平衡成本分析器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0102 | Liquidity Estimator流动性估计器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0103 | Portfolio Stress Tester组合压力测试器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0104 | Sector Exposure Manager行业敞口管理器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0105 | Factor Exposure Manager因子敞口管理器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0106 | Portfolio Benchmark Manager组合基准管理器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0107 | Carbon Footprint Calculator碳足迹计算器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0108 | Strategy Capacity Estimator策略容量估计器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0109 | Performance Attribution Engine绩效归因引擎 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0358 | §2.1 多源数据接入与分层存储架构 Data Ingestion Storage | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0359 | 模块3 缺口回补概率模型（Gap Fill Probability Model） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0360 | 模块4 逼空行情检测模型（Short Squeeze Detection Model） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0361 | 模块7 多指标背离检测模型（Multi-Indicator Divergence Detection Model） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0362 | 模块8 板块资金流再配置模型（Sector Flow Reallocation Model） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0363 | 模块10 动量领导因子与涨停板生态模型（Momentum Leadership & Limit-Up Factor） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0364 | 模块11 动量层级与板块持续性模型（Momentum Hierarchy & Persistence Model） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0365 | 模块12 板块间资金流迁移检测模型（Inter-Sector Flow Migration Detection） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0366 | 模块15 假突破与诱多检测模型（False Breakout & Bull Trap Detection Model） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0367 | 模块16 情绪-价格背离指数模型（Sentiment-Price Divergence Index） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0369 | 19.2 Ensemble-HMM增强框架 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0370 | 模块26 3秒级逆势资金流识别模块 Module 26 3-Second Contrarian Capital Flow Identification | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0371 | 26.5 逆势资金流与已有模块的联动 26.5 Contrarian Capital Flow Linkage with Existing Modules | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0372 | 模块31 协同交易行为检测模型（Coordinated Trading Detection Model） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0373 | 31.3 高级协同检测（基于ESMA MABUM框架） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0374 | 模块34 异质参与者互动模型（Heterogeneous Agent Interaction Model） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0376 | 模块51 波动率压缩与突破模型（Volatility Compression & Breakout Model） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0377 | 模块52 汇总：缺失模块与建议归属层映射（更新版） Module 52 Summary: Missing Modules and Suggested Layer Mapping (Updated) | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0378 | 模块58 附录：已有架构覆盖的功能（不重复列出） Module 58 Appendix: Functions Covered by Existing Architecture | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0379 | 模块58 附录二：已剔除模块说明（架构文档完全覆盖） Module 58 Appendix 2: Removed Modules Description | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0380 | Signal Factory §4.1 信号工厂九大子阶段 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0381 | §4.4 信号聚合器架构 Signal Aggregator | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0382 | 模块29 次日上涨概率统一门槛模块 Module 29 Next-Day Rise Probability Unified Threshold | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0383 | 模块27 主力假动作与筹码派发识别模块 Module 27 Main Force Fake Action and Chip Distribution Identification | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0384 | 模块23 量能体制自适应策略模型（Volume Regime Adaptive Strategy Model） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0385 | 模块32 市场风格体制识别模型（Market Style Regime Identification Model） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0386 | 模块28 利好落地变利空（预期透支）模块 Module 28 Good News Becomes Bad News (Expectation Overdraw) | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0387 | 28.5 与已有模块的联动 28.5 Linkage with Existing Modules | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0388 | §8.1 策略工厂(C-006)与信号工厂(C-028)的协作 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0389 | §8.5 组合优化引擎 Portfolio Engine | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0390 | 模块24 核心-卫星仓位管理模型（Core-Satellite Position Management Model） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0391 | Decision Orchestrator 决策编排器——缺失功能模块 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0392 | 模块57 多因子叠加择时模型（Multi-Factor Overlay Timing Model） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0393 | §12.4 C-033 过拟合系统性防护 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0394 | §20.8 方法论约束八：训练-服务一致性(Feature Store) | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0395 | 决策四：模型/策略漂移检测框架 Strategy Model | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0396 | C-006：策略工厂 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0397 | C-047：仓位管理唯一裁决中心 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0398 | C-016：知识图谱引擎 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0399 | C-027：因子工厂（P0） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0400 | C-028：信号工厂（P0） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0401 | C-033：过拟合系统性防护 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0402 | C-040：系统性压力测试 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0403 | §24 外部系统交互引用 External | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0404 | §24.1 外部系统交互矩阵 External | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0405 | §27 系统级成功指标引用 | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0406 | 🟢 生存线（Survival）—— 低于此线系统进入警告状态，需风控自动收紧；持续低于此线则系统不值得长期运行 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0407 | 🟡 健康线（Healthy）—— 系统运行良好，可以放心 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0408 | §29.1 多进程隔离与运行时架构（→A9运维架构） | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0409 | §29.2 特征存储 (Feature Store) | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0410 | §29.4 时序数据库与分层存储架构（→A3数据架构） | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0411 | §29.10 盘中即时反应决策引擎 Engine | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0412 | §29.27 多智能体编排框架选型与MCP协议（→A7 Agent架构） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0413 | §29.35 持续学习抗遗忘框架（v6.0新增） | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0414 | 裁定15: FinRL-X模块化交易基础设施 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0415 | 裁定18: 中金Quant 4.0框架对齐 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0416 | 裁定22: 持续学习抗遗忘框架（§29.35） Decision 22: Continuous Learning Anti-Forgetting Framework (§29.35) | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0417 | §29.21 学习系统桥接声明 | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0418 | §30 场外草稿区缺失模块补充 | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0419 | §30.1 核心价值链域缺失模块 Core | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0420 | §30.1.3 D-PF-CORE 组合核心域（18个模块） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0422 | §30.2 增强与扩展域缺失模块 | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0423 | §30.3 核心交易链域缺失模块 Core | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0424 | P0 模块明细 | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0425 | P1 模块分类汇总（92个） | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0426 | P2 模块分类汇总（30个） | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0427 | P3 模块分类汇总（3个） | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0428 | P1 模块分类汇总（99个） | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0429 | P2 模块分类汇总（29个） | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0430 | P1 模块分类汇总（85个） | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0431 | P2 模块分类汇总（62个） | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0432 | P3 模块分类汇总（1个） | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0433 | P1 模块分类汇总（7个） | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0434 | P2 模块分类汇总（11个） | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0435 | P1 模块分类汇总（5个） | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0436 | P2 模块分类汇总（7个） | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0437 | XS-EXT 模块分类汇总（5个） | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0438 | P1 模块分类汇总（14个） | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0439 | P2 模块分类汇总（17个） | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0440 | ❌不能建模块门禁条件分布 Cannot Build Module Gate Condition Distribution | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0441 | §30.4 ML与数据工程域缺失模块 | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0443 | §30.5 自治与基础设施域缺失模块 Base | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0444 | Governance Domain §30.6 运维安全治理域缺失模块 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0464 | L3-L6 决策/仓位/风控/执行/闭环数据 | D_PF_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0528 | Portfolio Core 组合核心 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0678 | 账户状态物化视图 Account Status View | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0691 | Portfolio Construction Engine 组合构建引擎 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0692 | Portfolio Risk Decomposer 组合风险分解器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0693 | Multi-Strategy Allocator 多策略分配器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0694 | Portfolio Rebalancer 组合再平衡器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0695 | Strategy Signal Router 策略信号路由器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0913 | Automatic Strategy Discovery 自动策略发现 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0919 | LLM Evolutionary Strategy Search LLM进化式策略搜索 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0926 | Multi-Track Fusion 四轨融合器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0927 | Decision Orchestrator 决策编排器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2254 | Auto Down-Weight 自动降权 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2312 | Portfolio State 组合状态检查点 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-2567 | C-034 Main Force Behavior Inference 主力行为推演 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2568 | C-039 Cross Market Transmission 跨市场传导 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2569 | C-045 Crowd Degree Detection 拥挤度检测 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2570 | C-006 Strategy Type Catalog 策略类型目录 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2595 | Capability Positioning Book 能力定位书 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3273 | StrategyRegistry 策略注册表 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4230 | Strategy Portfolio 策略组合 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4946 | Portfolio Optimization Engine 组合优化引擎 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4947 | Multi-Strategy Resonance Fusion 多策略共振融合层 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4948 | Factor Direct Layer 因子直通层 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4949 | Sell Decision Engine 卖出决策引擎 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4950 | MTF Four-Track Fusion 四轨融合器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4951 | Event Sourcing 事件溯源 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5066 | HRP/Black-Litterman Portfolio Optimization HRP/Black-Litterman组合优化 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-5253 | Liquidity Estimator 流动性估算器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5254 | Benchmark Manager 基准管理器 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5255 | Carbon Footprint 碳足迹 | D_PF_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
