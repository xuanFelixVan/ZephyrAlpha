---
ttl: permanent
doc_type: architecture_view
title: 策略间相关性验证
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.7.2"
date: 2026-08-15
topic: strategy_correlation_validation
scope: 07_trading_decision_architecture
---

> ## 结案报告（AI-NIGHT-001 复核 2026-08-19）
>
> **实际开发**：门禁/工具侧 production 实证——strategy_correlation_gate.py（MOD-PA-004，运营级 0.85/0.90 REJECT/HARD_REJECT 门禁）+ correlation_analyzer.py（MOD-L02-005，Spearman 因子级 + Pearson 滚动窗口）+ deflated_sharpe_calculator.py（C4 计算器）+ backtest/core/walk_forward.py。
>
> **最终成果**：G07 验证方法定稿（active v1.7.2）——双相关系数 + 情绪周期 4+1 分层 + multivariate stationary block-bootstrap + Neff 特征值分解 + 过拟合检测矩阵（DSR/PBO/PDR/PSI/DFR + deflated-alpha 四家）+ 正交性验证 + CUSUM/PSI 漂移监控的七部分报告模板与阈值体系（战略级 0.6 vs 运营级 0.85/0.90 分层）。
>
> **未做事项及原因**：计算生产侧全部未落码（grep 实证零命中）——① 数据预处理 pipeline（对数收益率+ADF+异常值+交易日对齐）与策略级相关矩阵计算；② multivariate stationary block-bootstrap 引擎（Patton-Politis-White 自动 block size，无 block_bootstrap/stationary_bootstrap 实现）；③ 情绪周期分层标签器（消费 BM-SEL-23-B）；④ Neff 特征值分解引擎（Ledoit-Wolf 前置）；⑤ 过拟合检测引擎（deflated-alpha v0.3.0 vendor 集成 + PDR/PSI/DFR）；⑥ §5.4 CUSUM/PSI 相关性漂移监控。属"门禁已就位等输入、计算模块尚缺"状态——待首批策略回测收益率序列就绪后随 G07 施工批次建设；DCC-GARCH（第二阶段）与 §5.5 半衰期/双曲衰减建模为远期登记。

# 策略间相关性验证

> 本备忘定义多策略上线前策略间相关性验证的方法、阈值、数据区间与报告模板（[30_multi_strategy_concurrency §6.2](30_multi_strategy_concurrency.md) 施工前必做项）。
> 性质：永久态讨论记录，可随项目演进而修订。
> 管理规范见 [01_design_memo_management_spec.md](01_design_memo_management_spec.md)。
> 路线图定位见 [00_index_trading_decision](00_index_trading_decision.md) G07（P1，G04 后立即）。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G07 策略间相关性验证 |
| 所属 | [30_multi_strategy_concurrency §6.2](30_multi_strategy_concurrency.md)（施工前必做） |
| 依赖 | G04（需策略定义才能算相关，[20_first_batch_strategies §2.5](20_first_batch_strategies.md) 差异化矩阵为输入） |
| 对标 | Morwane block-bootstrap 相关性验证 / Susan Potter block-bootstrap 2026-05 / QBase v2.5 组合适配检查 2026-04 / DCC-GARCH Engle (2002) / Patton-Politis-White 自动 block size / deflated-alpha v0.3.0 四家过拟合审计（DSR+PBO/CSCV+Harvey-Liu haircuts+White RC/Hansen SPA，2026-07-26）/ Bailey-López de Prado DSR (2014) / Bailey-Borwein-López de Prado-Zhu PBO/CSCV (2017) / Harvey-Liu haircuts (2015) / White Reality Check (2000) + Hansen SPA (2005) / Soloviov DSR & PBO controlled studies 2026-07 |
| 正交性 | ✅ 与 regime 正交（验证 sleeve 间相关性，不读 regime 输出） |
| 优先级 | P1（G04 后立即） |
| 状态 | 已定稿·待施工（门禁 MOD-PA-004 已 production，相关性矩阵计算 + block-bootstrap + 情绪周期分层 + 过拟合检测引擎 v1.6.0 待施工） |

## 2. 背景

### 2.1 项目处境
- G04 首批 3 策略已定（打板 + 多因子 + 事件驱动，[20_first_batch_strategies §2.5](20_first_batch_strategies.md) 差异化矩阵已论证五维差异化），但 §2.5 唯一风险点："打板与事件驱动都受情绪周期隐形驱动，相关性可能高于直觉"——本验证正是该风险的实测关
- [30_multi_strategy_concurrency §6.2](30_multi_strategy_concurrency.md) 明确施工前必做：5 候选策略两两相关矩阵，按情绪周期分层看，各阶段都 >0.6 则"多策略实为情绪 beta 穿多件衣服"，需重新审视
- **现有 production 是门禁（消费者），非计算（生产者）**：
  - `strategy_correlation_gate`（[MOD-PA-004](../../../03_modules/_domain_portfolio_alloc/strategy_correlation_gate/blueprint.md)，D_PF_ALLOC，production/evolving）：G12 相关性门禁，**消费已算好的指标做阈值判定**（Pearson >0.85 REJECT / >0.90 HARD_REJECT，因子重叠/股票池重叠/行业集中度/尾部相关）。模块 docstring 明确："相关性矩阵/因子重叠的*计算*属数据层职责，本模块只消费已计算好的指标做门禁判定"
  - `correlation_analyzer`（[MOD-L02-005](../../../03_modules/_domain_factor/blueprint.md)，D_FACTOR，production）：Spearman 因子相关性（**因子间**去重，非策略间），含 `compute_rolling_correlation`（Pearson 滚动窗口）
- 故本 spec 的"相关性矩阵计算 + block-bootstrap + 情绪周期分层"为**待施工**——门禁已就位等输入，计算模块尚缺

### 2.2 核心问题
5 候选策略两两相关矩阵怎么算？按情绪周期分层怎么看？>0.6 如何重新审视（与门禁 0.85/0.90 的关系）？验证数据区间多大？报告模板长什么样？

