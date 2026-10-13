---
ttl: task_bound
title: TDM 挂接清单环节册——§7.5 三线接口逐线挖＋c1_market.emotion_index 消费节点缺口＋unrouted fail-closed
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: TDM 挂接清单环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# TDM 挂接清单环节册（研究档 §7.5 三线契约→TDM 节点落位；§11.2"挂接不闭合"治本）

> 判定基准（研究档 §11）：TDM 大位置正确（矩阵列轴/总闸上游/四层温度计/传感器阵列/词汇收编机制在册），三处要修=①两套日级温度计并存（Q10，依赖补登裁定）②挂接不闭合（本册主体）③unrouted 日预算带空洞（Q12）。

## §1 逐项台账表（三线接口＋缺口件）

| 件名 | 仓内真源路径:行号 | 现状 | 消费方 | 缺口 | 六向定位 |
|---|---|---|---|---|---|
| 线 3（现状最好）：情绪**相位**→预算带 | config/trading_decision_map.yaml:400（总闸 TDM-E-L1 消费六段预算带："吸筹 30-50%/点火 50-70%/扩张 60-80%/亢奋封顶 30% 只卖不买"，月定大档日微调+R-055a fail-closed 地板 0.30） | ✅（在用） | 总闸 L1 输出当日总仓位上限 | 无（相位线现状=已在产；预算带数值调整=语义参数 Owner 门） | ①t0 六段物化 ②总闸 ③查表 ④在产 ⑤— ⑥六段标签 |
| unrouted 日预算带口径（Q12） | 六段 41.9% 不路由（unrouted 762 日，D 族冻结稿:49；未冻点 3.1 :55） | ⬜（无段日总闸口径未写） | 总闸 | **fail-closed 建议待批**：无段日按次谨慎档（与 R-055a"缺数落地板值"同精神——研究档 Q12 建议） | ①六段物化 unrouted ②总闸 ③谨慎档查表 ④待批 ⑤— ⑥— |
| 线 2：情绪**温度**→考试条件轴 | 立法在册=condition_package.py（MOD-BT-COND-PACKAGE，Owner 2026-09-23 夜裁①）：头部契约"统计可用层=情绪档×大盘状态（两轴全史）"；情绪值消费 c1_market.emotion_index v0.1.0 冻结公式；灰度五档 (0.2,0.4,0.6,0.8)；30 日地板；闭卷窗 [2019-01-04,2025-09-09]；状态轴选族 F4_BDI_MOMENTUM_Z20 | ✅（条件轴在产，GPU 网格输入包） | factory_grid_executor/f06_e4_wfa_exam/GPU 点火验收 | TDM 地图节点缺：condition_package 是 D_BACKTEST 域件，**trading_decision_map.yaml 无对应消费节点/data_refs 挂载**——地图面"条件轴在哪"不可见 | ①emotion_index+alt_regime ②考试族 ③条件胞 ④在产 ⑤— ⑥两轴列名不同名坑（signal_date vs trade_date 在册） |
| c1_market.emotion_index 表消费节点缺口 | 表生产=internal_compute_provider.py:766-767/:1735-1740（capability 路由）+:300（_TBL_EMOTION_INDEX）；**仓内真实消费方**=condition_package（冻结公式）、sector_state_pipeline.py:59/:109（板块偏好重映射）、emotion_index_replay、快照器 | ✅（表有消费方）🔨（TDM 地图零节点） | 见左 | **精确缺口**：非"表零消费"而是 **TDM 地图无节点**——S5/A 阵列/条件轴节点均未挂 data_refs 指向该表（研究档 §11.2-2"c1_market.emotion_index 表无 TDM 消费节点"实况精化） | ①builder 日批 ②条件轴/板块管线 ③— ④地图挂载缺 ⑤— ⑥8 列 schema |
| 线 1（主接口）：情绪**事件**→形态拐点确认器 | 候选挂位 A=entry_flow 传感器阵列 S6（新，Q14 选项一）；候选挂位 B=并入 S3（TDM:512-528，sensor/盘前，module_ref=lhb_premium_analyzer，data_refs [DS-082, DS-107]）；事件件=099/101（:7 均 testing 无消费方） | ⬜（两案待裁 Q14） | 大盘班拐点确认器（跨班接口） | 挂位裁决+边定义（事件节点→大盘班主接口节点的 payload_type/lag/pit_proof）；S6 新开 vs 并 S3 的净零权衡 | ①099/101 ②拐点确认器 ③事件离散面 ④待建节点 ⑤— ⑥事件表 |
| MOD-SIG-025 两下游接线 | market_sentiment_analyzer.py:5（CONSUMERS 自记"经 2026-09-05 AI-08 审计实证未接线——接线待排期"）：youzi_relay_emotion_engine、dual_engine_fusion_decision_engine | 🔨（production 件悬空待接） | 两候选下游（youzi 路继情绪/双引擎融合） | 接线排期（研究档 §6 消费层缺口）；接线时跨引擎传值必须经词表映射册 E2/E3 方向注记（2_L2 §2-1） | ①七维分数+灰度 ②youzi/融合 ③— ④接线待排 ⑤— ⑥— |
| S5 与 emotion_index 并存映射（Q10） | TDM:650（TDM-E-L1-S5 节点）+:575（11 信号 A1-A8/B1-B3）+:735（D20 水温解挂"日级温度计独立判定 5 档"）+S5 出边 :6187-6190（→L2-05-1/L1-AGG/L0-04）；emotion_index=六成分灰度 | 🔨（两套并存，分层依据悬空） | S5→L2-05-1/L1-AGG/L0-04（在册边） | **Q10 依据悬空**："温度计≠档位计"在册裁定不存在（#400 撞号）——P1 先补登真裁定，再定 A 分层并存互映射（建议）或 B 归一 | ①11 信号+六成分 ②AGG/L2-05-1 ③档 vs 灰度分层 ④待裁定 ⑤— ⑥同源指标冗余裁噪已预留（:580 相关性去重） |
| 相位→预算带的 unrouted 之外：S3 事件化挂边 | TDM:6171（S3→L1-AGG feed 在册）+:6174/:6259（S1↔S3 feedback） | ✅（S3 边在册） | L1-AGG | E4 事件化后的新边（S3 或 S6→拐点确认器）与既有边并存性检查 | ①S3 ②AGG ③— ④E4 事件边待建 ⑤— ⑥— |
| 新闻情绪线（S0-1） | TDM:619-634（TDM-E-L1-S0-1"新闻情绪语义分析"，parent_node=S0，:631"输出市场级+板块级情绪读数，喂 L1-S0 宏观判定与 L2-09 事件链"）+:6192（S0→AGG 边） | ✅（在册） | L1-S0、L2-09 | C6 升级（LLM 打分）走此节点，勿新开 | ①news 表 ②S0/L2-09 ③本地模型打分 ④在产 ⑤— ⑥market_news_sentiment_window |

