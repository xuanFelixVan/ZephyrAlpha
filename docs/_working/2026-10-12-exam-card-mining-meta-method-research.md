---
ttl: task_bound
title: 考试卡挖矿的元方法调研——机构与学界如何系统枚举信号邻域（挖矿日志内嵌）
session: st-metamine-20261012
created: '2026-10-12'
author: 主区会话（Owner 直令产出）
method_source: docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md（六向寻路/防噪音四闸/挖后自审闸）
status: active
---

# 考试卡挖矿的"元方法"调研——他们是怎么挖矿的

> **任务**：Owner 问"考试卡本身怎么挖矿？机构/学界/社区对'挖矿的方法'有没有一套？五轴卡族是不是不止 5 个？"
> **母节点**：信号考试卡的邻域枚举方法（元方法）。
> **方法**：按 mining_sop 执行——内部反查+全网搜索双向，挖矿日志内嵌本文（§2），防噪音四闸执行记录见 §7。
> **产出**：①轴清单超集（5 轴→**12 轴 + 3 本账**，§5）；②学界/业界挖矿流程三派对比（§3/§4）；③对"涨停邻域"新矿的直接落点（§6）。

## 0. 一句话结论

"挖矿的方法"在学界是**统计记账学**（管测试次数、增量贡献、复制、协议四本账），在业界是**两级漏斗工厂**（便宜宽测+昂贵窄考+去重过滤链），两者合成一套：**邻域整族批量预注册 → 宽测扫描 → 分诊 → 窄考 → 生命周期监控**。我们已建的八段 SOP 与 N 账本/探索分册正是这个结构；缺的是显式的**轴清单**——本调研收敛出 12 轴，确认"不止 5 个"。

## 1. 内部反查（先查自己家里已有什么）

