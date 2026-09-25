---
ttl: task_bound
title: L04-S3 子模块挖矿簿 · 候选池构建主链（TDM-E-L3 十五节点 → stock_candidate_pool 下游欠账）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L04
status: MINE 完成（六向封口）；本册边界=只挖"LANE-BUILD 接完之后还缺哪些下游"，不动实现码
---

# L04 · S3 候选池构建主链（L3 十五节点）

覆盖父簿 SKEL.md 的 **W2** 子块。实现侧（selection_funnel→negative_veto→aggregator 三来源接线）归 LANE-BUILD 车道，本册不重复挖实现，只挖**下游与旁路**。

**① 职责一句话**：把约 5,000 只 A 股逐阶段收敛成 10-20 只可交易候选池，并把"谁进池、为什么进、被谁否决、排第几"变成可回放的资产。

**② 现状实测**（含本册 CH 只读实测量，`ch_reader.query`）

| 项 | 实测值 | 出处 |
|---|---|---|
| 载体表存在性 | **实测：`c1_market.stock_candidate_pool` 在 CH 中已建表（system.tables 命中 1），行数 0、交易日 0（min/max 返回 1970-01-01 哨兵）** | 本册 CH 查询 |
| DDL 真源 | `schemas/categories/market/market_stock_candidate_pool.py`：16 列，`trade_date/stage/symbol(+MATERIALIZED exchange, symbol_canonical)/sleeve/...`，ReplacingMergeTree 按 (trade_date,stage,symbol) 同键替换；**PIT 消费契约明写在文件头**："决策日 T 取 max(trade_date) < T 的分区（shift(1) 防未来函数，对齐 daban_engine_load 先例）"；`calc_mode: lazy` | 文件 :25-75 本册 Read |
| 注册进 DDL 应用链 | `scripts/ch/apply_market_tables_ddl.py:474,556` 已 import 并注册目标表 | 本册 grep |
| 注册进机账 | `docs/03_modules/_cross_layer/database/business_data_categories.yaml:3172-3177` 与 `:5084-5089`（同一 category_id 出现两次，见 G6） | 本册 grep |
| 生产者 | `signal_ashare/core/candidate_pool_snapshot.py`（MOD-SIG-152，MATURITY=testing，CREATION-TOKEN `candidate-pool-snapshot-l04c01-20260925`）：`_TARGET_TABLE` :75、`POOL_INSERT_COLUMNS` 16 列 :97、`DEFAULT_STAGE: Final = "close_final"` :80-81（**pre_open/intraday_vN 仅注释预留，无产码**）、`run_pool_batch_for_day` | 本册 grep |
| 注入源现状 | `_BUNDLE_SOURCES: list[PoolBundleSource] = []`（:251）；全仓 grep `register_pool_bundle_source` **只有生产者文件自身的 3 处注记/文档，无任何注册调用点** → 契约"无注册源=空池如实缺省"当前生效 = **触发一次即写零行** | 本册 grep（:8,:34,:36,:251） |
| 生产触发面 | **已从"无"升为"有侧带"**：`strategy_pipeline/daily_gate_snapshot.py:290-317` `_collect_candidate_pool`（docstring 自称"LK-04 通电侧带（L04-C02 最小侵入）"，独立 try/except fail-open，异常折 `status=absent`）在 :418 `collect_gate_snapshot` 内被调（:420 传 switches）；上游 `daily_decision_orchestrator.py:75,688` 驱动 `collect_gate_snapshot(day, market_state, reader)` | 本册 grep/Read |
| 调度注册 | `src/zephyr/data/config/tasks.yaml` grep `daily_gate\|candidate\|gate_snapshot` **零命中** → 触发面不在数据采集批里（属策略侧日循环），本册未追到 AutoRuntime 内的调用注册点（长尾 T1） | 本册 grep |
| Tier 维护腿 | `pool_tier_maintenance.py`（MOD-SIG-139）外部引用实测仅 `signal_ashare/__init__.py:124`（导出面）+ 聚合器注记 :7/:10/:35/:204 → **无生产调用方**，故 DDL `tier_slot` 注记"未接线恒 NULL，不硬凑" | 本册 grep |
| 读方（消费侧） | 全仓 grep `stock_candidate_pool` 命中集 = 生产者 + 门快照采集 + DDL/apply 脚本 + 机账 yaml → **SELECT 该表的消费码 0 处**（L4 买卖 / P2-02 做T调度 / P1 体检 / BM-BUY-03 / 整装回测均未接，与生产者头注 :5 自述一致） | 本册 grep |
| 上游原料表 | 文档基线（SKEL W2②）：dragon_tiger_seat 4.5 年 / money_flow 六年 / limit_up_pool 54 日 / limit_up_down 49 日（DU-14）/ auction_snapshot+auction_book（DS-082）；本册未机测 | 12 号文 §1.2 基线 |

