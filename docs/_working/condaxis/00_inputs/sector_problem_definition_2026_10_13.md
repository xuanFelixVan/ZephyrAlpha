---
ttl: task_bound
title: 板块模块问题定义与全网调研记录
created: '2026-10-13'
session: st-sectordef-20261013
family_id: SECTOR-CAMPAIGN
status: draft_for_discussion
completes_when: §6 七问经条件轴总包 P1 统一呈批包呈 Owner 裁决且板块验证班三裁收口后，随 CONDAXIS-CAMPAIGN 战役归档
---

# 板块模块问题定义与全网调研记录（st-sectordef-20261013）

> **令据**：Owner 2026-10-13 口令（记录于本会话）：①先全网查清机构/量化社区/学术论文/最新算法/GitHub 的板块做法；②先定义"板块模块到底出什么产物、能指导做什么"，再倒推需要哪些数据；③全部沉淀于本文档。
> **纪律**：本稿为讨论稿，零裁定、零开考、零 CH；引用式冻结优先（指真源不抄数值）；仓内红线（热度传导 IC=-0.029 禁用、D109 先产特征不联动仓位）全文遵守。
> **分工**：仓内盘点由只读探查车道完成（2026-10-13）；全网调研由本会话四轮检索完成（arXiv API 两轮 + Web 搜索四轮，GNN 中文社区与龙头实战两检索超时未补）。

---

## §0 一页结论（TL;DR）

1. Owner 之问——"板块能出来什么结果？能指导做什么工作？"——本文给出形式化答案：**五件套输出物**（§1）。
2. "算法发明"需求很低：仓内识别层已建七八成（§4），词汇表与 A 股短线实战高度对齐；外部真正有增量的集中在**数据面（分析师预期修正）**与**验证面（统一 IC 普查）**两处（§3.6、§6）。
3. 最优先动作：五件套定义过审后，开**板块信号验证班**（判据预冻结→对在册 20+ 板块模块统一打靶）→ 按内收原则退役零增量模块 → 再谈执行接线与数据补采。

---

## §1 问题定义：板块模块到底是干什么的

### 1.1 Owner 提问的形式化（与状态识别类比）

- 状态识别 = {当下状态, 拐点信号}——两个明确产物。
- 板块模块应有同构的明确产物集：它回答的不是"预测涨跌"，而是**把四个交易问题变成机器可考的输出**：现在钱在哪些板块（WHICH）、各处于什么阶段（WHEN-IN）、什么时候进什么时候出（WHEN-TURN）、板块确认后买卖什么个股（WHAT）、当前环境允不允许做（WHETHER）。

### 1.2 五件套输出物（板块模块的存在意义）

| # | 输出物 | 回答的问题 | 形态 | 消费方 | 指导动作 |
|---|---|---|---|---|---|
| ① | **主线名单与梯队** | 现在钱在哪 | 主线 Top-N（1-3）+ 次线/潜线/补涨梯队标签 + 灰度合分 | 考试条件轴"板块域"字段；盘后主线简报 | 仓位在板块间怎么分 |
| ② | **板块状态/阶段** | 它处于什么阶段 | 生命周期五态（点火/主升/分歧/退潮/调整）+ 各态灰度 | 考试卡条件；卖出决策（接线后） | 启动=试仓、主升=持有、分歧=减、退潮=清 |
| ③ | **拐点信号集** | 什么时候进出 | 入场确认信号集（分歧转一致/梯队成型/龙头确立/资金持续净流入）＋出场预警信号集（拥挤极值/炸板率/虹吸触发/催化证伪），**每个信号独立可考** | 交易信号面 | 入场/出场时点 |
| ④ | **传导标的集** | 板块确认后买什么 | 板块→个股映射 + 传导强度排序（链上位置 × 传导时滞 × 龙头分档） | 个股选信号域 | 个股候选池 |
| ⑤ | **环境闸门读数** | 现在能不能做 | 大盘两态 × 情绪水温 → 板块操作允许矩阵 | 以上全部输出的前置门 | 环境不允许=全信号降档 |

### 1.3 明确边界（板块模块不是什么）

1. **不是热度榜**：朴素"板块热度→涨幅"外推已被本仓实测证伪（月 IC=-0.029，Owner 红线留档）——只做事件命中定位、不做热度预测是现行法。
2. **不是个股推荐器**：④只产出"板块确认后的传导候选"，个股级考试属于个股信号域。
3. **不是涨跌预测器**：事件方向语义（涨价/断供反号）建成之前，传导管线只定位不判向（仓内已立红线）。