**v1.6.0 扩展**：仅算相关性不够——多策略上线前还须回答"每个策略本身是否过拟合、组合是否捕捉正交 alpha 维度"：
- **多重检验问题**：5 候选策略从多少次参数搜索/组合试探中选出？若试了 N 次只挑最好的，最优 Sharpe 是 N 次零技能抽奖的最大值，naive 单检验 100% 误报（[marketmaker.cc 2026-06](https://marketmaker.cc/pt/blog/post/deflated-sharpe-multiple-testing/) 实证）
- **过拟合检测问题**：策略 IS 表现好但 OOS 退化多少算过拟合？PBO ~0.5 是抛硬币不是"半过拟合"，PBO null 是 0.5 不是 0（[pbo-search.marketmaker.cc 2026-07](https://pbo.marketmaker.cc/paper.pdf) controlled study）
- **正交维度问题**：堆叠相关指标（如打板 + 事件驱动都靠情绪周期）产生多重共线性，提供冗余数据而非独立信号确认；有效策略组合须捕捉数学正交的市场维度（[mental-momentum.ai 2026-06](https://mental-momentum.ai/) 实证 ML 喂原始价格持续优于喂显式技术指标）
- 这三个问题正是 §3.3 过拟合检测算法与 §3.1⑤ 报告模板新增第 6/7 部分要回答的

### 2.3 约束条件
- 情绪周期是隐形驱动（[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md)）→ 全样本相关性可能被主升/疯狂态主导，**必须分层看**才能识别"情绪 beta 穿多件衣服"
- **阈值分层（关键，避免与门禁矛盾）**：
  - **G07 战略级 >0.6**：重新审视策略组合（是否 alpha 同源/需合并/需降权）——本 spec
  - **门禁运营级 0.85/0.90**（MOD-PA-004）：REJECT/HARD_REJECT 阻止上线——已 production
  - 两者互补非冲突：0.6 是"战略警告，重新讨论"，0.85/0.90 是"运营硬否决，不准上线"
- 打板容量小、实盘样本少 → 验证主要靠回测日度收益率序列，实盘 track record 后复核

## 3. 决策：双相关系数 + 情绪周期分层 + block-bootstrap 置信区间 + 过拟合检测（待施工）

### 3.1 五项讨论要点逐项裁定

#### ① 5 候选策略两两相关矩阵 —— Pearson + Spearman 双版本（含数据预处理 pipeline）

**裁定**：用策略日度收益率序列算 **Pearson（线性）+ Spearman（秩，抗异常值）** 双版本，5 候选两两 10 对（C(5,2)=10）。算前强制数据预处理（防伪相关）。

- **5 候选清单**（[20_first_batch_strategies §2.1](20_first_batch_strategies.md) 更新后）：打板 / 多因子 / 事件驱动 / 价值反转 / 动量趋势（主升龙头已并入打板）
- **首批实测 3 对**（打板×多因子、打板×事件驱动、多因子×事件驱动），G11 第二批次补齐 10 对
- **数据预处理 pipeline（强制，防伪相关）**（[CSDN 2026-03](https://ask.csdn.net/questions/9432723) 实证 38.6% 基金序列非平稳→直接算相关伪相关率 61.2%）：
  1. **对数收益率统一**：所有策略统一用 r_t=ln(P_t/P_{t-1})，满足时间可加性；混用算术/对数致 Pearson 低估 0.07-0.12（打板高波动 vs 多因子低波动差异放大此偏误）
  2. **ADF 平稳性检验**：每条收益率序列 ADF 检验 p<0.05 才算 Pearson；非平稳序列一阶差分或改用协整检验（Engle-Granger），否则伪相关
  3. **异常值处理**：Modified Z-score（IQR 法）替代固定 10% 阈值动态识别连板日 ±10% 极值，提升估计稳定性 37%；不剔除但标注（Spearman 天然抗异常值）
  4. **交易日对齐**：统一有效交易日历，仅保留所有策略均有净值的日期，禁前向填充（前向填充使滚动相关标准差降低 23%，掩盖尾部协同）
- **双版本理由**：Pearson 是门禁 MOD-PA-004 消费的标准基准（口径一致）；Spearman 抗打板极端收益率（连板日 ±10% 极值会扭曲 Pearson）。`correlation_analyzer.compute_factor_correlation` 已实现 Spearman，可扩展到策略级
- **关键警告（[Soloviov signal-breadth 2026](https://signal-breadth.marketmaker.cc/)）**：相关性必须用 **PnL stream（收益率序列）**，禁用 binary 信号触发序列——二分法使相关性衰减约一半（tetrachoric effect），binary 估计永远高估分散 56%。本项目用 PnL 相关
- **对照**：QBase v2.5 2026-04 组合适配检查用"两两相关性矩阵标记 ≥0.40 的对"+ 边际 Sharpe 贡献（SR_candidate > ρ×SR_portfolio）；tickerly 2026-05 标准 <0.3、>0.5 显著共享

#### ② 按情绪周期分层看相关性 —— 用 BM-SEL-23-B 4+1 阶段打标签

**裁定**：用 BM-SEL-23-B 情绪周期 4+1 阶段（冰点/反核/主升/疯狂/退潮）给每个交易日打标签，分 5 段分别算相关矩阵。

- **分层理由**：全样本相关性可能被某阶段主导（主升态策略都涨→相关性虚高），分层看才知是否各阶段都高——[30 §6.2](30_multi_strategy_concurrency.md) "各阶段相关性都 >0.6"的"各阶段"即此意
- **隐式覆盖 stress correlation**：情绪周期分层的主升/疯狂态即高压力期（相关性飙升期），分层算相关 = 条件相关 = [invistaja 2026-08](https://invistaja.app.br/correlacao-portfolio-quant/) "最差回撤期相关"的结构化版本——全样本 Pearson 在危机期失效（invistaja 实证"相关性在压力期锁定上升"），分层是比滚动窗口更稳健的替代（DCC-GARCH §3.2 第二阶段是连续时变版）
- **本项目独创**：Morwane 按 3 态 Gaussian HMM regime 分层，本项目用情绪周期 4+1（更贴合 A 股打板/游资语境，[30 §1.3](30_multi_strategy_concurrency.md)）
- **前置依赖**：BM-SEL-23-B 情绪周期定位器的准确率（[30 §6.3](30_multi_strategy_concurrency.md) 待评估）——定位器错判会污染分层标签，需"置信度<60%→默认保守"兜底

#### ③ 若各阶段相关性 >0.6 则重新审视 —— 战略级警告（与门禁 0.85/0.90 互补）

**裁定**：>0.6 是**战略级重新审视**触发线，不是运营硬否决。

| 阈值 | 级别 | 触发动作 | 出处 |
|---|---|---|---|
| 各阶段 >0.6 | 战略警告 | 重新审视策略组合：检查 alpha 是否实际同源 / 是否需合并为单 sleeve / 是否需降权 | 本 spec（G07） |
| >0.85 | 运营否决 | REJECT，阻止该 pair 上线 | [MOD-PA-004](../../../03_modules/_domain_portfolio_alloc/strategy_correlation_gate/blueprint.md) 门禁 |
| >0.90 | 运营硬否决 | HARD_REJECT | 同上 |

- **>0.6 触发的审视清单**：① 信号源是否实际同源（如打板与事件驱动是否都靠情绪周期）② 持仓周期是否重叠 ③ 选股池交集率（[20 §2.6](20_first_batch_strategies.md) 低交集设计是否成立）④ 是否合并为单 sleeve（违反 charter 约束五"禁止堆砌相似策略"则合并）
- **0.6 取值依据**：QBase 2026 用 0.4-0.5 作组合适配，tickerly 2026 用 0.3 标准/0.5 显著共享；本项目 0.6 更宽松，因它是"战略重新讨论"非"硬否决"——留出讨论空间，真否决交给 0.85/0.90 门禁

#### ④ 验证数据区间 —— in-sample 2020-2026 + 按阶段样本量标注

**裁定**：in-sample 2020-2026（含牛熊 + 情绪周期完整循环），OOS 预留（[20 §4.4](20_first_batch_strategies.md) honest split）。

- **按情绪周期分层需每阶段 ≥30 交易日样本**，否则该阶段相关性不可信，标注"样本不足"
- 冰点/疯狂态稀有（[30 §2.2](30_multi_strategy_concurrency.md) 稀有态 <1%），样本可能不足 → 标注 + 用灰度软分配（[30 §6.5](30_multi_strategy_concurrency.md) 过渡期天按 P 比例贡献给多阶段）缓解
- **打板策略实盘样本少**（容量小、首批 track record 短）→ 首轮验证主要靠回测日度收益率，实盘 3 个月后复核

#### ⑤ 验证报告模板

**裁定**：报告含七部分（v1.6.0：原五部分 + 过拟合检测矩阵 + 正交性验证）——

1. **全样本 5×5 相关矩阵**（Pearson + Spearman 双版本，对角线=1，下三角 Pearson 上三角 Spearman 或两矩阵并列）
2. **分层 5×5×5 矩阵**（5 情绪阶段 × 5 策略 × 5 策略），每阶段标注样本量
3. **block-bootstrap 置信区间**（§3.2，multivariate 同步重采样，每对相关性 90% CI + P(ρ>0.6)）+ **Fisher z-transform 参数 CI 交叉验证**（z=0.5·ln((1+ρ)/(1-ρ))，z~N(0, 1/(n-3))，参数法与非参数 block-bootstrap 互验；两者 CI 区间一致则结论稳健，不一致则以 block-bootstrap 为准因其不假设正态）
4. **组合层有效下注数 Neff**（[stockalpha 2026-02](https://stockalpha.ai/alpha-learning/effective-number-of-bets-measuring-diversification-beyond-holding-counts)）：
   - **公式**：对 5×5 相关矩阵做特征值分解，**Neff=(Σλ)²/Σλ²**，衡量组合真正有多少独立风险方向。两两都<0.6 但 Neff<3 仍危险（5 策略实际只有<3 个独立下注）
   - **等相关近似**（仅辅助）：**Neff≈N/(1+(N-1)ρ̄)**（ρ̄=平均两两相关）作快速估算，但 [Soloviov 2026](https://signal-breadth.marketmaker.cc/) 警告此公式对 PnL stream 偏差随共同因子载荷 β 从 -56% 到 +91%——故以特征值分解 Neff 为准
   - **数值稳定性前置**：若 5 策略高度相关（正是本验证要检测的情况），样本相关矩阵近奇异、最小特征值≈0、特征值分解数值不稳定（[metricgate 2026-03](https://metricgate.com/blogs/ledoit-wolf-shrinkage-covariance-matrix/) "p close to n → smallest eigenvalues pushed near zero"）；须先 **Ledoit-Wolf 收缩**（Σ_shrink=(1-α)S+αF，F=等相关目标，α 闭式最优自动选择，保证正定、稳定特征值）再算 Neff
   - **α 双重用途**：收缩强度 α 本身也是"组合相关程度"的信号（α 大=噪声大/相关性结构弱）
   - **自洽性说明**：收缩后 Neff 偏乐观（收缩拉高最小特征值→Neff 偏大），故 Neff<3 判据需结合 α 共读——α 大（重收缩）即使 Neff≥3 也应警惕（原始矩阵噪声大/相关结构不可靠）；α 小（轻收缩）+ Neff≥3 才是稳健的分散结论
5. **结论**：是否"情绪 beta 穿多件衣服"——判定需**多指标交叉验证**（[clawrxiv 2026-04](https://www.clawrxiv.io/abs/2604.01213) 实证 5 种分散化指标对 3/11 行业方向不一致）：① 各阶段 >0.6 对数 ≥3 对 ② Neff<3 ③ 两两最大相关 >0.6，三条件任一触发即重新审视（§3.1③ 清单）
6. **过拟合检测矩阵**（§3.3，v1.6.0 新增——回答"每个策略本身是否过拟合、能否从 N 次试探中存活"）。每策略一行，至少 6 列：
   - **DSR**（Deflated Sharpe Ratio）：P(true SR > 0 | 已从 N 次试探中选最好)，DSR ≥ 0.95 通过（[Bailey-López de Prado 2014](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2465675)）
   - **PBO**（Probability of Backtest Overfitting，CSCV）：P(IS 冠军 OOS 落入下半场)，PBO <0.05 通过、≈0.5 抛硬币完全过拟合、>0.5 严重过拟合（[pbo-search.marketmaker.cc 2026-07](https://pbo.marketmaker.cc/paper.pdf) controlled study 明确 null=0.5；[dhawal.org 2026](https://dhawal.org/) PBO 阈值校准）
   - **OOS 退化斜率**（performance degradation slope）：IS→OOS Sharpe 回归斜率，>0 通过（deflated-alpha v0.3.0 输出）
   - **PDR**（Performance Degradation Ratio = (IS_SR − OOS_SR)/IS_SR）：PDR<0.5 通过、≥0.5 严重过拟合（[digitalninjasystems 2026-05](https://digitalninjasystems.com/)）
   - **PSI**（Parameter Stability Index = Best_SR / Avg_SR，注意与 §5.4 Population Stability Index 同名异义——本节是过拟合检测的参数稳定指数）：PSI<3.0 通过、≥3.0 过拟合（[digitalninjasystems 2026-05](https://digitalninjasystems.com/)）
   - **DFR**（Degrees of Freedom Ratio = N_obs / N_params）：DFR≥30 通过、<30 参数过多（[backtrex 2026-05](https://backtrex.com/en/blog/overfitting-backtesting-detect-prevent) 机构共识 ≥30 trades/parameter）
   - **胜率/PF 警戒线**（辅助）：胜率 >70% 或 profit factor >3.0 需极端怀疑（[digitalninjasystems 2026-05](https://digitalninjasystems.com/) 实证 70% 零售回测盈利策略前向测试变亏损）
   - **综合 verdict**：LIKELY_REAL / INCONCLUSIVE / LIKELY_OVERFIT（deflated-alpha v0.3.0 三态判定）
7. **策略组合正交性验证**（§3.3，v1.6.0 新增——回答"5 策略是否捕捉数学正交的市场维度"）。基于 [mental-momentum.ai 2026-06](https://mental-momentum.ai/) 的"有效指标组合须捕捉数学正交维度"原则，验证 5 候选策略是否覆盖以下三个正交维度而非堆叠共线指标：
   - **趋势方向**（trend direction）：打板 / 动量趋势 → 是否都靠情绪周期主升态？（若是则维度退化）
   - **执行时机**（execution timing）：事件驱动 / 多因子 → 是否都靠同一触发时点？
   - **风险大小**（risk sizing）：价值反转 → 是否独立于前两者？
   - 判定：① 若三维度都被同一隐性因子（情绪周期）驱动 → 组合退化，需引入正交新策略 ② 若至少两维度独立 → 组合有效 ③ 与 §3.1⑤ 结论"情绪 beta 穿多件衣服"互验（两结论一致则稳健，不一致则以正交性维度为准——维度退化是更深层的过拟合）
   - 对照 [20 §2.5](20_first_batch_strategies.md) 五维差异化矩阵（信号源/持仓周期/选股池/容量/容量约束）—— 本节是从数学正交性角度补强差异化矩阵

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-BT-05-I | 组合级过拟合检测 | §3.1⑤ 报告模板第 6 部分过拟合检测矩阵（DSR/PBO/OOS 退化斜率/PDR/PSI/DFR 六列+综合 verdict，§3.3 算法 why）+ 第 7 部分正交性验证（维度退化=组合层过拟合判定） | design 待施工（报告矩阵 v1.6.0 定型，计算模块待建） |

### 3.2 方法选型（why 决策，待施工）

| 方法 | 选用 | 理由 |
|---|---|---|
| **数据预处理 pipeline**（对数收益率+ADF+异常值+对齐） | ✅ 首轮强制 | CSDN 2026-03 实证 38.6% 序列非平稳→伪相关率 61.2%；不预处理直接算 Pearson 可致偏离 0.15+ |
| **Pearson 相关** | ✅ 首轮 | 线性相关标准基准，门禁 MOD-PA-004 消费口径一致 |
| **Spearman 秩相关** | ✅ 首轮 | 抗打板极端收益率（连板日 ±10%），`correlation_analyzer` 已用 |
| **stationary block-bootstrap 2000×（multivariate/paired 同步重采样）** | ✅ 首轮 | Politis-Romano stationary bootstrap（block length 几何分布，均值 ℓ），保留 autocorrelation/volatility clustering/cross-sectional correlation（Susan Potter 2026-05）；给相关性与 Sharpe 的 90% CI。**关键施工细节**：必须用 **multivariate/paired 版本**——同一时间 block 对所有 5 策略同步重采样（行重采样，[tsbootstrap 2026-07](https://tsbootstrap.readthedocs.io/en/latest/tutorials/multivariate_var.html) "resample whole rows, contemporaneous relationship carried along untouched"；[SignalY 2026-02](https://r-packages.io/packages/SignalY/block_bootstrap) "blocks sampled synchronously across all variables to preserve cross-sectional dependence, critical for joint distribution"）。若各自独立重采样→破坏策略间同期相关→置信区间失效 |
| **block size 自动选择（Patton-Politis-White）** | ✅ 首轮 | 替代固定 21 天——Patton-Politis-White (2009) 自动最优 block size 算法（`b.star`），估计值在真实最优 90%-110%；经验法则 ℓ≈c·n^(1/3)。21 天作为先验参考上限（打板 1-3 天持仓 + Morwane 月度范式），实际由数据驱动 |
| **按情绪周期 4+1 分层** | ✅ 首轮 | 本项目独创，[30 §1.3](30_multi_strategy_concurrency.md) 核心担忧是分层后仍高；离散 regime 方法 |
| **组合层有效下注数 Neff（特征值分解）** | ✅ 首轮 | Neff=(Σλ)²/Σλ² 补两两矩阵的盲区——两两都<0.6 但 Neff<3 仍危险（[stockalpha 2026-02](https://stockalpha.ai/alpha-learning/effective-number-of-bets-measuring-diversification-beyond-holding-counts)）；等相关简化 Neff≈N/(1+(N-1)ρ̄) 仅辅助（[Soloviov 2026](https://signal-breadth.marketmaker.cc/) 警告 PnL stream 偏差 -56%~+91%） |
| **DCC-GARCH（时变相关性）** | ⚠️ 第二阶段增强 | Engle (2002) Dynamic Conditional Correlation 捕捉**时变**相关性（Pearson/Spearman 是静态标量）；Soloviov 2026-07 实证 DCC 跟踪相关性路径 MAE=0.028 vs 静态 0.208（差 7 倍），静态协方差危机期违规率 2.2 倍名义值；只 2 参数 (a,b)，可扩展（d=50 仅 152 参数）。**与情绪周期分层互补**：DCC=连续时变，分层=离散 regime |
| Markov-switching DCC | ❌ 过重 | clawrxiv 2026-04 实证标准 DCC 在 regime 转换期低估 VaR 18%，MS-DCC 达 97.5% 覆盖——但参数多、个人项目过重；首轮用情绪周期分层（离散 regime）覆盖 DCC 转换期弱点 |
| naive i.i.d. bootstrap | ❌ | Susan Potter 2026-05 论证破坏时序结构；metricgate 2026-06 实证 AR(1) ϕ=0.7 时低估标准误至真值 40% |
| copula（尾部相关） | ❌ 首轮 | marketmaker.cc 2026-07 指出 DCC 与 copula 互补（copula 给静态灵活尾部结构）；但门禁 MOD-PA-004 已有 tail_correlation（EVT）维度覆盖尾部，首轮不重复 |
| tapered block bootstrap | ⚠️ 备选 | Paparoditis-Politis (2001) 减少 block 边缘偏差，精度更高；首轮 stationary bootstrap 已够，CI 过宽时升级 |
| **纯解析 DSR 公式（快速 screen）** | ⚠️ 辅助 | 作快速 screen，block-bootstrap 作严格确认（Susan Potter 建议两者并用）。**注意**：此行仅指闭式 PSR 公式（不含 N 修正），与完整 DSR 多重检验校正（下条）不同——前者是单检验基准，后者 deflates against N-trial expected max |
| **DSR 多重检验校正（完整版，Bailey-López de Prado 2014）** | ✅ 首轮（v1.6.0） | P(true SR > 0 | 已从 N 次试探中选最好)。null=0 时 naive 单检验对 N=1000 零技能策略 100% 误报（[marketmaker.cc 2026-06](https://marketmaker.cc/pt/blog/post/deflated-sharpe-multiple-testing/) 实证假阳性率 1.000），DSR 降到 0.001。**deflated benchmark SR₀** = 噪声天花板（N=1000 零技能抽奖的期望最大 Sharpe ≈ 1.63 年化），策略须超过此天花板而非 >0。**effective trials**（DSR Appendix 3）：相关策略试探 overstate N，用 N̂=ρ̄+(1−ρ̄)·M 估计有效独立试验数——本项目 5 候选策略若高度相关，effective N 远小于 nominal trial count，DSR 须用 effective N 而非 raw count（[dsr.marketmaker.cc 2026-07](https://dsr.marketmaker.cc/paper.pdf) controlled study 实证同一 trial matrix 5 估计器分歧达两个数量级 1.6~370.0，须给 robustness band） |
| **PBO via CSCV（Bailey-Borwein-López de Prado-Zhu 2017）** | ✅ 首轮（v1.6.0） | Combinatorially Symmetric Cross-Validation：T 行分 S=16 块，枚举 C(16,8)=12870 对称 IS/OOS 划分，IS 冠军在 OOS 排名的相对位 ω=rank_OOS/(N+1)，logit(ω)<0 即 IS 冠军 OOS 落入下半场，PBO=该事件频率。**PBO null=0.5 不是 0**（exchangeability 论证：纯噪声下 IS 冠军 OOS 等概率落任何位置），≈0.5=抛硬币完全过拟合，<0.05 通过，>0.5 严重过拟合（[pbo-search.marketmaker.cc 2026-07](https://pbo.marketmaker.cc/paper.pdf) controlled study 三 regime 实证：纯噪声 PBO=0.476、planted edge PBO=0.001、MA-crossover grid on random walk PBO=0.463）。**rank-based 抗 regime shift**（不变于 IS/OOS 间波动率变化）；与情绪周期分层正交（PBO 测"选择过程"是否 generalize，分层测"相关性结构"是否稳定）。工程参数 n_subsets=max(1000, 10×|Θ|)、window=floor(0.3×T)、n_perm=500（[CSDN 2026-03](https://blog.csdn.net/2501_92877300/article/details/150304073) PBO 三重脆弱性建议） |
| **OOS 退化斜率（performance degradation slope）** | ✅ 首轮（v1.6.0） | IS→OOS Sharpe 回归斜率，>0 通过。deflated-alpha v0.3.0 输出。**关键陷阱**：IS/OOS halves 互补，常胜策略即使有真 edge 也会显示反相关 halves——deflated-alpha 报告标注此 mechanical case（[deflated-alpha README 2026-07](https://github.com/0scarito/deflated-alpha) Limitations 节） |
| **PDR/PSI/DFR 过拟合检测指标** | ✅ 辅助（v1.6.0） | 三指标补 DSR/PBO 的盲区：① **PDR**=(IS_SR−OOS_SR)/IS_SR，≥0.5 严重过拟合（[digitalninjasystems 2026-05](https://digitalninjasystems.com/)）② **PSI**=Best_SR/Avg_SR，≥3.0 过拟合（**注意**：与 §5.4 Population Stability Index 同名异义，本节是 Parameter Stability Index 过拟合检测，§5.4 是漂移监控）③ **DFR**=N_obs/N_params，<30 参数过多（[backtrex 2026-05](https://backtrex.com/en/blog/overfitting-backtesting-detect-prevent) 机构共识）。胜率>70% 或 PF>3.0 警戒线（[digitalninjasystems 2026-05](https://digitalninjasystems.com/) 实证 70% 零售回测盈利策略前向测试变亏损） |
| **Harvey-Liu haircuts（Bonferroni/Holm/BHY）** | ✅ 首轮（v1.6.0，通过 deflated-alpha 工具一次集成） | 三种经典多重检验校正把 winner 的 t-stat p-value 调整后反推 haircut Sharpe：Bonferroni/Holm 控制 FWER，BHY 控制 FDR。**rank-1 特性**：Holm 与 Bonferroni 在 top-rank 完全一致（(M-1+1)p=Mp），不构成独立互验；BHY 在 top-rank 最保守（×Mc(M)≥M）。[dsr.marketmaker.cc 2026-07](https://dsr.marketmaker.cc/paper.pdf) controlled study：Bonferroni/Holm 假阳性率 0.057，BHY 0.007，均受控。**不独立实现**——通过 deflated-alpha audit() 一次集成避免过重 |
| **White Reality Check + Hansen SPA（bootstrap data-snooping）** | ✅ 首轮（v1.6.0，通过 deflated-alpha 工具一次集成） | White RC (2000) 用 stationary bootstrap 重采样整个 trial matrix 联合分布，构建"零技能抽奖 best 表现"的 null，p-value = 重采样 best ≥ 实测 best 的频率。Hansen SPA (2005) 加 studentization + consistent recentering 防止 poor high-variance alternatives 主导（conservative）。**关键**：bootstrap 重采样所有 K 试验联合，**保留 cross-trial 相关结构**——与 §3.2 stationary block-bootstrap 同源（Politis-Romano 1994），但应用场景不同（§3.2 重采样策略对算相关性 CI，本节重采样整个 trial matrix 算 best-performance null）。[dsr.marketmaker.cc 2026-07](https://dsr.marketmaker.cc/paper.pdf) controlled study：White RC 假阳性率 0.022，受控。**不独立实现**——通过 deflated-alpha audit() 一次集成 |
| **deflated-alpha v0.3.0 工具（一次 audit() 集成四家测试）** | ✅ 首轮（v1.6.0） | [deflated-alpha v0.3.0](https://github.com/0scarito/deflated-alpha)（2026-07-26）一个 audit() 接口运行全部四家过拟合检测：① Analytical（DSR+PSR+MinTRL）② Combinatorial（PBO/CSCV）③ Multiple-testing（Harvey-Liu Bonferroni/Holm/BHY）④ Bootstrap data-snooping（White RC + Hansen SPA）。输出 verdict LIKELY_REAL/INCONCLUSIVE/LIKELY_OVERFIT + 各 check value/status 表格。**为什么必须四家同跑**：[deflated-alpha 案例 (b) SMA crossover on zero-drift random walk](https://github.com/0scarito/deflated-alpha) 实证 DSR=0.989 几乎被骗 + SPA p=0.019 错误显著，只有 PBO=0.782 抓住过拟合——**没有单一测试充分**。**输入要求**：传入全部 N 次试探的 T×N returns matrix（不是仅 winner），只传 winner 无法审计。**effective trials**（v0.2.0）：N̂=ρ̄+(1−ρ̄)·M 自动估计有效独立数——估计器分歧与 robustness band 要求同上 DSR 行（同一 controlled study） |
| **PBO + SRD + DSR 三维交叉验证矩阵（CSDN 2026-03）** | ✅ 首轮（v1.6.0，作为 §3.1⑤ 报告模板第 6 部分的判定框架） | [CSDN 2026-03](https://blog.csdn.net/2501_92877300/article/details/150304073) PBO 三重脆弱性框架：① 子样本构造偏差（滑动窗口违反零均值假设）② 平稳性幻觉（结构性断点）③ 搜索空间覆盖不足。三维交叉验证：PBO（子样本失效频率，n_subsets≥1000，window≥6M，<0.10 警戒线）+ SRD（Sharpe Ratio Decay，滚动 12M 窗口斜率变化率，步长 1M，斜率<−0.03/年）+ DSR（校正多重检验后 Sharpe 显著性，有效独立策略数 K，DSR>1.0 显著）。**PBO 非贝叶斯后验概率，而是经验性拒绝率**——避免误解为"50% 概率过拟合" |

**待施工模块**：数据预处理 pipeline（对数收益率+ADF+异常值+对齐）+ 相关性矩阵计算（Pearson/Spearman，扩展 `correlation_analyzer` 到策略级）+ 组合层 Neff 特征值分解 + **multivariate stationary block-bootstrap 引擎**（Patton-Politis-White 自动 block size，2000×，5 策略同步行重采样）+ 情绪周期分层标签器（消费 BM-SEL-23-B 输出）+ **过拟合检测引擎**（v1.6.0 新增：deflated-alpha v0.3.0 工具集成，audit() 一次运行 DSR+PBO/CSCV+Harvey-Liu haircuts+White RC/Hansen SPA；输入要求传入全部 N 次试探的 T×N returns matrix；辅以 PDR/PSI/DFR 三指标）。第二阶段增强 DCC-GARCH（arch 库 univariate GARCH + DCC 两步估计）。门禁 MOD-PA-004 已就位待消费。

### 3.3 过拟合检测算法（v1.6.0 新增——why 决策）

§3.2 已把方法表列全，本节回答"为什么这套算法是必做施工环节，而非可选增强"：

**① 必要性——多策略上线前只算相关性不够**：
- §3.1①-⑤ 算的是"策略两两/分层/组合层相关性是否过高"，但**相关性低≠策略本身有效**——5 个低相关策略可能全是过拟合的噪声冠军（N 次试探选最好，naive 单检验 100% 误报——marketmaker.cc 2026-06 controlled study 实证，§2.2 已引）。低相关只是"分散假设成立"，不保证"每个 sleeve 有真 alpha"
- [20 §2.5](20_first_batch_strategies.md) 五维差异化矩阵从设计层论证策略差异，但**设计差异不等于统计显著性**——DSR/PBO 是从统计层验证设计层假设的工具

**② 算法分层——四家测试互验而非任一单选**：
- §3.2 方法表 deflated-alpha 行案例 (b) 实证：零漂移 random walk 上的 SMA crossover，DSR/SPA 均被骗（应 fail 却 pass），只有 PBO/CSCV 抓住过拟合——**没有单一测试充分**（数值见 §3.2/§8.3）
- 故 §3.2 方法表把四家全标"✅ 首轮"——Analytical（DSR）+ Combinatorial（PBO）+ Multiple-testing（Harvey-Liu）+ Bootstrap data-snooping（White RC/Hansen SPA）四角度互验
- deflated-alpha audit() 一次集成避免"四家分别实现"的过重——个人项目不可能独立实现 White RC + Hansen SPA 的 stationary bootstrap recentring

**③ 与 §3.1② 情绪周期分层的关系——正交非冗余**：
- §3.1② 算"per-regime 相关性是否各阶段都高"（相关性结构稳定性）
- §3.3 算"IS→OOS 选择过程是否 generalize"（策略有效性稳定性）
- 两者正交：一个策略可能 PBO=0（不过拟合）但 per-regime 相关性 >0.6（与其他策略共线）——前者说"它有真 edge"，后者说"它的 edge 与他人重叠"
- PBO 的 rank-based 设计（rank_OOS/(N+1)）**抗 regime shift**——与情绪周期分层的"主升态相关性飙升"问题正交

**④ effective trials 的争议性——标在 §7 待定问题**：
- DSR 假设 N 次试探独立，但策略试探高度相关（如打板策略试了 20 组参数，本质是 1 个 edge 的 20 种噪声变体）
- deflated-alpha v0.2.0 用 N̂=ρ̄+(1−ρ̄)·M 估计 effective N，但 controlled study 实证 5 个标准估计器在同一 trial matrix 上分歧达两个数量级（1.6~370.0，§3.2 DSR 行已引）
- 决策：报告 effective N 的 robustness band（最小到最大估计），而非点估计——若所有估计下 verdict 一致才下结论

**⑤ 与 §5.4 上线后漂移监控的关系——施工前一次性 vs 上线后持续**：
- §3.3 是施工前一次性过拟合检测（DSR/PBO 一次算完，verdict 决定是否上线）
- §5.4 是上线后持续漂移监控（CUSUM/PSI 持续追踪相关性结构变化）
- 两者互补：§3.3 防"上线即过拟合"，§5.4 防"上线后漂移到过拟合"

## 4. 考虑过的替代方案

### 4.1 naive i.i.d. bootstrap vs block-bootstrap —— 选 block-bootstrap
- **拒绝 naive**：Susan Potter 2026-05 明确论证 naive bootstrap 破坏 autocorrelation（动量/均值回归模式消失）、volatility clustering（GARCH 结构散失）、cross-sectional correlation（对冲关系断裂）——策略相关性验证恰恰依赖这三者
- **裁定 block-bootstrap**：21-day stationary blocks（Morwane proven），保留时序结构

### 4.2 纯 Pearson vs Pearson + Spearman —— 选双版本
- **拒绝纯 Pearson**：打板连板日 ±10% 极值会扭曲线性相关
- **裁定双版本**：Pearson 对齐门禁口径，Spearman 抗异常值，两者差异大时以 Spearman 为准并标注

### 4.3 全样本相关 vs 按情绪周期分层 —— 选分层
- **拒绝纯全样本**：全样本被主升/疯狂态主导，掩盖"各阶段都高"的真问题（[30 §6.2](30_multi_strategy_concurrency.md) 核心担忧）
- **裁定分层**：5 阶段分别算，检验"各阶段都 >0.6"——这才是"情绪 beta 穿多件衣服"的判据

### 4.4 静态相关 vs DCC-GARCH 时变 —— 选分层首轮 + DCC 第二阶段
- **拒绝首轮 DCC-GARCH**：静态 Pearson/Spearman 是标量，DCC 给时变矩阵，但 DCC 需 2 参数估计 + univariate GARCH 前置 + regime 转换期低估 VaR 18%（[clawrxiv 2026-04](https://www.clawrxiv.io/abs/2604.01458)）——首轮过重
- **裁定分层首轮 + DCC 第二阶段**：情绪周期 4+1 分层（§3.1②）是离散 regime 版的时变相关，首轮够用；若需连续时变细节（相关性何时飙升）则第二阶段引入 DCC-GARCH（§3.2 方法表 DCC-GARCH 行）

### 4.5 纯解析 DSR vs deflated-alpha 工具集成（v1.6.0 新增）—— 选工具集成
- **拒绝纯解析 DSR**：闭式 DSR 公式（PSR[SR*]）虽轻量，但 ① 缺 PBO/CSCV 互补（[deflated-alpha 案例 (b)](https://github.com/0scarito/deflated-alpha) 实证 DSR 单独被 SMA crossover on random walk 骗过）② 缺 Harvey-Liu haircut 与 White RC/Hansen SPA 互验 ③ effective trials 估计器选择争议大（[dsr.marketmaker.cc 2026-07](https://dsr.marketmaker.cc/paper.pdf) 实证 5 估计器分歧两个数量级），需工具内置多估计器对比
- **拒绝独立实现四家**：White RC + Hansen SPA 的 stationary bootstrap recentring 实现复杂（每 trial recenter 到自身 mean 才能满足 null by construction），个人项目独立实现易引入数值 bug
- **裁定 deflated-alpha v0.3.0 工具集成**：MIT 许可，纯 Python（numpy/scipy/pandas），`pip install git+https://github.com/0scarito/deflated-alpha.git`；audit() 一次跑四家，输出 verdict + 各 check status 表格，测试套件复现论文数值（DSR JPM 2014 N=100 → 0.9004；CSCV JoCF 2017 S=16 → 12870 组合；stationary bootstrap JASA 1994 mean block 1/q 验证）。**风险**：依赖外部包——标在 §6 待裁定（vendor 评估或 fork）。**备选**：[KinSushi/backtest-overfitting-lab](https://github.com/KinSushi/backtest-overfitting-lab) 2026-06 零第三方依赖（Python 标准库 only），DSR/PBO/RC/SPA battery，但功能不如 deflated-alpha 全面（无 effective trials 修正）——vendor 评估时对比

## 5. 上限定义

### 5.1 系统上限
- 5 候选策略两两 10 对 ×（Pearson + Spearman）×（全样本 + 5 阶段分层）× block-bootstrap 2000× = **一次性施工前验证**（非 runtime 周期任务）
- **过拟合检测**（v1.6.0 新增）：5 候选策略各自的参数搜索 history（T×N returns matrix，N=每策略试探次数）→ deflated-alpha audit() 一次跑四家 + PDR/PSI/DFR 三指标。audit() 成本 O(n_boot·T·N)，bootstrap 默认 off 需显式 `--bootstrap` 开启（deflated-alpha README Limitations）；5 策略各跑一次 audit ≈ 分钟级
- 门禁 MOD-PA-004（运营级 0.85/0.90）已 production，本验证（战略级 0.6）是其输入生产者

### 5.2 演进路径
- **第一阶段（首批 3 策略上线前）**：实测 3 对（打板×多因子、打板×事件驱动、多因子×事件驱动），block-bootstrap 2000×，5 阶段分层；**并行跑 §3.3 过拟合检测**（每策略各自的参数搜索 history 喂 deflated-alpha audit()，要求 LIKELY_REAL verdict 才上线）
- **第二阶段（G11 第二批次）**：补价值反转/动量趋势后全 10 对；过拟合检测同步覆盖新增 2 策略
- **第三阶段（实盘 track record 后）**：用实盘日度收益率复核回测相关性，验证回测-实盘一致性——并启动 §5.4 相关性漂移持续监控（CUSUM + PSI），非一次性复核；过拟合检测可重跑（实盘 track record 作新 OOS 喂 audit）

### 5.3 为何是上限而非妥协
- **2000× 非过重**（过度工程审查）：Morwane 同量级 small personal project 已用 2000×（21-day blocks）验证通过；Susan Potter 2026-05 称 bootstrap 是"杀死最多策略的步骤"高价值；2000× 一次性施工前验证非 runtime，5 策略 × 10 对 × 2000 resample on 日度收益率 ~秒-分钟级
- **降级路径**：算力不足时先 Pearson/Spearman 点估计 + DSR 解析公式 screen，block-bootstrap 作严格确认（Susan Potter 建议两者并用）；过拟合检测可先只跑 DSR+PBO（关 bootstrap），Harvey-Liu/White RC/Hansen SPA 通过 deflated-alpha `--bootstrap` flag 按需开
- **过度参数化风险已规避**：stationary block-bootstrap（Politis-Romano，Potter 推荐）+ Patton-Politis-White 自动 block size（数据驱动，非人工网格搜索）+ 一次 pass，不做多 block size × 多方法 × 多 window 的研究网格；DCC-GARCH 列第二阶段增强而非首轮，避免一次性引入过多方法
- **过拟合检测不构成过度工程**（v1.6.0 新增审查）：
  - 四家测试（DSR/PBO/Harvey-Liu/White RC+Hansen SPA）看似多，但通过 deflated-alpha 工具一次集成，**不增加独立实现负担**——本质是调用一个 `audit()` 接口读 verdict，非"自研四套统计引擎"
  - deflated-alpha v0.3.0 是 [0scarito 2026-07-26](https://github.com/0scarito/deflated-alpha) MIT 许可工具，3 commits 单一作者维护，依赖 numpy/scipy/pandas——轻量、无重型依赖（vs mlfinlab 已 paywall）
  - PDR/PSI/DFR 三指标是简单比率（除法），不构成额外施工
  - **风险点**：四家 verdict 不一致时如何决策（如 DSR pass 但 PBO fail）——标在 §7 待定问题，首轮以"任一 fail 即不上线"保守策略
  - **失败模式覆盖边界**（[Student One 2026-06](https://dashboard.studentone.tech/blog/out-of-sample-tests-counter-overfitting-menu/) 四模式分类）：G07 过拟合检测覆盖 **①选择过拟合**（DSR/PBO/Harvey-Liu/White RC 捕获"多试选优"统计假象）+ **④路径依赖**（PDR/PSI/DFR + block-bootstrap 捕获"单条历史路径幸存"假象）；**②参数过拟合**（walk-forward/purged K-fold 捕获"参数调到噪声"）+ **③泄漏**（purged K-fold 捕获"测试期信息渗入训练"）归策略开发者——[20 §4.4](20_first_batch_strategies.md) honest split 已含 walk-forward。下方"不做"项均属②③范畴或①④的冗余变体
  - **不做**：不做 walk-forward CV 与 PBO/CSCV 的双重跑（[20 §4.4](20_first_batch_strategies.md) honest split 已含 walk-forward；PBO/CSCV 是 walk-forward 的统计严格化版，两者冗余）；不做 Monte Carlo permutation test（deflated-alpha 已含 bootstrap data-snooping，permutation 是其变体）；不做 Combinatorial Purged Cross-Validation（CPCV，López de Prado 2018）——CPCV 是 CSCV 加 purge，本项目首批 3 策略无重叠训练数据，purge 无对象

### 5.4 相关性漂移监控（上线后持续）

§3.2 block-bootstrap 验证的是**施工前静态**相关性。上线后策略间相关性会漂移（regime 变化、拥挤度上升、共同因子暴露变化），原本 <0.6 的组合可能漂移到 >0.8——分散假设静默失效。需持续监控（[stockalpha 2026-02](https://stockalpha.ai/alpha-learning/concept-drift-alarms-for-quant-signals-detecting-when-alpha-decays) / [MathAndMarkets 2026-02](https://mathandmarkets.com/p/detecting-decay-in-real-time-when) / [brainbytes 2026-08](https://lobehub.com/it/skills/brainbytes-dev-everything-claude-trading-live-trading-monitoring)），非一次性复核。

- **CUSUM on rolling correlation**（主检测器）：对每对策略的滚动 63 日 Spearman ρ_t 做 CUSUM——S⁺ₜ = max(0, S⁺ₜ₋₁ + (ρ_t − ρ₀) − k)，ρ₀ = block-bootstrap 验证基线，k=0.5σ（σ=ρ_t 滚动标准差），告警阈值 h=4σ（[MathAndMarkets 2026-02](https://mathandmarkets.com/p/detecting-decay-in-real-time-when) ~0.5 次/年误报，检测延迟 ~50 交易日）。S⁺ₜ > h = 相关性结构性上升
- **PSI on correlation distribution**（辅助）：Population Stability Index 对比基线期与近 63 日 ρ 分布，PSI>0.2 调查 / >0.4 告警（[stockalpha 2026-02](https://stockalpha.ai/alpha-learning/concept-drift-alarms-for-quant-signals-detecting-when-alpha-decays)）
- **Page-Hinkley**（探索性备选）：不需预设 ρ₀，追踪累积偏离运行均值，适合 regime 切换探索（[stockalpha 2026-02](https://stockalpha.ai/alpha-learning/concept-drift-alarms-for-quant-signals-detecting-when-alpha-decays)）
- **分级响应**：告警 → 相关对权重×0.5 → 停止新入场 → 重跑 §3.2 block-bootstrap。复用项目现有 deadman switch / reconciler 监控基础设施（[00_index](00_index_trading_decision.md)），非新建独立监控系统
- **多重检验校正**：10 对 × 3 检测器 = 30 监控点，Benjamini-Hochberg FDR 控制误报率（[stockalpha 2026-02](https://stockalpha.ai/alpha-learning/concept-drift-alarms-for-quant-signals-detecting-when-alpha-decays)）

### 5.5 因子衰减与拥挤度建模（v1.7.0 新增——2026-08 最新理论研究，远期候选）

§5.4 CUSUM/PSI 监控的是**相关性漂移症状**，但因子衰减与拥挤度是其**根因**。2026 年出现两篇理论突破性论文，为因子衰减提供可检验的函数形式与因果机制——登记为远期候选，待首轮实盘 6-12 月后评估是否从"症状监控"升级为"根因建模"。

#### 5.5.1 Alpha 半衰期定理（Meng & Chen 2026-05，arXiv:2605.23905）

[Meng & Chen 2026-05, "AI-Driven Alpha Decay: Algorithmic Homogenization, Reflexive Signal Erosion, and the Paradox of Intelligent Markets"](https://arxiv.org/abs/2605.23905)（NYU）推导**Alpha 半衰期定理**，证明信号寿命随算法密度非线性缩短：

- **三大衰减通道**：① Signal Crowding（算法同质化——13F 数据 2013-2024 机构组合趋同度增长 42%）；② Performative Erosion（执行本身加速套利—— Reflexive）；③ Red Queen Race（被迫持续投入 AI 仅维持原地）
- **半衰期量化**：信号半衰期已从 pre-algo 时代的 5-7 年压缩至 **18 个月**；单调文化均衡下纯 alpha 恒为零
- **可观测同质性度量**：IV（云算力成本冲击）、LLM 发布时点的交错 DID、持仓 PCA / 交易同步性 / 文本方法相似度三种识别方法
- **对本项目启示**：① 首批 3 策略（打板/多因子/事件驱动）的 alpha 衰减监控应预期 18 个月半衰期而非传统 5-7 年，CUSUM 参数 k/h 可能需更激进；② Performative Erosion 提示执行层应避免可预测模式（如固定时间下单），与 41 号买入流分批时序随机化设计一致；③ Red Queen Race 提示项目需持续迭代 alpha 源（CAND 候选库治理），非"一次建好永久有效"
- **登记为远期候选**：MVP 阶段维持 §5.4 CUSUM/PSI 症状监控；Phase 2+ 评估是否引入半衰期建模做主动 alpha 退役管理

#### 5.5.2 双曲衰减因子拥挤度模型（Lee 2025-12，arXiv:2512.11913）

[Lee 2025-12, "Not All Factors Crowd Equally: Modeling, Measuring, and Trading on Alpha Decay"](https://arxiv.org/abs/2512.11913)（KAIST）从博弈论 Nash 均衡推导因子 alpha 衰减的具体函数形式：

- **双曲衰减公式**：α(t) = K/(1+λt)，K 为 alpha 容量、λ 为策略发现速率。8 个 Fama-French 因子（1963-2024）实证：动量因子双曲衰减拟合 R²=0.65，优于线性(0.51)和指数(0.61)
- **因子分类洞察**：**机械因子**（动量、反转）符合双曲衰减模型；**判断型因子**（价值、质量）不符合——印证"进入壁垒"分类（机械因子易复制→快速拥挤→双曲衰减；判断型需主观判断→慢拥挤→不衰减）
- **crowding 预测尾部风险而非均值**：拥挤的反转因子崩盘概率高 1.7-1.8 倍；拥挤的动量因子崩盘概率低(0.38 倍)——**crowding 可作风控信号而非 alpha 生成信号**
- **2015 后加速**：crowding 与因子 ETF 增长相关(ρ=-0.63)
- **对本项目启示**：① 打板（机械因子类）预期双曲衰减，需监控 λ 估计值变化做主动退役；② 多因子（判断型+机械型混合）需分因子类型监控——价值/质量因子衰减慢可长期持有，动量/反转类需定期刷新；③ crowding 信号应接入 35 号回撤 Protocol 作风控降仓触发器（拥挤→崩盘概率↑→预防性减仓），而非用作 alpha 方向信号；④ 与 §5.4 CUSUM 互补——CUSUM 监控相关性症状，Lee 模型监控拥挤根因
- **登记为远期候选**：MVP 阶段不实现双曲衰减拟合（需足够长的实盘 track record 估 λ）；Phase 2+ 首批 3 策略实盘 12 月后，用 Lee 双曲模型拟合各策略 alpha 衰减曲线，机械型策略 λ 做退役触发指标

## 6. 待裁定

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| block size 自动选择校验 | Patton-Politis-White 自动算法（§3.2）已定，需验证其在打板收益率序列上的输出是否落在 10-21 合理区间（21 天为 Morwane 月度范式先验上限，打板 1-3 天持仓或更短） | 首轮验证后看 b.star 输出 + CI 宽度 |
| DCC-GARCH 第二阶段引入时机 | 静态分层首轮验证完成后，若需时序细节（相关性何时飙升）则引入 | 首轮 3 对验证完成后 |
| 情绪周期定位器准确率 | BM-SEL-23-B 错判污染分层标签（[30 §6.3](30_multi_strategy_concurrency.md)） | G21 情绪周期×交易决策评估后 |
| 打板实盘样本量 | 容量小、首批 track record 短，回测-实盘一致性待验 | 首批 3 个月实盘后复核 |
| CUSUM 漂移监控参数 | k=0.5σ / h=4σ 为 MathAndMarkets 2026-02 经验值（Sharpe~1 策略），需在 A 股打板策略对上标定（打板波动更大，h 可能需调高） | 首批 3 个月实盘漂移监控后 |
| >0.6 触发后的合并/降权规则 | 重新审视清单已定，但合并为单 sleeve 的具体规则待 G11 | G11 第二批次讨论 |
| deflated-alpha 工具 vendor 评估（v1.6.0） | [deflated-alpha v0.3.0](https://github.com/0scarito/deflated-alpha) 是单作者 3 commits 项目，2026-07-26 发布，MIT 许可。需评估：① 直接 pip 依赖（升级风险）② fork 到项目内（维护成本）③ vendor 拷贝源码（许可证合规）。考虑项目"个人+100%AI 开发"属性，倾向 vendor 拷贝 + 保留上游同步机制 | 首轮过拟合检测施工前 |
| effective trials 估计器选择（v1.6.0） | [dsr.marketmaker.cc 2026-07](https://dsr.marketmaker.cc/paper.pdf) controlled study 实证同一 trial matrix 上 5 个标准估计器分歧达两个数量级（1.6 到 370.0）：在最小估计下 deflation 近乎失效，在最大估计下策略几乎都 fail。deflated-alpha v0.2.0 默认用 N̂=ρ̄+(1−ρ̄)·M（线性相关估计），但 ρ̄ 本身可被 overfit（M not much smaller than T 时相关矩阵 ill-conditioned） | 首轮过拟合检测后，看 effective N 估计区间是否跨越 verdict 临界 |
| PBO/CSCV block 数 S 选择（v1.6.0） | deflated-alpha 默认 S=16 → C(16,8)=12870 组合；[CSDN 2026-03](https://blog.csdn.net/2501_92877300/article/details/150304073) 建议 n_subsets=max(1000, 10×|Θ|)。本项目 5 候选策略参数空间小，S=16 可能过细（组合爆炸但每块样本少）；需在 T=2020-2026 日度数据（~1500 交易日）上标定 S，使每块 ≥30 交易日 | 首轮过拟合检测后 |
| 四家 verdict 不一致时的决策规则（v1.6.0） | deflated-alpha 案例 (b) 显示 DSR pass + SPA pass + PBO fail——此时应 fail（PBO 抓住过拟合）。但若 DSR pass + PBO pass + SPA fail 呢？首轮以"任一 fail 即不上线"保守策略，但可能误杀真 edge 策略 | 首轮 3 策略验证后看 verdict 不一致频率 |

## 7. 待定问题

| 开放问题 | 出处 | 决策状态 |
|---|---|---|
| block-bootstrap 引擎复用 backtest/walk_forward 还是新建 | 本 spec §3.2 | 待施工时核查现有 bootstrap 工具 |
| 情绪周期分层与 regime 12 态分层是否需双跑 | 本 spec §3.1② / [30 §6.5](30_multi_strategy_concurrency.md) | 首轮只跑情绪周期，regime 分层待评估 |
| **情绪周期定位器准确率敏感性** | §3.1② 分层 ρ 假设 BM-SEL-23-B 正确分类每日 regime；若误判率 20%，主升态混入冰点态日期→per-regime ρ 交叉污染偏高 | 定位器准确率验证后做敏感性分析（人为注入 10%/20%/30% 误判，观察 ρ 估计偏移）；若 ρ 偏移>0.05 则需在 §3.1② 加 robustness caveat |
| 尾部相关性（EVT）是否纳入 G07 验证 | [MOD-PA-004](../../../03_modules/_domain_portfolio_alloc/strategy_correlation_gate/blueprint.md) 门禁已有 tail_correlation 维度 | 首轮不做，门禁已覆盖 |
| **PBO/CSCV 与 §3.2 block-bootstrap 的关系**（v1.6.0） | §3.2 stationary block-bootstrap 重采样策略对算相关性 CI；PBO/CSCV 内部也用 stationary bootstrap（White RC/Hansen SPA）重采样整个 trial matrix 算 best-performance null。两者同源（Politis-Romano 1994）但应用场景不同——是否复用同一引擎实例？还是 deflated-alpha 内部独立实现？ | 施工时核查 deflated-alpha 内部 bootstrap 实现与项目 block-bootstrap 引擎是否可共享 |
| **effective N 估计器分歧的处理**（v1.6.0） | [dsr.marketmaker.cc 2026-07](https://dsr.marketmaker.cc/paper.pdf) 实证 5 估计器在同一 trial matrix 上分歧达 1.6~370.0（两个数量级）。若 effective N=1.6 则 deflation 近乎失效（任何 Sharpe 都 pass），若 =370 则几乎所有策略 fail。决策需选 ① 点估计（哪个估计器？）② robustness band（min~max 都 pass 才通过）③ deflated-alpha v0.2.0 默认 N̂=ρ̄+(1−ρ̄)·M | 首轮 3 策略过拟合检测后，看 5 估计器在打板/多因子/事件驱动 trial matrix 上的分歧范围 |
| **策略组合正交性维度的可操作定义**（v1.6.0） | §3.1⑤ 第 7 部分定义三正交维度（趋势方向/执行时机/风险大小），但"维度"如何量化验证？选项：① 定性映射（5 策略 → 3 维度的设计矩阵，检查每列≥1 策略）② 量化分解（PCA/因子分析，看主成分数 vs Neff）③ 与 §3.1⑤ Neff 互验（Neff≥3 即≥3 正交维度） | 首轮 5 策略验证后，看 Neff 与正交性维度判定是否一致 |
| **参数搜索 history 的留存**（v1.6.0） | deflated-alpha audit() 要求传入全部 N 次试探的 T×N returns matrix（不是仅 winner）。但项目开发流程是否记录所有"试过但未采用"的参数组合 returns？若只保留 winner，audit 无法运行。需建立参数搜索 history 留存规范（每策略开发日志记录 N 次试探的 returns matrix） | 首轮过拟合检测施工前，建立开发日志规范 |
| **deflated-alpha 与 A 股 T+1 / 不能做空约束的适配**（v1.6.0） | deflated-alpha 假设策略 returns 可自由多空，本项目 T+1 + 不能做空。returns matrix 本身不受影响（returns 是已实现的），但 DSR/PBO 的"零技能 null"假设可能偏——A 股做多 only 的零技能策略 Sharpe 分布与多空对称分布不同 | 首轮验证后看 DSR/PBO verdict 是否与 A 股市场直觉一致 |

## 8. 引用

### 8.1 相关设计备忘
- [20_first_batch_strategies.md](20_first_batch_strategies.md) §2.5 差异化矩阵（G07 输入）、§2.6 选股池交集（>0.6 审视清单③）、§4.4 honest split（数据区间）
- [30_multi_strategy_concurrency.md](30_multi_strategy_concurrency.md) §1.3 情绪周期隐形驱动、§6.2 施工前必做（本 spec 出处）、§6.3 情绪周期定位器准确率、§6.5 灰度软分配
- [00_index_trading_decision.md](00_index_trading_decision.md) §3 G07 讨论框架

### 8.2 depgraph 模块
| 模块 | blueprint_id | path | 本 spec 关系 | build_status |
|---|---|---|---|---|
| StrategyCorrelationGate | MOD-PA-004 | `src/zephyr/pf_alloc/core/strategy_correlation_gate.py` | 运营级门禁（消费本验证产出，0.85/0.90） | production |
| CorrelationAnalyzer | MOD-L02-005 | `src/zephyr/factor/analysis/correlation_analyzer.py` | Spearman 因子相关（扩展到策略级） | production |
| 策略相关性矩阵计算 | — | 待登记 | Pearson/Spearman 策略两两矩阵（含数据预处理 pipeline） | proposed |
| 组合层 Neff 引擎 | — | 待登记 | 特征值分解 (Σλ)²/Σλ² | proposed |
| stationary block-bootstrap 引擎 | — | 待登记（先核查 backtest/walk_forward） | multivariate 同步重采样，Patton-Politis-White 自动 block size，2000× | proposed |
| 情绪周期分层标签器 | — | 待登记（消费 BM-SEL-23-B） | 4+1 阶段打标签 | proposed |
| DCC-GARCH 引擎 | — | 待登记（第二阶段，arch 库） | 时变相关性 H_t=D_t R_t D_t | proposed（第二阶段） |
| 过拟合检测引擎 | — | 待登记（v1.6.0，集成 deflated-alpha v0.3.0） | audit() 一次运行 DSR+PBO/CSCV+Harvey-Liu haircuts+White RC/Hansen SPA，输出 verdict + PDR/PSI/DFR 辅助 | proposed |

### 8.3 开源实证参考（2026）
- [Morwane/multi-strategy-alpha-book](https://github.com/Morwane/multi-strategy-alpha-book)：block-bootstrap 2000×（21-day blocks），risk-throttle Sharpe 90% CI [+1.01, +1.87]，sleeve-correlation full-sample +0.04、rolling 126-day 低——§3.2 block-bootstrap 2000× 与 §3.1② 分层的直接范式来源
- [Susan Potter — Bootstrap Methods for Strategy Robustness 2026-05](https://www.susanpotter.net/quant/bootstrap-methods-strategy-robustness/)：论证 naive i.i.d. bootstrap 破坏 autocorrelation/volatility clustering/cross-sectional correlation，block-bootstrap 保留三者；multivariate stationary bootstrap 实现参考——§4.1 拒绝 naive、§3.2 选 stationary block-bootstrap 依据
- [QBase_v2.5 PORTFOLIO.md 2026-04](https://github.com/S1mon-code/QBase_v2/blob/main/docs/PORTFOLIO.md)：组合适配检查（相关性 <0.40、边际 Sharpe >0 即 SR_candidate > ρ×SR_portfolio、两两矩阵标记 ≥0.40）——§3.1①③ 阈值对照
- [tickerly — Diversify Trading Strategies 2026-05](https://tickerly.net/how-to-diversify-trading-strategies-for-better-performance/)：<0.3 标准、>0.5 显著共享风险；equicorrelated SR_parallel = √(N/(1+(N-1)ρ))·s；stress-period correlation spikes——§3.1③ 阈值对照与相关性破坏分散化的数学依据
- [marketmaker.cc — Cascade Strategies 2026-03](https://marketmaker.cc/en/blog/post/cascade-strategies-orchestration/)：SR_parallel 公式 + 高 ρ 摧毁 √N 分散收益——§3.1③ >0.6 重新审视的数学动机
- [Soloviov — Recovering Time-Varying Correlation with DCC-GARCH 2026-07](https://dcc-correlation.marketmaker.cc/paper.pdf)：受控合成数据实证 DCC 跟踪相关性路径危机窗口 MAE=0.028 vs 静态 0.208（7 倍），静态协方差危机期 VaR 违规率 0.111（2.2 倍名义 0.05），DCC 保持 0.063；DCC 参数可扩展（d=50 仅 152 参数 vs BEKK 6275）——§3.2/§4.4 DCC-GARCH 第二阶段增强依据
- [marketmaker.cc — DCC-GARCH Dynamic Correlations 2026-07](https://marketmaker.cc/en/blog/post/dcc-garch-dynamic-correlation-crypto)：相关性是带聚类和 regime 的时间序列，静态标量是多变量版"假设常数波动率"错误；DCC 与 copula 互补（DCC 给时变整体矩阵，copula 给静态尾部）——§4.4 静态 vs DCC 论证 + §3.2 copula 边界
- [clawrxiv 2604.01458 — DCC 低估 VaR 18% 及 MS-DCC 修正 2026-04](https://www.clawrxiv.io/abs/2604.01458)：60 组合 2000-2025 实证标准 DCC 在 regime 转换期 VaR 违规超名义 18.3%，Markov-switching DCC 达 97.5% 覆盖 vs 82.7%；regime 识别滞后是 DCC 失败主因——§3.2 拒绝 MS-DCC（过重）+ §4.4 情绪周期分层覆盖 DCC 转换期弱点的依据
- [Patton-Politis-White (2009) — Automatic Block-Length Selection](https://mathweb.ucsd.edu/~politis/PAPER/SBblockCORRECTION.pdf)：自动最优 block size 算法（R `b.star`），估计值在真实最优 90%-110%，N=800 时 RMSE 较 N=200 减半——§3.2 替代固定 21 天的数据驱动 block size 依据
- [metricgate — Choosing a Resampling Scheme 2026-06](https://metricgate.com/blogs/choosing-a-resampling-scheme-time-series/)：四方案对比（block/stationary/sieve/dependent wild），stationary bootstrap（Politis-Romano）随机化 block length 保证平稳性、对单一 block-length 不敏感；naive IID 在 AR(1) ϕ=0.7 低估标准误至真值 40%——§3.2 stationary bootstrap 选用 + naive 拒绝依据
- [tsbootstrap — Multivariate Bootstrap: Keeping Series in Step 2026-07](https://tsbootstrap.readthedocs.io/en/latest/tutorials/multivariate_var.html)：行重采样保留同期相关性（"resample whole rows, contemporaneous relationship carried along untouched"），block length 默认 Politis-White 自动选择——§3.2 multivariate/paired 同步重采样施工细节依据
- [SignalY block_bootstrap 2026-02](https://r-packages.io/packages/SignalY/block_bootstrap)："For multivariate series, blocks are sampled synchronously across all variables to preserve cross-sectional dependence. This is critical when bootstrap samples are used to construct confidence intervals for statistics that depend on the joint distribution"——§3.2 各自独立重采样破坏同期相关的警告依据
- [stockalpha — Effective Number of Bets 2026-02](https://stockalpha.ai/alpha-learning/effective-number-of-bets-measuring-diversification-beyond-holding-counts)：Neff=(Σλ)²/Σλ² 特征值分解衡量独立风险方向，HHI 权重版 Neff=1/Σw² 作快速 screen——§3.1⑤/§3.2 组合层 Neff 依据
- [Soloviov — How Many Correlated Signals Actually Diversify 2026](https://signal-breadth.marketmaker.cc/)：N_eff=N/(1+(N-1)ρ̄) 等相关近似受控验证——binary 信号精确（0.02% 误差），PnL stream 偏差随 β 从 -56% 到 +91%，二分法衰减相关约一半（tetrachoric）使 binary 高估分散 56%——§3.1① PnL vs binary 警告 + §3.1⑤ 等相关公式仅辅助依据
- [CSDN — 基金收益率相关系数计算 2026-03](https://ask.csdn.net/questions/9432723)：38.6% 序列非平稳→伪相关 61.2%；对数收益率统一+ADF 检验+Modified Z-score 异常值+交易日对齐四步 pipeline——§3.1①/§3.2 数据预处理强制依据
- [clawrxiv 2604.01213 — 五种分散化指标不一致 2026-04](https://www.clawrxiv.io/abs/2604.01213)：HHI/Shannon/Neff/diversification ratio/drawdown contribution 对 3/11 GICS 行业方向不一致——§3.1⑤ 多指标交叉验证依据
- [metricgate — Ledoit-Wolf Covariance Shrinkage 2026-03](https://metricgate.com/blogs/ledoit-wolf-shrinkage-covariance-matrix/)：p close to n 时样本协方差最小特征值被压至近 0（ill-conditioned），Ledoit-Wolf 闭式最优收缩强度 α 保证正定、稳定特征值——§3.1⑤ Neff 特征值分解数值稳定性前置依据
- [invistaja — Correlação no Pior Drawdown 2026-08](https://invistaja.app.br/correlacao-portfolio-quant/)：Pearson 在危机期失效（"相关性在压力期锁定上升"），应在最差回撤期测条件相关——§3.1② 情绪周期分层隐式覆盖 stress correlation 依据
- [stockalpha — Concept Drift Alarms 2026-02](https://stockalpha.ai/alpha-learning/concept-drift-alarms-for-quant-signals-detecting-when-alpha-decays)：PSI(>0.2/0.4)/CUSUM/Page-Hinkley/PELT 变点检测 + Benjamini-Hochberg FDR 多重检验校正 + 分级响应（告警→减仓→停入场→重验证）——§5.4 相关性漂移监控方法论依据
- [MathAndMarkets — CUSUM/Bayes Knowing When to Quit 2026-02](https://mathandmarkets.com/p/detecting-decay-in-real-time-when)：CUSUM S⁺ₜ=max(0, S⁺ₜ₋₁+(μ₀−xₜ)−k)，k=0.5σ/h=4σ balanced ~0.5 次/年误报，检测延迟~50 交易日（Sharpe~1）；Page-Hinkley 不需预设 μ₀——§5.4 CUSUM 参数与检测延迟依据
- [brainbytes-dev — Live Trading Monitoring 2026-08](https://lobehub.com/it/skills/brainbytes-dev-everything-claude-trading-live-trading-monitoring)：live vs backtest gap（执行滑点/数据差异/regime 变化/look-ahead 泄漏）+ drift detection + kill switch 分级——§5.4 上线后持续监控框架依据
- [deflated-alpha v0.3.0 — 0scarito 2026-07-26](https://github.com/0scarito/deflated-alpha)：MIT 许可 Python 工具，一个 audit() 接口运行四家过拟合检测（Analytical DSR+PSR+MinTRL / Combinatorial PBO-CSCV / Multiple-testing Harvey-Liu Bonferroni-Holm-BHY / Bootstrap data-snooping White RC+Hansen SPA），输出 verdict LIKELY_REAL/INCONCLUSIVE/LIKELY_OVERFIT + 各 check value/status 表格。v0.2.0 加 effective trials（DSR Appendix 3，N̂=ρ̄+(1−ρ̄)·M）。v0.1.0 DSR+PBO/CSCV+Harvey-Liu haircuts 一个接口。**案例 (b) SMA crossover on zero-drift random walk 实证 DSR=0.989 几乎被骗 + SPA p=0.019 错误显著，只有 PBO=0.782 抓住过拟合——没有单一测试充分**——§3.2 方法表 / §3.3 why 决策 / §4.5 工具集成裁定 / §5.3 过度工程审查 / §6 vendor 评估 / §8.2 depgraph 过拟合检测引擎依据
- [Soloviov — How Many Backtest Winners Survive Deflation? 2026-07](https://dsr.marketmaker.cc/paper.pdf)：DSR + Harvey-Liu haircuts + White RC controlled study。N=1000 零技能策略 naive 单检验假阳性率 1.000，DSR 降到 0.001，Harvey-Liu Bonferroni/Holm 0.057，BHY 0.007，White RC 0.022。**deflated benchmark SR₀ ≈ 1.63 年化 = 噪声天花板**。effective trials 5 估计器分歧 1.6~370.0（两个数量级），robustness band 而非点估计。regime-switching edge (3.92 SR) 下 DSR 用 raw trial count 错误拒绝（0.748<0.95），用 effective N < 144.8 才保留——§3.2 DSR effective trials / §3.3 ④ effective N 争议 / §4.5 拒绝纯解析 DSR / §7 effective N 估计器分歧处理依据
- [Soloviov — How Overfit Is Your Search? 2026-07](https://pbo.marketmaker.cc/paper.pdf)：PBO/CSCV controlled study。三 regime 实证：纯噪声 PBO=0.476±0.137、planted edge PBO=0.001、MA-crossover grid on random walk PBO=0.463。**PBO null=0.5 不是 0**（exchangeability 论证：纯噪声下 IS 冠军 OOS 等概率落任何位置），≈0.5=抛硬币完全过拟合。edge-strength sweep PBO 单调从 0.518 (zero edge) → 0.205 → 0.028 → 0.001 → 0.000 (Sharpe 3.17)——§3.2 PBO/CSCV / §3.1⑤ 报告模板第 6 部分 PBO 阈值校准依据
- [marketmaker.cc — Deflated Sharpe Ratio: Multiple Testing 2026-06](https://marketmaker.cc/pt/blog/post/deflated-sharpe-multiple-testing/)：DSR + Harvey-Liu haircuts + White RC 假阳性率对比表（数字同上 Soloviov DSR 条）+ 1000 零技能策略 best Sharpe 1.63 年化——§2.2 核心问题多重检验问题 / §3.3 ① 必要性论证依据
- [marketmaker.cc — Probability of Backtest Overfitting 2026-07](https://marketmaker.cc/en/blog/post/probability-backtest-overfitting-pbo)：PBO null=0.5 不是 1 的语义澄清。PBO ≈ 0.5 = 抛硬币完全过拟合，PBO ≈ 0 = 选择过程可信。三 regime 对照表（zero-edge 1.98 SR→0.06 OOS PBO 0.476 / planted edge 3.73→2.34 PBO 0.001 / MA-crossover grid 0.97→0.04 PBO 0.463）——§3.2 PBO 语义依据
- [usekeel — Probability of Backtest Overfitting 2026-05](https://usekeel.io/learn/probability-backtest-overfitting)：PBO/CSCV 算法 step-by-step（T 行分 S=16 块，C(16,8)=12870 对称 IS/OOS 划分，IS 冠军 OOS 相对位 ω=rank_OOS/(N+1)，logit(ω)<0 即落入下半场，PBO=该事件频率）。rank-based 抗 regime shift。PBO<0.5 better than chance、<0.1 strong signal、>0.5 actively perverse——§3.2 PBO/CSCV 算法描述依据
- [Bailey-López de Prado — Deflated Sharpe Ratio 2014](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2465675)：DSR 原始论文。PSR[SR*] 公式（含 skewness γ₃、kurtosis γ₄ 修正），E[max SR] 极值理论近似，MinTRL 最小 track record length。N 次独立试探假设，Appendix 3 effective trials 修正——§3.2 DSR 多重检验校正依据
- [Bailey-Borwein-López de Prado-Zhu — Probability of Backtest Overfitting 2017](https://scispace.com/pdf/the-probability-of-backtest-overfitting-4ublh83xkm.pdf)：PBO/CSCV 原始论文（JoCF）。combinatorially symmetric cross-validation 框架，model-free nonparametric，rank-based。PBO null=0.5 by exchangeability——§3.2 PBO/CSCV 依据
- [Harvey-Liu — Backtesting 2015](https://www.stat.berkeley.edu/users/aldous/157/Papers/harvey.pdf) / [Practical Applications 2016](https://faculty.fuqua.duke.edu/~charvey/Media/2016/Practical_applications_backtesting.pdf)：Harvey-Liu haircuts 原始论文（JPM 42(1)）。t=SR√T 链接，Bonferroni/Holm (FWER) + BHY (FDR) 三种多重检验校正，反推 haircut Sharpe。**反对固定 50% haircut**—— haircut 应非线性，modest SR + many trials → haircut 到 0，outstanding SR + few trials → 小 haircut——§3.2 Harvey-Liu haircuts 依据
- [White — Reality Check for Data Snooping 2000](https://www.jstor.org/stable/3003178) / [Hansen — Test for Superior Predictive Ability 2005](https://www.tandfonline.com/doi/abs/10.1198/073500104000000106)：White RC + Hansen SPA 原始论文。stationary bootstrap 重采样整个 trial matrix 联合分布，每 trial recenter 到自身 mean 满足 null by construction。Hansen SPA 加 studentization + consistent recentering 防 poor high-variance alternatives 主导——§3.2 White RC + Hansen SPA 依据
- [mental-momentum.ai — Combined Trading Signals and Overfitting Risk 2026-06](https://mental-momentum.ai/)：堆叠相关指标（RSI + Stochastic）产生多重共线性，提供冗余数据而非独立信号确认。穷举指标组合测试保证高回测过拟合概率。ML 喂原始价格持续优于喂显式技术指标。有效指标组合须捕捉数学正交的市场维度（趋势方向/执行时机/风险大小）。DSR 和交叉验证是测量真实 alpha 的高级统计框架——§2.2 正交维度问题 / §3.1⑤ 报告模板第 7 部分正交性验证依据
- [dhawal.org — Statistical Validation: Avoiding the Curve-Fit Trap 2026](https://dhawal.org/)：PBO 阈值校准（PBO ~0 稳健 / ~0.5 抛硬币高度过拟合 / >0.5 严重过拟合）。W_train/W_test 比率 4-10 是机构共识——§3.1⑤ 报告模板第 6 部分 PBO 阈值依据
- [digitalninjasystems — Overfitting in Backtesting 2026-05-30](https://digitalninjasystems.com/)：PDR=(IS_SR−OOS_SR)/IS_SR，PDR>0.5 严重过拟合；PSI=Best_SR/Avg_SR，PSI>3.0 过拟合；DFR=N_obs/N_params。胜率超 70% 或 PF 超 3.0 需极端怀疑。70% 零售回测盈利策略前向测试变亏损——§3.1⑤ 报告模板第 6 部分 PDR/PSI/DFR 依据
- [backtrex — Overfitting in Backtesting 2026-05](https://backtrex.com/en/blog/overfitting-backtesting-detect-prevent)：trades-to-parameters ratio ≥30:1 机构共识。Sharpe >3 backtest 可疑。IS/OOS 退化 >50% 警告。3 参数策略需 ≥90 trades——§3.1⑤ 报告模板第 6 部分 DFR 阈值依据
- [CSDN — PBO 三维交叉验证 2026-03](https://blog.csdn.net/2501_92877300/article/details/150304073)：PBO 非贝叶斯后验概率而是经验性拒绝率。三重脆弱性（子样本构造偏差/平稳性幻觉/搜索空间覆盖不足）。PBO + SRD + DSR 三维交叉验证矩阵（PBO n_subsets≥1000 window≥6M <0.10 警戒线 / SRD 滚动 12M 步长 1M 斜率<−0.03/年 / DSR 有效独立策略数 K DSR>1.0 显著）。工程参数 n_subsets=max(1000, 10×|Θ|)、window=floor(0.3×T)、n_perm=500——§3.2 PBO+SRD+DSR 三维交叉验证矩阵 / §3.3 依据
- [dmitridefreitas — Deflated Sharpe Ratio in Practice 2026-07](https://dmitridefreitas.com/papers/Deflated-Sharpe-Ratio-Working-Paper.pdf)：DSR 实战 working paper。N=200 零技能策略 best annualized SR=2.12，naive PSR=0.9999，DSR=0.81（低于 0.95 阈值）。DSR 是"对自己施加的纪律"——N 和 V 只有研究者知道——§3.2 DSR 实战数值依据
- [Keystone — Empirical Asset-Pricing Research Framework 2026-06](https://github.com/pancakes9798/Keystone)：实现 López de Prado validation stack（CPCV + DSR + PBO）。结论：no in-scope signal reliably beats 60/40 on risk-adjusted net-of-cost OOS basis（SPIVA ~90% active managers 不及 benchmark）——§3.3 ① 必要性论证（即使有完整 validation stack，多数策略仍 fail）依据
- [backtest-audit — Aliipou 2026-05](https://github.com/Aliipou/backtest-audit)：DSR + PBO + Monte Carlo permutation + walk-forward OOS + regime-conditional audit + robustness stress，输出 PASS/WARN/FAIL verdict。8 risk components——§3.1⑤ 报告模板第 6 部分 verdict 三态设计参考
- [KinSushi/backtest-overfitting-lab 2026-06](https://github.com/KinSushi/backtest-overfitting-lab)：DSR/PBO/Reality Check/SPA battery。零第三方依赖（Python 标准库 only），UTF-8 显式编码，cwd-independent path——§4.5 vendor 评估参考（替代 deflated-alpha 的备选）
- [Student One Research — The Full Menu: Every OOS Test 2026-06](https://dashboard.studentone.tech/blog/out-of-sample-tests-counter-overfitting-menu/)：4 种过拟合失败模式（参数/选择/泄漏/路径依赖）× 9 门禁分类法（holdout/walk-forward/purged K-fold/PBO/Romano-Wolf/SPA/MC block-bootstrap/cluster stability/FDR）——§5.3 失败模式覆盖边界分类依据：G07 覆盖①④、②③归策略开发者

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G07 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 骨架→active 回填 | 5 项讨论要点逐项裁定：①两两矩阵 Pearson+Spearman 双版本 ②情绪周期 4+1 分层 ③>0.6 战略级重新审视（与门禁 0.85/0.90 互补非冲突）④数据区间 2020-2026 + 阶段样本量标注 ⑤报告模板四部分；方法 why 决策（block-bootstrap 2000×/21-day，Morwane+Susan Potter 依据）；标待施工（门禁 MOD-PA-004 已 production，计算模块待建）；过度工程审查（2000× 非过重，降级路径+过度参数化规避）；2026 开源实证（Morwane/Susan Potter/QBase/tickerly/marketmaker） |
| 2026-08-10 | 1.1.0 | 算法深化（2026-08 最新实践审查） | §3.2 方法表扩充：DCC-GARCH（时变相关性，Soloviov 2026-07 实证跟踪误差差7倍）列第二阶段增强、Patton-Politis-White 自动 block size 替代固定21天、Markov-switching DCC 拒绝（过重，clawrxiv 2026-04 实证 MS-DCC 修正转换期低估18%）、copula 拒绝（门禁 EVT 已覆盖尾部）、tapered block bootstrap 备选；§4.4 新增静态 vs DCC-GARCH 替代方案裁定；§6 待裁定更新（block size 自动校验 + DCC 引入时机）；§8.3 加 Soloviov/metricgate/clawrxiv/Patton-Politis-White 引用 |
| 2026-08-10 | 1.2.0 | 施工流程/算法补全（伪相关防控+组合层） | ①新增数据预处理 pipeline（对数收益率+ADF+Modified Z-score+交易日对齐，CSDN 2026 实证防 61.2% 伪相关）+ Soloviov 警告（禁用 binary 信号相关，必须 PnL stream，二分法高估分散 56%）；⑤报告模板加组合层 Neff 特征值分解（stockalpha 2026）+ 多指标交叉验证（clawrxiv 2026 五指标 3/11 不一致）；§3.2 方法表加数据预处理 pipeline + Neff 两行；§8.2 depgraph 加 Neff 引擎行；§8.3 加 stockalpha/Soloviov signal-breadth/CSDN/clawrxiv 五指标引用 |
| 2026-08-10 | 1.3.0 | 施工致错细节补全 | §3.2 stationary block-bootstrap 明确必须用 multivariate/paired 同步重采样（同一时间 block 对 5 策略同步重采样，tsbootstrap 2026-07/SignalY 2026-02 依据），各自独立重采样破坏策略间同期相关致置信区间失效；⑤报告模板第3部分加 Fisher z-transform 参数 CI 交叉验证（参数法与非参数 block-bootstrap 互验，不一致以 block-bootstrap 为准）；§8.3 加 tsbootstrap/SignalY multivariate 引用 |
| 2026-08-10 | 1.4.0 | Neff 数值稳定性补全 | ⑤Neff 特征值分解前置 Ledoit-Wolf 收缩（5 策略高度相关时—正是本验证要检测的情况—样本相关矩阵近奇异、最小特征值≈0、特征值分解数值不稳定；Ledoit-Wolf 闭式最优 α 保证正定、稳定特征值，α 本身也是"组合相关程度"信号），metricgate 2026-03 依据；§8.3 加 metricgate Ledoit-Wolf 引用 |
| 2026-08-10 | 1.4.1 | 自洽性修正+stress correlation 显式化 | ⑤Ledoit-Wolf 自洽性说明（收缩后 Neff 偏乐观→Neff<3 判据需结合 α 共读：α 大即使 Neff≥3 也应警惕，α 小+Neff≥3 才稳健）；②情绪周期分层显式标注"隐式覆盖 stress correlation"（主升/疯狂态=高压力期，分层=条件相关=invistaja 2026-08"最差回撤期相关"结构化版）；§8.3 加 invistaja 2026-08 引用 |
| 2026-08-10 | 1.5.0 | 上线后漂移监控施工环节补全 | 新增 §5.4 相关性漂移监控（上线后持续）：CUSUM on rolling 63日 ρ（主检测器，k=0.5σ/h=4σ，MathAndMarkets 2026-02）+ PSI（辅助，>0.2/0.4，stockalpha 2026-02）+ Page-Hinkley（探索性备选）+ 分级响应（告警→减仓→停入场→重验证，复用 deadman/reconciler 基础设施）+ Benjamini-Hochberg FDR（30 监控点）；§5.2 第三阶段从"一次性复核"升级为"启动持续监控"；§6 加 CUSUM 参数标定待裁定；§8.3 加 stockalpha drift/MathAndMarkets CUSUM/brainbytes live monitoring 引用 |
| 2026-08-10 | 1.5.1 | 结构审计修正 | ⑤Neff 报告模板从单段文字墙拆为 5 子 bullet（公式/等相关近似/数值稳定性前置/α双重用途/自洽性说明，v1.2.0+1.4.0+1.4.1 三轮增量编辑累积结构债）；新增 §4.4 静态 vs DCC-GARCH 替代方案（v1.1.0 修订记录声称已加但实际内容在 §3.2 方法表，补齐结构一致性）；§8.2 depgraph block-bootstrap 行加"multivariate 同步重采样"（与 §3.2 一致） |
| 2026-08-10 | 1.5.2 | 依赖风险识别 | §7 加"情绪周期定位器准确率敏感性"待定问题（§3.1② 分层 ρ 假设 BM-SEL-23-B 正确分类每日 regime；误判率 20%→per-regime ρ 交叉污染偏高；需定位器准确率验证后做敏感性分析：人为注入 10%/20%/30% 误判观察 ρ 偏移，>0.05 则加 robustness caveat） |
| 2026-08-10 | 1.6.0 | 过拟合检测算法施工环节补全（2026-07 最新研究整合） | §2.2 核心问题扩展（多重检验/过拟合检测/正交维度三问题）；§3.1⑤ 报告模板新增第 6 部分（过拟合检测矩阵 DSR+PBO+OOS 退化斜率+PDR/PSI/DFR+verdict）与第 7 部分（策略组合正交性验证，趋势方向/执行时机/风险大小三正交维度）；§3.2 方法选型表补 8 行（DSR 完整版/PBO-CSCV/OOS 退化斜率/PDR-PSI-DFR/Harvey-Liu haircuts/White RC+Hansen SPA/deflated-alpha v0.3.0 工具/PBO+SRD+DSR 三维交叉验证矩阵）；新增 §3.3 过拟合检测算法 why 决策（必要性/算法分层/与情绪周期分层正交/effective trials 争议/与漂移监控关系）；新增 §4.5 纯解析 DSR vs deflated-alpha 工具集成替代方案；§5.1 系统上限加过拟合检测工作量；§5.2 演进路径加过拟合检测为施工前必做；§5.3 过度工程审查加 deflated-alpha 工具集成不构成过度工程论证；§6 待裁定加 4 项（deflated-alpha vendor 评估/effective trials 估计器/PBO-CSCV block 数 S/四家 verdict 不一致决策规则）；§7 待定问题加 5 项（PBO 与 block-bootstrap 关系/effective N 估计器分歧/正交性维度可操作定义/参数搜索 history 留存/deflated-alpha 与 A 股 T+1 适配）；§8.2 depgraph 加过拟合检测引擎行；§8.3 开源实证参考加 12 条（deflated-alpha v0.3.0/Soloviov DSR & PBO controlled studies/marketmaker DSR & PBO/usekeel PBO/Bailey-López de Prado DSR/Bailey-Borwein-López de Prado-Zhu PBO/Harvey-Liu haircuts/White RC+Hansen SPA/mental-momentum/dhawal/digitalninjasystems/backtrex/CSDN PBO 三维/dmitridefreitas DSR 实战/Keystone/backtest-audit/KinSushi）。整合 2026-07 deflated-alpha v0.3.0 四家过拟合审计工具与 DSR/PBO controlled studies 实证 |
| 2026-08-10 | 1.6.1 | 引用去重+scope 边界系统化 | §8.3 tickerly 重复引用合并（v1.6.0 外部编辑引入的重复条目）；§4.5 KinSushi 孤儿引用修复（标注 §4.5 但 §4.5 未提及→加 KinSushi 作 deflated-alpha 零依赖备选）；§5.3 新增失败模式覆盖边界（Student One 2026-06 四模式分类法：G07 覆盖①选择过拟合+④路径依赖、②参数过拟合+③泄漏归策略开发者 20 §4.4），将原 ad-hoc"不做"列表系统化为②③范畴或①④冗余变体；§8.3 加 Student One 引用 |
| 2026-08-10 | 1.7.0 | 因子衰减与拥挤度建模（2026-08 最新理论研究） | §5.5 新增因子衰减与拥挤度建模远期候选——① Meng & Chen 2026-05 arXiv:2605.23905 Alpha半衰期定理（NYU，三大衰减通道：Signal Crowding/Performative Erosion/Red Queen Race，半衰期从5-7年压缩至18个月，13F机构组合趋同度+42%）；② Lee 2025-12 arXiv:2512.11913 双曲衰减因子拥挤度模型（KAIST，博弈论Nash均衡推导α(t)=K/(1+λt)，动量因子R²=0.65优于线性/指数，机械因子符合双曲衰减而判断型因子不符合，crowding预测尾部风险而非均值→作风控信号非alpha信号）。与§5.4 CUSUM/PSI症状监控互补——从"症状监控"到"根因建模"的演进路径。登记为远期候选，MVP维持CUSUM/PSI，Phase 2+实盘12月后评估双曲衰减拟合 | 用户要求全网搜索2026-08-08最新研究+选项之外更好算法。因子衰减与拥挤度是相关性漂移的根因，此前§5.4仅监控症状（CUSUM/PSI），缺乏根因理论模型。Meng半衰期定理+Lee双曲衰减填补"为什么相关性会漂移"的理论空白，且Lee的"crowding预测尾部风险"洞察与35号回撤Protocol可直接联动（拥挤→崩盘概率↑→预防性减仓） |
| 2026-08-12 | 1.7.1 | 作战地图环节映射补强——锚定 BM-BT-05-I 组合级过拟合检测（§3.1⑤ 报告模板末映射块：第 6 部分过拟合检测矩阵 DSR/PBO/PDR/PSI/DFR+verdict + 第 7 部分正交性验证承载） | 语义已覆盖但正文未显式编号的环节锚定到承载小节，实现环节级可追溯；不改既有正文 |
| 2026-08-15 | 1.7.2 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-04）——重复信息真源+指针化 4 处：§3.2 deflated-alpha 行 effective trials 并指 DSR 行、§3.3① naive 误报引文并指 §2.2、§3.3② SMA 案例数值并指 §3.2/§8.3、§3.3④ 估计器分歧引文并指 §3.2、§8.3 marketmaker DSR 条假阳性率数字并指 Soloviov 条 | 8 类扫描 5 处均为类别 3（重复信息 ≥3 处）；参数/阈值/公式/裁定/BM 锚点/跨文档链接零丢失 |
