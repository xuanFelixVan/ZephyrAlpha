---
ttl: task_bound
completes_when: "机构实践对标证据入仓且被引用处带案卷出处"
---

> 来源：外部终审交付目录原件 `dossier_institution_practice.md`（2026-09-26 终审会话定稿），本仓内改名只为避开非 ASCII 路径与编码门；正文逐字节未改。
> 原件 sha256：be4660fd463b848d6a1bab195ef49af4b5c4aac4e83a152b561358c4cb0282d6
> 口径律：本目录是**终审修正层**；凡与 `02_field_corrections_and_new_cases.md` 冲突以 02 册为准，本目录只在其上打补丁与增波，不改写既有 27 册正文。

# 案卷：量化机构技术图形实践调研（dossier_institution_practice）

- 调研员：research-institution
- 日期：2026-09-26
- 用途：为"A 股量化系统图形技术库终审"提供机构实践证据。只出案卷，不出裁定。
- 方法：WebSearch 真实检索 15 次（6 大主题，每主题 2-3 次不同关键词，中英文均覆盖），所有 URL 均为实际检索返回的链接，未编造。
- 可信度评级：A（学术论文/官方一手文档）＞ B（行业平台技术文档/开源项目文档）＞ C（社区/自媒体/券商引流内容，仅作社区实践证据）。

---

## §一 每主题发现表

### 主题 1：多时间框架分析（MTF）/多周期共振在职业交易中的实践

| # | 关键发现 | 来源 URL | 可信度 |
|---|---|---|---|
| 1.1 | MTF 三层框架是职业标准做法：HTF（高周期）定方向/市场体制、MTF（中周期）找形态区、LTF（低周期）精确入场；时间级别间距建议 4:1~6:1；三层结构（Regime Filter / Setup Identifier / Execution Trigger）被称为"institutional blueprint" | https://bellsforex.com/master-series/multi-timeframe-analysis.html | B |
| 1.2 | 行业量化口径：无 HTF 语境的 LTF 信号胜率约 55%，叠加 HTF 方向共振后升至 65-68%（约 10 个百分点提升）；逆 HTF 方向交易胜率掉至约 40%——MTF 共振的本质是"条件提升胜率"，可直接量化 | https://www.quantum-algo.com/glossary/multi-timeframe-analysis | B |
| 1.3 | MTF 冲突时的机构纪律：高周期永远优先（HTF 优先原则），冲突时减仓 50% 或不做；且强调必须对"时间级别组合"本身做过拟合检验（防止策略只在特定周期组合有效） | https://bellsforex.com/master-series/multi-timeframe-analysis.html | B |
| 1.4 | 三时间框架完整工作流（Bias/Setup/Entry），"全对齐窗口"即 A+ 交易窗口；级别冲突时不做折中、不做平均 | https://www.quantum-algo.com/academy/multi-timeframe-mastery/ | B |
| 1.5 | 中文社区"双周期共振战法"：15 分钟定多空方向 + 1 分钟找止跌拐点入场——与 Owner 的"15分钟触及趋势线上沿时看 1 分钟两次不过前高即抛售"用法完全同构；铁律"大周期定生死，小周期定细节"，1 分钟信号不可单独使用（单独 1 分钟拉升大概率是诱多骗线） | https://www.toutiao.com/article/7672760147211518506/ | C |
| 1.6 | 中文社区分层共振体系："日线判向、60 分控节奏、15 分择点位"；离场同样分层（一级预警减仓/二级清仓：两个及以上周期同时转弱即无条件离场） | https://www.toutiao.com/a7671284574109876745 | C |
| 1.7 | 老牌"三重滤网"系统（Elder Triple Screen）即多周期共振的可系统化鼻祖：大周期 MA 定方向→中周期找回调→小周期指标金叉入场 | https://licai.jiantou8.com/ask/qa_7507336.html | C |
| 1.8 | 国内零售量化已工程化该框架：QMT 平台用 REFDATA 跨周期引用函数 + 共振条件逻辑实现"日线+60分钟+15分钟"共振选股，注意点为跨周期数据时间对齐 | https://licai.jiantou8.com/ask/qa_7488512.html | C |

**要点**：MTF/"多周期共振"是职业交易者（含机构风格内容）广泛使用的成熟框架，"HTF 定方向 + LTF 找入场/出场确认"与 Owner 的 15分钟+1分钟 用法完全同构，非个人臆造。但需注意方向性差异：主流纪律是**自上而下（HTF 优先，LTF 只做择时确认）**；Owner 的"从小级别依次影响大级别"（自下而上）在主流框架中属于少数派路径——LTF 率先转弱通常被解读为"提前离场信号"而非"决定大级别方向"，两者可兼容，但后者更接近反转交易逻辑，风险更高，恰是需要矩阵法用数据裁定的部分。

### 主题 2：主流平台形态识别能力对标

