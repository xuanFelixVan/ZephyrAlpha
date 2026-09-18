---
ttl: task_bound
rule_form: data
verifiability: manual
title: 全网算法挖矿摘要——2023-2026 因子挖掘实践检索（2026-09-19 通宵车道）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
session: st-bizmine-algo-20260919
---

# 全网算法挖矿摘要（st-bizmine-algo-20260919）

> **一句话**：四主题域 16 组检索命中（英文论文/开源实现/中文社区/博客四层全沾）；行业惯例证据链指向**预注册小矩阵+多重检验纪律**，与今晚 TICKM 协议/#304 数学一致——全网格扫描在学界与业界均非主流做法（详见 matrix_necessity_verdict.md）。来源分级：[论文]=peer-reviewed/working paper；[开源]=可运行实现；[社区]=量化社区/研报转载；[博客]=个人博客/媒体。检索时间 2026-09-19 04:10-04:40 UTC+8，后端限流 429 时已换词重试；未能打开全文的只引检索摘要并如实标注。

## 1. 开源因子库与合成算法

| 算法/库 | 要点 | 粒度 | 来源与分级 |
|---|---|---|---|
| Qlib Alpha158 | 158 个 K 线量价工程因子（KMID/ROC/MA/STD/MIN-MAX 比率族），ML 基准标配 | 日线原版，可平移到任意 bar | [开源] https://github.com/microsoft/qlib ；[开源] https://qlib.readthedocs.io/en/latest/component/data.html ；[博客] https://www.quantlabsnet.com/post/comprehensive-guide-to-microsoft-qlib-the-ai-oriented-quantitative-investment-platform |
| Qlib Alpha360 | 60 日×(OHLCV) 原始归一化特征 360 维，弱特征工程+强模型 | 日线原版；crypto 复现显示 MIN5/MIN10 日内特征信号最强（[博客] medium.com/@gwrx2005） | [开源] 同上 benchmarks README https://github.com/microsoft/qlib/blob/main/examples/benchmarks/README.md |
| WorldQuant 101 Alpha | Kakushadze 101 个显式公式 alpha（rank/ts_corr/ts_delta/delay/decay_linear 算子族），平均持仓 0.6-6.4 天，数据挖掘产物、低相关 | 日线原版；算子天然可平移分钟 bar | [论文] arXiv:1601.00991 https://arxiv.org/pdf/1601.00991 ；[开源] DolphinDB wq101alpha 全 101 因子实现 https://github.com/dolphindb/DolphinDBModules/blob/master/wq101alpha/README_CN.md ；[社区] BigQuant 复现 https://bigquant.com/wiki/doc/Gl3vglHyog ；[社区] 知乎 Alpha101 系列与流批一体实现 zhuanlan.zhihu.com |
| gplearn 遗传规划 | SymbolicTransformer 以 IC/rankIC 为 fitness 进化公式；算子集=ts_rank/ts_corr/delay/protected ops；parsimony 压制公式膨胀；中文社区标配（华泰 GP 系列研报为源头） | 基础特征任意粒度 | [开源] https://gplearn.readthedocs.io ；[社区] CSDN《利用遗传算法进行高频因子挖掘》（gplearn+DEAP）blog.csdn.net ；[社区] 华泰《基于遗传规划的选股因子挖掘》系列（模型知识标注，原文未重取） |
| AlphaNet（华泰 AI-32） | 类 CNN 特征提取层+自定义算子（cs_rank 等），端到端"因子挖掘+合成"一体化；续作《再探 AlphaNet》（2020）；2025 续作=大模型+强化学习（MaskablePPO，环境 AlphaPool）生成因子表达式 | 输入量价矩阵（原版日线，可分钟化） | [社区/论文] 华泰人工智能系列三十二（Scribd 可见）；[开源] jeremy-feng/AlphaNet https://github.com/jeremy-feng/AlphaNet ；[博客] fengchao.pro AlphaNet-V1 详解；[社区] 知乎《AlphaNet 因子挖掘网络——运算符嵌套和卷积神经网络》 |
| boosting 截面模型 | LightGBM 为 qlib 官方基准（LGBModel vs GRU/Transformer on Alpha158）；近年混合 LSTM+GBDT（arXiv 2025-05）、regime-aware LightGBM（MDPI，63 特征含跨资产） | 日频为主；特征可含日内聚合 | [开源] qlib benchmarks；[论文] arXiv 2009.11189（Qlib 平台）；[论文] dl.acm.org《Stock Return Prediction Using Hybrid ML》2025-04；[博客] joiv.org/scitepress/mdpi 各一篇（检索摘要级） |

