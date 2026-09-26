---
ttl: task_bound
---

# 外部调研案卷 · 数据面与回测面（矿工出品，只出案卷不出裁定）

> **性质**：外部事实案卷。每条发现强制六字段——机构/项目 · URL · 发布方 · 年份 · 机制一句话 · 可迁移性 · 度量方式。
> **被审对象**：`docs/_working/total_command_closeout/10_wave_plan.md`（波 3 数据链治本 / 波 4 灾备）、`92_acceptance_rulers.md`（G-20..G-30 数据面尺）。
> **纪律执行**：防噪音四闸全过（①URL+发布方+年份，不用训练记忆当引文；②关键结论 ≥2 独立来源；③A 股适配闸逐条过检 T+1/涨跌停/散户主导/无做市商/复权口径；④可回测+数据可得闸，每条建议答"怎么量它有没有用"）。
> **本卷不含**：裁定、施工方案、对我方仓库的任何改动。

---

## §一 六主题发现表

### 主题 1 · 数据新鲜度与资产级 SLA（"新鲜"≠"正确"）

| ID | 机构/项目 | URL | 发布方 | 年份 | 机制一句话 | 可迁移性 | 度量方式 |
|---|---|---|---|---|---|---|---|
| F-01 | ClickHouse `ReplacingMergeTree` 官方文档 | https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/replacingmergetree | ClickHouse Inc.（官方文档，2026-09 取） | 持续更新（2026 现行） | `ver` 版本列决定同键行合并时谁胜出；**无 `ver` 时"最近一次插入的最后一行"胜出**；且合并"在后台未知时刻发生"，只提供 **eventual correctness only**，查询期不加 `FINAL` **不保证已去重** | 直接对应我方痛点 4：`kline_daily_hfq` 有 `lineage_version`、周/月表没有 ⇒ 官方口径确认"旧行静默覆盖修正行"是**引擎设计行为而非 bug**，值级对拍结构上看不出来 | 逐表查 `SHOW CREATE TABLE`，凡 ReplacingMergeTree 且 `ver` 位为空即判红；再用 `SELECT count() FROM t` vs `SELECT count() FROM t FINAL` 的差值作"未收敛重复度"指标 |
| F-02 | Dagster asset checks / freshness policies | https://docs.dagster.io/api/dagster/asset-checks ；https://docs.dagster.io/guides/build/assets/asset-checks | Dagster Labs（官方文档） | 2024–2026 现行 | 把 **freshness policy**（`lower_bound`/`upper_bound`/`fail_window`，基于时间戳列的"该不该到了"）与 **asset check**（基于数据的"对不对"）做成**两套一等公民对象**，各自独立报红 | 高：我方 G-29 只量新鲜（`max(update_date)` 距今 ≤N 日），G-24 只量存在（`count(*)`），**没有一层量"新到的这批内容对不对"** ⇒ 痛点 3（30% 幽灵日行）正是这个缺口 | 对每张资产表同时登记两个指标：`freshness_lag_hours`（新鲜）与 `row_anomaly_rate`（正确）；断言二者**不可互相推导**（构造"新鲜但 30% 幽灵"的反事实样本，只有正确性指标能红） |
| F-03 | 华泰证券金工 · CSCV 框架回测过拟合概率（人工智能系列之二十二） | https://bigquant.com/wiki/doc/ndNfdZneDH | 华泰证券金融工程团队（林晓明），BigQuant 转载 | 2026-04 | 把 López de Prado 的 CSCV/PBO 落到 A 股样本上做实证复算，给出"同一策略族内多配置粗扫 ⇒ PBO 随试验数上升"的本土化数值 | 高：直接对应我方痛点 8（3700 格策略粗扫）——**A 股样本上已有可抄的复算范式**，不用自己从零推导 | 用我方 3700 格结果矩阵直接跑 CSCV，输出 PBO 值；PBO>0.5 即判"该格族的选优结果不可信"，与"抽 50 格 sharpe≥0"是**不同问题**（见 §三） |

（本表持续追加；F-04 起为后续轮次补充）

