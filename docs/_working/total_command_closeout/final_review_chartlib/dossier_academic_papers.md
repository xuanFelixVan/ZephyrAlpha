---
ttl: task_bound
completes_when: "图形信号施工引用出处可在仓内 grep 命中（G-76 判据）"
---

> 来源：外部终审交付目录原件 `dossier_academic_papers.md`（2026-09-26 终审会话定稿），本仓内改名只为避开非 ASCII 路径与编码门；正文逐字节未改。
> 原件 sha256：1ecac5b03d12914bf6873e1f7295c4d99643b4b3e3c2c6bd50cbc77df741f095
> 口径律：本目录是**终审修正层**；凡与 `02_field_corrections_and_new_cases.md` 冲突以 02 册为准，本目录只在其上打补丁与增波，不改写既有 27 册正文。

# 学术证据案卷：量化系统技术图形库终审（research-academic）

> 调研日期：2026-09-26。检索工具：WebSearch / WebFetch（真实检索，共 12 次检索，每主题 2-3 组中英文关键词）。
> 纪律声明：所有条目均附本次实际检索到、可访问的 URL/DOI；未检索到的明确写"未检索到"，无任何编造引用。
> 本案卷只出证据，不出裁定。证据强度分级：强（顶级期刊同行评审/大样本）、中强（同行评审或权威机构）、中（预印本/业界研报/二手引证）。

---

## §零 执行摘要（供终审快速引用的六条核心证据）

1. **规则法K线形态的学术基线是"无效"**：Marshall-Young-Rose (2006, JBF) 对道指 28 形态的 bootstrap 检验未发现任何形态扣成本后显著盈利；Sullivan-Timmermann-White (1999) 显示技术规则在 1980 年代中期后失效。TA-Lib 61 形态若单独接入策略考试，文献预期其名义夏普主要来自噪声。
2. **但"形态+上下文/机器过滤"在 A 股有正边际**：Lin et al. (2021, PLOS ONE) 用机器学习过滤的两日K线形态在 A 股全样本（2000-2020）上年化 36.73%、夏普 0.81，计入 0.2% 成本后仍盈利——这是对"信号库接入考试"最直接的 A 股合法性证据。
3. **Owner 的"多级别共振"假设有可形式化的学术工具**：Curme et al. (2015, QF) 的 Bonferroni/FDR 校正滞后相关网络 + Hayashi-Koike (2020) 的尺度逐层 lead-lag 估计器，把"小级别是否领先大级别"变成可检验统计量；Fang et al. (2025, arXiv) 在 A 股 1,283 只股票上证实强耦合对在 1 分钟尺度 lead-lag 最显著。
4. **"小级别领先"存在但有边界**：Gao-Han-Li-Zhou (2018, JFE) 的日内动量（首半小时预测末半小时）是标杆正向证据；澳洲市场未复现（Ho et al. 2021）提示效应依赖流动性；Curme et al. 显示 2002→2012 可验证链接减少，警示 A 股小级别信号会随市场有效性上升而衰减，考试应滚动进行。
5. **3700+ 格考试系统必须用 RC/SPA/StepM/DSR 族校正**：White (2000)、Hansen (2005)、Romano-Wolf (2005)、Hsu-Hsu-Kuan (2010)、Bailey-López de Prado (2014) 构成完整工具链；工程上最可落地的是 DSR（代入有效试验数与非正态修正），且必须披露全部尝试过的格子。
6. **A股特有层有强证据**：涨跌停板行为经济学（Jiang & Li 2026，149,589 次涨停事件 + 2020 创业板改革自然实验）与缠论券商级量化回测（中泰 2022：一类买点+大盘择时胜率 76.53%）存在；但**缠论无同行评审文献**，其"小转大"（小级别背驰引发大级别转折）恰是 Owner 假设的机会面与风险面所在。

---

## §一 各主题发现表

### 主题1：K线形态统计有效性（经典与最新）

