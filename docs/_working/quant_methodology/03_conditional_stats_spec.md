---
ttl: task_bound
title: 分册03 条件概率表统计规范——Wilson 下界/分层贝叶斯收缩/MIN_OBS 现行值/明示不作数
topic: conditional_probability_stats
created: "2026-09-24"
owner: ZephyrAlpha-Owner
---

# 分册03：条件概率表统计规范

> **大白话开场**：条件概率表（"某形态在某状态下历史的胜率表"）最大的敌人是**薄格子**——样本 5 次赢 4 次，裸胜率 80%，但你不敢真按 80% 下注。本册立法四件事：怎么把运气折扣算进去（Wilson）、怎么向邻居借样本（贝叶斯收缩）、最少要多少样本才开口（MIN_OBS）、不够样本时怎么诚实标注（明示不作数）。

## 1. Wilson 置信下界（本仓已在役的实现）

- **是什么**：二项比例的置信区间（Wilson score interval）的**下端点**。对小样本比正态近似保守得多：n=10、k=7（裸 70%）的 95% 下界 ≈39%。
- **本仓实现**：`src/zephyr/signal_ashare/strategy_signal/pattern_win_rate_provider.py` `_wilson_lower_bound(rate, n, z=1.96)`——n≤0 返回 0.0（**无样本=零信任**）；越界/NaN rate 直接 ValueError（fail-closed，rpt_v01+反驳者反例修的坑）。消费口径裁定留痕：**加权输入用 LB，raw 口径经 get()/get_detail() 另取**（消费班方案 v1.0 挖矿 M1 裁定；TradingView winrate 脚本同法）。
- **判据常量层同款**：`config/tool_exam_policy.yaml` wilson_z=1.96、wilson_confidence_level=0.95、**organ_score 报告必须带 Wilson 区间全宽**（不只报下界——区间宽度本身就是样本量的诚实披露）。
- **落表规范**：条件概率表每行输出四元组 `(raw_rate, n, wilson_lb, wilson_interval_width)`；任何下游加权/排序只许消费 `wilson_lb`；`interval_width > 0.3` 的行自动进"薄格"名单（触发 §4 纪律）。

## 2. 分层贝叶斯收缩（薄格子向邻居借样本）