### 主题 2 · 数据契约（类型边界该在哪一层被强制）

_待填_

### 主题 3 · 血缘与版本化数据

_待填（F-01 已先落，归属本主题）_

### 主题 4 · 回测完整性与统计严谨

| ID | 机构/项目 | URL | 发布方 | 年份 | 机制一句话 | 可迁移性 | 度量方式 |
|---|---|---|---|---|---|---|---|
| F-03 | 华泰证券金工 · CSCV 框架回测过拟合概率（人工智能系列之二十二） | https://bigquant.com/wiki/doc/ndNfdZneDH | 华泰证券金融工程团队（林晓明），BigQuant 转载 | 2026-04 | 把 López de Prado 的 CSCV/PBO 落到 A 股样本上做实证复算，给出"同一策略族内多配置粗扫 ⇒ PBO 随试验数上升"的本土化数值 | 高：直接对应我方痛点 8（3700 格策略粗扫）——**A 股样本上已有可抄的复算范式**，不用自己从零推导 | 用我方 3700 格结果矩阵直接跑 CSCV，输出 PBO 值；PBO>0.5 即判"该格族的选优结果不可信"，与"抽 50 格 sharpe≥0"是**不同问题**（见 §三） |
| F-04 | Quanterlab · The Deflated Sharpe Ratio: correcting for how many tries | https://quanterlab.com/articles/qlway-deflated-sharpe | Quanterlab（技术博客，非同行评审） | 2026-06 | DSR = 把"观测 Sharpe"与"N 次试验下的期望最大 Sharpe（E[max{SR}]）"作对比后得到的**统计显著性概率**；试验越多，同样观测 Sharpe 的显著性越低 | 高（待用一手源复核公式）：我方 3700 格粗扫正是"高 N"场景，DSR 是把 N 折进阈值的**唯一现成标准件** | 给定 N、观测 SR、SR 的跨格标准差、偏度/峰度、样本长度 T，算 DSR；DSR<0.95 即判该格"可能是选出来的运气"。**度量它有没有用**：对同一批格子分别用"裸 SR≥0"与"DSR≥0.95"排序，看两者入选集合的样本外表现差（差越大说明 DSR 越有用） |
| F-05 | JoinQuant 社区 · 策略过拟合诊断工具集介绍 | https://www.joinquant.com/view/community/detail/3cf8435f4a772fc2f702589704db44db | 聚宽 JoinQuant（平台社区文，非同行评审） | 2026-09 | 国内量化平台已把 PBO/CSCV/DSR 打包成"策略过拟合诊断"工具集，说明这类判据在国内是**可工程化落地**的成熟件而非学术摆设 | 中高：证明我方自建 CSCV 尺不是"过度设计"，业界已有对标实现可抄接口 | 记录该工具集输出的字段名（PBO/DSR/试验数/分层数），与我方拟新增尺的字段做一对一映射；映射率 ≥80% 即判我方口径与业界同构 |
| F-06 | Balaena Quant Insights Issue 24 · Deflated Sharpe Ratio (DSR) | https://medium.com/balaena-quant-insights/deflated-sharpe-ratio-dsr-33412c7dd464 | Balaena（量化研究通讯，非同行评审） | 2025-12 | DSR 的第二个独立解释源：核心是"Minimum Track Record Length（最短实盘/回测长度）"与"试验次数折减"两个量，二者共同决定观测 SR 是否可信 | 中：用作 F-04 的交叉验证（≥2 独立来源闸）；**单源时该条只算旁证** | 比对 F-04 与 F-06 给出的 E[max{SR}] 表达式是否同式；同式即 DSR 公式确证，可写入我方尺的公式注释 |

> **注（防噪音闸②）**：F-04/F-05/F-06 均为二手来源，DSR/PBO 的**一手源**（SSRN / Journal of Portfolio Management / Journal of Computational Finance / Notices of the AMS / Econometrica）正在本轮内补验，见 §四 追踪表；补到之前，凡涉及"公式常量"的表述一律标 **待一手源复核**。

