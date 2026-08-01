---
ttl: permanent
doc_type: architecture_view
status: draft
version: "0.2.0"
date: 2026-08-02
---

# 交易决策作战地图（总指挥图）

> 第四全景图 battle_map 真源：`battle_map_steps` / `battle_map_anchors` / `battle_map_edges` 三表 + 翻译真源 `module_translation_registry.yaml` §battle_map_steps 段。
> 本文档由 `generate_battle_map_diagram.py` 自动生成，禁止手编（改环节→改 DB/YAML 真源→重跑生成器）。

**环节总数**：44 ｜ **流转边**：48 ｜ **无锚点环节**（BM-INV-001）: 0

**状态分布**：🟨 候选态（候选池）=16 ｜ 🟧 设计态（待施工）=15 ｜ 🟦 运营态（已建）=12 ｜ 🟥 弃用态=1

## 颜色标注说明（panorama §九 五态）

- 🟦 蓝色实线 = 运营态（锚点模块 build_status=stable/generated/testing，已建）
- 🟧 橙色虚线 = 设计态（锚点模块 build_status=planned，待施工）
- 🟥 红色 = 弃用态（锚点模块 build_status=deprecated）
- ⬜ 灰色 = 缺失态（环节无锚点，BM-INV-001 君子协定违例，悬空决策风险）
- 🟨 黄色 = 候选态（承载模块在候选池，未进全景图）
- 🟡 标记 = 环节有候选池锚点（候选承载备选）

## 总指挥图（全流程）

```mermaid
%% 作战地图总指挥图（第 1/2 页）
flowchart LR
    BM_BUY_01["BM-BUY-01\n多情景对策生成 / Multi-Scenario Countermeasure\n根据明天的8种走法，从策略库里挑出对应的买入对策预案。 🟡候选"]:::design
    BM_BUY_02["BM-BUY-02\n四轨融合 / Four-Track Fusion (MTF)\n把逻辑驱动、数据驱动、人工指令、应急保命四路信号按优先级融成…"]:::design
    BM_BUY_03["BM-BUY-03\n决策编排 / Decision Orchestration (DO)\n把融合后的决策按5条路径（买/卖/做T/人工/应急）统一出口…"]:::design
    BM_BUY_04["BM-BUY-04\n分批建仓 / Batched Position Building\n不是一次买够，而是分几批买，每批都要重新确认条件还成立，跌破…"]:::design
    BM_BUY_05["BM-BUY-05\n做T日内套利 / Intraday T+0 Arbitrage\nA股T+1约束下的日内套利——每天扫全部持仓，找有日内T+0…"]:::design
    BM_BUY_06["BM-BUY-06\n外部指令盯盘 / External Order Monitoring\n接收用户从微信/前端发来的买卖调仓指令，解析后走风控检查→执…"]:::production
    BM_EXE_01["BM-EXE-01\n自适应风控审批 / Adaptive Risk Approval\n下单前的最后一道闸——风控审批，审不过的订单直接拦下，是订单… 🟡候选"]:::production
    BM_EXE_02["BM-EXE-02\n交易执行 / Trade Execution\n审过的订单真正发出去下单，拿回成交回报和盈亏数据。 🟡候选"]:::design
    BM_EXE_03["BM-EXE-03\n执行质量TCA / Execution Quality TCA\n每笔成交后做'成本尸检'——把决策时刻到最终成交的总成本拆成…"]:::production
    BM_POS_01["BM-POS-01\n仓位管理裁决 / Position Adjudication\n所有买卖决策都到这里统一算最终仓位——这是仓位决策的唯一裁决… 🟡候选"]:::design
    BM_POS_02["BM-POS-02\n标级仓位Kelly / Per-Symbol Kelly Sizing\n每只票该买多少——用Kelly公式算理论仓位，半Kelly硬…"]:::design
    BM_POS_03["BM-POS-03\n持仓状态机漂移 / Position State Machine & Drift\n每只票有自己的状态(NONE→BUILDING→ACTIVE…"]:::production
    BM_POS_04["BM-POS-04\n跨策略仓位硬限制 / Cross-Strategy Position Hard Limit\n多策略同标的仓位合并取sum不超上限，新策略上线仓位砍到正常…"]:::production
    BM_POS_05["BM-POS-05\n资金曲线回撤缩放 / Capital Curve Drawdown Scaling\n系统的'自动驾驶油门刹车'——赚钱了净值创新高就慢慢加仓(每…"]:::production
    BM_REC_01["BM-REC-01\n交易运营清算 / Trade Ops & Settlement\n把成交回报拿去清算、算费率、处理公司行为，变成运营数据。"]:::design
    BM_REC_02["BM-REC-02\n报告复盘 / Reporting & Review\n把运营数据做成复盘报告，看今天打得怎么样。"]:::design
    BM_REC_03["BM-REC-03\n闭环优化反馈 / Closed-Loop Optimization Feedback\n复盘完把教训反馈回每一层——因子衰减就换、信号不准就退、模型… 🟡候选"]:::production
    BM_SELL_01["BM-SELL-01\n突破成败信号 / Breakout Success/Failure Signal\n判断股价冲压力位是冲上去了还是冲不动——冲上去留着，冲不动止…"]:::production
    BM_SELL_02["BM-SELL-02\n卖出信号融合仲裁 / Sell Signal Fusion Arbitration\n把所有卖出信号（含突破成败）汇总仲裁，强制清仓永远最高优先级…"]:::production
    BM_SELL_03["BM-SELL-03\n卖出信号收集评分 / Sell Signal Collection & Scoring\n卖出端的'信号层'——先把持仓分级(Watch/Monito…"]:::production
    BM_SELL_04["BM-SELL-04\n止盈止损族 / Take-Profit & Stop-Loss Strategy Family\n卖出端的'策略工厂'——根据策略类型用不同的止盈止损范式(趋…"]:::design
    BM_SELL_05["BM-SELL-05\n置换再平衡卖出 / Replacement & Rebalance Sell\n机会成本驱动+权重偏离驱动的被动卖出——候选池有更优标的就卖…"]:::production
    BM_SELL_06["BM-SELL-06\n买卖冲突仲裁 / Buy-Sell Conflict Arbitration\n同一只票同时有买入和卖出信号时怎么办——卖出优先(保守原则)…"]:::production
    BM_SEL_01["BM-SEL-01\n数据接入与预处理 / Data Ingestion & Preprocessing\n把外面来的行情、新闻、另类数据收进来洗干净，按热度分层存好，… 🟡候选"]:::design
    BM_SEL_02["BM-SEL-02\n因子计算与信号生成 / Factor Compute & Signal Gen\n把洗干净的行情算成各种因子，再用因子工厂管起来，盘前算全量、… 🟡候选"]:::deprecated
    BM_SEL_03["BM-SEL-03\n市场状态感知 / Market State Sensing\n判断现在市场是什么脾气——趋势/波动/量能三维打分，再叠加体… 🟡候选"]:::design
    BM_SEL_04["BM-SEL-04\n次日8态走势预测 / Next-Day 8-State Forecast\n预测明天大盘和个股会走成哪种样子，8 种走势各占多少概率——… 🟡候选"]:::design
    BM_SEL_05["BM-SEL-05\n主力行为感知 / Main-Force Behavior Sensing\n识别庄家和主力资金在干什么——吸筹、洗盘、拉升还是出货弃庄，… 🟡候选"]:::candidate
    BM_SEL_06["BM-SEL-06\n跨市场传导感知 / Cross-Market Conduction Sensing\n美股、港股、汇率、商品一异动，立刻算出对A股的传导系数和影响… 🟡候选"]:::candidate
    BM_SEL_07["BM-SEL-07\n体制转换检测 / Regime Change Detection\n盯着市场脾气会不会变——趋势转震荡、牛转熊的切换点提前预警。 🟡候选"]:::candidate
    BM_SEL_01 --- |标准化行情| BM_SEL_02
    BM_SEL_02 --- |因子池| BM_SEL_03
    BM_SEL_03 --- |市场状态| BM_SEL_04
    BM_SEL_04 --- |8态预测| BM_BUY_01
    BM_SEL_02 --- |压力位因子| BM_SELL_01
    BM_SEL_03 --- |进度+阶段+轮动| BM_BUY_04
    BM_BUY_01 --- |买入预案| BM_BUY_02
    BM_BUY_02 --- |统一决策流| BM_BUY_03
    BM_BUY_04 --- |分批仓位方案| BM_POS_01
    BM_SELL_01 --- |突破成败信号| BM_SELL_02
    BM_SELL_02 --- |卖出决策| BM_POS_01
    BM_BUY_03 --- |编排后决策| BM_POS_01
    BM_POS_01 --- |仓位指令| BM_EXE_01
    BM_EXE_01 --- |审批后订单| BM_EXE_02
    BM_EXE_02 --- |成交回报| BM_REC_01
    BM_REC_01 --- |运营数据| BM_REC_02
    BM_REC_02 --- |复盘报告| BM_REC_03
    BM_REC_03 ->> |迭代反馈（IC衰减/重训练）| BM_SEL_02
    BM_SEL_03 -.- |C-021未就绪→跳过降级| BM_SEL_04
    BM_BUY_04 ->> |分批建仓完成→做T监控| BM_BUY_05
    BM_BUY_05 --- |T指令(底仓不变)→仓位裁决| BM_POS_01
    BM_BUY_06 --- |外部指令→风控检查| BM_EXE_01
    BM_BUY_05 ->> |做T信号→买卖冲突仲裁| BM_SELL_06
    BM_BUY_06 ->> |外部指令→买卖冲突仲裁| BM_SELL_06
    BM_SELL_01 --- |突破成败信号→收集评分| BM_SELL_03
    BM_SELL_03 --- |评分输出→止盈止损族| BM_SELL_04
    BM_SELL_03 --- |评分输出→置换再平衡| BM_SELL_05
    BM_SELL_04 --- |止盈止损决策→融合仲裁| BM_SELL_02
    BM_SELL_05 --- |置换再平衡→融合仲裁| BM_SELL_02
    BM_SELL_02 --- |融合仲裁→买卖冲突仲裁| BM_SELL_06
    BM_SELL_06 --- |统一决策→仓位裁决| BM_POS_01
    BM_SELL_05 ->> |再平衡触发→状态机漂移检测| BM_POS_03
    BM_POS_01 --- |风险配额→标级Kelly| BM_POS_02
    BM_POS_02 --- |标级仓位→跨策略硬限制| BM_POS_04
    BM_POS_03 ->> |漂移触发→标级仓位调整| BM_POS_02
    BM_POS_05 ->> |回撤缩放→标级仓位约束| BM_POS_02
    BM_POS_05 ->> |回撤缩放→跨策略硬限制| BM_POS_04
    BM_POS_04 --- |实际仓位→风控审批| BM_EXE_01
    BM_EXE_02 --- |成交回报→TCA分析| BM_EXE_03
    BM_EXE_03 --- |执行质量→报告复盘| BM_REC_02
    BM_EXE_03 -.- |TCA反馈→执行算法优化| BM_EXE_02
    BM_POS_04 --- |实际仓位→交易执行| BM_EXE_02
classDef production fill:#4A90D9,stroke:#2C5F8A,color:#fff,stroke-width:2px;
classDef design fill:#E8A33D,stroke:#B57520,color:#fff,stroke-width:2px,stroke-dasharray: 5 5;
classDef deprecated fill:#D93636,stroke:#A02020,color:#fff,stroke-width:2px;
classDef missing fill:#BBBBBB,stroke:#888888,color:#fff,stroke-width:2px;
classDef candidate fill:#F4D03F,stroke:#B7950B,color:#000,stroke-width:2px;
```

