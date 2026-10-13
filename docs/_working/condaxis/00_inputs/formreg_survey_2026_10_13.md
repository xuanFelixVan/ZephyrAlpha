---
ttl: task_bound
title: 状态与信号·全网勘查册——学术/机构实践/开源生态/A股适配四线汇查（大盘两态形态识别班前置研究）
created: '2026-10-13'
session: st-formreg-20261013
status: research_notes
family_id: FORMREG-CAMPAIGN
completes_when: §13 九项经条件轴总包 P1 统一呈批包呈 Owner 裁决且两态线打靶收口后，随 CONDAXIS-CAMPAIGN 战役归档
---

# 0. 本册定位与勘查方法

- **定位**：Owner 令"先全网查清顶尖机构/量化社区/学术/开源怎么做状态识别与拐点信号，查完把问题定下来，落 working 文档"。本册=证据与对照记录（research_notes），**非判据冻结件**——判据冻结仍走施工令 P2 呈批，"判据数值零自拟"纪律不变。
- **勘查方法**：2026-10-13 四条并行研究车道（学术主线/机构实践/开源生态/A股与中文实践）；通用纪律=一手来源优先、paywalled 标注、**查不到明说不编造**；GitHub 星数与活跃度经 GitHub API 当日实时核实。
- **配套仓内勘查**：regime 包 46 文件、D 族冻结稿（draft_for_ruling）、market_state 词表、condition_package 等已并查，衔接见 §12；此前讨论确认的治理冲突（#229 职责划界、D 族并行、词表登记）不在本册重复论证，只汇总为 §13 裁决项。

# 1. Owner 三问锚定（需求真源，原话）

1. "把识别板块状态、大盘状态这个事情先搞清楚……这套做出来应该还可以识别大盘、识别板块、识别宽基指数；个股可能有控盘，但我觉得应该也可以——它只是给到一个状态。"
2. "反转信号在哪里？改变结构的、改变状态的信号。"
3. "信号和状态，这两个事情最重要。"

→ 本册按"状态怎么建（§3-§6）／拐点信号怎么建（§4）／灰度怎么定（§5、§11）／跨标的泛化（§9）／A股适配（§8）／职责分层（§10）"组织。

# 2. 一页结论（TL;DR）

1. **"状态"与"信号"在文献里是两个成熟分离的子问题**，我们的三件套全部有对应物：状态=regime filtering（规则年代学或概率模型）；灰度=模型后验或统计量（BOCPD run-length 后验、jump 后验、trend-scanning t 值）；拐点信号=quickest change detection（虚报率约束下最小化检测延迟）。
2. **规则骨架的现成起点**：Pagan-Sossounov (2003) 牛熊年代学——滚动窗±8月、牛≥15月/熊≥6月（幅度>20%豁免）、完整周期<16月剔除（>30%豁免）、相位<4月一律剔除。机械、可复现、可审计，参数可直接进 P2 预冻结（换算到 A 股日线需自标——文献无日频/中国重校准=已知缺口，见 §3.4）。
3. **信号的理论骨架现成**：最快检测理论（Page CUSUM→Lorden/Moustakides minimax；Shiryaev 贝叶斯）把"最小段长-确认延迟-假报率"不可能三角正式化为一个最优化问题——P2 不自创拼盘，选准则+钉虚报率预算即可，延迟是预算的结果不是自由参数。
4. **概率模型风向**：裸 HMM 三病（label switching／态数选择／过频切换）；jump model（跳变惩罚→持久状态）近五年实证系统性优于 HMM，且有 Apache-2.0、sklearn 风格开源包（jumpmodels）。仓内 regime_detector 的 9态→4态降维史与裁定#304 锚定重排与全球风向同向——**两态层建在它上面不是推倒重来**。
5. **机构画像**：主流是"规则分档+多窗口分数"为主、模型为辅、输出概率化（S&P VEQTOR 波动率状态机／Two Sigma GMM 描述性四态／AQR 多窗口趋势分数／Fidelity 宏观时钟／Dorsey Wright 板块相对强度）。AQR 实证：主流趋势滤波器高度相关——**滤波器/参数选型性价比低，别把 P1/P3 精力花在挑滤波器上**。
6. **A股适配三个硬点**：±20% 美式阈值对 A 股偏保守（Tilburg 2025 实证，会漏 2013/2019 级中级行情）；牛熊锚点年表（998→6124／1849→5178／2440→3731）可当 P3 标定集；**"板块自身状态"在公开文献里是空白**（中外主流全是横截面相对排名）——我们的差异化增量。
7. **个股可行，但要加"可标注性过滤"**：高控盘/操纵代理特征（同步性/换手/流通盘/龙虎榜集中度）不过关的个股输出"数据不可信"，**"不可标注"本身立为状态枚举的一态**——有先例（Chi et al. 2016 指数与个股同法标注；JFE 2022 操纵识别；IEEE 2024 用 389 起证监会处罚案例训练检测器）。
8. **2024-2026 前沿**：deep switching SSM（IJF 2025）、ML 四态（SSGA 2025）、**A股相关矩阵聚类 5 态+崩盘预警（Frontiers 2025，精确率 96.4%，转移矩阵三对角=灰度应平滑衰减的证据）**、LLM 多智能体 regime council（2026 arXiv，早期）。conformal 校准 regime 置信度=公认缺口；仓内 B1/Brier、B2/CRPS 验证框架即行业标准做法，直接复用。