## §2 与既有资产边界

1. **三线分契约禁混一线**（研究档 §7.5）：线 1 事件（离散确认器）/线 2 温度（条件轴一根轴）/线 3 相位（预算带）——三条各自的 TDM 落位独立设计，禁"一个情绪节点包打三条线"（那会重演两套温度计并存的纠缠）。
2. **vs S5 的 11 信号**：S5 已含 A3 炸板率/A5 昨日涨停溢价（:576-577）——E4/E5 事件化时**原料同源**（:579-580"原始数据与 S2/S3 同源，用法不同：本节点消费当日读数+环比骤变"）——事件件读 S5 同源数据但不经 S5 节点（事件是离散触发，禁把传感器节点改造成事件路由器）。
3. **vs D125 折算通道**：策略路由 F-C1-01（config:4369）已消费 state_matrix 6 态查表——线 3 的 unrouted fail-closed 是总闸面（L1）不是路由面（F-C1），两个 unrouted 口径（D 族冻结稿 3.1 建议保持不路由+卡面单列）不冲突：总闸按谨慎档兜底，路由按 bucket 单列。
4. **vs sector_state_pipeline**：它消费 emotion_index 是板块域内部管线（:10-11 防循环禁回灌），**不算 TDM 挂接**——TDM 节点挂载是地图面新增 data_refs/module_ref，两事并行不互代。
5. **vs 大盘班接口**：线 1 的对端节点=大盘班"形态拐点信号"侧（formreg 班）——挂边落谁的 yaml 由 Q7 两班各挂互引件定（建议=输出侧挂边、消费侧挂引），本册只钉情绪侧挂位。