```mermaid
%% 作战地图总指挥图（第 2/2 页）
flowchart LR
    BM_SEL_08["BM-SEL-08\n板块轮动序列追踪 / Sector Rotation Sequence Tracking\n追踪板块强弱的轮动顺序，给回踩质量打A/B/C级，决定买入优… 🟡候选"]:::candidate
    BM_SEL_09["BM-SEL-09\n调整周期追踪 / Adjustment Cycle Tracking\n追踪板块调整走到哪了——进度≥80%才允许分批低吸，初期〈4… 🟡候选"]:::candidate
    BM_SEL_10["BM-SEL-10\n行情生命周期阶段 / Market Lifecycle Phase\n判断行情在春夏秋冬哪一季——冬季禁止抄底，秋季突破失败更倾向… 🟡候选"]:::candidate
    BM_SEL_11["BM-SEL-11\n知识图谱与因果推演 / Knowledge Graph & Causal Inference\n把事件、公司、行业的关联织成图谱，事件一来就推演传导路径，并… 🟡候选"]:::candidate
    BM_SEL_12["BM-SEL-12\n分布特征工程 / Distribution Feature Engineering\n给因子加料——滞后项、交互项、滚动统计量、签名方法，专门喂给… 🟡候选"]:::candidate
    BM_SEL_13["BM-SEL-13\n收益率条件密度预测 / Conditional Density Prediction\n不只预测明天涨多少，而是预测明天收益率的完整概率分布——偏多… 🟡候选"]:::candidate
    BM_SEL_14["BM-SEL-14\n共形预测 / Conformal Prediction\n给预测区间加数学保证——不管分布长什么样，区间覆盖率有数学证… 🟡候选"]:::candidate
    BM_SEL_15["BM-SEL-15\nSurvival止盈止损时间预测 / Survival Stop-Time Prediction\n预测止盈止损还有多久发生——不是固定N天，而是时间概率分布。 🟡候选"]:::candidate
    BM_SEL_16["BM-SEL-16\n分级指标过滤 / Tiered Screening Filter\n选股漏斗第一层——3秒级把全市场7000只砍到1200只，涨… 🟡候选"]:::candidate
    BM_SEL_17["BM-SEL-17\n初筛漏斗 / Coarse Screening Funnel\n漏斗第二层——60秒级从1200只筛到300只，看技术形态、… 🟡候选"]:::candidate
    BM_SEL_18["BM-SEL-18\n精筛评分 / Fine Scoring\n漏斗第三层——60秒级从300只评到50只，多维因子打分+市… 🟡候选"]:::candidate
    BM_SEL_19["BM-SEL-19\n事件驱动分布筛选 / Event-Driven Distribution Screening\n漏斗第四层——从50只筛到30只，看事件影响、事件修正后的概… 🟡候选"]:::candidate
    BM_SEL_20["BM-SEL-20\n多策略交叉投票 / Multi-Strategy Cross Voting\n漏斗第五层——多策略对每只票投YES/NO，加上主力合力和市… 🟡候选"]:::candidate
    BM_SEL_21["BM-SEL-21\n组合优化 / Portfolio Optimization\n漏斗第六层——从30只里算出最终N≤10只下单清单和每只权重… 🟡候选"]:::design
    BM_SEL_16 --- |漏斗L1→L2(~1200只)| BM_SEL_17
    BM_SEL_17 --- |漏斗L2→L3(~300只)| BM_SEL_18
    BM_SEL_18 --- |漏斗L3→L4(~50只)| BM_SEL_19
    BM_SEL_19 --- |漏斗L4→L5(~30只)| BM_SEL_20
    BM_SEL_20 --- |漏斗L5→L6| BM_SEL_21
classDef production fill:#4A90D9,stroke:#2C5F8A,color:#fff,stroke-width:2px;
classDef design fill:#E8A33D,stroke:#B57520,color:#fff,stroke-width:2px,stroke-dasharray: 5 5;
classDef deprecated fill:#D93636,stroke:#A02020,color:#fff,stroke-width:2px;
classDef missing fill:#BBBBBB,stroke:#888888,color:#fff,stroke-width:2px;
classDef candidate fill:#F4D03F,stroke:#B7950B,color:#000,stroke-width:2px;
```

## 分阶段导航

- [选股阶段（21 环节）](battle_map_01_stock_selection.md)
- [买入阶段（6 环节）](battle_map_02_buy_flow.md)
- [卖出阶段（6 环节）](battle_map_03_sell_flow.md)
- [仓位阶段（5 环节）](battle_map_04_position_management.md)
- [执行阶段（3 环节）](battle_map_05_execution.md)
- [对账阶段（3 环节）](battle_map_06_reconciliation.md)
- [横切视图（§13漏斗 / §14盘中事件 / §16冲突矩阵）](battle_map_07_cross_cutting.md)

## 全环节详情（6 件套）

### BM-BUY-01 多情景对策生成 / Multi-Scenario Countermeasure

> **大白话**：根据明天的8种走法，从策略库里挑出对应的买入对策预案。

**机制说明**：

L3 层。C-005 多情景对策，基于次日 8 态预测匹配 7 种价格运动情景，结合 C-006 策略工厂策略库生成买入预案。是四轨融合器逻辑驱动轨的输入。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 次日8态预测就绪 阈值: 7种价格运动情景 |
| ② 消费数据/因子 | 8态预测（来自 BM-SEL-04）<br>策略工厂策略库（来自 C-006 策略工厂） |
| ③ 参数 | scenario_count=7（范围 5-10，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 8态+策略库 → 处理: 多情景对策匹配 → 输出: 买入预案 → 下游: BM-BUY-02 四轨融合 |
| ⑤ 代码映射 | C-005 / 草图§8 L3 层 |
| ⑥ 降级/中止 | C-005 失效 → 降级固定策略查表 |

**指标文案（翻译真源 indicators_zh）**：

①触发：8态预测就绪；②消费：BM-SEL-04 8态 + C-006 策略库；③参数：scenario_count=7；④数据流：8态+策略库→多情景对策→买入预案→BM-BUY-02；⑤代码：C-005 L3 层；⑥降级：C-005 失效→固定策略查表。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-PF-002 | primary | planned | planned |
| depgraph | MOD-L05-001 | supplement | stable | generated |
| candidate | CAND-HARVEST-0015 | supplement | candidate | — |

**有效状态**：🟧 设计态（待施工） ｜ **环节自报**：design ｜ **层**：L3 ｜ **阶段**：buy_flow

### BM-BUY-02 四轨融合 / Four-Track Fusion (MTF)

> **大白话**：把逻辑驱动、数据驱动、人工指令、应急保命四路信号按优先级融成一条决策流——应急永远最优先。

**机制说明**：

L3 层 v8.0。四轨融合器(MTF)嵌入 C-005 和决策编排器之间，将逻辑驱动轨+数据驱动轨(AI Discovery)+人工指令轨+应急保命轨四路信号融合为统一决策流，优先级 应急>人工>自动。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 四路信号就绪（逻辑/数据/人工/应急） 阈值: 优先级 应急>人工>自动 |
| ② 消费数据/因子 | 逻辑驱动轨（买入预案）（来自 BM-BUY-01）<br>数据驱动轨（AI Discovery）（来自 轨道2）<br>人工指令轨（来自 轨道3）<br>应急保命轨（来自 轨道4） |
| ③ 参数 | priority_order=应急>人工>自动（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 四路信号 → 处理: 四轨融合器(MTF)优先级仲裁 → 输出: 统一决策流 → 下游: BM-BUY-03 决策编排 |
| ⑤ 代码映射 | MTF(v8.0) / 草图§1.8 主动脉 |
| ⑥ 降级/中止 | MTF 不可用 → 降级逻辑轨单线决策 |

**指标文案（翻译真源 indicators_zh）**：

①触发：四路信号就绪；②消费：BM-BUY-01 逻辑轨 + 轨道2/3/4；③参数：priority_order=应急>人工>自动；④数据流：四路信号→MTF优先级仲裁→统一决策流→BM-BUY-03；⑤代码：MTF(v8.0) §1.8；⑥降级：MTF 不可用→逻辑轨单线决策。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-PF-006 | primary | planned | planned |

**有效状态**：🟧 设计态（待施工） ｜ **环节自报**：design ｜ **层**：L3 ｜ **阶段**：buy_flow

### BM-BUY-03 决策编排 / Decision Orchestration (DO)

> **大白话**：把融合后的决策按5条路径（买/卖/做T/人工/应急）统一出口编排，处理冲突、去重、排时序。

**机制说明**：

L3 层 v8.0。决策编排器(DO)嵌入四轨融合器和 C-047 之间，作为 5 条决策路径的统一出口，执行优先级仲裁+冲突消解+去重+时序编排。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 统一决策流就绪 阈值: 5条决策路径（买/卖/做T/人工/应急） |
| ② 消费数据/因子 | 统一决策流（来自 BM-BUY-02） |
| ③ 参数 | path_count=5（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 统一决策流 → 处理: 决策编排器(DO)优先级仲裁+冲突消解+去重+时序编排 → 输出: 编排后决策 → 下游: BM-POS-01 仓位裁决 |
| ⑤ 代码映射 | DO(v8.0) / 草图§1.8 主动脉 |
| ⑥ 降级/中止 | DO 不可用 → 降级直通仓位裁决 |

**指标文案（翻译真源 indicators_zh）**：