**③ 六向台账**

| 向 | 发现（内部反查 ＋ 全网搜索） |
|---|---|
| ①上游该喂什么 | 内部：主链输入契约在码上齐（三来源注入 `PoolCandidateInput`，聚合器 `from_dual_pool_entry` :148、`from_fine_scored_entry` :159 两个鸭型镜像构造器**已在**，等上游 producer 调用）——即"上游该喂什么"已定，缺的是**谁喂**：dual_pool（selection_funnel/双池评分）与 strategy_chain（三 sleeve）两个注入源均无注册者；此外 S1 的 `conduction_adj`、S5 的可交易预检结论、L01 的 regime dominant 三项都只进 `snapshot_meta` 作"来源标尺"，不参与池成员判定（快照元自足设计，文件头 :48 附近）。外部：已查无（查法：漏斗入口的"该喂什么"属仓内契约问题，业界表述为 feature/universe 定义，无独立方法论可引；SKEL §4 已引 qlib Alpha158/360 作因子面参照，沿用） |
| ②下游该喂谁 | 内部：载体有了、**读方 0**（实测）→ 净新增缺口 G1；已登记但未接的四类下游= TDM-E-L4 买卖执行、P2-02 做T调度标的、P1 持仓体检、BM-BUY-03 决策编排，加整装回测（framework_composer）；DDL 已为回放留好 `pool_rank`（"喂 L4 只取未否决顺位前段的重放依据"）与 `vetoed 沉底照写`；`stage` 列设计支持 pre_open/intraday_vN，即**日内动态选股（L3-11）下游位在建但未产**（G4）。外部：池→执行的下游范式=排名制组合再平衡（TopK-Dropout，qlib，SKEL §4 已入图，沿用） |
| ③算法/机制业界学界 | 内部：聚合器纯函数核（430 行零 IO）已锁"容量 10-20/去重确定序/否决只标记不剔除"（SKEL W2② 基线）+ `_priority_key` :262 顺位键；Tier 升降剔状态机（165 行）。外部（换池=排序+匹配带换手约束是标准提法，两独立源）：《Optimizing portfolio selection through stock ranking and matching》Expert Systems with Applications（Elsevier，2025-04-15）https://www.sciencedirect.com/science/article/abs/pii/S0957417425000521 ；《Deep Reinforcement Learning for Optimal Portfolio Allocation》arXiv（2026-02-19）https://arxiv.org/html/2602.17098v1 （后者为综述性提法，含交易成本/换手约束下的换池决策）。**A 股适配闸**：两源均以日频连续可调仓为前提，本仓 T+1 + 涨跌停 → 换池只能盘后定、次日执行且涨停池成员可能买不进（现役 `vetoed 沉底照写` 与 `pool_rank` 前段重放正好兼容该约束，无需改造；需在 L4 侧补"池内但不可成交"降级路径，归 S5 可交易预检）。**本册判：现役 L3-05/L3-09 设计（顺位+Tier 升降剔+容量 10-20）与外部范式同构，无返工必要，缺的只是"跑起来+被读"** |
| ④后端代码缺什么 | 内部：缺四件——(a) **注入源生产者**（dual_pool/strategy_chain 两个 `PoolBundleSource` 实现 + 注册动作，属 LANE-BUILD 本批）；(b) **读门面**：无任何 `SELECT c1_market.stock_candidate_pool` 消费码，PIT shift(1) 契约只写在 DDL 注释里，**没有代码强制**（镜像 S2-G1 同类病灶，L01-S10-G1"状态读门面缺失"同族）→ 各下游若各自手写 SQL 会把"未来函数"重复发明 N 遍；(c) **池史盘点/哨兵**：表 0 行这件事没有任何机查（无"连续 N 日零行=告警"的 fail-visible 面，生产者只在批内 warning，事后无人知）；(d) `apply_market_tables_ddl.py` 与机账 yaml 双写已落，但 `business_data_categories.yaml` 内 `market_stock_candidate_pool` **出现两次（:3172 与 :5084）** → 机账重复条目。外部：已查无（查法：以"candidate pool persistence pattern open source"检索，开源侧无同名概念件；qlib 用 pickle/dataset 不落库，不构成可复用实现） |
| ⑤前端怎么呈现（只登记） | 内部：池快照的**人工面=零**（无看板、无日报消费该表；本册 grep 未命中任何 frontend 资产）；`snapshot_meta` 单表回放自足的设计意图（免 join 复原当日上下文）正是为"自动化体检/审计面板"备料。外部：已查无（查法：呈现惯例=榜单型，与 S1 龙头榜同类，无外部争议可引） |
| ⑥数据字段有没有 | 内部逐列核对 16 列：**在表**=trade_date/stage/symbol/exchange/symbol_canonical/sleeve/sleeves/rank_score/pool_rank/vetoed/veto_reasons/tier_slot/conduction_adj/score_components/snapshot_meta/version/data_source；**有列无值**=tier_slot（Tier 未接）、conduction_adj（W0 未接）、score_components（v1 由调用方注入，缺省 `{}`）→ 三列是"schema 先行、真值待接"的显式缺省（合规：禁拍假值冒充）；**缺列**=无"入池/出池事件"腿（只有快照行，池变更要靠两日快照差分自算，L3-09 的"Tier 归属变更流"在 SKEL W7③ 是需求但本表未建）→ G5；无 `universe_size`/漏斗各阶段存活数（压缩率无法从本表回放，漏斗阶段计数只在回测内存里）→ G7。外部：字段口径=业界"portfolio holding snapshot + turnover log"两件套，本仓只有前件 |