- **是什么**：经验贝叶斯/分层贝叶斯（empirical Bayes, hierarchical Bayes）——**给每个格子挂一个先验（邻居/同族格子的平均胜率），样本越少越向先验收缩**。公式（beta-binomial 共轭，最简形态）：`收缩胜率 = (k + α·p₀) / (n + α)`，p₀=先验均值（邻居均值），α=先验强度（等效"借来多少个虚拟样本"）；n→∞ 时收缩项消失，n→0 时完全等于 p₀。
- **出处**：Robinson, D. (2016), *Understanding beta binomial regression (using baseball statistics)*, varianceexplained.org（[varianceexplained.org](http://varianceexplained.org)——经验贝叶斯收缩的教科书级实例：棒球员安打率小样本向全局均值收缩）；教科书：*Bayes Rules!* ch.3 beta-binomial 模型（[bayesrulesbook.com](https://www.bayesrulesbook.com)）；多层版：Gelman et al. *Bayesian Data Analysis*（分层先验）。
- **本仓天然挂点（不用新建表）**：`c1_market.market_pattern_win_rate` 已有 **`__baseline__` 基准行**（`PatternWinRateProvider.get_baseline()`，全体事件同口径）——**这就是现成的 p₀**。收缩先验第一候选=基准行胜率；第二候选=同条件族（同 regime_tag/同 fwd_window）格子的均值。
- **纪律**：
  1. 收缩只改**表内展示值与加权输入的备选口径**，判开工闸仍用 Wilson 下界（闸门取保守者=min(Wilson LB, 收缩值)；二者都不过=不开）。
  2. α（先验强度）必须**预注册**（进 prereg 卡，改 α=作废重开），不许事后挑让格子好看的值。
  3. 收缩必须有出处字段：每行标注 `prior=p0 来源`（baseline / family-mean），禁无出处收缩。
  4. A 股适配：同族邻居必须同制度约束（T+1/涨跌停域），跨市场/跨制度借样本=驳回（挖矿 SOP 闸3）。

## 3. MIN_OBS 最小样本门槛——现行值实测（2026-09-24 全仓枚举）

条件概率域**主门槛=30 交易日地板**（现行生效）：

| 门槛 | 现行值 | 位置 | 语义 |
|------|--------|------|------|
| **条件胞地板（主门槛）** | **30 交易日** | `src/zephyr/backtest/regime_validation/condition_package.py` `_CELL_FLOOR_DAYS=30`（第 49 行） | 不达地板日期一律下沉 conditional-free；"禁凑 n，禁当独立样本"；达标胞实测 9/12（prereg 注） |
| 考试证据最低天数 | 60 天 | `config/exam_scale_cost_gate.yaml` cost_gate.min_days | 低于判不通过，fail-closed |
| T1 分层论域上限 | 18 格（Owner 上限） | condition_package.py §cell 论域（Owner 裁决①统计可用层） | 格子数本身也封顶，防"格多坑多" |
| 图形胜率物化 low_sample | 表内 low_sample 标记 | c1_market.market_pattern_win_rate（provider 只读：low_sample=true 或 hit_rate=NULL → 返回 None） | 消费方退化为无统计 |
| 情绪指数分位有效性 | 120 观测 | `src/zephyr/alt_data/emotion_index_builder.py` `_MIN_OBS=120` | 不足→insufficient |
| regime 周期分析 | 60 交易日 | `src/zephyr/regime/regime_cycle_analyzer.py` MIN_OBSERVATIONS=60 | 不足抛 ZA-REGIME-0030 |
| downside 样本 | 15 | `src/zephyr/pf_alloc/core/regime_meta_allocator.py` DOWNSIDE_MIN_OBSERVATIONS=15 | <15 强制中性 |
| 相关性 bootstrap | 8 | `src/zephyr/factor/analysis/correlation_block_bootstrap.py` MIN_OBS=8 | 不足抛 ValueError |
| DSR 矩估计 | 4 | `src/zephyr/simulation/deflated_sharpe_calculator.py` _MIN_OBS_FOR_MOMENTS=4 | <4 偏度/峰度取 0 占位并披露 |

**立法口径**：条件概率表引用 MIN_OBS 时一律指 **30 交易日地板（condition_package）**；其余门槛是各自域的家族值，跨域引用必须带路径与语义（"30 日地板"≠"60 天证据"≠"120 分位"——同名不同义是已知事故源，文档矛盾=事故，宪法 §4.4）。

## 4. 小样本格子"明示不作数"纪律（第三态立法）

**核心**：薄格子不是"通过"也不是"失败"，是**"不可考"**——必须落第三态，禁二值硬判。本仓已有同款先例（做T 方法矿总册三张分账：*"不可考 ≠ 通过 ≠ 失败，必须写第三态'不可考'"*，`.worktrees/st-t0-matrix-20260924/docs/_working/t0_matrix/METHOD_MINING_t0.md` 本册读法 §2）。

操作规范（对齐既有资产）：
1. **下沉而非删除**：不达地板的日期/格子下沉 conditional-free（condition_package 现行语义），格子行保留但标 `cell_eligible=False`——保留是为了"明示"，删除会制造幸存者表。
2. **返回 None 而非猜测**：win_rate provider 对 low_sample/查无返回 None（MOD-SIG-091 契约"无统计=None，消费方退化行为不变"）——**宁可不考，不可编考**。
3. **未决不硬判**：可判样本 <min_judgeable_n(5) → 记"未决"（tool_exam_policy significance.min_judgeable_n 同语义）。
4. **禁凑 n 三禁**（condition_package INARIANTS 原文）：禁凑 n、禁当独立样本、禁跨制度借样本。
5. **检查员条款**：任何引用条件胜率的下游（映射器加权/预算带/回测分层），若读到 `cell_eligible=False` 行，必须走退化路径并留痕——静默消费=违规。

## 5. 一段话版

**表上每行四元组 (raw, n, Wilson LB, 区间宽)；闸门只认 Wilson LB；薄格子向 `__baseline__`/同族收缩（α 预注册、出处留痕）；开口线=30 交易日地板+60 天证据天数；不达线=明示"不可考"下沉，禁凑禁删禁硬判。**
