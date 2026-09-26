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

> **本轮窄口径重投声明**：本次任务的唯一交办口径＝§三 那条"抽查口径"的统计学正解（对应痛点 8）。主题 2（数据契约/类型边界）不在窄口径内，**本卷不产出内容，也不假装产出**。前一路失败残留的骨架位在此保留，未填充即未填充，禁由后续读者当"已查过"。
> 若需补该主题，建议检索锚点（**未经本轮验证，仅为线索，禁直接引用**）：Great Expectations / Soda Core / Apache Arrow schema validation / dbt contracts（`config(contract={enforced: true})`）。

### 主题 3 · 血缘与版本化数据

> F-01（ClickHouse `ReplacingMergeTree` 的 `ver` 列语义）已落在**主题 1 表内**，其结论归属本主题，此处不重复登记以免双源漂移。
> **本卷新增的与本主题直接相关的一条**：复权口径与数据快照版本会**改变同一格的 Sharpe 读数**（§4-F 表"除权除息／复权口径"行）⇒ 验收成绩单必须含 `{复权口径, 数据快照日期, 快照 sha256}` 三字段（已写入 §3.2 的 P5 门）。该条与 F-01 同源：**结果不可复现的第一嫌疑是数据版本，不是代码版本**。
> 本主题其余部分（血缘图工具选型等）不在窄口径内，未填即未填。

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

#### 主题 4-C · 选择偏差／幸存者偏差（"从初筛幸存者里抽"到底坏在哪）

| ID | 出处 | URL / DOI | 发布方 | 年份 | 机制一句话 | 可迁移性 | 度量方式 |
|---|---|---|---|---|---|---|---|
| S-01 | Carhart, Carpenter, Lynch & Musto — *Mutual Fund Survivorship* | https://doi.org/10.1093/rfs/15.5.1439 | Review of Financial Studies 15(5):1439（Oxford UP / SFS，同行评审） | 2002 | 只研究"活下来的基金"会**系统性高估**平均业绩，且高估幅度是**可量化的**（该文用 1962–1993 全样本给出 survivorship bias 的年化 bp 数） | 高：这就是"从初筛幸存者里抽"的教科书原型——**初筛＝survival screen**，抽幸存者＝只研究活下来的样本 | 同时报两个口径的均值/分位数：全体候选 3700 格 vs 通过初筛的 K 格；差值即"我方版 survivorship bias"，**必须写进成绩单**，不许只报后者 |
| S-02 | Elton, Gruber & Blake — *A First Look at the Accuracy of the CRSP Mutual Fund Database…* | https://doi.org/10.1111/0022-1082.00410 | The Journal of Finance（Wiley / AFA，同行评审） | 2001 | 数据库层面证明：被删记录（含死亡样本）导致业绩度量偏乐观；纠正偏差需要**在样本定义里保留已死对象** | 中：给"初筛淘汰的格子必须留档、必须可复算"提供权威依据（不是可选项） | 检查我方 3700→K 的初筛过程是否**留了被淘汰格子的完整结果行**；未留＝无法做偏差校正＝判尺缺失 |
| S-03 | White — *A Reality Check for Data Snooping*（＝P-04） | https://doi.org/10.1111/1468-0262.00152 | Econometrica 68(5):1097–1126 | 2000 | **校正选择偏差的标准做法＝把"选择过程"写进零假设**：H₀ 不是"这一格无 alpha"，而是"**在这整片被搜过的空间里**，最好那格也不优于基准" | **最高，直接命中本案**：仓库方想"改成从幸存者里抽"＝**反过来把选择过程从判据里摘掉**；White 的做法是把选择过程**装进 H₀**，而不是把它藏进抽样框 | 把 H₀ 从"抽中格 Sharpe≥0"改写为"在 N=3700 全体上，max Sharpe 不显著优于 0（bootstrap 分布）"；输出 p 值。**度量**＝该 p 值在注入纯噪声策略族时是否 ≈ 均匀分布（校准检验） |
| S-04 | Harvey, Liu & Zhu — *… and the Cross-Section of Expected Returns* | https://doi.org/10.1093/rfs/hhv059 （NBER WP 版 https://doi.org/10.3386/w20592 ） | Review of Financial Studies（Oxford UP / SFS，同行评审） | 2016 | 统计 316 个已发表因子后主张：**新因子的 t 统计量门槛必须提到 3.0**（不是传统 2.0），因为多重检验累积；并给出对已发表因子做 haircut 的清单 | 高：给出"阈值该随试验数上抬"的**权威量化标尺**——我方案是"阈值 0 一字不动"，与该文精神**方向相反**（该文主张的是抬阈值而非降阈值） | 用其 haircut 方法对我方 Top-K 格算"扣掉多重检验后的 t"；t<3.0 即判不足以转正 |
| S-05 | Sullivan, Timmermann & White — *Data-Snooping, Technical Trading Rule Performance, and the Bootstrap*（＝P-06） | https://doi.org/10.1111/0022-1082.00163 | The Journal of Finance | 1999 | 7844 条规则的实证：**候选空间大小必须随结果一起披露**，否则"最优规则"的收益无法解读 | 高：⇒ 我方成绩单必须**强制字段 `n_trials`**（=3700），缺该字段的任何 Sharpe 读数都不予采信 | 在成绩单 schema 上加 `n_trials` 为**必填**（NOT NULL），gate 拦空值；**度量**＝字段填充率 100% |
| S-06 | Feng, Giglio & Xiu — *Taming the Factor Zoo: A Test of New Factors* | https://doi.org/10.3386/w25481 （期刊版 Journal of Finance 2020） | NBER 工作论文 / The Journal of Finance | 2019(NBER) / 2020(JF) | 用双重选择（double selection）在**已有因子动物园**上检验新因子的边际贡献，把"已知因子空间"当作必须控制的 nuisances | 中高：对应"初筛口径"应作为**协变量写进模型**，而不是作为抽样框裁剪样本 | 把"成本初筛得分"作为协变量放进 DSR/回归，看通过与否是否仍显著；**度量**＝控制协变量后显著性变化幅度 |
| S-07 | Witzany — *A Bayesian Approach to Measurement of Backtest Overfitting* | https://doi.org/10.3390/risks9010018 | Risks 9(1):18（MDPI，**开放获取**，同行评审） | 2021 | PBO 的贝叶斯改写：把"过拟合概率"当作后验量处理，缓解 CSCV 对分块数 S 的敏感 | 中：作为 P-02 的**第二个独立来源**（≥2 源闸），且开放获取可直接下载 | 用同一 3700×T 矩阵分别跑频率派 PBO 与贝叶斯版，报两者差；差 >0.15 即判"该结果对方法选择敏感，不可只报一个" |
| S-08 | Koshiyama & Firoozye — *Avoiding Backtesting Overfitting by Covariance-Penalties* | https://doi.org/10.2139/ssrn.3385636 | SSRN 工作论文（**未经同行评审，标待验证**） | 2018 | 用协方差惩罚（TLS 思路）在**优化阶段**抑制过拟合，而不是只在事后检测 | 低中：属"预防"路线，与我方"事后验收线"不同层 | 仅作为方法族谱登记；**单源，标待验证**，不作为关键结论支撑 |