### 1.4 与大盘两态班（st-formreg-20261013）的会合

⑤ 直接消费两态班输出。两班产品在考试条件轴上会合：**大盘态（单边↑/单边↓/横向）× 板块态（生命周期）× 个股传导（④）＝考试条件轴三段结构**。两态班解决"什么时候信信号"，本模块解决"信哪个板块的什么信号"。

---

## §2 倒推：五件套 × 数据/能力需求矩阵

| 输出物 | 所需数据/能力 | 仓内现状 |
|---|---|---|
| ① 名单 | 板块指数行情、宽度、成交占比、动量 | ✅ 齐（880 快照/582 板块盘中聚合/86 板块因子/sector_momentum、rrg、breadth） |
| ② 状态 | 涨停梯队、板块日度资金流、情绪水温 | ✅ 基本齐（limit_up_pool/fflow 日度/sentiment_cycle） |
| ③ 拐点 | 盘中资金流、炸板率、北向、催化剂方向 | ⚠️ 缺口：**板块分钟级资金流数据源不存在**（仓内实测留痕）；北向仅季度快照（2024-08 日频停发）；事件方向语义未建 |
| ④ 传导 | 产业链图谱、研报语料、财报、**分析师预期修正** | 链图谱 ✅（ig_* 十三表）＋语料 ✅（76,112 块）；**一致预期/修正宽度数据面空白** |
| ⑤ 闸门 | 大盘两态输出 | 由 st-formreg 班产出（对接点） |

**数据倒推结论**：①②⑤数据面齐；③④各有一个硬缺口（分钟级资金流、预期修正），是否补采属 Owner 门位（§6）。

---

## §3 全网调研

### 3.1 学术界

**经典理论根基（两篇 JOF）**
- **Moskowitz & Grinblatt (JOF 1999) "Do Industries Explain Momentum?"**：行业成分动量强且普遍，控制行业动量后个股动量大幅消退——"板块优先于个股"的理论根基，直接背书 Owner"板块最重要"的直觉。
- **Cohen & Frazzini (JOF 2008) "Economic Links and Predictable Returns"**：客户-供应商链接间收益可预测（links 组合月 alpha 约 1.5%），机理=有限注意，信息沿供应链缓慢扩散——仓内产业链传导链的理论对应物（后续 Cohen & Lou 2012 集团公司延续）。

**最新 arXiv（2020→2026 精选，按相关性）**
- **arXiv:2512.08000** Hawkes 过程分析中国股市传染：**高交易活跃期板块趋势持续，低活跃期呈现强烈板块轮动**——仓内"水温档放行"（sector_gate）设计的直接实证支持。
- **arXiv:2004.08759** 迁移熵构建中国 28 行业信息流网络：非银金融为信息源，市场随时间板块轮动——传导方向问题的实证方法学对应。
- **arXiv:2304.09947** 免梯度在线集成轮动：16 个异构模型自适应加权，证明**板块收益比个股更可预测**，带理论遗憾界——①合分排序器的候选算法。
- **arXiv:2108.02838** 两阶段法：宏观指标（CPI/GDP）→行业 ETF 价格预测→排序选前四；Echo State Network 表现最佳。
- **arXiv:2401.00001** 因子模型+基本面（PE/PB/EV/EBITDA/股息率+动量+短期反转）板块轮动框架。
- **arXiv:2506.04488** LARX 潜变量回归（监督扩散），重检美股-实体经济关系并揭示板块轮动的预测能力。
- **arXiv:2607.19005** 距离矩阵谱分析：危机期"coherent sector rotation"可识别驱动板块与顺序。
- **arXiv:2603.13252** "When Alpha Breaks"：2024 年 AI 主题行情与板块轮动导致横截面信号长周期失效——验证纪律的警示案例（信号会因风格切换整体失效，需两级不确定性部署）。
- **arXiv:2506.20930** 量子强化学习台股板块轮动：量子模型训练奖励高但实际收益/夏普不及经典 PPO——噱头路线不占优的对照证据。

**GNN 关系图族（8 篇精选）**
- 2512.08567 GraphSAGE 异构图（文章-公司-行业）+新闻嵌入；2412.06862 层级 GNN 行业关系图；2411.18997 GRU-PFG 因子图（CSI300 IC 超 HIST）；2409.08282 二级行业长期关系矩阵；2408.02899 SETN 文本+网络嵌入（主题基金）；2401.01846 DGDNN 熵驱动动态图；2309.06559 社交情绪+相关股票图；1909.10660 日经供应商知识图谱滚动窗口 GNN（20 年回测显著超基准）。
- **判定**：文献活跃，但公开可复现的 A 股板块级落地少。定位＝**④传导标的集的特征来源**（ML 升级方向），不是独立圣杯，不作为模型依赖。

