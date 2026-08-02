---
ttl: permanent
doc_type: architecture_view
status: active
version: "1.0.0"
date: 2026-08-03
---

# 作战地图·选股阶段

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/_zoomable_html/battle_map_01_stock_selection.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

> battle_map §stock_selection 阶段，21 环节。
> 本文档由 `generate_battle_map_diagram.py` 自动生成，禁止手编。

## 文档基本信息 / Document Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 阶段 | 选股（stock_selection） | Stage | 选股 |
| 环节数 | 21 | Steps | 21 |
| 流转边 | 14 | Edges | 14 |
| 状态分布 | 🟨 候选态（候选池）=16 ｜ 🟦 运营态（已建）=3 ｜ 🟧 设计态（待施工）=2 | State Distribution | 🟨 候选态（候选池）=16 ｜ 🟦 运营态（已建）=3 ｜ 🟧 设计态（待施工）=2 |

> **图例说明 / Legend**：
> - 🟦 **蓝色实线 = 运营态环节**（production，锚点模块已建）
> - 🟧 **橙色虚线 = 设计态环节**（design，锚点模块待施工）
> - 🟥 **红色 = 弃用态**（deprecated）
> - ⬜ **灰色 = 缺失态**（missing，环节无锚点，BM-INV-001 违例）
> - 🟨 **黄色虚线 = 候选态**（candidate，承载模块在候选池）
> - **实线箭头 ``-->`` = 运营态流转**（两端均 production）
> - **虚线箭头 ``-.->`` = 非运营态流转**（含设计/候选/混合）

## 阶段图 / Stage Diagram

