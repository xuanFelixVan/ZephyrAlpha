---
ttl: task_bound
title: 18 量化判据专业标准对表（全网文献对表报告）
doc_type: reference
---

# 18 · 量化判据专业标准对表（Owner 令：以专业为准，不自造；全网搜最新文献）

> 结论先行：17 号文判据 **约七成与专业机构做法同构**（标注出处后保留）；**两条自造判据已替换为行业标准件**；另补三件行业标准升级。文献检索时点 2026-09-26。

## 一、逐条对表

| 17 号文判据 | 对表结论 | 专业出处 |
|---|---|---|
| GPU 完成率/死亡率/n≥30/Wilson LB/五档单调非增 | ✅ 标准同构：假设检验区间估计（Wilson 区间是标准方法）；TCA 成本单调性是行业 sanity check；数据完整度=DAMA/ISO 8000 质量维（completeness 对权威源对照——881xxx 727 真值对账即此法） | Wilson (1927)；TCA 行业惯例；DAMA-DMBOK/ISO 8000 |
| ~~sharpe>2 占比>5% 可疑~~ | 🔄 **已替换**为三件套正式判据：haircut Sharpe（多校校正，非线性——高 Sharpe 少罚、边缘重罚，Man Group 明确反对"一刀切 50% 折扣"）+DSR+PBO | Harvey & Liu (2015 JPM, ~248 引)；Bailey & LdP (2014)；Bailey et al (2015/2017 PBO/CSCV, ~419 引) |
| N_eff≥12 | ✅ 仓内裁定#306 预注册族口径，与多校校正的 trials 计数精神一致 | 同上 DSR 框架 |
| 方案①两轮制 Spearman+top50 | ✅ 标准同构：多保真优化（successive halving/Hyperband 族）的代理保真度验证法（秩相关+top-k 重合）；阈值 0.99/0.9 为 T0 实测标定值 | Li et al (2017) Hyperband；ASHA |
| 做T 状态匹配四元组（n≥30+Wilson LB） | ✅ 保留；**升级件**：sharpe 类格补报 PSR（概率化夏普）与 MinTRL（最短_track_record_长度，Bailey-LdP） | Bailey & LdP (2012/2014) |
| ~~样本外衰减≤30%~~ | 🔄 **已替换**为 WFE≥50%（Pardo 行业公认线：OOS/IS×100）；我方 LB 衰减≤30% 降级为内控更严线双轨并行 | Pardo《The Evaluation and Optimization of Trading Strategies》；arXiv 2025-12 严格 WFA 框架 |
| 闭卷考+负结果台账 | ✅ 专业同构：HOLDOUT/预注册纪律正是 2024-2025 文献的共识解（见下条） | AFML (2018)；Arian et al (2024) |
| DSR/PBO/CPCV（02 册） | ✅ 正是文献公认的互补三件套；**最新证据**：Nefedov (2025 SSRN)——天真评估虚增年化夏普 ~3.6 倍、严格协议下六因子全灭；Arian (2024) 定位 CPCV 为 ML 时代稳健解；开源工具已普及（purged CV 兼容 scikit-learn） | 见左；最新两篇=本轮全网检索所得 |
| 做T 多周期全算+状态匹配 | ✅ 方法论同构：日内动量文献（market intraday momentum）+条件绩效分析（meta-labeling）；多假设校正用 Harvey-Liu | Gao-Han-Li-Zhou (2018)；LdP meta-labeling；Harvey (2019 RFS) |
| 交易链 30 交易日零丢弃/竞态压测 100 次 | ✅ 标准同构：回归测试+混沌工程（chaos engineering）惯例 | Netflix Chaos Monkey 族/Google SRE |
| 熔断 kill-9 重启一致 | ✅ crash-only software 恢复验证标准做法 | crash-only software (Candea & Fox) |
| 数据 ±5% SLO/连续 N 日 | ✅ SLO 惯例 | Google SRE |
| 蒸发治本 7 天 burn-in | ✅ SRE postmortem action item + burn-in 惯例 | Google SRE |
| 22 件五态（禁第六态） | ✅ 数字取证 chain-of-custody 证据链惯例 | DFIR 惯例 |
| 假设引擎每周 ≥5 条 | ⚠️ 内部运营 KPI（无行业标线）——保留但定性为内部节奏指标，非科学判据 | — |

## 二、替换明细（已写回 17 号文）

1. 一·垃圾触发线后新增"**多重检验正式判据**"行：haircut Sharpe+DSR+PBO 三件套逐格报告（粗筛 tripwire 保留为运行报警层）。
2. 三·做T 样本外判据改为 **WFE≥50%（Pardo 线）**，原 30% 衰减线降为内控更严线双轨。
3. 做T sharpe 类格升级 PSR/MinTRL 报告面（建议件）。

## 三、给 Owner 的大白话总结

你要的"不自造、用现成的"基本已经成立：**七成判据本来就是行业标准的方法**（置信区间、成本单调性、数据完整度对账、SRE 燃尽、混沌工程），这次对表把**剩下两条我方自造的也换成了带论文出处的标准件**——"夏普好得可疑"从拍脑袋占比换成了 Harvey-Liu 的非线性校正三件套，"样本外衰减 30%"换成了 Pardo 的 WFE≥50% 行业线（我们原线更严，保留为内控双轨）。另外全网最新文献给了两个定心丸：2024-2025 的研究（Arian、Nefedov）证明**没有这套防线的机构夏普平均虚增 3.6 倍**——我们提前把防线建了；CPCV 在 ML 时代被定位为稳健解——已经在我们退役重考的预注册里。

## 四、来源

- [Harvey & Liu (2015 JPM) Backtesting](https://papers.ssrn.com)（haircut Sharpe；[Duke 版](https://people.duke.edu)；[Man Group 解读：非线性校正](https://www.man.com)）
- [Bailey et al PBO/CSCV (SSRN, ~419 引)](https://papers.ssrn.com)；Bailey & LdP (2014) DSR；LdP《AFML》2018 CPCV
- [Arian et al (2024) Backtest overfitting in the ML era (ScienceDirect)](https://www.sciencedirect.com)；[Nefedov (2025 SSRN) How Much Sharpe is Illusory](https://papers.ssrn.com)
- [Pardo Walk-Forward Analysis (Wikipedia)](https://en.wikipedia.org)；[arXiv 2025-12 严格 WFA 框架](https://arxiv.org)
- [WFA 实务](https://algorier.com)；[IBKR walk-forward 综述 (2025-03)](https://www.interactivebrokers.com)