| 内部资产 | 已覆盖的轴/环节 |
|---|---|
| factor_mining_sop 八段一段闸（mining_sop 族） | 全流程骨架 S0-S7 + 多重检验纪律（贯穿）+ 预注册卡模板 v1.0 |
| F06 参数网格 schema（config/position_recipe_grid_schema.yaml） | **16 个配方维**：G_universe／D1 调仓频率／D2 调仓触发／E 单票 cap／H 换手 λ／A1 因子归一(rank/zscore/行业中性)／A2 合成权重／C sizing／B_top_n／F／I／J／K／X_stop／X_breaker／X_sector |
| 卡池分层（exam_cards/ 487 张） | L0 大盘态／L1 指数面／L2 板块面／L3 策略漏斗／L9 另类面 + entry/exit + comparison/ablation 卡型 |
| 卡面内置柱 | lag_profile(t+1..t+3)／quantile_decile 分桶／regime 条件化(裁定#365)／orthogonal_increment 正交增量／absolute_line_check 绝对线对照／overheating_reversal 过热腿 |
| 三个生成器 | lane_b(NL 假设)／lane_c(gplearn 公式)／lane_c2(LLM agent+AST 白名单+原创性闸——与 AlphaAgent 同源思路) |
| 治理件 | 探索分册(不计试次) vs N 账本(计试次)／neff 估计器预注册／组合层穷尽章程(F-06)／反向分诊 A_cap=4 先例／墓碑制退役 |
| 数据闸 | WO-A2 五分钟切片器（个股分钟面存在性核查）=分钟级轴的硬依赖 |

**反查结论**：配方轴（怎么组合）有 16 维很完整；**信号邻域轴（一个信号怎么掰开）没有显式清单**——散在卡面柱里，本调研补齐为 §5。

## 2. 全网挖掘日志（按向记录；检索式/命中/信噪判定）

### ① 统计严谨性向（学界怎么管"考了很多次"）
- 检索：factor zoo multiple testing / Harvey t-statistic → **signal**
  - Harvey, Liu, Zhu (2016, RFS)《…and the Cross-Section of Expected Returns》：清点 **316+ 个已发表因子**，结论=多数是新发现假象；处方=新因子 t 统计量门槛抬到 **3.0**（随历史测试总数上调、随测试间相关性下调）。
  - Feng, Giglio, Xiu (2020, JF)《Taming the Factor Zoo》：新因子的正确考法=**对已有因子池做 LASSO 双选择回归，只认边际增量**——不是"单独显著"而是"比别人多知道什么"。
  - Bryzgalova, Huang, Julliard《Bayesian Solutions for the Factor Zoo》(JF)：贝叶斯批量筛选（"跑了两千万亿个模型"）。
  - Hou, Xue, Zhang《Replicating Anomalies》 vs Jensen, Kelly, Pedersen《Is There a Replication Crisis in Finance?》：复制之争——先复制再谈新发现。
  - Arnott, Harvey, Markowitz (2019, JFDS)《A Backtesting Protocol in the Era of Machine Learning》：**七点回测协议**——类预注册流程＋**扣留最近一段历史数据永不碰**作最终 holdout。
  - Bailey & López de Prado《The Deflated Sharpe Ratio》；Bailey-Borwein-LdP-Zhu《PBO》(CSCV 组合对称交叉验证)：**1,000 次独立回测的期望最大 Sharpe≈3.26**——不记账的"最佳一格"几乎必然是运气。Novy-Marx (2015, NBER)：多信号组合回测的过拟合偏差。
- 判定：全 signal。这是"考试卡"体系的统计地基。

### ② 工业化枚举向（业界怎么批量生成+过滤）
- 检索：WorldQuant 101 alphas / BRAIN → **signal**
  - Kakushadze (2016)《101 Formulaic Alphas》(arXiv:1601.00991)：101 条真实在用公式的**模板库**——算子×价量字段的组合空间本身就是可枚举的。
  - WorldQuant BRAIN 平台工作流：表达式生成 → 模拟回测 → **过滤链**（Sharpe 门槛 / 换手率上限 / **对既有 alpha 池相关性 <0.7 去重**）→ 入池升级。
- 检索：AlphaGen AlphaAgent LLM alpha mining → **signal**
  - AlphaGen (Yu et al. 2023)：RL 生成公式化 alpha，**奖励=组合模型表现**（挖的是"对组合有增量"不是单因子好看）。
  - AlphaAgent (arXiv 2025-06)：LLM agent 挖矿，核心创新=**正则化新颖性**（对共线/冗余惩罚）——与我们 lane_c2 的 AST 白名单+原创性闸同源。
  - Shin et al. (2024)：预训练 alpha 库+协同生成。
- 判定：全 signal。

### ③ 中文卖方向（券商金工的因子工厂）
- 检索：金工 遗传规划 因子挖掘 IC 衰减 → **signal（多为研报库转述，全文未达）**
  - 华泰《基于遗传规划的选股因子挖掘》(2019-06)：GP 公式演化的系统测试。
  - 东北证券《DFQ 遗传规划价量因子挖掘系统》(2023-05)：对基础 GP 的 **7 点改进**（初始种群质量/防公式膨胀/降因子相关性/动态参数）。
  - 中信建投《因子衰减在多因子选股中的应用》；天风《半衰 IC 加权》(2017)：**IC 半衰期**作衰减加权=生命周期轴的实务化。
  - 开源证券《因子失效原因与讨论》(2025-01)：拥挤度与衰减。
  - 浙商 Alpha-GPT 点评：**量价因子有效周期从 3-5 年缩到 6-12 个月**——挖矿重心正从"发现"转向"生命周期管理"。
- 判定：signal（转述级，全文留待后续深挖，见 §7）。

### ④ 日内/涨停直系向（本矿的正系文献）
- 检索：Seasholes Wu limit up Shanghai / magnet effect → **signal**
  - Seasholes & Wu (2007, JEF)《Predictable behavior, profits, and attention》：**上交所涨停=注意力捕获事件**（高收益+高量+上新闻）→ 个人投资者净买入 → 价格过冲 → **随后数日反转**。这就是我们考出的"涨停家数 IC 为负"的机制学锚。
  - Cai et al. (2022)《Investor attention, aggregate limit-hits, and stock returns》：**聚合涨停天数=注意力测度**——"涨停家数"卡的国际同型。
  - 磁性效应文献（中国涨跌停、创业板 10%→20% 自然实验）：价格临近涨停会加速——时点轴的连续版。
- 检索：intraday momentum / overnight vs intraday returns → **signal**
  - Gao, Han, Li, Zhou (2018, JF)《Market Intraday Momentum》：**头半小时收益预测尾半小时**（美股，Sharpe≈0.9）——日内时点轴的奠基文献；A 股日内动量/反转已有跟随研究。
  - Lou, Polk, Skouras《A tug of war: Overnight versus intraday expected returns》：**知名因子几乎只在隔夜或只在日内赚**（动量隔夜赚日内亏）——任何日频信号都该拆隔夜/日内两列。
  - Bogousslavsky (2021, JFE)；Aboody et al.：隔夜收益=散户情绪代理、预测反转。
- 判定：全 signal，且直接命中"涨停邻域"（§6）。

### 噪音记录（四闸滤出，如实记）
首发出噪 3 次：Harvey→电影《Harvey》(IMDB)；遗传规划→人类遗传资源管理条例；intraday→Investopedia 科普。全部换词重挖后命中，未采信任何一条噪音源。

## 3. 学界共识：考试卡之前先管四本账

1. **测试次数账**：t≥3.0 起步且随测试总数上调（Harvey-Liu-Zhu）；1,000 次回测的期望最大 Sharpe≈3.26（DSR）；PBO/CSCV 量化"选出来的最好一格是过拟合"的概率。→ 内部对应：N 账本计试次、neff 估计器、反向分诊 A_cap=4。
2. **增量账**：新信号的判定标准是"对既有池的边际贡献"（Feng-Giglio-Xiu），不是孤立显著。→ 内部导生卡只有 orthogonal_increment 对母卡一条回归；**升级方向=对整个情绪/价量因子族回归取残差**。
3. **复制账**：复制优先于新发现（Hou-Xue-Zhang vs Jensen-Kelly-Pedersen 之争）。→ 我们的同义动作=route-audit 复跑与 recast 重考（已经做过）。
4. **协议账**：Arnott-Harvey-Markowitz 七点协议——类预注册＋**扣留最近末段数据永不碰**作终极 holdout。→ 我们有冻结+OOS，但没有"末段永扣"条款，可议。

## 4. 业界挖矿流程：两派一条河

- **理论先行派**（AQR/学界）：机制假设 → 预注册冻结 → 窄考。= 我们八段 SOP 的骨架。
- **数据先行派**（WorldQuant/GP/RL/LLM）：算子×字段模板空间批量生成 → **两级漏斗**（宽测模拟便宜跑 → 过滤链：Sharpe/换手/相关性去重 → 入池）→ 对池顶做窄考。三种发动机：GP（华泰/东北 DFQ：种群质量+防膨胀+降相关）、RL（AlphaGen 组合奖励）、LLM agent（AlphaAgent 正则新颖性）。
- **收敛形态**：宽测便宜、窄测昂贵、中间隔一道去重+分诊。我们的"探索分册不计试次 → 分诊立族(A_cap) → N 账本正考"就是同一条河。
- **范围/停止条件**：内部已有"矿脉枯竭判据"；学界补充=**FDR 控制下边际产出递减**即停；业界补充=因子寿命缩短（6-12 个月）→ 挖矿管线必须带**生命周期监控段**（IC 半衰期加权/拥挤度/退役墓碑）——这是轴清单里最容易被漏的一段。

## 5. 主要产出：轴清单超集（5 轴 → 12 轴 + 3 本账）

Owner 原五轴=量级/时点/horizon/影响面/加速度（加速度并入变换轴）。超集按三组组织：

### 第一组：信号本体（把一条信号掰开）
| # | 轴 | 定义 | 内部现状 | 出处锚 |
|---|---|---|---|---|
| T1 | **变换轴** | level/一阶变化/**二阶加速**/rank/zscore/波动率归一/行业中性/**隔夜-日内拆分** | A1 归一维(rank/zscore/neutral)已有；加速与隔夜拆分未见 | Lou-Polk-Skouras；101 Alphas 算子表 |
| T2 | **事件构造轴** | 事件定义本身是可枚举空间（涨停/炸板/断板/首板/连板高度/晋级/烂板…每条=不同事件）；事件研究形态 | 打板族卡已铺 7-8 种事件；无"事件清单总册" | Seasholes-Wu；Cai et al. |
| T3 | **量级轴** | 绝对阈值/分位桶/尾部档/桶宽 | quantile_decile+absolute_line_check 已有 | 母卡 >P90 反转腿 |
| T4 | **时点轴** | 日内发生时刻（开盘 N 分钟/午前/午后/尾盘）、速度（达到 K 家耗时） | **空白**（数据闸 WO-A2） | Gao et al. 日内动量；磁性效应 |
| T5 | **horizon 轴** | T+1..T+N 阶梯、周/月、峰值半衰期 | lag_profile 只建 t+1..t+3；长窗换卡面 target 无族 | 半衰 IC 加权（天风/中信建投） |
| T6 | **数据粒度轴** | 日频/分钟/tick | 分钟级=W O-A2 数据闸 | AlphaGen 输入面板 |

### 第二组：映射面（影响谁——Owner 的"五角星"）
| # | 轴 | 定义 | 内部现状 |
|---|---|---|---|
| T7 | **目标轴** | 指数收益/板块超额/个股截面/情绪状态转移/量能/波动回撤/执行成本 | 卡池分层已铺；无"单信号×全目标"影响面矩阵族 |
| T8 | **宇宙轴** | hs300/zz500/全A/剔除规则 | 网格 G_universe 已有 |
| T9 | **状态条件轴** | regime/情绪六段/流动性档/波动率档/拥挤度 | regime 条件化(裁定#365)+地量卡已有；拥挤度未见 |

### 第三组：关系与治理（跟别的信号怎么处、怎么养老）
| # | 轴 | 定义 | 内部现状 | 出处锚 |
|---|---|---|---|---|
| T10 | **组合正交轴** | 残差化/AND/OR/**对因子族整体回归** | orthogonal_increment 只对母卡单条 | Feng-Giglio-Xiu |
| T11 | **形态轴** | 响应曲线形状本身作命题（单调/U形/阈值跳） | 合成VIX卡已预写倒U条款；无形态族 | — |
| T12 | **生命周期轴** | 半衰监控/拥挤度监控/衰减加权/退役墓碑 | 墓碑制已有；IC 半衰监控未见 | 天风/中信建投/浙商/开源 |

**+3 本账（贯穿治理，非轴）**：测试次数账（试次/neff/DSR 思想）｜增量账（对池边际）｜复制账（复跑审计）。已有雏形，按 §3 升级。

## 6. 对"涨停邻域"的直接落点（Owner 新矿）

文献证实这条矿脉是国际正系（Seasholes-Wu 机制+ Cai et al. 测度），且给出了我们还没立的格：

1. **隔夜/日内拆分列**（T1）：涨停溢价/晋级率的反转很可能只在隔夜腿或日内腿——Lou-Polk-Skouras 证明因子收益普遍偏向一边。**一张卡拆两列，零数据闸，立即可考**。
2. **日内时点族**（T4）：开盘 1/5/10/…/60 分钟、午前/午后的涨停家数×量级×后续收益——Gao et al. 头半小时动量直接支持。**硬依赖=WO-A2 分钟面**，建议提速呈批。
3. **磁性效应腿**（T4 连续版）：临近涨停的封板加速（价格距涨停距离的时间导数）。
4. **horizon 阶梯**（T5）：涨停事件的 T+1..T+10 成族预注册，替代现在"每卡钉死次日"。
5. **增量账升级**（T10）：涨停族信号对"情绪因子族"整体残差化，回答"是否只是已有情绪因子的影子"。

## 7. 防噪音四闸执行记录 + 挖后自审闸

- **四闸**：来源分级（顶刊/SSRN=一手；平台官方文档=一手；券商研报=转述二级；博客/百科=仅线索不入证据）；时效（优先 2016-2025）；相关性（母节点直接命中才入）；可验证性（每条带可回溯出处，§8）。
- **自审（过度工程判定）**：本调研产出的是"轴清单+三本账+落点清单"，全部可映射到已有 S3 卡模板与现有治理件，无新机构建议 → 判**方向有效、不过度工程**。
- **开放问题**：①券商研报全文不可达（GP 参数细节、半衰 IC 公式留待深挖）；②A 股微结构数据面（龙虎榜/席位）未挖；③Kozak-Nagel-Santosh《Shrinking the Cross-Section》、Gu-Kelly-Xiu《Empirical Asset Pricing via ML》为本轮未单独检索的经典补充，下轮验证后升级为正式引用。

## 8. 来源清单（全网向；内部资产见 §1）

- Harvey, Liu, Zhu (2016 RFS)：…and the Cross-Section of Expected Returns（t≥3.0，316 因子清点）
- Feng, Giglio, Xiu (2020 JF)：Taming the Factor Zoo（LASSO 边际增量）
- Bryzgalova, Huang, Julliard (JF)：Bayesian Solutions for the Factor Zoo
- Hou, Xue, Zhang：Replicating Anomalies；Jensen, Kelly, Pedersen：Is There a Replication Crisis in Finance?
- Arnott, Harvey, Markowitz (2019 JFDS)：A Backtesting Protocol in the Era of Machine Learning
- Bailey & López de Prado：The Deflated Sharpe Ratio；Bailey-Borwein-LdP-Zhu (2015 SSRN)：PBO/CSCV
- Novy-Marx (2015 NBER)：Backtesting Strategies Based on Multiple Signals
- Kakushadze (2016)：101 Formulaic Alphas，arXiv:1601.00991
- WorldQuant BRAIN：worldquantbrain.com（模拟→Sharpe/换手/相关性<0.7 过滤链）
- AlphaGen (Yu et al. 2023)：github.com/ICT-FinD-Lab/alphagen（RL 组合奖励）
- AlphaAgent (arXiv 2025-06)：LLM-Driven Alpha Mining with Regularized Novelty
- Shin et al. (2024)：Synergistic Formulaic Alpha Generation
- Seasholes & Wu (2007 JEF)：Predictable behavior, profits, and attention（上交所涨停注意力反转）
- Cai et al. (2022)：Investor attention, aggregate limit-hits, and stock returns
- Gao, Han, Li, Zhou (2018 JF)：Market Intraday Momentum（头半小时→尾半小时）
- Lou, Polk, Skouras：A tug of war: Overnight versus intraday expected returns
- Bogousslavsky (2021 JFE)：The cross-section of intraday and overnight returns
- 华泰证券 (2019-06)：基于遗传规划的选股因子挖掘；东北证券 (2023-05)：DFQ 遗传规划价量因子挖掘系统
- 中信建投：因子衰减在多因子选股中的应用；天风 (2017)：半衰 IC 加权；开源 (2025-01)：因子失效原因与讨论；浙商：Alpha-GPT 点评（因子寿命 6-12 月）

## 9. 全仓考试对象普查与元方法适用矩阵（2026-10-12 追加，Owner 直令）

> 问题："这套元方法是不是能用到所有需要回测/考试的 scenario？" 本节=全仓普查+逐族判定。

### 9.1 考试对象六族清单（落盘件实测）

| 族 | 对象 | 成绩册/落盘件 | 现状 |
|---|---|---|---|
| A 信号/因子 | 考试卡 487（calibration/comparison/ablation）；指标批3 143 条；因子批1 175；另类因子；板块因子；codesym 因子；FCT-MOM-029 重考 | exam_scores_v1(44 行)／indicator_exam_scores_v1＋indicator_conditional_exam_scores_v1／factor_exam_scores_v1／alt_factor_exam_scores_v1／sector_factor_exam_v1／codesym_factor_exam_v1／mom029_prereg_v2+reexam_v2 | 正考中，44 行全 FAIL；指标 78 pass |
| B 策略配方 | F06 网格 362,880 格（幸存者 recipe 38b453ca3683）；批2 161 策略；codesym 策略；注册册 8 条；引擎层 8 个 strategy_id | f06_survivors.csv／strategy_exam_scores_v1／codesym_strategy_exam_v1／strategy_registry.yaml evidence／bt-*.json(60 件) | 1 个网格幸存者；STR-VREV-025 三窗全绿进模拟盘 |
| C 组合/配置 | 5 套资产分配器；防守机制（ATR 止损对照）；仓位配方 | allocator_shadow_report_v1／exit_sim_report_v1／X_stop/X_breaker 维 | 止损 A/B 首个环节级成功（+0.62 Sharpe） |
| D 状态识别/环境 | HMM 状态识别器（4/5 FAIL）；情绪指数择时（3 卷 FAIL）；情绪六段重建规则 | state_recognizer_exam_v1／emotion_index_exam_v1 | 六段规则未冻结＝无考试资格 |
| E 工程件 | GPU 引擎 W1；判官路由审计；成本模型假设（G6 双口径） | 各 exam run 件／18_route_audit_replay | W1 PASS；路由复跑零差异 |
| F 挖矿器元层 | lane_b/c/c2 产出质量；LLM 研究员档位 | intake 台账；GPU-01 档位 A/B（未注册未跑） | 元层考试空白 |

### 9.2 元方法适用判定（12 轴+3 账逐族套）

| 族 | 判定 | 套法 | 轴集变化 |
|---|---|---|---|
| A 信号/因子 | **全套直接适用** | 12 轴原样；批3 的 78 pass 大多为负 IC→正是反向分诊 A 类候选池（套 20_reverse_triage 模板） | 不变 |
| B 策略配方 | **适用，换轴** | 16 配方维即轴清单；元方法补充=幸存者邻域加密（72 格广度对照批已是实例）＋**DSR/PBO 折减**（362,880 格挑最好，期望最大 Sharpe≈3.26 的陷阱直接适用，幸存者 1.72→OOS 0.831 须打折重述） | 信号本体六轴→配方维；T5→D1 调仓频率；T9→regime 分窗 |
| C 组合/配置 | **适用** | 参数邻域 mini-grid（止损=ATR 倍数×回看窗×类型——dualwindow 卡+X_stop 维已起步）；分配器 5 套→层数/权重/触发参数网格 | 量级/时点轴→参数取值轴 |
| D 状态识别/环境 | **适用，先补冻结资格** | 对象是分类器不是信号：状态定义本身=可枚举空间（段数/边界/特征集/重建规则）；六段规则未冻=先走 S3 冻结 | T2 事件构造→状态构造；T5→状态持续期 |
| E 工程件 | **部分适用（换契约轴）** | 考"等价/达标"非"预测力"——信号轴不适用；但复制账/协议账适用（路由复跑=复制账实例）；成本参数可做敏感性考试 | 换等价性/容差/性能线契约轴 |
| F 挖矿器元层 | **适用且杠杆最高** | 对"研究员"考试：档位 A/B（产出量/入考通过率/幻觉率）=GPU-01 本体；这是"考考试出题人" | T7 目标轴→假说产量/通过率/原创性 |

### 9.3 尚未入考的对象（S0 缺口清单）
TDM 节点主张参数（"催化剂加权 20%"类，卡面已承诺由响应曲线定）；风控约束栈六层参数（trading_decision_map.yaml:4538：总仓位/回撤限额/波动率目标/集中度/流动性/相关性）；成本模型滑点 bp 表敏感性；RL 执行算法（B-007 后）；分配器邻域；LLM 档位。

### 9.4 优先级建议（元方法推广排序）
1. **幸存者 recipe 的 DSR/PBO 折减重述**——统计合法性刚需，零数据依赖，全仓最重要一件；
2. ATR 止损邻域 mini-grid（已证 A/B 有效，顺着参数轴挖）；
3. 批3 指标 78 pass 反向分诊（现成候选池+现成模板）；
4. 分配器 5 套参数网格；
5. 注册册 8 策略 ablation 分解卡（哪条腿在贡献——ablation 卡型现成）；
6. GPU-01 档位 A/B 落地（元层：研究员质量决定上游假说供给）。
**全局注意**：六族各挖各的邻域=多重检验再爆一次，须开**全局试次预算册**（一族一预算，跨族统一折减口径）。

## 追加·2026-10-13 挖矿二班：D 族资格位的一条反证指针（原行零改动）

本件 §9 表里 `D 状态识别/环境` 两行原文——":174 六段规则未冻结＝无考试资格"与":185 适用，先补冻结资格"
**原样保留不改写**（在册判定属其属主班，按更正另起、留旧案卷的纪律处理）。本班据
`docs/_working/2026-10-12-d-family-qualification-freeze-draft.md` §5 四件判据跑了一轮验收，读数为**四件全绿**：
重建幂等（两次独立进程重放 1,824 日 `dominant`/`six_phase` 逐日零不一致，正对照改 start 出行数变化以排除缓存假绿）、
段定义冻结（`sixphase-v1` 行级版本＋漂移守卫测试 12 passed 实跑）、PIT 无前视（三个截断窗历史标签逐日全等）、
逐日落台可读（`docs/_working/t0_matrix/six_phase_history_v1.csv` 逐日 10 列，5 条考卷路径实读为真源）。
细节与结构性风险（`load_phase_panel` 不钉 run_id、unrouted 762 日=41.9% 合法态、ablation 卡三面仅解一面）
见 `docs/_working/minedig2_campaign/10_dfamily_qualification_acceptance.md`。

⇒ 就"D 族能否进考试宇宙"这一问，:174 的"无考试资格"判定**在 2026-10-13 之后不再成立**；
但资格≠分数：本班零开考，判定权仍留 E2/E4。普查计数面（D 族资格状态列）的改写归普查件属主或统筹定序，本班不代改。