| # | 发现 | 论文/来源 | URL/DOI（实际检索到） | 证据强度 |
|---|---|---|---|---|
| 1.1 | 28种K线形态在道指成分股（1992-2001）经 bootstrap 模拟检验，**无单一形态在扣除交易成本后有统计显著利润**；看涨/看跌形态后的收益与随机不可区分 | Marshall, Young & Rose (2006), "Candlestick technical trading strategies: Can they create value for investors?", *Journal of Banking & Finance* 30(8): 2303-2323 | 引证页：https://ideas.repec.org/a/taf/appiec/v48y2016i35p3345-3354.html （含完整书目）；综述：https://alpha-suite.org/blog/candlestick-patterns-evidence | 强 |
| 1.2 | 同团队后续结论：K线择时对美股大盘股"总体不盈利"，但作者明确保留"**不能排除与其他择时技术互补**"的可能——这是给"形态+其他条件组合"留的学术口子 | Marshall, Young & Rose (2007), "Market timing with candlestick technical analysis", *Journal of Financial Transformation* 20: 18-25 | https://ideas.repec.org/a/ris/jofitr/0834.html | 强 |
| 1.3 | Bulkowski 统计（美股 1991-2020 约 103 形态、26,518 样本）：**全形态平均胜率约 51.3%（掷硬币区间），仅 8/103 超过 60%**；Doji 约 49.7%。最优形态（Three-line strike 84%、Three black crows 78%、Evening star 72%）多为罕见形态 | Bulkowski, *Encyclopedia of Candlestick Charts*（书，Wiley 2008）+ thepatternsite.com 数据页 | https://thepatternsite.com/CandlePerformers.html ；https://www.thepatternsite.com/KirkInterview.html ；统计汇总：https://planmyretire.com/university/trading/deep-dives/candlestick-patterns.html | 中强（非同行评审但样本极大、方法论公开） |
| 1.4 | Bulkowski 工程结论：**高（tall）形态显著优于矮形态**（上行突破 86%、下行突破 97% 的情况）；"busted pattern"（破位后 10% 内反转）本身可作交易信号；RSI 等指标"数据越多表现越差"的教训 | 同上（Bulkowski 访谈） | https://www.thepatternsite.com/KirkInterview.html | 中 |
| 1.5 | Horton (2009)：星/乌鸦/十字星在美股无优于随机入场的预测力；Fock et al. (2005)：DAX 期货日内 19 形态**即使不计交易成本**也大多不显著优于随机交易基准；叠加其他技术指标后收益提高但仍不显著 | Horton (2009), *QREF* 49(2): 283-294；Fock, Klein & Zwerger (2005)（经 Stockholm 大学 kandidat 报告文献综述页核实） | https://kurser.math.su.se/pluginfile.php/20130/mod_folder/content/0/Kandidat/2023/2023_18_report.pdf?forcedownload=1 | 中强（二手引证） |
| 1.6 | **低效率市场反例**：台湾市场"形态确认入场、反向形态确认离场"策略下部分形态显著盈利（Lu, Shiu & Liu 2012；Lu 2014, *Pacific-Basin Finance Journal* 26: 65-78）；泰国市场整体不盈利（Tharavanij et al. 2017, *SAGE Open*） | 上述各文 | 引证页：https://ideas.repec.org/a/taf/appiec/v48y2016i35p3345-3354.html ；https://ideas.repec.org/a/ris/jofitr/0834.html | 中强 |
| 1.7 | **A股大样本实证（对本系统最直接相关）**：北航团队对 2000-2020 全部中国股票，用 4 种机器学习方法 + 11 类特征对任意两日/三日K线组合做形态识别（PRML 模型）：过滤后的两日K线形态预测次日方向，TOP10 策略**年均收益 36.73%、夏普 0.81、信息比率 2.37**，计入 0.2% 交易成本后仍盈利；市场同期最大回撤 52.28% 而组合回撤均 <40% | Lin, Liu, Yang, Wu & Jiang (2021), "Improving stock trading decisions based on pattern recognition using machine learning technology", *PLOS ONE* 16(8): e0255558 | https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0255558 ；DOI: 10.1371/journal.pone.0255558；全文镜像：https://pmc.ncbi.nlm.nih.gov/articles/PMC8345893/ | 强（同行评审、A股全样本、含成本） |
| 1.8 | 形式化方法：Hu, Si, Fong & Lau (2019) 提出K线形态分类的形式化方法（蜡烛参数空间 + 语法规则）；Caginalp & Laurent (1998) 用 MA3 趋势规则做受控检验，发现部分价格形态有（弱的）预测力 | Hu et al. (2019), *Applied Soft Computing* 84: 105700；Caginalp & Laurent (1998), *Applied Mathematical Finance* 5: 181-205 | 引证页：https://pmc.ncbi.nlm.nih.gov/articles/PMC8345893/（参考文献列表含两条全文信息） | 中强（二手引证） |
| 1.9 | 券商视角：西南证券对单K/双K/多K形态在A股做有效性测试（大阳线/倒锤线正面、射击之星/乌云盖顶负面等）；另一券商"情绪系数加权K线评分"因子 2012-2026 年化 26.22%、信息比率 1.54（样本内回测，无多重检验校正） | 西南证券《基于历史K线形态的因子选股研究》；《情绪系数加权个股K线评分的选股策略》 | https://www.fxbaogao.com/detail/4862659 ；https://stock.finance.sina.com.cn/stock/go.php/vReport_Show/kind/11/rptid/833305794559/index.phtml | 中（业界研报，样本内） |

**主题1小结**：规则法K线形态单独使用在成熟市场基本无效；A股作为散户占比高、效率较低的市场，形态经机器学习过滤/组合后存在可计成本的正边际（Lin et al. 2021 为最直接证据）。上下文条件（趋势/位置/量能）是文献共识的放大器。

### 主题2：深度学习图形识别（CNN/Transformer/GNN，2023-2026 重点）