①触发：统一决策流就绪；②消费：BM-BUY-02 统一决策流；③参数：path_count=5；④数据流：统一决策流→DO 仲裁/消解/去重/时序→编排后决策→BM-POS-01；⑤代码：DO(v8.0) §1.8；⑥降级：DO 不可用→直通仓位裁决。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-PF-007 | primary | planned | planned |

**有效状态**：🟧 设计态（待施工） ｜ **环节自报**：design ｜ **层**：L3 ｜ **阶段**：buy_flow

### BM-BUY-04 分批建仓 / Batched Position Building

> **大白话**：不是一次买够，而是分几批买，每批都要重新确认条件还成立，跌破关键位置就停手。

**机制说明**：

分批建仓环节把单次买入拆成 N 批，每批买入前重新校验触发条件（满足 M/N 阈值）。
目的是降低择时风险——避免一次性在错误时点满仓。每批之间留间隔（默认 1 交易日），
让市场给出二次确认。任一批次触发降级条件（如跌破前低）则暂停后续批次并进入止损评估。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 满足2/3（调整周期到位/二次回落/缩量） 阈值: 2/3 |
| ② 消费数据/因子 | §6.6 调整周期进度（来自 BM-SEL-03）<br>§6.7 生命周期阶段（来自 BM-SEL-03）<br>§6.1.3 轮动序列（来自 BM-SEL-03）<br>量比（来自 BM-SEL-02） |
| ③ 参数 | batch_count=2（范围 2-4，代码当前: 待实现，状态: proposed）<br>batch_interval=1交易日（范围 1-3，代码当前: 待实现，状态: proposed）<br>satisfy_threshold=2/3（范围 1/3-3/3，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 进度+阶段+轮动 → 处理: 分批条件判定 → 输出: L3.5 分批仓位方案 → 下游: BM-POS-01 仓位裁决 |
| ⑤ 代码映射 | MOD-待定 / 草图§1.3 v4.1 |
| ⑥ 降级/中止 | 跌破前低 → 暂停后续批次→触发止损评估 |

**指标文案（翻译真源 indicators_zh）**：

①触发：满足 2/3（调整周期到位 / 二次回落 / 缩量）才放行下一批；
②消费：§6.6 建仓进度、§6.7 阶段判定、§6.1.3 轮动序列、量比；
③参数：分批数=2（可配 2-4）、间隔=1 交易日、满足阈值=2/3；
④数据流：进度+阶段+轮动→条件判定→L3.5 仓位决策→L4 执行；
⑤代码映射：MOD-xxx / src/zephyr/.../xxx.py；
⑥降级：跌破前低→暂停后续批次→止损评估。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-PA-006 | primary | planned | planned |

**有效状态**：🟧 设计态（待施工） ｜ **环节自报**：design ｜ **层**：L3 ｜ **阶段**：buy_flow

### BM-BUY-05 做T日内套利 / Intraday T+0 Arbitrage

> **大白话**：A股T+1约束下的日内套利——每天扫全部持仓，找有日内T+0空间的票，先买后卖或先卖后买赚差价，底仓净数量不变。

**机制说明**：

§8.3 C-012 独立做T信号管线 + §1.4第五层 T-Trade Coordinator。每日扫描全部持仓→分析每只当天是否有日内套利空间。
触发条件三选三全满足：今日波动率预期>做T空间阈值 + 风险可控(单次最大亏损<硬上限) + 底仓净数量不变。
两种模式：先买后卖(低位买入→高位卖出底仓部分) / 先卖后买(高位卖出底仓→低位买回)。
方向约束：黄线持续向上(强涨)→只做正T / 黄线持续向下(强跌)→只做反T。
做T仓位铁律：单次做T≤底仓30% / 净收益<1.5%不做 / 失误止损1.5% / 做T胜率目标>70%。
与其他信号交互(§5.6注入规则表权威定义)：C-004风控减仓→做T信号直接丢弃；C-035判定出货/弃庄→做T信号自动丢弃；流动性不足→做T信号丢弃；C-011洗盘阶段→做T允许。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 今日波动率预期>做T空间阈值 + 风险可控 + 底仓净数量不变 阈值: 做T胜率>70% |
| ② 消费数据/因子 | 全部持仓列表（来自 BM-POS-01）<br>分时因子(量比/CVD/VPIN)（来自 BM-SEL-02/C-009管线）<br>C-011/C-035主力阶段（来自 BM-SEL-05）<br>流动性评分（来自 BM-EXE-01/C-004）<br>风控减仓名单（来自 BM-EXE-01） |
| ③ 参数 | 单次做T上限=≤底仓30%（范围 -，代码当前: 待实现，状态: proposed）<br>净收益门槛=≥1.5%（范围 -，代码当前: 待实现，状态: proposed）<br>失误止损=1.5%（范围 -，代码当前: 待实现，状态: proposed）<br>做T空间阈值=今日波动率预期（范围 -，代码当前: 待实现，状态: proposed）<br>单次最大亏损硬上限=—（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 持仓+分时因子 → 处理: 做T机会识别+方向约束(强涨只正T/强跌只反T) → 输出: T-Trade指令(先买后卖/先卖后买) → 下游: BM-POS-01 仓位裁决(底仓不变)→BM-EXE-01 风控→BM-EXE-02 执行 |
| ⑤ 代码映射 | MOD-SELL-018 / 草图§8.3 C-012 + §1.4第五层 |
| ⑥ 降级/中止 | 底仓不足/流动性不足/标的在风控减仓名单/C-035判定出货弃庄 → 做T信号直接丢弃（见§5.6注入规则表） |

**指标文案（翻译真源 indicators_zh）**：

①触发：今日波动率预期>做T空间阈值+风险可控+底仓不变(做T胜率>70%)；②消费：全部持仓(BM-POS-01)+分时因子(BM-SEL-02)+主力阶段(BM-SEL-05)+流动性评分(BM-EXE-01)+风控减仓名单(BM-EXE-01)；③参数：单次做T≤底仓30%、净收益≥1.5%、失误止损1.5%(proposed)；④数据流：持仓+分时→机会识别+方向约束→T指令→仓位裁决(底仓不变)→风控→执行；⑤代码：MOD-SELL-018 t_trade_coordinator(planned)；⑥降级：底仓不足/流动性不足/风控减仓/庄家出货弃庄→做T信号直接丢弃。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-SELL-018 | primary | planned | planned |

**有效状态**：🟧 设计态（待施工） ｜ **环节自报**：design ｜ **层**：L3 ｜ **阶段**：buy_flow

### BM-BUY-06 外部指令盯盘 / External Order Monitoring

> **大白话**：接收用户从微信/前端发来的买卖调仓指令，解析后走风控检查→执行，是人工干预系统的入口。

**机制说明**：

§8.4 C-013 外部指令盯盘。数据流：用户指令(微信/前端)→C-013指令解析→C-004风控检查→C-031置信度分层→C-002执行。
输入：用户买入/卖出/调仓指令(标的代码+方向+数量+紧急程度)。
处理规则：C-013解析用户意图→转化为标准交易指令；C-004风控检查(标的在风控减仓名单→拦截建仓→通知用户)；C-031置信度分层(大额下单需人工确认B-013.6)；通过检查→C-002执行。
输出：执行结果→微信推送确认 / 拦截结果→微信推送拦截原因。
运行时间：交易时段(09:30-15:00)实时接收；盘前(09:15-09:25)仅接受集合竞价指令。
与§16冲突矩阵关系：C-004风控拦截 vs C-013外部指令→风控>用户指令(C-004优先)。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 用户指令到达(微信/前端) 阈值: 交易时段实时+盘前集合竞价 |
| ② 消费数据/因子 | 用户指令(标的+方向+数量+紧急度)（来自 外部输入）<br>风控减仓名单（来自 BM-EXE-01）<br>C-031置信度分级（来自 横切） |
| ③ 参数 | 大额确认阈值=B-013.6（范围 -，代码当前: 待实现，状态: proposed）<br>集合竞价窗口=09:15-09:25（范围 -，代码当前: 待实现，状态: proposed）<br>连续竞价窗口=09:30-15:00（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 用户指令 → 处理: C-013解析→标准交易指令→C-004风控检查→C-031置信度 → 输出: 执行结果/拦截结果 → 下游: BM-EXE-01 风控→BM-EXE-02 执行→微信推送确认/拦截原因 |
| ⑤ 代码映射 | MOD-L08-001 / 草图§8.4 C-013（前端入口，后端解析模块待建） |
| ⑥ 降级/中止 | 风控拦截建仓 → 通知用户拦截原因（C-004优先级>用户指令） |

**指标文案（翻译真源 indicators_zh）**：

①触发：用户指令到达(微信/前端)，交易时段实时+盘前集合竞价；②消费：用户指令(标的+方向+数量+紧急度)+风控减仓名单(BM-EXE-01)+C-031置信度(横切)；③参数：大额确认阈值B-013.6、集合竞价09:15-09:25、连续竞价09:30-15:00(proposed)；④数据流：用户指令→解析→风控→置信度→执行→微信推送；⑤代码：MOD-L08-001 trade_panel(stable，前端入口，后端解析模块待建)；⑥降级：风控拦截建仓→通知用户拦截原因(C-004优先级>用户指令)。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-L08-001 | primary | stable | generated |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：横切 ｜ **阶段**：buy_flow

### BM-EXE-01 自适应风控审批 / Adaptive Risk Approval

> **大白话**：下单前的最后一道闸——风控审批，审不过的订单直接拦下，是订单拦截器不是事后检查。

**机制说明**：

L4 层。C-004 自适应风控，作为订单拦截器：C-005 生成预案→MTF→DO→C-047 裁决仓位→C-004 风控审批后才→C-002 执行。C-004 仅依赖 C-001/C-002/C-009/C-021/C-047，不依赖 C-005。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 仓位指令就绪 阈值: 订单拦截器（审批后才执行） |
| ② 消费数据/因子 | 仓位指令（来自 BM-POS-01）<br>C-001/C-002/C-009/C-021/C-047 状态（来自 多环节） |
| ③ 参数 | risk_threshold=自适应（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 仓位指令 → 处理: C-004 风控审批（订单拦截） → 输出: 审批后订单 → 下游: BM-EXE-02 交易执行 |
| ⑤ 代码映射 | C-004 / 草图§9 L4 层 |
| ⑥ 降级/中止 | C-004 不可用 → 降级硬编码仓位上限10%（应急保命轨） |

**指标文案（翻译真源 indicators_zh）**：

①触发：仓位指令就绪；②消费：BM-POS-01 仓位指令 + 多环节状态；③参数：risk_threshold=自适应；④数据流：仓位指令→C-004 审批拦截→审批后订单→BM-EXE-02；⑤代码：C-004 L4 层；⑥降级：C-004 不可用→硬编码仓位上限10%。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-L06-001 | primary | production | generated |
| candidate | CAND-RSK-014 | supplement | deferred | — |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L4 ｜ **阶段**：execution