# 3. 学术主线A：牛熊年代学（"两态三向+拐点"的规则化祖先）

## 3.1 Pagan & Sossounov (2003)——主骨架

- 出处：J. Applied Econometrics 18(1):23-46，DOI 10.1002/jae.664（原文 paywalled；参数经 bbdetection R 包文档与 SSRN 3105209 交叉核实）。
- 机制：把 Bry-Boschan 定日算法移植到月度对数股价——①滚动窗找局部峰谷 ②强制峰谷交替 ③censoring：太短相位并入邻相、太短周期合并、剔除贴近样本首尾的峰谷。

| 规则 | 数值（美股月频） |
|---|---|
| 峰谷搜索窗 | ±8 个月 |
| 牛市相位最短 | 15 个月（幅度>20% 豁免） |
| 熊市相位最短 | 6 个月（幅度>20% 豁免） |
| 完整周期最短 | 16 个月（幅度>30% 豁免） |
| 相位硬下限 | 4 个月，一律剔除 |

- 坑：①参数为美股月频校准，A 股日频直接套会漏相位（工程惯例 8 个月≈160-170 交易日，**无权威出处**）；②censoring 需右端确认=非实时，拐点定案滞后一个窗口；③原文名词是牛/熊两态，"横向"只是两态间的短相位——**"横向"独立成态需自己立规则**（进 §11 问题4）。
- 【未直核】原文 terminal censoring 精确月数；"15% 豁免"未查到原文依据（bbdetection 实现为 20%）。

## 3.2 同族方法

- **Bry & Boschan (1971)**, NBER TP20：月/季频原型；价值=censoring 思想（时长+幅度双门槛）被一切后继者继承。
- **Lunde & Timmermann (2004)**, JBES 22(2):273-287：±20% 对数价差阈值交替定义牛熊；实证**熊市 hazard 随时长递增**（越跌越接近结束）、牛市时长依赖弱——对"单边↓段平均更短"的先验有支撑。
- A股/非美应用：Z. Li（Palgrave 章节，P-S 法识别中国 20 牛熊段/19 完整周期）；**Chi et al. (2016, SEF)——指数与个股同法标注（个股可行性的直接先例）**；Yang (2025, Tilburg)——±20% 对 A 股"过于保守"并调参；Hanna (2018, IRFA)——P-S vs L-T 两路线系统对比。

## 3.3 工程要点

- P-S 类规则是**离线年代学**（确认制），不是在线信号——与变点检测（§4）是互补分工：规则法定"历史真值段"，在线法出"实时灰度与告警"。
- 双门槛（时长+幅度）思想可直接搬进我们 P2：横向→单边的确认=持续天数门槛+幅度门槛双条件。

## 3.4 缺口（即我们的活）

未查到 P-S 参数的日频/中国市场正式重校准文献——P3 必须在 A 股样本上自标定+留证（预注册协议，引仓内 regime_recal_protocol 先例）。

# 4. 学术主线B：变点检测（拐点信号的理论骨架）

## 4.1 最快检测理论：不可能三角的正式形式

- Page (1954) CUSUM+ARL；Lorden (1971) minimax（最坏平均检测延迟 WADD 最小化，CUSUM 渐近最优）；Moustakides (1986) 精确最优；Shiryaev (1963) 贝叶斯版（对"变化后验概率"设阈值最优）。综述：Veeravalli & Banerjee, arXiv:1210.5552。
- 统一结论：**在虚报率（ARL）约束下最小化检测延迟**。
- 对我们的意义：P2 不自创"斜率阈值+最短天数"拼盘，而是①选准则（minimax→CUSUM／贝叶斯→Shiryaev/BOCPD）②钉虚报率预算（平均每 N 日允许一次假拐点）③确认延迟是预算的结果，不是独立自由参数——Owner 令里"最小长度/斜率阈值"两问在此理论里合成一个问题。

## 4.2 BOCPD（在线、天然出灰度）

- Adams & MacKay (2007), arXiv:0710.3742：在线精确贝叶斯滤波，递推维护 run-length 后验 p(r_t|r_<t)；hazard 可设常数（原文示例 1/250）。
- **p(r_t=0) = "本时刻是新状态起点"的概率 = 天然拐点灰度**，无需重训练。
- 坑：对 hazard 与观测先验敏感；金融厚尾建议 Student-t 观测模型或 robust BOCPD（Altamirano et al., ICML 2023, PMLR 202:642-663）。
- 在线/离线分工（工程惯例，ruptures 作者系综述同款）：**BOCPD 在线出 PIT 信号，离线法（PELT/kernel CP/e-divisive）定期复核历史标注**——正好映射我们 P3（离线全量标注）与 P4（实时预测卡）两条验收线。

