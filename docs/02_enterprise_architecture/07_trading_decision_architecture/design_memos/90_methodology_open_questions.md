---
ttl: permanent
doc_type: architecture_view
title: 方法论约束遗留提案
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "2.0.0"
date: 2026-08-12
topic: methodology_open_questions
scope: 07_trading_decision_architecture
---

# 方法论约束遗留提案

> **状态**：21 项遗留提案。#1-#11 源自原《能力定位书》§3 约束一~十三；#12-#21 源自系统宪章多轮精简移出项（成功指标/基准/PIT/资产分级/行为边界/资产覆盖/大额下单/工程细节/做T方法论）。
>
> **v0.2.0 审查结论（2026-08-10）**：逐项与项目现状（30_multi_strategy v1.9.0 / 10_regime_detector_spec v1.8.0 / 11_regime_backtest §0.5 / 已施工代码）对齐，并参考 2026 年量化方法论最新实践。结果：
> - ✅ **已裁定 4 项**（#3 组合构建 / #4 风险模型 / #6 回测门禁 / #11 仓位管理）——30_multi_strategy_concurrency 已定稿替代方案，本稿保留原始内容作历史记录，标注裁定结论与映射关系
> - ⚠️ **纠正 1 项**（#7 T+1次日预测）——原稿"8态已被12态替代"不准确：8态(BM-SEL-04)是独立下游消费者(次日走势预测，未建)，与 regime 检测(市场状态)是不同概念；但 8态→直接决策映射确实过时(Model A 策略自主决策)
> - 🔧 **更正引用 1 项**（#9 数据分层 Layer2 "8态预测"→regime 检测）
> - 📝 **保留待讨论 15 项**（#1/#2/#5/#8/#12-#21）——真正未决的方法论问题
>
> **v0.3.0 二轮审查（2026-08-10）**：补 6 项施工算法缺口——#2 SHAP 因子评估 / #5 平方根冲击律 / #8 Amihud+LVaR / #19 执行算法四层谱系 / #20 DTW 策略相似度 / #21 做 T 正反 T 方法论
>
> **v0.4.0 三轮审查（2026-08-10）**：补 6 项施工算法缺口——#1 管线谱系+四族分类 / #13 Barra 归因+Smart Beta 基准 / #14 PIT 财报双日期+重述泄漏 / #15 A 股流通市值 6 级分层 / #17 Policy-as-Code(OPA/Rego) / #18 Instrument Master 最小字段集。**12 项待讨论项已补 2026 算法**（#1/#2/#5/#8/#13/#14/#15/#17/#18/#19/#20/#21），剩余 #12/#16 成功指标阈值待回测验证、#10 密度预测见 91 号文档
>
> **v0.5.0 四轮审查（2026-08-10）**：补 3 项——#16 成功指标补五层评估体系+阈值共识 / #20 B-010 补策略退役决策树（Edge Decay 三分法+5 预警信号） / #2 补 GP 自动因子挖掘（发现维度）。**15 项待讨论项全部已补 2026 算法或明确裁定**（#1/#2/#5/#8/#12/#13/#14/#15/#16/#17/#18/#19/#20/#21 + #10 见 91 号），仅剩阈值校准待回测数据。Doc 91 补 Conformal Prediction 为 Phase 0（比 LSTM+GMM 更简更稳健）
>
> **v0.6.0 五轮审查（2026-08-10）**：补 4 项施工算法缺口+更优算法——#1 补 2026-08 打板环境剧变实证（溢价 4.2%→1.7%/炸板率 40%→68%/程序化新规/打板情绪量化算法）；#7 补 A 股预测天花板 52-53%实证（firsh.me 9 版迭代，突破口在信息源非架构，8态暂缓建议）；#20 补 Alpha Decay 数学模型（指数衰减 α(t)=α₀·e^(-λt)+成本地板+复杂度-过拟合差距+容量 4/9 规则）。Doc 91 补 RWC（Regime-Weighted Conformal, Oxford 2026-08-03）为 Phase 0 最优变体——复用项目 regime 检测器，比 TCP 架构原生匹配
>
> **v0.7.0 六轮审查（2026-08-10）**：补 4 项施工算法缺口+选项外更优算法——#1 补 akshare 连板接力筛选算法（封成比≥5%/流通市值≤250 亿开源代码）+6 维度涨停规律（4 分时硬性指标）+8 月游资转型实证（电子板块净流出 187 亿/12 算力龙头减持 22%）；#2 补 PPO 自适应 alpha 加权（arxiv 2509.01393 U Hyogo 2026）为因子动态加权远期选项（抗 alpha decay）；#11 补 Kelly 分数实证（g(f*)=SR²/2+Half-Kelly 75%增长+1/4 Kelly 95%增长+Lisa Chang 案例+drawdown 恢复数学+动态分数 Kelly 建议）；#20 补退役决策树第 4 选项 Layering（pomegra.io 2026 叠加新信号）。Doc 91 补 Information-Entropic DL+GP+Kelly+CVaR（Entropy 2026,28,485 A 股 4 股实证）为 Phase 1.5 统一框架+RWC 关键告诫（压力期残余 2.29% exceedance）+DeepONet 尾部分位数
>
> **v0.8.0 七轮审查（2026-08-10）**：补 5 项施工算法缺口+选项外更优算法——#1 补 4 个开源打板工具生态（short-term-stock-picker 评分系统/A-Share-Sector-Alpha-Hunter 蓄势弹簧/stk_explore 双数据源+历史封板率）；#2 补 PeerJ cs-3630 三层框架（LLM+多智能体+PPO，OOS 年化 53.87%/Sharpe 1.702）为 PPO 系统化升级路径+CGX 多智能体 LLM 对抗辩论（MDPI Electronics 15:3453 2026-08-04，Sharpe 1.90/MaxDD -85%）为 28 号情绪周期 LLM 化远期选项；#3 补 HRP（Hierarchical Risk Parity, López de Prado）为 naive risk parity 进阶选项；#11 补 Conformal Kelly（arxiv 2608.01494 2026-08-02，"慢而稳 conformal 胜过快而自适应"反直觉发现+drawdown dial 风控）+Bayesian Kelly/RMSE Kelly 轻量级校准（Phase 0.5 介于 RWC 与 Info-Entropic DL+GP 之间）；#20 补退役决策树第 5 选项 EvoQuant（arxiv 2607.12455 HKUST 2026-07 LLM 自演化重优化，A 股 4 策略 Sharpe -0.298→0.538）+LangGraph+Harness CI/CD 工程实现+90 天滚动相关性剔除规则（youcanbuildthings 2026-05）
>
> **v0.9.0 八轮审查（2026-08-10）**：补 2 项施工算法缺口+选项外更优算法——#7 补 **Wasserstein HMM**（arxiv 2603.04441 Columbia 2026-02，预测性 model-order selection+ Wasserstein template tracking 解决 regime 标签漂移，Sharpe 2.18 vs SPX 1.18/MaxDD -5.43%），**直接对应项目 12 号 A2 FAIL（OOS/IS=0.340 标签对齐失败）**——是项目 regime 检测器 Phase 2 修复的候选方案；#2 补 **F²Agent**（arxiv 2608.05668 NUS 2026-08-06 极新，多模态多智能体 LLM+modality-aware adaptive fusion+noise-robust consistency，比 CGX 更进一步，GOOG 120.48%/TSLA 148.41%）+**市场依赖通信**（arxiv 2511.13614 CMU 2025-11，细化 CGX：竞争式适用高波动科技股/协作式适用稳定股/金融股抵抗所有通信）+**MarketSenseAI 自适应集成**（arxiv 2604.17327 2026-04，4 specialist agent+synthesis，agent 贡献随 regime 轮换非主导 agent，ICIR +0.489）
>
> **v1.0.0 九轮审查（2026-08-10）**：补 2 项施工算法缺口+选项外更优算法，**"Wasserstein 家族"三件套成形**——#1 补 **Tail-Aware MDN**（arxiv 2601.14049 Paris-Dauphine 2026-01 + ESANN 2026 扩展，skewed Student-t Mixture Density Network 专攻 locally explosive time series，**与 A 股打板"涨停→炸板"动力学原生匹配**，skewed t 替代 Gaussian mixture 捕获右偏+左重尾，dual reweighting 解决炸板日稀有极端事件学习不足，配套 local explosive dynamics 检测作气泡态前置门控）；#3 补 **Certified Wasserstein DRO 组合**（arxiv 2608.07032 Hsieh&Gan 2026-08-07 极新）+**Shift-Aware Wasserstein-DRO CVaR**（arxiv 2512.16748 Columbia NeurIPS 2025）+**Wasserstein-Kelly**（JUSTC 2025 USTC）——与 v0.9.0 #7 Wasserstein HMM 形成 regime 层+组合层+仓位层"Wasserstein 家族"三件套，统一用 Wasserstein 距离作鲁棒性度量
>
> **v1.1.0 十轮审查（2026-08-10）**：补 2 项选项外更优算法——#7 补 **BR-iHMM**（Yiu/Sánchez-Betancourt/Cartea/Duran-Martin 2026，doubly outlier-robust online infinite HMM，预测误差降低最多 67%，与 Wasserstein HMM 正交互补：Wasserstein HMM 解决标签漂移，BR-iHMM 解决离群点毒化 emission/transition+无限状态数自适应）；#3 补 **Wasserstein 生成式数据建模**（Huang et al. preprints 2026-02-28，WGAN+Wasserstein DRO 组合，Wasserstein 家族生成式扩展，与 91 号 Phase 2 GPD/TailGAN 共享 GAN 栈协同）
>
> **v1.2.0 十一轮审查（2026-08-10）**：补 4 项施工算法 why 缺口+选项外更优算法+过度工程纠偏，聚焦 2026-08 极新研究——① #1/#2 补 **A 股涨跌停 upstream contamination**（arxiv 2507.07107v2 USTC 2026-05-09，涨停收盘价不可执行却进入滚动窗口聚合，IC 虚高 18% / 实现 Sharpe -0.44，mask-first 设计是 why），**与打板策略原生相关**；② #6 补 **AlgoXpert IS-WFA-OOS 协议**（arxiv 2603.09219v1 2026-03-10，plateau 优先+purge gap+majority-pass/catastrophic-veto 门控）+**plateau 启发式受控验证**（Soloviov plateau.marketmaker.cc 2026，"选 plateau"作选择偏置有效 +0.12-0.31 OOS Sharpe，但作独立过拟合检验弱）+**PBO 零假设=0.5 而非 1**（marketmaker.cc 2026-07-01，PBO≈0.5=完全过拟合=抛硬币）；③ #19 补 **Conformal-gated 执行 vs RL 执行**（SOIC Vol.16 2026-08 pp.1334-1349 U Hull，conformal 门控使成本方差 19.1→10.0bps，PPO 跨种子高方差不稳定胜过静态调度——**反向印证"慢而稳 conformal 胜过 RL"在执行域同样成立**，质疑个人系统 RL 执行必要性）；④ regime 层补 **Robust HMM 替代谱系**（egargale/hmm_test PRD #20 2026-05-29：Huber Robust HMM/Student-t/GH/Feature Saliency/BR-iHMM/AH-HMM Tampouris&Dritsaki 2026），Wasserstein HMM 之外另有 6 候选。**过度工程纠偏**：v1.0.0"Wasserstein 家族三件套"+conformal 五变体栈（slow→EWMA→RWC→ACI→COP）经多轮累积偏"加法"，本次标注最小可行 baseline 边界，需人决策是否收敛选项。
>
> **v1.3.0 十二轮审查（2026-08-10）**：补 2 项选项外更优算法——① #3 补 **MFCCA 多重分形组合分配**（arxiv 2608.04987 Kakinaka&Umeno 2026-08 极新，带符号波动函数作风险泛函，q=2 退化为 mean-variance 的尺度依赖极限，样本内外均降低 drawdown/VaR/ES 不损失收益，符号保持比波动阶聚合对尾部风险贡献更大），列为 risk parity 远期五级递进第五级（Phase 4+ 非 MVP）；② #1 补 **Lévy 家族重尾升级交叉引用**（见 91 号 v1.2.0）——DeepLévy（α-stable mixture+CFM，α<2 方差无限）作 Student-t MDN 极端尾部升级+Lévy-Flow（VG/NIG normalizing flow，VaR Kupiec p=1.00）作 Phase 2 生成式精度替代，形成 Student-t/α-stable/VG-NIG 三家族重尾密度预测完整谱系。**延续 v1.2.0 过度工程纠偏**：MFCCA 与 Lévy 家族均定位为远期升级/替代非 baseline，MVP baseline 边界不变。
>
> **v1.4.0 十三轮审查（2026-08-10）**：补 3 项选项外更优算法，聚焦 2026-07/08 极新研究+风控优先原则核心——① #2 补 **Cross-Sectional Heterogeneity LSTM**（arxiv 2608.05755 Döbelt 2026-08-06 极新，learnable sector embeddings+宏观协变量+label smoothing/dropout/gradient clipping 正则，S&P 500 long-short 超基准，可解释 sector contribution metric）——是 25 号多因子+22 号板块轮动的"输入端截面增强"非新增架构，对接 91 号 v1.3.0 Phase 1.5+ 截面特征增强；② #4 补 **Drawdown Risk Beyond Brownian Motion**（arxiv 2608.00127 Landolfi 2026-07-31 极新，扩展 RSB 回撤框架，4 决策测度查找表 MaxDD/Max Loss/Final Negative Time/Longest Recovery Time，非高斯下四测度分化致 Gaussian 表系统性误警，fBM 长记忆是 sqrt(T) 校准失效非路径深化）——**直接对应项目风险优先原则核心（4 级回撤 Protocol + drawdown_controller）**，提供数据驱动阈值校准路径（8/15/20/25%→MaxDD 分位数），与 91 号 Lévy 家族形成"密度预测→回撤测度"上下游闭环；③ #18 补 **CAI++ Copula Asymmetry Index**（Risks 2026,14,86 Hatzopoulos&Statiou 2026-04-13，股跌&波升 vs 股升&波降 滚动频率差 rank-based 非参数尾部不对称依赖，CAI++ 框架 smoothing/standardization/delayed execution/hysteresis/cost-aware mapping 转防御信号，50 对实证 vs 60-40 占优但不替代 risk parity）——是 §18 股指期货 P2 背景级的"防御信号转化"路径，定位 drawdown_controller/kill_switch Phase 2 事前防御 overlay。**延续过度工程纠偏**：三项均定位 Phase 1.5+/Phase 2 升级非 MVP baseline，Cross-Sectional LSTM 是输入端增强非新增架构，Landolfi 查找表+CAI 属风控优先原则核心增强符合风险模块优先施工硬约束。
>
> **v1.5.1 十四轮审查（2026-08-10）**：补 1 项选项外更优算法，聚焦组合构建层 HRP 局限——#3 补 **TRP 拓扑风险平价**（arxiv 2604.16773 Nayar/Ainasse/Kulkarni FMI Technologies 2026-04-18，从相关性-距离图提取稀疏有根 MST 拓扑+传播法则将带符号信号映射为组合权重，Mixed Split-Replication Coefficient α_u(ρ)=(1-ρ)+ρ/b(u) 控制信号传播，ρ=0 退化为纯信号归一化/ρ=1 退化为保守等分）——**直击 HRP 两大局限**：① HRP 仅 long-only（递归二分+逆方差只能产生非负权重，long-short 需额外中性化），TRP 原生支持多空（w_v=s_v×g_v 正信号→多头/负信号→空头）；② HRP 纯风险分配忽略 alpha 信号（辛辛苦苦生成的多因子 alpha 被 HRP 完全忽略），TRP 保留信号方向（w_v=L×s_v×g_v/||x||₁）。**Semi-Supervised TRP 变体 II** 的"市场根→行业 ETF→个股"层级直接对接 22 号板块轮动（申万一级 28 行业作第二层）。**risk parity 远期递进扩为六层**：naive→HRP（long-only）/TRP（long-short+信号）→Certified W-DRO→W-GAN→MFCCA。同步 91 号 v1.4.0 补 **Exformer 极端自适应 Transformer**（arxiv 2607.02437 2026-07-02，极端自适应注意力 Extreme Attention 专攻稀有极端事件间 event-aware 依赖，与打板"涨停→炸板"原生匹配，与 QFCQT 正交分工全局 regime 突变 vs 局部极端事件）。**延续过度工程纠偏**：TRP 是 HRP 的多空+信号增强非全新架构（MST+DFS ~150 行），Exformer 是标准 MHA 稀疏化变体（~100 行），均定位 Phase 1.5+/Phase 2 升级非 MVP baseline。

> **v1.6.0 审查（2026-08-10，对应文档 v1.17.0）**：整合 2026-08-04~10 全网搜索 8 项最新研究发现——① #3 组合构建层补 **C-WRP（Certified Wasserstein Robust Portfolio）**（arXiv:2608.07032，v1.0.0 已登记 Wasserstein 家族组合层，本次补充 LP 化+certified approximation error bound 视角，MVP 用三因子乘法替代优化器，C-WRP 是远期升级路径，Phase 4+ 远期候选）+**RRP（Robust Risk Parity with GARCH+Market State）**（Finance Research Letters vol.92(C) 2026，中国市场 2012-2024 实证全面优于 TRP/EW/GMV，risk parity 递进"A 股实证优化"中间档）；② #7 regime 层补 **VRMD（Velocity-Regime Manipulation Detection）**（arXiv:2608.05373，Gaussian HMM regime+option-Delta velocity 检测盘中操纵，关键反面结果：regime 条件化用 recall 换 precision 上限约 25%——**已评估不整合**，反面结果支持项目 4 态 HMM 不过度细分的决策）；③ #10/91 密度预测补 **FCVE（Finite-Sample Conformal Joint VaR-ES）**（Mathematics 14(15):2847 2026-08-06，conformal risk control 耦合 VaR breach frequency+magnitude，non-exchangeable swap-distance bound+regime-drift bound+heavy-tail rate，Phase 2 远期候选，是 RWC/TWC 的 joint VaR-ES 扩展）；④ #19 执行算法补 **A-CRaQL（Adaptive CVaR Risk-Aware Q-Learning）**（arXiv:2608.04305 ICAIF'26，不改 CVaR 估计器重新设计训练流程，CVaR Bellman residual 降 ~85%——**已评估不整合**，与 v0.8.0"Conformal-gated 执行 vs RL 执行"结论一致"慢而稳 conformal 胜过 RL"在执行域同样成立，RL 执行在个人系统必要性存疑，conformal 闸控已足够）；⑤ #2 因子工程补**量化"双杀"压力测试**（2026-07 沪深300指增平均超额-1.51%/中证500-4.54%/动量因子单月回撤超 20 个百分点十年罕见，印证因子拥挤度监控必要性）；⑥ 新增 **A股市场结构变化（2026-07/08）** 小节——A股交易新规（盘后固定价格交易扩容全部 A 股+沪深 ETF/主板 ST/*ST 涨跌幅 5%→10%/上交所基金收盘连续竞价改集合竞价/深交所创业板引入做市商）+微盘股策略失效机制（科技股虹吸→流动性枯竭→量化同质化多杀多→退市新规基本面恶化，微盘 Q1 归母净利同比-79.25%）+量化"双杀"压力测试，需在 24/25/26 号策略文档同步更新施工约束+因子拥挤度监控+流动性门槛强化。**延续过度工程纠偏**：VRMD/A-CRaQL 明确标注"已评估不整合"，C-WRP/RRP/FCVE 均定位 Phase 2+/Phase 4+ 远期候选非 MVP baseline。

> **v2.0.0 全量裁定（2026-08-12，架构审查终审）**：21 项遗留提案**全部完成裁定**，文档从 draft 升 active。裁定分布：✅ 已裁定维持 4 项（#3/#4/#6/#11，同步修正锚点）｜✅ 本轮新裁定 10 项（#1 策略类型修订采纳 / #2 因子IC双轨采纳 / #5 成本简化采纳 / #8 流动性简化采纳 / #9 数据分层修订采纳 / #13 基准 sleeve 级多基准 / #14 PIT 确认已施工 / #15 资产分级两维精简 / #17 行为边界拒绝OPA改choke point / #19 大额下单默认限价单）｜✅ 合并裁定 2 项（#12 并入 #16；#21 做T采纳为受约束 overlay+四规则）｜❌ 暂缓/远期 2 项（#7 T+1 8态预测暂缓建设 / #10 密度预测远期维持 91 号）｜📝 待用户裁定 5 项（P-1~P-5 建议方向已给，见「待定问题」节）。**重要更正**：① 11 号 v1.5.2 确认 A2 验证器降 4 态后已 **PASS**（OOS/IS=1.042），本文档多处"12 号 A2 FAIL"表述过时——Wasserstein HMM 从"A2 修复必需"降级为 Phase 3+ 可选增强；② 91 号实际仅 v0.1.2 骨架，本文档引用的"91 号 v0.4.0~v1.4.0"内容（四阶段路线/RWC/Lévy/Exformer）**均未落盘到 91 号**，标注为规划态；③ 30 号锚点从 v1.3.3 更新至 v2.5.0（Kelly 已升级 Fractional Kelly 25-50% 三档演进，PerformanceScore 口径已改 Sortino）；④ §3 FirmRiskAggregator 模块编号 MOD-POS-001→MOD-POS-021 修正；⑤ #5 印花税"千1"→卖出单边万5（2023-08 减半后现行）；⑥ BM-BT-07/BT-10 状态三方口径对齐（decision_gate.py 策略路径已 production，regime 验证 Phase 5 门控未完成；BT-10 PIT 已 production）。新增「已施工设施盘点」节（通用规则 #11）。裁定依据：第一性原理 + 2026-08 业界/量化社区/氛围编程社区调研 + system_charter §2 硬边界（1人+100%AI+单机+小资金）。
>
> **重要**：讨论时以项目实际代码和已定稿文档为准。regime 检测器 spec 为 12 态（10_regime_detector_spec v1.5.1），但**实际实现为 4 态 HMM + 3 overlay = 7 维概率**（11_regime_backtest §0.5.2，BIC 扫描发现 9 态过度细分降为 4 态，A2 已 PASS）。

## 遗留提案总览

| 原编号 | 主题 | 对应G主题 | 与现状的关系 | v2.0.0 裁定 |
|:------:|------|:--------:|-------------|:-----------:|
| 约束一 | 策略类型目录(6大类) | G04 | 项目实际"首批3策略"；registry 6类口径（daban/multifactor/event_driven/value_reversal/momentum_trend/sector_rotation）与本稿6大类不一致 | ✅ 修订采纳（四族双层标注，原6大类表 deprecated） |
| 约束二 | 因子分类与IC阈值 | G01 | G01因子工程总纲已定稿（15号），IC阈值未验证 | ✅ 修订采纳（静态地板+滚动分位双轨+BHY FDR+ICIR≥0.5） |
| 约束三 | 组合构建硬约束 | G12 | ✅ 已裁定：30_multi_strategy 定 risk parity + Kelly firm层，非risk budgeting | ✅ 维持（锚点更新 v2.5.0，MOD-POS-021 编号修正） |
| 约束四 | 风险模型(L1/L2/L3) | G16-G18 | ✅ 已裁定：30_multi_strategy §2.5 定 4级回撤Protocol(8/15/20/25%)，非L1/L2/L3 | ✅ 维持（代码 5/10 阈值与文档 8/15/20/25 口径对账待 G13/G14） |
| 约束五 | 成本模型细节 | G22 | 宪章只保留成本结构(不含费率)，细节待讨论 | ✅ 简化采纳（砍 Almgren-Chriss MVP、最低佣金5元显式建模、印花税更正万5） |
| 约束七 | 回测门禁(V1~V6) | G23 | ✅ 已裁定：项目用 BM-BT-01~07 体系，V1-V6 已映射（见 §6） | ✅ 维持（BT-10 PIT 已 production、BM-BT-07 口径澄清） |
| 约束九 | T+1次日预测(8态) | G02 | 8态(BM-SEL-04)是独立下游消费者(未建)；8态→直接决策映射过时(Model A) | ❌ 暂缓建设（52-53%天花板未突破，远期窄目标重启条件已定义） |
| 约束十 | 流动性风险 | G18 | G18已定稿（37号 v1.0.16），liquidity_monitor(Amihud) 已 production | ✅ 简化采纳（压力退出时间>1天→禁开仓；LVaR 简化式 Phase 2） |
| 约束十一 | 数据分层使用(Layer0~4) | G01 | Layer2 引用已更正为 regime 检测；样本权重代码未施工 | ✅ 修订采纳（半衰期 HL 2-3年参数化；断裂期降权保留不剔除） |
| 约束十二 | 密度预测(QNN) | 无 | 已拆为91_density_prediction独立讨论（⚠️ 91号实际 v0.1.2 骨架，引用内容未落盘） | ⏸️ 远期维持（Phase 0 基线=slow unweighted conformal，91号待回填） |
| 约束十三 | 仓位管理(C-047) | G12/G13 | ✅ 已裁定：30_multi_strategy §2.1/§7.2 用 MOD-POS-020/021/022，非C-047 | ✅ 维持（半Kelly→Fractional Kelly 25-50% 锚点更新） |
| §9移出 | 成功指标交易参数 | — | 阈值拍脑袋未验证 | ✅ 并入 #16（线性收紧规则 deprecated，已被4级Protocol替代） |
| §3移出 | 基准设计 | — | benchmark_registry 已建（沪深300/中证500/中证全指/绝对收益） | ✅ 修订采纳（sleeve级多基准；废弃60/40拼合基准） |
| §3移出 | PIT一致性 | — | pit_query + pit_manager 已 production | ✅ 确认已施工（双值存储等价语义已覆盖；泄漏检查增强 Phase 2） |
| §4移出 | 资产分级(P0-P3) | — | universe_registry 已建（static/dynamic/rule_based） | ✅ 修订采纳（两维精简：准入×数据覆盖；P0-P3 deprecated） |
| §9移出 | 系统级成功指标 | — | KPI 监控代码未施工（55号 draft） | ✅ 修订采纳（生存线下调 Sharpe≥0.8；健康/卓越线实盘6-12月校准） |
| §5移出 | 行为边界(B-002~B-005) | G16/G22 | 43门禁+风控强制+时段校验已施工；OPA 未施工 | ✅ 修订采纳（拒绝 OPA；choke point+YAML规则，OPA 降远期） |
| §4移出 | 资产与市场覆盖 | — | instrument 契约+symbol_normalizer+~100 schema 已施工 | ✅ 修订采纳（轻量 Instrument Master 表 Phase 2，拒绝重型系统） |
| B-013.6 | 大额下单 | G22 | ex_sor TWAP/VWAP/POV/ICEBERG 已施工 | ✅ 修订采纳（默认限价单+打板专用路径；删5%ADV硬条款；算法执行降远期） |
| B-008/010/012/013 | 工程细节 | — | echo-guard/退役/相关性门禁已施工；指纹库/DTW 未施工 | ✅ 逐项裁定（B-010 三维指纹 Phase 2；B-012/B-013 归治理文档闭环） |
| — | 做T方法论 | — | 3个做T策略+tick基类+回放已 production | ✅ 采纳为受约束 overlay（sizing/regime过滤/失败处置/冲突管理四规则） |

---

## 已施工设施盘点（v2.0.0 新增，通用规则 #11）

> 盘点日期 2026-08-12。范围：src/zephyr/ 代码、docs/01_policies_and_standards/_registry/catalogs/ 注册表、schemas/、tests/、治理脚本。**先清楚有什么→才知道怎么改→才知道该删除/退役什么**。21 项中 8 项已施工、8 项部分施工、5 项未施工（施工缺口均已在对应条目登记 Phase 2 方案）。

| # | 主题 | 判定 | 已施工设施（证据路径） | 缺口 |
|---|------|:----:|----------------------|------|
| 1 | 策略类型/工厂/注册表 | 🟧 部分 | `catalogs/strategy_registry.yaml`（REG-STR-001 active，6类口径=daban/multifactor/event_driven/value_reversal/momentum_trend/sector_rotation，含 lifecycle/decay/capacity 字段）；`governance/strategies/strategy_base.py` StrategyRegistry（production）；`pf_core/strategy_engine/strategy_runner.py`（MOD-L05-001） | 独立 strategy_factory 模块未建（runner autodiscover 已覆盖注册职能） |
| 2 | 因子分类与IC | 🟦 主干 | `catalogs/factor_registry.yaml`（含 ic_mean/icir 阈值字段）；`factor/analysis/` 全套（ic_decay/ic_ir_calc/decay_monitor/three_level_judgment/correlation_analyzer）+ `governance/factor_pool_manager.py`（8状态生命周期）+ 测试齐备 | SHAP 未施工；多重检验校正（Bonferroni/BHY）未施工 |
| 3 | 组合构建 | 🟦 已施工 | `position/core/strategy_book.py`（MOD-POS-020 production，equal_weight/risk_parity/custom，显式禁 Kelly/MVO）；`firm_risk_aggregator.py`（MOD-POS-021 production，pre_kelly_aggregate→Kelly→post_kelly_clip，kelly_param_source="density_pdf" 接口预留）；`budget_change_handler.py`（MOD-POS-022）；`pf_alloc/core/regime_meta_allocator.py`（MOD-PA-007，Shrinkage 只减不增、floor 5%/cap 40%） | 30号 §7.2 自注 RegimeMetaAllocator 代码仍骨架（C1验证已过） |
| 4 | 风险模型 | 🟦 已施工 | `position/core/drawdown_controller.py`（MOD-POS-008 production：5级 VaR 风险级 GREEN~BLACK + Soft 5%/Hard 10% 策略止损 + 黑天鹅 7 模式）；`risk/core/var_calculator.py`+`var_backtester.py`+`tail_risk_monitor.py`+`stress_test_engine.py`；kill_switch 三处实现；`catalogs/risk_limit_registry.yaml`（9类限额） | ⚠️ 代码阈值（Soft 5%/Hard 10%）与文档 4级 Protocol（8/15/20/25%）双轨并存，30号 §2.5 已自注"须 G13/G14 明确映射"——对账未闭环 |
| 5 | 成本模型 | 🟦 已施工 | `catalogs/cost_model_registry.yaml`（CST-ASTOCK-001：佣金万3/印花税万5/过户费/滑点；slippage_model: fixed/linear/square_root）；`ex_sor/services/slippage_analyzer.py`（平方根冲击律 impact=coeff×√participation×vol_bps）；`transaction_cost_optimizer.py`（Kyle λ 简化） | 做T额外成本专门条目未建 |
| 6 | 回测门禁 | 🟦 主干 | 双引擎 `backtest/implementations/vectorized_engine.py`+`event_driven_engine.py`；`core/decision_gate.py`（MOD-BT-001 production：IS Sharpe>0.5→WFA 多数通过+灾难否决→OOS≥70% IS；偏差>30%告警/>50%退役）；`core/overfitting_detector.py`（三维度）；`core/walk_forward.py`；`core/tick_replay.py`；`simulation/deflated_sharpe_calculator.py` 代码已存在 | Purged K-Fold/Permutation Test/PBO 未施工（文档级）；CPCV 配置预留；⚠️ BM-BT-05-G（DSR）battle_map 标 design 但代码已存在——口径需对账 |
| 7 | T+1 次日8态预测 | ⬜ 未施工 | 仅登记：BM-SEL-04 status=design（10号 §2.1"下游消费者，非检测器本身"） | 全部未建——v2.0.0 裁定暂缓建设 |
| 8 | 流动性风险 | 🟧 部分 | `risk/core/liquidity_monitor.py`（production：Amihud ILLIQ+成交量萎缩比率+HALT/WARNING，已接入 default_risk_manager_orchestrator，有测试）；37号流动性危机 memo | LVaR、退出时间估算、流动性评分体系、跌停/停牌概率维度未施工 |
| 9 | 数据分层 | 🟧 部分 | `docs/.../contracts/data_retention_contract.yaml` 10层留存分层（数据治理语义）；`config/data/survivorship_policy.yaml` | 训练样本 Layer0-4 分层+指数衰减/半衰期样本权重未施工（与留存分层语义正交） |
| 10 | 密度预测 | ⬜ 未施工 | `feedback_loop/evolution/conformal_prediction.py` 简易 CP 骨架（进化模块用，非市场密度）；firm_risk_aggregator `kelly_param_source="density_pdf"` 消费接口预留 | RWC/LSTM+GMM/MDN 均未实现；91号文档 v0.1.2 骨架待回填 |
| 11 | 仓位管理 | 🟦 已施工 | `position/core/` 14 模块全家桶（position_sizing_engine MOD-POS-001、position_drift_monitor MOD-POS-003、position_audit_logger MOD-POS-009 哈希链、position_limit_enforcer 单票≤5%NAV、rebalance_engine、cash_manager 等） | ±2%/±3% 漂移带数值未在源码直接确认（drift monitor 存在，阈值在 blueprint/配置）；"再平衡收益>2×成本"规则无显式实现（30号用 ε_pos=5% 收敛容差+no-trade 半带 Phase 2 候选替代） |
| 12/16 | 成功指标/KPI | ⬜ 未施工 | 相邻设施：`config/sli_registry.yaml`+`alert_rules.yaml`（基础设施 SLO，非交易 KPI）；decision_gate "偏差>50%退役"是最接近的健康线逻辑 | 生存/健康/卓越/失败四档监控代码未建（55号 monitoring draft） |
| 13 | 基准设计 | 🟦 注册表 | `catalogs/benchmark_registry.yaml`（REG-BMK-001：沪深300/中证500/中证全指/绝对收益，含 active_share/style_drift_detection 字段）；`backtest/core/metrics.py`；`pf_core/core/performance_attribution_engine.py` | 中证1000/中证2000/万得全A sleeve 级基准条目未登记；benchmark_symbol 仅字符串未结构化（注册表自注） |
| 14 | PIT一致性 | 🟦 已施工 | `data/pit_query.py`（announce_date<=query_time+LIMIT 1 BY 取查询时点最新版本+embargo_clause+AS OF JOIN，白名单财务表）；`backtest/core/pit_manager.py`（PIT三公理+pit_consistency_test）；`scripts/arch_guard/fitness_functions/check_survivorship_bias.py`；测试齐备 | 术语映射：first_filed≈announce_date（已覆盖）；重述双值=ClickHouse ReplacingMergeTree 版本语义（等价覆盖）；deliberate future-date 泄漏测试未自动化 |
| 15 | 资产分级 | 🟧 部分 | `catalogs/universe_registry.yaml`（REG-UNI-001：static/dynamic/rule_based 三型；UNI-RULE-001 全A可交易池[剔ST/退市风险/次新<60天/日均成交额<1000万]） | P0-P3/eligible 三态未施工；流通市值分层字段未建；tradability_mask 函数代码零命中 |
| 17 | 行为边界 | 🟧 部分 | 43门禁引擎 `gov_enforcement/rule_enforcement/gate_engine/gate_engine.py`+`_registry.yaml`；`scripts/git_guard.py`；`risk/risk_limits.py`+`implementations/default_position_limit_checker.py`+`g7_position_limits.yaml`（集中度/仓位上限）；`ex_core/trading_session.py`（时段校验）；`programmatic_trading_guard.py`/`cancel_rate_guard.py`/`price_cage.py` | OPA/Rego 未施工（v2.0.0 裁定拒绝，改 choke point 方案）；单一订单出口架构确认待验证（40号 G22 已施工 commit 015826ae） |
| 18 | 资产与市场覆盖 | 🟧 部分 | `trading/trading_contracts/market/instrument.py`（Stock/ETF/Future/Option/Bond/FX/Crypto 契约）；`data/symbol_normalizer/normalizer.py`；schemas ~100 类（A股/ST/港股/可转债/期货/期权/ETF/LOF/美股/指数成分/日历） | 独立 Instrument Master 主数据模块未建；ST 状态 PIT 跟踪散见于 universe 过滤规则未独立成表 |
| 19 | 大额下单/算法执行 | 🟦 MVP | `ex_sor/core/algo_execution_selector.py`（TWAP/VWAP/ICEBERG/POV 选择器，>5%ADV 倾向 ICEBERG，决策留痕）；`algo_trading_engine.py`；ADV/参与率计算在 slippage_analyzer；`reporting/default_tca_engine.py`（TCA） | v2.0.0 裁定默认路径改限价单——选择器默认策略配置项待调（非新建） |
| 20 | 工程细节 | 🟧 部分 | echo-guard/CodeSAGE（`echo-guard.yml`+`clone_guard/engines/echo_guard_adapter.py` 主检测引擎+多引擎聚合器）；策略退役 lifecycle（strategy_registry candidate→retired）+`pf_alloc/strategy_lifecycle_event.py`；decay_monitor 双实现；`pf_alloc/core/strategy_correlation_gate.py`（MOD-PA-004：>0.85 REJECT/>0.90 HARD_REJECT/尾部相关0.70） | 策略指纹库未建；DTW PnL 相似度未施工；intent netting 零命中；90天滚动相关持久化条件未确认 |
| 21 | 做T | 🟦 已施工 | `pf_core/intraday_surge_fall_strategy.py`（30秒冲高回落）+`orderbook_imbalance_strategy.py`（盘口失衡）+`vwap_reversion_strategy.py`（VWAP回归）+`strategy_engine/tick_strategy_base.py` 基类+`backtest/core/tick_replay.py` 回放引擎；测试齐备 | 做T sizing/regime过滤/失败处置/冲突管理四规则未配置化（v2.0.0 裁定补齐）；做T成本条目（见#5） |

**注册表配套（12 个业务注册表已建 6 个）**：✅ factor/strategy/universe/benchmark/cost_model/risk_limit；❌ technical_indicator/execution_algo/data_asset/chart_pattern/field_dictionary/experiment（62 号文档规划中，`experiment_tracking/` 代码模块已施工但注册表未建）。

**盘点结论对裁定的约束**：① 凡"已施工"项的裁定以代码真源为准（不做文档级重复设计）；② 缺口项全部登记 Phase 2 施工方案（见各条目"施工方案"），MVP 零新增——符合 system_charter §2 硬边界（单人单机不新增架构组件）；③ 需退役/降级的历史内容在各条目标 deprecated，不删除（保留历史可追溯）。

---

## 1. 策略类型目录（原约束一）

> 对应 G04（首批3策略定义）｜ ✅ **v2.0.0 裁定：修订采纳（四族+管线双层标注），原 6 大类表 deprecated**

**✅ v2.0.0 裁定结论**：

- **本质**：策略分类的目的是隔离收益来源、衰减假设与风控属性，不是越细越好。2026 业界/社区已收敛到"按收益来源"的四族（动量趋势/因子投资/均值回归/事件驱动），本稿原 6 大类按"信号来源"分类且与 strategy_registry.yaml 实际登记的 6 类（daban/multifactor/event_driven/value_reversal/momentum_trend/sector_rotation）口径不一致。
- **裁定**：① **原 6 大类表（动量/均值回归/价值/事件驱动/做T/防御）标 deprecated** 作历史参考——其中"防御"不是策略族而是 regime 下组合层风控行为（归 34 号 Shrinkage 节流），"做T"不是独立策略族而是底仓 overlay（见 §21）；② **项目现行口径以 strategy_registry.yaml 6 类为真源**（已施工注册表），新增策略沿用该 6 类声明族归属，四族+管线谱系作分析标注层（四族管"是什么 alpha"，管线管"在哪个环节"）；③ **首批 3 策略 ⊂ 目录关系确认**：打板=事件驱动族×短线情绪动量交叉（daban）、多因子=因子投资族（multifactor）、事件驱动=事件驱动族（event_driven）；④ **策略工厂强制目录内生产——采纳为治理规则**：AI 生成策略必须声明族归属+alpha 假设+容量，防无法归类的过拟合怪物（经 strategy_registry candidate 状态+43 门禁强制）。
- **施工方案**：零新增施工——strategy_registry.yaml 已有 lifecycle/capacity/decay 字段，新增策略登记时强制族归属声明即可（治理流程，Phase 0 生效）。
- **过度工程审查**：四族标注是元数据非新架构；不建独立 strategy_factory 模块（strategy_runner autodiscover 已覆盖注册职能）。✅ 通过。

**原始内容（deprecated，保留作历史记录）**：

| 策略大类 | 子类 | 信号来源 | 适用市场状态 |
|---------|------|---------|------------|
| 动量类 | 趋势跟踪/突破/动量反转/板块轮动 | 量价因子 | ①②③趋势向上/⑪板块轮动 |
| 均值回归类 | 统计套利/配对交易/超跌反弹 | 价差/估值因子 | ④⑤震荡/⑥压缩突破 |
| 价值类 | 深度价值/GARP/质量因子 | 基本面因子 | ④⑤震荡/①②趋势向上 |
| 事件驱动类 | 财报超预期/政策催化/重组 | 事件因子+另类数据 | ⑩事件驱动叠加态 |
| 做T类 | 日内T+0套利(底仓) | 分时因子+波动率 | ③⑥高波动列 |
| 防御类 | 低波动/红利/对冲 | 风险因子 | ⑦⑧⑨趋势向下 |

**待讨论问题**：
- 6大类框架是否采用？项目当前讨论的是"首批3策略（打板+多因子+事件驱动）"，与6大类目录是什么关系？
- 策略工厂是否强制只能生产目录内类型？

**2026 更优框架补充（v0.4.0）**：原 6 大类按"信号来源"分类，2026 有两种更先进的分类法：
- **管线谱系（Pipeline Taxonomy）**——Shehral 2026-04（Northeastern，~50 篇论文综述）：将 8 个子领域映射到六阶段信息处理管线（数据获取→信号生成→组合构建→交易执行→风险管理→元层编排），揭示跨领域依赖。优势：暴露策略间的管线依赖（如执行算法影响 StatArb 盈利性）
- **四族分类（Four Families）**——vzeman 2026-05（系统性权益交易研究）：A 动量/趋势（cross-sectional momentum 12-1，net Sharpe ~0.65）+ B 因子投资（"Big Five" value/momentum/quality/size/low-vol）+ C 均值回归/StatArb（pairs + OU 过程）+ D 事件驱动/波动率风险溢价。优势：每族有实证 Sharpe 区间，避免"拍脑袋"
- **项目映射**：首批 3 策略 → 打板(D 事件驱动变体) + 多因子(B 因子投资) + 事件驱动(D)，主要落在 B+D 两族。原 6 大类的"做 T 类"和"防御类"在四族中归入 C(日内均值回归) 和 B(low-vol 因子)
- **建议**：6 大类可保留作历史参考，新策略分类用四族+管线谱系双层标注（四族管"是什么 alpha"，管线管"在哪个环节"）

**2026 打板环境剧变实证（v0.6.0 补充）**：五轮审查发现 2026 年 8 月 A 股打板生态发生**结构性剧变**，影响"打板"作为策略类型的可行性边界：
- **打板次日溢价坍塌**——东方财富 2026-08-03（极新）：2023 年 A 股打板次日平均溢价 4.2%，**2026 年已降至 1.7%**（高位科技涨停次日溢价中位数为负）。炸板率从 2023 年 40% 升至 **2026 年 68%**。量化成交占全市场 35%+（中小盘题材股 50%+），量化通过机器学习完整复刻游资盘口特征（点火大单/封板挂单/分时脉冲），从"助攻者"变为"最大对手盘"
- **4 月程序化新规**——2026-04 交易所程序化交易新规落地：实时监控多账户联动、大额对倒、频繁撤单，打击联合坐庄。9 连板以上标的易触发监管停牌核查（爱丽家居 9 连板后停牌）
- **打板情绪量化算法**——legulegu 2026-08-07（涨停板情绪综合评分）：6 指标加权评分（封单强度/炸板率/连板转化率/涨停成交额/封板效率/涨停均市值），百分位排名×权重，范围 0-100。赢牛资管 2026-06：炸板率+溢价率双指标划分情绪 4 阶段（高潮期炸板率<20%→分歧期 30-50%→退潮期>50%→冰点期从极高回落），与项目情绪周期 4+1 阶段（冰点/反核/主升/疯狂/退潮）对应
- **启示**：① 打板策略的 alpha 在 2026 显著衰减（溢价 4.2%→1.7%），需纳入 #20 Alpha Decay 监控（半衰期可能缩短）；② 项目打板策略（24 号）需补**炸板率/溢价率情绪因子**作为择时门控（退潮期>50% 炸板率时停打板）；③ 程序化新规合规层（申报速率≤15 笔/秒、撤单率≤15%）是打板策略的硬约束（已在 24 号文档登记施工缺失）；④ 量化对手盘意味着打板策略需从"跟游资"转向"反量化"——低位干净筹码小票+事件催化新题材（2026-08 游资新共识）

**2026 打板筛选施工算法补充（v0.7.0）**：六轮审查发现打板策略的**具体筛选算法**在 2026 已有开源实现和量化规律，可作为 24 号文档施工算法缺失（涨停时间分层量化/换手率黄金标准）的补充：
- **akshare 连板接力筛选算法**（CSDN 2026-08-05，开源代码）：基于 akshare `stock_zt_pool_em` 接口的连板接力股票池筛选，硬性条件：① 股价≤30 元 ② 总市值≤300 亿 ③ 流通市值≤250 亿 ④ 最后封板时间≤14:30 ⑤ 炸板次数≤5 ⑥ 排除断板再涨停 ⑦ **封成比≥5%**（封板资金/成交额）。排序：连板数降序→首次封板时间升序。**与项目对接**：24 号打板策略的"涨停时间分层量化"施工缺失可直接采用此筛选条件（封成比≥5% 是封板强度的核心指标，封板时间≤14:30 避免尾盘投机板）
- **6 维度涨停规律**（犇犇浅谈 2026-08，3200 只隔日涨停复盘）：前一日 6 维度全部达标→隔日涨停概率 91%（声称值，需独立验证）：① 分时盘口痕迹（90% 时间在均价线上方+2-3 次脉冲试盘+振幅≤2.5%+大单压盘不砸盘）② 量价换手标准 ③ K 线位置蓄势 ④ 尾盘异动信号 ⑤ 板块联动加持 ⑥ 集合竞价前置预期。**4 个分时硬性指标**（前一日）：股价 90% 时间在分时均价线上方回踩秒级收回/盘中 2-3 次脉冲试盘冲高 2-4% 回落/全天振幅≤2.5% 窄幅锯齿/压力位大单压盘但不主动砸盘
- **8 月游资转型实证**（东方财富 2026-08-03）：申万电子板块 8 月 3 日主力资金净流出 187 亿；公募基金二季度重仓的 12 只算力龙头 7 月下旬平均减持 22%；8 月 2 日工业富联盘中触及跌停（游资千万资金承接 vs 量化上万手抛单瞬间砸穿）。**量化对手盘完整复刻游资盘口特征**（点火大单/封板挂单/分时脉冲），微秒级捕捉
- **个人系统适用性**：akshare 筛选算法可直接复用（开源+akshare 已是项目数据源）；6 维度规律的 91% 概率为社区声称值需独立回测验证，但 4 个分时硬性指标可作为打板策略的**前置筛选特征**（与 24 号 BM-SEL-22 短线评分卡 7 维互补）；8 月游资转型实证进一步确认 #1 v0.6.0 打板环境剧变结论

**2026 开源打板工具生态补充（v0.8.0）**：七轮审查发现 2026 年有多个活跃的 A 股打板/短线选股开源工具，可作为 24 号打板策略的施工参考：
- **short-term-stock-picker**（GitHub online0001, 2026-04-22，MIT 许可）：短线强势股筛选工具，6 维筛选（流通市值≤150 亿/20 日内≥1 次涨停/MA5>MA10>MA20 多头排列/换手率 0.5-10%/量比>1.0）+ 评分系统（涨停数×20+技术分+量比×5）。技术分=MA 多头 20 分+放量 1.5×15 分+放量 1.2×10 分+量价配合 10 分。**与项目对接**：评分系统可作为 24 号 BM-SEL-22 短线评分卡的对照参考（开源 MIT 可直接借鉴评分逻辑）
- **A-Share-Sector-Alpha-Hunter**（GitHub lewismessthecode, 2025-12）：板块轮动猎手，3 维度（热门板块偏离度识别"蓄势弹簧"+小盘 Bottom 20% 高弹性+历史涨停数据导出）。**与项目对接**：22 号板块轮动策略的"sector deviation 蓄势弹簧"概念可参考
- **stk_explore zhangting.py**（GitHub feiwenxiong, 2026-07-29）：涨停池工具，支持同花顺 dataapi（continuous_limit_up/limit_up_pool）+ akshare 双数据源，含近一年涨停封板率字段。**与项目对接**：双数据源（同花顺+akshare）可作为项目数据源冗余方案；"近一年涨停封板率"是打板策略的**历史封板强度特征**（与 #1 v0.7.0 当日封成比互补——历史封板率管长期，当日封成比管当日）
- **个人系统适用性**：4 个工具均为开源（MIT/无许可），akshare 已是项目数据源，可直接复用评分逻辑/筛选条件/双数据源方案。**建议**：24 号打板策略施工时参考 short-term-stock-picker 的评分系统+stk_explore 的双数据源+akshare 连板接力筛选，形成"历史封板率+当日封成比+6 维度涨停规律"三维筛选

**2026 Tail-Aware MDN——打板密度预测的"选项之外更好答案算法"（v1.0.0 补充）**：九轮审查发现 **Tail-Aware Mixture Density Network**（arxiv 2601.14049, Dumitrescu/Peignon/Thomas, Paris-Dauphine PSL, 2026-01-20；ESANN 2026 会议版扩展）是**与 A 股打板原生匹配**的密度预测算法——打板股票的"涨停→炸板"动力学正是论文研究的 **locally explosive time series**（局部爆炸性时序：上升模式后突然崩裂）：
- **locally explosive behavior = 打板动力学**——论文针对 mixed causal-noncausal ARMA 过程建模的"bubble dynamics"（气泡动力学：急剧上升→突然崩裂），与 A 股打板的"连板加速→炸板崩裂"是**同一类时序模式**。传统 causal ARMA 模型（均值回归）无法捕获这种"前向依赖"（当前值依赖未来冲击）的非线性特征，正是打板策略难以用传统时序模型预测的根因
- **skewed t-distribution 替代 Gaussian Mixture**——论文核心创新：用 skewed Student-t 分布作 MDN 混合分量，而非传统 Gaussian。**关键优势**：① Gaussian 混合的指数衰减尾部**系统性低估极端事件概率**（即炸板概率被低估）；② skewed t 同时捕获**重尾**（自由度 ν 控制尾部厚度）+ **偏态**（λ 控制不对称性）——打板收益分布是右偏（涨停上限）+ 左重尾（炸板暴跌），skewed t 原生匹配，Gaussian mixture 需 5+ 分量才能近似
- **dual reweighting + post-hoc recalibration**（ESANN 2026 版扩展）：① **dual reweighting strategy**——训练时对极端事件（炸板日）加权，解决"稀有极端事件学习不足"问题；② **post-hoc recalibration**——重加权导致的分布偏移用 local PIT modeling 事后校正。**这是 conformal 校准（91 号 Phase 0）的密度预测对应**——conformal 校准区间，PIT recalibration 校准完整密度
- **local explosive dynamics 检测**（Blasques/Koopman/Mingoli/Telg, JTSA 2025, vol 46(5):966-980）：配套的**局部爆炸性检测检验**——用 path-level deviations + growth rates 检验给定持续期/规模的气泡是否存在，分布可解析确定或数值近似。**与项目对接**：可作为打板策略的**"是否处于气泡态"前置检测器**——检测到 locally explosive dynamics 时，打板策略切换到"炸板防御模式"（缩仓+提高炸板率门槛）
- **实证**：natural gas price（2026-01 版）+ inflation（HAL 2026 版扩展）两个实证，Monte Carlo 模拟证明比现有方法优越。**关键**：训练后 MDN 产生**近瞬时密度预测**（near-instantaneous），适合日频/盘中实时推理
- **与项目对接**：① 24 号打板策略的**密度预测层**应优先评估 Tail-Aware MDN 而非 Gaussian Mixture——打板的 locally explosive 特征使 skewed t 比 Gaussian 原生匹配，**炸板概率估计精度直接决定打板策略的存活率**；② 91 号 Phase 1 LSTM+GMM 应升级为 **LSTM + skewed t MDN**（而非 Gaussian Mixture），尤其对打板相关标的；③ local explosive dynamics 检测可作为打板策略的**气泡态前置门控**（检测到气泡→进入炸板防御模式）；④ **过度工程评估**：Tail-Aware MDN 复杂度与 LSTM+GMM 相当（仅混合分量从 Gaussian 换 skewed t + dual reweighting），属"算法替换"非"新增栈"，**非过度工程**
- **与 91 号 v0.8.0 的协同**：91 号 Phase 0 conformal 给 VaR/ES 区间保证，Phase 1 LSTM+skewed t MDN 给完整密度（尤其炸板尾部），两者递进非替代——conformal 管区间覆盖，skewed t MDN 管尾部形状
- **v1.3.0 补充——Lévy 家族重尾升级（见 91 号 v1.2.0）**：当 Student-t MDN 在熔断/股灾期 VaR_99 仍超标时，91 号 v1.2.0 补 **DeepLévy**（α-stable mixture+CFM，α<2 方差无限是数学上最重尾部）作 Phase 1 极端尾部升级，与 Tail-Aware MDN（Student-t 族）形成**重尾密度预测三家族完整谱系**（Student-t / α-stable / VG-NIG）。Student-t 族是 baseline，α-stable 族是极端尾部升级，VG-NIG 族（Lévy-Flow）是 Phase 2 生成式精度替代（VaR 直接校准 Kupiec p=1.00）。**定位为升级/替代非 baseline**，Phase 1 首选仍 Tail-Aware MDN

**2026 短期趋势跟踪失效微结构账户——tick size 归一化作策略存活判据（v1.14.0 补充，20/24 号策略容量评估参考）**：三十五轮审查全网搜索发现 [arXiv:2607.01550, 2026-07-02, Kurth/Eisler/Rej/Bouchaud](https://arxiv.org/abs/2607.01550) "Is Trend Still Your Friend? A Microstructural Account of the Demise of Short-Term Trend-Following" 是与项目打板/动量趋势 sleeve 容量评估直接相关的微结构实证：
- **核心发现——短期趋势跟踪 2009 年后失效**：用~100 种流动性期货合约（1995-2025）+ CTA 代理，文档化 2009 年后短期趋势跟踪 PnL 崩塌。**区分退化与存活趋势的横截面变量是波动率归一化 tick size**——小 tick 合约趋势 PnL 崩塌而大 tick 合约保持
- **机制解释——自我实现反馈循环的断裂**：趋势跟踪通过"趋势信号→方向性交易→市场冲击→强化价格变动"的自我实现反馈循环盈利。HFT 主导做市商的流动性撤回行为在**小 tick 稀疏订单簿**上打破了此循环（小 tick 合约做市商可低成本撤单→趋势信号触发的方向性交易找不到对手盘→反馈循环断裂）
- **与项目的相关性评估**：
  - **打板策略（24 号）**：A 股打板标的通常是小盘股（流通市值≤250 亿），股价 5-30 元，tick 0.01 元，**波动率归一化 tick size 约 0.01%-0.2%**，属论文定义的"小 tick 合约"类别。但 A 股打板逻辑与期货趋势跟踪不同——打板是隔夜跳空+涨停板机制+情绪驱动，非纯趋势跟踪信号。论文的"小 tick→趋势失效"机制对打板的启示是：**量化对手盘（v0.6.0 已登记）在小 tick 稀疏订单簿上的流动性撤回行为会加剧打板策略的炸板风险**，与 24 号 §2.4 PEAD Inversion 极端反应修正协同
  - **动量趋势策略（20 号策略E）**：若项目未来实施动量趋势 sleeve，论文的"波动率归一化 tick size 作策略存活判据"可直接用作**策略容量评估的前置筛选指标**——优先选择大 tick 标的（股价≥50 元或 tick size 占比≥0.5%），避开小 tick 标的的容量陷阱
- **过度工程评估**：tick size 归一化是诊断指标非新增算法，实施成本=0（`tick_size_pct = 0.01 / close`，已有数据）。**定位为 20/24 号策略容量评估的参考诊断指标**——非 MVP 必需，Phase 2 策略扩展到动量趋势 sleeve 时作为标的筛选维度之一。**非过度工程**：是诊断指标的计算非新增架构
- **不采纳项**：论文研究的期货趋势跟踪场景与项目 A 股打板/多因子/事件驱动场景差异较大，"趋势跟踪失效"结论不直接迁移。但"tick size 归一化作存活判据"的诊断思路有借鉴价值

---

## 2. 因子分类与IC阈值（原约束二）

> 对应 G01（数据与特征层规范）｜ ✅ **v2.0.0 裁定：修订采纳（双轨阈值 + BHY FDR + ICIR≥0.5）**

**✅ v2.0.0 裁定结论**：

- **本质**：IC 门槛的真正问题是多重检验下的假阳性控制，不是绝对水平。2026 实证：A 股 |IC|>0.02 微弱有效、>0.05 优秀、ICIR>0.5 可用；qlib Alpha158 基准 RankIC≈0.04-0.05；|IC|>0.1 大概率有前视偏差。
- **裁定**：① **静态地板保留**（|RankIC|≥0.03 量价 / 0.02 基本面 / 0.025 另类）——与研究共识不冲突，作快速初筛；② **叠加相对轨道**：同类因子滚动 RankIC 分布前 50% 分位（抗 regime 漂移，替代"绝对阈值一刀切"）；③ **硬性统计门禁**：ICIR≥0.5 + BHY 控制 FDR q=10%（单批筛选 >100 因子时 t 门槛升 2.8，Harvey-Liu-Zhu 标准）；④ **5 大类入池角色保留**（量价/基本面/另类/宏观/风险），与项目 factor 域 10 类属性分类（value/quality/momentum/...）正交并存——前者管"入池角色与阈值"，后者管"因子属性标注"，映射关系待 G01/15 号对齐；⑤ 另类因子样本短，静态门槛仅辅助，以 3 个月样本外跟踪为准。
- **Alpha 因子入池流程**（闭环原待讨论问题）：IC/RankIC 回测 → BHY FDR 校正 → ICIR≥0.5 → 滚动分位前 50% → factor_pool_manager candidate 状态 → 3 个月样本外跟踪 → active。
- **施工方案**：① **BHY FDR 多重检验校正**（factor/analysis/ 新增 ~80 行，statsmodels multipletests 直接可用，Phase 2）；② 滚动分位评估嵌入 decay_monitor（Phase 2）；③ SHAP 非线性评估（远期，Phase 3+，借开源库）；④ GP 自动因子挖掘（远期探索，非 MVP）。集成点：factor_pool_manager 入池门禁（abs001_gate）。
- **过度工程审查**：BHY 是统计标准工具非新架构；SHAP/GP 均降级远期。✅ 通过。

**原始内容**：

| 因子大类 | 入池IC阈值 | 在组合中的角色 |
|---------|-----------|-------------|
| 量价因子 | \|IC\|>0.03 | Alpha来源 |
| 基本面因子 | \|IC\|>0.02 | Alpha来源+风险控制 |
| 另类因子 | \|IC\|>0.025 | Alpha补充 |
| 宏观因子 | —（不直接入池） | 市场状态判定输入 |
| 风险因子 | —（不要求IC） | 风险分解+中性化 |

**待讨论问题**：
- IC阈值（0.03/0.02/0.025）的依据是什么？需要回测验证。
- 5大类分类是否合理？是否需要增减？
- Alpha因子入池流程（IC回测+多重检验校正）的具体实现方案？

**2026 更优算法补充（v0.3.0）**：IC 仅衡量线性预测力，2026 行业标准已补充 **SHAP 特征重要性**作为非线性评估互补：
- **SHAP（SHapley Additive exPlanations）**——2026 因子评估标准（MSCI 2026-03 / mental-momentum 2026-06）：满足一致性公理，捕获非线性交互，支持全局+局部解释。MSCI 用 SHAP 解释 ML 因子跨 regime 的贡献变化（动量/残差波动率/流动性重要性随时间漂移）
- **MinShap**（arxiv 2604.15107, 2026-07）：基于 Shapley 的特征冗余检测——标准 SHAP 可能给冗余特征正归因，MinShap 用最小聚合识别"在所有条件上下文中仍相关"的非冗余特征
- **SHAP 在交易模型的注意事项**（mental-momentum 2026-06）：① 高相关金融数据导致归因稀释→需 VIF 过滤或 Group Shapley；② 随机背景数据集导致前视偏差→须严格时序滚动窗口；③ SHAP 测量统计相关非因果→易被误读为"经济叙事"
- **建议**：IC 作为快速筛选门槛（线性），SHAP 作为深度评估（非线性+regime漂移），两者互补不替代

**2026 因子发现补充（v0.5.0）**：SHAP 管因子"评估"，GP 管因子"发现"——两个维度互补：
- **遗传规划自动因子挖掘（GP）**——CSDN 2026-06：模拟进化（交叉+变异）在算子空间搜索因子表达式，适应度=IC/Sharpe。终端集=基础数据（open/close/volume/PE），函数集=数学算子（rank/ts_corr/delay）。经典 AlphaNet 用深度学习替代 GP（黑箱但捕获更复杂模式）
- **EAFD（Embedding-Aware Feature Discovery）**——arxiv 2603.15713（Sber AI Lab, 2026-03）：LLM 驱动的自反思特征生成 agent，桥接学习嵌入与可解释特征。alignment（解释嵌入已有信息）+ complementarity（发现嵌入缺失信号）双准则，比纯嵌入/纯特征基线 +5.8%
- **个人系统适用性**：GP 需要大量计算（千代进化）且易过拟合（搜索空间越大越严重），**建议先用 SHAP 评估已有因子，GP 自动挖掘列为 G01 因子工程的远期探索项**（非 MVP 必需）

**2026 因子动态加权补充（v0.7.0）**：六轮审查发现因子"合成"环节除 IC 加权/等权/回归/max_ir/min_variance 五种（25 号已 production）外，2026 有**自适应权重**的远期选项：
- **PPO 自适应 alpha 加权**——arxiv 2509.01393（University of Hyogo, 2026, Int J Data Science & Analytics）：PPO agent 实时调整 LLM 生成的 50 个 formulaic alpha 的权重，状态=市场波动率+近期收益+信号相关性，奖励=Sharpe（惩罚 MaxDD）。vs 等权/B&H/随机/动量基线，PPO 在多数情况下 Sharpe 更高+MaxDD 更小。**核心价值**：抗 alpha decay——动态重分配资本远离衰减信号，无需手动因子重校准
- **与 25 号现有五方法的分工**：IC 加权/等权/回归/max_ir/min_variance 是**静态**加权（按历史 IC/方差确定权重，周期性重校准）；PPO 是**动态**加权（实时按市场状态调整）。25 号 v1.1.0 已登记 PPO 为远期选项（与 IC 半衰期加权/GAN_GRU ML 因子/Bayesian 变点检测/Bootstrap 半衰期 CI 并列）
- **个人系统适用性**：PPO 需要 RL 训练栈（Stable Baselines3）+episode 设计+reward shaping，复杂度高于静态加权。**建议列为 25 号 Phase 2 远期演进**（IC 半衰期加权先行，PPO 作为 RL 加权的终局选项），非 MVP 必需

**2026 LLM+多智能体+PPO 三层框架补充（v0.8.0）**：七轮审查发现 PeerJ cs-3630（Asia University, 2026-03-12）提供 PPO 自适应加权的**完整工业实现参考**——三层框架（LLM 语义+多智能体+PPO 决策）是 25 号 PPO 远期选项的系统化升级路径：
- **三层架构**：① LLM 语义层（处理非结构化数据：新闻/财报/公告→因子分数）；② 多智能体协作层（5 个专业 agent 通过 Model Context Protocol 协调，生成日频因子分数）；③ PPO 决策层（4 层全连接 [40×40/128/128/3]，1600 维状态向量，3 个动作，clipped surrogate objective + 波动率调整仓位 + 交易成本感知策略更新）
- **实证结果**：5 个美股 25 年历史数据，严格时间分区防前视偏差。OOS 2024-07~2025-06（高波动期）：平均年化 **53.87%**，Sharpe **1.702**，MaxDD **12.54%**（vs B&H 26.08%/0.765/30.24%）。vs 15 个基线模型 Diebold-Mariano p<0.0001（Bonferroni 校正后）。消融研究：完整三层比最佳两组合 +15.35pp（架构协同效应真实）
- **核心价值**：三层框架把"LLM 管语义+多智能体管协作+PPO 管决策"分工明确，比单一 PPO 更鲁棒（高波动期传统方法负收益时三层框架仍正收益）。**波动率调整仓位**与项目 4 级回撤 Protocol 互补（PPO 层做连续调整，4 级 Protocol 做离散硬触发）
- **与项目对接**：① 项目 100% AI 开发，三层框架是 PPO 远期选项的系统化升级路径——LLM 语义层可复用项目已有 LLM 能力，多智能体层可复用项目已有 agent 架构，PPO 层是 25 号 v1.1.0 已登记的远期选项；② **波动率调整仓位**是 #11 动态分数 Kelly 的 PPO 实现（替代手工 regime→分数映射表）；③ **过度工程评估**：三层框架复杂度高（5 agent + PPO + LLM），属 25 号 Phase 3+ 远期终局，非 MVP 必需——MVP 先用 25 号五静态方法+IC 半衰期加权，Phase 2 评估 PPO 单层，Phase 3+ 评估三层框架

**2026 多智能体 LLM 对抗辩论 CGX 补充（v0.8.0 极新）**：七轮审查发现 2026-08-04 发布的 **CGX（Consensus-Gated Execution）**（MDPI Electronics 15:3453）是"选项之外更好的答案算法"——Bull/Bear 多智能体 LLM 三轮对抗辩论+Meta-Evaluator 共识门控执行，是 28 号情绪周期的 LLM 化远期选项：
- **CGX 架构**：Bull agent（看多论据）vs Bear agent（看空论据）三轮结构化辩论，Meta-Evaluator 综合双方论据→按共识强度门控执行。可调共识阈值平衡交易频率与信号质量
- **实证结果**：52 周聚合研究（2024）Sharpe **1.90**，MaxDD **11.6%**，3× 趋势跟踪。4 年多 regime 验证（2022-2025，417 个双周 sessions 跨熊/复苏/牛/混合）：**MaxDD 降低 85%，年化波动率降低 86%**，2022 熊市 Bear gate 阻止 93% sessions，2024 牛市仅 12%——**regime 自适应门控**
- **核心价值**：对抗辩论（adversarial debate）+ 共识门控（consensus gating）是"资本保全的原理性框架"。比单 agent LLM 决策更鲁棒（强制考虑对立观点），比纯量化 regime 检测更灵活（LLM 理解非结构化事件）
- **与项目对接**：① 28 号情绪周期 4+1 阶段（冰点/反核/主升/疯狂/退潮）的 LLM 化远期选项——Bull/Bear 辩论可替代或补充情绪周期的阶段判定（情绪周期管"是什么阶段"，CGX 管"这个阶段该不该交易"）；② CGX 的"共识阈值门控"与 34 号 RegimeMetaAllocator 的 Shrinkage 互补——Shrinkage 管"减多少仓"，CGX 管"该不该开仓"；③ **过度工程评估**：多智能体 LLM 辩论复杂度高（3+ LLM agent + 辩论编排 + Meta-Evaluator），属 28 号 Phase 4+ 远期愿景，非 MVP 必需——MVP 先用情绪周期 4+1 阶段+regime Shrinkage，Phase 4+ 评估 CGX 作为 LLM 化决策层

**2026 多智能体 LLM 细化研究补充（v0.9.0 极新）**：八轮审查发现 CGX 之后 2026 有三篇关键研究**细化多智能体 LLM 交易的设计要点**，是 CGX 远期选项的工程化补充：
- **F²Agent 多模态融合**（arxiv 2608.05668, NUS 新加坡国立大学, 2026-08-06 极新）：CGX 是"单模态（文本/价格）+对抗辩论"，F²Agent 是"**多模态+自适应融合**"——部署专业化 agent 层级提取模态特定信号（新闻/基本面/技术/宏观），引入 **modality-aware adaptive fusion mechanism + noise-robust consistency regularization** 动态捕获跨模态依赖、生成抗噪交易信号。**实证**：6 股票+加密资产，平均年化收益相对提升 **20%+**，GOOG 120.48%/TSLA 148.41%，超 16 个基线。**核心价值**：比 CGX 多了"模态融合"维度——CGX 假设 agent 看相同信息辩论，F²Agent 显式建模不同模态信号的依赖结构+噪声鲁棒性
- **市场依赖通信**（arxiv 2511.13614, CMU Carnegie Mellon, 2025-11，450 实验×21 个月）：5-agent LLM 交易系统比较 5 种组织结构（隔离基线→协作对话→竞争对话）。**关键发现**：通信改善性能，但**最优通信设计依赖市场特征**——① **竞争式对话**（adversarial）在高波动科技股占优；② **协作式对话**（collaborative）在稳定通用股占优；③ **金融股抵抗所有通信干预**（金融股信息已高效，多 agent 通信无增量）。**意外发现**：所有结构（含隔离 agent）收敛到相似策略对齐——透明性不必然导致有害多样性损失；性能差异源于**行为机制**（竞争 agent 聚焦个股配置，协作 agent 发展技术框架）；**对话质量评分与收益零相关**（ sophisticated discussion ≠ better performance）
- **MarketSenseAI 自适应集成**（arxiv 2604.17327, Alpha Tensor, 2026-04，19 个月 S&P 500 实证）：4 specialist agent（News/Fundamentals/Dynamics/Macro）+ synthesis agent。strong-buy 等权组合 +2.18%/月 vs 被动基准 +1.15%，Monte Carlo null p=0.003，**ICIR +0.489 (p=0.024)**。**关键发现**：NNLS 归因揭示 **adaptive-integration mechanism 而非 dominant-agent effect**——agent 贡献随 regime 轮换（S&P 500 Fundamentals 主导，S&P 100 Macro 主导，Dynamics 作偶发动量信号），agent 轮换与 strong-buy 选择的行业构成+宏观日历事件同步移动
- **三研究的共同启示**：① 多智能体 LLM 交易的**关键不是"多 agent"而是"通信/融合设计"**——F²Agent 管模态融合，市场依赖通信管对话结构（竞争 vs 协作），MarketSenseAI 管归因机制（自适应集成 vs 主导 agent）；② **金融股/高效率市场对多 agent 通信无增量**——项目 A 股小盘题材股（低效市场）是多 agent LLM 交易的更适合场景；③ **对话质量 ≠ 收益**——不能只看 agent 讨论多 sophisticated，要看是否改善配置决策
- **与项目对接**：① F²Agent 的多模态融合是 28 号情绪周期 LLM 化的**进一步演进**——情绪周期当前用量化指标（炸板率/连板高度），F²Agent 可引入新闻情绪+基本面+技术+宏观的多模态 agent；② 市场依赖通信的"竞争 vs 协作依市场特征"启示——项目打板策略（高波动题材股）适用竞争式辩论，多因子策略（稳定股）适用协作式；③ MarketSenseAI 的"agent 贡献随 regime 轮换"与项目 regime 检测器原生对接——regime 状态→agent 权重映射（r3 牛市 Fundamentals 主导，r4 熊市 Macro 主导）；④ **过度工程评估**：三研究均属 28 号 Phase 4+ 远期愿景，非 MVP 必需——MVP 先用情绪周期 4+1 阶段，Phase 4+ 评估 F²Agent 多模态融合+市场依赖通信设计+MarketSenseAI 自适应集成

**2026 截面异质性 LSTM 补充（v1.4.0 极新）**：十三轮审查发现 2026-08-06 发布的 **Cross-Sectional Heterogeneity LSTM**（arxiv 2608.05755, Döbelt）是"选项之外更好的答案算法"——标准 LSTM 忽略截面异质性（不同板块动力学不同），Cross-Sectional LSTM 用 **learnable sector embeddings + 宏观协变量 + label smoothing/dropout/gradient clipping 正则**捕获截面资产动力学：
- **核心方法**：① 在 LSTM 输入端拼接 learnable sector embeddings（每个板块一个低维向量，端到端学习板块特异性动力学）；② 引入宏观经济协变量（利率/通胀/汇率等）作额外输入维度；③ 正则化栈：label smoothing（防过拟合硬标签）+ dropout + gradient clipping。S&P 500 long-short 组合实证超 basic LSTM/RF/buy-and-hold，可解释 sector contribution metric
- **与 25 号多因子策略的对接**：① 25 号现用 IC 加权/等权/回归/max_ir/min_variance 五静态方法合成因子，**截面异质性是合成前的输入端增强**——sector embeddings 让模型"知道"某因子在电子板块 vs 消费板块的有效性不同；② 25 号 v1.1.0 已登记"行业轮动信号"作 alpha 来源之一，Cross-Sectional LSTM 是其神经网络化实现（替代手工行业哑变量）；③ **实证规模**：S&P 500 long-short 是成熟市场大盘，A 股小盘题材股截面异质性更强（板块效应显著），预期增益更大
- **与 22 号板块轮动的对接**：① 22 号现用板块动量+相对强度，Cross-Sectional LSTM 的 sector embeddings 可直接输出"板块相对强弱"的向量表示，比手工动量指标更丰富；② sector contribution metric 提供板块归因（哪个板块贡献了收益），与 22 号的板块轮动判定闭环
- **与 91 号 v1.3.0 的交叉引用**：Cross-Sectional LSTM 已纳入 91 号 Phase 1.5+ 截面特征增强（详见 91 号 v1.3.0 实现路径表），本节补充其与 22/25 号的具体对接路径
- **过度工程评估**：sector embeddings + 宏观协变量是输入端增强非新增架构（LSTM 主体不变），实现增量小（~50 行 embedding 层 + 协变量拼接）。**定位为 22/25 号 Phase 1.5+ 截面增强**，非 MVP 必需——MVP 先用 25 号五静态方法+手工行业哑变量，Phase 1.5+ 评估 Cross-Sectional LSTM 作输入端升级

**2026 Body-Tail 因子分解检验+Robust Spatial-Sign 重尾因子检验（v1.11.0 补充，因子评估方法学增强）**：二十一轮审查全网搜索发现 2 项因子评估方法学的未登记新研究，与 SHAP/IC 互补：
- **Body-Tail Factor Test**（[arXiv:2606.23596, Shin, Sogang University, 2026-06-26 v3](https://arxiv.org/abs/2606.23596)）——将因子收益分解为 body（中心部分）+ tail（尾部部分），recombination identity 对每个因子模型成立。**关键发现**：q5 因子虽然 spanning 最强但 **body alpha 为负、tail alpha 为正**——Sharpe 与 pricing error 可分离，传统单一 IC/Sharpe 评估会掩盖"因子在正常波动 vs 极端波动下表现分化"。**项目对接**：25 号因子评估当前用 IC（线性）+ SHAP（非线性），Body-Tail Test 提供**第三维度——body/tail 分解**：A 股涨跌停使 tail alpha 与 body alpha 差异显著（涨停日 tail 主导、非涨停日 body 主导），IC 可能被 tail 主导而 body 无信号。**部分采纳**：纯统计检验实施成本低（~50 行），定位为 25 号 Phase 2 因子评估增强——对每个候选因子同时报告 body IC + tail IC + total IC，淘汰"total IC 正但 body IC 负"的伪信号因子
- **Robust Spatial-Sign Conditional Alpha**（[arXiv:2604.12252, Zhao/Wang, 2026-04-14](https://arxiv.org/abs/2604.12252)）——条件因子模型的 spatial-sign max-type + sum-type Cauchy 组合检验，渐近独立。**核心优势**：适用于**重尾+时变系数+高维 N>T** 场景，优于 GRS 检验与 sub-Gaussian 假设方法。**项目对接**：25 号因子评估当前用 IC 的 t 检验（假设近似正态），A 股收益重尾（涨跌停/缺口）使 t 检验失效——Spatial-Sign 检验是**重尾鲁棒的因子显著性检验**，与 Body-Tail Test 互补（Body-Tail 管 body/tail 分解，Spatial-Sign 管重尾鲁棒性）。**部分采纳**：纯统计检验实施成本低（~60 行），定位为 25 号 Phase 2 因子显著性检验升级——替代 IC t 检验作重尾场景的默认检验

**2026 Uncertainty-Adjusted Sorting——不确定性调整排序替代点预测排序（v1.12.0 补充，25 号 Phase 4 ML 组合构建增强）**：三十二轮审查全网搜索发现 [arXiv:2601.00593, 2026-01](https://arxiv.org/abs/2601.00593) "Uncertainty-Adjusted Sorting for Asset Pricing with Machine Learning" 是"选项之外更好的答案算法"——直接对应 25 号 Phase 4 ML 合成引入后的**组合构建排序**环节：
- **核心方法**：ML 资产定价的 portfolio construction 普遍用点预测（point prediction）排序选股，但点预测忽略资产级估计不确定性（asset-specific estimation uncertainty）。本文提出简单改动——用**不确定性调整预测区间**（uncertainty-adjusted prediction bounds）替代点预测排序。跨多种 ML 模型+美国股票面板，此方法相对点预测排序改善组合表现
- **关键发现**：① 增益主要来自**波动率降低**（非收益提升）——不确定性调整使组合避开高不确定性股票，降波动；② 增益在**灵活 ML 模型上最强**（模型越灵活，不确定性估计越有价值）；③ 增益即使区间由**部分或错误设定的不确定性信息**构建仍持续（鲁棒）；④ 增益由**资产级不确定性**驱动，非时间级或总体预测不确定性
- **与 25 号 Phase 4 ML 合成栈的层次互补**：25 号已登记 ML 合成三件套——① LambdaRankIC（v1.6.0）管**训练目标**（MSE→Rank IC）；② RankGLU（v1.7.0）管**预测头架构**（线性→GLU 门控）；③ **Uncertainty-Adjusted Sorting（本项）管组合构建排序**（点预测→不确定性调整区间）。三者正交：LambdaRankIC 优化模型怎么训练，RankGLU 优化模型怎么输出，Uncertainty-Adjusted Sorting 优化输出怎么用——"训练→输出→排序"完整 ML 合成流水线各自独立增强
- **A 股适配**：A 股涨跌停/停牌/缺口使单股收益不确定性估计天然偏高，Uncertainty-Adjusted Sorting 自动降权高不确定性股票（如涨停股次日不确定性高→降权），与 25 号 v1.5.0 Mask-First 可交易性掩码协同——掩码过滤不可交易股，不确定性调整降权高不确定股，两层防御
- **过度工程评估**：不确定性调整排序是排序逻辑的简单改动（点预测→预测区间下界/加权），实施成本低（~30 行：预测区间计算+排序键替换）。**定位为 25 号 Phase 4 ML 合成引入后的组合构建增强**——MVP 先用 IC 加权线性合成（无 ML 模型→无不确定性估计→不适用），Phase 4 ML 合成引入后（有模型预测+不确定性估计）启用 Uncertainty-Adjusted Sorting 替代点预测排序。**非过度工程**：是 ML 合成的"标配排序逻辑"，非新增架构

**2026 财信三维情绪模型"情绪浓度"维度——行业联动度作情绪周期第三维（v1.13.0 补充，28 号 Phase 2 远期候选）**：三十四轮审查中文来源搜索发现 [财信证券 2026-08-10 三维情绪模型跟踪周报](http://m.microbell.com/wap_detail.aspx?id=af811c52426cdd2d4a3fb234e46cf9d5)（刘飞彤，S0530522070001）提供 28 号情绪周期未覆盖的第三维度——"情绪浓度"：
- **三维模型架构**：① 情绪温度（主力买入率，中频~31 天周期）+ ② 情绪预期（期货升贴水+期权 PCR 合成，中高频~16 天周期）+ ③ **情绪浓度（中信三级行业第一主成分方差贡献率，低频~30 天周期）**。高浓度→Beta 行情（系统性同涨跌），低浓度→Alpha 分化机会；浓度超警戒线 0.83 并形成顶部预示市场拐点
- **情绪浓度算法**：对中信三级行业体系指数收益率矩阵做 PCA，第一主成分方差贡献率=情绪浓度。此值越高代表全市场资产相关性越高（资金共识强但同质化风险累积），超过 0.83 警戒线=牛熊转折预警
- **与 28 号现有 5 阶段的互补性**：28 号 v1.10.0 已有情绪温度（炸板率/连板高度/封板率→冰点/反核/主升/疯狂/退潮 5 阶段）+ BOCPD/CUSUM 四法对比，**但无"行业联动度"维度**。情绪浓度提供独立第三维——衡量"资金是集中共识（高浓度 Beta 行情）还是分散分化（低浓度 Alpha 机会）"，与 22 号虹吸态识别（少数板块吸金）正交互补：虹吸态管"资金往哪去"，情绪浓度管"资金是否共识"
- **A 股适配性评估**：① **情绪温度维度**（主力买入率）与 28 号已有的炸板率/连板高度/封板率重叠，不整合；② **情绪预期维度**（期货升贴水+期权 PCR）**不适用**——项目是 A 股 miniQMT 个人系统，无股指期货/ETF 期权数据接入；③ **情绪浓度维度**（行业 PCA 第一主成分）**可整合**——项目已有 `sector_snapshot` 表（582 只 880xxx/881xxx 板块指数，production），可直接做 PCA 计算第一主成分方差贡献率
- **HMM 模式转移规律**（财信 2025-03 专题报告）：情绪模式四象限（温度升/降 × 预期升/降）的 HMM 转移矩阵——"温度↓预期↓"最可能→"温度↓预期↑"（情绪修复渐进性），"温度↑预期↑"最可能→"温度↓预期↑"（全面向好难持续）。与 28 号 §3.2 不可跳跃约束（阶段逐级转移）同构
- **过度工程评估**：情绪浓度计算是标准 PCA（numpy.linalg.svd ~20 行），数据源已具备（sector_snapshot）。**定位为 28 号 Phase 2 远期候选**——MVP 先用 5 阶段情绪周期（production），Phase 2 评估情绪浓度作"市场拐点预警"第三维（浓度>0.83 触发退潮预警，领先 28 号评分降级 1-2 日）。**非过度工程**：是情绪周期的维度扩展非新增架构，与 22 号虹吸态识别共享 sector_snapshot 数据源

**2026 IGF BBP 相变因子数检测——RMT 因子数检测层增强（v1.14.0 补充，15 号 Phase 2+ 因子数检测增强）**：三十五轮审查全网搜索发现 [arXiv:2607.06908, 2026-07-08, García-Medina](https://arxiv.org/abs/2607.06908) "Iterative Detection of Global Factors Near the BBP Phase Transition" 是"选项之外更好的答案算法"——直接对应 15 号 v1.19.0 RMT 去噪因子权重的**检测层**增强：
- **核心方法——Iterative Global Factor (IGF) 算法**：结合自适应 Marčenko-Pastur 边缘重校准 + participation-ratio 去局域化滤波器。在 BBP 相变附近（弱因子可能与 Marčenko-Pastur 谱边缘波动混淆时），仅靠特征值准则可能失败/模糊，IGF 通过**同时检查谱分离和特征向量延展性**恢复真实因子数
- **实证基础**：S&P 500 收益，IGF 检测到比 Onatski 检验更丰富动态的全局因子（中位数 7 个）
- **与 15 号 v1.19.0 RMT 去噪因子权重的层次互补**：15 号 v1.19.0 已整合 RMT 去噪因子权重（arXiv:2606.28540 Belzile 综述引用），是**权重层**——对已确定的因子做去噪加权。IGF 是**检测层**——在权重层之前确定"有多少个真实因子"。两者正交互补：IGF 管"有多少因子"，RMT 去噪管"这些因子怎么加权"，"检测→加权"流水线各自独立增强
- **A 股适配**：A 股因子截面（量价/基本面/另类）的相关矩阵在 BBP 相变附近可能有弱因子被噪声谱边缘淹没，IGF 的 participation-ratio 去局域化滤波器可恢复这些弱因子。3-5 策略规模下因子数检测需求不高（通常 5-15 个因子），但因子池扩展到 20+ 时 IGF 的检测精度优势显现
- **过度工程评估**：IGF 实施成本中等（~80 行：MP 边缘重校准 + participation-ratio 计算 + 迭代滤波），是 RMT 家族检测层的标准工具。**定位为 15 号 Phase 2+ 因子数检测增强**——MVP 先用固定因子数（IC 筛选阈值确定），Phase 2+ 因子池扩展到 20+ 时启用 IGF 替代固定因子数假设。**非过度工程**：是 RMT 去噪权重层的检测层补充非新增架构，与 15 号 v1.19.0 形成"检测→加权"完整 RMT 流水线

**2026 量化"双杀"压力测试——因子拥挤度监控的实证背书（v1.6.0 补充，对应文档 v1.17.0）**：2026-07 A 股量化"双杀"压力测试提供因子拥挤度监控的实证背书：
- **核心数据**：2026-07 沪深300 指增平均超额 **-1.51%**、中证500 指增 **-4.54%**；动量因子单月回撤超 **20 个百分点**（十年罕见）。机制：因子拥挤（crowding）→ 同质化量化策略集中平仓 → 多杀多 → 因子短期崩溃
- **与项目对接**：对应 #2 因子工程。印证**因子拥挤度监控的必要性**——因子不是越多越好，拥挤因子在压力期会同时崩溃放大回撤。需在因子监控模块增加拥挤度指标：
  - **因子拥挤度指标**（measuring factor crowding）：① 因子收益相关性（拥挤因子间相关性趋 1）；② 因子持仓位集中度（top-N 持仓重叠率）；③ 因子周转率（拥挤因子换手趋同）；④ 外部信号（如北向资金集中度、龙虎榜机构抱团度）
  - **与 32 号 correlation_dedup 的层次互补**：32 号管**策略间**相关性去重（P-90 相关性剔除），因子拥挤度管**因子间**拥挤度监控——策略间去重是事后（已合成），因子间拥挤是事前（入池前筛）
- **定位**：需在 25 号多因子策略的因子监控模块增加拥挤度指标。Phase 2 候选（MVP 先用 IC+SHAP 筛选，Phase 2 引入拥挤度监控），非 MVP 必需

---

## 3. 组合构建硬约束（原约束三）

> 对应 G12（仓位算法spec）｜ ✅ **已裁定（2026-08-05，30_multi_strategy；v2.0.0 锚点更新至 v2.5.0）**

**原始内容**：

| 层次 | 选择 | 核心规则 |
|------|------|---------|
| 信号→仓位 | 风险预算(Risk Budgeting) | 不可使用等权或固定比例 |
| 仓位上限 | 市场状态驱动动态调整 | ①②80%→⑨10%共9档+2叠加态；市场状态仓位上限为硬上限，风险预算不可超过 |
| 再平衡 | 日频信号驱动+周频强制再平衡 | 每周五收盘后强制再平衡 |
| 集中度 | 行业偏离≤基准±10%（⑪时±15%，绝对上限30%）；风格暴露≤±0.3标准差 | 条件性硬约束+风格中性化 |

**✅ 裁定结论**：30_multi_strategy_concurrency §2.1 已定 **Model A（独立账本 + firm 风险聚合）**，分层裁定如下（v2.0.0 注：30 号已演进至 v2.5.0——firm 层 Kelly 升级为三档演进：Phase 1 Fractional Kelly 25-50%、Phase 2 Bayesian Kelly、Phase 3 远期 Conformal Kelly；PerformanceScore 口径 Sharpe→Sortino；具体 fraction 待 31 号 G12 标定）：
- **策略层（StrategyBook）**：risk parity / 等权（**不用 Kelly，不用 MVO**）——"风险预算"方案被 risk parity 替代
- **组合层（MOD-POS-021 FirmRiskAggregator）**：Kelly 精裁决 + 求和 + 硬上限裁剪（**不做 MVO，不做协方差估计**）【v2.0.0 修正：原稿误标 MOD-POS-001——MOD-POS-001=position_sizing_engine，FirmRiskAggregator=MOD-POS-021，见 30 号 §7.2】
- **meta 层（RegimeMetaAllocator）**：regime 灰度概率→Shrinkage 风险节流（**仅节流不重定向**），budget 公式 = normalize(Base × PerformanceScore × Shrinkage)
- **市场状态→仓位**：不通过"9档+2叠加态硬映射"，而是 Shrinkage 置信度→风险节流映射（max(P)<60%→Shrinkage 0.3 … >95%→1.0）
- **再平衡**：budget 变动三级升级（Tier1 封锁→Tier2 自平衡→Tier3 强裁），非固定周频

**2026 行业实证**：
- Columbia University arxiv 2412.12350（2024-12）：多因子市场中性策略对比 equal-weight / risk parity / min-variance，**risk parity 胜出**（更高 Sharpe、更低 beta、更小 MaxDD）
- ersantana.com（2026-03）：risk parity = equal risk contribution，比 Markowitz 更稳定、对收益预测不敏感，是 2026 主流组合构建方法
- Morwane/multi-strategy-alpha-book（30_multi_strategy §7.4 核心实证）：risk-parity 基准 Sharpe +1.43，regime 做风险节流后 MaxDD 从 −14.2% 缩至 −10.3%，Calmar +38%

**2026 HRP 更优算法补充（v0.8.0）**：七轮审查发现 naive risk parity（inverse-vol）之外，**Hierarchical Risk Parity（HRP, López de Prado）** 是 2026 更优的 risk parity 变体，可作为 30_multi_strategy StrategyBook risk parity 的进阶选项：
- **naive risk parity 局限**（vzeman 2026-05 systematic_equity_trading_research）：`weight_i = (1/vol_i) / Σ(1/vol_j)` 仅按个体波动率反比分配，**忽略策略间相关性**——两个高相关策略会获得合计过高的风险预算
- **HRP 方法**（López de Prado）：先用相关性矩阵做**层次聚类**（hierarchical clustering）将策略分组（相关高的聚一类），再在聚类树层级内**自顶向下分配风险**。相关性高的策略组共享一个风险预算，组内再按 inverse-vol 细分。**优势**：无需协方差矩阵求逆（数值稳定），对相关性结构变化更鲁棒，避免 Markowitz 的 corner solutions
- **实证**（vzeman 2026-05）：HRP 在相关性结构突变时（如危机期相关性飙升）比 naive risk parity 和 min-variance 更稳定，MaxDD 更小。dananalytics 2026-03-26 三原则（Individual Edge + Low Correlation + Combined Risk Limits）中"Low Correlation"的工程实现就是 HRP
- **与项目对接**：30_multi_strategy StrategyBook risk parity 当前为 inverse-vol（naive），可升级为 HRP 作为 Phase 2 演进——① 复用 23 号策略相关性文档的 PnL 相关性矩阵作聚类输入；② 聚类层级=策略族（动量/因子/事件驱动），族内 inverse-vol，族间按聚类距离分配；③ 与 34 号 RegimeMetaAllocator 的 Shrinkage 正交（HRP 管策略间静态风险分配，Shrinkage 管 regime 动态风险节流）。**待 G12 细化**：HRP 聚类阈值与重平衡频率

**2026 Wasserstein DRO 组合——"Wasserstein 家族"补齐组合层（v1.0.0 补充）**：九轮审查发现 **Certified High-Dimensional Wasserstein Robust Portfolio Optimization**（arxiv 2608.07032, Hsieh & Gan, 2026-08-07 极新）与 v0.9.0 #7 Wasserstein HMM（regime 层）形成 **"Wasserstein 家族"三件套**——regime 层（Wasserstein HMM）+ 组合层（Wasserstein DRO）+ 仓位层（Wasserstein-Kelly）统一用 Wasserstein 距离作鲁棒性度量：
- **Wasserstein DRO 组合核心方法**——以经验分布为中心、Wasserstein 距离为半径的"分布模糊集"（ambiguity ball）内做 worst-case 期望效用最大化。① order-1 Wasserstein 模糊下，长期-only + box support + one-norm ground metric 时，对偶化得到**多项式规模线性规划**（可扩展到 1000 资产）；② supporting hyperplanes majorize 效用函数，uniform utility-approximation error 同时 bound robust-value error 和 near-optimality gap；③ 实证：月频 476 资产再平衡，可扩展到 1000 资产
- **为什么是"选项之外更好的答案算法"**——项目当前组合层（30_multi_strategy §2.1）用 risk parity（静态）+ Kelly（动态），**未显式建模"收益分布本身的不确定性"**。Wasserstein DRO 显式建模分布不确定性（ambiguity ball 半径 δ 反映投资者对经验分布的可信度），是 risk parity 的**鲁棒性增强层**：① δ→0 退化为经验分布（无鲁棒性）；② δ→∞ 过度保守；③ δ 适中在"数据驱动"与"鲁棒性"间平衡。与 HRP（管相关性结构）、Kelly（管仓位缩放）正交——Wasserstein DRO 管**分布不确定性**
- **Shift-Aware Wasserstein-DRO CVaR**（arxiv 2512.16748, Long, Columbia, NeurIPS 2025 Workshop）：配套的**分布漂移感知**校准——用 Gaussian-supremum validation + block multiplier bootstrap 在时序依赖下选择 Wasserstein 半径 δ，保证 CVaR 约束在分布漂移下仍可行。**与项目对接**：A 股 regime 切换频繁（政策市），shift-aware δ 校准是 Wasserstein DRO 在 A 股落地的关键——固定 δ 会要么过保守（牛市）要么不达标（熊市）
- **Wasserstein-Kelly**（JUSTC 2025, 55(8):0805, Sun & Zou, USTC）：用 coherent Wasserstein metric 做 Kelly 组合优化的分布鲁棒版，凸规划可解，在控制波动率和 MaxDD 上优于经典 Kelly。**与项目对接**：项目 firm 层 Kelly 精裁决（30_multi_strategy §2.1）的远期鲁棒化选项——经典 Kelly 假设收益分布已知，Wasserstein-Kelly 显式建模分布不确定性
- **"Wasserstein 家族"三件套与项目分层对应**：
  | 层 | 模块 | Wasserstein 方法 | 解决的问题 | 已登记版本 |
  |---|---|---|---|---|
  | **regime 层** | 10 号 regime 检测器 | Wasserstein HMM（template tracking） | regime 标签漂移（A2 FAIL） | v0.9.0 #7 |
  | **组合层** | 30 号 StrategyBook risk parity | Wasserstein DRO 组合 | 收益分布不确定性 | **v1.0.0 #3（本节）** |
  | **仓位层** | 30 号 FirmRiskAggregator Kelly | Wasserstein-Kelly | Kelly 分布鲁棒化 | **v1.0.0 #3（本节）** |
- **过度工程评估**：Wasserstein DRO 复杂度中等（线性规划可解，1000 资产可扩展），但**项目当前 risk parity + Kelly 已覆盖核心需求**，Wasserstein DRO 是"鲁棒性增强"非"必需修复"。**建议**：列为 30 号 StrategyBook risk parity 的 Phase 3+ 远期演进（naive risk parity → HRP → Wasserstein DRO 三级递进），非 MVP 必需。Wasserstein-Kelly 同列为 firm 层 Kelly 的远期鲁棒化选项。**关键告诫**：Wasserstein DRO 的 δ 选择是"delicate"（arxiv 2512.16748 原文）——δ 太小危险（分布漂移下违反约束），δ 太大杀性能，必须配套 shift-aware 校准

**2026 Wasserstein 生成式数据建模——Wasserstein 家族的生成式扩展（v1.1.0 补充）**：十轮审查发现 **Wasserstein Generative Data Modeling for Robust Portfolio Optimization**（Huang et al., preprints.org 2026-02-28）将 Wasserstein DRO 与 **Wasserstein GAN** 结合，是"Wasserstein 家族"的**生成式扩展**——用 GAN 重建资产收益的潜在分布，捕获非高斯特征和尾部依赖，再在 Wasserstein 模糊集内做鲁棒优化：
- **核心方法**：① WGAN 重构资产收益潜在分布（捕获非高斯特征+尾部依赖，超越 Certified Wasserstein DRO 的经验分布假设）；② Wasserstein 距离构造不确定性集，在分布扰动下动态平衡经验风险最小化与鲁棒性；③ 双优化机制交替更新生成参数和优化参数，自适应对齐变化的市场结构
- **实证**：多资产数据集上 Sharpe 更高+MaxDD 更低+鲁棒性更强（vs RL-based 和 mean-variance 基线）
- **与 Certified Wasserstein DRO 的分工**：Certified DRO（arxiv 2608.07032）用经验分布+多项式 LP（轻量可扩展）；Wasserstein 生成式用 GAN 重建分布（更表达尾部依赖但训练更重）。**定位**：Certified DRO 是 Phase 3+ 首选（LP 可解），Wasserstein 生成式是 Phase 4+ 选项（需 GAN 训练栈，但捕获非高斯尾部依赖更强，与 91 号 Phase 2 GPD/TailGAN 路径协同）
- **与项目对接**：① 30 号 risk parity 的远期三级递进可扩为四级：naive risk parity → HRP → Certified Wasserstein DRO → Wasserstein 生成式（v1.1.0 补充第四级，非 MVP 必需）；② Wasserstein 生成式与 91 号 Phase 2 GPD（GAN 生成式预测分布）共享 GAN 栈，可协同设计；③ ⚠️ 此文为 preprint（未经同行评审），需独立验证后采用
- **过度工程评估**：Wasserstein 生成式需 WGAN 训练栈+双优化机制，复杂度高于 Certified DRO。**建议**：列为 Phase 4+ 远期探索（Certified DRO 先行），非 MVP 必需

**2026 MFCCA 多重分形组合分配——选项之外更好的答案算法（v1.3.0 补充）**：十二轮审查发现 **Portfolio Allocation under Heterogeneous Scales and Multifractality**（arxiv 2608.04987, Kakinaka & Umeno, 2026-08 极新）提出基于**多重分形互相关分析（MFCCA）**的组合分配模型，是 mean-variance 的**多重分形扩展**——
- **核心方法**：风险泛函定义为 MFCCA 的**带符号波动函数**（signed fluctuation function），由尺度 s 和波动阶 q 索引。与 MFDCCA 类（先去趋势协方差再聚合）不同，MFCCA **保留符号**——同向运动（co-moving）与反向运动（counter-moving）以相反符号贡献风险。**关键**：q=2 时该二次型退化为组合序列本身的去趋势波动函数，**mean-variance 准则成为其尺度依赖极限**
- **实证**：金融多资产应用中，MFCCA 准则在每个要求收益水平上，样本内外均**降低 drawdown/VaR/ES**（vs mean-variance 基准），且**不损失实现组合收益**。**符号保持比波动阶聚合对尾部风险降低贡献更大**——即"区分同向/反向"比"聚合不同幅度"更重要
- **为什么是"选项之外更好的答案"**——项目组合层（30_multi_strategy §2.1）用 risk parity + Kelly，**未建模资产间的多重分形互相关结构**（即相关性随时间尺度 s 和波动幅度 q 变化的异质性）。A 股多策略场景（打板+多因子+事件驱动）的策略间相关性正是多重分形的（政策市 regime 切换使策略间相关性的尺度结构异质），MFCCA 是 risk parity/HRP 之外的多重分形维度补充
- **与项目对接**：① 30 号 risk parity 的远期递进可扩为五级：naive risk parity → HRP → Certified Wasserstein DRO → Wasserstein 生成式 → **MFCCA 多重分形**（v1.3.0 补充第五级，非 MVP 必需）；② MFCCA 的"符号保持"特性（同向 vs 反向运动）对接项目策略相关性监控（23_strategy_correlation_validation）——传统 Pearson 相关性只看幅度不看方向结构，MFCCA 补充方向维度；③ **过度工程评估**：MFCCA 需估计多重分形谱+带符号波动函数，复杂度高于 HRP 但低于 Wasserstein DRO，列为 Phase 4+ 远期探索，非 MVP 必需

**2026 TRP 拓扑风险平价——HRP 的多空+信号增强变体（v1.5.0 极新补充）**：十四轮审查发现 **Topological Risk Parity（TRP, arxiv 2604.16773, Nayar/Ainasse/Kulkarni, FMI Technologies, 2026-04-18）** 是"选项之外更好的答案算法"——直击 HRP 的两大局限（**不支持多空+忽略 alpha 信号**），是 HRP 的原生增强非全新架构：
- **HRP 的两大局限**：① **仅 long-only**——HRP 递归二分+逆方差分配只能产生非负权重，无法直接用于 long/short 或 market-neutral 组合（项目 25 号多因子策略的 long-short 组合需额外中性化处理）；② **纯风险分配忽略信号**——HRP 不接收任何 alpha 信号输入，仅按相关性结构分配风险预算，辛辛苦苦生成的多因子 alpha 被 HRP 完全忽略
- **TRP 核心方法**——从相关性-距离图提取**稀疏有根拓扑**（rooted MST），用**传播法则**将带符号信号映射为组合权重：① **Activity Filter** 选活跃资产集 A（平均绝对收益 m_i > ε 且信号 |s_i| > τ）；② **Mantegna 距离** D_ij = √((1-ρ_ij)/2) 构建 MST 稀疏骨干；③ **Mixed Split-Replication Coefficient** α_u(ρ) = (1-ρ) + ρ/b(u)（ρ∈[0,1] 控制信号传播，b(u)=分支数）；④ **拓扑因子** g_v = ∏ α_u(ρ)（根到 v 路径上所有祖先 α 的乘积）；⑤ **最终权重** w_v = L × (s_v × g_v) / ||x||₁（L1 归一化到目标杠杆 L）
- **两种变体**：① **Rooted MST Allocator**（变体 I）——纯数据驱动，根节点选最大度/最大信号/指定指数；② **Semi-Supervised TRP**（变体 II）——**强制经济先验层级**：市场根（SPY 哑节点）→ 行业 ETF（第二层）→ 个股，用 DFS 从根提取有根生成树。**变体 II 直接对接项目 22 号板块轮动**——用 IF/IC 作市场根，申万一级/二级行业指数作第二层，个股作叶子节点
- **关键参数 ρ 的两极行为**：ρ=0 时 α_u=1，退化为**纯信号归一化分配**（无拓扑影响，w_v = L×s_v/||s||₁）；ρ=1 时 α_u=1/b(u)，退化为**保守等分**（信号沿树等分到子节点）。ρ∈(0,1) 在"信号保留"与"拓扑正则化"间平衡——ρ 越大越保守（类似 HRP 的风险均衡），ρ 越小越激进（类似纯信号驱动）
- **vs HRP 的本质区别**：① TRP **保留信号方向**（w_v = s_v × g_v，正信号→多头，负信号→空头），HRP 丢弃信号方向（纯逆方差分配）；② TRP **非保守传播**——分支节点处信号不完全传给子节点（α_u < 1 当 ρ>0），允许层级结构塑造暴露同时保留特质仓位，HRP 在每次二分时保守传播全部权重；③ TRP 的**稀疏 MST 骨干**（n-1 条边）比 HRP 的稠密聚类树对噪声更鲁棒
- **与项目对接**：① 30 号 StrategyBook risk parity 当前为 inverse-vol（naive），HRP 是 Phase 2 演进——**TRP 是 HRP 的多空+信号增强替代**，当 25 号多因子策略需要 long-short 组合时，TRP 比 HRP 更原生（HRP 需额外中性化，TRP 原生支持多空）；② **Semi-Supervised TRP 变体 II** 的"市场根→行业 ETF→个股"层级直接对接 22 号板块轮动的行业结构（申万一级 28 个行业指数作第二层）；③ TRP 的"拓扑因子 g_v"与 34 号 RegimeMetaAllocator 的 Shrinkage 正交——TRP 管策略间静态拓扑风险分配，Shrinkage 管 regime 动态风险节流；④ **ρ 参数对接 regime**——可设计 regime→ρ 映射（r3 牛市 ρ 低=信号驱动，r4 熊市 ρ 高=保守等分），是 34 号 Shrinkage 的拓扑维度补充
- **过度工程评估**：TRP 的 MST 构建+传播法则实现成本中等（~150 行，MST 用 Kruskal/Prim 算法，传播用 DFS）。**定位为 30 号 StrategyBook risk parity 的 Phase 2 演进**（与 HRP 并列二选一：long-only 用 HRP，long-short 用 TRP），非 MVP 必需。**risk parity 远期递进扩为六层**：naive risk parity → HRP（long-only） / **TRP（long-short+信号，v1.5.0 补充）** → Certified Wasserstein DRO → Wasserstein 生成式 → MFCCA 多重分形。实证规模仍小（2026-04 发布，crypto universe 实证），A 股需独立验证 TRP 的 MST 拓扑结构稳定性

**2026 MINGLE 因子-图联合框架——选项之外更好的答案算法（v1.9.0 极新补充）**：十五轮审查发现 **MINGLE（Mutually-INformed Graph-Locality and Exposures framework, arxiv 2608.06618, Chehab/Iacovides/Yazdanparast/Mandic, Imperial College London, 2026-08-06 极新）** 是"选项之外更好的答案算法"——**直击 HRP/TRP 的图构建层根本局限**：它们用**观测到的相关性**（Mantegna 距离 D=√((1-ρ)/2)）构建图拓扑，而相关性是**有限样本产物**+**共动而非因果**。MINGLE 将图局部性从"观测共动"重新定义为"**系统因子暴露画像相似性**"，是因子域+图域的**联合框架**非纯图方法：
- **核心方法**——通过 ADMM（Alternating Direction Method of Multipliers）**联合学习**潜在因子表示+其诱导的图拓扑：① **因子域**学习资产的潜在因子暴露（捕获系统性收益的潜在数据结构）；② **图域**构建暴露相似性图（exposure-similarity graph，非相关性图）；③ **互正则化**——因子域与图域相互约束：因子暴露定义图局部性，图拓扑反过来正则化因子学习。**关键区别**：HRP/TRP 用 ρ 构建图→MINGLE 用因子暴露构建图→图更对齐经济部门（非有限样本噪声）
- **vs HRP/TRP 的本质区别**：① HRP/TRP 的图是**相关性图**（ρ→Mantegna 距离→MST），受有限样本噪声驱动；MINGLE 的图是**暴露相似性图**（因子暴露→相似度→图拓扑），由经济结构驱动；② HRP/TRP **纯图方法**忽略因子结构（系统性收益的潜在因子被丢弃），MINGLE **因子+图联合**同时捕获系统性因子+特质冲击；③ HRP/TRP 的图构建与分配是**两步串行**（先建图再分配），MINGLE 是**一步联合**（ADMM 同时优化因子+图+分配）
- **实证**：暴露相似性图比传统相关性图**更对齐已建立的经济部门**；基于该表示构建的组合在**不同波动率 regime 和交易成本水平上持续优于**基于相关性的对应组合；配对统计检验确认增益来自图域与因子域的调和
- **与项目对接**：① **图构建层升级**——HRP/TRP 的 Mantegna 距离图可升级为 MINGLE 的暴露相似性图，是"图构建"层的增强非"分配"层的增强（HRP-TRP 管分配，MINGLE 管图构建），三者可组合（MINGLE 图 + TRP 分配 = MINGLE-TRP）；② **对接 22 号板块轮动**——MINGLE 的"暴露相似性图对齐经济部门"直接验证项目 22 号板块轮动的行业结构假设（申万行业分类对应 MINGLE 的因子暴露聚类）；③ **对接 25 号多因子**——MINGLE 的因子暴露画像直接复用 25 号多因子策略的因子库（打分/IC 加权/正交化后的因子暴露作 MINGLE 的输入）；④ **对接 32 号 FirmRiskAggregator**——MINGLE 的因子+图联合表示为 firm 层风险聚合提供更丰富的依赖结构（非简单相关性矩阵）
- **过度工程评估**：MINGLE 需 ADMM 求解器+因子学习+图拓扑学习三组件，复杂度高于 HRP/TRP（纯图+分配），与已拒绝的 HRP/MVO 同类复杂度。**v1.6.0 已评估后不采纳 MVP**——ADMM+图拓扑学习对个人系统偏重，5 策略规模边际收益不显著，依赖因子暴露矩阵估计引入不稳定性。**定位为 Phase 5+ 远期候选**（与 MFCCA 同条件：策略数>8 且 32 号 correlation_dedup 漏检率高时重评）——当 HRP/TRP 的相关性图在 A 股政策市（regime 切换频繁导致相关性结构不稳定）表现不佳且策略规模扩展到 >8 时，MINGLE 的因子暴露图是升级选项（因子暴露比相关性更 regime-stable）。**risk parity 远期递进参考**：naive risk parity → HRP（long-only）/TRP（long-short+信号）→ Certified Wasserstein DRO → Wasserstein 生成式 → MFCCA 多重分形 → **MINGLE 因子-图联合（v1.9.0 补充，Phase 5+ 远期）**。实证规模仍小（2026-08 发布），A 股需独立验证因子暴露图的 regime 稳定性

**2026 C-WRP（Certified Wasserstein Robust Portfolio）——Wasserstein 家族组合层 LP 化视角补充（v1.6.0 补充，对应文档 v1.17.0）**：[arXiv:2608.07032](https://arxiv.org/abs/2608.07032)（Hsieh & Gan, 2026-08-07）已在 v1.0.0 登记为 Wasserstein 家族三件套的组合层，v1.8.0 已补充认证误差界，本次从 **LP 化+certified approximation error bound 工程可行性视角**补充——
- **核心创新（LP 化视角）**：高维 Wasserstein DRO 组合优化的 LP 化方法——supporting hyperplane majorize 效用函数 + 对偶化子问题，将原问题转化为**多项式规模线性规划**，提供 **certified approximation error bound**（uniform utility-approximation error 同时 bound robust-value error 和 near-optimality gap），支持 476-1000+ 资产月频调仓
- **与项目三因子乘法的对比**：项目 MVP 组合层用**三因子乘法**（alpha 信号 × risk parity 逆方差 × Kelly 缩放，O(N) 复杂度）替代优化器。C-WRP 的 LP 化虽多项式可解但需凸优化求解器（cvxpy/scipy.optimize），与三因子乘法 O(N) 复杂度不符
- **定位**：**Phase 4+ 远期候选**（v1.0.0 原定 Phase 3+，本次更新为 Phase 4+——MVP 三因子乘法先行，C-WRP 是三因子乘法的远期升级路径，当策略数显著扩大且三因子乘法证明不足时评估）。**不进 MVP 理由**：LP 化虽比传统 DRO 可行，但仍需凸优化求解器，与三因子乘法 O(N) 复杂度不符

**2026 RRP（Robust Risk Parity with GARCH + Market State）——A 股实证优化的 risk parity 中间档（v1.6.0 补充，对应文档 v1.17.0）**：Finance Research Letters vol.92(C), 2026 提出 **RRP**——risk parity + adaptive perturbation + GARCH 波动率预测 + 市场状态识别 + factor-structured covariance，是 risk parity 递进中的"A 股实证优化"中间档：
- **核心方法**：① risk parity 基础上引入 adaptive perturbation（自适应扰动）增强鲁棒性；② GARCH 波动率预测替代历史波动率（前瞻性更好）；③ 市场状态识别（market state）条件化风险分配；④ factor-structured covariance 降低估计维度
- **关键实证**：**中国市场 2012-2024 数据**，RRP 在 returns/Sharpe/vol/MaxDD/Calmar 上全面优于 TRP（Traditional Risk Parity）/EW（等权）/GMV（最小方差）——**A 股 native 实证是最大优势**
- **与项目 risk parity 递进的关系**：RRP 可插入 HRP 与 TRP 之间作为"A 股实证优化"中间档：naive risk parity → HRP（long-only） / TRP（long-short+信号）→ **RRP（A 股实证优化，v1.6.0 补充）** → Certified W-DRO → W-GAN → MFCCA → MINGLE
- **与项目对接**：① 30 号 StrategyBook risk parity 当前为 inverse-vol（naive），RRP 的 GARCH 波动率预测可复用项目 10 号 regime 检测器的市场状态输出；② RRP 的 factor-structured covariance 与 15 号因子模型对接（因子暴露矩阵作结构化协方差输入）；③ **中国市场 2012-2024 实证**是项目 A 股落地的直接证据（vs HRP/TRP 的 crypto/美股实证）
- **过度工程评估**：RRP 需 GARCH 波动率模型+市场状态识别+factor-structured covariance 三组件，复杂度高于 naive risk parity 但低于 Wasserstein DRO。**定位为 Phase 2+ 远期候选**（中国市场实证是最大优势，但 MVP 用 inverse-vol Morwane 实证已足够），非 MVP 必需

**2026 SciPhy RL——物理信息神经网络组合优化（v1.18.0 补充，[arXiv:2607.15195](https://arxiv.org/abs/2607.15195) Halperin & Itkin 2026-07）**：将组合优化表述为扩展状态空间连续时间控制问题，**累积成本纳入状态**，二次价格冲击项，通过路径 HJB 用物理信息神经网络离线求解。动作从交易速率重定义为**离散目标持仓**——14 资产 ETF 宇宙，Gibbs 策略产生显著样本外 Sharpe 提升。**与项目对接**：① "目标持仓"框架贴近实盘（T+1 下只需决定目标持仓，次日执行），与 31 号 FirmTargetPortfolio 产出形态一致；② 成本内生化避免回测虚高（与 52 号 Pre-Registration 互补——Pre-Registration 防过拟合，SciPhy 成本内生化防成本低估）；③ **定位 Phase 4+ 远期候选**——PINN 求解器复杂度高，MVP 三因子乘法先行，当策略数扩大且三因子乘法证明不足时评估。

**2026 HRT 双层 RL——选股+执行分层强化交易者（v1.18.0 补充，[arXiv:2410.14927](https://arxiv.org/abs/2410.14927) Zhao & Welsch MIT 2026-05）**：双层 RL——高层控制器（HLC）因子化稀疏选择增/减/持方向；低层控制器（LLC）风险感知转换为可行组合权重，含 **turnover、回撤、文本风险惩罚**。Sharpe 1.24，turnover 0.090。**与项目对接**：① 双层分解（选股+执行）天然适配 A 股"选股 T 日，执行 T+1"流程，与 30 号 sleeve 框架（alpha sleeve+execution sleeve）结构同构；② turnover/回撤/文本风险惩罚是项目 42 号 TradeLevelCircuitBreaker + 35 号回撤 Protocol + 26 号事件 NLP 的 RL 统一框架；③ **定位 Phase 5+ 远期候选**——RL 基础设施依赖（与 TT-DAC-PS/MAP-Elites 同条件），MVP 不引入。

**2026 Finance-Grounded 损失函数——turnover 正则化+MDD 损失（v1.18.0 补充，[arXiv:2509.04541](https://arxiv.org/abs/2509.04541) Khubiyev 等 2026-02 Sirius/MIPT）**：从 Sharpe 比率、PnL、最大回撤（MDD）直接推导损失函数族，加 **turnover 正则化**显式约束交易活动。模型训练目标与下游评估指标对齐。**与项目对接**：① turnover 正则化对 A 股高换手策略降成本关键（打板 sleeve 日换手>100%，多因子周换手 20-40%），直接嵌入 25 号多因子因子模型训练目标；② MDD 损失直接优化回撤，与 35 号 4 级回撤 Protocol 的"事后硬触发"互补——MDD 损失是"事前训练优化"（模型学会控制回撤），4 级 Protocol 是"事后硬保护"；③ **定位 Phase 2+ 远期候选**——仅需修改损失函数（非架构变更），实施门槛低于 SciPhy/HRT，当 25 号因子模型从 IC 加权升级到 ML 合成时同步评估。

**2026 Strat-LLM——T+1 滚动策略对齐 LLM 交易（v1.18.0 补充，[arXiv:2605.06024](https://arxiv.org/abs/2605.06024) Huang & Yu 2026-05）**：分层策略对齐协议——专家策略分类法、交互模式、**T+1 滚动决策与反馈**。2025 年全年 live-forward，集成序列价格、实时新闻、年报。**关键发现**：推理模型在 Free Mode 靠内部逻辑达峰值；标准模型需 Strict Mode 作风险锚；对齐效用依赖 regime（牛市 Free/Guided 抓动量，熊市 Strict 减回撤）；35B 模型在严格约束下最优；标准 LLM 陷高胜率陷阱。**与项目对接**：① 显式 T+1 滚动决策与项目 T+1 约束天然适配，61 号 AlphaCrafter/Alpha-R1 的 LLM agent 框架可借鉴 Strat-LLM 的 T+1 滚动反馈机制；② regime 依赖的对齐策略（牛市 Free/熊市 Strict）与 10 号 regime 检测器+30 号 budget Shrinkage 结构同构；③ **定位 Phase 5+ 远期候选**——LLM 推理成本高（35B 模型），MVP 用 26 号 Qwen2.5-7B 单阶段 NLP 管道，当 LLM 推理成本下降+实盘 6-12 月后评估升级。

**2026 稀疏衰减 Sparse Decay——稀疏组合约束加速因子衰减 + RMT 去噪权重分配（v1.18.1 补充，[arXiv:2507.17211](https://arxiv.org/abs/2507.17211) Chen/Luo/Zhang/Liu/Zhang 2026-08-07 港城大+上财）**：提出 **"稀疏衰减"（sparse decay）新现象**——因子在稀疏组合（ℓ0 范数约束，仅选 m 个资产）下衰减**快于**密集组合。机制：稀疏约束放大单资产特异性噪声，因子预测的截面排序在少数资产上更易被 idiosyncratic 冲击推翻。解决方案：LLM+进化算法自动生成 alpha 因子 + **redundancy-aware 权重分配模块**——随机矩阵理论 (RMT) 去噪因子相关矩阵（剔除 Marchenko-Pastur 谱噪声特征值）+ 正则化二次规划分配权重，零额外调参开销。CSI300/CSI500 + 美股/港股实证优于统计与优化基线。**与项目对接**：① **稀疏衰减概念填补 25 号衰减监控的认知盲区**——25 号当前用 Alpha-R1（拥挤衰减）+ AlphaPROBE（过拟合衰减）+ McLean-Pontiff（发表后衰减）+ CUSUM（统计衰减），但均假设组合稠密；打板 sleeve 持仓极稀疏（单票几万~几十万，2-5 只），稀疏衰减是打板 sleeve 独有的衰减维度——因子在打板稀疏持仓下失效更快，须更短的半衰期阈值/更快的淘汰节奏。② **RMT 去噪因子相关矩阵**是 25 号因子合成的直接增强——当前 IC 加权/回归合成未做因子间相关性去噪，RMT 剔除噪声特征值可提升合成 alpha 的信噪比（与 25 号 §3.1 残差代数 Phase 4 候选正交——残差代数管"合成方法"，RMT 管"输入因子矩阵去噪"）。③ **定位 Phase 2+ 候选**——RMT 去噪是矩阵运算（非架构变更），实施门槛低；稀疏衰减阈值校准依赖打板 sleeve 实盘 IC 衰减数据（与 25 号 ic_decay.py 联动），Phase 2 各 sleeve IC 半衰期稳定后评估。

**2026 VD-MEAC 价值分布 Actor-Critic——critic 学全分布+熵正则（v1.18.1 补充，[Front. Artif. Intell. 2026-01](https://doi.org/10.3389/frai.2025.1709493) Yang/Wang/Fu/Huang/Zhou 南方电网资本）**：Value Distribution Maximum Entropy Actor-Critic——critic 网络学习未来收益的**完整分布**（非点估计），避免点估计导致的风险寻求行为；熵正则化平衡探索-利用。A 股实证平均收益 2.490 / Sharpe 2.978。**与项目对接**：① **价值分布概念是 HRT 双层 RL 的增量改进**——HRT（v1.18.0 已登记）的 critic 用点估计，VD-MEAC 用分布估计更适配 A 股重尾收益分布（与 36 号 Student-t ν 状态变量同源——重尾须分布建模非点估计）；② 熵正则化解决 RL 探索-利用失衡，A 股 regime 切换频繁须持续探索；③ **定位 Phase 5+ 远期候选（HRT 增量）**——不单独登记为独立候选，作为 HRT 双层 RL 升级到"分布 critic+熵正则"版本的增量改进参考，当 HRT 在 Phase 5+ 评估时一并考虑价值分布扩展。

**保留的待讨论问题**（细节未定，不阻塞核心流程）：
- 集中度硬约束（行业偏离±10%、风格暴露±0.3σ）的阈值依据？——FirmRiskAggregator 裁剪规则待 G13 讨论【v2.0.0 补充：代码侧现状=position_limit_enforcer 单票≤5% NAV + concentration_monitor 单票 8% 告警/行业 30% 上限，G13 对账时以代码真源为起点校准】
- StrategyBook 内 risk parity 的具体实现（inverse-vol？ERC？）？——待 G12 细化【v2.0.0 补充：代码现状=inverse-vol（volatility_data 输入），已 production；远期递进 HRP/TRP→RRP→C-WRP→W-GAN→MFCCA→MINGLE 见上各版本补充，均 Phase 2+/远期，MVP 不变】

---

## 4. 风险模型（原约束四）

> 对应 G16-G18（风控落地）｜ ✅ **已裁定（2026-08-05，30_multi_strategy §2.5；v2.0.0 补口径对账注记）**

**原始内容**：L1实时监控(延迟<1秒)+L2日频因子风险模型(申万31行业+4风格因子)+L3压力测试；VaR/CVaR作为L2量化输入，VaR回测通过率>95%。

**✅ 裁定结论**：30_multi_strategy §2.5 已定 **StrategyBook Drawdown Protocol（4级回撤 + 恢复机制 + 分层风控 + VaR/ES 辅助 + Kill Switch）**，L1/L2/L3 三层架构被替代。映射关系：

| 原始 L1/L2/L3 | 替代方案（30_multi_strategy §2.5） |
|---|---|
| L1 实时监控 | Kill Switch 紧急熔断（单日亏损>6%→平仓+暂停3天；流动性危机→停止开仓）|
| L2 日频因子风险模型 | **4级回撤 Protocol**（Level1 警告 8% / Level2 减仓 15% / Level3 停仓 20% / Level4 清仓 25%）+ VaR/ES 辅助监控 |
| L3 压力测试 | 恢复机制（回撤企稳 50%→解除停仓；Level4 后强制休息 5 交易日）+ 分层风控（单策略 vs 组合）|

- **VaR/ES 角色**：辅助监控指标（VaR_95 > 1.2×入场→减仓 20%；ES_95 > 1.3×入场→再减仓 20%），**不是** L2 量化输入的主模型
- **申万31行业+4风格因子**：FirmRiskAggregator **不做协方差估计**（30_multi_strategy §2.2），因子风险模型未采用
- **行业基准**：LedgerMind 2026-05 / ARKA 2026 / Sina 量化FOF 2026-07 / tradingwyckoff 2026-01 / 赢牛资管 2026-05（详见 30_multi_strategy §2.5 行业来源）

**保留的待讨论问题**（细节未定）：
- 压力测试的场景设计？——4级 Protocol 覆盖回撤场景，但极端事件（黑天鹅）压力测试方案待 G16 细化【v2.0.0 补充：stress_test_engine.py 已内置行业冲击情景；2026-07 量化"双杀"episode 应纳入极端 regime 回测场景（见附录 A.3）】
- VaR/ES 的计算方法（历史模拟法？参数法？蒙特卡洛？）？——待 G17 讨论【v2.0.0 补充：代码现状=var_calculator.py 历史模拟+参数法+var_backtester 回验已 production，G17 对账时以代码真源为准；RWC 压力期校准为 Phase 2 增强（见 v1.12.0 补充）】

**⚠️ v2.0.0 口径对账注记**：代码 `drawdown_controller.py`（MOD-POS-008）当前为 5 级 VaR 风险级（GREEN~BLACK）+ Soft Stop 5%/Hard Stop 10% 策略止损 + 黑天鹅 7 模式，与本文档/30 号 §2.5 的 4 级回撤 Protocol（8/15/20/25% 净值域）双轨并存。30 号 §2.5 开头已自注"须在 G13/G14 讨论中明确两视角的映射关系"。**裁定方向（待 G13/G14 闭环）**：4 级回撤 Protocol 是净值域硬红线（mandatory），5 级 VaR 风险级+Soft/Hard 止损是策略级监控层——两者并存不冲突，但触发阈值的映射关系（如 Soft 5% vs Level1 8%）须在 35 号 drawdown_protocol_impl 落码时统一，避免双阈值打架。

**2026 回撤风险非高斯扩展补充（v1.4.0 极新，风控优先原则核心）**：十三轮审查发现 2026-07-31 发布的 **Drawdown Risk Beyond Brownian Motion**（arxiv 2608.00127, Landolfi, Epiphany）是"选项之外更好的答案算法"——**直接对应项目风险优先原则的核心模块（4 级回撤 Protocol + drawdown_controller）**，揭示项目当前 Gaussian 假设下的回撤表系统性误警：
- **核心方法**：扩展 Rej-Seager-Bouchaud (RSB) 回撤框架，将 P&L 建模为带漂移布朗运动（σ=1 归一化，SR=μ），蒙特卡洛生成 4 个决策相关测度的查找表（lookup table）：① **最大回撤深度**（MaxDD，多倍年波动率）；② **最大单期损失**（Max Loss）；③ **末态负时间**（Final Negative Time，策略在水下占比）；④ **最长恢复时间**（Longest Recovery Time）。风险经理可直接读表判断"当前回撤是统计正常 pain 还是 edge 衰减信号"
- **关键发现 1——非高斯下四测度分化**：固定真实 Sharpe 与波动率，变化偏度/肥尾/波动率聚类/Sharpe 估计不确定性，**四个测度不同步移动**——单一 Gaussian 表系统性误警（mis-warn）。项目 4 级回撤 Protocol 的 8/15/20/25% 硬阈值若基于 Gaussian 表，可能在肥尾 regime 误判"正常 pain"为"该止损"或在偏态 regime 误判"该止损"为"正常 pain"
- **关键发现 2——长记忆性是尺度校准失效非路径几何深化**：用 fractional Brownian motion (fBM) 替换短记忆持续性，最大回撤深度在持续性下的"放大"**几乎完全是自相似色散尺度效应**（self-similar dispersion scaling, T^(H-1/2)）而非路径几何深化——是**平方根时间校准的失效**，非内在危险。启示：项目若用 sqrt(T) 缩放 VaR/ES（如 VaR_10d = VaR_1d × √10），在长记忆 regime 会系统性高估回撤风险
- **与项目 4 级回撤 Protocol 的对接**：① 当前 4 级 Protocol 阈值（8/15/20/25%）是经验设定，**Landolfi 框架提供数据驱动的阈值校准路径**——按策略真实 Sharpe+波动率+偏度+肥尾+Hurst 指数生成 4 测度查找表，Level1-4 阈值可映射到 MaxDD 分布的分位数（如 Level2 15% = MaxDD 75 分位）；② **末态负时间+最长恢复时间**是 30 号 §2.5 恢复机制（回撤企稳 50%→解除停仓/Level4 后休息 5 交易日）的量化补充——"企稳 50%"可替换为"恢复时间分布中位数"；③ **非高斯分化**支持项目 #16 系统级成功指标（v0.5.0 五层评估）的"单一指标陷阱"告诫——回撤评估需多测度联合而非单一 MaxDD
- **与 91 号 v1.2.0 Lévy 家族的协同**：Landolfi 放松 Gaussian 假设的方向（偏度/肥尾/波动率聚类）与 91 号 Tail-Aware MDN（skewed Student-t）+ DeepLévy（α-stable）+ Lévy-Flow（VG/NIG）一致——密度预测层提供非高斯分布，Landolfi 框架消费非高斯分布生成回撤查找表，形成"密度预测→回撤风险测度"的上下游闭环
- **过度工程评估**：蒙特卡洛查找表是离线预计算（非在线推理），实现成本中等（~200 行仿真+查找表）。**定位为 drawdown_controller Phase 2 阈值校准升级**（MVP 先用经验 8/15/20/25% 阈值，Phase 2 用 Landolfi 查找表数据驱动校准），非 MVP 必需但属风控优先原则的核心增强——风险相关模块优先施工至 production 符合项目硬约束

**2026 Sharp Tail Bounds——分布无关尾部概率解析上界（v1.11.0 极新，风控理论背书）**：二十一轮审查发现 2026-08-06 发布的 **Sharp Tail Bounds Beyond Twice the Mean**（[arXiv:2608.06317](https://arxiv.org/abs/2608.06317), Strack/Westermann, UC Berkeley）是风险度量理论工具——对 n 个独立非负、均值≤1 的随机变量，证明 **P[ΣXi≥t] ≤ 1−(1−1/t)^n**（对所有 t≥2n+1），该界在二元 i.i.d.（P[Xi=0]=1−1/t, P[Xi=t]=1/t）下取等且在放松问题中仍是最优：
- **核心价值——分布无关（distribution-free）解析上界**：项目 36 号 VaR/ES 当前用历史模拟法+参数法，本界提供第三条路径——不需要假设正态/Student-t/任何参数族，仅需各策略损失均值≤1（归一化后）即给出尾部概率严格上界。是"参数估计噪声→权重脆弱"问题（v1.9.0 ① Fragile Frontier Sobol 诊断）的理论兜底——即使协方差矩阵估计完全失效，此界仅依赖均值约束仍成立
- **与多策略组合 VaR 聚合的对接**：项目 3-5 策略（打板/多因子/事件驱动）日损失分布为独立非负随机变量（假设 sleeve 间独立），组合日损失超阈值 t 的概率有闭式上界 1−(1−1/t)^n。可用于验证历史模拟 VaR_99 是否超过解析上界——若历史模拟值显著超解析界，提示历史样本含异常极端事件需审查；若历史模拟值远低于解析界，提示样本期未覆盖最坏二元场景
- **二元 i.i.d. 取等的 A 股启示**：界在最坏情况（二元分布）下取等——A 股涨跌停（±10%）天然接近二元分布（涨停≈+10%/跌停≈−10%/平盘≈0%），此界对 A 股打板策略的损失聚合特别紧致（其他连续分布下界更松但安全边际更大）。这与 v1.0.0 Tail-Aware MDN 的"打板=locally explosive 二元化"洞察一致
- **与 Landolfi 回撤查找表（v1.4.0 ②）的协同**：Landolfi 提供非高斯下 4 测度查找表（MaxDD/Max Loss/Final Negative Time/Longest Recovery Time），Sharp Tail Bounds 提供**单期损失超阈值的解析包络**——Landolfi 的 Max Loss 测度可用此界作单期理论上界，多期 MaxDD 用 Landolfi 蒙特卡洛查找表，两者形成"单期解析界→多期仿真表"上下游闭环
- **适用条件与局限**：① t≥2n+1 即阈值需超 2 倍策略数+1（归一化后），对 3-5 策略组合 t≥7-11，对应归一化损失需超 7-11 倍单策略均值——是**极端尾部**场景，非日常 VaR_95 范畴，适用于 VaR_99.5+/ES_99 极端尾部校验；② 仅给上界非精确值，实际尾部概率可能远低于界（保守方向）；③ 假设独立性，策略间相关性>0 时界偏松（高估尾部概率=保守方向，与 32 号 correlation_dedup 正相关策略漏检风险对冲）
- **过度工程评估**：纯理论工具（11KB 论文无代码），实施成本=0（闭式公式直接套用 `bound = 1 - (1-1/t)**n`），**定位为 36 号 VaR/ES 的理论背书工具**（验证历史模拟 VaR 极端尾部是否超解析上界），非独立施工算法非 MVP 必需——属风控优先原则的理论增强

**2026 Bayesian GP 尾部外推——honest credible region 尾部估计（v1.11.0 补充，密度预测远期候选）**：二十一轮审查发现 [arXiv:2510.14637, Carl/Padoan/Rizzelli, 2025-10-16](https://arxiv.org/abs/2510.14637) 提供**尾部外推的贝叶斯可信区间**——β-mixing 条件下 Gaussian Process 的 Bayesian 后验，渐近 honest credible regions，动态条件尾分位估计：
- **核心方法**：用 GP 对尾部超出阈值的数据建模，贝叶斯后验给出尾部分位数的 credible region（不仅点估计还有置信区间）。优于 naive Bayesian 和 MLE 置信域，支持 ARMA/GARCH/Markov copula 等依赖结构
- **与项目对接**：91 号密度预测 Phase 2 GPD/TailGAN 当前用频率派尾部估计（给点估计），Bayesian GP 提供"尾部外推的 honest credible region"——不仅给 VaR/ES 点估计还给置信区间，与 Sharp Tail Bounds 互补（GP 给精确尾部密度+CI，Sharp Tail Bounds 给分布无关上界包络），与 36 号 Landolfi 回撤查找表互补（GP 给单期尾部密度，Landolfi 给多期回撤仿真表）
- **过度工程评估**：GP+贝叶斯推断复杂度中等（~200 行+MCMC 采样），**定位为 91 号 Phase 3+ 远期候选**（当 91 号从 GPD 升级到贝叶斯尾部估计时评估），非 MVP 必需——MVP 先用 91 号 Phase 0-1 conformal+LSTM+GMM baseline

**2026 Regime-Weighted Conformal Calibration——压力期 VaR 校准（v1.12.0 极新，36 号 VaR 校准增强）**：三十二轮审查全网搜索发现 [arXiv:2602.03903v3, Schmitt, University of Oxford, 2026-08-03](https://arxiv.org/abs/2602.03903) "Taming Tail Risk: Conformal Calibration for Nonstationary Portfolio VaR" 是"选项之外更好的答案算法"——直接对应项目 36 号 VaR/ES 监控的**压力期失准**问题：
- **核心方法——Regime-Weighted Conformal Calibration (RWC)**：model-agnostic 包装器，包裹任意条件分位数预测器（历史模拟/参数法/蒙特卡洛/GARCH-EDCG 等），用过去预测误差构建安全缓冲（safety buffer）。权重 = 指数时间衰减 × regime 相似度权重，使近期+同 regime 的预测误差获更高权重。TWC（Time-Weighted Calibration，纯时间衰减无 regime 权重）是 RWC 的特例
- **覆盖率理论保证**：在**平滑 regime 漂移**（smooth regime drift）下，对任意数据驱动权重推导覆盖率上下界——**不假设加权可交换性**（weighted exchangeability），比经典 conformal prediction 的可交换性假设更弱、更适配金融非平稳性
- **实证基础**：CRSP 指数 + 16 个美国股票组合，Basel 相关的 99% 和 97.5% 水平。**TWC 是漂移下的强默认**（time-weighted 已足够），**regime 加权改善慢适应预测器的压力期校准**（slowly adapting forecasters 在 stress period 被 regime 权重拉回校准），诊断指标指示何时 localization 可靠
- **与项目 36 号的对接**：① 36 号 VaR/ES 当前用历史模拟法+参数法，**压力期失准是已知问题**——VaR 预测的超额发生率集中在压力期（loss 最大时），这正是 36 号 v1.0.0 已登记的"VaR 回测通过率>95%"门禁的痛点。RWC 提供 model-agnostic 校准层，在 VaR 预测值外包一层 conformal buffer，使超额发生率在 stress period 也逼近名义水平；② 36 号的 regime 检测（10 号 HMM 12 态）天然提供 RWC 所需的 regime 相似度权重——两个 regime 状态向量距离近→权重高，与 10 号 HMM 后验概率对接
- **与 §4 已登记三项的层次互补**：① Sharp Tail Bounds（v1.11.0）给分布无关解析上界（极端尾部 t≥2n+1 包络）；② Bayesian GP（v1.11.0）给尾部外推 honest credible region（精确尾部密度+CI）；③ Landolfi 回撤查找表（v1.4.0）给非高斯多期回撤 4 测度；④ **RWC（本项）给压力期校准**——四者形成"极端尾部上界→精确尾部密度→多期回撤仿真→压力期校准"的完整 VaR 风控栈，各自正交不重叠
- **与 52 号回测门禁的对接**：RWC 是 online/sequential conformal 方法，天然适配 52 号的 IS→WFA→OOS 门控——WFA 窗口滚动更新 conformal buffer，OOS 验证校准后超额发生率是否达标（Basel traffic-light 框架）
- **过度工程评估**：RWC 是 wrapper 方法（不改预测器本身，只加校准层），实施成本低（~150 行：误差序列存储+指数衰减+regime 相似度矩阵+buffer 求解）。**定位为 36 号 Phase 2 VaR 校准增强**——MVP 先用历史模拟 VaR baseline + VaR 回测通过率>95% 门禁，Phase 2 实盘 TCA 数据积累后加 RWC 校准层解决压力期失准。与 Landolfi 回撤查找表同 Phase 2 启用条件（需实盘数据校准）。**非过度工程**：wrapper 模式轻量，且解决的是 36 号已登记的已知痛点（压力期失准），非新增功能

**2026 分布漂移标度律——检测样本量下界+核带宽校准（v1.15.0 补充，regime/变点检测理论背书）**：四十轮审查全网搜索 2026-08-08~10 最新研究发现 [arXiv:2608.01268, Kaleche, 2026-08-02, stat.ML](https://arxiv.org/abs/2608.01268) "Scale Law for Detecting Distribution Shift + Kernel Calibration Rule" 是分布漂移检测的理论工具——直接对应项目 10 号 regime 检测 + 55/61 号变点检测的"何时该信任检测结果"问题：
- **核心方法——标度律 N\* ≥ log(1/f)/(2ε)**：从 Chebyshev 极值问题导出检测分布漂移所需的最小样本量标度律——以频率 f 发生、精度 ε 检测分布漂移需 N\* ≥ log(1/f)/(2ε) 样本。这是"检测能力下界"——低于此样本量，任何检测器（HMM/CUSUM/MMD/BOCPD）都无法可靠区分"真实漂移"与"采样噪声"
- **核校准规则——RBF MMD 带宽 = 特征尺度**：Maximum Mean Discrepancy (MMD) 是分布漂移检测的标准非参数检验，但 RBF 核带宽选择长期依赖经验（median heuristic 等）。本文证明带宽应匹配特征尺度（feature scale），且带宽匹配的核检验在对抗设定（adversarial setting）下主导拓扑替代方法（topological alternatives）
- **与项目 10 号 regime 检测的对接**：10 号 HMM 12 态检测器的"regime 转换置信度"依赖后验概率阈值——标度律提供"当前样本量是否足以信任此次转换判定"的理论判据。A 股 regime 切换频繁（政策市），短窗口（如 20 日）检测到的 regime 转换可能低于 N\* 下界→应降权或延长确认窗口
- **与 55/61 号变点检测的对接**：55 号 LBD-FDR/Robust CUSUM/Tail-adaptive CUSUM/RCD/DeCAFS 五项变点检测 + 61 号 ARM/DPitG/Betting on Bets/RLCP/Decaying-ε-FOCuS 五项选项外更优算法均需"检测到变点后判断是否可信"——标度律提供事后可信度判据（检测窗口 ≥ N\* → 可信；< N\* → 需补样本或标"低置信变点"）
- **与 §4 RWC（v1.12.0）的协同**：RWC 假设"平滑 regime 漂移"（smooth regime drift）但未提供"漂移是否已发生"的形式化检验——标度律 + 核校准填补此空白：MMD 检验（带宽校准后）判断漂移是否发生，标度律判断样本量是否足够，RWC 在确认漂移后启动 regime 加权校准。三者形成"漂移检测→可信度判据→校准启动"上下游闭环
- **过度工程评估**：纯理论工具（标度律是闭式公式 N\* = log(1/f)/(2ε)，核校准是参数选择规则），实施成本 ≈ 0（与 Sharp Tail Bounds 同类）。**定位为 10/55/61 号检测器的理论背书工具**——不独立施工，仅作"检测结果可信度判据"嵌入现有检测器的置信度输出层。非 MVP 必需，属检测理论增强

---

## 5. 成本模型细节（原约束五）

> 对应 G22（下单对接）｜ ✅ **v2.0.0 裁定：简化采纳（砍 Almgren-Chriss MVP、策略分档滑点、最低佣金显式建模）**

**✅ v2.0.0 裁定结论**：

- **本质**：个人小资金成本结构是"固定费用主导、冲击可忽略"——order/ADV<0.1% 时平方根冲击 <5bps，相对价差可忽略。第一性原理：成本模型的精度只需匹配"决策所需精度"——判断策略赚不赚钱需要准确的固定成本，不需要精确的冲击曲线。
- **裁定**：① **Almgren-Chriss 不采纳进 MVP**（留 cost_model_registry impact_model 接口字段，远期资金量级到单票百万+再启用）——v0.3.0 平方根冲击律结论维持（个人资金冲击可忽略）；② **滑点按策略分档**：高流动票 0.05-0.1%，打板/事件票 0.15-0.3% 并乘成交概率折减（打板买入有封板买不进概率，预期滑点须按条件成交修正）；③ **最低 5 元佣金必须显式建模**——单笔 <5 万元时实际费率被抬升至万5以上，是小资金+做T高频的最大隐性成本，回测漏建会系统性高估收益；④ **印花税率更正**：原稿"千1卖出"已过时——2023-08-28 减半后现行为**卖出单边 0.05%（万5）**，与 cost_model_registry CST-ASTOCK-001 登记一致（佣金万3/印花税万5，费率按账户配置不硬编码，宪章已定）；⑤ **做T额外成本**：滑点×2 合理保留（一买一卖两次滑点）；单次往返硬成本≈0.10-0.15%（双边佣金+卖出印花税+双倍滑点），**预期价差≥0.3% 才有正期望**——此阈值作为做T开仓的硬性前置条件（与 §21 regime 过滤规则联动）；失败风险溢价保留，用隔夜底仓暴露×隔夜 VaR 估算（LVaR 简化式见 §8）。
- **施工方案**：① cost_model_registry 增补**做T成本条目**（CST-T0-001：双边佣金+印花税+滑点×2+失败风险溢价，~30 行 YAML，Phase 1）；② 回测成本计算器确认最低佣金 5 元建模（检查项，若未建则 ~20 行修补，Phase 1）；③ 策略分档滑点参数写入各策略配置（Phase 1）。集成点：回测引擎成本注入点 + 做T策略开仓前置检查。
- **过度工程审查**：全部复用已有注册表与成本注入点，无新架构；Almgren-Chriss 显式降级远期。✅ 通过。

**原始内容**：佣金万2.5双边+印花税千1卖出【v2.0.0 更正：现行万5卖出单边】+滑点(基础0.05%+动态)+市场冲击(Almgren-Chriss)+做T额外成本(滑点×2+失败风险溢价)；回测必须包含全部四类成本。

**注意**：宪章已保留成本结构（佣金+印花税+滑点+市场冲击+做T额外成本），但不硬编码费率。本节讨论的是具体模型细节。

**待讨论问题**：
- Almgren-Chriss市场冲击模型是否采用？参数如何校准？
- 滑点模型（基础+动态）的具体实现？
- 做T额外成本的滑点×2倍率是否合理？
- 费率如何按账户动态配置？

**2026 算法补充（v0.3.0）**：市场冲击建模 2026 已有成熟经验公式，无需从零设计：
- **平方根冲击律（Square-Root Impact Law）**——2026 经验验证标准（arxiv 2603.29086, 2026-03 / jonathankinlay 2026-05）：`市场冲击 = α × σ × √(order_size / ADV)`，其中 σ 为日波动率、ADV 为日均成交额。冲击与订单规模呈**凹函数**（非线性），这是 Bouchaud 等经验研究的共识
- **Almgren-Chriss 分解**：永久冲击（permanent，随成交量线性累积）+ 临时冲击（temporary，仅影响当笔成交后衰减）。2026 进阶为**瞬态冲击模型**（transient impact，指数衰减核 + 平方根缩放，arxiv 2601.22113）
- **个人 A 股适用性**：个人资金量 order_size/ADV 通常 <0.1%，平方根冲击律算出的冲击 <1bp，**可忽略**。回测中用固定滑点（万2.5双边+0.05%基础滑点）已足够；仅当单标的持仓 >1% ADV 时需启用动态冲击模型
- **做T额外成本**：滑点×2 合理（一买一卖两次滑点）；失败风险溢价 = 隔夜底仓暴露 × 隔夜 VaR，可用 #8 的 LVaR 框架量化

---

## 6. 回测门禁（原约束七）

> 对应 G23（回测框架对接）｜ ✅ **已裁定：项目用 BM-BT-01~07 体系，V1-V6 已映射**

**原始内容**：

| 验证层级 | 验证对象 | 验证方法 | 优先级 |
|---------|---------|---------|:-----:|
| V1 因子验证 | 单因子IC/ICIR/分组单调性 | Purged K-Fold+Embargo | P0 |
| V2 信号验证 | 单信号方向准确率/Brier Score | Walk-Forward | P0 |
| V3 策略验证 | 单策略PnL/Sharpe/回撤 | Walk-Forward+Permutation Test | P0 |
| V4 管线验证 | 全链路端到端 | Walk-Forward+模拟盘 | P0 |
| V5 日内信号验证 | 分时指标/做T买卖点 | Walk-Forward逐笔+滑点建模 | P0 |
| V6 风控验证 | 风控触发/熔断/保护性减仓 | 极端场景重放 | P1 |

**✅ 裁定结论**：项目实际用 **BM-BT-01~07** 编号体系（battle_map_03_backtest_validation + 52_backtest_framework_docking + 11_regime_backtest §2.1）。V1-V6 → BM-BT 映射：

| V1-V6（原） | BM-BT（现状） | 验证方法 | 状态 |
|---|---|---|---|
| V1 因子验证 | BM-BT-01~02 | Purged K-Fold + Embargo + 向量化/事件驱动引擎 | ✅ 已施工（BT-01~04 stable） |
| V2 信号验证 | BM-BT-03 | Walk-Forward + 指标计算（Sharpe/Sortino/MaxDD/IC/IR） | ✅ 已施工（BT-05~09 stable） |
| V3 策略验证 | BM-BT-04~05 | Walk-Forward + Permutation Test + **Deflated Sharpe (BM-BT-05-G)** + 过拟合检测三维度 | 🟧 部分（BM-BT-05-G 待实现）【v2.0.0 口径注记：`simulation/deflated_sharpe_calculator.py` 代码已存在，battle_map_03 标 BM-BT-05-G 环节为 design——代码先于登记，G23 对账时确认是否已完成接入 metrics 管线；Purged K-Fold/Permutation Test/PBO 未施工】 |
| V4 管线验证 | BM-BT-06~07 | IS→WFA→OOS 上线门控 + 模拟盘 | 🟧 decision_gate.py（MOD-BT-001）策略路径已 production；regime 验证 Phase 5 门控未完成（11 号 §0.5.1）【v2.0.0 口径澄清】 |
| V5 日内信号验证 | BM-BT（Tick 回放） | Walk-Forward 逐笔 + 滑点建模（秒级/30秒/5秒） | ✅ 已施工（Tick 回放引擎） |
| V6 风控验证 | BM-BT（风控重放） | 极端场景重放 | 📝 待实现 |

**2026 行业实证**（Purged K-Fold / Walk-Forward / DSR 为 2026 标准实践）：
- honest-backtest（2026-06）：PurgedKFold + embargo 是防时间泄漏的标准做法，"plain K-fold leaks in time"
- backtest-guard（2026-07）：**Deflated Sharpe Ratio (DSR) + Probabilistic Sharpe Ratio (PSR)** 是多重检验校正的标准方法——测 80 个变体后 p=0.05 的"显著"结果有 98.3% 是噪声
- mathandmarkets.com（2026-05）：walk-forward 验证将 in-sample Sharpe 0.71 削至 OOS 0.48（-32%），是防自欺的核心工具
- walk-forward-validation skill（2026-07）：purged CV + embargo + regime-aware fold selection 是 2026 生产级标配；CPCV（组合净化交叉验证）是 walk-forward 的进阶替代
- **v1.10.1 新增**：[Darmanin 2026-07-22 arXiv:2607.20093](https://arxiv.org/abs/2607.20093) "Retail Trader's Ruin"（Hecatus Research, Malta）提出**三门控联合"实际可行性"（real-world viability）框架**——比 DSR 单维统计门控更全面：(1) **统计优势门控**（多重检验校正后的统计显著——含 Benjamini-Yekutieli 分层控制+平稳 bootstrap 置信区间+暴露匹配基准+单边声明排除检验+等价性检验）；(2) **经济可行性门控**（交易成本后净 alpha>0——A 股印花税 0.05%+佣金万2.5+滑点 0.1% 三层成本扣除）；(3) **存活率门控**（杠杆下有限资金存活率——两融/配资场景下破产概率 < 阈值）。**关键负结果**：6 个候选策略中 4 个被 REFUTED（振荡器/成交量/日历/K线形态），趋势和动量为 INCONCLUSIVE——印证 A 股 2026 量化危机中"简单信号失效"趋势。**对本项目评估**：与 BM-BT-05-G Deflated Sharpe 互补——DSR 管统计维度，Darmanin 三门控框架把经济可行性和存活率也纳入上线门控，**记为 Phase 2 候选**（BM-BT-05-G 实施时同步引入经济可行性+存活率两维度，避免"统计显著但实盘亏钱"陷阱）。FINRA/ESMA 杠杆场景可类比 A 股两融场景。

**保留的待讨论问题**：
- "策略上线必须通过 V3+V4+模拟盘"标准是否采用？——对应 BM-BT-07 IS→WFA→OOS 门控，待 52_backtest_framework_docking 细化【v2.0.0 注：52 号实际仍为 v0.1.0 骨架，00 号索引标"active v1.7.4"与 52 号 frontmatter 不符，属索引漂移；决策逻辑已施工于 decision_gate.py】
- 幸存者偏差防护（PIT 股票池）的实现状态？——BM-RES-01 特征存储(PIT) + AS OF JOIN，**BT-10 已 production**（battle_map_03 确认 pit_manager stable/production，"PIT管理器未就绪→回测不可信"硬阻断已生效）【v2.0.0 更正：原稿"BT-10 已规划"过时】

---

## 7. T+1次日预测（原约束九）

> 对应 G02（regime spec，已定稿）｜ ⚠️ **纠正（v0.2.0）：原稿"8态已被12态替代"不准确** ｜ ❌ **v2.0.0 裁定：暂缓建设（BM-SEL-04 降级远期）**

**❌ v2.0.0 裁定结论（暂缓建设）**：

- **本质**：次日方向是低信噪比问题，边际信息被隔夜噪声淹没；T+1 下预测对也未必能兑现（当日买不了）。决策论上仓位调整需要的是期望收益/风险比，不是方向点预测。
- **裁定理由**：① **52-53% 天花板 2026 年无突破证据**——纯价量个股方向准确率天花板（firsh.me 9 版迭代 p=0.007）与 2026 各项独立复现（SPY 57-58% 指数、含乐观偏差）一致；加情绪的混合模型文献报 60-68% 但普遍缺 walk-forward 与成本核算，可信度低；龙虎榜净买入单因子次日胜率≈50%（2026-07 实证）；② **8 类细分后单类准确率更低**——52-53% 的方向边缘摊薄到 8 态后单态可用性极低，且"高开低走"等态的可交易性依赖盘中执行，日线模型给不了；③ **regime 7维概率 + VaR/ES 区间已覆盖其作用**（"明天大概率怎么走"的决策需求=风险节流+区间保证，非方向点预测）；④ 方向≠盈利（非对称亏损吞噬统计优势）。
- **裁定**：**BM-SEL-04 暂缓建设，从 design 降级为远期候选**。8态→直接决策映射确认废弃（v0.2.0 已裁定）；8态→特征输入角色一并暂缓（价量信息已被 regime+因子库覆盖，增量有限）。**唯一例外**：打板策略内部的"次日高开概率"是其自身参数，用条件概率表（历史统计，非独立模型）估计即可，不属于 BM-SEL-04。**远期重启条件**（全部满足才可重启评估）：① 系统稳定盈利（生存线达标）；② 目标收窄为"开盘 30 分钟走势"（非全日 8 态）；③ 概率输出仅接入仓位微调（非直接决策）。
- **⚠️ v2.0.0 重要更正——A2 已 PASS**：本节后文多处"直接对应项目 12 号 A2 FAIL（OOS/IS=0.340）"的表述**已过时**。11 号 v1.5.2 §0.5.4 确认：经 BIC 扫描降为 4 态后，A2 OOS/IS 一致率从 0.340 升至 **1.042（PASS，门槛 0.7）**，过拟合消除。因此 **Wasserstein HMM 从"A2 修复必需"降级为 Phase 3+ 可选增强**（标签漂移的长期鲁棒性改进，非修复痛点），P-1/P-3 待定项的紧迫性同步下降（见「待定问题」节更新）。
- **过度工程审查**：不建 8 态模型=做减法，✅ 通过。

**原始内容**：次日走势8态叠加模型(高开高走/高开低走/低开高走/低开低走/平开高走/平开低走/震荡收平/剧烈震荡)；8态→今日决策映射(P1+P5>60%→买入加分20%，P4+P6>60%→降权30%推迟，P8>30%→仓位减半)；分阶段实现Phase1=3态→Phase2=5态→Phase3=8态。

**⚠️ 纠正结论（v0.2.0）**：原稿"❌ 已过时：8态已被12态替代"**不准确**，需区分两个层面：

1. **8态概念未被替代**——8态 T+1 次日走势预测（BM-SEL-04）是**独立的下游消费者**，与 regime 检测器是不同概念：
   - **regime 检测器**（BM-SEL-03-B）= 市场状态分类（趋势×波动率网格 + 特殊覆盖层），回答"现在是什么市场"
   - **8态 T+1 预测**（BM-SEL-04）= 次日开/收走势概率分布（高开高走等），回答"明天大概率怎么走"
   - 10_regime_detector_spec §2.1 明确：BM-SEL-04 是"下游消费者，非检测器本身"，状态 🟧 design（未建）
   - 两者用途不同，8态未被 regime 替代，只是尚未施工

2. **8态→直接决策映射确实过时**——原始映射（P1+P5>60%→买入加分20%）与 Model A 架构冲突：
   - Model A（30_multi_strategy §2.1）：**策略自主做 alpha 决策**，regime 仅通过 Shrinkage 做**风险节流**（不重定向资金、不直接调买卖）
   - 8态预测若消费，应作为策略层的**输入特征**或 Shrinkage 的**置信度参考**，而非直接"买入加分/降权/仓位减半"
   - 即：8态→决策的"直接映射"角色过时，但 8态→特征/信号的"输入"角色仍可成立

3. **regime 实现态数更正**——spec 为 12 态，但**实际实现为 4 态 HMM + 3 overlay = 7 维概率**（11_regime_backtest §0.5.2）：
   - BIC 扫描发现 9 态过度细分（OOS/IS 一致率仅 0.34），降为 4 态后一致率升至 1.042
   - 4 态语义：r1 低波震荡(27.6%) / r2 中波震荡(37.4%) / r3 牛市趋势(14.9%) / r4 熊市阴跌(20.2%)
   - +3 overlay 特殊态：CRISIS / RECOVERY / BREAKOUT

**保留的待讨论问题（v2.0.0 已闭环）**：
- 8态 T+1 预测（BM-SEL-04）是否仍需建设？还是 regime 7维概率 + 策略自身 alpha 已足够？——✅ **已裁定：暂缓建设，后者已足够**（见上裁定）
- 若建，8态概率如何作为策略输入特征（而非直接决策映射）消费？——✅ 已闭环：暂不建设；远期重启时限定"概率输出仅接入仓位微调"
- 分阶段实现计划（Phase1=3态→Phase2=5态→Phase3=8态）是否需要更新为与 regime 7维对齐？——✅ 已闭环：分阶段计划随暂缓建设一并冻结

**2026 预测天花板实证（v0.6.0 补充）**：五轮审查发现 A 股次日预测有**实证天花板**，是决定 BM-SEL-04 是否建设的关键证据：
- **A 股日线价量数据可预测性天花板约 52-53%**——firsh.me 2026-07（9 版架构迭代实验，71 只 A 股 2017-2026 日线，统计检验 p=0.007）：纯价量数据（19 维跨股可比特征：均线比率/MACD/RSI/布林带/量比/多期收益率/OBV/MFI/VWAP 偏离/振幅/波动率）的方向准确率天花板约 52-53%。9 版迭代（v1 静态注意力→v9 DeepSeek MLA 生产级信号）证明**突破口不在架构而在信息源**——注意力机制相对均值池化仅 +2.9-3.5pp（配对 t 检验 p<0.05），跨股训练比单股训练关键（v5 首次稳定超越 LSTM）
- **方向准确率 ≠ 盈利**——同实验关键告诫：错误信号的非对称亏损会吞噬统计优势。52-53% 方向准确率若配以对称止盈止损仍可能亏损（盈亏比 <1 时 53% 胜率不足够）
- **启示对 BM-SEL-04**：若 8态 T+1 预测**仅用价量数据**，将撞 52-53% 天花板，增量价值有限。要突破天花板必须**增加信息源**：① 情绪因子（涨停/跌停数、炸板率、连板高度——见 #21 打板情绪周期）；② 资金因子（北向/游资/主力净流入）；③ 事件因子（政策/财报/重组）；④ 另类数据（龙虎榜、Level2 盘口）。项目 regime 检测器已用 4 态 HMM + 3 overlay（含 CRISIS/RECOVERY/BREAKOUT），本身就是"价量+情绪+事件"的多源融合——8态预测若建设应复用 regime 的多源特征，而非另起炉灶只用价量
- **与 #10 密度预测的关系**：8态预测是"分类"（明天属于哪态），密度预测是"回归+分布"（明天收益的完整 PDF）。密度预测用 RWC（91 号 v0.5.0）可给 VaR/ES 区间保证，比 8态分类更直接对接风控。**建议**：8态预测暂缓建设，先用 regime 7维概率 + RWC VaR/ES 区间覆盖"明天怎么走"的需求；若策略层确需 8态特征，应作为 regime 多源特征的下游消费者而非独立模型

**2026 Wasserstein HMM——regime 标签漂移的直接解决方案（v0.9.0 补充）**：八轮审查发现 **Wasserstein HMM**（arxiv 2603.04441, Boukardagha, Columbia University, 2026-02-21）是"选项之外更好的答案算法"——**直接对应项目 12 号 A2 FAIL（OOS/IS 一致率 0.340，标签对齐 Hungarian 失败）**，是项目 regime 检测器 Phase 2 修复的候选方案：
- **regime 标签漂移问题**——项目 12 号 A2 验证器已 FAIL：HMM 每次 refit 后，状态标签可能"换号"（state 0 在 refit A 是牛市，refit B 是熊市），导致 OOS/IS 一致率仅 0.340，Hungarian 算法标签对齐仍失败。这是 HMM 的**固有 label-switching 问题**（所有 HMM 共有，非项目实现 bug）
- **Wasserstein HMM 三要素**：① **严格因果滚动 Gaussian HMM 估计**（无前视）；② **预测性 model-order selection**——用 one-step-ahead log-likelihood 性能动态选择 regime 数量，**regime 复杂度自适应**（而非固定 4 态或 12 态）；③ **Wasserstein template tracking**——用 2-Wasserstein 距离将当前 Gaussian 分量映射到**持久化 regime 模板**，**解决 label-switching**（每次 refit 后用 Wasserstein 距离匹配历史模板，而非重新编号）
- **实证结果**：跨资产日频 universe，Wasserstein HMM Sharpe **2.18**（vs 等权 1.59 / SPX B&H 1.18），MaxDD **-5.43%**（vs SPX -14.62%）。2025-04 "Liberation Day" 股市抛售期间，策略动态降低股票暴露转向防御资产，削减 peak-to-trough 损失。vs 非参数 KNN 条件矩估计器（同特征+同优化层），参数化 regime 模型**换手率显著更低、权重演化更平滑**——**regime 推断稳定性（尤其身份保持+自适应复杂度控制）是关键**
- **与项目对接**：① 项目 10 号 regime 检测器 spec 12 态 / 实际 4 态 HMM+3 overlay，**Wasserstein template tracking 可直接解决 A2 FAIL 的标签漂移**——在每次 walk-forward refit 后用 Wasserstein 距离匹配历史 regime 模板，而非依赖 Hungarian 事后对齐；② **预测性 model-order selection** 与项目 BIC 扫描（发现 9 态过度细分降为 4 态）互补——BIC 是离线选阶，Wasserstein HMM 是在线自适应选阶，可在 regime 复杂度变化时动态增减状态数；③ **交易成本感知 MVO** 与项目 30 号 BudgetChangeHandler 三级升级互补（Wasserstein HMM 论文用 MVO，项目用 risk parity+Kelly，但 regime 概率→风险节流的路径一致）
- **过度工程评估**：Wasserstein HMM 复杂度中等（滚动 HMM + Wasserstein 距离 + 模板匹配），比项目当前 4 态 HMM 多了模板追踪层，但**直接解决已 FAIL 的 A2 验证器**，属"修复必需"非"锦上添花"。**建议**：列为 12 号 Phase 2 A2 修复的候选方案（与 Hungarian 事后对齐并列评估），非 MVP 必需——MVP 先用当前 4 态 HMM+3 overlay，Phase 2 A2 修复时评估 Wasserstein template tracking 的增量价值

**2026 VRMD（Velocity-Regime Manipulation Detection）——regime 条件化的反面结果（v1.6.0 补充，对应文档 v1.17.0，已评估不整合）**：[arXiv:2608.05373](https://arxiv.org/abs/2608.05373)（2026-08-05）提出 VRMD——Gaussian HMM regime + option-Delta velocity 检测盘中操纵，关键反面结果印证项目 regime 设计决策：
- **核心方法**：① Gaussian HMM 识别市场 regime；② option-Delta velocity（期权 Delta 变化速度）检测盘中价格操纵；③ regime 条件化提升操纵检测精度
- **关键反面结果**：regime 条件化用 recall 换 precision——**precision 上限约 25%**（即 regime 条件化后操纵检测的精确度上限仅 25%，远低于实用阈值）。**regime 细分越多，precision 越低**——印证 regime 过度细分损害而非提升检测质量
- **与项目对接**：对应 #7 regime 层。VRMD 的反面结果**印证项目 4 态 HMM 不过度细分的决策**（BIC 扫描发现 9 态过度细分降为 4 态，OOS/IS 一致率从 0.340 升至 1.042）——regime 条件化不是越多越好，4 态已是精度-鲁棒性的平衡点
- **已评估不整合理由**：① VRMD 的操纵检测场景（option-Delta velocity）不适用于 A 股个人系统（无期权数据接入）；② regime 条件化的反面结果（precision 上限 25%）是**支持现有设计**的反面证据，无需引入操纵检测模块；③ 项目 4 态 HMM+3 overlay 已覆盖 regime 检测需求，VRMD 无增量价值
- **定位**：**已评估不整合**——反面结果支持现有设计（4 态 HMM 不过度细分），无需引入操纵检测

---

## 8. 流动性风险（原约束十）

> 对应 G18（流动性危机处理）｜ ✅ **v2.0.0 裁定：简化采纳（压力退出时间禁开仓 + LVaR 简化式 + A股特有维度）**

**✅ v2.0.0 裁定结论**：

- **本质**：个人小资金的流动性风险不是冲击成本（可忽略），而是"极端情形卖不出"（跌停粘连/停牌/ST 退市）。指标服务于仓位上限与开仓许可，不服务于交易信号。
- **裁定**：① **"超1天→降仓位"阈值修订**——个人单票 <0.1% ADV，正常市况退出 <1 小时，原阈值无意义。改为**压力情景退出时间**：`退出天数 = 持仓 / (ADV × 0.3 压力折扣 × 10% 参与率)`，>1 天→**禁新开仓**（精准拦截微盘股与跌停粘连票，与附录 A.2 微盘流动性枯竭联动）；② **连续评分 + 同源 3 档开关并存**：连续 ILLIQ 评分供 Kelly/risk parity 调权，同源派生 3 档离散开关（正常/降档/禁开仓）供 4 级 Protocol 触发——两套输出同一数据源，不建两套指标；③ **LVaR 简化式**：`LVaR = VaR × √退出天数 + 半价差`（完整 Kyle Lambda 估计器不建，日频 Amihud 已足够）；④ **必须加入 A 股特有维度**：跌停概率、停牌/ST/退市警示——比 ILLIQ 更致命（微盘 Q1 归母净利 -79.25% 退市风险，附录 A.2）；⑤ 做T流动性前置检查：量比>1 且预期振幅>2×单边成本（与 §21 联动）；⑥ 流动性降级模式保留（ILLIQ >历史 90 分位→VaR 升级 LVaR，喂入 30 号 §2.5.4 VaR_95 减仓触发）。
- **施工方案**（liquidity_monitor.py Phase 2 扩展，~100 行）：① 压力退出时间计算+禁开仓开关（复用已有 ADV/ILLIQ 输入）；② LVaR 简化式接入 var_calculator；③ 跌停/停牌/ST 维度从 universe_registry 过滤规则取数（已施工）。集成点：default_risk_manager_orchestrator（已接入 liquidity_monitor）+ 4 级 Protocol 触发链。验证：2026-07 微盘枯竭 episode 回放（附录 A.2）。
- **过度工程审查**：复用已 production 的 liquidity_monitor 扩展，不新建独立流动性系统；Kyle Lambda 完整版/实时评分流显式不建。✅ 通过。

**原始内容**：实时流动性评分+流动性调整VaR(LVaR)+退出时间估算(超1天→降仓位)+做T流动性前置检查+流动性降级模式(VaR退化为标准VaR+0.5%溢价)。

**待讨论问题**：
- 流动性评分的指标构成和计算方法？
- LVaR与标准VaR的切换条件？
- 退出时间估算的模型？
- "超1天→降仓位"的阈值是否合理？
- 做T流动性前置检查的具体规则？

**2026 算法补充（v0.3.0）**：流动性度量 2026 已有标准指标，可直接采用：
- **Amihud 非流动性指标**——2026 低频流动性度量标准（factors.directory 2026 / microalphas 2026-06 / metricgate 2026-06）：`ILLIQ = mean(|r_t| / V_t) × 10^6`，其中 r_t 为日收益率、V_t 为日成交额。值越大流动性越差。仅需日频数据，是 Kyle's Lambda 的高频代理
- **流动性调整 VaR（LVaR）**（GinkGO 2026-05）：`LVaR = VaR + Liquidity_Cost × Position_Size`，其中 `Liquidity_Cost = ILLIQ × Volume × Kyle_lambda`。将流动性成本纳入 VaR，更准确反映小盘股和高波动期风险
- **Kyle's Lambda**（价格冲击系数）：`ΔP = λ × OrderFlow`，OLS 回归可得。高频精确但需 Tick 数据；日频可用 Amihud 替代
- **与 #4 风险模型的关系**：LVaR 是 #4 VaR/ES 辅助监控的**流动性增强版**——当 ILLIQ > 历史 90 分位时，标准 VaR 自动升级为 LVaR（加流动性溢价），喂入 30_multi_strategy §2.5.4 的 VaR_95 减仓触发逻辑
- **退出时间估算**：`退出天数 ≈ Position_Size / (ADV × max_participation_rate)`，max_participation_rate 通常取 5-10%（超 10% 会显著冲击价格）

---

## 9. 数据分层使用（原约束十一）

> 对应 G01（数据与特征层规范）｜ 🔧 **更正引用（v0.2.0）** ｜ ✅ **v2.0.0 裁定：修订采纳（半衰期参数化 + 断裂期降权保留 + Layer4 drift 触发）**

**✅ v2.0.0 裁定结论**：

- **本质**：非平稳市场下"近期相关性"与"regime 覆盖度"的权衡；窗口与衰减是同一枚硬币（指数衰减=软窗口）。
- **裁定**：① **Layer0-4 五层分层采纳**，起始年份（1990/2005/2015/2020/近1年）依据成立（1990=A股开市全历史压力测试、2005=股改后现代市场结构、2015=两融+量化兴起、2020=注册制+机构化加速）；② **权重参数化改为半衰期**：`w(t) = 0.5^(t/HL)`，HL≈2-3 年（与原"近1年=1.0/5年=0.3/10年=0.1"等价但更直观、可调单参数）；③ **结构断裂期（2015 股灾/2018 熊市/2024 微盘崩盘）不剔除**——这是 regime 检测与压力测试最稀缺的样本，训练时降权 50% 保留，并单独作为压力测试集（剔除=丢掉最宝贵的极端 regime 训练信号）；④ **Layer4 加 drift 触发**：特征分布漂移或 IC 衰减超阈值即触发重训，不只按日历滚动（与 decay_monitor 联动）；⑤ 用途分配：Layer2 用途已更正为 regime 检测（v0.2.0 ✅）。
- **施工方案**：半衰期样本权重实现在训练数据加载层（15 号/G01 Phase 2，~40 行：`sample_weight = 0.5 ** (days_ago / (HL*252))`，HL 默认 2.5 年），断裂期清单配置化。注意与已有 10 层数据留存分层（data_retention_contract，数据治理语义）正交——留存管"数据存多久"，样本权重管"训练用多重"，两者不冲突。
- **过度工程审查**：单参数半衰期替代 5 层硬权重=做减法；不建独立样本权重服务。✅ 通过。

**原始内容**：Layer0(1990-至今)仅压力测试；Layer1(2005-至今)体制检测+长周期因子验证；Layer2(2015-至今)8态预测+因子IC验证；Layer3(2020-至今)因子模型训练+Walk-Forward；Layer4(近1年252天)在线训练+实时生成。指数衰减权重：近1年=1.0，5年前=0.3，10年前=0.1。

**🔧 更正（v0.2.0）**：Layer2 引用的"8态预测"应更正为 **regime 检测**（spec 12 态 / 实际实现 4 态 HMM + 3 overlay = 7 维概率，见 §7）。8态 T+1 次日预测（BM-SEL-04）是独立的下游消费者，非数据分层用途的引用对象。

**待讨论问题**：
- Layer0-4的五层分层是否采用？
- 各Layer的起始年份（1990/2005/2015/2020/近1年）的依据？
- 指数衰减权重（1.0/0.3/0.1）是否合理？
- 各Layer的用途分配是否需要调整？（Layer2 已更正为 regime 检测）

---

## 10. 密度预测（原约束十二）

> 已拆为独立讨论稿：[91_density_prediction.md](91_density_prediction.md) ｜ ⏸️ **v2.0.0 裁定：远期维持，MVP 不建**

**⏸️ v2.0.0 裁定注记**：① **维持远期**——MVP 用历史模拟 VaR + feedback_loop 已有简易 conformal 骨架，密度预测完整栈（RWC→LSTM+skewed-t MDN→扩散→QNN）全部 Phase 1+ 以后；② **⚠️ 文档漂移警示**：91 号实际仅 **v0.1.2 骨架（45 行）**，本文档各版本引用的"91 号 v0.4.0 四阶段路线 / v0.5.0 RWC / v0.6.0 Info-Entropic DL+GP / v1.2.0 Lévy / v1.3.0 Cross-Sectional / v1.4.0 Exformer"等内容**均未落盘到 91 号**——下文所有"见 91 号 vX.Y.Z"引用应视为**规划态提案**（真源在本文档），91 号回填前不代表已定稿方案；③ Phase 0 基线候选维持 slow unweighted rolling conformal（Conformal Kelly v0.8.0 实证"慢而稳"最优）；④ 8 态概率"Phase 4 后从 PDF 积分派生"随 §7 暂缓建设一并冻结。

**2026 FCVE（Finite-Sample Conformal Joint VaR-ES）——RWC/TWC 的 joint VaR-ES 扩展（v1.6.0 补充，对应文档 v1.17.0）**：Mathematics 14(15):2847（2026-08-06）提出 FCVE——conformal risk control 耦合 VaR breach frequency 与 breach magnitude，是 91 号 Phase 0 conformal 路径的 joint VaR-ES 扩展：
- **核心创新**：① conformal risk control 同时控制 VaR breach frequency（违反频率）与 breach magnitude（违反幅度）——传统 conformal 只控制覆盖率（frequency），FCVE 同时控制 severity；② non-exchangeable swap-distance bound（非可交换数据的 swap 距离界）+ regime-drift bound（regime 漂移界）+ heavy-tail rate（重尾收敛速率）——三重有限样本保证
- **与 91 号 Phase 0 conformal 路径的关系**：91 号已定 RWC（Regime-Weighted Conformal, Oxford 2026-08-03）为 Phase 0 最优变体（复用项目 regime 检测器，比 TCP 架构原生匹配）。FCVE 是 RWC/TWC 的 **joint VaR-ES 扩展**——RWC 管 VaR 单一分位数的 regime 加权校准，FCVE 管 VaR+ES 联合校准（breach frequency + magnitude）
- **与项目对接**：① 36 号 VaR/ES 当前用历史模拟+参数法，FCVE 的 conformal risk control 是 model-agnostic 校准层（包裹任意分位数预测器）；② FCVE 的 non-exchangeable swap-distance bound 对 A 股 regime 频繁切换场景（政策市）特别适用；③ heavy-tail rate 对 A 股涨跌停重尾场景提供有限样本保证
- **过度工程评估**：FCVE 需 conformal risk control 框架+swap-distance 计算+regime-drift bound+heavy-tail rate 四组件，复杂度高于 RWC（wrapper 模式 ~150 行）。**定位为 Phase 2 远期候选**——RWC 已定为 Phase 0 最优变体（91 号 v0.5.0），FCVE 是 Phase 2 joint VaR-ES 升级路径（当 36 号 VaR/ES 需要 joint breach frequency+magnitude 控制时启用），非 MVP 必需

---

## 11. 仓位管理（原约束十三）

> 对应 G12（仓位算法）/ G13（FirmRiskAggregator）｜ ✅ **已裁定（2026-08-05，30_multi_strategy；v2.0.0 锚点更新至 v2.5.0 + 遗留问题闭环）**

**原始内容**：C-047仓位裁决不可绕过(唯一例外：C-004风控veto)；半Kelly硬上限；漂移再平衡阈值(总仓位±2%/单标的±3%)；再平衡成本-收益规则(收益改善>2×成本才执行)；资金曲线驱动仓位缩放(回撤>5%→总仓位缩减10%，>10%→缩减20%)。

**✅ 裁定结论**：30_multi_strategy §2.1/§7.2 已定模块编号与定位：
- **C-047 → MOD-POS-021（FirmRiskAggregator）+ MOD-POS-001（position_sizing_engine）**：firm 层求和 + 硬上限裁剪（021）+ Kelly 精裁决（001）——C-047 旧"唯一裁决中心"职能由两模块分层承接（§7.2 depgraph 已登记）【v2.0.0 注记：AI_review_instructions.md 写"C-047→MOD-POS-001"系不完整映射；module_translation_registry / battle_map_positioning / sell_conflict_arbitrator blueprint 仍以 C-047 描述现行决策链，属旧架构描述未清理，需 G12/G13 对账时同步修订】
- **半 Kelly 定位**：**firm 层精裁决工具**（非全局硬上限）——StrategyBook 用 risk parity/等权（不用 Kelly），Kelly 仅在 firm 层组合级使用【v2.0.0 锚点更新：30 号 v2.5.0 已升级为 Fractional Kelly 25-50%（Phase 1）→ Bayesian Kelly（Phase 2）→ Conformal Kelly（Phase 3 远期）三档演进，fraction 待 31 号 G12 标定】
- **资金曲线驱动仓位缩放 → 4级回撤 Protocol**（§2.5）：回撤 8%/15%/20%/25% 四级触发，替代原"回撤>5%→-10%，>10%→-20%"线性规则
- **模块编号体系**（§7.2）：MOD-POS-020（StrategyBook）/ MOD-POS-021（FirmRiskAggregator）/ MOD-PA-007（RegimeMetaAllocator）/ MOD-POS-022（BudgetChangeHandler）

**保留的待讨论问题（v2.0.0 已闭环）**：
- 漂移再平衡阈值（±2%/±3%）的依据？——✅ **已闭环**：30 号 §2.4 实际采用 ε_pos=5% 收敛容差（Tier2→Tier3）+ no-trade 半带公式 `b*=[3cσ²/(2λ)]^(1/3)`（Phase 2 候选）替代 C-047 旧阈值；代码侧 position_drift_monitor（MOD-POS-003）已施工漂移检测，阈值在配置。±2%/±3% 旧值**标 deprecated**（与 Model A 分层架构不兼容——策略层粗仓位天然有波动，±2% 会过度交易）
- 再平衡成本-收益规则（>2×成本）的阈值是否合理？——✅ **已闭环**：no-trade 半带公式即成本-收益规则的理论化（半带宽度由成本 c、波动 σ、风险厌恶 λ 内生决定），Phase 1 用 ε_pos=5% 固定容差已隐含"小漂移不再平衡"；">2×成本"线性规则**标 deprecated**

**2026 Kelly 分数选择实证补充（v0.7.0）**：六轮审查发现 Kelly 分数（full/half/quarter）的选择 2026 已有充分实证，项目 firm 层"半 Kelly 精裁决"可进一步细化：
- **Kelly 最优增长率 = ½ Sharpe²**（marketmaker.cc 2026-06-23 / elearnmarkets 2026-08-06）：连续形式 `f* = μ/σ²`，最大几何增长率 `g(f*) = SR²/2`。**启示**：Sharpe 翻倍→增长率 4 倍；项目提升 Sharpe 比提升 Kelly 分数更有效
- **Half-Kelly 性价比**（marketmaker.cc 2026-06-23）：half-Kelly 捕获 75% 增长率@50% 波动率。**1/4 Kelly** 捕获 95% 增长率@显著降回撤——Lisa Chang 案例（signalpilot 2026）：full Kelly 16.8%→6 连败（0.1% 概率）→-62% 回撤；切 1/4 Kelly（4.2%）→6 个月 +56% 恢复，MaxDD -12%（vs -62%）。**同 edge，survivable variance**
- **drawdown 恢复数学**（straderz 2026-08）：-20% 需 +25% 恢复，-50% 需 +100%，-90% 需 +900%。**启示**：4 级回撤 Protocol Level 4（25%）需 +33% 恢复，已接近"非常严重"档位——Kelly 分数选择直接影响是否触发 Level 4
- **与项目对接**：项目 firm 层"半 Kelly 精裁决"可进一步细化为**动态分数 Kelly**——① 低波动 regime（r1/r2）用 half-Kelly（75% 增长）；② 高波动/CRISIS overlay 用 quarter-Kelly（95% 增长+回撤控制）；③ 与 91 号 v0.6.0 Information-Entropic DL+GP 的"微分熵→Kelly"统一（低熵→half-Kelly，高熵→quarter-Kelly）。**待 G12 细化**：动态分数 Kelly 的 regime→分数映射表

**2026 Conformal Kelly 实证补充（v0.8.0 极新）**：七轮审查发现 2026-08-02 发布的 **Conformal Kelly**（arxiv 2608.01494, ACS Athens）是"选项之外更好的答案算法"——将 Conformal Prediction 区间作为 fractional Kelly 的缩放因子，是 91 号 v0.6.0 RWC（Phase 0）与 Information-Entropic DL+GP（Phase 1.5）之间的**原生桥接**：
- **Conformal Kelly 核心方法**：用 75% conformal 区间宽度缩放仓位——区间变窄→加仓，区间变宽→缩仓。6 年开发窗口（2016-2021）含交易成本+1 日执行延迟+严格杠杆上限，**28.5% 年化净对数增长，Sharpe 1.34，MaxDD 27.7%**（vs S&P 500 B&H 15.9%，同杠杆被动组合 21-22%）。区间覆盖率 74.8% vs 75% 目标（达标）
- **⚠️ 反直觉关键发现**：**每加快自适应/regime 加权的 tweak 反而损失 0.7-5.3pp 年化增长**。最佳表现是**最简方法：slow, unweighted, per-asset rolling conformal quantiles**。原因：当区间用于"仓位缩放"而非"单点预测描述"时，**宽度的稳定性比局部锐度更重要**——过快自适应会因 outlier 过度反应导致仓位抖动。conformal width 比教科书标准差年化多 2.1pp 增长
- **drawdown dial 风控**：当 conformal 区间下行连续失误远超历史率时，视为"模型已坏"信号→降杠杆。开发窗口 MaxDD 27.7%→20.3%，Sharpe 提升，rank-based p=1/41≈0.024（beat 所有 40 个 placebo 版本）
- **lockbox 验证**：2022+ 数据密封+预注册配置+解释规则。OOS 全窗口校准保持（0.745 coverage vs 0.750 target），但增长未保持（两配置 8.5%/7.0% 年化，低于被动基准）——**告诫：开发窗口 Sharpe 1.34 不保证 OOS 复现，Conformal Kelly 的价值在校准+风控而非增长**
- **与 91 号 v0.6.0 RWC 告诫的双向验证**：91 号 v0.6.0 已记录 RWC"压力期残余 2.29% exceedance"+"base 越迟钝 regime 加权越有价值"，Conformal Kelly 进一步实证"每加快自适应反损增长"——**两篇独立研究共同指向：慢而稳的 conformal 胜过快而自适应的 conformal**。项目 RWC 启动时应优先用 slow unweighted rolling conformal 作 baseline，再评估 regime 加权的增量价值
- **与项目对接**：① 91 号 Phase 0 RWC 启动时，**先实现 slow unweighted per-asset rolling conformal 作 baseline**（Conformal Kelly 实证此最简方法最优），再评估 RWC regime 加权的增量；② 项目 firm 层 Kelly 精裁决可用 Conformal Kelly 的"区间宽度→仓位缩放"作为动态分数 Kelly 的**数据驱动实现**（替代手工 regime→分数映射表）；③ drawdown dial 是 4 级回撤 Protocol 的**预测性补充**——4 级 Protocol 是事后硬触发，drawdown dial 是事前软预警（conformal 连续下行失误→降杠杆，不等回撤实际发生）

**2026 轻量级 Kelly 校准补充（v0.8.0）**：七轮审查发现 91 号 v0.6.0 Information-Entropic DL+GP（GP 微分熵→Kelly）是"重"方案（需 CNN-Transformer+GP 全栈），2026 有两个"轻"方案可直接用于项目 firm 层 Kelly 精裁决，作为 Phase 0.5 介于 RWC 与 Info-Entropic DL+GP 之间：
- **Bayesian Kelly Criterion**（Sukhov 2026, GitHub sergeisukhovmkt/​Bayesian-Kelly-Criterion-with-Parameter-Uncertainty）：`f* = (p̄ - (1-p̄)/b) · n_eff/(n_eff+κ)`，其中 p̄=α/(α+β) 为 Beta 共轭先验后验均值、n_eff=α+β 为有效样本量、κ 为正则化强度。**核心价值**：样本量少时自动收缩到 0（n_eff≪κ→f*≈0），样本量多时逼近经典 Kelly（n_eff≫κ→f*≈经典 Kelly）。参数不确定性直接编码进仓位，无需 GP 全栈
- **RMSE 校准 Kelly**（MarketRegimeNet, GitHub lu8848 2026-03，开源）：`f* = 2p-1; α = max(0, 1 - c·RMSE/|f*|); f = α·f*`，其中 c 为保守系数（1.0-2.0 可调）、RMSE 为预测器均方根误差。**核心价值**：低置信信号（RMSE 大）自动近零分配，无硬概率阈值——比"置信度<60%→不交易"的硬切更平滑
- **三方案分工**（v0.8.0 更新 91 号实现路径）：① Phase 0 RWC（区间保证，零训练）；② **Phase 0.5 Bayesian/RMSE Kelly**（轻量级 Kelly 校准，仅需胜率+样本量/RMSE，~20 行代码）；③ Phase 1 LSTM+GMM（完整密度）；④ Phase 1.5 Information-Entropic DL+GP（统一框架·密度+Kelly+CVaR）。Phase 0.5 是 Phase 0 区间→Phase 1.5 完整密度的中间档，用胜率不确定性校准 Kelly 而无需建模完整分布

---

## 讨论优先级建议（v2.0.0 更新：全量裁定完成，此表转为施工优先级）

> **v2.0.0 更新**：21 项全部裁定完成（✅ 维持 4 项+新裁定 12 项+合并 1 项+暂缓/远期 2 项+待用户裁定 P-1~P-5）。原"讨论优先级"转为**施工优先级**——指导 Phase 1/2 施工排期。

| 施工优先级 | 主题 | v2.0.0 裁定 | 施工动作 |
|:------:|------|:----:|------|
| — | #3 组合构建 / #4 风险模型 / #6 回测门禁 / #11 仓位管理 | ✅ 已裁定维持 | 无新增施工；G12/G13/G14 对账项跟进（阈值口径/C-047 旧描述清理/52号索引漂移） |
| P1 | #5 成本模型 | ✅ 简化采纳 | cost_model_registry 增补做T成本条目 CST-T0-001 + 最低佣金5元建模确认（Phase 1） |
| P1 | #13 基准设计 | ✅ sleeve 级多基准 | benchmark_registry 增补中证1000/2000/万得全A 条目（Phase 1，~30行 YAML） |
| P1 | #19 大额下单 | ✅ 默认限价单 | ex_sor 选择器默认策略配置项调整 + 打板专用执行路径确认（Phase 1，40号已施工范围内） |
| P2 | #2 因子IC | ✅ 双轨采纳 | BHY FDR 校正 ~80行 + 滚动分位嵌入 decay_monitor（Phase 2） |
| P2 | #8 流动性 | ✅ 简化采纳 | liquidity_monitor 扩展：压力退出时间+LVaR简化式+跌停/ST维度 ~100行（Phase 2） |
| P2 | #9 数据分层 | ✅ 修订采纳 | 半衰期样本权重 ~40行（Phase 2，15号/G01） |
| P2 | #15 资产分级 | ✅ 两维精简 | universe_registry 增补准入×数据覆盖维度字段+流通市值分层计算字段（Phase 2） |
| P2 | #16 成功指标 | ✅ 修订采纳 | 生存线监控落码（55号 KPI 监控施工）；健康/卓越线实盘 6-12 月后校准（Phase 2+） |
| P2 | #17 行为边界 | ✅ choke point | 单一订单出口架构验证（40号范围内）+ YAML 规则归并（Phase 2） |
| P2 | #18 资产覆盖 | ✅ 轻量 IM | Instrument Master 轻量表（复用现有 schema，盘前 xtdata 同步，Phase 2） |
| P2 | #20 工程细节 | ✅ 逐项裁定 | 策略指纹库+DTW（echo-guard Phase 2）；B-008/B-012/B-013 归治理配置闭环 |
| P2 | #21 做T | ✅ 受约束 overlay | 四规则配置化（sizing/regime过滤/失败处置/冲突管理，Phase 2，做T策略配置项） |
| P2 | #1 策略类型 | ✅ 修订采纳 | 零新增施工——新增策略强制族归属声明（治理流程，即时生效） |
| P2 | #14 PIT | ✅ 确认已施工 | deliberate future-date 泄漏测试自动化（Phase 2 增强，BT-10 体系内） |
| ⏸️ | #7 T+1 8态 / #10 密度预测 | ❌ 暂缓/远期 | 不施工（重启条件见 §7；91号待回填） |
| 📝 | P-1~P-5 选项收敛 | 待用户裁定 | 建议方向见「待定问题」节，用户确认后按方向执行 |

---

## 12. 成功指标中的交易参数（原§9健康线+灰色地带）

> 源自宪章§9系统级成功指标。宪章保留成功指标的结构（生存/健康/卓越/失败四档），但具体交易参数移入此处待讨论校准。｜ ✅ **v2.0.0 裁定：并入 #16，线性收紧规则 deprecated**

**✅ v2.0.0 裁定结论**：

- **IC 阈值作为成功指标**：随 #2 双轨化（静态地板+BHY FDR+ICIR≥0.5），不再单列。
- **"每+1%→仓位-2%"线性收紧规则：标 deprecated**——已被 4 级回撤 Protocol（8/15/20/25% 离散档位+恢复机制）替代。离散档位优于线性规则：① 触发点明确可审计（线性规则在连续回撤下每日微调仓位，产生不必要的换手成本）；② 恢复机制防抖动（线性规则无 hysteresis，回撤在阈值附近震荡会反复调仓）。灰色地带 15-25% 区间即 Level2~Level4 覆盖域，无需另设规则。
- **"20%触发紧急告警"与 4 级 Protocol Level 3（20% 停仓）一致** ✅——告警是 Level 3 动作的配套通知，无冲突。
- **审批频次阈值（3次通知/4次审视）**：保留为 C-031 信任模型的默认配置，上线后按实盘审批数据校准（Phase 2）。第一性原理：审批频次阈值的本质是"AI 置信度退化预警"，合理阈值只能从实盘审批分布反推，拍脑袋值作默认、实盘校准是标准做法。

**原始内容**：
- 健康线IC阈值：因子池分类平均IC | 量价>0.03/基本面>0.02/另类>0.025
- 灰色地带：回撤15%-25%→C-004自动收紧(回撤每+1%仓位上限-2%)，20%触发紧急告警
- 灰色地带：审批2~5次/天→3次通知提醒，4次触发C-031信任模型审视

**待讨论问题**：
- IC阈值作为成功指标：与#2因子分类IC阈值合并讨论，阈值依据需回测验证
- "每+1%→仓位-2%"线性收紧规则：与#11资金曲线驱动仓位缩放(回撤>5%→-10%，>10%→-20%)和4级回撤Protocol如何统一？
- "20%触发紧急告警"：与4级Protocol Level 3（20%）是否一致？
- 审批频次阈值（3次通知/4次审视）：依据是什么？

---

## 13. 基准设计选择（原§3约束二）

> 基准选择会随市场发展和投资策略变化，不是硬边界。｜ ✅ **v2.0.0 裁定：sleeve 级多基准，废弃 60/40 拼合基准**

**✅ v2.0.0 裁定结论**：

- **本质**：基准的唯一功能是"刻画策略可被动获得的机会集（opportunity set）"——超额=主动部分。基准与策略持仓风格错配，测出来的 alpha 就是噪音。打板策略对标沪深300，等于用大盘蓝筹尺量小票情绪策略，超额虚高且无信息量。
- **裁定**：① **废弃 60%沪深300+40%中证500 拼合基准**（两边都不贴合，属伪精确）；② **采纳 sleeve 级多基准**：打板/事件驱动→中证2000（小盘机会集，2026 私募中证2000指增近1年平均超额 17.41% 是主战场）；多因子→中证1000（若偏小盘）或万得全A（全市场选股）；③ **沪深300 保留为大盘宽基锚**（绝对超额参照+与公募对比的统一口径）；中证A500 并列观察（2026 公募基准改革后 A500 是机构新锚，A500 ETF 成交额已超沪深300 ETF，但个人系统 sleeve 级基准优先）；④ **组合层仅报绝对收益+最大回撤**，不强行设相对基准（多 sleeve 拼合后相对基准无意义）；⑤ Smart Beta 基准暂缓（个人系统过度——v0.4.0 Barra 归因+Smart Beta 双层方案降级为远期，style-adjusted alpha 概念保留为分析视角）；⑥ 资产覆盖扩展（港股/期货）后按 sleeve 各自增设基准，不建统一全球基准。
- **施工方案**：benchmark_registry.yaml 增补中证1000/中证2000/万得全A 条目（~30 行 YAML，Phase 1）；策略注册表条目关联 sleeve 基准（strategy_registry 已有 BMK-INDEX-001 引用机制）。验证：回测报告同时输出 sleeve 基准超额+组合绝对收益。
- **过度工程审查**：仅注册表条目增补，无新架构；Smart Beta/Barra 归因降级远期。✅ 通过。

**原始内容**：相对基准=沪深300；超额收益=组合收益-沪深300收益；组合基准=60%沪深300+40%中证500(仅绩效评估)。

**待讨论问题**：
- 沪深300是否是最合适的相对基准？中证A500、万得全A等替代？
- 60/40的沪深300+中证500组合基准配比依据？
- 资产覆盖扩展（港股、期货）后基准是否需要调整？

**2026 算法补充（v0.4.0）**：基准设计 2026 的核心进步是**归因驱动的基准选择**——先分解 alpha 来源，再选对应基准：
- **Barra 式归因**——KTD-Fin（arxiv 2605.28359, Tsinghua+Stepfun, 2026-05）：将组合收益分解为 market beta + style exposure + stock-selection alpha。关键发现：LLM 交易 agent 的"alpha"在泄漏控制后**大部分是被动市场/风格暴露**，persistent stock-selection alpha 有限。**启示**：如果项目组合的"超额收益"主要是小盘/低波风格暴露，应对标风格基准而非沪深300
- **Smart Beta 基准**——中证指数 2026-07：多因子策略指数体系（红利多因子 932315 / 价值多因子 931052 / 质量多因子 930939 / 沪深300质量成长低波 931375）。如果策略有明确风格倾斜，应用对应 Smart Beta 指数作基准，而非宽基
- **建议**：基准分两层——① 宽基层（沪深300，衡量绝对超额）+ ② 风格层（按策略风格选 Smart Beta，衡量 style-adjusted alpha）。只有 style-adjusted alpha > 0 才是真正的选股能力

---

## 14. PIT一致性实现方案（原§3约束三）

> PIT原则是量化回测铁律（防止前视偏差），原则本身不变，但实现方案会演进。｜ ✅ **v2.0.0 裁定：确认已施工主干，补 2 项 Phase 2 增强**

**✅ v2.0.0 裁定结论**（对照已施工设施逐项闭环原待讨论问题）：

- **PIT 数据架构实现方案**：✅ 已施工——`data/pit_query.py`（announce_date<=query_time + LIMIT 1 BY 取查询时点最新版本 + embargo_clause + AS OF JOIN，白名单财务表）+ `backtest/core/pit_manager.py`（PIT 三公理 + pit_consistency_test）。**采纳"时间戳标注+AS OF JOIN"路线，不建独立 PIT 数据库**（与已施工一致）。
- **财报双日期问题**：✅ 已覆盖——A 股语义映射：`first_filed ≈ announce_date`（公告日），pit_query 用 announce_date 过滤即"必须用 first_filed join"的等价实现。**重述泄漏双值存储**：✅ 等价覆盖——ClickHouse ReplacingMergeTree 版本语义下，"取查询时点最新版本"= 当时的 original_value，最新修订值通过全量刷新可得，restated 标志可由版本数>1 派生。
- **特征版本管理机制**：✅ experiment_tracking 模块已施工（config/models/query）；配合 factor_registry 版本字段。"旧版保留≥5年"**采纳**（监管+复现需要，ClickHouse 存储成本可忽略）。
- **PIT 自动化校验**：🟧 Phase 2 增强——deliberate future-date test（label_date=tomorrow 确认零特征 join）自动化纳入 BT-10 体系；时间精度陷阱（date vs timestamp 粒度统一用 date_trunc）加入 PIT 校验 checklist。
- **施工方案**：仅 Phase 2 泄漏测试自动化增强（~50 行测试用例，tests/backtest/ 体系内）。其余无新增施工。
- **过度工程审查**：确认现有实现等价覆盖 2026 标准做法，不引入新组件。✅ 通过。

**原始内容**：因子统一定义-计算-存储-服务(Single Source of Truth)；训练数据Day T因子值=Day T收盘可计算值(PIT铁律)；特征版本管理(逻辑变更时训练集与推理版本号一致，旧版保留≥5年)。

**待讨论问题**：
- PIT的数据架构实现方案？（Point-in-Time数据库 vs 时间戳标注）
- 特征版本管理的具体机制？
- "旧版保留≥5年"的保留策略是否合理？
- PIT一致性校验的自动化方案？

**2026 算法补充（v0.4.0）**：PIT 实现 2026 已有精确的量化研究和成熟模式，项目 BT-10 PIT 模块应直接采用：
- **财报双日期问题**——tradevodata 2026-07（313,562 行实测）：每条基本面数据有**两个日期**：period_end（报告期末，数字描述的期间）vs first_filed（首次发布日，数字可知的时刻）。**平均差距 43 天**（SEC 大型加速申报人 60 天，加速 75 天，其他 90 天）。用 period_end join = 给回测 43 天"免费预知"。**必须用 first_filed join**
- **重述泄漏（Restatement Leak）**——tradevodata 实测 18,539 行（5.9%）被后续申报修订 >0.5%。解法：存储 `original_value`（首次报告值，回测用）+ `latest_value`（最新修订值，实时筛选用）+ `restated` 标志。A 股同理：年报修正、会计差错更正
- **Observation Spine 模式**——ml-digest 2026：先构建"观测脊"（entity × as_of_time 主键），所有特征相对 as_of_time 计算（latest-known-value 用 AS OF JOIN，window aggregate 用 `WHERE feature_time ≤ as_of_time`）。标签单独计算，必须 `label_time > as_of_time`
- **时间精度陷阱**——theneuralbase 2026-04：label_date 是 date 但 transaction_time 是 timestamp 时，`cast('date')` 截断到午夜会掩盖日内泄漏。必须 `date_trunc('day', ...)` 显式统一粒度。**泄漏检查必须在所有 join 之后**（上游单个泄漏 join 感染整个特征行）
- **项目对接**：BT-10 PIT 模块（module_translation_registry 已登记）应实现：① 财报用 first_filed 而非 period_end；② original_value/latest_value 双值存储；③ observation spine + AS OF JOIN；④ 自动化泄漏检查（deliberate future-date test：label_date=tomorrow，确认零特征 join）

---

## 15. 资产分级标准（原§4 P0-P3）

> 当前P0-P3自制分级混合了交易准入、数据覆盖、研究范围三个维度，需按专业标准重设计。｜ ✅ **v2.0.0 裁定：两维精简采纳（准入×数据覆盖），P0-P3 deprecated，研究范围维暂缓**

**✅ v2.0.0 裁定结论**：

- **本质**：分级的目的是驱动差异化行为（能不能交易/数据订多频/研究跟不跟），维度数应与行为决策数匹配。3-5 策略小系统只有两类行为决策：交易准入（风控拦截）+ 数据订阅（成本决策）——第三维"研究范围"对 3-5 策略小系统是过度设计。
- **裁定**：① **采纳两维**：交易准入（eligible/restricted/prohibited——直接驱动风控拦截）+ 数据覆盖（real-time/EOD——直接驱动订阅成本，miniQMT 实时流与盘后批量分层）；② **研究范围维暂缓**——用 universe_registry 已有 static/dynamic/rule_based 标签字段承载（已施工），不建独立维度；③ **P0-P3 自制分级标 deprecated**（语义混叠：P0"交易级"≈eligible、P1"待验证"≈candidate 状态、P2"背景级"≈EOD 数据——全部可由两维+universe 标签等价表达，且不映射任何执行动作）；④ **流通市值 6 级分层采纳为交易准入内的子维度**（"市值定调子"原则：同一信号在不同市值段含义不同，是打板/信号解释的第一道筛子——1000亿+/300-1000/100-300/50-100/20-50/<20亿）；⑤ 与 #18 关系确认：本节定义分类框架（两维+市值子维度），#18 定义品种清单，互补不变。
- **施工方案**（Phase 2）：universe_registry 增补 `eligibility`（eligible/restricted/prohibited）与 `data_tier`（realtime/eod）两字段 + 流通市值分层计算字段（数据已有，~30 行计算+登记）；eligible 判定规则复用 UNI-RULE-001 已有过滤链（剔 ST/退市风险/次新/低成交额）。
- **过度工程审查**：三维全套+P0-P3 双轨并行被显式拒绝（减法）；市值分层是计算字段非新数据源。✅ 通过。

**原始内容**：
- P0 交易级：直接下单
- P1 待验证交易级：技术可交易，是否交易由回测决定
- P1 信号级：不买但盯着看
- P2 背景级：盘前拉取一次
- P3 远期：预留接口

**专业机构做法**（参考）：
- 交易准入维度：eligible / restricted / prohibited
- 数据覆盖维度：real-time / delayed / EOD
- 研究范围维度：investment universe / tracking universe / research universe

**待讨论问题**：
- 采用三维度分离还是单一维度？
- 各维度的具体分类标准？
- 与现有P0-P3标签的映射关系？

**2026 算法补充（v0.4.0）**：资产分级 2026 有 A 股专用的市值分层标准，应作为交易准入维度的第一道筛子：
- **流通市值 6 级分层**——CSDN 2026-08-08（极新）：A 股按**流通市值**（非总市值）分 6 档，每档玩家结构和波动逻辑不同：

  | 流通市值 | 角色 | 主要玩家 | 波动逻辑 |
  |---|---|---|---|
  | 1000 亿+ | 超级大蓝筹 | 公募/社保/北向 | 业绩驱动，波动小 |
  | 300-1000 亿 | 行业头部/白马 | 北向/公募核心 | 行业景气驱动 |
  | 100-300 亿 | 成长股/二线龙头 | 机构覆盖中等 | 成长+估值博弈 |
  | 50-100 亿 | 中小盘 | 机构覆盖少 | 共识弱、流动性中等 |
  | 20-50 亿 | 小盘(游资主场) | 游资 | 题材/资金驱动，波动大 |
  | <20 亿 | 超小盘 | 散户/游资做妖 | 高风险，主力不太进 |

- **"市值定调子"原则**——CSDN 2026-08-08：同一信号在不同市值段含义不同。大蓝筹"放量大涨"=机构业绩建仓；小盘"放量大涨"=游资拉题材准备出货。**不先看市值就把两种信号喂同一模型 = 训练精神分裂的判断器**。流通市值是第一道筛子，排在所有技术指标之前
- **与三维度分级的融合**：市值分层是"交易准入维度"的子维度（eligible 内再按市值分档），与数据覆盖维度（real-time/delayed/EOD）、研究范围维度（investment/tracking/research universe）正交。建议：交易准入 = eligible/restricted/prohibited × 市值6档；P0-P3 映射为研究范围维度

---

## 16. 系统级成功指标（原§9全文）

> 具体收益率/Sharpe/回撤阈值均为拍脑袋数字，不属于硬边界。宪章使命已定义"资产长期复利增长"为成功标准。｜ ✅ **v2.0.0 裁定：修订采纳（生存线数值下调 + 健康/卓越线实盘校准 + 五层框架映射）**

**✅ v2.0.0 裁定结论**：

- **本质**：KPI 阈值的意义是触发"继续/降仓/关停"决策，不是许愿。拍脑袋的绝对数值在 regime 切换时必然失效；2026-07 量化双杀后，"年化超额≥10%"是头部机构水平，设为生存线会误杀可用策略。
- **2026 实证锚点**：私募股票量化多头 2026 上半年平均超额仅 3.11%（去年同期 14.17%）；公募 300 指增 YTD 超额 3.00%；头部 50 亿+私募超额 5.51%；Sharpe 1.0-2.0 为专业合格线，>3.0 持续反而可疑；回测 Sharpe 2.0 实盘通常衰减至 1.0-1.5。
- **裁定**：① **生存线修订**：滚动 12 个月超额>0 且 MaxDD<15% 且 Sharpe≥0.8（替换原"年化超额≥10%、Sharpe≥1.0"）；失败指标维持（连续 6 个月亏损/回撤>25% 与 4 级 Protocol Level4 一致✅）；② **健康线/卓越线暂缓定死**——上线时只锁死生存线（风控属性），运行 6-12 个月（≥30 个收益观测点，统计显著性下限）后用实盘分布校准；③ **五层评估框架采纳为结构**（存活→边际→效率→鲁棒→部署，v0.5.0 已补），原三档映射进前三层：存活=生存线（MaxDD 三维度：深度+持续时间+恢复时间）、健康=边际（Profit Factor>1.5+Expectancy>0）+效率（Sharpe/Calmar）、卓越=鲁棒（跨 regime 稳定性+OOS 一致性）；④ **打板 KPI 单列**：炸板率、隔日溢价、胜率（打板 alpha 结构与多因子不同，不共用超额阈值）；⑤ 成功指标分阶段设定：MVP 期=生存线+失败指标；完整版=五层全量（实盘校准后）。
- **施工方案**（Phase 2，55 号监控文档施工范围内）：生存线+失败指标监控落码（复用 decision_gate 偏差告警通道+alert_rules.yaml 框架，~100 行）；健康/卓越线定义为配置占位，实盘校准后启用。验证：用回测数据回放生存线触发逻辑。
- **过度工程审查**：砍掉拍脑袋阈值=减误报；五层框架是评估结构非新系统；不建独立 KPI 平台（复用 alert_rules）。✅ 通过。

**原始内容**：
- 生存线：年化超额≥10%、Sharpe≥1.0、回撤<15%、uptime>99.9%、审批<2次、Sharpe偏差<30%
- 健康线：年化超额≥15%、Sharpe≥1.5、回撤<10%、A/B周期<6周、IC达标、准确率>60%、修复率>90%、误触发<5%
- 卓越线：年化超额≥25%、Sharpe≥2.0、回撤<8%、容量>3x
- 失败指标：连续6个月亏损、回撤>25%、停机>5分钟/月、审批>5次/月
- 灰色地带：回撤15-25%按4级Protocol、停机50秒-5分钟加强监控、审批偏高触发审视

**待讨论问题**：
- 阈值需要历史回测验证，不能拍脑袋
- 生存/健康/卓越三档划分是否合理？
- 失败指标的阈值依据？
- 成功指标是否应该分阶段设定（MVP vs 完整版）？

**2026 算法补充（v0.5.0）**：成功指标 2026 已形成多层评估体系，比原"生存/健康/卓越"三档更系统：
- **五层评估框架**——nexusfi 2026-06：① 存活层（MDD 深度+持续时间+恢复时间）→ ② 边际层（是否有 edge：Profit Factor>1.5, Expectancy>0）→ ③ 效率层（风险调整：Sharpe/Sortino/Calmar）→ ④ 鲁棒性层（跨 regime 稳定性、OOS 一致性）→ ⑤ 可部署层（容量、延迟、操作可靠性）。**每层回答不同问题**，不能跨层比较
- **关键指标阈值共识**（LedgerMind 2026-05 / tradingwyckoff 2026-01 / nexusfi 2026-06）：
  - Sharpe <1.0 差 / 1.0-2.0 好 / 2.0-3.0 优 / **>3.0 可疑（过拟合）**——BarclayHedge 对冲基金均值仅 0.89
  - Calmar >2.0 好 / >3.0 优 / **>5.0 极罕见（可能过拟合）**
  - Profit Factor >1.5 好 / 1.5-2.0 良 / **趋近 1.0 = edge 消失**
  - MDD 三维度：**深度**（百分比）+ **持续时间**（Time Under Water）+ **恢复时间**——不能只看深度
- **单一指标陷阱**——nexusfi 2026-06：Sharpe 2.0 在 6 个月低波动窗口好看，从未经历 VIX 飙升 ≠ 好。75% 胜率但平均亏损 4×平均盈利 = 负期望。**必须多维交叉验证**
- **与项目 4 级回撤 Protocol 的对接**：原"生存/健康/卓越"三档可映射为五层框架的前三层（存活=MDD+4级Protocol / 健康=边际+效率 / 卓越=鲁棒性），后两层（鲁棒性+可部署）需补充分别对应 #6 回测门禁（OOS 一致性）和 G22 执行层（容量+延迟）

---

## 17. 行为边界重构（原B-002~B-005）

> 这4条从§5移除，不是因为概念错误，而是框架不专业——把风险参数、交易所规则、架构原则包装成"禁止AI做"的行为禁令。机构做法是通过系统设计让这些事架构上不可能发生。｜ ✅ **v2.0.0 裁定：拒绝 OPA/Rego，采纳 choke point + 配置化 YAML 规则**

**✅ v2.0.0 裁定结论**：

- **本质**：B-002~B-005 是"永不成立"约束，需要的是**架构上的不可绕过性**（所有订单唯一出口+默认拒绝），而非策略语言表达力。机构标准做法（SEC 15c3-5 / MiFID II RTS 6 强制盘前检查）：pre-trade risk gate 作为订单路径上同进程单一 choke point——"不存在任何绕过网关到达交易所的路径"。
- **裁定**：① **拒绝 OPA/Rego**——OPA 是云原生多团队多服务授权治理的事实标准，但对单机单人 Python 系统引入 sidecar 进程+Rego 学习曲线，属杀鸡用牛刀（v0.4.0 的 PaC/OPA 建议**修订降级为远期**：若未来演化为多进程微服务再议）；② **采纳 choke point 方案**：唯一 OrderGateway 持有 xttrader 句柄，策略层不 import 交易接口——物理不可绕过；规则用 YAML 声明（杠杆上限/集中度/交易时段白名单/单日限额）+ Pydantic 校验 + Gateway 内顺序检查链 + **默认拒绝**；每次拒绝写结构化审计日志；③ **已施工等效设施确认**：43 门禁引擎 + risk_limits + default_position_limit_checker + g7_position_limits.yaml（集中度/仓位）+ trading_session（时段）+ programmatic_trading_guard + cancel_rate_guard + price_cage——B-002~B-005 语义已**大部分覆盖**，缺口=单一订单出口的架构确认。
- **原待讨论问题闭环**：杠杆/集中度上限→risk_limit_registry（limit_type=leverage/concentration 已登记）+ g7_position_limits；交易时段校验→ex_core/trading_session.py（已施工）；不可绕过保证→choke point 架构（见施工方案）。
- **施工方案**（Phase 2）：① 验证 40 号执行层（G22 已施工 commit 015826ae）所有下单路径收敛到单一出口（架构检查项，若非单一出口则归并）；② 将散落的硬编码限额（position_limit_enforcer 单票≤5% NAV 等）归并到 risk_limit_registry YAML 声明式配置。
- **过度工程审查**：拒绝 OPA=做减法；复用已有门禁体系。✅ 通过。

**原始内容**：
- B-002 禁止AI使用超过杠杆上限 → 应在风险模型中设定，由风控引擎强制
- B-003 禁止AI对单一标的集中度超上限 → 应由回测和风险模型决定，不硬编码
- B-004 禁止AI在非交易时段提交订单 → 交易所规则，执行层技术校验
- B-005 禁止AI绕过风控引擎直接下单 → 架构原则，风控引擎在关键路径

**待讨论问题**：
- 杠杆/集中度上限应放在风险模型的哪个模块？（30_multi_strategy_concurrency的FirmRiskAggregator？）
- 交易时段校验放在执行层的哪个组件？
- 风控引擎在关键路径的架构设计如何保证不可绕过？

**2026 算法补充（v0.4.0）**：行为边界 2026 的标准实现是 **Policy-as-Code（PaC）**——把"禁止 AI 做 X"从文档规则变为可执行代码，在订单提交前自动拦截：
- **OPA（Open Policy Agent）+ Rego**——2026 事实标准（GeekWorkBench 2026-03 / IBM 2026-06 / cloudification 2026-05）：用声明式 Rego 语言编码风控规则，OPA 引擎在交易执行前评估每个订单请求，违反规则自动 deny + 记录审计日志。CNCF 毕业项目，Netflix/Capital One 在用
- **金融级 AI Agent 权限矩阵**——CSDN 2026-05（NIST SP 800-204D 对齐）：主体-客体-环境三元组实时评估 `(subject, object, context)`，支持动态上下文感知（如"仅交易时段+可信网络+用户授权"才允许下单）。SPIFFE ID 为每个 AI agent 分配唯一身份
- **B-002~B-005 的 PaC 映射**：

  | 原行为边界 | PaC 实现（Rego 策略） | 评估点 |
  |---|---|---|
  | B-002 杠杆上限 | `deny if order.leverage > config.max_leverage` | FirmRiskAggregator 下单前 |
  | B-003 集中度上限 | `deny if portfolio.concentration(symbol) > config.max_concentration` | FirmRiskAggregator 下单前 |
  | B-004 非交易时段 | `deny if not is_trading_hours(now())` | 执行层 C-002 订单提交前 |
  | B-005 绕过风控 | 架构保证——OPA 在关键路径，所有订单必经 OPA 评估，无 bypass 路径 | 架构铁律 |

- **优势**：策略与代码解耦（改规则不改代码）、Git 版本控制+PR 审查、审计日志自动生成、规则一次编写处处执行。**比"文档规则+人工审查"严格得多**，是 2026 金融系统行为边界的事实标准

---

## 18. 资产与市场覆盖范围（原§4）

> 市场覆盖范围会随账户权限开放、新品种上市、策略演进随时变化，不是硬边界。Charter 只保留原则"能不能买看账户通道，值不值得买看回测结果"，具体品种清单和分级移入此处待讨论。｜ ✅ **v2.0.0 裁定：轻量 Instrument Master（见本节裁定结论）**

**原始内容**：

A股核心矩阵：

| 品种 | 级别 | 数据源 | 数量 | 交易通道 |
|------|:----:|--------|:----:|---------|
| A股全市场 | P0 | miniQMT+iFind | ~5000只 | miniQMT |
| ETF | P0 | miniQMT | ~800只 | miniQMT |
| LOF | P0 | miniQMT | ~400只 | miniQMT |
| REITs | P0 | miniQMT | ~30只 | miniQMT |
| 可转债 | P1待验证 | miniQMT | ~500只 | miniQMT |
| 新股申购 | P1信号级 | iFind/交易所 | 按日历 | — |
| 股指期货 | P2背景级 | iFind | IF/IC/IH/IM | ❌需期货账户 |

其他市场：港股(恒生+AH联动股，P1待验证)；全球(美股指数/行业ETF/中概股/期货/VIX/美债，P2背景级)；汇率/大宗/债券(P2背景级)；加密货币(P3远期)。

**专业机构做法**：
- Instrument Master（标的主数据）：全市场品种的静态属性（代码、类型、上市日、退市日），运行时系统维护
- Eligibility Engine（准入引擎）：按账户权限+券商能力+法规动态计算"能不能交易"
- Universe Definition（投资域定义）：由投资策略决定"研究哪些、交易哪些"
- 三套系统独立运行，不在 charter 中硬编码品种清单

**与 #15 资产分级的关系**：#15 讨论分级维度（交易准入/数据覆盖/研究范围三维度分离），本节讨论品种清单和覆盖范围。两者互补：#15 定义分类框架，#18 定义具体内容。

**✅ v2.0.0 裁定结论**：

- **裁定**：① **采纳轻量 Instrument Master**——不自建重型系统（机构 200+ 字段对个人系统是公认过度设计教训），用 miniQMT 标的信息 + ClickHouse 补充字段 = 轻量 A 股 IM；② **最小字段集**：v0.4.0 的 15 字段 + A 股必需补充——板块代码（主板/科创/创业/北证，决定涨跌幅 ±10%/20%/30%）、ST/*ST 标志及变更日期（2026-07 新规后主板 ST 已 ±10%+单日买入≤50万股限制，直接影响交易准入）、退市整理期标志、上市日期（次新过滤）、停牌标志、昨收价（算涨跌停价）、最小申报单位（主板 100 股/科创板 200 股起）；③ **ST 状态 PIT 跟踪采纳**（A 股特有需求，schema 已有 market_st_stock_list，落 effective_date 表）；④ **标识符映射采纳**——证券代码+交易所作 canonical ID，symbol_normalizer 已施工✅；⑤ **准入引擎**用 #17 choke point 方案的 YAML 规则（非 OPA）；⑥ **投资域定义放 universe_registry**（已施工✅）；⑦ 新品种扩展路径：可转债（schema 已有 market_convertible_bond 系列，P1 待验证→回测验证后转 eligible）→港股（schema 已有 hk 系列，需港股通权限）→期货（P2 背景级维持，需期货账户）。
- **原待讨论问题闭环**：IM 建设=轻量表（非重型系统）✅；准入规则配置=YAML（账户权限+券商能力+法规）✅；投资域=universe_registry ✅；新品种流程=可转债→港股→期货渐进路径 ✅。
- **施工方案**（Phase 2）：ClickHouse 建轻量 IM 表（复用现有 schema，~1 张表+每日盘前 xtdata 同步脚本 ~80 行），ST 状态 PIT 子表；与 universe_registry 的 eligibility 字段联动（#15）。
- **过度工程审查**：拒绝 200+ 字段重型 IM/独立 Eligibility Engine 服务=做减法；全部复用现有 schema。✅ 通过。

**2026 算法补充（v0.4.0）**：Instrument Master 2026 有成熟设计模式，A 股个人系统可用最小字段集：
- **最小字段集**——Finantrix 2026-03：机构级 200+ 字段但实际常用 <50。A 股个人系统**最小 15 字段**：证券代码 / 交易所(SH/SZ/BJ) / 证券类型 / 上市日期 / 退市日期 / 复权因子历史 / 股本变更历史 / ST/*ST 状态变更 / 流通股本 / 总股本 / 行业分类 / 交易单位 / 最小变动价位 / 涨跌停规则 / 是否融资融券标的
- **PIT 跟踪**——Intrinio 2026-02：Instrument Master 必须支持 PIT 查询（#14 PIT 一致性的延伸）。退市公司、ST 变更、股本变更都需 effective_date 记录，否则回测有幸存者偏差。A 股退市率低但 ST/*ST 变更频繁，**ST 状态 PIT 跟踪是 A 股特有需求**
- **标识符映射**——Intrinio 2026-02 / LSEG QA：canonical internal ID + 外部 ID 映射。A 股用**证券代码+交易所**作 canonical（比全球 CUSIP/ISIN/FIGI 简单），但 miniQMT/iFind/交易所代码可能不一致，需映射层
- **建议**：不自建重型 Instrument Master，用 miniQMT 标的信息 + ClickHouse 补充字段（退市日/ST 变更/复权因子）= 轻量级 A 股 Instrument Master。准入引擎用 #17 的 OPA Policy-as-Code 实现【v2.0.0 更正：OPA 已在 §17 裁定拒绝，准入引擎改用 choke point 方案的 YAML 规则】

**2026 尾部不对称防御分配 CAI++ 补充（v1.4.0 极新）**：十三轮审查发现 2026-04-13 发布的 **Copula Asymmetry Index (CAI++)**（Risks 2026, 14, 86, Hatzopoulos & Statiou, University of Piraeus/Aegean）是"选项之外更好的答案算法"——**测量 equity-volatility 尾部不对称依赖并转化为防御分配信号**，直接对应项目资产覆盖范围中"股指期货 P2 背景级"的防御性使用：
- **核心方法**：① **CAI（Copula Asymmetry Index）**= 滚动窗口内联合"股跌&波升"尾部事件经验频率 - 镜像态"股升&波降"经验频率（rank-based 非参数，无需 copula 拟合）；② **CAI++ 实现框架**将 CAI 转化为可操作防御分配信号：smoothing（平滑）→ standardization（标准化）→ delayed execution（延迟执行，防假信号）→ hysteresis（迟滞，防抖动）→ cost-aware portfolio mapping（成本感知组合映射）
- **实证规模**：2000 年起 50 个 equity-volatility 对（SPX/VIX, NDQ/VXN, 油价/OVX 等），vs B&H/60-40/inverse-vol risk parity/SMA-200 四基准。CAI 提升多数对的终端财富，vs 60-40 在最终财富+Sharpe 上显著占优
- **关键发现——CAI 不替代低波动结构化分散**：CAI 在 equity-centric/balanced 组合上作 tail-aware overlay 有效，但**不主导 structurally diversified low-volatility allocations**——risk parity 在下行风险+风险调整指标上仍占优。**定位为尾部感知叠加层非低波动基线替代**
- **与项目资产覆盖的对接**：① 项目 §18 股指期货 IF/IC/IH/IM 是 P2 背景级（❌ 需期货账户），CAI++ 提供"背景级股指期货 → 防御信号"的转化路径——用 IF/IC 收益 + 隐含波动率代理（项目 10 号 synthetic VIX）计算 CAI，CAI 高位→降仓位（防御）；② A 股"股跌&波升"不对称依赖显著（政策市恐慌期 VIX-like 指数飙升），CAI 比线性相关系数更早捕获尾部联动；③ **延迟执行+迟滞**与项目 30 号 §2.5 4 级回撤 Protocol 的"恢复机制"（回撤企稳 50%→解除）同构——都是防抖动设计
- **与 91 号密度预测的协同**：CAI 的 rank-based 非参数尾部依赖测量与 91 号 Conformal Prediction（分布无关）哲学一致——都不假设参数化分布。CAI 管"股-波尾部不对称"，Conformal 管"预测区间覆盖"，两者正交可叠加
- **过度工程评估**：CAI 计算极简（~30 行滚动频率差），CAI++ 框架（平滑+标准化+延迟+迟滞+成本映射）~100 行。**定位为 drawdown_controller / kill_switch 的 Phase 2 防御信号升级**（MVP 先用 4 级回撤硬阈值，Phase 2 加 CAI 作事前防御 overlay），非 MVP 必需。实证规模 50 对是成熟市场，A 股需独立验证 CAI 信号有效性

---

## 19. 大额下单控制与算法执行（原B-013.6）

> 单笔限额应由风险模型动态计算（基于 ADV、波动率、流动性），不是 charter 硬编码。大额订单用算法执行（TWAP/VWAP/IS），不是人工审批。｜ ✅ **v2.0.0 裁定：默认限价单 + 打板专用路径，删 5%ADV 硬条款，算法执行降远期**

**✅ v2.0.0 裁定结论**：

- **本质**：TWAP/VWAP 解决的是"订单规模相对市场成交量足够大、自身冲击推动价格"的问题。个人单票几万~几十万 vs A 股小盘日成交数千万~数亿，占比通常 <0.5% ADV，冲击成本可忽略（见 §5）；拆单反而增加时延暴露（执行越慢，逆向价格风险越大）。
- **裁定**：① **删除"单笔>5% ADV 切算法执行"硬条款**——个人资金量级永远触不到，是伪精确；② **默认单笔限价单**（miniQMT 10 笔/秒限制对单账户个人策略绰绰有余）；③ **打板买入逻辑上不可拆单**——打板是"抢排队优先级"（封板后买不进、未封时抢速度），正确做法是**打板专用执行路径**：集合竞价/早盘瞬时单笔限价（涨停价）申报+封单强度过滤（封成比≥5%，见 §1 v0.7.0）；④ **防异常交易监控**：单笔 >该票分钟级均量 5 倍时简单分 2-3 笔、间隔 3-5 秒（避免单笔记入交易所异常交易监控，2026-04 程序化新规）；⑤ **IS（Implementation Shortfall）作为记录指标**（每日复盘校准滑点假设，default_tca_engine 已施工），非执行算法选型依据；⑥ **人工审批仅用于极端情况**（突破风险预算上限），常规订单零审批（原 B-013.6"大额必审批"语义废弃——X 随 AUM 变化，硬编码无意义）；⑦ **TWAP/VWAP/POV/ICEBERG 代码保留但降级远期**——ex_sor 已施工的算法族在资金量级到单票百万+前不启用；RL 执行/MAP-Elites 维持"已评估不整合"（v0.8.0/v1.6.0 结论）。
- **原待讨论问题闭环**：ADV 阈值→删除✅；算法选择策略→默认限价单✅；模块位置→ex_sor 已施工✅；流动性枯竭 fallback→#8 压力退出时间禁开仓开关+kill_switch 流动性危机停开仓（已施工）✅；与 BudgetChangeHandler 协同→大额 budget 变动走三级升级（30 号 §2.4 已定）✅。
- **施工方案**（Phase 1，40 号已施工范围内的配置调整）：algo_execution_selector 默认策略改为限价单直投；打板策略走独立执行函数。验证：TCA 复盘 IS 分布与滑点假设偏差。
- **过度工程审查**：删硬条款+降级算法族=做减法；无新增组件。✅ 通过。

**原始内容**：B-013.6 禁止AI自主执行大额下单（超过风控框架设定的单笔限额）→ C-002交易执行在单笔金额超过限额时自动拦截→推送人工审批→C-031置信度分层中大额下单永远属于"需人工确认"级别。

**专业机构做法**：
- 仓位限额 = f(ADV, 波动率, 流动性, 相关性) — 全部动态参数
- 大额订单用算法执行（TWAP/VWAP/IS），自动拆单
- 真正的控制：单笔订单量 / ADV > X% 时自动切算法执行，X 由风险模型计算
- 机构不会在 charter 写"超过X万需审批"，因为 X 随 AUM 变化
- 人工审批仅用于极端情况（如突破风险预算上限），不用于常规大额订单

**待讨论问题**：
- ADV 阈值（如单笔>5% ADV 切算法执行）是否合理？
- TWAP/VWAP/IS 三种算法的选择策略？（按波动率？按成交量分布？）
- 算法执行模块放在 C-002 交易执行还是独立模块？
- 极端情况（流动性枯竭）下的 fallback 方案？
- 与 30_multi_strategy_concurrency 的 BudgetChangeHandler 三级升级如何协同？

**2026 执行算法层级补充（v0.3.0）**：执行算法 2026 已形成清晰四层谱系，个人系统按需取用：
- **第一层：静态算法（TWAP/VWAP/POV）**——基线方案（quant67 2026-05）：TWAP 均匀时间切片（抗操纵但可预测）、VWAP 按成交量曲线切片（需历史量曲线拟合+在线纠偏）、POV 按实时市场量参与（跟单陷阱）。A 股散户**默认用此层**
- **第二层：优化算法（Almgren-Chriss IS）**——均值-方差最优轨迹（arxiv 2606.08379）：IS = 决策价与实际执行价之差，AC 框架在市场冲击与时序风险间求最优。λ→0 退化为 TWAP，λ>0 前置加载减少价格风险
- **第三层：RL 自适应（PPO/TD3/TT-DAC-PS）**——2026 前沿（arxiv 2606.08379 / Stanford CS224R / jonathankinlay 2026-05）：PPO 在 LOB 回放上 IS 2.13bps vs VWAP 5.23bps（$21B 名义，arxiv 2601.22113）；TT-DAC-PS 双目标+策略平滑超 PPO/SAC/A2C。**需 LOB 数据+仿真器+~20h 训练，个人 A 股不适用**（散户无 LOB 接入、资金量小、T+1 限制）
- **第四层：质量多样性（MAP-Elites）**——regime 专家集成（arxiv 2601.22113, 2026-01）：生成按流动性×波动率索引的多样化策略组合，各 niche 内 8-10% 提升。**计算密集，机构级**
- **个人 A 股结论**：TWAP/VWAP + 平方根冲击律成本估算**足够**。RL 执行是机构级（大单+LOB 接入+高频），个人系统属过度工程。单笔 >5% ADV 时切 VWAP，否则直接市价/限价单
- **核心指标**：Implementation Shortfall（IS）是执行质量的统一度量，`IS = (P_execution - P_decision) / P_decision`

**2026 A-CRaQL（Adaptive CVaR Risk-Aware Q-Learning）——RL 执行训练流程改进（v1.6.0 补充，对应文档 v1.17.0，已评估不整合）**：[arXiv:2608.04305](https://arxiv.org/abs/2608.04305)（ICAIF'26, Wu/Lei/Huang, 2026-08-06）提出 A-CRaQL——不改 CVaR 估计器与 Bellman 不动点，仅重新设计训练流程，将 CVaR Bellman residual 降约 85%。已在 v1.10.0 登记于 41 号 Phase 5+ RL 训练流程候选，本次补充至 #19 执行算法层评估：
- **核心创新**：6 项协同训练机制——① per-cell sizing（逐格内步长）；② outer-rate decay（外层速率同步衰减）；③ VaR 内变量早期校正；④ coverage-first sampling（覆盖优先再贪婪采样）；⑤ 成熟估计渐进后缀聚合；⑥ 在线可观测标度校准。**不引入新 RL 算法而是改进训练流程**，CVaR Bellman residual 降 ~85%
- **与 v0.8.0 Conformal-gated 执行结论的一致性**：v0.8.0 已登记 SOIC Vol.16（U Hull 2026-08）实证 conformal 门控成本方差 19.1→10.0bps 优于 PPO RL 执行（跨种子高方差不稳定），反向印证"慢而稳 conformal 胜过快而自适应 RL"在执行域同样成立。A-CRaQL 虽改进 CVaR 估计收敛性，但**仍是 RL 训练流程**，不改变"RL 执行在个人系统必要性存疑"的根本结论
- **已评估不整合理由**：① RL 执行在个人系统的必要性存疑——个人 A 股散户无 LOB 接入、资金量小、T+1 限制，RL 执行的增量价值有限（v0.3.0 已定）；② conformal 闸控已足够——v0.8.0 实证 conformal 门控优于 RL 执行，项目 MVP 用 TWAP/VWAP + 平方根冲击律成本估算（v0.3.0 已定）；③ A-CRaQL 的训练流程改进仅在"已采用 CVaR 目标 RL 执行"前提下有价值，而项目 P-4 决策项已建议方向①放弃 41 号阶段 7 执行 RL
- **定位**：**已评估不整合**——与 v0.8.0 Conformal-gated 执行结论一致"慢而稳 conformal 胜过 RL"在执行域同样成立，RL 执行在个人系统必要性存疑，conformal 闸控已足够。记为 41 号 Phase 5+ RL 训练流程候选（v1.10.0 已登记），仅当未来资金量增长后重启 RL 执行时评估

---

## 20. 工程细节移出项（原B-008/B-010/B-012/B-013）

> 以下条目从 charter §4 移出，原因是工程实现细节或重复映射，不属于 charter 级安全边界。归入各自模块配置项。｜ ✅ **v2.0.0 裁定：逐项闭环（见本节开头裁定结论）**

**✅ v2.0.0 裁定结论**：

- **B-008（单次自迭代变更范围）**：✅ 采纳归 C-007 配置项。阈值裁定：**单轮迭代 ≤3 个参数 或 ≤1 个模块**（按影响半径分组，取更严者）——第一性原理：变更范围阈值的本质是"故障爆炸半径控制"，单人系统无并行团队，小步快跑+git 可回滚是最优；具体数值上线后按迭代成功率校准（Phase 2）。
- **B-010（退役策略相似度）**：✅ 采纳**三维指纹**（AST 哈希精确复制 + CodeSAGE 语义嵌入 + DTW PnL 形态）——AST/CodeSAGE 已施工（echo-guard），**DTW 为 Phase 2 施工缺口**（~80 行，dtw-python/fastdtw 库）；退役决策树采纳五选项版（人工重优化 / EvoQuant LLM 自演化[远期] / Layering / 暂停减仓 / 退役），触发条件用 v0.5.0 决策树+5 预警信号（Sharpe<1.5 AND IC<0.05 AND 3次改造失败 AND 维护成本>收益30%）。**90 天滚动相关性剔除规则**：与已施工 strategy_correlation_gate（MOD-PA-004：>0.85 REJECT/>0.90 HARD_REJECT）口径统一——**采用现有 0.85/0.90 阈值 + 补"持续 30 天"持久化条件**（Phase 2，避免单日噪声误剔除）；intent netting 列为 41/42 号 Phase 2 订单合并优化（非本节）。
- **B-012（付费数据源审批）**：✅ 闭环——归运营策略文档+Administrator 审批，治理规则已足够，无需代码。
- **B-013（版权）**：✅ 闭环——依赖 §5 L-005 合规映射（《著作权法》第24条），策略工厂产出不含原始内容即可，**不增加额外版权检查步骤**（避免重复治理）。
- **施工方案**（Phase 2）：① echo-guard 扩展策略指纹库（退役策略 AST+CodeSAGE+DTW 三维入库，~100 行）；② strategy_correlation_gate 补持久化条件；③ EvoQuant LLM 自演化重优化列远期（验证器引导管线=BM-BT 体系原生对接，非 MVP）。
- **过度工程审查**：指纹库复用 echo-guard 引擎非新建；EvoQuant 显式远期；B-012/B-013 零代码。✅ 通过。

---

**原始内容（含各版本算法补充，保留作施工参考）**：

- **B-008 禁止AI在单次自迭代中同时修改过多关联参数** → 工程实现细节，归 C-007 闭环优化引擎配置项（每轮迭代变更范围阈值）
  - 原执行机制：C-007闭环优化引擎限制每轮迭代的变更范围（阈值由配置）
  - 问题：阈值如何配置？按参数类型分组？按影响半径？

- **B-010 禁止AI上线与已退役策略高度相似的新策略** → 工程实现细节，归 C-006 策略工厂配置项（退役策略指纹库+相似度比对阈值）
  - 原执行机制：C-006策略工厂维护退役策略指纹库，新策略上线前做相似度比对（阈值由配置）
  - 问题：相似度比对用什么算法？AST 哈希？策略逻辑指纹？
  - **2026 算法补充（v0.3.0）**：策略相似度检测有两个维度，需分别用不同算法：
    - **代码逻辑相似度**（防换名复活）：项目已有 **echo-guard**（AST 哈希 Tier1 + CodeSAGE 语义嵌入 Tier2），覆盖此需求。AST 哈希捕获精确复制，CodeSAGE 嵌入捕获跨模块 copy-paste 级重复（sim≥0.94）
    - **PnL 曲线相似度**（防行为等价新瓶旧酒）：**DTW（Dynamic Time Warping）**优于 Pearson 相关——DTW 允许时间轴非线性对齐，捕获"形态相似但相位偏移"的策略（CSDN 2026 / Polito 论文 2026-03）。DTW + Pearson 联合过滤（TeknoTrader 2026-03）：DTW 管形状、Pearson 管方向，两者均超阈值才算相似
    - **DTW 局限**（Polito 2026-03）：DTW 特征在**稳定低波动 regime 有用**，高波动 regime 传统指标更好；**跨资产不迁移**（需重新校准）。建议作为 echo-guard 的 PnL 维度补充，非替代
  - **策略退役决策树**（v0.5.0 补充）——退役是 B-010 指纹库的前提，2026 有量化标准：
    - **生命周期事实**——DeepTradeX 2026：68% 系统化策略在 18-24 个月内需要重大修改或退役（市场条件变化+regime 切换）
    - **Edge Decay 三分法**——luxalgo 2026-08-03（极新）：**重优化**（核心逻辑仍成立+OOS 正+邻近参数相似→调参）/ **暂停减仓**（证据混合+expectancy 趋零+回撤超常但可辩护→砍半仓位观察）/ **退役**（OOS expectancy 负+walk-forward 持续失败+成本吞噬 edge+前提不再成立→永久下线）
    - **5 大预警信号**——CSDN 2026-06-04（WorldQuant Alpha 失效）：① 因子拥挤度（相关性>0.6 或 HHI>0.25）；② 收益分布异变（偏度>1.5 / 峰度>3.5 或 <2.5 / 日胜率连续 20 日<52%）；③ 市场状态适应性衰减（HMM 检测状态切换亏损）；④ IC 持续<0.05；⑤ 维护成本>收益 30%
    - **退役决策树**：`if (Sharpe<1.5 AND IC<0.05 AND 3次改造失败 AND 维护成本>收益30%) → 退役`
    - **滚动窗口**——luxalgo 2026-08-03：30-50 笔交易做早期预警，100+ 笔做确认；回撤漂移>1.5-2×历史最大回撤；胜率降 10-15pp 连续两窗口；Profit Factor 从 1.5-2.0 滑向 1.0
    - **与 B-010 对接**：退役策略指纹入库（AST+CodeSAGE+DTW 三维指纹）前，先用上述决策树量化确认"确实应退役"而非"正常回撤恐慌"

  - **Alpha Decay 数学模型（v0.6.0 补充）**——退役决策树的量化基础，2026 已有成熟数学框架：
    - **指数衰减模型**——mathandmarkets 2026-02-22（Half-Lives of Alpha 系列 Part 1）：`α(t) = α₀ · e^(-λt)`，其中 α₀ 为初始 alpha、λ 为衰减率、t 为发现后月数。半衰期 `t½ = ln(2)/λ = 0.693/λ`。经验值：动量策略 t½ 约 20 个月（λ≈0.035），因子拥挤后 t½ 缩短
    - **交易成本地板**——alpha 不衰减到零而是衰减到**成本地板**以下就不可交易。个人 A 股往返成本约 1-2%（佣金+印花税+滑点），年化 alpha <1.5% 即为拖累。可交易半衰期 < 数学半衰期：α₀=5%、λ=0.035 时数学 t½=20 月，但可交易期约 34 月（衰减到 1.5% 成本地板）
    - **复杂度-过拟合差距**——mathandmarkets 实证（6 版双分配器策略）：backtest-reality gap 随复杂度恶化（V1 简单动量 -66% → V3 多因子+波动率增强 -82% → V5 ML 模型 -100% 即完全反转）。**启示**：复杂策略的回测 Sharpe 更需 DSR/PSR 校正（见 #6），简单策略的回测更可信
    - **容量天花板 4/9 规则**——hftradingbook 2026-06-04（Capacity & alpha decay）：net edge per unit = g - c·√Q（g=gross edge, c=impact coefficient, Q=deployed size）。盈亏平衡容量 `Q* = (g/c)²`，但**利润最大化规模 Qmax = 4/9 · Q***（约 44%）。启示：策略应运行在容量天花板内 44% 处，而非逼近天花板——逼近天花板时边际利润递减且对冲击恶化脆弱
    - **与项目对接**：① 策略上线后记录 α₀（入场 Sharpe/IC）和月度衰减，估算 λ 和 t½；② 当 α(t) 跌至成本地板（年化 1.5%）时触发 luxalgo Edge Decay 三分法（重优化/暂停/退役）；③ 容量管理：单策略资金 ≤ Qmax = 4/9·Q*，而非逼近 Q*
    - **2026-07 A 股量化"双杀"实证（v0.9.0 补充）**——策略退役决策树被触发的真实案例：2026 年 7 月 A 股量化行业遭遇 Alpha+Beta 罕见"双杀"——指数下跌（Beta）+ 超额收益失效（Alpha）同时发生。**动量因子一个月回撤超过 20 个百分点**（过去十年罕见），摩根士丹利 TMT 动量组合 17 个交易日峰谷回撤约 40%，整体全球动量因子峰谷回撤约 28%。中证 500 指增策略平均收益 -17.80%（超额 -4.54%），中证 1000 指增策略平均收益 -19.13%（超额 -1.69%），多数量化指增产品超额收益转负。根因：市场极致风格收敛 + AI 板块高位回调 + 动量因子信号滞后（模型持仓仍集中前期涨幅最大标的，未及时减仓）+ 因子同向回撤（原本对冲的动量/Beta/流动性因子同步走弱，多因子分散风险底层逻辑短期失效）。量化私募管理规模已迈入 3 万亿元时代（较 2024 年几乎翻倍），百亿量化私募 71 家——规模扩张加剧容量天花板压力。**与项目对接**：① 印证 #20 退役决策树"Sharpe<1.5 AND IC<0.05"触发条件——动量因子月回撤 -20pp 即 IC 持续<0.05 的极端形态，策略上线后须监控 α(t) 衰减至成本地板时触发三分法（重优化/暂停/退役）；② 印证 #1 v0.6.0 打板环境剧变结论——量化对手盘完整复刻游资盘口特征，7 月双杀中量化基金是波动的"受害者而非加害者"（高盛 Prime Brokerage 数据），但算法同质化共振放大了调整幅度；③ 印证 #3 HRP 远期选项的必要性——因子同向回撤时 naive risk parity 分散失效，HRP 层次聚类可识别因子隐性相关性；④ 项目 4 级回撤 Protocol（8/15/20/25%）是防御此类极端风格切换的硬底线——7 月创业板指 -23% 已触达 Level3（20% 减仓）阈值，若无回撤 Protocol 满仓科技成长将遭毁灭性回撤（来源：[券商中国/私募瞭望站 2026-08](https://finance.sina.com.cn/wm/2026-07-22/doc-iniirshq4747946.shtml) / [新浪财经/浪说量化 2026-07-16](https://finance.sina.com.cn/wm/2026-07-16/doc-inihzfcw4407169.shtml) / 高盛 Prime Brokerage 内部备忘录）

  - **退役决策树第 4 选项——Layering（v0.7.0 补充）**：六轮审查发现 luxalgo 三分法（重优化/暂停/退役）之外，pomegra.io 2026 提出**第 4 选项：Layering**——在衰减策略上叠加新信号：
    - **Layering 定义**（pomegra.io 2026 Alpha Decay Management）：保留衰减策略运行但**叠加新 alpha 源**——衰减策略的 residual edge + 新信号的 fresh edge = 组合 edge 回升。比"退役"灵活（保留 residual edge），比"重优化"激进（引入新信号而非调参）
    - **与三分法的关系**：三分法是"原策略怎么办"（调参/砍仓/下线），Layering 是"原策略+新信号怎么办"（叠加）。两者非互斥——可先 Layering 观察组合 edge 是否回升，不回升再走三分法
    - **机构实践**（pomegra.io 2026）：多数 quant firm 用 hybrid——保留衰减策略运行（reduced allocation）+ 同时研究新信号，而非直接退役。**formal alpha decay analysis 是 portfolio governance 的标准组成**
    - **与项目对接**：项目 24 号打板策略在 2026 环境剧变下（溢价 4.2%→1.7%）可考虑 Layering——保留打板 residual edge + 叠加"反量化"新信号（低位干净筹码小票+事件催化新题材，2026-08 游资新共识）。比直接退役打板更平滑，符合 #1 v0.6.0 打板环境剧变结论
    - **退役决策树更新（v0.7.0）**：`if (α(t) < 成本地板) → {重优化 | Layering(叠加新信号) | 暂停减仓 | 退役}`，Layering 作为重优化与暂停之间的中间档

  - **退役决策树第 5 选项——LLM 自演化重优化 EvoQuant（v0.8.0 补充）**：七轮审查发现 2026-07 发布的 **EvoQuant**（arxiv 2607.12455, HKUST(GZ)+Paradoox AI, 2026-07-14）是"选项之外更好的答案算法"——用 LLM 自演化+验证器引导实现**自动化策略重优化**，比人工重优化更系统化，比 Layering 更深度（改策略代码而非叠加信号）：
    - **EvoQuant 四模块**：① 策略摄入与表示（代码→AST+语义图）；② 基线评估与证据构建（回测瓶颈定位：weak signal / risk rule / parameter drift）；③ 策略优化管线（LLM 诊断瓶颈→生成语义受控候选编辑→多阶段验证管线选最优）；④ 迭代精炼+最终输出（优化经验蒸馏为可复用知识，持续自改进）
    - **实证结果**：7 个代表策略（4 A 股 + 3 加密），平均 test Sharpe **-0.298→0.538**，最佳策略相对改善 **199%**。MACD-RSI-Bollinger +1.383 Sharpe 点（变正），oversold reversal +1.516（变正）。含 walk-forward 验证+交易成本压力测试+消融研究
    - **关键创新——验证器引导**：直接用 LLM 重写策略会引入 hallucinated edits / strategy drift / backtest overfitting。EvoQuant 用**多阶段验证管线**（语义检查+回测+walk-forward+压力测试）选最优候选，**蒸馏优化经验为可复用知识**实现持续自改进。比"LLM 直接吐代码"严格得多
    - **工程实现参考——LangGraph + Harness CI/CD**（CSDN 2026-08-07，极新）：基于 LangGraph 状态机的长程量化 Agent，**严苛风控守门人 should_continue 路由**：`if (Sharpe>=1.5 AND MaxDD<=15%) → submit；elif (iteration>=max_iter) → abort；else → reflect`。**核心风控修复**：达到最大反思次数仍未达标时**坚决 ABORT 而非 submit**——带着亏损或平庸策略强行上线是对本金的谋杀。Harness CI/CD 隔离沙盒回测+Shell 严格状态码判定，撕碎 LLM 的"迎合评测指标的幽灵策略"
    - **与项目对接**：① 项目 100% AI 开发，EvoQuant 的"LLM 自演化重优化"是天然的策略退役决策树第 5 选项——`if (α(t) < 成本地板) → {人工重优化 | EvoQuant LLM 自演化重优化 | Layering | 暂停减仓 | 退役}`，EvoQuant 作为人工重优化的自动化替代；② EvoQuant 的"验证器引导"与项目 BM-BT-01~07 回测门禁体系原生对接（验证管线=BM-BT-05 walk-forward+BM-BT-05-G DSR+BM-BT-07 IS→WFA→OOS）；③ LangGraph+Harness 工程实现是 C-007 闭环优化引擎的 LLM 化升级参考——严苛风控守门人 should_continue 路由可直接编码进 C-007 迭代逻辑（iteration>=max→abort 而非 submit）；④ EvoQuant 的"优化经验蒸馏为可复用知识"与项目 echo-guard 的策略指纹库互补——echo-guard 防重复，EvoQuant 知识库促复用
    - **退役决策树更新（v0.8.0）**：`if (α(t) < 成本地板) → {人工重优化 | EvoQuant LLM 自演化重优化 | Layering(叠加新信号) | 暂停减仓 | 退役}`，EvoQuant 作为人工重优化的自动化替代（深度改代码），Layering 为信号叠加（不改代码），两者非互斥可组合

  - **衰减感知再验证闭环 revalidate（v1.5.0 补充，十四轮审查）**：[AlphaCrafter](https://arxiv.org/abs/2605.05580)（arXiv:2605.05580, 2026）多智能体框架提出 **revalidate** 机制——Miner Agent 周期性重验因子池中每个因子的 IC/ICIR/换手/覆盖/**跨 regime 衰减剖面**，**自动剪枝显著衰减的因子**。与项目对接：① **revalidate 概念可独立于多智能体框架使用**——项目 `factor_pool_manager.py`（ADR-FAC-006）已有 8 状态生命周期治理，revalidate 是其"定期重验"环节的 2026 学术背书（周期性 IC 重验+衰减剖面评估+自动淘汰 = 项目已有 decay_monitor.py + three_level_judgment.py 的学术印证）；② **跨 regime 衰减剖面**是新增维度——当前 decay_monitor.py 用全局 IC 衰减曲线，AlphaCrafter 建议按 regime 分桶评估衰减剖面（如熊市态因子衰减可能加速），与 10 号 regime detector 分桶输出协同；③ **多智能体框架本身不采纳**（过度工程——个人项目不需要 Miner/Screener/Trader 三智能体闭环），仅借鉴 revalidate + 跨 regime 衰减剖面两个概念，列为 `factor_pool_manager.py` Phase 2 增强方向

  - **A 股羊群效应 Johnson S_U 尾部指标（v1.6.0 补充，十五轮审查）**：[arXiv:2607.27063](https://arxiv.org/abs/2607.27063)（2026-07-29）用 agent-based 网络模型解释 A 股动量与反转——局部羊群效应 + 延迟信息扩散 → 过冲 → 反转。实证部分用 **Johnson S_U 变换**构建滚动尾部羊群指标，与 CSAD/LSV 对比，在重大市场冲击期间上升。**与项目对接**：① 32 号已有 HBI/CSAD 拥挤度检测（laoyulaoyu 2026-07 O(N) 纯价格），Johnson S_U 是 CSAD 的**尾部增强版**——CSAD 用线性偏离度，Johnson S_U 用非线性变换捕捉尾部羊群（极端羊群在 CSAD 中被线性压缩，S_U 变换恢复尾部信息）；② A 股散户主导，羊群效应显著，Johnson S_U 指标可作 25 号多因子策略的**另类因子**或 37 号流动性危机的**预警信号**；③ **agent-based 网络模型本身不采纳**（理论工具非施工算法），仅借鉴 Johnson S_U 尾部羊群指标概念；④ 实现成本适中（Johnson S_U 变换 ~50 行，scipy.stats.johnsonsu 可直接使用），记为 Phase 2 候选（与 32 号 HBI/CSAD 并列评估，实盘 6 月后校准 S_U 参数）

  - **MINGLE 联合因子图框架评估（v1.6.0 补充，十五轮审查）——不采纳**：[arXiv:2608.06618](https://arxiv.org/abs/2608.06618)（2026-08-06）提出 Mutually-INformed Graph-Locality and Exposures (MINGLE) 框架，用"系统性因子暴露画像"而非观测共动重新定义图局部性，统一 ADMM 框架联合学习潜在因子表示及图拓扑。**评估后不采纳**：① ADMM 求解器 + 图拓扑学习对个人系统偏重（与已拒绝的 HRP/MVO 同类复杂度）；② 5 策略规模下图局部性的边际收益不显著（MINGLE 优势在 N>20 大资产池）；③ 32 号已裁定"不做 MVO、不做协方差估计"（30 号 §3.1），MINGLE 虽不解 MVO 但依赖因子暴露矩阵估计，同样引入估计不稳定性；④ 记为 Phase 5+ 远期候选条件：策略数 >8 且 correlation_dedup 实测漏检率高时重评

  - **策略相关性 90 天滚动剔除规则（v0.8.0 补充）**：七轮审查发现 youcanbuildthings 2026-05-06（Multi Strategy Trading Bot Python）提供 23 号策略相关性文档的施工算法补充：
    - **90 天滚动相关性剔除规则**：两策略 90 天滚动相关性 >0.70 持续 30 天→剔除低 Sharpe 策略。`correlation_drop(returns_df, threshold=0.70, persistence_days=30)` 返回待剔除列表。**理由**：相关性 >0.70 持续 30 天=分散收益消失，运行两策略只增加经纪费+操作风险
    - **per-strategy drawdown circuit breaker**：15% half / 25% zero——与项目 4 级回撤 Protocol（Level2 15% 减仓 / Level4 25% 清仓）原生对接
    - **intent netting**：多策略对同一标的反向订单在送 broker 前净额结算（Strategy A long 100 + Strategy B short 60 → net long 40 一笔订单）——减少一半经纪费。与项目 BudgetChangeHandler 三级升级互补
    - **与项目对接**：23 号策略相关性文档可补入此 90 天滚动相关性剔除规则作为策略退役的**相关性触发条件**（与 Alpha Decay 的 Sharpe/IC 触发条件并列）；intent netting 是 41/42 号买卖流程的订单合并优化

- **B-012 禁止AI自动订阅付费数据源** → 成本控制是运营策略，归运营策略文档（数据源变更需 Administrator 审批）
  - 原执行机制：数据源变更需人工审批（Administrator角色）
  - 问题：付费数据源审批流程放在哪个运营文档？

- **B-013 禁止AI在未经用户确认的情况下使用用户提供的UP主/频道内容做商业用途** → 版权合规已在 §5 L-005 法规映射覆盖（《著作权法》第24条），重复
  - 原执行机制：C-006策略工厂的爬取功能仅用于个人研究，产出策略代码不包含原始内容
  - 问题：是否需要在策略工厂中增加版权检查步骤，还是完全依赖 §5 L-005 合规映射？

**待讨论问题（v2.0.0 已闭环，见本节开头裁定结论）**：
- B-008 的"变更范围阈值"如何配置？——✅ ≤3 参数或 ≤1 模块取严者，上线后校准
- B-010 的"相似度比对"用什么算法？——✅ 三维指纹（AST+CodeSAGE+DTW）
- B-012 的付费数据源审批流程放在哪个运营文档？——✅ 归运营策略文档+Administrator 审批
- B-013 是否需要在策略工厂中增加版权检查步骤？——✅ 不需要，依赖 L-005 合规映射

---

## 21. 做T方法论定义

> "做T"在 charter §1.3（13个优化维度之一）/ §3 约束一（做T额外成本）/ §7 A-003（T+1制度不变→做T）多处引用但从未正式定义。系统已有3个做T策略代码实现但无方法论文档。本节补全定义。｜ ✅ **v2.0.0 裁定：采纳为受约束 overlay + 补齐四规则**

**✅ v2.0.0 裁定结论**（闭环原待讨论问题）：

- **容量上限**：个人资金（单票几万~几十万）远触不到容量顶——真正约束是**成本**（单次往返硬成本≈0.10-0.15%，见 §5）与**胜率纪律**。容量估算式留档：容量≈底仓市值×做T仓位比×日内可成交性。
- **底仓 sizing 规则**：**单次做T仓位 ≤ 底仓 20-30%**（取保守端——打板/事件策略底仓本身波动大；文档原建议 1/3~1/2 偏激进），做T专用资金与主策略仓位**分账记账**（成交回报分账以归因）。
- **做T 与 regime 关系**：**仅在量比>1 且预期振幅 >2×单边成本（≈0.3%）时开仓**；低波/缩量日强制不做（r1 低波震荡态默认关闭做T）；与 §8 流动性前置检查共用阈值。
- **做T 失败处置**：① 反T 未接回：**14:30 后强制限价/市价接回**（宁可亏价差不留隔夜敞口）；② 正T 买入后无法当日卖出是 T+1 固有风险——以**"买入前底仓可卖量"为硬约束**（可卖量=0 时禁开正T），且设单笔止损 -1.5%~-2%。
- **与主策略协同/冲突**：**主策略卖出信号优先于做T持有**；做T层每日开盘从主策略持仓快照同步"可用底仓额度"，两层成交回报分账记录。
- **3 个已有策略整合**：暂不整合为统一框架——三者 alpha 来源不同（冲高回落=日内动量反转、盘口失衡=微结构、VWAP回归=均值回归），保留独立策略，统一走 tick_strategy_base 基类（已施工✅）；是否合并待实盘 6 个月各自 IC/胜率数据说话。
- **施工方案**（Phase 2）：四规则配置化写入做T策略配置（tick_strategy_base 配置项：max_t_position_ratio=0.25 / min_volume_ratio=1.0 / min_expected_amplitude=2×cost / force_cover_time=14:30 / stop_loss=-1.5%~-2%，~50 行配置+校验）。验证：tick_replay 回放四规则触发正确性（已有回放引擎）。
- **过度工程审查**：全部配置项非新架构；不建统一做T框架。✅ 通过。

---

**定义**：

做T = 持有底仓 + 日内高抛低吸。在A股T+1制度下，通过持有底仓变相实现T+0：当日卖出底仓份额（高抛），当日再买回等量份额（低吸），收盘后底仓数量不变但持仓成本降低。本质是利用日内波动赚取差价，非方向性策略。

**与"日内T+0额外成本"的区别**：
- "做T"是策略类型（底仓+日内高抛低吸）
- "做T额外成本"是该策略产生的额外成本（滑点×2+失败风险溢价），是成本模型的一个组成部分（charter §3 约束一）

**已有代码实现**（src/zephyr/pf_core/）：
- `intraday_surge_fall_strategy.py` — 30秒冲高回落做T策略
- `orderbook_imbalance_strategy.py` — 盘口失衡反转做T策略
- `vwap_reversion_strategy.py` — VWAP回归做T策略
- `tick_strategy_base.py` — Tick级策略/做T基类
- `core/tick_replay.py` — 秒级做T专用回放引擎

**成本模型**（charter §3 约束一引用）：
- 做T额外成本 = 滑点×2（一买一卖两次滑点）+ 失败风险溢价（日内未买回底仓的隔夜风险）
- 具体滑点模型和失败风险溢价计算见 #5 成本模型细节

**适用条件**：
- 标的：高波动+高流动性（满足日内波动空间 > 做T额外成本）
- 底仓：已有持仓且不动用底仓做方向性赌注
- 频率：3秒Tick用于做T买卖点触发（charter §2 约束四）
- 风控：底仓暴露风险+日内操作风险（需纳入风险模型）

**待讨论问题**：
- 做T策略的容量上限？（单标的做T容量受日内成交量限制）
- 底仓sizing规则？（底仓多大才能支撑做T而不影响主策略仓位）
- 做T与regime的关系？（高波动regime做T收益高，低波动regime做T可能亏损）
- 做T失败（日内未买回底仓）的处置规则？
- 做T与主策略的协同/冲突？（做T可能影响主策略的持仓周期和信号）
- 3个已有做T策略的alpha来源差异？是否需要在统一框架下整合？

**2026 方法论补充（v0.3.0）**：A 股做 T 有标准两种模式，2026 实践已清晰：
- **正 T（先低吸后高抛）**（sina 2026-07）：盘中低位买入→反弹后卖出等量底仓。适用震荡上行/低开反弹行情。风险：买入后持续大跌→仓位被动加重
- **反 T（先高抛后低吸）**（sina 2026-07）：高位卖出底仓→回落后买回等量。适用震荡下行/高开回落行情。风险：卖出后持续拉升→踏空丢筹码。**反 T 难度更高**，单边大涨慎用
- **仓位管理**：建议用底仓的 1/3~1/2 做日内，保留一半打底防踏空；收盘持仓总量≈开盘（做 T 不增加总仓位）
- **日内指标三层栈**（quantzee 2026-06，2026 日内交易标准）：① VWAP（日内公允价值+机构参考）+ ② 趋势工具（SuperTrend 或 EMA 确认方向）+ ③ 动量振荡器（RSI 或 MACD 定时入场）。专业交易员用 2-4 个指标，**不超过 4 个**（多了信号冲突）
- **量化做 T 路径**（arxiv 2103.13507）：MLP 预测日内趋势→11:20 前买入→14:50 卖出；每日重训练防隔日 gap。项目已有 3 个做 T 策略（冲高回落/盘口失衡/VWAP回归），可按此框架整合
- **避开前 30 分钟**（quantzee 2026-06）：开盘 30 分钟内假信号率最高，所有市场通用规则

## A股市场结构变化（2026-07/08）

> **v1.6.0 新增（对应文档 v1.17.0）**：2026-07/08 A 股市场结构发生多项重要变化，影响策略施工约束。需在 24/25/26 号策略文档同步更新。

### A.1 A 股交易新规（2026-07-06 实施）

**核心变化**：
1. **盘后固定价格交易扩容**——从科创板/创业板扩展至**全部 A 股和沪深 ETF**（15:05-15:30）。影响：尾盘流动性结构已变，龙虎榜 2026 机构信号校准需同步更新（尾盘定价机制变化影响"尾盘抢筹"信号解读）
2. **主板 ST/*ST 涨跌幅放宽**——从 5% 放宽至 **10%**。影响：ST 股波动率结构变化（波动率上限翻倍），影响 ST 股策略的风险参数校准+VaR 估算
3. **上交所基金收盘竞价调整**——收盘连续竞价改为**集合竞价**。影响：ETF 策略尾盘执行需调整（集合竞价 vs 连续竞价的冲击成本模型不同）
4. **深交所创业板引入做市商**——影响：创业板流动性结构改善，但做市商行为可能引入新的微观结构模式

**施工约束影响**：
- **24 号打板策略**：尾盘执行逻辑需评估"盘后固定价格交易"对打板尾盘抢筹的影响（15:00 收盘后 15:05-15:30 的盘后交易可能分流尾盘流动性）
- **26 号龙虎榜策略**：2026 机构信号校准需更新（尾盘流动性结构已变，传统"尾盘抢筹=机构买入"假设需重新验证）
- **ST 股策略**：涨跌幅 5%→10% 后，ST 股波动率参数需重新校准（历史波动率数据含 5% 涨跌幅限制，需 regime 切换处理）

### A.2 微盘股策略失效机制（2026-07 深度复盘）

**核心机制**：科技股虹吸 → 微盘流动性枯竭 → 量化同质化多杀多 → 退市新规基本面恶化
- **科技股虹吸**：2026-07 科技板块（AI/算力/半导体）持续吸金，微盘股资金净流出
- **流动性枯竭**：微盘股日均成交额下降，买卖价差扩大
- **多杀多**：量化策略同质化（拥挤因子+相似仓位）→ 压力期同时平仓 → 多杀多加速下跌
- **退市新规基本面恶化**：微盘股 2026 Q1 归母净利同比 **-79.25%**，退市风险加剧

**施工约束影响**：
- **25 号多因子策略 build_tradability_mask**：需强化流动性门槛——① 提高日均成交额下限（微盘流动性枯竭使原阈值过低）；② 增加退市风险预警（基本面恶化+退市新规）；③ 监控因子拥挤度（同质化多杀多风险）
- **选股策略流动性过滤**：流动性过滤阈值需 regime 感知（压力期提高门槛，正常期维持）

### A.3 量化"双杀"压力测试（2026-07）

**核心数据**：
- 沪深300 指增平均超额 **-1.51%**
- 中证500 指增 **-4.54%**
- 动量因子单月回撤超 **20 个百分点**（十年罕见）
- 因子拥挤（crowding）→ 同质化量化策略集中平仓 → 多杀多

**施工约束影响**：
- **#2 因子工程**：需在因子监控模块增加拥挤度指标（详见 §2 量化"双杀"压力测试条目）
- **#6 回测门禁**：压力测试场景需纳入 2026-07 量化"双杀"episode 作极端 regime 回测
- **#4 风险模型**：动量因子单月回撤超 20pp 印证 4 级回撤 Protocol（8/15/20/25%）的 20% Level3 触发必要性

## 待定问题（v1.2.0 新增——需人决策的开放问题）

> 以下 5 项均源自十一轮审查（v1.2.0）过度工程纠偏——多轮审查累积的"加法"（Wasserstein 家族四件套+conformal 五变体栈+Robust HMM 七候选+RL 执行+过拟合检测三协议）已超出 MVP 最小可行边界，需人决策收敛选项。AI 不擅自发挥，标记如下供人裁定。

| # | 决策项 | 背景 | 最小可行 baseline | 候选项 | 建议方向（非裁定） |
|---|---|---|---|---|---|
| **P-1** | **Wasserstein 家族是否收敛** | v0.9.0-v1.1.0 累积形成 regime 层（W-HMM）+组合层（Certified DRO）+仓位层（W-Kelly）+生成式扩展（W-GAN）"四件套"，统一用 Wasserstein 距离作鲁棒性度量 | **regime 层 W-HMM 单独先上**（直接对应 12 号 A2 FAIL 修复），组合层+仓位层+生成式扩展列为 Phase 3+ 远期 | ① 全上四件套（统一度量但工程量大）② 只上 W-HMM（最小可行，其余 naive risk parity+参数化 Kelly+经验分布已足够 MVP）③ 不上（现有方案已足够，Wasserstein 是锦上添花） | **方向②**：W-HMM 先上（有 A2 FAIL 痛点驱动），其余 Phase 3+ 按需引入，避免一次性堆栈 |
| **P-2** | **Conformal 五变体栈是否收敛** | v0.4.0-v0.9.0 累积形成 slow unweighted → EWMA 标准化 → RWC regime 加权 → ACI → COP 五变体递进栈（91 号 Phase 0） | **slow unweighted + EWMA 标准化**（Conformal Kelly 实证最优 baseline + v0.8.0 修复 conditional coverage 8pp gap，共 ~60 行） | ① 全上五变体（最完备但维护复杂）② baseline+ACI（修复 post-break，A 股政策市 regime break 频繁场景必需，~80 行）③ baseline+RWC（复用 regime 检测器，压力期校准更好，~140 行）④ 只上 baseline（最简但 conditional coverage 未修复） | **方向②**：slow unweighted+EWMA+ACI 三层（Conformal Kelly"慢而稳"最优+EWMA 修复 conditional+ACI 修复 post-break），RWC/COP 作为压力期不达标时的升级 |
| **P-3** | **Robust HMM 候选选哪个** | v0.9.0-v1.2.0 累积 7 候选：Wasserstein HMM（标签漂移）+BR-iHMM（离群鲁棒）+Huber Robust HMM+Student-t HMM+GH HMM+Feature Saliency HMM+AH-HMM（egargale/hmm_test PRD #20 2026-05-29） | **Wasserstein HMM**（v0.9.0：Columbia 实证 Sharpe 2.18 vs SPX 1.18，直接对应 12 号 A2 FAIL 标签对齐失败，model-order selection+template tracking 双重解决） | ① Wasserstein HMM（标签漂移，轻量）② BR-iHMM（离群鲁棒+无限状态，67% 误差降低，但更重）③ Student-t HMM（肥尾鲁棒，最轻量但只解决 emission 不解决 label-switching）④ Huber Robust HMM（折中） | **方向①**：Wasserstein HMM 先上（直接解决 A2 FAIL），BR-iHMM 作离群点密集场景升级，其余列为对照评估 |
| **P-4** | **RL 执行是否实施** | v0.3.0 定执行算法四层谱系（TWAP/VWAP→AC→RL PPO/TD3→MAP-Elites），v1.2.0 补 Conformal-gated 执行（SOIC Vol.16 2026-08 U Hull）实证 conformal 门控成本方差 19.1→10.0bps 优于 PPO RL 执行（跨种子高方差不稳定），反向印证"慢而稳 conformal 胜过 RL"在执行域成立 | **TWAP/VWAP + 平方根冲击律成本估算**（v0.3.0 已定：个人 A 股散户默认用此层，足够） | ① 放弃 41 号阶段 7 执行 RL（Conformal-gated 实证更优+个人系统无 LOB 接入+资金量小+T+1 限制）② 保留 RL 执行作远期选项（资金量增长后可能需要）③ Conformal-gated 执行替代 RL 执行（中等复杂度，需 conformal 校准层） | **方向①**：放弃 41 号阶段 7 执行 RL（个人系统过度工程），保留 TWAP/VWAP 作 MVP 执行层，Conformal-gated 作远期升级选项 |
| **P-5** | **过拟合检测协议选哪个** | v1.2.0 补 3 项：AlgoXpert IS-WFA-OOS 协议（arxiv 2603.09219v1 2026-03-10，plateau 优先+purge gap+majority-pass/catastrophic-veto 门控）+plateau 启发式受控验证（Soloviov plateau.marketmaker.cc 2026，选择偏置有效 +0.12-0.31 OOS Sharpe 但独立检验弱）+PBO 零假设=0.5（marketmaker.cc 2026-07-01，PBO≈0.5=完全过拟合=抛硬币） | **现有 BM-BT-01~07 体系**（项目已裁定：#6 v0.2.0 标✅已裁定，Purged K-Fold+DSR/PSR 已含） | ① 现有体系+AlgoXpert IS-WFA-OOS（最严谨，plateau 优先+purge gap+双门控）② 现有体系+PBO 零假设=0.5（最简增量，仅改 PBO 零假设）③ 现有体系+plateau 启发式（选择偏置有效但独立检验弱，作辅助非主协议）④ 不改（现有 BM-BT-01~07 已足够） | **方向②**：现有体系+PBO 零假设=0.5 修正（最小增量，修正 PBO 零假设从 1 改为 0.5 即可，AlgoXpert/plateau 列为 Phase 2+ 升级） |

> **v2.0.0 更新（A2 PASS 后续航重估）**：① **P-1/P-3 紧迫性下调**——11 号 v1.5.2 确认 A2 降 4 态后已 PASS（OOS/IS=1.042），Wasserstein HMM 从"A2 修复必需"降级为 Phase 3+ 可选增强，P-1 原建议方向②的理由"A2 FAIL 痛点驱动"已消失——若用户确认 P-1，建议改为"W-HMM 与 BR-iHMM 均列 Phase 3+ 远期对照评估，MVP 维持 4 态 HMM+3 overlay 不动"；② **P-5 建议修订**——v1.7.0 Soloviov 实证 PSR AUC 0.808 > DSR 0.785 > PBO 0.669，建议方向②修正为"现有体系 + PSR 主诊断 + DSR 补充 + PBO 零假设=0.5 修正"；③ P-2/P-4 维持原建议（方向② slow unweighted+EWMA+ACI / 方向① 放弃 RL 执行）。**五项仍全部待用户裁定**。
>
> **收敛原则**：MVP 阶段优先选择"最小可行 baseline"列方案，候选项列为 Phase 2+/3+ 按需引入。多轮审查累积的"加法"需通过人决策收敛为"减法"——保留有痛点驱动的，暂缓锦上添花的（Wasserstein 组合/仓位层、COP、RL 执行、AlgoXpert 协议）。【v2.0.0 注：W-HMM 的 A2 痛点已随 A2 PASS 消失，收敛原则相应更新】

## 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.1 | 文件名 discussion_020_methodology_open_questions.md → 90_methodology_open_questions.md（段位编号制），内容不变 | 文档体系重排，新旧名对照见 00_index_trading_decision §10 |
| 2026-08-09 | 0.1.2 | 文档头统一：title/H1 去"讨论稿："前缀，scope 归一为 07_trading_decision_architecture；章节编号与正文零变更 | 15 篇有内容文档结构统一（骨架体系收尾），规范真源 01_design_memo_management_spec §4.2 |
| 2026-08-10 | 0.2.0 | 逐项审查 21 提案与项目现状对齐：① #3/#4/#6/#11 标✅已裁定（30_multi_strategy v1.3.3 替代方案+映射）；② #7 纠正"8态已被12态替代"为不准确（8态 BM-SEL-04 是独立下游消费者未建，非被 regime 替代；但8态→直接决策映射过时）；补 regime spec 12态 vs 实际实现 4态+3overlay=7维差异（11_regime §0.5.2）；③ #9 更正 Layer2 "8态预测"引用为 regime 检测；④ #3/#6 补 2026 行业实证（risk parity/Columbia arxiv/Purged K-Fold/DSR）；⑤ 总览表+优先级表反映裁定状态 | 架构审查：与 30_multi_strategy / 10_regime / 11_regime / 已施工代码对齐 + 2026 量化方法论最新实践验证 |
| 2026-08-10 | 0.3.0 | 二轮深度审查补 6 项施工算法缺口+更优替代：① #2 因子IC 补 SHAP 特征重要性（MSCI 2026-03/MinShap arxiv 2604.15107）作为非线性评估互补；② #5 成本模型补平方根冲击律+Almgren-Chriss 分解（arxiv 2603.29086）+个人 A 股冲击可忽略结论；③ #8 流动性补 Amihud 非流动性指标+LVaR+Kyle Lambda（2026 标准）；④ #19 大额下单补 2026 执行算法四层谱系（TWAP/VWAP→AC→RL PPO/TD3→MAP-Elites）+个人系统 TWAP/VWAP 足够结论；⑤ #20 B-010 补 DTW 策略相似度检测（优于 Pearson，CSDN/Polito 2026-03）+与 echo-guard 互补；⑥ #21 做 T 补正 T/反 T 定义+日内指标三层栈（quantzee 2026-06） | 二轮审查：施工环节流程算法缺口补充 + 2026 年 8 月最新研究实践算法验证 + 过度工程审查（RL 执行/DTW 跨资产均标注个人系统适用边界） |
| 2026-08-10 | 0.4.0 | 三轮深度审查补 6 项施工算法缺口+更优替代：① #1 策略类型补 2026 管线谱系（Shehral 2026-04）+四族分类（vzeman 2026-05）替代原 6 大类；② #13 基准设计补 Barra 式归因（KTD-Fin arxiv 2605.28359）+Smart Beta 基准（中证指数 2026-07）；③ #14 PIT 实现补财报双日期（period_end vs first_filed，平均差 43 天，tradevodata 2026-07）+重述泄漏（original_value/latest_value）+observation spine 模式；④ #15 资产分级补 A 股流通市值 6 级分层（CSDN 2026-08-08 极新）+市值定调子原则；⑤ #17 行为边界补 Policy-as-Code（OPA/Rego 2026 标准）+B-002~B-005 映射表；⑥ #18 资产覆盖补 Instrument Master 最小 15 字段集+ST 状态 PIT 跟踪 | 三轮审查：剩余 15 待讨论项的施工算法缺口补充 + 2026 年 8 月 8 日最新研究（CSDN 2026-08-08 A 股市值分层）+ 文档结构审查（21 项顺序保留历史可追溯，优先级表末尾重组） |
| 2026-08-10 | 0.5.0 | 四轮深度审查补 3 项+1 项重大更优替代：① #16 成功指标补 2026 五层评估体系（nexusfi 存活→边际→效率→鲁棒→部署）+Sharpe>3 可疑/Calmar>5 极罕+MDD 三维度+单一指标陷阱；② #20 B-010 补策略退役决策树（luxalgo 2026-08-03 Edge Decay 三分法+WorldQuant 5 预警信号 CSDN 2026-06-04+68%策略 18-24 月需改造）+退役决策树代码+滚动窗口标准；③ #2 补 GP 自动因子挖掘（CSDN 2026-06）+EAFD（arxiv 2603.15713）作为因子发现维度（SHAP 管评估，GP 管发现）+个人系统远期探索标注 | 四轮审查：成功指标体系化 + 策略退役量化标准（B-010 指纹库前提）+ 因子发现自动化趋势（个人系统远期） |
| 2026-08-10 | 0.6.0 | 五轮深度审查补 4 项施工算法缺口+更优算法：① #1 补 2026-08 打板环境剧变实证（东方财富 2026-08-03：溢价 4.2%→1.7%/炸板率 40%→68%/4 月程序化新规/legulegu 6 指标情绪评分+赢牛资管 4 阶段）；② #7 补 A 股预测天花板 52-53%实证（firsh.me 2026-07 九版迭代 p=0.007，突破口在信息源非架构，8态暂缓建议+复用 regime 多源特征）；③ #20 B-010 补 Alpha Decay 数学模型（mathandmarkets 2026-02 指数衰减 α(t)=α₀·e^(-λt)+半衰期+成本地板+复杂度-过拟合差距 V1→V5 恶化实证+hftradingbook 容量 4/9 规则 Qmax=4/9·Q*）；④ Doc 91 同步补 RWC（Oxford 2026-08-03）为 Phase 0 最优变体 | 五轮审查：施工算法缺口清零（#7 预测天花板决定 BM-SEL-04 取舍+#20 退役数学模型补全+#1 打板环境剧变影响策略可行性）+ 选项之外更优算法（RWC 复用 regime 检测器，架构原生匹配） |
| 2026-08-10 | 0.7.0 | 六轮深度审查补 4 项施工算法缺口+选项外更优算法：① #1 补 akshare 连板接力筛选算法（CSDN 2026-08-05 开源：封成比≥5%/股价≤30 元/流通市值≤250 亿/封板时间≤14:30）+6 维度涨停规律（犇犇浅谈 2026-08 3200 只复盘：4 分时硬性指标）+8 月游资转型实证（东方财富 2026-08-03：电子板块净流出 187 亿/12 算力龙头减持 22%/工业富联跌停案例）；② #2 补 PPO 自适应 alpha 加权（arxiv 2509.01393 U Hyogo 2026）为因子动态加权远期选项（抗 alpha decay，与 25 号五静态方法互补）；③ #11 补 Kelly 分数实证（marketmaker.cc 2026-06-23 g(f*)=SR²/2+Half-Kelly 75%增长@50%波动+1/4 Kelly 95%增长+Lisa Chang 案例	full→-62% / 1/4→-12%+drawdown 恢复数学+动态分数 Kelly 建议）；④ #20 补退役决策树第 4 选项 Layering（pomegra.io 2026 叠加新信号，三分法→四分法）。Doc 91 同步补 Information-Entropic DL+GP+Kelly+CVaR 为 Phase 1.5+RWC 关键告诫+DeepONet | 六轮审查：施工算法缺口清零（#1 打板筛选开源算法+6 维度规律+#2 因子动态加权+#11 Kelly 分数实证+#20 退役第 4 选项）+ 选项之外更优算法（PPO 抗 decay/Layering 叠加/动态分数 Kelly/Info-Entropic DL+GP 统一框架）+ 2026-08 最新研究验证 |
| 2026-08-10 | 0.8.0 | 七轮深度审查补 5 项施工算法缺口+选项外更优算法：① #1 补 4 个开源打板工具生态（short-term-stock-picker 6 维筛选+评分系统/A-Share-Sector-Alpha-Hunter 蓄势弹簧/stk_explore 双数据源+历史封板率/A-Share-Sector-Alpha-Hunter）；② #2 补 PeerJ cs-3630 三层框架（LLM+多智能体+PPO，OOS 年化 53.87%/Sharpe 1.702/MaxDD 12.54%）为 PPO 系统化升级路径+CGX 多智能体 LLM 对抗辩论（MDPI Electronics 15:3453 2026-08-04，Sharpe 1.90/MaxDD 11.6%/2022 熊市 Bear gate 阻止 93% sessions）为 28 号情绪周期 LLM 化远期选项；③ #3 补 HRP（Hierarchical Risk Parity, López de Prado）为 naive risk parity 进阶选项（层次聚类分配风险，忽略策略间相关性的局限）；④ #11 补 Conformal Kelly（arxiv 2608.01494 2026-08-02，75% CP 区间缩放仓位/28.5% 年化/Sharpe 1.34/"慢而稳 conformal 胜过快而自适应"反直觉发现+drawdown dial 风控 MaxDD 27.7%→20.3%）+Bayesian Kelly（Sukhov 2026 `f*=(p̄-(1-p̄)/b)·n_eff/(n_eff+κ)`）/RMSE Kelly（MarketRegimeNet `f=α·f*, α=max(0,1-c·RMSE/|f*|)`）轻量级校准为 Phase 0.5 介于 RWC 与 Info-Entropic DL+GP 之间；⑤ #20 补退役决策树第 5 选项 EvoQuant（arxiv 2607.12455 HKUST 2026-07 LLM 自演化+验证器引导重优化，A 股 4 策略 Sharpe -0.298→0.538/最佳+199%）+LangGraph+Harness CI/CD 工程实现（should_continue 路由 iteration>=max→abort）+90 天滚动相关性剔除规则（youcanbuildthings 2026-05，>0.70 持续 30 天→剔除低 Sharpe）+intent netting+per-strategy drawdown circuit breaker | 七轮审查：施工算法缺口清零（#1 开源打板生态+#2 LLM+多智能体+PPO 三层框架+#3 HRP+#11 Conformal Kelly+轻量级 Kelly 校准+#20 EvoQuant LLM 自演化重优化+90 天相关性剔除）+ 选项之外更优算法（Conformal Kelly 反直觉"慢而稳"/EvoQuant LLM 自演化/HRP 层次聚类/CGX 多智能体对抗辩论）+ 2026-08-04 极新研究验证 |
| 2026-08-10 | 0.9.0 | 八轮深度审查补 2 项施工算法缺口+选项外更优算法：① #7 补 **Wasserstein HMM**（arxiv 2603.04441 Columbia 2026-02-21，预测性 model-order selection 用 one-step-ahead log-likelihood 动态选 regime 数量+Wasserstein template tracking 用 2-Wasserstein 距离将 Gaussian 分量映射到持久化 regime 模板解决 label-switching，Sharpe 2.18 vs SPX 1.18/MaxDD -5.43%/2025-04 Liberation Day 动态降股票暴露）——**直接对应项目 12 号 A2 FAIL（OOS/IS=0.340 标签对齐 Hungarian 失败）**，是 regime 检测器 Phase 2 A2 修复候选方案（与 Hungarian 事后对齐并列评估），非 MVP 必需；② #2 补 **F²Agent**（arxiv 2608.05668 NUS 2026-08-06 极新，多模态多智能体 LLM+modality-aware adaptive fusion+noise-robust consistency regularization，比 CGX 多了模态融合维度，GOOG 120.48%/TSLA 148.41%/平均年化 +20%）+**市场依赖通信**（arxiv 2511.13614 CMU 2025-11，450 实验：竞争式适用高波动科技股/协作式适用稳定股/金融股抵抗所有通信/对话质量与收益零相关）+**MarketSenseAI 自适应集成**（arxiv 2604.17327 2026-04，4 specialist agent+synthesis，ICIR +0.489/agent 贡献随 regime 轮换非主导 agent）为 CGX 远期选项的工程化细化 | 八轮审查：施工算法缺口清零（#7 regime 标签漂移直接解决方案 Wasserstein HMM 对应 A2 FAIL+#2 多智能体 LLM 细化三研究）+ 选项之外更优算法（Wasserstein HMM 标签追踪/F²Agent 多模态融合/市场依赖通信设计/MarketSenseAI 自适应集成）+ 2026-08-06 极新研究验证（F²Agent）+ 直接解决项目已 FAIL 验证器（A2） |
| 2026-08-10 | 1.0.0 | 九轮深度审查补 2 项施工算法缺口+选项外更优算法，**"Wasserstein 家族"三件套成形**：① #1 补 **Tail-Aware MDN**（arxiv 2601.14049 Dumitrescu/Peignon/Thomas Paris-Dauphine PSL 2026-01-20 + ESANN 2026 扩展，skewed Student-t Mixture Density Network 专攻 locally explosive time series，**与 A 股打板"涨停→炸板"动力学原生匹配**——mixed causal-noncausal ARMA 建模 bubble dynamics = 打板连板加速→炸板崩裂，skewed t 替代 Gaussian mixture 捕获右偏（涨停上限）+左重尾（炸板暴跌），dual reweighting 解决炸板日稀有极端事件学习不足，post-hoc PIT recalibration 校准完整密度，配套 local explosive dynamics 检测（Blasques/Koopman JTSA 2025 46(5):966-980）作气泡态前置门控）——是 91 号 Phase 1 LSTM+GMM 的"算法替换"升级（Gaussian→skewed t），非新增栈非过度工程；② #3 补 **Certified Wasserstein DRO 组合**（arxiv 2608.07032 Hsieh&Gan 2026-08-07 极新，order-1 Wasserstein 模糊集 worst-case 期望效用最大化，多项式规模 LP 可扩展 1000 资产）+**Shift-Aware Wasserstein-DRO CVaR**（arxiv 2512.16748 Long Columbia NeurIPS 2025 Workshop，Gaussian-supremum validation+block multiplier bootstrap 时序依赖下选 δ，分布漂移感知）+**Wasserstein-Kelly**（JUSTC 2025 55(8):0805 Sun&Zou USTC，coherent Wasserstein metric Kelly 分布鲁棒版凸规划可解）——与 v0.9.0 #7 Wasserstein HMM 形成 **regime 层（Wasserstein HMM template tracking）+ 组合层（Wasserstein DRO）+ 仓位层（Wasserstein-Kelly）"Wasserstein 家族"三件套**，统一用 Wasserstein 距离作鲁棒性度量；列为 30 号 Phase 3+ 远期演进（naive risk parity→HRP→Wasserstein DRO 三级递进），非 MVP 必需 | 九轮审查：施工算法缺口清零（#1 打板密度预测原生匹配算法 Tail-Aware MDN+#3 Wasserstein 家族组合层补齐）+ 选项之外更优算法（Tail-Aware MDN locally explosive 原生匹配打板/Wasserstein 家族三件套统一鲁棒性度量）+ 2026-08-07 极新研究验证（arxiv 2608.07032）+ 文档从 v0.9.0 升至 v1.0.0 里程碑（21 项提案施工算法全覆盖+Wasserstein 家族成形） |
| 2026-08-10 | 1.1.0 | 十轮审查补 2 项选项外更优算法：① #7 补 **BR-iHMM**（Yiu/Sánchez-Betancourt/Cartea/Duran-Martin 2026，doubly outlier-robust online infinite HMM，Dirichlet Process 无限状态数自适应+emission/transition 双重离群鲁棒+在线流式更新，金融时序预测误差降低最多 67%）——与 v0.9.0 Wasserstein HMM 正交互补（Wasserstein HMM 解决标签漂移 label-switching，BR-iHMM 解决离群点毒化 emission/transition），列为 12 号 Phase 2 A2 修复第二候选（Wasserstein HMM 优先更轻量，BR-iHMM 作离群点密集场景升级）；② #3 补 **Wasserstein 生成式数据建模**（Huang et al. preprints 2026-02-28，WGAN 重构资产收益潜在分布+Wasserstein 模糊集鲁棒优化+双优化机制交替更新）——Wasserstein 家族生成式扩展（Certified DRO 用经验分布+LP，Wasserstein 生成式用 GAN 重建分布捕获非高斯尾部依赖），与 91 号 Phase 2 GPD/TailGAN 共享 GAN 栈协同，列为 Phase 4+ 远期探索（⚠️ preprint 需独立验证） | 十轮审查：选项外更优算法补充（BR-iHMM 从离群鲁棒方向补全 regime 检测 A2 修复方案+Wasserstein 生成式扩展家族覆盖非高斯尾部依赖）+ 2026 最新研究验证（BR-iHMM 67% 误差降低/preprints 2026-02-28 Wasserstein GAN+DRO）+ Wasserstein 家族从三件套扩展为四件套（regime 层 W-HMM+组合层 Certified DRO+仓位层 W-Kelly+生成式扩展 W-GAN） |
| 2026-08-10 | 1.2.0 | 十一轮审查补 4 项施工算法 why 缺口+选项外更优算法+过度工程纠偏：① #1/#2 补 A 股涨跌停 upstream contamination（arxiv 2507.07107v2 USTC 2026-05-09，涨停收盘价不可执行却进滚动窗口聚合致 IC 虚高 18%/Sharpe -0.44，mask-first 设计是 why）；② #6 补 AlgoXpert IS-WFA-OOS 协议（arxiv 2603.09219v1 2026-03-10 plateau 优先+purge gap+majority-pass/catastrophic-veto 门控）+plateau 启发式受控验证（Soloviov plateau.marketmaker.cc 2026，选择偏置有效 +0.12-0.31 OOS Sharpe 但独立过拟合检验弱）+PBO 零假设=0.5（marketmaker.cc 2026-07-01）；③ #19 补 Conformal-gated 执行 vs RL 执行（SOIC Vol.16 2026-08 U Hull，conformal 门控成本方差 19.1→10.0bps，PPO 跨种子高方差——反向印证"慢而稳 conformal 胜过 RL"在执行域成立，质疑个人系统 RL 执行必要性）；④ regime 层补 Robust HMM 替代谱系（egargale/hmm_test PRD #20 2026-05-29：Huber Robust/Student-t/GH/Feature Saliency/AH-HMM）；⑤ 过度工程纠偏：标注 Wasserstein 三件套+conformal 五变体栈经多轮累积偏"加法"，最小可行 baseline 边界需人决策收敛 | 十一轮审查：2026-08 极新研究（upstream contamination/AlgoXpert 协议/plateau 验证/PBO 零假设/conformal-gated 执行/Robust HMM 谱系）补施工算法 why 缺口 + 过度工程纠偏（多轮加法累积需收敛）+ 待定问题节补 5 项需人决策项 |
| 2026-08-10 | 1.3.0 | 十二轮审查补 2 项选项外更优算法+Lévy 家族交叉引用：① #3 补 **MFCCA 多重分形组合分配**（arxiv 2608.04987 Kakinaka&Umeno 2026-08 极新，带符号波动函数 signed fluctuation function 作风险泛函，MFCCA 保留符号使同向/反向运动以相反符号贡献风险，q=2 退化为 mean-variance 的尺度依赖极限，金融多资产实证样本内外均降低 drawdown/VaR/ES 不损失收益，符号保持比波动阶聚合对尾部风险贡献更大）——列为 30 号 risk parity 远期五级递进第五级（naive→HRP→Certified W-DRO→W-GAN→MFCCA，Phase 4+ 非 MVP）；② #1 补 **Lévy 家族重尾升级交叉引用**（见 91 号 v1.2.0）——DeepLévy（arxiv 2605.10364v3 UNSW 2026-05-14，α-stable mixture+特征函数匹配 CFM 绕开不可解 PDF，α<2 方差无限是数学上最重参数化尾部）作 Student-t MDN 极端尾部升级+Lévy-Flow（arxiv 2604.00195 Drissi 2026-03，VG/NIG normalizing flow 替换 Gaussian 基，VaR Kupiec p=1.00+ES 低估仅 1.6%）作 Phase 2 生成式精度替代，形成 Student-t/α-stable/VG-NIG 三家族重尾密度预测完整谱系；③ 文档头补 v1.3.0 审查说明 | 十二轮审查：选项外更优算法补充（MFCCA 多重分形是 mean-variance 的多重分形扩展+Lévy 家族是 Student-t 之外的重尾密度预测谱系）+ 2026-08 极新研究验证（arxiv 2608.04987/2605.10364v3/2604.00195）+ 延续 v1.2.0 过度工程纠偏（MFCCA 与 Lévy 家族均定位远期升级/替代非 baseline） |
| 2026-08-10 | 1.4.0 | 十三轮审查补 3 项选项外更优算法，聚焦 2026-07/08 极新研究+风控优先原则核心：① #2 补 **Cross-Sectional Heterogeneity LSTM**（arxiv 2608.05755 Döbelt 2026-08-06 极新，learnable sector embeddings+宏观协变量+label smoothing/dropout/gradient clipping 正则，S&P 500 long-short 超基准+可解释 sector contribution metric）——是 25 号多因子+22 号板块轮动的"输入端截面增强"非新增架构（LSTM 主体不变，~50 行 embedding 层+协变量拼接），对接 91 号 v1.3.0 Phase 1.5+ 截面特征增强；② #4 补 **Drawdown Risk Beyond Brownian Motion**（arxiv 2608.00127 Landolfi 2026-07-31 极新，扩展 RSB 回撤框架，蒙特卡洛生成 4 决策测度查找表 MaxDD/Max Loss/Final Negative Time/Longest Recovery Time，非高斯下固定 Sharpe+波动率变化偏度/肥尾/波动率聚类/Sharpe 估计不确定性致四测度分化→单一 Gaussian 表系统性误警，fBM 长记忆的"放大"是自相似色散尺度效应 T^(H-1/2) 非 path geometry 深化→sqrt(T) 校准失效非内在危险）——**直接对应项目风险优先原则核心（4 级回撤 Protocol 8/15/20/25% + drawdown_controller）**，提供数据驱动阈值校准路径（按真实 Sharpe+波动率+偏度+肥尾+Hurst 生成查找表，Level1-4 映射 MaxDD 分位数），末态负时间+最长恢复时间量化 30 号 §2.5 恢复机制（企稳 50%→恢复时间分布中位数），与 91 号 Lévy 家族形成"密度预测→回撤测度"上下游闭环，定位 drawdown_controller Phase 2 阈值校准升级；③ #18 补 **CAI++ Copula Asymmetry Index**（Risks 2026,14,86 Hatzopoulos&Statiou 2026-04-13，CAI=滚动窗口联合"股跌&波升"尾部事件经验频率-镜像态"股升&波降"经验频率 rank-based 非参数，CAI++ 框架 smoothing/standardization/delayed execution/hysteresis/cost-aware portfolio mapping 转防御信号，2000 年起 50 对 equity-volatility 实证 vs B&H/60-40/inverse-vol risk parity/SMA-200，vs 60-40 占优但不替代 risk parity 定位 tail-aware overlay）——是 §18 股指期货 IF/IC/IH/IM P2 背景级的"防御信号转化"路径（用 IF/IC 收益+10 号 synthetic VIX 算 CAI），延迟执行+迟滞与 4 级回撤恢复机制同构防抖动，定位 drawdown_controller/kill_switch Phase 2 事前防御 overlay | 十三轮审查：选项外更优算法补充（Cross-Sectional LSTM 截面异质性输入端增强+Landolfi 非高斯回撤测度查找表+CAI++ 尾部不对称防御信号）+ 2026-07/08 极新研究验证（arxiv 2608.05755/2608.00127/Risks 2026,14,86）+ 风控优先原则核心增强（Landolfi 直击 4 级回撤阈值校准+CAI 事前防御 overlay，风险模块优先施工符合硬约束）+ 延续过度工程纠偏（三项均定位 Phase 1.5+/Phase 2 升级非 MVP baseline，Cross-Sectional LSTM 是输入端增强非新增架构） |
| 2026-08-10 | 1.5.0 | 十四轮审查补 3 项选项外更优算法评估（2026-08-08 最新研究全网搜索）：① #20 补 **AlphaCrafter revalidate 衰减感知再验证闭环**（arxiv 2605.05580, 2026）——多智能体框架中 Miner Agent 周期性重验因子 IC/ICIR/换手/覆盖/跨 regime 衰减剖面+自动剪枝显著衰减因子。**仅借鉴 revalidate 概念+跨 regime 衰减剖面两个维度**（项目 factor_pool_manager 已有 8 状态生命周期治理+decay_monitor+three_level_judgment，revalidate 是其学术印证），多智能体框架本身不采纳（过度工程）；② #2 评估 **Functional Orthogonality ICML 2026**（arxiv 2606.21385 Simon/Frossard/De Vleeschouwer）——生成映射 Jacobian 正交约束实现非线性正交化，替代 PCA/Gram-Schmidt 线性正交。**评估后不采纳**：25 号 §3.1 已拒绝线性正交化（8-15 因子规模下 correlation_dedup 已足够），非线性正交化更复杂且损失可解释性，ICML 纯数学理论远超项目需求；③ #8 评估 **Low-Rank Graphon Contagion**（arxiv 2608.04529 Feng 2026-08-06）——异质金融网络动态阈值困境传染的低秩与 graphon 极限渐近理论。**评估后不采纳**：理论渐近结果（N→∞）对 A 股 3-5 策略小规模组合无直接适用性，37 号 Hawkes+SaR 双层预警已覆盖流动性危机传染检测需求 | 十四轮审查：全网搜索 2026-08-08 最新研究（arxiv 2605.05580/2606.21385/2608.04529），3 项选项外更优算法经评估后 1 项部分采纳（AlphaCrafter revalidate 概念借鉴）+2 项不采纳（functional orthogonality 过度复杂+graphon 渐近理论不适用小规模）。延续过度工程纠偏纪律 |
| 2026-08-10 | 1.5.1 | 十四轮审查补 1 项选项外更优算法+91 号同步：① #3 补 **TRP 拓扑风险平价**（arxiv 2604.16773 Nayar/Ainasse/Kulkarni FMI Technologies 2026-04-18）——从相关性-距离图提取稀疏有根 MST 拓扑+传播法则将带符号信号映射为组合权重。**直击 HRP 两大局限**：① HRP 仅 long-only（递归二分+逆方差只能产生非负权重），TRP 原生支持多空（w_v=s_v×g_v 正信号→多头/负信号→空头）；② HRP 纯风险分配忽略 alpha 信号，TRP 保留信号方向（w_v=L×s_v×g_v/||x||₁）。核心参数 Mixed Split-Replication Coefficient α_u(ρ)=(1-ρ)+ρ/b(u)，ρ=0 退化为纯信号归一化/ρ=1 退化为保守等分。Semi-Supervised TRP 变体 II 的"市场根→行业 ETF→个股"层级直接对接 22 号板块轮动（申万一级 28 行业作第二层）。ρ 参数可对接 regime（r3 牛市 ρ 低=信号驱动，r4 熊市 ρ 高=保守等分），是 34 号 Shrinkage 的拓扑维度补充。risk parity 远期递进扩为六层：naive→HRP（long-only）/TRP（long-short+信号）→Certified W-DRO→W-GAN→MFCCA。定位 Phase 2 演进（与 HRP 并列二选一），非 MVP 必需；② 同步 91 号 v1.4.0 补 **Exformer 极端自适应 Transformer**（arxiv 2607.02437 2026-07-02，极端自适应注意力 Extreme Attention 专攻稀有极端事件间 event-aware 依赖，与打板"涨停→炸板"原生匹配，与 QFCQT 正交分工全局 regime 突变 vs 局部极端事件，Phase 1.5+ backbone 升级） | 十四轮审查：选项外更优算法（TRP 直击 HRP 多空+信号两大局限，Semi-Supervised 变体对接 22 号板块轮动）+ 2026-04 极新研究验证（arxiv 2604.16773）+ 91 号同步（Exformer 极端自适应 Transformer v1.4.0）+ 延续过度工程纠偏（TRP 是 HRP 增强非全新架构 MST+DFS ~150 行，Exformer 是标准 MHA 稀疏化变体 ~100 行） |
| 2026-08-10 | 1.6.0 | 十五轮审查补 2 项选项外更优算法评估（2026-08-08/09 最新研究全网搜索）：① 补 **A 股羊群效应 Johnson S_U 尾部指标**（arxiv 2607.27063, 2026-07-29）——agent-based 网络模型解释 A 股动量与反转，Johnson S_U 变换构建滚动尾部羊群指标，与 CSAD/LSV 对比在重大冲击期上升。**部分采纳**：agent-based 模型不采纳（理论工具），仅借鉴 Johnson S_U 尾部羊群指标概念——CSAD 的尾部增强版（非线性变换恢复尾部信息），可作 25 号另类因子或 37 号预警信号，scipy.stats.johnsonsu ~50 行实现，Phase 2 候选与 32 号 HBI/CSAD 并列评估；② 评估 **MINGLE 联合因子图框架**（arxiv 2608.06618, 2026-08-06）——"系统性因子暴露画像"重新定义图局部性+ADMM 联合学习。**评估后不采纳**：ADMM+图拓扑学习对个人系统偏重（与已拒绝 HRP/MVO 同类复杂度），5 策略规模边际收益不显著，依赖因子暴露矩阵估计引入不稳定性，记 Phase 5+ 远期候选 | 十五轮审查：全网搜索 2026-08-08/09 最新研究（arxiv 2607.27063/2608.06618），2 项选项外更优算法经评估后 1 项部分采纳（Johnson S_U 尾部羊群指标概念借鉴）+1 项不采纳（MINGLE ADMM 过度复杂）。延续过度工程纠偏纪律。注：本轮搜索发现的大部分 2026-08 研究（arXiv:2608.00127 回撤查找表/arXiv:2602.03903 RWC/arXiv:2603.04441 Wasserstein HMM/arXiv:2606.09478 CSI300 regime HARQ/arXiv:2606.12843 A股 TreeSHAP/arXiv:2608.03616 级联 EWS 警示/arXiv:2605.23905 AI alpha 衰减同质化/arXiv:2602.00080 GT-Score）已在之前各轮审查中分别集成到对应文档（35/10/13/34/15/37/61/14 号），本轮仅新增 2 项未覆盖研究 |
| 2026-08-10 | 1.7.0 | 十六轮审查补 7 项选项外更优算法评估（2026-08-08~10 最新研究全网搜索，后台 agent 返回 18 篇 2026-07/08 论文+实践源，筛除已在之前各轮集成的 11 篇，新增 7 项未覆盖研究评估）：① **ARM 检测器无关变点归因**（arXiv:2608.01691 Peng/Wu/Yan/Chen/Shen 2026-08-03）——wrapper 接受任意检测器（HMM/PELT/Bai-Perron）定位的变点，返回经认证的坐标级归因+位置/尺度类型标签，三重有限样本保证（per-coordinate validity / FWER Westfall-Young permutation / FDR Benjamini-Yekutieli+e-BH），2008 金融危机五金融序列验证+公开代码。**部分采纳**：55 号 §3.11 v1.11.0 刚补五项鲁棒变点检测算法（LBD-FDR/Robust CUSUM/Tail-adaptive CUSUM/RCD/DeCAFS），ARM 是它们的**归因层 wrapper**——检测器管"何时变"，ARM 管"哪些坐标变了+误差控制"，正交互补非竞争。记为 55 号 §3.11 Phase 2 升级（FWER/FDR 控制是 Basel LR_ind/LR_cc 条件覆盖要求的直接对应）；② **Plateaus/Peaks 过拟合诊断排序**（Soloviov 2026-06 dsr.marketmaker.cc + github.com/suenot/plateau-robustness）——控制仿真已知 ground-truth Sharpe surface，**plain PSR vs zero skill 是最强单一诊断 AUC 0.808，领先 DSR 0.785 和 PBO 0.669**；plateau-geometry 单独弱（AUC 0.501=随机）但与统计量组合有效；选择规则偏好去噪 landscape 的宽最优 OOS Sharpe +0.12~0.31。**部分采纳**：更新 P-5 过拟合检测协议评估——当前 P-5 建议方向②（现有体系+PBO 零假设=0.5），Soloviov 实证进一步建议 **PSR 应作主诊断（AUC 最高）+DSR 补充+PBO 零假设修正**，非 DSR 优先。54 号 deflated-alpha 三重验证 + 55 号五层检测链中 DSR/PBO 的主次排序需据此调整；③ **流动性审计 Systemic Fragility Index**（arXiv:2606.29018 Aldridge 2026-06）——多期 regret 分解+model-free 流动性分类器（realized cost × strategy decision 协方差符号=提供方 vs 消费方）+恢复 Roll implied spread+聚合流动性失衡闭式 fire-sale+**显式"early-warning properties"节用 ρ̂ 作 regime 指示器**+系统性风险扩展含 Fragility Multiplier+observable Systemic Fragility Index（CRSP 2016-2025 校准）。**部分采纳**：37 号流动性危机当前用卖压+价差+Hawkes，Systemic Fragility Index 是 model-free 的**系统性脆弱度合成指标**（不依赖订单流建模，用 regret 分解直接计算），与 37 号 Hawkes 微观结构预警正交互补（Hawkes 管 event clustering，Fragility Index 管 system-level 脆弱度）。记为 37 号 Phase 2 候选；④ **流动性危机=基本面锚定失败**（arXiv:2607.16970 Novotny 2026-07-18）——agent-based 订单簿模型，流动性供给锚定基本面价值，恢复力（均值回归+簿册回填）是鲁棒内在稳定器；**核心发现：流动性危机是基本面锚定失败，非做市失败**；order parameter = 簿册单边性（one-sidedness，流动性压力指标，非方向性崩盘）；六条传输通道压力均不传至耦合的平静市场。**部分采纳**：37 号当前用 sell_pressure（卖压）+ spread（价差）作双条件触发，Novotny 的"簿册单边性"是**新信号维度**——卖压管方向性抛售，单边性管流动性撤退（卖方挂单全撤/买方挂单稀缺），两者正交。A 股涨跌停是单边性极端态（涨停=纯买方单边簿，跌停=纯卖方单边簿），miniQMT 可获取十档盘口计算单边性。记为 37 号 Phase 2 候选（与 VPIN/OBI/Depth-to-Vol 并列）；⑤ **重尾流动性需求 Student-t ν 状态变量**（arXiv:2607.01198 Çetin/Lin/Livieri LSE 2026-07-21）——序列限价订单簿+不对称信息+重尾（Student-t ν>2）非知情订单流，更重尾扁平深度价格影响+减缓学习——**"流动性尾部风险是价格发现的状态变量"**，单参数 ν 控制稀有流动性 regime 发生频率，10 级 AAPL 数据实证。**部分采纳**：36 号 VaR/ES 当前用历史模拟+参数法，ν 参数是**尾部流动性 regime 的 principled 标量度量**——比历史模拟更可解释（ν→∞ 退化为 Gaussian 基线，ν 小=重尾=尾部流动性事件频发），可作为 36 号 §3 波动率调整的**前瞻状态变量**（ν 下降→预期尾部流动性事件增多→VaR 上调）。记为 36 号 Phase 2 候选；⑥ **Numinor SAM 供应链网络因子放大器**（numinor.io 2026-05）——标准因子通过 ChinaScope 供应链 peer 网络（SAM）路由，22 因子 Barra 式 A 股模型 +0.149 ΔICIR / +0.54~0.72 Sharpe lift / 8/8 walk-forward 年正（2019-2026），**贡献是组合波动降低 ~37% 非均值收益增强**——是现有因子簿的 amplifier。**评估后条件性采纳**：25 号多因子当前用 Winsorize/MAD 去极值+前向收益行业调整+残差 alpha 合成，SAM 是**网络结构因子增强**（行业调整管产业链，SAM 管供应链上下游传导），但依赖 ChinaScope 供应链数据（付费数据源）。记为 Phase 2 候选（数据可得时评估，akshare/tushare 有部分供应链数据但覆盖度远低于 ChinaScope）；⑦ **华泰三级全球流动性风险预警模型**（华泰金工 2026-03）——三层架构：央行流动性（价格/量/预期，27 央行）+融资流动性（SOFR vs IORB/EFFR/FFRU/OIS 阈值+FX risk-reversal 套息交易去杠杆）+市场流动性（8 跨资产 implied vol 指数 VIX/VXN/RVX/MOVE/GVZ/OVX/VXEEM/COP 滚动 Z-score），9 资产组合 2008-2026：年化 5.31%→8.76% / Sharpe 0.56→1.22 / MaxDD -34.55%→-14.09%。**部分采纳**：37 号流动性危机当前 A 股盘内+日频双级监控，华泰三级框架提供**全球流动性系统性视角**——A 股与全球流动性强相关（北向资金=外资流入通道），8 跨资产 vol 指数的滚动 Z-score 是**cross-asset 早期预警信号**（VIX 飙升领先 A 股波动率 1-3 天）。记为 37 号 Phase 2 候选（与 Systemic Fragility Index 互补——Fragility 管 A 股微观结构脆弱度，华泰三级管全球宏观流动性环境）。**不采纳项**：⑧ Microstructure Mean Reversion（arXiv:2608.00885 2026-08-01）closed-form OU band θ*(θ*-φ)=s_G² 适用于秒级 HF market-making，A 股 T+1+miniQMT 中低频不适用，记 Phase 5+ 远期参考；⑨ Diffusive Paradox（arXiv:2608.00988 2026-08-04）理论物理论文非可施工算法，记理论参考；⑩ CVaR Puts+Trend（arXiv:2607.00883 2026-07-01）temporal separation 原理概念有用但 A 股个人投资者无期权市场不可施工，记理论参考；⑪ FinSMART（arXiv:2607.28127 2026-07-30）market-aligned RL for sentiment GRPO 过重，记 Phase 5+ 远期；⑫ Text-enhanced regime（arXiv:2605.30363 v2 2026-08-02）LLM+FOMC+VAR 检测器无关验收模式有借鉴价值，但 FOMC 美国专属，A 股对应政策局会议纪要/央行货政报告，记 10 号 Phase 3+ 远期 | 十六轮审查：全网搜索 2026-08-08~10 最新研究（后台 agent 返回 18 篇 2026-07/08 论文+实践源），筛除已在之前各轮集成的 11 篇（Conformal Kelly/Non-Gaussian Drawdown/Barzykin Passive Impact/HMM+BIC 4-state 负结果/Interpretable A-share decomposition/GT-Score/RWC/Wasserstein HMM/CSI300 regime HARQ/AI alpha decay/Cascading EWS），新增 7 项未覆盖研究评估——4 项部分采纳（ARM 变点归因 wrapper+Systemic Fragility Index+基本面锚定失败单边性+Student-t ν 状态变量）+1 项条件性采纳（Numinor SAM 数据依赖）+1 项部分采纳更新既有评估（Plateaus/Peaks PSR>DSR>PBO 排序更新 P-5）+1 项部分采纳（华泰三级全球流动性 EWS）+5 项不采纳/远期。延续过度工程纠偏纪律——7 项采纳均定位 Phase 2 候选非 MVP baseline，5 项不采纳均因过度复杂或不适用 |
| 2026-08-10 | 1.8.0 | 十七轮审查补 4 项选项外更优算法评估（2026-08-07~10 最新研究全网搜索，后台 agent 返回 12 篇 2026-08-05~07 论文，筛除已在之前各轮集成的 8 篇，新增 4 项未覆盖研究评估）：① **QLoRA 情感分类≠可交易 alpha 负结果**（arXiv:2608.04200 Luo 2026-08-04）——基准测试 TF-IDF NB/FinBERT/Financial-RoBERTa/zero-shot Qwen2.5-7B/QLoRA Qwen2.5/LLaMA3/Mistral 共 7 模型在 S&P 100 2019 Benzinga 标题上的情感分类，**所有 7 模型分类准确率高（Mistral-7B 0.884）但 28 个模型-时间窗测试中 Newey-West+FDR 校正后无一显著**（最大 rank IC 0.0143 FinBERT 1 日），分类准确率与可交易截面信号存在明确鸿沟。**部分采纳**：26 号 v1.5.1 已有"QLoRA 情绪 OOS 经济性弱警示"，本论文提供**独立第三方实证背书**——高分类准确率不等于可交易 alpha。同时登记 **Newey-West+FDR 校正模板**作为情感因子的标准验证流程（rank IC × 模型-时间窗网格 → Newey-West 异方差自相关校正 → Benjamini-Hochberg FDR 多重检验校正）；② **MFCCA 符号化多重分形组合分配——更新既有登记**（arXiv:2608.04987 Kakinaka & Umeno 2026-08-05）——用 MFCCA（多重分形交叉相关性分析）的**符号化涨落函数**作风险泛函替代协方差矩阵，保留局部去趋势协方差的符号（同向 vs 反向贡献相反），q=2 退化为均值-方差。**实证**：OOS 降低 drawdown/VaR/ES 且不损失收益。**更新既有登记**：90 号已有"MFCCA 多重分形组合分配"登记，本论文新增**符号化**变体证据（OOS drawdown 降低）。**不改变采纳决定**：30 号 §3.1 已裁定"不做 MVO、不做协方差估计"，MFCCA 符号化虽非 MVO 但仍是协方差矩阵的多重分形扩展，3-5 策略规模下复杂度不匹配。维持 Phase 5+ 远期候选（策略数>8 且 32 号 correlation_dedup 漏检率高时重评，与 MINGLE 同条件）；③ **Wasserstein 鲁棒组合优化认证误差界——更新既有登记**（arXiv:2608.07032 Hsieh & Gan 2026-08-07）——高维 Wasserstein 分布鲁棒组合优化（order-1 Wasserstein 模糊集），long-only+box support+one-norm ground metric 下用支撑超平面 majorize 效用+对偶化子问题→多项式规模 LP，**均匀效用近似误差界同时界 robust-value 误差和近优性 gap**，月度 476 资产再平衡验证可扩展至 1000 资产。**更新既有登记**：90 号已有"Wasserstein 家族四件套（regime/组合/仓位/生成式层）"登记，本论文新增**认证误差界**（computable gap，多数 DRO 论文不给可计算 gap）。**不改变采纳决定**：项目已拒绝 MVO，Wasserstein 鲁棒组合是 MVO 的鲁棒版本，30 号 §3.1 约束不变。维持 Phase 5+ 远期候选；④ **Stationary Ambiguity 稳健 RL 训练**（arXiv:2608.04832 Mueller/Akkari/Wood/Gonon 2026-08-05）——策略在仿真中优化后随时间失去鲁棒性因策略推断隐参数并特化于它；提出"stationary ambiguity"：模糊性随系统状态变化但不系统性衰减，导出稳态滤波过程。**对冲问题验证**：stationary ambiguity 下训练的策略对隐因子（如波动率 regime 切换）保持鲁棒性。**不采纳（MVP）**：项目 RL 组件（41 号阶段 7 执行 RL）为 Phase 4+ 远期，当前 MVP 无 RL 策略。记为 41 号 Phase 5+ RL 训练方法论候选——当阶段 7 RL 施工时采用"state-dependent parameter randomization 使滤波过程稳态"原则，避免策略过拟合到检测到的 regime。**不采纳项**：⑤ Distress contagion graphon（arXiv:2608.04529）低秩因子化+图函数极限+占据时间恢复模型，理论性 systemic-risk 框架，需 A 股机构间暴露数据，记 Phase 5+ 理论参考；⑥ Policy-distance certificates（arXiv:2608.05901）Fenchel 对偶+Doob 补偿+占据测度的策略约束认证，理论诊断工具，记 Phase 5+ 理论参考；⑦ Lambda-quantiles（arXiv:2608.07122）泛化 VaR/CVaR 的状态依赖分位数，纯理论无实证，记理论参考 | 十七轮审查：全网搜索 2026-08-07~10 最新研究（后台 agent 返回 12 篇 2026-08-05~07 论文），筛除已在之前各轮集成的 8 篇（CVaR RaQL/Cross-Sectional LSTM/FinSMART/MINGLE/HMM+BIC 4-state 负结果等），新增 4 项未覆盖研究评估——1 项部分采纳（QLoRA 情感负结果独立背书+Newey-West+FDR 验证模板）+2 项更新既有登记不改变采纳决定（MFCCA 符号化/Wasserstein 认证误差界均维持 Phase 5+）+1 项不采纳 MVP（Stationary Ambiguity RL 训练记 41 号 Phase 5+）+3 项不采纳理论参考。延续过度工程纠偏纪律。施工算法完整性审查 5 篇文档（36/22/25/42/41 号）结论：22 号 5 状态分类有完整 4 维输入+规则映射伪代码（v1.6.0 补全）、25 号 MAD 去极值+行业中性化有伪代码、42 号 Chandelier Exit 有公式+降级伪代码、41 号 C-031 分批建仓有伪代码+输出契约，均无施工算法缺失 |
| 2026-08-10 | 1.9.0 | 十八轮审查补 5 项选项外更优算法评估（2026-08-08~10 最新研究全网搜索，后台 agent 返回 45 篇 2026-08-03~10 论文+行业报告，筛除已在之前各轮集成的 34 篇，新增 5 项未覆盖研究评估）：① **Fragile Frontier: Markowitz 脆弱性诊断 Sobol 全局敏感性**（[arXiv:2608.03518, 2026-08-04, Pellegrino/Vannucci/Siciliano](https://arxiv.org/abs/2608.03518)）——用 Sobol 指数对 Markowitz 组合做全局敏感性分析，映射输入不确定性和构造选择沿有效前沿传播：低目标收益由 l2 正则化主导，激进收益由权重上限和预期收益扰动主导，有效分散化急剧下降+权重分散上升。多资产 ETF 宇宙多宇宙脆弱性图谱。**部分采纳**：32 号 G13 已裁定"不做 MVO、不做协方差估计"，本文提供**独立定量背书**——Markowitz 有效前沿在激进收益区由预期收益微扰主导权重分配（Sobol 指数高），正是"参数估计噪声→权重脆弱"的量化证据。不改变裁定但增强信心：32 号 O(N) inverse-vol 自然叠加在 3-5 策略规模下是 Sobol 脆弱性诊断下的最优选择（零参数估计→零 Sobol 敏感性）。若未来策略数>N 阈值考虑 MVO 路线时，须先跑 Sobol 诊断确认脆弱性可控。记为 32 号 Phase 5+ MVO 重评的前置诊断工具；② **AlphaSchema: LLM 驱动结构化 Alpha 挖掘（A 股 CSI 实证）**（[arXiv:2607.26642, 2026-07-30, Yi et al. 清华/Monash](https://arxiv.org/abs/2607.26642)）——将 alpha 挖掘解耦为语义探索与代码实现，每个候选因子表示为五维 schema plan（Event/Context/Qualities/Direction/Output），LLM 翻译 schema→可执行因子，累积奖励学习语义空间代理模型。**中国市场（CSI）实证**：+FUNDAMENTAL 变体 IR=1.0877, AER=11.94%。**部分采纳**：15 号 v1.16.0 已登记 CogAlpha/AlphaAgent 等 LLM alpha 挖掘参考，AlphaSchema 新增**五维 schema plan 解耦设计**——语义探索（人类可解释因子逻辑）与代码实现（LLM 翻译）分离，降低纯 GP/RL 黑箱因子过拟合风险。A 股 native 实证是关键优势（vs AlphaEval 在美股）。记为 15 号 Phase 3+ 远期候选（与 CogAlpha 并列评估，schema plan 的可解释性约束对齐项目"可解释性优先"原则）；③ **FINSABER: LLM 交易策略 20 年长期评估 regime 负结果**（[arXiv:2505.07078, KDD 2026, Li et al. 爱丁堡/UCLA/牛津/SKKU](https://arxiv.org/abs/2505.07078)）——20 年+100+标的回测框架，关键发现：**LLM 策略在牛市过度保守（跑输被动基准），在熊市过度激进（遭受重创）**，需要 regime 感知和自适应风险控制而非单纯增加框架复杂度。**部分采纳**：与 mathandmarkets V6.3 集成负结果（G02 前沿演进⑤）+ HMM+BIC 4-state 负结果（G02 ⑧）形成"三重 regime 负结果警示"——①集成平均压扁信号（mathandmarkets）；②regime 条件化检测以 recall 换 precision（HMM+BIC）；③LLM 策略无 regime 感知在牛熊两端均失效（FINSABER）。三项共同验证项目 regime→Shrinkage"节流"而非"条件化检测"设计的正确性。FINSABER 额外启示：LLM 策略的 regime 感知须嵌入风险控制层（非信号层），与 28 号情绪周期 sleeve 内 alpha 择时+34 号 regime 元分配 budget 节流的分工一致。登记为 90 号 regime 设计哲学的第三项独立背书；④ **Preference Robust Distortion Risk Measures**（[arXiv:2608.02854, 2026-08-03, Bernard & Pesenti](https://arxiv.org/abs/2608.02854)）——用 Wasserstein 距离和 Bregman 散度在扭曲函数上构建模糊集，推导最坏/最好情况扭曲风险度量的闭式解，扩展到秩依赖效用（RDU）。**不采纳**：理论风险度量框架，扭曲函数模糊集对 A 股个人量化系统过度抽象——项目风险度量已定（VaR/ES/CVaR+回撤 Protocol 四级阈值），偏好稳健性在 3-5 策略规模下边际收益极低。记为 Phase 5+ 理论参考；⑤ **Preying on Leveraged ETFs 收盘再平衡操纵**（[arXiv:2608.03703, 2026-08-04, Zhao](https://arxiv.org/abs/2608.03703)）——韩国 2026 市场极端波动由套利者捕食杠杆 ETF 收盘再平衡驱动，年化波动率增加 47 个百分点。**部分采纳**：A 股有分级基金/杠杆 ETF（虽 2020 年后分级基金退场但杠杆 ETF 2024 年起重启），37 号流动性危机当前监控卖压+价差+Hawkes，LETF 收盘再平衡操纵是**新操纵模式维度**——套利者提前买入→收盘价成交放大→制造的流动性中卖出。与 40 号执行层 14:50-14:57 尾盘集中执行窗口直接相关：若 A 股 LETF 规模增长，尾盘操纵风险上升，40 号须评估"避开 LETF 再平衡日尾盘"执行约束。记为 37 号/40 号 Phase 2 候选（监控 A 股 LETF 规模增长，当前规模较小暂不紧急）。**不采纳项**：⑥ Smooth Structural Change in Cointegrated Systems（arXiv:2608.03773）核加权局部降秩 VECM，regime 检测方法学参考但 A 股无协整策略不适用，记 10 号 Phase 5+ 理论参考；⑦ Autonomous Formulaic Alpha Discovery 综述（arXiv:2608.01789）进化计算视角 alpha 挖掘综述，非新算法，记 15 号参考；⑧ LLM 激活探测 ESG（arXiv:2608.07208）线性探测从冻结 LLM 激活提取概念度量，需中文 LLM 适配，记 26 号 Phase 5+ 远期；⑨ F²Agent 多模态交易智能体（arXiv:2608.05668）美股/加密货币测试，过重架构，记 Phase 5+ 远期；⑩ Hawkes-Driven OTC Market Making（arXiv:2608.02002）OTC 外汇做市场景，Hawkes 方法论已覆盖，记理论参考；⑪ Public Trader Identity（arXiv:2608.04373）DeFi 钱包地址特定，A 股无对应数据，记理论参考 | 十八轮审查：全网搜索 2026-08-08~10 最新研究（后台 agent 返回 45 篇 2026-08-03~10 论文+行业报告），筛除已在之前各轮集成的 34 篇（CVaR RaQL/Cross-Sectional LSTM/FinSMART/MINGLE/HMM+BIC 4-state 负结果/Non-Gaussian Drawdown/Barzykin Passive Impact/ARM/QLoRA/MFCCA/Wasserstein DRO/Stationary Ambiguity/Systemic Fragility Index/基本面锚定失败/Student-t ν/SAM/华泰三级 EWS/GT-Score/RWC 等），新增 5 项未覆盖研究评估——3 项部分采纳（Fragile Frontier Markowitz Sobol 诊断背书"不做MVO"+AlphaSchema A 股 LLM alpha 挖掘 schema plan+FINSABER LLM regime 负结果第三重背书）+1 项不采纳理论（Preference Robust Distortion）+1 项条件性采纳（Preying on LETF 监控 A 股 LETF 规模增长）+6 项不采纳/远期。延续过度工程纠偏纪律。施工算法完整性审查结论：本轮审查覆盖 38 篇文档全量版本号一致性扫描，修复 5 篇文档 8 处版本漂移（35/36/32/52/53 号），36 号补全缺失 v1.17.0 修订记录，90 号补全缺失 v1.9.0 修订记录。施工流程算法闭环无缺失独立环节 |
| 2026-08-10 | 1.10.0 | 十九轮审查补 3 项选项外更优算法评估（2026-08-08~10 第五轮全网搜索，后台 agent 返回 12 篇 2026-08-01~06 论文，对照 v1.0.0-v1.9.0 已集成清单去重后筛除 9 篇已评估，新增 3 项未覆盖研究评估）：① **遍历 Markov 过程密度拟合优度检验**（[arXiv:2608.03088, 2026-08-04, Martin/Nishiyama/Stachurski/Xie](https://arxiv.org/abs/2608.03088)）——提出密度型 GoF 检验，将数据与零假设指定的模型类比较，若类中无模型的平稳密度匹配数据则拒绝，无需指定备择假设，对 1/√n 局部备择有非平凡功效。**部分采纳**：项目 10/11/12 号 regime 验证体系当前用 AIC/BIC/预测似然/Wasserstein 距离做模型选择，缺**正式的平稳密度拟合优度检验**——本检验直接回答"regime HMM 模型类是否正确刻画状态平稳分布"，与 A2 标签对齐验证正交（A2 管 label-switching，GoF 管 distribution fit）。Stachurski 是计算经济学权威（QuantEcon），实施成本低（纯统计检验~40 页）。记为 12 号 Phase 2 验证工具集候选（与 Wasserstein HMM template tracking 并列——W-HMM 管 label 漂移修复，GoF 管 model class 适用性事前检验）；② **CVaR 风险感知 Q-Learning 自适应有限预算训练**（[arXiv:2608.04305, 2026-08-05, ICAIF '26, Wu/Lei/Huang](https://arxiv.org/abs/2608.04305)）——不改变 CVaR 估计器与 Bellman 不动点，仅重新设计训练流程（6 项协同机制：逐格内步长/外层速率同步衰减/VaR 内变量早期校正/覆盖优先再贪婪采样/成熟估计渐进后缀聚合/在线可观测标度校准），将 CVaR Bellman 残差降约 85%。**部分采纳**：项目 41 号阶段 7 执行 RL 已评估 TT-DAC-PS/MAP-Elites/Constrained RL+Shield 三法分工（成本/适应性/合规），本方法**不引入新 RL 算法而是改进训练流程**，与三法正交——若 41 号采用 CVaR 目标（Constrained RL 路线），此训练控制器可直接配套降残差。8 页实施成本低。记为 41 号 Phase 5+ RL 训练流程候选（与 v1.8.0 Stationary Ambiguity 并列——Ambiguity 管参数鲁棒性，本方法管 CVaR 估计收敛性）；③ **Proper-Score 观测驱动滤波器**（[arXiv:2608.02828, 2026-08-03, Livieri/Palmari](https://arxiv.org/abs/2608.02828)）——将观测驱动滤波器更新规则从对数分数（log-score）推广到任意可微 proper scoring rule，分解出"风险曲率"与"创新波动性"两分量（对数分数下由 Bartlett 恒等式重合，一般情形分离），有界驱动限制极端观测对滤波路径传递——对金融肥尾数据是关键优势。**不采纳（MVP）/记远期**：项目 28 号已用 score-driven（Tsaknaki 2024 BOCPD score-driven 引用），本方法是其严格理论推广（88 页），实施成本高（需选 scoring rule+scaling+AR 参数）。核心实用洞察——"有界驱动限制极端观测传递"对 A 股肥尾（涨跌停/缺口）有接口价值。记为 28 号 Phase 3+ 远期增强候选（当 28 号 BOCPD 升级到 generalized score-driven 时评估 proper scoring rule 替换 log-score）。**不采纳项**：④ 组合次优性熵度量（arXiv:2607.09505 Sharma）纯理论 5KB 无实证，Kelly 偏差 KL 散度对偶表示概念有诊断价值但需 tilted measure 估计，记 31 号 Phase 5+ 理论参考；⑤ 基准相对回撤持续期（arXiv:2607.11335 Sekine/Wunsch）HJB 投影型控制相对基准回撤持续期，项目回撤是绝对回撤非相对基准，记 35 号 Phase 5+ 远期；⑥ Path Portfolio Optimization（arXiv:2608.02355 Noguer i Alonso）rough path signature 作组合坐标，样本量门槛高（每参数~6 观测），记 Phase 5+ 理论候选 | 十九轮审查：全网搜索 2026-08-08~10 最新研究第五轮（后台 agent 返回 12 篇 2026-08-01~06 论文），对照 v1.0.0-v1.9.0 已集成清单去重后筛除 9 篇已评估（Drawdown Beyond Brownian/RWC Schmitt/Autonomous Alpha Discovery 综述/Hawkes OTC/Cross-Sectional LSTM/graphon contagion/put+trend CVaR/Microstructure Mean Reversion 等），新增 3 项未覆盖研究评估——2 项部分采纳（遍历 Markov GoF 检验记 12 号 Phase 2+CVaR Q-Learning 训练记 41 号 Phase 5+）+1 项记远期（Proper-score 滤波器记 28 号 Phase 3+）+3 项不采纳理论参考。延续过度工程纠偏纪律。**施工算法完整性审查结论**：本轮对 20/21/23/24/26/27 号 Alpha 策略层 + 10/11/12/15/50/51/60 号基础层+治理层共 13 篇文档施工算法完整性深度审查——所有文档施工流程算法闭环无缺失独立环节。Explore agent 初报的"施工算法缺失"经逐篇核实均为**误报**（agent 仅读 excerpts 未读全文算法章节）：10 号 §9.12 施工环节算法完整性审查已回填全部 6 HMM 特征+overlay 维度+RiskSignal 系数；15 号 §3.4 因子预处理三步法（去极值/标准化/中性化）+ Mask-First 掩码算法完整（中性化标注"未实现"属骨架态非 spec 缺失）；20 号 §2.3 多因子筛选含双曲衰减 α(t)=K/(1+λt)+半衰期排序表+AlphaEval 五维评估；23 号 §3.2 方法选型表含 block-bootstrap/PBO/CSCV/DSR/Harvey-Liu/White RC 全公式；24 号 5 个 ```python 块含 classify_echelon_health/score_consecutive_height/MidBoardLossSignal 完整施工算法；26 号 9 个 ```python 块。00_index §7.3 占用表版本漂移 1 处修复（61 号 v2.2.0→v2.3.0） |
| 2026-08-10 | 1.10.1 | 二十轮审查补 1 项选项外更优算法+回归测门禁维度：① #6 回测门禁补 **Darmanin 三门控联合"实际可行性"框架**（[arXiv:2607.20093, 2026-07-22, Darmanin/Hecatus Research Malta](https://arxiv.org/abs/2607.20093) "Retail Trader's Ruin: An Anatomy of Popular Signal Failures"）——比 DSR 单维统计门控更全面的三门控框架：(1) 统计优势门控（多重检验校正后显著——Benjamini-Yekutieli 分层控制+平稳 bootstrap CI+暴露匹配基准+单边声明排除检验+等价性检验）；(2) 经济可行性门控（交易成本后净 alpha>0）；(3) 存活率门控（杠杆下有限资金存活率）。**关键负结果**：6 候选策略 4 个被 REFUTED（振荡器/成交量/日历/K线形态），趋势和动量 INCONCLUSIVE——印证 A 股 2026 量化危机"简单信号失效"趋势。**部分采纳**：与 BM-BT-05-G Deflated Sharpe 互补——DSR 管统计维度，Darmanin 三门控把经济可行性+存活率纳入上线门控，**记为 Phase 2 候选**（BM-BT-05-G 实施时同步引入避免"统计显著但实盘亏钱"陷阱）。FINRA/ESMA 杠杆场景可类比 A 股两融场景。 | 二十轮审查：全网搜索 2026-08-08 最新研究（后台 agent 返回 15 篇 2026-07/08 论文），筛除已在之前各轮集成的 12 篇（DSR Soloviov 2026-07 已在 v1.4.0 §4.5 ③/基本面锚定失败 Novotny 已在 v1.7.0 ④/Student-t ν 已在 v1.7.0 ⑤等），新增 3 项未覆盖研究评估——1 项部分采纳（Darmanin 三门控框架补回测门禁维度+2 项将登记到 36/37 号专项文档）+延续过度工程纠偏纪律。本轮回归 #6 回测门禁维度，补全 BM-BT-05-G DSR 单维度的"经济可行性+存活率"两个维度 |
| 2026-08-10 | 1.11.0 | 二十一轮审查补 4 项选项外更优算法+风控理论背书工具登记（2026-08-08 最新研究全网搜索，后台 agent 返回 30+篇 2026-07/08 论文，对照 v1.0.0-v1.10.1 已集成清单去重后筛除 26 篇已评估，新增 4 项未覆盖研究评估）：① #4 风险模型补 **Sharp Tail Bounds Beyond Twice the Mean**（[arXiv:2608.06317, 2026-08-06, Strack/Westermann UC Berkeley](https://arxiv.org/abs/2608.06317)）——对 n 个独立非负、均值≤1 随机变量证明 P[ΣXi≥t] ≤ 1−(1−1/t)^n（∀t≥2n+1），二元 i.i.d.（P[Xi=0]=1−1/t, P[Xi=t]=1/t）下取等且放松问题中仍最优。**核心价值**：分布无关（distribution-free）解析上界——不需假设正态/Student-t/任何参数族，仅依赖均值约束即给尾部概率严格上界，是 36 号 VaR/ES 历史模拟+参数法之外的第三条路径。**部分采纳**：定位为 36 号 VaR/ES 理论背书工具（验证历史模拟 VaR 极端尾部是否超解析上界），非独立施工算法。与 v1.4.0 ② Landolfi 回撤查找表协同（单期解析界→多期仿真表上下游闭环），与 v1.9.0 ① Fragile Frontier Sobol 诊断协同（参数估计噪声→权重脆弱的理论兜底），二元 i.i.d. 取等对 A 股涨跌停±10%二元分布特别紧致。适用条件 t≥2n+1 对 3-5 策略 t≥7-11 属极端尾部 VaR_99.5+范畴非日常 VaR_95。实施成本=0（闭式公式 `bound = 1 - (1-1/t)**n`）；② #2 因子分类补 **Body-Tail Factor Test**（[arXiv:2606.23596, Shin Sogang University, 2026-06-26 v3](https://arxiv.org/abs/2606.23596)）——将因子收益分解为 body（中心部分）+ tail（尾部部分），recombination identity 对每个因子模型成立。**关键发现**：q5 因子 spanning 最强但 body alpha 为负、tail alpha 为正——Sharpe 与 pricing error 可分离。**部分采纳**：25 号因子评估当前用 IC+SHAP，Body-Tail Test 提供第三维度 body/tail 分解——A 股涨跌停使 tail alpha 与 body alpha 差异显著，IC 可能被 tail 主导而 body 无信号。纯统计检验~50 行，定位 25 号 Phase 2 因子评估增强——对每个候选因子同时报告 body IC + tail IC + total IC，淘汰"total IC 正但 body IC 负"的伪信号因子；③ #2 因子分类补 **Robust Spatial-Sign Conditional Alpha**（[arXiv:2604.12252, Zhao/Wang, 2026-04-14](https://arxiv.org/abs/2604.12252)）——条件因子模型的 spatial-sign max-type + sum-type Cauchy 组合检验，渐近独立。**核心优势**：适用于重尾+时变系数+高维 N>T 场景，优于 GRS 检验与 sub-Gaussian 假设方法。**部分采纳**：25 号因子评估当前用 IC t 检验（假设近似正态），A 股收益重尾使 t 检验失效——Spatial-Sign 检验是重尾鲁棒的因子显著性检验，与 Body-Tail Test 互补（Body-Tail 管 body/tail 分解，Spatial-Sign 管重尾鲁棒性）。纯统计检验~60 行，定位 25 号 Phase 2 因子显著性检验升级——替代 IC t 检验作重尾场景的默认检验；④ #4 风险模型补 **Bayesian GP Tail Extrapolation**（[arXiv:2510.14637, Carl/Padoan/Rizzelli, 2025-10-16](https://arxiv.org/abs/2510.14637)）——β-mixing 条件下 Gaussian Process 的 Bayesian 后验，渐近 honest credible regions，动态条件尾分位估计。优于 naive Bayesian 和 MLE 置信域，支持 ARMA/GARCH/Markov copula。**记远期**：91 号密度预测 Phase 2 GPD/TailGAN 当前用频率派尾部估计（给点估计），Bayesian GP 提供"尾部外推的 honest credible region"——不仅给 VaR/ES 点估计还给置信区间，与 Sharp Tail Bounds 互补（GP 给精确尾部密度+CI，Sharp Tail Bounds 给分布无关上界包络）。GP+贝叶斯推断复杂度中等~200 行+MCMC，定位 91 号 Phase 3+ 远期候选 | 二十一轮审查：全网搜索 2026-08-08 最新研究（后台 agent 返回 30+篇 2026-07/08 论文），对照 v1.0.0-v1.10.1 已集成清单去重后筛除 26 篇已评估（Landolfi Drawdown/RWC Schmitt/MFCCA Kakinaka/Wasserstein HMM/ARM/QLoRA/Systemic Fragility Index/Student-t ν/AlphaSchema/FINSABER/LBD-FDR/Hawkes OTC/Microstructure Mean Reversion/Path Portfolio/Stationary Ambiguity/CVaR Q-Learning/Proper-Score/Lambda-quantiles/EVOQUANT/CSI300 regime HARQ/China Hawkes/Garcia Seuma criticality/An&Dai Transfer Entropy Hawkes/Weng Johnson S_U/Zhou square-root impact/MINGLE 等），新增 4 项未覆盖研究评估——3 项部分采纳（Sharp Tail Bounds 风控理论背书+Body-Tail 因子分解+Robust Spatial-Sign 重尾检验）+1 项记远期（Bayesian GP 尾部外推）。延续过度工程纠偏纪律——4 项均定位 Phase 2+/Phase 3+ 升级非 MVP baseline，Body-Tail+Spatial-Sign 是纯统计检验~50-60 行实施成本低，Sharp Tail Bounds 实施成本=0 闭式公式，Bayesian GP 是 91 号远期候选。施工算法完整性结论：本轮为选项外更优算法+理论工具登记，无新增施工算法缺失 |
| 2026-08-10 | 1.12.0 | 三十二轮审查补 2 项选项外更优算法（2026-08 最新研究全网搜索，聚焦 ML 合成排序层 + VaR 压力期校准层两个施工缺口）：① #2 因子分类补 **Uncertainty-Adjusted Sorting**（[arXiv:2601.00593, 2026-01](https://arxiv.org/abs/2601.00593) "Uncertainty-Adjusted Sorting for Asset Pricing with Machine Learning"）——ML 资产定价的组合构建普遍用点预测排序选股，本文用**不确定性调整预测区间**替代点预测排序。跨多种 ML 模型+美国股票面板，增益主要来自波动率降低（避开高不确定性股票）非收益提升，增益在灵活 ML 模型上最强，即使区间由部分或错误设定的不确定性信息构建仍持续（鲁棒）。**部分采纳**：与 25 号 Phase 4 ML 合成栈三件套正交——LambdaRankIC（v1.6.0）管训练目标、RankGLU（v1.7.0）管预测头架构、**Uncertainty-Adjusted Sorting（本项）管组合构建排序**，"训练→输出→排序"完整 ML 合成流水线各自独立增强。A 股涨跌停/停牌/缺口使单股收益不确定性天然偏高，自动降权高不确定性股票（涨停股次日不确定性高→降权），与 25 号 v1.5.0 Mask-First 可交易性掩码协同。实施成本低（~30 行：预测区间计算+排序键替换），定位 25 号 Phase 4 ML 合成引入后启用，非 MVP baseline；② #4 风险模型补 **Regime-Weighted Conformal Calibration (RWC)**（[arXiv:2602.03903v3, Schmitt, University of Oxford, 2026-08-03](https://arxiv.org/abs/2602.03903) "Taming Tail Risk: Conformal Calibration for Nonstationary Portfolio VaR"）——model-agnostic 包装器包裹任意条件分位数预测器，用过去预测误差构建安全缓冲，权重=指数时间衰减×regime 相似度权重。在**平滑 regime 漂移**下推导覆盖率上下界，**不假设加权可交换性**（比经典 conformal prediction 可交换性假设更弱）。CRSP 指数+16 美国股票组合 Basel 99%/97.5% 水平实证：TWC 是漂移下强默认，regime 加权改善慢适应预测器压力期校准。**部分采纳**：36 号 VaR/ES 压力期失准是已知痛点（超额发生率集中在压力期），RWC 提供 model-agnostic 校准层在 VaR 预测值外包 conformal buffer；36 号的 regime 检测（10 号 HMM 12 态）天然提供 RWC 所需 regime 相似度权重。与 §4 已登记三项形成"极端尾部上界→精确尾部密度→多期回撤仿真→压力期校准"完整 VaR 风控栈：Sharp Tail Bounds（v1.11.0）+Bayesian GP（v1.11.0）+Landolfi 回撤查找表（v1.4.0）+RWC（本项），四者正交不重叠。wrapper 模式轻量（~150 行），定位 36 号 Phase 2 VaR 校准增强，与 Landolfi 同 Phase 2 启用条件（需实盘数据校准） | 三十二轮审查：聚焦 ML 合成排序层（25 号 Phase 4）+VaR 压力期校准层（36 号 Phase 2）两个施工缺口，2 项选项外更优算法均部分采纳定位 Phase 2/Phase 4 升级非 MVP baseline。Uncertainty-Adjusted Sorting 实施成本低~30 行是 ML 合成标配排序逻辑非新增架构；RWC 是 wrapper 模式轻量~150 行解决 36 号已登记压力期失准痛点。延续过度工程纠偏纪律。施工算法完整性结论：本轮为选项外更优算法登记，无新增施工算法缺失 |
| 2026-08-10 | 1.13.0 | 三十四轮审查补 1 项选项外更优算法（中文来源搜索 2026-08-08~10 最新券商金工研究）：① 情绪周期补 **财信三维情绪模型"情绪浓度"维度**（[财信证券 2026-08-10 三维情绪模型跟踪周报](http://m.microbell.com/wap_detail.aspx?id=af811c52426cdd2d4a3fb234e46cf9d5)，刘飞彤 S0530522070001）——三维架构：情绪温度（主力买入率，中频~31 天周期）+情绪预期（期货升贴水+期权 PCR，中高频~16 天周期）+**情绪浓度（中信三级行业第一主成分方差贡献率，低频~30 天周期）**。高浓度→Beta 行情（系统性同涨跌），低浓度→Alpha 分化机会，浓度超警戒线 0.83 并形成顶部预示市场拐点。**部分采纳**：仅采纳"情绪浓度"第三维——28 号 v1.10.0 已有 5 阶段情绪温度+BOCPD/CUSUM 四法但无"行业联动度"维度，情绪浓度提供独立第三维衡量"资金是否共识"（vs 虹吸态管"资金往哪去"，正交互补）。情绪温度维度与 28 号炸板率/连板高度重叠不整合；情绪预期维度需期货/期权数据项目无接入不适用；情绪浓度仅需 sector_snapshot（582 只板块指数 production 已有）做 PCA~20 行可整合。HMM 模式转移规律（财信 2025-03 专题）与 28 号 §3.2 不可跳跃约束同构。定位 28 号 Phase 2 远期候选（浓度>0.83 触发退潮预警领先评分降级 1-2 日），非 MVP baseline | 三十四轮审查：中文来源（雪球/东方财富/券商金工）2026-08-08~10 全网搜索，对照 v1.0.0-v1.12.0 已集成清单去重，发现财信三维情绪模型"情绪浓度"维度是 28 号情绪周期未覆盖的独立第三维（行业 PCA 第一主成分方差贡献率）。arxiv 英文来源本轮 2026-08-04~10 候选（MINGLE/MFCCA/Wasserstein DRO/Path Portfolio/AutoQuant/LLM 因子搜索/Adaptive CVaR RaQL/CCAR Shapley/Microstructure Mean Reversion）均已在 v1.0.0-v1.12.0 各轮分别评估整合或不采纳。1 项部分采纳定位 Phase 2 远期候选。延续过度工程纠偏纪律。施工算法完整性结论：本轮为选项外更优算法登记，无新增施工算法缺失 |
| 2026-08-10 | 1.14.0 | 三十五轮审查补 2 项选项外更优算法（2026-08-08~10 最新研究全网搜索，后台 agent 返回 22 篇 2026-07/08 论文+行业报告，对照 v1.0.0-v1.13.0 已集成清单去重后筛除 15 篇已评估，新增 2 项未覆盖高价值研究评估+3 项简略提及）：① #2 因子分类补 **IGF BBP 相变因子数检测**（[arXiv:2607.06908, 2026-07-08, García-Medina](https://arxiv.org/abs/2607.06908) "Iterative Detection of Global Factors Near the BBP Phase Transition"）——结合自适应 Marčenko-Pastur 边缘重校准+participation-ratio 去局域化滤波器，在 BBP 相变附近（弱因子可能与 MP 谱边缘波动混淆时）通过同时检查谱分离和特征向量延展性恢复真实因子数。S&P 500 收益 IGF 检测中位数 7 个全局因子（比 Onatski 检验更丰富）。**部分采纳**：与 15 号 v1.19.0 RMT 去噪因子权重正交互补——15 号 v1.19.0 是**权重层**（对已确定因子去噪加权），IGF 是**检测层**（确定有多少真实因子），"检测→加权"流水线各自独立增强。A 股因子截面在 BBP 相变附近可能有弱因子被噪声谱边缘淹没，IGF 的 participation-ratio 去局域化滤波器可恢复。实施成本~80 行，定位 15 号 Phase 2+ 因子数检测增强（因子池扩展到 20+ 时启用），非 MVP baseline；② #1 策略类型目录补 **短期趋势跟踪失效微结构账户**（[arXiv:2607.01550, 2026-07-02, Kurth/Eisler/Rej/Bouchaud](https://arxiv.org/abs/2607.01550) "Is Trend Still Your Friend?"）——~100 种流动性期货合约（1995-2025）文档化 2009 年后短期趋势跟踪 PnL 崩塌，区分退化与存活趋势的横截面变量是波动率归一化 tick size（小 tick 合约趋势 PnL 崩塌而大 tick 保持）。机制：HFT 主导做市商在小 tick 稀疏订单簿上的流动性撤回打破"趋势信号→方向性交易→市场冲击→强化价格变动"自我实现反馈循环。**部分采纳**：A 股打板标的（股价 5-30 元 tick 0.01 元 tick size 占比 0.01%-0.2%）属"小 tick 合约"类别，论文"小 tick→趋势失效"机制对打板的启示是量化对手盘在小 tick 稀疏订单簿上的流动性撤回加剧炸板风险（与 24 号 §2.4 PEAD Inversion 协同）。tick size 归一化是诊断指标非新增算法实施成本=0，定位 20/24 号策略容量评估参考诊断指标，Phase 2 动量趋势 sleeve 扩展时作标的筛选维度。**不采纳项**：③ SS-GEN 尾部生成估计（arXiv:2607.10700）与 91 号 GPD/TailGAN 重叠记远期参考；④ Spectral Variance Ratio 多记忆因子模型（arXiv:2607.03858）长期股权收益动态分解属低频 memory 维度与项目日频交易正交记远期参考；⑤ State-Dependent L2 Liquidity（arXiv:2607.09230）crypto futures 数据 A 股适用性需评估记 37 号 Phase 3+ 远期 | 三十五轮审查：全网搜索 2026-08-08~10 最新研究（后台 agent 返回 22 篇 2026-07/08 论文），对照 v1.0.0-v1.13.0 已集成清单去重后筛除 15 篇已评估（Landolfi Drawdown/Çetin 流动性尾部/RWC Schmitt/MFCCA Kakinaka/Path Portfolio Noguer/Proper-Score Livieri/Markov GoF Stachurski/CVaR RaQL Wu/Stationary Ambiguity Mueller/Cross-Sectional LSTM Döbelt/Joint VaR/ES Ye/Preference Robust Distortion Bernard/Public Trader Identity/LRISK 等），新增 2 项未覆盖高价值研究部分采纳（IGF 因子数检测层+tick size 策略存活判据）+3 项简略提及不详细登记（SS-GEN/Spectral VR/State-Dependent L2）。延续过度工程纠偏纪律——2 项采纳均定位 Phase 2+/Phase 2 远期候选非 MVP baseline，IGF ~80 行是 RMT 检测层标准工具，tick size 归一化是诊断指标成本=0。施工算法完整性结论：本轮为选项外更优算法登记，无新增施工算法缺失 |
| 2026-08-10 | 1.15.0 | 四十轮审查补 1 项选项外更优算法（2026-08-08~10 最新研究全网搜索，后台 agent 返回 12 篇 2026-08 候选论文，对照 v1.0.0-v1.14.0 已集成清单去重后筛除 11 篇已评估，新增 1 项未覆盖理论工具登记）：① #4 风险模型补 **分布漂移标度律+核校准规则**（[arXiv:2608.01268, Kaleche, 2026-08-02, stat.ML](https://arxiv.org/abs/2608.01268) "Scale Law for Detecting Distribution Shift + Kernel Calibration Rule"）——从 Chebyshev 极值问题导出检测分布漂移所需最小样本量标度律 N\* ≥ log(1/f)/(2ε)（以频率 f 发生、精度 ε 检测漂移的样本量下界）+ RBF 核 MMD 带宽应匹配特征尺度的校准规则（带宽匹配核检验在对抗设定下主导拓扑替代方法）。**部分采纳**：纯理论工具（闭式公式+参数选择规则）实施成本≈0，与 Sharp Tail Bounds（v1.11.0）同类定位为理论背书。与 §4 RWC（v1.12.0）形成上下游闭环——RWC 假设"平滑 regime 漂移"但未提供"漂移是否已发生"的形式化检验，标度律+核校准填补此空白（MMD 检验判断漂移是否发生→标度律判断样本量是否足够→RWC 启动 regime 加权校准）。与 10 号 HMM regime 检测 + 55/61 号变点检测对接（检测结果可信度判据：检测窗口≥N\*→可信，<N\*→低置信变点）。定位 10/55/61 号检测器理论背书工具非独立施工，非 MVP 必需 | 四十轮审查：全网搜索 2026-08-08~10 最新研究（后台 agent 返回 12 篇 2026-08 q-fin/stat.ML 候选），对照 v1.0.0-v1.14.0 已集成清单去重后筛除 11 篇已评估（MFCCA 2608.04987/Non-Gaussian Drawdown 2608.00127/Wasserstein DRO 2608.07032/MINGLE 2608.06618/行业 embedding LSTM 2608.05755/RLCP 2608.06206/Markov GoF 2608.03088/Proper-Score 2608.02828/Conformal Kelly 2608.01494 等均已在 v1.0.0-v1.14.0 各轮分别评估整合），新增 1 项未覆盖理论工具部分采纳。延续过度工程纠偏纪律——标度律是闭式公式实施成本≈0 属检测理论增强非 MVP baseline。施工算法完整性结论：本轮为理论工具登记，无新增施工算法缺失。**关键发现**：2026-08-08~10 高价值算法均已被前几轮整合（9/10 已注册），印证第三十三轮"继续文档审查边际价值已极低，价值增长点转向代码施工"结论 |
| 2026-08-10 | 1.16.0 | 五十七轮审查补 2 项 KDD 2026 选项外更优算法（三路并行 agent 审查：全网最新算法搜索+00_index 结构审计+代码施工路径规划。后台 agent 返回 arXiv q-fin 08-01~10 全扫+KDD 2026 接受论文+中文券商金工+GitHub，对照 v1.0.0-v1.15.0 已集成清单去重后筛除 18+ 篇已评估，新增 2 项未覆盖 KDD 2026 研究评估）：① #1 策略类型目录补 **ReCAP Regime-Adaptive Continual Learning for Portfolio Management**（[arXiv:2606.00143, KDD 2026, Pan et al. 西南财经大学](https://arxiv.org/abs/2606.00143)）——将持续学习（Continual Learning）集成到组合管理，用自适应 regime 检测模块将历史数据分割为变长 regime，学习 regime 特定的策略向量构建策略库；交易时用 regime-gate 模块自适应组合策略向量。**不采纳（MVP）/记远期**：项目 G15 已裁定"简单乘法不做 MVO"+ PPO A股 DRL 负结果（年化 10.24% 未超 equal-weight 12.62%）+ End-to-End Parametric Portfolio 仅中等成本下匹配 equal-weight——三重负结果共同验证"简单 robust baseline 优于 DRL 组合优化"。ReCAP 的"策略库+regime-gate 组合"本质上接近 MVO/学习思路，与 G15 裁定有张力。但 ReCAP 的"持续学习避免灾难性遗忘"概念有借鉴价值——34 号 RegimeMetaAllocator 当前用 PerformanceScore 滚动窗口，可借鉴 EWC（Elastic Weight Consolidation）正则化防止旧 regime 经验被新 regime 覆盖。记为 34 号 Phase 5+ 远期候选（仅当策略数显著扩大+简单乘法证明不足时评估，须以 equal-weight 为基准），非 MVP baseline；② #2 因子分类补 **TIPS Transformer with Inductive Prior Synthesis**（[arXiv:2603.16985, KDD 2026](https://arxiv.org/abs/2603.16985)）——通过知识蒸馏将因果性、局部性、周期性等归纳偏置注入 Transformer，用注意力掩码作为教师模型，蒸馏合成为统一的学生模型。在多市场 regime 下验证超额收益。**部分采纳**：与 25 号 Phase 4 ML 合成栈三件套正交互补——LambdaRankIC（v1.6.0）管训练目标、RankGLU（v1.7.0）管预测头架构、**TIPS（本项）管归纳偏置注入**，三者各自独立增强。"归纳偏置蒸馏"对 A 股量价因子有效（A 股周期性=涨跌停 T+1、局部性=板块联动、因果性=事件驱动），但实施成本高（知识蒸馏 pipeline+教师模型训练）。记为 25 号 Phase 4+ ML 合成远期候选（当 ML 合成栈引入后评估，与 Uncertainty-Adjusted Sorting v1.12.0 同 Phase 4 启用条件），非 MVP baseline。**已去重排除 18+ 篇**：Fragile Frontier Sobol（v1.9.0 已登记✅）、Velocity Manipulation（10/13/15 号已登记为 regime conditioning 负面结果✅）、Preference Robust Distortion（v1.9.0 ④ 评估不采纳✅）、Ergodic Markov GOF（v1.10.0 已登记+12 号 v0.8.1 并发登记✅）、MINGLE/Stationary Ambiguity/CVaR RaQL/MFCCA/Path Signature/Hawkes OTC/微结构均值回归/Liquidation Cascade/Non-Gaussian Drawdown/Certified Wasserstein/Shapley 归因/Conformal Kelly 等 18 篇全部已在之前轮次整合 | 五十七轮审查：三路并行 agent 审查（全网最新算法搜索+00_index 结构审计+代码施工路径规划）。全网搜索 2026-08-08~10 最新研究+KDD 2026 接受论文，对照 v1.0.0-v1.15.0 已集成清单去重后筛除 18+ 篇已评估，新增 2 项未覆盖 KDD 2026 研究评估——1 项不采纳 MVP 记远期（ReCAP 与 G15 裁定有张力+DRL 负结果，仅借鉴 EWC 持续学习概念）+1 项部分采纳记远期（TIPS 归纳偏置蒸馏与 ML 合成栈三件套正交互补，Phase 4+ 启用）。延续过度工程纠偏纪律——2 项均定位 Phase 4+/Phase 5+ 远期候选非 MVP baseline。施工算法完整性结论：本轮为 KDD 2026 选项外更优算法登记，无新增施工算法缺失，延续第三十一~五十六轮共 27 轮持续确认闭环——高价值算法均已被前几轮整合，价值增长点转向代码施工 |
| 2026-08-10 | 1.17.0 | 整合 2026-08-04~10 全网搜索 8 项最新研究发现（审查历史摘要区新增 v1.6.0 审查记录）：① #3 组合构建层补 **C-WRP（Certified Wasserstein Robust Portfolio）**（[arXiv:2608.07032](https://arxiv.org/abs/2608.07032)，v1.0.0 已登记 Wasserstein 家族组合层，本次补充 LP 化+certified error bound 工程可行性视角，MVP 用三因子乘法替代优化器，C-WRP 是远期升级路径，Phase 4+ 远期候选）+**RRP（Robust Risk Parity with GARCH+Market State）**（Finance Research Letters vol.92(C) 2026，中国市场 2012-2024 实证全面优于 TRP/EW/GMV，risk parity 递进"A 股实证优化"中间档，Phase 2+ 远期候选）；② #7 regime 层补 **VRMD（Velocity-Regime Manipulation Detection）**（[arXiv:2608.05373](https://arxiv.org/abs/2608.05373)，regime 条件化用 recall 换 precision 上限约 25%——**已评估不整合**，反面结果支持项目 4 态 HMM 不过度细分决策）；③ #10/91 密度预测补 **FCVE（Finite-Sample Conformal Joint VaR-ES）**（Mathematics 14(15):2847 2026-08-06，conformal risk control 耦合 VaR breach frequency+magnitude，non-exchangeable swap-distance bound+regime-drift bound+heavy-tail rate，Phase 2 远期候选，RWC/TWC 的 joint VaR-ES 扩展）；④ #19 执行算法补 **A-CRaQL（Adaptive CVaR Risk-Aware Q-Learning）**（[arXiv:2608.04305](https://arxiv.org/abs/2608.04305) ICAIF'26，不改 CVaR 估计器重新设计训练流程，CVaR Bellman residual 降 ~85%——**已评估不整合**，与 v0.8.0"Conformal-gated 执行 vs RL 执行"结论一致"慢而稳 conformal 胜过 RL"在执行域同样成立，RL 执行在个人系统必要性存疑，conformal 闸控已足够）；⑤ #2 因子工程补**量化"双杀"压力测试**（2026-07 沪深300指增平均超额-1.51%/中证500-4.54%/动量因子单月回撤超 20 个百分点十年罕见，印证因子拥挤度监控必要性，需在 25 号因子监控模块增加拥挤度指标）；⑥ 新增**"A股市场结构变化（2026-07/08）"**小节——A 股交易新规（盘后固定价格交易扩容全部 A 股+沪深 ETF/主板 ST/*ST 涨跌幅 5%→10%/上交所基金收盘连续竞价改集合竞价/深交所创业板引入做市商）+微盘股策略失效机制（科技股虹吸→流动性枯竭→量化同质化多杀多→退市新规基本面恶化，微盘 Q1 归母净利同比-79.25%，需在 25 号 build_tradability_mask 强化流动性门槛）+量化"双杀"压力测试，需在 24/25/26 号策略文档同步更新施工约束 | 整合 2026-08-04~10 最新研究发现：4 项算法（C-WRP/RRP/VRMD/A-CRaQL）+1 项密度预测扩展（FCVE）+3 项市场结构变化（交易新规/微盘股失效/量化双杀）。VRMD/A-CRaQL 标注"已评估不整合"并给出理由，C-WRP/RRP/FCVE 定位 Phase 2+/Phase 4+ 远期候选非 MVP baseline。延续过度工程纠偏纪律——文档审查边际价值已极低，但 2026-08 市场结构变化（交易新规+微盘股失效+量化双杀）影响施工约束需登记 |
| 2026-08-10 | 1.18.0 | 七十三轮审查补 4 项 2026-08 选项外更优算法远期候选（后台 agent 返回 23 篇 2026-08 论文，逐篇核验 18 篇已登记+3 篇未登记低适用性+2 篇新增登记，剩余 4 篇高价值远期候选本次登记）：① #3 组合构建层补 **SciPhy RL**（[arXiv:2607.15195](https://arxiv.org/abs/2607.15195) Halperin&Itkin 2026-07，PINN 路径 HJB 离线求解，离散目标持仓适配 T+1，成本内生化，Phase 4+ 远期候选）+**HRT 双层 RL**（[arXiv:2410.14927](https://arxiv.org/abs/2410.14927) Zhao&Welsch MIT 2026-05，选股+执行双层 RL，turnover/回撤/文本风险惩罚，与 30 号 sleeve 框架结构同构，Phase 5+ 远期候选）+**Finance-Grounded 损失函数**（[arXiv:2509.04541](https://arxiv.org/abs/2509.04541) Khubiyev 等 2026-02，turnover 正则化+MDD 损失，训练目标与评估指标对齐，Phase 2+ 远期候选，实施门槛最低仅需改损失函数）+**Strat-LLM**（[arXiv:2605.06024](https://arxiv.org/abs/2605.06024) Huang&Yu 2026-05，T+1 滚动策略对齐 LLM，regime 依赖对齐策略牛市 Free/熊市 Strict，35B 模型严格约束下最优，Phase 5+ 远期候选） | 七十三轮审查：后台 agent 返回 23 篇 2026-08 论文，逐篇核验后 18 篇已在前几轮登记（MINGLE/EFS/Sector-LSTM/操纵检测/CVaR Q-Learning/微观结构均值回复/羊群效应/Wasserstein 鲁棒组合/多重分形组合/F2Agent/FinSMART/困境传染/非布朗回撤/A 股多日换手/平方根冲击精确解/被动市场冲击/信号自适应序贯执行/市价+限价 RL 执行），3 篇未登记低适用性（AMM DeFi/PD-at-Risk 信用风险/LOBIN A 股高频监管），2 篇新增登记（EvoMarket→53 号 v1.6.4 T+1 native 模拟器+被动市场冲击已登记 40 号），4 篇高价值远期候选本次登记 90 号。延续过度工程纠偏纪律——4 项均定位 Phase 2+/Phase 4+/Phase 5+ 远期候选非 MVP baseline |
| 2026-08-10 | 1.18.1 | 七十四轮审查补 2 项 2026-08 选项外更优算法（全网搜索 2026-08-07~10 最新研究，对照 v1.0.0-v1.18.0 已集成清单去重后新增 2 项未覆盖研究）：① #2 因子分类补 **稀疏衰减 Sparse Decay + RMT 去噪权重分配**（[arXiv:2507.17211](https://arxiv.org/abs/2507.17211) Chen/Luo/Zhang/Liu/Zhang 2026-08-07 港城大+上财）——"稀疏衰减"新现象：因子在稀疏组合（ℓ0 约束，仅选 m 资产）下衰减快于密集组合（稀疏约束放大单资产特异性噪声）。RMT 去噪因子相关矩阵（剔除 Marchenko-Pastur 谱噪声特征值）+正则化 QP 权重分配。CSI300/CSI500 实证。**部分采纳 Phase 2+**：稀疏衰减概念填补 25 号衰减监控认知盲区（Alpha-R1/AlphaPROBE/McLean-Pontiff/CUSUM 均假设组合稠密，打板 sleeve 持仓极稀疏 2-5 只是独有衰减维度）；RMT 去噪是 25 号因子合成直接增强（与残差代数 Phase 4 正交）；② #3 组合构建层补 **VD-MEAC 价值分布 Actor-Critic**（[Front. Artif. Intell. 2026-01](https://doi.org/10.3389/frai.2025.1709493) Yang 等 南方电网资本）——critic 学未来收益完整分布（非点估计）避免风险寻求行为+熵正则化平衡探索利用，A 股 Sharpe 2.978。**定位 Phase 5+ HRT 增量**：不单独登记，作 HRT 双层 RL 升级到"分布 critic+熵正则"版本的增量改进参考（价值分布适配 A 股重尾与 36 号 Student-t ν 同源） | 七十四轮审查：全网搜索 2026-08-07~10 最新研究，对照 v1.0.0-v1.18.0 已集成清单去重后新增 2 项——1 项部分采纳 Phase 2+（稀疏衰减+RMT 去噪填补打板 sleeve 稀疏持仓衰减盲区）+1 项定位 Phase 5+ HRT 增量（VD-MEAC 价值分布不单独登记）。延续过度工程纠偏纪律。同步：53 号 v1.6.5 补 square-root law 理论背书（2608.00988+2606.07059，将 square-root 选型从工程实证升级为 EMH 扩散约束理论必然） |
| 2026-08-12 | 2.0.0 | 架构审查终审全量裁定（draft→active）：21 项全部裁定——维持 4 项（#3/#4/#6/#11 锚点更新 v2.5.0）+新裁定 12 项（#1 四族双层原6大类deprecated/#2 双轨IC+BHY FDR+ICIR≥0.5/#5 砍AC+最低佣金5元+印花税更正万5/#8 压力退出时间禁开仓+LVaR简化/#9 半衰期HL2-3年+断裂期降权保留/#12 并入#16线性收紧deprecated/#13 sleeve级多基准废弃60/40/#14 PIT确认已施工/#15 两维精简P0-P3 deprecated/#16 生存线下调Sharpe≥0.8+健康卓越实盘校准/#17 拒绝OPA改choke point/#18 轻量IM拒绝重型/#19 默认限价单+打板专用路径删5%ADV条款/#20 逐项闭环三维指纹Phase 2/#21 受约束overlay四规则）+暂缓/远期 2 项（#7 T+1 8态暂缓+重启条件/#10 密度预测远期）+P-1~P-5 待用户裁定。新增「已施工设施盘点」节（通用规则 #11：8 已施工/8 部分/5 未施工，12 注册表 6/12 已建）。6 处口径修复（§3 MOD-POS-001→021/#5 印花税千1→万5/BM-BT-07 三方口径/BT-10 已 production/30号锚点 v1.3.3→v2.5.0/91号引用标注规划态）。A2 已 PASS 更正（W-HMM 降 Phase 3+）。讨论优先级表转施工优先级表（P1：做T成本/benchmark增补/执行限价单）。每项裁定含第一性原理+2026 调研+施工方案+过度工程审查（MVP 零新增，缺口全部 Phase 1/2 登记） | 全量架构审查：基础设施盘点（src/zephyr 全域+注册表+schema+测试+治理脚本）+ 第一性原理逐项裁定 + 2026-08 业界/量化社区/氛围编程社区调研 + system_charter §2 硬边界适配（1人+100%AI+单机+小资金）+ 交叉文档口径对账（30/10/11/91/52/00 号发现 9 处不一致并修复本文档侧） |