**LLM/NLP 族**
- **arXiv:2603.22305 CN-Buzz2Portfolio**：中文市场基准，LLM 把每日热点财经新闻映射为宏观+行业板块资产配置，"压缩-感知-配置"三阶段 Agent 工作流——与仓内 news→板块管线（W3/W5）升级方向最直接对口。
- **arXiv:2608.14014 Buy the Rumor, Sell the News**：LLM 蒸馏分类器给 457 万条新闻打 17 类事件标签；发现**市场对"数字类"新闻反应不足、对"故事类"新闻过度反应**——对事件方向语义（§6-5）与出场信号（过度反应=退潮前兆）双重可用。
- **arXiv:2606.12210** 零样本 NLI 从新闻提取短期信号**无法超越简单基线**——零样本 LLM 直接读市不可行，须蒸馏任务专用分类器（方法论红线）。
- 2509.12611 AD-FCoT 类比思维链（纯提示工程）；2505.19430 FIN-FORCE 前向反事实基准；2403.12285 FinLlama（Llama2 LoRA 金融情感）。

### 3.2 A 股卖方金工（研报系）

- **华泰金工《量化行业轮动的"崎岖之路"》（2026-03）**：复盘基本面/交易面/机器学习三维度，明确**传统基本面因子因行业逻辑漂移而失效**——单靠财报慢变量做轮动不够。
- **招商证券"预期共振"**：分析师预期修正共振做月度行业推荐系列。
- **国盛证券**：人民币资产风险溢价构建 A 股-美股跨市场轮动。
- **高切低指数**（量化社区通用）：各二级行业累计收益方差作板块切换计时器，高位方差放大≈资金从高位板块切向低位——与仓内 `sector_siphon`（虹吸态）同现象异命名。
- **《周频多因子行业轮动模型》（2024-01）**：分析师一致预期净利润三个月环比等预期因子构造。
- **富国基金 ETF 轮动因子（2025-01）**：卖方分析师预期调整反映行业景气度。
- 开源证券"聪明钱"/KyFactor 特色因子系列（魏建榕团队）；东北证券《基于资金流向的行业轮动》；A 股价量因子行业轮动（2023）。

### 3.3 买方/数据商实践

- **FactSet 复合模型**：盈利预测 + **修正宽度（revision breadth）** + 价格动量合成；**盈利修正=基本面动量，1-6 个月有效**（Interactive Brokers 综述同口径）——买方板块选股第一大输入，仓内空白。
- **Fidelity 业务周期轮动**：复苏→过热→滞胀→衰退四相位转板块——"大盘状态 × 板块"环境闸门的机构版。
- **Quantpedia Sector Momentum Rotational System**：板块动量轮动扣费后仍盈利的系统化验证。

### 3.4 量化社区与 GitHub 开源

- **hugo2046/QuantsPlaybook**：100+ 券商金工研报复现（光大/华泰/招商/国信），轮动类策略代码迁移底座。
- **garroshub/Quant_Sector_Rotation_Strategy**：ETF 动量+波动率轮动 + LLM 策略分析集成。
- GitHub topics：`a-shares`（A 股 ETF 轮动研究回测平台：walk-forward/向量化/事件驱动）、`china-stocks`（87 端点 34 数据源 A 股全栈数据包：K线/逐笔/研报/资金面/舆情）、`multi-factor-model`；`leoncuhk/awesome-quant-ai` 资源清单。
- 聚宽/掘金（BigQuant）社区另有大量开源轮动策略代码可迁移。

### 3.5 A 股短线实战社区（游资/龙头战法）

情绪周期（冰点→启动→主升→分歧→退潮）、龙头战法、连板梯队与高度断层、**分歧转一致**入场、**一致转分歧/炸板率/虹吸**出场。这套词汇仓内已全部模块化（§4.3），是仓内与本土实战对齐度最高的部分。

### 3.6 调研结论：对仓内真正有增量的东西（排序）

