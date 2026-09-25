---
ttl: task_bound
doc_type: log
title: L04-S6 子模块挖矿簿 · 个股状态轴物化与条件概率面（载体史深/概率表范式/回补可达性）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L04
status: MINE 完成（六向封口；本册含对 LK-05/C07 立项口径的实测改判）
---

# L04 · S6 个股状态轴物化 + 条件概率面

覆盖父簿 SKEL.md 的 **W7** 子块（M-41/D22 载体 ⊕ LK-05 概率表）。与 S3 的分工：S3 挖"链与下游"，本册挖"状态轴本身的历史深度、概率面方法论与回补可达性"。

**① 职责一句话**：让"某日某股在池内的身份与分数"成为可回放的史，并在此之上把"板块状态→个股 T+1 收益分布"变成机器算得出的条件概率。

**② 现状实测**

| 项 | 实测值 | 出处 |
|---|---|---|
| 载体 | `c1_market.stock_candidate_pool` **实测：表已建、行数 0**（父簿 S3 同测复核）→ 本环节"状态真值全史 ✗"由推测升为**实测零史** | 本册/ S3 CH 查询 |
| 池 PIT 契约 | DDL 文件头明写"决策日 T 取 max(trade_date) < T 的分区（shift(1) 防未来函数，对齐 daban_engine_load 先例）"——**仅注释承载，无读码、无单测钉住**（全仓 grep 无 SELECT 该表） | `schemas/categories/market/market_stock_candidate_pool.py` 头注 + 本册 grep |
| 仓内先例①（父簿所指） | `c1_market.daban_engine_load` **实测 1,453 行 / 2026-09-01..2026-09-22 / uniqExact(trade_date)=16**，查询日 2026-09-26 → **尾巴断了 2-4 个自然日、史深仅 16 个交易日**；生产触发=`tasks.yaml:3422 daban_engine_load_daily`（source=internal，`schedule: daily_kline`，incremental=true，DAG 前置四件 `daban_board_event_derive/index_quote_snapshot/kline_index_incremental/market_breadth_snapshot_minute`，:3424-3428）；生产者 `ex_core/daban_load_producer.py` 头注 :4-:8（MATURITY=**testing**，INVARIANTS"事件驱动非周期…批产生产者"） | 本册 CH + tasks.yaml + grep |
| 仓内先例②（**父簿未登记，本册净新增**） | `c1_market.market_pattern_win_rate` **实测 4,239 行**，列=`pattern_id/timeframe/regime_tag/direction/fwd_window/n_events/hit_rate/avg_fwd_ret/low_sample/updated_at` → **仓内早已存在一张"格子×样本数×命中率×前视均收益×低样本标记"的条件概率表面**，且带 `regime_tag` 状态轴与 `fwd_window` 前视窗 | 本册 CH 实测（`system.columns` + 行数） |
| 其生产腿（在产） | `tasks.yaml:3370-3381 pattern_win_rate_materialize`（MOD-SIG-145/JOB-108）：`dependencies: ["pattern_event_incremental"]` 事件触发 DAG 尾部重物化，描述"market_pattern_event × kline_daily 前视窗口命中率，(pattern_id,timeframe,regime,direction,fwd_window) 粒度 + **baseline 对照**；ReplacingMergeTree(updated_at) 全量重放幂等；喂 `pattern_win_rate_provider`/MOD-SIG-115" | 本册 tasks.yaml + grep |
| 读方 | `src/zephyr/signal_ashare/strategy_signal/pattern_win_rate_provider.py`（MOD-SIG-115）等 strategy_signal 家族 6 件（scanner/pattern_event_job/pattern_event_store/pattern_evidence_certifier/pattern_signal_runtime）→ 该概率表**有真读方**，是完整闭环先例 | 本册 grep |
| 个股层概率表（本环节需求） | **实测：CH 内不存在任何"板块状态×传导分×池层 → 个股 T+1 收益分布"的表**（`name ILIKE '%prob%'` 无命中，`%win_rate%` 仅上表）→ LK-05"空白"判语成立，但**"未立项"改判为"范式已在库、缺的是换条件轴"** | 本册 CH 实测 |
| 上游状态输入可用性 | L01 侧 regime 快照有 run 台账问题（L01-S6-G1 净登 5 run 谁作正身）；L03 侧 sector_state 实测 426,985 行/729 板块/2022-09-01..2026-09-24（S2 册实测）→ **板块状态腿史深 4 年可用，个股池腿史深 0 天**，两腿差距 4 年=条件概率表当前不可算的唯一硬因 | 本册 S2 实测 + L01 册 |