## 4.3 Trend-Scanning Labels（López de Prado ~2020）

- 机制：对每个 t 试多组变长 span，各做 y~t 线性回归，取 |t 值| 最大的 span——符号=方向标签、**|t 值|=连续灰度**、span 终点=自适应 horizon；与 meta-labeling 天然咬合。
- **PIT 红线**：作为训练标签合法（标签在 span 闭合 t1 才观测）；若当实时状态指示器，"在 t 时刻选 |t| 最大的 span"用了 t 之后的数据即违 PIT——实时用途必须只认已闭合 span 或把 t1 当等待期。
- 已知缺陷：横盘噪声期 span 选择不稳、t 值厚尾失真、对 span 网格敏感（→ P2 必须钉死 span 网格）。
- 出处【部分未直核】：MLAM/课程讲义与 SSRN（编号未查到）；实现文档 mlfinpy。

# 5. 学术主线C：概率状态模型（HMM→jump model→深度）

## 5.1 HMM 家族与三病

- Hamilton (1989), Econometrica：Markov-switching 起点。
- 三病：①label switching（似然对状态置换不变）②态数选择（LR 检验非正则，用 BIC/AIC）③**过频切换与样本外漂移**——jump 文献的核心批评。
- 仓内对照：三病分别对应裁定#304 锚定重排（已治①）、BIC 降态史 9→4（已治②）、以及两态层要治的③。

## 5.2 Jump models（近五年实证风向）

- 思想：转移加 L1 跳变惩罚→学习持久状态，直接治过频切换；输出=各态后验+跳变代价（连续量，天然灰度语义）。
- 论文链：Nystrup, Boyd, Lindström & Madsen（惩罚跳变学持久 HMM，arXiv 2017／ESWA 2020【venue 以开源包 README 为准，未直核期刊页】）；Nystrup et al.《A jump model for regime identification》（Annals of Operations Research）；Nystrup, Kolm & Lindström《Feature selection in jump models》（ESWA 2021, 184:115558——sparse JM "outperforms all other methods, remarkably robust to noise"）；Shu & Kolm (2024, J. Asset Management——JM 信号下行控制优于 HMM 与买入持有)；Zhang & Kolm arXiv:2402.05272（JM 配置优于 HMM）。
- 开源：`jumpmodels`（PyPI v0.1.1, 2024-10；GitHub Yizhan-Oliver-Shu/jump-models，171★，Apache-2.0，Princeton Mulvey 组；JM/CJM/SJM 三型，sklearn 风格）。
- 【诚实注】各文为定性结论+夏普改善，未核实到统一 SOTA 胜出数字。

## 5.3 非参数、深度与 A 股近作（2024-2026）

- **Sticky HDP-HMM**（Fox et al. 2011, Ann. Appl. Stat. 5(2A):1020-1056）：态数自动学+自粘性抑制碎片切换；但可用实现全是 MCMC（pyhsmm 停更/bnpy 停更/Bayesian-HMM 88★），日频 PIT 滚动生产太重——**工程结论：用跳变惩罚近似 sticky，不引 MCMC**。
- **DS³M** deep switching SSM（arXiv:2106.02329，刊 Int. J. Forecasting 2025）：比 HMM 基线给出更长更真实的 regime 持续期；基线族=Deep Markov Model（Krishnan et al., AAAI 2017）。
- **SSGA**《Decoding Market Regimes with ML》(2025)：1995-2024 美股四态 ML 分类。
- **Pang & Lin (2025, Frontiers in Physics)——A股数据，本勘查最贴近我们的一篇**：沪深300 滚动相关矩阵→MDS 降维→K-means 聚 5 态；**转移矩阵近似三对角**（状态只在相邻态间跳，跳变罕见）——"灰度应沿相邻态平滑衰减而非二值翻转"的数学依据；高相关态对应 2015 崩盘；崩盘预警精确率 96.4%/召回 96.8%，优于 VIX/谱方法/吸收率基线。
- LLM：Market Regime Council（Pei 2026, arXiv——多智能体 LLM+Shapley 信用分配做 regime 分类）——早期，未成体系；专门 LLM regime 分类文献仍稀缺【搜 abundantly，宁缺勿滥】。
- 校准：Brier/CRPS 是标准（**仓内 B1 校准/B2 CRPS 已有=行业标准做法**）；conformal 用于 regime 置信度：未查到代表作（缺口，可作研究性附加不进关键路径）。

# 6. 机构实践画像