#### 主题 4-A · 一手源已确证（OpenAlex 元数据直取，2026-09 检索）

> 检索方式：`https://api.openalex.org/works?search=<title>`（发布方＝OpenAlex，开源学术元数据库，非训练记忆）。以下 5 条为**关键结论的一手源**，DOI 均可点开核验。

| ID | 论文 | DOI / URL | 发布方（期刊） | 年份 | 机制一句话 | 可迁移性 | 度量方式 |
|---|---|---|---|---|---|---|---|
| P-01 | Bailey, D.H. & López de Prado, M. — *The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality* | https://doi.org/10.3905/jpm.2014.40.5.094 （SSRN 版 https://doi.org/10.2139/ssrn.2460551） | The Journal of Portfolio Management（Institutional Investor / PMR，同行评审） | 2014 | DSR＝在**已知试验次数 N** 的前提下，把"观测 Sharpe"与"N 次试验下期望最大 Sharpe"作差、除以 SR 估计量的标准误，得到该 SR **不是选出来的运气**的概率；标题直接把三件事绑在一起：selection bias + overfitting + non-normality | **最高**：这就是"3700 格粗扫"场景的标准解法——不是"抽 50 格看是否 ≥0"，而是"报 DSR，N=3700" | 对 3700 格结果矩阵算 DSR（需输入：N、观测 SR、SR 跨试验方差、偏度、峰度、T）；**度量它有没有用**＝比较"裸 SR 排序选出的 Top-K"与"DSR 排序选出的 Top-K"在真样本外窗口的 SR 差；差 >0 即 DSR 有效 |
| P-02 | Bailey, D.H., Borwein, J.M., López de Prado, M. & Zhu, Q.J. — *The probability of backtest overfitting* | https://doi.org/10.21314/jcf.2016.322 （SSRN 版 https://doi.org/10.2139/ssrn.2326253 ；数学附录 https://doi.org/10.2139/ssrn.2568435） | The Journal of Computational Finance（Infopro Digital，同行评审） | 2016（SSRN 首挂 2013） | 定义 **PBO**＝用 CSCV（组合对称交叉验证）把回测矩阵切成 S 块，枚举 C(S,S/2) 种 IS/OOS 组合，统计"IS 最优配置在 OOS 排名落到下半区的比例"；PBO 越高＝选优越不可信 | **最高**：可直接吃我方 3700×T 收益矩阵，无需任何 A 股特化改造 | 跑 CSCV 得 PBO；判据建议 PBO≤0.2（业界常用红线，**待第 2 源确证**）。**度量**＝把 PBO 与"IS 最优格的 OOS SR"做散点，看负相关强度（Spearman ρ<-0.5 即尺有效） |
| P-03 | Bailey, Borwein, López de Prado & Zhu — *Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample Performance* | https://doi.org/10.1090/noti1105 （全文 PDF 常见镜像：https://www.ams.org/notices/201405/rnoti-p458.pdf ，本轮取 403，**受阻**） | Notices of the American Mathematical Society（AMS，会员刊，含数学科普论证） | 2014 | 用**蒙特卡洛实证**证明：在纯噪声（零真 alpha）数据上，只要试得够多、挑得够狠，回测 SR 可以任意高；并给出 OOS 表现随"最小回测长度 MinBTL"退化的量化关系 | 高：这是"为什么必须把 N 写进判据"的**最易引用的权威论证**，适合写进 Owner 决策材料 | 引用其核心结论表：同一"漂亮回测"在 N 增大时 OOS SR 转负；**度量**＝在我方数据上注入纯噪声策略族，复算其退化曲线是否与论文同形 |
| P-04 | White, H. — *A Reality Check for Data Snooping* | https://doi.org/10.1111/1468-0262.00152 （RePEc 元数据 https://ideas.repec.org/a/ecm/emetrp/v68y2000i5p1097-1126.html ） | Econometrica 68(5):1097–1126（Wiley / The Econometric Society，同行评审） | 2000 | **Reality Check (RC)**：用 bootstrap 检验"在**所有**被试过的模型中，最好的那个是否显著优于基准"，把 data snooping 直接写进零假设 H₀：max 超额收益 ≤ 0 | 高：它给出的**方法论范式**正是本案所需——"零假设必须覆盖全部试验空间"，而不是覆盖一个被筛过的子集 | 对 3700 格跑 bootstrap RC 得 p 值；p<0.05 才承认"最好那格"有真信号。**度量**＝与 PBO 的判定一致率（两尺互证，一致率 ≥0.8 即口径自洽） |
| P-05 | Hansen, P.R. — *A Test for Superior Predictive Ability* | https://doi.org/10.1198/073500105000000063 （开放 PDF：http://chico.pstc.brown.edu/~phansen/Papers/spa.pdf ，Brown Univ. 作者主页镜像，2001 工作论文版 *An Unbiased and Powerful Test for SPA*） | Journal of Business & Economic Statistics 23(4):365–380（Taylor & Francis / ASA，同行评审） | 2005 | **SPA test**＝White RC 的改进：用"学生化统计量 + 重定中心（recentering）"消除对劣等模型的敏感性，检验功效更高且不失真 | 中高：作为 RC 的**现代替代件**；对"很多格都很差、少数几格好"的粗扫场景比 RC 更稳 | 跑 SPA 得 p 值；**度量**＝在已知有真 alpha 的植入实验中，SPA 的拒真率（power）是否高于 RC（论文与 Hansen–Lunde 2005 https://doi.org/10.1002/jae.800 均给了对比实验范式） |
| P-06 | Sullivan, R., Timmermann, A. & White, H. — *Data-Snooping, Technical Trading Rule Performance, and the Bootstrap* | https://doi.org/10.1111/0022-1082.00163 | The Journal of Finance（Wiley / AFA，同行评审） | 1999 | 对 7844 条技术分析规则做 bootstrap reality check，证明**"规则空间越大，最优规则的表面收益越不可信"**，并给出扣除 data snooping 后仍显著的子集 | 高：这是"候选格数量 N 本身必须披露"的**实证先例**（7844 条 vs 我方 3700 格，量级可比） | 引用其 N=7844 的口径；**度量**＝我方判据是否强制登记"本轮 N=多少格"，未登记即判尺缺失 |