| # | 关键发现 | 来源 URL | 可信度 |
|---|---|---|---|
| 2.1 | TradingView 官方"自动图表形态"技术路线：建立在枢轴点上——每根 K 线看前 5 根+后 5 根确认枢轴，扫描最近 600 根 K 线；支持"进行中"形态（最后两点未定时即早期识别）并给目标价；多形态重叠取最高优先级；共 15 个形态指标，Premium 订阅功能 | https://www.tradingview.com/blog/cn/auto-chart-patterns-37311/ | A（官方博客） |
| 2.2 | TradingView 生态主流社区实现 = 枢轴点 + 几何规则验证：峰值相等用 ATR/百分比容差，加最小高度/宽度/R:R 过滤；再叠加突破确认引擎（ATR 突破缓冲、实体收盘确认、量能过滤、冷却期） | https://fr.tradingview.com/scripts/tradingstrategies/ | B |
| 2.3 | Trendoscope Auto Chart Patterns（递归 zigzag 法）：多级别递归 zigzag 提取枢轴→检查最近 5-6 个枢轴能否构成有效"趋势线对"（上线触所有峰、下线触所有谷、区间内 K 线不越界）→按趋势线方向/收敛发散/平行关系分类为楔形/三角/通道。纯几何规则，无模板匹配 | https://ar.tradingview.com/scripts/zigzagindicator/page-5/ | B |
| 2.4 | 社区"AI 评分"形态引擎：在几何验证之上加 5 维评分（形状拟合/对称性/量能衰减/时间窗口/趋势语境 EMA21-55），跟踪 Detected/Completed/Failed 生命周期——**失败形态本身作为强反向信号**是该类引擎的卖点 | https://www.tradingview.com/scripts/statistics/page-25 | B |
| 2.5 | 平台方承认的固有局限：枢轴确认需右侧 K 线（确认延迟，防重绘的代价）；形态质量分只度量几何符合度，"不代表未来胜率"；同一结构两个交易者可识别出不同形态（识别本质是解释性的） | https://ar.tradingview.com/scripts/page-18 | B |
| 2.6 | 文华财经"云端形态选股"（官方文档）：机制 = 计算所选形态收盘价序列与全部合约最近 N 日收盘价序列的**相关系数**，按相关系数排序筛选——即模板/相关性匹配路线，非几何规则；支持 15分钟/日/周线，取样最多 500 根 | https://www.wenhua.com.cn/new_guide/Wh7/view3-5.html | A（官方文档） |
| 2.7 | 同花顺"形态识别/形态选股"：基于预设经典形态规则自动标注，并提供**基于历史数据的回测统计（历史上涨概率、平均涨幅）**作为决策参考——大厂把"识别+历史胜率统计"打包成零售功能 | https://mams.10jqka.com.cn/new/server/html/98183.html 、https://licai.jiantou8.com/ask/qa_7504160.html | B（官方教程）/C（引流问答） |
| 2.8 | 通达信本身无官方形态引擎，但存在 ChanlunX 等 DLL 插件生态把缠论笔/线段/中枢数据接入通达信公式选股体系 | https://blog.csdn.net/gitblog_00346/article/details/162550826 | C |

**要点**：平台形态识别存在三条清晰技术路线——(1) 枢轴点+几何规则+ATR 容差（TradingView 官方及主流社区）；(2) 收盘价序列相关系数模板匹配（文华财经）；(3) 在几何规则之上叠加评分/ML 排序（社区进阶版）。ML 用于打分而非定义形态。项目自研的 10+ 形态模块（缠论/庄股/假突破等）在"定义层"已超过任何主流零售平台，无建库缺口。

### 主题 3：A 股特有场景（缠论/庄股/假突破）的量化实践现状

