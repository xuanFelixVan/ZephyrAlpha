---
ttl: task_bound
title: 资金行为识别调研总册（成交量/筹码峰/资金流）——问题定义+输出契约草案+全网调研
created: '2026-10-13'
session: st-capflow-20261013
family_id: CAPFLOW-RESEARCH
status: research_dossier_for_ruling
completes_when: §10 六条经条件轴总包 P1 统一呈批包呈 Owner 裁决且资金线四模块收口＋筹码转正考试完成后，随 CONDAXIS-CAMPAIGN 战役归档
---

# 资金行为识别调研总册（成交量/筹码峰/资金流）

> **纪律声明**：本册只做两件事——①把"成交量/筹码峰/资金流到底解决什么问题、出什么结果"定义清楚（§2 输出契约**草案**）；②固化全网调研与仓内盘点（§3-§8）。**判据面零冻结、数值零自拟、零考试**（对齐 st-minedig-20261012 D 族冻结稿同款纪律"只起草呈批，不自行开考"）。§2/§9 全部条目为候选草案，须经 Owner 呈批后才进判据预冻结。
> **与隔壁班关系**：大盘两态形态班（st-formreg-20261013，另对话在跑）管"价在做什么"（形态+拐点）；本册对象管"谁在做、还剩谁没卖、上面压着谁"——两班产出在考试条件轴（`condition_package`，情绪灰度×大盘状态分层口径=Owner 2026-09-23 夜裁）会合。

## §1 Owner 问题原话锚定（需求真源）

- "成交量、筹码峰、资金流……他们最终的结构目标是一个东西，那就是**找到资金的进场、出场信号，进了哪些东西，流向了哪些地方**。"
- "资金永远会流向阻力最小的方式。"（本册 §2.5 给出可算化翻译，不当公理用）
- "状态识别其实有明确的东西——**当下是什么状态、拐点是什么时候、信号是什么样子**。那成交量/筹码峰/资金流，它应该出什么东西？它应该识别出什么东西？"
- "**先说它解决什么问题、出来什么结果、能指导做什么，先把这个搞清楚，再倒推后面需要哪些数据、需要哪些东西。**"

## §2 问题定义：资金行为层的输出契约（草案 v0，呈批件）

### 2.1 与状态识别的同构对齐

| | 大盘形态班（状态识别） | 资金行为层（本册对象） |
|---|---|---|
| 回答的问题 | **价**在做什么形态 | **人**在做什么动作 |
| 输出 | 当下形态 + 灰度值 + 拐点信号 | 结构快照 + 流量性质 + 主体画像 + 合成状态/信号 |
| 观测对象 | 价格序列（最硬） | 成交量的三个侧面（流量→存量→主体，可靠性递减） |
| 在考试宇宙的位置 | 考试条件轴·大盘状态腿 | 考试条件轴·资金行为腿（候选）+ 拐点信号候选源 |

### 2.2 输出契约四件套（候选草案）

**A. 筹码结构快照（存量体检，日频）**——回答"筹码现在什么结构、供给从哪来"
- A1 获利盘占比（谁在成本线上方→止盈供给）；A2 套牢峰位置/距离（上方阻力地图，"阻力最小方向"的可算化：价上方 5%/10%/20% 缓冲带内历史筹码密度，候选指标名 `upside_resistance_quantile`）；A3 筹码集中度形态（单峰密集/双峰/发散→方向选择临近 vs 无共识）；A4（个股）股东户数趋势（筹码集中/分散的低频硬证据）。
- 学术对偶：处置效应→资本利得覆盖 CGO（Grinblatt & Han 2005，§4）——获利盘构成上方供给、套牢盘构成阻力，参考价分布有截面预测力。**这是"筹码峰"从经验到学术的桥**。

**B. 流量性质判定（增量诊断，日频）**——回答"今天的量是什么性质"
- B1 量价动态二分：放量+收益正自相关=知情推动（趋势燃料）vs 放量+收益反转=流动性出货（Llorente-Michaely-Saar-Wang 2002，§4）——同一根放量 K 线，两种相反含义，此判据是最小可行版。B2 effort/result 偏离（Wyckoff 口径：量努力 vs 价结果），仓内 `wyckoff_engine.py` 已占坑。

