---
ttl: task_bound
title: 分册02 过拟合防线总册——多重比较、DSR/PBO/CPCV 与本仓三件套的组合防线
topic: overfitting_defense
created: "2026-09-24"
owner: ZephyrAlpha-Owner
---

# 分册02：过拟合防线总册

> **大白话开场**：过拟合=把历史上的巧合当成了规律。防它的核心困难是：**你搜得越多，纯靠运气撞出来的"圣杯"越多**——这不是纪律松紧问题，是算术问题。防线必须"事前封卷子、事中记次数、事后打折扣"，三段缺一不可。

## 1. 多重比较问题（Multiple Comparisons）——本仓的算术现实

**一句话**：每次检验有 5% 的概率把噪声判成信号；检验 N 次，假阳性期望 ≈ 0.05×N——搜 1 万个格子，哪怕全部是噪声，也会"自然长出"约 500 个"显著"格子。

本仓的数量级（全部有文件证据）：

| 空间 | 规模 | 真源 |
|------|------|------|
| 组合层参数网格 N_raw | 默认 context 362,880；全激活 11,612,160 | `config/position_recipe_grid_schema.yaml` 头注 |
| GPU 三路搜索预算 | T1 17,100 + T2 13,000 + T0 标定 200 = 30,300 格（含五档成本门） | `config/search_space_prereg.yaml` budget_caps |
| 条件胞×策略格 | 条件胞（4 灰度×F4 三态=12 胞、30 日地板达标 9）×策略×成本档 | prereg condition_stratification + `src/zephyr/backtest/regime_validation/condition_package.py` |
| 单格检验次数 | ×5 成本档（每格过五档门） | `config/exam_scale_cost_gate.yaml` tiers_bp |

按 0.05 口径，30,300 次试验的纯运气假阳性期望 ≈ **1,500 个**。**所以"哪个格子分最高"这个问题本身没有意义，有意义的是"这个高分在知道我试了 30,300 次之后还剩多少"**——这就是校正的含义。

## 2. 机构标准工具三件（论断均注出处）