### BM-EXE-02 交易执行 / Trade Execution

> **大白话**：审过的订单真正发出去下单，拿回成交回报和盈亏数据。

**机制说明**：

L4 层。C-002 交易执行：下单+成交回报，产出交易指令+成交回报+PnL 数据。是数据流主动脉的末端执行节点。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 风控审批通过 阈值: 下单+成交回报 |
| ② 消费数据/因子 | 审批后订单（来自 BM-EXE-01） |
| ③ 参数 | order_algo=自适应（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 审批后订单 → 处理: C-002 下单+成交回报 → 输出: 交易指令+成交回报+PnL → 下游: BM-REC-01 运营清算 |
| ⑤ 代码映射 | C-002 / 草图§9 L4 层 |
| ⑥ 降级/中止 | C-002 失败 → 订单重试+告警 |

**指标文案（翻译真源 indicators_zh）**：

①触发：风控审批通过；②消费：BM-EXE-01 审批后订单；③参数：order_algo=自适应；④数据流：审批后订单→C-002 下单→交易指令+成交回报+PnL→BM-REC-01；⑤代码：C-002 L4 层；⑥降级：C-002 失败→订单重试+告警。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-XS-002 | primary | planned | planned |
| depgraph | MOD-EX-030 | supplement | planned | planned |
| candidate | CAND-HARVEST-0021 | supplement | candidate | — |
| candidate | CAND-EX-001 | supplement | deferred | — |
| candidate | CAND-EX-002 | supplement | deferred | — |

**有效状态**：🟧 设计态（待施工） ｜ **环节自报**：design ｜ **层**：L4 ｜ **阶段**：execution

### BM-EXE-03 执行质量TCA / Execution Quality TCA

> **大白话**：每笔成交后做"成本尸检"——把决策时刻到最终成交的总成本拆成时机成本+市场冲击+滑点+佣金，对比VWAP/TWAP/开盘价/收盘价基准，反馈给执行算法优化下次。

**机制说明**：

§9.2 C-046执行质量分析TCA(Trade Cost Analysis) + Implementation Shortfall。
Implementation Shortfall(IS)：决策时刻→最终成交的总成本分解(时机成本+市场冲击+滑点+佣金)。IS是执行质量的核心指标——衡量"决策意图"与"实际成交"之间的总损耗。
Pre-trade/At-trade/Post-trade三阶段TCA：
  Pre-trade：下单前预估执行成本(基于历史TCA+C-042策略容量约束)，用于执行计划生成。
  At-trade：下单时实时监控执行进度(实际执行vs计划轨迹偏差>阈值→暂停+告警)。
  Post-trade：成交后做成本归因(滑点来源/冲击成本/执行延迟)，反馈到执行算法。
执行基准对比：每笔订单vs VWAP/TWAP/开盘价/收盘价，评估执行质量优劣。
与Almgren-Chriss最优执行框架的协同：C-046历史TCA数据→执行计划生成→大单拆分策略→参与率控制(<15%分钟成交量)→执行时间窗口选择(开盘前5min/收盘前10min/均匀分布)→执行进度监控。
密度感知的执行时机优化(§9.2 v3.4新增)：基于条件PDF选择最优执行窗口——条件PDF右偏(正偏)→买入信号→优先在开盘执行(预期上涨概率高)；条件PDF左偏(负偏)→卖出信号→优先在开盘执行；条件PDF对称但宽(高不确定性)→延迟到收盘前执行。Almgren-Chriss的最优轨迹可基于条件PDF而非历史波动率计算。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 成交回报到达 阈值: — |
| ② 消费数据/因子 | 成交回报（来自 BM-EXE-02）<br>决策时刻价格（来自 BM-BUY-04/BM-SELL-02）<br>VWAP/TWAP/开盘价/收盘价（来自 L0）<br>C-042策略容量（来自 L3）<br>C-046历史TCA数据（来自 本环节） |
| ③ 参数 | IS成本分解=时机成本+市场冲击+滑点+佣金（范围 -，代码当前: 待实现，状态: proposed）<br>TCA阶段=Pre-trade/At-trade/Post-trade（范围 -，代码当前: 待实现，状态: proposed）<br>执行基准=VWAP/TWAP/开盘价/收盘价（范围 -，代码当前: 待实现，状态: proposed）<br>参与率控制=<15%分钟成交量（范围 -，代码当前: 待实现，状态: proposed）<br>执行进度偏差阈值=—（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 成交回报+决策时刻价格 → 处理: IS成本分解+三阶段TCA+基准对比 → 输出: 执行质量评分+成本归因 → 下游: 反馈到BM-EXE-02执行算法(Almgren-Chriss) + BM-REC-02复盘 |
| ⑤ 代码映射 | MOD-L07-001 / 草图§9.2 C-046（MOD-L07-001 default_tca_engine） |
| ⑥ 降级/中止 | TCA引擎未就绪 → 仅记录成交不分析(复盘缺执行质量维度) |

**指标文案（翻译真源 indicators_zh）**：

①触发：成交回报到达；②消费：成交回报(BM-EXE-02)+决策时刻价格(BM-BUY-04/BM-SELL-02)+VWAP/TWAP/开盘价/收盘价(L0)+C-042策略容量(L3)+C-046历史TCA数据(本环节)；③参数：IS成本分解(时机+冲击+滑点+佣金)、Pre/At/Post三阶段、执行基准VWAP/TWAP/开盘/收盘、参与率<15%、执行进度偏差阈值(proposed)；④数据流：成交回报+决策时刻价格→IS成本分解+三阶段TCA+基准对比→执行质量评分+成本归因→反馈到执行算法+复盘；⑤代码：MOD-L07-001 default_tca_engine(stable)；⑥降级：TCA引擎未就绪→仅记录成交不分析(复盘缺执行质量维度)。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-L07-001 | primary | stable | generated |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L4 ｜ **阶段**：execution

### BM-POS-01 仓位管理裁决 / Position Adjudication

> **大白话**：所有买卖决策都到这里统一算最终仓位——这是仓位决策的唯一裁决中心，谁都别想绕过。

**机制说明**：

L3.5 层。C-047（P0，v4.0 新增）仓位管理唯一裁决中心，嵌入决策编排器和 C-004 之间。所有仓位决策（含分批仓位方案）经 C-047 裁决后才进入风控审批和执行。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 编排后决策（买/卖）就绪 阈值: 仓位决策唯一裁决中心 |
| ② 消费数据/因子 | 编排后决策（来自 BM-BUY-03）<br>卖出决策（来自 BM-SELL-02）<br>分批仓位方案（来自 BM-BUY-04） |
| ③ 参数 | position_cap=目标仓位（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 买/卖决策+分批方案 → 处理: C-047 仓位唯一裁决 → 输出: 最终仓位指令 → 下游: BM-EXE-01 风控审批 |
| ⑤ 代码映射 | C-047 / 草图§1.8 主动脉（v4.0新增 P0） |
| ⑥ 降级/中止 | C-047 不可用 → 降级固定比例仓位查表 |

**指标文案（翻译真源 indicators_zh）**：

①触发：编排后决策（买/卖）就绪；②消费：BM-BUY-03 编排决策 + BM-SELL-02 卖出决策 + BM-BUY-04 分批方案；③参数：position_cap=目标仓位；④数据流：买/卖决策+分批方案→C-047唯一裁决→最终仓位指令→BM-EXE-01；⑤代码：C-047 §1.8（v4.0 P0）；⑥降级：C-047 不可用→固定比例仓位查表。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-POS-001 | primary | planned | planned |
| candidate | CAND-HARVEST-0019 | supplement | candidate | — |

**有效状态**：🟧 设计态（待施工） ｜ **环节自报**：design ｜ **层**：L3.5 ｜ **阶段**：position_management

### BM-POS-02 标级仓位Kelly / Per-Symbol Kelly Sizing

> **大白话**：每只票该买多少——用Kelly公式算理论仓位，半Kelly硬上限截断(禁止全Kelly)，在风险配额内决策，再用密度PDF的偏度/峰度/前瞻VaR做分布感知调整(防御性只减不增)。

**机制说明**：

§1.5 第四层标层 + §20.13约束13.2半Kelly硬上限 + §4.5.1-A3 Kelly公式升级。
Kelly仓位决策：从条件PDF直接积分计算胜率p和赔率b→Kelly分数→半Kelly仓位(0.5×f*)。
半Kelly约束为硬上限(约束13.2)：禁止使用全Kelly(定义与完整论证见约束12.13)。
v5.0风险配额约束：Kelly在风险配额内决策(每标的边际风险贡献MRC)——架构范式从"独立Kelly+硬约束截断"升级为"风险预算+约束优化"。
分布感知调整(防御性原则，默认只减不增)：
  偏度调整：偏度>0(正偏=上涨惊喜概率高)→仓位×(1+偏度调整系数)；偏度<0(负偏=下跌风险大)→仓位×(1-|偏度|调整系数)。
  峰度调整：超额峰度>0(厚尾=极端事件概率高)→仓位×(1-峰度惩罚系数)；超额峰度≤0→不调整。
  前瞻性VaR约束：前瞻性95%VaR>阈值→仓位上限自动下调；前瞻性95%CVaR>阈值→仓位上限进一步下调(CVaR比VaR更严格)。
  调整后约束：调整后仓位≤原优化仓位(防御性原则，默认只减不增)。⚠️正偏分布允许有限加仓但幅度不超过原优化仓位的10%(约束12.6)。
Kelly仓位与原优化仓位取较小值(防御性原则: Kelly只减不增)。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 买入信号到达 / 再平衡触发 阈值: — |
| ② 消费数据/因子 | 买入信号+得分（来自 BM-BUY-04）<br>风险配额(每标的MRC)（来自 BM-POS-01风险预算层）<br>密度PDF(偏度/峰度/VaR/CVaR)（来自 BM-SEL-13）<br>流动性评分(退出时间<1天)（来自 BM-EXE-01） |
| ③ 参数 | Kelly公式=0.5×f*(半Kelly)（范围 -，代码当前: 待实现，状态: proposed）<br>半Kelly硬上限=禁止全Kelly（范围 -，代码当前: 待实现，状态: proposed）<br>偏度调整系数=正偏×(1+α)/负偏×(1-|α|)（范围 -，代码当前: 待实现，状态: proposed）<br>峰度惩罚系数=超额峰度>0→×(1-β)（范围 -，代码当前: 待实现，状态: proposed）<br>前瞻VaR阈值=95%VaR>阈值→仓位上限下调（范围 -，代码当前: 待实现，状态: proposed）<br>正偏加仓幅度=≤原优化仓位10%（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 信号+风险配额+密度PDF → 处理: Kelly求解→半Kelly截断→风险配额约束→分布感知调整(防御性只减不增) → 输出: 标级仓位建议 → 下游: BM-POS-04 跨策略硬限制 → BM-EXE-01 风控 |
| ⑤ 代码映射 | MOD-POS-001 / 草图§1.5 第四层 + §20.13约束13.2 |
| ⑥ 降级/中止 | Kelly引擎未就绪 → 降级为固定比例仓位(按市场状态查表§20.3) |