| 机构 | 方法 | 用途 | 可借鉴点 |
|---|---|---|---|
| Two Sigma (2021, 官网) | GMM 对 17 因子收益截面聚类→4态（Steady State/Crisis/Inflation/Walking on Ice） | **描述性**：压力测试与组合韧性，作者明言"非预测工具" | 对特征截面而非价格聚类；簇数交叉验证；输出概率不输出硬标签 |
| S&P DJI Dynamic VEQTOR (2009-) | VIX vs 其 2周/6月均值→三档状态机，周再平衡 | 规则化指数产品 | **波动率分档+状态机全公开**——"规则骨架"的最硬公开样本 |
| AQR | 12m 动量符号+多窗口趋势分数；Levine & Pedersen (FAJ 2016) | 趋势跟随过滤 | **主流滤波器高度相关、无显著更优**——选型性价比低，多窗口混合即可 |
| Man AHL | ML 2014 起实盘（与 Oxford-Man 合作） | 趋势产品内核 | 【未直核】regime/meta-labeling 具体篇目未查到，不列名 |
| Fidelity | 概率模型标经济四阶段→行业超配概率地图（1962 起） | 板块配置 | 板块状态**依附宏观时钟**，不独立建模 |
| Dorsey Wright (Nasdaq) | 板块相对强度排名+点数图，规则全公开 | 板块轮动 | **板块自身状态独立建模的最硬公开样本**（横截面相对强度路线） |
| BlackRock / MSCI | 股债相关性 regime／增长×通胀因子归因 | 战略配置 | 方向性；无日频方法论文档公开【未直核】 |
| SG Trend Index 成分 CTA | 【未直核，专有】 | — | CTA 通行公开面：多窗均线交叉+1-12m 时序动量+vol targeting（~10% 年化常见档） |
| Merrill 投资时钟 (2004) | 增长×通胀四象限→资产/行业轮动 | 宏观 regime 原型 | QE 时代映射失真批评（二手）；象限切换无显著性检验 |

- **多周期仲裁的行业答案**：主流=**多窗口信号加权混合**（AQR/AHL 公开页），"高层定向+低层择时"硬分层未找到机构一手 SOP（更接近零售/从业者书惯例）。→ 我们的多周期设计建议采"多窗口连续分数+可选层级约束"，见 §11 问题2。
- **meta-labeling 采纳链**：AFML (2018)→Hudson & Thames/Joubert (SSRN 2022 理论框架)→Thumm (PM Research 2023 集成)→QuantConnect《Why Meta-Labeling Is Not a Silver Bullet》(2023-01)；**无大型机构公开署名在用**；regime 变量作 meta-model 特征是有据可循的组合方向（SSRN 已有"Regime Shift and the Limits of Supervised Meta-labelling"一类工作）。

# 7. 开源生态选型表

星数/活跃度均经 GitHub API 2026-10-13 当日核实，非凭记忆。

| 仓库 | ★ | 活跃 | 许可 | 定位 | 可借性 |
|---|---|---|---|---|---|
| deepcharles/ruptures | ~~2,096~~ | ~~2026-10 活跃~~ | BSD-2 | 离线变点全家桶（PELT/KernelCPD/Binseg/…） | **直接用**（P3 离线标注+参数校准）【更正 2026-10-13 总包核验车道：星数/活跃度原记失准——deepcharles/ruptures=1,689★ 且 2025-01 后停推，主仓已迁 centre-borelli/ruptures=2,486★、2026-03 活跃、BSD-2 不变；§15 链接同步改指新主仓】 |
| Yizhan-Oliver-Shu/jump-models | 171 | 2025-01 | Apache-2.0 | JM/CJM/SJM，sklearn 风格（Nordea 系论文对应） | **重点候选**（状态引擎，自带持久态+灰度语义） |
| sktime/sktime | 10,063 | 2026-10 极活跃 | BSD-3 | detection 模块（HMM/Binseg/ClaSP/CROPS/CAPA…）统一 fit/predict | **直接用**（多检测器横评集成层） |
| hmmlearn/hmmlearn | 3,437 | 2024-10 | BSD-3 | HMM 基础库（官方声明 limited-maintenance） | 直接用（仓内已用）；注意停更风险 |
| facebookresearch/Kats | 6,496 | 休眠（仅兼容性提交） | MIT | CUSUMDetector/BOCPD 等单文件可摘 | 移植思想/摘模块（依赖树陈旧勿整库引） |
| kieranjwood/slow-momentum-fast-reversion | 278 | 2026-03 | MIT | JFDS 2022 官方码：在线 CPD"位置+严重度"嵌入深度动量网络，50 期货组合 Sharpe+1/3 | **移植思想**（拐点输出三元组与我们需求直接同构） |
| stumpy-dev/stumpy | 4,161 | 2026-10 | BSD-3 | matrix profile；官方语义分段教程（Fluss） | 移植思想（拐点候选产生器/横盘段识别） |
| LSEG 3-method blueprint | 64 | 2023 | 自有 | HMM+k-means+GMM 三法横评 SPY（含可跑码） | 参考实现（三法横评框架可搬） |
| tubakhxn/Market-Regime-Detection-System | 114 | 2026-02 | MIT | SPY bull/bear/sideways 三态（与我们目标几乎同构） | 参考骨架（研究脚本级） |
| issaz/signature-regime-detection | 42 | 2023 | — | path signature+MMD 非参数在线 regime（Horvath & Issa 2023） | 移植思想（多维/非马尔可夫场景） |
| hudson-and-thames/mlfinlab | 4,939 | 冻结（README 自述仅收 issue） | 自定义 | trend-scanning 等已转付费门户 | 不适用（按论文自实现；无高星开源替身） |
| mattjj/pyhsmm / bnpy / Bayesian-HMM | 579/235/88 | 停更 | MIT | sticky HDP-HMM MCMC 实现 | 不适用（太重，PIT 生产不可行） |
| vnpy / abu / qlib | 45.8k/18.9k/49.3k | 活跃/停更/活跃 | MIT/GPL-3/MIT | 中文生态三库逐一核实：**均无 regime/state 层**（qlib 最近邻=DDG-DA 滚动重训） | 不适用；**abu GPL-3.0 传染性——禁止引代码** |