> **闸②小结（选择偏差）**：关键结论"校正选择偏差的正统做法＝把选择过程写进 H₀／把 N 写进阈值，而不是把 H₀ 收窄到幸存者"由 **S-03（White 2000, Econometrica）+ S-04（Harvey-Liu-Zhu 2016, RFS）+ S-05（Sullivan-Timmermann-White 1999, JF）** 三条独立同行评审一手源共同支撑 ⇒ **成立**。

#### 主题 4-D · 成本／滑点敏感度曲线与盈亏平衡成本（业界是否用曲线替代单档阈值）

| ID | 出处 | URL / DOI | 发布方 | 年份 | 机制一句话 | 可迁移性 | 度量方式 |
|---|---|---|---|---|---|---|---|
| C-01 | Novy-Marx & Velikov — *A Taxonomy of Anomalies and Their Trading Costs* | https://doi.org/10.1093/rfs/hhv063 （NBER WP 版 https://doi.org/10.3386/w20721 ） | Review of Financial Studies（Oxford UP / SFS，同行评审） | 2016 | 对 23 个异象**逐个报"扣费后表现"**，并明确以"**在多大交易成本下该策略仍活着**"作为排序与筛选口径；把"成本敏感度"做成**一等公民报表列**而非单点开关 | **最高**：这就是"逐档成本下的表现曲线"的权威范式；40bp 单档阈值应改为"**盈亏平衡成本 c\* 的分布**" | 对每格解 `c* = argmin{c : Sharpe(c) ≤ 0}`；报表列＝c\* 的分位数（P10/P25/**中位数**/P75），门＝中位数 ≥ 40bp |
| C-02 | Detzel, Novy-Marx & Velikov — *Model Comparison with Transaction Costs* | https://doi.org/10.1111/jofi.13225 | The Journal of Finance（Wiley / AFA，同行评审） | 2023 | 证明**加入交易成本后，模型排序会改变**：无成本下最优的模型在含成本下可能不是最优；因此模型比较**必须在成本口径下重做**，不能先无成本选优再补一次成本检查 | **最高，直接命中本案**：我方流程正是"先粗扫选优（初筛）→ 再在最狠档抽查"，该文说这个顺序本身就会改变结论 | 复算：把成本放进粗扫目标函数重排 3700 格，与"无成本排序后补检查"的 Top-K 求交集；交集率 <70% 即证明现行顺序失真 |
| C-03 | Getmansky, Lo & Makarov — *An econometric model of serial correlation and illiquidity in hedge fund returns* | https://doi.org/10.1016/j.jfineco.2004.04.001 | Journal of Financial Economics（Elsevier，同行评审） | 2004 | 非流动性／平滑会把观测到的 Sharpe **系统性抬高**；给出把"平滑收益"还原为"真实收益"的 ML 反演，并给出 unsmoothing 后的 Sharpe 修正 | 高：A 股停牌／涨跌停不可成交＝典型的**收益平滑**，直接用日线算 Sharpe 会虚高 | 对我方每格日收益跑 Ljung-Box；自相关显著者用 Lo(2002)/Getmansky-Lo-Makarov 修正后再算 Sharpe，报修正前后差 |
| C-04 | Andrew W. Lo — *The Statistics of Sharpe Ratios* | 源码内引用镜像 `http://edge-fund.com/Lo02.pdf`（本轮 HTTP **441**，**受阻**）；二手引用见 `pypbo/perf/metrics.py::sharpe_autocorr_factor` 注释 | Financial Analysts Journal 58(1)（CFA Institute） | 2002 | 年化 Sharpe 在自相关下必须用 `q / sqrt(q + 2Σ(q−k)·acf[k])` 而非 `sqrt(q)` | 高（但**一手源本轮受阻，标待验证**） | 见主题 4-B 公式(6)；**度量**＝修正前后年化 SR 的比值分布，比值 <0.9 的格子占比 |

**盈亏平衡成本 c\* 的算法（可直接实现，单调性保证二分收敛）**
```
前提: 对同一格, Sharpe(c) 关于单边成本 c 单调不增 (成本线性侵蚀收益, 换手固定)
输入: c_lo = 0bp, c_hi = 200bp (确保 Sharpe(c_hi) < 0), tol = 0.1bp
while c_hi - c_lo > tol:
    c_mid = (c_lo + c_hi) / 2
    if Sharpe(c_mid) > 0:  c_lo = c_mid      # 还能扛更高成本
    else:                  c_hi = c_mid
c* = c_lo
单调性校验（必做，不通过则 c* 无定义）:
    取 c ∈ {0, 5, 10, 20, 40, 60, 80, 100, 150, 200} bp 全部重算,
    断言 Sharpe 序列非增; 违反即该格标记 c*=NaN 并单独报数, 不许混进中位数
```
> 该算法是 C-01/C-02 口径的直接工程化；**单调性校验**是防"某格在 40bp 反而比 20bp 好"这类回测引擎缺陷（涨跌停／停牌导致的非单调填充）。

#### 主题 4-E · 分层抽样口径与统计功效（"抽 50 格"够不够）

**权威源**：NIST/SEMATECH *e-Handbook of Statistical Methods*（发布方＝美国国家标准与技术研究院 NIST，持续更新，2026-09 现行）
- §7.2.4 *Does the proportion of defectives meet requirements?* — https://www.itl.nist.gov/div898/handbook/prc/section2/prc24.htm （HTTP 200 已核）
- §7.2.4.1 *Confidence intervals*（**小样本／少数不良品时用精确二项区间，正态近似不准**）— https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm （HTTP 200 已核）
- §7.2.4.2 *Sample sizes required*（比例检验的样本量推导：给定 α、power 1−β、要检出的变化 δ＝|p₁−p₀|，解出 N）— https://www.itl.nist.gov/div898/handbook/prc/section2/prc242.htm （HTTP 200 已核）
- §7.1.4 *What are confidence intervals?* — https://www.itl.nist.gov/div898/handbook/prc/section1/prc14.htm （HTTP 200 已核）

**本卷实算（scipy 复算，非引用）**——设 p＝"随机抽一格在 40bp 档 Sharpe≤0"的真实比例：