**指标文案（翻译真源 indicators_zh）**：

①触发：买入信号到达/再平衡触发；②消费：买入信号+得分(BM-BUY-04)+风险配额MRC(BM-POS-01风险预算层)+密度PDF偏度/峰度/VaR/CVaR(BM-SEL-13)+流动性评分(BM-EXE-01)；③参数：Kelly=0.5×f*(半Kelly)、半Kelly硬上限、偏度调整系数、峰度惩罚系数、前瞻VaR阈值、正偏加仓≤10%(proposed)；④数据流：信号+风险配额+密度PDF→Kelly求解→半Kelly截断→风险配额约束→分布调整(只减不增)→标级仓位→跨策略硬限制→风控；⑤代码：MOD-POS-001 position_sizing_engine(planned)；⑥降级：Kelly引擎未就绪→降级为固定比例仓位(按市场状态查表§20.3)。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-POS-001 | primary | planned | planned |

**有效状态**：🟧 设计态（待施工） ｜ **环节自报**：design ｜ **层**：L3.5 ｜ **阶段**：position_management

### BM-POS-03 持仓状态机漂移 / Position State Machine & Drift

> **大白话**：每只票有自己的状态(NONE→BUILDING→ACTIVE→OBSERVING→REDUCING→EXITING→CLOSED)，权重漂移超±2%(组合)/±3%(单标的)就触发再平衡评估，观察期内禁止新买入。

**机制说明**：

§1.4 v6.0持仓状态机扩展 + §20.13约束13.3-13.4仓位漂移再平衡。
持仓状态机(每标的独立)：NONE→BUILDING→ACTIVE→OBSERVING→REDUCING→EXITING→CLOSED(冷却期)。
OBSERVING(观察期)：软止损触发/异常开盘/暴跌不直接卖→进入观察期。观察期超时(收盘前15min)→确认执行 / 观察期收回(价格回到止损位上方)→解除。观察期内禁止新买入(防止在不确定状态下加仓)。
仓位漂移再平衡阈值(约束13.3)：组合总仓位漂移超过±2%时触发再平衡评估；单标的仓位漂移超过±3%时触发标的级再平衡评估。再平衡评估不等于立即执行——须综合考虑交易成本(见13.4)。
再平衡成本-收益决策规则(约束13.4)：再平衡执行前必须计算预期收益改善vs交易成本(佣金+滑点+冲击成本)。只有预期收益改善>2×交易成本时才执行再平衡。市场状态为⑦阴跌/⑧加速下跌/⑨恐慌崩盘时成本系数×1.5。
v6.0持仓时间预算(Position Time Budget)：每标的最大持仓时间→超时自动触发退出评估。时间预算由策略类型+市场状态决定：趋势策略>30天/均值回归<10天。持仓时间超预算→信号评分器自动提升卖出信号权重。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 状态转换事件 / 仓位漂移>阈值 阈值: — |
| ② 消费数据/因子 | 持仓状态(NONE/BUILDING/ACTIVE/OBSERVING/REDUCING/EXITING/CLOSED)（来自 BM-POS-01）<br>当前权重（来自 BM-POS-01）<br>目标权重（来自 BM-POS-02）<br>漂移幅度（来自 BM-POS-01） |
| ③ 参数 | 组合漂移触发评估=±2%（范围 -，代码当前: 待实现，状态: proposed）<br>单标的漂移触发评估=±3%（范围 -，代码当前: 待实现，状态: proposed）<br>OBSERVING超时=收盘前15min（范围 -，代码当前: 待实现，状态: proposed）<br>观察期禁止新买入=是（范围 -，代码当前: 待实现，状态: proposed）<br>再平衡收益改善门槛=>2×交易成本（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 持仓状态+权重 → 处理: 状态机迁移+漂移检测+再平衡成本-收益决策 → 输出: 再平衡评估结果(执行/解除) → 下游: BM-POS-02 标级仓位调整 / BM-SELL-05 置换再平衡 |
| ⑤ 代码映射 | MOD-POS-002 / 草图§1.4 v6.0（MOD-POS-002状态机+MOD-POS-003漂移监控） |
| ⑥ 降级/中止 | 状态机未就绪 → 全部按ACTIVE处理，漂移监控退化为日终对账 |

**指标文案（翻译真源 indicators_zh）**：

①触发：状态转换事件/仓位漂移>阈值；②消费：持仓状态(NONE/BUILDING/ACTIVE/OBSERVING/REDUCING/EXITING/CLOSED)(BM-POS-01)+当前权重(BM-POS-01)+目标权重(BM-POS-02)+漂移幅度(BM-POS-01)；③参数：组合漂移±2%、单标的±3%、OBSERVING超时收盘前15min、观察期禁止新买入、再平衡收益改善>2×成本(proposed)；④数据流：持仓状态+权重→状态机迁移+漂移检测+再平衡成本-收益决策→再平衡评估结果→标级仓位调整/置换再平衡；⑤代码：MOD-POS-002 状态机(stable)+MOD-POS-003 漂移监控(stable)；⑥降级：状态机未就绪→全部按ACTIVE处理，漂移监控退化为日终对账。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-POS-002 | primary | stable | stable |
| depgraph | MOD-POS-003 | supplement | stable | stable |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L3.5 ｜ **阶段**：position_management

### BM-POS-04 跨策略仓位硬限制 / Cross-Strategy Position Hard Limit

> **大白话**：多策略同标的仓位合并取sum不超上限，新策略上线仓位砍到正常的30%，行业偏离/风格暴露有硬约束，C-047是仓位裁决唯一中心(只有C-004风控veto能绕过)。

**机制说明**：

§1.5 第三层策略层 + §20.3仓位上限框架 + §20.13约束13.1仓位裁决不可绕过。
跨策略仓位合并：同标的多策略合并→取sum不超上限。
策略冷启动约束：新策略仓位上限=正常×30%(防止新策略未验证即满仓)。
仓位上限框架(§20.3，市场状态驱动动态调整)：C-021市场状态判定→9态(①平稳牛市80%/②动量牛市80%/③恐慌反弹60%/④窄幅盘整40%/⑤宽幅震荡50%/⑥压缩突破60%/⑦阴跌30%/⑧加速下跌20%/⑨恐慌崩盘10%)+2叠加态(⑩事件驱动=基础×70%/⑪板块轮动=基础，行业集中度放宽至±15%)。
集中度控制(§20.3)：单一行业偏离不超过基准±10%(板块轮动叠加态⑪激活时放宽至±15%，绝对上限30%)；大小盘/价值成长风格暴露不超过±0.3标准差。
仓位裁决不可绕过(约束13.1)：所有常规仓位决策必须经过C-047裁决，任何能力不可绕过C-047直接设置仓位。⚠️例外：①C-004风控veto(风控优先级最高，可否决C-047的仓位裁决)；②§29.10即时反应引擎紧急子通道(仅限减仓操作、绕过四层裁决流程但仍受C-047仓位上限约束、须事后补录)。
仲裁规则——风险预算仓位 vs 市场状态仓位上限：当风险预算计算出的仓位超过市场状态驱动的仓位上限时，市场状态仓位上限为硬上限，风险预算分配的仓位不可超过该上限(取min)。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 多策略同标的仓位合并 / 新策略上线 / 仓位上限框架触发 阈值: — |
| ② 消费数据/因子 | 各策略仓位建议（来自 BM-POS-02）<br>策略冷启动状态（来自 L3策略工厂）<br>仓位上限框架(9态+2叠加态)（来自 BM-SEL-03/C-021）<br>行业偏离/风格暴露（来自 BM-SEL-21）<br>C-047仓位裁决（来自 BM-POS-01） |
| ③ 参数 | 同标的多策略合并=取sum不超上限（范围 -，代码当前: 待实现，状态: proposed）<br>新策略仓位上限=正常×30%（范围 -，代码当前: 待实现，状态: proposed）<br>行业偏离=±10%/叠加态±15%/绝对30%（范围 -，代码当前: 待实现，状态: proposed）<br>风格暴露=±0.3标准差（范围 -，代码当前: 待实现，状态: proposed）<br>仓位裁决不可绕过=C-047唯一裁决(例外:C-004风控veto)（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 多策略仓位+冷启动+上限框架 → 处理: 合并+冷启动折扣+行业/风格硬约束截断+C-047裁决 → 输出: 实际仓位(≤硬上限) → 下游: BM-EXE-01 风控审批 → BM-EXE-02 执行 |
| ⑤ 代码映射 | MOD-POS-010 / 草图§1.5 第三层 + §20.13约束13.1 |
| ⑥ 降级/中止 | 限制器未就绪 → 单策略独立决策(超限风险，需风控层兜底) |

**指标文案（翻译真源 indicators_zh）**：

①触发：多策略同标的仓位合并/新策略上线/仓位上限框架触发；②消费：各策略仓位建议(BM-POS-02)+策略冷启动状态(L3策略工厂)+仓位上限框架9态+2叠加态(BM-SEL-03/C-021)+行业偏离/风格暴露(BM-SEL-21)+C-047仓位裁决(BM-POS-01)；③参数：同标的多策略取sum不超上限、新策略仓位=正常×30%、行业偏离±10%/叠加态±15%/绝对30%、风格暴露±0.3标准差、C-047唯一裁决(例外C-004风控veto)(proposed)；④数据流：多策略仓位+冷启动+上限框架→合并+冷启动折扣+行业/风格硬约束截断+C-047裁决→实际仓位(≤硬上限)→风控→执行；⑤代码：MOD-POS-010 position_limit_enforcer(stable)；⑥降级：限制器未就绪→单策略独立决策(超限风险，需风控层兜底)。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-POS-010 | primary | stable | stable |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L3.5 ｜ **阶段**：position_management

### BM-POS-05 资金曲线回撤缩放 / Capital Curve Drawdown Scaling