| # | 发现 | 论文/来源 | URL/DOI | 证据强度 |
|---|---|---|---|---|
| 2.1 | 系统性消融研究（3种图像编码 × 5种图元配置 × 4种架构，Bitcoin/Ethereum/S&P500，2018-2024）：**4层简单 CNN 直接读原始K线图达 AUC 0.892，超过 ResNet18/EfficientNet-B0/Vision Transformer**；128×128 低分辨率、纯价格图（无成交量/均线）反而最优；ImageNet 迁移学习提升 4-16%；GradCAM 显示模型确实学到视觉形态特征 | "Visual Chart Representations for Cryptocurrency Regime Prediction: A Systematic Deep Learning Study" (2026), arXiv:2605.00875 | https://ar5iv.arxiv.org/html/2605.00875 | 中强（系统实验设计） |
| 2.2 | K线图→图像 + CNN/ResNet/VGG，台湾股市三分类准确率最高 **92%**（图像法开山作之一） | Kusuma et al. (2019), arXiv:1903.12258, "Using Deep Learning Neural Networks and Candlestick Chart Representation to Predict Stock Market" | https://arxiv.org/abs/1903.12258 （经 arXiv:2410.19291 的 RePEc 引证页核实：https://ideas.repec.org/p/arx/papers/2410.19291.html ） | 中 |
| 2.3 | GAF-CNN：把K线编码为 Gramian Angular Field 图像做形态分类（金融图像表征另一主流路线） | Chen & Tsai (2020), *Financial Innovation*, "Encoding candlesticks as images for pattern classification using convolutional neural networks" | 引证页：https://ideas.repec.org/p/arx/papers/2410.19291.html | 中强（同行评审） |
| 2.4 | **A股 4,454 只股票**：TS-OHLCT 图像（换手率替代成交量、周末时间分隔符）+ 多尺度残差/融合 CNN（MSR-CNN/SMSFR-CNN）：未来 5 天方向阳性预测值 **61.15%**、阴性 63.37%，回测总收益 165%；针对长序列图像过拟合问题设计多尺度分解 | Pei, Yan et al. (2024), arXiv:2410.19291 | https://arxiv.org/abs/2410.19291 ；https://ideas.repec.org/p/arx/papers/2410.19291.html | 中（预印本，A股大样本） |
| 2.5 | GNN 用于股票间结构（非单票图形）：异构 GNN（量价因子为节点、行业/共同持仓/共同覆盖为边）月频因子 RankIC 0.125、夏普 2.95；与 RNN 时序融合后 RankIC 0.131、夏普 3.40、多头超额年化 25.4% | 国内券商金工 GNN 系列研究（2024） | https://ima.qq.com/wiki/?shareId=348c40e103f10af3274324c2078c0234369b59723103b78744a4406f27fb732b ；东方证券 ASTGNN：https://www.sohu.com/a/782247849_121649707 | 中（业界研报，样本内） |
| 2.6 | 时空 GNN 时序综述（2024，arXiv:2410.22377）：GNN 同时建模变量间与时间依赖是主流方向；华泰金工综述确认 Transformer 注意力（iTransformer/Crossformer/Master）+ 分块（PatchTST 思想）为多变量协同与长序列建模新宠，level2 数据图像化 + ViT 用于微观结构 | "A Systematic Literature Review of Spatio-Temporal Graph Neural Network Models for Time Series Forecasting and Classification" (2024) | https://arxiv.org/abs/2410.22377 （经网易学术转载核实：https://www.163.com/dy/article/JI3O8VQJ0511PEBT.html ）；华泰综述：https://finance.sina.com.cn/stock/stockzmt/2026-01-23/doc-inhifvnk1177812.shtml | 中强（综述）/ 中（业界） |

### 主题3：多时间框架/多尺度分析（"跨周期共振"与"小级别领先大级别"）