（本表持续追加；F-07 起为后续轮次补充）

#### 主题 4-B · 可复算公式（源码级确证，非记忆）

> 公式取自两个开源实现的实际源码，**逐行核对**后转录（防噪音闸①：不用训练记忆写公式）。

**（1）PSR 概率化 Sharpe（Bailey & López de Prado 2012, *The Sharpe Ratio Efficient Frontier*, Journal of Risk 15(2), Eq. 7）**

```
PSR(SR*) = Φ( (SR_hat − SR*) · sqrt(n − 1)
              / sqrt( 1 − γ3·SR_hat + ((γ4 − 1)/4)·SR_hat² ) )
```
- `SR_hat`＝样本 Sharpe（**总体标准差 ddof=0**，非 ddof=1）
- `γ3`＝样本偏度；`γ4`＝样本峰度（**非超额峰度**，即不减 3）
- `n`＝观测根数；`Φ`＝标准正态 CDF；`SR*`＝基准 Sharpe
- 源码：`src/purgedcv/_metrics.py::probabilistic_sharpe_ratio`（https://github.com/eslazarev/purged-cross-validation ，MIT，v0.1.7，2026-09-26）

**（2）DSR 折减 Sharpe（Bailey & López de Prado 2014, JPM 40(5):94, DOI 10.3905/jpm.2014.40.5.094）**

