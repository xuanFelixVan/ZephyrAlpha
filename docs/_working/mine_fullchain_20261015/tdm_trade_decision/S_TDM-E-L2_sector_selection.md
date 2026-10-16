---
ttl: task_bound
doc_type: tdm_mining_note
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
skeleton_row: TDM-E-L2
flow: entry_flow
node_count: 29
session: mine-fullchain-tdm-20261015
---

# S_TDM-E-L2 板块选择（29 节点）

## 1. 定义

一句话：钱只去最强的地方（PT-02）——板块层总枢纽经十个子环节（强度/轮动/调整进度/板块级市场状态/水温响应/个股传导/回踩质量/生命周期/催化剂/补涨比价）产出当日板块候选池（3-5 个主攻板块）排序喂 L3 个股层。

展开：29 节点=枢纽+10 子环节+18 孙节点，盘后段为主（strength/rotation/ecology 系 postmarket），水温响应 premarket、传导放行与回踩 intraday、催化剂链 continuous。层级隔离铁律在 L2-06：只传"板块强度调节分+龙头定位"两字段给个股层，个股层不得直接引用板块买卖结论（强度传导系数封闭：10 分=+15%/6 分=+5%/<6 分=-10%，与 position_recipe_grid_schema.yaml X_sector 维 L2-06 三级放行口径一致：板块>6 ∧ 个股强度>5 ∧ 日成交>2e8 元）。骨架总纲写 30 节点、地图实读 29（漂移记录于 §4）。

## 2. 六向台账

### 2.1 输入面（有证）
- 入边：TDM-E-L1→TDM-E-L2（总闸放行）；TDM-F-C3-05→TDM-E-L2（传感器可靠度）；TDM-E-L1-AGG→TDM-E-L2-05-1（水温封顶）；TDM-E-L1-S0-1→TDM-E-L2-09-1（新闻情绪喂事件链）。
- 数据面：data_refs 在册（全图 81 节点带 data_refs 之列）；板块资金流供数挂图13-D13-19（日内五快照，骨架 §2.4 行）。

### 2.2 输出面（有证）
- 出边 29 条：L2→L3（总枢纽 sequence）；L2-06-3→L3/L3-02（强度传导）；L2-05-1→L3-06（水温→环境开关）；L2-06-2→L3-07-1（龙头→打板链）；L2-09-2→L0-02/L3-04（冲击流→偏离监控/负面否决）；L2-04→L9-V3（板块状态快照）；L2-03-1/L2-07-1→L4。
- X_sector 维（position_recipe_grid_schema.yaml line 88-99）消费 L2-01 四路子分与 L2-06 三级放行=考卷面挂接在案（phase>=3 展开、当前折叠）。

### 2.3 SSOT 真源（有证）
- config/trading_decision_map.yaml#TDM-E-L2（line 849）至 L2-10（line 1984），29 节点行号连读。
- casebooks 挂 15 处（本段最多，CASEBOOK-005#过拟合与前视 等）；goal 块各节点在册。
- position_recipe_grid_schema.yaml#X_sector（mx07-W5 施工批）=板块强度池+传导后处理考卷维真源。

### 2.4 代码模块（有证，27/29 节点 ref 实存）
- 综合件：sector_strength_aggregator.py（MOD-SIG-142）、sector_ecology_judge.py（MOD-SIG-143）、sector_conduction.py（MOD-SIG-136）。
- 分析件族（signal_ashare/sector/）：sector_analyzer/rrg/momentum/breadth/divergence/adjustment/rotation_state/siphon/gate/leader/pullback 全实存；data/sector_ranking_engine.py（MOD-L00-004）；regime/market_forecast_fusion.py（MOD-REGIME-012）；intelligence/news_chain_node_linker.py（MOD-INT-NEWS-CHAIN）+chain_impact_resolver.py（MOD-INT-CHAIN-IMPACT）。
- 无 ref 节点 2 个=TDM-E-L2（父枢纽）与 TDM-E-L2-05（水温响应中枢纽）——地图 INV-1 明文 module_ref=null=缺口节点 warning 级，两节点均为结构枢纽，子节点全有锚。

### 2.5 门禁约束（有证）
- 四门同前（MAP-ALIGNMENT/TDM-MOUNT-COVERAGE/ALGO-NOTE-SYNC/ALGO-FLOW-LINK）；本环节 12+ 节点 algo_note 带 ALGO_FLOW 出仓记（2026-09-15 批），ALGO-FLOW-LINK 锚校验覆盖面最大。

### 2.6 自动化触发（有证）
- 盘后段（01/02/03/04/06-3/08/10）随盘后批跑；premarket 段（05-1/05-2/09）挂盘前；06-1/06-2/07 系 intraday；09-1/09-2 continuous 事件驱动。
- 挂接宿主：strategy_pipeline/daily_decision_orchestrator.py（pipeline_events 挂 daily_kline SUCCESS 末棒，"调度器不是策略：只读齐→合成拍板→落库分发"）+dloop 编排链。

## 3. 自审闸三态

| 向 | 态 | 打分依据 |
|---|---|---|
| 输入面 | pass | 总闸/可靠度/水温/新闻四路入边全在册 |
| 输出面 | pass | 出边 29 条+考卷维 X_sector 挂接 |
| SSOT | pass | 29 节点行+casebooks 15 处+grid 维真源 |
| 代码模块 | pass | 27/29 实存；2 个 null 均结构枢纽（INV-1 允许，子全有锚） |
| 门禁约束 | pass | 四门+ALGO_FLOW 出仓锚最多环节 |
| 自动化触发 | pass | postmarket/premarket/intraday/continuous 四档各归位 |

**总评：pass（6/6，附漂移注记）**。

## 4. 缺口与建议

1. 骨架总纲写 L2=30 节点、地图实读 29——建议骨架下批对齐（同族漂移 L1 10→9、L3 26→25、L4 16→15、C2 6→5，疑为骨架把流根/父枢纽重复计入）。
2. L2-05 水温响应中枢纽无实现锚（两子节点有锚）——若水温三件套权重/门槛/象限参数需独立调参器，建议补挂 MOD 锚或声明 not-trading。
3. 状态矩阵无 TDM-E-L2 格（24 格挂在 L1/L4/P2/C1）——板块候选池与六段状态的联动只经 L2-05 水温档，属设计正交，建议在 L2-05 algo_note 补一句声明防误读为缺格。