> **大白话**：系统的"自动驾驶油门刹车"——赚钱了净值创新高就慢慢加仓(每次+5%)，亏钱回撤超5%就砍仓位10%、超10%就砍20%，回到回撤前高点才能恢复原仓位。

**机制说明**：

§9.1 C-032资金曲线自诊断 + §20.13约束13.5资金曲线驱动的仓位缩放。
C-032资金曲线自诊断(跨层)：预判层预警(结构性恶化早期预警)+监控层异常检测(资金曲线异常模式检测)。
资金曲线驱动的仓位缩放(约束13.5)：
  盈利扩张：组合净值创新高后，可逐步扩大总仓位上限(每次+5%，最大不超过§20.3框架的硬上限)。
  亏损收缩：组合回撤超过5%时，总仓位上限自动缩减10%；回撤超过10%时，总仓位上限自动缩减20%。
  恢复条件：净值回到回撤前高点方可恢复原仓位上限。
连续亏损触发链(§9.1熔断层)：连续N个交易日亏损→C-032资金曲线检测→C-015推送告警+触发C-031降级+AI输出诊断报告。
C-032异常模式检测：识别资金曲线的结构性恶化(非随机下行趋势)vs随机波动，区分"正常回撤"和"策略失效"。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 组合净值更新 / 回撤超阈值 / 连续亏损 阈值: — |
| ② 消费数据/因子 | 组合净值历史（来自 BM-REC-01）<br>回撤幅度（来自 BM-POS-01）<br>连续亏损天数（来自 BM-EXE-01/C-032）<br>资金曲线异常模式（来自 C-032） |
| ③ 参数 | 回撤>5%=仓位上限缩减10%（范围 -，代码当前: 待实现，状态: proposed）<br>回撤>10%=仓位上限缩减20%（范围 -，代码当前: 待实现，状态: proposed）<br>盈利扩张=每次+5%(不超§20.3硬上限)（范围 -，代码当前: 待实现，状态: proposed）<br>恢复条件=净值回到回撤前高点（范围 -，代码当前: 待实现，状态: proposed）<br>连续N日亏损触发=C-032检测→C-015告警→C-031降级（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 净值+回撤+连续亏损 → 处理: 资金曲线自诊断+回撤检测+仓位上限缩放/扩张 → 输出: 仓位上限缩放系数 → 下游: BM-POS-02 标级仓位约束 / BM-POS-04 跨策略硬限制 |
| ⑤ 代码映射 | MOD-POS-007 / 草图§9.1 C-032（MOD-POS-007资金曲线+MOD-POS-008回撤控制） |
| ⑥ 降级/中止 | 回撤控制器未就绪 → 仅资金曲线告警不自动缩放(需人工干预) |

**指标文案（翻译真源 indicators_zh）**：

①触发：组合净值更新/回撤超阈值/连续亏损；②消费：组合净值历史(BM-REC-01)+回撤幅度(BM-POS-01)+连续亏损天数(BM-EXE-01/C-032)+资金曲线异常模式(C-032)；③参数：回撤>5%→仓位上限缩减10%、回撤>10%→缩减20%、盈利扩张每次+5%(不超§20.3硬上限)、恢复条件=净值回到回撤前高点、连续N日亏损→C-032检测→C-015告警→C-031降级(proposed)；④数据流：净值+回撤+连续亏损→资金曲线自诊断+回撤检测+仓位上限缩放/扩张→仓位上限缩放系数→标级仓位约束/跨策略硬限制；⑤代码：MOD-POS-007 资金曲线(stable)+MOD-POS-008 回撤控制(planned)；⑥降级：回撤控制器未就绪→仅资金曲线告警不自动缩放(需人工干预)。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-POS-007 | primary | stable | stable |
| depgraph | MOD-POS-008 | supplement | planned | planned |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L3.5 ｜ **阶段**：position_management

### BM-REC-01 交易运营清算 / Trade Ops & Settlement

> **大白话**：把成交回报拿去清算、算费率、处理公司行为，变成运营数据。

**机制说明**：

L5/运营层。C-017 交易运营：清算/费率/公司行为。是闭环反馈路径的起点，承接 C-002 交易执行产出。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 成交回报就绪 阈值: 清算/费率/公司行为 |
| ② 消费数据/因子 | 成交回报（来自 BM-EXE-02） |
| ③ 参数 | settle_cycle=T+1（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 成交回报 → 处理: C-017 清算+费率+公司行为 → 输出: 运营数据 → 下游: BM-REC-02 报告复盘 |
| ⑤ 代码映射 | C-017 / 草图§1.8 闭环反馈 |
| ⑥ 降级/中止 | C-017 不可用 → 手动清算兜底 |

**指标文案（翻译真源 indicators_zh）**：

①触发：成交回报就绪；②消费：BM-EXE-02 成交回报；③参数：settle_cycle=T+1；④数据流：成交回报→C-017 清算/费率/公司行为→运营数据→BM-REC-02；⑤代码：C-017 §1.8 闭环；⑥降级：C-017 不可用→手动清算兜底。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-TRADING-003 | primary | planned | planned |
| depgraph | MOD-RPT-027 | supplement | planned | planned |

**有效状态**：🟧 设计态（待施工） ｜ **环节自报**：design ｜ **层**：L5 ｜ **阶段**：reconciliation

### BM-REC-02 报告复盘 / Reporting & Review

> **大白话**：把运营数据做成复盘报告，看今天打得怎么样。

**机制说明**：

L5 层。C-010 报告复盘：把运营数据加工成复盘报告，作为闭环优化的输入素材。MOD-RPT-027 是自我复盘的输入素材。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 运营数据就绪 阈值: 复盘报告 |
| ② 消费数据/因子 | 运营数据（来自 BM-REC-01） |
| ③ 参数 | report_freq=日/周（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 运营数据 → 处理: C-010 报告复盘 → 输出: 复盘报告 → 下游: BM-REC-03 闭环优化 |
| ⑤ 代码映射 | C-010 / 草图§1.8 闭环反馈 |
| ⑥ 降级/中止 | C-010 不可用 → 降级基础 PnL 报表 |

**指标文案（翻译真源 indicators_zh）**：

①触发：运营数据就绪；②消费：BM-REC-01 运营数据；③参数：report_freq=日/周；④数据流：运营数据→C-010 报告复盘→复盘报告→BM-REC-03；⑤代码：C-010 §1.8 闭环；⑥降级：C-010 不可用→基础 PnL 报表。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-RPT-026 | primary | planned | planned |
| depgraph | MOD-RPT-015 | supplement | planned | planned |

**有效状态**：🟧 设计态（待施工） ｜ **环节自报**：design ｜ **层**：L5 ｜ **阶段**：reconciliation

### BM-REC-03 闭环优化反馈 / Closed-Loop Optimization Feedback

> **大白话**：复盘完把教训反馈回每一层——因子衰减就换、信号不准就退、模型漂移就重训，形成正向闭环。

**机制说明**：

L5 层。C-007 闭环优化：反馈到 L1~L4+L3.5 每层（IC衰减→因子替代、准确率监控→信号退役、漂移检测→模型重训练、A/B 淘汰、阈值校准）。每轮迭代改动必须经过 C-003 回测门禁。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 复盘报告就绪 阈值: 反馈到 L1~L4+L3.5 每层 |
| ② 消费数据/因子 | 复盘报告（来自 BM-REC-02） |
| ③ 参数 | feedback_layers=L1~L4+L3.5（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 复盘报告 → 处理: C-007 闭环优化（IC衰减/准确率/漂移检测→重训练） → 输出: 因子/信号/策略/风控迭代信号 → 下游: BM-SEL-02 因子计算（反向闭环） |
| ⑤ 代码映射 | C-007 / 草图§1.8 闭环反馈 |
| ⑥ 降级/中止 | C-007 不可用 → 降级人工复盘 |

**指标文案（翻译真源 indicators_zh）**：

①触发：复盘报告就绪；②消费：BM-REC-02 复盘报告；③参数：feedback_layers=L1~L4+L3.5；④数据流：复盘报告→C-007 闭环优化→迭代信号→BM-SEL-02（反向闭环）；⑤代码：C-007 §1.8 闭环；⑥降级：C-007 不可用→人工复盘。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-L02-004 | primary | production | stable |
| candidate | CAND-WFO-001 | supplement | deferred | — |
| candidate | CAND-SIM-002 | supplement | deferred | — |
| candidate | CAND-BT-001 | supplement | deferred | — |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L5 ｜ **阶段**：reconciliation

### BM-SELL-01 突破成败信号 / Breakout Success/Failure Signal

> **大白话**：判断股价冲压力位是冲上去了还是冲不动——冲上去留着，冲不动止损，连冲3次不行强制清仓。

**机制说明**：

L2-A 层 v4.1。突破成败信号模型：压力位来自 L1 因子层，突破成功（N日站稳+放量）→持有/加仓，突破失败（回落>阈值）→止损，第 K≥3 次挑战失败→强制清仓。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 触及压力位后判定 阈值: N日站稳=成功；回落>阈值=失败；K≥3次失败=强制离场 |
| ② 消费数据/因子 | 压力位（前高/均线/斐波那契）（来自 BM-SEL-02 L1因子层）<br>挑战次数（来自 L2-A） |
| ③ 参数 | stand_days=N日（范围 3-10，代码当前: 待实现，状态: proposed）<br>fail_pullback_threshold=阈值（范围 -，代码当前: 待实现，状态: proposed）<br>force_exit_attempts=3（范围 2-5，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 压力位+挑战次数 → 处理: 突破成败判定 → 输出: 持有/止损/强制清仓信号 → 下游: BM-SELL-02 卖出融合仲裁 |
| ⑤ 代码映射 | MOD-待定 / 草图§1.4 v4.1 |
| ⑥ 降级/中止 | 突破成败判定未就绪 → 降级§8.2 支撑位破位→立即清仓 |

**指标文案（翻译真源 indicators_zh）**：

①触发：触及压力位后判定；②消费：BM-SEL-02 压力位因子 + 挑战次数；③参数：stand_days=N日、fail_pullback_threshold、force_exit_attempts=3；④数据流：压力位+挑战次数→突破成败判定→持有/止损/清仓信号→BM-SELL-02；⑤代码：§1.4 v4.1；⑥降级：判定未就绪→§8.2 支撑位破位立即清仓。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-SELL-003 | primary | planned | stable |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L2A ｜ **阶段**：sell_flow

### BM-SELL-02 卖出信号融合仲裁 / Sell Signal Fusion Arbitration

> **大白话**：把所有卖出信号（含突破成败）汇总仲裁，强制清仓永远最高优先级，谁的信号最狠听谁的。

**机制说明**：