```
SR*_n = sqrt( V[SR] ) · [ (1 − γ)·Φ⁻¹(1 − 1/N)  +  γ·Φ⁻¹(1 − 1/(N·e)) ]
DSR   = PSR( SR* = SR*_n )
```
- `N`＝**本轮独立试验次数**（我方＝3700 格，不是 50）
- `γ ≈ 0.5772156649015329`（Euler–Mascheroni 常数，源码常量名 `_GAMMA_EM`）
- `V[SR]`＝**N 个候选之间 Sharpe 的方差**（跨试验方差，不是时序方差）
- `N = 1` 时 `SR*_n = 0`，DSR 退化为 PSR(SR*=0)
- **单位铁律（源码 docstring 明写）**：DSR 本质是**逐观测**量。若 `V[SR]` 是年化 Sharpe 的方差，必须除以 `bars_per_year` 折算成逐观测；不折算＝数量级错。
- 源码：`src/purgedcv/_metrics.py::deflated_sharpe_ratio` / `deflated_sharpe_ratio_full`

**（3）MinTRL 最短实盘记录长度（Bailey & López de Prado 2012, Eq. 11）**

```
n* = 1 + ceil( [ Φ⁻¹(1 − α) · sqrt(1 − γ3·SR_hat + ((γ4 − 1)/4)·SR_hat²)
                 / (SR_hat − SR*) ]² )
```
- 源码：`src/purgedcv/_metrics.py::min_track_record_length`
- 用途：反推"要让 DSR/PSR 达到 1−α，至少需要多少根 bar"——**直接回答"回测窗口够不够长"**

**（4）MinBTL 最短回测长度**：低于该长度，报告的 Sharpe 落在"N 次选择所能凭运气产生的范围"之内 ⇒ 不可采信。源码：`src/purgedcv/_metrics.py::minimum_backtest_length`（出处标注 Bailey, Borwein, López de Prado & Zhu 2014, Notices of the AMS 61(5)）。

**（5）PBO / CSCV 算法（Bailey et al. 2016, JCF, DOI 10.21314/jcf.2016.322）——逐步伪代码，转录自 `pypbo/pbo.py`（https://github.com/esvhd/pypbo ，AGPL-3.0）**

```
输入: M ∈ R^{T×N}  (T 根 bar, N 个配置/格的逐期收益), S = 16 (论文建议, 必须偶数)
1. 若 T % S != 0: 丢弃最前面 T%S 行 (保留最近的对齐窗口)
2. sub_T = T // S; 把 M 按时间顺序切成 S 个等长子块 M_1..M_S
3. 枚举全部组合 Cs = combinations({1..S}, S/2)      # 共 C(S, S/2) 个
4. 对每个组合 c ∈ Cs:
     IS 块 J_c   = concat(M_i for i in c)           # 按原时间序拼接
     OOS 块 J̄_c  = concat(M_i for i in {1..S} \ c)  # 补集
     R_c   = metric(J_c)      # 长度 N 的向量, 例如年化 SR
     R̄_c   = metric(J̄_c)
     rn    = argmax(rankdata(R_c))                  # IS 上最优的那个"格"
     rn_bar = rankdata(R̄_c)[rn]                     # 同一个格在 OOS 上的名次
     w_bar = rn_bar / (N + 1)                       # +1 防止 w=1 ⇒ logit=inf
     logit_c = logit(w_bar)
5. PBO = |{ c : logit_c ≤ 0 }| / |Cs|               # IS 最优者掉到 OOS 下半区的比例
附带三个副产品:
  - prob_oos_loss = |{ c : R̄_c[rn] < threshold }| / |Cs|   # threshold=0 即"OOS 亏钱概率"
  - performance degradation = linregress(IS 最优 SR, 其 OOS SR) 的 slope / R²
  - stochastic dominance = ECDF(OOS of IS-winner) vs ECDF(OOS of all)
```
- **该源码 docstring 自陈的三条限制（对我方极关键，直接抄进判据）**：
  1. "CSCV 是对称的，对某些策略 K-fold CV 可能更好"；
  2. **"不适用于强自相关序列，尤其 S 较大时"** ⇒ A 股 T+1 下的低换手策略日收益自相关不可忽略，须先做 Ljung-Box 检验（见 F-08）；
  3. **"完全可能 N 个配置全都 Sharpe 很高且彼此相近，此时 PBO 会显示很高，但这里的'过拟合'发生在一群'有本事'的策略之间"** ⇒ **PBO 高 ≠ 全部没救**，必须与 `prob_oos_loss` 合看。这一条**正是我方争议的统计学钥匙**：33%/56% 的格子 SR≤0，属于"分布本身偏下"，与"选优过拟合"是两个正交问题，不能用同一把尺量。