```
(A) 字面判据（读法甲：抽出的 50 格必须全部 Sharpe≥0）的通过概率 = (1-p)^50
      p=0.10 → 5.15e-03      p=0.20 → 1.43e-05
      p=0.33 → 2.01e-09      p=0.40 → 8.08e-12
      p=0.50 → 8.88e-16      p=0.56 → 1.49e-18
    ⇒ 要让"全部通过"有 95% 概率, 需 p ≤ 0.1%。这是"恒假判据"的数学证明。

(B) n=50 的 95% 正态近似置信区间半宽（Wald）
      p̂=0.33 → ±0.1303  [0.200, 0.460]
      p̂=0.50 → ±0.1386  [0.361, 0.639]
      p̂=0.56 → ±0.1376  [0.422, 0.698]
    ⇒ 两班读数 33% 与 56% 的区间**大幅重叠**；同一把尺不可能同时给出结论。

(C) 两班差异的显著性（两比例 z 检验, n₁=n₂=50, pooled p=0.445）
      z = −2.314, 双侧 p = 0.021
    ⇒ 名义上"勉强显著"，但 (B) 已显示**任一班自己的读数都分辨不出 20% 与 60%**；
      即：能检出"两班不同"，不能检出"总体是否合格"——**尺的量程与门的量程不匹配**。

(D) 要把 95% CI 半宽压到 ≤10pp 需要的 n（NIST §7.2.4.2 口径）
      保守 p=0.50 → n ≥ 96.04 → **97**
      p=0.40 → 93   p=0.33 → 85   p=0.25 → 73
      压到 ≤5pp（p=0.33）→ n ≥ **340**
    ⇒ **n=50 在功效上不够**；"82"这个数对应 p≈0.30–0.33 假设下的近似值，
      严格保守（p=0.5）应为 **97**；若要 ±5pp 则需 **340**。
      （⚠ 姊妹册 `93_owner_menu.md` L31 写的 "n≈82" 属**同一公式、非保守 p 假设**，
        本卷按 NIST 保守口径给 **97**；两者都对，差别只在假设的 p，须写明假设。）

(E) 80% 功效、α=0.05 双侧，单样本比例检验分辨 10pp
      p₀=0.33 → p₁=0.43 : n ≥ 179.10 → **180**
      p₀=0.50 → p₁=0.60 : n ≥ 193.85 → **194**
    ⇒ "置信区间精度"与"检验功效"是两个不同要求；若门要写成
      "H₀: p ≥ p₀ 可被拒绝"，n 必须 ≥180，不是 50 也不是 97。
```

**分层口径（业界可抄的四个轴）**

| 轴 | 层 | 依据 | 每层最小 n |
|---|---|---|---|
| 成本档 | 0 / 5 / 10 / 20 / 40 bp | C-01（成本敏感度是一等公民） | 每档全量报 c\*，**不抽样**（c\* 是解析解，抽样无意义） |
| 换手 | 低 / 中 / 高 三分位 | C-02（成本敏感度与换手强耦合，不分层会互相抵消） | ≥30（正态近似下限） |
| 策略族 | kelly / halflife / 动量 / 均值回归 … | S-04/S-05（族内试验数决定 haircut） | ≥30 |
| 市场状态 | 上涨 / 震荡 / 下跌（按样本期指数收益切三段） | C-03（状态依赖的收益平滑） | ≥30，且**三段都要报**，禁只报最好那段 |

> **关键判断（本卷最强的一条）**：**一旦判据对象换成"盈亏平衡成本 c\*"，"抽 50 格"这个动作本身就该删除**。理由：c\* 是每格用二分法解出的确定量，**全体幸存者都能算**（成本＝每格多跑约 10 次回测），没有必要抽样；不抽样就没有抽样误差、没有置信区间、没有幸存者抽样框之争。**分层仍然要留**，但用途从"抽样框"变成"**报告维度**"（按换手×策略族×市场状态分组报 c\* 的中位数与分位数）。
> 这一条把"仓库方的修法"从**必要**降级为**多余**：改抽样框是在给一把量不准的尺换尺架，正解是换尺。

#### 主题 4-F · A 股适配（逐条过检：T+1 / 涨跌停 / 集合竞价 / 停牌复牌 / 复权 / 散户主导 / 无做市商）

| ID | 出处 | URL / DOI | 发布方 | 年份 | 对"成本档 Sharpe"的影响 | 度量方式 |
|---|---|---|---|---|---|---|
| A-01 | Wan, Xie, Gu, Jiang, Chen, Xiong, Zhang & Zhou — *Statistical Properties and Pre-Hit Dynamics of Price Limit Hits in the Chinese Stock Markets* | https://doi.org/10.1371/journal.pone.0120312 （PLOS ONE 10:e0120312，**开放获取**，HTTP 200 已核） | PLOS ONE（Public Library of Science，同行评审） | 2015 | A 股实证：**涨停触发次数 > 跌停**；触发后**价格延续多于反转**；**未发现磁吸效应（no magnet effect）**，但存在**冷却效应（cooling-off）**⇒ 涨跌停不是"把价格推到位"，而是"把成交冻结住" | 统计我方回测中被判"涨跌停不可成交"的订单占比；该占比 >5% 的格子，其 40bp 档 Sharpe **不可与其余格子同池比较**（须单列） |
| A-02 | Chen, Gao, He & Jiang — *Daily price limits and destructive market behavior* | https://doi.org/10.1016/j.jeconom.2018.09.014 （NBER WP 版 https://doi.org/10.3386/w24014 ） | Journal of Econometrics（Elsevier，同行评审） | 2018 | 用中国数据证明日涨跌停会诱发**破坏性市场行为**（过度波动/操纵），即涨跌停**改变了滑点分布的形态**，不是简单的"截断" | 对涨跌停日的成交价差做分布检验（与正常日对比 KS 检验）；分布不同即证明"单档滑点常数"建模错误 |
| A-03 | Cho, Russell, Tiao & Tsay — *The magnet effect of price limits: evidence from high-frequency data on Taiwan Stock Exchange* | https://doi.org/10.1016/s0927-5398(02)00024-5 | Journal of Empirical Finance（Elsevier，同行评审） | 2003 | 高频数据下检验"磁吸效应"（临近限价时成交加速）的方法论范式；**与 A-01 结论相反方向**⇒ 磁吸效应**市场依赖**，不能假定 A 股必然有或必然无 | 用同一方法在我方 tick/分钟数据上复算；**结论必须来自我方数据，不许引用台股结论当 A 股结论** |
| A-04 | Liu, Stambaugh & Yuan — *Size and value in China* | https://doi.org/10.1016/j.jfineco.2019.03.008 | Journal of Financial Economics（Elsevier，同行评审） | 2019 | A 股最小市值段被**壳价值（shell value）**污染，标准 size 因子在 A 股失效；作者用**剔除最小 30% 市值**的做法重建因子 ⇒ **"全体候选"这个抽样框在 A 股本身就不干净** | 检查我方 3700 格宇宙是否含壳股；若含，须**同时报"含壳"与"剔壳"两套 c\* 分布** |
| A-05 | Leippold, Wang & Zhou — *Machine learning in the Chinese stock market* | https://doi.org/10.1016/j.jfineco.2021.08.017 | Journal of Financial Economics（Elsevier，同行评审） | 2021 | A 股上做 ML 选股的完整实证与回测口径（含 A 股特有的可投资性约束处理） | 对照该文的可投资性约束清单（涨停不可买/跌停不可卖/停牌剔除/最小市值），逐条核我方回测引擎是否实现；**缺项清单即整改单** |
| A-06 | Carpenter, Lu & Whitelaw — *The Real Value of China's Stock Market* | https://doi.org/10.3386/w20957 （期刊版 Journal of Financial Economics 2021） | NBER 工作论文 / Elsevier | 2015(NBER) | A 股定价效率与散户主导结构对价格信息含量的影响 ⇒ 散户主导市场的**冲击成本对订单规模高度非线性** | 对我方回测的滑点模型做"规模敏感性"检查：同一策略在 1×/5×/10× 目标仓位下 c\* 的变化；变化 >20% 即判"滑点模型不含冲击成本，40bp 单档口径失真" |

**A 股逐条过检结论（本卷判断，非引文）**