L3 层。卖出信号融合仲裁：7 类卖出信号+突破成败信号汇总，最高优先级（强制清仓）取胜。卖出决策引擎是复合能力（§20.16），不单独分配 C 编号。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 7类卖出信号+突破成败汇总 阈值: 最高优先级=强制清仓 |
| ② 消费数据/因子 | 突破成败信号（来自 BM-SELL-01）<br>7类卖出信号（来自 卖出策略工厂） |
| ③ 参数 | signal_count=7+1（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 多源卖出信号 → 处理: 融合仲裁（最高优先级取胜） → 输出: 卖出决策 → 下游: BM-POS-01 仓位裁决 |
| ⑤ 代码映射 | MOD-待定（D-SELL-DECISION） / 草图§1.4 / 依赖图D-SELL-DECISION |
| ⑥ 降级/中止 | 融合仲裁未就绪 → 降级各卖出信号独立触发（不经融合） |

**指标文案（翻译真源 indicators_zh）**：

①触发：7类卖出信号+突破成败汇总；②消费：BM-SELL-01 突破成败 + 卖出策略工厂7类信号；③参数：signal_count=7+1；④数据流：多源卖出信号→融合仲裁→卖出决策→BM-POS-01；⑤代码：D-SELL-DECISION；⑥降级：融合未就绪→各信号独立触发。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-SELL-007 | primary | planned | stable |
| depgraph | MOD-SELL-001 | supplement | planned | stable |
| depgraph | MOD-SELL-002 | supplement | planned | planned |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L3 ｜ **阶段**：sell_flow

### BM-SELL-03 卖出信号收集评分 / Sell Signal Collection & Scoring

> **大白话**：卖出端的"信号层"——先把持仓分级(Watch/Monitor/Hold)，再收集7类卖出信号，多时间框架共振加权，产出卖出信号评分和紧迫度。

**机制说明**：

§1.4 第零层持仓分级 + 第一层卖出信号层 + v6.0多时间框架共振。
第零层持仓分级(Position Triage)：不是所有持仓都需同等监控。🔴Watch List(亏损接近止损/主力异常/突破关键位/量价背离)→实时卖出信号生成+融合仲裁(秒级)；🟡Monitor List(正常持仓)→定期扫描(5分钟级)；🟢Hold List(深度盈利+远离止损+长期持有)→仅重大事件触发。分级维度：风险敞口/盈亏状态/信号活跃度/流动性/持仓状态机阶段。动态升降：Monitor→Watch(亏损扩大5%)/Watch→Monitor(风险解除)。
第一层7类卖出信号：基本面恶化/技术面顶部形态/量价背离/主力出货/相对强弱/机会成本置换/时间止损。v4.1突破成败信号(已在BM-SELL-01)。v8.2拥挤度卖出信号。
v6.0多时间框架共振：每个卖出信号标注时间框架(日线/60min/15min/5min)，三级嵌套(日线定方向→60min定日内趋势→15min定交易级信号)，共振检测(多时间框架同方向→权重×1.5)，冲突消解(小周期与大周期冲突→大周期为准)。
L2-B/C/D显式注入：L2-B吸筹期降权/出货期加权；L2-C熊市阈值降低/牛市提高；L2-C v8.0日历约束(交割日/财报前/节前)；L2-D黑天鹅→绕过融合仲裁直接强制卖出。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 持仓分级触发(Watch秒级/Monitor 5分钟级/Hold事件驱动) 阈值: Watch List扫描=秒级 |
| ② 消费数据/因子 | 持仓列表(成本/盈亏/天数/状态)（来自 BM-POS-01）<br>7类卖出信号源（来自 L2-A/L2-B/L2-C/L2-D）<br>L2-B主力阶段（来自 BM-SEL-05）<br>L2-C市场状态+日历约束（来自 BM-SEL-03）<br>L2-D黑天鹅事件（来自 BM-SEL-11） |
| ③ 参数 | Watch List扫描频率=秒级（范围 -，代码当前: 待实现，状态: proposed）<br>Monitor List扫描频率=5分钟（范围 -，代码当前: 待实现，状态: proposed）<br>共振权重倍数=×1.5（范围 -，代码当前: 待实现，状态: proposed）<br>时间框架层级=日线→60min→15min（范围 -，代码当前: 待实现，状态: proposed）<br>熊市卖出阈值降低=—（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 持仓+7类信号源 → 处理: 分级+收集+多时间框架共振+市场状态条件化权重 → 输出: 卖出信号评分+紧迫度 → 下游: BM-SELL-02 融合仲裁 / BM-SELL-04 止盈止损族 |
| ⑤ 代码映射 | MOD-SELL-001 / 草图§1.4 第一层（MOD-SELL-001收集器+MOD-SELL-002评分器） |
| ⑥ 降级/中止 | 评分器未就绪 → 各卖出信号独立触发不经过融合（保守原则） |

**指标文案（翻译真源 indicators_zh）**：

①触发：持仓分级触发(Watch秒级/Monitor 5分钟级/Hold事件驱动)；②消费：持仓列表(BM-POS-01)+7类卖出信号源(L2A/B/C/D)+主力阶段(BM-SEL-05)+市场状态+日历(BM-SEL-03)+黑天鹅事件(BM-SEL-11)；③参数：Watch秒级/Monitor 5分钟、共振权重×1.5、日线→60min→15min三级(proposed)；④数据流：持仓+信号源→分级+收集+共振+状态条件化权重→评分+紧迫度→融合仲裁/止盈止损族；⑤代码：MOD-SELL-001 收集器(stable)+MOD-SELL-002 评分器(planned)；⑥降级：评分器未就绪→各卖出信号独立触发不经过融合(保守原则)。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-SELL-001 | primary | stable | stable |
| depgraph | MOD-SELL-002 | supplement | planned | planned |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L2A ｜ **阶段**：sell_flow

### BM-SELL-04 止盈止损族 / Take-Profit & Stop-Loss Strategy Family

> **大白话**：卖出端的"策略工厂"——根据策略类型用不同的止盈止损范式(趋势宽止损/均值回归中止损/套利无止损/高频紧止损/Carry宽止损)，叠加猎杀防护和期权定价评估。

**机制说明**：

§1.4 第二层卖出策略工厂(C-006卖出子集) + v6.0策略类型→止损范式映射 + 止损猎杀防护 + 止损期权定价评估。
止盈策略族：固定止盈/移动止盈/分批止盈/时间加权止盈。
v6.0策略类型→止损范式映射层(Strategy-Specific Stop Framework)：趋势跟踪→宽止损(否则必被震出)+移动止损为主；均值回归→中等止损(不盈利=论点错误)+固定止损为主；统计套利→无传统止损(用组合对冲+仓位管理替代)；高频→极紧止损(论点失效立即退出)；Carry→极宽止损或无止损(接受小亏大赚)。
止损策略族：固定止损/波动率止损(ATR)/密度感知止损/移动止损。逻辑止损族：基本面/技术面/事件/主力出货止损。
v6.0止损猎杀防护(Stop-Hunting Protection)：止损位偏移1-2%防猎杀；软止损模式(到达止损位→不立即执行→进入OBSERVING观察期→收盘价<止损位→执行/收回→解除)。
v6.0止损期权定价评估(Stop-Loss as Embedded Option)：设止损=卖出隐含看跌期权→止损越紧隐含期权费越高→成本过高则换退出方式(时间止损/手动观察退出)。
v4.1突破成败策略族：压力位突破失败→止损卖出；第K次挑战失败(K≥3)→强制离场。
v6.0分批退出模式(Scaling Out)：等分退出(1/3-1/3-1/3)/倒金字塔(50%-30%-20%)/混合退出/风险驱动退出/逆向中止(第一批卖出后反弹超X%→暂停剩余批次)。
密度感知动态止盈止损：止盈位=条件PDF的75%分位数(正偏时更高/负偏时更保守)；止损位=条件PDF的5%分位数(厚尾时止损更宽/薄尾时更紧)。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 评分输出>阈值 / 突破成败信号触发 阈值: — |
| ② 消费数据/因子 | 卖出信号评分（来自 BM-SELL-03）<br>策略类型（来自 L3策略工厂）<br>ATR波动率（来自 BM-SEL-02）<br>密度PDF分位数（来自 BM-SEL-13）<br>压力位/支撑位（来自 BM-SEL-02）<br>突破成败信号（来自 BM-SELL-01） |
| ③ 参数 | 止盈位=PDF 75%分位数（范围 -，代码当前: 待实现，状态: proposed）<br>止损位=PDF 5%分位数（范围 -，代码当前: 待实现，状态: proposed）<br>止损偏移=1-2%防猎杀（范围 -，代码当前: 待实现，状态: proposed）<br>趋势策略止损=宽止损+移动（范围 -，代码当前: 待实现，状态: proposed）<br>均值回归止损=中等+固定（范围 -，代码当前: 待实现，状态: proposed）<br>高频止损=极紧（范围 -，代码当前: 待实现，状态: proposed）<br>Carry止损=极宽或无（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 评分+策略类型+波动率 → 处理: 止盈策略族+止损策略族+逻辑止损族+猎杀防护+期权定价评估 → 输出: 止盈/止损决策(部分/全部清仓) → 下游: BM-SELL-02 融合仲裁 / BM-SELL-05 置换再平衡 |
| ⑤ 代码映射 | MOD-SELL-004 / 草图§1.4 第二层（MOD-SELL-004止盈+MOD-SELL-005止损） |
| ⑥ 降级/中止 | 策略类型→止损范式映射未就绪 → 退化为固定止损范式 |

**指标文案（翻译真源 indicators_zh）**：

①触发：评分输出>阈值/突破成败信号触发；②消费：卖出评分(BM-SELL-03)+策略类型(L3)+ATR波动率(BM-SEL-02)+密度PDF分位数(BM-SEL-13)+压力位/支撑位(BM-SEL-02)+突破成败信号(BM-SELL-01)；③参数：止盈位PDF 75%分位数、止损位PDF 5%分位数、止损偏移1-2%、趋势宽/均值回归中/高频紧/Carry宽(proposed)；④数据流：评分+策略类型+波动率→止盈族+止损族+逻辑止损+猎杀防护+期权定价→止盈/止损决策→融合仲裁/置换再平衡；⑤代码：MOD-SELL-004 止盈(planned)+MOD-SELL-005 止损(planned)；⑥降级：策略类型→止损范式映射未就绪→退化为固定止损范式。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-SELL-004 | primary | planned | planned |
| depgraph | MOD-SELL-005 | supplement | planned | planned |

**有效状态**：🟧 设计态（待施工） ｜ **环节自报**：design ｜ **层**：L3 ｜ **阶段**：sell_flow