| # | 发现 | 论文/来源 | URL/DOI | 证据强度 |
|---|---|---|---|---|
| 3.1 | **核心文献**：NYSE 100 大市值股日内 lead-lag 网络统计验证（Bonferroni + FDR 双重多重检验校正）：**采样频率越细（<30 分钟），统计显著的信息溢出链接急剧增多**；2002-2003 比 2011-2012 链接更多（市场有效性上升）。方法论上示范了"跨周期滞后相关如何统计验证" | Curme, Tumminello, Mantegna, Stanley & Kenett (2015), *Quantitative Finance* 15(8): 1375-1386（arXiv:1401.0462） | http://arxiv.org/pdf/1401.0462.pdf ；https://ideas.repec.org/p/arx/papers/1401.0462.html | 强 |
| 3.2 | **尺度逐层 lead-lag 估计器**（Daubechies 小波滤波，处理非同步高频数据、无需插值）：NASDAQ-100 实证发现**不同时间尺度上存在两类性质不同的 lead-lag 结构**——即"跨尺度共振"在方法上可分解、可估计 | Hayashi & Koike (2020), "Multi-scale analysis of lead-lag relationships in high-frequency financial markets", arXiv:1708.03992 | https://arxiv.org/pdf/1708.03992v4.pdf | 强（方法论） |
| 3.3 | **A股多粒度实证（与 Owner 假设同构）**：1,283 只 A 股、1/5/15 分钟 + 日线两阶段框架（日频相关/DTW/秩度量锁定强耦合对 → 高频互相关/Granger/回归检测 lead-lag）：**强耦合股票对在更细时间尺度上 lead-lag 更显著** | Fang, Wu & Tong (2025), "From Data Acquisition to Lag Modeling: Quantitative Exploration of A-Share Market with Low-Coupling System Design", arXiv:2506.19255 | https://arxiv.org/abs/2506.19255 ；https://ar5iv.arxiv.org/html/2506.19255 | 中（预印本，直接针对A股） |
| 3.4 | **日内动量（"早段领先晚段"的标杆证据）**：标普500 ETF 高频数据（1993-2013）：**开盘后第一个半小时收益预测最后一个半小时收益**，统计与经济意义均显著；在高波动日、高成交量日、衰退日、宏观新闻日更强；扩展到 10 只最活跃 ETF 均成立 | Gao, Han, Li & Zhou (2018), "Market intraday momentum", *Journal of Financial Economics* 129(2): 394-414 | https://ideas.repec.org/a/eee/jfinec/v129y2018i2p394-414.html ；DOI: 10.1016/j.jfineco.2018.05.009 | 强 |
| 3.5 | 外部效度警示：澳大利亚市场**未复现**日内动量（日交易笔数太少）——该效应依赖流动性/交易活跃度 | Ho, Lv & Schultz (2021), "Market intraday momentum in Australia", *Pacific-Basin Finance Journal* 65: 101499 | https://ideas.repec.org/a/eee/pacfin/v65y2021ics0927538x21000068.html ；DOI: 10.1016/j.pacfin.2021.101499 | 强 |
| 3.6 | 层次化 HMM 形式化"多尺度"：fHMM R 包（JSS 2024）实现**层次 HMM 联合建模多个时间分辨率的数据流**；Adam & Oelschläger (2020) 用 HHMM 联合建模月频成交量 + 日频对数收益（高盛股票 16 年）；Sandoval & Hernández 用 HHMM + 小波变换订单簿做日内 USD/COP 策略（zig-zag 特征） | Oelschläger, Adam & Michels (2024), *Journal of Statistical Software* 109(9)；Adam & Oelschläger (2020, IWSM)；Sandoval & Hernández (IEEE) | https://www.researchgate.net/publication/381142116_fHMM_Hidden_Markov_Models_for_Financial_Time_Series_in_R （DOI: 10.18637/jss.v109.i09）；HHMM 股票应用：https://scholar.google.ca/citations?view_op=view_citation&hl=en&user=C8WuHG4AAAAJ&citation_for_view=C8WuHG4AAAAJ:ufrVoPGSRksC ；IEEE：https://ieeexplore.ieee.org/document/7237178/authors | 强（JSS）/ 中强 |
| 3.7 | 小波增强 + 状态分层：BIST100/标普500/上证综指 2015-2025，三层 Daubechies-4 小波分解特征 + RF/SVR/LSTM/GRU，**三状态高斯 HMM 识别牛/熊/震荡后分层检验**：小波增强配置在各指数各算法上降低预测误差 20-40%，Diebold-Mariano 检验全局及各状态内均显著 | Okşak, Büyükkör & Sarıtaş (2025), "Wavelet-enhanced multimodel framework for stock market forecasting", *Borsa Istanbul Review* | https://sciencedirect.com/science/article/pii/S2214845025002108 | 中强 |
| 3.8 | Huth & Abergel：高频 lead-lag 关系在短时间尺度上更显著（多个尺度上检测） | Huth & Abergel (2011), HAL hal-00645685 | 引证页：https://ideas.repec.org/p/arx/papers/1401.0462.html | 中 |

### 主题4：事件研究/信号分层统计与多重检验方法论