| 制度 | 对"40bp 单档 Sharpe"的具体破坏 | 处置 |
|---|---|---|
| **T+1** | 当日买入不可当日卖 ⇒ 日内策略的回测收益被人为平滑；且日收益出现**结构性自相关** | 禁 `×sqrt(252)` 直接年化；必须过 Ljung-Box，用 Lo(2002) 修正（主题 4-B 公式(6)）后再比阈值。**度量**＝修正前后年化 SR 差异 >10% 的格子占比 |
| **涨跌停不可成交** | 收益分布被**双向截断**：涨停日的应得收益记 0（少赚）、跌停日的应亏损失记 0（少亏）⇒ 分布**非对称变形**，Sharpe 的分子分母同时失真，且方向不定 | 回测必须显式记 `unfillable_at_limit` 计数；该计数 >0 的格子，其 Sharpe **不可与 ==0 的格子同池排序**。**度量**＝两池 c\* 中位数之差 |
| **集合竞价（开/收盘）** | 开盘 9:15–9:25 与收盘 14:57–15:00 的价格形成机制不同，滑点分布与连续竞价**不同分布** | 若策略在竞价时段成交，须按**竞价专属滑点档**单独算 c\*，不许套用连续竞价的 40bp。**度量**＝竞价成交占比与两档 c\* 差 |
| **停牌／复牌** | 停牌期收益被前值填充 ⇒ **人为零波动**，直接抬高 Sharpe；复牌日常伴随跳空（补跌/补涨） | 停牌日必须**从分母剔除**（不是填 0）；复牌首日的跳空必须计入成本。**度量**＝"填 0"与"剔除"两种口径下 Sharpe 的差；差 >0.1 即判口径敏感 |
| **除权除息／复权口径** | 前复权（qfq）会**回溯改写历史价格**，导致同一格在不同日期跑出的 Sharpe 不可比；后复权（hfq）保留历史但绝对价位失真 | 验收必须锁定**单一复权口径 + 数据快照日期**，并把快照 sha256 写进成绩单。**度量**＝同一格在两个快照上的 Sharpe 差；差 >0.05 即判"结果依赖数据版本"（此条与本卷主题 1 的 F-01 `ver` 列问题同源） |
| **散户主导／无做市商** | 无做市商 ⇒ 无持续报价义务 ⇒ 流动性在小市值段**断崖式**分布；散户情绪驱动 ⇒ 滑点分布**厚尾且状态依赖** | 40bp 作为"最狠档"须**按市值分层重新校准**：大盘股 40bp 可能是宽松档、微盘股 40bp 可能是乐观档。**度量**＝按市值五分位分别报 c\* 分布；若五分位间 c\* 中位数差 >20bp，则"全局单一 40bp 档"判失效 |

#### 主题 4-G · 开源实现参照（仓库名 + 文件路径 + license + 成熟度）

| 仓库 | 关键文件路径 | License | 星数/最近推送 | 成熟度判断 |
|---|---|---|---|---|
| `esvhd/pypbo` — https://github.com/esvhd/pypbo | `pypbo/pbo.py`（CSCV/PBO 全流程）、`pypbo/perf/metrics.py`（Sharpe 变体、Lo 自相关修正、Sortino/Omega/Calmar） | **AGPL-3.0**（⚠ 传染性最强，**禁直接抄进我方闭源仓**，只可读逻辑后自写） | 140★ | 算法**忠实原论文**（docstring 直接标 SSRN 2326253，并自陈 4 条限制），但依赖老旧（`seaborn`、`statsmodels 0.8.0`），测试覆盖薄（README 自陈 "TODO: Add test cases"）⇒ **参照实现，不是可依赖件** |
| `eslazarev/purged-cross-validation`（包名 `purgedcv`）— https://github.com/eslazarev/purged-cross-validation | `src/purgedcv/_metrics.py`（PSR/DSR/MinTRL/MinBTL 闭式公式）、`src/purgedcv/_pbo.py`、`src/purgedcv/_cpcv.py`、`src/purgedcv/_path_metrics.py`、`src/purgedcv/optuna_integration.py`（`TrialSharpeRecorder` 直接产出 DSR 需要的 `V[SR]`）、`examples/optuna_dsr_cookbook.py`、`examples/backtest_overfitting_audit.ipynb`、`arxiv_paper.pdf` | **MIT**（可安全引用/移植） | 35★，v0.1.7 发布于 **2026-09-26**（活跃） | **本卷首选参照**：全类型标注（自陈过 mypy strict）、有 `tests/test_pbo.py`+`tests/test_metrics.py`+`tests/e2e/` 共 40+ 测试文件、有 `CITATION.cff`（可正式引用）、有 Zenodo DOI（`.zenodo.json`）、CI（`.github/workflows/ci.yml`）。星数低但**工程成熟度高于 pypbo** |
| `quantskills/skill-backtest-overfit` — https://github.com/quantskills/skill-backtest-overfit | `scripts/overfit_report.py`、`references/methodology.md`、`references/anti-patterns.md`、`examples/run_demo.py` | **GPL-3.0**（传染性，同 AGPL 处置） | 37★ | 价值在**判据形态**：直接输出 `PASS/FAIL` + DSR/PBO/haircut/MinTRL 四件套，且 README 给了可复现的 demo 数字（200 个纯噪声策略挑最好 → 观测年化 Sharpe 1.65 → DSR 0.63 < 0.95 → **FAIL**；注入真 edge → 年化 2.58 → DSR 0.98 → PASS）。**这就是我方该建的门的形状** |
| `hudson-and-thames/mlfinlab` — https://github.com/hudson-and-thames/mlfinlab | 原含 backtest overfitting 模块 | **NOASSERTION**（非标准 OSI 许可，商用风险不明） | 4933★，**最近推送 2023-10-02 ⇒ 已停更**（作者转向付费产品） | **不推荐**：停更 + 许可不明。历史上是 AFML 配套实现，现仅可当文献读 |
| `hudson-and-thames/portfoliolab` — https://github.com/hudson-and-thames/portfoliolab | （无 backtest overfitting 模块） | NOASSERTION | 188★，最近推送 **2021-12-02 ⇒ 停更** | **不适用**：定位是组合优化，不含 DSR/PBO |
| `stefan-jansen/machine-learning-for-trading` — https://github.com/stefan-jansen/machine-learning-for-trading | 书配套 notebook（含 purged CV / CPCV 章节） | **MIT** | 21031★，最近推送 2026-09-24（活跃） | 成熟度最高的**教学级**参照；适合抄"怎么组织一次 backtest audit"的流程，不适合抄判据阈值 |
| `quantopian/pyfolio` — https://github.com/quantopian/pyfolio | `pyfolio/tears.py` | **Apache-2.0** | 6425★，最近推送 **2023-12-23 ⇒ 实质停更**（Quantopian 已倒闭） | 报表能力强但**不含 DSR/PBO/成本敏感度曲线**；后继社区分支可用，本卷不作关键依赖 |
| `ranaroussi/quantstats` — https://github.com/ranaroussi/quantstats | `quantstats/stats.py`、`quantstats/_plotting/` | **Apache-2.0** | 7658★，最近推送 2026-09-26（活跃） | 活跃、许可友好，但**同样不含 DSR/PBO/c\***；可用作 Sharpe/回撤等基础指标的交叉校验器 |
| `polakowo/vectorbt` — https://github.com/polakowo/vectorbt | `vectorbt/portfolio/`（`fees`/`slippage` 参数化） | **NOASSERTION**（开源版 Apache-2.0 但仓内声明复杂，商用须核） | 9189★，最近推送 2026-09-26（活跃） | **成本档扫描的最佳工程件**：`fees`/`slippage` 是向量化参数，可对同一策略一次跑出 10 个成本档的收益矩阵 ⇒ 直接支撑 C-01 的"逐档成本 Sharpe 曲线"与 c\* 二分。许可需先核 |
| `skfolio-org/skfolio` — https://github.com/skfolio-org/skfolio | （本轮 GitHub API 返回 Not Found，**受阻**；官方站点 https://skfolio.org ） | 待核 | 待核 | 已知含 `CombinatorialPurgedCV`（sklearn 协议），但**本轮未能取到仓库元数据**，标待验证 |