| # | 关键发现 | 来源 URL | 可信度 |
|---|---|---|---|
| 3.1 | 缠论算法化已成熟：chan.py 开源框架实现 K 线合并→分型→笔（严格/非严格）→线段（seg_algo 可选 chan 特征序列/break 算法）→中枢（合并/扩展）→买卖点全流水线；支持 1 秒到年线全周期、多级别联立分析、增量更新、缓存优化 | https://www.hqwc.cn/a/504375.html 、https://www.hqwc.cn/a/503938.html | B |
| 3.2 | chan.py 关键参数即量化缠论的核心旋钮：bi_strict（严格笔）、seg_algo、zs_combine（中枢合并）、divergence_rate=0.9（背驰阈值）、min_zs_cnt；可视化支持笔/线段/中枢/买卖点/趋势线全绘制 | https://blog.gitcode.com/eaf38ed1c2d375acbc403e562f747e07.html | B |
| 3.3 | 缠论量化的已知痛点：线段划分算法无绝对优劣，"chan 算法"适合震荡市、"break 算法"适合趋势市——算法对行情风格敏感，需按市场状态切换（这本身就是"格子分层"的一个维度） | https://blog.gitcode.com/eaf38ed1c2d375acbc403e562f747e07.html | B |
| 3.4 | ChanlunX 通达信插件证明缠论算法化已下沉到散户工具链：可在通达信公式内直接调用笔/线段/中枢 DLL 函数做三条件选股（上升线段+突破笔中枢+放量 1.2 倍） | https://blog.csdn.net/gitblog_00346/article/details/162550826 | C |
| 3.5 | 庄股识别的量化口径（社区总结）：筹码集中度公式 = 0.4×股东户数降幅 + 0.3×大宗交易占比 + 0.3×分时异常天数，>70 分高风险；辅以 Level-2 控盘度指标（委托买卖量比>5:1 持续 30 分钟、万手大单撤单率>60%）、建仓期特征（60 日振幅<15% 且换手<1%） | https://xueqiu.com/8515332715/322938388 | C |
| 3.6 | 基于监管处罚书的庄股回测（含金量较高的社区研究）：全市场 5009 只样本，从证监会处罚决定书提炼四个可量化"物理特征"——账户组持股占流通股>10%、单日买入占市场成交>10%（181 日）、自买自卖对倒占成交最高 25.32%、价格独立行走（+175.58% vs 同期深成指 -9.36%，偏离 185 个百分点）；弱信号"放量滞涨日占比"高组暴跌 64.3% vs 低组 54.8%（方向对、力度弱，只能当佐证）；新旧庄股对比：注册制后多账户联合坐庄、周期 6-12 个月、出货靠大宗+量化对倒 | https://www.toutiao.com/article/7686275273276293683 | C |
| 3.7 | 盘口级庄股手法特征（对倒/试盘/洗盘）的定性规则集：低位窄幅+巨量长阳后回落=试盘；高开不攻缓慢回落=吸引买盘暗中出货；大单净流入但股价跌=对倒打压；回调浅+缩量=锁仓良好；换手>20% 疑似对倒 | https://www.caiair.cn/news/zhuanggu-zongji-kanpan-jiqiao-501.html 、https://www.jiuyangongshe.com/a/4dwzpv4mwlb | C |
| 3.8 | 假突破量化统计（2026 年数据）：日内突破失败率 50-70%，且**随时间级别单调变化**——1 分钟 68-72% 失败、5 分钟 60-65%、15 分钟 55-60%、小时线约 50%、日线 40-45%；定义 = 收盘回到前 20 根 K 线区间内（5 根 K 线窗口）；量能是唯一最可靠实时判别（<1.5-2 倍均量的突破大概率是流动性扫掠） | https://fortraders.com/blog/false-breakouts-why-they-happen-how-to-trade | B |
| 3.9 | 假突破过滤的回测证据：基准突破胜率 38.4%；量能过滤（1.5 倍均量）→48.2%；收盘位置过滤（收盘于突破 K 线区间上/下 25%）→44.8%；**回踩确认过滤→56.2%**（代价：交易数-58%）；三过滤叠加→62.4%、Sharpe 0.74→1.18（代价：交易数-74%）；假突破占突破信号 50-70% | https://quantengines.com/blog/breakout-trading-strategy | B |
| 3.10 | ORB（开盘区间突破）假信号过滤：约 70% 开盘区间突破在首小时失败；三过滤器 = 量能较前五日同时段中位数扩张>35%、区间宽度/14 日 ATR 异常（<0.4 高危假突破）、实体收盘越过边界而非影线 | https://fazencapital.com/learn/en/orb-false-breakout-filters | B |
| 3.11 | ML 假突破过滤器（行业综述口径）：随机森林（特征含日内波动离散度、订单簿失衡、动量衰减、宏观体制旗标）可削减 30-40% 假信号、Sharpe 0.92→1.27；2000 年代实证：股市突破假信号率约 45%，危机期>60% | https://api.finexus.net/api/news/events/78bb23ef-a64c-4b71-932a-fc46ede8fd2c/html | B |

**要点**：缠论量化在开源社区已高度成熟（chan.py 可直接对标/复用），庄股识别有监管处罚书背书的可量化特征但学术级研究缺失，假突破有最丰富的量化证据（失败率随时间级别单调变化+三过滤器有效）。三者共同点：**都已有"定义层"方案，缺的都是条件组合下的统计检验**。

### 主题 4：支撑阻力位/趋势线算法方案