**③ 六向台账**

| 向 | 发现（内部反查 ＋ 全网搜索） |
|---|---|
| ①上游该喂什么 | 内部：概率表四元组的输入端，本环节能凑齐的三个轴=板块状态（sector_state，4 年史）、传导调节分（S1，**无值**）、池层/Tier（S3，**无史**）→ 结论：**四元组里两个轴是零史**，任何"先建表后填数"的尝试都会得到空表；此外 `regime_tag`（L01）与 `direction`（做T方向，L05）是现成范式里存在、本环节尚未声明的可选条件轴。外部：已查无（查法：以"conditional return distribution given sector state"主题检索，命中的是行业动量溢出类（已在 S1 册入图），无同名"条件收益分布表"的标准提法，不臆造外部定论） |
| ②下游该喂谁 | 内部：概率面的下游=①L04-C07 考试卡（预注册）②仓位/预算层（P1-T2 排名持续性同族消费）③BM-BUY-03 决策编排（要的是"P(涨｜状态)"而非点位）④整装回测的胜率基线；**注意 `market_pattern_win_rate` 的 `baseline` 对照设计正缺本环节对等物**——若无 baseline，"板块强势时个股胜率高"可能被"整市上涨期胜率高"混淆（条件概率表的经典混淆=无条件基准未剥离）。外部：已查无（查法：概率表→执行的下游语义无外部方法论争议，属本仓地图接线义务） |
| ③算法/机制业界学界 | 内部：**复用现成范式即最优解**（`pattern_win_rate_materialize` 的五元组 + n_events + low_sample + baseline + 全量重放幂等 = 已解决"格子化、低样本、基准、幂等"四件事，比父簿为 C07 引的"P1 表四元组 + 17 号文格子四元组 n≥30/Wilson LB"更近、已在产、有机读列）。外部（小样本格子估计要收缩/经验贝叶斯——本册**仅登记题录，不据此入图**）：《Empirical Bayes Shrinkage Calculator》metricgate 工程文档（2025-03-12 https://metricgate.com/docs/empirical-bayes-shrinkage/ ）与《如何对 Beta 因子进行稳健估计?》星火多因子专题报告 10（2020，quant-wiki 镜像 PDF https://asset.quant-wiki.com/pdf/%E6%98%9F%E7%81%AB%E5%A4%9A%E5%9B%A0%E5%AD%90%E4%B8%93%E9%A2%98%E6%8A%A5%E5%91%8A10%EF%BC%9A%E5%A6%82%E4%BD%95%E5%AF%B9Beta%E5%9B%A0%E5%AD%90%E8%BF%9B%E8%A1%8C%E7%A8%B3%E5%81%A5%E4%BC%B0%E8%AE%A1%EF%BC%9F.pdf ）→ 两源一是工具站一是镜像题录（原发布方/年份待核），按闸 1/闸 2 标 **待验证不入图**；本册结论改由**内部实证**承载（现役 `low_sample` 列即该问题的仓内处方）。**A 股适配闸**：胜率格子的前视窗须按 T+1 + 涨跌停不可成交日剔除（`fwd_window` 列已有，但"涨停日不可买"的剔除规则属 S5 域，须在同一格子口径内声明，否则胜率虚高——本册登记为 C07 预注册卡的必含条款） |
| ④后端代码缺什么 | 内部缺三件——(a) 池史本身（S3-G2 注入源，他车道在途）；(b) **零史期的替代路径未立**：可先用"回测侧逐日现算 + 落同一张表（标 `data_source='replay'`）"把 2026 年史补出来（回测已能跑通 L3 链），当前**无任何代码做这件事**，DDL 也预留了 `version`/`data_source` 两列 → 净新增缺口 G3；(c) 概率表计算件（C07）无归属包——现成同类件在 `signal_ashare/strategy_signal/`（MOD-SIG-145 家族），父簿 C07 未指定复用该包，容易另起炉灶（G4）。外部：已查无（查法：以"open source conditional win rate table ClickHouse"检索无可复用件；qlib 的 report 层是回测输出非库内史，SKEL §4 已判） |
| ⑤前端怎么呈现（只登记） | 内部：`pattern_win_rate_provider` 的胜率已被 `frontend/dashboard/api_server.py` 侧引用（grep 命中 `win_rate` 字样）→ 概率面**已有呈现先例可借**（形态胜率卡），个股传导概率上线时复用同一卡型即可，登记不施工。外部：已查无（查法：胜率/概率呈现=格子热力图惯例，无争议） |
| ⑥数据字段有没有 | 内部逐字段：池快照 16 列**全在但全空**（史深 0）；概率表所需 `fwd_ret`（个股前视收益）→ kline_daily 可算 ✓；`sector_strength`（条件轴一）→ L03 表在、注入腿缺（S1-G2）✗；`conduction_adj`（条件轴二）→ 列在值无 ✗；`pool_rank/tier_slot`（条件轴三）→ 列在值无 ✗；`baseline` 对照组 ✓范式在（现役胜率件已含）；`low_sample`/`n_events` ✓范式在。**质量画像**：唯一"字段+值双全"的条件轴是板块状态（4 年），其余三轴值史=0 → 本环节的"数据有没有"答案是**分轴而异**，不可整体打 ✓/✗ |