> 展示 选股 阶段全部 21 个环节及流转边，颜色区分五态。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'clusterBkg': 'transparent', 'clusterBorder': 'transparent', 'fontSize': '14px'}}}%%
%% 选股阶段图
flowchart TD
    BM_SEL_01["【BM-SEL-01 数据接入与预处理】<br/>把外面来的行情、新闻、另类数据收进来洗干净，按热<br/>度分层存好，供后面所有环节使用。<br/>作战环节 / battle-step<br/>(生产态 / production)<br/>🟡候选承载<br/>【Data Ingestion &amp; Preprocessing】"]
    BM_SEL_02["【BM-SEL-02 因子计算与信号生成】<br/>把洗干净的行情算成各种因子，再用因子工厂管起来，<br/>盘前算全量、盘中补增量。<br/>作战环节 / battle-step<br/>(生产态 / production)<br/>🟡候选承载<br/>【Factor Compute &amp; Signal Gen】"]
    BM_SEL_03["【BM-SEL-03 市场状态感知】<br/>判断现在市场是什么脾气——趋势/波动<br/>/量能三维打分，再叠加体制转换检测。<br/>作战环节 / battle-step<br/>(设计态 / design)<br/>🟡候选承载<br/>【Market State Sensing】"]
    BM_SEL_04["【BM-SEL-04 次日8态走势预测】<br/>预测明天大盘和个股会走成哪种样子，8<br/>种走势各占多少概率——A股T+1制度下这是核心决策依据<br/>。<br/>作战环节 / battle-step<br/>(设计态 / design)<br/>🟡候选承载<br/>【Next-Day 8-State Forecast】"]
    BM_SEL_05["【BM-SEL-05 主力行为感知】<br/>识别庄家和主力资金在干什么——吸筹、洗盘、拉升还是<br/>出货弃庄，给选股和做T提供主力视角。<br/>作战环节 / battle-step<br/>(候选态 / candidate)<br/>🟡候选承载<br/>【Main-Force Behavior Sensing】"]
    BM_SEL_06["【BM-SEL-06 跨市场传导感知】<br/>美股、港股、汇率、商品一异动，立刻算出对A股的传<br/>导系数和影响幅度。<br/>作战环节 / battle-step<br/>(候选态 / candidate)<br/>🟡候选承载<br/>【Cross-Market Conduction Sensing】"]
    BM_SEL_07["【BM-SEL-07 体制转换检测】<br/>盯着市场脾气会不会变——趋势转震荡、牛转熊的切换点<br/>提前预警。<br/>作战环节 / battle-step<br/>(候选态 / candidate)<br/>🟡候选承载<br/>【Regime Change Detection】"]
    BM_SEL_08["【BM-SEL-08 板块轮动序列追踪】<br/>追踪板块强弱的轮动顺序，给回踩质量打A/B<br/>/C级，决定买入优先级。<br/>作战环节 / battle-step<br/>(候选态 / candidate)<br/>🟡候选承载<br/>【Sector Rotation Sequence Tracking】"]
    BM_SEL_09["【BM-SEL-09 调整周期追踪】<br/>追踪板块调整走到哪了——进度≥80%才允许分批低吸，初<br/>期&lt;40%直接拦截。<br/>作战环节 / battle-step<br/>(候选态 / candidate)<br/>🟡候选承载<br/>【Adjustment Cycle Tracking】"]
    BM_SEL_10["【BM-SEL-10 行情生命周期阶段】<br/>判断行情在春夏秋冬哪一季——冬季禁止抄底，秋季突破<br/>失败更倾向强制离场。<br/>作战环节 / battle-step<br/>(候选态 / candidate)<br/>🟡候选承载<br/>【Market Lifecycle Phase】"]
    BM_SEL_11["【BM-SEL-11 知识图谱与因果推演】<br/>把事件、公司、行业的关联织成图谱，事件一来就推演<br/>传导路径，并区分关联因子和因果因子。<br/>作战环节 / battle-step<br/>(候选态 / candidate)<br/>🟡候选承载<br/>【Knowledge Graph &amp; Causal Inference】"]
    BM_SEL_12["【BM-SEL-12 分布特征工程】<br/>给因子加料——滞后项、交互项、滚动统计量、签名方法<br/>，专门喂给密度预测模型。<br/>作战环节 / battle-step<br/>(候选态 / candidate)<br/>🟡候选承载<br/>【Distribution Feature Engineering】"]
    BM_SEL_13["【BM-SEL-13 收益率条件密度预测】<br/>不只预测明天涨多少，而是预测明天收益率的完整概率<br/>分布——偏多少、尾巴多厚、极端情况多罕见。<br/>作战环节 / battle-step<br/>(候选态 / candidate)<br/>🟡候选承载<br/>【Conditional Density Prediction】"]
    BM_SEL_14["【BM-SEL-14 共形预测】<br/>给预测区间加数学保证——不管分布长什么样，区间覆盖<br/>率有数学证明。<br/>作战环节 / battle-step<br/>(候选态 / candidate)<br/>🟡候选承载<br/>【Conformal Prediction】"]
    BM_SEL_15["【BM-SEL-15 Survival止盈止损时间预测】<br/>预测止盈止损还有多久发生——不是固定N天，而是时间<br/>概率分布。<br/>作战环节 / battle-step<br/>(候选态 / candidate)<br/>🟡候选承载<br/>【Survival Stop-Time Prediction】"]
    BM_SEL_16["【BM-SEL-16 分级指标过滤】<br/>选股漏斗第一层——3秒级把全市场7000只砍到1200只，<br/>涨停跌停停牌ST次新弃庄统统按规则排除。<br/>作战环节 / battle-step<br/>(候选态 / candidate)<br/>🟡候选承载<br/>【Tiered Screening Filter】"]
    BM_SEL_17["【BM-SEL-17 初筛漏斗】<br/>漏斗第二层——60秒级从1200只筛到300只，看技术形态<br/>、量价配合、板块强度、主力阶段、市场状态适配。<br/>作战环节 / battle-step<br/>(候选态 / candidate)<br/>🟡候选承载<br/>【Coarse Screening Funnel】"]
    BM_SEL_18["【BM-SEL-18 精筛评分】<br/>漏斗第三层——60秒级从300只评到50只，多维因子打分+<br/>市场状态动态偏移+主力+8态+拥挤度+密度分布全用上<br/>。<br/>作战环节 / battle-step<br/>(候选态 / candidate)<br/>🟡候选承载<br/>【Fine Scoring】"]
    BM_SEL_19["【BM-SEL-19 事件驱动分布筛选】<br/>漏斗第四层——从50只筛到30只，看事件影响、事件修正<br/>后的概率分布、传导链风险，没事件数据源就跳过。<br/>作战环节 / battle-step<br/>(候选态 / candidate)<br/>🟡候选承载<br/>【Event-Driven Distribution Screening】"]
    BM_SEL_20["【BM-SEL-20 多策略交叉投票】<br/>漏斗第五层——多策略对每只票投YES<br/>/NO，加上主力合力和市场状态否决，少数服从多数。<br/>作战环节 / battle-step<br/>(候选态 / candidate)<br/>🟡候选承载<br/>【Multi-Strategy Cross Voting】"]
    BM_SEL_21["【BM-SEL-21 组合优化】<br/>漏斗第六层——从30只里算出最终N≤10只下单清单和每只<br/>权重，行业、市值、风险、相关性、拥挤度全约束。<br/>作战环节 / battle-step<br/>(生产态 / production)<br/>🟡候选承载<br/>【Portfolio Optimization】"]
    BM_SEL_01 ~~~ BM_SEL_05 ~~~ BM_SEL_06 ~~~ BM_SEL_07 ~~~ BM_SEL_08 ~~~ BM_SEL_09 ~~~ BM_SEL_10 ~~~ BM_SEL_11 ~~~ BM_SEL_12 ~~~ BM_SEL_13 ~~~ BM_SEL_14 ~~~ BM_SEL_15 ~~~ BM_SEL_16
    BM_SEL_02 ~~~ BM_SEL_17
    BM_SEL_03 ~~~ BM_SEL_18
    BM_SEL_04 ~~~ BM_SEL_19
    BM_SEL_01 -->|标准化行情 / data_flow| BM_SEL_02
    BM_SEL_02 -.->|因子池 / data_flow| BM_SEL_03
    BM_SEL_03 -.->|市场状态 / data_flow| BM_SEL_04
    BM_SEL_03 -.->|C-021未就绪→跳过降级 / degradation| BM_SEL_04
    BM_SEL_16 -.->|漏斗L1→L2(~1200只) / data_flow| BM_SEL_17
    BM_SEL_17 -.->|漏斗L2→L3(~300只) / data_flow| BM_SEL_18
    BM_SEL_18 -.->|漏斗L3→L4(~50只) / data_flow| BM_SEL_19
    BM_SEL_19 -.->|漏斗L4→L5(~30只) / data_flow| BM_SEL_20
    BM_SEL_20 -.->|漏斗L5→L6 / data_flow| BM_SEL_21
classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
classDef deprecated fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
classDef missing fill:#eeeeee,stroke:#9e9e9e,stroke-width:2px,color:#000
classDef candidate fill:#fffde7,stroke:#f9a825,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    class BM_SEL_01,BM_SEL_02,BM_SEL_21 production
    class BM_SEL_03,BM_SEL_04 design
    class BM_SEL_05,BM_SEL_06,BM_SEL_07,BM_SEL_08,BM_SEL_09,BM_SEL_10,BM_SEL_11,BM_SEL_12,BM_SEL_13,BM_SEL_14,BM_SEL_15,BM_SEL_16,BM_SEL_17,BM_SEL_18,BM_SEL_19,BM_SEL_20 candidate