| # | 关键发现 | 来源 URL | 可信度 |
|---|---|---|---|
| 4.1 | 工业级 S/R 方案 = DBSCAN 密度聚类：收集回看期全部 OHLC 价格点→核密度估计做价格热力图→DBSCAN 聚簇、簇心即支撑阻力→按成交量加权→按近期交互指数衰减加权；与 Volume Profile（POC/VAH/VAL）交叉验证的点位置信度更高（引 CFA Institute 口径：量能验证过的支撑位守住概率高 23%） | https://www.tradealgo.com/trading-guides/ai-trading/ai-technical-analysis-guide | B |
| 4.2 | 学术前沿 DeepSupp（arXiv 2025, HKUST）：多头注意力机制 + 相关性矩阵 + 自编码器做表征学习，最终支撑位仍用 **DBSCAN 无监督聚类**提取；在 S&P 500 上六项金融指标全面超越六个基线；论文确认 SR 研究谱系：Osler (2000/2001) 实证央行/机构发布的 S/R 位对未来价格有统计显著影响、高频数据价格更可能在 S/R 位反弹；Menkhoff (2010) 调查：86% 专业基金经理使用技术分析 | https://ar5iv.arxiv.org/html/2507.01971 | A |
| 4.3 | DBSCAN 用于 A 股箱体识别的社区实践：在价格-时间平面聚簇识别箱体边界，明确警告参数敏感性（ε 影响大）、不同密度簇混杂时失效、计算复杂度问题——与项目"网格搜索调参"能力天然互补 | https://juejin.cn/post/7560516750553071679 | C |
| 4.4 | TradingView 上 DBSCAN S/R 指标（dandrideng）：对历史 K 线关键顶底点做密度聚类，核心区叠加次数越多支撑阻力越强；作者明示"聚类算法不适用于所有市场，需按市场和时间级别调参" | https://www.tradingview.com/script/K7GER7s2/ | B |
| 4.5 | 密度聚类算法横评（DOAJ 期刊论文）：Dynamic Quantum clustering、Weighted Adaptive Mean Shift、DBSCAN、EM、k-means 等在同一股市数据上对比，Dynamic Quantum 因适应模式变化胜出（配对 t 检验显著）——聚类路线内部也有选型空间 | https://doaj.org/article/740b04b4e82c4ac1b959a9d4ef210a6a | A |
| 4.6 | RANSAC 趋势线拟合的标准实现（LuxAlgo Machine Learning Regression Trend，MT 平台同款）：随机抽 2 点拟合直线→容差内为内点→保留内点最多的模型，迭代至最大次数；相比普通线性回归更保守（对离群值不敏感）；离群点数量本身可作为噪声度量；参数 = 最小内点数/容差（Auto 自适应）/最大迭代 | https://fr.tradingview.com/scripts/trend-channel/ 、https://tradingfinder.com/products/indicators/mt4/machine-learning-regression-trend-free-download/ | B |
| 4.7 | 供需区（Supply/Demand Zone）识别的规则化方案：consolidation-then-impulse——先找"基地"（连续 N 根实体<ATR 的盘整 K 线）→紧跟脉冲 K 线（实体>1.5×ATR）→区顶/区底取基地 K 线的最高/最低；区域生命周期管理（Active→Tested→Mitigated→Deleted），**新鲜度规则与传统 S/R 相反：测试次数越多区域越弱**（未回测的"新鲜区"最强，回踩确认概率口径 60-70%） | https://de.tradingview.com/script/4TN4nsy6-Auto-Supply-Demand-Zones-Proozac 、https://crosstrade.io/learn/price-action/supply-and-demand-zones | B |
| 4.8 | 供需区方法的诚实局限（业内自评）："同一张图给五个供需交易者会画出五套不同的区域"；假说合理但不可证明（看不到订单簿残留），正确做法是按一致规则画区+定义失效条件+度量结果 | https://fipsapp.com/blog/supply-and-demand-trading | B |

**要点**：S/R 选型图谱清晰——(1) 传统枢轴点（TradingView 官方 5/5 根确认）；(2) DBSCAN 聚类（工业+学术双主流，DeepSupp 学术与 tradealgo 工业方案殊途同归）；(3) RANSAC 趋势线（成熟开源实现，参数少、可解释）；(4) 供需区规则法（consolidation-then-impulse，几何规则可完全代码化）。共同教训：所有方案都强调**参数必须按品种/周期/波动状态自适应（ATR 归一化）**，且都承认识别层易、检验层难。

### 主题 5："多周期共振矩阵/格子"相关实践（条件分层统计）