### 主题 5 · 数据质量门的失败模式（fail-open / fail-closed）

> 本案的门是**第三种失败模式**，业界分类里没有名字，本卷命名为 **fail-always（恒假判据）**：门既不放行也不给出有用信息，只是永久报红。它比 fail-open（该拦不拦）更隐蔽，因为它看起来"很严"。

| 失败模式 | 定义 | 本案对应 | 外部依据 | 检出尺 |
|---|---|---|---|---|
| **fail-open** | 门在该红时绿 | 若把"抽 50 格"改成"抽 50 格取均值 Sharpe≥0"，则负格比例 56% 时仍可能绿 ⇒ 门被稀释成摆设 | White 2000（P-04/S-03）：H₀ 覆盖不到选择空间＝门形同虚设 | 注入"应当红的反事实样本"，看门是否红（红队用例不落盘＝判据没跑） |
| **fail-closed（正确）** | 门在该红时红、在该绿时绿 | 目标态 | NIST §7.2.4：比例检验的 α/power/δ 三件套必须先定，再定 N | 双向注入：注入已知坏样本必红、注入已知好样本必绿 |
| **fail-always（恒假）** | 门在任何真实参数下都红 | **本案现状**：读法甲下通过概率 = (1−p)^50，p=0.33 时 **2.01e-09** | 本卷 §4-E 实算(A)；判据可满足性属"元判据"，业界无直接文献，**本卷标为原创推断（单源，标待验证）** | **门可满足性检验（satisfiability pre-check）**：上线任何验收线前，先算"在参数的合理取值域内，门通过概率是否 >0"；<1e-6 即判恒假，禁上线 |
| **fail-anyway（恒真）** | 门在任何参数下都绿 | 风险面：若把判据改成"幸存者里抽 50 格，均值 Sharpe≥0"且幸存者已被强筛 ⇒ 门几乎必绿 | S-01/S-02（幸存者偏差量级可测） | 同上做反向注入：构造"应当红"的幸存者集合，门必须红 |

**可直接抄的元判据（本卷建议新增的一把尺，编号建议 G-XX 由 Owner 定）**
```
尺名: 判据可满足性预检 (ACCEPTANCE-SATISFIABILITY-PRECHECK)
适用: 任何写进冻结预注册件的验收线
步骤:
  1. 把判据写成 通过概率 = f(θ) 的显式函数, θ = 全部未知参数
  2. 给 θ 一个"合理取值域" Θ (来源: 历史实测 + 业界文献, 必须写明出处)
  3. 算 sup_{θ∈Θ} f(θ)
  4. 判定:
       sup f(θ) < 1e-6          ⇒ 恒假, 禁上线, 退回改写
       sup f(θ) > 1 - 1e-6     ⇒ 恒真, 禁上线, 退回改写
       否则                     ⇒ 可满足, 允许上线, 但必须同时报 n 与 CI 半宽
本案代入: f(p) = (1-p)^50, Θ = [0.10, 0.56] (两班实测读数)
          sup = f(0.10) = 5.15e-03 < 1e-6? 否 —— 但 5.15e-03 意味着
          "要门有 5‰ 的通过率, 需真实负格比例 ≤10%", 而两班实测均 ≥33%
          ⇒ 在实测支撑的 Θ' = [0.33, 0.56] 上, sup f = 2.01e-09 < 1e-6 ⇒ 判恒假
```
> **怎么量它有没有用**：把该尺回溯跑在本仓历史上所有"上线后被证明恒红/恒绿"的门上，统计**召回率**（该尺能否事前判出）与**误报率**（判恒假但实际能过的门有几把）。召回 <0.7 即尺本身不合格。

### 主题 6 · 可观测性与自愈（演练判据怎么写才不恒红不恒绿）

**六条写法铁律（每条带外部依据）**

| # | 铁律 | 依据 | 反例（本案原写法） | 正例 |
|---|---|---|---|---|
| 1 | **判据对象必须是连续量，不能是"计数达标"** | NIST §7.2.4.2（比例检验需先定 δ 与 power）；C-01（成本敏感度是连续曲线） | "50 格里 Sharpe≤0 的格子数为 0" | "全体幸存者 c\* 的中位数 ≥ 40bp" |
| 2 | **抽样框必须等于判据声称要覆盖的总体** | S-03（White 2000：H₀ 必须覆盖全搜索空间）；S-01/S-02（幸存者偏差可量化） | 声称覆盖"本轮全部候选"，实抽"通过初筛的幸存者" | 全体 3700 格全量算 c\*（不抽样），初筛只用于**报告分层**不用于裁剪样本 |
| 3 | **试验次数 N 是判据的必填输入，不是元数据** | S-05（1999, JF：候选空间大小必须随结果披露）；P-01（DSR 的 N） | 判据里完全没有 N | 判据显式含 `n_trials=3700`，缺失即尺红 |
| 4 | **阈值必须随 N 上抬，不许"一字不动"** | S-04（Harvey-Liu-Zhu 2016, RFS：t 门槛提到 3.0）；P-01（DSR 的 SR\*ₙ 随 N 单调上升） | "阈值 0 一字不动"作为修法卖点 | 阈值口径＝`DSR ≥ 0.95`（等价于"扣掉 N=3700 次选择后仍显著"），40bp 作为**成本锚**保留 |
| 5 | **每次读数必须带区间，不带区间的点读数不作判据** | NIST §7.2.4.1（小样本用精确二项区间）；本卷 §4-E 实算(B) | "33%"／"56%" 两个裸数字 | "33% [95% CI 20.0%–46.0%]"，且**区间重叠时判"不可分辨"而非判红** |
| 6 | **门必须有双向注入测试，且用例落盘** | 主题 5 表（fail-open / fail-always / fail-anyway 三态） | 门只跑过一次真实数据就冻结 | 上线前跑三个用例：已知坏样本→必红；已知好样本→必绿；边界样本→报"不可分辨" |

---

## §二 我方 8 条痛点逐条对标