## 2. 日内/微结构 alpha（含主流检验粒度）

| 算法 | 要点与**主流检验粒度** | 本仓数据适配 | 来源与分级 |
|---|---|---|---|
| OFI 订单流不平衡 | OFI 与价格变动线性关系、斜率∝1/深度，解释 60-80% 当期价格变动；MLOFI 扩展到多档深度向量；Cont 2023 跨资产 cross-impact。**检验粒度=逐事件/秒级 LOB 事件流，聚合研究常用 1min-5min** | tick_data 有 direction/bid/ask（逐笔成交级）→可做"成交签名 OFI 代理"；**真 OFI/MLOFI 需 LOB 逐档事件流，本仓 tick_depth_5 仅 07-24 起 40 日**（观测级） | [论文] Cont-Kukanov-Stoikov arXiv:1011.6402（JFE 2014）https://arxiv.org ；[论文] MLOFI（Xu 等，Oxford ORA ora.ox.ac.uk）；[论文] Cont《Cross-impact of order flow imbalance in equity markets》2023 tandfonline.com；[博客] emergentmind.com OFI 概览 |
| VPIN 流毒性 | 等成交量桶（非时间 bar！）+BVC/tick rule 买卖分类；flash crash 争议（Andersen-Bondarenko 2014 反证）。**粒度=成交量桶，分钟 bar 可做近似（功效降）** | tick 逐笔 21 个月可做真体积桶版；1min 可做 BVC 近似版 | [论文] Easley-López de Prado-O'Hara《Flow Toxicity and Liquidity in a High-Frequency World》NYU stern.nyu.edu；[论文] Andersen-Bondarenko sciencedirect.com 2014；[开源] yt-feng/VPIN github.com；[博客] questdb.com/paperswithbacktest.com 实现指南 |
| Amihud 日内版/Realized Illiquidity | 经典日频 \|ret\|/成交额 的日内重构：Barardehi-Boguth-Deng《Night and Day of Amihud》拆交易时段 vs 隔夜 price impact；Lou-Polk 高频 price-impact 基准；FAJ《Realized Illiquidity》=realized vol/成交量。**检验粒度=日内高频聚合到日频截面，5-30min bar 足够** | 1min（4.7 年）直接可算；E 盘挂回后可拉 2000-2021 长历史 | [论文] afajof.org Realized Illiquidity 2023；[论文] Barardehi et al. SSRN/Chapman；[论文] Lou-Polk JFE；基线=Amihud 2002（RFS） |
| 隔夜/日内收益分解 | A股隔夜收益系统性为负且与 T+1 规则挂钩；"Opening Low Going High"隔夜→日内反转；异常因子隔夜/日内口径分裂。**粒度=日线分解+开盘段分钟** | 日线+1min 开盘段即可；底仓 T 语义受 T+1 约束 | [论文] ResearchGate《Overnight return puzzle and the T+1 trading rule》；[论文] Wang 2022 SciOpen《Opening Low and Going High》；[论文] Semantic Scholar《Overnight versus intraday returns of anomalies in China》 |
| 日内动量/反转（A 股） | Chu 等 2019：**A 股开盘后半小時收益预测当日剩余收益（动量）+反转结构**；Gao-Han-Li-Zhou JFE 2018 市场日内动量（SPY 前 30min→后 30min）。**检验粒度=1-5min bar 聚合到半小时段** | kline 1min 2021-09 起 4.7 年+指数 tick（8.9 亿行）直接可考；与今晚 auction_gap 日内回吐发现互证 | [论文] Chu et al. 2019 Journal of Empirical Finance sciencedirect.com；[论文] Gao et al. JFE 129(2) 2018 sciencedirect.com/papers.ssrn.com |
| VWAP 偏离 | 偏离 VWAP 均值回归+标准差带择时（FX 起源，社区广泛用于日内执行基准）；与开盘动量可组合为过滤器 | 1min/5min 重构 VWAP；与 T 车道 W3 绿区簇（高波 ETF/个股）衔接 | [博客] thevwap.com/crosstrade VWAP reversion（社区实践级）；学术锚=Elaut et al. 日内动量（模型知识标注，本轮未重取原文） |