**C. 主体画像（行为归因，日频+事件）**——回答"谁在买谁在卖"
- 七类主体（仓内 MOD-SIG-088 已立封闭枚举：北向/公募/私募/游资/量化/散户/产业资本），每类：方向、强度、置信度、**证据链**（大单五档=弱证据、两融增速=杠杆盘、大宗折价=机构/减持盘、龙虎席位=游资事件、股东户数=结果验证、ETF 申赎=配置盘、解禁=潜在卖压）。
- 事实前提（§8）：北向只剩季度披露；融券做空腿 2024-07 后可忽略；**A 股"资金出场"五条腿=卖出+两融偿还+解禁减持+大宗折价出货+ETF 赎回**。

**D. 合成状态+拐点信号集（对齐状态识别的"状态+拐点"）**
- D1 净积累/派发状态：连续值（如 [-1,+1]）+ 离散三态（积累/派发/中性）+ 置信度——框架用 MOD-SIG-088 七类画像骨架（其 strength 公式现为"MVP 初拍值待标定"，标定是其转正前提）。
- D2 拐点信号集候选（**判据面零冻结**，仅列方向待 P2 预冻结）：建仓完成族（股东户数连降+底部单峰密集+缩量企稳…）；派发启动族（放量滞涨+获利盘高位+大单转净流出+两融偿还加速…）。

### 2.3 一句话职责分界

状态识别管"价在做什么"；资金行为层管"**谁在做+还剩谁没卖+上面压着谁**"。它是形态层拐点信号的第一候选源（隔壁班 P1 挖"单边启动信号"，资金面就是信号池）——两班是输入-输出关系，不是替代关系。

### 2.4 能指导什么工作（四个消费方向）

1. **择时/仓位**：派发信号→减仓预警；积累完成→纳入关注池（信号不进决策，trial 期纪律=裁定 #257④ 同款）。
2. **选股过滤**：筹码结构过滤（上行阻力小+底部集中=阻力最小方向的可算版）。
3. **考试条件轴**：作为条件维度（"在资金积累状态下开考策略 X"），挂 `condition_package` 大盘状态腿旁边。
4. **风控预警**：两融增速极端、解禁潮前瞻、天量异动、板块虹吸（`sector_siphon.py` 已在）。

### 2.5 "阻力最小"的可算化翻译（不当公理用）

"资金永远流向阻力最小处"不可证伪，禁止直接当模型假设。可算化对应物：①微观结构面=最小冲击执行（metaorder 沿流动性路径，√Q 冲击律，§4）；②筹码面=上方无密集套牢峰+下方筹码锁定（→A2 指标）。两句话都可检验，翻译完才准进系统。

## §3 外部调研①：机构实践

- **执行台（微观结构派）**：机构对自己 metaorder 全知，核心科技=冲击成本模型+执行算法（VWAP/POV/IS）。**反论：市面留下的足迹是被算法刻意整形过的——这是"大单≠主力"的根源**（机构拆单把大单伪装成小单）。冲击律 √Q 是执行算法定价的核心实证（Bucci et al. 线性→√ 交叉，CFM 实证数据，§4）。
- **配置端（定位代理派）**：美股 13F（季度）、港股 CCASS；A 股对应物=两融余额、龙虎榜席位、大宗折价、股东户数、ETF 申赎、基金季报重仓——**全是低频代理，机构从不只用代理变量做决策**。
- **卖方金工（中文研报主力）**：开源金工"大小单重定标"路线（§5）是代表——用逐笔数据还原真实大单，正面对拆单失真。
- **A 股本土行为派**：龙虎榜游资席位网络、封单/打板行为学、竞价抢筹识别（仓内 auction/seat 模块对应）。
- **负结果同样重要**：龙虎榜朴素跟随策略回测**严重负收益**（知乎量化实战回测文，⭕）——支持"代理变量先过事件研究再上岗"纪律。