| # | 痛点（我方实测） | 业界标准做法 | 我方方案当前处方 | 差距 | 改法（外部依据） | 度量 |
|---|---|---|---|---|---|---|
| 1 | 假绿灯：记账 SUCCESS 而目标表 0 行 | **部分可迁移**：本卷主题 5 给出门的三态失效分类（fail-open／fail-always／fail-anyway）＋双向注入检验法＋"门可满足性预检"元判据 | 波 3.2 + G-21/G-22 | 现有 G-21/G-22 只查"记账态 vs 行数"这一对；**没有一层查"这把尺本身能不能红/能不能绿"** | 把主题 5 的三态注入测试挂到 G-21/G-22：上线前必须落盘三个用例（已知坏→红、已知好→绿、边界→INDETERM） | 三用例落盘率＝100%；回溯跑历史假绿灯事故，召回率 ≥0.7 |
| 2 | 类型边界崩溃 `'str' > 'date'` | （窄口径外，本轮未查——禁当已查） | 波 3.1 + G-20 | （窄口径外） | （窄口径外） | （窄口径外） |
| 3 | 新鲜度/污染分不清 | Dagster 双轨（freshness policy ≠ asset check） | 波 3.3 明确"新鲜度用业务表 `max(date)` 不用 `system.` 面"+ G-29 | **只补了新鲜度真源，没补正确性轨**；`max(date)` 新鲜与 30% 幽灵行是两个正交指标 | 按 F-02 拆成两套尺：新鲜尺（时延）+ 正确尺（幽灵日检出率） | _待填_ |
| 4 | 后复权表族缺版本列 | ClickHouse 官方：无 `ver` ⇒ "最近插入的最后一行胜出"，只保证 eventual correctness | 波 3.9 "hfq 族来源独占验证尺" + G-28 | **"来源独占"防的是"两个写者口径混写"，防不住"同一写者用旧口径重写覆盖修正行"**；且族内 11 张只提了独占、未提版本列补齐 | 按 F-01 给周/月表补 `ver`（可复用 `lineage_version`），读侧统一 `argMax(col, ver)` 或 `FINAL` | _待填_ |
| 5 | 测试污染生产账本 | _待填_ | 波 3.8 + G-27（sha256 前后不变） | _待填_ | _待填_ | _待填_ |
| 6 | 空壳表 11/12 count=0，三套张数口径互异 | _待填_ | 波 3.5 + G-24 | _待填_ | _待填_ | _待填_ |
| 7 | 探库工具静默失败 | _待填_ | G-30 + §五第 4 条"静默失败面禁用" | _待填_ | _待填_ | _待填_ |
| 8 | 预注册考试链：3700 格粗扫 / "抽 50 格最狠滑点档 sharpe≥0" | **成本敏感度曲线 + 盈亏平衡成本 c\* 全量算**（C-01 RFS 2016、C-02 JF 2023）；**多重检验折减 DSR/PBO**（P-01 JPM 2014、P-02 JCF 2016）；**选择过程写进 H₀**（S-03 Econometrica 2000、S-05 JF 1999）；**阈值随 N 上抬**（S-04 RFS 2016）；**样本量按 power 定**（NIST §7.2.4.2） | 92 册无对应尺；10 册波 2.4 只提"回测哨兵"代码复杂度 | **三处全缺**：①该验收线在统计上不可过（读法甲下 P(通过)=(1−p)^50，p=0.33 ⇒ **2.01e-09**），但我方 41 把尺里没有一把量"验收线本身是否可满足"（主题 5 的 fail-always 态）；②判据里没有 `n_trials` 字段 ⇒ 3700 次试验的多重检验成本被全额免单；③n=50 的 CI 半宽 ±0.13 ⇒ 两班 33%/56% 区间重叠，尺的量程撑不起门 | 见 §三：主推 **B（c\* 中位数 ≥40bp，全量不抽样）∧ C（DSR ≥0.95, N=3700）并联**；次选 A 案但必须附 §3.4 全 7 条 | ①门可满足性预检的召回率/误报率（主题 5 尺）②成绩单 `n_trials` 字段填充率＝100% ③c\* 非单调格占比 ≤5% ④DSR 与裸 SR 两套 Top-K 的样本外 SR 差 >0（证明 DSR 有用）⑤双向注入三用例落盘且全过 |

---

## §三 判据级建议（针对第 4 条"抽查口径"的统计学正解）

> ⚑ **门位声明（必读）**：本节改的是**判据口径**，而该判据写在**冻结的预注册件**里（防"考卷跟着答案改"）。按本仓 `risk_tier_registry.yaml` 人机门位分级，**冻结判据件口径变更属 Owner 门位（high tier）**。
> **AI 只能给证据，不能拍板。** 本节所有内容＝案卷与可粘贴草案，**不构成生效判据**，亦不代表任何审批状态。

### 3.0 结论一句话

**仓库方的改法（"从通过成本初筛的幸存者里分层抽"，阈值 0 一字不动）在统计上站不住——但不是因为它"引入了幸存者偏差"这么轻，而是因为它没有触及真正的病根：那把尺的判据对象错了。**

三条独立成立的理由：

1. **恒假没被修掉。** 读法甲（抽出的 50 格全部须 Sharpe≥0）下通过概率 = (1−p)^50。幸存者池的 p 只是从 0.33–0.56 降到某个更小的 p′；要有 95% 通过率需 p′ ≤ 0.1%，要有 50% 通过率需 p′ ≤ 1.4%。**"幸存者"这个筛子能把 p′ 压到 1.4% 以下吗？没有任何实测数据支撑这个假设。** 改法把一个 2.01e-09 的数换成一个未知的更小的数——**从"确定恒假"变成"大概率恒假"**，门的失效性质没变，只是变得更难被发现（这正是主题 5 里的 fail-always → 潜伏态）。
2. **量不准没被修掉。** n=50 的 95% CI 半宽 ±0.13–0.14（§4-E 实算 B）。**两班实测 33% 与 56% 的区间大幅重叠**；即便换成幸存者池，n=50 仍然分辨不出 20% 与 60%。要压到 ±10pp 需 **n=97**（NIST §7.2.4.2 保守口径，p=0.5）；要 80% 功效分辨 10pp 需 **n=180–194**。
3. **方向反了。** 选择偏差的正统校正＝**把选择过程装进零假设**（White 2000, Econometrica）／**把试验次数 N 装进阈值**（Harvey-Liu-Zhu 2016, RFS：t 门槛 2.0→3.0）／**把 N 装进 Sharpe 的折减**（Bailey-López de Prado 2014, JPM：DSR）。仓库方的改法做的是**把选择过程从判据里摘出去、藏进抽样框**——这是这三条文献共同反对的动作。而且"阈值 0 一字不动"作为卖点，与 S-04 的主张**方向相反**：N=3700 时阈值不但不能不动，还**必须上抬**（见 3.3 的实算：DSR≥0.95 在 N=3700、跨格年化 SR 标准差 0.5 时，等价于要求年化 Sharpe ≥ **1.81**，远高于 0）。

**但改法里有一半是对的、必须保留**：把"分层"引进来是对的（分层口径见 §4-E 表）。**错的是把分层用于"抽样框"**。正解＝**分层保留，抽样删除**：判据对象换成每格都能全量算出的**盈亏平衡成本 c\***，分层降级为**报告维度**。

### 3.1 三个候选改法（并列呈报，不替 Owner 选）