### 2.1 Deflated Sharpe Ratio（DSR，缩水夏普）
- **出处**：Bailey, D. H. & López de Prado, M. (2014), *The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality*, Journal of Portfolio Management 40(5)（全文：[davidhbailey.com](https://www.davidhbailey.com)）；SSRN 收录（[papers.ssrn.com](https://papers.ssrn.com)）。
- **大白话**：先算"如果你瞎试了 N 次，最好的那个 Sharpe 大概率能到多少"（期望最大值，随 N 涨），再看你的策略 Sharpe 是否**显著超过这个注水基线**，同时把偏度/峰度（收益分布的歪与肥尾）折进去。
- **本仓资产**：`src/zephyr/simulation/deflated_sharpe_calculator.py`（模块头自称"全仓 DSR 唯一真源"，MOD-SIM-024，样本<3 拒绝、退化态 fail-closed）；试验次数喂入纪律=exam_policy §2.2"喂全部留痕试验次数，禁只喂幸存配置"；次数账本=`src/zephyr/backtest/core/n_trial_ledger.py`（prereg e7_defense：`dsr_denominator: n_trial_ledger cumulative_trials`、`dsr_floating: true`——门槛随累计试验数浮动）。

### 2.2 PBO（Probability of Backtest Overfitting，回测过拟合概率）
- **出处**：Bailey, D. H., Borwein, J. M., López de Prado, M. & Zhu, Q. J. (2017), *The Probability of Backtest Overfitting*, Journal of Computational Finance 20(4), 39-69（Risk Journals，[risk.net](https://www.risk.net)）；预印本 SSRN 2015（[papers.ssrn.com](https://papers.ssrn.com)）。
- **大白话**：把数据切成若干子集两两组合（CSCV），每次都问"样本内选中的最优配置，到样本外是不是掉到中位数以下"。掉的概率就是 PBO。**PBO 的零假设是 0.5 不是 0**——PBO≈0.5=硬币翻转=完全过拟合；≈0 可信（这条误读澄清有受控实证：零 edge 场景 PBO 实测 0.476，植入 edge 后 0.001——[marketmaker.cc 2026-07](https://marketmaker.cc/en/blog/post/probability-backtest-overfitting-pbo/)，本仓 62 号 §7.2 转引落地）。
- **本仓资产**：G2 过拟合检查门已立法 `FAIL if bt.pbo_value > 0.2`（0.2-0.5 区间仍阻断），见 `docs/_archive/62_business_registry_construction.md` §4.13 G2（第 869 行）。

### 2.3 CPCV（Combinatorial Purged Cross-Validation，组合净化交叉验证）
- **出处**：López de Prado, M. (2018), *Advances in Financial Machine Learning*, Wiley, ch.11-12（CPCV 与 purge/embargo；[wiley.com](https://www.wiley.com)）；学术确证：Arian et al. (2024), *Backtest overfitting in the machine learning era*, ScienceDirect（[sciencedirect.com](https://www.sciencedirect.com)）。
- **大白话**：普通"训练段/验证段"只考一次，结论依赖切法运气；CPCV 把数据分成 N 份、穷举各种组合当测试集，得到**多条回测路径**，看路径分布的稳定性；"净化"=训练/测试边界处删掉标签重叠区（purge）再加缓冲带（embargo），防时间序列标签泄漏。
- **本仓资产**：G2 门已立法 `cpcv_oos_sharpe_std/mean > 0.5 FAIL`（切法敏感=过拟合）+ catastrophic-veto + mean≤0 FAIL（62 号 §4.13 G2，第 873-876 行）。

### 2.4 相连大坑：试验相关时裸 DSR 会误杀
- Soloviov (2026-07), *How Many Backtest Winners Survive Deflation?*（[github.com/suenot/deflated-sharpe-search](https://github.com/suenot/deflated-sharpe-search)）：参数网格里相邻试验高度相关，裸 DSR 用原始 trial 数会把真实 edge 错杀（受控实验：真实 Sharpe 3.92 被判 0.748）。修复=相关时禁裸 DSR，改用 bootstrap 类检验（White RC / Hansen SPA），并报"有效试验数区间带"而非单值。
- **本仓已落地同款**：62 号 G2 新增 `trial_correlated` + `bootstrap_test_passed` 检查（第 877 行 + 第 1369 行落地记录）。**这是本仓方法论先于直觉的一处：DSR 不是越严越好，要配合试验结构。**

## 3. 本仓三件套 × 新工具 = 完整防线（组合表）

三件套现状：
1. **预注册**：`config/search_space_prereg.yaml`——冻结语义="GPU 正式开跑前唯一搜索空间真源；改空间=作废重开预注册（禁跑中改）"；frozen_at/owner_signoff 待 Owner 批文回填；族外尝试禁事后入族（e7_defense.family_registry_required）。
2. **闭卷考（HOLDOUT）**：闭卷窗 [2019-01-04, 2025-09-09]，窗外数据禁入（禁校正/调参/定档，condition_package 闭卷纪律）；T2=主效应**前 20% 层**参数展开+复验（prereg tier2_points 注）；负结果如实入 negatives.csv 禁删改（prereg honesty + exam_policy §5 负结果台账）。
3. **成本门**：五档滑点 [0,5,10,20,40]bp 全档存活地板 0.0 + 单调非增 + 换手 8x 上限，任何粗扫阶段禁跳成本门（prereg cost_gate_in_every_tier，Owner 采纳令）。

组合防线阶梯（事前→事中→事后→前向）：

| 层 | 工具 | 状态 | 组合语义 |
|----|------|------|---------|
| 事前 | 预注册封空间+封判据 | ✅ 在役（prereg 冻结机制） | 不封卷子，后面全是自欺 |
| 事前 | 封闭族声明（N_eff） | ✅ exam_policy §1.2 | 族里必须含失败者，防幸存者记账 |
| 事中 | 成本门×五档+换手门 | ✅ 在役（exam_cost_gate） | 把"成本后还活着"焊进每一格，不是最后补考 |
| 事中 | 闭卷窗/前 20% HOLDOUT | ✅ 在役（condition_package+prereg T2） | 定档与展开数据隔离 |
| 事中 | n_trial_ledger 全量记账 | ✅ 在役（接线见 prereg e7_defense.ledger_required） | DSR 的原料，后补=造假（exam_policy §1.4） |
| 事后 | DSR 浮动门槛 | ✅ 在役（deflated_sharpe_calculator+dsr_floating） | 对"试了 N 次的最大值"打折 |
| 事后 | PBO>0.2 门 | ◐ G2 立法在册，引擎字段接线待验 | 对"IS 冠军 OOS 掉队"概率定门槛 |
| 事后 | CPCV 路径稳定性门 | ◐ G2 立法在册，引擎字段接线待验 | 对"切法运气"定价 |
| 事后 | trial 相关性→bootstrap 带修复 | ◐ 同上（62 号已落地检查字段） | 防校正器本身被试验结构骗 |
| 事后 | 负结果台账 negatives.csv | ✅ 在役（exam_policy §5+prereg honesty） | 防"只报喜"的文件柜偏差 |
| 前向 | 模拟盘绿 N 日 | ✅ 在役（prereg honesty：进模拟盘仍走既定三步，本预注册不开捷径） | OOS 的终极形态是未来 |

**组合逻辑一句话**：预注册保证"考题事先封卷"，成本门保证"活着的一定是扣完成本的"，闭卷/HOLDOUT 保证"分数不是抄来的"，n_trial_ledger+DSR 保证"第一名的分数按总考试人数打折"，PBO/CPCV 保证"第一名换一张卷子还是第一名"，负结果台账保证"没考上的也留档"，模拟盘保证"最终考官是明天"。

## 4. 落地顺序建议（不施工，供裁定）

1. 先接线 PBO/CPCV 引擎字段消费（G2 已立法，62 号 §4.13；缺的是 f06/批量执行器回填 `pbo_value`/`cpcv_*` 字段）——边际收益最大，因为预注册+DSR 已在役。
2. DSR 分母已挂 n_trial_ledger 累计口径（裁定#306 N_eff 预注册族口径）；PBO/CPCV 接线后沿用同一账本，禁另立第二试验计数器（禁第二套门控，回测 SOP README §6）。
3. CPCV 的 purge/embargo 参数须入预注册（改参数=作废重开），不得跑中调。

——出处汇总：DSR=JPM 2014（davidhbailey.com / papers.ssrn.com）；PBO=JCF 2017 20(4) 39-69（risk.net）；CPCV=AFML Wiley 2018（wiley.com）；PBO 零假设澄清=marketmaker.cc 2026-07（62 号转引）；trial 相关修复=github.com/suenot/deflated-sharpe-search 2026-07（62 号转引落地）。