- **结论**：ruptures（离线标注）+ jumpmodels（状态引擎）+ Kats 摘 BOCPD（在线信号）+ sktime（横评集成）即可搭全栈；trend-scanning 按论文自实现；**中文生态确认空白——自建即差异化**。

# 8. A股适配与中文实践

## 8.1 牛熊年表锚点（可作 P3 对照集）

998.23 (2005-06-06)→6124.04 (2007-10-16)；1849.65 (2013-06-25 钱荒底)→5178.19 (2015-06-12)；2440.91 (2019-01-04)→3731.69 (2021-02-18)。来源：人民网《中国经济周刊》2020-12-15／上海统计局年鉴。**无单一权威定义**——通行=美式 ±20% 技术阈值+大级别按"翻倍级涨幅+持续一年以上+政策/估值拐点"人工划定，各券商策略报告划分互有出入【具体研报篇目未核到，见 §14】。

## 8.2 阈值适配

Yang (2025, Tilburg)：±20% 对 A 股"过于保守"（会漏 2013、2019 级中级行情）→ 需按 A 股波动放阈值。**结论：阈值参数是 A 股自标定项（P2 预冻结+留证），不是文献可抄的定数。**

## 8.3 "结构市"启示

本土"结构市/慢牛"概念=指数横向+个股/行业单边——**状态层必须"标的自身态"与"截面分布"双输出**（指数判横向的同一天，一半行业可以判单边）。与仓内广度帧资产（advance/ breadth）正好衔接。

## 8.4 板块：公开文献空白=我们的增量

中文卖方行业轮动主流=横截面相对排名（动量/景气/资金流）+拥挤度风控滤波；**未见任何公开工作对"板块自身状态"（而非排名）独立建模**；英文侧最硬=Dorsey Wright 相对强度（§6）。→ 板块状态标注=差异化增量。拥挤度指标（换手分位/估值分位/持仓集中度：MSCI 微盘拥挤报告、SSRN 7269512 量化拥挤）可作"单边态置信度衰减因子"。

## 8.5 个股：可行 + 可标注性过滤

- 先例：Chi et al. (2016) 对指数与**个股**同法标注（可行性直接证据）。
- 操纵文献：Titman, Wei & Zhao (JFE 2022, 公司行为操纵)；Gul-Kim-Qiu (2010) 股价同步性作为控盘代理；Liu et al. (2024, IEEE，389 起证监会操纵处罚案例训练检测器)。【Jian & Zhang 2009 庄股专文未核到原文，不背书】
- 防坑共识：高控盘代理=极端换手/小流通盘/收盘价异动/高同步性/龙虎榜席位集中 → 处置=**前置"可标注性过滤器"，不过关者输出"数据不可信"而非强行给状态——"不可标注"立为状态枚举一态**。
- 中文卖方：华西证券"HMM 模型择时及配置策略"（二手引用，原文需慧博/东财人工核）；华泰/招商/广发/兴业/海通等具体篇目在线未核到——**不编标题**，留 §14 人工补查。

# 9. 跨标的泛化：同一引擎，四个标的面（回应 Owner 第 1 问）

| 标的面 | 可行性 | 校准差异 | 关键防线 |
|---|---|---|---|
| 大盘宽基 | ✅ 文献最厚（P-S/L-T/VEQTOR 全是指数层） | 主标定集（§8.1 锚点年表） | 钉死标的定义（§11 问题1） |
| 板块/行业指数 | ✅ 文献空白=增量 | 阈值按行业波动分组标定；行业样本更短 | **板块自身态**与**相对大盘态**分开输出（结构市证据 §8.3） |
| 个股 | ✅ 有先例，但分布更厚尾+操纵污染 | 更短记忆窗+更宽阈值 | **可标注性过滤→"数据不可信"态**；防同义反复（价格衍生量喂形态判别） |
| （延伸）ETF/港美 | 原则同 | 各自标定 | 交易时段/制度差异 |

- **架构含义**：引擎="特征层+状态机+灰度+变点检测"四件通用件；每个标的面只换**参数组**——参数组分面预冻结，与仓内"判据预冻结+按域分级"纪律同构。Owner 预判"个股应该也可以"成立，但必须带过滤器，理由是操纵股的趋势持续性是人为的，状态机学到的是控盘行为不是市场形态。