| # | 关键发现 | 来源 URL | 可信度 |
|---|---|---|---|
| 5.1 | 最接近"共振矩阵"的机构级实践——华泰金工多维择时研究：26 个底层因子（估值/情绪/资金/技术四类）× 按开仓方向拆分的四条子路径（追高/抄底/追空/逃顶），**逐格统计各因子在各路径下的夏普，每路径只取夏普前 8 的子维度**；路径优选模型（B 模型）日频夏普 1.72，显著优于不分层的 1.48；关键结论："量价指标擅长追高、期权隐波擅长抄底"——即不同格子适用不同信号，指标应只在其擅长场景启用 | https://stockfinance.sina.cn/stock/go.php/paper/reportid/832861541425/index.phtml 、https://t.10jqka.com.cn/pid_628501373.shtml | A（券商金工研报） |
| 5.2 | 深度学习 A 股策略论文（2025，alphaXiv）：网格搜索模块系统遍历 1344 个参数组合（止盈 1.0-6.0%×止损 0.8-3.0%×持有期 3-15 天×移动止损），多目标函数 = 胜率 25%+风险调整收益 35%+换手效率 25%+一致性 15%；用 HMM 识别市场体制、**逐体制确定最优参数**；严格 walk-forward（2010-2020 训练/2020-2021 验证/2021-2024 样本外）+ 真实成本建模（佣金+印花税+冲击成本） | https://www.alphaxiv.org/overview/2506.6356 | A |
| 5.3 | 大规模条件组合回测的方法论警示（StatOasis，36,252 次回测）：在**零边际数据**上随机组合 5000 条规则做搜索，最好结果年化 6.4%、Sharpe 0.65——"搜索出来的冠军"必须扣除搜索空间本身产生的虚假 alpha；真实 SPY 上 5000 条规则仅 0.2%（10 条）在样本内外都跑赢买入持有；垃圾条件（星期几）在零边际数据上会进入 top25，在真实数据上不会——这提供了真伪判别法 | https://statoasis.com/post/how-to-prepare-your-trading-strategy-for-live-markets-learn-robustness-testing | B |
| 5.4 | 条件过滤的系统检验范例（StatOasis，15,552 次回测）：对 RSI(2) 基准策略逐个检验量能/波动过滤器（96 个匹配配置×每过滤器），方法学要点：**镜像测试**（若过滤器和它的反面都有效，即噪声）、最小样本门槛（过滤后信号<15% 即弃用）、过滤器必须在全参数网格上有效而非只在最优点有效（"只在单一阈值有效的过滤器是参数不是过滤器"）、过滤器是修饰器不能拯救错误方向的主逻辑 | https://www.statoasis.com/post/volatility-filters-that-work-boost-strategy-performance-of-rsi2 | B |
| 5.5 | "条件胜率"理论框架（findices）：**指标没有独立胜率，只有规则的条件胜率**——脱离"品种/周期/入场条件/出场逻辑/成本模型/样本外协议"的完整系统定义，"哪个指标最好"是无意义的问题；样本量≥30 独立交易仅是弱统计下限，聚类结果（同一波动事件的连续信号）会虚增有效样本 | https://findices.com/articles/best-technical-analysis-indicators-a | B |
| 5.6 | 券商金工"技术指标月报"式实践：27 个技术指标在沪深300/中证500/中证1000+31 个申万行业指数共 34 个指数上逐格回测；单信号维度：量价"背离"类指标平均超额年化 3.75%；多信号合成（5/7 信号）+ 滚动搜索法选最优指标组合；按风险偏好分"滚动稳健/滚动追涨"两套 | http://fxbaogao.com/detail/4928061 | B（研报摘要页） |
| 5.7 | A 股因子研究的标准基础设施即"格子统计"：分层回测（按因子值分 5/10 组逐组统计年化/波动/夏普/回撤/胜率，检验单调性）+ IC/RankIC/ICIR + walk-forward 滚动验证——与 Owner 要的"每个格子的夏普率"在方法论上同构，只是分层轴从"因子值分位"换成"周期×形态条件" | https://xuangutong.com.cn/article/100159281 、https://blog.csdn.net/gitblog_00889/article/details/153901774 | C/B |

**要点**：未检索到任何机构或社区公开做过 Owner 所设想的**完整"多时间框架 × 多形态"矩阵**（每个格子统计胜率/夏普）的一手案例。但"按条件分层、逐格统计、只在高夏普格子里启用信号"的方法论本身是机构标配（华泰金工路径优选、A 股论文体制分层网格搜索、因子分层回测体系均为同构实现）。Owner 的矩阵法是把机构标准方法论应用到"周期×形态"轴上的自然推广——方向有据，且 StatOasis 的搜索偏差证据（5.3/5.4）恰好说明：矩阵法**必须**配套镜像测试、最小样本门槛、全网格一致性检验，否则格子数爆炸后必然挖出虚假高夏普格子。

### 主题 6：K 线形态有效性的真实结论（学术+业界证伪/证实）