| 案 | 判据对象 | 阈值口径 | 抽样 | 优点 | 代价 | 外部依据 |
|---|---|---|---|---|---|---|
| **A（仓库方原案）** | 抽中格在 40bp 档的 Sharpe | ≥ 0，一字不动 | 从初筛幸存者里**分层抽 n=50** | 改动最小，只改抽样框 | ①恒假大概率仍在（3.0-1）②n=50 仍量不准（3.0-2）③幸存者抽样框＝把选择过程藏起来，方向反（3.0-3）④引入新的口径争议："通过初筛"本身成了未冻结的自由参数 | 无支持性一手源；反证见 S-01/S-02/S-03/S-04 |
| **B（本卷推荐）** | 每格的**盈亏平衡成本 c\***（使 Sharpe(c)=0 的最小 c） | **全体幸存者 c\* 的中位数 ≥ 40bp** | **不抽样**（全量算）；分层只用于**报告** | ①40bp 锚一字不动 ②"Sharpe≥0"语义一字不动（只是从"看一眼"变成"解到零点"）③无抽样⇒无抽样误差、无幸存者抽样框之争 ④每格一个确定量，可逐格追溯 ⑤单调性校验能顺带暴露回测引擎缺陷 | 每格多跑约 10 次回测（二分法，成本线性、可并行） | C-01（RFS 2016）成本敏感度作一等公民；C-02（JF 2023）含成本重排序会改变结论；§4-D 的 c\* 算法 |
| **C（最强，可与 B 并联）** | 每格的 **DSR**（扣掉 N=3700 次选择后的显著性概率） | **DSR ≥ 0.95** | **不抽样**（全量算） | ①直接把"3700 格粗扫"这件事**写进判据**（S-05 要求的 n_trials 披露）②阈值随 N 自动上抬（S-04）③输出是概率，天然带不确定性 | 需要 `V[SR]`（跨格 Sharpe 方差）作为输入 ⇒ 必须留档全部 3700 格结果；且 DSR 对偏度/峰度敏感，厚尾时会给出反直觉读数 | P-01（JPM 2014, DOI 10.3905/jpm.2014.40.5.094）；P-02（JCF 2016）配套 PBO；S-04（RFS 2016）；实现见 `purgedcv/_metrics.py`（MIT） |

**本卷意见（仅意见，非裁定）**：**B 为主 + C 为并**。理由——B 单独用会漏掉"选出来的运气"（B 只管成本承受力，不管多重检验）；C 单独用会漏掉"成本口径失真"（C 的输入 Sharpe 本身就受涨跌停/停牌/T+1 影响）。B∧C 并联后，两把尺量的是**两个正交的失效面**，且都不含抽样。

### 3.2 可直接粘贴的判据改写草案（B 案，含公式/伪代码/阈值口径）

```
【判据编号】G-COST-BREAKEVEN-40BP（原"成本门抽查口径"替换件）
【门位】Owner（high tier）——冻结预注册件口径变更，AI 不得自行生效
【判据对象】盈亏平衡成本 c*（每格一个确定量，非抽样统计量）
【锚点】40bp 单边成本，一字不动
【语义】"Sharpe ≥ 0" 一字不动，仅从"单档抽查"改为"逐格解到零点"

一、定义
   对格 g、单边成本 c（单位 bp）：
       Sharpe_g(c) = 年化( 逐期净收益(c) )   # 净收益已扣佣金+印花税+滑点(c)+冲击成本
   盈亏平衡成本：
       c*_g = min{ c ≥ 0 : Sharpe_g(c) ≤ 0 }
   若 Sharpe_g(0) ≤ 0 ⇒ c*_g = 0
   若 Sharpe_g(200bp) > 0 ⇒ c*_g = ">200"，单列，不计入中位数

二、求解算法（二分，单调性为前提且必须校验）
   c_lo, c_hi, tol = 0.0, 200.0, 0.1     # bp
   assert Sharpe_g(200.0) <= 0, "上界不足, 扩到 500bp"
   while c_hi - c_lo > tol:
       c_mid = (c_lo + c_hi) / 2
       if Sharpe_g(c_mid) > 0: c_lo = c_mid
       else:                   c_hi = c_mid
   c*_g = c_lo
   # 单调性校验（必做；不通过则 c*_g = NaN 并单独计数, 禁混入中位数）
   grid = [0, 5, 10, 20, 40, 60, 80, 100, 150, 200]
   srs  = [Sharpe_g(c) for c in grid]
   assert all(srs[i] >= srs[i+1] for i in range(len(srs)-1)), \
          f"格 {g} 成本-Sharpe 非单调, 疑回测引擎缺陷(涨跌停/停牌填充)"

三、Sharpe 口径（A 股适配，四条强制）
   1. 年化：禁 ×sqrt(252)。先跑 Ljung-Box(q=252)；p<0.05 则用
        factor = q / sqrt( q + 2·Σ_{k=1..q-1} (q-k)·acf[k] )
      否则用 sqrt(q)。（Lo 2002；实现见 pypbo/perf/metrics.py::sharpe_autocorr_factor）
   2. 标准差用总体口径 ddof=0（与 PSR/DSR 公式一致）
   3. 停牌日：从分子分母**同时剔除**（禁填 0）；复牌首日跳空计入成本
   4. 涨跌停不可成交：显式记 unfillable_at_limit 计数；计数>0 的格子**单列池**

四、通过条件（全部满足才绿）
   P1  中位数门:  median{ c*_g : g ∈ 幸存者, c*_g 有效 } ≥ 40.0 bp
   P2  尾部门:    P10{ c*_g } ≥ 0 bp                # 最差的 10% 也不能一上线就亏
   P3  分层门:    对每个 (换手三分位 × 策略族 × 市场状态三段) 层,
                  层内 c* 中位数 ≥ 40.0 bp 的层数占比 ≥ 80%
                  每层最小样本 n_layer ≥ 30; 不足 30 的层判 "INSUFFICIENT-N" 而非绿
   P4  规模门:    同一策略在 1×/5×/10× 目标仓位下 c* 的相对变化 ≤ 20%
                  (A-06: 散户主导+无做市商 ⇒ 冲击成本非线性)
   P5  数据版本门: 成绩单必须含 {复权口径, 数据快照日期, 快照 sha256, n_trials}
                  四字段缺一即尺红（S-05: n_trials 必须随结果披露）

五、判红/判灰的三态输出（禁二值）
   PASS        P1–P5 全满足
   INDETERM    任一层 n<30, 或 c* 非单调格数占比 >5%
   FAIL        P1 或 P2 或 P3 或 P4 不满足
   ⇒ INDETERM 必须触发补数据/补跑, 不许默认降级为 PASS（fail-open 防线）

六、报告必须同时给出（不许只报中位数）
   - c* 的 P10/P25/median/P75/P90
   - 幸存者数 K 与 全体候选数 N（**两个都要**，比例 K/N 即"初筛通过率"，
     是 S-01/S-02 要求的幸存者偏差披露口径）
   - 非单调格清单 + unfillable_at_limit>0 格清单（单列池）
```

### 3.3 可直接粘贴的判据改写草案（C 案，DSR 并联门）