# 10. 状态 vs 信号：职责分层（回应 Owner 第 2、3 问）

- **状态=nowcast（当下切片）**：{单边↑, 单边↓, 横向, 数据不可信} × 灰度∈[0,1]。供给考试条件轴（横截面切片：某卡只在"大盘=单边↑ ∧ 灰度≥θ"的日子开考）。全标的覆盖、无 unrouted 死角（治仓内 41.9% 同类缺口）。
- **信号=event（转移预测）**：拐点三元组=**位置/方向/严重度**（Wood 系"position+severity"输出设计与我们需求直接同构，JFDS 2022）。理论预算=虚报率换延迟（§4.1）。事件驱动供给卡与状态切换触发器。
- **分层纪律**：两者共享特征层，**判据分别冻结**；灰度口径分开——状态灰度=后验置信度（"我多确定现在是横向"），信号灰度=转移概率/严重度（"横向快结束了"）。混用会把两个不同的命题搅在一起。
- 拓扑约束（Pang & Lin 2025 三对角转移实证）：**状态机拓扑要先钉**——横向邻接双单边；单边↑↔单边↓直接互转须经横向或给更高门槛（进 §13 裁决项4）。

# 11. 七个 P2 问题的文献答案对照表

| # | 问题 | 文献/行业主流 | 建议默认（**均待Owner裁决**） | 备选 |
|---|---|---|---|---|
| 1 | 大盘标的钉哪个 | 机构对"所交易标的本身"建模；广度作特征不作目标 | 主目标=沪深300 或中证全指（P2 钉一个+卡面披露）；等权全A/广度帧=特征腿 | 双标的并行各出各卡 |
| 2 | 多周期仲裁 | 多窗口加权混合（AQR/AHL）；硬分层无机构一手 SOP | 日/周各出态+灰度；冲突时**周态作日态的方向先验约束**（层级是先验不是裁决） | 纯分数混合不分层 |
| 3 | 灰度值定义 | 三种量分属不同模型：后验置信度（HMM/jump）／转移概率（BOCPD/Shiryaev）／强度分（trend-scanning \|t\|） | **双轨制**：状态灰度=模型后验（主轨），强度灰度=回归 t 值（辅轨）；各自过 B1 校准/B2 CRPS；卡面声明用哪轨 | 单轨后验 |
| 4 | 最小段长/确认延迟 | P-S 双门槛（时长+幅度）+quickest detection（ARL 约束定延迟） | 周层=P-S 参数换算并按 A 股重标（P2）；日层=BOCPD/CUSUM，**先钉 ARL 虚报率预算，延迟是结果** | 全规则 CUSUM 法 |
| 5 | 多重比较校正 | White Reality Check／Hansen SPA／Deflated Sharpe（LdP 系） | 信号池入场=预注册假设卡（引仓内 recal 协议先例）；按池规模做 SPA/DSR 校正后才许进 P3 | Bonferroni/BH 简易版 |
| 6 | PIT 滞后面 | trend-scanning span 闭合／P-S censoring 右端滞后／BOCPD 天然在线 | 三源各自滞后天数钉死+卡面披露（复用 PIT_TAIL_LAG 机制）；实时指示器只认已闭合 span | — |
| 7 | N 值（预测期） | trend-scanning 自适应窗（训练标签）；行业按持有期对齐 | 按考试卡持有期分档钉死（如 5/10/20 日）；自适应窗只用于训练标签生成，不进实时面 | 全自适应 |

# 12. 与仓内资产的衔接点（不推倒重来清单）

1. **regime 包（46 py）**：特征层（MOD-REGIME-002 FEATURE_NAMES）、walk-forward 季度重拟合、锚定重排（裁定#304）、B1 校准/B2 CRPS/A1-A4/C1 验证框架**全复用**——两态层建其上：以"7 维概率"为输入之一，做语义重排+全交易日覆盖。
2. **D 族冻结稿**（draft_for_ruling）：§3.1 r1/r2 不路由与 §3.3 两源分歧 21.09%，由两态层的"全标的覆盖+唯一宏观轴"方案接管（接管声明进 §13 裁决项8）。
3. **market_state.py 词表（SH-VOCAB-001）**：两态词表（单边↑/单边↓/横向/数据不可信+灰度语义）走 state_vocabulary_registry 登记；**预先给出与 7 态/四档/六段/盘中五态的映射表**，避免第 29 套词表。
4. **condition_package**（情绪灰度×大盘状态，Owner 2026-09-23 夜裁①分层口径）：两态输出作为其大盘腿升级，**不另立平行条件轴**。
5. **PIT 机制**：sixphase-v1 的 PIT_TAIL_LAG／CLOSED_BOOK_CUTOFF／warmup／重放幂等（recal 协议 §5）直接继承为新层重建资格判据。
6. **裁定前置**：#229/#230"态层=风险分档、方向判别归因子层"的职责划界需立新裁定反转/扩界（§13 裁决项1）——**这是开工的先决门**。