| # | 发现 | 论文/来源 | URL/DOI | 证据强度 |
|---|---|---|---|---|
| 4.1 | **Reality Check**：形式化"数据窥探"（同一数据集反复用于推断与模型选择）；bootstrap 联合检验"全策略空间中最优者是否真跑赢基准"。Sullivan, Timmermann & White (1999) 用 RC 复检 Brock et al. (1992) 26 条规则：**DJIA 技术规则在 80 年代中期后失去预测力** | White (2000), *Econometrica* 68(5): 1097-1126；Sullivan, Timmermann & White (1999) | 方法论综述页（Glasgow 大学 eprints）：https://eprints.gla.ac.uk/246954/2/246954.pdf ；Nottingham 讲义：https://live-uk-uon.contensis.com/research/groups/grangercentre/documents/confs/paper-kuan-july-2009.pdf | 强（二手引证完整） |
| 4.2 | **SPA 检验**：White RC 过于保守（加入足够多劣质规则可把 RC 的检验功效压到零）；SPA 用样本依赖分布与标准化统计量提升功效。应用结论：**Hsu & Kuan (2005) 发现技术规则在年轻指数（NASDAQ、Russell 2000）上显著盈利、在成熟指数（DJIA、S&P500）上不盈利** | Hansen (2005), *Journal of Business & Economic Statistics* 23(4): 410-418；Hsu & Kuan (2005) | 同上 Glasgow eprints 综述页；https://www.st-andrews.ac.uk/~wwwecon/repecfiles/2/1302.pdf | 强（二手引证完整） |
| 4.3 | **Stepwise 检验（识别全部而非仅一个显著模型）**：Romano & Wolf (2005) StepM；Hsu, Hsu & Kuan (2010) Step-SPA。实证：9,120 条均线规则 + 7,260 条过滤规则——**ETF 上市前技术规则显著、ETF 上市后可交易版本上显著规则消失/大幅减少**（套利者交易掉了利润）；Qi & Wu (2006) 用 RC 检验 2,127 条外汇规则 | Hsu, Hsu & Kuan (2010)；Romano & Wolf (2005)；Qi & Wu (2006) | https://live-uk-uon.contensis.com/research/groups/grangercentre/documents/confs/paper-kuan-july-2009.pdf ；https://www.st-andrews.ac.uk/~wwwecon/repecfiles/2/1302.pdf | 强（二手引证完整） |
| 4.4 | **Deflated Sharpe Ratio（对 3700+ 格考试系统最直接的工具）**：DSR 同时校正（a）多重试验下的选择偏差——需代入试验次数与试验间平均相关（有效独立试验数公式）；（b）收益非正态。配套概念：Probabilistic SR、最小回测长度、最小业绩记录长度。作者演示：穷举策略空间后样本内夏普 1.04 的"最优"策略，样本外夏普仅 0.07；**未披露试验次数的回测一文不值** | Bailey & López de Prado (2014), "The Deflated Sharpe Ratio", *Journal of Portfolio Management* 40(5): 94-107 | https://www.ssrn.com/abstract=2460551 ；全文：https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf ；DOI: 10.2139/ssrn.2460551 | 强（直接检索到全文） |
| 4.5 | 回测过拟合概率族：Bailey, Borwein, López de Prado & Zhu 的"Pseudo-mathematics and financial charlatanism"（*Notices of the AMS* 61(5): 458-471, 2014）与"probability of backtest overfitting"（*Journal of Computational Finance* 20(4), 2017）；Harvey, Liu & Zhu (2016) 对数百个因子主张 t>3.0 门槛（*RFS* 29(1): 29-68）；配套教科书式总结见 portfoliooptimizationbook 第 8.3 节 | 上述各文 | 引证与总结：https://portfoliooptimizationbook.com/book/8.3-dangers-backtesting.html ；https://www.davidhbailey.com/dhbtalks/dhb-london-quant.pdf | 强（二手引证完整） |
| 4.6 | "信号×市场状态"条件矩阵的学术范式：多模型 ensemble-HMM 投票框架识别牛/熊/中性状态后，regime-aware 策略在 Russell 3000 与 S&P 500 ETF 上支持有效决策（*Data Science in Finance and Economics* 2025, 5(4): 466-501, DOI: 10.3934/DSFE.2025019）；结合 3.7（HMM 分层 + Diebold-Mariano 逐状态检验）构成"条件矩阵逐格检验"的方法论模板 | Rethyam Gupta et al. (2025)；Okşak et al. (2025) | https://www.aimspress.com/article/doi/10.3934/DSFE.2025019?viewType=HTML ；https://sciencedirect.com/science/article/pii/S2214845025002108 | 中强 |

### 主题5：趋势线/支撑阻力自动检测算法

| # | 发现 | 论文/来源 | URL/DOI | 证据强度 |
|---|---|---|---|---|
| 5.1 | **SR（支撑/阻力）水平统计显著存在的直接证据**：启发式发现算法在日内价格序列上找到的 SR 水平**能以统计显著性反转价格趋势**；**此前反弹次数越多的 SR 水平，再次反弹概率越高**；SR 强度随时间衰减（反弹概率递减）；SR 水平带来的暂时可预测性不能被 AR(1)（平稳或非平稳）解释——即不是伪象 | Chung & Bellotti (2021), "Evidence and Behaviour of Support and Resistance Levels in Financial Time Series", arXiv:2101.07410 | https://arxiv.org/abs/2101.07410 （https://ideas.repec.org/p/arx/papers/2101.07410.html ；全文 https://arxiv.org/pdf/2101.07410 ） | 中强 |
| 5.2 | 经典微观结构解释：Osler (2000) 证明汇市日内汇率对"整数位阻力/支撑"的服从，源于交易者停损单/止盈单聚集在整数价位（订单流聚类）——SR 水平有真实的订单流微观基础；Osler (2001) 进一步用订单数据解释技术分析为何"成功" | Osler (2000), "Support for resistance: technical analysis and intraday exchange rates", *FRBNY Economic Policy Review* (Jul): 53-68；Osler (2001), FRBNY Staff Report 125 | 引证页：https://ideas.repec.org/p/arx/papers/2101.07410.html | 强（二手引证） |
| 5.3 | 进化优化自动趋势线：PSO 优化支撑/阻力线参数用于算法交易：**自动生成的 SR 线单独使用不显著优于 Buy & Hold**；作者结论"作为多输入综合系统的输入之一时可能更好"——与 Marshall 2006 的"互补保留"措辞一致 | Yıldırım, Uçar & Özbayoğlu (2019), IEEE UBMYK/IISEC 2019, pp. 1-6 | https://ieeexplore.ieee.org/document/8965471/ ；机构库：https://gcris.etu.edu.tr/handle/20.500.11851/3853 | 中 |
| 5.4 | Pivot/ZigZag 类算法的学术使用范式：HHMM 高频策略文献以 **zig-zag 模式**（转折点序列）构造特征向量、以小波变换订单簿量能做观测，隐状态捕捉升/降趋势 regime；线性回归（最小二乘/最小绝对偏差/似然）+ 稳健回归（M-estimator）被用于趋势线参数估计（滑铁卢大学工程设计文档，工程实现参考） | Sandoval & Hernández (IEEE 7237178)；Univ. of Waterloo 工程文档 | https://ieeexplore.ieee.org/document/7237178/authors ；https://uwaterloo.ca/systems-design-engineering/smartshelf/stock-trend-technical-analysis-system | 中 |
| 5.5 | 分型（fractal）算法可追溯来源：缠论研报与学术 HHMM 文献均以"局部极值 + 确认规则"（等价于 Williams fractal / ZigZag 思想）作为结构识别的原子操作（见 §一主题6 中泰证券研报：分型→笔→线段→中枢的完整算法化）；A 股 T+1 制度对日内结构识别的影响（如周末效应与时间分隔符设计，见 2.4） | 中泰证券（2022）；Pei et al. (2024) | 见主题6/主题2 URL | 中 |