```
【判据编号】G-DSR-N3700（与 G-COST-BREAKEVEN-40BP 并联，两门都绿才放行）
【门位】Owner（high tier）

一、公式（源码级确证, purgedcv/_metrics.py, MIT）
   SR*_N = sqrt( V[SR] ) · [ (1-γ)·Φ⁻¹(1 - 1/N) + γ·Φ⁻¹(1 - 1/(N·e)) ]
   DSR   = Φ( (SR_hat - SR*_N)·sqrt(n-1)
              / sqrt( 1 - γ3·SR_hat + ((γ4-1)/4)·SR_hat² ) )
   γ = 0.5772156649015329 (Euler–Mascheroni)
   N = n_trials（本轮全部候选格数，本案 = 3700；禁填抽样数 50）
   V[SR] = 3700 格之间 Sharpe 的方差（跨试验方差，非时序方差）
   单位铁律：DSR 是逐观测量。V[SR] 若为年化方差，必须 / bars_per_year(=252)

二、本卷实算（scipy 复算，输入=年化 Sharpe 跨格标准差 sd）
   E[max z] 随 N:   N=50 → 2.2763   N=200 → 2.7655   N=900 → 3.2250
                    N=3700 → 3.6103  N=17100 → 3.9899
   N=3700 时的 DSR 年化门槛 SR*:
        sd=0.25 → SR* = 0.9026      sd=0.50 → SR* = 1.8051
        sd=0.75 → SR* = 2.7077      sd=1.00 → SR* = 3.6103
   ⇒ **"阈值 0" 在 N=3700 下的真实等价阈值约为年化 Sharpe 1.8（sd=0.5 假设）**
      这就是 S-04（Harvey-Liu-Zhu 2016, RFS）"阈值必须随试验数上抬"的本地数值版。
      仓库方"阈值 0 一字不动"若指字面 0，等于**把 N=3700 的多重检验成本全部免单**。

三、通过条件
   P6  对每个拟转正格 g：DSR_g ≥ 0.95（α=0.05）
   P7  同时报 PBO（CSCV, S=16）：PBO ≤ 0.20
        ⚠ PBO 单独不足以判死（pypbo docstring 自陈："可能 N 个配置全都 Sharpe 高且相近,
          此时 PBO 高但过拟合发生在一群有本事的策略之间"）
        ⇒ PBO 必须与 prob_oos_loss（threshold=0）合看:
             PBO>0.20 且 prob_oos_loss>0.50 ⇒ FAIL
             PBO>0.20 且 prob_oos_loss≤0.50 ⇒ INDETERM（人工复核，禁自动绿）
   P8  MinTRL 检查：若 SR_hat ≤ SR*_N ⇒ MinTRL = ∞ ⇒ 直接 FAIL
        （本卷实算 H：年化 SR_obs=1.0 vs SR*=1.805 ⇒ MinTRL 无穷，再多数据也救不回；
          SR_obs=2.5 ⇒ MinTRL≈1430 bars ≈5.7 年；SR_obs=3.0 ⇒ ≈487 bars ≈1.9 年）
   P9  CSCV 前置校验：先对每格日收益跑 Ljung-Box；显著自相关的格占比 >30% ⇒
        CSCV 结果标 LOW-CONFIDENCE（pypbo docstring 自陈"不适用于强自相关序列,
        尤其 S 较大时"），须降到 S=8 复算并同报

四、报告字段（成绩单 schema，缺任一即尺红）
   n_trials, var_sharpe, bars_per_year, skew, kurtosis, n_obs,
   observed_sr, sr_star, dsr, pbo, prob_oos_loss, min_trl, s_blocks
   （字段名对齐 purgedcv 的 DSRDiagnostics dataclass，便于直接对接）
```

### 3.4 若 Owner 坚持 A 案（最小改动），必须附的 7 个条件

> 本卷不推荐 A 案；但若采纳，以下 7 条**缺一不可**，否则改法在统计上不成立。

| # | 条件 | 依据 | 怎么量它有没有用 |
|---|---|---|---|
| A1 | **把初筛阈值写进零假设**：H₀ 不得写成"抽中格 Sharpe≥0"，须写成"在**含初筛规则**的选择流程下，随机抽中格的 Sharpe≥0 的概率 ≥ q"，q 须先冻结 | S-03 White 2000（选择过程入 H₀） | 检查判据文本里是否出现初筛规则的**机器可执行定义**（不是自然语言描述）；出现即达标 |
| A2 | **同时报全体候选基准**：每次报"幸存者池通过率"，必须并列报"全体 3700 格通过率"与"初筛通过率 K/N" | S-01 Carhart 2002、S-02 Elton-Gruber-Blake 2001（幸存者偏差量级必须可算） | 成绩单是否三数齐全；缺一即尺红。差值 = 我方版 survivorship bias（bp/年化） |
| A3 | **n 从 50 提到 97**（95% CI 半宽 ≤10pp，NIST 保守口径 p=0.5）；若门要写成可拒绝的假设检验，n 须 ≥180（80% 功效分辨 10pp） | NIST §7.2.4.2；本卷 §4-E 实算 (D)(E) | 复算 `n = z²·p(1-p)/e²`；n<97 即判"精度不足"，门输出强制标 INDETERM |
| A4 | **分层最小样本 n_layer ≥ 30**，不足的层判 INSUFFICIENT-N，禁并入总池 | 正态近似下限（NIST §7.2.4）；§4-E 分层表 | 统计各层 n；<30 的层数 >20% 即判抽样设计不合格 |
| A5 | **读数必须带 95% CI，小样本/少数不良用精确二项区间**（正态近似在 p̂→0 时不准） | NIST §7.2.4.1 | 报告里每个比例是否带区间；裸数字即尺红 |
| A6 | **禁"阈值 0 一字不动"当卖点**：必须并列报 DSR 门槛（3.3 节实算的 SR*≈1.8 年化），让 Owner 看见"字面 0"与"统计等价阈值"的差距 | S-04 Harvey-Liu-Zhu 2016（阈值随 N 上抬）；P-01 DSR | 成绩单是否同时含 `observed_sr` 与 `sr_star`；只含前者即判"多重检验成本被免单" |
| A7 | **门必须过双向注入测试且用例落盘**：注入"应当红"的幸存者集合→必红；注入"应当绿"的→必绿；注入边界→必报 INDETERM | 主题 5/6（fail-open / fail-always / fail-anyway 三态） | 三个用例的落盘文件路径 + 执行日志；缺任一即门未验证（本仓既有铁律：红队用例不落盘＝判据没跑） |

### 3.5 本卷对"改法站不站得住"的最终判断（证据句，非裁定）

- **"从初筛幸存者里分层抽"这半句**：分层＝站得住（§4-E 四轴，业界可抄）；幸存者抽样框＝**站不住**（S-01/S-02/S-03 三源同向反对；且它把选择过程从判据里摘出去，与 White 2000 的正统做法相反）。
- **"阈值 0 一字不动"这半句**：**站不住**。N=3700 时 DSR≥0.95 的统计等价阈值约为**年化 Sharpe 1.8**（本卷实算，sd=0.5 假设）；把阈值钉在字面 0 等于免掉全部多重检验成本，与 Harvey-Liu-Zhu 2016（RFS）的主张方向相反。
- **"抽 50 格"这半句**：**站不住，且应当整句删除**。n=50 的 CI 半宽 ±0.13–0.14，两班读数 33%/56% 区间重叠 ⇒ 尺的量程不足以支撑门；而一旦判据对象换成 c\*，**全量可算，无需抽样**。
- **改法整体**：**不成立**。它修的是抽样框（次要缺陷），没修判据对象（主要缺陷）；恒假性质大概率仍在（(1−p′)^50，p′ 无实测支撑）。**正解是 B∧C 并联**（§3.2 + §3.3），或退而求其次采 A 案并附 §3.4 全 7 条。

---

## §四 受阻与查无

_待填_

---

## §五 我最没把握的 3 条

_待填_