```

## 环节详情

### BM-SEL-01 数据接入与预处理 / Data Ingestion & Preprocessing

> **大白话**：把外面来的行情、新闻、另类数据收进来洗干净，按热度分层存好，供后面所有环节使用。

**机制说明**：

L0 层入口。每个 miniQMT Tick（3秒）触发，把 miniQMT/iFind/tushare 行情+新闻+另类数据经事件总线写入分层时序存储（Redis 热+ClickHouse 温+Parquet 冷）。是整个数据流主动脉的起点。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 每个 miniQMT Tick（3秒）+ 盘前定时 阈值: Tick 频率 3s |
| ② 消费数据/因子 | miniQMT/iFind/tushare 行情+新闻（来自 外部数据源）<br>另类数据（社交情绪/供应链）（来自 外部另类数据源） |
| ③ 参数 | tick_frequency=3s（范围 1-10s，代码当前: 3s，状态: implemented）<br>storage_tiering=Redis热+ClickHouse温+Parquet冷（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 外部数据源 → 处理: 事件总线+分层时序存储 → 输出: 标准化行情/因子原料 → 下游: BM-SEL-02 因子计算 |
| ⑤ 代码映射 | C-001 / 草图§2 L0 层 |
| ⑥ 降级/中止 | 数据源断流 → 仅执行卖出指令（应急保命轨） |

**指标文案（翻译真源 indicators_zh）**：

①触发：每 3 秒 Tick + 盘前定时；②消费：外部行情/新闻/另类数据；③参数：tick_frequency=3s、分层存储策略；④数据流：外部源→事件总线→分层存储→BM-SEL-02；⑤代码：C-001 L0 层；⑥降级：数据源断流→仅执行卖出指令。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-MKT-003 | primary | planned | generated |
| depgraph | MOD-INF-002 | supplement | production | generated |
| candidate | CAND-AISA-001 | supplement | candidate | — |
| candidate | CAND-DAT-001 | supplement | deferred | — |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L0 ｜ **阶段**：stock_selection

### BM-SEL-02 因子计算与信号生成 / Factor Compute & Signal Gen

> **大白话**：把洗干净的行情算成各种因子，再用因子工厂管起来，盘前算全量、盘中补增量。

**机制说明**：

L1 层。因子工厂全生命周期管理，盘前全量+盘中增量双模计算，产出因子池（设计容量≥150，运行≤64）。叠加分布特征工程（滞后项/交互项/签名方法）喂密度预测模型。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 盘前全量 + 盘中增量（双模） 阈值: 因子池 ≤64（≤60活跃+≤4休眠） |
| ② 消费数据/因子 | 标准化行情（来自 BM-SEL-01）<br>因子工厂全生命周期管理（来自 C-027 因子工厂） |
| ③ 参数 | factor_pool_max=64（范围 32-128，代码当前: 待实现，状态: proposed）<br>compute_mode=盘前全量+盘中增量（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 标准化行情 → 处理: 因子计算+分布特征工程 → 输出: 因子池+信号原料 → 下游: BM-SEL-03 市场状态 / BM-SELL-01 突破成败 |
| ⑤ 代码映射 | C-009/C-027 / 草图§3 L1 层 |
| ⑥ 降级/中止 | 因子层全部失效 → 降级硬编码均线规则（应急保命轨） |

**指标文案（翻译真源 indicators_zh）**：

①触发：盘前全量+盘中增量；②消费：BM-SEL-01 标准化行情 + C-027 因子工厂；③参数：factor_pool_max=64、双模计算；④数据流：行情→因子计算→因子池→BM-SEL-03/BM-SELL-01；⑤代码：C-009/C-027 L1 层；⑥降级：因子层全失效→硬编码均线规则。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-L02-001 | primary | production | generated |
| candidate | CAND-SIG-002 | supplement | deferred | — |
| candidate | CAND-FAC-001 | supplement | deferred | — |
| candidate | CAND-FAC-002 | supplement | deferred | — |
| candidate | CAND-INT-001 | supplement | deferred | — |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L1 ｜ **阶段**：stock_selection

### BM-SEL-03 市场状态感知 / Market State Sensing

> **大白话**：判断现在市场是什么脾气——趋势/波动/量能三维打分，再叠加体制转换检测。

**机制说明**：

L2-C 层。3×3×3 立方体（量能=第3维度）+ 日历修饰器（交割日/财报季）+ 体制转换检测（HMM/变点）+ Survival 止盈止损时间预测。是 P1 增强环节，激活时嵌入 C-009 和 C-005 之间。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 盘前 + 盘中周期触发 阈值: 3×3×3 立方体（量能=第3维度） |
| ② 消费数据/因子 | 因子池（来自 BM-SEL-02）<br>量能/日历修饰（来自 L2-C） |
| ③ 参数 | matrix_dims=3×3×3（范围 3×3→3×3×3，代码当前: Phase1-2: 3×3，状态: testing）<br>regime_detection=HMM/变点（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 因子池 → 处理: 3×3矩阵+体制转换检测 → 输出: 市场状态标签+Survival时间预测 → 下游: BM-SEL-04 次日预测 / BM-BUY-02 四轨融合 |
| ⑤ 代码映射 | C-021 / 草图§6 L2-C 层 |
| ⑥ 降级/中止 | C-021 未就绪 → 主动脉跳过本环节（8节点7跳降级模式） |

**指标文案（翻译真源 indicators_zh）**：

①触发：盘前+盘中周期；②消费：BM-SEL-02 因子池 + 量能/日历；③参数：matrix_dims=3×3×3（Phase1-2 跑 3×3）、regime=HMM；④数据流：因子池→3×3矩阵+体制检测→市场状态+Survival→BM-SEL-04/BM-BUY-02；⑤代码：C-021 L2-C；⑥降级：C-021 未就绪→主动脉跳过（8节点7跳降级）。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-SIG-036 | primary | planned | planned |
| candidate | CAND-HARVEST-0007 | supplement | candidate | — |

**有效状态**：🟧 设计态（待施工） ｜ **环节自报**：design ｜ **层**：L2C ｜ **阶段**：stock_selection

### BM-SEL-04 次日8态走势预测 / Next-Day 8-State Forecast

> **大白话**：预测明天大盘和个股会走成哪种样子，8 种走势各占多少概率——A股T+1制度下这是核心决策依据。

**机制说明**：

L2-C 层。T+1 次日 8 态走势预测（大盘+个股双预测体系）。Phase 1-2 先跑稳 3 态→5 态，Phase 4 后从密度预测 PDF 积分派生 8 态概率，统计一致性更强。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 盘前 T+1 预测（A股T+1制度） 阈值: 8态概率 P1~P8 |
| ② 消费数据/因子 | 市场状态（来自 BM-SEL-03）<br>条件PDF（密度预测）（来自 L2-A 密度预测） |
| ③ 参数 | state_count=8（范围 3→5→8（分阶段），代码当前: Phase1-2: 3态，状态: testing）<br>pdf_integration=Phase4 从PDF积分派生（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 市场状态+条件PDF → 处理: 8态预测（大盘+个股双预测） → 输出: T+1 8态概率分布 → 下游: BM-BUY-01 多情景对策 |
| ⑤ 代码映射 | C-014 / 草图§6.2 |
| ⑥ 降级/中止 | C-014 未就绪 → 降级二值涨/跌预测 |

**指标文案（翻译真源 indicators_zh）**：

①触发：盘前 T+1 预测；②消费：BM-SEL-03 市场状态 + 密度预测条件PDF；③参数：state_count=8（分阶段 3→5→8）、PDF 积分派生；④数据流：市场状态+PDF→8态预测→T+1概率分布→BM-BUY-01；⑤代码：C-014 §6.2；⑥降级：C-014 未就绪→二值涨/跌预测。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-SIG-037 | primary | planned | planned |
| candidate | CAND-HARVEST-0008 | supplement | candidate | — |

**有效状态**：🟧 设计态（待施工） ｜ **环节自报**：design ｜ **层**：L2C ｜ **阶段**：stock_selection

### BM-SEL-05 主力行为感知 / Main-Force Behavior Sensing

> **大白话**：识别庄家和主力资金在干什么——吸筹、洗盘、拉升还是出货弃庄，给选股和做T提供主力视角。

**机制说明**：

L2-B 层。C-011 六阶段识别（吸筹/洗盘/拉升/出货）+ C-034 主力推演 + C-035 庄家画像 + C-036 群体博弈合力。
产出主力阶段标签和弃庄概率，注入漏斗第二/三层加分/扣分，并约束做T（出货/弃庄阶段丢弃做T信号）。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 盘前全量+盘中增量 阈值: 六阶段识别 |
| ② 消费数据/因子 | 龙虎榜/资金流/大宗交易（来自 L0）<br>因子池（来自 BM-SEL-02） |
| ③ 参数 | 识别阶段数=6（范围 -，代码当前: 待实现，状态: proposed）<br>弃庄概率门槛=95%（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: L0资金流 → 处理: C-011六阶段+C-034推演+C-035庄家+C-036合力 → 输出: 主力阶段标签+弃庄概率 → 下游: BM-SEL-17/18 漏斗加分 |
| ⑤ 代码映射 | 缺失态-未实现 / 草图§5 L2-B |
| ⑥ 降级/中止 | 主力层未就绪 → 漏斗第二/三层不加分（仅技术+基本面） |

**指标文案（翻译真源 indicators_zh）**：

①触发：盘前全量+盘中增量；②消费：龙虎榜/资金流/大宗交易+因子池；③参数：识别阶段数=6、弃庄概率门槛95%；④数据流：L0资金流→C-011/034/035/036→注入信号层/漏斗；⑤代码：缺失态-未实现（草图§5）；⑥降级：主力层未就绪→漏斗不加分（仅技术+基本面）。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-0005 | primary | candidate | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：design ｜ **层**：L2B ｜ **阶段**：stock_selection

### BM-SEL-06 跨市场传导感知 / Cross-Market Conduction Sensing

> **大白话**：美股、港股、汇率、商品一异动，立刻算出对A股的传导系数和影响幅度。

**机制说明**：

L2-C 层。C-039 跨市场传导量化模型，消费全球市场异动事件，计算传导系数→预测A股影响幅度→触发全量/板块重算。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 美股/港股/汇率/商品异动到达 |
| ② 消费数据/因子 | 全球市场数据（来自 L0）<br>传导路径图（来自 L2-D知识图谱） |
| ③ 参数 | 传导系数模型=—（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 全球异动 → 处理: C-039传导系数计算 → 输出: A股影响幅度预测 → 下游: 全量/板块重算 |
| ⑤ 代码映射 | 缺失态-未实现 / 草图§6.3 C-039 |
| ⑥ 降级/中止 | C-039未就绪 → 异动仅告警不量化传导 |

**指标文案（翻译真源 indicators_zh）**：

①触发：美股/港股/汇率/商品异动到达；②消费：全球市场数据+传导路径图(L2-D)；③参数：传导系数模型(proposed)；④数据流：全球异动→C-039传导系数→A股影响幅度→重算；⑤代码：缺失态-未实现（草图§6.3）；⑥降级：C-039未就绪→异动仅告警不量化传导。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-0009 | primary | candidate | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：design ｜ **层**：L2C ｜ **阶段**：stock_selection

### BM-SEL-07 体制转换检测 / Regime Change Detection

> **大白话**：盯着市场脾气会不会变——趋势转震荡、牛转熊的切换点提前预警。

**机制说明**：

L2-C 层。市场状态连续评分偏离 + HMM/变点检测，识别体制切换，输出前瞻性预警。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 状态评分偏离+HMM/变点检测 |
| ② 消费数据/因子 | 市场状态评分（来自 BM-SEL-03） |
| ③ 参数 | 检测方法=HMM+变点（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 状态评分 → 处理: 体制检测 → 输出: regime切换信号 → 下游: 前瞻性预警 |
| ⑤ 代码映射 | 缺失态-未实现 / 草图§6.4 |
| ⑥ 降级/中止 | 体制检测未就绪 → 仅用当前状态不预警切换 |

**指标文案（翻译真源 indicators_zh）**：

①触发：状态评分偏离+HMM/变点；②消费：市场状态评分(L2C)；③参数：检测方法=HMM+变点(proposed)；④数据流：评分→体制检测→切换预警；⑤代码：缺失态-未实现（草图§6.4）；⑥降级：未就绪→仅用当前状态不预警切换。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-0368 | primary | candidate | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：design ｜ **层**：L2C ｜ **阶段**：stock_selection

### BM-SEL-08 板块轮动序列追踪 / Sector Rotation Sequence Tracking

> **大白话**：追踪板块强弱的轮动顺序，给回踩质量打A/B/C级，决定买入优先级。

**机制说明**：

L2-C 层 v4.1。板块轮动序列追踪，输出回踩质量等级（A/B/C），用于分批建仓标的优先级排序和突破失败降级。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 盘后板块强度更新 |
| ② 消费数据/因子 | 板块排名/资金流（来自 L0/L1） |
| ③ 参数 | 回踩质量等级=A/B/C（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 板块强度 → 处理: 轮动序列追踪 → 输出: 回踩质量等级A/B/C → 下游: BM-BUY-04 买入优先级/突破失败降级 |
| ⑤ 代码映射 | 缺失态-未实现 / 草图§6.1.3 v4.1 |
| ⑥ 降级/中止 | 轮动序列未就绪 → 不按回踩质量排序标的 |

**指标文案（翻译真源 indicators_zh）**：

①触发：盘后板块强度更新；②消费：板块排名/资金流(L0/L1)；③参数：回踩质量等级=A/B/C(proposed)；④数据流：板块强度→轮动序列→回踩质量→买入优先级；⑤代码：缺失态-未实现（草图§6.1.3）；⑥降级：未就绪→不按回踩质量排序。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-1649 | primary | candidate | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：design ｜ **层**：L2C ｜ **阶段**：stock_selection

### BM-SEL-09 调整周期追踪 / Adjustment Cycle Tracking

> **大白话**：追踪板块调整走到哪了——进度≥80%才允许分批低吸，初期<40%直接拦截。

**机制说明**：

L2-C 层 v4.1。调整周期进度追踪，进度≥80%激活分批建仓条件①，进度<40%初期拦截低吸信号。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 盘中周期更新 阈值: 进度≥80%激活分批 |
| ② 消费数据/因子 | 板块新高占比（来自 L0） |
| ③ 参数 | 进度阈值=80%（范围 -，代码当前: 待实现，状态: proposed）<br>初期拦截线=40%（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 新高占比 → 处理: 调整周期进度计算 → 输出: 进度百分比 → 下游: BM-BUY-04 分批条件①/初期拦截 |
| ⑤ 代码映射 | 缺失态-未实现 / 草图§6.6 v4.1 |
| ⑥ 降级/中止 | 调整周期未就绪 → 分批条件①缺位（2/3→1/2） |

**指标文案（翻译真源 indicators_zh）**：

①触发：盘中周期更新，进度≥80%激活分批；②消费：板块新高占比(L0)；③参数：进度阈值80%、初期拦截线40%(proposed)；④数据流：新高占比→调整进度→分批条件①/初期拦截；⑤代码：缺失态-未实现（草图§6.6）；⑥降级：未就绪→分批条件①缺位（2/3→1/2）。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-1651 | primary | candidate | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：design ｜ **层**：L2C ｜ **阶段**：stock_selection

### BM-SEL-10 行情生命周期阶段 / Market Lifecycle Phase

> **大白话**：判断行情在春夏秋冬哪一季——冬季禁止抄底，秋季突破失败更倾向强制离场。

**机制说明**：

L2-C 层 v4.1。行情生命周期阶段（春夏秋冬），驱动季节性硬规则：冬季禁抄底、秋季第三次挑战失败强制离场概率更高。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 盘后阶段判定 |
| ② 消费数据/因子 | 板块新高占比趋势（来自 L0） |
| ③ 参数 | 阶段数=4（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 新高占比趋势 → 处理: 生命周期阶段判定 → 输出: 春夏秋冬标签 → 下游: 冬季禁抄底/秋季强制离场 |
| ⑤ 代码映射 | 缺失态-未实现 / 草图§6.7 v4.1 |
| ⑥ 降级/中止 | 生命周期未就绪 → 不加季节性约束 |

**指标文案（翻译真源 indicators_zh）**：

①触发：盘后阶段判定；②消费：板块新高占比趋势(L0)；③参数：阶段数=4(proposed)；④数据流：新高占比趋势→生命周期阶段→冬季禁抄底/秋季强制离场；⑤代码：缺失态-未实现（草图§6.7）；⑥降级：未就绪→不加季节性约束。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-1642 | primary | candidate | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：design ｜ **层**：L2C ｜ **阶段**：stock_selection

### BM-SEL-11 知识图谱与因果推演 / Knowledge Graph & Causal Inference

> **大白话**：把事件、公司、行业的关联织成图谱，事件一来就推演传导路径，并区分关联因子和因果因子。

**机制说明**：

L2-D 层。C-016 六类知识图谱 + 事件驱动因果推演 + Causal ML（DML/CausalForest/DoWhy），区分关联因子vs因果因子，输出事件传导链供漏斗第四层消费。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 事件到达→匹配受影响节点+传导路径 |
| ② 消费数据/因子 | 事件流（来自 L0）<br>因子池（来自 BM-SEL-02） |
| ③ 参数 | 图谱类型数=6（范围 -，代码当前: 待实现，状态: proposed）<br>因果方法=DML/CausalForest/DoWhy（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 事件 → 处理: C-016图谱匹配+Causal ML筛选 → 输出: 传导链+因果因子集 → 下游: BM-SEL-19 漏斗第四层 |
| ⑤ 代码映射 | 缺失态-未实现 / 草图§7 L2-D |
| ⑥ 降级/中止 | L2-D未就绪 → 漏斗第四层跳过 |

**指标文案（翻译真源 indicators_zh）**：

①触发：事件到达→匹配受影响节点+传导路径；②消费：事件流+因子池；③参数：图谱类型数=6、因果方法=DML/CausalForest/DoWhy(proposed)；④数据流：事件→图谱匹配→传导链+Causal ML筛选→漏斗第四层；⑤代码：缺失态-未实现（草图§7）；⑥降级：未就绪→漏斗第四层跳过。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-0462 | primary | candidate | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：design ｜ **层**：L2D ｜ **阶段**：stock_selection

### BM-SEL-12 分布特征工程 / Distribution Feature Engineering

> **大白话**：给因子加料——滞后项、交互项、滚动统计量、签名方法，专门喂给密度预测模型。

**机制说明**：

L1 层。分布特征工程（§3.5），产出滞后项/交互项/滚动统计量/签名方法Signature，作为密度预测模型的特征输入。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 盘前因子计算同步产出 |
| ② 消费数据/因子 | 基础因子（来自 BM-SEL-02） |
| ③ 参数 | 特征族=滞后/交互/滚动统计/签名（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 基础因子 → 处理: 分布特征工程 → 输出: 滞后/交互/滚动/签名特征 → 下游: BM-SEL-13 密度预测输入 |
| ⑤ 代码映射 | 缺失态-未实现 / 草图§3.5 |
| ⑥ 降级/中止 | 分布特征未就绪 → 密度预测退化为点估计 |

**指标文案（翻译真源 indicators_zh）**：

①触发：盘前因子计算同步产出；②消费：基础因子(L1)；③参数：特征族=滞后/交互/滚动统计/签名(proposed)；④数据流：基础因子→分布特征→密度预测输入；⑤代码：缺失态-未实现（草图§3.5）；⑥降级：未就绪→密度预测退化为点估计。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-1371 | primary | candidate | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：design ｜ **层**：L1 ｜ **阶段**：stock_selection

### BM-SEL-13 收益率条件密度预测 / Conditional Density Prediction

> **大白话**：不只预测明天涨多少，而是预测明天收益率的完整概率分布——偏多少、尾巴多厚、极端情况多罕见。

**机制说明**：

L2-A 层。f(r|X_t) 条件PDF，分阶段实现（参数化→混合→非参数化归一化流/扩散），派生偏度/峰度/前瞻VaR/CVaR/8态概率P1~P8。被8态预测、组合优化、风控共形VaR三层消费。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 信号层产出条件PDF |
| ② 消费数据/因子 | 分布特征（来自 BM-SEL-12）<br>因子池（来自 BM-SEL-02） |
| ③ 参数 | Phase路径=参数化→混合→非参数化（范围 -，代码当前: 待实现，状态: proposed）<br>派生量=偏度/峰度/前瞻VaR/CVaR/P1~P8（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 分布特征+因子 → 处理: 密度预测模型 → 输出: 条件PDF+派生统计量 → 下游: BM-SEL-04 8态积分/BM-SEL-21 组合优化/BM-EXE-01 共形VaR |
| ⑤ 代码映射 | 缺失态-未实现 / 草图§4.5 |
| ⑥ 降级/中止 | 密度预测未就绪 → 8态用离散估计无分布增强 |

**指标文案（翻译真源 indicators_zh）**：

①触发：信号层产出条件PDF；②消费：分布特征+因子池(L1)；③参数：Phase=参数化→混合→非参数化，派生偏度/峰度/前瞻VaR/CVaR/P1~P8(proposed)；④数据流：分布特征→PDF→派生量→8态/组合优化/风控；⑤代码：缺失态-未实现（草图§4.5）；⑥降级：未就绪→8态用离散估计无分布增强。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-4924 | primary | candidate | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：design ｜ **层**：L2A ｜ **阶段**：stock_selection

### BM-SEL-14 共形预测 / Conformal Prediction

> **大白话**：给预测区间加数学保证——不管分布长什么样，区间覆盖率有数学证明。

**机制说明**：

L2-A 层。共形预测（分布无关），在密度预测PDF上叠加覆盖率保证区间，输出给风控共形VaR和信号置信区间。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 密度预测输出后叠加共形区间 |
| ② 消费数据/因子 | 密度预测PDF（来自 BM-SEL-13） |
| ③ 参数 | 覆盖率=95%（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 密度PDF → 处理: 共形预测 → 输出: 覆盖率保证区间 → 下游: BM-EXE-01 共形VaR/信号置信区间 |
| ⑤ 代码映射 | 缺失态-未实现 / 草图§1.7 |
| ⑥ 降级/中止 | 共形预测未就绪 → 区间无数学覆盖率保证 |

**指标文案（翻译真源 indicators_zh）**：

①触发：密度预测输出后叠加共形区间；②消费：密度预测PDF(L2A)；③参数：覆盖率=95%(proposed)；④数据流：PDF→共形→覆盖率保证区间→风控共形VaR/信号置信区间；⑤代码：缺失态-未实现（草图§1.7）；⑥降级：未就绪→区间无数学覆盖率保证。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-1428 | primary | candidate | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：design ｜ **层**：L2A ｜ **阶段**：stock_selection

### BM-SEL-15 Survival止盈止损时间预测 / Survival Stop-Time Prediction

> **大白话**：预测止盈止损还有多久发生——不是固定N天，而是时间概率分布。

**机制说明**：

L2-C 层。Survival 分析，预测止盈/止损发生时间和状态持续，输出给仓位时间预算和止盈止损时点。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 市场状态层产出时间分布 |
| ② 消费数据/因子 | 市场状态（来自 BM-SEL-03） |
| ③ 参数 | 预测目标=止盈/止损发生时间（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 市场状态 → 处理: Survival分析 → 输出: 止盈止损时间分布 → 下游: BM-POS-01 仓位时间预算/止盈止损时点 |
| ⑤ 代码映射 | 缺失态-未实现 / 草图§1.7 |
| ⑥ 降级/中止 | Survival未就绪 → 止盈止损用固定规则 |

**指标文案（翻译真源 indicators_zh）**：

①触发：市场状态层产出时间分布；②消费：市场状态(L2C)；③参数：预测目标=止盈/止损发生时间(proposed)；④数据流：市场状态→Survival时间分布→止盈止损时点+状态持续；⑤代码：缺失态-未实现（草图§1.7）；⑥降级：未就绪→止盈止损用固定规则。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-1429 | primary | candidate | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：design ｜ **层**：L2C ｜ **阶段**：stock_selection

### BM-SEL-16 分级指标过滤 / Tiered Screening Filter

> **大白话**：选股漏斗第一层——3秒级把全市场7000只砍到1200只，涨停跌停停牌ST次新弃庄统统按规则排除。

**机制说明**：

§13 漏斗第一层。3秒级，绝对排除（涨停封板/跌停/停牌）+ 门禁排除（ST/*ST）+ AUM分级成交额门槛 + 次新股份级 + 庄家弃庄概率排除，>80%淘汰。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 3秒级Tick 阈值: 7000→1200只(>80%淘汰) |
| ② 消费数据/因子 | 涨跌停/停牌/ST标记（来自 L0）<br>AUM分级（来自 配置）<br>上市天数（来自 L0）<br>庄家弃庄概率（来自 BM-SEL-05） |
| ③ 参数 | 成交额门槛(AUM≤100万)=≥500万（范围 -，代码当前: 待实现，状态: proposed）<br>次新上市<30天=绝对排除（范围 -，代码当前: 待实现，状态: proposed）<br>弃庄概率>95%=排除（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 全市场~7000只 → 处理: 物理/门禁/分级/概率排除 → 输出: ~1200只 → 下游: BM-SEL-17 初筛漏斗 |
| ⑤ 代码映射 | 缺失态-未实现 / 草图§13 漏斗L1 |
| ⑥ 降级/中止 | 过滤模块未就绪 → 仅排除涨跌停/停牌，其余放行 |

**指标文案（翻译真源 indicators_zh）**：

①触发：3秒级Tick，7000→1200只；②消费：涨跌停/停牌/ST标记+AUM分级+上市天数+弃庄概率(L2B)；③参数：成交额门槛(AUM≤100万)≥500万、次新<30天排除、弃庄>95%排除(proposed)；④数据流：全市场→物理/门禁/分级/概率排除→1200只→初筛；⑤代码：缺失态-未实现（草图§13 L1）；⑥降级：未就绪→仅排除涨跌停/停牌。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-4377 | primary | candidate | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：design ｜ **层**：L0 ｜ **阶段**：stock_selection

### BM-SEL-17 初筛漏斗 / Coarse Screening Funnel

> **大白话**：漏斗第二层——60秒级从1200只筛到300只，看技术形态、量价配合、板块强度、主力阶段、市场状态适配。

**机制说明**：

§13 漏斗第二层。60秒级，技术形态（均线多头/KDJ金叉/MACD底背离）+ 量价（量比>1.5/换手>1%）+ 板块强度（前30%）+ C-011主力阶段加分 + C-021状态适配（恐慌崩盘仅留防御型）。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 60秒级 阈值: 1200→300只 |
| ② 消费数据/因子 | 技术形态(均线/KDJ/MACD)（来自 BM-SEL-02）<br>量价(量比/换手)（来自 L0）<br>板块强度（来自 L0）<br>C-011主力阶段（来自 BM-SEL-05）<br>C-021市场状态（来自 BM-SEL-03） |
| ③ 参数 | 量比阈值=>1.5（范围 -，代码当前: 待实现，状态: proposed）<br>板块排名=前30%（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 分级过滤输出~1200只 → 处理: 技术+量价+板块+主力+状态 → 输出: ~300只 → 下游: BM-SEL-18 精筛评分 |
| ⑤ 代码映射 | 缺失态-未实现 / 草图§13 漏斗L2 |
| ⑥ 降级/中止 | 初筛未就绪 → 直接全量进精筛（算力风险） |

**指标文案（翻译真源 indicators_zh）**：

①触发：60秒级，1200→300只；②消费：技术形态(L1)+量价(L0)+板块强度(L0)+C-011主力(L2B)+C-021状态(L2C)；③参数：量比>1.5、板块排名前30%(proposed)；④数据流：分级过滤→技术+量价+板块+主力+状态→300只→精筛；⑤代码：缺失态-未实现（草图§13 L2）；⑥降级：未就绪→全量进精筛（算力风险）。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-1648 | primary | candidate | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：design ｜ **层**：L2A ｜ **阶段**：stock_selection

### BM-SEL-18 精筛评分 / Fine Scoring

> **大白话**：漏斗第三层——60秒级从300只评到50只，多维因子打分+市场状态动态偏移+主力+8态+拥挤度+密度分布全用上。

**机制说明**：

§13 漏斗第三层。60秒级，多维因子综合评分（价值40%/动量30%/质量20%/情绪10%）+ C-021状态动态偏移（±10%）+ 跨截面Z-score + C-034/C-035主力评分 + C-014 8态修正 + C-045拥挤度扣分 + 密度预测偏度/峰度/VaR增强。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 60秒级 阈值: 300→50只 |
| ② 消费数据/因子 | 多维因子（来自 BM-SEL-02）<br>C-021状态偏移（来自 BM-SEL-03）<br>C-034/C-035主力评分（来自 BM-SEL-05）<br>C-014 8态修正（来自 BM-SEL-04）<br>C-045拥挤度（来自 L4）<br>密度偏度/峰度/VaR（来自 BM-SEL-13） |
| ③ 参数 | 基础权重=价值40%/动量30%/质量20%/情绪10%（范围 -，代码当前: 待实现，状态: proposed）<br>状态偏移=±10%（范围 -，代码当前: 待实现，状态: proposed）<br>前瞻VaR扣分=15%（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 初筛输出~300只 → 处理: 综合评分(基础+偏移+主力+8态+拥挤+密度) → 输出: Z-score排名~50只 → 下游: BM-SEL-19 事件驱动筛选 |
| ⑤ 代码映射 | 缺失态-未实现 / 草图§13 漏斗L3 |
| ⑥ 降级/中止 | 精筛未就绪 → 等权综合评分 |

**指标文案（翻译真源 indicators_zh）**：

①触发：60秒级，300→50只；②消费：多维因子(L1)+C-021偏移(L2C)+C-034/035主力(L2B)+C-014 8态(L2C)+C-045拥挤(L4)+密度偏度/峰度/VaR(L2A)；③参数：基础权重价值40%/动量30%/质量20%/情绪10%、状态偏移±10%、前瞻VaR扣分15%(proposed)；④数据流：初筛→综合评分(基础+偏移+主力+8态+拥挤+密度)→Z-score→50只；⑤代码：缺失态-未实现（草图§13 L3）；⑥降级：未就绪→等权综合评分。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-0375 | primary | candidate | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：design ｜ **层**：L2A ｜ **阶段**：stock_selection

### BM-SEL-19 事件驱动分布筛选 / Event-Driven Distribution Screening

> **大白话**：漏斗第四层——从50只筛到30只，看事件影响、事件修正后的概率分布、传导链风险，没事件数据源就跳过。

**机制说明**：

§13 漏斗第四层 v3.4。60秒级，事件影响评分（L2-D图谱）+ 事件驱动条件PDF修正（上涨概率下降>15%淘汰）+ 事件传导链风险。开通条件：事件数据源+知识图谱+NLP就绪。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 60秒级 阈值: 50→30只(需事件数据源+知识图谱+NLP) |
| ② 消费数据/因子 | L2-D事件影响链（来自 BM-SEL-11）<br>事件驱动密度修正（来自 BM-SEL-13）<br>传导链路径（来自 BM-SEL-11） |
| ③ 参数 | 上涨概率下降门槛=>15%淘汰（范围 -，代码当前: 待实现，状态: proposed）<br>开通条件=事件数据源+知识图谱+NLP（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 精筛输出~50只 → 处理: 事件影响+条件PDF修正+传导链 → 输出: ~30只 → 下游: BM-SEL-20 多策略投票 |
| ⑤ 代码映射 | 缺失态-未实现 / 草图§13 漏斗L4 v3.4 |
| ⑥ 降级/中止 | 未开通 → 跳过本层，第三层直接进第五层 |

**指标文案（翻译真源 indicators_zh）**：

①触发：60秒级，50→30只，需事件数据源+知识图谱+NLP；②消费：L2-D事件影响链+事件驱动密度修正(L2A)+传导链(L2D)；③参数：上涨概率下降>15%淘汰、开通条件=事件数据源+知识图谱+NLP(proposed)；④数据流：精筛→事件影响+条件PDF修正+传导链→30只；⑤代码：缺失态-未实现（草图§13 L4 v3.4）；⑥降级：未开通→跳过本层，第三层直接进第五层。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-4937 | primary | candidate | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：design ｜ **层**：L2D ｜ **阶段**：stock_selection

### BM-SEL-20 多策略交叉投票 / Multi-Strategy Cross Voting

> **大白话**：漏斗第五层——多策略对每只票投YES/NO，加上主力合力和市场状态否决，少数服从多数。

**机制说明**：

§13 漏斗第五层。60秒级，策略A价值反转(30%)+策略B动量趋势(25%)+策略C事件驱动(20%)投票 + C-034/C-036主力合力投票 + C-021状态否决（状态不允许→否决买入）。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 60秒级 阈值: 30→30只 |
| ② 消费数据/因子 | 策略A价值反转（来自 L3）<br>策略B动量趋势（来自 L3）<br>策略C事件驱动（来自 L3）<br>C-034/C-036主力合力（来自 BM-SEL-05）<br>C-021状态否决（来自 BM-SEL-03） |
| ③ 参数 | 策略权重=A30%/B25%/C20%（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 事件筛选输出~30只 → 处理: 多策略YES/NO+主力+合力+状态否决 → 输出: ~30只 → 下游: BM-SEL-21 组合优化 |
| ⑤ 代码映射 | 缺失态-未实现 / 草图§13 漏斗L5 |
| ⑥ 降级/中止 | 投票未就绪 → 单策略决定 |

**指标文案（翻译真源 indicators_zh）**：

①触发：60秒级，30→30只；②消费：策略A/B/C(L3)+C-034/036主力合力(L2B)+C-021状态否决(L2C)；③参数：策略权重A30%/B25%/C20%(proposed)；④数据流：事件筛选→多策略YES/NO+主力+合力+状态否决→30只；⑤代码：缺失态-未实现（草图§13 L5）；⑥降级：未就绪→单策略决定。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| candidate | CAND-HARVEST-3225 | primary | candidate | — |

**有效状态**：🟨 候选态（候选池） ｜ **环节自报**：design ｜ **层**：L3 ｜ **阶段**：stock_selection

### BM-SEL-21 组合优化 / Portfolio Optimization

> **大白话**：漏斗第六层——从30只里算出最终N≤10只下单清单和每只权重，行业、市值、风险、相关性、拥挤度全约束。

**机制说明**：

§13 漏斗第六层 + §8.5 组合优化引擎。max Σ(w×score) s.t. 仓位上限(C-021)/容量(C-042)/行业偏离(±10%)/风格暴露/相关性(corr<0.7)/拥挤度(C-045)。叠加分布感知仓位调整（偏度/峰度/前瞻VaR）+ Kelly半仓位。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 60秒级 阈值: 30→N≤10只 |
| ② 消费数据/因子 | 候选标的+得分（来自 BM-SEL-18）<br>仓位上限（来自 BM-SEL-03）<br>C-042策略容量（来自 L3）<br>C-045拥挤度（来自 L4）<br>密度PDF参数（来自 BM-SEL-13） |
| ③ 参数 | 行业偏离=±10%/叠加态±15%/绝对30%（范围 -，代码当前: 待实现，状态: proposed）<br>相关性上限=corr<0.7（范围 -，代码当前: 待实现，状态: proposed）<br>Kelly=半Kelly硬上限（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 投票输出~30只 → 处理: maxΣ(w×score) s.t.仓位/容量/行业/风格/相关性/拥挤 → 输出: N只下单清单+权重 → 下游: BM-BUY-01 多情景对策 |
| ⑤ 代码映射 | MOD-PF-002 / 草图§8.5 组合优化引擎（部分建设） |
| ⑥ 降级/中止 | 组合优化未就绪 → 等权配置 |

**指标文案（翻译真源 indicators_zh）**：

①触发：60秒级，30→N≤10只；②消费：候选标的+得分(L2A)+仓位上限(L2C)+C-042容量(L3)+C-045拥挤(L4)+密度PDF(L2A)；③参数：行业偏离±10%/叠加态±15%/绝对30%、corr<0.7、半Kelly硬上限(proposed)；④数据流：投票输出→优化求解→N只下单清单→买入流；⑤代码：MOD-PF-002 组合优化器（部分建设）；⑥降级：未就绪→等权配置。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-PF-002 | primary | planned | generated |
| candidate | CAND-PFALLOC-001 | supplement | deferred | — |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L3 ｜ **阶段**：stock_selection


[← 返回总指挥图](battle_map_panorama.md)