### BM-SELL-05 置换再平衡卖出 / Replacement & Rebalance Sell

> **大白话**：机会成本驱动+权重偏离驱动的被动卖出——候选池有更优标的就卖A买B，权重偏离超阈值或周五强制再平衡就调整，用倒金字塔分批退出。

**机制说明**：

§1.4 第二层置换策略族 + 组合再平衡驱动卖出 + v6.0分批退出模式。
置换策略族：机会成本驱动的卖出(卖A买B)——候选池有更优标的→置换卖出当前持仓中相对弱势的标的。
组合再平衡驱动卖出：权重偏离>阈值→被动卖出。§20.13约束13.3-13.4：组合总仓位漂移>±2%触发再平衡评估；单标的漂移>±3%触发标的级再平衡评估。再平衡执行前必须计算预期收益改善vs交易成本(佣金+滑点+冲击成本)，只有预期收益改善>2×交易成本时才执行。市场状态为⑦阴跌/⑧加速下跌/⑨恐慌崩盘时成本系数×1.5。
v6.0分批退出模式(Scaling Out Architecture)：等分退出(1/3-1/3-1/3)/倒金字塔退出(50%-30%-20%)/混合退出(止盈第一批+移动止损第二批)/风险驱动退出(按MRC减仓)/逆向中止条件(第一批卖出后价格反弹超X%→暂停剩余批次→重新评估)。批次间隔：至少1个交易日/紧迫度>0.8时可缩短至盘中。
再平衡频率(§20.3)：日频信号驱动+周频强制再平衡(每周五收盘后)。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 候选池有更优标的 / 权重偏离>阈值 / 周五强制再平衡 阈值: — |
| ② 消费数据/因子 | 候选池(更优标的)（来自 BM-SEL-21）<br>当前持仓权重（来自 BM-POS-01）<br>目标权重（来自 BM-POS-02）<br>交易成本（来自 BM-EXE-03/C-046） |
| ③ 参数 | 组合漂移阈值=±2%（范围 -，代码当前: 待实现，状态: proposed）<br>单标的漂移阈值=±3%（范围 -，代码当前: 待实现，状态: proposed）<br>再平衡收益改善=>2×交易成本（范围 -，代码当前: 待实现，状态: proposed）<br>倒金字塔减仓=20%-30%-50%（范围 -，代码当前: 待实现，状态: proposed）<br>批次间隔=1交易日（范围 -，代码当前: 待实现，状态: proposed）<br>阴跌/加速下跌/恐慌崩盘成本系数=×1.5（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 候选池+持仓权重 → 处理: 机会成本驱动置换+权重偏离再平衡+倒金字塔分批退出 → 输出: 置换/再平衡卖出清单 → 下游: BM-SELL-02 融合仲裁 → BM-POS-01 仓位调整 |
| ⑤ 代码映射 | MOD-SELL-006 / 草图§1.4 第二层（MOD-SELL-006置换+MOD-POS-004再平衡引擎） |
| ⑥ 降级/中止 | 再平衡引擎未就绪 → 仅机会成本驱动置换，跳过权重偏离再平衡 |

**指标文案（翻译真源 indicators_zh）**：

①触发：候选池有更优标的/权重偏离>阈值/周五强制再平衡；②消费：候选池(BM-SEL-21)+当前持仓权重(BM-POS-01)+目标权重(BM-POS-02)+交易成本(BM-EXE-03)；③参数：组合漂移±2%、单标的±3%、再平衡收益改善>2×成本、倒金字塔20-30-50%、批次间隔1交易日、阴跌/加速下跌/恐慌崩盘成本×1.5(proposed)；④数据流：候选池+持仓权重→机会成本置换+权重偏离再平衡+倒金字塔分批→卖出清单→融合仲裁→仓位调整；⑤代码：MOD-SELL-006 置换(planned)+MOD-POS-004 再平衡引擎(planned)；⑥降级：再平衡引擎未就绪→仅机会成本驱动置换，跳过权重偏离再平衡。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-SELL-006 | primary | planned | stable |
| depgraph | MOD-POS-004 | supplement | planned | planned |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L3 ｜ **阶段**：sell_flow

### BM-SELL-06 买卖冲突仲裁 / Buy-Sell Conflict Arbitration

> **大白话**：同一只票同时有买入和卖出信号时怎么办——卖出优先(保守原则)；做T信号遇到风控减仓/庄家出货怎么办——直接丢弃；外部指令遇到风控拦截怎么办——风控优先。

**机制说明**：

§1.4 第四层卖出信号融合与仲裁 + §16能力冲突矩阵(权威定义)。
卖出vs买入冲突仲裁：同标的有买入+卖出信号→卖出优先(保守原则)。
部分卖出vs全部清仓决策树：根据卖出紧迫度评分(紧急清仓vs从容退出)+信号强度决定。
卖出紧迫度评分：紧急清仓(黑天鹅/风控熔断)vs从容退出(机会成本/再平衡)。
§16冲突矩阵权威定义的交互规则(与§9.3重叠条目以§16为准)：
  C-004风控拦截 vs C-013外部指令→风控>用户指令，建仓被拦截→通知用户(C-004优先)；
  C-004风控拦截 vs C-031置信度→风控不可被AI否决，人类也不可撤销已执行风控动作(C-004优先)；
  C-012做T vs C-004风控→标的在风控减仓名单→做T信号直接丢弃(C-004优先)；
  C-012做T vs C-035庄家→庄家出货/弃庄阶段→做T信号自动丢弃(C-035优先)；
  流动性不足 vs C-012做T→标的流动性评分低于阈值→做T信号丢弃(流动性优先)；
  C-032资金曲线异常 vs C-004熔断→连续亏损→C-015告警→触发C-031降级(C-032→C-031)；
  相关性体制切换 vs C-004 VaR→相关性趋同→VaR置信度上调+仓位上限降低；
  体制转换预警 vs C-005多情景对策→HMM/CUSUM检测到体制转换→预案自动切换为保守型；
  密度预测尾部风险 vs C-004风控→前瞻性95%CVaR>阈值→触发风控减仓(即使历史模拟VaR未超限)；
  密度预测校准失败 vs C-004风控→尾部校准不通过→前瞻性VaR/CVaR降级为历史模拟+流动性溢价；
  密度预测偏度 vs C-031置信度→PDF偏度与信号方向相反→置信度下调15%→可能降级执行模式。


**6 件套（结构化，DB indicators JSONB）**：

| 要素 | 内容 |
|---|---|
| ① 触发条件 | 同标的同时有买入+卖出信号 / C-012做T vs 风控/庄家 / C-013 vs 风控 阈值: — |
| ② 消费数据/因子 | 买入信号（来自 BM-BUY-04）<br>卖出信号（来自 BM-SELL-03/04/05）<br>C-012做T信号（来自 BM-BUY-05）<br>C-004风控状态（来自 BM-EXE-01）<br>C-035庄家阶段（来自 BM-SEL-05）<br>C-013外部指令（来自 BM-BUY-06） |
| ③ 参数 | 买卖冲突=卖出优先(保守原则)（范围 -，代码当前: 待实现，状态: proposed）<br>C-012 vs C-004=风控优先（范围 -，代码当前: 待实现，状态: proposed）<br>C-012 vs C-035出货弃庄=做T信号丢弃（范围 -，代码当前: 待实现，状态: proposed）<br>C-013 vs C-004=风控优先（范围 -，代码当前: 待实现，状态: proposed）<br>流动性不足 vs C-012=做T信号丢弃（范围 -，代码当前: 待实现，状态: proposed） |
| ④ 数据流 | 输入: 买卖信号+做T+外部指令+风控+庄家 → 处理: 冲突检测+优先级仲裁(§16冲突矩阵权威定义) → 输出: 统一决策指令 → 下游: BM-POS-01 仓位裁决 → BM-EXE-01 风控 → BM-EXE-02 执行 |
| ⑤ 代码映射 | MOD-SELL-008 / 草图§1.4 第四层 + §16冲突矩阵 |
| ⑥ 降级/中止 | 仲裁器未就绪 → 按硬规则(卖出优先/风控优先)兜底 |

**指标文案（翻译真源 indicators_zh）**：

①触发：同标的同时有买入+卖出信号/C-012做T vs 风控庄家/C-013 vs 风控；②消费：买入信号(BM-BUY-04)+卖出信号(BM-SELL-03/04/05)+做T信号(BM-BUY-05)+风控状态(BM-EXE-01)+庄家阶段(BM-SEL-05)+外部指令(BM-BUY-06)；③参数：买卖冲突→卖出优先、C-012 vs C-004→风控优先、C-012 vs C-035出货弃庄→做T丢弃、C-013 vs C-004→风控优先、流动性不足 vs C-012→做T丢弃(proposed)；④数据流：买卖信号+做T+外部指令+风控+庄家→冲突检测+优先级仲裁(§16权威)→统一决策→仓位裁决→风控→执行；⑤代码：MOD-SELL-008 buy_sell_conflict_arbitrator(stable)；⑥降级：仲裁器未就绪→按硬规则(卖出优先/风控优先)兜底。


**锚点（环节↔模块双向关联）**：

| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |
|---|---|---|---|---|
| depgraph | MOD-SELL-008 | primary | stable | stable |

**有效状态**：🟦 运营态（已建） ｜ **环节自报**：design ｜ **层**：L3.5 ｜ **阶段**：sell_flow

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
| depgraph | MOD-MKT-003 | primary | planned | planned |
| depgraph | MOD-INF-002 | supplement | production | generated |
| candidate | CAND-AISA-001 | supplement | candidate | — |
| candidate | CAND-DAT-001 | supplement | deferred | — |

**有效状态**：🟧 设计态（待施工） ｜ **环节自报**：design ｜ **层**：L0 ｜ **阶段**：stock_selection

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
| depgraph | MOD-L02-001 | primary | production | deprecated |
| candidate | CAND-SIG-002 | supplement | deferred | — |
| candidate | CAND-FAC-001 | supplement | deferred | — |
| candidate | CAND-FAC-002 | supplement | deferred | — |
| candidate | CAND-INT-001 | supplement | deferred | — |

**有效状态**：🟥 弃用态 ｜ **环节自报**：design ｜ **层**：L1 ｜ **阶段**：stock_selection

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
| depgraph | MOD-PF-002 | primary | planned | planned |
| candidate | CAND-PFALLOC-001 | supplement | deferred | — |

**有效状态**：🟧 设计态（待施工） ｜ **环节自报**：design ｜ **层**：L3 ｜ **阶段**：stock_selection