**④ 缺口清单**（沿用 L04-Cxx／LK-xx／Dxx／DU-xx；新缺口续编并注"册内未见"）

| 编号 | 内容 | 状态 |
|---|---|---|
| L04-C01/C02（既有） | 载体补建 + 生产挂点 | 本册**改判**：载体与挂点侧带均已落地（表在 CH、`_collect_candidate_pool` 在产链、DDL 已入 apply），**未完项从"建"转为"喂真值 + 被读"**；C02 的"实现接线"归 LANE-BUILD |
| LK-04（既有） | L3 生产挂点缺失 | 由 ✗ 改 🟡：挂点在、池为空（无源=零行） |
| D22/M-41（既有） | 池成员持久化载体 | 载体已建，建议销账为"已落地待验收（连续 10 交易日有真值行）" |
| D19/D21/DU-03/DU-14（既有） | Universe 剔除字段浅史 / 流通股本 / margin_trading 断 4 日 / 涨跌停浅史群 | 沿用（SKEL W2⑥） |
| CNS-10/CNS-11（既有） | 次新过滤接线 / 竞价强度因子 | 沿用（归 S5 与日内腿） |
| **L04-S3-G1** | 载体读方 0：无 PIT 读门面、四类下游全未接——**册内未见**（SKEL 只记"下游吃不到真值"，未记"连读码都不存在"） | 新登 |
| **L04-S3-G2** | 注入源未注册（`_BUNDLE_SOURCES` 空）→ 通电后表恒 0 行，"死表风险"从假设变为实测 | 新登（与 LANE-BUILD 交接边界：本册只登记，不施工） |
| **L04-S3-G3** | 零行无哨兵：表 0 行/池空日没有任何机查面（连续零行=静默）——**册内未见** | 新登 |
| **L04-S3-G4** | `stage` 只产 `close_final`，`pre_open/intraday_vN` 无产码 → L3-11 日内动态选股池快照腿缺（竞价腿 auction_snapshot/auction_book 数据在、无池产物） | 新登 |
| **L04-S3-G5** | 池成员变更流（入池/出池/Tier 升降）无事件表，L3-09 需求（SKEL W7③）只能靠两日快照差分自算——**册内未见** | 新登 |
| **L04-S3-G6** | 机账 `business_data_categories.yaml` 同一 category_id 重复两条（:3172 / :5084）——**册内未见** | 新登 |
| **L04-S3-G7** | 漏斗各阶段存活数/压缩率未随池落库（九阶段漏斗在回测内存，生产侧无"当日各阶段剩多少"史）→ 漏斗参数漂移不可归因——**册内未见** | 新登 |
| **L04-S3-G8** | 挂点归属未定：`daily_gate_snapshot` 不在 tasks.yaml、由策略侧编排器驱动，本册未追到 AutoRuntime 事件登记点 → "挂点是否存在于生产日循环"仍不能打勾（长尾 T1） | 新登（待核类，禁提前判"缺"或"有"） |