### 主题6：缠论量化与中国市场特有研究

| # | 发现 | 论文/来源 | URL/DOI | 证据强度 |
|---|---|---|---|---|
| 6.1 | **缠论完整算法化 + 大样本回测**：分型→笔→线段→走势中枢全部算法化，识别第一/二/三类买卖点形成闭环择时；上证50/沪深300/中证500 成分股 2010-01 至 2022-05 回测：**一类买点在沪深300 成分股上胜率 63.47%、盈亏比 3.25、单次闭环平均收益 5.45%；叠加大盘择时后胜率 76.53%、盈亏比 4.78、平均收益 9.46%**；报告自述"远超前三篇传统技术形态策略" | 中泰证券《技术分析算法、框架与实战之四：基于缠论形态学的择时策略》(2022) | https://stock.finance.sina.com.cn/stock/go.php/vReport_Show/kind/11/rptid/724251214428/index.phtml | 中（券商研报，样本内，无多重检验校正） |
| 6.2 | 缠论量化解析：按"包含关系→分型→笔→线段→中枢→走势类型"逐级算法化，用 MACD 面积/黄白线位置判别背驰定位一二三类买卖点，在上证指数 **5 分钟级别**走势上完整实现；作者同时指出缺陷：非标准背驰、最后中枢位置确定等主观残留 | 长江证券《量化视角下的缠论初步解析》 | https://vip.stock.finance.sina.com.cn/q/go.php/vReport_Show/kind/strategy/rptid/3415201/index.phtml | 中 |
| 6.3 | 券商回测汇总（二手）：长江——缠论三类买卖点作独立因子提供年化 4-6% 增量；山西证券——缠论策略回测收益 24.5%、夏普 2.34；2015-2024 某策略扣成本后胜率 57.8%、盈亏比 2.26。批判方观点：缠论"级别递归/走势终完美"具有事后可解释性（不可证伪风险），"小转大"（小级别背驰引发大级别转折）是最主要不确定性来源——**注意：这与 Owner 的"小级别领先大级别"假设正面相关，既是机会也是主要风险** | 叩富网汇总（引述多家券商） | https://licai.jiantou8.com/ask/qa_7381084.html | 中（二手汇总） |
| 6.4 | 缠论学术同行评审论文：**未检索到**英文同行评审期刊上以"Chan theory/Chanlun"为主题的量化有效性论文（检索词：Chanlun 量化 实证 / Chan theory quantitative）。存在的证据层：券商金工研报（6.1/6.2）、技术博客回测（https://tsight.io/articles/8003172 ：某股 2021-2025 日线回测，结论谨慎）、工程实现（iTick 教程 https://blog.itick.org/en/stock-api/itick-chanlun-strategy-backtesting-tutorial ）。学术缺口本身是终审应记录的事实 | ——（缺口） | 上述 URL | 缺口 |
| 6.5 | **涨停板/游资行为（强证据）**：理性预期模型 + 2011-2023 主板/中小板 **149,589 次涨停事件**：封板股隔夜收益 +2.43%（t=8.31）但 120 日反转 -2.64%（t=-4.02）；炸板股次日开盘 -5.25%（事件组中最极端）；2020 创业板 10%→20% 改革作为自然实验证明**放宽涨跌幅减轻投机扭曲**（10% 维持概率 0.67→0.43，降 24 个百分点）；模型统一解释磁吸效应、波动溢出、延迟价格发现 | Jiang & Li (2026), "When Walls Become Targets: Strategic Speculation and Price Dynamics under Price Limit", SSRN 6955939 | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6955939 ；全文镜像：https://www.cfrn.com.cn/uploads/master/paper/20250709/686e72d8373a5.pdf ；讲座纪要：https://sbf.uibe.edu.cn/xsyj/xsxx/c38bc2b8e8884022a54c33e1b77d4fb9.htm | 中强（工作论文，超大规模事件样本+自然实验） |
| 6.6 | 账户级证据：深交所 2012-2015 全部A股账户数据（机构 + 五档个人），证明**大资金投机者推价至涨停封板、次日卖出获利**的"破坏性交易行为"存在且导致价格过度反应；机构持股比例高的股票该行为受抑制 | Jiang (Wenxi), Gao (Zhenyu) et al., "Daily price limits and destructive market behaviour"（CUHK） | https://cbk.bschool.cuhk.edu.hk/do-daily-price-limits-stabilize-the-markets/ | 强（账户级数据） |
| 6.7 | T+1 与涨停策略实证（学位论文）：沪深 2013-2017 数据验证"追击涨停板"策略**穿越牛熊获取超额收益**；大投机者参与度是成败决定因素；监管加强与机构持股比例上升有抑制作用 | 香港理工大学 D.Mgt 论文 (2019)《被利用的涨跌停制度》 | https://theses.lib.polyu.edu.hk/handle/200/13346?mode=full | 中 |