1. **分析师预期修正数据面**（一致预期+修正宽度）——买方第一大输入、卖方"预期共振"核心，仓内空白；补采=花钱门位。
2. **LLM 事件分类+方向语义**（2608.14014 方法论：蒸馏任务专用、拒绝零样本）——传导反号与出场信号③"催化证伪"的前提。
3. **Hawkes/迁移熵估计链上传导时滞**（2512.08000 / 2004.08759）——升级现 BFS 等权衰减假设的实证方法。
4. **免梯度在线集成排序器**（2304.09947）——①合分的理论保底候选（多信号自适应加权+遗憾界）。
5. GNN 关系图——④的特征来源（谨慎、最后）。

---

## §4 仓内资产盘点（探查车道 2026-10-13）

### 4.1 产业链本体（PG `ig_*` 十三表，production/evolving）

- 真源：`scripts/industry_graph/apply_industry_graph_ddl.py`（PostgreSQL depgraph 图谱域）。表含 ig_chain（链+level）、ig_node（环节，11 节点已挂子链）、ig_edge（structure|supply）、ig_node_company（环节↔股票 PIT 三时间戳）、ig_company_edge、ig_fact（五元组事实）、ig_chunk（**E 盘语料 76,112 块**）、ig_io_edge（**国家统计局 2020 年 153 部门投入产出系数**）等。
- 规模：CKG2021 导入 4,654 上市公司 / 511 申万行业 / 95,559 产品 / 110,153 产品-产品边；chainmap 前端约 61 条链、47~48 簇（C01~C48）。
- 维护族：`scripts/industry_graph/`（import_ckg_dataset、ths_import、websearch_ingest、io_ingest、p0~p3 语料抽取、merge_semiconductor_chains、normalize_global_edges、quality_*）；提交门 `industry_chain_map_gate.py`。

### 4.2 信号侧传导管线（W1-W6 已落码，未完全结案）

- `signal_ashare/industry_chain_graph.py`（MOD-SIG-125，production/evolving）：SQLite 轻量图，节点=company|segment，边=supply|material|demand|byproduct（权重 (0,1]），N 跳 BFS 乘积衰减。**与 PG ig_* 大图互不联通（双真源，§6-4）**。
- 新闻→链→标的：`news_chain_node_linker`（W3，规则法 MVP）→ `chain_impact_resolver`（W4，BFS N 跳衰减；**涨价/断供语义反号未做**）→ `chain_impact_stream`（W5，盘中事件冲击流+只读端点 `GET /api/chain-impact-stream`，api_server.py:4793）。
- 辅助：`policy_theme_mapper`（政策主题→申万受益/受损，design）、`concept_factor_mapper`（股票↔概念逆向索引，design）——**两者均未投产**。
- **红线**：热度传导预测已证伪（月 IC=-0.029 留档），只做事件命中定位不做涨跌预测。

### 4.3 板块信号族（`signal_ashare/sector/`，20+ 模块，成熟度断层）

- production：`sector_analyzer`（板块情绪结构：涨停比/连板梯队/趋势，TDM-E-L2-01-1 与 02-2 双挂）、`sector_crowding_launch`（拥挤度启动，evolving）。
- testing：`sector_divergence`（轮动序列）、`sector_leader`（龙头识别四档 leader/backbone/follower）、`sector_momentum_persistence`（生命周期）、`sector_state_aggregator`、`sector_volume_anomaly`、`sector_attribute_rules`。
- design：`sector_strength_aggregator`（强度四路合分 [0,100]，前 15% 入候选池，TDM-E-L2-01）、`sector_ecology_judge`（板块级市场状态）、`sector_conduction`（板块→个股强度加权传导）。
- new：`sector_momentum`（多周期动量）、`sector_breadth`（资金流聚合）、`sector_rrg`（RRG 轮动 JdK DualEma+象限确认）、`sector_rotation_state`（轮动五分类）、`sector_siphon`（虹吸态）、`sector_adjustment`（调整周期进度）、`sector_pullback`（回踩 ABC 质量）、`sector_gate`（三级放行/水温响应）。
- 上层：`mainline_candidates`（MOD-SIG-061 主线候选 Top3-5）、`mainline_probability`（MOD-SIG-064 四因子主线概率，权重"初拍待实盘标定"）；`strength_ic_data_assembler`/`strength_ic_weight_calibrator`（短线强度 IC 校准——**仓内已有 IC 校准先例**）。

### 4.4 数据/事件/执行面