## 3. 另类数据 alpha（对照今晚九面板已探结论）

| 方向 | 最新做法 | 今晚仓内对照 | 来源与分级 |
|---|---|---|---|
| 文本/新闻情绪：LLM 打分 vs 词典法 | LLM 头条打分→次日收益（López-Lira & Tang 2023 U Florida，ChatGPT 跑赢均值）；2025-26 续作：LLM 对历史收益外推过度（Chen 2025 AFA）、LLM 新闻情绪管线（arXiv 2026）。共识=LLM 打分在覆盖广度与语义深度上压过词典法，但需控成本与泄漏 | news_sentiment_window 隔夜情绪 intra IC +0.262（n=92 天、单 regime）已证实"做T 语义可用"；**全文/全量 LLM 打分管线待建（research_report 20GB 未搬、今晚车道禁 LLM 调用）**——升格前置=LSG 网关+小样本标定 | [论文] afajof.org Chen 2025；[论文] arXiv 2026 LLM news sentiment；[社区] planadviser.com/hkaift.com López-Lira & Tang 报道 |
| 龙虎榜/资金流 | 聚宽社区：机构席位净买呈 V 字型（两端均有超额）；华尔街见闻 2021：量化私募席位净流入>1 亿→20 日累计超额约 +1.43%（峰值第 14 日 +2.28%）；通用回测=上榜次日开盘买/隔日收盘卖 | 今晚 F3 已探：席位净买 h5 +0.079/h10 +0.054（t 7.0，短漂移衰减）；买方席位拥挤 -0.072 反指；**数据窗 2022-01..2024-02，需核实断供后增量** | [社区] zhuanlan.zhihu.com 三维量化文；[社区] wallstreetcn.com 2021-10-31；[社区] xueqiu.com 短线玩法文；[社区] baike.baidu.com 回测惯例 |
| 舆情热度 | 方正金工《股票舆情热度的反转效应与"热点反应"因子》（2025-03）：情绪剧变时段涨跌幅→热点反转因子，**周频 IC 4.54%/ICIR 6.14/胜率 81%**（研报宣称，未独立复核）；理论锚=Barber-Odean 注意力驱动买入→高关注反转 | 今晚 ALT-B：hot_rankchg f1 +0.093（n=22 天功效低）、hot_value 列全空；**数据积累至 ≥120 日（约 2026-12）后可对表方正构造** | [社区] finance.sina.com.cn 转载方正研报 2025-03-13；[社区] guba.eastmoney.com/xueqiu.com 数据源面；理论=[论文] Barber-Odean attention（模型知识标注） |

## 4. 多重检验与"全粒度全组合矩阵"的行业惯例（Owner 问题证据核）