| # | 关键发现 | 来源 URL | 可信度 |
|---|---|---|---|
| 6.1 | Marshall, Young & Rose (2006, Journal of Banking & Finance)：DJIA 35 只股票 1992-2001，bootstrap 方法检验 K 线形态，**扣除交易成本后无统计显著的预测力/获利性**——最常被引用的系统性证伪 | https://lup.lub.lu.se/luur/download?func=downloadFile&recordOId=8877738&fileOId=8877838 、https://alpha-suite.org/blog/candlestick-patterns-evidence | A |
| 6.2 | Marshall, Young & Chang (2006/2008)：同方法检验东京证券交易所最大 100 只股票（1975-2002），同样无预测力——K 线技术发源地市场亦被证伪；Fock et al. (2005) 用 DAX 期货 5 分钟数据加 MA/RSI/MACD 过滤也无改善 | https://businessperspectives.org/images/pdf/applications/publishing/templates/article/assets/1934/imfi_en_2007_04_1_Goo.pdf | A |
| 6.3 | 正面证据并存：Caginalp & Laurent (1998) S&P500 全样本 8 种三日反转形态 Z 检验全部显著（短期）；Goo, Chen & Chang (2007) 台湾市场 26 形态弱正（看跌形态 3-4 天、看涨 9-10 天持有期）；**Zhu, Atri & Yegen（中国市场）：bearish harami 对低流动性股票有效、bullish engulfing/piercing 对高流动性小盘有效**——A 股直接证据，且与流动性分层挂钩 | https://businessperspectives.org/images/pdf/applications/publishing/templates/article/assets/1934/imfi_en_2007_04_1_Goo.pdf 、https://ajosr.org/wp-content/uploads/journal/published_paper/volume-3/issue-4/ajsr2025_2htV4t35.pdf | A |
| 6.4 | 泰国 SET50 十年数据：多数形态均值收益与零无差异；**用 %D/RSI/MFI 技术过滤并不能提高形态的获利性或预测准确度**——简单叠加指标过滤非万能 | https://murex.mahidol.ac.th/en/publications/profitability-of-candlestick-charting-patterns-in-the-stock-excha | A |
| 6.5 | 失效机理剖析：形态出现频率太高（doji 约 5-8% 交易日）稀释信息量；**去语境化**（无位置/无趋势/无量能的"裸形态"）是主因——形态必须作为条件与其他轴组合才有价值，这从反面论证了条件矩阵路线 | https://alpha-suite.org/blog/candlestick-patterns-evidence | B |
| 6.6 | Bulkowski《Encyclopedia of Chart Patterns》统计体系（500 股票 1991-1996 库 + 三十年数据）：63 种形态的突破后平均涨幅/失败率/目标达成率全量统计（如三重底：盈亏平衡失败率 13%、平均涨幅 46%、目标达成 74%、回踩率 65%）；关键规律：**同一形态牛市/熊市表现分化（看涨形态熊市失败率大增）→ 市场体制过滤是统计必需而非可选项**；高频出现形态与高性能形态排名互不相关 | https://thepatternsite.com/id75.html 、https://www.thepatternsite.com/frequency.html 、https://tradelosstracker.com/library/book/344-encyclopedia-of-chart-patterns-second-edition-bulkowski/extended | A（原书数据站点） |
| 6.7 | TA-Lib 形态的机械回测（外汇，23 年数据，105 次 walk-forward 回测，1813 笔交易）：21 形态中 6 种在 5 个货币对上完全无法触发（TA-Lib 严格机械标准下）；能触发的最好形态（Doji Star）平均收益仅 +0.002%，全部形态胜率 6%-35%，一致性（盈利测试窗口占比）最高 42.5%——TA-Lib 检测层"能用"与信号层"有边际"是两回事 | https://www.portfoliosignals.com/blog/forex-candlestick-backtest | B |
| 6.8 | TA-Lib 全量形态回测（S&P 500，2000 至今，60+ 形态，2:1 盈亏比规则）：**最高形态胜率仅 47.71%**，看涨形态出现后更可能先触发止损而非止盈；结论：单独使用无预测价值，需结合趋势线/量能/确认 K 线 | https://readmedium.com/backtesting-all-candlestick-patterns-which-is-the-best-72a0ea8afcb4 | B |
| 6.9 | A 股 TA-Lib 实战调优案例（CSDN）：同一 CDL2CROWS 形态，银行股原始胜率 65% vs 科技股 42%；加成交量过滤后 72%/58%，再加 50 日均线趋势过滤后 75%/63%——**形态胜率强烈依赖标的风格与过滤条件，且过滤器的提升幅度可量化**；作者给出的工作流 = 基准测试→单因子分析→参数网格搜索+前向滚动回测（避免过拟合，目标夏普/卡尔玛最优） | https://blog.csdn.net/numpy6sculptor/article/details/155184034 | C |

**要点**：学术主流结论 = "裸 K 线形态无独立获利性"（Marshall 系列三连证伪），但存在两条系统性例外：(1) 新兴市场弱正（台湾、中国大陆，且按流动性分层）；(2) 体制/条件依赖（Bulkowski 牛熊分化、A 股调优案例 65%→75%）。这两条例外恰好都指向同一个工程结论：**形态的价值在条件组合（格子）里，不在形态本身**。

---

## §二 对"接线优先于建库"的机构证据

1. **"识别层"已全面商品化，无护城河。** TradingView 官方自动形态（枢轴+几何规则，Premium 功能）、文华财经云端形态选股（相关系数匹配）、同花顺形态识别（预设规则+历史胜率统计）——三大零售平台都已内置形态识别，且技术路线公开（§一 主题 2）。项目已有 TA-Lib 61 形态 + 215 列指标 + 10+ 形态模块，定义层存量已超过任何零售平台。机构实践中"如何定义形态"不是差异化来源。

2. **差异化在"检验层"，且检验层是稀缺能力。** 同花顺把"历史回测统计（历史上涨概率/平均涨幅）"作为形态识别的卖点捆绑（https://mams.10jqka.com.cn/new/server/html/98183.html ）；A 股 TA-Lib 调优实践的核心工作流就是"基准→单因子→网格搜索+walk-forward"（https://blog.csdn.net/numpy6sculptor/article/details/155184034 ）——即 Owner 说的"接线进 T1/T2 网格搜索"正是这类工作流的系统化。

3. **信号定义得再好，不进条件检验就是负资产。** StatOasis 证明搜索空间本身年产 6.4% CAGR/0.65 Sharpe 的虚假冠军（https://statoasis.com/post/how-to-prepare-your-trading-strategy-for-live-markets-learn-robustness-testing ）；findices 证明"指标无独立胜率，规则才有条件胜率"（https://findices.com/articles/best-technical-analysis-indicators-a ）。10+ 个形态模块如果不逐格检验，等于把 215 列指标的过拟合风险又复制了一份。