# 13. 需 Owner 裁决清单（P2 呈批预清单）

| # | 裁决项 | 选项（**建议默认加粗**） |
|---|---|---|
| 1 | **#229 职责反转裁定** | **立新裁定：态层新增"形态向"职责，原风险分档职责保留并行**；或维持 #229、两态层全部下沉因子层 |
| 2 | 主目标指数 | **沪深300**／中证全指／双标的并行 |
| 3 | 灰度主口径 | **双轨（后验主+强度辅）**／单轨后验 |
| 4 | 状态机拓扑 | **横向邻接双单边；单边↑↔↓须经横向或高门槛**／全连通 |
| 5 | ARL 虚报率预算 | 数值待 P2 按历史拐点密度反推后呈批（不自拟） |
| 6 | 信号池校正规则 | **SPA/DSR**／简易 BH |
| 7 | 个股"数据不可信"态 | **确认入枚举**／个股暂不做 |
| 8 | D 族接管声明 | **3.1/3.3 由两态层接管，冻结稿同批改挂**／两线并存分轴 |
| 9 | 多周期仲裁 | **周态作日态方向先验**／分数混合不分层 |

# 14. 勘查缺口（人工补查清单）

1. 券商金工原文：华泰/招商/广发/兴业/海通/国盛/东方"市场状态/牛熊划分/趋势-震荡判别"篇目——慧博/东财研报库人工检索（在线引擎不可达）。
2. P-S 原文 terminal censoring 精确月数；"15% 豁免"有无原文依据（原文 paywalled，现口径经 bbdetection+SSRN 3105209 交叉核实）。
3. trend-scanning 的 SSRN 编号与最终权威出处。
4. jump model 论文期刊 venue 核实（ESWA 2020 说以 jump-models 包 README 为准）。
5. SG Trend Index 成分内部过滤规则（专有，预计不可得，止念）。
6. Jian & Zhang (2009) 庄股专文原文核实。
7. MDPI Forecasting（Tian, Kalman+隐状态 CSI300）403 未开，补核。

# 15. 来源清单

## 学术

- Pagan & Sossounov 2003, JAE 18(1):23-46, DOI 10.1002/jae.664【原文 paywalled，参数经二手交叉核实】https://onlinelibrary.wiley.com/doi/10.1002/jae.664
- bbdetection R 包（P-S 参数实现：window=8, bull=15, bear=6, percent=20）https://cran.r-project.org/web/packages/bbdetection/bbdetection.pdf
- SSRN 3105209（P-S 规则复述源）https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3105209
- Bry & Boschan 1971, NBER TP20 https://www.nber.org/books-and-chapters/cyclical-analysis-time-series-selected-procedures-and-computer-programs
- Lunde & Timmermann 2004, JBES 22(2):273-287 https://www.tandfonline.com/doi/abs/10.1080/07350010314424000
- Hanna 2018, IRFA 55:93-110 https://www.sciencedirect.com/science/article/abs/pii/S1057521917301539
- Z. Li, Palgrave 章节（中国 20 牛熊段）https://link.springer.com/chapter/10.1057/9781137464699_3
- Chi et al. 2016, SEF 33(4), DOI 10.1108/SEF-01-2015-0036【Emerald 付费墙】
- Page 1954 https://www.jstor.org/stable/2332556 ｜ Lorden 1971 https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-42/issue-6/Procedures-for-Reacting-to-a-Change-in-Distribution/10.1214/aoms/1177693235.full ｜ Shiryaev 1963 https://epubs.siam.org/doi/10.1137/1108004 ｜ Veeravalli & Banerjee 综述 https://arxiv.org/abs/1210.5552
- BOCPD https://arxiv.org/abs/0710.3742 ｜ robust BOCPD, ICML 2023 (PMLR 202:642-663)
- PELT https://arxiv.org/abs/1101.1438 ｜ kernel CP (JMLR 20, 2019) ｜ ruptures 综述（Signal Processing 167:107299）https://centre-borelli.github.io/detection/
- trend-scanning 实现文档 https://mlfinpy.readthedocs.io/latest/Labelling【SSRN 编号未核】
- Hamilton 1989, Econometrica 57(2):357-384 ｜ HMM 可识别性 https://mc-stan.org/docs/stan-users-guide/hmm.html
- Jump models：ESWA 2021 (184:115558) https://www.sciencedirect.com/science/article/pii/S0957417421009647 ｜ Zhang & Kolm https://arxiv.org/html/2402.05272v1 ｜ Shu & Kolm 2024 SSRN 4719989 ｜ PyPI https://pypi.org/project/jumpmodels/
- Sticky HDP-HMM：Fox et al. 2011, Ann. Appl. Stat. 5(2A):1020-1056
- DS³M https://arxiv.org/html/2106.02329v3（IJF 2025）｜ SSGA 2025 https://www.ssga.com/library-content/assets/pdf/global/pc/2025/decoding-market-regimes-with-machine-learning.pdf ｜ An et al. 2025, Heliyon https://www.sciencedirect.com/science/article/pii/S2589004225001841
- **Pang & Lin 2025, Frontiers in Physics（A股 5 态+三对角转移+崩盘预警）** https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2025.1647667/full