| 证据 | 结论 | 来源与分级 |
|---|---|---|
| Harvey-Liu-Zhu RFS 2016（313 因子/591 检验） | 因子动物园数据窥探：传统 t>1.96 失效，**新因子 t 需 >3.0**（且门槛随已测数量上行）；"多数发表发现可能是假发现" | [论文] academic.oup.com RFS 29(1)；sites.duke.edu PDF；SSRN |
| Deflated Sharpe（Bailey & López de Prado, JPM 2014） | 对 N 次试验的**期望最大 Sharpe** 做收缩（极值/Euler-Mascheroni 近似）+非正态修正→DSR；试验数 N 必须如实累计（跨轮累计） | [论文] davidhbailey.com 全文；[博客] marti.ai 2018 Python 走读；[论文] LdP《The False Discovery Rate in Finance》SSRN 2026 |
| PBO 回测过拟合概率（Bailey-Borwein-LdP-Zhu 2015） | CSCV 组合对称交叉验证估计"选到的参数组合在 OOS 排名掉半"的概率；网格扫描标配配套 | [论文] papers.ssrn.com 2326253（J. Computational Finance）；[开源] pypbo |
| 复制危机之争（Jensen-Kelly-Pedersen, JF 2023） | 153 因子 82%+ 可复制（用统一管线+更高门槛）——业界主流=**先验假设族+统一协议+高门槛**，非全网格扫描 | [论文] JF 2023（onlinelibrary.wiley.com，检索摘要级） |
| 中文社区口径 | quant67.com《回测陷阱》：数据窥探+Bonferroni/BH-FDR 修正是参数网格标配；知乎《美丽的回测》介绍 PBO 定量过拟合概率——中文社区同样以"控试验数+OOS 纪律"为正解，无"全格挑最好"正统 | [博客/社区] quant67.com；zhuanlan.zhihu.com |
| 与本仓裁定兼容性 | HLZ t>3.0 ↔ 本仓预注册 0.1% 双侧线 \|t\|>3.29；DSR ↔ #304 期望最大 Sharpe 数学与 G3 门 DSR>0.5；BH-FDR q=0.10 ↔ TICKM 协议 §多重检验全格 BH | 本仓真源：tick_matrix_protocol.md / #304 / bizmine_general_order.md §2 |

**小结（裁定书详见 matrix_necessity_verdict.md）**：检索未发现任何学术或业界正统推荐"粒度×数据×信号全组合网格扫描后挑最好"；主流=有限先验假设+预注册/IS-OOS 纪律+多重检验修正（t>3.0 / DSR / BH-FDR / PBO）。"全矩阵"作为探索性**筛**可以，但必须配 N 累计账与 FDR，且**筛≠考**。

## 6. 实现队列 Top3 伪码级设计段（对应 implementation_queue.csv id=1/2/3，供下一班直接施工）

### 6.1 OFI 代理：成交签名买卖不平衡（tick→1/5/15min 聚合）

- 数据：`c1_market.tick_data`（price/volume/direction，个股 2025-01 起 21 个月）。direction 缺失行用 tick rule 兜底（price↑=buy, ↓=sell, 平=延续前值）。
- 真源出处：Cont-Kukanov-Stoikov 2014；本代理用"成交签名不平衡"近似订单簿事件 OFI（LOB 事件流缺失，depth5 仅 40 日）。

```python
# 每 symbol 每交易日：
# 1) 逐笔签名 signed_vol_i = volume_i * (+1 if direction==buy else -1)   # tick rule 兜底
# 2) 聚合到窗 w ∈ {1min, 5min, 15min}：
#    ofi_w(t) = sum_{i in w(t)} signed_vol_i / ADV_daily                 # 成交额占比归一（跨票可比）
#    delta_p_w(t) = (mid_w(t) - mid_w(t-1)) / tick_size_adjusted         # 窗末对窗初中间价变动
# 3) 价格冲击检验（预注册主假设 H1）：
#    per symbol-day: regress delta_p_w on ofi_w → beta_i；横截面 beta_i 与
#    流动性（ADV、日内 Amihud）负相关 = 文献复现检查（Cont: slope ∝ 1/depth）
# 4) 因子化（预注册主假设 H2）：15:00 收盘时点用当日累计 ofi_15min 排序 → 次日开→收 IC；
#    IS=2025-01..2025-12，OOS=2026-01..2026-09；桶=vol_pct T-1 三桶（0.3200/0.7040）
# 功效预期：21 个月≈370 交易日/股；分 3 桶后每桶≈120 日踩功效门（verdict §3.6）
# 禁：日内频仓翻转判读只到 T+1 开盘 PIT 口径；未复权暂定条款照写
```