4. **机构真实做法印证。** 华泰金工对 26 个择时因子逐路径（格子）统计夏普、只在前 8 格启用信号（https://t.10jqka.com.cn/pid_628501373.shtml ）；券商金工月报对 27 个指标在 34 个指数逐格回测（http://fxbaogao.com/detail/4928061 ）——机构的工程重心在"信号×条件×标的"的统计矩阵，不在新增信号定义。

**案卷结论（证据指向）**：四条独立证据链（平台商品化、回测偏差研究、条件胜率理论、机构研报实践）一致指向"接线优先于建库"。

## §三 对"多周期共振矩阵法"的机构对标

1. **方法论同构的机构级实现存在**：华泰金工"因子×路径"矩阵（逐格夏普、按格优选，夏普 1.48→1.72，https://stockfinance.sina.cn/stock/go.php/paper/reportid/832861541425/index.phtml ）与 A 股深度学习论文的"1344 参数网格×HMM 体制分层"（https://www.alphaxiv.org/overview/2506.6356 ），都是"逐格统计收益/夏普+按格选用"的成熟实践；A 股因子研究的分层回测体系（5/10 分组逐组统计夏普）是全行业标准基础设施（https://xuangutong.com.cn/article/100159281 ）。Owner 的矩阵法 = 把这套标准方法论的分层轴换成"时间级别×形态条件"。

2. **矩阵法的最小版本已有行业口径**：LTF 信号单独 55% vs 叠加 HTF 共振 65-68%（https://www.quantum-algo.com/glossary/multi-timeframe-analysis ），假突破过滤 38.4%→62.4%、Sharpe 0.74→1.18（https://quantengines.com/blog/breakout-trading-strategy ），A 股形态+趋势过滤 65%→75%（https://blog.csdn.net/numpy6sculptor/article/details/155184034 ）——"条件叠加提升格子表现"在多个独立数据集上反复复现，矩阵法的前提成立。

3. **但完整"多周期×多形态"矩阵无公开先例**：检索到的最接近实现是双周期两格对比（quantum-algo）和因子×路径矩阵（华泰），未见任何公开的"5×5 时间级别×形态"全矩阵回测案例。此为 Owner 方法的原创性所在，也意味着无外部经验可借鉴格子的统计功效问题（见 §六）。

4. **矩阵法的配套纪律有明确证据**：StatOasis 镜像测试（过滤器与其反面同有效即噪声）、最小样本门槛（信号留存<15% 即弃）、全网格一致性（只在单点有效的条件是参数不是过滤器）三条规则（https://www.statoasis.com/post/volatility-filters-that-work-boost-strategy-performance-of-rsi2 ）应作为矩阵法的内置质检，否则格子数组合爆炸后必然产出虚假高夏普格子（搜索偏差：5000 规则里 41.5% 样本内盈利但仅 0.2% 双期跑赢基准）。

5. **体制分层是被反复验证的必要轴**：Bulkowski 同一形态牛熊失败率大分化（https://tradelosstracker.com/library/book/344-encyclopedia-of-chart-patterns-second-edition-bulkowski/extended ）、华泰路径优选、A 股论文 HMM 分层——矩阵若不含市场体制维度，格子的夏普会被牛混合熊稀释。

## §四 对支撑阻力/趋势线算法的选型证据

1. **DBSCAN 聚类是工业+学术双主流**：工业方案（tradealgo：KDE 热力图+DBSCAN+量能加权+时间衰减，https://www.tradealgo.com/trading-guides/ai-trading/ai-technical-analysis-guide ）与学术前沿（DeepSupp：注意力表征学习后仍用 DBSCAN 提取支撑位，https://ar5iv.arxiv.org/html/2507.01971 ）殊途同归；TradingView 社区与 A 股掘金社区均有开源可复现实现（https://www.tradingview.com/script/K7GER7s2/ 、https://juejin.cn/post/7560516750553071679 ）。**证据强度最高的选型**。
2. **RANSAC 趋势线是成熟且可解释的方案**：LuxAlgo 实现给出完整算法参数集（最小内点/容差 Auto 自适应/最大迭代），离群点数量可兼作噪声指标（https://fr.tradingview.com/scripts/trend-channel/ ）；MT4/MT5 有移植版。适合 Owner 场景中"下降通道趋势线"这类结构化趋势线拟合。
3. **供需区规则法完全可代码化**：consolidation-then-impulse（基地 N 根实体<ATR + 脉冲>1.5×ATR）+ 新鲜度生命周期（Active/Tested/Mitigated），社区共识口径"新鲜区首次回测确认概率 60-70%、测试越多越弱"（https://crosstrade.io/learn/price-action/supply-and-demand-zones 、https://de.tradingview.com/script/4TN4nsy6-Auto-Supply-Demand-Zones-Proozac ）——与传统 S/R"测试越多越强"方向相反，两者不可混用，矩阵法恰好能对这两种假设分别裁定。
4. **所有方案共同的前置条件：ATR 归一化自适应**。TradingView 官方容差、LuxAlgo RANSAC Auto 容差、供需区 ATR 脉冲阈值、DBSCAN ε 敏感性警告——横跨全部四类方案的共同工程教训。
5. **S/R 位本身有实证有效性背书**：Osler 系列研究（机构发布 S/R 位对价格有统计显著影响、高频数据更可能反弹）与 86% 基金经理使用技术分析的调查（经 DeepSupp 论文引用，https://ar5iv.arxiv.org/html/2507.01971 ）。