**④ 缺口清单**（沿用 L04-Cxx／LK-xx／M-xx；新缺口续编并注"册内未见"）

| 编号 | 内容 | 状态 |
|---|---|---|
| M-41/D22（既有） | 池成员持久化载体 | 本册改判：载体已建（S3 实测），**"史深 0"是本册新量化**（0 行） |
| LK-05（既有） | 个股层状态轴物化与概率表空白 | 本册改判：概率表**范式不空白**（`market_pattern_win_rate` 4,239 行在产，五元组+low_sample+baseline），空白的是**本环节的条件轴取值**；C07 措辞应从"立项"改"复用换轴" |
| L04-C07（既有） | 个股层状态轴概率表立项 | 沿用；本册补两条硬约束（①前视窗须剔涨停不可成交日 ②格子必含 baseline 对照） |
| **L04-S6-G1** | **被复用的先例本身在断更**：`daban_engine_load` 实测止 2026-09-22、史深仅 16 交易日、MATURITY=testing → "复用 daban 模式即零新调度器"这一父簿判语的隐含前提（先例健康）**未验**，新表可能继承同一断尾病——**册内未见** | 新登 |
| **L04-S6-G2** | 状态轴史深不对称（板块腿 4 年 vs 池腿 0 日）→ 概率表最早可算日=池表首行日+120 交易日，**该日历约束在任何册子里未写**，导致 C07 排期无锚——**册内未见** | 新登 |
| **L04-S6-G3** | 零史期无回补路径：回测侧已能逐日跑通 L3 链，却无"以 `data_source='replay'` 回补池史"的件；DDL 已留 version/data_source 两列而无人用——**册内未见** | 新登 |
| **L04-S6-G4** | 概率表计算件归属包未指定（现成同类=MOD-SIG-145 `pattern_win_rate_materialize` 家族），存在"另起炉灶建第二张胜率表"风险——**册内未见** | 新登 |
| **L04-S6-G5** | 池 PIT 契约（shift(1)）只活在注释里，无读门面/单测钉住（与 S3-G1 同根，此处后果更重：未来函数直接污染概率表）——**册内未见** | 新登（与 S3-G1 合并执行） |

**⑤ 自审闸三态裁定**