### 6.2 A 股市场日内动量：开盘半小时→尾盘（1min 聚合）

- 数据：`kline_1min`（2021-09 起 4.7 年）+ 指数/板块 tick（可选交叉验证）。出处：Gao et al. JFE 2018；Chu et al. 2019（A 股直接证据，含反转分支）。

```python
# 每 symbol 每交易日（主口径=市场聚合，副口径=个股截面）：
# r_0930_1000(t) = (P_1000 - P_0930) / P_0930        # 开盘半小时收益
# r_1430_1500(t) = (P_1500 - P_1430) / P_1430        # 尾盘半小时收益（可交易段=14:30 后）
# H1（市场版）：以全市场等权/市值加权 r_0930_1000 的时序分位排序 →
#    预测当日 r_1430_1500：符号检验 + Spearman，IS=2021-09..2024-12，OOS=2025-01..2026-09
# H2（个股版）：个股 r_0930_1000 截面五分位 → 当日剩余段收益
#    Chu 2019 预期=高分组动量延续+极端档反转（凹型）；预注册时把"动量/反转分段点"
#    在 IS 期钉死（如 r_first 分位 0.8 以上=反转段），禁 OOS 挑段
# 判读门：|t|>3.29（0.1% 双侧）+ OOS 同号 + 全格 BH q=0.10（若与 6.1/6.3 同波考试）
# 与既有资产关系：与 auction_gap 当日回吐（ALT-B）互证；不做 ETF 做T 判定（归 T 协议）
```

### 6.3 VWAP 偏离回归：条件化做 T 窄测（衔接 W3 绿区簇）

- 数据：`kline_1min`/`kline_etf_1min` 重构滚动 VWAP；标的=W3 预注册绿区簇（588200/513330/300561 等，宇宙规则已 frozen 勿改）。出处：社区实践（thevwap.com）+日内动量过滤组合。

```python
# 每 symbol 每交易日（仅 W3 绿区标的；T+1 底仓语义，禁止裸日内回转假设）：
# vwap(t) = cumsum(p_i * v_i) / cumsum(v_i)           # 当日累计，p=1min close
# dev(t) = (p(t) - vwap(t)) / vwap(t)
# sigma_dev = IS 期 dev 的滚动 σ（窗 20 日，参数 IS 钉死）
# 入场（多头腿）：dev < -k * sigma_dev（k 在 IS 期网格 {1.0,1.5,2.0} 预注册，OOS 禁调）
# 出场：dev 回穿 0 或 15:00 强平；过滤：开盘半小时动量（6.2 信号）同号才开仓
# 成本：双口径（五分位按标的 ADV 分档 Q1-Q5 + Owner-001 1.5bp 档）+ 佣金万0.854
#       + 卖出印花税万5（个股）+ ¥5 地板；T+1：当日买入腿不可卖，回测按底仓 T 记账
# 判定：req_cap 门沿用 W3 脱红/绿区带（≤0.50 脱红 / ≤0.25 绿区）；regime 灰度桶
#       （vol_pct T-1 三桶）条件化披露；多重检验位置=3 标的×3 参数×3 桶，写进卡
# 与 #304 关系：产出=新单假设预注册卡草案（走 Owner 快签），本设计不做全矩阵
```

## 7. 检索方法与诚实条款

- 工具=WebSearch（后端偶发 429 限流，已换关键词/中英文重试）；共发起 13 组查询、命中 11 组（2 组超时/限流后由相邻查询覆盖）。
- 未重取原文全文的条目已标注"检索摘要级"或"模型知识标注"；研报宣称数值（方正 IC 4.54%、华泰 GP 系列）未经独立复核，引用时注明"研报宣称"。
- 中文源覆盖：知乎（4 处）/雪球（2 处）/集思录（0 命中，如实登记）/CSDN/DolphinDB/BigQuant/华尔街见闻/新浪财经。
- 本车道零查库零回测；仓内数据可得性均引自今晚已落盘文档（tick_inventory_total.md、altdata_probe_report.md、altdata_b_report.md、bizmine_general_order.md）。