---

## §二 传统形态（规则法/TA-Lib）vs ML 形态：对比证据汇总

1. **规则法基线（成熟市场）**：Marshall-Young-Rose (2006) 的 bootstrap 检验是"规则法K线形态无效"的标杆；Sullivan-Timmermann-White (1999) 进一步显示规则法在 80 年代中期后失效。这两篇构成对"TA-Lib 61 形态直接当信号用"的最强质疑。
2. **规则法在 A 股/新兴市场**：Lin et al. (2021, PLOS ONE) 的关键设计是"**不做固定形态定义，而是枚举两日/三日K线组合再用机器学习筛选**"——这等于承认固定规则形态（TA-Lib 式）在 A 股也需过滤/加权才有边际；其 36.73% 年化 + 成本内检验是目前 A 股最强的公开同行评审证据。
3. **ML 图像法上限更高但有条件**：简单 CNN（4层）即可达 0.892 AUC 且优于大型预训练模型（2.1）；换手率替代成交量、时间分隔符等 A 股特化设计带来增益（2.4）。但所有 ML 论文报告的准确率都是**样本内或仅时间序列切分**，未见任何一篇做了 White/Hansen/DSR 式多重检验校正——ML 论文的"高准确率"与规则法的"无效"之间没有做过同数据、同成本、同校正的严格对撞。
4. **未检索到**"同一 A 股数据集上 TA-Lib 规则形态 vs CNN 图像法直接对比"的论文——这是证据链的真实缺口，终审时应将其列为"系统自建考试比引用文献更可靠"的理由。
5. **共识放大器**：上下文条件（趋势、SR 位置、量能）是规则法与 ML 法文献共同指向的增益来源（1.3 Bulkowski 的"tall pattern"、fxfoundations 教材性总结、Lin et al. 的过滤机制）。这与 Owner"形态必须挂在趋势线/结构位置上"的直觉一致。

## §三 多时间框架"共振"的学术形式化证据

1. **"跨周期确认"可被形式化为"多尺度滞后相关的统计验证"**：Curme et al. (2015) 的 Bonferroni/FDR 校正滞后相关网络、Hayashi & Koike (2020) 的尺度逐层 lead-lag 估计器，是两个可直接借鉴的方法论模板——它们把"15分钟级事件与1分钟级信号的先后/领先关系"变成可检验的统计量。
2. **"小级别领先大级别"有正向证据，但有边界条件**：
   - 正向：采样越细、可验证的 lead-lag 链接越多（3.1）；A股强耦合对在 1 分钟尺度 lead-lag 最显著（3.3）；日内动量"早半小时预测晚半小时"在标普500 成立且在高波动/高量日更强（3.4）。
   - 边界：效应依赖流动性（澳洲未复现，3.5）；市场有效性上升会侵蚀链接数（2002 vs 2011, 3.1）；ETF 上市即侵蚀规则利润（4.3）——A 股"小级别领先"信号存在随量化化进程衰减的风险，考试系统应内置滚动再检验。
3. **Owner 假设（15分钟触趋势线 + 1分钟两次不过前高 → 抛售预警）的学术对应物**是"条件事件研究 + 跨尺度验证"：以 3.1/3.2 的校正滞后相关定义"领先"是否统计显著，以 4.6 的 regime 分层框架定义"共振格子"。文献支持把"两次不过前高"（等价于 zig-zag 双顶失败的微观结构）当作事件触发器——zig-zag 特征在 HHMM 文献中已是标准做法（5.4）。
4. **多尺度特征工程**：小波（Daubechies）分解在跨市场实验中稳定降低 20-40% 预测误差且按 regime 分层显著（3.7）；层次 HMM 是联合建模多时间分辨率的现成工具（fHMM, 3.6）。若系统要"矩阵法算每格夏普"，层次 HMM + 小波是多尺度轴的学术正统选型。

## §四 信号矩阵 + 多重检验：方法论建议（衔接 3700 格考试系统）

1. **3700+ 格本质就是 White (2000) 定义的"策略宇宙"**。文献结论明确：对格内最优者做单格 t 检验必然产生假阳性；必须对"最优格"做 RC/SPA 检验（4.1/4.2），对"全部显著格"用 StepM/Step-SPA（4.3）。
2. **DSR 是工程上最可落地的工具**（4.4）：对每格报告 Deflated Sharpe，代入（a）有效试验数 = 试验总数与格间平均相关（格子高度相关时有效试验数远小于 3700）；（b）收益非正态修正。配套纪律：**记录并披露全部尝试过的格子**——未披露试验数的回测"一文不值"（Bailey-López de Prado 原话）。
3. **经验数值警戒线**：Harvey-Liu-Zhu (2016) 主张因子发现 t > 3.0（4.5）；Bailey 等演示样本内夏普 1.04 → 样本外 0.07 的完整案例（4.4）——考试系统的"通过线"应设在扣除选择效应之后的 DSR，而非名义夏普。
4. **矩阵的行/列设计建议（源自文献）**：
   - 市场状态轴：用 HMM（2-5 状态）而非单一阈值（200日均线式）做 regime 分层，且**分层只用于评估、不进训练**（3.7 的做法），避免泄露；
   - 每格检验：格子内样本量 + 该格被"顺便看过"的次数都入账；
   - 时间稳定性：Sullivan et al. (1999) 与 Hsu et al. (2010) 的教训是规则盈利性随市场结构（ETF/量化占比）漂移，建议滚动窗口重考而非一次性终审。