## 机构

- Two Sigma: Botte & Bao, 2021 https://www.twosigma.com/articles/a-machine-learning-approach-to-regime-modeling/
- Levine & Pedersen 2016, FAJ 72(3) https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2579674 ｜ AQR TSMOM (JFE 2012) https://www.aqr.com/Insights/Research/Journal-Article/Time-Series-Momentum ｜ A Century of Evidence (JPM 2017) https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing
- Man AHL https://www.man.com/insights/the-rise-of-machine-learning ｜ https://www.man.com/capabilities/trend-following
- S&P DJI Dynamic VEQTOR https://www.spglobal.com/spdji/en/indices/strategy/sp-500-dynamic-vektor-index/【403，细节自方法论文档转述，未逐条复核】
- Fidelity 板块时钟 https://www.fidelity.com/learning-center/trading-investing/markets-trends/business-cycle-indicator-map ｜ Dorsey Wright https://dorseywright.nasdaq.com/docs
- meta-labeling：AFML (Wiley 2018) ｜ https://github.com/hudson-and-thames/meta-labeling ｜ Joubert SSRN 2022 ｜ Thumm, PM Research 2023
- Merrill 投资时钟 2004（镜像检索命中）；二手评述 macro-ops.com／moomoo.com
- Quantpedia《Defining Market Cycles Out of Sample》https://quantpedia.com/defining-market-cycles-out-of-sample ｜ 《Avoid Equity Bear Markets…》三部曲（2023-03 起，标题核实、正文反爬未展开）

## 开源（均经 GitHub API 2026-10-13 核实）

- https://github.com/centre-borelli/ruptures （主仓，2,486★ 2026-03 活跃；deepcharles/ruptures 为旧址 1,689★ 停推——2026-10-13 核验更正）｜ https://github.com/Yizhan-Oliver-Shu/jump-models ｜ https://github.com/sktime/sktime ｜ https://github.com/hmmlearn/hmmlearn ｜ https://github.com/facebookresearch/Kats ｜ https://github.com/kieranjwood/slow-momentum-fast-reversion ｜ https://github.com/stumpy-dev/stumpy ｜ https://github.com/LSEG-API-Samples/Article.RD.Python.MarketRegimeDetectionUsingStatisticalAndMLBasedApproaches ｜ https://github.com/tubakhxn/Market-Regime-Detection-System ｜ https://github.com/issaz/signature-regime-detection ｜ https://github.com/hudson-and-thames/mlfinlab ｜ https://github.com/mattjj/pyhsmm ｜ https://github.com/jamesross2/Bayesian-HMM ｜ https://github.com/vnpy/vnpy ｜ https://github.com/bbfamily/abu ｜ https://github.com/microsoft/qlib

## A股/中文

- 人民网《中国经济周刊》2020-12-15（30年3次大牛市年表）http://paper.people.com.cn ｜ 上海统计局年鉴（6124.04）https://tjj.sh.gov.cn
- Tilburg 2025（P-S 阈值对 A 股过于保守）arno.uvt.nl【检索摘要可见，原文未开】
- STEMM Press 2026-01（BERT 行业轮动）http://www.stemmpress.com/uploadfile/202601/7d9f9eb977576c0.pdf
- SSRN 7269512（量化拥挤）https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7269512
- Titman, Wei & Zhao, JFE 2022 ｜ Gul, Kim & Qiu 2010, JFE ｜ Liu et al. 2024, IEEE（389 起处罚案例）
- 华西证券 HMM 择时【二手引用】https://www.scribd.com/document/848024790/

## 尾注

- 勘查车道：4 条并行研究线（学术/机构/开源/A股），全程"查不到明说"纪律；星数与活跃度经 GitHub API 当日核实。
- 本册未做任何判据裁定；全部参数性"建议默认"均为文献主流的转述+仓内先例的映射，裁决权在 Owner（§13）。
- **核验更正记录（2026-10-13 总包 P0②③ 核验车道，9 仓内断言＋5 外部抽检）**：①§7 ruptures 行星数/活跃度更正（见该行内注，GitHub API 双仓实读）；②bbdetection 参数补双源口径（CRAN PDF 手册 window=8/bull=15/bear=6/percent=20 与 R 源码示例 setpar_dating_alg(4,6,4,16,20)/(4,6,5,15,20) 两档并存，P2 引用时双引防单一二手源）；③其余 8 条仓内断言（regime 46 py 实数一致、#229/#230/#304 语义相符、SH-VOCAB-001、condition_package 逐字吻合、B1/B2、PIT_TAIL_LAG/recal 协议、41.9% 出处、D 族 21.09%）与 4 条外部锚点（jumpmodels 171★/v0.1.1/Apache-2.0、Pang & Lin 96.4%/96.8%、BOCPD、P-S DOI）全部坐实，零误差。