| 项 | 裁定 | 理由（量尺=终局全貌） |
|---|---|---|
| G1 先例断更 | **移交数据线 + 本环节挂起**（解锁条件=`daban_engine_load_daily` 恢复至 T-1 且连续 10 日有行） | 复用先例前先验先例健康，是"抄作业抄到错答案"的防线；不自行修先例（跨域，属打板/数据线）；**不得以"它是别人的表"跳过**——终局全貌下无人工核对，先例病必传染新表 |
| G2 史深不对称日历 | **施工（P2，纯登记动作）** | 把"C07 最早可算日历"写进 C07 卡的启动条件即消灭"反复问能不能开算"的人工往复；成本一句话，收益是排期可机读 |
| G3 回补路径 | **施工（建议编 L04-C11，优先级高于新建概率表）** | 主判据：一次回补把"等 120 交易日"变成"当天就有 4 年池史"，直接解锁 C07 与全部下游；**但必须与真值日批分开标尺**（`data_source='replay'` + 独立 version），否则回补数据冒充盘后真值=终局最不可容忍的污染；反驳者一问（本册加试，见 §⑤末） |
| G4 归属包 | **施工（一句话改卡）** | 净零：明确"扩 MOD-SIG-145 的粒度枚举，不新建第二张胜率表"，防重复立卡（§4 内收铁律"同域重复簇→收敛唯一"） |
| G5 PIT 钉住 | **施工（随 S3-G1 读门面批）** | 与 S3-G1 同一件解决两册，禁分两次施工 |
| C07 本体 | **挂起排期** | 解锁条件三件齐：①池真值史 ≥120 交易日（或 G3 回补完成）②S1 传导分有值（S1-G2 施工完）③S5 停牌/涨停可成交口径进格子定义；终局必须要（个股层概率面是"状态→期望"链条的收口），**非封矿** |

**反驳者一问（G3 大候选加试，最强三条反因 + 最坏情形）**
1. 回补的池史是"用今日算法回看昨日"，与真值日批**不是同一口径**（参数/阈值随版本演化），回补数据会给出一个"从未真实存在过的池"→ 最坏情形：概率表建立在假历史上，考试全部通过而实盘不复现。**处方**：回补行必带 `version` + `data_source='replay'` + 回补时点的 `snapshot_meta.algo_fingerprint`，概率表考试默认**只认真值行**，回补行只作先验与量级估计。
2. 回补要跑全史日批（2020-03 起，约 1,500+ 交易日），与"GPU 被 T1 独占、机器上另有 11 条车道"冲突 → 最坏情形：挤占生产采集窗口。**处方**：CPU-only 分段回填 + 登记 `process_reaper_keep` 防误杀 + 单次窗口 ≤N 日。
3. 上游因子值不可回补（S4-G1 存储层零施工），回补出的"评分明细"必为残缺 → 最坏情形：池成员能回补、`score_components` 不可回补，半张假表。**处方**：回补范围限定"成员+顺位+否决"三列族，其余列显式 NULL（沿用生产者"禁拍假值冒充"不变量）。
→ 三条反因均可被处方对冲，故判**施工**而非封；但排期在真值日批稳定之后（先有真值，再谈回补对照）。

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | signal/noise 与归因 |
|---|---|---|---|
| R1 | 内部：daban 先例（头注 + tasks.yaml DAG + CH 行数/史深/尾巴） | signal | 16 交易日 + 止 09-22 + MATURITY=testing → 先例健康未验（G1） |
| R2 | 内部：全库概率/胜率表枚举 + 列结构 + 生产腿 | signal（改判级） | 净发现 `market_pattern_win_rate` 在产概率表（父簿与 SKEL 均未登记）→ LK-05/C07 口径改判 |
| R3 | 内部：池表零行复核 + PIT 契约承载方式 | signal | 史深 0 实测；shift(1) 只在注释 |
| R4 | 外部：小样本格子收缩（1 轮） | noise 2 → 降级为"题录登记，不入图" | 归因=命中的是工具站文档与镜像 PDF（无原发布方/年份，闸 1 不可溯）；本向结论改由内部实证（low_sample 列）承载，未以模型记忆冒充"业界都这么做" |
| R5 | 外部：条件收益分布表标准提法 | 已查无（查法见 §①行） | 记档 |

**长尾（本册调研未尽，明确列出）**
- T1 `pattern_win_rate_materialize` 的 `low_sample` 阈值取值与 17 号文 n≥30/Wilson LB 是否同值（决定 C07 能否直接沿用现役格子判据）。
- T2 `daban_engine_load` 断尾原因（任务失败史/DAG 前置未落）——属数据线，本册只登记"断尾"事实。
- T3 个股前视收益 `fwd_ret` 的既有计算件位置（`kline_daily` 直取还是已有 provider 封装），影响 C07 工时估计。

**本册封矿判据自评**：六向已填（含两处"已查无/降级题录"），T1-T3 未清空 → **状态=MINING（长尾在册）**。