5. **"矩阵法算出共振每个格子的夏普率"本身在方法上成立**，等价于 4.6 的 regime-conditional 信号表现矩阵 + 逐格 Diebold-Mariano/DSR；文献先例是 Okşak et al. (2025) 按三状态分层的显著性检验。唯一要补的是：格与格之间不是独立试验，必须用考虑相关的校正（RC/SPA/DSR 的有效试验数机制，而非 Bonferroni 除以 3700）。

## §五 趋势线/支撑阻力算法选型证据

1. **首选证据链**：Chung & Bellotti (2021) 证明 SR 水平可被启发式算法发现且反转趋势统计显著、有"反弹次数越多越有效"与"随时间衰减"两条可编码规律（5.1）——直接支持系统把"触及下降趋势线上沿"作为事件轴，且支持给"多次验证的线"加权、给老旧的线降权。
2. **微观基础**：Osler (2000/2001) 的订单流聚集解释（整数位/前高前低的止损单堆积）说明 SR 有效性不是图形学迷信而有订单簿基础（5.2）——A 股涨跌停板会额外制造"人造 SR"（6.5 的封板价行为），这是 A 股特有的一层。
3. **算法选型**：转折点检测（zig-zag/fractal）→ 线参数估计（稳健回归/M-estimator 优于 OLS）→ 线筛选（PSO 等优化或启发式）三段式，分别有 5.4/5.3/5.1 的文献支撑。
4. **警示**：PSO 优化 SR 线单独使用不优于 Buy&Hold（5.3）——趋势线信号必须进入组合/矩阵（与本系统"接入考试"的方向一致），不要单信号上线。

## §六 低把握/未覆盖项（如实申报）

1. **缠论同行评审文献不存在（未检索到）**：全部缠论量化证据为券商研报/博客/学位论文层（6.1-6.3），无一经过 RC/SPA/DSR 校正；中泰研报的 76.53% 胜率是样本内且回测口径（选样、成本）不完全透明。
2. **"TA-Lib 规则 vs CNN 同数据直接对比"论文未检索到**（§二第4条）——终审若需要此对比，应由考试系统自测，文献无法代劳。
3. Marshall et al. (2006) 原文为 ScienceDirect 付费墙，本次以其 RePEc 引证页 + 多个二手来源交叉核实；White (2000)/Hansen (2005) 原文同理（以大学 eprints 综述页交叉核实）。书目信息（卷期页码）均来自 RePEc/CitEc 引擎，可靠性高但非出版商页面。
4. 未单独检索：EMD（经验模态分解）专用于交易信号的论文（本次以小波文献覆盖多尺度轴，EMD 仅在个别综述中被提及）；"假突破/庄股形态"的中文学术文献；图中 GNN 用于"单票价格结构"（而非股票间关系图）的同行评审论文——券商研报有（HIST 等模型），但属业界层证据。
5. arXiv:2605.00875（主题2.1）为 2026 年预印本，未经同行评审；其中"简单 CNN 优于 ViT"的结论在加密货币 regime 任务上取得，外推到 A 股 15 分钟 K 线需自测。
6. 检索时间截至 2026-09-26；SSRN/RePEc 页面内容以当日快照为准。

---

## §七 与系统现状的逐项衔接（补充备忘，非裁定）

| 系统现状组件 | 学术证据对接 | 关键条目 |
|---|---|---|
| TA-Lib 61 种 K 线形态 | 成熟市场无效基线；A股需机器过滤/上下文加权后才有边际；建议形态信号只作为考试矩阵的候选轴，不单信号上线 | 1.1 / 1.3 / 1.7 |
| 215 列技术指标 | 指标越多 = 试验空间越大 = 多重检验越严；Hsu-Hsu-Kuan 的 9,120 均线规则实证表明多数指标规则会被 Step-SPA 剔除 | 4.3 / 4.4 |
| 缠论结构模块 | 券商级回测为正（中泰 76.53% 胜率），但无同行评审、无多重检验；建议按普通信号入考，不因来源特殊豁免 | 6.1-6.4 |
| 庄股形态/假突破 | Bulkowski 的"busted pattern"（假突破后反向）是文献中明确可交易的信号；涨停板行为学（封板/炸板不对称收益）提供 A 股特有的事件轴 | 1.4 / 6.5 / 6.6 |
| 资金流形态 | Osler 订单流聚集为 SR/资金位提供微观基础；本主题未做专门文献检索（见 §六） | 5.2 |
| 缺口：信号接入策略考试（网格搜索条件轴） | 全部证据指向同一结论：矩阵法本身学术成立（regime-conditional signal performance），但每格夏普必须过 DSR/SPA 校正，且滚动重考 | §四 全节 |
| T1 粗扫 3700 格 | 与 Qi-Wu (2006) 的 2,127 条外汇规则、Hsu-Hsu-Kuan 的 16,380 条规则同量级，文献处理方式（Stepwise 全家桶）可直接移植 | 4.3 |

---
*案卷完。共 7 节、31+ 条证据条目，每条附实际检索到的 URL/DOI。*