## §3 施工要点（实读代码的坑）

1. **挂节点的净零申报**：新增 S6（若 Q14 选 A）须按宪法 §4 全资产净零声明替代/合并对象（候选=S3 的 E4 语义上收+099/101 接线位）；若选 B（并入 S3）则零新节点，代价是 S3 的 casebook（CASEBOOK-001#outage）面变宽须同步注记。
2. **边定义三字段**：TDM edges 惯例 payload_type/frequency/lag/pit_proof（:6171/:6187-6190 同款）——事件边建议 {payload_type: event, frequency: daily, lag: "0d"（盘后 15:10 可得）, pit_proof: 待红蓝}; 相位线现有边 pit_proof=legacy-unaudited（:6187）——挂接施工**禁给新边抄 legacy-unaudited**（新边必须自带 PIT 断言，t0 物化件红蓝 PIT 断言先例）。
3. **地图缺口的表述纪律**：条件轴节点补挂时 data_refs 用既有 DS 编号（禁新造 DS-id；emotion_index 表若无可引 DS-id 则走"表真源路径注记"惯例——施工班查 data_source_registry 后定）。
4. **025 接线的方向注记**：两下游 youzi（EmotionPhase 4+1）与 dual_engine_fusion 跨引擎传值必须经映射册 E2/E3 行（最热→RETREATING vs 最热→MANIA 方向陷阱，2_L2 §3-2）——接线 PR 必带映射层，禁直传 sentiment_phase 字面量。
5. **S5 互映射（若 Q10 选 A）**：映射表落位候选=market_state.py 常量区（SH-VOCAB-001 同款，state_vocabulary_registry 同步登记）——禁散落 config 各处；映射=语义参数=Owner 门。
6. **unrouted fail-closed 的落地形态**：总闸 algo_note（:400）追加一句"无段日按次谨慎档"即可（语义变更走 Owner 批），禁新开 fallback 节点——口径与 R-055a 地板值 0.30 的关系（谨慎档 vs 地板值）在呈批包写明，防双兜底打架。
7. **测试红线**：车道内跑 TDM yaml 变更类测试须带仓外 --basetemp（宪法 §9.6）；挂接施工本身是 config+src 改动，走施工班（本车道零改动）。

## §4 自审闸三态裁定

**裁定=施工（挂接清单落 yaml，待 P1 呈批后执行）**。理由：
- 主判据：挂接不闭合=契约停在纸面（研究档 §11.2-2 明断）——把三线落成 TDM 节点/边/预算带口径，消灭"地图上找不到情绪"的人工解释环节，终局必需。
- 时序：全部挂接动作**呈批前置**——Q10（补登裁定）/Q12（fail-closed）/Q14（S6 vs S3）三项未裁前零落地；裁后施工量小（yaml 挂载+025 接线+边定义）。
- **分线三态**：线 3 相位→预算带=✅ 在用（仅 unrouted 口径补句待批）；线 2 温度→条件轴=件在产仅地图挂载（纯机械，裁后即施）；线 1 事件→确认器=⬜ 主缺口（Q14 挂位+099/101 接线+边定义，依赖 3_L3 先发波）。
- 反驳者一问：①"是否过度挂接？"——三线各有独立消费方（总闸/考试/拐点确认器），无一线是装饰；最小施工面=线 2 挂载+线 1 接线，零新计算件；②"是否与大盘班抢边？"——Q7 互引件机制在案，输出侧挂边消费侧挂引，无双真源。
- 挂起面：Q10 分层映射的映射表本体（依赖补登裁定）；S5 归一案（B 选项）整体不动（D20 定稿面大，建议 A）。
- 封矿面：无。