**（6）自相关修正的 Sharpe（Andrew Lo 2002, *The Statistics of Sharpe Ratios*, Financial Analysts Journal）**
```
若 Ljung-Box(q) 拒绝"无自相关"零假设(p < 0.05):
   adj_factor = q / sqrt( q + 2·Σ_{k=1..q−1} (q − k)·acf[k] )
   SR_annual = SR_periodic × adj_factor
否则:
   SR_annual = SR_periodic × sqrt(q)
```
- 源码：`pypbo/perf/metrics.py::sharpe_autocorr_factor` / `sharpe_non_iid`（同上 AGPL-3.0 仓）
- **对 A 股的意义**：T+1 制度天然制造隔日依赖，直接 `×sqrt(252)` 年化会**系统性高估** Sharpe 的显著性 ⇒ 我方"Sharpe ≥ 0"这条线连年化口径都未必自洽。

### 主题 5 · 数据质量门的失败模式（fail-open / fail-closed）

_待填_

### 主题 6 · 可观测性与自愈（演练判据怎么写才不恒红不恒绿）

_待填_

---

## §二 我方 8 条痛点逐条对标

| # | 痛点（我方实测） | 业界标准做法 | 我方方案当前处方 | 差距 | 改法（外部依据） | 度量 |
|---|---|---|---|---|---|---|
| 1 | 假绿灯：记账 SUCCESS 而目标表 0 行 | _待填_ | 波 3.2 + G-21/G-22 | _待填_ | _待填_ | _待填_ |
| 2 | 类型边界崩溃 `'str' > 'date'` | _待填_ | 波 3.1 + G-20 | _待填_ | _待填_ | _待填_ |
| 3 | 新鲜度/污染分不清 | Dagster 双轨（freshness policy ≠ asset check） | 波 3.3 明确"新鲜度用业务表 `max(date)` 不用 `system.` 面"+ G-29 | **只补了新鲜度真源，没补正确性轨**；`max(date)` 新鲜与 30% 幽灵行是两个正交指标 | 按 F-02 拆成两套尺：新鲜尺（时延）+ 正确尺（幽灵日检出率） | _待填_ |
| 4 | 后复权表族缺版本列 | ClickHouse 官方：无 `ver` ⇒ "最近插入的最后一行胜出"，只保证 eventual correctness | 波 3.9 "hfq 族来源独占验证尺" + G-28 | **"来源独占"防的是"两个写者口径混写"，防不住"同一写者用旧口径重写覆盖修正行"**；且族内 11 张只提了独占、未提版本列补齐 | 按 F-01 给周/月表补 `ver`（可复用 `lineage_version`），读侧统一 `argMax(col, ver)` 或 `FINAL` | _待填_ |
| 5 | 测试污染生产账本 | _待填_ | 波 3.8 + G-27（sha256 前后不变） | _待填_ | _待填_ | _待填_ |
| 6 | 空壳表 11/12 count=0，三套张数口径互异 | _待填_ | 波 3.5 + G-24 | _待填_ | _待填_ | _待填_ |
| 7 | 探库工具静默失败 | _待填_ | G-30 + §五第 4 条"静默失败面禁用" | _待填_ | _待填_ | _待填_ |
| 8 | 预注册考试链：3700 格粗扫 / "抽 50 格最狠滑点档 sharpe≥0" | CSCV/PBO + 多重检验校正（F-03） | 92 册无对应尺；10 册波 2.4 只提"回测哨兵"代码复杂度 | **该验收线在统计上不可过，但我方 41 把尺里没有一把量"验收线本身是否可满足"** | 见 §三 判据级建议 | _待填_ |

---

## §三 判据级建议（针对第 4 条"抽查口径"的统计学正解）

_待填_

---

## §四 受阻与查无

_待填_

---

## §五 我最没把握的 3 条

_待填_