- 资金流：板块**日度**资金流（东财 fflow，`sector_fund_flow_collector`，testing）；**板块分钟级资金流数据源不存在（实测留痕）**；北向**季度**快照（`northbound_hold_analysis`，production；日频 2024-08 停发）；个股 money_flow（c1_market）；`capital_flow_pattern_analyzer`（五类资金线形态，production/stable）。
- 板块数据底座：`sector_state_pipeline`（kline_sector_880+涨停池+money_flow→c1_market.sector_state，T 日 15:10 收口，testing）、`sector_snapshot_collector`（880 实时→CH，production）、`sector_intraday_aggregator`（582 板块盘中聚合，production）、`sector_factor_manager`（86 板块因子，testing）、`sector_report_builder`（盘后全景报告，production）。
- 涨停/情绪/执行：`limit_up/` 族（连板梯队+封板时间+断层+Granger 领导-跟随）、`youzi_relay_emotion_engine`（production/stable）、打板执行域 `ex_core/daban_*`（连板梯队×情绪周期前置门控+7 类动作，production/stable）、`sentiment/sentiment_cycle`（水温档真源，new）、`emotion_index_builder`（experimental，板块热度不回灌防循环）。
- 事件因果：`intelligence/event_chain_causal_graph.py`（MOD-INT-EVENT-CHAIN，production/evolving）——事件节点词表+Granger 因果边+贝叶斯条件概率表；与 D-ALT-22 规则传导模板、causal_inference_engine 分工明确。
- TDM：`config/trading_decision_map.yaml` 的 **TDM-E-L2 板块选择子树约 28 节点全部挂 module_ref**（L2-01 强度综合 … L2-09 催化剂[已挂 news_chain_node_linker/chain_impact_resolver]、L2-10 同源补涨比价 supply_chain_momentum）。

### 4.5 综合判定

数据底座厚（L1 行情层自评约 95%），识别层模块面全但成熟度低——**缺的不是"怎么识别板块"，而是①验证（哪个信号真的有 IC）②执行闭环（板块→个股→订单自动接线，`sell_decision/` 目前零板块引用）③两个数据硬缺口④链图谱双真源⑤事件方向语义**。

---

## §5 算法映射：五件套 ← 外部方法 × 仓内现状 × 建议动作

| 输出物 | 仓内载体（状态） | 外部对应方法 | 建议动作 |
|---|---|---|---|
| ① 名单梯队 | sector_strength_aggregator（design）+ mainline_probability（testing） | 行业动量经典口径（Moskowitz-Grinblatt）；免梯度在线集成（2304.09947） | 验证班先打靶；合分排序器不成再换在线集成 |
| ② 状态阶段 | sector_rotation_state / momentum_persistence（testing） | Hawkes 活跃度分态结论（2512.08000）；RRG 象限 | 验证时把"活跃度档"加为②的输入特征 |
| ③ 拐点信号 | crowding_launch（production）、pullback ABC、梯队断层、sentiment_cycle | 高切低计时器；分歧转一致口径（社区）；"数字/故事反应不对称"（2608.14014） | 入场/出场信号逐个立卡独立考，禁打包 |
| ④ 传导标的 | industry_chain_graph + chain_impact_resolver（testing） | Cohen-Frazzini 链上动量；迁移熵时滞估计；GNN 特征；CN-Buzz2Portfolio 新闻→板块 LLM 路线 | 先补方向语义→再试时滞估计→GNN 最后 |
| ⑤ 环境闸门 | sector_gate 水温响应（new） | Fidelity 周期轮动（机构版）；Hawkes 高/低活跃期结论 | 直接消费大盘两态班输出，闸门矩阵进 P2 预冻结 |

---

## §6 缺口清单与开放问题（呈 Owner 裁决）

| # | 问题 | 现状与选项 |
|---|---|---|
| 6.1 | **板块口径**：通达信 880 / 申万 / 概念多套并存（880 快照、582 盘中聚合、86 板块因子数字互不一致，需澄清） | 需路由规则与唯一主口径，避免复刻 D 族稿 §3.3 那种"两宏观轴 21% 分歧"事故 |
| 6.2 | **分析师预期数据源采购**（一致预期+修正宽度） | 仓内空白；花钱=Owner 门位。候选：Choice/朝阳永续/恒生聚源/tushare；对应外部方法：招商"预期共振"、FactSet 修正宽度、周频多因子轮动 |
| 6.3 | **板块分钟级资金流不存在**（仓内实测留痕） | 选项：外购分钟数据 / 日度聚合代理 / ③出场的盘中腿降级 |
| 6.4 | **链图谱双真源**（SQLite 小图 vs PG ig_* 大图） | 收敛方向待裁：并入大图 or 小图 API 化只读 |
| 6.5 | **事件方向语义**（涨价/断供反号，W4 遗留） | 规则词表 vs LLM 蒸馏分类（2608.14014 方法论：任务专用蒸馏、拒绝零样本——2606.12210 证明零样本不可行）；前置=新闻源面拍板 |
| 6.6 | **验证班开班** | 判据预冻结清单草案见附录 A；与大盘两态班同纪律 |
| 6.7 | **执行接线时机** | 验证闭环之后才接 sell_decision 读板块态（不给未验证信号接扳机） |