## §4 外部调研②：学术锚点（经典 → 2025 最新）

**量（足迹）**：
- Llorente-Michaely-Saar-Wang (2002)：量价动态符号判知情交易 vs 流动性交易（本契约 B1 依据，🔍知识库）。
- Blume-Easley-O'Hara (1994) 量含信息；Campbell-Grossman-Wang (1993) 量价联合动态；Gervais et al. (2001) 高量收益溢价（均 🔍）。

**筹码（存量结构）**：
- Shefrin-Statman (1985) 处置效应；Odean (1998) 实证；**Grinblatt & Han (2005) 资本利得覆盖 CGO**——筹码分布的学术对偶（🔍）。
- Volume profile / POC / value area（70% 量）现状检索：**全部是从业者/教学来源，追溯至 Steidlmayer CBOT market profile (1980s)，无同行评审实证**（✅检索确认）——学术替代物就是 CGO/参考价。

**资金流（主体归因+冲击）**：
- Kyle (1985) λ；Amihud (2002) 非流动性；VPIN 流毒性（Easley-López de Prado-O'Hara 2012）；OFI 线性冲击（Cont-Kukanov-Stoikov 2014）及 [跨资产 OFI](https://www.tandfonline.com)（✅）、[MLOFI 多档位](https://www.semanticscholar.org)（✅）、[Kolm 等深度订单流失衡](https://ideas.repec.org)——**订单流特征训练显著优于订单簿状态直接训练**（✅）。
- **2025 最新**：[Maitrier, Loeper & Bouchaud《The Subtle Interplay between Square-root Impact, Order Imbalance & Volatility II: An Artificial Market Generator》(arXiv:2509.05065)](https://export.arxiv.org/abs/2509.05065)——合成市场生成器验证 √冲击×相关性 metaorder 理论、可从匿名 tape 恢复冲击（✅）【更正 2026-10-13 总包核验车道：原册标题《…Impact, Order Flow, and Price Diffusivity》非该编号真实标题，系与系列前作主题拼接，已按 export.arxiv.org 实读更正】；[Double Square-Root Law (arXiv:2502.16246)](https://arxiv.org/html/2503.18199v1)（⭕）；[Generating realistic metaorders from public data (arXiv:2503.18199)](https://arxiv.org/html/2503.18199v1)——用公开数据生成 metaorder 复现冲击风格化事实（✅）；Durin et al. 2023 两个 √ 律（参与率角色，⭕）；[Bucci et al. 线性→√ 交叉实证（CFM）](https://www.cfm.com/wp-content/uploads/2022/12/120-Crossover-from-linear-to-square-root-market-impact.pdf)（✅）。
- **成交方向判定（trade classification）**：美股因成交无方向标记需 Lee-Ready (1991)/tick test 推断，2024-25 趋势=ML 分类替代规则法（[ Lee-Ready primer](https://ml4trading.io/primer/trade-signing-and-the-lee-ready-algorithm/)（✅）、[公司债市场 ML 分类](https://www.researchgate.net/publication/378828001)（✅）、[Trade signing in fast markets](https://www.semanticscholar.org/paper/5896f9b1d16bdd52abc275ff42bcc9fa8f090f19)（✅）、[arXiv:2511.06177 push-response](https://arxiv.org/html/2511.06177)（⭕））。**A 股不同：L1/L2 快照自带内外盘方向标记，无需 Lee-Ready；但档位划分按单笔金额，拆单失真同样存在**——所以问题不是"判方向"而是"重定标"（§5 开源金工路线）。
- 大宗交易：Seppi (1992, JFE) 知情交易者大宗折价理论、Frino et al. (2007) 大宗价格冲击（⭕）、[Peng-Liu 2024《Microstructure of the Chinese stock market》](https://www.sciencedirect.com)（⭕，A 股大宗定义与微观结构）。

## §5 外部调研③：中文研报 / A 股特化

- **[开源金工《大小单重定标与资金流因子改进》(2022)](https://bigquant.com/wiki/doc/h3cQsAVEjF)**（✅）：逐笔数据重定标大小单、识别真实主力——仓内走"重定标路线"的对标研报。多份"大单 vs 小单 alpha 能力"对比研报在册线索（⭕）。
- **[《金融研究》2025 年第 1 期《主力资金异象和投资者信息博弈》](http://www.jryj.org.cn/CN/Y2025/V535/I1/189)**（✅）：散户跟随主力是信息博弈均衡非纯非理性——主力净流入横截面预测力的理论解释。
- **口径分裂警示**：[东财按单笔金额分档口径说明](https://stock.eastmoney.com/news/1423,20110101117172217.html)（✅）；[Wind/Choice/iFinD/大智慧口径互不一致](https://finance.sina.com.cn/stock/focus/2019-09-10/doc-iicezzrq4887775.shtml)（✅）——任何大单因子必须钉死数据商口径。
- **两融现状**（✅东财数据中心，2026-10-08 快照）：两融余额约 2.57 万亿、占流通市值 2.69%、两融成交占全市场 8.28%——杠杆盘是日频可测的真实主体。常见因子构造：融资余额变化率、融资买入额/成交额、余额占流通市值比（⭕，研报原文检索未命中，慧博/迈博汇金闭库）。
- **大宗交易**：折价率=(大宗价-收盘)/收盘，深折价偏向知情卖出/减持过桥，溢价偏向利益输送/接盘协作（⭕）；A 股大宗平台平均折价约 6.6%（⭕单一来源未复核）。
- **龙虎榜**：朴素跟随策略负收益（§3）；有效用法是席位网络/营业部画像而非跟随买入（⭕）。
- **股东户数**：户数连降=筹码集中是市场共识经验，"降幅/连降期数"为常用构造（⭕）；券商研报线索：东方证券筹码分布因子系列、开源微观结构系列（🔍检索未命中原文，待补）。
- **北向披露制度**（✅检索确认+东财页面提示）：2024-04-12 港交所通告，2024-05-13 起取消盘中实时买入/卖出/净买额披露（[东财沪深港通页](https://data.eastmoney.com/hsgtcg)已标"不再展示北向资金净买额数据"），个股持股明细改**季度**——北向日频"smart money"用法已死，季频诊断尚可。

## §6 外部调研④：GitHub 开源地图

| 仓库/资源 | 内容 | 对本项目的价值 |
|---|---|---|
| microsoft/qlib | A 股数据+Alpha158/360 量价因子 | 量价因子清单对标（🔍） |
| DeepLOB / TransLOB | L2 订单簿深度学习（2019/2020） | 竞价/日内监控参考（🔍） |
| nkaz001/hftbacktest | L2 逐笔回测引擎 | L2 工程参考（🔍） |
| vnpy OrderflowAddon | 足迹图/orderflow 分析 | 日内足迹可视化参考（🔍） |
| akshare / tushare | 大单/两融/龙虎/大宗/筹码（东财 CYQ）接口 | 仓内已在用（📋） |
| 通达信 CYQ 逆向实现（多个 repo） | 换手递推衰减分布 | 仓内 chips.py 内核同构（🔍） |
| [lnsongxf/Quantitative-analysis](https://github.com/lnsongxf/Quantitative-analysis) | 中资金工研报复现集 | 研报因子复现参考（⭕） |
| [github topics: order-flow](https://github.com/topics/order-flow) / [a-stock](https://github.com/topics/a-stock) / [china-stocks](https://github.com/topics/china-stocks) | 订单流/A股数据工具集散地 | 检索入口（✅） |
| [a_stock_level2_data](https://skillsllm.com/skill/a-stock-level2-data) | A 股 L2 逐笔+十档+龙虎+资金流接口目录 | L2 数据源候选清单（⭕） |
| quant-wiki.com | A 股研报合集 | 研报复索入口（⭕） |

## §7 仓内资产对照（三视角已有/成熟度/缺口）

### 7.1 数据面（出奇地全）

| 数据 | 表/通道 | 状态 |
|---|---|---|
| 大单五档资金流 | `c1_market.money_flow`（tushare pro.moneyflow 主源 5540 行/日，akshare fallback，tasks.yaml:182-195）＋大盘聚合 `market_fund_flow_daily`（akshare stock_market_fund_flow 东财大盘口径，fallback_sources 显式置空，tasks.yaml:3687-3700） | ✅在产【更正 2026-10-13 总包核验车道：原文把 tushare 5540 行/日主源描述嫁接到 market_fund_flow_daily——两张表两口径，个股大单五档=money_flow（tushare 主源），大盘聚合=market_fund_flow_daily（akshare 唯一源）；原文"intraday 另有 market_money_flow 表"亦不符，market_money_flow 是 money_flow 的 registry 逻辑名（日频），盘中只有板块级 sector_fund_flow】 |
| 两融 | `market_margin_trading`（akshare，akshare_provider.py:1941） | ✅在产 |
| 大宗交易+折价率 | `market_block_trade`（折价率均值已在 cohort_daily_ledger 计算） | ✅在产 |
| 龙虎榜 | dragon_tiger 落库 | ✅在产 |
| 股东户数 | akshare 东财续采（2026-09-18 接线；此前断供两月才被发现→supply_sentinel 诞生背景） | ✅在产 |
| 北向 | hk_hold **季度**快照（northbound_hold_fetcher） | ⚠️仅季度 |
| ETF 份额 | `market_etf_share_snapshot`/nav/list | ✅在库（申赎流量=差分派生，🔍待工程） |
| 解禁/增减持 | event_calendar（解禁前瞻已接） | ✅在产 |
| tick/竞价 | `tick_data` 主表 miniQMT 清退后**无在跑供给通道**，桥流实时只落 `tick_depth_5`（data_supply_sentinel.yaml:633）；竞价快照由 tick_depth_5 派生（ch_auction_derive） | ⚠️半断供 |
| 逐笔委托（L2 订单流） | 未检索到在册采集 | ❌缺口 |

### 7.2 模块面（三视角都有人占坑，成熟度参差）

| 视角 | 模块 | 成熟度 |
|---|---|---|
| 量 | `factor/technical_indicators/volume.py` 17 指标（OBV/MFI/**VWAP**/VR/AD/PVT/WVAD/VWMA/ADOSC/EOM/KVO/NVI/PVI/FORCE_INDEX/WAD/VO/MARKETFI，对齐通达信【核验注 2026-10-13：恰好 17 个，原册括号漏列 VWAP】） | production |
| 量 | `wyckoff_engine.py`、`volume_regime_adaptive.py` | 在册 |
| 量 | `auction_microstructure_analyzer.py`（MOD-SIG-089，竞价五族特征+抢筹/诱多/压价） | testing |
| 筹码 | `factor/technical_indicators/chips.py`（CYQ 迭代衰减内核 compute_chip_metrics，IND-CHIPS-001 获利盘） | 在册 |
| 筹码 | `regime/features/chip_distribution_engine.py`（MOD-REGIME-005：VWAP 三角+换手递推+筹码龄+32 网格；2026-10-04 winner 剖面） | **trial**（裁定 #257④ 打回：零消费端+伪分布；量纲已修，转正需消费端考试卡） |
| 资金流 | `capital_flow_pattern_analyzer.py`（MOD-SIG-022：四线五形态+散户狂热反向） | production |
| 资金流 | `capital_behavior_orchestrator.py`（MOD-SIG-088：七类画像+六阶段推演+EMA 修正→CapitalConsensus） | testing（**strength 公式=MVP 初拍待标定**） |
| 资金流 | `institutional_behavior_analyzer.py`（MOD-SIG-021 六阶段主链）、`banker_pattern_simulator.py` | 在册 |
| 资金流 | `seat_pattern_analyzer.py`（limit_up/ 下单文件【核验更正：原册"seat_pattern_analyzer/classifier.py"子路径不存在】）、`lhb_premium_analyzer.py`、`event_dragon_tiger.py`、`manipulation_avoidance_detector.py`（risk/ 下）、`sector/sector_siphon.py`＋`sector/sector_divergence.py`（两个独立文件【核验更正：原册"sector_siphon/divergence.py"路径不符】） | 在册 |

### 7.3 三个病灶（P0 优先收口，先于任何新建）

1. **行为归因重复簇**：SIG-022（四线）/SIG-088（七类画像）/SIG-021（六阶段）/banker_pattern_simulator 四模块同域——按内收判据 w5_1"同域重复簇→收敛唯一"须裁定谁吞谁。
2. **筹码引擎 trial 卡死循环**：转正需要消费端考试卡，考试卡需要判据预冻结——这是本契约 A 件的第一场考试，也是天然突破口。
3. **北向日频信号族已死**：披露制度漂移的现成案例——数据审计必须带"披露制度漂移监测"（supply_sentinel 管断供，不管制度变更）。

## §8 陷阱与事实修正（写码前必读八条）

1. **大单≠主力**：算法拆单是行业标配，机构反而伪装小单；大单净流入须重定标（逐笔委托）或降级为弱证据。
2. **北向日频已死**（2024-05-13，§5）；用 hk_hold 季度做低频诊断可以，别再建日频北向信号。
3. **融券做空腿可忽略**：2024-07-11 转融券暂停、融券保证金 100%/私募 120%、余额降至百亿以下、占成交<0.1%（⭕检索摘要）——"资金出场"五条腿见 §2.2-C。
4. **口径分裂**：大单五档数据商口径互不一致（§5），换源即换因子，必须钉死 source 列（仓内表已有 data_source 列，好习惯保持）。
5. **量必须配价**：任何单独的量指标（OBV 类）不单独上岗，配 LM2002/effort-result 性质判定（§4）。
6. **代理变量先过事件研究**：龙虎榜朴素跟随负收益是现成反例（§3/§5）；每个代理变量一张考试卡，与"只用价量"基线比增量。
7. **PIT/滞后钉死**：大单盘后 T+0 晚、两融 T+1 早、龙虎榜 T+1 晚间、大宗 T+1、股东户数公告制不定时、ETF 份额 T+1、北向季度。信号可用时点逐条登记。
8. **多重检验**：主体画像候选证据链 7+条，信号池越大越容易挑出历史好看的——P2 预冻结须含"信号池规模→通过门槛"校正规则（与隔壁班同款纪律）。

## §9 倒推映射：输出契约 → 判据 → 数据 → 现状

| 契约件 | 所需数据 | 仓内现状 | 缺口 |
|---|---|---|---|
| A1 获利盘 | kline_daily OHLCV+换手三源 | chips.py 内核+IND-CHIPS-001 在产（chips.py 头注 production【核验注：原册"trial"与头注口径不一，以文件头注为准；trial 的是 chip_distribution_engine（MOD-REGIME-005）】） | 消费端考试卡（转正） |
| A2 阻力分位数 | 同上 | 内核可派生 | 指标未建+判据待冻结 |
| A3 集中度形态 | 同上+流通股本 | blueprint 明示 D21 待"单峰密集度全语义" | 流通股本工程 |
| A4 股东户数 | akshare 股东户数表 | ✅在产 | 因子构造待冻结 |
| B1 量价性质 | kline_daily | volume.py 17 指标但无 LM 判定（🔍待复核） | LM 因子未建 |
| B2 effort/result | kline_daily | wyckoff_engine 在册 | 判据待冻结 |
| C1 大单五档 | money_flow（个股，tushare 主源）＋market_fund_flow_daily（大盘聚合，akshare） | ✅在产（见 §7.1 更正注） | 重定标依赖逐笔委托（❌） |
| C2 两融 | market_margin_trading | ✅在产 | 因子构造待冻结 |
| C3 大宗折价 | market_block_trade | ✅在产（折价率已算） | 事件研究待做 |
| C4 席位 | dragon_tiger | ✅落库+seat 模块 | 负结果在案：禁朴素跟随 |
| C5 北向 | hk_hold 季度 | ✅仅季度 | 放弃日频幻想 |
| C6 ETF 申赎 | market_etf_share_snapshot | ✅在库 | 差分派生工程未立项 |
| C7 解禁 | event_calendar | ✅在产 | 前瞻窗口待冻结 |
| D 合成 | A+B+C 全部 | MOD-SIG-088 骨架在（testing） | strength 标定+判据预冻结 |

## §10 未决问题清单（呈批裁决项）

| # | 待裁 | 选项 |
|---|---|---|
| 10.1 | §2 输出契约四件套是否批准为资金行为层的官方输出面 | A 批准四件套（A 结构/B 性质/C 画像/D 合成）；B 改裁 |
| 10.2 | 四个行为归因模块收口 | 按 w5_1 出合并方案呈批（建议方向：SIG-088 为壳、SIG-021 为主链、SIG-022/banker_simulator 降级为特征供给） |
| 10.3 | 筹码引擎 trial 转正路径 | 以 A1 获利盘消费卡为转正考试（对齐裁定 #257④"指数级试点再评估"） |
| 10.4 | 逐笔委托（L2 订单流）是否开新采集 | 重定标路线的前提；tick_data 主表已无供给通道，先审计可得性再定 |
| 10.5 | 是否开"资金行为班"施工令（对标 st-formreg） | P0=收口三病灶+P1=数据审计+P2=判据预冻结（含本册 §8.8 多重检验规则） |
| 10.6 | ETF 申赎流量派生工程是否立项 | share_snapshot 差分即可，成本低 |

## §11 检索方法与证据等级

- 检索面：WebSearch 共 10 查（8 实效命中/2 失败），中英双语，含 GitHub topics 定向。
- 证据等级：✅=检索直接命中原文链接；⭕=检索摘要转述（原文未开/闭库，如慧博研报）；🔍=模型知识库（非本次检索，经典文献为主）；📋=仓内在册可直接复核。
- 已知检索盲区：券商金工研报原文多在慧博/迈博汇金闭库，仅拿到题录线索（§5 股东户数/两融/ETF 段）；ETF 资金流择时专项检索两次失败，该段为知识库级（🔍），呈批后可补定向检索。

---

## 核验更正记录（2026-10-13 总包 P0②③ 核验车道）

17 条核验（12 仓内＋5 外部）10+4 条坐实。实质更正 5 处（均已入正文内注）：
1. **§7.1 首行＋§9 C1（最重）**：大单五档（个股）数据源=tushare pro.moneyflow 主源 5540 行/日＋akshare fallback 属 `c1_market.money_flow`（tasks.yaml:182-195）；`market_fund_flow_daily` 是 akshare 东财大盘口径、fallback 显式置空（tasks.yaml:3687-3700）——原册把两者源描述嫁接错位。
2. **§7.1 market_money_flow**：为 money_flow 的 registry 逻辑名（日频），非盘中表；盘中只有板块级 sector_fund_flow。
3. **§7.2 路径两处**：seat_pattern_analyzer=limit_up/ 下单文件；sector_siphon 与 sector_divergence=两个独立文件。
4. **§4 arXiv:2509.05065 标题**：更正为真实标题《…Order Imbalance & Volatility II: An Artificial Market Generator》（Maitrier, Loeper & Bouchaud）。
5. **§9 A1 口径**：IND-CHIPS-001（chips.py）头注=production；trial 的是 MOD-REGIME-005 chip_distribution_engine（裁定 #257④）。banker_pattern_simulator 实际编号 MOD-SIG-113（production）。
6. 坐实项抽查：margin_trading（akshare_provider.py:1941 逐字命中）、block_trade 折价率（cohort_daily_ledger.py:34-35/:354）、股东户数 09-18 切源（tasks.yaml:602-617）＋supply_sentinel 诞生背景（yaml:11-12）、hk_hold 季度（tasks.yaml:2209-2218）、tick 半断供（yaml:633-634 逐字）、volume.py 恰 17 指标、LM2002 仓内零实现（全 src grep 零命中）、ETF 申赎差分未立项、#257④ trial 转述逐点吻合、LMSW 2002 RFS 15(4):1005-1047、Grinblatt-Han 2005 JFE 78(2)、开源金工重定标研报、北向 2024-05-13 停盘中实时披露（港交所 2024-04-12 通告）。