**⑤ 自审闸三态裁定**

| 项 | 裁定 | 理由（量尺=终局全貌） |
|---|---|---|
| G1 读门面 + 下游接线 | **施工（本环节头号新施工项，建议编 L04-C09）** | 载体无人读=资产零收益；一个 PIT 读门面件（`shift(1)` 强制、返回当日池快照）同时消灭"每个下游自己发明取法"的人工核对，主判据一票放行；与 L04-C02 实现批串行（源先于读） |
| G2 注入源 | **挂起排期（等 LANE-BUILD）** | 已授权他车道施工中，本簿禁重复施工（连坐纪律 §3.4）；解锁条件=LANE-BUILD 落地后由本簿复核"首行真值日" |
| G3 零行哨兵 | **施工** | 终局=无人值守，0 行日必须由机器发现；复用既有数据哨兵框架（12 号文 DU 面），不新建子系统 |
| G4 日内 stage | **挂起排期** | 解锁条件=盘中事件通道有主（同 S1-G3）+ L3-11 竞价腿消费方立项；终局要（日内动态选股是本环节不可少的一段），非封矿 |
| G5 变更流事件表 | **挂起排期** | 解锁条件=C01 累计 ≥20 交易日真值（事件表可由快照差分回填，先建表=空表；差分脚本可作一次性探路降级） |
| G6 机账重复 | **施工 P3（顺手）** | 纯登记一致性，单条删除 |
| G7 漏斗阶段存活数 | **施工（并入 G1 门面批的列扩展，不另立表）** | 压缩率是漏斗参数唯一可归因面；净零声明：不新建表，`snapshot_meta` 内加 `funnel_survivors` 逐阶段 dict 即可 |
| G8 挂点归属 | **待核（非三态，属挖矿未尽项）** | 见长尾 T1，禁在本册下结论 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | signal/noise 与归因 |
|---|---|---|---|
| R1 | 内部：注入源/表读方/DDL 列 | signal | `_BUNDLE_SOURCES=[]` 无注册点、SELECT 消费码 0、16 列三列无值 |
| R2 | 内部：stage/tier 接线 + CH 实测表存在性与行数 | signal | 表已建、0 行；DEFAULT_STAGE 仅 close_final |
| R3 | 内部：触发链（gate_snapshot → orchestrator）+ tasks.yaml 反查 | signal（部分） | 侧带在、调度登记未追到 → G8 待核 |
| R4 | 外部：换池/池维护算法（RL ranking-matching）1 轮 | signal | 两独立源（ESIWA 2025 / arXiv 2026-02）；本册 noise 归因=检索命中含大量通用 RL 组合分配论文（无换池语义），已按闸 1/2 剔除 xueshu.baidu 聚合页（无原始发布方与年份，不可溯） |
| R5 | 外部：开源池持久化范式 | 已查无（查法见 §④行） | 记档 |

**长尾（本册调研未尽，明确列出）**
- T1 AutoRuntime 生产日循环是否真的调 `collect_gate_snapshot`（须查 `zephyr.trading` 事件登记/工作流装配点），决定 G8 与 LK-04 的最终勾。
- T2 九阶段漏斗 `selection_funnel.py` 逐阶段阈值与 YAML L3-02 对表（父簿 SKEL §0 已列 24/25 号 detail 文档未读，本册未补读，属施工级余量）。
- T3 三 sleeve（daban/multifactor/event_driven）各自候选产出的可用性——归 sleeve 车道，本册只登记边界不越界。

**本册封矿判据自评**：六向已填（含三处"已查无+查法"），T1-T3 未清空 → **状态=MINING（长尾在册）**。