---

## 附录 A：板块信号验证班开班要素（草案，未开考，等五件套过审后呈批）

- **P0 普查对象**：`signal_ashare/sector/` 全模块 + `mainline_candidates`/`mainline_probability` + limit_up 梯队族可考信号；逐件登记"能复用什么/缺什么"。
- **P1 判据预冻结（看数前）**：样本期与 PIT 规则（沿 sixphase-v1 先例：PIT_TAIL_LAG/CLOSED_BOOK_CUTOFF/warmup/重放幂等）；前瞻窗口（建议 20 日远期收益 rank IC + 60 日确认双口径）；**多重比较校正**（信号池规模→通过门槛关系先冻结）；验收线按板块拐点样本量现实（百级）定置信区间。
- **P2 产出**：逐模块 IC/命中率/衰减曲线 → 三裁（保持现状 / 降级为特征 / 退役）。
- **纪律**：判据零自拟、预冻结后才跑数、D109 先产特征不联动仓位、热度传导红线不复辟。

## 附录 B：来源清单

**学术（arXiv ID 见文内）**：2512.08000（Hawkes 中国传染）、2004.08759（迁移熵信息流）、2304.09947（在线集成轮动）、2108.02838（两阶段宏→行业）、2401.00001（因子+基本面轮动）、2506.04488（LARX）、2607.19005（矩阵谱分析）、2603.13252（When Alpha Breaks）、2506.20930（量子 RL 对照）、GNN 族 8 篇（2512.08567/2412.06862/2411.18997/2409.08282/2408.02899/2401.01846/2309.06559/1909.10660）、LLM 族（2603.22305 CN-Buzz2Portfolio、2608.14014 新闻定价、2606.12210 零样本极限、2509.12611 AD-FCoT、2505.19430 FIN-FORCE、2403.12285 FinLlama、2608.19526）。
**经典**：Moskowitz & Grinblatt, "Do Industries Explain Momentum?", JOF 1999（[JSTOR](https://www.jstor.org)）；Cohen & Frazzini, "Economic Links and Predictable Returns", JOF 2008（[SSRN](https://papers.ssrn.com)）。
**卖方/买方**：[华泰金工行业轮动崎岖之路](https://finance.sina.com.cn/wm/2026-03-27/doc-inhskrvx9631921.shtml)、[国盛 A股-美股轮动](https://www.fxbaogao.com/detail/3839319)、[周频多因子行业轮动（分析师预期因子）](https://file.iyanbao.com/pdf)、[富国 ETF 轮动因子](https://pdf.dfcfw.com/pdf/H301_AP202303241584531377_1.pdf)、[FactSet 盈利预测复合模型](https://go.factset.com)、[IB 盈利修正综述](https://www.interactivebrokers.com)、[Fidelity Sector Rotation](https://www.fidelity.com)、[Quantpedia 板块动量](https://quantpedia.com/strategies/sector-momentum-rotational-system)。
**GitHub**：[hugo2046/QuantsPlaybook](https://github.com/hugo2046/QuantsPlaybook)、[garroshub/Quant_Sector_Rotation_Strategy](https://github.com/garroshub/Quant_Sector_Rotation_Strategy)、[topics/a-shares](https://github.com/topics/a-shares)、[topics/china-stocks](https://github.com/topics/china-stocks)、[leoncuhk/awesome-quant-ai](https://github.com/leoncuhk/awesome-quant-ai)。
**仓内真源锚**：`scripts/industry_graph/apply_industry_graph_ddl.py`、`src/zephyr/signal_ashare/sector/`、`src/zephyr/intelligence/{news_chain_node_linker,chain_impact_resolver,chain_impact_stream,event_chain_causal_graph}.py`、`config/trading_decision_map.yaml`（TDM-E-L2）、`docs/_working/2026-09-09-news-industry-wiring-directive.md`。

---

*本稿为讨论稿。下一步等 Owner 对 §1.2 五件套与 §6 七项的裁决；五件套过审后按附录 A 起草验证班开班令。*