## §五 A 股特有（缠论/庄股/假突破）的社区实践证据

1. **缠论：算法化成熟，可直接对标 chan.py**。分型/笔/线段/中枢/背驰全流水线有开源参考实现（含背驰阈值 divergence_rate=0.9 等量化旋钮），且已知痛点明确（线段算法对行情风格敏感，chan 算法适合震荡、break 适合趋势——应作为矩阵的一个条件轴而非固定选择）（https://www.hqwc.cn/a/504375.html 、https://blog.gitcode.com/eaf38ed1c2d375acbc403e562f747e07.html ）。项目已有缠论模块属于社区主流路线。
2. **庄股：有监管处罚书背书的量化特征，但无学术级验证**。最扎实证据是处罚书回测（§一 3.6：持股>10%/成交占比>10%/对倒 25.32%/价格独立 185pct 四特征 + 放量滞涨弱信号），社区筹码集中度公式（0.4/0.3/0.3 加权）可复现（https://xueqiu.com/8515332715/322938388 ）。风险提示：庄股识别的公开内容多为避雷视角（识别出货），把"庄股行为"反转为**交易信号**（如跟庄）的公开量化实践未检索到。
3. **假突破：证据最充分的 A 股可用模块**。失败率随时间级别单调（1 分钟 68-72% → 日线 40-45%）、三过滤器（量能/收盘位置/回踩）提升路径完整量化（38.4%→62.4%，Sharpe 0.74→1.18）（https://fortraders.com/blog/false-breakouts-why-they-happen-how-to-trade 、https://quantengines.com/blog/breakout-trading-strategy ）。注意：这些统计来自美股/期货/外汇，A 股涨跌停制度下的假突破统计未检索到（见 §六）。
4. **游资 vs 庄家需区分建模**：社区共识"短线游资≠长线庄家"（游资快进快出不留底仓、庄家控盘数月以上），两类主体的图形足迹不同（https://www.toutiao.com/article/7660345357116686888/ ）——项目"庄股形态"模块若不区分两者，条件轴会互相污染。

## §六 低把握/未覆盖项（如实申报）

1. **未检索到**任何机构/社区公开的完整"多时间框架 × 多形态"矩阵回测一手案例（§三.3）。矩阵法方向有同构方法论支撑，但格子粒度（多少个周期×多少形态）的统计功效设计无外部经验可循——格子里样本量不足时的置信度处理（如贝叶斯收缩、最小交易数门槛）需自建。
2. **未检索到**私募/公募内部使用图形技术的直接一手资料；本案卷以"机构风格教育内容+券商金工研报+开源社区"三角近似，券商金工研报（华泰等）是最接近机构一手的证据，但其因子体系以量价/估值/情绪为主，**纯图形形态因子在券商金工体系中地位边缘**——这一"边缘化"本身是否因为形态无边际（Marshall 证伪）还是因为难以工程化，证据不足以裁定。
3. **未检索到** A 股涨跌停制度下假突破/突破统计的系统研究（现有假突破统计均来自无涨跌停限制市场）；T+1 制度对"1 分钟级别信号→当日抛售"执行路径的约束（Owner 场景中"不用等 15 分钟走完即抛售"在 T+1 下的可执行性）未在检索中出现，属于本案卷无法覆盖的 A 股制度性问题。
4. **tradealgo 声称** Two Sigma/Renaissance 用 CNN 做形态识别"准确率 82%（据专利文件）"——无法从可靠来源核实，按营销内容处理，不作为证据采用（https://www.tradealgo.com/trading-guides/ai-trading/ai-technical-analysis-guide ）。
5. **供需区/订单块有效性无学术检验**：业内自评"假说合理但不可证明"（https://fipsapp.com/blog/supply-and-demand-trading ）；文华财经相关系数匹配形态选股的官方文档未给出任何胜率统计。这两类信号的"定义存在、边际未证"状态与 TA-Lib 形态在回测前的状态相同。
6. **中文来源质量警示**：庄股/缠论/双周期共振的中文一手内容大量来自自媒体与券商引流问答（可信度 C 级），数字（如"胜率极高"、筹码公式权重）未经独立验证；监管处罚书回测（§一 3.6）与 chan.py 代码文档是其中相对最可靠的两类。
7. **Bulkowski 统计的适用边界**：其数据集为美股日线（1970s-2010s），A 股的直接证据只有 Zhu/Atri/Yegen 一篇（按流动性分层的弱正结果）；形态统计的跨市场移植（美股→A 股、日线→15 分钟线）在检索中无系统研究支撑，是矩阵法需要自行回答的问题。

---
*案卷完。共 6 章，引用 URL 43 处（去重后 36 个独立来源），其中 A 级 12 处、B 级 17 处、C 级 14 处。*
